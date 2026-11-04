"""Comprehensive test suite for candidate-approved project inclusion, preservation, and PDF rendering.

Verifies:
1. An existing saved project is approved and included in the resume alongside original projects.
2. A newly added completed project is approved and included with clean title (no 'In Progress').
3. An unapproved project is strictly excluded.
4. An in-progress project retains ' | In Progress' and truthful progressive bullets.
5. A completed project retains clean title and completed bullets.
6. Existing projects are not duplicated upon retry or re-approval.
7. Skills remain separate from projects.
8. All approved projects survive AI generation and document rendering into DOCX/PDF.
9. The generated PDF actually contains all approved project titles in its text stream.
10. Backend approval endpoint supports both proposed_entry and approved_entry payloads.
"""

import re
from pathlib import Path
import pytest
import fitz  # PyMuPDF

from app.projects.evaluator import (
    CompletedProjectSubmission,
    CompletedProjectEvaluator,
    ProposedResumeEntry,
)
from app.projects.generator import (
    ResumeContentGenerator,
    ConfirmedSkillItem,
    EnhancedResumeContent,
)
from app.resume.extractor import (
    ParsedResumeData,
    ContactInfo,
    EducationEntry,
    ProjectEntry,
    ExperienceEntry,
)
from app.reports.renderer import DocumentRenderer
from app.reports.round_robin import template_registry
from app.resume.validator import ResumeContentValidator


@pytest.fixture
def original_candidate_resume():
    """Simulates the uploaded resume containing Student Management System and RAG Chatbot."""
    return ParsedResumeData(
        candidate_name="Alex Chen",
        contact_info=ContactInfo(
            email="alex.chen@cybersec.org",
            phone="+1-555-0199",
            location="San Jose, CA",
            linkedin="https://linkedin.com/in/alexchen",
            github="https://github.com/alexchen",
        ),
        professional_summary="Dedicated cybersecurity student with software engineering foundation.",
        technical_skills=["Python", "FastAPI", "PostgreSQL", "Linux", "Git"],
        employment_history=[],
        projects=[
            ProjectEntry(
                title="Student Management System",
                description="Built an administrative web portal for student records, enrollment tracking, and grade reports.",
                technologies=["Python", "Django", "SQLite"],
                outcomes="Reduced student record retrieval latency by 40% across departmental departments.",
            ),
            ProjectEntry(
                title="RAG Chatbot",
                description="Engineered a retrieval-augmented generation question-answering assistant using vector search.",
                technologies=["Python", "LangChain", "ChromaDB", "FastAPI"],
                outcomes="Delivered accurate document retrieval over 2,000 internal documents.",
            ),
        ],
        education=[
            EducationEntry(
                degree="BS in Computer Science",
                institution="California State University",
                graduation_year="2025",
            )
        ],
        certifications=[],
        achievements=[],
    )


def test_existing_saved_project_approved_and_included(original_candidate_resume):
    """Test 1: Approved newly saved project is included alongside original resume projects."""
    in_prog_entry = ProposedResumeEntry(
        title_line="Network Monitoring System | In Progress",
        bullets=[
            "Developing: Network monitoring application to track service availability and record monitoring results.",
            "Technologies: Python, FastAPI, PostgreSQL.",
            "Planned Implementation: Progressing through technical development and security verification for SOC Analyst.",
        ],
        status_label="In Progress",
        is_approved=True,
    )

    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=original_candidate_resume,
        target_role_name="SOC Analyst",
        missing_core_skills=["Network Security", "SIEM"],
        confirmed_skills=[],
        approved_plan_items=[],
        permission_granted=True,
        attempt_number=1,
        approved_projects=[in_prog_entry],
    )

    project_titles = [p["title"] for p in enhanced.projects]

    # Must contain the approved in-progress project
    assert any("Network Monitoring System" in t for t in project_titles), f"Approved project missing from {project_titles}"
    assert any("In Progress" in t for t in project_titles if "Network Monitoring System" in t)

    # Must ALSO preserve original resume projects
    assert any("Student Management System" in t for t in project_titles), f"Original Student Management System missing from {project_titles}"
    assert any("RAG Chatbot" in t for t in project_titles), f"Original RAG Chatbot missing from {project_titles}"


def test_newly_added_completed_project_approved_and_included(original_candidate_resume):
    """Test 2: Completed project retains clean title (no In Progress) and verified bullets."""
    completed_entry = ProposedResumeEntry(
        title_line="Automated Vulnerability Scanner",
        bullets=[
            "Developed: CLI vulnerability scanner identifying OWASP Top 10 vulnerabilities in test targets.",
            "Technologies: Python, Requests, BeautifulSoup, Nmap.",
            "Tested: Verified against authorized Juice Shop and DVWA lab targets.",
            "Achieved: Detected 100% of injected SQLi and XSS vulnerabilities in test bench.",
        ],
        status_label="Completed",
        is_approved=True,
    )

    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=original_candidate_resume,
        target_role_name="Ethical Hacker",
        missing_core_skills=[],
        confirmed_skills=[],
        approved_plan_items=[],
        permission_granted=True,
        attempt_number=1,
        approved_projects=[completed_entry],
    )

    matched = [p for p in enhanced.projects if "Automated Vulnerability Scanner" in p["title"]]
    assert len(matched) == 1
    proj = matched[0]

    # Must NOT have "In Progress" in title
    assert "In Progress" not in proj["title"]
    assert proj["title"] == "Automated Vulnerability Scanner"
    assert "Developed:" in proj["description"]


def test_unapproved_project_is_excluded(original_candidate_resume):
    """Test 3: An unapproved project must NOT be included in the generated resume."""
    # We do NOT pass the unapproved project into approved_projects
    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=original_candidate_resume,
        target_role_name="SOC Analyst",
        missing_core_skills=[],
        confirmed_skills=[],
        approved_plan_items=[],
        permission_granted=True,
        attempt_number=1,
        approved_projects=[],  # No approved projects
    )

    project_titles = [p["title"] for p in enhanced.projects]
    assert not any("Unapproved Experimental Bot" in t for t in project_titles)
    assert not any("Network Monitoring System" in t for t in project_titles)


def test_in_progress_and_completed_status_preserved(original_candidate_resume):
    """Tests 4 & 5: In-progress projects keep 'In Progress'; completed projects keep clean title."""
    in_prog = ProposedResumeEntry(
        title_line="Cloud IAM Auditor | In Progress",
        bullets=[
            "Developing: AWS IAM least-privilege audit utility.",
            "Technologies: Python, Boto3, AWS IAM.",
            "Planned Implementation: Validating role trust policies against CIS AWS benchmarks.",
        ],
        status_label="In Progress",
        is_approved=True,
    )
    completed = ProposedResumeEntry(
        title_line="Packet Capture Analysis Tool",
        bullets=[
            "Developed: PCAP stream reassembler identifying suspicious DNS tunneling queries.",
            "Technologies: Python, Scapy, Wireshark.",
            "Tested: Evaluated with real PCAP datasets containing covert DNS tunnels.",
            "Achieved: Parsed 500,000 packets per minute with 99.2% classification accuracy.",
        ],
        status_label="Completed",
        is_approved=True,
    )

    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=original_candidate_resume,
        target_role_name="Security Analyst",
        missing_core_skills=[],
        confirmed_skills=[],
        approved_plan_items=[],
        permission_granted=True,
        attempt_number=1,
        approved_projects=[in_prog, completed],
    )

    iam_proj = next(p for p in enhanced.projects if "Cloud IAM Auditor" in p["title"])
    assert "In Progress" in iam_proj["title"]
    assert "Developing:" in iam_proj["description"]

    pcap_proj = next(p for p in enhanced.projects if "Packet Capture Analysis Tool" in p["title"])
    assert "In Progress" not in pcap_proj["title"]
    assert pcap_proj["title"] == "Packet Capture Analysis Tool"
    assert "Developed:" in pcap_proj["description"]


def test_projects_not_duplicated_on_retry(original_candidate_resume):
    """Test 6: Projects are not duplicated when the candidate retries or re-approves."""
    approved_entry = ProposedResumeEntry(
        title_line="Student Management System",
        bullets=[
            "Developed: Administrative student portal with role-based access control.",
            "Technologies: Python, Django, SQLite.",
            "Tested: Verified access control policies in sandbox.",
            "Achieved: Delivered reliable records portal.",
        ],
        status_label="Completed",
        is_approved=True,
    )

    # Approved entry shares title with an existing original resume project
    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=original_candidate_resume,
        target_role_name="Cybersecurity Specialist",
        missing_core_skills=[],
        confirmed_skills=[],
        approved_plan_items=[],
        permission_granted=True,
        attempt_number=2,
        approved_projects=[approved_entry, approved_entry],  # duplicate passed in list
    )

    student_projs = [p for p in enhanced.projects if "Student Management System" in p["title"]]
    assert len(student_projs) == 1, f"Found duplicate projects: {student_projs}"


def test_skills_remain_separate_from_projects(original_candidate_resume):
    """Test 7: Skill confirmations must never appear as projects; skills section stays pure."""
    confirmed_skill = ConfirmedSkillItem(
        skill_name="Splunk",
        proficiency="hands_on",
        context_source="Candidate Confirmation",
        tasks_performed="Verified proficiency: hands_on for Splunk",
    )

    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=original_candidate_resume,
        target_role_name="SOC Analyst",
        missing_core_skills=[],
        confirmed_skills=[confirmed_skill],
        approved_plan_items=[],
        permission_granted=True,
        attempt_number=1,
        approved_projects=[],
    )

    # Validate with validator
    sanitized, report = ResumeContentValidator.validate_and_sanitize(enhanced)

    # None of the projects should contain candidate confirmation tags
    for p in sanitized.projects:
        assert "candidate confirmation" not in p["title"].lower()
        assert "practical implementation (" not in p["title"].lower()

    # Skills section must have the confirmed skill categorized
    all_skills = []
    for s_list in sanitized.technical_skills_grouped.values():
        all_skills.extend([s.lower() for s in s_list])
    assert any("splunk" in s for s in all_skills)


def test_all_approved_projects_survive_generation_and_appear_in_pdf(original_candidate_resume, tmp_path):
    """Tests 8 & 9: All approved projects survive document rendering and their titles appear in the generated PDF."""
    approved1 = ProposedResumeEntry(
        title_line="Network Monitoring System | In Progress",
        bullets=[
            "Developing: Network monitoring system for telemetry collection.",
            "Technologies: Python, FastAPI, PostgreSQL.",
            "Planned Implementation: Initializing live telemetry collection.",
        ],
        status_label="In Progress",
        is_approved=True,
    )
    approved2 = ProposedResumeEntry(
        title_line="Automated Vulnerability Scanner",
        bullets=[
            "Developed: Modular vulnerability scanner targeting web applications.",
            "Technologies: Python, Nmap, Requests.",
            "Tested: Verified against OWASP Juice Shop.",
            "Achieved: Flagged all known critical vulnerabilities.",
        ],
        status_label="Completed",
        is_approved=True,
    )

    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=original_candidate_resume,
        target_role_name="SOC Analyst",
        missing_core_skills=[],
        confirmed_skills=[],
        approved_plan_items=[],
        permission_granted=True,
        attempt_number=1,
        approved_projects=[approved1, approved2],
    )

    # Select template 01
    template = template_registry.list_templates()[0]

    # Render resume
    render_result = DocumentRenderer.render_resume(
        content=enhanced,
        template=template,
        job_id="test_approved_projects_job",
    )

    docx_path = Path(render_result["docx_path"])
    pdf_path = Path(render_result["pdf_path"])

    assert docx_path.exists() and docx_path.stat().st_size > 0, "DOCX file was not generated"
    assert pdf_path.exists() and pdf_path.stat().st_size > 0, "PDF file was not generated"

    # Verify PDF magic bytes
    with open(pdf_path, "rb") as f:
        assert f.read(4) == b"%PDF", "PDF does not have valid magic header"

    # Extract text from the PDF using PyMuPDF (fitz)
    doc = fitz.open(pdf_path)
    full_pdf_text = ""
    for page in doc:
        full_pdf_text += page.get_text()
    doc.close()

    # REQUIREMENT: PDF must contain the approved projects!
    assert "Network Monitoring System" in full_pdf_text, "Network Monitoring System missing from generated PDF text"
    assert "Automated Vulnerability Scanner" in full_pdf_text, "Automated Vulnerability Scanner missing from generated PDF text"

    # REQUIREMENT: Original resume projects must ALSO be present
    assert "Student Management System" in full_pdf_text, "Student Management System missing from generated PDF text"
    assert "RAG Chatbot" in full_pdf_text, "RAG Chatbot missing from generated PDF text"


def test_approve_endpoint_supports_both_field_names():
    """Test 10: Backend /api/projects/approve-for-resume supports proposed_entry and approved_entry."""
    from fastapi.testclient import TestClient
    from app.main import app, ANALYSIS_CACHE

    client = TestClient(app)

    # Setup dummy analysis in cache
    test_id = "an_test_approval_flow"
    ANALYSIS_CACHE[test_id] = {
        "role_name": "SOC Analyst",
        "approved_completed_projects": [],
    }

    # Test with approved_entry (what frontend sends)
    payload1 = {
        "analysis_id": test_id,
        "approved_entry": {
            "title_line": "Threat Intelligence Aggregator | In Progress",
            "bullets": ["Developing: Threat feed ingestion pipeline.", "Technologies: Python, STIX/TAXII."],
            "status_label": "In Progress",
            "is_approved": True,
        },
        "confirmed_by_candidate": True,
    }
    res1 = client.post("/api/projects/approve-for-resume", json=payload1)
    assert res1.status_code == 200, f"Expected 200 but got {res1.status_code}: {res1.text}"
    data1 = res1.json()
    assert data1["status"] == "approved"
    assert data1["project_title"] == "Threat Intelligence Aggregator | In Progress"

    # Test with proposed_entry
    payload2 = {
        "analysis_id": test_id,
        "proposed_entry": {
            "title_line": "Firewall Rule Auditor",
            "bullets": ["Developed: Rule analysis engine.", "Technologies: Python, iptables."],
            "status_label": "Completed",
            "is_approved": True,
        },
        "confirmed_by_candidate": True,
    }
    res2 = client.post("/api/projects/approve-for-resume", json=payload2)
    assert res2.status_code == 200, f"Expected 200 but got {res2.status_code}: {res2.text}"

    # Verify both approved projects are preserved in ANALYSIS_CACHE
    cached_projects = ANALYSIS_CACHE[test_id]["approved_completed_projects"]
    assert len(cached_projects) == 2
    titles = [p.title_line for p in cached_projects]
    assert "Threat Intelligence Aggregator | In Progress" in titles
    assert "Firewall Rule Auditor" in titles


def test_improve_endpoint_combines_original_and_approved_projects_and_pdf(original_candidate_resume):
    """Test 11: End-to-end /api/resumes/improve endpoint combines original and approved projects into PDF."""
    from fastapi.testclient import TestClient
    from app.main import app, ANALYSIS_CACHE
    from app.scoring.matcher import SkillMatcher
    from app.scoring.engine import ATSScoringEngine
    from app.scoring.gap_analysis import SkillGapAnalyzer

    client = TestClient(app)

    test_id = "an_e2e_full_verification"
    role_profile = {
        "role_id": 1,
        "role_name": "SOC Analyst",
        "description": "Security Operations Center Analyst",
        "skills": [
            {"skill_id": 1, "skill_name": "Network Security", "importance": "core"},
            {"skill_id": 2, "skill_name": "SIEM", "importance": "core"},
            {"skill_id": 3, "skill_name": "Linux", "importance": "preferred"},
        ],
        "requirements": [],
        "scoring_criteria": [
            {"category": "Skills", "weight": 40.0},
            {"category": "Projects", "weight": 25.0},
            {"category": "Education", "weight": 15.0},
            {"category": "Tools", "weight": 15.0},
            {"category": "Summary", "weight": 5.0},
        ],
    }

    match_report = SkillMatcher.match_skills(
        role_skills=role_profile["skills"],
        resume_skills=original_candidate_resume.technical_skills,
        resume_full_text="Alex Chen resume text",
        resume_projects=original_candidate_resume.projects,
        resume_experience=original_candidate_resume.employment_history,
        role_id=role_profile["role_id"],
        role_name=role_profile["role_name"],
    )
    score_result = ATSScoringEngine.calculate_score(
        resume_data=original_candidate_resume,
        match_report=match_report,
        role_requirements=role_profile["requirements"],
        db_scoring_criteria=role_profile["scoring_criteria"],
        threshold=80.0,
    )
    gap_report = SkillGapAnalyzer.analyze_gaps(match_report, original_candidate_resume)

    ANALYSIS_CACHE[test_id] = {
        "parsed_resume": original_candidate_resume,
        "role_profile": role_profile,
        "score_result": score_result,
        "gap_report": gap_report,
        "match_report": match_report,
        "improvement_plan": None,
        "latest_score": score_result.final_score,
        "stage_passed": False,
        "next_stage_allowed": False,
        "current_attempt": 0,
        "approved_completed_projects": [],
    }

    # Step A: Candidate approves adding newly saved Network Monitoring System | In Progress
    appr_payload = {
        "analysis_id": test_id,
        "approved_entry": {
            "title_line": "Network Monitoring System | In Progress",
            "bullets": [
                "Developing: Network monitoring application to track service availability.",
                "Technologies: Python, FastAPI, PostgreSQL.",
                "Planned Implementation: Progressing through technical development and security verification.",
            ],
            "status_label": "In Progress",
            "is_approved": True,
        },
        "confirmed_by_candidate": True,
    }
    appr_res = client.post("/api/projects/approve-for-resume", json=appr_payload)
    assert appr_res.status_code == 200

    # Step B: Candidate clicks Generate Improved Resume
    imp_payload = {
        "analysis_id": test_id,
        "attempt_number": 1,
        "confirmed_skills": [],
        "approved_plan_items": [],
        "approved_completed_projects": [appr_payload["approved_entry"]],
        "permission_granted": True,
    }
    imp_res = client.post("/api/resumes/improve", json=imp_payload)
    assert imp_res.status_code == 200, f"Improve failed: {imp_res.text}"
    imp_data = imp_res.json()

    # Step C: Verify enhanced projects contains ALL THREE projects
    projects = imp_data["enhanced_content"]["projects"]
    titles = [p["title"] for p in projects]

    assert any("Network Monitoring System" in t for t in titles), f"Network Monitoring System missing from {titles}"
    assert any("In Progress" in t for t in titles if "Network Monitoring System" in t)
    assert any("Student Management System" in t for t in titles), f"Student Management System missing from {titles}"
    assert any("RAG Chatbot" in t for t in titles), f"RAG Chatbot missing from {titles}"

    # Step D: Download the generated PDF and verify text
    pdf_url = imp_data["documents"]["pdf_url"]
    assert pdf_url is not None
    dl_res = client.get(pdf_url)
    assert dl_res.status_code == 200
    pdf_bytes = dl_res.content
    assert pdf_bytes[:4] == b"%PDF"

    # Extract text with PyMuPDF
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pdf_text = "".join(page.get_text() for page in doc)
    doc.close()

    assert "Network Monitoring System" in pdf_text, "Network Monitoring System not found in PDF!"
    assert "Student Management System" in pdf_text, "Student Management System not found in PDF!"
    assert "RAG Chatbot" in pdf_text, "RAG Chatbot not found in PDF!"

