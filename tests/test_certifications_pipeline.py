"""Comprehensive regression tests for candidate certifications pipeline across all 30 templates.

Validates:
1. Clean extraction of genuine candidate certifications.
2. Line-wrap and broken-hyphen reconstruction (e.g. 'Sys-' + 'tems (DBMS)', 'Young Professional' + 'Python').
3. Strict exclusion of coding challenge profiles/platforms (LeetCode, HackerRank, CodeChef, CODING PROFILES).
4. Structured data preservation via CertificationEntry models without inventing metadata.
5. AI Generator preservation of certifications as protected data.
6. ATS formatting and dedicated CERTIFICATIONS section rendering across all 30 templates (T01 - T30) in both DOCX and PDF.
7. Clean omission of CERTIFICATIONS section when candidate has no certifications.
"""

import io
import tempfile
from pathlib import Path
import pytest
import docx
import fitz

from app.resume.extractor import ResumeExtractor, ParsedResumeData, CertificationEntry, ContactInfo
from app.resume.validator import ResumeContentValidator
from app.projects.generator import ResumeContentGenerator, EnhancedResumeContent
from app.reports.templates import template_registry
from app.reports.renderer import DocumentRenderer


CANDIDATE_RAW_RESUME_WITH_CERTS = """
VISHNU PRASATH D
dvishnuprasathvpd@gmail.com | +91-9025671812 | Coimbatore, India

PROFESSIONAL SUMMARY
Cybersecurity specialist and Python developer dedicated to offensive security, penetration testing, and secure system design.

TECHNICAL SKILLS
Programming Languages: Python, Java, SQL
Cybersecurity Tools: Burp Suite, Nmap, Wireshark, Metasploit

PROJECTS
Student Management System
Developed full-stack web management system using FastAPI and PostgreSQL with role-based access control.

CERTIFICATIONS
• Data Structures and Algorithms (DSA)
• Cloud Computing
• Database Management Sys-
  tems (DBMS)
• Internet of Things (IoT)
• Young Professional
  Python

CODING PROFILES
• LeetCode
• CodeChef
• HackerRank

EDUCATION
Bachelor of Engineering in Computer Science
Nehru Institute of Engineering and Technology, 2024
"""

EXPECTED_5_CERTS = [
    "Data Structures and Algorithms (DSA)",
    "Cloud Computing",
    "Database Management Systems (DBMS)",
    "Internet of Things (IoT)",
    "Young Professional Python",
]


class TestCertificationsExtraction:
    """Verifies that the resume parser and extractor correctly capture all certifications."""

    def test_extracts_all_five_original_certifications(self):
        parsed = ResumeExtractor.extract(CANDIDATE_RAW_RESUME_WITH_CERTS)
        assert parsed.certifications == EXPECTED_5_CERTS

    def test_reconstructs_hyphenated_and_wrapped_lines_without_bullets(self):
        raw_text = """
VISHNU PRASATH D
dvishnuprasathvpd@gmail.com

CERTIFICATIONS
Data Structures and Algorithms (DSA)
Cloud Computing
Database Management Sys-
tems (DBMS)
Internet of Things (IoT)
Young Professional
Python
CODING PROFILES
LeetCode
CodeChef
HackerRank
"""
        parsed = ResumeExtractor.extract(raw_text)
        assert parsed.certifications == EXPECTED_5_CERTS

    def test_excludes_coding_challenge_platforms_and_headers(self):
        parsed = ResumeExtractor.extract(CANDIDATE_RAW_RESUME_WITH_CERTS)
        lower_certs = [c.lower() for c in parsed.certifications]
        for prohibited in ["leetcode", "codechef", "hackerrank", "coding profiles", "codeforces", "github"]:
            assert prohibited not in lower_certs

    def test_populates_structured_certifications_without_inventing_metadata(self):
        parsed = ResumeExtractor.extract(CANDIDATE_RAW_RESUME_WITH_CERTS)
        assert len(parsed.structured_certifications) == 5
        for entry in parsed.structured_certifications:
            assert isinstance(entry, CertificationEntry)
            assert entry.name in EXPECTED_5_CERTS
            assert entry.certification_name in EXPECTED_5_CERTS
            # No fabricated issuing organizations or dates
            assert entry.issuing_organization is None
            assert entry.issuer is None
            assert entry.issue_date is None
            assert entry.date is None
            assert entry.credential_id is None


class TestCertificationsValidationAndGeneration:
    """Verifies that the validator and generator strictly preserve candidate certifications."""

    def test_validator_preserves_five_certifications(self):
        parsed = ResumeExtractor.extract(CANDIDATE_RAW_RESUME_WITH_CERTS)
        enhanced = ResumeContentGenerator._generate_with_heuristics(
            resume=parsed,
            role_name="Ethical Hacker",
            missing_core_skills=[],
            confirmed_skills=[],
            approved_plan_items=[],
        )
        sanitized, report = ResumeContentValidator.validate_and_sanitize(enhanced)
        assert sanitized.certifications == EXPECTED_5_CERTS

    def test_generator_does_not_convert_certifications_into_skills(self):
        parsed = ResumeExtractor.extract(CANDIDATE_RAW_RESUME_WITH_CERTS)
        enhanced = ResumeContentGenerator._generate_with_heuristics(
            resume=parsed,
            role_name="Ethical Hacker",
            missing_core_skills=[],
            confirmed_skills=[],
            approved_plan_items=[],
        )
        all_skills = [
            skill.lower()
            for group in enhanced.technical_skills_grouped.values()
            for skill in group
        ]
        for cert in EXPECTED_5_CERTS:
            assert cert.lower() not in all_skills


class TestTemplateRenderingAcrossAll30Templates:
    """Verifies that all 30 templates render CERTIFICATIONS in DOCX and PDF when present."""

    @pytest.fixture
    def content_with_certs(self):
        return EnhancedResumeContent(
            candidate_name="VISHNU PRASATH D",
            contact_header="dvishnuprasathvpd@gmail.com | +91-9025671812",
            contact_details={"email": "dvishnuprasathvpd@gmail.com", "phone": "+91-9025671812"},
            professional_headline="Offensive Cybersecurity Specialist",
            professional_summary="Results-oriented cybersecurity practitioner seeking to apply technical proficiency as an Ethical Hacker.",
            technical_skills_grouped={
                "Programming Languages": ["Python", "SQL"],
                "Cybersecurity Tools": ["Burp Suite", "Nmap", "Wireshark"],
            },
            experience=[],
            projects=[{
                "title": "Student Management System",
                "description": "Developed web-based system with FastAPI and PostgreSQL.",
                "bullets": ["Integrated PostgreSQL for persistent storage.", "Built RESTful endpoints."],
            }],
            education=[{
                "degree": "Bachelor of Engineering",
                "institution": "Nehru Institute of Engineering and Technology",
                "graduation_year": "2024",
            }],
            certifications=EXPECTED_5_CERTS,
            structured_certifications=[CertificationEntry(name=c, certification_name=c) for c in EXPECTED_5_CERTS],
            achievements=[],
        )

    @pytest.fixture
    def content_without_certs(self):
        return EnhancedResumeContent(
            candidate_name="JANE DOE",
            contact_header="jane.doe@example.com | +1 555-0199",
            contact_details={"email": "jane.doe@example.com", "phone": "+1 555-0199"},
            professional_headline="Security Analyst",
            professional_summary="Security analyst focused on defense-in-depth and security monitoring.",
            technical_skills_grouped={"Tools": ["Splunk", "Wireshark"]},
            experience=[],
            projects=[{"title": "Log Analyzer", "description": "Python log tool", "bullets": ["Analyzed syslog entries."]}],
            education=[{"degree": "B.S. in Cybersecurity", "institution": "State University"}],
            certifications=[],
            structured_certifications=[],
            achievements=[],
        )

    def test_docx_rendering_all_30_templates(self, content_with_certs, content_without_certs):
        templates = template_registry.list_templates()
        assert len(templates) == 30

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            for t in templates:
                tid = t.template_id

                # Render with certifications
                docx_path = tmp / f"{tid}_certs.docx"
                DocumentRenderer._render_docx(content_with_certs, t, docx_path)
                doc = docx.Document(str(docx_path))
                docx_text = "\n".join(p.text for p in doc.paragraphs)

                assert "CERTIFICATIONS" in docx_text.upper(), f"Template {tid}: CERTIFICATIONS section header missing in DOCX"
                for cert in EXPECTED_5_CERTS:
                    assert cert in docx_text, f"Template {tid}: Certification '{cert}' missing in DOCX"

                # Verify placement after PROJECTS
                proj_idx = docx_text.upper().find("PROJECTS")
                cert_idx = docx_text.upper().find("CERTIFICATIONS")
                assert proj_idx != -1 and cert_idx != -1, f"Template {tid}: Projects or Certifications not found in DOCX"
                assert cert_idx > proj_idx, f"Template {tid}: CERTIFICATIONS must appear after PROJECTS in DOCX"

                # Render without certifications: MUST omit cleanly
                docx_no_path = tmp / f"{tid}_no_certs.docx"
                DocumentRenderer._render_docx(content_without_certs, t, docx_no_path)
                doc_no = docx.Document(str(docx_no_path))
                docx_no_text = "\n".join(p.text for p in doc_no.paragraphs)
                assert "CERTIFICATIONS" not in docx_no_text.upper(), f"Template {tid}: CERTIFICATIONS section should be omitted when empty in DOCX"

    def test_pdf_rendering_all_30_templates(self, content_with_certs, content_without_certs):
        templates = template_registry.list_templates()
        assert len(templates) == 30

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            for t in templates:
                tid = t.template_id

                # Render with certifications
                pdf_path = tmp / f"{tid}_certs.pdf"
                DocumentRenderer._render_pdf(content_with_certs, t, pdf_path)
                pdf_doc = fitz.open(str(pdf_path))
                pdf_text = "\n".join(page.get_text() for page in pdf_doc)
                pdf_doc.close()

                assert "CERTIFICATIONS" in pdf_text.upper(), f"Template {tid}: CERTIFICATIONS section header missing in PDF"
                for cert in EXPECTED_5_CERTS:
                    assert cert in pdf_text, f"Template {tid}: Certification '{cert}' missing in PDF"

                # Verify placement after PROJECTS
                proj_idx = pdf_text.upper().find("PROJECTS")
                cert_idx = pdf_text.upper().find("CERTIFICATIONS")
                assert proj_idx != -1 and cert_idx != -1, f"Template {tid}: Projects or Certifications not found in PDF"
                assert cert_idx > proj_idx, f"Template {tid}: CERTIFICATIONS must appear after PROJECTS in PDF"

                # Render without certifications: MUST omit cleanly
                pdf_no_path = tmp / f"{tid}_no_certs.pdf"
                DocumentRenderer._render_pdf(content_without_certs, t, pdf_no_path)
                pdf_no_doc = fitz.open(str(pdf_no_path))
                pdf_no_text = "\n".join(page.get_text() for page in pdf_no_doc)
                pdf_no_doc.close()
                assert "CERTIFICATIONS" not in pdf_no_text.upper(), f"Template {tid}: CERTIFICATIONS section should be omitted when empty in PDF"

