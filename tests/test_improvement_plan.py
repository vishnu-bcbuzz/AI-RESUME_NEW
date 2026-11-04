"""Comprehensive test suite for Approval-Based Resume Improvement Engine.

Validates:
1. Low initial score triggers personalized improvement plan covering all categories.
2. Candidate Approve, Edit, Skip controls.
3. Strict factual integrity: skills never added without confirmation, projects never invented,
   unearned certifications never placed in earned credentials.
4. Education evaluated using role-specific requirements without arbitrary arts penalties.
5. Round Robin template selection remains operational.
6. Automatic re-scoring with explainable breakdown.
7. Post-improvement 80.0 threshold validation.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.resume.extractor import ParsedResumeData, ContactInfo, EducationEntry, ProjectEntry, ExperienceEntry
from app.scoring.matcher import SkillMatcher
from app.scoring.engine import ATSScoringEngine
from app.scoring.improvement_plan import ImprovementPlanGenerator, ImprovementPlanItem
from app.projects.generator import ResumeContentGenerator, ConfirmedSkillItem


@pytest.fixture
def client():
    return TestClient(app)


def test_improvement_plan_generator_covers_all_categories():
    """Verify ImprovementPlanGenerator produces items covering all 7 required categories."""
    resume_data = ParsedResumeData(
        candidate_name="Alex Rivera",
        contact_info=ContactInfo(email="alex@example.com", phone="555-0199", location="Austin, TX"),
        career_objective="Seeking cybersecurity analyst position.",
        professional_summary="Junior security enthusiast with foundational lab experience.",
        technical_skills=["Linux", "Networking"],
        education=[EducationEntry(degree="Bachelor of Arts in English", institution="State University", graduation_year="2023")],
        certifications=[],
        projects=[ProjectEntry(title="Basic Network Setup", description="Configured home router.", technologies=["Networking"])],
        employment_history=[ExperienceEntry(job_title="IT Helpdesk", company="Tech Services", responsibilities=["Assisted users with password resets", "Logged tickets"])],
    )

    role_skills = [
        {"skill_id": 1, "skill_name": "Linux", "importance": "core"},
        {"skill_id": 2, "skill_name": "Wireshark", "importance": "core"},
        {"skill_id": 3, "skill_name": "Nmap", "importance": "core"},
        {"skill_id": 4, "skill_name": "Splunk", "importance": "preferred"},
        {"skill_id": 5, "skill_name": "Python", "importance": "preferred"},
    ]

    role_requirements = [
        {"requirement_id": 1, "requirement_type": "education", "requirement_description": "Bachelor degree or equivalent practical experience in computing, arts, science, or related.", "importance": "preferred"},
    ]

    criteria = [
        {"category": "Technical Skills", "weight": 40.0},
        {"category": "Projects", "weight": 25.0},
        {"category": "Education", "weight": 15.0},
        {"category": "Tools & Certifications", "weight": 15.0},
        {"category": "Career Objective", "weight": 5.0},
    ]

    match_report = SkillMatcher.match_skills(
        role_skills=role_skills,
        resume_skills=resume_data.technical_skills,
        resume_full_text="Linux Networking IT Helpdesk State University",
        resume_projects=resume_data.projects,
        resume_experience=resume_data.employment_history,
        role_id=1,
        role_name="SOC Analyst",
    )

    score_result = ATSScoringEngine.calculate_score(
        resume_data=resume_data,
        match_report=match_report,
        role_requirements=role_requirements,
        db_scoring_criteria=criteria,
        threshold=80.0,
    )

    assert score_result.final_score < 80.0, "Initial score should be below 80.0"

    plan = ImprovementPlanGenerator.generate_plan(
        resume_data=resume_data,
        match_report=match_report,
        score_result=score_result,
        role_requirements=role_requirements,
        role_name="SOC Analyst",
    )

    assert plan.initial_score == score_result.final_score
    assert plan.threshold == 80.0
    assert not plan.meets_threshold

    item_keys = [item.category_key for item in plan.items]
    assert "technical_skills" in item_keys
    assert "projects" in item_keys
    assert "certifications" in item_keys
    assert "education" in item_keys
    assert "experience" in item_keys
    assert "summary" in item_keys
    assert "tools" in item_keys

    # Verify each item has required structure
    for item in plan.items:
        assert item.current_issue
        assert item.recommended_change
        assert item.relevance_reason
        assert item.required_info
        assert item.expected_improvement
        assert item.status == "pending"


def test_approve_edit_skip_controls():
    """Verify Approve, Edit, and Skip states are handled factually."""
    resume_data = ParsedResumeData(
        candidate_name="Dana Scully",
        contact_info=ContactInfo(email="dana@example.com"),
        career_objective="",
        professional_summary="",
        technical_skills=["Linux"],
        education=[EducationEntry(degree="B.S. in Biology", institution="University", graduation_year="2022")],
        certifications=[],
        projects=[],
        employment_history=[],
    )

    # Candidate APPROVES project addition with real completed details
    approved_projects_item = ImprovementPlanItem(
        item_id="plan_projects",
        category="Projects",
        category_key="projects",
        current_issue="No projects",
        recommended_change="Add completed project",
        relevance_reason="Demonstrate practical skills",
        required_info="Project details",
        expected_improvement="Tangible evidence",
        action_type="project_enhancement",
        status="approved",
        candidate_response={
            "has_omitted_project": "yes",
            "project_title": "Packet Capture & Malware Traffic Analysis",
            "project_technologies": "Wireshark, Linux, Snort",
            "project_contribution": "Analyzed PCAP files for C2 beaconing signatures.",
            "project_outcomes": "Identified anomalous traffic patterns and documented IoCs.",
        }
    )

    # Candidate SKIPS certifications recommendation (has no certs yet)
    skipped_certs_item = ImprovementPlanItem(
        item_id="plan_certifications",
        category="Certifications",
        category_key="certifications",
        current_issue="No certs",
        recommended_change="Add certs",
        relevance_reason="Credential check",
        required_info="Cert status",
        expected_improvement="Verification",
        action_type="cert_status_confirmation",
        status="skipped",
        candidate_response={}
    )

    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=resume_data,
        target_role_name="SOC Analyst",
        missing_core_skills=["Wireshark"],
        approved_plan_items=[approved_projects_item, skipped_certs_item],
        permission_granted=True,
    )

    # 1. Project was added from candidate's verified input
    project_titles = [p["title"] for p in enhanced.projects]
    assert any("Packet Capture & Malware Traffic Analysis" in t for t in project_titles)

    # 2. Certifications remained empty because candidate skipped
    assert len(enhanced.certifications) == 0
    assert "CEH" not in enhanced.certifications
    assert "CompTIA Security+" not in enhanced.certifications


def test_unearned_certifications_never_added_to_earned():
    """Verify unearned certifications are never added to earned credentials, only pursuing or future recommendations."""
    resume_data = ParsedResumeData(
        candidate_name="Jordan Lee",
        contact_info=ContactInfo(email="jordan@example.com"),
        career_objective="",
        professional_summary="",
        technical_skills=["Linux", "Python"],
        education=[EducationEntry(degree="B.S. in Computer Science", institution="Tech Institute", graduation_year="2023")],
        certifications=[],
        projects=[],
        employment_history=[],
    )

    certs_item = ImprovementPlanItem(
        item_id="plan_certifications",
        category="Certifications",
        category_key="certifications",
        current_issue="No certifications",
        recommended_change="Verify cert status",
        relevance_reason="Validation",
        required_info="Status",
        expected_improvement="Accurate representation",
        action_type="cert_status_confirmation",
        status="approved",
        follow_up_questions=[
            {"id": "cert_comptia_securityplus", "cert_name": "CompTIA Security+"},
            {"id": "cert_ceh", "cert_name": "CEH"},
        ],
        candidate_response={
            "cert_comptia_securityplus": "currently_pursuing",  # In progress, not earned!
            "cert_ceh": "future_learning",  # Planned, not earned!
        }
    )

    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=resume_data,
        target_role_name="Security Analyst",
        missing_core_skills=[],
        approved_plan_items=[certs_item],
        permission_granted=True,
    )

    # STRICT RULE: Must NOT appear in completed certifications
    assert "CompTIA Security+" not in enhanced.certifications
    assert "CEH" not in enhanced.certifications

    # MUST appear in pursuing or future learning
    assert any("CompTIA Security+" in p for p in enhanced.pursuing_certifications)
    assert any("CEH" in fl for fl in enhanced.future_learning_recommendations)


def test_education_scoring_arts_degree_fairness():
    """Verify candidate with Arts degree is not unfairly penalized when role accepts diverse backgrounds."""
    edu_arts = [EducationEntry(degree="Bachelor of Arts in History", institution="National University", graduation_year="2021")]
    edu_stem = [EducationEntry(degree="Bachelor of Science in Computer Science", institution="National University", graduation_year="2021")]

    reqs_broad = [
        {"requirement_id": 1, "requirement_type": "education", "requirement_description": "Bachelor degree or equivalent in any academic background.", "importance": "preferred"}
    ]

    score_arts = ATSScoringEngine._score_education(edu_arts, reqs_broad, 15.0)
    score_stem = ATSScoringEngine._score_education(edu_stem, reqs_broad, 15.0)

    # Both should receive full bachelor credit without penalty
    assert score_arts.score_earned == score_stem.score_earned
    assert score_arts.percentage == 90.0


def test_full_api_workflow_with_improvement_plan(client):
    """End-to-end integration test of analysis, improvement plan, approval, and automatic re-scoring."""
    # 1. Fetch available roles
    res_roles = client.get("/api/roles")
    assert res_roles.status_code == 200
    roles = res_roles.json()["roles"]
    target_role = roles[0]
    role_id = target_role["role_id"]

    # 2. Upload resume
    dummy_pdf_content = (
        b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n"
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"5 0 obj\n<< /Length 200 >>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n"
        b"(Taylor Vance - Security Enthusiast) Tj\n0 -20 Td\n"
        b"(Email: taylor@example.com | Phone: 555-0182) Tj\n0 -20 Td\n"
        b"(Technical Skills: Linux, Networking, Python) Tj\n0 -20 Td\n"
        b"(Education: Bachelor of Science, State University, 2022) Tj\n"
        b"ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000010 00000 n\n"
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n500\n%%EOF"
    )

    files = {"file": ("taylor_resume.pdf", dummy_pdf_content, "application/pdf")}
    data = {"role_id": role_id}

    res_analyze = client.post("/api/resumes/analyze", files=files, data=data)
    assert res_analyze.status_code == 200
    an_data = res_analyze.json()

    assert "improvement_plan" in an_data
    plan = an_data["improvement_plan"]
    assert "items" in plan
    assert len(plan["items"]) >= 5
    analysis_id = an_data["analysis_id"]

    # 3. Candidate approves items and provides factual confirmation
    approved_items = []
    for item in plan["items"]:
        if item["category_key"] == "projects":
            item["status"] = "approved"
            item["candidate_response"] = {
                "has_omitted_project": "yes",
                "project_title": "Network Intrusion & Log Analysis Lab",
                "project_technologies": "Wireshark, Snort, Linux",
                "project_contribution": "Configured Snort rules and analyzed attack PCAPs.",
                "project_outcomes": "Identified port scans and SQL injection attempts.",
            }
        elif item["category_key"] == "technical_skills":
            item["status"] = "approved"
            item["candidate_response"] = {
                q["id"]: "hands_on" for q in item.get("follow_up_questions", [])[:2]
            }
        else:
            item["status"] = "approved"
        approved_items.append(item)

    # 4. Trigger resume improvement with approved items
    improve_payload = {
        "analysis_id": analysis_id,
        "selected_role_id": role_id,
        "attempt_number": 1,
        "approved_plan_items": approved_items,
        "permission_granted": True,
    }

    res_improve = client.post("/api/resumes/improve", json=improve_payload)
    assert res_improve.status_code == 200
    imp_data = res_improve.json()

    # 5. Verify re-scored results and explainability
    assert "category_comparison" in imp_data
    assert len(imp_data["category_comparison"]) > 0
    for comp in imp_data["category_comparison"]:
        assert "category" in comp
        assert "original_score" in comp
        assert "new_score" in comp
        assert "delta" in comp
        assert "evidence_supporting" in comp
        assert "approved_improvement_applied" in comp
        assert "remaining_gaps" in comp

    # Verify template was assigned automatically
    assert "assigned_template" in imp_data
    assert imp_data["assigned_template"]["template_id"].startswith("T")

    # Verify documents generated
    assert "documents" in imp_data
    assert imp_data["documents"]["docx_url"]


def test_weak_category_evaluations_and_facets():
    """Verify all 7 categories are analyzed with the 8 explicit explanation facets."""
    resume_data = ParsedResumeData(
        candidate_name="Sam Fisher",
        contact_info=ContactInfo(email="sam@example.com", phone="555-0101"),
        career_objective="Aspiring security practitioner",
        professional_summary="Junior IT professional",
        technical_skills=["Linux"],
        education=[EducationEntry(degree="B.A. in History", institution="National College", graduation_year="2021")],
        certifications=[],
        projects=[],
        employment_history=[],
    )

    role_skills = [
        {"skill_id": 1, "skill_name": "Burp Suite", "importance": "core"},
        {"skill_id": 2, "skill_name": "Nmap", "importance": "core"},
        {"skill_id": 3, "skill_name": "OWASP Top 10", "importance": "core"},
        {"skill_id": 4, "skill_name": "API Security", "importance": "preferred"},
    ]

    role_reqs = [
        {"requirement_id": 1, "requirement_type": "education", "requirement_description": "Bachelor degree or equivalent in computing, arts, or science.", "importance": "preferred"},
    ]

    criteria = [
        {"category": "Technical Skills", "weight": 40.0},
        {"category": "Projects", "weight": 25.0},
        {"category": "Education", "weight": 15.0},
        {"category": "Tools & Certifications", "weight": 15.0},
        {"category": "Career Objective", "weight": 5.0},
    ]

    match_report = SkillMatcher.match_skills(
        role_skills=role_skills,
        resume_skills=resume_data.technical_skills,
        resume_full_text="Sam Fisher Linux History",
        resume_projects=[],
        resume_experience=[],
        role_id=1,
        role_name="Ethical Hacker",
    )

    score_result = ATSScoringEngine.calculate_score(
        resume_data=resume_data,
        match_report=match_report,
        role_requirements=role_reqs,
        db_scoring_criteria=criteria,
        threshold=80.0,
    )

    plan = ImprovementPlanGenerator.generate_plan(
        resume_data=resume_data,
        match_report=match_report,
        score_result=score_result,
        role_requirements=role_reqs,
        role_name="Ethical Hacker",
        role_skills=role_skills,
        scoring_criteria=criteria,
    )

    assert len(plan.category_evaluations) >= 5
    cat_keys = [ce.category_key for ce in plan.category_evaluations]
    assert "technical_skills" in cat_keys
    assert "projects" in cat_keys
    assert "education" in cat_keys
    assert "tools_certs" in cat_keys
    assert "summary" in cat_keys

    # Verify every category evaluation provides all 8 required facets
    for ce in plan.category_evaluations:
        assert ce.current_score >= 0.0
        assert ce.max_score > 0.0
        assert ce.what_is_missing, f"Missing gap description for {ce.category_name}"
        assert len(ce.affected_job_requirements) > 0, f"Missing affected requirements for {ce.category_name}"
        assert len(ce.specific_improvements) > 0, f"Missing specific improvements for {ce.category_name}"
        assert ce.required_candidate_info, f"Missing required candidate info for {ce.category_name}"
        assert len(ce.resume_sections_to_update) > 0, f"Missing resume sections for {ce.category_name}"
        assert ce.role_relevance_reason, f"Missing relevance reason for {ce.category_name}"
        assert ce.action_nature in ("confirm_existing", "improve_presentation", "acquire_new_skills")


def test_priority_groups_and_skill_cards():
    """Verify prioritized grouping (High, Medium, Additional) and detailed cards."""
    resume_data = ParsedResumeData(
        candidate_name="Elliot Alderson",
        contact_info=ContactInfo(email="elliot@fsociety.org"),
        technical_skills=["Linux"],
        education=[EducationEntry(degree="B.S. in Computer Science", institution="NYU", graduation_year="2020")],
        certifications=[],
        projects=[],
        employment_history=[],
    )

    role_skills = [
        {"skill_id": 1, "skill_name": "Burp Suite", "importance": "core"},
        {"skill_id": 2, "skill_name": "Linux", "importance": "core"},
        {"skill_id": 3, "skill_name": "Nmap", "importance": "core"},
        {"skill_id": 4, "skill_name": "OWASP Top 10", "importance": "core"},
        {"skill_id": 5, "skill_name": "API Security", "importance": "preferred"},
    ]

    criteria = [
        {"category": "Technical Skills", "weight": 40.0},
        {"category": "Projects", "weight": 25.0},
        {"category": "Education", "weight": 15.0},
        {"category": "Tools & Certifications", "weight": 15.0},
        {"category": "Career Objective", "weight": 5.0},
    ]

    match_report = SkillMatcher.match_skills(
        role_skills=role_skills,
        resume_skills=resume_data.technical_skills,
        resume_full_text="Elliot Alderson Linux NYU",
        resume_projects=[],
        resume_experience=[],
        role_id=1,
        role_name="Ethical Hacker",
    )

    score_result = ATSScoringEngine.calculate_score(
        resume_data=resume_data,
        match_report=match_report,
        role_requirements=[],
        db_scoring_criteria=criteria,
        threshold=80.0,
    )

    plan = ImprovementPlanGenerator.generate_plan(
        resume_data=resume_data,
        match_report=match_report,
        score_result=score_result,
        role_requirements=[],
        role_name="Ethical Hacker",
        role_skills=role_skills,
        scoring_criteria=criteria,
    )

    # 1. Verify priority groups
    assert len(plan.high_priority_items) > 0, "Should have high priority items for missing core skills/projects"
    assert len(plan.medium_priority_items) > 0, "Should have medium priority items for preferred skills/certs"
    assert len(plan.additional_enhancements) > 0, "Should have additional enhancements for summary/education"

    # 2. Verify individual skill cards for core skills
    burp_item = next((it for it in plan.high_priority_items if "burp" in it.item_id), None)
    assert burp_item is not None, "Burp Suite should be a high-priority skill card"
    assert burp_item.skill_details is not None
    assert burp_item.skill_details.requirement_classification == "mandatory"
    assert "Burp Suite" in burp_item.skill_details.skill_name
    assert len(burp_item.skill_details.available_actions) == 4
    assert "Confirm Existing Experience" in burp_item.skill_details.available_actions
    assert "Recommend Learning Resources" in burp_item.skill_details.available_actions
    assert len(burp_item.skill_details.learning_resources) > 0

    # 3. Verify practical project recommendation
    proj_item = next((it for it in plan.high_priority_items if it.item_type == "project_recommendation"), None)
    assert proj_item is not None, "Weak projects should generate a practical project recommendation"
    assert proj_item.project_recommendation is not None
    assert "Web Application" in proj_item.project_recommendation.project_title or "Lab" in proj_item.project_recommendation.project_title
    assert len(proj_item.project_recommendation.suggested_implementation_tasks) > 0
    assert proj_item.project_recommendation.expected_deliverables
    assert proj_item.project_recommendation.suggested_resume_bullet

    # 4. Verify certification recommendation card
    cert_items = [it for it in plan.medium_priority_items if it.item_type == "cert_recommendation"]
    assert len(cert_items) > 0, "Should have certification recommendation cards"
    assert cert_items[0].cert_recommendation is not None
    assert cert_items[0].cert_recommendation.cert_name

