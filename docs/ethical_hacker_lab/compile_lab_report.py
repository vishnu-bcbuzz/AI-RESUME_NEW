"""Compiles docs/ethical_hacker_lab/WEB_APP_SECURITY_TESTING_REPORT.md and embedded figures into a professional, publication-quality DOCX and vector PDF report."""

import os
import re
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import fitz

BASE_DIR = Path("V:/ai_jobagent/docs/ethical_hacker_lab")
MD_PATH = BASE_DIR / "WEB_APP_SECURITY_TESTING_REPORT.md"
DOCX_OUT = BASE_DIR / "Web_Application_Security_Testing_Lab_Technical_Report.docx"
PDF_OUT = BASE_DIR / "Web_Application_Security_Testing_Lab_Technical_Report.pdf"

# Color Palette (Cybersecurity Theme)
COLOR_PRIMARY = RGBColor(15, 23, 42)      # Slate 900
COLOR_SECONDARY = RGBColor(185, 28, 28)   # Red 700 (Ethical Hacker Accent)
COLOR_TEXT = RGBColor(51, 65, 85)         # Slate 700
COLOR_MUTED = RGBColor(100, 116, 139)     # Slate 500


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
    run_t = p_title.add_run("WEB APPLICATION SECURITY TESTING LAB & VULNERABILITY REMEDIATION")
    run_t.font.name = "Calibri"
    run_t.font.size = Pt(26)
    run_t.font.bold = True
    run_t.font.color.rgb = COLOR_SECONDARY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = p_sub.add_run("Technical Security Assessment Report & Vulnerability Remediation Architecture")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(13)
    run_sub.font.color.rgb = COLOR_PRIMARY
    run_sub.font.bold = True
    p_sub.paragraph_format.space_after = Pt(16)

    p_desc = doc.add_paragraph()
    p_desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_desc = p_desc.add_run(
        "Domain: Cybersecurity  |  Role: Ethical Hacker  |  Difficulty: Intermediate\n"
        "Platform: Local Isolated Web Testing Environment (Docker Desktop)"
    )
    run_desc.font.name = "Calibri"
    run_desc.font.size = Pt(10.5)
    run_desc.font.italic = True
    run_desc.font.color.rgb = COLOR_MUTED
    p_desc.paragraph_format.space_after = Pt(40)

    # Metadata table on cover page
    tbl = doc.add_table(rows=6, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta = [
        ("Project Title:", "Web Application Security Testing Lab & Vulnerability Remediation"),
        ("Domain & Role:", "Cybersecurity  |  Ethical Hacker (Penetration Tester)"),
        ("Target Platform:", "Docker Desktop (OWASP Juice Shop / DVWA on 127.0.0.1)"),
        ("Core Tooling:", "Burp Suite Community, Nmap, Python 3, Chromium Browser"),
        ("Scoring Standard:", "FIRST Common Vulnerability Scoring System (CVSS v3.1)"),
        ("Report Date:", "October 2026 | Technical Assessment Plan & Verification Deliverable"),
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

        # Code block
        if sline.startswith("```"):
            continue

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
            # Image Embed: ![Caption](filename.png)
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
    pdf_doc = fitz.open()

    # Cover Page
    page = pdf_doc.new_page(width=595.28, height=841.89)  # A4 pt
    
    # Top Accent Bar (Red / Ethical Hacker Theme)
    page.draw_rect(fitz.Rect(0, 0, 595.28, 12), color=None, fill=(0.72, 0.11, 0.11))

    # Title & Subtitle
    page.insert_text(fitz.Point(54, 100), "WEB APPLICATION SECURITY TESTING LAB", fontsize=21, fontname="helv", color=(0.72, 0.11, 0.11))
    page.insert_text(fitz.Point(54, 124), "& VULNERABILITY REMEDIATION", fontsize=21, fontname="helv", color=(0.72, 0.11, 0.11))
    page.insert_text(fitz.Point(54, 148), "Technical Security Assessment Report & Vulnerability Remediation Architecture", fontsize=12, fontname="helv", color=(0.06, 0.09, 0.16))
    page.insert_text(fitz.Point(54, 168), "Domain: Cybersecurity  |  Role: Ethical Hacker  |  Difficulty Level: Intermediate", fontsize=9.5, fontname="helv", color=(0.4, 0.45, 0.55))

    page.draw_line(fitz.Point(54, 180), fitz.Point(541, 180), color=(0.8, 0.83, 0.88), width=1.0)

    # Insert Architecture on Cover Page
    arch_path = BASE_DIR / "fig2_system_architecture_lab.png"
    if arch_path.exists():
        page.insert_image(fitz.Rect(54, 195, 541, 530), filename=str(arch_path))

    # Metadata Box
    page.draw_rect(fitz.Rect(54, 550, 541, 740), color=(0.8, 0.83, 0.88), fill=(0.96, 0.97, 0.98), width=1.0)
    meta_y = 575
    metadata = [
        ("Project Title:", "Web Application Security Testing Lab & Vulnerability Remediation"),
        ("Candidate Role:", "Ethical Hacker / Web Application Penetration Tester"),
        ("Target Environment:", "Docker Desktop Container (OWASP Juice Shop / DVWA on 127.0.0.1)"),
        ("Assessment Tooling:", "Burp Suite Community, Nmap Scanner, Python 3, Chromium Proxy"),
        ("Scoring Metric:", "Common Vulnerability Scoring System (CVSS v3.1 Base Metrics)"),
        ("Assessment Scope:", "Strictly Confined to Local Authorized Target (127.0.0.1)"),
        ("Verification Status:", "Executed & Verified Test Cases Documented"),
    ]
    for lbl, val in metadata:
        page.insert_text(fitz.Point(70, meta_y), lbl, fontsize=9.0, fontname="helv", color=(0.72, 0.11, 0.11))
        page.insert_text(fitz.Point(195, meta_y), val, fontsize=8.5, fontname="helv", color=(0.2, 0.25, 0.35))
        meta_y += 22

    # Footer
    page.draw_line(fitz.Point(54, 790), fitz.Point(541, 790), color=(0.8, 0.83, 0.88), width=0.8)
    page.insert_text(fitz.Point(54, 805), "FUTRSEC Ethical Hacker Lab | Web Application Security Assessment Report", fontsize=8, fontname="helv", color=(0.4, 0.45, 0.55))
    page.insert_text(fitz.Point(510, 805), "Page 1", fontsize=8, fontname="helv", color=(0.4, 0.45, 0.55))

    # Pages 2+: Integrated Diagrams & Context
    figures = [
        ("Figure 1: Complete Project Workflow Flowchart", BASE_DIR / "fig1_project_workflow_flowchart.png",
         "Depicts the complete execution workflow including Phase 1 (Lab Setup & Docker Isolation), Phase 2 (Nmap & Burp Reconnaissance), Phase 3 (Vulnerability Discovery), the critical Verification Decision Node with Evidence Review loop, and Phase 4 (CVSS Scoring & Remediation Reporting)."),
        ("Figure 3: Structured Vulnerability Assessment & Remediation Cycle", BASE_DIR / "fig3_vulnerability_verification_cycle.png",
         "Illustrates the closed-loop methodology from attack surface mapping to targeted vulnerability probing (SQLi, XSS, IDOR), automated proof-of-concept verification with Python, CVSS v3.1 scoring, and developer code remediation.")
    ]

    for fig_title, fig_file, explanation in figures:
        p = pdf_doc.new_page(width=595.28, height=841.89)
        p.draw_rect(fitz.Rect(0, 0, 595.28, 12), color=None, fill=(0.72, 0.11, 0.11))
        
        # Section Title
        p.insert_text(fitz.Point(54, 55), "FUTRSEC SECURITY ASSESSMENT SPECIFICATION & WORKFLOW VISUALS", fontsize=10.5, fontname="helv", color=(0.72, 0.11, 0.11))
        p.draw_line(fitz.Point(54, 65), fitz.Point(541, 65), color=(0.8, 0.83, 0.88), width=1.0)
        
        p.insert_text(fitz.Point(54, 90), fig_title, fontsize=13, fontname="helv", color=(0.06, 0.09, 0.16))

        # Insert Figure Image
        if fig_file.exists():
            p.insert_image(fitz.Rect(54, 110, 541, 620), filename=str(fig_file))

        # Explanation Box
        p.draw_rect(fitz.Rect(54, 635, 541, 755), color=(0.8, 0.83, 0.88), fill=(0.96, 0.97, 0.98), width=1.0)
        p.insert_text(fitz.Point(68, 655), "Assessment Methodology & Architectural Context:", fontsize=10, fontname="helv", color=(0.72, 0.11, 0.11))
        
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

        ey = 678
        for l in lines:
            p.insert_text(fitz.Point(68, ey), l, fontsize=9.0, fontname="helv", color=(0.2, 0.25, 0.35))
            ey += 18

        # Footer
        p.draw_line(fitz.Point(54, 790), fitz.Point(541, 790), color=(0.8, 0.83, 0.88), width=0.8)
        p.insert_text(fitz.Point(54, 805), "FUTRSEC Ethical Hacker Lab | Web Application Security Assessment Report", fontsize=8, fontname="helv", color=(0.4, 0.45, 0.55))
        p.insert_text(fitz.Point(500, 805), f"Page {pdf_doc.page_count}", fontsize=8, fontname="helv", color=(0.4, 0.45, 0.55))

    pdf_doc.save(str(PDF_OUT))
    pdf_doc.close()
    print(f"Generated PDF Report at: {PDF_OUT}")


if __name__ == "__main__":
    build_docx_report()
    build_pdf_report()
    print("Compilation of Ethical Hacker Lab technical report documents completed.")

