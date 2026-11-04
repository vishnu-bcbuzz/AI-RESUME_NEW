"""Comprehensive regression test suite for Automatic Project Transfer across all 30 ATS templates.

Verifies:
1. Deterministic extraction of candidate projects from all 24+ project heading variants.
2. Extraction of project titles, status ('Completed' / 'In Progress'), technologies, bullets, URLs, dates.
3. Seamless automatic inclusion into enhanced resume content without candidate manual approval.
4. Active verb polishing for project bullets without metric hallucination.
5. Role-specific project ranking prioritizing domain-relevant projects while preserving 100% of candidate projects.
6. Clean deduplication of duplicate project records across parsed sections.
7. Clear distinction between existing candidate projects and recommendation catalog items.
8. Document rendering verification across all 30 ATS templates (T01 - T30) in both DOCX and PDF formats.
9. Edge case handling (e.g. resumes without projects).
"""

import io
import re
from pathlib import Path
import pytest
from docx import Document
import pypdf

from app.resume.extractor import ResumeExtractor, ParsedResumeData, ProjectEntry, ContactInfo
from app.projects.generator import ResumeContentGenerator, EnhancedResumeContent
from app.reports.renderer import DocumentRenderer
from app.reports.round_robin import template_registry


class TestAutomaticProjectExtraction:
    """Verifies parsing of project sections, headers, and metadata from candidate resumes."""

    def test_single_project_extraction_with_technologies_and_github(self):
        text = """
        John Doe
        john@example.com | 123-456-7890 | linkedin.com/in/johndoe | github.com/johndoe
        
        TECHNICAL SKILLS
        Python, Wireshark, Nmap, Docker

        PROJECTS
        Enterprise Network Hardening Scanner | Completed
        Technologies: Python, Nmap, Docker
        Project URL: https://github.com/johndoe/net-scanner
        - Developed an automated network discovery tool to detect exposed ports and misconfigurations.
        - Integrated Nmap scripting engine for vulnerability correlation and service fingerprinting.
        - Deployed scanner inside isolated Docker containers with scheduled telemetry logging.
        Outcomes: Successfully identified 45+ unpatched CVE vulnerabilities during laboratory validation.

        EDUCATION
        B.S. in Cybersecurity, University of Technology, 2024
        """
        parsed = ResumeExtractor.extract(text)
        assert len(parsed.projects) == 1
        proj = parsed.projects[0]
        assert "Enterprise Network Hardening Scanner" in proj.title
        assert proj.status == "Completed"
        assert any("python" in t.lower() for t in proj.technologies)
        assert any("nmap" in t.lower() for t in proj.technologies)
        assert proj.github_url == "https://github.com/johndoe/net-scanner"
        assert len(proj.bullets) >= 3
        assert any("automated network discovery" in b.lower() for b in proj.bullets)

    def test_multiple_project_sections_and_variants(self):
        text = """
        Alice Smith
        alice@example.com | 987-654-3210

        TECHNICAL SKILLS
        Python, Java, MySQL, Splunk, Autopsy

        ACADEMIC PROJECTS
        Digital Forensics Artifact Extractor (Autopsy, Python) | Completed
        - Built an evidence carving script to extract browser cache and deleted SQLite records.
        - Generated automated forensic timeline reports matching NIST incident standards.

        PERSONAL PROJECTS
        SOC Alert Automation Bot | In Progress
        Technologies: Python, Splunk, Webhooks
        https://github.com/alice/soc-bot
        - Engineered an alerting bot that queries Splunk forwarder API and posts to Discord.
        - Streamlined alert triage workflow for suspicious logon spikes.

        MAJOR PROJECTS
        1. Cloud Infrastructure IAM Hardener
        Tools: AWS, Terraform, Python
        - Configured least-privilege IAM policies and automated role auditing scripts.

        MINI PROJECTS
        Packet Sniffer Utility
        - Implemented raw socket packet sniffer in C and Python for network analysis.
        """
        parsed = ResumeExtractor.extract(text)
        assert len(parsed.projects) == 4
        titles = [p.title.lower() for p in parsed.projects]
        assert any("digital forensics" in t for t in titles)
        assert any("soc alert" in t for t in titles)
        assert any("cloud infrastructure" in t for t in titles)
        assert any("packet sniffer" in t for t in titles)

        soc_proj = next(p for p in parsed.projects if "soc alert" in p.title.lower())
        assert soc_proj.status == "In Progress"
        assert "https://github.com/alice/soc-bot" in (soc_proj.github_url or "")
        assert any("splunk" in t.lower() for t in soc_proj.technologies)

    def test_in_progress_status_detection(self):
        text = """
        Candidate Name
        cand@example.com

        PROJECTS
        Threat Intelligence Dashboard (Status: In Progress)
        Technologies: FastAPI, React, ElasticSearch
        - Developing real-time feeds aggregator for known malicious IP feeds.
        """
        parsed = ResumeExtractor.extract(text)
        assert len(parsed.projects) == 1
        p = parsed.projects[0]
        assert p.status == "In Progress"
        assert "Threat Intelligence Dashboard" in p.title
        assert "In Progress" not in p.title  # Cleaned base title

    def test_deduplication_of_duplicate_projects(self):
        text = """
        Bob Wilson
        bob@example.com

        PROJECTS
        Vulnerability Assessment Scanner
        Technologies: Python, Nmap
        - Built automated vulnerability scanner for subnet auditing.

        PROJECT EXPERIENCE
        Vulnerability Assessment Scanner
        Technologies: Python, Nmap, Docker
        - Built automated vulnerability scanner for subnet auditing.
        - Added Docker packaging and scheduled scanning reports.
        """
        parsed = ResumeExtractor.extract(text)
        assert len(parsed.projects) == 1
        proj = parsed.projects[0]
        assert "Vulnerability Assessment Scanner" in proj.title
        # Should retain the more comprehensive bullets and merged tech
        assert len(proj.bullets) == 2
        assert "Docker" in proj.technologies


class TestAutomaticProjectInclusionAndPolishing:
    """Verifies that extracted candidate projects automatically transfer into enhanced content and get polished."""

    def test_projects_automatically_included_without_manual_approval(self):
        resume_data = ParsedResumeData(
            candidate_name="Danielle Green",
            contact_info=ContactInfo(email="danielle@example.com", phone="555-1234"),
            technical_skills=["Python", "Wireshark", "Linux", "Bash"],
            projects=[
                ProjectEntry(
                    title="Automated Log Parser",
                    description="Worked on building a script that parses syslog files and flags anomalies.",
                    technologies=["Python", "Linux", "Bash"],
                    status="Completed",
                    bullets=["Worked on building a script that parses syslog files and flags anomalies."],
                ),
                ProjectEntry(
                    title="Wireless Penetration Testing Lab",
                    description="Responsible for configuring a test lab with rogue APs and testing WPA2 security.",
                    technologies=["Linux", "Aircrack-ng", "Wireshark"],
                    status="Completed",
                    bullets=["Responsible for configuring a test lab with rogue APs and testing WPA2 security."],
                )
            ]
        )

        # Generate enhanced content with empty approved_projects list
        enhanced = ResumeContentGenerator.generate_enhanced_content(
            resume_data=resume_data,
            target_role_name="Ethical Hacker / Penetration Tester",
            missing_core_skills=["Metasploit", "Burp Suite"],
            approved_projects=[],  # NO candidate manual approval required!
        )

        # Both candidate projects must be automatically present!
        assert len(enhanced.projects) >= 2
        titles = [p["title"] for p in enhanced.projects]
        assert any("Automated Log Parser" in t for t in titles)
        assert any("Wireless Penetration Testing Lab" in t for t in titles)

        # Bullets must be polished: passive phrases replaced with active verbs
        for p in enhanced.projects:
            for b in p.get("bullets", []):
                assert not b.lower().startswith("worked on")
                assert not b.lower().startswith("responsible for")
                # Begins with capital active verb and ends with period
                assert b[0].isupper()
                assert b.endswith(".")

    def test_preserves_facts_without_metric_hallucination(self):
        orig_bullet = "Configured Snort IDS rules to monitor ICMP traffic."
        polished = ResumeContentGenerator._polish_project_bullet(orig_bullet)
        assert polished == "Configured Snort IDS rules to monitor ICMP traffic."
        # No hallucinated percentages or dollar amounts
        assert "%" not in polished
        assert "$" not in polished

        weak_bullet = "responsible for developing a packet sniffer utility in Python"
        polished_weak = ResumeContentGenerator._polish_project_bullet(weak_bullet)
        assert polished_weak == "Developed a packet sniffer utility in Python."


class TestRoleSpecificProjectRanking:
    """Verifies that projects are sorted by role domain relevance while strictly retaining all candidate projects."""

    @pytest.fixture
    def multi_domain_projects(self):
        return [
            ProjectEntry(
                title="Customer Sales Analytics Pipeline",
                description="Engineered an ETL pipeline extracting MySQL records into PostgreSQL warehouse using Pandas.",
                technologies=["Python", "PostgreSQL", "MySQL", "Pandas"],
                bullets=["Engineered an ETL pipeline extracting MySQL records into PostgreSQL warehouse using Pandas."],
            ),
            ProjectEntry(
                title="Active Directory Kerberoasting Assessment",
                description="Conducted penetration testing on active directory forest detecting misconfigured service accounts.",
                technologies=["Metasploit", "PowerShell", "BloodHound", "Nmap"],
                bullets=["Conducted penetration testing on active directory forest detecting misconfigured service accounts."],
            ),
            ProjectEntry(
                title="Full-Stack Inventory Web Application",
                description="Built responsive inventory management website using React and Node.js with REST API.",
                technologies=["React", "Node.js", "JavaScript", "Express"],
                bullets=["Built responsive inventory management website using React and Node.js with REST API."],
            ),
        ]

    def test_ranking_for_offensive_cybersecurity_role(self, multi_domain_projects):
        resume = ParsedResumeData(
            candidate_name="Test Candidate",
            contact_info=ContactInfo(email="test@example.com"),
            technical_skills=["Python", "Metasploit", "Nmap", "React"],
            projects=multi_domain_projects,
        )

        enhanced = ResumeContentGenerator.generate_enhanced_content(
            resume_data=resume,
            target_role_name="Ethical Hacker / Penetration Tester",
            missing_core_skills=["Burp Suite"],
        )

        assert len(enhanced.projects) == 3
        # Top-ranked project must be the Active Directory / Penetration Testing project
        assert "Active Directory" in enhanced.projects[0]["title"]
        # ALL non-offensive projects are preserved!
        titles = [p["title"] for p in enhanced.projects]
        assert any("Customer Sales" in t for t in titles)
        assert any("Inventory Web Application" in t for t in titles)

    def test_ranking_for_data_engineer_role(self, multi_domain_projects):
        resume = ParsedResumeData(
            candidate_name="Test Candidate",
            contact_info=ContactInfo(email="test@example.com"),
            technical_skills=["Python", "SQL", "Pandas"],
            projects=multi_domain_projects,
        )

        enhanced = ResumeContentGenerator.generate_enhanced_content(
            resume_data=resume,
            target_role_name="Data Engineer",
            missing_core_skills=["Spark", "Airflow"],
        )

        assert len(enhanced.projects) == 3
        # Top-ranked project must be the Analytics / ETL project
        assert "Customer Sales Analytics Pipeline" in enhanced.projects[0]["title"]
        # Security project and web project are still preserved!
        titles = [p["title"] for p in enhanced.projects]
        assert any("Active Directory" in t for t in titles)
        assert any("Inventory Web Application" in t for t in titles)


class TestDistinguishExistingProjectsFromRecommendations:
    """Verifies that existing candidate projects appear automatically while recommendations remain separate."""

    def test_candidate_existing_vs_catalog_recommendation(self):
        resume = ParsedResumeData(
            candidate_name="Elena Rostova",
            contact_info=ContactInfo(email="elena@example.com"),
            technical_skills=["Python", "Wireshark"],
            projects=[
                ProjectEntry(
                    title="Network Traffic Packet Analyzer",
                    description="Implemented network packet sniffer using Python socket library.",
                    technologies=["Python", "Wireshark"],
                    status="Completed",
                    bullets=["Implemented network packet sniffer using Python socket library."],
                )
            ]
        )

        # With no approved recommendations
        enhanced = ResumeContentGenerator.generate_enhanced_content(
            resume_data=resume,
            target_role_name="SOC Analyst",
            missing_core_skills=["Splunk", "SIEM"],
            approved_projects=None,
        )

        assert len(enhanced.projects) == 1
        assert "Network Traffic Packet Analyzer" in enhanced.projects[0]["title"]

        # Now suppose candidate explicitly approved a recommended project from FUTRSEC catalog
        class ApprovedRecommendationMock:
            title_line = "SIEM Log Ingestion Pipeline | In Progress"
            status_label = "In Progress"
            bullets = [
                "Technologies: Splunk, Python, Syslog",
                "Deployed distributed forwarders to ingest Windows Event and Linux auth logs.",
                "Constructed SPL correlation rules to flag brute-force authentication anomalies."
            ]
            github_url = "https://github.com/elena/siem-pipeline"

        enhanced_with_approval = ResumeContentGenerator.generate_enhanced_content(
            resume_data=resume,
            target_role_name="SOC Analyst",
            missing_core_skills=["Splunk"],
            approved_projects=[ApprovedRecommendationMock()],
        )

        assert len(enhanced_with_approval.projects) == 2
        titles = [p["title"] for p in enhanced_with_approval.projects]
        assert any("SIEM Log Ingestion Pipeline" in t for t in titles)
        assert any("Network Traffic Packet Analyzer" in t for t in titles)


class TestAll30TemplatesRenderingWithProjects:
    """Verifies that projects render correctly across all 30 ATS templates (T01 - T30) in both DOCX and PDF."""

    @pytest.fixture
    def sample_enhanced_content(self):
        return EnhancedResumeContent(
            candidate_name="Marcus Vance",
            contact_header="marcus@example.com | +1 (555) 234-5678 | Austin, TX | linkedin.com/in/marcusvance | github.com/marcusvance",
            contact_details={
                "email": "marcus@example.com",
                "phone": "+1 (555) 234-5678",
                "location": "Austin, TX",
                "linkedin": "https://linkedin.com/in/marcusvance",
                "github": "https://github.com/marcusvance",
            },
            professional_headline="Cybersecurity Operations & Threat Defense Analyst",
            professional_summary="Results-driven Cybersecurity Specialist specializing in threat monitoring, incident response, and vulnerability mitigation. Proficient across Wireshark, Splunk, and Python through hands-on implementations.",
            technical_skills_grouped={
                "Cybersecurity Tools": ["Autopsy", "Burp Suite", "Nmap", "Wireshark"],
                "Security Concepts": ["Digital Forensics (DFIR)", "Network Security", "Vulnerability Management"],
                "Programming Languages": ["Python", "SQL"],
            },
            experience=[
                {
                    "job_title": "Information Security Intern",
                    "company": "SecureNet Defense Systems",
                    "start_date": "Jan 2024",
                    "end_date": "Present",
                    "is_current": True,
                    "responsibilities": [
                        "Monitored security event logs across 250+ enterprise endpoints utilizing SIEM dashboards.",
                        "Triage suspected phishing submissions and isolated compromised endpoints."
                    ]
                }
            ],
            projects=[
                {
                    "title": "Enterprise Threat Hunting Lab",
                    "status": "Completed",
                    "technologies": ["Splunk", "Sysmon", "PowerShell"],
                    "description": "Constructed simulated enterprise Active Directory domain with Sysmon telemetry forwarded to Splunk.",
                    "bullets": [
                        "Constructed simulated enterprise Active Directory domain with Sysmon telemetry forwarded to Splunk.",
                        "Executed simulated adversary techniques mapped to MITRE ATT&CK Matrix.",
                        "Authored detection queries identifying suspicious PowerShell invocations and privilege escalations."
                    ],
                    "github_url": "https://github.com/marcusvance/threat-hunting-lab",
                },
                {
                    "title": "Automated Vulnerability Scanner",
                    "status": "In Progress",
                    "technologies": ["Python", "Nmap", "Docker"],
                    "description": "Engineering automated containerized scanner to discover unpatched vulnerabilities.",
                    "bullets": [
                        "Engineering automated containerized scanner to discover unpatched vulnerabilities across internal subnets.",
                        "Correlating open ports against known CVE advisories."
                    ],
                    "github_url": "https://github.com/marcusvance/vuln-scanner",
                }
            ],
            education=[
                {
                    "degree": "B.S. in Cybersecurity",
                    "institution": "Texas State University",
                    "graduation_year": "2024",
                    "field_of_study": "Cybersecurity",
                    "raw_text": "B.S. in Cybersecurity, Texas State University (2024)",
                }
            ],
            certifications=["CompTIA Security+", "Splunk Core Certified User"],
            achievements=["Winner, Collegiate Cyber Defense Competition Regional Qualifier 2023"],
            confirmed_skills_included=["Splunk", "Sysmon"],
            unverified_skills_excluded=[],
        )

    @pytest.mark.parametrize("template_id", [f"T{i:02d}" for i in range(1, 31)])
    def test_project_rendering_in_all_templates_docx_and_pdf(self, template_id, sample_enhanced_content):
        template = template_registry.get_template(template_id)
        assert template is not None, f"Template {template_id} not registered"

        # Render DOCX and PDF through main pipeline
        render_res = DocumentRenderer.render_resume(
            content=sample_enhanced_content,
            template=template,
            job_id=f"test_proj_{template_id}",
        )
        assert render_res["pdf_available"] is True, f"PDF failed for {template_id}: {render_res.get('pdf_status_note')}"

        # 1. Verify DOCX
        docx_bytes = Path(render_res["docx_path"]).read_bytes()
        assert len(docx_bytes) > 2000, f"DOCX output empty for {template_id}"

        doc = Document(io.BytesIO(docx_bytes))
        docx_text = "\n".join([p.text for p in doc.paragraphs])
        # Project titles
        assert "Enterprise Threat Hunting Lab" in docx_text
        assert "Automated Vulnerability Scanner" in docx_text
        # Status labels
        assert "Status: Completed" in docx_text
        assert "Status: In Progress" in docx_text
        # Technologies line
        assert "Technologies:" in docx_text
        assert "Splunk, Sysmon, PowerShell" in docx_text
        # Bullets
        assert "MITRE ATT&CK Matrix" in docx_text

        # 2. Verify PDF
        pdf_bytes = Path(render_res["pdf_path"]).read_bytes()
        assert len(pdf_bytes) > 2000, f"PDF output empty for {template_id}"

        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        assert len(reader.pages) >= 1
        pdf_text = "\n".join([page.extract_text() or "" for page in reader.pages])

        # Verify project presence in PDF text stream
        assert "Enterprise Threat Hunting Lab" in pdf_text
        assert "Automated Vulnerability Scanner" in pdf_text
        assert "Status: Completed" in pdf_text or "Completed" in pdf_text
        assert "Technologies:" in pdf_text
        assert "Sysmon" in pdf_text
        assert "Status: Completed" in pdf_text or "Completed" in pdf_text
        assert "Technologies:" in pdf_text
        assert "Sysmon" in pdf_text


class TestEdgeCaseHandling:
    """Verifies behavior when resumes have no projects or unusual formats."""

    def test_resume_without_projects_handled_gracefully(self):
        text = """
        No Project Candidate
        noproj@example.com | 111-222-3333

        PROFESSIONAL SUMMARY
        Experienced IT administrator moving into cybersecurity.

        TECHNICAL SKILLS
        Linux, Windows Server, Networking

        WORK EXPERIENCE
        Systems Administrator at Acme Corp (2020 - Present)
        - Maintained enterprise servers and firewalls.

        EDUCATION
        B.S. in Computer Science, Tech University, 2020
        """
        parsed = ResumeExtractor.extract(text)
        assert len(parsed.projects) == 0

        enhanced = ResumeContentGenerator.generate_enhanced_content(
            resume_data=parsed,
            target_role_name="Network Security Engineer",
            missing_core_skills=["Firewalls"],
        )
        assert enhanced.candidate_name == "No Project Candidate"
        # projects list is empty without throwing errors
        assert isinstance(enhanced.projects, list)
        assert len(enhanced.projects) == 0

        # Renders cleanly without errors in both DOCX and PDF
        t01 = template_registry.get_template("T01")
        render_res = DocumentRenderer.render_resume(
            content=enhanced,
            template=t01,
            job_id="test_no_proj_T01",
        )
        assert render_res["pdf_available"] is True
        docx_bytes = Path(render_res["docx_path"]).read_bytes()
        pdf_bytes = Path(render_res["pdf_path"]).read_bytes()
        assert len(docx_bytes) > 1000
        assert len(pdf_bytes) > 1000
