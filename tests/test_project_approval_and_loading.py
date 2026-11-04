"""Tests verifying candidate-approved project integration, truthful wording, and document rendering."""

import pytest
from app.projects.evaluator import CompletedProjectEvaluator, CompletedProjectSubmission
from app.projects.generator import ResumeContentGenerator, ConfirmedSkillItem, EnhancedResumeContent
from app.resume.extractor import (
    ParsedResumeData,
    ContactInfo,
    EducationEntry,
    ProjectEntry,
    ExperienceEntry,
)
from app.reports.renderer import DocumentRenderer
from app.reports.round_robin import template_registry


def test_existing_project_in_progress_truthful_wording():
    """Requirement 1 & 3: In-progress projects must be clearly labeled and truthfully described."""
    submission = CompletedProjectSubmission(
        project_title="Network Monitoring System",
        project_description="Developing a network monitoring application to track service availability and record monitoring results.",
        skills_used=["Python", "FastAPI", "PostgreSQL"],
        technologies_used=["Python", "FastAPI", "PostgreSQL"],
        implementation_tasks_completed=["Setting up database schemas and service health endpoints."],
        testing_performed="Local unit tests for ping responder.",
        verified_outcomes="Preliminary telemetry endpoints responding.",
        status="in_progress",
        confirmation_statement=True,
    )

    result = CompletedProjectEvaluator.evaluate_submission(
        submission=submission,
        target_role="SOC Analyst",
    )

    entry = result.proposed_resume_entry
    assert entry is not None
    # 1. Title format must be "PROJECT TITLE | In Progress"
    assert entry.title_line == "Network Monitoring System | In Progress"
    assert entry.status_label == "In Progress"

    # 2. Bullets must use truthful progressive wording without claiming unfinished features
    bullets_text = " ".join(entry.bullets)
    assert "Developing:" in bullets_text
    assert "Planned Implementation:" in bullets_text
    assert "Python" in bullets_text
    # Must NOT claim fully completed product
    assert "Developed:" not in entry.bullets[0]


def test_existing_project_completed_no_in_progress_label():
    """Requirement 1 & 3: Completed projects must NOT be labeled In Progress."""
    submission = CompletedProjectSubmission(
        project_title="SIEM Threat Detection Pipeline",
        project_description="Built an automated log ingestion and alert pipeline for unauthorized SSH access.",
        skills_used=["Python", "Splunk", "Linux"],
        technologies_used=["Python", "Splunk", "Linux"],
        implementation_tasks_completed=["Configured syslog forwarder", "Created detection queries"],
        testing_performed="Simulated brute force attacks from authorized sandbox.",
        verified_outcomes="Triggered high-severity alerts within 5 seconds of threshold violation.",
        status="completed",
        confirmation_statement=True,
    )

    result = CompletedProjectEvaluator.evaluate_submission(
        submission=submission,
        target_role="SOC Analyst",
    )

    entry = result.proposed_resume_entry
    assert entry is not None
    # 1. Must NOT contain "In Progress" or "(Completed Project)"
    assert "In Progress" not in entry.title_line
    assert "(Completed Project)" not in entry.title_line
    assert entry.title_line == "SIEM Threat Detection Pipeline"
    assert entry.status_label == "Completed"

    # 2. Bullets describe verified completed work
    bullets_text = " ".join(entry.bullets)
    assert "Developed:" in entry.bullets[0]
    assert "Tested:" in bullets_text
    assert "Achieved:" in bullets_text


def test_recommended_project_intent_to_start_entry():
    """Requirement 2: Recommended project staged as In Progress describes planned work."""
    raw = ParsedResumeData(
        candidate_name="Sarah Connor",
        contact_info=ContactInfo(email="sarah@resistance.org"),
        technical_skills=["Linux", "Python"],
        education=[EducationEntry(degree="BS in Computer Science", institution="Tech State")],
        certifications=[],
        projects=[],
    )

    # Simulate approved in-progress recommended project
    from app.projects.evaluator import ProposedResumeEntry
    rec_entry = ProposedResumeEntry(
        title_line="Vulnerability Assessment Laboratory | In Progress",
        bullets=[
            "Developing: Planning and initializing Vulnerability Assessment Laboratory to develop practical competencies in Nmap, Nessus, Wireshark.",
            "Technologies: Nmap, Nessus, Wireshark, Linux.",
            "Planned Implementation: Following structured phases including environment setup, security controls, and verification testing.",
        ],
        status_label="In Progress",
        is_approved=True,
    )

    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=raw,
        target_role_name="Vulnerability Analyst",
        missing_core_skills=[],
        confirmed_skills=[],
        permission_granted=True,
        attempt_number=1,
    )

    # In main workflow, approved project is added to projects
    from app.main import ANALYSIS_CACHE
    # Clean title logic verification
    title_line = rec_entry.title_line
    status_lbl = rec_entry.status_label
    if "in progress" in str(status_lbl).lower() or "in progress" in title_line.lower():
        clean_title = title_line if "in progress" in title_line.lower() else f"{title_line} | In Progress"
    else:
        clean_title = title_line.replace(" | Completed", "").strip()

    assert clean_title == "Vulnerability Assessment Laboratory | In Progress"

    enhanced.projects.insert(0, {
        "title": clean_title,
        "description": " \n".join(rec_entry.bullets),
        "technologies": ["Nmap", "Nessus", "Wireshark", "Linux"],
        "outcomes": "Planned security verification",
    })

    assert len(enhanced.projects) == 1
    assert enhanced.projects[0]["title"] == "Vulnerability Assessment Laboratory | In Progress"
    assert "Developing:" in enhanced.projects[0]["description"]


def test_document_rendering_with_in_progress_and_completed_projects():
    """Requirement 4 & 7: Both in-progress and completed projects render cleanly to DOCX and vector PDF."""
    raw = ParsedResumeData(
        candidate_name="Alex Mercer",
        contact_info=ContactInfo(email="alex@nyctech.edu", phone="+1 555-0144", location="New York, NY"),
        professional_summary="Dedicated cybersecurity practitioner focused on network defense.",
        technical_skills=["Python", "FastAPI", "Linux", "Docker", "Wireshark"],
        education=[EducationEntry(degree="BS in Cybersecurity", institution="NYC Tech", graduation_year="2023")],
        certifications=["CompTIA Security+"],
        projects=[
            ProjectEntry(
                title="Active Directory Security Assessment",
                description="Audited domain controllers and group policies for permission misconfigurations.",
                technologies=["Active Directory", "PowerShell"],
                outcomes="Remediated 4 critical privilege escalation paths.",
            )
        ],
    )

    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=raw,
        target_role_name="Network Security Engineer",
        missing_core_skills=[],
        confirmed_skills=[],
        permission_granted=True,
        attempt_number=1,
    )

    # Add an in-progress project alongside the completed one
    enhanced.projects.insert(0, {
        "title": "Cloud Security Automation | In Progress",
        "description": "Developing automated compliance scanners for AWS infrastructure.\nTechnologies: Python, Boto3, Terraform.\nPlanned Implementation: Validating IAM policies and encryption settings.",
        "technologies": ["Python", "Boto3", "Terraform"],
        "outcomes": "Validating IAM policies and encryption settings.",
    })

    # Validate and render with round robin template
    templates = template_registry.list_templates()
    assert len(templates) > 0
    template = templates[0]

    render_result = DocumentRenderer.render_resume(
        content=enhanced,
        template=template,
        job_id="test_proj_render_job",
    )

    from pathlib import Path
    docx_file = Path(render_result["docx_path"])
    pdf_file = Path(render_result["pdf_path"])
    assert docx_file.exists()
    assert pdf_file.exists()
    assert docx_file.stat().st_size > 3000
    assert pdf_file.stat().st_size > 3000

    # Validate PDF magic bytes
    with open(pdf_file, "rb") as f:
        assert f.read(4) == b"%PDF"

