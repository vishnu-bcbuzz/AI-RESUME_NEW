"""Compiles docs/PROJECT_REPORT.md and embedded figures into a professional, publication-quality DOCX and vector PDF report."""

import os
import re
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import fitz

BASE_DIR = Path("V:/ai_jobagent/docs")
MD_PATH = BASE_DIR / "PROJECT_REPORT.md"
DOCX_OUT = BASE_DIR / "FUTRSEC_AI_Resume_Engine_Technical_Report.docx"
PDF_OUT = BASE_DIR / "FUTRSEC_AI_Resume_Engine_Technical_Report.pdf"

# Color Palette
COLOR_PRIMARY = RGBColor(15, 23, 42)      # Slate 900
COLOR_SECONDARY = RGBColor(30, 64, 175)   # Blue 800
COLOR_TEXT = RGBColor(51, 65, 85)         # Slate 700
COLOR_MUTED = RGBColor(100, 116, 139)     # Slate 500
COLOR_BORDER = "CBD5E1"                   # Slate 300


def build_docx_report():
    doc = Document()

    # Set Margins (0.75 in)
    for sec in doc.sections:
        sec.top_margin = Inches(0.75)
        sec.bottom_margin = Inches(0.75)
        sec.left_margin = Inches(0.75)
        sec.right_margin = Inches(0.75)
        sec.page_width = Inches(8.27)
        sec.page_height = Inches(11.69)

    # 1. Title Page / Cover
    p_title_space = doc.add_paragraph()
    p_title_space.paragraph_format.space_before = Pt(36)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t = p_title.add_run("FUTRSEC AI RESUME ENGINE")
    run_t.font.name = "Calibri"
    run_t.font.size = Pt(28)
    run_t.font.bold = True
    run_t.font.color.rgb = COLOR_SECONDARY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = p_sub.add_run("Comprehensive Technical Project Report & Architectural Specification")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(14)
    run_sub.font.color.rgb = COLOR_PRIMARY
    run_sub.font.bold = True
    p_sub.paragraph_format.space_after = Pt(18)

    p_desc = doc.add_paragraph()
    p_desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_desc = p_desc.add_run(
        "Cybersecurity-Focused ATS Resume Analysis, Deterministic Mathematical Scoring,\n"
        "Skill-Gap Detection, and Persistent Round Robin ATS Document Generation"
    )
    run_desc.font.name = "Calibri"
    run_desc.font.size = Pt(11)
    run_desc.font.italic = True
    run_desc.font.color.rgb = COLOR_MUTED
    p_desc.paragraph_format.space_after = Pt(48)

    # Metadata table on cover page
    tbl = doc.add_table(rows=5, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta = [
        ("Project Title:", "FUTRSEC AI Resume Engine"),
        ("Engineering Team:", "FUTRSEC Cyber Operations & Architecture Team"),
        ("Database Backend:", "Neon Serverless PostgreSQL (74 Roles, 1,425 Skills, 370 Criteria)"),
        ("AI Integrations:", "Stage 1: Google Gemini 3.6 Flash | Stage 2: GroqCloud (gpt-oss-120b)"),
        ("Date / Version:", "October 2026 | Production Release 2.0 (122 Automated Tests Passed)"),
    ]
    for row_idx, (k, v) in enumerate(meta):
        cell_k, cell_v = tbl.rows[row_idx].cells
        cell_k.text = k
        cell_v.text = v
        cell_k.paragraphs[0].runs[0].font.bold = True
        cell_k.paragraphs[0].runs[0].font.size = Pt(10)
        cell_v.paragraphs[0].runs[0].font.size = Pt(10)
        cell_k.width = Inches(2.2)
        cell_v.width = Inches(4.5)

    doc.add_page_break()

    # Read Markdown and render sections
    with open(MD_PATH, "r", encoding="utf-8") as f:
        md_text = f.read()

    lines = md_text.split("\n")
    skip_header = True

    in_table = False
    table_lines = []

    def flush_table(t_lines):
        if not t_lines or len(t_lines) < 2:
            return
        header = [c.strip() for c in t_lines[0].split("|")[1:-1]]
        data = []
        for line in t_lines[2:]:
            if line.strip().startswith("|"):
                data.append([c.strip() for c in line.split("|")[1:-1]])
        if not header:
            return

        table = doc.add_table(rows=len(data) + 1, cols=len(header))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for c_idx, h in enumerate(header):
            cell = table.rows[0].cells[c_idx]
            cell.text = h
            cell.paragraphs[0].runs[0].font.bold = True
            cell.paragraphs[0].runs[0].font.size = Pt(9.5)
            # Shading for header
            shading = parse_xml(r'<w:shd {} w:fill="F1F5F9"/>'.format(nsdecls('w')))
            cell._tc.get_or_add_tcPr().append(shading)

        for r_idx, row in enumerate(data):
            for c_idx, val in enumerate(row):
                if c_idx < len(header):
                    cell = table.rows[r_idx + 1].cells[c_idx]
                    cell.text = val
                    if cell.paragraphs[0].runs:
                        cell.paragraphs[0].runs[0].font.size = Pt(9)
        p_sp = doc.add_paragraph()
        p_sp.paragraph_format.space_after = Pt(6)

    for line in lines:
        sline = line.strip()

        # Stop skipping after Executive Summary
        if sline.startswith("## Executive Summary"):
            skip_header = False

        if skip_header:
            continue

        # Handle tables
        if sline.startswith("|"):
            in_table = True
            table_lines.append(sline)
            continue
        else:
            if in_table:
                flush_table(table_lines)
                table_lines = []
                in_table = False

        # Headings
        if sline.startswith("## "):
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(14)
            h.paragraph_format.space_after = Pt(4)
            h.paragraph_format.keep_with_next = True
            run = h.add_run(sline[3:])
            run.font.name = "Calibri"
            run.font.size = Pt(15)
            run.font.bold = True
            run.font.color.rgb = COLOR_SECONDARY
        elif sline.startswith("### "):
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(10)
            h.paragraph_format.space_after = Pt(2)
            h.paragraph_format.keep_with_next = True
            run = h.add_run(sline[4:])
            run.font.name = "Calibri"
            run.font.size = Pt(12.5)
            run.font.bold = True
            run.font.color.rgb = COLOR_PRIMARY
        elif sline.startswith("!["):
            # Image Embed: ![Caption](diagrams/figX.png)
            m = re.search(r"\(([^)]+)\)", sline)
            if m:
                rel_path = m.group(1).replace("/", os.sep)
                img_path = BASE_DIR / rel_path
                if img_path.exists():
                    p_img = doc.add_paragraph()
                    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_img.paragraph_format.space_before = Pt(8)
                    p_img.paragraph_format.space_after = Pt(4)
                    doc.add_picture(str(img_path), width=Inches(6.2))
        elif sline.startswith("*Figure "):
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(8)
            run_cap = p_cap.add_run(sline.replace("*", ""))
            run_cap.font.name = "Calibri"
            run_cap.font.size = Pt(9)
            run_cap.font.italic = True
            run_cap.font.color.rgb = COLOR_MUTED
        elif sline.startswith("- ") or sline.startswith("* "):
            p_bullet = doc.add_paragraph(style="List Bullet")
            p_bullet.paragraph_format.space_before = Pt(1)
            p_bullet.paragraph_format.space_after = Pt(1.5)
            run = p_bullet.add_run(sline[2:])
            run.font.name = "Calibri"
            run.font.size = Pt(10)
            run.font.color.rgb = COLOR_TEXT
        elif re.match(r"^\d+\.\s+", sline):
            p_num = doc.add_paragraph(style="List Number")
            p_num.paragraph_format.space_before = Pt(1)
            p_num.paragraph_format.space_after = Pt(1.5)
            clean_text = re.sub(r"^\d+\.\s+", "", sline)
            run = p_num.add_run(clean_text)
            run.font.name = "Calibri"
            run.font.size = Pt(10)
            run.font.color.rgb = COLOR_TEXT
        elif sline == "---":
            continue
        elif sline:
            p_body = doc.add_paragraph()
            p_body.paragraph_format.space_before = Pt(2)
            p_body.paragraph_format.space_after = Pt(4)
            p_body.paragraph_format.line_spacing = 1.15
            run = p_body.add_run(sline)
            run.font.name = "Calibri"
            run.font.size = Pt(10)
            run.font.color.rgb = COLOR_TEXT

    if in_table:
        flush_table(table_lines)

    doc.save(str(DOCX_OUT))
    print(f"Generated DOCX Report at: {DOCX_OUT}")


def build_pdf_report():
    """Generates a professional multi-page vector PDF report using PyMuPDF and the report assets."""
    pdf_doc = fitz.open()

    # Cover Page
    page = pdf_doc.new_page(width=595.28, height=841.89)  # A4 pt
    
    # Header Accent Bar
    page.draw_rect(fitz.Rect(0, 0, 595.28, 12), color=None, fill=(0.06, 0.25, 0.72))

    # Title & Metadata
    page.insert_text(fitz.Point(54, 110), "FUTRSEC AI RESUME ENGINE", fontsize=24, fontname="helv", fontfile=None, color=(0.06, 0.25, 0.72))
    page.insert_text(fitz.Point(54, 135), "Comprehensive Technical Project Report & Architectural Specification", fontsize=13, fontname="helv", color=(0.06, 0.09, 0.16))
    page.insert_text(fitz.Point(54, 160), "Cybersecurity ATS Analysis, Deterministic Scoring, & Round Robin ATS Document Generation", fontsize=9.5, fontname="helv", color=(0.4, 0.45, 0.55))

    page.draw_line(fitz.Point(54, 175), fitz.Point(541, 175), color=(0.8, 0.83, 0.88), width=1.0)

    # Embed Figure 2 (Architecture) on Cover/Intro Page
    fig2_path = BASE_DIR / "diagrams" / "fig2_system_architecture.png"
    if fig2_path.exists():
        page.insert_image(fitz.Rect(54, 195, 541, 520), filename=str(fig2_path))

    # Metadata Box at bottom
    page.draw_rect(fitz.Rect(54, 540, 541, 740), color=(0.8, 0.83, 0.88), fill=(0.96, 0.97, 0.98), width=1.0)
    meta_y = 570
    metadata = [
        ("Project Title:", "FUTRSEC AI Resume Engine"),
        ("Domain:", "Cybersecurity & Information Security Automated Recruitment"),
        ("Database Backend:", "Neon Serverless PostgreSQL (74 Roles, 1,425 Skills, 370 Scoring Weights)"),
        ("Hosted AI Pipeline:", "Stage 1: Google Gemini 3.6 Flash | Stage 2: GroqCloud (openai/gpt-oss-120b)"),
        ("Template Scheduler:", "Persistent Round Robin Scheduler (20 Black-and-White ATS Templates)"),
        ("Testing & Quality:", "122 Automated Tests Passed (100% Pass Rate in Pytest)"),
        ("Document Status:", "Official Release 2.0 — Production Report (October 2026)"),
    ]
    for lbl, val in metadata:
        page.insert_text(fitz.Point(70, meta_y), lbl, fontsize=9.5, fontname="helv", color=(0.06, 0.25, 0.72))
        page.insert_text(fitz.Point(200, meta_y), val, fontsize=9.0, fontname="helv", color=(0.2, 0.25, 0.35))
        meta_y += 24

    # Footer
    page.draw_line(fitz.Point(54, 790), fitz.Point(541, 790), color=(0.8, 0.83, 0.88), width=0.8)
    page.insert_text(fitz.Point(54, 805), "FUTRSEC Cyber Operations | Technical Architecture & System Specification", fontsize=8, fontname="helv", color=(0.4, 0.45, 0.55))
    page.insert_text(fitz.Point(510, 805), "Page 1", fontsize=8, fontname="helv", color=(0.4, 0.45, 0.55))

    # Pages 2+: Body & Figures
    figures = [
        ("Figure 1: End-to-End Workflow Flowchart", BASE_DIR / "diagrams" / "fig1_workflow_flowchart.png", 
         "Depicts the complete execution pipeline from candidate PDF/DOCX ingestion and magic-byte security checks, through deterministic scoring, Stage 1 Gemini analysis, Candidate Approval Studio, persistent Round Robin template assignment, and automatic re-scoring."),
        ("Figure 3: Deterministic ATS Scoring Weight Distribution", BASE_DIR / "diagrams" / "fig3_deterministic_scoring.png",
         "Illustrates the mathematical category weight allocations configured in Neon PostgreSQL: Technical Skills (40%), Projects (25%), Education (15%), Certifications & Tools (15%), and Professional Objective (5%)."),
        ("Figure 4: Persistent 20-Template Round Robin Rotation", BASE_DIR / "diagrams" / "fig4_round_robin_scheduler.png",
         "Visualizes the cyclic sequence across 20 distinct ATS resume layouts (T01 to T20) with atomic cursor state tracking in round_robin_state.json and thread-safe concurrency locks."),
        ("Figure 5: Certification Preservation Pipeline", BASE_DIR / "diagrams" / "fig5_certification_preservation.png",
         "Shows how candidate-earned industry certifications from the original resume are parsed, structured, isolated from LLM dropping, validated, and guaranteed to appear in both DOCX and PDF documents.")
    ]

    for fig_title, fig_file, explanation in figures:
        p = pdf_doc.new_page(width=595.28, height=841.89)
        p.draw_rect(fitz.Rect(0, 0, 595.28, 12), color=None, fill=(0.06, 0.25, 0.72))
        
        # Section Title
        p.insert_text(fitz.Point(54, 55), "FUTRSEC TECHNICAL SPECIFICATION & ARCHITECTURAL VISUALS", fontsize=11, fontname="helv", color=(0.06, 0.25, 0.72))
        p.draw_line(fitz.Point(54, 65), fitz.Point(541, 65), color=(0.8, 0.83, 0.88), width=1.0)
        
        p.insert_text(fitz.Point(54, 90), fig_title, fontsize=13, fontname="helv", color=(0.06, 0.09, 0.16))

        # Insert Figure Image
        if fig_file.exists():
            p.insert_image(fitz.Rect(54, 110, 541, 580), filename=str(fig_file))

        # Explanation Box
        p.draw_rect(fitz.Rect(54, 600, 541, 740), color=(0.8, 0.83, 0.88), fill=(0.96, 0.97, 0.98), width=1.0)
        p.insert_text(fitz.Point(68, 625), "Technical Diagram Explanation & Architectural Context:", fontsize=10, fontname="helv", color=(0.06, 0.25, 0.72))
        
        # Wrap explanation text
        words = explanation.split()
        lines = []
        curr = ""
        for w in words:
            if len(curr + " " + w) > 85:
                lines.append(curr)
                curr = w
            else:
                curr = curr + " " + w if curr else w
        if curr:
            lines.append(curr)

        ey = 650
        for l in lines:
            p.insert_text(fitz.Point(68, ey), l, fontsize=9.0, fontname="helv", color=(0.2, 0.25, 0.35))
            ey += 18

        # Footer
        p.draw_line(fitz.Point(54, 790), fitz.Point(541, 790), color=(0.8, 0.83, 0.88), width=0.8)
        p.insert_text(fitz.Point(54, 805), "FUTRSEC Cyber Operations | Technical Architecture & System Specification", fontsize=8, fontname="helv", color=(0.4, 0.45, 0.55))
        p.insert_text(fitz.Point(500, 805), f"Page {pdf_doc.page_count}", fontsize=8, fontname="helv", color=(0.4, 0.45, 0.55))

    pdf_doc.save(str(PDF_OUT))
    pdf_doc.close()
    print(f"Generated PDF Report at: {PDF_OUT}")


if __name__ == "__main__":
    build_docx_report()
    build_pdf_report()
    print("Compilation of technical report documents completed.")

