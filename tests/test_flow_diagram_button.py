"""Tests for View Flow Diagram button functionality, distinct project workflows,
browser SVG rendering, and preservation of existing PDF/DOCX downloads.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.projects.plan_generator import PrimaryProjectPlanGenerator
import fitz


@pytest.fixture
def client():
    return TestClient(app)


def test_enterprise_network_hardening_workflow_spec():
    """Verify that Enterprise Network Hardening & Vulnerability Remediation Lab

    has the exact specified workflow with decision branches and loop reconnection.
    """
    plan = PrimaryProjectPlanGenerator._build_network_security_plan(
        plan_id="plan_net_test",
        generated_date="October 29, 2026",
        role_name="Network Security Engineer",
        difficulty="Intermediate",
        unmatched_skills=["iptables", "OpenVAS"],
        matched_skills=["Linux"],
    )

    workflow = plan.project_workflow
    assert workflow is not None, "Workflow must be defined on project plan"
    assert len(workflow) >= 10, "Workflow must contain all implementation stages"

    labels = [step["label"] for step in workflow]

    # Verify stage progression
    assert "START" in labels[0]
    assert "Virtual Network Setup" in labels
    assert "Deploy Ubuntu Server VMs" in labels
    assert "Configure Network and Verify Connectivity" in labels
    assert "Nmap Reconnaissance" in labels
    assert "OpenVAS Vulnerability Assessment" in labels
    assert "Linux Hardening and Firewall Configuration" in labels
    assert "Post-Hardening Security Validation" in labels
    assert "Generate Security Assessment Report" in labels
    assert "END" in labels[-1]

    # Verify decision node and branches
    decision_steps = [s for s in workflow if s.get("type") == "decision"]
    assert len(decision_steps) == 1, "Must contain exactly one decision node"
    dec = decision_steps[0]

    assert dec["label"] == "Are security requirements satisfied?"
    assert dec["no_action"] == "Review findings and perform further hardening."
    assert dec["yes_action"] == "Document verified results."

    # Verify NO branch reconnection to the hardening stage
    target_step_num = dec["no_target_step"]
    target_step = next(s for s in workflow if s["step"] == target_step_num)
    assert "Hardening" in target_step["label"] or target_step.get("is_loop_target") is True


def test_different_projects_have_distinct_workflows():
    """Verify that different projects generate distinct workflows matching their actual implementation plan."""
    net_plan = PrimaryProjectPlanGenerator._build_network_security_plan(
        "p1", "date", "Network Security", "Intermediate", [], []
    )
    web_plan = PrimaryProjectPlanGenerator._build_ethical_hacker_plan(
        "p2", "date", "Ethical Hacker", "Intermediate", [], []
    )
    soc_plan = PrimaryProjectPlanGenerator._build_soc_analyst_plan(
        "p3", "date", "SOC Analyst", "Intermediate", [], []
    )
    cloud_plan = PrimaryProjectPlanGenerator._build_cloud_security_plan(
        "p4", "date", "Cloud Security", "Intermediate", [], []
    )
    appsec_plan = PrimaryProjectPlanGenerator._build_appsec_plan(
        "p5", "date", "Application Security", "Intermediate", [], []
    )

    net_labels = [s["label"] for s in net_plan.project_workflow]
    web_labels = [s["label"] for s in web_plan.project_workflow]
    soc_labels = [s["label"] for s in soc_plan.project_workflow]
    cloud_labels = [s["label"] for s in cloud_plan.project_workflow]
    appsec_labels = [s["label"] for s in appsec_plan.project_workflow]

    # Workflows must be distinct
    assert net_labels != web_labels
    assert net_labels != soc_labels
    assert web_labels != cloud_labels
    assert soc_labels != appsec_labels

    # Role-specific content checks
    assert any("Virtual Network" in l for l in net_labels)
    assert any("Docker" in l or "Burp" in l for l in web_labels)
    assert any("SIEM" in l or "Splunk" in l for l in soc_labels)
    assert any("Cloud" in l or "Terraform" in l for l in cloud_labels)
    assert any("CI/CD" in l or "SAST" in l for l in appsec_labels)


def test_api_workflow_endpoint(client):
    """Verify the /api/projects/workflow endpoint returns the correct workflow specification."""
    # Test Enterprise Network Hardening
    res1 = client.get("/api/projects/workflow?title=Enterprise Network Hardening %26 Vulnerability Remediation Lab")
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["project_title"] == "Enterprise Network Hardening & Vulnerability Remediation Lab"
    assert len(data1["workflow"]) >= 10
    dec = next(s for s in data1["workflow"] if s.get("type") == "decision")
    assert dec["label"] == "Are security requirements satisfied?"
    assert dec["no_action"] == "Review findings and perform further hardening."

    # Test Web Application Security
    res2 = client.get("/api/projects/workflow?title=Web Application Security Testing Lab %26 Vulnerability Remediation")
    assert res2.status_code == 200
    data2 = res2.json()
    assert len(data2["workflow"]) >= 7
    assert data1["workflow"] != data2["workflow"]


def test_project_plan_pdf_does_not_contain_diagrams(client):
    """Verify that project implementation plan PDF generation remains clean and text-based

    without embedding flow diagrams, as required.
    """
    res = client.get("/api/projects/download-plan/plan_test_nodir/pdf")
    assert res.status_code == 200
    pdf_bytes = res.content
    assert pdf_bytes.startswith(b"%PDF-")

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    assert len(doc) >= 1

    # Ensure zero images in the PDF document
    for page in doc:
        assert len(page.get_images()) == 0, "Implementation plan PDF must not contain embedded diagram images"


def test_project_plan_docx_download_intact(client):
    """Verify that DOCX plan download endpoint continues to function normally."""
    res = client.get("/api/projects/download-plan/plan_test_docx/docx")
    assert res.status_code == 200
    assert res.content.startswith(b"PK\x03\x04")

