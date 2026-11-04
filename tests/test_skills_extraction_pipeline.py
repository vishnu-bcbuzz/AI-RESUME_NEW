"""Comprehensive test suite for Technical Skills Extraction, Classification,
Normalization, Data Cleaning, and Point-Wise Rendering across all templates.
"""

import pytest
import os
import fitz
import docx
from typing import Dict, List

from app.resume.skills_taxonomy import (
    is_valid_technical_skill,
    normalize_skill_name,
    classify_skill,
    structure_and_classify_skills,
    STANDARD_CATEGORIES,
    CATEGORY_CYBER_TOOLS,
    CATEGORY_SEC_CONCEPTS,
    CATEGORY_PROG_LANGUAGES,
    CATEGORY_OPERATING_SYSTEMS,
    CATEGORY_FRAMEWORKS,
    CATEGORY_DATABASES,
    CATEGORY_CLOUD_DEVOPS,
    CATEGORY_DATA_SCIENCE,
    CATEGORY_NETWORKING,
)
from app.resume.extractor import ParsedResumeData, ContactInfo, ExperienceEntry, ProjectEntry, EducationEntry, ResumeExtractor
from app.resume.validator import ResumeContentValidator, ValidationReport
from app.projects.generator import ResumeContentGenerator, EnhancedResumeContent
from app.reports.renderer import DocumentRenderer
from app.reports.templates import template_registry, ResumeTemplate


class TestSkillValidationAndFiltering:
    """Verifies that non-skills are strictly rejected with zero false positives."""

    def test_rejects_personal_contact_information(self):
        contact = ContactInfo(
            email="alex.turner@cyberdefense.org",
            phone="+1 (555) 789-2341",
            location="San Francisco, California, USA",
            linkedin="https://linkedin.com/in/alexturner-sec",
            github="https://github.com/alexturner",
        )
        candidate_name = "Alex Turner"

        # Explicit candidate details
        assert not is_valid_technical_skill("Alex Turner", candidate_name, contact)
        assert not is_valid_technical_skill("alex.turner@cyberdefense.org", candidate_name, contact)
        assert not is_valid_technical_skill("+1 (555) 789-2341", candidate_name, contact)
        assert not is_valid_technical_skill("San Francisco, CA", candidate_name, contact)
        assert not is_valid_technical_skill("https://linkedin.com/in/alexturner-sec", candidate_name, contact)
        assert not is_valid_technical_skill("github.com/alexturner", candidate_name, contact)

        # Generic contact patterns
        assert not is_valid_technical_skill("john.doe@gmail.com")
        assert not is_valid_technical_skill("9876543210")
        assert not is_valid_technical_skill("+91 98450 12345")
        assert not is_valid_technical_skill("New York, NY")
        assert not is_valid_technical_skill("Bengaluru, Karnataka")

    def test_rejects_company_names_and_job_titles(self):
        job_terms = [
            "Senior Security Engineer",
            "Software Development Intern",
            "Vanguard Cyber Defense Corp",
            "Google LLC",
            "Microsoft Corporation",
            "Systems Administrator",
            "Full-Time Employee",
            "Internship",
            "Part-Time Trainee",
            "Team Lead",
        ]
        for term in job_terms:
            assert not is_valid_technical_skill(term), f"Expected '{term}' to be rejected as a non-skill"

    def test_rejects_dates_and_employment_durations(self):
        date_terms = [
            "June 2021 – Present",
            "2020 - 2024",
            "Jan 2022 to May 2023",
            "3 years",
            "August 2019",
            "Current",
            "Present",
        ]
        for term in date_terms:
            assert not is_valid_technical_skill(term), f"Expected '{term}' to be rejected as a non-skill"

    def test_rejects_education_and_degree_information(self):
        edu_terms = [
            "Bachelor of Science in Computer Science",
            "B.Tech in Information Security",
            "Master of Science in Cybersecurity",
            "Stanford University",
            "MIT",
            "GPA: 3.8/4.0",
            "Dean's Honor List",
            "Graduated Magna Cum Laude",
            "High School Diploma",
        ]
        for term in edu_terms:
            assert not is_valid_technical_skill(term), f"Expected '{term}' to be rejected as a non-skill"

    def test_rejects_certifications(self):
        cert_terms = [
            "Certified Ethical Hacker (CEH v12)",
            "CompTIA Security+ (SY0-601)",
            "CISSP",
            "OSCP",
            "AWS Certified Solutions Architect",
            "CISM",
            "CISA",
        ]
        for term in cert_terms:
            assert not is_valid_technical_skill(term), f"Expected '{term}' to be rejected from skills section"

    def test_rejects_project_descriptions_and_outcomes(self):
        descriptions = [
            "Deployed isolated multi-node virtual environment simulating enterprise subnet topologies",
            "Configured stateful host firewalls with iptables reducing exposure by 75%",
            "Conducted automated network port scans with Nmap and OpenVAS to establish baselines",
            "Remediated critical vulnerabilities across test machines",
        ]
        for desc in descriptions:
            assert not is_valid_technical_skill(desc), f"Expected long description to be rejected: '{desc}'"

    def test_rejects_evaluation_metrics_and_statistics(self):
        metrics = [
            "MAE", "RMSE", "MSE", "R2 Score", "R²", "Accuracy: 95%",
            "Precision", "Recall", "ROC AUC", "Loss: 0.04", "EDA",
            "Mean Absolute Error", "Root Mean Square Error",
        ]
        for metric in metrics:
            assert not is_valid_technical_skill(metric), f"Expected metric '{metric}' to be rejected"


class TestSkillNormalizationAndClassification:
    """Verifies standard 9 categories and canonical name normalization."""

    def test_skill_normalization(self):
        assert normalize_skill_name("postgres") == "PostgreSQL"
        assert normalize_skill_name("POSTGRESQL") == "PostgreSQL"
        assert normalize_skill_name("burp") == "Burp Suite"
        assert normalize_skill_name("burp suite") == "Burp Suite"
        assert normalize_skill_name("react") == "React.js"
        assert normalize_skill_name("reactjs") == "React.js"
        assert normalize_skill_name("aws") == "AWS"
        assert normalize_skill_name("amazon web services") == "AWS"
        assert normalize_skill_name("k8s") == "Kubernetes"
        assert normalize_skill_name("py") == "Python"
        assert normalize_skill_name("golang") == "Go"

    def test_classification_into_9_standard_categories(self):
        # 1. Cybersecurity Tools
        assert classify_skill("Burp Suite") == CATEGORY_CYBER_TOOLS
        assert classify_skill("Nmap") == CATEGORY_CYBER_TOOLS
        assert classify_skill("Wireshark") == CATEGORY_CYBER_TOOLS
        assert classify_skill("Metasploit") == CATEGORY_CYBER_TOOLS
        assert classify_skill("OpenVAS") == CATEGORY_CYBER_TOOLS
        assert classify_skill("Nessus") == CATEGORY_CYBER_TOOLS
        assert classify_skill("Splunk") == CATEGORY_CYBER_TOOLS

        # 2. Security Concepts
        assert classify_skill("Penetration Testing") == CATEGORY_SEC_CONCEPTS
        assert classify_skill("Vulnerability Assessment") == CATEGORY_SEC_CONCEPTS
        assert classify_skill("Incident Response") == CATEGORY_SEC_CONCEPTS
        assert classify_skill("Threat Modeling") == CATEGORY_SEC_CONCEPTS
        assert classify_skill("Cryptography") == CATEGORY_SEC_CONCEPTS
        assert classify_skill("Zero Trust") == CATEGORY_SEC_CONCEPTS

        # 3. Programming Languages
        assert classify_skill("Python") == CATEGORY_PROG_LANGUAGES
        assert classify_skill("Java") == CATEGORY_PROG_LANGUAGES
        assert classify_skill("C++") == CATEGORY_PROG_LANGUAGES
        assert classify_skill("JavaScript") == CATEGORY_PROG_LANGUAGES
        assert classify_skill("TypeScript") == CATEGORY_PROG_LANGUAGES
        assert classify_skill("SQL") == CATEGORY_PROG_LANGUAGES
        assert classify_skill("Bash") == CATEGORY_PROG_LANGUAGES

        # 4. Operating Systems
        assert classify_skill("Linux") == CATEGORY_OPERATING_SYSTEMS
        assert classify_skill("Ubuntu") == CATEGORY_OPERATING_SYSTEMS
        assert classify_skill("Kali Linux") == CATEGORY_OPERATING_SYSTEMS
        assert classify_skill("Windows Server") == CATEGORY_OPERATING_SYSTEMS

        # 5. Frameworks & Libraries
        assert classify_skill("FastAPI") == CATEGORY_FRAMEWORKS
        assert classify_skill("Django") == CATEGORY_FRAMEWORKS
        assert classify_skill("Flask") == CATEGORY_FRAMEWORKS
        assert classify_skill("React.js") == CATEGORY_FRAMEWORKS
        assert classify_skill("Node.js") == CATEGORY_FRAMEWORKS
        assert classify_skill("Spring Boot") == CATEGORY_FRAMEWORKS

        # 6. Databases
        assert classify_skill("PostgreSQL") == CATEGORY_DATABASES
        assert classify_skill("MySQL") == CATEGORY_DATABASES
        assert classify_skill("MongoDB") == CATEGORY_DATABASES
        assert classify_skill("Redis") == CATEGORY_DATABASES
        assert classify_skill("SQLite") == CATEGORY_DATABASES

        # 7. Cloud & DevOps
        assert classify_skill("AWS") == CATEGORY_CLOUD_DEVOPS
        assert classify_skill("Docker") == CATEGORY_CLOUD_DEVOPS
        assert classify_skill("Kubernetes") == CATEGORY_CLOUD_DEVOPS
        assert classify_skill("Terraform") == CATEGORY_CLOUD_DEVOPS
        assert classify_skill("Git") == CATEGORY_CLOUD_DEVOPS
        assert classify_skill("CI/CD") == CATEGORY_CLOUD_DEVOPS

        # 8. Data Science & Machine Learning
        assert classify_skill("Pandas") == CATEGORY_DATA_SCIENCE
        assert classify_skill("NumPy") == CATEGORY_DATA_SCIENCE
        assert classify_skill("PyTorch") == CATEGORY_DATA_SCIENCE
        assert classify_skill("TensorFlow") == CATEGORY_DATA_SCIENCE
        assert classify_skill("Scikit-Learn") == CATEGORY_DATA_SCIENCE

        # 9. Networking Technologies
        assert classify_skill("TCP/IP") == CATEGORY_NETWORKING
        assert classify_skill("DNS") == CATEGORY_NETWORKING
        assert classify_skill("Firewall Configuration") == CATEGORY_NETWORKING
        assert classify_skill("Packet Analysis") == CATEGORY_NETWORKING

    def test_unclassified_gibberish_returns_none(self):
        # Must return None rather than defaulting to Cybersecurity Tools
        assert classify_skill("RandomString12345") is None
        assert classify_skill("Acme Corporation") is None
        assert classify_skill("Senior Manager") is None


class TestStructuredSkillsPipeline:
    """Verifies end-to-end cleaning and classification of noisy skill lists."""

    def test_structure_and_classify_skills_filters_corrupted_tokens(self):
        noisy_input = [
            # Legitimate skills
            "Python", "burp suite", "wireshark", "nmap", "postgres", "Docker", "aws", "Linux",
            # Candidate contact info
            "Jordan Hayes", "jordan@cybersec.io", "+1 555-438-9201", "San Francisco, CA",
            # Company and job titles
            "Vanguard Cyber Defense Corp", "Security Operations Analyst", "Software Engineer",
            # Degrees and certs
            "Bachelor of Science in Computer Science", "CompTIA Security+", "CEH v12",
            # Metrics
            "MAE: 0.12", "RMSE", "R2: 0.94", "EDA",
            # Duplicates in different cases
            "PYTHON", "PostgreSQL", "DOCKER",
        ]

        contact = ContactInfo(
            email="jordan@cybersec.io",
            phone="+1 555-438-9201",
            location="San Francisco, CA",
        )

        result = structure_and_classify_skills(
            raw_skills=noisy_input,
            candidate_name="Jordan Hayes",
            contact_info=contact,
            target_role_name="SOC Analyst",
        )

        # 1. No contact info, companies, jobs, certs, or metrics present
        all_flattened = [s.lower() for skills in result.values() for s in skills]
        assert "jordan hayes" not in all_flattened
        assert "jordan@cybersec.io" not in all_flattened
        assert "vanguard cyber defense corp" not in all_flattened
        assert "security operations analyst" not in all_flattened
        assert "bachelor of science in computer science" not in all_flattened
        assert "comptia security+" not in all_flattened
        assert "mae: 0.12" not in all_flattened
        assert "rmse" not in all_flattened

        # 2. Genuine skills normalized and categorized
        assert "Python" in result[CATEGORY_PROG_LANGUAGES]
        assert "Burp Suite" in result[CATEGORY_CYBER_TOOLS]
        assert "Wireshark" in result[CATEGORY_CYBER_TOOLS]
        assert "Nmap" in result[CATEGORY_CYBER_TOOLS]
        assert "PostgreSQL" in result[CATEGORY_DATABASES]
        assert "Docker" in result[CATEGORY_CLOUD_DEVOPS]
        assert "AWS" in result[CATEGORY_CLOUD_DEVOPS]
        assert "Linux" in result[CATEGORY_OPERATING_SYSTEMS]

        # 3. Deduplication succeeded: Python and Docker only appear once
        assert result[CATEGORY_PROG_LANGUAGES].count("Python") == 1
        assert result[CATEGORY_CLOUD_DEVOPS].count("Docker") == 1
        assert result[CATEGORY_DATABASES].count("PostgreSQL") == 1

        # 4. Empty categories are omitted
        for cat, items in result.items():
            assert len(items) > 0, f"Category '{cat}' is empty but was not omitted"


class TestValidatorAndGeneratorIntegration:
    """Verifies validator and generator enforce clean technical skills."""

    def test_validator_cleans_corrupted_skills(self):
        corrupted_content = EnhancedResumeContent(
            candidate_name="Morgan Reed",
            contact_header="morgan.reed@example.com | 555-0192 | Boston, MA",
            contact_details={"email": "morgan.reed@example.com", "phone": "555-0192", "location": "Boston, MA"},
            professional_headline="Cybersecurity Analyst",
            professional_summary="Practitioner with experience in threat analysis and network defense.",
            technical_skills_grouped={
                "Cybersecurity Tools": ["Burp Suite", "Morgan Reed", "555-0192", "Nmap"],
                "Programming Languages": ["Python", "Acme Corporation", "Senior Analyst", "SQL"],
                "Invalid Group": ["RMSE", "Bachelor of Science", "CEH"],
            },
            experience=[],
            projects=[],
            education=[],
            certifications=["CompTIA Security+"],
            achievements=[],
        )

        report = ValidationReport()
        ResumeContentValidator._validate_and_sanitize_skills(corrupted_content, report)

        cleaned = corrupted_content.technical_skills_grouped
        flattened = [s.lower() for skills in cleaned.values() for s in skills]

        assert "morgan reed" not in flattened
        assert "555-0192" not in flattened
        assert "acme corporation" not in flattened
        assert "senior analyst" not in flattened
        assert "rmse" not in flattened
        assert "bachelor of science" not in flattened
        assert "ceh" not in flattened

        assert "Burp Suite" in cleaned[CATEGORY_CYBER_TOOLS]
        assert "Nmap" in cleaned[CATEGORY_CYBER_TOOLS]
        assert "Python" in cleaned[CATEGORY_PROG_LANGUAGES]
        assert "SQL" in cleaned[CATEGORY_PROG_LANGUAGES]


class TestDocumentRenderingCompactSkills:
    """Verifies that all templates render compact comma-separated skills in DOCX and PDF."""

    def test_render_docx_and_pdf_with_compact_skills(self, tmp_path):
        sample = EnhancedResumeContent(
            candidate_name="Jordan Hayes",
            contact_header="jordan.hayes@cybersec.io | +1 (555) 438-9201 | San Francisco, CA",
            contact_details={"email": "jordan.hayes@cybersec.io", "phone": "+1 (555) 438-9201", "location": "San Francisco, CA"},
            professional_headline="Cybersecurity Specialist",
            professional_summary="Dedicated security professional with proven experience in vulnerability assessments and network defense.",
            technical_skills_grouped={
                "Cybersecurity Tools": ["Burp Suite", "Nmap", "Wireshark", "OpenVAS"],
                "Programming Languages": ["Python", "Java", "SQL"],
            },
            experience=[
                {
                    "job_title": "Security Analyst",
                    "company": "Vanguard Security",
                    "start_date": "2022",
                    "end_date": "Present",
                    "responsibilities": ["Executed vulnerability scans using OpenVAS."],
                }
            ],
            projects=[
                {
                    "title": "Network Hardening Lab",
                    "description": "Configured firewall rules.",
                    "technologies": ["Nmap", "Wireshark"],
                    "bullets": ["Configured stateful host firewalls."],
                }
            ],
            education=[
                {"degree": "B.S. in Computer Science", "institution": "State University", "graduation_year": "2022"}
            ],
            certifications=["CompTIA Security+"],
            achievements=["1st Place Cyber Defense Competition"],
        )

        tmpl = template_registry.get_template("T01")
        result = DocumentRenderer.render_resume(sample, tmpl, job_id="test_compact_render")

        docx_path = result["docx_path"]
        pdf_path = result["pdf_path"]

        assert os.path.exists(docx_path)
        assert os.path.exists(pdf_path)

        # 1. Inspect DOCX: One compact paragraph per category, bold label, comma-separated skills
        doc = docx.Document(docx_path)
        cyber_p = next((p for p in doc.paragraphs if "Cybersecurity Tools:" in p.text), None)
        assert cyber_p is not None, "Expected paragraph with 'Cybersecurity Tools:' in DOCX"
        assert cyber_p.text == "Cybersecurity Tools: Burp Suite, Nmap, Wireshark, OpenVAS"
        assert cyber_p.paragraph_format.space_before == 0 or cyber_p.paragraph_format.space_before is None
        assert cyber_p.paragraph_format.space_after.pt in (2.0, 2.5, 3.0)

        # Check bold label and regular skills
        assert len(cyber_p.runs) >= 2
        assert cyber_p.runs[0].bold is True
        assert cyber_p.runs[0].text == "Cybersecurity Tools: "
        assert cyber_p.runs[1].bold is False
        assert "Burp Suite, Nmap, Wireshark, OpenVAS" in cyber_p.runs[1].text

        prog_p = next((p for p in doc.paragraphs if "Programming Languages:" in p.text), None)
        assert prog_p is not None, "Expected paragraph with 'Programming Languages:' in DOCX"
        assert prog_p.text == "Programming Languages: Python, Java, SQL"
        assert prog_p.runs[0].bold is True
        assert prog_p.runs[1].bold is False

        # No individual skill bullets should exist in the skills section
        docx_bullet_texts = [p.text for p in doc.paragraphs if p.style.name == "List Bullet"]
        assert "Burp Suite" not in docx_bullet_texts
        assert "Python" not in docx_bullet_texts

        # 2. Inspect PDF: Compact text, category and comma-separated skills together
        pdf_doc = fitz.open(pdf_path)
        pdf_text = ""
        for page in pdf_doc:
            pdf_text += page.get_text()

        assert "Cybersecurity Tools:" in pdf_text
        assert "Burp Suite, Nmap, Wireshark, OpenVAS" in pdf_text
        assert "Programming Languages:" in pdf_text
        assert "Python, Java, SQL" in pdf_text
