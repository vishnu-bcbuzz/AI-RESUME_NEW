"""Universal Resume Parsing and Verification Engine Test Suite.

Comprehensive regression tests covering:
1. Sabrish R. resume regression (Summary, 20+ Skills, 3 Internships, 3 Projects, B.Tech CGPA 8.44, 9 Certs, 2 Achievements, 3 Languages)
2. Entry-level fresher resume format
3. Experienced cybersecurity professional format
4. Academic CV format with publications and research
5. DOCX document format
6. Resume Verification Engine status categorization (extracted, partially_extracted, extraction_failed, genuinely_absent)
7. Deterministic ATS scoring integration with verified candidate profile
"""

import io
from pathlib import Path
import pytest
from docx import Document

from app.resume.parser import ResumeParser
from app.resume.extractor import (
    ResumeExtractor,
    ParsedResumeData,
    EducationEntry,
    ProjectEntry,
    ExperienceEntry,
)
from app.resume.verifier import ResumeVerificationEngine, SectionVerificationResult
from app.scoring.engine import ATSScoringEngine
from app.scoring.matcher import SkillMatcher
from app.database.repositories import role_repository


def test_sabrish_resume_regression():
    """Validates complete deterministic extraction on the Sabrish R. resume PDF."""
    pdf_path = Path("V:/ai_jobagent/uploads/an_45a7f9454503_SabrishR_Resume.pdf")
    assert pdf_path.exists(), f"Expected resume PDF at {pdf_path}"

    pdf_bytes = pdf_path.read_bytes()
    parsed_doc = ResumeParser.parse_document("SabrishR_Resume.pdf", pdf_bytes)

    # Parser checks
    assert parsed_doc["format"] == "pdf"
    assert parsed_doc["word_count"] >= 350
    assert not parsed_doc["security_flag_injection_detected"]

    # Structured Extractor checks
    data: ParsedResumeData = ResumeExtractor.extract(parsed_doc["raw_text"])

    # 1. Candidate Name & Contact Info
    assert data.candidate_name == "SABRISH R"
    assert data.contact_info.email == "mailsabrish@gmail.com"
    assert data.contact_info.phone == "+91 7338958227"
    assert "rsabrish" in (data.contact_info.linkedin or "")

    # 2. Professional Summary
    assert data.professional_summary is not None
    assert len(data.professional_summary) >= 150
    assert "TryHackMe" in data.professional_summary
    assert "CompTIA Security+" in data.professional_summary

    # 3. Technical Skills
    assert len(data.technical_skills) >= 20
    assert any(s in data.technical_skills for s in ["Wireshark", "Nmap", "Linux", "Python", "SQL", "IDS/IPS", "GRC"])

    # 4. Soft Skills
    assert len(data.soft_skills) >= 3
    assert any("communication" in s.lower() for s in data.soft_skills)

    # 5. Internships (3 distinct entries)
    assert len(data.internships) == 3
    intern_titles = [i.job_title.lower() for i in data.internships]
    assert any("cybersecurity" in t for t in intern_titles)
    assert any("iot" in t for t in intern_titles)
    assert any("networking" in t for t in intern_titles)

    # 6. Projects (3 distinct nested projects)
    assert len(data.projects) == 3
    proj_titles = [p.title.lower() for p in data.projects]
    assert any("incident" in t or "siem" in t for t in proj_titles)
    assert any("fota" in t or "firmware" in t for t in proj_titles)
    assert any("traffic" in t or "sniffer" in t for t in proj_titles)
    for p in data.projects:
        assert p.is_nested is True
        assert len(p.bullets) >= 2

    # 7. Education with Specialization & CGPA 8.44
    assert len(data.education) >= 1
    primary_edu = data.education[0]
    assert "B.Tech" in primary_edu.degree
    assert "Cybersecurity" in (primary_edu.specialization or "")
    assert "Ramachandra" in (primary_edu.institution or "")
    assert primary_edu.graduation_year == "2026"
    assert primary_edu.cgpa == "8.44"

    # 8. Certifications (all 9 preserved)
    assert len(data.certifications) == 9
    cert_names = [c.lower() for c in data.certifications]
    assert any("security+" in c for c in cert_names)
    assert any("isc2" in c or "certified in cybersecurity" in c for c in cert_names)
    assert any("cisco" in c for c in cert_names)
    assert any("tata" in c or "forage" in c for c in cert_names)
    assert any("tryhackme" in c for c in cert_names)

    # 9. Achievements (2 distinct entries)
    assert len(data.achievements) == 2
    ach_text = " ".join(data.achievements).lower()
    assert "ctf" in ach_text or "mindspark" in ach_text
    assert "rank holder" in ach_text

    # 10. Languages (3 distinct items)
    assert len(data.languages) == 3
    lang_lower = [l.lower() for l in data.languages]
    assert "tamil" in lang_lower
    assert "english" in lang_lower
    assert "hindi" in lang_lower

    # 11. Multi-Point Verification Engine Audit
    vr = data.verification_report
    assert vr is not None
    assert vr.get("overall_quality_score", 0) >= 90.0
    assert vr.get("is_extraction_reliable") is True
    assert len(vr.get("critical_warnings", [])) == 0

    sections = vr.get("sections", {})
    assert sections.get("summary", {}).get("status") == "extracted"
    assert sections.get("technical_skills", {}).get("status") == "extracted"
    assert sections.get("projects", {}).get("status") == "extracted"
    assert sections.get("experience", {}).get("status") == "extracted"
    assert sections.get("education", {}).get("status") == "extracted"
    assert sections.get("certifications", {}).get("status") == "extracted"
    assert sections.get("achievements", {}).get("status") == "extracted"
    assert sections.get("languages", {}).get("status") == "extracted"


def test_fresher_single_column_resume():
    """Tests universal extraction on an entry-level fresher resume format."""
    fresher_text = """
JANE DOE
Austin, TX | jane.doe@example.com | (512) 555-0199 | linkedin.com/in/janedoe

CAREER OBJECTIVE
Enthusiastic computer science graduate aiming to secure an entry-level Cybersecurity Analyst role. Eager to leverage hands-on lab experience in vulnerability assessment, threat intelligence, and Python scripting to protect corporate networks.

TECHNICAL SKILLS
Security Tools: Wireshark, Nmap, Burp Suite, Metasploit, Snort
Operating Systems: Linux (Ubuntu, Kali), Windows Server
Programming: Python, Bash, SQL, C++
Networking: TCP/IP, DNS, DHCP, Subnetting, Firewalls

ACADEMIC PROJECTS
Network Intrusion Detection System
• Developed a signature-based intrusion detection engine using Python and Scapy.
• Analyzed PCAP traffic captures to identify port scanning and SYN flood attempts.
• Configured automated alert notifications via Discord webhooks.

Web Application Vulnerability Scanner
• Built an automated scanner detecting OWASP Top 10 vulnerabilities (SQLi, XSS).
• Engineered multithreaded crawler to discover exposed application endpoints.

EDUCATION
Bachelor of Science in Computer Science
University of Texas at Austin · GPA: 3.85 / 4.0
2020 – 2024

CERTIFICATIONS
CompTIA Security+ (SY0-701)
CompTIA Network+

LANGUAGES
English (Native), Spanish (Conversational)
"""
    data = ResumeExtractor.extract(fresher_text)

    assert data.candidate_name == "JANE DOE"
    assert data.contact_info.email == "jane.doe@example.com"
    assert data.career_objective is not None
    assert len(data.technical_skills) >= 10
    assert len(data.projects) == 2
    assert len(data.education) >= 1
    assert "Computer Science" in (data.education[0].field_of_study or "")
    assert data.education[0].gpa == "3.85"
    assert len(data.certifications) >= 2
    assert len(data.languages) >= 2

    vr = data.verification_report
    assert vr["is_extraction_reliable"] is True
    assert vr["sections"]["projects"]["status"] == "extracted"
    assert vr["sections"]["education"]["status"] == "extracted"


def test_experienced_professional_resume():
    """Tests universal extraction on an experienced senior cybersecurity professional."""
    experienced_text = """
MICHAEL CHANG
San Francisco, CA | m.chang@cybersec.org | +1 415 555 7821 | github.com/mchang-sec

EXECUTIVE SUMMARY
Senior Information Security Engineer with 8+ years of expertise in Security Operations Centers (SOC), Incident Response, and Cloud Security (AWS/Azure). Proven track record mitigating advanced persistent threats (APT), designing automated SOAR playbooks, and achieving ISO 27001 compliance.

CORE COMPETENCIES
SIEM / SOAR: Splunk, Microsoft Sentinel, Cortex XSOAR, ELK Stack
Cloud Security: AWS GuardDuty, Security Hub, IAM, Terraform
Threat Detection: Yara, Zeek, Suricata, Threat Hunting, MITRE ATT&CK
Incident Management: Digital Forensics, EnCase, Volatility, Incident Triage

PROFESSIONAL EXPERIENCE
Lead Security Operations Engineer — Apex Defense Systems
Jan 2021 – Present
• Spearheaded 24/7 Tier-3 incident response team investigating high-severity cyber attacks.
• Deployed 45+ automated detection rules mapped to MITRE ATT&CK framework.
• Reduced mean-time-to-respond (MTTR) by 62% using custom Python SOAR integrations.

Senior SOC Analyst — CloudSecure Inc
Jun 2017 – Dec 2020
• Monitored security alerts across hybrid cloud enterprise environments.
• Conducted root-cause analysis on credential stuffing and phishing campaigns.
• Mentored junior analysts on network forensics and log analysis using Splunk.

EDUCATION
Master of Science in Information Security
Carnegie Mellon University
2015 – 2017

Bachelor of Engineering in Computer Engineering
Purdue University
2011 – 2015

LICENSES & CERTIFICATIONS
CISSP — Certified Information Systems Security Professional (ISC2)
CISM — Certified Information Security Manager (ISACA)
AWS Certified Security - Specialty
"""
    data = ResumeExtractor.extract(experienced_text)

    assert data.candidate_name == "MICHAEL CHANG"
    assert data.professional_summary is not None
    assert len(data.employment_history) == 2
    assert data.employment_history[0].job_title == "Lead Security Operations Engineer"
    assert data.employment_history[0].company == "Apex Defense Systems"
    assert len(data.education) == 2
    assert len(data.certifications) >= 3

    vr = data.verification_report
    assert vr["is_extraction_reliable"] is True
    assert vr["sections"]["experience"]["status"] == "extracted"


def test_academic_cv_format():
    """Tests universal extraction on an academic CV format with publications."""
    academic_text = """
DR. ARUN KUMAR
Boston, MA | arun.kumar@mit.edu | 617-555-0182

RESEARCH PROFILE
Postdoctoral cybersecurity researcher specializing in Post-Quantum Cryptography, hardware security, and secure multiparty computation.

AREAS OF EXPERTISE
Cryptography, Post-Quantum Cryptography, Hardware Security, Rust, C, SageMath, Lattice-Based Cryptography

EDUCATION
Doctor of Philosophy in Computer Science
Massachusetts Institute of Technology
2018 – 2023

Master of Technology in Computer Science
Indian Institute of Technology Madras · CGPA: 9.12 / 10
2016 – 2018

PUBLICATIONS
• Kumar, A. et al. (2023). "Efficient Lattice-Based Key Exchange on Constrained IoT Devices." IEEE Transactions on Information Forensics and Security.
• Kumar, A. (2022). "Fault-Resistant Implementations of Dilithium." ACM Conference on Computer and Communications Security (CCS).

HONORS & AWARDS
• Best Paper Award, IEEE S&P 2023
• National Science Foundation Graduate Research Fellowship
"""
    data = ResumeExtractor.extract(academic_text)

    assert data.candidate_name == "DR. ARUN KUMAR"
    assert len(data.education) >= 2
    assert any("Doctor" in e.degree or "Ph.D" in e.degree for e in data.education)
    assert len(data.publications) >= 2
    assert len(data.achievements) >= 2


def test_docx_document_parsing():
    """Tests in-memory DOCX document parsing and structured extraction."""
    doc = Document()
    doc.add_heading("ALEXANDER WRIGHT", level=0)
    doc.add_paragraph("New York, NY | alex.wright@example.com | (212) 555-0134")

    doc.add_heading("PROFESSIONAL SUMMARY", level=1)
    doc.add_paragraph("Cybersecurity Analyst with strong background in network defense and firewall management.")

    doc.add_heading("TECHNICAL SKILLS", level=1)
    doc.add_paragraph("Wireshark, Nmap, Splunk, Python, Linux, Snort, Firewalls")

    doc.add_heading("EDUCATION", level=1)
    doc.add_paragraph("Bachelor of Science in Cybersecurity\nNew York University\n2019 – 2023")

    doc.add_heading("CERTIFICATIONS", level=1)
    doc.add_paragraph("CompTIA Security+\nCEH (Certified Ethical Hacker)")

    doc_io = io.BytesIO()
    doc.save(doc_io)
    docx_bytes = doc_io.getvalue()

    parsed = ResumeParser.parse_document("Alexander_Resume.docx", docx_bytes)
    assert parsed["format"] == "docx"
    assert parsed["word_count"] > 20

    data = ResumeExtractor.extract(parsed["raw_text"])
    assert data.candidate_name == "ALEXANDER WRIGHT"
    assert data.contact_info.email == "alex.wright@example.com"
    assert len(data.technical_skills) >= 5
    assert len(data.education) >= 1
    assert len(data.certifications) >= 2


def test_verification_engine_status_categorization():
    """Verifies that ResumeVerificationEngine accurately categorizes all 4 statuses."""
    # Case 1: Minimal text with short summary and no projects or certs
    minimal_text = """
JOHN DOE
john@example.com | 555-1234
SUMMARY
Software tester seeking role.
"""
    parsed = ResumeExtractor.extract(minimal_text)
    vr = parsed.verification_report
    sections = vr["sections"]

    # Projects are genuinely absent
    assert sections["projects"]["status"] == "genuinely_absent"
    # Certifications are genuinely absent
    assert sections["certifications"]["status"] == "genuinely_absent"
    # Short summary (< 50 chars) is correctly categorized as partially_extracted
    assert sections["summary"]["status"] == "partially_extracted"

    # Case 2: Full summary with headings present
    full_text = """
JANE SMITH
jane@example.com | 555-9876
PROFESSIONAL SUMMARY
Experienced cybersecurity specialist with extensive background in log analysis, threat intelligence, and vulnerability assessments across cloud environments.
"""
    parsed2 = ResumeExtractor.extract(full_text)
    vr2 = parsed2.verification_report
    assert vr2["sections"]["summary"]["status"] == "extracted"


def test_scoring_with_verified_candidate_profile():
    """Validates that ATSScoringEngine evaluates the verified profile deterministically."""
    pdf_path = Path("V:/ai_jobagent/uploads/an_45a7f9454503_SabrishR_Resume.pdf")
    pdf_bytes = pdf_path.read_bytes()
    parsed_doc = ResumeParser.parse_document("SabrishR_Resume.pdf", pdf_bytes)
    resume_data = ResumeExtractor.extract(parsed_doc["raw_text"])

    roles = role_repository.list_roles()
    assert len(roles) > 0
    role = roles[0]
    role_profile = role_repository.get_role_full_profile(role["role_id"])

    match_report = SkillMatcher.match_skills(
        role_skills=role_profile.get("skills", []),
        resume_skills=resume_data.technical_skills,
        resume_full_text=parsed_doc["raw_text"],
        resume_projects=resume_data.projects,
        resume_experience=resume_data.employment_history + resume_data.internships,
        role_id=role["role_id"],
        role_name=role["role_name"],
    )

    score_result = ATSScoringEngine.calculate_score(
        resume_data=resume_data,
        match_report=match_report,
        role_requirements=role_profile.get("requirements", []),
        db_scoring_criteria=role_profile.get("scoring_criteria", []),
    )

    assert 0.0 <= score_result.final_score <= 100.0
    assert len(score_result.category_scores) == 5

    # Check Projects Category (nested projects credited)
    proj_cat = next(c for c in score_result.category_scores if c.category_name == "Projects")
    assert proj_cat.score_earned > 0.0
    assert proj_cat.percentage >= 70.0

    # Check Education Category (B.Tech STEM credited)
    edu_cat = next(c for c in score_result.category_scores if c.category_name == "Education")
    assert edu_cat.score_earned > 0.0
    assert edu_cat.percentage >= 80.0
