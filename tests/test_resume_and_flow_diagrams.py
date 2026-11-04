"""Test suite for Part A (Resume Formatting & Summaries) and Part B (Domain Project Recommendations & Flowcharts)."""

import os
import json
import pytest
import fitz
from docx import Document
from pathlib import Path

from app.projects.catalog import (
    project_catalog_repository,
    ALL_CATALOG_PROJECTS,
    SUPPORTED_DOMAINS,
    CYBERSECURITY_PROJECTS,
    DATA_SCIENCE_PROJECTS,
    CLOUD_DEVOPS_PROJECTS,
    FULL_STACK_PROJECTS,
)
from app.projects.generator import EnhancedResumeContent, ResumeContentGenerator
from app.reports.templates import template_registry
from app.reports.renderer import DocumentRenderer
from app.resume.extractor import ResumeExtractor, ParsedResumeData, ContactInfo, EducationEntry, ExperienceEntry, ProjectEntry
from app.resume.validator import ResumeContentValidator


def test_supported_domains_and_project_counts():
    """Verify that each supported domain has exactly five distinct project recommendations."""
    domains = project_catalog_repository.list_domains()
    assert len(domains) == 4, f"Expected 4 supported domains, got {len(domains)}"
    for d in domains:
        assert d["project_count"] == 5, f"Domain {d['domain']} must have exactly 5 projects, got {d['project_count']}"

    # Verify Cybersecurity domain specifically has the 5 specified projects
    cs_projects = project_catalog_repository.list_projects_by_domain("Cybersecurity")
    assert len(cs_projects) == 5
    cs_titles = [p["project_title"] for p in cs_projects]
    assert "Web Application Security Testing Lab & Vulnerability Remediation" in cs_titles
    assert "Network Monitoring and Anomaly Detection" in cs_titles
    assert "Phishing Email Detection and Security Analysis" in cs_titles
    assert "Security Log Analysis and Threat Detection" in cs_titles
    assert "File Integrity Monitoring and Security Alerting" in cs_titles


def test_project_catalog_structure_and_workflow():
    """Verify that every project has all required specification fields and distinct workflow stages."""
    required_keys = [
        "project_id", "project_title", "domain", "difficulty_level", "description",
        "learning_objectives", "required_technologies", "prerequisites",
        "implementation_phases", "expected_deliverables", "testing_validation_plan",
        "project_workflow", "skills_demonstrated"
    ]

    for p in ALL_CATALOG_PROJECTS:
        for k in required_keys:
            assert k in p and p[k], f"Project {p.get('project_id')} missing field: {k}"

        wf = p["project_workflow"]
        assert len(wf) >= 5, f"Project {p['project_id']} workflow must contain at least 5 stages"

        # Verify START and END nodes exist
        types = [node.get("type") for node in wf]
        assert "start" in types, f"Project {p['project_id']} missing START node"
        assert "end" in types, f"Project {p['project_id']} missing END node"

        # Verify decision node with branches exists
        decision_nodes = [node for node in wf if node.get("type") == "decision"]
        assert len(decision_nodes) >= 1, f"Project {p['project_id']} missing decision node"
        dec = decision_nodes[0]
        assert dec.get("yes_next") or dec.get("next_node"), f"Decision node in {p['project_id']} missing YES branch"
        assert dec.get("no_next"), f"Decision node in {p['project_id']} missing NO branch"


def test_standalone_html_interface_exists_and_contains_svg():
    """Verify that project-flow-diagrams.html exists, is readable locally, and contains valid SVG rendering."""
    html_file = Path("project-flow-diagrams.html")
    assert html_file.exists(), "project-flow-diagrams.html does not exist in root directory"

    content = html_file.read_text(encoding="utf-8")
    assert len(content) > 10000, "HTML file is too small or incomplete"

    # Verify key interface elements
    assert "FUTRSEC Domain Project Catalog" in content
    assert "Select Engineering Domain" in content
    assert "View Project Flow" in content
    assert "window.print()" in content
    assert "@media print" in content

    # Verify embedded projects data
    assert "Web Application Security Testing Lab & Vulnerability Remediation" in content
    assert "Customer Churn Predictive Modeling and Retention Engine" in content
    assert "Automated Multi-Stage CI/CD Deployment Pipeline" in content
    assert "Enterprise Inventory Management System" in content

    # Verify SVG components
    assert "<svg" in content
    assert "marker-end=" in content
    assert 'id="arrowDark"' in content
    assert 'id="arrowGreen"' in content
    assert 'id="arrowAmber"' in content


def test_resume_summary_conciseness_and_word_count():
    """Verify that generated professional summary targets approximately 40-60 words without metric or tool dumps."""
    sample_resume = ParsedResumeData(
        candidate_name="Alex Mercer",
        contact_info=ContactInfo(email="alex.mercer@example.com", phone="+1 555-019-2834", location="San Jose, CA"),
        professional_summary="Junior security enthusiast with experience in web apps and network basics.",
        technical_skills=["Burp Suite", "Nmap", "Python", "Linux", "SQL", "EDA", "MAE", "RMSE"],
        education=[EducationEntry(degree="Bachelor of Science", field_of_study="Cybersecurity", institution="State University", graduation_year="2024")],
        certifications=["CompTIA Security+"],
        employment_history=[],
        projects=[ProjectEntry(title="Local Security Lab", description="Assessed vulnerabilities in local target.", technologies=["Burp Suite", "Nmap"])],
    )

    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=sample_resume,
        target_role_name="Ethical Hacker",
        missing_core_skills=[],
        confirmed_skills=[],
        attempt_number=1,
    )

    # Sanitize via validator
    sanitized, report = ResumeContentValidator.validate_and_sanitize(enhanced)
    summary = sanitized.professional_summary
    words = summary.split()
    word_count = len(words)

    # Verify word count is in 40-60 word range
    assert 38 <= word_count <= 65, f"Summary word count should be ~40-60 words, got {word_count}: '{summary}'"

    # Verify NO evaluation metrics leaked into summary
    for metric in ["EDA", "MAE", "RMSE", "R2", "R²", "AUC", "confusion matrix"]:
        assert metric.lower() not in summary.lower(), f"Prohibited metric '{metric}' found in summary"

    # Verify role relevance
    assert "ethical hacker" in summary.lower() or "cybersecurity" in summary.lower() or "security" in summary.lower()


def test_technical_skills_categorization_and_metric_exclusion():
    """Verify skills are categorized dynamically with clean labels, and metrics are excluded."""
    sample_skills = [
        "Python", "Java", "SQL", "JavaScript",
        "React", "Node.js", "Express.js", "Spring Boot",
        "PostgreSQL", "MySQL", "MongoDB",
        "Burp Suite", "Nmap", "Wireshark",
        "AWS", "Docker", "Git", "GitHub",
        "Pandas", "NumPy", "scikit-learn",
        "Algorithms", "Data Structures",
        "EDA", "MAE", "RMSE", "R²"  # Should be filtered out!
    ]

    sample_resume = ParsedResumeData(
        candidate_name="Jordan Vance",
        contact_info=ContactInfo(email="jordan.vance@example.com", phone="+1 555-014-9988"),
        professional_summary="Cybersecurity professional with hands-on technical skills.",
        technical_skills=sample_skills,
        education=[EducationEntry(degree="B.S. in Computer Science", institution="Tech Institute", graduation_year="2023")],
        certifications=["CEH"],
        employment_history=[ExperienceEntry(job_title="Security Intern", company="SecureWorks", start_date="2023", end_date="Present", is_current=True, responsibilities=["Tested web apps."])],
        projects=[],
    )

    enhanced = ResumeContentGenerator.generate_enhanced_content(
        resume_data=sample_resume,
        target_role_name="Ethical Hacker",
        missing_core_skills=[],
        confirmed_skills=[],
        attempt_number=1,
    )

    sanitized, report = ResumeContentValidator.validate_and_sanitize(enhanced)
    grouped = sanitized.technical_skills_grouped

    # 1. Verify metrics are completely excluded
    all_grouped_skills = [s.lower() for slist in grouped.values() for s in slist]
    for bad in ["eda", "mae", "rmse", "r2", "r²", "r-squared"]:
        assert bad not in all_grouped_skills, f"Metric '{bad}' was not excluded from technical skills!"

    # 2. Verify certs are not in technical skills (CEH should be in certifications)
    assert "ceh" not in all_grouped_skills

    # 3. Verify standard categories exist and contain correct skills
    assert "Cybersecurity Tools" in grouped
    assert any("burp" in s.lower() for s in grouped["Cybersecurity Tools"])
    assert any("nmap" in s.lower() for s in grouped["Cybersecurity Tools"])

    assert "Programming Languages" in grouped
    assert any("python" in s.lower() for s in grouped["Programming Languages"])
    assert any("java" in s.lower() for s in grouped["Programming Languages"])

    assert "Databases" in grouped
    assert any("postgresql" in s.lower() or "mysql" in s.lower() for s in grouped["Databases"])

    assert "Cloud & DevOps" in grouped
    assert any("docker" in s.lower() or "git" in s.lower() or "aws" in s.lower() for s in grouped["Cloud & DevOps"])

    assert "Data Science & Machine Learning" in grouped
    assert any("pandas" in s.lower() or "scikit" in s.lower() for s in grouped["Data Science & Machine Learning"])

    # 4. For Ethical Hacker role, Cybersecurity Tools must be prioritized first
    categories_order = list(grouped.keys())
    assert categories_order[0] == "Cybersecurity Tools", f"Cybersecurity Tools must be first category for Ethical Hacker, got: {categories_order[0]}"


def test_docx_and_pdf_generation_integrity():
    """Verify that both DOCX and PDF render correctly without overlap and with proper formatting."""
    content = EnhancedResumeContent(
        candidate_name="JORDAN VANCE",
        contact_header="jordan.vance@example.com | +1 (555) 014-9988 | Austin, TX | linkedin.com/in/jordanvance",
        contact_details={"email": "jordan.vance@example.com", "phone": "+1 (555) 014-9988"},
        professional_headline="Ethical Hacker & Security Engineer",
        professional_summary=(
            "Results-driven Computer Science graduate specializing in Ethical Hacker methodologies, application security, and hands-on vulnerability analysis. "
            "Demonstrates core capability across Burp Suite, Nmap, Python through academic implementations and isolated lab projects. "
            "Dedicated to applying defense-in-depth security principles, proactive threat assessment, and robust engineering to protect enterprise environments."
        ),
        technical_skills_grouped={
            "Cybersecurity Tools": ["Burp Suite", "Nmap", "Wireshark", "Metasploit"],
            "Programming Languages": ["Python", "Java", "JavaScript", "SQL"],
            "Frameworks & Libraries": ["React", "Node.js", "Express.js", "Spring Boot"],
            "Databases": ["PostgreSQL", "MySQL", "MongoDB"],
            "Cloud & DevOps": ["AWS", "Docker", "Git", "GitHub"],
            "Data Science & Machine Learning": ["Pandas", "NumPy", "scikit-learn"],
        },
        experience=[
            {
                "job_title": "Security Analyst Intern",
                "company": "CyberDefense Labs",
                "start_date": "2023",
                "end_date": "Present",
                "is_current": True,
                "responsibilities": [
                    "Conducted vulnerability assessments of web endpoints using Burp Suite and documented remediation steps.",
                    "Analyzed network capture files with Wireshark to identify suspicious protocol payloads."
                ]
            }
        ],
        projects=[
            {
                "title": "Web Application Security Testing Lab & Vulnerability Remediation",
                "technologies": ["Burp Suite", "Docker", "OWASP Juice Shop", "Python"],
                "description": "Deployed isolated web security testing environment to assess OWASP Top 10 vulnerabilities.",
                "outcomes": "Identified 5 security flaws with CVSS v3.1 scoring and verified patches."
            }
        ],
        education=[
            {
                "degree": "Bachelor of Science in Cybersecurity",
                "institution": "University of Texas",
                "graduation_year": "2023",
                "gpa": "3.85"
            }
        ],
        certifications=["CompTIA Security+ (SY0-601)"],
        achievements=["National Cyber League Top 10% Finisher"],
        confirmed_skills_included=[],
        unverified_skills_excluded=[],
        pursuing_certifications=[],
        approved_improvements_applied=[],
        sections_rewritten=[],
        future_learning_recommendations=[],
        pending_confirmations=[],
        generator_mode="test",
        attempt_number=1,
    )

    tmpl = template_registry.get_template("T01")
    result = DocumentRenderer.render_resume(content, tmpl, "test_verification_run")

    docx_path = result["docx_path"]
    pdf_path = result["pdf_path"]

    assert os.path.exists(docx_path), "DOCX output file was not generated"
    assert os.path.exists(pdf_path), "PDF output file was not generated"

    # Inspect DOCX
    docx_doc = Document(docx_path)
    full_docx_text = "\n".join([p.text for p in docx_doc.paragraphs])
    assert "JORDAN VANCE" in full_docx_text
    assert "Cybersecurity Tools:" in full_docx_text
    assert "Burp Suite, Nmap, Wireshark, Metasploit" in full_docx_text

    # Inspect PDF
    pdf_doc = fitz.open(pdf_path)
    assert len(pdf_doc) >= 1
    page1 = pdf_doc[0]
    pdf_text = page1.get_text()
    assert "JORDAN VANCE" in pdf_text
    assert "Cybersecurity Tools:" in pdf_text
    assert "Burp Suite" in pdf_text

    # Check that divider does not overlap text
    drawings = page1.get_drawings()
    assert len(drawings) >= 1, "Expected divider lines in PDF output"

    words = page1.get_text("words")
    heading_words = [w for w in words if "SKILLS" in w[4].upper()]
    first_skill_words = [w for w in words if "Cybersecurity" in w[4]]

    if heading_words and first_skill_words:
        h_bottom = max(w[3] for w in heading_words)
        s_top = min(w[1] for w in first_skill_words)
        assert s_top > h_bottom, f"First skill text (top={s_top}) overlaps heading (bottom={h_bottom})"

    pdf_doc.close()
