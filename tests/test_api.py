"""Integration tests for FUTRSEC FastAPI REST API endpoints."""

import io
import fitz
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def test_resume_pdf():
    doc = fitz.open()
    page = doc.new_page()
    text = """
    Barry Allen
    ballen@centralcitysec.org | +1 555-0188 | Central City, MO
    CAREER OBJECTIVE
    Junior Penetration Tester seeking an Ethical Hacker position to conduct threat emulation.
    TECHNICAL SKILLS
    Python, Linux, Wireshark, Metasploit, Nmap, Burp Suite, Network Security
    CERTIFICATIONS
    CEH
    EDUCATION
    Bachelor of Science in Cybersecurity - CCU, 2023
    PROJECTS
    Port Scanner Lab
    Developed automated TCP/UDP scanner in Python to identify unpatched services.
    """
    page.insert_text(fitz.Point(50, 50), text)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


def test_api_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("healthy", "degraded")
    assert "app" in data
    assert "database" in data


def test_api_roles_list():
    res = client.get("/api/roles")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 74
    assert len(data["roles"]) >= 74


def test_api_role_detail():
    res = client.get("/api/roles/1")
    assert res.status_code == 200
    data = res.json()
    assert data["role_id"] == 1
    assert "skills" in data
    assert "requirements" in data
    assert "scoring_criteria" in data


def test_api_role_skills():
    res = client.get("/api/roles/1/skills")
    assert res.status_code == 200
    data = res.json()
    assert "skills" in data
    assert len(data["skills"]) > 0


def test_api_templates():
    res = client.get("/api/templates")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 30


def test_api_end_to_end_resume_workflow(test_resume_pdf):
    # 1. Analyze Resume
    files = {"file": ("barry_resume.pdf", test_resume_pdf, "application/pdf")}
    data = {"role_id": 1}

    analyze_res = client.post("/api/resumes/analyze", data=data, files=files)
    assert analyze_res.status_code == 200
    an_data = analyze_res.json()
    assert "analysis_id" in an_data
    assert "score_result" in an_data
    assert an_data["score_result"]["final_score"] >= 0.0
    analysis_id = an_data["analysis_id"]

    # 2. Trigger Resume Improvement & Round Robin Selection
    improve_res = client.post("/api/resumes/improve", json={"analysis_id": analysis_id})
    assert improve_res.status_code == 200
    imp_data = improve_res.json()
    assert "assigned_template" in imp_data
    assert "job_id" in imp_data
    assert imp_data["documents"]["docx_url"] is not None

    file_id = imp_data["job_id"]

    # 3. Download DOCX
    dl_res = client.get(f"/api/resumes/download/{file_id}?format=docx")
    assert dl_res.status_code == 200
    assert len(dl_res.content) > 5000

    # 4. Accept and Rescore
    rescore_res = client.post("/api/resumes/accept-and-rescore", json={"analysis_id": analysis_id})
    assert rescore_res.status_code == 200
    resc_data = rescore_res.json()
    assert "original_score" in resc_data
    assert "new_score" in resc_data
    assert "score_delta" in resc_data


def test_path_traversal_protection():
    res = client.get("/api/resumes/download/..%2F..%2Fetc%2Fpasswd?format=docx")
    assert res.status_code in (400, 403, 404)
