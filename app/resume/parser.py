"""Resume document parsing module for PDF and DOCX files.

Handles secure file validation, content verification, text extraction,
scanned document detection, prompt-injection sanitization, and temporary file cleanup.
"""

import io
import re
import zipfile
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import fitz  # PyMuPDF
from pypdf import PdfReader
from docx import Document

from app.config import settings

logger = logging.getLogger("futrsec.parser")


class ResumeParsingError(Exception):
    """Custom exception raised when resume parsing fails validation or processing."""
    pass


class ResumeParser:
    """Secure parser for candidate resumes in PDF and DOCX formats."""

    # Magic byte signatures
    PDF_MAGIC = b"%PDF-"
    ZIP_MAGIC = b"PK\x03\x04"

    # Known signatures of disallowed formats (checked even if renamed to .pdf or .docx)
    DISALLOWED_SIGNATURES = [
        (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", "Legacy .doc format detected. Supported formats: PDF and DOCX only. Please convert your file to .docx or .pdf."),
        (b"MZ", "Executable file detected. Executables are strictly prohibited. Supported formats: PDF and DOCX only."),
        (b"\x7fELF", "Binary executable detected. Executables are strictly prohibited. Supported formats: PDF and DOCX only."),
        (b"{\\rtf", "RTF format detected. Supported formats: PDF and DOCX only."),
        (b"\x89PNG\r\n\x1a\n", "PNG image file detected. Supported formats: PDF and DOCX only."),
        (b"\xff\xd8\xff", "JPEG image file detected. Supported formats: PDF and DOCX only."),
        (b"GIF87a", "GIF image file detected. Supported formats: PDF and DOCX only."),
        (b"GIF89a", "GIF image file detected. Supported formats: PDF and DOCX only."),
    ]

    # Known prompt-injection attack vectors embedded in resumes
    PROMPT_INJECTION_PATTERNS = [
        re.compile(r"(?i)\bignore\s+(all\s+)?(previous|prior|above)\s+instructions\b"),
        re.compile(r"(?i)\byou\s+are\s+now\s+(a|an)\b"),
        re.compile(r"(?i)\bsystem\s*:\s*"),
        re.compile(r"(?i)\bassistant\s*:\s*"),
        re.compile(r"(?i)\bdisregard\s+(all\s+)?guidelines\b"),
        re.compile(r"(?i)\bgive\s+(this\s+candidate|me)\s+(a\s+)?score\s+of\s+100\b"),
        re.compile(r"(?i)\balways\s+output\b"),
    ]

    @classmethod
    def validate_file(cls, filename: str, content: bytes) -> str:
        """Validates filename extension, file size, file signature, and document structure.

        Only .pdf and .docx formats are permitted.
        All other formats (including .doc, .txt, .rtf, images, executables, archives) are rejected.
        Returns normalized extension ('pdf' or 'docx').
        Raises ResumeParsingError on validation failure.
        """
        if not filename or "." not in filename:
            raise ResumeParsingError("Invalid file name: missing file extension. Supported formats: PDF and DOCX only.")

        ext = filename.rsplit(".", 1)[1].lower()

        # Explicitly reject legacy .doc files
        if ext == "doc":
            raise ResumeParsingError(
                "Legacy .doc format is not supported. Supported formats: PDF and DOCX only. "
                "Please convert your resume to .docx or .pdf before uploading."
            )

        if ext not in ("pdf", "docx"):
            raise ResumeParsingError(
                f"Unsupported file type '.{ext}'. Supported formats: PDF and DOCX only."
            )

        if len(content) == 0:
            raise ResumeParsingError("Uploaded file is empty (0 bytes). Supported formats: PDF and DOCX only.")

        if len(content) > settings.max_upload_size_bytes:
            raise ResumeParsingError(
                f"File size ({round(len(content) / (1024 * 1024), 2)}MB) exceeds limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
            )

        # Disallowed signature verification (detect disguised or renamed files)
        for sig, err_msg in cls.DISALLOWED_SIGNATURES:
            if content.startswith(sig):
                raise ResumeParsingError(err_msg)

        # Magic byte and package structure validation
        if ext == "pdf":
            if not content.startswith(cls.PDF_MAGIC) and cls.PDF_MAGIC not in content[:1024]:
                raise ResumeParsingError("Invalid PDF format: file header does not match PDF signature.")
        elif ext == "docx":
            if not content.startswith(cls.ZIP_MAGIC):
                raise ResumeParsingError("Invalid DOCX format: file header does not match DOCX/ZIP signature.")
            # Verify it's an actual DOCX containing word/document.xml and [Content_Types].xml
            try:
                with zipfile.ZipFile(io.BytesIO(content)) as zf:
                    namelist = zf.namelist()
                    if "word/document.xml" not in namelist or "[Content_Types].xml" not in namelist:
                        raise ResumeParsingError("Invalid DOCX format: missing word/document.xml package structure.")
            except zipfile.BadZipFile:
                raise ResumeParsingError("Corrupted or unreadable DOCX archive.")

        return ext

    @classmethod
    def _extract_page_text_column_aware(cls, page: fitz.Page) -> str:
        """Extracts text from a PDF page respecting multi-column layouts and visual flow.

        Detects two-column or multi-column regions and sequences blocks column-by-column
        (Header -> Left Column Top-to-Bottom -> Right Column Top-to-Bottom -> Bottom/Footer),
        preventing interleaved text across columns.
        """
        blocks = [b for b in page.get_text("blocks") if b[6] == 0 and b[4].strip()]
        if not blocks:
            return ""

        page_width = page.rect.width
        mid_x = page_width / 2.0

        # Check for two-column structure (blocks predominantly on left vs right)
        left_blocks = [b for b in blocks if b[2] <= mid_x + 30 and b[0] < mid_x - 30]
        right_blocks = [b for b in blocks if b[0] >= mid_x - 30 and b[2] > mid_x + 30]

        # If significant two-column layout detected (at least 2 distinct blocks on each side)
        if len(left_blocks) >= 2 and len(right_blocks) >= 2:
            min_col_y = min(min(b[1] for b in left_blocks), min(b[1] for b in right_blocks))
            max_col_y = max(max(b[3] for b in left_blocks), max(b[3] for b in right_blocks))

            # Header blocks above column split (e.g., candidate name, contact info)
            top_blocks = sorted([b for b in blocks if b[3] <= min_col_y + 10], key=lambda b: (b[1], b[0]))
            # Footer blocks below column split
            bottom_blocks = sorted([b for b in blocks if b[1] >= max_col_y - 10 and b not in top_blocks], key=lambda b: (b[1], b[0]))

            col_left = sorted([b for b in left_blocks if b not in top_blocks and b not in bottom_blocks], key=lambda b: (b[1], b[0]))
            col_right = sorted([b for b in right_blocks if b not in top_blocks and b not in bottom_blocks], key=lambda b: (b[1], b[0]))

            remaining = [b for b in blocks if b not in top_blocks and b not in bottom_blocks and b not in col_left and b not in col_right]
            remaining_sorted = sorted(remaining, key=lambda b: (b[1], b[0]))

            ordered_blocks = top_blocks + col_left + col_right + remaining_sorted + bottom_blocks
            return "\n".join(b[4].strip() for b in ordered_blocks if b[4].strip())
        else:
            # Single-column / standard flow: sort blocks top-to-bottom, left-to-right
            sorted_blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
            return "\n".join(b[4].strip() for b in sorted_blocks if b[4].strip())

    @classmethod
    def extract_text_from_pdf(cls, content: bytes) -> Tuple[str, Dict[str, Any]]:
        """Extracts text from PDF content using column-aware PyMuPDF with pypdf fallback."""
        text_parts = []
        page_count = 0
        has_images = False

        # Attempt 1: PyMuPDF (fast, accurate, column-aware)
        try:
            doc = fitz.open(stream=content, filetype="pdf")
            page_count = len(doc)
            for page in doc:
                page_text = cls._extract_page_text_column_aware(page)
                if page_text.strip():
                    text_parts.append(page_text)
                if len(page.get_images()) > 0:
                    has_images = True
            doc.close()
        except Exception as exc:
            logger.warning("PyMuPDF parsing encountered an issue: %s. Trying pypdf fallback...", exc)
            try:
                reader = PdfReader(io.BytesIO(content))
                page_count = len(reader.pages)
                for page in reader.pages:
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        text_parts.append(page_text)
            except Exception as inner_exc:
                raise ResumeParsingError(f"Failed to read PDF document: {inner_exc}")

        combined_text = "\n".join(text_parts).strip()
        word_count = len(combined_text.split())

        # Check for scanned image PDF or insufficient text
        if len(combined_text) < 100 or word_count < 20:
            if has_images:
                raise ResumeParsingError(
                    "Unable to extract readable text from PDF. The document may be a scanned image without an embedded text layer. "
                    "Please upload a text-searchable PDF (with selectable text) or a DOCX document, or apply OCR before uploading."
                )
            elif page_count == 0:
                raise ResumeParsingError("PDF document has 0 pages.")
            else:
                raise ResumeParsingError(
                    "The uploaded document contains insufficient text content to perform ATS analysis (fewer than 20 words detected). "
                    "Please ensure the file contains full resume content and is text-searchable."
                )

        combined_text = cls.dehyphenate_text(combined_text)

        metadata = {
            "page_count": page_count,
            "has_images": has_images,
            "character_count": len(combined_text),
            "word_count": len(combined_text.split()),
            "format": "pdf",
        }
        return combined_text, metadata

    @classmethod
    def dehyphenate_text(cls, text: str) -> str:
        """Fixes words and bullet points split by line-wrap hyphens."""
        if not text:
            return ""
        # Syllable breaks where second line is lowercase continuation: "authenti-\n cation" -> "authentication"
        text = re.sub(r"(\b[A-Za-z]+)-\s*\n\s*([a-z]+)", r"\1\2", text)
        # Line wrapped words split with trailing hyphen followed by capital or symbol: "Cloud-\n Computing" -> "Cloud-Computing"
        text = re.sub(r"(\b[A-Za-z]+)-\s*\n\s*([A-Za-z]+)", r"\1-\2", text)
        return text

    @classmethod
    def extract_text_from_docx(cls, content: bytes) -> Tuple[str, Dict[str, Any]]:
        """Extracts text from DOCX content preserving document flow and table structure."""
        try:
            from docx.oxml.text.paragraph import CT_P
            from docx.oxml.table import CT_Tbl
            from docx.text.paragraph import Paragraph
            from docx.table import Table

            doc = Document(io.BytesIO(content))
            text_parts = []
            para_count = 0
            tbl_count = 0

            # Iterate through body children in true document sequence
            for child in doc.element.body:
                if isinstance(child, CT_P):
                    p = Paragraph(child, doc)
                    text = p.text.strip()
                    if text:
                        text_parts.append(text)
                        para_count += 1
                elif isinstance(child, CT_Tbl):
                    tbl = Table(child, doc)
                    tbl_count += 1
                    for row in tbl.rows:
                        seen_cells = set()
                        row_items = []
                        for cell in row.cells:
                            if cell._tc not in seen_cells:
                                seen_cells.add(cell._tc)
                                ct = cell.text.strip()
                                if ct:
                                    row_items.append(ct)
                        if row_items:
                            text_parts.append(" | ".join(row_items))

            # Fallback if doc.element.body had no recognized elements
            if not text_parts:
                for paragraph in doc.paragraphs:
                    text = paragraph.text.strip()
                    if text:
                        text_parts.append(text)
                for table in doc.tables:
                    for row in table.rows:
                        row_texts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                        if row_texts:
                            text_parts.append(" | ".join(row_texts))

            combined_text = "\n".join(text_parts).strip()
            word_count = len(combined_text.split())

            if not combined_text or word_count < 5:
                raise ResumeParsingError("DOCX document contains no readable text content.")

            metadata = {
                "paragraph_count": para_count or len(doc.paragraphs),
                "table_count": tbl_count or len(doc.tables),
                "character_count": len(combined_text),
                "word_count": word_count,
                "format": "docx",
            }
            return combined_text, metadata
        except ResumeParsingError:
            raise
        except Exception as exc:
            raise ResumeParsingError(f"Failed to read DOCX document: {exc}")

    @classmethod
    def sanitize_untrusted_text(cls, raw_text: str) -> Tuple[str, bool]:
        """Cleans control characters and neutralizes prompt-injection attempts.

        Returns (sanitized_text, injection_detected).
        """
        # Strip null bytes and control chars (preserve newlines, tabs, carriage returns)
        cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", raw_text)

        # Detect and defuse prompt-injection patterns
        injection_detected = False
        for pattern in cls.PROMPT_INJECTION_PATTERNS:
            if pattern.search(cleaned):
                injection_detected = True
                # Neutralize matched command completely
                cleaned = pattern.sub(r"[UNTRUSTED_CONTENT_FILTERED]", cleaned)

        return cleaned, injection_detected

    @classmethod
    def parse_document(cls, filename: str, content: bytes) -> Dict[str, Any]:
        """Main entry point: validates, extracts, sanitizes, and returns document data."""
        ext = cls.validate_file(filename, content)

        if ext == "pdf":
            raw_text, meta = cls.extract_text_from_pdf(content)
        elif ext == "docx":
            raw_text, meta = cls.extract_text_from_docx(content)
        else:
            raise ResumeParsingError(f"Unsupported format: {ext}")

        sanitized_text, injection_detected = cls.sanitize_untrusted_text(raw_text)

        if injection_detected:
            logger.warning("Potential prompt-injection or suspicious pattern detected in resume: %s", filename)

        return {
            "filename": filename,
            "format": ext,
            "raw_text": sanitized_text,
            "character_count": len(sanitized_text),
            "word_count": len(sanitized_text.split()),
            "metadata": meta,
            "security_flag_injection_detected": injection_detected,
        }
