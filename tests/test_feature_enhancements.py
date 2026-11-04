"""Unit tests for FUTRSEC Feature Enhancements:
- Skill Proficiency ("No Experience Yet")
- Weakest Resume Areas (8 Categories with 6 required fields)
- Single Personalized Primary Project Recommendation
- Complete Project Implementation Plan (Sections A-J)
- DOCX and PDF Project Document Generation
- Completed Project Submission & 3-Tier Weakness Analysis (Green/Amber/Grey)
- Next Action Recommendation & Approval-Gated Resume Entry
- Education Scoring Rule (Configurable 3-point non-computing deduction)
"""

import os
from pathlib import Path
import pytest

from app.config import settings
from app.resume.extractor import ParsedResumeData, ContactInfo, EducationEntry, ProjectEntry
from app.scoring.matcher import SkillMatcher
from app.scoring.engine import ATSScoringEngine
from app.scoring.improvement_plan import ImprovementPlanGenerator
from app.projects.plan_generator import PrimaryProjectPlanGenerator
from app.projects.plan_renderer import ProjectPlanDocumentRenderer
from app.projects.evaluator import (
    CompletedProjectSubmission,
    CompletedProjectEvaluator,
)


@pytest.fixture
def sample_candidate_data():
    """Builds a realistic fresh graduate cybersecurity resume."""
    return ParsedResumeData(
        candidate_name="Alex Rivera",
        contact_info=ContactInfo(email="alex@example.com", phone="+1-555-0199", location="Austin, TX"),
        career_objective="Aspiring Ethical Hacker seeking entry-level security testing opportunities.",
        professional_summary="Passionate junior security enthusiast with foundational Linux and networking lab experience.",
        technical_skills=["Linux", "Wireshark", "Python", "TCP/IP"],
        certifications=[],
        education=[
            EducationEntry(
                degree="Bachelor of Arts in English Literature",
                institution="State University",
                graduation_year="2024",
                field_of_study="English Literature",
            )
        ],
        projects=[
            ProjectEntry(
                title="Home Network Traffic Capture",
                description="Analyzed local TCP/UDP packet streams using Wireshark and documented protocols.",
                technologies=["Wireshark", "Linux"],
                outcomes="Captured and inspected 5,000 packets to understand handshake sequences.",
            )
        ],
    )


@pytest.fixture
def sample_role_requirements():
    return [
        {"requirement_id": 1, "requirement_type": "education", "requirement_description": "Bachelor degree in Computer Science, Engineering, or relevant technical field preferred.", "importance": "mandatory"},
        {"requirement_id": 2, "requirement_type": "certification", "requirement_description": "Industry certification such as CEH, Security+, or PenTest+.", "importance": "preferred"},
        {"requirement_id": 3, "requirement_type": "experience", "requirement_description": "Demonstrated hands-on security assessment or CTF experience.", "importance": "mandatory"},
    ]


@pytest.fixture
def sample_role_skills():
    return [
        {"skill_id": 1, "skill_name": "Burp Suite", "importance": "core"},
        {"skill_id": 2, "skill_name": "OWASP Top 10", "importance": "core"},
        {"skill_id": 3, "skill_name": "Linux", "importance": "core"},
        {"skill_id": 4, "skill_name": "Python", "importance": "core"},
        {"skill_id": 5, "skill_name": "Nmap", "importance": "preferred"},
        {"skill_id": 6, "skill_name": "Metasploit", "importance": "preferred"},
        {"skill_id": 7, "skill_name": "API Security", "importance": "additional"},
    ]


def test_education_scoring_rule_deduction(sample_candidate_data, sample_role_requirements, sample_role_skills):
    """Test Section 11: Arts / Non-computing degree receives 3-point deduction transparently."""
    match_report = SkillMatcher.match_skills(
        role_skills=sample_role_skills,
        resume_skills=sample_candidate_data.technical_skills,
        resume_full_text=sample_candidate_data.career_objective + " " + " ".join(sample_candidate_data.technical_skills),
        resume_projects=sample_candidate_data.projects,
        resume_experience=sample_candidate_data.employment_history,
        role_id=1,
        role_name="Ethical Hacker",
    )
    score_result = ATSScoringEngine.calculate_score(
        resume_data=sample_candidate_data,
        match_report=match_report,
        role_requirements=sample_role_requirements,
        db_scoring_criteria=[],
    )

    edu_score = next(c for c in score_result.category_scores if c.category_name == "Education")
    assert edu_score.details.get("education_deduction_applied") is True
    assert edu_score.details.get("education_deduction_pts") == settings.NON_COMPUTING_EDUCATION_DEDUCTION
    assert "Arts/Non-Computing" in edu_score.explanation
    assert "-3.0" in edu_score.explanation or "-3" in edu_score.explanation


def test_education_scoring_rule_stem_full_credit(sample_role_requirements, sample_role_skills):
    """Test Section 11: Computing / Engineering degrees receive full credit without deduction."""
    stem_candidate = ParsedResumeData(
        candidate_name="Sam Tech",
        contact_info=ContactInfo(email="sam@example.com"),
        technical_skills=["Linux", "Python"],
        education=[
            EducationEntry(
                degree="Bachelor of Engineering in Computer Science",
                institution="Tech University",
                graduation_year="2024",
                field_of_study="Computer Science",
            )
        ],
        projects=[],
    )
    match_report = SkillMatcher.match_skills(
        role_skills=sample_role_skills,
        resume_skills=stem_candidate.technical_skills,
        resume_full_text="Linux Python Computer Science Engineering",
        resume_projects=[],
        resume_experience=[],
        role_id=1,
        role_name="Ethical Hacker",
    )
    score_result = ATSScoringEngine.calculate_score(
        resume_data=stem_candidate,
        match_report=match_report,
        role_requirements=sample_role_requirements,
        db_scoring_criteria=[],
    )

    edu_score = next(c for c in score_result.category_scores if c.category_name == "Education")
    assert edu_score.details.get("is_stem") is True
    assert edu_score.details.get("education_deduction_applied") is False
    assert edu_score.score_earned == edu_score.weight  # 15.0 / 15.0


def test_weakest_resume_areas_all_8_categories(sample_candidate_data, sample_role_requirements, sample_role_skills):
    """Test Section 2: Evaluate all 8 categories with the 6 required fields."""
    match_report = SkillMatcher.match_skills(
        role_skills=sample_role_skills,
        resume_skills=sample_candidate_data.technical_skills,
        resume_full_text=sample_candidate_data.career_objective + " " + " ".join(sample_candidate_data.technical_skills),
        resume_projects=sample_candidate_data.projects,
        resume_experience=sample_candidate_data.employment_history,
        role_id=1,
        role_name="Ethical Hacker",
    )
    score_result = ATSScoringEngine.calculate_score(
        resume_data=sample_candidate_data,
        match_report=match_report,
        role_requirements=sample_role_requirements,
        db_scoring_criteria=[],
    )
    plan = ImprovementPlanGenerator.generate_plan(
        resume_data=sample_candidate_data,
        match_report=match_report,
        score_result=score_result,
        role_requirements=sample_role_requirements,
        role_name="Ethical Hacker",
        role_skills=sample_role_skills,
    )

    assert len(plan.category_evaluations) == 8
    expected_categories = [
        "Technical Skills",
        "Projects",
        "Education",
        "Tools and Certifications",
        "Professional Summary or Career Objective",
        "Work Experience and Internships",
        "Relevant Achievements and Supporting Evidence",
        "Resume Organization and ATS Readability",
    ]

    for cat in plan.category_evaluations:
        assert cat.category_name in expected_categories
        # 1. Current score and max score
        assert cat.current_score is not None
        assert cat.max_score is not None
        # 2. Main weakness
        assert len(cat.what_is_missing) > 0
        # 3. Why the weakness matters for role
        assert len(cat.role_relevance_reason) > 0
        # 4. Specific improvement recommendation
        assert len(cat.specific_improvements) > 0
        # 5. Whether candidate confirmation is needed
        assert isinstance(cat.confirmation_needed, bool)
        # 6. Recommended next action
        assert len(cat.recommended_next_action) > 0


def test_single_personalized_project_recommendation(sample_candidate_data, sample_role_requirements, sample_role_skills):
    """Test Section 3 & 4: Exactly one primary project recommendation with sections A through J."""
    plan = PrimaryProjectPlanGenerator.generate_single_plan(
        role_name="Ethical Hacker",
        unmatched_skills=["Burp Suite", "OWASP Top 10", "Nmap"],
        matched_skills=["Linux", "Python"],
        existing_projects_count=1,
    )

    # Section A: Project Overview
    assert plan.overview.project_title
    assert plan.overview.target_role == "Ethical Hacker"
    assert plan.overview.difficulty in ("Beginner", "Intermediate", "Advanced")
    assert plan.overview.problem_statement
    assert plan.overview.project_objective
    assert plan.overview.relevance_to_role
    assert len(plan.overview.weaknesses_addressed) > 0

    # Section B: Skills Breakdown
    assert len(plan.skills.existing_skills_applied) > 0
    assert len(plan.skills.skills_to_be_learned) > 0
    assert len(plan.skills.all_targeted_skills) > 0

    # Section C: Tech Stack
    assert len(plan.technology_stack) >= 4
    assert "Burp Suite Community Edition" in plan.technology_stack or "Burp Suite" in str(plan.technology_stack)

    # Section D: Implementation Phases
    assert len(plan.phases) >= 3
    for phase in plan.phases:
        assert phase.phase_number > 0
        assert phase.title
        assert phase.objective
        assert len(phase.tasks) > 0
        assert phase.expected_output
        assert phase.verification_method

    # Section E: Project Structure
    assert len(plan.project_structure) >= 4
    assert any("README.md" in item.path for item in plan.project_structure)

    # Section F: Deliverables
    assert len(plan.final_deliverables) >= 4

    # Section G: Testing & Validation
    assert len(plan.testing_and_validation) >= 2
    # Verify authorized testing emphasis
    assert any("authorized" in rule.lower() for rule in plan.testing_and_validation)

    # Section H: Learning Outcomes
    assert len(plan.learning_outcomes) >= 3

    # Section I: Resume Guide
    assert plan.resume_documentation_guide.framework
    assert len(plan.resume_documentation_guide.sample_bullets) >= 2

    # Section J: GitHub Guide
    assert len(plan.github_and_presentation) >= 2
    # Verify security caution: no passwords/API keys
    assert any("never" in g.lower() or "caution" in g.lower() or "password" in g.lower() for g in plan.github_and_presentation)


def test_docx_and_pdf_document_generation():
    """Test Section 5: Real DOCX and PDF documents generated with real file paths."""
    plan = PrimaryProjectPlanGenerator.generate_single_plan(
        role_name="SOC Analyst",
        unmatched_skills=["Splunk", "Snort"],
        matched_skills=["Wireshark"],
        plan_id="test_soc_plan_doc",
    )

    doc_meta = ProjectPlanDocumentRenderer.render_plan_documents(plan)
    assert doc_meta["docx_path"]
    assert Path(doc_meta["docx_path"]).exists()
    assert Path(doc_meta["docx_path"]).stat().st_size > 500

    assert doc_meta["pdf_available"] is True
    assert doc_meta["pdf_path"]
    assert Path(doc_meta["pdf_path"]).exists()
    assert Path(doc_meta["pdf_path"]).stat().st_size > 500


def test_completed_project_submission_and_weakness_analysis():
    """Test Section 6, 7, 8, 9: Completed project submission, 3-tier weakness analysis, next action, and approval entry."""
    submission = CompletedProjectSubmission(
        project_title="OWASP Juice Shop Vulnerability Assessment",
        project_description="Conducted black-box security testing on a local OWASP Juice Shop Docker container.",
        skills_used=["Burp Suite", "OWASP Top 10", "SQL Injection"],
        technologies_used=["Burp Suite Community", "Docker", "Python"],
        implementation_tasks_completed=[
            "Deployed Juice Shop container locally via Docker on port 3000.",
            "Configured Burp Suite intercepting proxy to map application endpoints.",
            "Verified SQL Injection vulnerability on login authentication endpoint.",
        ],
        testing_performed="Verified SQLi payload in Burp Repeater against local test sandbox; captured HTTP 200 responses with authentication bypass.",
        verified_outcomes="Documented 3 verified vulnerabilities in formal report with CVSS v3.1 severity scores and developer remediation steps.",
        status="completed",
        github_url="https://github.com/alexrivera/juiceshop-security-assessment",
        documentation_notes="Complete setup instructions and sanitized findings included in README.md.",
        confirmation_statement=True,
    )

    result = CompletedProjectEvaluator.evaluate_submission(submission, target_role="Ethical Hacker")

    # Section 7: Three clear categories
    assert len(result.demonstrated) > 0  # Green
    assert isinstance(result.improvement_needed, list)  # Amber
    assert isinstance(result.not_yet_submitted, list)  # Grey

    # Section 8: Single recommended next action
    assert result.recommended_next_action
    assert isinstance(result.recommended_next_action, str)

    # Section 9: Proposed resume entry format
    entry = result.proposed_resume_entry
    assert "OWASP Juice Shop" in entry.title_line
    assert "|" in entry.title_line or entry.title_line == submission.project_title
    assert len(entry.bullets) == 4
    assert any("Developed:" in b for b in entry.bullets)
    assert any("Used:" in b for b in entry.bullets)
    assert any("Tested:" in b for b in entry.bullets)
    assert any("Achieved:" in b for b in entry.bullets)
    assert entry.is_approved is False
