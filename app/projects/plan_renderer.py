"""Document renderer for Project Implementation Plans in DOCX and PDF formats.

Generates:
1. Editable DOCX document via python-docx
2. Professional PDF document via PyMuPDF (fitz)
Adheres strictly to student-accessible, structured formatting with sections A through J.
Does not transmit unnecessary candidate personal data into project documents.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Tuple
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
import fitz  # PyMuPDF

from app.config import settings
from app.projects.plan_generator import ProjectImplementationPlan

logger = logging.getLogger("futrsec.plan_renderer")


class ProjectPlanDocumentRenderer:
    """Renders comprehensive project implementation plans into editable DOCX and PDF files."""

    PRIMARY_COLOR = RGBColor(26, 54, 93)     # #1A365D Deep Navy
    SECONDARY_COLOR = RGBColor(74, 85, 104)  # #4A5568 Slate Gray
    TEXT_COLOR = RGBColor(45, 55, 72)        # #2D3748 Dark Charcoal
    ACCENT_GREEN = RGBColor(16, 185, 129)    # #10B981 Emerald
    BORDER_COLOR = "CBD5E0"

    @classmethod
    def render_plan_documents(
        cls,
        plan: ProjectImplementationPlan,
    ) -> Dict[str, Any]:
        """Renders both DOCX and PDF documents for a project implementation plan."""
        settings.PROJECT_PLANS_DIR.mkdir(parents=True, exist_ok=True)
        docx_path = settings.PROJECT_PLANS_DIR / f"{plan.plan_id}.docx"
        pdf_path = settings.PROJECT_PLANS_DIR / f"{plan.plan_id}.pdf"

        # 1. Render DOCX
        cls._render_docx(plan, docx_path)

        # 2. Render PDF via PyMuPDF
        pdf_success = False
        pdf_note = ""
        try:
            cls._render_pdf(plan, pdf_path)
            pdf_success = True
            pdf_note = "Implementation plan PDF generated successfully via PyMuPDF."
        except Exception as exc:
            logger.warning("Could not generate implementation plan PDF: %s", exc)
            pdf_note = f"PDF generation limitation: {exc}. Primary DOCX format provided."

        return {
            "plan_id": plan.plan_id,
            "project_title": plan.overview.project_title,
            "docx_path": str(docx_path),
            "docx_filename": docx_path.name,
            "docx_url": f"/api/projects/download-plan/{plan.plan_id}/docx",
            "pdf_path": str(pdf_path) if pdf_success else None,
            "pdf_filename": pdf_path.name if pdf_success else None,
            "pdf_url": f"/api/projects/download-plan/{plan.plan_id}/pdf" if pdf_success else None,
            "pdf_available": pdf_success,
            "pdf_status_note": pdf_note,
        }

    @classmethod
    def _add_section_heading(cls, doc: Document, text: str):
        """Adds a standard styled section heading with a bottom border."""
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = cls.PRIMARY_COLOR

        pPr = p._p.get_or_add_pPr()
        pBdr = parse_xml(
            f'<w:pBdr {nsdecls("w")}>'
            f'<w:bottom w:val="single" w:sz="6" w:space="3" w:color="{cls.BORDER_COLOR}"/>'
            f'</w:pBdr>'
        )
        pPr.append(pBdr)

    @classmethod
    def _render_docx(cls, plan: ProjectImplementationPlan, output_path: Path) -> None:
        """Constructs an editable, well-formatted DOCX implementation plan."""
        doc = Document()

        # Set page margins: 0.75 in
        for section in doc.sections:
            section.top_margin = Inches(0.75)
            section.bottom_margin = Inches(0.75)
            section.left_margin = Inches(0.75)
            section.right_margin = Inches(0.75)

        # Title Block
        p_title = doc.add_paragraph()
        p_title.paragraph_format.space_before = Pt(0)
        p_title.paragraph_format.space_after = Pt(2)
        r_title = p_title.add_run(plan.overview.project_title)
        r_title.font.name = "Calibri"
        r_title.font.size = Pt(18)
        r_title.font.bold = True
        r_title.font.color.rgb = cls.PRIMARY_COLOR

        # Subtitle / Metadata
        p_sub = doc.add_paragraph()
        p_sub.paragraph_format.space_before = Pt(0)
        p_sub.paragraph_format.space_after = Pt(12)
        r_sub = p_sub.add_run(
            f"FUTRSEC Project Implementation Plan  |  Target Role: {plan.overview.target_role}  |  "
            f"Difficulty: {plan.overview.difficulty}  |  Date: {plan.generated_date}"
        )
        r_sub.font.name = "Calibri"
        r_sub.font.size = Pt(10)
        r_sub.font.bold = True
        r_sub.font.color.rgb = cls.SECONDARY_COLOR

        # -------------------------------------------------------------
        # Section A: Project Overview
        # -------------------------------------------------------------
        cls._add_section_heading(doc, "A. Project Overview")
        p_prob = doc.add_paragraph()
        p_prob.paragraph_format.space_before = Pt(3)
        p_prob.paragraph_format.space_after = Pt(4)
        r = p_prob.add_run("Problem Statement: ")
        r.bold = True
        p_prob.add_run(plan.overview.problem_statement)

        p_obj = doc.add_paragraph()
        p_obj.paragraph_format.space_before = Pt(3)
        p_obj.paragraph_format.space_after = Pt(4)
        r = p_obj.add_run("Project Objective: ")
        r.bold = True
        p_obj.add_run(plan.overview.project_objective)

        p_rel = doc.add_paragraph()
        p_rel.paragraph_format.space_before = Pt(3)
        p_rel.paragraph_format.space_after = Pt(4)
        r = p_rel.add_run("Relevance to Role: ")
        r.bold = True
        p_rel.add_run(plan.overview.relevance_to_role)

        if plan.overview.weaknesses_addressed:
            p_weak = doc.add_paragraph()
            p_weak.paragraph_format.space_before = Pt(3)
            p_weak.paragraph_format.space_after = Pt(2)
            r = p_weak.add_run("Weaknesses Addressed:")
            r.bold = True
            for w in plan.overview.weaknesses_addressed:
                p_bullet = doc.add_paragraph(style="List Bullet")
                p_bullet.paragraph_format.space_before = Pt(1)
                p_bullet.paragraph_format.space_after = Pt(2)
                p_bullet.add_run(w)

        # -------------------------------------------------------------
        # Section B: Skills to Be Demonstrated
        # -------------------------------------------------------------
        cls._add_section_heading(doc, "B. Skills to Be Demonstrated")
        p_skills_exist = doc.add_paragraph()
        p_skills_exist.paragraph_format.space_before = Pt(3)
        p_skills_exist.paragraph_format.space_after = Pt(2)
        r = p_skills_exist.add_run("Existing Skills Applied: ")
        r.bold = True
        p_skills_exist.add_run(", ".join(plan.skills.existing_skills_applied))

        p_skills_learn = doc.add_paragraph()
        p_skills_learn.paragraph_format.space_before = Pt(3)
        p_skills_learn.paragraph_format.space_after = Pt(4)
        r = p_skills_learn.add_run("Skills You Will Learn / Demonstrate: ")
        r.bold = True
        p_skills_learn.add_run(", ".join(plan.skills.skills_to_be_learned))

        # -------------------------------------------------------------
        # Section C: Technology Stack
        # -------------------------------------------------------------
        cls._add_section_heading(doc, "C. Technology Stack")
        for tech, desc in plan.technology_details.items():
            p_tech = doc.add_paragraph(style="List Bullet")
            p_tech.paragraph_format.space_before = Pt(1)
            p_tech.paragraph_format.space_after = Pt(2)
            r = p_tech.add_run(f"{tech}: ")
            r.bold = True
            p_tech.add_run(desc)

        # -------------------------------------------------------------
        # Section D: Implementation Phases
        # -------------------------------------------------------------
        cls._add_section_heading(doc, "D. Implementation Phases")
        for phase in plan.phases:
            p_ph_head = doc.add_paragraph()
            p_ph_head.paragraph_format.space_before = Pt(8)
            p_ph_head.paragraph_format.space_after = Pt(2)
            r_ph = p_ph_head.add_run(f"Phase {phase.phase_number}: {phase.title}")
            r_ph.bold = True
            r_ph.font.size = Pt(11.5)
            r_ph.font.color.rgb = cls.PRIMARY_COLOR

            p_ph_obj = doc.add_paragraph()
            p_ph_obj.paragraph_format.space_before = Pt(1)
            p_ph_obj.paragraph_format.space_after = Pt(2)
            r = p_ph_obj.add_run("Objective: ")
            r.bold = True
            p_ph_obj.add_run(phase.objective)

            p_tasks_lbl = doc.add_paragraph()
            p_tasks_lbl.paragraph_format.space_before = Pt(2)
            p_tasks_lbl.paragraph_format.space_after = Pt(1)
            r = p_tasks_lbl.add_run("Step-by-Step Tasks:")
            r.bold = True

            for task in phase.tasks:
                p_task = doc.add_paragraph(style="List Bullet")
                p_task.paragraph_format.space_before = Pt(1)
                p_task.paragraph_format.space_after = Pt(1)
                p_task.add_run(task)

            p_ph_out = doc.add_paragraph()
            p_ph_out.paragraph_format.space_before = Pt(2)
            p_ph_out.paragraph_format.space_after = Pt(1)
            r = p_ph_out.add_run("Expected Output: ")
            r.bold = True
            p_ph_out.add_run(phase.expected_output)

            p_ph_ver = doc.add_paragraph()
            p_ph_ver.paragraph_format.space_before = Pt(1)
            p_ph_ver.paragraph_format.space_after = Pt(4)
            r = p_ph_ver.add_run("Verification / Testing Method: ")
            r.bold = True
            p_ph_ver.add_run(phase.verification_method)

        # -------------------------------------------------------------
        # Section E: Project Structure
        # -------------------------------------------------------------
        cls._add_section_heading(doc, "E. Project Structure")
        p_struct_intro = doc.add_paragraph()
        p_struct_intro.paragraph_format.space_after = Pt(3)
        p_struct_intro.add_run("Recommended repository folder layout and purpose of key files:")

        for item in plan.project_structure:
            p_item = doc.add_paragraph(style="List Bullet")
            p_item.paragraph_format.space_before = Pt(1)
            p_item.paragraph_format.space_after = Pt(2)
            r = p_item.add_run(f"`{item.path}`: ")
            r.bold = True
            p_item.add_run(item.description)

        # -------------------------------------------------------------
        # Section F: Final Deliverables
        # -------------------------------------------------------------
        cls._add_section_heading(doc, "F. Final Deliverables")
        for d in plan.final_deliverables:
            p_del = doc.add_paragraph(style="List Bullet")
            p_del.paragraph_format.space_before = Pt(1)
            p_del.paragraph_format.space_after = Pt(2)
            p_del.add_run(d)

        # -------------------------------------------------------------
        # Section G: Testing and Validation
        # -------------------------------------------------------------
        cls._add_section_heading(doc, "G. Testing and Validation")
        for t in plan.testing_and_validation:
            p_test = doc.add_paragraph(style="List Bullet")
            p_test.paragraph_format.space_before = Pt(1)
            p_test.paragraph_format.space_after = Pt(2)
            p_test.add_run(t)

        # -------------------------------------------------------------
        # Section H: Expected Learning Outcomes
        # -------------------------------------------------------------
        cls._add_section_heading(doc, "H. Expected Learning Outcomes")
        for lo in plan.learning_outcomes:
            p_lo = doc.add_paragraph(style="List Bullet")
            p_lo.paragraph_format.space_before = Pt(1)
            p_lo.paragraph_format.space_after = Pt(2)
            p_lo.add_run(lo)

        # -------------------------------------------------------------
        # Section I: Resume Documentation Guide
        # -------------------------------------------------------------
        cls._add_section_heading(doc, "I. Resume Documentation Guide")
        p_guide_info = doc.add_paragraph()
        p_guide_info.paragraph_format.space_after = Pt(3)
        r = p_guide_info.add_run(f"Bullet Structure Framework: ")
        r.bold = True
        p_guide_info.add_run(plan.resume_documentation_guide.framework)

        p_ex_lbl = doc.add_paragraph()
        p_ex_lbl.paragraph_format.space_before = Pt(2)
        p_ex_lbl.paragraph_format.space_after = Pt(2)
        r = p_ex_lbl.add_run("Example Bullet Points (Use only after completing the actual work):")
        r.bold = True

        for b in plan.resume_documentation_guide.sample_bullets:
            p_bullet = doc.add_paragraph(style="List Bullet")
            p_bullet.paragraph_format.space_before = Pt(1)
            p_bullet.paragraph_format.space_after = Pt(2)
            p_bullet.add_run(b)

        p_gn = doc.add_paragraph()
        p_gn.paragraph_format.space_before = Pt(3)
        p_gn.paragraph_format.space_after = Pt(4)
        r = p_gn.add_run("Integrity Policy: ")
        r.bold = True
        p_gn.add_run(plan.resume_documentation_guide.guidance_notes)

        # -------------------------------------------------------------
        # Section J: GitHub and Presentation
        # -------------------------------------------------------------
        cls._add_section_heading(doc, "J. GitHub and Presentation")
        for g in plan.github_and_presentation:
            p_gh = doc.add_paragraph(style="List Bullet")
            p_gh.paragraph_format.space_before = Pt(1)
            p_gh.paragraph_format.space_after = Pt(2)
            p_gh.add_run(g)

        doc.save(str(output_path))
        logger.info("Saved project implementation plan DOCX to %s", output_path)

    @classmethod
    def _render_pdf(cls, plan: ProjectImplementationPlan, output_path: Path) -> None:
        """Renders corresponding clean PDF implementation plan using PyMuPDF (fitz)."""
        doc = fitz.open()
        page = doc.new_page(width=612, height=792)  # Standard Letter

        margin_left = 45.0
        margin_right = 567.0
        max_y = 740.0
        current_y = 48.0

        primary_color = (26 / 255.0, 54 / 255.0, 93 / 255.0)
        secondary_color = (74 / 255.0, 85 / 255.0, 104 / 255.0)

        def check_page_break(needed_space: float = 30.0):
            nonlocal current_y, page
            if current_y + needed_space > max_y:
                page = doc.new_page(width=612, height=792)
                current_y = 48.0

        # Title
        page.insert_text(
            fitz.Point(margin_left, current_y),
            plan.overview.project_title[:70],
            fontsize=15.0,
            fontname="helv",
            color=primary_color,
        )
        current_y += 18.0

        # Subtitle
        sub_line = (
            f"FUTRSEC Project Plan  |  Role: {plan.overview.target_role}  |  "
            f"Difficulty: {plan.overview.difficulty}  |  Date: {plan.generated_date}"
        )
        page.insert_text(
            fitz.Point(margin_left, current_y),
            sub_line[:90],
            fontsize=8.5,
            fontname="helv",
            color=secondary_color,
        )
        current_y += 12.0

        # Divider
        page.draw_line(
            fitz.Point(margin_left, current_y),
            fitz.Point(margin_right, current_y),
            color=primary_color,
            width=1.0,
        )
        current_y += 16.0

        def add_pdf_section_header(title: str):
            nonlocal current_y
            check_page_break(25.0)
            page.insert_text(
                fitz.Point(margin_left, current_y),
                title.upper(),
                fontsize=10.5,
                fontname="helv",
                color=primary_color,
            )
            current_y += 4.0
            page.draw_line(
                fitz.Point(margin_left, current_y),
                fitz.Point(margin_right, current_y),
                color=(0.8, 0.85, 0.9),
                width=0.5,
            )
            current_y += 12.0

        def add_pdf_wrapped_text(text: str, prefix: str = "", font_size: float = 8.5):
            nonlocal current_y
            check_page_break(20.0)
            full_text = f"{prefix}{text}"
            rect = fitz.Rect(margin_left, current_y, margin_right, current_y + 40.0)
            rc = page.insert_textbox(rect, full_text, fontsize=font_size, fontname="helv")
            current_y += max(14.0, (len(full_text) // 90 + 1) * 11.0)

        # Section A: Overview
        add_pdf_section_header("A. Project Overview")
        add_pdf_wrapped_text(plan.overview.project_objective, "Objective: ")
        add_pdf_wrapped_text(plan.overview.problem_statement, "Problem: ")
        add_pdf_wrapped_text(plan.overview.relevance_to_role, "Relevance: ")
        current_y += 6.0

        # Section B: Skills
        add_pdf_section_header("B. Skills to Be Demonstrated")
        add_pdf_wrapped_text(", ".join(plan.skills.existing_skills_applied), "Existing Applied: ")
        add_pdf_wrapped_text(", ".join(plan.skills.skills_to_be_learned), "Skills to Learn: ")
        current_y += 6.0

        # Section C: Tech Stack
        add_pdf_section_header("C. Technology Stack")
        for tech, desc in list(plan.technology_details.items())[:5]:
            add_pdf_wrapped_text(f"{tech}: {desc}", "• ")
        current_y += 6.0

        # Section D: Phases
        add_pdf_section_header("D. Implementation Phases")
        for phase in plan.phases:
            check_page_break(35.0)
            page.insert_text(
                fitz.Point(margin_left, current_y),
                f"Phase {phase.phase_number}: {phase.title}",
                fontsize=9.5,
                fontname="helv",
                color=primary_color,
            )
            current_y += 12.0
            add_pdf_wrapped_text(phase.objective, "  Objective: ")
            for t in phase.tasks[:3]:
                add_pdf_wrapped_text(t, "    - ")
            add_pdf_wrapped_text(phase.expected_output, "  Output: ")
            current_y += 4.0

        # Section E: Deliverables & Testing
        add_pdf_section_header("E. Final Deliverables & Safe Testing")
        for d in plan.final_deliverables[:4]:
            add_pdf_wrapped_text(d, "• Deliverable: ")
        for t in plan.testing_and_validation[:2]:
            add_pdf_wrapped_text(t, "• Testing Policy: ")
        current_y += 6.0

        # Section F: Resume Guide
        add_pdf_section_header("F. Resume Documentation Guide")
        for b in plan.resume_documentation_guide.sample_bullets:
            add_pdf_wrapped_text(b, "• Sample Bullet: ")
        add_pdf_wrapped_text(plan.resume_documentation_guide.guidance_notes, "Note: ")

        doc.save(str(output_path))
        doc.close()
        logger.info("Saved project implementation plan PDF to %s", output_path)
