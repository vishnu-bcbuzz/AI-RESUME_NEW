"""Automated tests for resume content generator and document renderer."""

from pathlib import Path
import pytest
from app.projects.generator import ResumeContentGenerator
from app.reports.templates import template_registry
from app.reports.renderer import DocumentRenderer
from app.resume.extractor import ParsedResumeData, ContactInfo, ProjectEntry, EducationEntry


@pytest.fixture
def sample_resume():
    return ParsedResumeData(
        candidate_name="Diana Prince",
        contact_info=ContactInfo(email="diana@sec.io", phone="+1 555-4321", location="Washington, DC"),
        career_objective="Security Architect seeking Cloud Security Engineer position.",
        technical_skills=["AWS Security", "Kubernetes", "Terraform", "Python", "Linux", "IAM"],
        education=[EducationEntry(degree="Bachelor of Engineering", institution="Themyscira Tech", graduation_year="2021")],
        certifications=["AWS Certified Security - Specialty"],
        projects=[
            ProjectEntry(
                title="Multi-Cloud IAM Auditor",
                description="Built automated auditing tool to detect overprivileged IAM roles across AWS accounts.",
                technologies=["Python", "AWS", "Boto3"],
            )
        ],
    )


def test_generator_preserves_facts(sample_resume):
    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=sample_resume,
        target_role_name="Cloud Security Engineer",
        missing_core_skills=["CIS Benchmarks"],
    )
    assert enhanced.candidate_name == "Diana Prince"
    assert "diana@sec.io" in enhanced.contact_header
    assert len(enhanced.certifications) == 1
    assert "AWS Certified Security - Specialty" in enhanced.certifications
    assert len(enhanced.pending_confirmations) > 0


def test_render_all_templates(sample_resume):
    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=sample_resume,
        target_role_name="Cloud Security Engineer",
        missing_core_skills=[],
    )

    templates = template_registry.list_templates(active_only=True)
    assert len(templates) == 30, f"Expected 30 templates, got {len(templates)}"

    for tmpl in templates:
        rendered = DocumentRenderer.render_resume(
            content=enhanced,
            template=tmpl,
            job_id=f"test_render_{tmpl.template_id}",
        )
        assert Path(rendered["docx_path"]).exists()
        assert Path(rendered["docx_path"]).stat().st_size > 5000  # valid DOCX
        if rendered["pdf_available"]:
            assert Path(rendered["pdf_path"]).exists()
            assert Path(rendered["pdf_path"]).stat().st_size > 1000  # valid PDF


def test_clickable_email_in_docx(sample_resume):
    from docx import Document as DocxDocument
    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=sample_resume,
        target_role_name="Cloud Security Engineer",
        missing_core_skills=[],
    )
    tmpl = template_registry.get_template("T01")
    rendered = DocumentRenderer.render_resume(enhanced, tmpl, job_id="test_email_docx")
    docx_file = Path(rendered["docx_path"])
    assert docx_file.exists()

    doc = DocxDocument(str(docx_file))
    # 1. Verify external relationship targets mailto:
    hyperlink_targets = [
        rel.target_ref for rel in doc.part.rels.values()
        if "hyperlink" in rel.reltype
    ]
    assert any("mailto:diana@sec.io" in target for target in hyperlink_targets)

    # 2. Verify paragraph XML contains w:hyperlink and w:color val="0044CC"
    found_email_hyperlink = False
    for p in doc.paragraphs:
        xml_str = p._p.xml
        if "mailto:diana@sec.io" in xml_str or "diana@sec.io" in xml_str:
            if "w:hyperlink" in xml_str and "0044CC" in xml_str:
                found_email_hyperlink = True
                break
    assert found_email_hyperlink is True


def test_clickable_email_in_pdf(sample_resume):
    import fitz
    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=sample_resume,
        target_role_name="Cloud Security Engineer",
        missing_core_skills=[],
    )
    tmpl = template_registry.get_template("T01")
    rendered = DocumentRenderer.render_resume(enhanced, tmpl, job_id="test_email_pdf")
    assert rendered["pdf_available"] is True
    pdf_file = Path(rendered["pdf_path"])
    assert pdf_file.exists()

    doc = fitz.open(str(pdf_file))
    first_page = doc[0]
    links = first_page.get_links()
    assert len(links) > 0

    mailto_links = [lnk["uri"] for lnk in links if lnk.get("uri") == "mailto:diana@sec.io"]
    assert len(mailto_links) >= 1
    doc.close()


def test_separate_skills_and_projects_and_no_blank_pages(sample_resume):
    import fitz
    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=sample_resume,
        target_role_name="Cloud Security Engineer",
        missing_core_skills=[],
    )
    tmpl = template_registry.get_template("T01")
    rendered = DocumentRenderer.render_resume(enhanced, tmpl, job_id="test_sections_quality")

    # Verify PDF pages are non-empty
    doc = fitz.open(str(rendered["pdf_path"]))
    for p in doc:
        text = p.get_text()
        assert len(text.strip()) > 0  # No blank pages
    all_text = "\n".join([p.get_text() for p in doc])
    assert "TECHNICAL SKILLS" in all_text
    assert "PROJECTS" in all_text
    doc.close()
