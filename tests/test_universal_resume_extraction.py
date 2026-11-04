"""Universal regression test suite for FUTRSEC resume extraction and structured parsing.

Covers 15 distinct candidate resume formats, layouts, and structural variants:
 1. Single-column resume.
 2. Two-column / multi-column resume (PyMuPDF block layout).
 3. Resume with unusual section headings and formatting decorations.
 4. Resume without a summary / objective section.
 5. Fresher resume without work experience.
 6. Resume with multiple projects across different domains.
 7. Resume with multiple certifications.
 8. Resume with long categorized technical skills.
 9. Multi-page PDF resume.
10. Scanned image-based PDF (clear descriptive error).
11. PDF with broken line wrapping and hyphenation.
12. DOCX resume with tables, merged cells, and bullet lists.
13. Fresher resume with projects and education only.
14. Experienced professional resume with extensive employment history.
15. Cybersecurity-focused resume with specialized tools, concepts, and certs.
"""

import io
import pytest
import fitz
from docx import Document

from app.resume.parser import ResumeParser, ResumeParsingError
from app.resume.extractor import (
    ResumeExtractor,
    ResumeExtractionError,
    ParsedResumeData,
    ProjectEntry,
    ExperienceEntry,
    EducationEntry,
)
from app.scoring.matcher import SkillMatcher
from app.scoring.engine import ATSScoringEngine


# Helper to build in-memory PDF
def build_pdf(pages_text: list[str]) -> bytes:
    doc = fitz.open()
    for text in pages_text:
        page = doc.new_page(width=595, height=842)  # A4
        page.insert_text((50, 60), text, fontsize=10)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


class TestUniversalResumeFormats:
    """Universal regression suite validating all 15 resume formats."""

    # 1. Single-column resume
    def test_01_single_column_resume(self):
        text = """
        Marcus Vance
        marcus.vance@defense-sec.io | (415) 555-0199 | San Francisco, CA
        https://linkedin.com/in/marcusvance | https://github.com/marcusvance

        PROFESSIONAL SUMMARY
        Dedicated cybersecurity analyst with 4 years of experience defending cloud infrastructure, performing network vulnerability scans, and configuring SIEM monitoring.

        TECHNICAL SKILLS
        Cybersecurity Tools: Wireshark, Nmap, Burp Suite, Splunk, Snort
        Languages: Python, Bash, SQL
        Operating Systems: Linux, Windows Server

        EXPERIENCE
        SOC Analyst | Apex Defense Systems | 2021 - Present
        - Monitored real-time intrusion alerts using Splunk SIEM and Snort IDS.
        - Triaged and escalated 200+ network security incidents following NIST guidelines.

        PROJECTS
        Automated PCAP Analyzer
        Technologies: Python, Wireshark, Scapy
        - Built automated packet dissection script to detect DNS tunneling and anomalous beaconing.
        - Published open-source telemetry dashboard on GitHub.

        EDUCATION
        Bachelor of Science in Computer Science
        University of California, Berkeley, 2020

        CERTIFICATIONS
        CompTIA Security+
        CompTIA CySA+
        """
        parsed = ResumeExtractor.extract(text)
        assert parsed.candidate_name == "Marcus Vance"
        assert parsed.contact_info.email == "marcus.vance@defense-sec.io"
        assert parsed.contact_info.phone == "(415) 555-0199"
        assert parsed.professional_summary is not None
        assert len(parsed.technical_skills) >= 5
        assert len(parsed.employment_history) == 1
        assert len(parsed.projects) == 1
        assert len(parsed.education) == 1
        assert len(parsed.certifications) == 2
        assert parsed.extraction_metadata["technical_skills"].status == "extracted"

    # 2. Two-column / multi-column resume
    def test_02_two_column_multicolumn_resume(self):
        doc = fitz.open()
        page = doc.new_page(width=600, height=800)
        # Top Header spanning width
        page.insert_textbox(fitz.Rect(50, 30, 550, 80), "Elena Rostova\nelena@cyberintel.org | +1 202-555-0177 | Washington, DC\nhttps://github.com/erostova")
        # Left Column (Skills & Education)
        left_text = (
            "TECHNICAL SKILLS\n"
            "Python, Go, Wireshark, Burp Suite, Docker\n\n"
            "EDUCATION\n"
            "Bachelor of Science in Information Security\n"
            "Georgetown University, 2022\n\n"
            "CERTIFICATIONS\n"
            "CompTIA Security+\n"
            "CEH (Certified Ethical Hacker)\n"
        )
        page.insert_textbox(fitz.Rect(50, 90, 270, 700), left_text)
        # Right Column (Experience & Projects)
        right_text = (
            "PROFESSIONAL SUMMARY\n"
            "Information security specialist focusing on red team operations and vulnerability assessments.\n\n"
            "WORK EXPERIENCE\n"
            "Security Consultant | CyberDefend LLC | 2022 - Present\n"
            "- Performed web application vulnerability assessments using Burp Suite.\n"
            "- Automated reporting workflows using Python scripts.\n\n"
            "PROJECTS\n"
            "Zero Trust Gateway\n"
            "Technologies: Go, Docker, Linux\n"
            "- Built mutual TLS authentication gateway for microservices.\n"
        )
        page.insert_textbox(fitz.Rect(320, 90, 550, 700), right_text)

        buf = io.BytesIO()
        doc.save(buf)
        doc.close()
        pdf_bytes = buf.getvalue()

        parsed_doc = ResumeParser.parse_document("two_column.pdf", pdf_bytes)
        parsed = ResumeExtractor.extract(parsed_doc["raw_text"])

        assert parsed.candidate_name == "Elena Rostova"
        assert parsed.contact_info.email == "elena@cyberintel.org"
        assert len(parsed.technical_skills) >= 4
        assert len(parsed.education) >= 1
        assert len(parsed.employment_history) >= 1
        assert len(parsed.projects) >= 1
        assert len(parsed.certifications) >= 1

    # 3. Resume with unusual section headings
    def test_03_resume_with_unusual_section_headings(self):
        text = """
        Aiden Thorne
        aiden.thorne@proton.me | +44 7700 900123

        ## SUMMARY OF QUALIFICATIONS
        High-performing cybersecurity professional with strong foundation in digital forensics and malware reverse engineering.

        ### TECH STACK & TOOLS
        Wireshark, Autopsy, Ghidra, Python, C++, Linux, Volatility

        === RELEVANT WORK EXPERIENCE ===
        Forensic Investigator | GuardLine Security | 2021 - 2024
        - Extracted filesystem artifacts and analyzed memory dumps.

        1. NOTABLE PROJECTS:
        Memory Dump Artifact Parser
        Technologies: Python, Volatility
        - Developed automated plugin to parse process memory trees.

        [ACADEMIC CREDENTIALS]
        B.S. in Computer Forensics | University of London | 2021

        *** CREDENTIALS & LICENSES ***
        • GIAC Certified Forensic Analyst (GCFA)
        • Certified Ethical Hacker

        ~ KEY ACCOMPLISHMENTS ~
        - 1st place in National Cyber League CTF 2023.
        """
        parsed = ResumeExtractor.extract(text)
        assert parsed.candidate_name == "Aiden Thorne"
        assert parsed.professional_summary is not None
        assert len(parsed.technical_skills) >= 5
        assert len(parsed.employment_history) == 1
        assert len(parsed.projects) == 1
        assert len(parsed.education) == 1
        assert len(parsed.certifications) >= 1
        assert len(parsed.achievements) == 1

    # 4. Resume without a summary
    def test_04_resume_without_summary(self):
        text = """
        David Miller
        david.miller@email.com | 555-123-4567

        TECHNICAL SKILLS
        Python, Java, SQL, Linux, Git

        EDUCATION
        B.S. in Computer Science | Texas A&M University, 2023

        PROJECTS
        Port Scanner Tool
        Technologies: Python, Sockets
        - Built multi-threaded TCP SYN scanner.
        """
        parsed = ResumeExtractor.extract(text)
        assert parsed.candidate_name == "David Miller"
        assert parsed.professional_summary is None
        assert parsed.career_objective is None
        assert parsed.extraction_metadata["summary"].status == "not_found"
        assert len(parsed.technical_skills) >= 4

    # 5. Fresher resume without experience
    def test_05_fresher_resume_without_experience(self):
        text = """
        Priya Sharma
        priya.sharma@gmail.com | +91 98765 43210 | Bengaluru, India

        CAREER OBJECTIVE
        Enthusiastic computer science graduate seeking an entry-level security analyst role to apply practical skills in vulnerability testing and scripting.

        TECHNICAL SKILLS
        Python, C++, SQL, Wireshark, Nmap, Linux

        PROJECTS
        Packet Sniffer and Logger
        Technologies: Python, Scapy
        - Implemented packet capture script analyzing ARP spoofing attacks.

        EDUCATION
        Bachelor of Technology in Information Technology
        Anna University, 2024
        GPA: 8.7

        CERTIFICATIONS
        • Young Professional Python
        • Database Management Systems (DBMS)
        """
        parsed = ResumeExtractor.extract(text)
        assert parsed.candidate_name == "Priya Sharma"
        assert parsed.career_objective is not None
        assert len(parsed.employment_history) == 0
        assert parsed.extraction_metadata["experience"].status == "not_found"
        assert len(parsed.projects) == 1
        assert len(parsed.education) == 1
        assert len(parsed.certifications) == 2

    # 6. Resume with multiple projects
    def test_06_resume_with_multiple_projects(self):
        text = """
        Liam Chen
        liam.chen@devsec.io | 650-555-0144

        TECHNICAL SKILLS
        Python, Go, Docker, AWS, Terraform, Kubernetes

        PROJECTS
        Cloud Security Posture Monitor | Completed
        Technologies: Python, AWS, Boto3
        Project URL: https://github.com/liamchen/cspm-tool
        - Audited AWS S3 bucket policies and IAM roles against CIS benchmarks.

        Kubernetes Network Policy Generator | Completed
        Technologies: Go, Kubernetes
        Project URL: https://github.com/liamchen/k8s-policy-gen
        - Generated automated zero-trust network policies for namespace isolation.

        API Vulnerability Scanner | In Progress
        Technologies: Python, FastAPI, Docker
        Project URL: https://github.com/liamchen/api-sec-scan
        - Scanned REST endpoints for Broken Object Level Authorization (BOLA).

        EDUCATION
        B.S. in Software Engineering, San Jose State University, 2022
        """
        parsed = ResumeExtractor.extract(text)
        assert len(parsed.projects) == 3
        titles = [p.title.lower() for p in parsed.projects]
        assert any("cloud security" in t for t in titles)
        assert any("kubernetes" in t for t in titles)
        assert any("api vulnerability" in t for t in titles)
        api_proj = next(p for p in parsed.projects if "api" in p.title.lower())
        assert api_proj.status == "In Progress"

    # 7. Resume with multiple certifications
    def test_07_resume_with_multiple_certifications(self):
        text = """
        Sofia Alvarez
        sofia@cloudsec.net | 305-555-0188

        TECHNICAL SKILLS
        AWS, Azure, Python, Terraform, Docker

        CERTIFICATIONS
        • AWS Certified Security - Specialty
        • CompTIA Security+
        • Certified Ethical Hacker (CEH)
        • Microsoft Certified: Azure Security Engineer Associate (AZ-500)
        • Young Professional Python

        CODING PROFILES
        LeetCode: leetcode.com/sofia
        HackerRank: hackerrank.com/sofia

        EDUCATION
        B.S. in Computer Science | Florida International University, 2021
        """
        parsed = ResumeExtractor.extract(text)
        assert len(parsed.certifications) == 5
        # Verify coding profiles are strictly excluded from certifications
        for cert in parsed.certifications:
            assert "leetcode" not in cert.lower()
            assert "hackerrank" not in cert.lower()

    # 8. Resume with long technical skills sections
    def test_08_resume_with_long_technical_skills(self):
        text = """
        Alexander Wright
        alex.wright@systems.org | 617-555-0155

        TECHNICAL SKILLS
        Programming Languages: Python, Java, C++, Go, Bash, SQL, JavaScript, TypeScript
        Cybersecurity Tools: Wireshark, Nmap, Burp Suite, Metasploit, Splunk, Snort, Autopsy, Volatility
        Cloud & DevOps: AWS, Docker, Kubernetes, Terraform, Git, GitHub, GitLab, CI/CD, Ansible
        Databases: PostgreSQL, MySQL, MongoDB, Redis
        Operating Systems: Linux, Windows Server, Kali Linux

        EDUCATION
        Master of Science in Cybersecurity | Northeastern University, 2023
        """
        parsed = ResumeExtractor.extract(text)
        assert len(parsed.technical_skills) >= 15
        assert "Python" in parsed.technical_skills
        assert "Wireshark" in parsed.technical_skills
        assert "AWS" in parsed.technical_skills
        assert "PostgreSQL" in parsed.technical_skills

    # 9. Multi-page resume
    def test_09_multi_page_resume(self):
        page1 = """
        Rachel Green
        rachel.green@secops.com | 212-555-0123 | New York, NY
        https://linkedin.com/in/rachelgreen

        PROFESSIONAL SUMMARY
        Experienced SecOps engineer with 6 years leading vulnerability response and SIEM monitoring.

        TECHNICAL SKILLS
        Splunk, Wireshark, Python, Linux, AWS, Snort, Incident Response

        WORK EXPERIENCE
        Senior SecOps Engineer | CyberGuard Financial | 2021 - Present
        - Managed enterprise SIEM logging across 400+ Linux servers.
        - Reduced incident detection-to-containment time by 35%.
        """
        page2 = """
        Rachel Green - Page 2

        WORK EXPERIENCE (CONTINUED)
        Security Analyst | Global Data Corp | 2018 - 2021
        - Triaged phishing and malware alerts.
        - Wrote Python automation scripts for log normalization.

        EDUCATION
        B.S. in Information Systems, NYU, 2018

        CERTIFICATIONS
        CompTIA Security+
        CompTIA CySA+
        """
        pdf_bytes = build_pdf([page1, page2])
        parsed_doc = ResumeParser.parse_document("rachel_multipage.pdf", pdf_bytes)
        assert parsed_doc["metadata"]["page_count"] == 2

        parsed = ResumeExtractor.extract(parsed_doc["raw_text"])
        assert parsed.candidate_name == "Rachel Green"
        assert len(parsed.employment_history) >= 1
        assert len(parsed.education) >= 1
        assert len(parsed.certifications) >= 1

    # 10. Scanned/image-based PDF (clear descriptive error)
    def test_10_scanned_image_based_pdf(self):
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)
        # Insert a 1x1 dummy image pixmap to simulate scanned image
        pix = fitz.Pixmap(fitz.csRGB, (0, 0, 100, 100), 1)
        pix.clear_with(255)
        page.insert_image(fitz.Rect(50, 50, 500, 750), pixmap=pix)
        page.insert_text((50, 800), "Scanned by MobileApp")
        buf = io.BytesIO()
        doc.save(buf)
        doc.close()
        pdf_bytes = buf.getvalue()

        with pytest.raises(ResumeParsingError) as exc_info:
            ResumeParser.parse_document("scanned.pdf", pdf_bytes)

        err_msg = str(exc_info.value)
        assert "scanned image" in err_msg.lower() or "text-searchable" in err_msg.lower()
        assert "OCR" in err_msg or "selectable text" in err_msg.lower()

    # 11. PDF with broken line wrapping
    def test_11_pdf_with_broken_line_wrapping(self):
        text_with_broken_hyphens = """
        Nathan Drake
        nathan@drake-sec.com | 555-987-6543

        TECHNICAL SKILLS
        authenti-
        cation, Vulnerabi-
        lity Management, Cloud-
        Computing, Wire-
        shark

        EDUCATION
        B.S. in Computer Science | Stanford University, 2021
        """
        dehyphenated = ResumeParser.dehyphenate_text(text_with_broken_hyphens)
        assert "authentication" in dehyphenated
        assert "Vulnerability" in dehyphenated
        assert "Wireshark" in dehyphenated

    # 12. DOCX with tables and bullet lists
    def test_12_docx_with_tables_and_bullet_lists(self):
        doc = Document()
        doc.add_heading("Kavita Nair", level=0)
        doc.add_paragraph("kavita.nair@techcorp.in | +91 91234 56789")

        doc.add_heading("Summary", level=1)
        doc.add_paragraph("Security analyst skilled in cloud architecture and vulnerability scanning.")

        doc.add_heading("Technical Skills", level=1)
        # Create a table for skills layout
        table = doc.add_table(rows=2, cols=2)
        table.cell(0, 0).text = "Languages: Python, Java"
        table.cell(0, 1).text = "Tools: Nmap, Wireshark"
        table.cell(1, 0).text = "Databases: MySQL, PostgreSQL"
        table.cell(1, 1).text = "Cloud: AWS, Docker"

        doc.add_heading("Education", level=1)
        doc.add_paragraph("B.E. in Information Technology, Mumbai University, 2022")

        doc.add_heading("Projects", level=1)
        doc.add_paragraph("Vulnerability Scanner Suite")
        doc.add_paragraph("Technologies: Python, Nmap")
        p_bullet = doc.add_paragraph(style='List Bullet')
        p_bullet.add_run("Automated subnet IP sweeping and service fingerprinting.")

        buf = io.BytesIO()
        doc.save(buf)
        docx_bytes = buf.getvalue()

        parsed_doc = ResumeParser.parse_document("kavita_resume.docx", docx_bytes)
        parsed = ResumeExtractor.extract(parsed_doc["raw_text"])

        assert parsed.candidate_name == "Kavita Nair"
        assert len(parsed.technical_skills) >= 4
        assert len(parsed.education) == 1
        assert len(parsed.projects) == 1

    # 13. Fresher resume with projects and education only
    def test_13_fresher_resume_projects_and_education_only(self):
        text = """
        Tariq Mansoor
        tariq.m@gatech.edu | 404-555-0166 | Atlanta, GA
        https://github.com/tariq-m

        EDUCATION
        Bachelor of Science in Computer Science
        Georgia Institute of Technology, May 2024
        GPA: 3.9

        PROJECTS
        Distributed Key-Value Store
        Technologies: Go, Docker, Raft
        Project URL: https://github.com/tariq-m/raft-kv
        - Implemented leader election and log replication using the Raft consensus algorithm.
        - Evaluated partition tolerance across 5 simulated nodes in Docker.

        Secure File Transfer Protocol
        Technologies: Python, Cryptography, Sockets
        - Built encrypted transport layer utilizing AES-GCM and RSA key exchange.
        """
        parsed = ResumeExtractor.extract(text)
        assert parsed.candidate_name == "Tariq Mansoor"
        assert len(parsed.employment_history) == 0
        assert len(parsed.certifications) == 0
        assert len(parsed.education) == 1
        assert len(parsed.projects) == 2

        # Verify ATS scoring handles missing optional sections without throwing exceptions
        mock_report = SkillMatcher.match_skills(
            role_skills=[{"skill_name": "Python", "importance": "core"}, {"skill_name": "Docker", "importance": "preferred"}],
            resume_skills=parsed.technical_skills,
            resume_full_text=text,
            resume_projects=parsed.projects,
            resume_experience=parsed.employment_history,
            role_id=1,
            role_name="Software Security Engineer",
        )
        score_res = ATSScoringEngine.calculate_score(
            resume_data=parsed,
            match_report=mock_report,
            role_requirements=[],
            db_scoring_criteria=[],
        )
        assert 0.0 <= score_res.final_score <= 100.0

    # 14. Experienced professional resume with extensive history
    def test_14_experienced_professional_resume(self):
        text = """
        Christopher Martinez
        chris.martinez@enterprise-sec.com | 312-555-0182 | Chicago, IL
        https://linkedin.com/in/chrismartinez

        EXECUTIVE SUMMARY
        Principal security engineer with 12+ years directing incident response teams, enterprise network defense, and zero-trust migrations.

        CORE COMPETENCIES
        SIEM Architecture, Threat Hunting, Penetration Testing, Python, Linux, AWS Security, Splunk, CrowdStrike

        PROFESSIONAL EXPERIENCE
        Principal Security Engineer | Citadel Defense | 2020 - Present
        - Led cross-functional team of 8 SOC analysts defending financial infrastructure.
        - Architected automated SOAR playbooks reducing mean-time-to-remediate from 4 hours to 18 minutes.

        Senior Security Analyst | Midwest Financial | 2016 - 2020
        - Conducted continuous network monitoring and threat hunting across 1,200 endpoints.
        - Deployed Splunk enterprise cluster and designed custom alert correlation searches.

        Security Operations Specialist | Global Telco | 2012 - 2016
        - Triaged tier 1 and tier 2 firewall alerts and investigated phishing attempts.

        EDUCATION
        B.S. in Computer Engineering | University of Illinois Urbana-Champaign, 2012

        PROFESSIONAL CERTIFICATIONS
        • Certified Information Systems Security Professional (CISSP)
        • Certified Ethical Hacker (CEH)
        """
        parsed = ResumeExtractor.extract(text)
        assert parsed.candidate_name == "Christopher Martinez"
        assert len(parsed.employment_history) >= 2
        assert len(parsed.certifications) >= 1
        assert len(parsed.education) == 1
        assert parsed.professional_summary is not None

    # 15. Cybersecurity-focused resume with specialized tools and certs
    def test_15_cybersecurity_specialized_resume(self):
        text = """
        Zara Khan
        zara.khan@offensive-sec.io | +1 617-555-0190 | Boston, MA
        https://github.com/zarakhan | https://linkedin.com/in/zarakhan

        PROFESSIONAL SUMMARY
        Offensive cybersecurity specialist with hands-on expertise in web application security testing, exploit development, and network penetration testing.

        TECHNICAL SKILLS
        Cybersecurity Tools: Burp Suite, Metasploit, Nmap, Wireshark, Kali Linux, Ghidra, Nessus, SQLMap
        Security Concepts: OWASP Top 10, Penetration Testing, Vulnerability Assessment, Network Security
        Languages: Python, Bash, C, Assembly (x86/x64)

        PROJECTS
        Web Application Exploit Lab
        Technologies: Burp Suite, Python, OWASP Top 10
        Project URL: https://github.com/zarakhan/exploit-lab
        - Crafted manual payloads for SQL injection, stored XSS, and SSRF vulnerabilities.
        - Automated vulnerability verification scripts in Python.

        Enterprise Active Directory Penetration Test
        Technologies: Metasploit, Nmap, Kali Linux
        - Executed kerberoasting and privilege escalation simulations in isolated lab domain.

        CERTIFICATIONS
        • Offensive Security Certified Professional (OSCP)
        • Certified Ethical Hacker (CEH)
        • CompTIA Security+

        EDUCATION
        B.S. in Cybersecurity | Northeastern University, 2023
        """
        parsed = ResumeExtractor.extract(text)
        assert parsed.candidate_name == "Zara Khan"
        assert len(parsed.technical_skills) >= 8
        assert any("burp suite" in s.lower() for s in parsed.technical_skills)
        assert any("metasploit" in s.lower() for s in parsed.technical_skills)
        assert len(parsed.projects) == 2
        assert len(parsed.certifications) == 3
        assert "OSCP" in parsed.certifications or "Offensive Security Certified Professional (OSCP)" in parsed.certifications
        assert len(parsed.education) == 1

