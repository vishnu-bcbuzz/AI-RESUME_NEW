"""Standard ATS-friendly resume document generator for DOCX and PDF formats.

Applies the layout, typography, section order, and styling of the Round Robin-selected template.
Generates fully editable DOCX via python-docx and corresponding PDF via PyMuPDF (fitz).
Strictly ATS-compliant, single-column readable structures without parsing obstacles.
Strictly black text on pure white background: NO colors, NO gradients, NO emojis.
"""

import logging
import re
import uuid
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE
import fitz  # PyMuPDF

from app.config import settings
from app.reports.templates import ResumeTemplate
from app.projects.generator import EnhancedResumeContent

logger = logging.getLogger("futrsec.renderer")

BLACK_RGB = RGBColor(0, 0, 0)
BLACK_PDF = (0.0, 0.0, 0.0)
LINK_BLUE_HEX = "0044CC"
LINK_BLUE_PDF = (0.0, 0.27, 0.8)


def add_docx_hyperlink(
    paragraph,
    url: str,
    text: str,
    font_name: str = "Calibri",
    font_size_pt: float = 9.5,
    color: str = LINK_BLUE_HEX,
    underline: bool = True,
):
    """Adds a clickable hyperlink run to a python-docx paragraph.

    Embeds an external relationship and attaches a styled run inside <w:hyperlink>.
    """
    part = paragraph.part
    r_id = part.relate_to(url, RELATIONSHIP_TYPE.HYPERLINK, is_external=True)

    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)

    new_run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")

    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:ascii"), font_name)
    rFonts.set(qn("w:hAnsi"), font_name)
    rPr.append(rFonts)

    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), str(int(font_size_pt * 2)))
    rPr.append(sz)

    c = OxmlElement("w:color")
    c.set(qn("w:val"), color)
    rPr.append(c)

    if underline:
        u = OxmlElement("w:u")
        u.set(qn("w:val"), "single")
        rPr.append(u)

    new_run.append(rPr)

    t = OxmlElement("w:t")
    t.text = text
    if text.startswith(" ") or text.endswith(" "):
        t.set(qn("xml:space"), "preserve")
    new_run.append(t)

    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)


def extract_contact_segments(content: EnhancedResumeContent) -> List[Dict[str, Any]]:
    """Splits candidate contact information into structured tokens with blue clickable hyperlinks.

    Extracts verified candidate email address (mailto:), LinkedIn/GitHub links, and standard text components.
    """
    header_str = (content.contact_header or "").strip()
    cd = content.contact_details or {}

    raw_tokens: List[str] = []
    if header_str:
        raw_tokens = [t.strip() for t in header_str.split("|") if t.strip()]
    elif cd:
        for k in ("email", "phone", "location", "linkedin", "github"):
            val = cd.get(k)
            if val and str(val).strip():
                raw_tokens.append(str(val).strip())

    email_pattern = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    items: List[Dict[str, Any]] = []

    for token in raw_tokens:
        email_match = email_pattern.search(token)
        if email_match:
            email_addr = email_match.group(0)
            prefix = token[:email_match.start()]
            suffix = token[email_match.end():]
            if prefix:
                items.append({"text": prefix, "is_link": False, "url": ""})
            items.append({"text": email_addr, "is_link": True, "url": f"mailto:{email_addr}"})
            if suffix:
                items.append({"text": suffix, "is_link": False, "url": ""})
        elif "linkedin.com" in token.lower():
            clean_url = token if token.startswith("http") else f"https://{token}"
            items.append({"text": token, "is_link": True, "url": clean_url})
        elif "github.com" in token.lower():
            clean_url = token if token.startswith("http") else f"https://{token}"
            items.append({"text": token, "is_link": True, "url": clean_url})
        elif token.lower().startswith("http://") or token.lower().startswith("https://"):
            items.append({"text": token, "is_link": True, "url": token})
        else:
            items.append({"text": token, "is_link": False, "url": ""})

    # Assemble into segments with " | " separators
    segments: List[Dict[str, Any]] = []
    for idx, item in enumerate(items):
        if idx > 0 and not item["text"].startswith(" ") and not (segments and segments[-1]["text"].endswith(" ")):
            segments.append({"text": " | ", "is_link": False, "url": ""})
        segments.append(item)

    return segments


class DocumentRenderer:
    """Renders resume content according to the assigned Round Robin template layout."""

    @classmethod
    def render_resume(
        cls,
        content: EnhancedResumeContent,
        template: ResumeTemplate,
        job_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Main rendering pipeline. Produces DOCX and corresponding PDF."""
        file_id = job_id or f"resume_{uuid.uuid4().hex[:12]}"
        settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        docx_path = settings.OUTPUT_DIR / f"{file_id}.docx"
        pdf_path = settings.OUTPUT_DIR / f"{file_id}.pdf"

        # 1. Render DOCX with template layout and typography
        cls._render_docx(content, template, docx_path)

        # 2. Render PDF with matching layout, typography, and pagination
        pdf_generated = False
        pdf_note = ""
        try:
            cls._render_pdf(content, template, pdf_path)
            pdf_generated = True
            pdf_note = "PDF generated successfully via PyMuPDF multi-page rendering engine."
        except Exception as exc:
            logger.warning("PDF generation could not complete: %s", exc)
            pdf_note = f"PDF conversion limitation: {exc}. Primary DOCX format provided."

        return {
            "file_id": file_id,
            "template_id": template.template_id,
            "template_name": template.template_name,
            "docx_path": str(docx_path),
            "docx_filename": docx_path.name,
            "pdf_path": str(pdf_path) if pdf_generated else None,
            "pdf_filename": pdf_path.name if pdf_generated else None,
            "pdf_available": pdf_generated,
            "pdf_status_note": pdf_note,
        }

    @classmethod
    def _render_docx(cls, content: EnhancedResumeContent, template: ResumeTemplate, output_path: Path) -> None:
        """Constructs an ATS-friendly DOCX document reflecting the chosen template layout."""
        # Ensure the selected template respects the mandatory ATS specifications
        style_cfg = template.style_config or {}
        # Verify font family is allowed before any rendering begins
        allowed_fonts = {"Arial", "Calibri", "Aptos", "Times New Roman"}
        font_name = style_cfg.get("font_family", "Calibri")
        if font_name not in allowed_fonts:
            raise RuntimeError(f"Unsupported font '{font_name}'. Must be one of {allowed_fonts}")

        doc = Document()
        # Set A4 portrait page size (210 mm × 297 mm) – values in inches for python-docx
        for sec in doc.sections:
            sec.page_width = Inches(8.27)   # 210 mm
            sec.page_height = Inches(11.69)  # 297 mm
            # Apply margins (default 0.75 in, overridden per template but clamped to allowed range)
            margins_in = max(0.5, min(style_cfg.get("margins_in", 0.75), 0.75))
            sec.top_margin = Inches(margins_in)
            sec.bottom_margin = Inches(margins_in)
            sec.left_margin = Inches(margins_in)
            sec.right_margin = Inches(margins_in)

        font_name = style_cfg.get("font_family", "Calibri")
        heading_font = style_cfg.get("heading_font", font_name)
        body_size_val = style_cfg.get("body_font_size_pt", 10.5)
        body_size_pt = Pt(body_size_val)
        heading_size_pt = Pt(style_cfg.get("heading_font_size_pt", 12.5))
        title_size_pt = Pt(style_cfg.get("title_font_size_pt", 22.0))
        contact_size_pt = Pt(style_cfg.get("contact_font_size_pt", 9.5))
        is_centered = style_cfg.get("header_alignment") == "center"
        header_align = WD_ALIGN_PARAGRAPH.CENTER if is_centered else WD_ALIGN_PARAGRAPH.LEFT

        # --- 1. Candidate Name (Header) ---
        p_name = doc.add_paragraph()
        p_name.alignment = header_align
        p_name.paragraph_format.space_before = Pt(0)
        p_name.paragraph_format.space_after = Pt(2)
        run_name = p_name.add_run(content.candidate_name)
        run_name.font.name = heading_font
        run_name.font.size = title_size_pt
        run_name.font.bold = True
        run_name.font.color.rgb = BLACK_RGB

        # --- 1b. Professional Headline ---
        if content.professional_headline:
            p_hl = doc.add_paragraph()
            p_hl.alignment = header_align
            p_hl.paragraph_format.space_before = Pt(0)
            p_hl.paragraph_format.space_after = Pt(2)
            run_hl = p_hl.add_run(content.professional_headline)
            run_hl.font.name = heading_font
            run_hl.font.size = Pt(10.5)
            run_hl.font.bold = True
            run_hl.font.color.rgb = BLACK_RGB

        # --- 2. Contact Details Header with Clickable Email and Links ---
        p_contact = doc.add_paragraph()
        p_contact.alignment = header_align
        p_contact.paragraph_format.space_before = Pt(0)
        p_contact.paragraph_format.space_after = Pt(style_cfg.get("section_spacing_before_pt", 8.0))

        contact_segs = extract_contact_segments(content)
        if contact_segs:
            for seg in contact_segs:
                if seg["is_link"]:
                    add_docx_hyperlink(
                        p_contact,
                        url=seg["url"],
                        text=seg["text"],
                        font_name=font_name,
                        font_size_pt=style_cfg.get("contact_font_size_pt", 9.5),
                        color=LINK_BLUE_HEX,
                        underline=True,
                    )
                else:
                    run = p_contact.add_run(seg["text"])
                    run.font.name = font_name
                    run.font.size = contact_size_pt
                    run.font.color.rgb = BLACK_RGB
        else:
            run_contact = p_contact.add_run(content.contact_header)
            run_contact.font.name = font_name
            run_contact.font.size = contact_size_pt
            run_contact.font.color.rgb = BLACK_RGB

        # Divider line below header if specified
        divider_style = style_cfg.get("divider_style", "solid")
        if divider_style in ("solid", "thick", "double") and template.template_id in ("T01", "T04", "T07", "T10", "T20", "T26", "T30"):
            pPr = p_contact._p.get_or_add_pPr()
            pBdr = parse_xml(r'<w:pBdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                             r'<w:bottom w:val="single" w:sz="6" w:space="3" w:color="000000"/>'
                             r'</w:pBdr>')
            pPr.append(pBdr)

        # Helper to add section headers styled per template
        def add_section_header(title: str):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(style_cfg.get("section_spacing_before_pt", 8.0))
            p.paragraph_format.space_after = Pt(style_cfg.get("section_spacing_after_pt", 3.0))
            p.paragraph_format.keep_with_next = True
            # Formal centered headers for classic corporate templates
            if is_centered and template.template_id in ("T01", "T04", "T07", "T10", "T20", "T26", "T30"):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT

            run = p.add_run(title.upper())
            run.font.name = heading_font
            run.font.size = heading_size_pt
            run.font.bold = True
            run.font.color.rgb = BLACK_RGB

            if divider_style in ("solid", "thick", "double"):
                sz = "12" if divider_style == "thick" else "6"
                val = "double" if divider_style == "double" else "single"
                pPr = p._p.get_or_add_pPr()
                pBdr = parse_xml(f'<w:pBdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                                 f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="6" w:color="000000"/>'
                                 f'</w:pBdr>')
                pPr.append(pBdr)

        # Section render handlers
        def render_summary():
            if not content.professional_summary:
                return
            title = titles.get("summary", "Professional Summary")
            add_section_header(title)
            p_sum = doc.add_paragraph()
            p_sum.paragraph_format.space_before = Pt(2)
            p_sum.paragraph_format.space_after = Pt(4)
            p_sum.paragraph_format.line_spacing = 1.15
            run_sum = p_sum.add_run(content.professional_summary)
            run_sum.font.name = font_name
            run_sum.font.size = body_size_pt
            run_sum.font.color.rgb = BLACK_RGB

        def render_skills():
            if not content.technical_skills_grouped:
                return
            title = titles.get("skills", "Technical Skills")
            add_section_header(title)
            skills_font_size = Pt(min(max(body_size_val, 10.0), 10.5))

            for group_name, skills_list in content.technical_skills_grouped.items():
                if not skills_list:
                    continue

                # One compact paragraph per skill category: Bold label + comma-separated skills
                p_skill = doc.add_paragraph()
                p_skill.paragraph_format.left_indent = Pt(0)
                p_skill.paragraph_format.first_line_indent = Pt(0)
                p_skill.paragraph_format.space_before = Pt(0)
                p_skill.paragraph_format.space_after = Pt(2.5)  # 2–3 pt spacing after
                p_skill.paragraph_format.line_spacing = 1.05

                run_label = p_skill.add_run(f"{group_name}: ")
                run_label.font.name = font_name
                run_label.font.size = skills_font_size
                run_label.font.bold = True
                run_label.font.color.rgb = BLACK_RGB

                run_skills = p_skill.add_run(", ".join(skills_list))
                run_skills.font.name = font_name
                run_skills.font.size = skills_font_size
                run_skills.font.bold = False
                run_skills.font.color.rgb = BLACK_RGB

        def render_experience():
            if not content.experience:
                return
            title = titles.get("experience", "Professional Experience")
            add_section_header(title)
            exp_fmt = style_cfg.get("experience_format", "title_company_line")

            for exp in content.experience:
                p_job = doc.add_paragraph()
                p_job.paragraph_format.space_before = Pt(style_cfg.get("item_spacing_pt", 4.0))
                p_job.paragraph_format.space_after = Pt(1)
                p_job.paragraph_format.keep_with_next = True

                title_text = exp.get("job_title", "Role")
                company = exp.get("company") or "Organization"
                start = exp.get("start_date") or ""
                end = exp.get("end_date") or ("Present" if start else "")
                if start and end:
                    dates = f" ({start} – {end})"
                elif end:
                    dates = f" ({end})"
                elif start:
                    dates = f" ({start})"
                else:
                    dates = ""

                if exp_fmt == "two_line":
                    run_title = p_job.add_run(title_text)
                    run_title.font.name = heading_font
                    run_title.font.size = Pt(11)
                    run_title.font.bold = True
                    run_title.font.color.rgb = BLACK_RGB

                    p_sub = doc.add_paragraph()
                    p_sub.paragraph_format.space_before = Pt(0)
                    p_sub.paragraph_format.space_after = Pt(1)
                    p_sub.paragraph_format.keep_with_next = True
                    run_comp = p_sub.add_run(f"{company}{dates}")
                    run_comp.font.name = font_name
                    run_comp.font.size = Pt(10)
                    run_comp.font.italic = True
                    run_comp.font.color.rgb = BLACK_RGB
                else:
                    run_title = p_job.add_run(title_text)
                    run_title.font.name = heading_font
                    run_title.font.size = Pt(11)
                    run_title.font.bold = True
                    run_title.font.color.rgb = BLACK_RGB

                    run_comp = p_job.add_run(f" | {company}{dates}")
                    run_comp.font.name = font_name
                    run_comp.font.size = Pt(10)
                    run_comp.font.italic = True
                    run_comp.font.color.rgb = BLACK_RGB

                for resp in exp.get("responsibilities", []):
                    p_resp = doc.add_paragraph(style="List Bullet")
                    p_resp.paragraph_format.space_before = Pt(0)
                    p_resp.paragraph_format.space_after = Pt(style_cfg.get("bullet_spacing_pt", 2.0))
                    p_resp.paragraph_format.line_spacing = 1.15
                    run_resp = p_resp.add_run(resp)
                    run_resp.font.name = font_name
                    run_resp.font.size = body_size_pt
                    run_resp.font.color.rgb = BLACK_RGB

        def render_internships():
            if not content.internships:
                return
            title = titles.get("internships", "Internships & Practicum")
            add_section_header(title)
            for intern in content.internships:
                p_int = doc.add_paragraph()
                p_int.paragraph_format.space_before = Pt(style_cfg.get("item_spacing_pt", 4.0))
                p_int.paragraph_format.space_after = Pt(1)
                p_int.paragraph_format.keep_with_next = True

                run_ititle = p_int.add_run(intern.get("job_title", "Intern"))
                run_ititle.font.name = heading_font
                run_ititle.font.size = Pt(11)
                run_ititle.font.bold = True
                run_ititle.font.color.rgb = BLACK_RGB

                org = intern.get("company") or "Host Organization"
                start = intern.get("start_date") or ""
                end = intern.get("end_date") or ("Present" if start else "")
                if start and end:
                    dates = f" ({start} – {end})"
                elif end:
                    dates = f" ({end})"
                elif start:
                    dates = f" ({start})"
                else:
                    dates = ""
                run_icomp = p_int.add_run(f" | {org}{dates}")
                run_icomp.font.name = font_name
                run_icomp.font.size = Pt(10)
                run_icomp.font.italic = True
                run_icomp.font.color.rgb = BLACK_RGB

                for resp in intern.get("responsibilities", []):
                    p_resp = doc.add_paragraph(style="List Bullet")
                    p_resp.paragraph_format.space_before = Pt(0)
                    p_resp.paragraph_format.space_after = Pt(style_cfg.get("bullet_spacing_pt", 2.0))
                    p_resp.paragraph_format.line_spacing = 1.15
                    run_resp = p_resp.add_run(resp)
                    run_resp.font.name = font_name
                    run_resp.font.size = body_size_pt
                    run_resp.font.color.rgb = BLACK_RGB

        def render_projects():
            if not content.projects:
                return
            title = titles.get("projects", "Projects")
            add_section_header(title)

            for proj in content.projects:
                p_proj = doc.add_paragraph()
                p_proj.paragraph_format.space_before = Pt(style_cfg.get("item_spacing_pt", 4.0))
                p_proj.paragraph_format.space_after = Pt(1)
                p_proj.paragraph_format.keep_with_next = True

                # Title
                p_title = proj.get("title", "Project")
                clean_title = re.sub(r"\s*\|\s*(?:Status:\s*)?(?:In Progress|Completed)$", "", p_title, flags=re.IGNORECASE).strip() or p_title
                run_pt = p_proj.add_run(clean_title)
                run_pt.font.name = heading_font
                run_pt.font.size = Pt(11)
                run_pt.font.bold = True
                run_pt.font.color.rgb = BLACK_RGB

                # Status: Completed | In Progress
                status = proj.get("status") or ("In Progress" if "in progress" in p_title.lower() else "Completed")
                run_status = p_proj.add_run(f" | Status: {status}")
                run_status.font.name = font_name
                run_status.font.size = Pt(9.5)
                run_status.font.italic = True
                run_status.font.color.rgb = BLACK_RGB

                # Technologies
                techs = proj.get("technologies", [])
                if techs:
                    p_tech = doc.add_paragraph()
                    p_tech.paragraph_format.space_before = Pt(1)
                    p_tech.paragraph_format.space_after = Pt(1)
                    p_tech.paragraph_format.keep_with_next = True

                    r_tech_lbl = p_tech.add_run("Technologies: ")
                    r_tech_lbl.font.name = font_name
                    r_tech_lbl.font.size = body_size_pt
                    r_tech_lbl.font.bold = True
                    r_tech_lbl.font.color.rgb = BLACK_RGB

                    r_tech_val = p_tech.add_run(", ".join(techs))
                    r_tech_val.font.name = font_name
                    r_tech_val.font.size = body_size_pt
                    r_tech_val.font.color.rgb = BLACK_RGB

                # Project URL / GitHub if present
                proj_url = proj.get("github_url") or proj.get("project_url")
                if proj_url:
                    p_url = doc.add_paragraph()
                    p_url.paragraph_format.space_before = Pt(0)
                    p_url.paragraph_format.space_after = Pt(1)
                    p_url.paragraph_format.keep_with_next = True

                    r_url_lbl = p_url.add_run("Project URL: ")
                    r_url_lbl.font.name = font_name
                    r_url_lbl.font.size = Pt(9.5)
                    r_url_lbl.font.bold = True
                    r_url_lbl.font.color.rgb = BLACK_RGB

                    clean_url_display = proj_url
                    full_link = proj_url if proj_url.startswith("http") else f"https://{proj_url}"
                    add_docx_hyperlink(p_url, full_link, clean_url_display, font_name=font_name, font_size_pt=9.5)

                # Bullets: 2 to 4 concise bullet points explaining actual implementation
                bullets = proj.get("bullets")
                desc = proj.get("description", "")
                if not bullets and desc:
                    bullets = [b.strip() for b in desc.split("\n") if b.strip()]
                if not bullets and proj.get("outcomes"):
                    bullets = [proj.get("outcomes")]

                valid_bullets = []
                if bullets:
                    for b in bullets:
                        b_clean = b.strip()
                        if b_clean and not b_clean.lower().startswith("technologies:"):
                            valid_bullets.append(b_clean)

                for b in valid_bullets[:4]:
                    p_desc = doc.add_paragraph(style="List Bullet")
                    p_desc.paragraph_format.space_before = Pt(0)
                    p_desc.paragraph_format.space_after = Pt(style_cfg.get("bullet_spacing_pt", 2.0))
                    p_desc.paragraph_format.line_spacing = 1.15
                    run_desc = p_desc.add_run(b)
                    run_desc.font.name = font_name
                    run_desc.font.size = body_size_pt
                    run_desc.font.color.rgb = BLACK_RGB

        def render_certifications():
            certs = content.certifications or []
            pursuing = getattr(content, "pursuing_certifications", []) or []
            if not certs and not pursuing:
                return
            title = titles.get("certifications", "Certifications")
            add_section_header(title)

            cert_spacing_after = Pt(style_cfg.get("bullet_spacing_pt", 2.0))

            for cert in certs:
                if not cert:
                    continue
                if isinstance(cert, str):
                    c_name = cert.strip()
                elif isinstance(cert, dict):
                    c_name = (cert.get("certification_name") or cert.get("name") or "").strip()
                elif hasattr(cert, "certification_name") and cert.certification_name:
                    c_name = cert.certification_name.strip()
                elif hasattr(cert, "name") and cert.name:
                    c_name = cert.name.strip()
                else:
                    c_name = str(cert).strip()

                if not c_name:
                    continue

                p_c = doc.add_paragraph(style="List Bullet")
                p_c.paragraph_format.space_before = Pt(0)
                p_c.paragraph_format.space_after = cert_spacing_after
                p_c.paragraph_format.line_spacing = 1.15
                run_c = p_c.add_run(c_name)
                run_c.font.name = font_name
                run_c.font.size = body_size_pt
                run_c.font.bold = False
                run_c.font.color.rgb = BLACK_RGB

            for pur in pursuing:
                if not pur:
                    continue
                p_pur = doc.add_paragraph(style="List Bullet")
                p_pur.paragraph_format.space_before = Pt(0)
                p_pur.paragraph_format.space_after = cert_spacing_after
                p_pur.paragraph_format.line_spacing = 1.15
                run_pur = p_pur.add_run(f"{pur} (Pursuing)")
                run_pur.font.name = font_name
                run_pur.font.size = body_size_pt
                run_pur.font.italic = True
                run_pur.font.color.rgb = BLACK_RGB

        def render_education():
            if not content.education:
                return
            title = titles.get("education", "Education")
            add_section_header(title)
            for edu in content.education:
                p_edu = doc.add_paragraph()
                p_edu.paragraph_format.space_before = Pt(2)
                p_edu.paragraph_format.space_after = Pt(2)

                run_deg = p_edu.add_run(edu.get("degree", "Degree"))
                run_deg.font.name = heading_font
                run_deg.font.size = Pt(10.5)
                run_deg.font.bold = True
                run_deg.font.color.rgb = BLACK_RGB

                inst = edu.get("institution") or ""
                year = f" ({edu.get('graduation_year')})" if edu.get("graduation_year") else ""
                gpa = f" | GPA: {edu.get('gpa')}" if edu.get("gpa") else ""
                run_inst = p_edu.add_run(f" — {inst}{year}{gpa}")
                run_inst.font.name = font_name
                run_inst.font.size = body_size_pt
                run_inst.font.color.rgb = BLACK_RGB

        def render_achievements():
            if not content.achievements:
                return
            title = titles.get("achievements", "Key Career Achievements")
            add_section_header(title)
            for ach in content.achievements:
                p_ach = doc.add_paragraph(style="List Bullet")
                p_ach.paragraph_format.space_before = Pt(0)
                p_ach.paragraph_format.space_after = Pt(style_cfg.get("bullet_spacing_pt", 2.0))
                p_ach.paragraph_format.line_spacing = 1.15
                run_ach = p_ach.add_run(ach)
                run_ach.font.name = font_name
                run_ach.font.size = body_size_pt
                run_ach.font.color.rgb = BLACK_RGB

        section_map = {
            "summary": render_summary,
            "skills": render_skills,
            "experience": render_experience,
            "internships": render_internships,
            "projects": render_projects,
            "certifications": render_certifications,
            "education": render_education,
            "achievements": render_achievements,
        }

        titles = style_cfg.get("section_titles", {})
        section_order = list(style_cfg.get(
            "section_order",
            ["summary", "skills", "experience", "internships", "projects", "certifications", "education", "achievements"],
        ))

        # Ensure certifications and core sections are present in standard ATS order
        if (content.certifications or getattr(content, "pursuing_certifications", None)) and "certifications" not in section_order:
            if "projects" in section_order:
                idx = section_order.index("projects")
                section_order.insert(idx + 1, "certifications")
            elif "skills" in section_order:
                idx = section_order.index("skills")
                section_order.insert(idx + 1, "certifications")
            else:
                section_order.append("certifications")

        if content.experience and "experience" not in section_order:
            if "certifications" in section_order:
                idx = section_order.index("certifications")
                section_order.insert(idx + 1, "experience")
            elif "projects" in section_order:
                idx = section_order.index("projects")
                section_order.insert(idx + 1, "experience")
            else:
                section_order.append("experience")

        if content.education and "education" not in section_order:
            section_order.append("education")

        for sec in section_order:
            if sec in section_map:
                section_map[sec]()

        doc.save(str(output_path))
        logger.info("Saved ATS DOCX resume to %s", output_path)

    @classmethod
    def _render_pdf(cls, content: EnhancedResumeContent, template: ResumeTemplate, output_path: Path) -> None:
        """Renders corresponding clean, multi-page PDF document using PyMuPDF (fitz).

        Strictly black text on white pages, with automatic page overflow, true font measurement,
        and section layout matching the selected Round Robin template.
        """
        doc = fitz.open()
        style_cfg = template.style_config or {}

        # Geometry & margins
        margins_in = style_cfg.get("margins_in", 0.75)
        left_m = margins_in * 72.0
        right_m = 612.0 - left_m
        top_m = margins_in * 72.0
        bottom_m = 792.0 - (margins_in * 72.0)
        printable_width = right_m - left_m

        # Font mapping
        font_family = style_cfg.get("font_family", "Calibri")
        is_serif = "times" in font_family.lower() or "georgia" in font_family.lower()

        reg_font = "times-roman" if is_serif else "helv"
        bold_font = "tibo" if is_serif else "hebo"
        italic_font = "tiit" if is_serif else "heit"

        font_objects = {
            reg_font: fitz.Font(reg_font),
            bold_font: fitz.Font(bold_font),
            italic_font: fitz.Font(italic_font),
        }

        # Page state tracking
        page = doc.new_page(width=612, height=792)
        current_y = top_m + 14.0

        def ensure_space(needed_pt: float):
            nonlocal page, current_y
            if current_y + needed_pt > bottom_m:
                page = doc.new_page(width=612, height=792)
                current_y = top_m + 14.0

        def wrap_text(text: str, font_key: str, size: float, max_w: float) -> List[str]:
            words = text.split()
            if not words:
                return []
            font_obj = font_objects[font_key]
            lines = []
            curr = ""
            for word in words:
                # If a single word is longer than max_w, chunk it to avoid clipping
                if font_obj.text_length(word, size) > max_w:
                    if curr:
                        lines.append(curr)
                        curr = ""
                    sub = ""
                    for ch in word:
                        if font_obj.text_length(sub + ch, size) <= max_w:
                            sub += ch
                        else:
                            if sub:
                                lines.append(sub)
                            sub = ch
                    curr = sub
                    continue

                test = f"{curr} {word}".strip() if curr else word
                if font_obj.text_length(test, size) <= max_w:
                    curr = test
                else:
                    if curr:
                        lines.append(curr)
                    curr = word
            if curr:
                lines.append(curr)
            return lines

        def draw_line_text(text: str, font_key: str, size: float, x: float):
            page.insert_text(
                fitz.Point(x, current_y),
                text,
                fontsize=size,
                fontname=font_key,
                color=BLACK_PDF,
            )

        def draw_paragraph(text: str, font_key: str, size: float, x: float, max_w: float, gap: float = 3.0):
            nonlocal current_y
            lines = wrap_text(text, font_key, size, max_w)
            for line in lines:
                ensure_space(size + gap)
                draw_line_text(line, font_key, size, x)
                current_y += (size + gap)

        def draw_bullet_point(text: str, font_key: str, size: float, indent: float = 14.0):
            nonlocal current_y
            bullet_char = "•"
            ensure_space(size + 3.0)
            max_w = printable_width - indent
            lines = wrap_text(text, font_key, size, max_w)
            if not lines:
                return
            draw_line_text(bullet_char, bold_font, size, left_m + 2.0)
            for idx, line in enumerate(lines):
                if idx > 0:
                    ensure_space(size + 2.5)
                draw_line_text(line, font_key, size, left_m + indent)
                current_y += (size + 2.5)
            current_y += 1.5

        is_centered = style_cfg.get("header_alignment") == "center"

        # --- 1. Candidate Name ---
        title_size = style_cfg.get("title_font_size_pt", 22.0)
        ensure_space(title_size + 6.0)
        if is_centered:
            name_w = font_objects[bold_font].text_length(content.candidate_name, title_size)
            name_x = left_m + (printable_width - name_w) / 2.0
        else:
            name_x = left_m
        draw_line_text(content.candidate_name, bold_font, title_size, name_x)
        current_y += (title_size * 0.85 + 4.0)

        # --- 1b. Professional Headline ---
        if content.professional_headline:
            ensure_space(14.0)
            hl_size = 10.5
            if is_centered:
                hl_w = font_objects[bold_font].text_length(content.professional_headline, hl_size)
                hl_x = left_m + (printable_width - hl_w) / 2.0
            else:
                hl_x = left_m
            draw_line_text(content.professional_headline, bold_font, hl_size, hl_x)
            current_y += 14.0

        # --- 2. Contact Details Header with Clickable Email and Links ---
        contact_size = style_cfg.get("contact_font_size_pt", 9.5)
        contact_segs = extract_contact_segments(content)
        if not contact_segs and content.contact_header:
            contact_segs = [{"text": content.contact_header, "is_link": False, "url": ""}]

        if contact_segs:
            lines = []
            curr_line = []
            curr_w = 0.0

            for seg in contact_segs:
                sw = font_objects[reg_font].text_length(seg["text"], contact_size)
                if curr_w + sw > printable_width and curr_line:
                    if curr_line and curr_line[-1]["text"].strip() == "|":
                        sep = curr_line.pop()
                        curr_w -= font_objects[reg_font].text_length(sep["text"], contact_size)
                    lines.append((curr_line, curr_w))
                    if seg["text"].strip() == "|":
                        curr_line = []
                        curr_w = 0.0
                    else:
                        curr_line = [seg]
                        curr_w = sw
                else:
                    curr_line.append(seg)
                    curr_w += sw

            if curr_line:
                lines.append((curr_line, curr_w))

            for line_segs, line_w in lines:
                ensure_space(contact_size + 3.0)
                if is_centered:
                    cx = left_m + (printable_width - line_w) / 2.0
                else:
                    cx = left_m

                for seg in line_segs:
                    sw = font_objects[reg_font].text_length(seg["text"], contact_size)
                    if seg["is_link"]:
                        page.insert_text(
                            fitz.Point(cx, current_y),
                            seg["text"],
                            fontsize=contact_size,
                            fontname=reg_font,
                            color=LINK_BLUE_PDF,
                        )
                        rect = fitz.Rect(cx, current_y - contact_size * 0.85, cx + sw, current_y + contact_size * 0.2)
                        page.insert_link({"kind": fitz.LINK_URI, "from": rect, "uri": seg["url"]})
                        page.draw_line(
                            fitz.Point(cx, current_y + 1.2),
                            fitz.Point(cx + sw, current_y + 1.2),
                            color=LINK_BLUE_PDF,
                            width=0.6,
                        )
                    else:
                        page.insert_text(
                            fitz.Point(cx, current_y),
                            seg["text"],
                            fontsize=contact_size,
                            fontname=reg_font,
                            color=BLACK_PDF,
                        )
                    cx += sw
                current_y += (contact_size + 3.5)

        # Divider line below header if specified
        divider_style = style_cfg.get("divider_style", "solid")
        if divider_style in ("solid", "thick", "double") and template.template_id in ("T01", "T04", "T07", "T10", "T20", "T26", "T30"):
            current_y += 2.0
            page.draw_line(fitz.Point(left_m, current_y), fitz.Point(right_m, current_y), color=BLACK_PDF, width=1.0)
            current_y += 6.0

        def add_pdf_section_heading(title: str):
            nonlocal current_y
            before_sp = style_cfg.get("section_spacing_before_pt", 8.0)
            after_sp = style_cfg.get("section_spacing_after_pt", 3.0)
            h_size = style_cfg.get("heading_font_size_pt", 12.0)
            ensure_space(before_sp + h_size + after_sp + 20.0)
            current_y += (before_sp + h_size)

            upper_title = title.upper()
            if is_centered and template.template_id in ("T01", "T04", "T07", "T10", "T20", "T26", "T30"):
                tw = font_objects[bold_font].text_length(upper_title, h_size)
                hx = left_m + (printable_width - tw) / 2.0
            else:
                hx = left_m
            draw_line_text(upper_title, bold_font, h_size, hx)
            current_y += 7.0

            if divider_style in ("solid", "thick", "double"):
                lw = 1.5 if divider_style == "thick" else 0.75
                page.draw_line(fitz.Point(left_m, current_y), fitz.Point(right_m, current_y), color=BLACK_PDF, width=lw)
                current_y += (after_sp + 14.5)
            else:
                current_y += (after_sp + 8.0)

        body_size = style_cfg.get("body_font_size_pt", 10.0)
        titles = style_cfg.get("section_titles", {})

        def pdf_summary():
            if not content.professional_summary:
                return
            add_pdf_section_heading(titles.get("summary", "Professional Summary"))
            draw_paragraph(content.professional_summary, reg_font, body_size, left_m, printable_width)
            nonlocal current_y
            current_y += 3.0

        def pdf_skills():
            if not content.technical_skills_grouped:
                return
            add_pdf_section_heading(titles.get("skills", "Technical Skills"))
            nonlocal current_y
            skills_size = min(max(body_size, 10.0), 10.5)
            line_height = skills_size + 2.0
            cat_spacing = 2.5

            for group_name, skills_list in content.technical_skills_grouped.items():
                if not skills_list:
                    continue

                label_text = f"{group_name}: "
                label_w = font_objects[bold_font].text_length(label_text, skills_size)
                skills_text = ", ".join(skills_list)
                words = skills_text.split()
                if not words:
                    continue

                first_line_words = []
                remaining_words = []
                avail_w_first = printable_width - label_w
                curr_w = 0.0
                space_w = font_objects[reg_font].text_length(" ", skills_size)

                for idx, word in enumerate(words):
                    w_w = font_objects[reg_font].text_length(word, skills_size)
                    needed = w_w if not first_line_words else (space_w + w_w)
                    if curr_w + needed <= avail_w_first:
                        first_line_words.append(word)
                        curr_w += needed
                    else:
                        remaining_words = words[idx:]
                        break

                ensure_space(line_height + 2.0)
                # Bold category label at standard left margin
                draw_line_text(label_text, bold_font, skills_size, left_m)
                # First line of skills immediately following the colon
                if first_line_words:
                    ftext = " ".join(first_line_words)
                    draw_line_text(ftext, reg_font, skills_size, left_m + label_w)
                current_y += line_height

                # Continuation lines wrap naturally aligned with paragraph left margin
                if remaining_words:
                    rem_text = " ".join(remaining_words)
                    rem_lines = wrap_text(rem_text, reg_font, skills_size, printable_width)
                    for rline in rem_lines:
                        ensure_space(line_height + 2.0)
                        draw_line_text(rline, reg_font, skills_size, left_m)
                        current_y += line_height

                current_y += cat_spacing

            current_y += 1.0

        def pdf_experience():
            if not content.experience:
                return
            add_pdf_section_heading(titles.get("experience", "Professional Experience"))
            nonlocal current_y
            exp_fmt = style_cfg.get("experience_format", "title_company_line")
            item_sp = style_cfg.get("item_spacing_pt", 4.0)

            for exp in content.experience:
                ensure_space(20.0)
                current_y += item_sp
                title_text = exp.get("job_title", "Role")
                company = exp.get("company") or "Organization"
                start = exp.get("start_date") or ""
                end = exp.get("end_date") or ("Present" if start else "")
                if start and end:
                    dates = f" ({start} – {end})"
                elif end:
                    dates = f" ({end})"
                elif start:
                    dates = f" ({start})"
                else:
                    dates = ""

                if exp_fmt == "two_line":
                    t_lines = wrap_text(title_text, bold_font, 10.5, printable_width)
                    for tl in t_lines:
                        draw_line_text(tl, bold_font, 10.5, left_m)
                        current_y += 13.0
                    c_lines = wrap_text(f"{company}{dates}", italic_font, 9.5, printable_width)
                    for cl in c_lines:
                        draw_line_text(cl, italic_font, 9.5, left_m)
                        current_y += 12.0
                else:
                    head_line = f"{title_text} | {company}{dates}"
                    h_lines = wrap_text(head_line, bold_font, 10.5, printable_width)
                    for hl in h_lines:
                        draw_line_text(hl, bold_font, 10.5, left_m)
                        current_y += 13.0

                for resp in exp.get("responsibilities", []):
                    draw_bullet_point(resp, reg_font, body_size)

        def pdf_internships():
            if not content.internships:
                return
            add_pdf_section_heading(titles.get("internships", "Internships & Practicum"))
            nonlocal current_y
            item_sp = style_cfg.get("item_spacing_pt", 4.0)

            for intern in content.internships:
                ensure_space(20.0)
                current_y += item_sp
                ititle = intern.get("job_title", "Intern")
                org = intern.get("company") or "Host Organization"
                start = intern.get("start_date") or ""
                end = intern.get("end_date") or ("Present" if start else "")
                if start and end:
                    dates = f" ({start} – {end})"
                elif end:
                    dates = f" ({end})"
                elif start:
                    dates = f" ({start})"
                else:
                    dates = ""
                head_line = f"{ititle} | {org}{dates}"
                h_lines = wrap_text(head_line, bold_font, 10.5, printable_width)
                for hl in h_lines:
                    draw_line_text(hl, bold_font, 10.5, left_m)
                    current_y += 13.0

                for resp in intern.get("responsibilities", []):
                    draw_bullet_point(resp, reg_font, body_size)

        def pdf_projects():
            if not content.projects:
                return
            add_pdf_section_heading(titles.get("projects", "Projects"))
            nonlocal current_y
            item_sp = style_cfg.get("item_spacing_pt", 4.0)

            for proj in content.projects:
                ensure_space(24.0)
                current_y += item_sp

                # Title & Status
                ptitle = proj.get("title", "Project")
                clean_title = re.sub(r"\s*\|\s*(?:Status:\s*)?(?:In Progress|Completed)$", "", ptitle, flags=re.IGNORECASE).strip() or ptitle
                status = proj.get("status") or ("In Progress" if "in progress" in ptitle.lower() else "Completed")
                head_line = f"{clean_title} | Status: {status}"

                h_lines = wrap_text(head_line, bold_font, 10.5, printable_width)
                for hl in h_lines:
                    draw_line_text(hl, bold_font, 10.5, left_m)
                    current_y += 13.0

                # Technologies line
                techs = proj.get("technologies", [])
                if techs:
                    ensure_space(12.0)
                    tech_label = "Technologies: "
                    tech_val = ", ".join(techs)
                    lbl_w = font_objects[bold_font].text_length(tech_label, body_size)
                    draw_line_text(tech_label, bold_font, body_size, left_m)

                    val_words = tech_val.split()
                    f_words = []
                    r_words = []
                    curr_tw = 0.0
                    sp_w = font_objects[reg_font].text_length(" ", body_size)
                    avail_tw = printable_width - lbl_w
                    for idx, w in enumerate(val_words):
                        ww = font_objects[reg_font].text_length(w, body_size)
                        need = ww if not f_words else (sp_w + ww)
                        if curr_tw + need <= avail_tw:
                            f_words.append(w)
                            curr_tw += need
                        else:
                            r_words = val_words[idx:]
                            break
                    if f_words:
                        draw_line_text(" ".join(f_words), reg_font, body_size, left_m + lbl_w)
                    current_y += (body_size + 2.5)

                    if r_words:
                        rem_tech_lines = wrap_text(" ".join(r_words), reg_font, body_size, printable_width - lbl_w)
                        for rtl in rem_tech_lines:
                            ensure_space(body_size + 2.5)
                            draw_line_text(rtl, reg_font, body_size, left_m + lbl_w)
                            current_y += (body_size + 2.5)

                # Project URL / GitHub if present
                proj_url = proj.get("github_url") or proj.get("project_url")
                if proj_url:
                    ensure_space(12.0)
                    url_lbl = "Project URL: "
                    lbl_uw = font_objects[bold_font].text_length(url_lbl, body_size - 0.5)
                    draw_line_text(url_lbl, bold_font, body_size - 0.5, left_m)

                    clean_url_display = proj_url
                    full_link = proj_url if proj_url.startswith("http") else f"https://{proj_url}"
                    url_w = font_objects[reg_font].text_length(clean_url_display, body_size - 0.5)

                    page.insert_text(
                        fitz.Point(left_m + lbl_uw, current_y),
                        clean_url_display,
                        fontsize=body_size - 0.5,
                        fontname=reg_font,
                        color=LINK_BLUE_PDF,
                    )
                    rect = fitz.Rect(left_m + lbl_uw, current_y - (body_size - 0.5) * 0.85, left_m + lbl_uw + url_w, current_y + (body_size - 0.5) * 0.2)
                    page.insert_link({"kind": fitz.LINK_URI, "from": rect, "uri": full_link})
                    page.draw_line(
                        fitz.Point(left_m + lbl_uw, current_y + 1.2),
                        fitz.Point(left_m + lbl_uw + url_w, current_y + 1.2),
                        color=LINK_BLUE_PDF,
                        width=0.6,
                    )
                    current_y += (body_size + 2.5)

                # 2 to 4 concise bullet points explaining actual implementation
                bullets = proj.get("bullets")
                desc = proj.get("description", "")
                if not bullets and desc:
                    bullets = [b.strip() for b in desc.split("\n") if b.strip()]
                if not bullets and proj.get("outcomes"):
                    bullets = [proj.get("outcomes")]

                valid_bullets = []
                if bullets:
                    for b in bullets:
                        b_clean = b.strip()
                        if b_clean and not b_clean.lower().startswith("technologies:"):
                            valid_bullets.append(b_clean)

                for b in valid_bullets[:4]:
                    draw_bullet_point(b, reg_font, body_size)

        def pdf_certifications():
            certs = content.certifications or []
            pursuing = getattr(content, "pursuing_certifications", []) or []
            if not certs and not pursuing:
                return
            add_pdf_section_heading(titles.get("certifications", "Certifications"))
            nonlocal current_y

            for cert in certs:
                if not cert:
                    continue
                if isinstance(cert, str):
                    c_name = cert.strip()
                elif isinstance(cert, dict):
                    c_name = (cert.get("certification_name") or cert.get("name") or "").strip()
                elif hasattr(cert, "certification_name") and cert.certification_name:
                    c_name = cert.certification_name.strip()
                elif hasattr(cert, "name") and cert.name:
                    c_name = cert.name.strip()
                else:
                    c_name = str(cert).strip()

                if not c_name:
                    continue

                draw_bullet_point(c_name, reg_font, body_size)

            for pur in pursuing:
                if not pur:
                    continue
                draw_bullet_point(f"{pur} (Pursuing)", italic_font, body_size)
            current_y += 1.5

        def pdf_education():
            if not content.education:
                return
            add_pdf_section_heading(titles.get("education", "Education"))
            nonlocal current_y
            for edu in content.education:
                ensure_space(14.0)
                deg = edu.get("degree", "Degree")
                inst = edu.get("institution") or ""
                year = f" ({edu.get('graduation_year')})" if edu.get("graduation_year") else ""
                gpa = f" | GPA: {edu.get('gpa')}" if edu.get("gpa") else ""
                line = f"{deg} — {inst}{year}{gpa}"
                draw_paragraph(line, reg_font, body_size, left_m, printable_width, gap=2.0)
            current_y += 3.0

        def pdf_achievements():
            if not content.achievements:
                return
            add_pdf_section_heading(titles.get("achievements", "Key Career Achievements"))
            for ach in content.achievements:
                draw_bullet_point(ach, reg_font, body_size)

        pdf_section_map = {
            "summary": pdf_summary,
            "skills": pdf_skills,
            "experience": pdf_experience,
            "internships": pdf_internships,
            "projects": pdf_projects,
            "certifications": pdf_certifications,
            "education": pdf_education,
            "achievements": pdf_achievements,
        }

        section_order = list(style_cfg.get(
            "section_order",
            ["summary", "skills", "experience", "internships", "projects", "certifications", "education", "achievements"],
        ))

        # Ensure certifications and core sections are present in standard ATS order
        if (content.certifications or getattr(content, "pursuing_certifications", None)) and "certifications" not in section_order:
            if "projects" in section_order:
                idx = section_order.index("projects")
                section_order.insert(idx + 1, "certifications")
            elif "skills" in section_order:
                idx = section_order.index("skills")
                section_order.insert(idx + 1, "certifications")
            else:
                section_order.append("certifications")

        if content.experience and "experience" not in section_order:
            if "certifications" in section_order:
                idx = section_order.index("certifications")
                section_order.insert(idx + 1, "experience")
            elif "projects" in section_order:
                idx = section_order.index("projects")
                section_order.insert(idx + 1, "experience")
            else:
                section_order.append("experience")

        if content.education and "education" not in section_order:
            section_order.append("education")

        for sec in section_order:
            if sec in pdf_section_map:
                pdf_section_map[sec]()

        # Remove any unnecessary trailing blank pages
        while len(doc) > 1:
            last_page = doc[-1]
            if not last_page.get_text().strip() and len(last_page.get_links()) == 0:
                doc.delete_page(len(doc) - 1)
            else:
                break

        doc.save(str(output_path))
        doc.close()
        logger.info("Saved ATS PDF resume to %s", output_path)
