"""Tests for the Project Completion Tracking System in FUTRSEC AI Resume Engine.

Verifies:
1. Recommendation of cybersecurity projects based on candidate skills and role.
2. Candidate acceptance and rejection of recommended projects.
3. Assignment of milestones, measurable tasks, and deadlines.
4. Task completion progress updates and dynamic completion percentage calculation.
5. Evidence submission with GitHub URL validation and report documentation.
6. Admin and AI evidence verification (approval, revision requests, rejection).
7. Strict 6 project statuses: Not Started, In Progress, Submitted, Under Review, Revision Required, Completed.
8. Dashboard metrics aggregation.
9. Strict resume integration: only verified completed projects are eligible for resumes; uncompleted projects are excluded.
10. Assignment deletion and cleanup.
"""

import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.projects.tracking import (
    project_tracking_service,
    ProjectAssignmentInput,
    MilestoneEvidenceSubmission,
    VerificationReviewInput,
)

client = TestClient(app)


@pytest.fixture
def test_candidate_id():
    """Generates an isolated unique candidate ID for testing."""
    cid = f"test_cand_{uuid.uuid4().hex[:8]}"
    yield cid
    # Teardown: ensure any test projects are cleaned up
    try:
        projects = project_tracking_service.get_candidate_projects(cid)
        for p in projects:
            project_tracking_service.delete_candidate_project(p["id"])
    except Exception:
        pass


def test_project_recommendations_ranking():
    """Tests that project recommendations are ranked by relevance to target job role and skill gaps."""
    res = client.get(
        "/api/tracking/recommendations",
        params={
            "role_name": "Ethical Hacker",
            "candidate_skills": ["Python", "Linux"],
            "unmatched_skills": ["Metasploit", "Burp Suite", "OWASP Top 10"],
        },
    )
    assert res.status_code == 200
    recommendations = res.json()
    assert len(recommendations) > 0

    top = recommendations[0]
    assert "project_id" in top
    assert "project_title" in top
    assert "relevance_score" in top
    assert "match_reasons" in top
    assert "phases_preview" in top
    assert top["relevance_score"] > 0
    # Higher rank should have higher or equal relevance score
    for i in range(len(recommendations) - 1):
        assert recommendations[i]["relevance_score"] >= recommendations[i + 1]["relevance_score"]


def test_reject_project_recommendation(test_candidate_id):
    """Tests candidate rejecting a recommended project."""
    res = client.post(
        "/api/tracking/reject",
        json={
            "candidate_id": test_candidate_id,
            "project_id": "CS-01",
            "reason": "Already completed similar lab in university coursework",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "rejected"
    assert data["project_id"] == "CS-01"
    assert "declined" in data["reason"].lower() or "completed" in data["reason"].lower()


def test_project_assignment_lifecycle(test_candidate_id):
    """Tests the full assignment lifecycle: assignment, tasks, milestones, evidence, and verification."""
    # 1. Assign project
    assign_res = client.post(
        "/api/tracking/assign",
        json={
            "candidate_id": test_candidate_id,
            "project_id": "CS-01",
            "role_name": "Ethical Hacker",
            "candidate_name": "Test Candidate",
            "custom_deadline_days": 28,
        },
    )
    assert assign_res.status_code == 200
    project = assign_res.json()
    project_id = project["id"]
    assert project["candidate_id"] == test_candidate_id
    assert project["status"] in ("In Progress", "Not Started")
    assert project["completion_percentage"] == 0.0
    assert len(project["milestones"]) >= 3

    # Check first milestone and tasks
    m1 = project["milestones"][0]
    assert m1["milestone_number"] == 1
    assert m1["total_tasks_count"] > 0
    assert len(m1["tasks"]) == m1["total_tasks_count"]
    first_task = m1["tasks"][0]
    assert first_task["is_completed"] is False

    # 2. Update task progress
    task_res = client.post(
        "/api/tracking/tasks/update",
        json={
            "candidate_project_id": project_id,
            "milestone_id": m1["id"],
            "task_id": first_task["id"],
            "is_completed": True,
        },
    )
    assert task_res.status_code == 200
    task_data = task_res.json()
    assert task_data["is_completed"] is True
    assert task_data["milestone_completed_tasks"] == 1
    assert task_data["project_completion_percentage"] > 0.0

    # 3. Evidence Submission: invalid GitHub URL should be rejected
    bad_evidence_res = client.post(
        "/api/tracking/evidence/submit",
        json={
            "candidate_project_id": project_id,
            "milestone_id": m1["id"],
            "evidence_type": "github_repo",
            "github_url": "https://notgithub.com/bad/repo",
            "report_text": "Completed tasks for phase 1",
        },
    )
    assert bad_evidence_res.status_code == 400

    # 4. Evidence Submission: valid GitHub URL and report text
    good_evidence_res = client.post(
        "/api/tracking/evidence/submit",
        json={
            "candidate_project_id": project_id,
            "milestone_id": m1["id"],
            "evidence_type": "github_repo",
            "github_url": "https://github.com/testcandidate/ethical-hacker-lab",
            "report_text": "Successfully deployed isolated Docker container lab and verified network segmentation.",
            "notes": "All phase 1 acceptance criteria met.",
        },
    )
    assert good_evidence_res.status_code == 200
    ev_data = good_evidence_res.json()
    assert ev_data["status"] == "Submitted"
    assert "evidence_id" in ev_data

    # Check project details reflects submission
    detail_res = client.get(f"/api/tracking/project/{project_id}")
    assert detail_res.status_code == 200
    det = detail_res.json()
    assert det["milestones"][0]["status"] == "Submitted"
    assert len(det["milestones"][0]["evidence"]) >= 1

    # 5. Verification Review: Revision Required flow
    rev_res = client.post(
        "/api/tracking/verify",
        json={
            "candidate_project_id": project_id,
            "milestone_id": m1["id"],
            "verdict": "revision_required",
            "score": 65.0,
            "feedback": "Docker container requires explicit firewall rule isolation.",
            "revision_instructions": "Add iptables drop rules and re-submit proof.",
            "reviewer_name": "Lead Security Auditor",
        },
    )
    assert rev_res.status_code == 200
    rev_data = rev_res.json()
    assert rev_data["status"] == "Revision Required"
    assert rev_data["project_status"] == "Revision Required"

    # Verify that milestone is marked Revision Required
    detail_res2 = client.get(f"/api/tracking/project/{project_id}")
    assert detail_res2.json()["milestones"][0]["status"] == "Revision Required"

    # 6. Verification Review: Approval flow
    approve_res = client.post(
        "/api/tracking/verify",
        json={
            "candidate_project_id": project_id,
            "milestone_id": m1["id"],
            "verdict": "approved",
            "score": 95.0,
            "feedback": "Iptables drop rules implemented and verified successfully.",
            "reviewer_name": "Lead Security Auditor",
        },
    )
    assert approve_res.status_code == 200
    app_data = approve_res.json()
    assert app_data["status"] == "Completed"

    # 7. AI Automated Verification endpoint test
    # Submit evidence for milestone 2
    m2 = det["milestones"][1]
    client.post(
        "/api/tracking/evidence/submit",
        json={
            "candidate_project_id": project_id,
            "milestone_id": m2["id"],
            "evidence_type": "github_repo",
            "github_url": "https://github.com/testcandidate/ethical-hacker-lab",
            "report_text": "Executed Nmap scans, identified OWASP top 10 injection vulnerabilities, documented proof of concept.",
        },
    )
    ai_verify_res = client.post(
        "/api/tracking/ai-verify",
        json={
            "candidate_project_id": project_id,
            "milestone_id": m2["id"],
        },
    )
    assert ai_verify_res.status_code == 200
    ai_data = ai_verify_res.json()
    assert ai_data["verdict"] in ("approved", "revision_required")
    assert "feedback" in ai_data


def test_resume_integration_strict_verification_rule(test_candidate_id):
    """Strict Rule: Only projects that are verified completed are eligible for resumes."""
    # 1. Uncompleted project: assign project
    assign_res = client.post(
        "/api/tracking/assign",
        json={
            "candidate_id": test_candidate_id,
            "project_id": "CS-01",
            "role_name": "Ethical Hacker",
            "candidate_name": "Truthful Candidate",
        },
    )
    project_id = assign_res.json()["id"]

    # Incomplete project must NOT be returned for resume
    verified_res = client.get(f"/api/tracking/verified-for-resume/{test_candidate_id}")
    assert verified_res.status_code == 200
    assert len(verified_res.json()) == 0

    # 2. Approve all milestones to complete the project
    detail = client.get(f"/api/tracking/project/{project_id}").json()
    for m in detail["milestones"]:
        client.post(
            "/api/tracking/verify",
            json={
                "candidate_project_id": project_id,
                "milestone_id": m["id"],
                "verdict": "approved",
                "score": 92.0,
                "feedback": f"Verified deliverable for {m['title']}.",
                "reviewer_name": "Staff Security Engineer",
            },
        )

    # Now that ALL milestones are approved, project should be Completed, verified, and eligible for resume
    comp_detail = client.get(f"/api/tracking/project/{project_id}").json()
    assert comp_detail["status"] == "Completed"
    assert comp_detail["is_verified"] is True
    assert comp_detail["eligible_for_resume"] is True

    # 3. Verified project is now returned with truthful bullets
    verified_res2 = client.get(f"/api/tracking/verified-for-resume/{test_candidate_id}")
    assert verified_res2.status_code == 200
    v_list = verified_res2.json()
    assert len(v_list) == 1
    assert v_list[0]["status"] == "Completed"
    assert "Verified" in v_list[0]["status_label"]
    assert len(v_list[0]["bullets"]) >= 1


def test_dashboard_stats_aggregation(test_candidate_id):
    """Tests dashboard metrics aggregation."""
    # Create two projects for candidate
    p1 = client.post(
        "/api/tracking/assign",
        json={
            "candidate_id": test_candidate_id,
            "project_id": "CS-01",
            "role_name": "Ethical Hacker",
        },
    ).json()

    p2 = client.post(
        "/api/tracking/assign",
        json={
            "candidate_id": test_candidate_id,
            "project_id": "CS-02",
            "role_name": "SOC Analyst",
        },
    ).json()

    # Get candidate-specific dashboard
    dash_res = client.get(f"/api/tracking/dashboard?candidate_id={test_candidate_id}")
    assert dash_res.status_code == 200
    dash = dash_res.json()

    assert dash["total_assigned"] >= 2
    assert "in_progress" in dash
    assert "completed" in dash
    assert "pending_submissions" in dash
    assert "overall_completion_percentage" in dash
    assert "milestone_stats" in dash
    assert dash["milestone_stats"]["total"] >= 6
    assert len(dash["projects"]) >= 2


def test_status_update_and_project_deletion(test_candidate_id):
    """Tests updating project status and deleting assignment."""
    p = client.post(
        "/api/tracking/assign",
        json={
            "candidate_id": test_candidate_id,
            "project_id": "CS-03",
            "role_name": "Network Security Engineer",
        },
    ).json()
    project_id = p["id"]

    # Update status to Under Review
    status_res = client.patch(
        f"/api/tracking/project/{project_id}/status",
        json={"status": "Under Review"},
    )
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "Under Review"

    # Delete assignment
    del_res = client.delete(f"/api/tracking/project/{project_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "deleted"

    # Verify not found after delete
    get_res = client.get(f"/api/tracking/project/{project_id}")
    assert get_res.status_code == 404

