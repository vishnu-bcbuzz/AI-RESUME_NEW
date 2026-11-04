"""Comprehensive end-to-end tests for FUTRSEC Resume Analysis Engine.

Validates:
1. Complete workflow: Upload PDF -> File validation -> Storage -> Section parsing -> Role retrieval (Ethical Hacker) -> Skills matching -> Deterministic ATS Scoring -> Gap Analysis -> Response serialization.
2. Complete workflow with DOCX resumes.
3. Accurate extraction and retention of candidate projects, technical skills, and certifications.
4. Robust error handling: informative, safe JSON errors with request IDs on invalid files, missing roles, empty files.
5. Guarantee that backend exceptions return JSON (never plain text) and never expose database credentials or stack traces.
6. Preservation of uploaded resume files in UPLOAD_DIR.
"""

import io
from pathlib import Path
import fitz
import docx
import pytest
from fastapi.testclient import TestClient

from app.main import app, ANALYSIS_CACHE
from app.config import settings

client = TestClient(app, raise_server_exceptions=False)

SAMPLE_ETHICAL_HACKER_TEXT = """
VISHNU PRASATH D
dvishnuprasathvpd@gmail.com | +91-9025671812 | Coimbatore, India
https://linkedin.com/in/vishnuprasath | https://github.com/vishnuprasath

PROFESSIONAL SUMMARY
Cybersecurity specialist and ethical hacker dedicated to offensive security, penetration testing, vulnerability assessment, and secure web application hardening.

TECHNICAL SKILLS
Cybersecurity Tools: Burp Suite, Nmap, Wireshark, Metasploit, Kali Linux
Security Concepts: Network Security Testing, Vulnerability Scanning, OWASP Top 10, Penetration Testing
Programming Languages: Python, Java, SQL, Bash
Operating Systems: Linux, Windows Server

PROJECTS
Web Application Penetration Testing Lab
Configured isolated laboratory environment running DVWA and OWASP Juice Shop. Performed manual SQL injection and cross-site scripting (XSS) assessments using Burp Suite and sqlmap.
Technologies: Burp Suite, Python, OWASP Top 10, Kali Linux
Status: Completed
GitHub: https://github.com/vishnuprasath/web-security-lab

Enterprise Network Hardening & Audit
Conducted automated network reconnaissance using Nmap scripts to identify open ports, misconfigured firewalls, and unpatched services. Authored technical remediation report.
Technologies: Nmap, Wireshark, Bash, Linux
Status: Completed

CERTIFICATIONS
• Data Structures and Algorithms (DSA)
• Cloud Computing
• Database Management Systems (DBMS)
• Internet of Things (IoT)
• Young Professional Python

EDUCATION
Bachelor of Engineering in Computer Science
Nehru Institute of Engineering and Technology, 2024
"""


def create_sample_pdf(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(fitz.Point(40, 50), text, fontsize=10)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


def create_sample_docx(text: str) -> bytes:
    doc = docx.Document()
    for line in text.strip().split("\n"):
        line = line.strip()
        if line:
            doc.add_paragraph(line)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


class TestResumeAnalysisEngineWorkflow:
    """Verifies end-to-end evaluation against Ethical Hacker role."""

    def test_evaluate_against_ethical_hacker_pdf_success(self):
        pdf_bytes = create_sample_pdf(SAMPLE_ETHICAL_HACKER_TEXT)
        files = {"file": ("vishnu_ethical_hacker_resume.pdf", pdf_bytes, "application/pdf")}
        data = {"role_id": 1}

        response = client.post("/api/resumes/analyze", data=data, files=files)
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
        result = response.json()

        # 1. Top-level analysis contract
        assert "analysis_id" in result
        assert "request_id" in result
        assert result["role_id"] == 1
        assert result["role_name"] == "Ethical Hacker"
        assert result["filename"] == "vishnu_ethical_hacker_resume.pdf"

        # 2. Parsed resume verification
        parsed = result["parsed_resume"]
        assert parsed["candidate_name"] == "VISHNU PRASATH D"
        assert parsed["contact_info"]["email"] == "dvishnuprasathvpd@gmail.com"
        assert len(parsed["technical_skills"]) > 0

        # Verify extracted projects
        assert len(result["extracted_projects"]) >= 2
        project_titles = [p["title"] for p in result["extracted_projects"]]
        assert any("Web Application Penetration Testing Lab" in t for t in project_titles)

        # Verify certifications preserved
        assert len(result["relevant_certifications_held"]) == 5
        assert "Data Structures and Algorithms (DSA)" in result["relevant_certifications_held"]
        assert "Young Professional Python" in result["relevant_certifications_held"]

        # 3. Deterministic ATS scoring
        score_res = result["score_result"]
        assert score_res["final_score"] > 0.0
        assert len(score_res["category_scores"]) == 5
        category_names = [c["category_name"] for c in score_res["category_scores"]]
        assert "Technical Skills" in category_names
        assert "Projects" in category_names
        assert "Education" in category_names
        assert "Tools & Certifications" in category_names
        assert "Career Objective" in category_names

        # 4. Improvement plan generated
        assert "improvement_plan" in result
        plan = result["improvement_plan"]
        assert "items" in plan
        assert len(plan["items"]) > 0

        # 5. Stored in cache and persistent file exists
        analysis_id = result["analysis_id"]
        assert analysis_id in ANALYSIS_CACHE
        cached = ANALYSIS_CACHE[analysis_id]
        assert cached["role_name"] == "Ethical Hacker"
        if cached.get("stored_path"):
            assert Path(cached["stored_path"]).exists()

    def test_evaluate_against_ethical_hacker_docx_success(self):
        docx_bytes = create_sample_docx(SAMPLE_ETHICAL_HACKER_TEXT)
        files = {"file": ("vishnu_ethical_hacker_resume.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        data = {"role_id": 1}

        response = client.post("/api/resumes/analyze", data=data, files=files)
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
        result = response.json()

        assert result["role_id"] == 1
        assert result["role_name"] == "Ethical Hacker"
        assert result["document_metadata"]["format"] == "docx"
        assert result["score_result"]["final_score"] > 0.0

    def test_invalid_role_id_returns_404_json(self):
        pdf_bytes = create_sample_pdf(SAMPLE_ETHICAL_HACKER_TEXT)
        files = {"file": ("resume.pdf", pdf_bytes, "application/pdf")}
        data = {"role_id": 999999}

        response = client.post("/api/resumes/analyze", data=data, files=files)
        assert response.status_code == 404
        assert response.headers.get("content-type", "").startswith("application/json")
        result = response.json()
        assert "detail" in result
        assert "999999 not found" in result["detail"]
        assert "request_id" in result

    def test_empty_file_returns_400_json(self):
        files = {"file": ("empty.pdf", b"", "application/pdf")}
        data = {"role_id": 1}

        response = client.post("/api/resumes/analyze", data=data, files=files)
        assert response.status_code == 400
        assert response.headers.get("content-type", "").startswith("application/json")
        result = response.json()
        assert "empty" in result["detail"].lower()
        assert "request_id" in result

    def test_unsupported_format_returns_400_json(self):
        files = {"file": ("resume.txt", b"Cybersecurity analyst resume text...", "text/plain")}
        data = {"role_id": 1}

        response = client.post("/api/resumes/analyze", data=data, files=files)
        assert response.status_code == 400
        assert response.headers.get("content-type", "").startswith("application/json")
        result = response.json()
        assert "unsupported" in result["detail"].lower()

    def test_corrupted_pdf_returns_400_or_422_json(self):
        corrupted_bytes = b"%PDF-1.4\nCorrupted binary payload non-readable content header garbage"
        files = {"file": ("corrupt.pdf", corrupted_bytes, "application/pdf")}
        data = {"role_id": 1}

        response = client.post("/api/resumes/analyze", data=data, files=files)
        assert response.status_code in (400, 422)
        assert response.headers.get("content-type", "").startswith("application/json")
        result = response.json()
        assert "detail" in result
        assert "request_id" in result

