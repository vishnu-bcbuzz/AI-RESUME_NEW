"""Tests to verify the removal of the standalone Project Workflows module

Confirms that:
1. The sidebar contains strictly the 7 specified navigation items.
2. Project Workflows and the ExternalLink icon are removed.
3. Standalone endpoints /project-flow-diagrams.html and /diagrams are decoupled/removed.
4. Core features (roles, templates, projects, catalog, workflow API) remain intact.
"""

from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_sidebar_contains_strictly_seven_nav_items():
    sidebar_file = Path("frontend/src/components/Sidebar.tsx")
    assert sidebar_file.exists()
    content = sidebar_file.read_text(encoding="utf-8")

    # Verify "Project Workflows" is removed
    assert "Project Workflows" not in content, "Sidebar must not contain 'Project Workflows'"
    assert "project-flow-diagrams.html" not in content, "Sidebar must not link to project-flow-diagrams.html"
    assert "ExternalLink" not in content, "ExternalLink icon must be removed"
    assert "Workflow," not in content, "Workflow icon must not be imported"

    # Strictly 7 navigation items
    expected_items = [
        "Dashboard",
        "Cybersecurity Jobs",
        "Analyze Resume",
        "Resume Improvement",
        "Analysis History",
        "Template Gallery",
        "Settings",
    ]
    for item in expected_items:
        assert item in content, f"Sidebar must contain '{item}'"


def test_standalone_endpoints_removed():
    """Verify standalone HTML endpoints are decoupled from FastAPI backend."""
    res1 = client.get("/project-flow-diagrams.html")
    assert res1.status_code == 404

    res2 = client.get("/diagrams")
    assert res2.status_code == 404


def test_core_platform_preserved():
    """Verify cybersecurity roles, project catalog, and workflows remain intact."""
    roles_res = client.get("/api/roles")
    assert roles_res.status_code == 200
    roles_data = roles_res.json()
    assert roles_data["total"] == 74
    assert len(roles_data["roles"]) == 74

    wf_res = client.get("/api/projects/workflow?title=Web Application Security Testing Lab %26 Vulnerability Remediation")
    assert wf_res.status_code == 200
    assert "workflow" in wf_res.json()
