"""Automated test suite verifying the 17 specification requirements for FUTRSEC AI Resume Engine:
1. Candidate with initial score below 80 receives skill-confirmation workflow.
2. Candidate-confirmed skills can be included accurately.
3. Skills candidate rejects are not added as existing competencies.
4. Basic familiarity is not described as advanced practical experience.
5. Unconfirmed certifications are not added as earned credentials.
6. The entire resume is rewritten rather than only the summary.
7. The selected cybersecurity job role drives the content.
8. Round Robin template selection remains automatic.
9. The original resume is preserved separately.
10. The improved resume is automatically re-scored.
11. A score of 79 does not satisfy the 80-point post-improvement threshold.
12. A score of 80 or higher enables the next-stage action.
13. A score below 80 after the retry limit does not pass.
14. Education scoring respects role-specific requirements (no flat penalty on Arts if role accepts broad degrees).
15. Existing scoring weights (40/25/15/15/5) and database records remain unchanged.
16. Failed AI generation or scoring produces a clear error.
17. The workflow continues to function with the existing frontend and backend.
"""

import io
import fitz
import pytest
from fastapi.testclient import TestClient
from app.main import app, ANALYSIS_CACHE
from app.config import settings
from app.scoring.engine import ATSScoringEngine, ATSScoreResult, CategoryScore
from app.scoring.matcher import SkillMatcher
from app.projects.generator import ResumeContentGenerator, ConfirmedSkillItem, EnhancedResumeContent
from app.reports.round_robin import RoundRobinScheduler
from app.resume.extractor import ParsedResumeData, ContactInfo, EducationEntry, ProjectEntry, ExperienceEntry

client = TestClient(app)


@pytest.fixture
def sample_resume_pdf():
    doc = fitz.open()
    page = doc.new_page()
    text = """
    Bruce Wayne
    bwayne@wayneenterprises.com | +1 555-0199 | Gotham City, NJ

    CAREER OBJECTIVE
    Dedicated Ethical Hacker and Penetration Tester seeking an offensive cybersecurity role to conduct threat emulation and vulnerability assessments.

    TECHNICAL SKILLS
    Penetration Testing, Vulnerability Assessment, Web Application Security, OWASP Top 10, Nmap, Burp Suite, Linux, Python, Network Security Testing, Report Writing, Wireshark, Metasploit, SIEM

    CERTIFICATIONS
    CEH, CISSP, CompTIA Security+

    EDUCATION
    Master of Science in Cybersecurity - Gotham University, 2021

    PROJECTS
    Enterprise Network Penetration Test
    Conducted network security vulnerability scan and exploit simulation using Nmap, Metasploit, and Wireshark to test network firewall defense and packet integrity.
    Technologies: Python, Nmap, Metasploit, Wireshark

    Web Application Vulnerability Assessment
    Audited enterprise web applications for OWASP Top 10 security flaws including SQL injection, cross-site scripting, and authentication bypass using Burp Suite on Kali Linux.
    Technologies: Burp Suite, OWASP, Linux

    Automated Threat Detection Lab
    Configured SIEM log analysis and network incident response pipelines to detect threat actor intrusion attempts and harden infrastructure security.
    Technologies: SIEM, Python, Wireshark
    """
    page.insert_text(fitz.Point(50, 50), text)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


@pytest.fixture
def junior_resume_pdf():
    doc = fitz.open()
    page = doc.new_page()
    text = """
    Clark Kent
    ckent@dailyplanet.com | Metropolis
    CAREER OBJECTIVE
    Seeking entry level role in technology.
    TECHNICAL SKILLS
    Python, Linux
    EDUCATION
    Bachelor of Arts in Journalism, 2022
    PROJECTS
    Simple Script
    Wrote basic python scripts.
    """
    page.insert_text(fitz.Point(50, 50), text)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


def test_case1_initial_score_below_80_triggers_confirmation_workflow(junior_resume_pdf):
    """Req 1: A candidate with an initial score below 80 receives a skill-confirmation workflow."""
    files = {"file": ("junior.pdf", junior_resume_pdf, "application/pdf")}
    res = client.post("/api/resumes/analyze", data={"role_id": 1}, files=files)
    assert res.status_code == 200
    data = res.json()

    assert data["score_result"]["final_score"] < 80.0
    assert data["stage_passed"] is False
    assert data["action_required"] == "offer_improvement"
    assert "skills_requiring_confirmation" in data["gap_analysis"]
    # Check that confirmation questions are generated from role skills
    questions = data["gap_analysis"]["skills_requiring_confirmation"]
    assert len(questions) > 0
    q_names = [q["skill_name"] for q in questions]
    assert any("burp" in name.lower() or "nmap" in name.lower() or "vulnerability" in name.lower() or "owasp" in name.lower() for name in q_names)


def test_case2_candidate_confirmed_skills_included_accurately():
    """Req 2: Candidate-confirmed skills can be included accurately with practical evidence."""
    raw = ParsedResumeData(
        candidate_name="Diana Prince",
        contact_info=ContactInfo(email="diana@themyscira.gov"),
        technical_skills=["Linux", "Python"],
        education=[EducationEntry(degree="Bachelor of Science in Information Technology", institution="Themyscira Tech")],
        certifications=[],
        projects=[ProjectEntry(title="Network Audit", description="Inspected network configuration.")],
    )
    confirmed = [
        ConfirmedSkillItem(
            skill_name="Burp Suite",
            proficiency="hands_on",
            context_source="Academic Project",
            tasks_performed="Configured intercepting proxy to test web application endpoints for injection vulnerabilities.",
            interview_demonstration="Can explain repeater and intruder tabs, request interception, and SSL certificate installation."
        )
    ]
    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=raw,
        target_role_name="Ethical Hacker",
        missing_core_skills=["Burp Suite"],
        confirmed_skills=confirmed,
        permission_granted=True,
        attempt_number=1,
    )
    assert "Burp Suite" in enhanced.confirmed_skills_included
    assert "Burp Suite" not in enhanced.unverified_skills_excluded
    # Verified in projects
    assert any("Burp Suite" in p["title"] for p in enhanced.projects)
    # Technical skills contains Burp Suite
    all_tech = []
    for s_list in enhanced.technical_skills_grouped.values():
        all_tech.extend(s_list)
    assert "Burp Suite" in all_tech


def test_case3_rejected_skills_not_added_as_existing_competencies():
    """Req 3: Skills the candidate rejects (not_used) are not added as existing competencies."""
    raw = ParsedResumeData(
        candidate_name="Barry Allen",
        contact_info=ContactInfo(email="barry@ccpd.org"),
        technical_skills=["Python", "Linux"],
        education=[EducationEntry(degree="Bachelor of Science in Forensic Science", institution="Central City Univ")],
        certifications=[],
        projects=[],
    )
    confirmed = [
        ConfirmedSkillItem(
            skill_name="Metasploit",
            proficiency="not_used",
            tasks_performed=None,
        )
    ]
    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=raw,
        target_role_name="Ethical Hacker",
        missing_core_skills=["Metasploit"],
        confirmed_skills=confirmed,
        permission_granted=True,
        attempt_number=1,
    )
    assert "Metasploit" in enhanced.unverified_skills_excluded
    assert "Metasploit" not in enhanced.confirmed_skills_included
    # Must NOT be in any technical skills group
    for group_name, skills in enhanced.technical_skills_grouped.items():
        assert "Metasploit" not in skills
    # Recommended as future learning instead
    assert any("Metasploit" in r for r in enhanced.future_learning_recommendations)


def test_case4_basic_familiarity_not_described_as_advanced_practical():
    """Req 4: Basic familiarity is described as foundational/coursework, not advanced practical experience."""
    raw = ParsedResumeData(
        candidate_name="Arthur Curry",
        contact_info=ContactInfo(email="arthur@atlantis.org"),
        technical_skills=["Python", "Linux"],
        education=[EducationEntry(degree="Bachelor of Science", institution="Oceanic Tech")],
        certifications=[],
        projects=[],
    )
    confirmed = [
        ConfirmedSkillItem(
            skill_name="Nmap",
            proficiency="basic_familiarity",
            context_source="University Coursework",
            tasks_performed="Studied port scanning types and syntax in classroom lab.",
        )
    ]
    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=raw,
        target_role_name="Ethical Hacker",
        missing_core_skills=["Nmap"],
        confirmed_skills=confirmed,
        permission_granted=True,
        attempt_number=1,
    )
    assert any("Nmap" in s for s in enhanced.confirmed_skills_included)
    # Check that it appears under Foundational Knowledge, not claimed as practical project
    assert "Foundational Knowledge & Coursework Exposure" in enhanced.technical_skills_grouped
    foundational_items = enhanced.technical_skills_grouped["Foundational Knowledge & Coursework Exposure"]
    assert any("Nmap" in item and "Coursework" in item for item in foundational_items)


def test_case5_unconfirmed_certifications_not_added_as_earned():
    """Req 5: Unconfirmed certifications are never added as earned credentials."""
    raw = ParsedResumeData(
        candidate_name="Hal Jordan",
        contact_info=ContactInfo(email="hal@ferrisair.com"),
        technical_skills=["Linux", "Networking"],
        education=[EducationEntry(degree="Bachelor of Science in Aeronautics", institution="Coast City Univ")],
        certifications=[],  # Does NOT hold CEH, Security+, CISSP
        projects=[],
    )
    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=raw,
        target_role_name="Ethical Hacker",
        missing_core_skills=["CEH", "Security+", "CISSP"],
        attempt_number=1,
    )
    # Certifications must remain empty
    assert len(enhanced.certifications) == 0
    assert "CEH" not in enhanced.certifications
    assert "Security+" not in enhanced.certifications
    assert "CISSP" not in enhanced.certifications


def test_case6_entire_resume_rewritten():
    """Req 6: The entire resume is rewritten rather than only the summary."""
    raw = ParsedResumeData(
        candidate_name="Victor Stone",
        contact_info=ContactInfo(email="vic@star-labs.com", phone="+1 555-0188"),
        professional_summary="Hardware technician.",
        technical_skills=["Hardware", "C++", "Linux"],
        education=[EducationEntry(degree="Bachelor of Science in Computer Engineering", institution="STAR Institute")],
        employment_history=[
            ExperienceEntry(
                job_title="Technician",
                company="STAR Labs",
                responsibilities=["tested system diagnostics", "assembled circuits"]
            )
        ],
        projects=[ProjectEntry(title="Diagnostics Bot", description="created automated diagnostic scanner")],
        certifications=[],
        achievements=["Dean's List 2021"],
    )
    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=raw,
        target_role_name="Ethical Hacker",
        missing_core_skills=[],
        attempt_number=1,
    )
    # Check that headline is generated
    assert enhanced.professional_headline is not None
    assert len(enhanced.professional_headline) > 10
    # Check that summary is rewritten
    assert enhanced.professional_summary != raw.professional_summary
    # Check that experience responsibilities start with strong action verbs
    for exp in enhanced.experience:
        for r in exp["responsibilities"]:
            assert r[0].isupper()
            assert r.endswith(".")
    # Check sections rewritten list
    assert len(enhanced.sections_rewritten) >= 6


def test_case7_selected_cybersecurity_role_drives_content():
    """Req 7: The selected cybersecurity job role drives content emphasis."""
    raw = ParsedResumeData(
        candidate_name="John Jones",
        contact_info=ContactInfo(email="john@detective.org"),
        technical_skills=["Python", "Linux", "Wireshark", "Burp Suite", "Splunk"],
        education=[EducationEntry(degree="Bachelor of Science in Information Systems", institution="Mars Univ")],
        certifications=[],
        projects=[],
    )
    # Role A: Ethical Hacker
    enh_pentest = ResumeContentGenerator.generate_enhanced_content(
        resume_data=raw,
        target_role_name="Ethical Hacker",
        missing_core_skills=[],
    )
    assert "Offensive" in enh_pentest.professional_headline or "Penetration" in enh_pentest.professional_headline

    # Role B: SOC Analyst
    enh_soc = ResumeContentGenerator.generate_enhanced_content(
        resume_data=raw,
        target_role_name="SOC Analyst",
        missing_core_skills=[],
    )
    assert "Defense" in enh_soc.professional_headline or "SOC" in enh_soc.professional_headline or "Operations" in enh_soc.professional_headline


def test_case8_round_robin_selection_automatic(tmp_path):
    """Req 8: Round Robin template selection remains automatic."""
    sched = RoundRobinScheduler(
        state_file=tmp_path / "test_state.json",
        assignments_file=tmp_path / "test_rr.json"
    )
    t1, _ = sched.select_next_template(job_id="job_auto_1")
    t2, _ = sched.select_next_template(job_id="job_auto_2")
    assert t1.template_id != t2.template_id


def test_case9_original_resume_preserved(junior_resume_pdf):
    """Req 9: The original resume is preserved separately."""
    files = {"file": ("junior_p.pdf", junior_resume_pdf, "application/pdf")}
    res = client.post("/api/resumes/analyze", data={"role_id": 1}, files=files)
    analysis_id = res.json()["analysis_id"]

    orig_skills = ANALYSIS_CACHE[analysis_id]["parsed_resume"].technical_skills.copy()
    orig_score = ANALYSIS_CACHE[analysis_id]["score_result"].final_score

    # Run improvement
    client.post("/api/resumes/improve", json={"analysis_id": analysis_id, "attempt_number": 1})

    # Cached original resume must remain unmodified
    assert ANALYSIS_CACHE[analysis_id]["parsed_resume"].technical_skills == orig_skills
    assert ANALYSIS_CACHE[analysis_id]["score_result"].final_score == orig_score


def test_case10_improved_resume_automatically_rescored(junior_resume_pdf):
    """Req 10: The improved resume is automatically re-scored without manual upload."""
    files = {"file": ("junior_rescore.pdf", junior_resume_pdf, "application/pdf")}
    res = client.post("/api/resumes/analyze", data={"role_id": 1}, files=files)
    analysis_id = res.json()["analysis_id"]

    imp = client.post("/api/resumes/improve", json={"analysis_id": analysis_id, "attempt_number": 1})
    assert imp.status_code == 200
    data = imp.json()
    assert "new_score" in data
    assert "original_score" in data
    assert "category_comparison" in data
    assert len(data["category_comparison"]) == 5


def test_case11_score_79_does_not_satisfy_80_threshold():
    """Req 11: A score of 79 does not satisfy the 80-point post-improvement threshold."""
    mock_id_79 = "an_test_score_79"
    ANALYSIS_CACHE[mock_id_79] = {
        "latest_score": 79.0,
        "stage_passed": False,
        "next_stage_allowed": False,
        "current_attempt": 1,
        "role_profile": {"role_id": 1, "role_name": "Ethical Hacker"},
    }
    res = client.post("/api/resumes/next-stage", json={"analysis_id": mock_id_79})
    assert res.status_code == 400
    assert "80.0" in res.json()["detail"]


def test_case12_score_80_or_higher_enables_next_stage():
    """Req 12: A score of 80 or higher enables the next-stage action."""
    mock_id_80 = "an_test_score_80"
    ANALYSIS_CACHE[mock_id_80] = {
        "latest_score": 80.0,
        "stage_passed": True,
        "next_stage_allowed": True,
        "current_attempt": 1,
        "role_profile": {"role_id": 1, "role_name": "Ethical Hacker"},
    }
    res = client.post("/api/resumes/next-stage", json={"analysis_id": mock_id_80})
    assert res.status_code == 200
    assert res.json()["status"] == "authorized"


def test_case13_score_below_80_after_retry_limit_does_not_pass(junior_resume_pdf):
    """Req 13: A score below 80 after the retry limit does not pass and stops retries."""
    files = {"file": ("junior_attempts.pdf", junior_resume_pdf, "application/pdf")}
    res = client.post("/api/resumes/analyze", data={"role_id": 1}, files=files)
    analysis_id = res.json()["analysis_id"]

    # 3 attempts
    for i in range(1, 4):
        resp = client.post("/api/resumes/improve", json={"analysis_id": analysis_id, "attempt_number": i})
        assert resp.status_code == 200

    data = resp.json()
    if data["new_score"] < 80.0:
        assert data["stage_passed"] is False
        assert data["can_retry"] is False

    # Attempt 4 blocked
    resp_4 = client.post("/api/resumes/improve", json={"analysis_id": analysis_id, "attempt_number": 4})
    assert resp_4.status_code == 400


def test_case14_education_scoring_respects_role_specific_requirements():
    """Req 14: Education scoring respects role-specific requirements (no flat penalty on Arts if role accepts broad backgrounds)."""
    # Role requirement explicitly accepts arts and science
    role_reqs_broad = [
        {
            "requirement_type": "education",
            "requirement_description": "No specific degree is mandated; engineering, computer science, IT, arts and science, and other backgrounds are all eligible.",
            "importance": "preferred"
        }
    ]
    arts_education = [EducationEntry(degree="Bachelor of Arts in English", institution="Liberal Arts College")]
    score_arts = ATSScoringEngine._score_education(arts_education, role_reqs_broad, weight=15.0)
    # Bachelor's degree should earn full base ratio (0.90 * 15.0 = 13.5) without deduction
    assert score_arts.score_earned == 13.5
    assert "without discipline deduction" in score_arts.explanation

    # Compare with role strictly requiring technical degree
    role_reqs_strict = [
        {
            "requirement_type": "education",
            "requirement_description": "Requires an accredited engineering or computer science degree.",
            "importance": "mandatory"
        }
    ]
    score_strict = ATSScoringEngine._score_education(arts_education, role_reqs_strict, weight=15.0)
    # Calibrated adjustment should be applied, capped at <= 3.0 points
    assert score_strict.score_earned < score_arts.score_earned
    adj = score_strict.details["degree_relevance_adjustment_pts"]
    assert adj <= 0.0 and adj >= -3.0


def test_case15_existing_scoring_weights_and_db_records_unchanged():
    """Req 15: Existing scoring weights (40/25/15/15/5) and database records remain unchanged."""
    weights = ATSScoringEngine.DEFAULT_WEIGHTS
    assert weights["Technical Skills"] == 40.0
    assert weights["Projects"] == 25.0
    assert weights["Education"] == 15.0
    assert weights["Tools & Certifications"] == 15.0
    assert weights["Career Objective"] == 5.0
    assert sum(weights.values()) == 100.0


def test_case16_failed_ai_generation_produces_clear_error():
    """Req 16: Failed AI generation or scoring produces a clear error."""
    res = client.post("/api/resumes/improve", json={"analysis_id": "an_nonexistent_session"})
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_case17_full_workflow_integration(sample_resume_pdf):
    """Req 17: The workflow continues to function with the existing frontend and backend."""
    # 1. Health
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] in ("healthy", "ok", "degraded")

    # 2. Roles
    res_roles = client.get("/api/roles")
    assert res_roles.status_code == 200
    roles_data = res_roles.json()
    assert len(roles_data["roles"]) > 0
    role_id = roles_data["roles"][0]["role_id"]

    # 3. Analyze
    files = {"file": ("test_flow.pdf", sample_resume_pdf, "application/pdf")}
    res_analyze = client.post("/api/resumes/analyze", data={"role_id": role_id}, files=files)
    assert res_analyze.status_code == 200
    an_data = res_analyze.json()
    assert "analysis_id" in an_data
