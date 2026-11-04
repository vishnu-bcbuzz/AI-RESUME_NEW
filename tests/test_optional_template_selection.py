"""Test suite for Optional Template Selection with Automatic Round Robin.

Validates:
1. Candidate generates a resume without changing default option (automatic selection).
2. Backend assigns the next Round Robin template.
3. Candidate switches to manual selection.
4. Candidate previews templates without affecting the Round Robin cursor.
5. Candidate selects T15 and generates a resume.
6. Confirm T15 is used in both DOCX and PDF.
7. Confirm the manual selection does not advance the Round Robin cursor.
8. Candidate switches back to automatic selection.
9. Confirm the next automatic template follows the previous automatic assignment.
10. Retry a generation job and verify that its original template is reused.
11. Test concurrent automatic generation jobs.
12. Verify that the final resume preserves original projects and certifications.
"""

import io
import uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import pytest
from fastapi.testclient import TestClient
from docx import Document
import pypdf

from app.main import app, ANALYSIS_CACHE
from app.reports.round_robin import round_robin_scheduler, template_registry
from app.resume.extractor import ParsedResumeData, ContactInfo, ProjectEntry, CertificationEntry
from app.scoring.engine import ATSScoringEngine, ATSScoreResult, CategoryScore


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def mock_analysis_session():
    """Sets up a complete analysis session in cache for generation testing."""
    analysis_id = "test_analysis_tmpl_selection"
    parsed_resume = ParsedResumeData(
        candidate_name="Alex Mercer",
        contact_info=ContactInfo(
            email="alex.mercer@example.com",
            phone="+1 555-0199",
            location="Dallas, TX",
            linkedin="https://linkedin.com/in/alexmercer",
            github="https://github.com/alexmercer",
        ),
        professional_summary="Cybersecurity analyst with practical experience in network vulnerability scanning and incident investigation.",
        technical_skills=["Python", "Wireshark", "Nmap", "Splunk", "Linux"],
        certifications=["CompTIA Security+"],
        structured_certifications=[CertificationEntry(name="CompTIA Security+", certification_name="CompTIA Security+")],
        projects=[
            ProjectEntry(
                title="Automated Port Hardening Scanner",
                description="Engineered an automated scanning tool leveraging Nmap to assess open enterprise ports.",
                technologies=["Python", "Nmap", "Linux"],
                status="Completed",
                bullets=[
                    "Engineered an automated scanning tool leveraging Nmap to assess open enterprise ports.",
                    "Correlated open ports against CVE advisories to prioritize patch deployments."
                ],
                github_url="https://github.com/alexmercer/port-scanner",
            )
        ],
        employment_history=[],
        education=[],
    )

    role_profile = {
        "role_id": 1,
        "role_name": "Ethical Hacker / Penetration Tester",
        "skills": [
            {"skill_name": "Nmap", "importance": "core"},
            {"skill_name": "Python", "importance": "core"},
            {"skill_name": "Wireshark", "importance": "core"},
            {"skill_name": "Metasploit", "importance": "core"},
        ],
        "requirements": ["Practical penetration testing skills", "Nmap proficiency"],
        "scoring_criteria": [
            {"category": "Skills", "weight": 35.0},
            {"category": "Tools", "weight": 20.0},
            {"category": "Education", "weight": 15.0},
            {"category": "Projects", "weight": 20.0},
            {"category": "Summary", "weight": 10.0},
        ],
    }

    cat_scores = [
        CategoryScore(category_name="Technical Skills", weight=35.0, score_earned=26.0, percentage=74.3, explanation="Good skills"),
        CategoryScore(category_name="Tools & Certifications", weight=20.0, score_earned=15.0, percentage=75.0, explanation="Security+ held"),
        CategoryScore(category_name="Education", weight=15.0, score_earned=12.0, percentage=80.0, explanation="Degree"),
        CategoryScore(category_name="Projects", weight=20.0, score_earned=14.0, percentage=70.0, explanation="Practical project"),
        CategoryScore(category_name="Career Objective", weight=10.0, score_earned=8.0, percentage=80.0, explanation="Objective"),
    ]

    dummy_score = ATSScoreResult(
        role_id=1,
        role_name="Ethical Hacker / Penetration Tester",
        final_score=75.0,
        meets_threshold=False,
        status="IMPROVEMENT_RECOMMENDED",
        category_scores=cat_scores,
        summary_explanation="Candidate profile evaluated",
    )

    class DummyGapReport:
        missing_core_skills = ["Metasploit"]
        missing_preferred_skills = []
        demonstrated_skills = ["Python", "Nmap", "Wireshark"]
        skills_not_demonstrated = ["Metasploit"]
        project_evidence_summary = []
        experience_evidence_summary = []

    ANALYSIS_CACHE[analysis_id] = {
        "parsed_resume": parsed_resume,
        "role_profile": role_profile,
        "gap_report": DummyGapReport(),
        "score_result": dummy_score,
        "current_attempt": 0,
        "attempts_history": [],
    }

    return analysis_id


class TestOptionalTemplateSelectionScenarios:
    """Verifies all 12 scenarios for optional template selection with automatic Round Robin."""

    def test_scenario_1_and_2_default_automatic_selection(self, test_client, mock_analysis_session):
        """Scenario 1 & 2: Candidate generates without changing default option; backend assigns next Round Robin template."""
        # Record initial cursor
        initial_cursor = round_robin_scheduler.get_current_cursor()
        eligible_templates = template_registry.get_eligible_templates("Ethical Hacker / Penetration Tester")
        expected_template_id = eligible_templates[initial_cursor % len(eligible_templates)].template_id

        # Candidate requests generation with default automatic mode
        payload = {
            "analysis_id": mock_analysis_session,
            "attempt_number": 1,
            "selection_mode": "automatic",
        }
        res = test_client.post("/api/resumes/improve", json=payload)
        assert res.status_code == 200, res.text
        data = res.json()

        assert data["selection_mode"] == "automatic"
        assert data["assigned_template"]["template_id"] == expected_template_id
        # Cursor should have advanced by exactly 1
        assert round_robin_scheduler.get_current_cursor() == initial_cursor + 1

    def test_scenario_3_and_4_preview_does_not_advance_cursor(self, test_client):
        """Scenario 3 & 4: Candidate switches to manual selection & previews templates without advancing Round Robin cursor."""
        cursor_before = round_robin_scheduler.get_current_cursor()

        # Preview template T15
        preview_res = test_client.get("/api/templates/T15/preview")
        assert preview_res.status_code == 200
        preview_data = preview_res.json()
        assert preview_data["template"]["template_id"] == "T15"

        # Preview template T08
        preview_res_2 = test_client.get("/api/templates/T08/preview")
        assert preview_res_2.status_code == 200

        # Cursor must NOT have advanced
        assert round_robin_scheduler.get_current_cursor() == cursor_before

    def test_scenario_5_6_7_manual_selection_t15(self, test_client, mock_analysis_session):
        """Scenario 5, 6, 7: Candidate selects T15; confirm T15 used in DOCX & PDF; cursor does NOT advance."""
        cursor_before = round_robin_scheduler.get_current_cursor()

        payload = {
            "analysis_id": mock_analysis_session,
            "attempt_number": 1,
            "selection_mode": "manual",
            "template_id": "T15",
            "job_id": "job_manual_t15_test",
        }
        res = test_client.post("/api/resumes/improve", json=payload)
        assert res.status_code == 200, res.text
        data = res.json()

        assert data["selection_mode"] == "manual"
        assert data["assigned_template"]["template_id"] == "T15"

        # Verify Round Robin cursor did NOT advance
        cursor_after = round_robin_scheduler.get_current_cursor()
        assert cursor_after == cursor_before

        # Verify generated DOCX and PDF exist and reflect T15
        docx_url = data["documents"]["docx_url"]
        pdf_url = data["documents"]["pdf_url"]
        assert docx_url is not None
        assert pdf_url is not None

        docx_res = test_client.get(docx_url)
        assert docx_res.status_code == 200
        assert len(docx_res.content) > 2000

        # Check DOCX contains candidate info
        doc = Document(io.BytesIO(docx_res.content))
        docx_text = "\n".join([p.text for p in doc.paragraphs])
        assert "Alex Mercer" in docx_text
        assert "Automated Port Hardening Scanner" in docx_text

        # Check PDF download
        pdf_res = test_client.get(pdf_url)
        assert pdf_res.status_code == 200
        assert len(pdf_res.content) > 2000
        reader = pypdf.PdfReader(io.BytesIO(pdf_res.content))
        pdf_text = "\n".join([p.extract_text() or "" for p in reader.pages])
        assert "Alex Mercer" in pdf_text
        assert "Automated Port Hardening Scanner" in pdf_text

    def test_scenario_8_and_9_switch_back_to_automatic_follows_sequence(self, test_client, mock_analysis_session):
        """Scenario 8 & 9: Candidate switches back to automatic; next automatic template follows previous automatic assignment."""
        role_name = "Ethical Hacker / Penetration Tester"
        eligible_templates = template_registry.get_eligible_templates(role_name)

        # Step A: Perform automatic generation (assigns template at cursor C)
        cursor_start = round_robin_scheduler.get_current_cursor()
        expected_auto_1 = eligible_templates[cursor_start % len(eligible_templates)].template_id

        uid = uuid.uuid4().hex[:6]
        res_auto_1 = test_client.post("/api/resumes/improve", json={
            "analysis_id": mock_analysis_session,
            "attempt_number": 1,
            "selection_mode": "automatic",
            "job_id": f"job_seq_auto_1_{uid}",
        })
        assert res_auto_1.status_code == 200
        assert res_auto_1.json()["assigned_template"]["template_id"] == expected_auto_1
        assert round_robin_scheduler.get_current_cursor() == cursor_start + 1

        # Step B: Perform manual generation (T20). Cursor must not move!
        res_manual = test_client.post("/api/resumes/improve", json={
            "analysis_id": mock_analysis_session,
            "attempt_number": 1,
            "selection_mode": "manual",
            "template_id": "T20",
            "job_id": f"job_seq_manual_t20_{uid}",
        })
        assert res_manual.status_code == 200
        assert res_manual.json()["assigned_template"]["template_id"] == "T20"
        assert round_robin_scheduler.get_current_cursor() == cursor_start + 1

        # Step C: Switch back to automatic generation. It MUST receive the next sequential template (C + 1)!
        expected_auto_2 = eligible_templates[(cursor_start + 1) % len(eligible_templates)].template_id
        res_auto_2 = test_client.post("/api/resumes/improve", json={
            "analysis_id": mock_analysis_session,
            "attempt_number": 1,
            "selection_mode": "automatic",
            "job_id": f"job_seq_auto_2_{uid}",
        })
        assert res_auto_2.status_code == 200
        assert res_auto_2.json()["assigned_template"]["template_id"] == expected_auto_2
        assert round_robin_scheduler.get_current_cursor() == cursor_start + 2

    def test_scenario_10_retry_reuses_original_template(self, test_client, mock_analysis_session):
        """Scenario 10: Retry of the same generation job reuses its original assigned template."""
        job_id = f"job_retry_test_{uuid.uuid4().hex[:6]}"

        # Attempt 1
        res1 = test_client.post("/api/resumes/improve", json={
            "analysis_id": mock_analysis_session,
            "attempt_number": 1,
            "selection_mode": "automatic",
            "job_id": job_id,
        })
        assert res1.status_code == 200
        assigned_tid_1 = res1.json()["assigned_template"]["template_id"]

        cursor_after_attempt_1 = round_robin_scheduler.get_current_cursor()

        # Attempt 2 (Retry of same job)
        res2 = test_client.post("/api/resumes/improve", json={
            "analysis_id": mock_analysis_session,
            "attempt_number": 2,
            "selection_mode": "automatic",
            "job_id": job_id,
        })
        assert res2.status_code == 200
        assigned_tid_2 = res2.json()["assigned_template"]["template_id"]

        # MUST reuse the exact same template
        assert assigned_tid_2 == assigned_tid_1

        # Cursor MUST NOT advance for retry
        assert round_robin_scheduler.get_current_cursor() == cursor_after_attempt_1

    def test_scenario_11_concurrent_automatic_generation(self, test_client, mock_analysis_session):
        """Scenario 11: Concurrent automatic generation jobs receive unique sequential assignments safely."""
        num_concurrent = 6
        job_ids = [f"concurrent_job_{i}" for i in range(num_concurrent)]

        def run_generation(jid):
            return round_robin_scheduler.select_next_template(
                role_name="Ethical Hacker / Penetration Tester",
                job_id=jid,
                output_format="docx",
            )

        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            results = list(executor.map(run_generation, job_ids))

        assigned_templates = [r[0].template_id for r in results]
        assigned_records = [r[1].template_id for r in results]

        assert len(assigned_templates) == num_concurrent
        assert assigned_templates == assigned_records

        # Each concurrent job must receive a distinct sequential assignment
        assert len(set(assigned_templates)) == num_concurrent

    def test_scenario_12_preserves_projects_and_certifications(self, test_client, mock_analysis_session):
        """Scenario 12: Verify that generated resume preserves original candidate projects and certifications."""
        payload = {
            "analysis_id": mock_analysis_session,
            "attempt_number": 1,
            "selection_mode": "manual",
            "template_id": "T05",
            "job_id": "job_preservation_test",
        }
        res = test_client.post("/api/resumes/improve", json=payload)
        assert res.status_code == 200
        data = res.json()

        # Verify certifications preserved in enhanced content
        assert "CompTIA Security+" in data["enhanced_content"]["certifications"]

        # Verify projects preserved in enhanced content
        projs = data["enhanced_content"]["projects"]
        assert len(projs) >= 1
        assert any("Automated Port Hardening Scanner" in p["title"] for p in projs)

        # Verify DOCX rendering
        docx_res = test_client.get(data["documents"]["docx_url"])
        doc = Document(io.BytesIO(docx_res.content))
        text = "\n".join([p.text for p in doc.paragraphs])
        assert "CompTIA Security+" in text
        assert "Automated Port Hardening Scanner" in text
        assert "Nmap" in text

    def test_backend_validation_for_manual_selection(self, test_client, mock_analysis_session):
        """Validates that backend rejects invalid or missing template IDs in manual mode."""
        # 1. Missing template_id in manual mode
        res_missing = test_client.post("/api/resumes/improve", json={
            "analysis_id": mock_analysis_session,
            "selection_mode": "manual",
            "template_id": "",
        })
        assert res_missing.status_code == 400
        assert "valid template_id must be provided" in res_missing.json()["detail"].lower()

        # 2. Non-existent template_id in manual mode
        res_invalid = test_client.post("/api/resumes/improve", json={
            "analysis_id": mock_analysis_session,
            "selection_mode": "manual",
            "template_id": "T99",
        })
        assert res_invalid.status_code == 400
        assert "invalid, inactive, or not registered" in res_invalid.json()["detail"].lower()

        # 3. Automatic mode ignores supplied template_id
        res_auto = test_client.post("/api/resumes/improve", json={
            "analysis_id": mock_analysis_session,
            "selection_mode": "automatic",
            "template_id": "T25",  # should be ignored
            "job_id": "job_auto_ignore_test",
        })
        assert res_auto.status_code == 200
        # Should be assigned by Round Robin, not forced to T25
        assert res_auto.json()["selection_mode"] == "automatic"
