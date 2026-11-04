import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from app.main import app
from app.projects.plan_generator import PrimaryProjectPlanGenerator
from app.projects.plan_renderer import ProjectPlanDocumentRenderer
from app.projects.evaluator import (
    CompletedProjectSubmission,
    CompletedProjectEvaluator,
)

client = TestClient(app)

def test_view_plan_pdf_endpoint():
    """Verify GET /api/projects/view-plan/{plan_id} returns an inline PDF with correct headers and valid magic bytes."""
    # 1. Generate a project plan
    plan = PrimaryProjectPlanGenerator.generate_single_plan(
        role_name="Security Operations Center (SOC) Analyst",
        unmatched_skills=["SIEM", "Log Analysis", "Wireshark"],
        matched_skills=["Linux"],
        existing_projects_count=0
    )
    doc_meta = ProjectPlanDocumentRenderer.render_plan_documents(plan)
    plan_id = plan.plan_id
    assert plan_id is not None

    # 2. Call view-plan endpoint
    response = client.get(f"/api/projects/view-plan/{plan_id}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "inline" in response.headers["content-disposition"]
    assert f'filename="FUTRSEC_Project_Plan_{plan_id}.pdf"' in response.headers["content-disposition"]
    
    # Verify magic bytes of PDF
    assert response.content.startswith(b"%PDF-")
    assert len(response.content) > 500


def test_view_plan_regenerates_if_file_missing():
    """Verify that if the PDF file is removed from disk, view-plan regenerates it on the fly rather than 404ing."""
    plan = PrimaryProjectPlanGenerator.generate_single_plan(
        role_name="SOC Analyst",
        unmatched_skills=["OWASP Top 10", "Burp Suite", "SAST"],
        matched_skills=["Python"],
        existing_projects_count=1
    )
    doc_meta = ProjectPlanDocumentRenderer.render_plan_documents(plan)
    plan_id = plan.plan_id
    pdf_path = Path(doc_meta["pdf_path"])
    
    # Delete the PDF file on disk
    if pdf_path.exists():
        pdf_path.unlink()
    assert not pdf_path.exists()

    # Call view-plan - should regenerate on the fly
    response = client.get(f"/api/projects/view-plan/{plan_id}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF-")


def test_download_plan_disposition_param():
    """Verify that download-plan supports disposition=inline or attachment."""
    plan = PrimaryProjectPlanGenerator.generate_single_plan(
        role_name="SOC Analyst",
        unmatched_skills=["AWS IAM", "CloudTrail", "Terraform"],
        matched_skills=[],
        existing_projects_count=0
    )
    ProjectPlanDocumentRenderer.render_plan_documents(plan)
    plan_id = plan.plan_id

    # Test attachment (default)
    res_attach = client.get(f"/api/projects/download-plan/{plan_id}/pdf")
    assert res_attach.status_code == 200
    assert "attachment" in res_attach.headers["content-disposition"]

    # Test inline
    res_inline = client.get(f"/api/projects/download-plan/{plan_id}/pdf?disposition=inline")
    assert res_inline.status_code == 200
    assert "inline" in res_inline.headers["content-disposition"]


def test_project_weakness_evaluation_and_approved_project():
    """Verify candidate project submission weakness evaluation and candidate approval into resume."""
    # Test submission
    submission = CompletedProjectSubmission(
        project_title="Automated SOC Log Pipeline",
        project_description="Developed a centralized log ingestion and alerting pipeline using Python, Elasticsearch, and Suricata for threat detection.",
        github_url="https://github.com/candidate/soc-log-pipeline",
        technologies_used=["Python", "Elasticsearch", "Suricata", "Docker"],
        implementation_tasks_completed=["Parsed syslog events", "Configured Suricata IDS rules", "Built dashboard alerts"]
    )
    
    analysis = CompletedProjectEvaluator.evaluate_submission(submission, target_role="Security Operations Center (SOC) Analyst")
    assert analysis.verdict in ["suitable", "acceptable", "needs_revision", "inconclusive_evidence"]
    assert len(analysis.demonstrated) > 0
    assert analysis.proposed_resume_entry is not None
    assert "Automated SOC Log Pipeline" in analysis.proposed_resume_entry.title_line

    # Test that proposed resume entry has bullets and tech stack
    entry = analysis.proposed_resume_entry
    assert len(entry.bullets) >= 1
