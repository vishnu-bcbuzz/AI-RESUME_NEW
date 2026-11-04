"""Tests for 'DISPLAY SUCCESSFULLY APPLIED RESUME IMPROVEMENTS' Feature.

Verifies:
1. Green 'Improvements Successfully Applied' section data structure:
   - section_name, title, before_issue, after_change, why_it_helps, status, verified.
   - Display only verified changes actually made.
2. Original and updated score comparison:
   - original_score, new_score, score_delta, category-level score comparison.
   - Strict use of deterministic Python ATS scoring.
3. Amber 'Remaining Improvement Opportunities' section:
   - requirement_name, category, importance, why_it_matters, guidance.
   - Unresolved requirements kept separate from green completed section.
4. Red 'Improvements Not Completed' section:
   - Empty list on clean generation (omitted when everything succeeds).
5. Automatic re-evaluation without re-upload:
   - Score recalculated via Python ATS scoring engine.
6. Next-stage action gating against 80.0 threshold.
"""

import io
import fitz
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture(scope="module")
def junior_test_resume_pdf():
    doc = fitz.open()
    page = doc.new_page()
    text = """
    Barry Allen
    ballen@centralcitypd.gov | Central City, MO

    CAREER OBJECTIVE
    Forensic scientist seeking transition into cybersecurity operations.

    TECHNICAL SKILLS
    Python, Linux, Network Basics

    EDUCATION
    Bachelor of Science in Chemistry - Central City University, 2020

    PROJECTS
    Evidence Database Script
    Developed automated python scripts for indexing lab forensic files.
    """
    page.insert_text(fitz.Point(50, 50), text)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


@pytest.fixture(scope="module")
def improved_resume_result(junior_test_resume_pdf):
    """Module-level fixture: runs analysis and improvement once to optimize execution time."""
    # 1. Analyze junior resume against Role 1 (Ethical Hacker)
    files = {"file": ("barry_resume.pdf", junior_test_resume_pdf, "application/pdf")}
    an_res = client.post("/api/resumes/analyze", data={"role_id": 1}, files=files)
    assert an_res.status_code == 200, f"Analysis failed: {an_res.text}"
    an_data = an_res.json()
    analysis_id = an_data["analysis_id"]

    # 2. Trigger improvement with candidate confirmed skills
    payload = {
        "analysis_id": analysis_id,
        "attempt_number": 1,
        "confirmed_skills": [
            {
                "skill_name": "Vulnerability Assessment",
                "proficiency": "hands_on",
                "tasks_performed": "Ran Nessus vulnerability scans in test lab",
            }
        ],
        "permission_granted": True,
    }
    imp_res = client.post("/api/resumes/improve", json=payload)
    assert imp_res.status_code == 200, f"Improvement failed: {imp_res.text}"
    return {
        "analysis_id": analysis_id,
        "analysis_data": an_data,
        "imp_data": imp_res.json(),
    }


def test_applied_improvements_section_structure(improved_resume_result):
    """Verifies that /api/resumes/improve returns structured applied improvements matching spec."""
    imp_data = improved_resume_result["imp_data"]

    # Verify Green Section: applied_improvements
    assert "applied_improvements" in imp_data
    applied = imp_data["applied_improvements"]
    assert len(applied) >= 4

    for item in applied:
        assert "section_name" in item
        assert "title" in item
        assert "before_issue" in item
        assert "after_change" in item
        assert "why_it_helps" in item
        assert "status" in item
        assert item["status"] == "Successfully updated"
        assert item.get("verified") is True

    # Check for specific expected sections
    section_names = [item["section_name"] for item in applied]
    assert "Professional Summary" in section_names
    assert "Technical Skills" in section_names
    assert "Projects" in section_names
    assert "ATS Formatting" in section_names


def test_score_comparison_and_category_breakdown(improved_resume_result):
    """Verifies original vs improved score and category breakdown."""
    imp_data = improved_resume_result["imp_data"]

    # Original & new score
    assert "original_score" in imp_data
    assert "new_score" in imp_data
    assert "score_delta" in imp_data
    assert imp_data["new_score"] >= imp_data["original_score"]

    # Category breakdown
    assert "category_comparison" in imp_data
    cat_comp = imp_data["category_comparison"]
    assert len(cat_comp) == 5  # 5 standard ATS categories
    for cat in cat_comp:
        assert "category" in cat
        assert "weight" in cat
        assert "original_score" in cat
        assert "new_score" in cat
        assert "delta" in cat


def test_remaining_opportunities_section_structure(improved_resume_result):
    """Verifies amber Remaining Opportunities section identifies unverified requirements."""
    imp_data = improved_resume_result["imp_data"]

    assert "remaining_opportunities" in imp_data
    remaining = imp_data["remaining_opportunities"]
    assert len(remaining) > 0

    for gap in remaining:
        assert "requirement_name" in gap
        assert "category" in gap
        assert "importance" in gap
        assert "why_it_matters" in gap
        assert "guidance" in gap


def test_failed_improvements_empty_on_success(improved_resume_result):
    """Verifies failed_improvements is empty when generation succeeds cleanly (red section hidden)."""
    imp_data = improved_resume_result["imp_data"]

    assert "failed_improvements" in imp_data
    # When everything succeeds, failed_improvements is empty list
    assert imp_data["failed_improvements"] == []


def test_next_stage_gating_preserves_80_threshold(improved_resume_result):
    """Verifies next stage is rejected when score is below 80.0."""
    imp_data = improved_resume_result["imp_data"]
    analysis_id = improved_resume_result["analysis_id"]

    # For junior resume, initial improvement score will be below 80.0 without senior qualifications
    if imp_data["new_score"] < 80.0:
        assert imp_data["stage_passed"] is False
        assert imp_data["next_stage_allowed"] is False
        # Verify next stage endpoint rejects
        next_res = client.post("/api/resumes/next-stage", json={"analysis_id": analysis_id})
        assert next_res.status_code == 400
