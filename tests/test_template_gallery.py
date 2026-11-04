"""Tests for the Resume Template Gallery, template inspection, sample candidate previews,
and strict preservation of the automatic Round Robin scheduling system.
"""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.reports.templates import template_registry
from app.reports.round_robin import round_robin_scheduler


@pytest.fixture
def client():
    return TestClient(app)


def test_template_registry_count_and_uniqueness():
    """Verify that exactly 30 distinct templates exist in the registry with unique IDs and names."""
    templates = template_registry.list_templates(active_only=False)
    assert len(templates) == 30, f"Expected exactly 30 templates, found {len(templates)}"

    template_ids = [t.template_id for t in templates]
    template_names = [t.template_name for t in templates]

    # Verify ID uniqueness
    assert len(set(template_ids)) == 30, "Template IDs must all be unique"
    # Verify Name uniqueness
    assert len(set(template_names)) == 30, "Template names must all be unique"

    # Verify ID range T01 to T30
    expected_ids = [f"T{i:02d}" for i in range(1, 31)]
    assert sorted(template_ids) == sorted(expected_ids)

    for t in templates:
        assert t.template_name, f"Template {t.template_id} must have a name"
        assert t.description, f"Template {t.template_id} must have a description"
        assert t.style_config, f"Template {t.template_id} must have a style_config"
        cfg = t.style_config
        assert "font_family" in cfg
        assert "header_alignment" in cfg
        assert "section_order" in cfg
        assert cfg["section_order"] == ["summary", "skills", "projects", "certifications", "experience", "education"]


def test_api_list_templates(client):
    """Verify the /api/templates endpoint reports all 30 templates."""
    res = client.get("/api/templates")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 30
    assert len(data["templates"]) == 30

    ids = [t["template_id"] for t in data["templates"]]
    assert len(set(ids)) == 30


def test_api_template_detail_and_404(client):
    """Verify retrieval of single template details and proper 404 for invalid ID."""
    res = client.get("/api/templates/T01")
    assert res.status_code == 200
    data = res.json()
    assert data["template_id"] == "T01"
    assert data["template_name"] == "Professional Classic"

    res_invalid = client.get("/api/templates/T99")
    assert res_invalid.status_code == 404


def test_template_preview_contains_all_required_sections(client):
    """Verify template preview displays sample candidate info covering all required sections:

    - Header and contact details
    - Professional summary
    - Technical skills
    - Projects
    - Work experience
    - Education
    - Certifications
    """
    res = client.get("/api/templates/T02/preview")
    assert res.status_code == 200
    data = res.json()

    assert data["template"]["template_id"] == "T02"
    sample = data["sample_content"]

    # 1. Header and contact details
    assert sample["candidate_name"]
    assert sample["contact_header"]
    assert sample["contact_details"]["email"]
    assert sample["contact_details"]["phone"]
    assert sample["contact_details"]["location"]

    # 2. Professional summary
    assert sample["professional_summary"]
    assert len(sample["professional_summary"].split()) >= 30

    # 3. Technical skills
    skills_grouped = sample["technical_skills_grouped"]
    assert len(skills_grouped) >= 3
    assert "Cybersecurity Tools" in skills_grouped

    # 4. Projects
    projects = sample["projects"]
    assert len(projects) >= 1
    assert "title" in projects[0]
    assert "description" in projects[0]
    assert "technologies" in projects[0]

    # 5. Work experience
    experience = sample["experience"]
    assert len(experience) >= 1
    assert "job_title" in experience[0]
    assert "company" in experience[0]
    assert len(experience[0]["responsibilities"]) >= 2

    # 6. Education
    education = sample["education"]
    assert len(education) >= 1
    assert "degree" in education[0]
    assert "institution" in education[0]

    # 7. Certifications
    certs = sample["certifications"]
    assert len(certs) >= 2


def test_template_preview_streams_pdf_and_docx(client):
    """Verify that PDF and DOCX preview streams return valid binary documents."""
    # PDF preview stream
    res_pdf = client.get("/api/templates/T03/preview/pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert res_pdf.content.startswith(b"%PDF-")
    assert len(res_pdf.content) > 2000

    # DOCX preview stream
    res_docx = client.get("/api/templates/T03/preview/docx")
    assert res_docx.status_code == 200
    assert "openxmlformats" in res_docx.headers["content-type"]
    assert res_docx.content.startswith(b"PK\x03\x04")
    assert len(res_docx.content) > 5000


def test_previewing_never_advances_round_robin_cursor(client):
    """CRITICAL: Verify previewing templates NEVER advances the Round Robin cursor or affects live queue."""
    initial_cursor = round_robin_scheduler.get_current_cursor()

    # Preview multiple different templates across the entire T01-T30 catalog
    for tid in ["T01", "T05", "T10", "T15", "T20", "T21", "T25", "T30"]:
        res_prev = client.get(f"/api/templates/{tid}/preview")
        assert res_prev.status_code == 200

        res_pdf = client.get(f"/api/templates/{tid}/preview/pdf")
        assert res_pdf.status_code == 200

        res_docx = client.get(f"/api/templates/{tid}/preview/docx")
        assert res_docx.status_code == 200

        # Cursor must remain strictly unchanged after every single preview operation
        assert round_robin_scheduler.get_current_cursor() == initial_cursor

    final_cursor = round_robin_scheduler.get_current_cursor()
    assert final_cursor == initial_cursor, "Round Robin cursor was modified during template preview!"


def test_all_30_templates_have_valid_preview_endpoints(client):
    """Verify that all 30 templates from T01 to T30 respond with 200 for preview details."""
    for i in range(1, 31):
        tid = f"T{i:02d}"
        res = client.get(f"/api/templates/{tid}/preview")
        assert res.status_code == 200, f"Template {tid} failed preview endpoint"
        data = res.json()
        assert data["template"]["template_id"] == tid
        assert data["documents"]["docx_url"] == f"/api/templates/{tid}/preview/docx"
        assert data["documents"]["pdf_url"] == f"/api/templates/{tid}/preview/pdf"

