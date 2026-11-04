"""Structured information extraction module for candidate resumes.

Extracts candidate contact details, summary, technical skills, education,
certifications, projects, work experience, internships, and achievements.
Uses deterministic rule-based NLP and section boundary parsing.
Never fabricates missing data.
"""

import re
from typing import List, Dict, Any, Optional, Tuple, Set
from pydantic import BaseModel, Field

from app.resume.skills_taxonomy import (
    is_valid_technical_skill,
    normalize_skill_name,
    NORMALIZATION_MAP,
    CATEGORY_MAPPING,
)
from app.resume.verifier import ResumeVerificationEngine


class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None


class EducationEntry(BaseModel):
    degree: str
    field_of_study: Optional[str] = None
    specialization: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[str] = None
    gpa: Optional[str] = None
    cgpa: Optional[str] = None
    percentage: Optional[str] = None
    raw_text: Optional[str] = None


class ProjectEntry(BaseModel):
    title: str
    description: str
    technologies: List[str] = Field(default_factory=list)
    outcomes: Optional[str] = None
    status: Optional[str] = "Completed"
    github_url: Optional[str] = None
    project_url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)
    is_nested: bool = False
    parent_context: Optional[str] = None


class ExperienceEntry(BaseModel):
    job_title: str
    company: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    responsibilities: List[str] = Field(default_factory=list)
    raw_text: Optional[str] = None


class CertificationEntry(BaseModel):
    name: str = ""
    certification_name: str = ""
    issuing_organization: Optional[str] = None
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    date: Optional[str] = None
    expiration_date: Optional[str] = None
    credential_id: Optional[str] = None
    url: Optional[str] = None

    def __init__(self, **data: Any):
        if "name" in data and "certification_name" not in data:
            data["certification_name"] = data["name"]
        elif "certification_name" in data and "name" not in data:
            data["name"] = data["certification_name"]
        if "issuer" in data and "issuing_organization" not in data:
            data["issuing_organization"] = data["issuer"]
        elif "issuing_organization" in data and "issuer" not in data:
            data["issuer"] = data["issuing_organization"]
        if "date" in data and "issue_date" not in data:
            data["issue_date"] = data["date"]
        elif "issue_date" in data and "date" not in data:
            data["date"] = data["issue_date"]
        super().__init__(**data)


class ResumeExtractionError(Exception):
    """Custom exception raised when resume extraction fails on unrecoverable issues."""
    pass


class SectionMetadata(BaseModel):
    status: str = "not_found"  # extracted, partially_extracted, not_found, ambiguous, fallback_used
    confidence: float = 0.0     # 0.0 to 1.0
    heading_detected: Optional[str] = None
    item_count: int = 0
    extraction_method: str = "direct"  # direct, fallback_scan, none


class ParsedResumeData(BaseModel):
    candidate_name: Optional[str] = None
    contact_info: ContactInfo = Field(default_factory=ContactInfo)
    career_objective: Optional[str] = None
    professional_summary: Optional[str] = None
    technical_skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    education: List[EducationEntry] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    structured_certifications: List[CertificationEntry] = Field(default_factory=list)
    projects: List[ProjectEntry] = Field(default_factory=list)
    employment_history: List[ExperienceEntry] = Field(default_factory=list)
    internships: List[ExperienceEntry] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    publications: List[str] = Field(default_factory=list)
    raw_sections: Dict[str, str] = Field(default_factory=dict)
    extraction_metadata: Dict[str, SectionMetadata] = Field(default_factory=dict)
    verification_report: Dict[str, Any] = Field(default_factory=dict)


class ResumeExtractor:
    """Extracts structured information from raw resume text."""

    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    PHONE_PATTERN = re.compile(r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b")
    LINKEDIN_PATTERN = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+", re.IGNORECASE)
    GITHUB_PATTERN = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*", re.IGNORECASE)

    # Standard heading aliases across 9 core resume categories
    HEADING_ALIASES: Dict[str, List[str]] = {
        "summary": [
            "professional summary", "summary", "profile", "professional profile",
            "about me", "career objective", "objective", "executive summary",
            "summary of qualifications", "background", "overview", "career profile",
            "profile summary", "personal profile", "professional overview",
            "biography", "bio", "qualification summary", "career summary",
        ],
        "objective": [
            "career objective", "objective", "professional objective", "target role",
        ],
        "skills": [
            "technical skills", "skills", "core competencies", "key skills",
            "skills & tools", "skills and tools", "technical proficiencies",
            "areas of expertise", "technologies", "tech stack", "programming languages",
            "tools & technologies", "tools and technologies", "hard skills",
            "skills matrix", "technical competencies", "technical expertise",
            "technical knowledge", "skills & technologies", "skills and technologies",
            "core skills", "it skills", "computer skills", "software skills",
            "technical toolset", "competencies", "areas of knowledge",
            "technical skillset", "technical background",
        ],
        "experience": [
            "work experience", "professional experience", "employment history",
            "experience", "work history", "professional background",
            "relevant experience", "career history", "employment",
            "career experience", "work background", "experience highlights",
            "practical experience", "industry experience", "career background",
            "relevant work experience", "cybersecurity experience",
        ],
        "internships": [
            "internships", "internship experience", "internship history",
            "internship", "practical training", "practicum", "industrial training",
        ],
        "education": [
            "education", "academic background", "academic qualifications",
            "educational qualifications", "qualifications", "degrees",
            "academic credentials", "educational background", "academic history",
            "education & training", "education and training", "academic record",
            "higher education", "educational credentials", "academic profile",
        ],
        "certifications": [
            "certifications", "licenses & certifications", "licenses and certifications",
            "professional certifications", "certificates", "credentials",
            "accreditations", "certifications & credentials", "certifications and credentials",
            "professional credentials", "certificates & licenses", "certificates and licenses",
            "certifications & training", "certifications and training",
            "training & certifications", "training and certifications",
            "licenses", "industry certifications",
        ],
        "projects": [
            "projects", "academic projects", "personal projects", "technical projects",
            "professional projects", "key projects", "notable projects", "major projects",
            "selected projects", "project experience", "project portfolio",
            "capstone projects", "capstone project", "coursework projects",
            "mini projects", "recent projects", "software projects",
            "systems projects", "system projects", "engineering projects",
            "applied projects", "relevant projects", "hands-on projects",
            "practical projects", "client projects", "industry projects",
            "research projects", "project work", "development projects",
            "cybersecurity projects", "project highlights", "portfolio",
        ],
        "achievements": [
            "achievements", "honors & awards", "honors and awards",
            "key achievements", "awards", "recognitions", "accomplishments",
            "awards & honors", "awards and honors", "honors",
            "key accomplishments", "extracurricular achievements",
            "extracurricular activities", "activities & achievements",
        ],
        "languages": [
            "languages", "languages known", "language proficiencies",
            "linguistic skills", "languages spoken", "language skills",
        ],
        "soft_skills": [
            "soft skills", "interpersonal skills", "personal skills",
            "leadership skills", "behavioral skills",
        ],
        "publications": [
            "publications", "research papers", "papers published",
            "published works", "academic publications", "conference papers",
        ],
        "coding_profiles": [
            "coding profiles", "coding profile", "coding platforms",
            "competitive programming", "coding handles", "online judges",
        ],
    }

    # Standard section heading regex patterns
    SECTION_HEADERS = {
        "summary": re.compile(
            r"(?i)^(?:professional\s+summary|summary|profile|professional\s+profile|about\s+me|executive\s+summary|career\s+profile|summary\s+of\s+qualifications|background|overview|profile\s+summary|personal\s+profile|professional\s+overview|qualification\s+summary)\b"
        ),
        "objective": re.compile(r"(?i)^(?:career\s+objective|objective|professional\s+objective|target\s+role)\b"),
        "skills": re.compile(
            r"(?i)^(?:technical\s+skills(?:\s*(?:&|and)\s*(?:competencies|technologies|tools|abilities))?|"
            r"skills\s*(?:&|and)\s*(?:technologies|tools)|core\s+competencies|key\s+skills|skills|"
            r"technical\s+competencies|technical\s+expertise|areas\s+of\s+expertise|technical\s+proficiencies|"
            r"technical\s+knowledge|technologies|tech\s+stack|programming\s+languages|tools\s*(?:&|and)\s*technologies|"
            r"hard\s+skills|skills\s+matrix|core\s+skills|it\s+skills|computer\s+skills|software\s+skills|"
            r"technical\s+toolset|competencies|areas\s+of\s+knowledge|technical\s+skillset|technical\s+background)\b"
        ),
        "experience": re.compile(
            r"(?i)^(?:work\s+experience|professional\s+experience|employment\s+history|experience|"
            r"work\s+history|employment|professional\s+background|career\s+history|relevant\s+experience|"
            r"career\s+experience|work\s+background|experience\s+highlights|practical\s+experience|"
            r"industry\s+experience|career\s+background|relevant\s+work\s+experience|cybersecurity\s+experience)\b"
        ),
        "internships": re.compile(r"(?i)^(?:internships|internship\s+experience|internship\s+history|internship|practicum|practical\s+training|industrial\s+training)\b"),
        "education": re.compile(
            r"(?i)^(?:education|academic\s+background|academic\s+qualifications|educational\s+qualifications|"
            r"qualifications|degrees|academic\s+credentials|educational\s+background|academic\s+history|"
            r"education\s*(?:&|and)\s*training|academic\s+record|higher\s+education|educational\s+credentials|academic\s+profile)\b"
        ),
        "certifications": re.compile(
            r"(?i)^(?:certifications|licenses\s*(?:&|and)\s*certifications|professional\s+certifications|"
            r"certificates|licenses|credentials|accreditations|certifications\s*(?:&|and)\s*credentials|"
            r"professional\s+credentials|certificates\s*(?:&|and)\s*licenses|certifications\s*(?:&|and)\s*training|"
            r"training\s*(?:&|and)\s*certifications|industry\s+certifications)\b"
        ),
        "projects": re.compile(
            r"(?i)^(?:projects|"
            r"academic\s+projects|"
            r"personal\s+projects|"
            r"technical\s+projects|"
            r"professional\s+projects|"
            r"major\s+projects|"
            r"mini\s+projects|"
            r"capstone\s+projects?|"
            r"key\s+(?:technical\s+)?projects|"
            r"selected\s+projects|"
            r"notable\s+projects|"
            r"relevant\s+projects|"
            r"recent\s+projects|"
            r"coursework\s+projects?|"
            r"software\s+projects?|"
            r"systems?\s+projects?|"
            r"engineering\s+projects?|"
            r"applied\s+projects?|"
            r"hands[\s-]on\s+projects?|"
            r"practical\s+projects?|"
            r"client\s+projects?|"
            r"industry\s+projects?|"
            r"research\s+projects?|"
            r"project\s+experience|"
            r"project\s+work(?:\s*(?:&|and)\s*implementations?)?|"
            r"project\s+portfolio|"
            r"projects?\s*(?:&|and)\s*(?:experience|implementations?|activities)|"
            r"development\s+projects|"
            r"cybersecurity\s+projects|"
            r"project\s+highlights|"
            r"portfolio)\b"
        ),
        "achievements": re.compile(
            r"(?i)^(?:achievements|honors\s*(?:&|and)\s*awards|key\s+achievements|awards|honors|"
            r"recognitions|accomplishments|awards\s*(?:&|and)\s*honors|key\s+accomplishments|"
            r"extracurricular\s+achievements|extracurricular\s+activities|activities\s*(?:&|and)\s*achievements)\b"
        ),
        "languages": re.compile(
            r"(?i)^(?:languages\s+known|language\s+proficiencies|linguistic\s+skills|languages\s+spoken|language\s+skills|languages)\b"
        ),
        "soft_skills": re.compile(
            r"(?i)^(?:soft\s+skills|interpersonal\s+skills|personal\s+skills|leadership\s+skills|behavioral\s+skills)\b"
        ),
        "publications": re.compile(
            r"(?i)^(?:publications|research\s+papers|papers\s+published|published\s+works|academic\s+publications|conference\s+papers)\b"
        ),
        "coding_profiles": re.compile(r"(?i)^(?:coding\s+profiles?|coding\s+platforms?|competitive\s+programming|coding\s+handles?|online\s+judges?)\b"),
    }

    # Known cybersecurity certification acronyms & names
    CYBER_CERTS = [
        "CEH", "Certified Ethical Hacker", "CISSP", "CompTIA Security+", "Security+",
        "CompTIA Network+", "Network+", "CompTIA CySA+", "CySA+", "CompTIA PenTest+",
        "PenTest+", "CompTIA CASP+", "CASP+", "OSCP", "Offensive Security Certified Professional",
        "OSWE", "OSCE", "OSEP", "OSED", "CRTP", "CRTE", "eJPT", "eCPPT",
        "CISM", "Certified Information Security Manager", "CISA", "Certified Information Systems Auditor",
        "CRISC", "CCSP", "Certified Cloud Security Professional", "GSEC", "GCIH", "GCFA", "GNFA", "GPEN",
        "GXPN", "AWS Certified Security - Specialty", "Microsoft Certified: Security Operations Analyst Associate",
        "SC-200", "AZ-500", "Certified in Cybersecurity", "CC", "SSCP", "ISO 27001 Lead Auditor"
    ]

    DEGREE_PATTERNS = [
        re.compile(r"(?i)\b(bachelor('s)?|b\.?s\.?|b\.?tech\.?|b\.?e\.?|b\.?a\.?|undergraduate)\b(?:\s+in\s+([A-Za-z\s]+))?"),
        re.compile(r"(?i)\b(master('s)?|m\.?s\.?|m\.?tech\.?|m\.?e\.?|m\.?b\.?a\.?|postgraduate)\b(?:\s+in\s+([A-Za-z\s]+))?"),
        re.compile(r"(?i)\b(ph\.?d\.?|doctorate|doctor\s+of\s+philosophy)\b(?:\s+in\s+([A-Za-z\s]+))?"),
        re.compile(r"(?i)\b(associate('s)?|diploma)\b(?:\s+in\s+([A-Za-z\s]+))?"),
    ]

    @classmethod
    def _clean_heading_candidate(cls, line: str) -> str:
        """Cleans and normalizes a candidate heading line."""
        cleaned = line.strip()
        # Strip leading decorative symbols
        cleaned = re.sub(r"^[\s•\*\-\–\—\u2022\u25e6\u2043\u2219\u00b7\u25cf\u25cb\u25aa\u25ab·▪▫◦#=_~|/\\+]+", "", cleaned).strip()
        # Strip leading numbering like 1., 1), I., Section 1:, Part A:
        cleaned = re.sub(r"^(?:(?:section|part|category)\s+[0-9IVX]+|[0-9IVX]+|[A-Z])[\.\)\:\-\s]\s*", "", cleaned, flags=re.I).strip()
        # Strip trailing parenthetical notes (e.g. "Projects (Academic & Personal)" -> "Projects")
        cleaned = re.sub(r"\s*\([^)]*\)\s*$", "", cleaned).strip()
        # Strip enclosing quotes or brackets
        cleaned = re.sub(r"^[\"\'\(\[\{<]+|[\"\'\)\]\}>]+$", "", cleaned).strip()
        # Strip trailing decorative symbols, colons, dashes
        cleaned = re.sub(r"[\s\:\-\–\—\_\=\~\|\/\*#]+$", "", cleaned).strip()
        cleaned = re.sub(r"\s+", " ", cleaned).strip().lower()
        return cleaned

    @classmethod
    def _is_probable_heading(cls, line: str) -> bool:
        """Context-aware heuristic: checks if a line is a section heading rather than body text."""
        stripped = line.strip()
        if not stripped or len(stripped) > 85:
            return False
        if stripped.endswith((".", ";")) and not re.match(r"^[0-9IVX]+\.\s*$", stripped):
            return False
        words = stripped.split()
        if len(words) > 10:
            return False
        if "@" in stripped or "http://" in stripped or "https://" in stripped or "www." in stripped:
            return False

        # Reject inline key-value pairs (e.g., "Technologies: Python, Nmap", "Project URL: ...", "Status: Completed")
        if ":" in stripped:
            parts = stripped.split(":", 1)
            before = parts[0].strip()
            after = parts[1].strip()
            if after:
                # Allowed only if before is a numbering/section prefix e.g. "Section 1: Technical Skills"
                is_numbering_prefix = bool(re.match(r"^(?:(?:section|part|category)\s+[0-9IVX]+|[0-9IVX]+|[A-Z])$", before, flags=re.I))
                if not is_numbering_prefix:
                    return False

        first_word = words[0].lower().rstrip(":,.")
        narrative_starters = {
            "i", "my", "we", "our", "he", "she", "responsible", "assisted",
            "developed", "engineered", "managed", "implemented", "configured",
            "maintained", "designed", "created", "performed", "utilized", "conducted"
        }
        if first_word in narrative_starters and len(words) > 3:
            return False
        return True

    @classmethod
    def _match_heading(cls, line: str) -> Optional[str]:
        """Matches a line against recognized heading aliases and regexes."""
        if not cls._is_probable_heading(line):
            return None

        cleaned = cls._clean_heading_candidate(line)
        if not cleaned:
            return None

        # 1. Exact alias match
        for category, aliases in cls.HEADING_ALIASES.items():
            if cleaned in aliases:
                return category

        # 2. Prefix alias match (e.g. "Core Competencies & Tools" -> "skills")
        for category, aliases in cls.HEADING_ALIASES.items():
            for alias in aliases:
                if cleaned.startswith(alias) and (len(cleaned) == len(alias) or cleaned[len(alias)] in " &-/|"):
                    return category

        # 3. Pattern match
        for section_name, pattern in cls.SECTION_HEADERS.items():
            if pattern.search(cleaned):
                return section_name

        return None

    @classmethod
    def extract(cls, text: str) -> ParsedResumeData:
        """Extracts structured fields from raw document text."""
        if not text or len(text.strip()) < 20:
            raise ResumeExtractionError("The uploaded document contains insufficient text content to perform ATS analysis.")

        sections, detected_headings = cls._segment_sections_with_metadata(text)
        header_sec = sections.get("header", "")
        contact = cls._extract_contact(text, header_text=header_sec)
        name = cls._extract_name(text, contact.email)

        # Objective / Summary
        summary = sections.get("summary")
        objective = sections.get("objective")
        if not summary and objective:
            summary = objective
        if not objective and summary:
            objective = summary

        # Skills (with fallback full text search)
        skills_sec = sections.get("skills", "")
        soft_skills_sec = sections.get("soft_skills", "")
        skills = cls._extract_skills(skills_sec, text, candidate_name=name, contact_info=contact)
        soft_skills = cls._extract_soft_skills(skills_sec, soft_skills_sec)
        skills_method = "direct" if skills_sec else ("fallback_scan" if skills else "none")

        # Certifications (with fallback cyber cert search)
        certs_sec = sections.get("certifications", "")
        certifications = cls._extract_certifications(certs_sec, text)
        certs_method = "direct" if certs_sec else ("fallback_scan" if certifications else "none")

        # Education (with full text fallback)
        edu_sec = sections.get("education", "")
        education = cls._extract_education(edu_sec, text)
        edu_method = "direct" if edu_sec else ("fallback_scan" if education else "none")

        # Experience, Internships & Nested Projects
        exp_sec = sections.get("experience", "")
        internships_sec = sections.get("internships", "")
        employment, internships, nested_projects = cls._extract_experience_with_nested(
            exp_section=exp_sec, intern_section=internships_sec, full_text=text
        )
        exp_method = "direct" if (exp_sec or internships_sec) and (employment or internships) else "none"
        if not employment and not internships and not exp_sec and not internships_sec:
            fallback_exp = cls._extract_experience_fallback(text)
            if fallback_exp:
                employment = [e for e in fallback_exp if "intern" not in e.job_title.lower()]
                internships = [e for e in fallback_exp if "intern" in e.job_title.lower()]
                exp_method = "fallback_scan"

        # Projects (Standalone + Nested)
        proj_sec = sections.get("projects", "")
        standalone_projects = cls._extract_projects(proj_sec) if proj_sec else []
        if not standalone_projects and not nested_projects and not proj_sec:
            standalone_projects = cls._extract_projects_fallback(text)

        all_projects = cls._deduplicate_projects(standalone_projects + nested_projects)
        proj_method = (
            "direct" if (proj_sec and standalone_projects) or nested_projects
            else ("fallback_scan" if all_projects else "none")
        )

        # Achievements
        achievements_sec = sections.get("achievements", "")
        achievements = cls._extract_list_items(achievements_sec)

        # Languages
        lang_sec = sections.get("languages", "")
        languages = cls._extract_languages(lang_sec, text)

        # Publications
        pub_sec = sections.get("publications", "")
        publications = cls._extract_list_items(pub_sec)

        # Build SectionExtractionMetadata
        metadata = {
            "contact_info": SectionMetadata(
                status="extracted" if (contact.email or contact.phone) else "partially_extracted",
                confidence=1.0 if (contact.email and contact.phone) else 0.7,
                item_count=sum(1 for v in [contact.email, contact.phone, contact.linkedin, contact.github, contact.location] if v),
                extraction_method="direct",
            ),
            "summary": SectionMetadata(
                status="extracted" if summary else "not_found",
                confidence=1.0 if summary else 0.0,
                heading_detected=detected_headings.get("summary") or detected_headings.get("objective"),
                item_count=1 if summary else 0,
                extraction_method="direct" if summary else "none",
            ),
            "technical_skills": SectionMetadata(
                status="extracted" if skills_sec and skills else ("fallback_used" if skills else "not_found"),
                confidence=1.0 if skills_sec and skills else (0.85 if skills else 0.0),
                heading_detected=detected_headings.get("skills"),
                item_count=len(skills),
                extraction_method=skills_method,
            ),
            "projects": SectionMetadata(
                status="extracted" if all_projects else "not_found",
                confidence=1.0 if all_projects else 0.0,
                heading_detected=detected_headings.get("projects") or ("Nested in Experience" if nested_projects else None),
                item_count=len(all_projects),
                extraction_method=proj_method,
            ),
            "experience": SectionMetadata(
                status="extracted" if (employment or internships) else "not_found",
                confidence=1.0 if (employment or internships) else 0.0,
                heading_detected=detected_headings.get("experience") or detected_headings.get("internships"),
                item_count=len(employment) + len(internships),
                extraction_method=exp_method,
            ),
            "education": SectionMetadata(
                status="extracted" if edu_sec and education else ("fallback_used" if education else "not_found"),
                confidence=1.0 if edu_sec and education else (0.85 if education else 0.0),
                heading_detected=detected_headings.get("education"),
                item_count=len(education),
                extraction_method=edu_method,
            ),
            "certifications": SectionMetadata(
                status="extracted" if certs_sec and certifications else ("fallback_used" if certifications else "not_found"),
                confidence=1.0 if certs_sec and certifications else (0.85 if certifications else 0.0),
                heading_detected=detected_headings.get("certifications"),
                item_count=len(certifications),
                extraction_method=certs_method,
            ),
            "achievements": SectionMetadata(
                status="extracted" if achievements else "not_found",
                confidence=1.0 if achievements else 0.0,
                heading_detected=detected_headings.get("achievements"),
                item_count=len(achievements),
                extraction_method="direct" if achievements else "none",
            ),
            "languages": SectionMetadata(
                status="extracted" if languages else "not_found",
                confidence=1.0 if languages else 0.0,
                heading_detected=detected_headings.get("languages"),
                item_count=len(languages),
                extraction_method="direct" if languages else "none",
            ),
        }

        parsed_data = ParsedResumeData(
            candidate_name=name,
            contact_info=contact,
            career_objective=objective,
            professional_summary=summary,
            technical_skills=skills,
            soft_skills=soft_skills,
            education=education,
            certifications=certifications,
            structured_certifications=[CertificationEntry(name=c, certification_name=c) for c in certifications],
            projects=all_projects,
            employment_history=employment,
            internships=internships,
            achievements=achievements,
            languages=languages,
            publications=publications,
            raw_sections=sections,
            extraction_metadata=metadata,
        )

        # Multi-Point Verification Engine Audit
        verification_report = ResumeVerificationEngine.verify(
            raw_text=text,
            parsed_resume=parsed_data,
            raw_sections=sections,
        )
        parsed_data.verification_report = verification_report.model_dump()
        return parsed_data

    @classmethod
    def _segment_sections(cls, text: str) -> Dict[str, str]:
        """Segments text into distinct sections based on recognized headings."""
        sections, _ = cls._segment_sections_with_metadata(text)
        return sections

    @classmethod
    def _segment_sections_with_metadata(cls, text: str) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Segments text into distinct sections and records detected heading text."""
        lines = [line.strip() for line in text.split("\n")]
        sections: Dict[str, List[str]] = {}
        detected_headings: Dict[str, str] = {}
        current_section = "header"
        sections[current_section] = []

        for line in lines:
            if not line:
                continue

            matched_header = cls._match_heading(line)

            if matched_header:
                if matched_header == "projects" and "projects" in sections and sections["projects"]:
                    sections["projects"].append("--- NEW_PROJECT_SECTION ---")
                current_section = matched_header
                detected_headings[current_section] = line
                if current_section not in sections:
                    sections[current_section] = []
            else:
                sections[current_section].append(line)

        return {k: "\n".join(v).strip() for k, v in sections.items() if v}, detected_headings

    @classmethod
    def _extract_contact(cls, text: str, header_text: Optional[str] = None) -> ContactInfo:
        """Extracts contact details using regex patterns."""
        email_match = cls.EMAIL_PATTERN.search(text)
        phone_match = cls.PHONE_PATTERN.search(text)
        linkedin_match = cls.LINKEDIN_PATTERN.search(text)
        github_match = cls.GITHUB_PATTERN.search(text)

        # Location heuristic: ONLY inspect genuine header lines before any section headings
        location = None
        source_text = header_text if header_text is not None else text
        header_lines = [l.strip() for l in source_text.split("\n") if l.strip()][:6]
        for line in header_lines:
            # Stop if line looks like a heading or lists technical tools/skills
            if cls._match_heading(line):
                break
            if any(kw in line.lower() for kw in ("python", "java", "tools", "skills", "nmap", "wireshark", "burp", "aws", "docker")):
                continue
            loc_match = re.search(r"\b([A-Z][a-zA-Z\s]+,\s*(?:[A-Z]{2}|USA|India|UK|United States|Canada|Germany|Australia|Singapore|[A-Z][a-z]+))\b", line)
            if loc_match and "@" not in line and "http" not in line:
                cand_loc = loc_match.group(1).strip()
                if not any(kw in cand_loc.lower() for kw in ("python", "java", "tools", "skills", "burp", "sql", "linux", "cloud", "aws")):
                    location = cand_loc
                    break

        return ContactInfo(
            email=email_match.group(0) if email_match else None,
            phone=phone_match.group(0).strip() if phone_match else None,
            linkedin=linkedin_match.group(0) if linkedin_match else None,
            github=github_match.group(0) if github_match else None,
            location=location,
        )

    @classmethod
    def _extract_name(cls, text: str, email: Optional[str]) -> Optional[str]:
        """Infers candidate name from top lines of the resume."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines[:8]:
            clean_line = re.sub(r"^[#*_~=\|\-\s•·]+|[#*_~=\|\-\s•·]+$", "", line).strip()
            if not clean_line:
                continue
            # Skip lines with contact markers
            if "@" in clean_line or "http" in clean_line or re.search(r"\d{3}", clean_line):
                continue
            # Skip lines that match section headings
            if cls._match_heading(clean_line):
                continue
            words = clean_line.split()
            # Typical candidate name is 1-4 words
            if 1 <= len(words) <= 4:
                if any(w.lower() in ("resume", "cv", "curriculum", "vitae", "profile", "summary", "page") for w in words):
                    continue
                if all(w[0].isupper() or w.lower() in ("de", "van", "von", "jr", "sr", "iii", "ii") for w in words if w and w[0].isalpha()):
                    return clean_line

        if email:
            local_part = email.split("@")[0]
            parts = re.split(r"[._-]", local_part)
            clean_parts = [p.capitalize() for p in parts if p.isalpha() and p.lower() not in ("mail", "email", "job", "work", "resume")]
            if clean_parts:
                return " ".join(clean_parts)

        return None

    CATEGORY_PREFIX_PATTERN = re.compile(
        r"^(?:programming\s+languages?|languages?|core\s+competencies?|cybersecurity\s+tools?|security\s+tools?|tools?|"
        r"developer\s+tools?|development\s+tools?|databases?|dbms|tools(?:\s*(?:/|&|and)\s*databases?)?|"
        r"technologies(?:\s*(?:/|&|and)\s*frameworks?)?|cloud(?:\s*(?:&|and)\s*(?:devops|infrastructure))?|cloud\s+computing|"
        r"data\s+science(?:\s*(?:&|and)\s*(?:machine\s+learning|ml))?|machine\s+learning|"
        r"networking(?:\s*(?:technologies|concepts))?|security\s+concepts?|"
        r"frameworks?(?:\s*(?:&|and)\s*libraries?)?|operating\s+systems?|web\s+technologies?|"
        r"version\s+control|computer\s+science\s+fundamentals?|relevant\s+coursework|course\s*work|"
        r"libraries?|methodologies?|platforms?|technical\s+skills?|competencies?|[A-Za-z\s&/]{3,30})\s*[:\-]\s*",
        re.IGNORECASE
    )

    METRIC_OR_NON_SKILL_PATTERN = re.compile(
        r"(?i)\b(?:eda|mae|rmse|mse|r2|r²|r-squared|auc|roc|accuracy|precision|recall|f1[- ]score|"
        r"loss|p-value|confusion\s+matrix|model\s+evaluation|exploratory\s+data\s+analysis|"
        r"mean\s+absolute\s+error|root\s+mean\s+square|leetcode|hackerrank|codechef|geeksforgeeks|"
        r"kaggle|codeforces|coursera|udemy|edx|datacamp|nptel|coding\s+profiles?)\b"
    )

    NON_CERT_PATTERNS = [
        re.compile(r"(?i)\b(?:leetcode|hackerrank|codechef|geeksforgeeks|kaggle|codeforces|github|topcoder|hackerearth|atcoder|coding\s+profiles?)\b"),
    ]

    DATE_RANGE_PATTERN = re.compile(
        r"(?i)\b(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*|\d{1,2})?\s*\d{4}\s*[-–—to]+\s*"
        r"(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*|\d{1,2})?\s*(?:\d{4}|present|current)\b|"
        r"\b\d{1,2}\s+[A-Za-z]+\s+\d{4}\s*[-–—]\s*\d{1,2}\s+[A-Za-z]+\s+\d{4}\b"
    )

    @classmethod
    def _reconstruct_certification_lines(cls, certs_section: str) -> List[str]:
        """Reconstructs certification entries across line wraps, broken hyphens, and missing bullets."""
        if not certs_section:
            return []

        lines = [line.strip() for line in certs_section.split("\n") if line.strip()]
        items: List[str] = []
        current_item = ""

        for line in lines:
            # Stop immediately if section transitions to coding profiles or handles
            if re.match(r"(?i)^(?:coding\s+profiles?|coding\s+platforms?|competitive\s+programming|coding\s+handles?)\b", line):
                break

            bullet_match = re.match(r"^[\s•\*\-\u2022\u25E6\u2043\u2219\u00B7\u25CF\u25CB\u25AA\u25AB·]+|^\(?\d+[.)\]]\s*", line)
            has_bullet = bool(bullet_match)
            cleaned_line = re.sub(r"^[\s•\*\-\u2022\u25E6\u2043\u2219\u00B7\u25CF\u25CB\u25AA\u25AB·]+|^\(?\d+[.)\]]\s*", "", line).strip()
            if not cleaned_line:
                continue

            # Skip standalone section titles
            if cleaned_line.lower() in ("certifications", "licenses & certifications", "credentials", "professional certifications"):
                continue

            is_continuation = False
            if current_item:
                if current_item.endswith("-"):
                    is_continuation = True
                elif not has_bullet:
                    # Check for line-wrapped multi-word certifications like "Young Professional" + "Python"
                    if current_item.lower().endswith("young professional") and cleaned_line.lower().startswith("python"):
                        is_continuation = True
                    # Check for broken word or parenthetical continuations like "tems (DBMS)" or "(AWS-SAA)"
                    elif cleaned_line.lower().startswith(("tems", "tem", "(", "[", "&", "and", "with", "using")) or cleaned_line[0].islower():
                        is_continuation = True
                    elif current_item.endswith(","):
                        is_continuation = True

            if is_continuation:
                if current_item.endswith("-"):
                    # Reconstruct hyphenated split (e.g. "Database Management Sys-" + "tems (DBMS)" -> "Database Management Systems (DBMS)")
                    current_item = current_item[:-1] + cleaned_line
                else:
                    current_item = current_item + " " + cleaned_line
            else:
                if current_item:
                    items.append(current_item)
                current_item = cleaned_line

        if current_item:
            items.append(current_item)

        return items

    @classmethod
    def _extract_skills(
        cls,
        skills_section: str,
        full_text: str,
        candidate_name: Optional[str] = None,
        contact_info: Optional[ContactInfo] = None,
    ) -> List[str]:
        """Extracts technical skills list, stripping category prefixes and strictly filtering out non-skills."""
        skills: Set[str] = set()

        if skills_section:
            # When a dedicated skills section is present, extract and validate tokens from it
            tokens = re.split(r"[,|•\*\n;]\s*", skills_section)
            for token in tokens:
                cleaned = token.strip()
                cleaned = cls.CATEGORY_PREFIX_PATTERN.sub("", cleaned).strip()
                cleaned = re.sub(r"^[(\[\-:\s]+|[)\]\-:\s]+$", "", cleaned).strip()

                if "(" in cleaned:
                    sub_parts = re.split(r"[()]", cleaned)
                    for sp in sub_parts:
                        sp_clean = sp.strip()
                        if is_valid_technical_skill(sp_clean, candidate_name, contact_info):
                            skills.add(normalize_skill_name(sp_clean))
                    continue

                if is_valid_technical_skill(cleaned, candidate_name, contact_info):
                    skills.add(normalize_skill_name(cleaned))
        else:
            # When NO skills section was found, search full_text ONLY for recognized canonical skills
            # (Strictly avoids treating arbitrary full-text sentences, names, or companies as skills)
            for alias, canonical in NORMALIZATION_MAP.items():
                if len(alias) >= 3 or alias in ("c", "r", "go", "c#", "c++", "js", "ts", "sql", "aws", "gcp"):
                    pattern = rf"\b{re.escape(alias)}\b"
                    if re.search(pattern, full_text, re.IGNORECASE):
                        if is_valid_technical_skill(canonical, candidate_name, contact_info):
                            skills.add(canonical)

        return sorted(list(skills))

    @classmethod
    def _extract_certifications(cls, certs_section: str, full_text: str) -> List[str]:
        """Extracts confirmed candidate certifications, reconstructing line wraps and strictly excluding coding profiles."""
        cert_items: List[str] = []

        # 1. Reconstruct and extract specific lines from the certifications section if present
        if certs_section:
            reconstructed = cls._reconstruct_certification_lines(certs_section)
            for item in reconstructed:
                cleaned = item.strip()
                if not cleaned or len(cleaned) >= 100:
                    continue

                # Exclude section titles
                if cleaned.lower() in ("certifications", "licenses & certifications", "credentials", "coding profiles"):
                    continue

                # Exclude coding challenge platforms and coding profile URLs
                if any(p.search(cleaned) for p in cls.NON_CERT_PATTERNS):
                    continue

                if cleaned not in cert_items:
                    cert_items.append(cleaned)

        # 2. Check for known cyber certifications
        if not cert_items:
            # If no dedicated section was identified, search full_text for known cyber certifications
            for cert in cls.CYBER_CERTS:
                pattern = re.compile(rf"\b{re.escape(cert)}\b", re.IGNORECASE)
                if pattern.search(full_text):
                    if cert not in cert_items:
                        cert_items.append(cert)
        else:
            # If section exists, ensure known cyber certifications mentioned are captured
            # without adding redundant acronym duplicates when full certification name is already present
            for cert in cls.CYBER_CERTS:
                pattern = re.compile(rf"\b{re.escape(cert)}\b", re.IGNORECASE)
                if pattern.search(certs_section):
                    already_represented = any(
                        cert.lower() == existing.lower()
                        or f"({cert.lower()})" in existing.lower()
                        or f" {cert.lower()}" in existing.lower()
                        or (len(cert) > 4 and cert.lower() in existing.lower())
                        for existing in cert_items
                    )
                    if not already_represented:
                        cert_items.append(cert)

        return cert_items

    @classmethod
    def _extract_education(cls, edu_section: str, full_text: str) -> List[EducationEntry]:
        """Extracts education records preserving degree, specialization, institution, year, and GPA/CGPA."""
        entries: List[EducationEntry] = []
        source = edu_section if edu_section else full_text

        year_pattern = re.compile(r"\b(19\d{2}|20\d{2})\b")
        cgpa_gpa_pattern = re.compile(
            r"(?i)\b(?:C?GPA|grade|percentage|marks?)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?(?:\s*/\s*[0-9]+)?%?)\b"
        )

        section_institution = cls._infer_institution(source)
        lines = [line.strip() for line in source.split("\n") if line.strip()]
        current_entry: Optional[Dict[str, Any]] = None

        def save_current_edu():
            nonlocal current_entry
            if current_entry and current_entry.get("degree"):
                raw_combined = " \n ".join(current_entry["raw_lines"])
                entries.append(EducationEntry(
                    degree=current_entry["degree"],
                    field_of_study=current_entry.get("field_of_study"),
                    specialization=current_entry.get("specialization"),
                    institution=current_entry.get("institution") or section_institution,
                    graduation_year=current_entry.get("graduation_year"),
                    gpa=current_entry.get("gpa"),
                    cgpa=current_entry.get("cgpa"),
                    percentage=current_entry.get("percentage"),
                    raw_text=raw_combined,
                ))
            current_entry = None

        for line in lines:
            is_new_degree = False
            deg_title = None

            for pattern in cls.DEGREE_PATTERNS:
                m = pattern.search(line)
                if m:
                    is_new_degree = True
                    deg_title = m.group(0).strip()
                    break

            if is_new_degree and deg_title:
                save_current_edu()

                field_of_study = None
                specialization = None

                full_deg_m = re.search(
                    r"\b(Bachelor|Master|Doctor|Associate|B\.?E\.?|B\.?Tech|B\.?S\.?|M\.?S\.?|M\.?Tech)\s+of\s+[A-Za-z\s]+",
                    line,
                    re.IGNORECASE,
                )
                if full_deg_m:
                    deg_title = full_deg_m.group(0).strip()

                for sep in ["—", "–", " - ", " in ", " in: "]:
                    if sep in line:
                        parts = line.split(sep, 1)
                        field_of_study = parts[1].strip()
                        specialization = parts[1].strip()
                        break

                current_entry = {
                    "degree": deg_title,
                    "field_of_study": field_of_study,
                    "specialization": specialization,
                    "institution": cls._infer_institution(line),
                    "graduation_year": None,
                    "gpa": None,
                    "cgpa": None,
                    "percentage": None,
                    "raw_lines": [line],
                }

                cgpa_m = cgpa_gpa_pattern.search(line)
                if cgpa_m:
                    val = cgpa_m.group(1).strip()
                    if "%" in val:
                        current_entry["percentage"] = val
                    else:
                        current_entry["cgpa"] = val
                        current_entry["gpa"] = val.split("/")[0].strip()

                yr_m = year_pattern.search(line)
                if yr_m:
                    current_entry["graduation_year"] = yr_m.group(0)

            elif current_entry:
                current_entry["raw_lines"].append(line)

                cgpa_m = cgpa_gpa_pattern.search(line)
                if cgpa_m and not current_entry["cgpa"]:
                    val = cgpa_m.group(1).strip()
                    if "%" in val:
                        current_entry["percentage"] = val
                    else:
                        current_entry["cgpa"] = val
                        current_entry["gpa"] = val.split("/")[0].strip()

                yr_matches = year_pattern.findall(line)
                if yr_matches and not current_entry["graduation_year"]:
                    current_entry["graduation_year"] = yr_matches[-1]

                if not current_entry["institution"]:
                    line_inst = cls._infer_institution(line)
                    if line_inst:
                        current_entry["institution"] = line_inst
                    else:
                        cleaned_line = cgpa_gpa_pattern.sub("", line)
                        cleaned_line = year_pattern.sub("", cleaned_line).strip(" ·|,–—-")
                        if len(cleaned_line) > 5 and not re.match(
                            r"(?i)^(?:first|second|distinction|grade|cgpa|gpa|class|percentage|cbse|icse)\b",
                            cleaned_line,
                        ):
                            current_entry["institution"] = cleaned_line

        save_current_edu()
        return entries

    @classmethod
    def _infer_institution(cls, text: str) -> Optional[str]:
        inst_pattern = re.compile(
            r"(?i)\b([A-Za-z\s,]+(?:University|College|Institute(?:\s+of\s+[A-Za-z\s]+)?|Polytechnic|Academy|Faculty(?:\s+of\s+[A-Za-z\s]+)?|School|Vidyalaya))\b"
        )
        m = inst_pattern.search(text)
        if m:
            clean_inst = m.group(1).strip()
            clean_inst = re.sub(r"[\d\n]+.*$", "", clean_inst).strip()
            if len(clean_inst) > 3:
                return clean_inst
        return None

    @classmethod
    def _extract_projects(cls, projects_section: str) -> List[ProjectEntry]:
        """Extracts genuine project records and parses technologies, dates, status, and bullets."""
        if not projects_section:
            return []

        projects: List[ProjectEntry] = []
        raw_lines = projects_section.split("\n")

        current_title: Optional[str] = None
        current_status: str = "Completed"
        current_bullets: List[str] = []
        current_techs: List[str] = []
        current_github: Optional[str] = None
        current_url: Optional[str] = None
        current_start: Optional[str] = None
        current_end: Optional[str] = None
        current_outcomes: Optional[str] = None

        def commit_project():
            nonlocal current_title, current_status, current_bullets, current_techs
            nonlocal current_github, current_url, current_start, current_end, current_outcomes
            if not current_title:
                return

            clean_title = current_title.strip()
            # Remove any leading numbers or list prefixes e.g. "1. ", "Project 1: "
            clean_title = re.sub(r"^(?:project\s*\d+|[0-9IVX]+\.)\s*[:\-]?\s*", "", clean_title, flags=re.IGNORECASE).strip()
            clean_title = re.sub(r"^[\d\.\-\*\#\s]+", "", clean_title).strip()
            clean_title = re.sub(r"[\s\|\-\:\_]+$", "", clean_title).strip()

            if not clean_title or len(clean_title) < 3:
                return

            # Skip generic section headers mistakenly captured as titles
            if clean_title.lower() in (
                "projects", "academic projects", "personal projects", "technical projects",
                "key projects", "major projects", "mini projects", "capstone projects",
                "project experience", "software projects", "engineering projects",
                "professional projects", "notable projects", "selected projects"
            ):
                return

            # If description bullets are empty, look for outcomes
            if not current_bullets and current_outcomes:
                current_bullets = [current_outcomes]

            desc_str = " \n".join(current_bullets) if current_bullets else ""

            projects.append(ProjectEntry(
                title=clean_title,
                description=desc_str,
                technologies=list(dict.fromkeys(current_techs)),
                outcomes=current_outcomes,
                status=current_status,
                github_url=current_github,
                project_url=current_url,
                start_date=current_start,
                end_date=current_end,
                bullets=current_bullets,
            ))

            current_title = None
            current_status = "Completed"
            current_bullets = []
            current_techs = []
            current_github = None
            current_url = None
            current_start = None
            current_end = None
            current_outcomes = None

        for raw_line in raw_lines:
            line = raw_line.strip()
            if not line:
                continue

            # Skip section delimiter markers
            if "--- NEW_PROJECT_SECTION ---" in line:
                commit_project()
                continue

            # Check for sub-headings like "Academic Projects:", "Personal Projects:"
            if re.match(r"(?i)^(?:academic|personal|technical|major|mini|key|capstone|professional)\s+projects?\s*[:\-]?$", line):
                commit_project()
                continue

            # 1. Check for dedicated technologies / tools line
            tech_match = re.match(
                r"(?i)^(?:technologies(?:\s+used)?|tech\s+stack|tools(?:\s*(?:&|and)\s*technologies)?|tools\s+used|environment|built\s+with|stack|key\s+technologies)\s*[:\-]\s*(.*)$",
                line
            )
            if tech_match:
                tech_text = tech_match.group(1).strip()
                for t in re.split(r"[,;|/]", tech_text):
                    t_c = re.sub(r"^[(\[\s]+|[)\]\.\s]+$", "", t).strip()
                    if t_c and t_c.lower() not in [x.lower() for x in current_techs]:
                        current_techs.append(t_c)
                continue

            # 2. Check for GitHub / Project URL line
            gh_m = cls.GITHUB_PATTERN.search(line)
            if gh_m:
                gh_url = gh_m.group(0)
                if not current_github:
                    current_github = gh_url
                cleaned = re.sub(r"(?i)^(?:project\s+url|github|repo(?:sitory)?|code|demo|link|website)\s*[:\-]\s*", "", line).strip()
                cleaned = cleaned.replace(gh_url, "").strip()
                if not cleaned or cleaned in ("-", "|", ":", "/", ".", "https://", "http://"):
                    continue
                line = cleaned

            url_m = re.search(r"(?:https?://)?(?:www\.)?[a-zA-Z0-9_\-\.]+\.[a-zA-Z]{2,}(?:/[^\s]*)?", line)
            if url_m and "github" not in url_m.group(0).lower():
                p_url = url_m.group(0)
                if not current_url and not current_github:
                    current_url = p_url
                cleaned = re.sub(r"(?i)^(?:project\s+url|github|repo(?:sitory)?|code|demo|link|website)\s*[:\-]\s*", "", line).strip()
                cleaned = cleaned.replace(p_url, "").strip()
                if not cleaned or cleaned in ("-", "|", ":", "/", ".", "https://", "http://"):
                    continue
                line = cleaned

            if re.match(r"(?i)^(?:project\s+url|github|repo(?:sitory)?|code|demo|link|website)\s*[:\-]", line):
                continue

            # 3. Check for explicit Status line
            status_match = re.match(r"(?i)^status\s*[:\-]\s*(in\s*progress|completed|ongoing|current|finished)\b", line)
            if status_match:
                st = status_match.group(1).strip()
                current_status = "In Progress" if "progress" in st.lower() or "ongoing" in st.lower() or "current" in st.lower() else "Completed"
                continue

            # 4. Check for explicit Outcomes / Results line
            outcome_match = re.match(r"(?i)^(?:outcomes?|results?|achievements?|impact)\s*[:\-]\s*(.*)$", line)
            if outcome_match:
                out_txt = outcome_match.group(1).strip()
                current_outcomes = out_txt
                current_bullets.append(out_txt)
                continue

            # 5. Check if line represents a numbered title vs a bullet item
            is_numbered_title = bool(
                re.match(r"^(?:Project\s*\d+|[0-9IVX]+[\.\)])\s*[:\-]?\s*[A-Z]", line)
                and len(line) < 85
                and not line.endswith(".")
            )
            is_bullet = (
                not is_numbered_title
                and bool(re.match(r"^[\s•\*\-\–\—\u2022]|^(?:\d+\.|\([a-z0-9]+\)|\[\d+\])\s+", line))
            )

            # 6. Check if line represents a project title / header line
            has_pipe_or_paren = "|" in line or ("(" in line and ")" in line and len(line) < 85)
            words = line.split()
            is_clean_short_title = len(words) <= 6 and not line.endswith((".", ";")) and not is_bullet
            starts_with_action_verb = bool(re.match(r"(?i)^(?:developed|engineered|implemented|configured|deployed|built|created|designed|conducted|analyzed|evaluated|integrated|maintained|led|managed|researched)\b", line)) and len(words) > 5

            is_title_candidate = (
                not is_bullet
                and len(line) < 95
                and not re.match(r"(?i)^(?:project\s+url|github|repo|code|demo|link|technologies|tech\s+stack|tools|status|outcomes?|results?)\b", line)
                and (
                    is_numbered_title
                    or has_pipe_or_paren
                    or is_clean_short_title
                    or (not starts_with_action_verb and not line.endswith("."))
                )
            )

            if is_title_candidate:
                commit_project()

                raw_title = line
                # Check for status inside title line
                if re.search(r"(?i)\b(?:in\s*progress|ongoing|current)\b", raw_title):
                    current_status = "In Progress"
                    raw_title = re.sub(r"(?i)\s*[\(\[\-\|]?\s*(?:in\s*progress|ongoing|current)\s*[\)\]\-\|]?", "", raw_title).strip()
                elif re.search(r"(?i)\b(?:completed|finished)\b", raw_title):
                    current_status = "Completed"
                    raw_title = re.sub(r"(?i)\s*[\(\[\-\|]?\s*(?:completed|finished)\s*[\)\]\-\|]?", "", raw_title).strip()

                # Check for dates inside title line
                date_m = cls.DATE_RANGE_PATTERN.search(raw_title)
                if date_m:
                    raw_dates = date_m.group(0)
                    date_parts = re.split(r"[-–—to]+", raw_dates)
                    current_start = date_parts[0].strip() if len(date_parts) > 0 else None
                    current_end = date_parts[1].strip() if len(date_parts) > 1 else None
                    raw_title = raw_title[:date_m.start()] + raw_title[date_m.end():]

                # Check for technologies in pipe or parentheses
                if "|" in raw_title:
                    parts = [p.strip() for p in raw_title.split("|") if p.strip()]
                    raw_title = parts[0]
                    for extra in parts[1:]:
                        for t in re.split(r"[,;/]", extra):
                            t_clean = re.sub(r"^[(\[\s]+|[)\]\.\s]+$", "", t).strip()
                            if t_clean and len(t_clean) < 30 and t_clean.lower() not in [x.lower() for x in current_techs]:
                                current_techs.append(t_clean)

                paren_match = re.search(r"\(([^)]+)\)", raw_title)
                if paren_match:
                    paren_content = paren_match.group(1).strip()
                    if "," in paren_content or any(kw in paren_content.lower() for kw in ("python", "java", "sql", "aws", "docker", "c++", "linux", "react", "fastapi")):
                        for t in re.split(r"[,;/]", paren_content):
                            t_clean = t.strip()
                            if t_clean and t_clean.lower() not in [x.lower() for x in current_techs]:
                                current_techs.append(t_clean)
                        raw_title = raw_title[:paren_match.start()] + raw_title[paren_match.end():]

                current_title = raw_title.strip()
            else:
                cleaned_desc = re.sub(r"^[\s•\*\-\–\—\u2022]+|^(?:\d+\.|\([a-z0-9]+\)|\[\d+\])\s+", "", line).strip()
                if cleaned_desc:
                    if current_bullets and current_bullets[-1].endswith("-"):
                        current_bullets[-1] = current_bullets[-1][:-1] + cleaned_desc
                    else:
                        current_bullets.append(cleaned_desc)

        commit_project()

        # If description is a single large paragraph without bullets, split into clean sentences
        for p in projects:
            if len(p.bullets) == 1 and len(p.bullets[0]) > 90:
                sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])", p.bullets[0]) if s.strip()]
                if len(sentences) > 1:
                    p.bullets = sentences
                    p.description = " \n".join(sentences)

        return cls._deduplicate_projects(projects)

    @classmethod
    def _deduplicate_projects(cls, projects: List[ProjectEntry]) -> List[ProjectEntry]:
        """Deduplicates projects while strictly preserving distinct candidate projects."""
        if len(projects) <= 1:
            return projects

        deduped: List[ProjectEntry] = []
        for p in projects:
            norm_title = re.sub(r"[^a-zA-Z0-9]", "", p.title.lower())

            match_idx = -1
            for idx, existing in enumerate(deduped):
                exist_norm = re.sub(r"[^a-zA-Z0-9]", "", existing.title.lower())
                if norm_title and norm_title == exist_norm:
                    match_idx = idx
                    break
                if p.github_url and existing.github_url and p.github_url.lower() == existing.github_url.lower():
                    match_idx = idx
                    break

            if match_idx >= 0:
                existing = deduped[match_idx]
                for t in p.technologies:
                    if t.lower() not in [x.lower() for x in existing.technologies]:
                        existing.technologies.append(t)
                if len(p.bullets) > len(existing.bullets):
                    existing.bullets = p.bullets
                    existing.description = p.description
                if p.status == "In Progress":
                    existing.status = "In Progress"
                if not existing.github_url and p.github_url:
                    existing.github_url = p.github_url
                if not existing.outcomes and p.outcomes:
                    existing.outcomes = p.outcomes
            else:
                deduped.append(p)

        return deduped

    @classmethod
    def _extract_projects_fallback(cls, full_text: str) -> List[ProjectEntry]:
        """Scans full text for project blocks when no dedicated projects section heading was recognized."""
        if not full_text:
            return []

        lines = [line.strip() for line in full_text.split("\n") if line.strip()]
        proj_blocks: List[str] = []
        current_block: List[str] = []
        collecting = False

        for idx, line in enumerate(lines):
            # Skip contact header lines containing personal github/email
            if idx < 6 and ("@" in line or "linkedin.com" in line or (cls.GITHUB_PATTERN.search(line) and "github.com/in/" not in line)):
                continue

            is_proj_marker = bool(
                re.match(r"(?i)^(?:project\s*\d+|[0-9IVX]+[\.\)])\s*[:\-]?\s*[A-Z]", line)
                or (cls.GITHUB_PATTERN.search(line) and idx >= 6)
                or re.match(r"(?i)^(?:technologies(?:\s+used)?|tech\s+stack|tools\s+used)\s*[:\-]", line)
            )

            if is_proj_marker and not collecting:
                if idx > 0 and not lines[idx - 1].startswith(("-", "•", "*")) and len(lines[idx - 1]) < 80:
                    prev_line = lines[idx - 1]
                    if "@" not in prev_line and "linkedin.com" not in prev_line:
                        current_block.append(prev_line)
                collecting = True

            if collecting:
                current_block.append(line)
                if cls._match_heading(line) and not is_proj_marker:
                    collecting = False
                    if current_block:
                        proj_blocks.append("\n".join(current_block))
                        current_block = []
                elif len(current_block) >= 12:
                    collecting = False
                    proj_blocks.append("\n".join(current_block))
                    current_block = []

        if current_block:
            proj_blocks.append("\n".join(current_block))

        found: List[ProjectEntry] = []
        for block in proj_blocks:
            extracted = cls._extract_projects(block)
            for p in extracted:
                if p.title and not any(p.title.lower() == existing.title.lower() for existing in found):
                    found.append(p)

        return found

    @classmethod
    def _extract_experience_fallback(cls, full_text: str) -> List[ExperienceEntry]:
        """Scans full text for employment blocks when no dedicated experience section heading was recognized."""
        if not full_text:
            return []

        lines = [line.strip() for line in full_text.split("\n") if line.strip()]
        exp_lines: List[str] = []
        collecting = False

        for line in lines:
            if cls.DATE_RANGE_PATTERN.search(line) and any(
                kw in line.lower()
                for kw in ("engineer", "analyst", "developer", "specialist", "intern", "consultant", "administrator", "lead", "manager", "officer")
            ):
                collecting = True

            if collecting:
                if cls._match_heading(line) and not cls.DATE_RANGE_PATTERN.search(line):
                    break
                exp_lines.append(line)
                if len(exp_lines) >= 30:
                    break

        if exp_lines:
            return cls._extract_experience("\n".join(exp_lines))
        return []

    @classmethod
    def _extract_experience_with_nested(
        cls,
        exp_section: str,
        intern_section: str = "",
        full_text: str = "",
    ) -> Tuple[List[ExperienceEntry], List[ExperienceEntry], List[ProjectEntry]]:
        """Extracts employment history, internships, and any nested projects."""
        combined_exp_text = ""
        if exp_section and intern_section:
            combined_exp_text = exp_section + "\n\n" + intern_section
        elif exp_section:
            combined_exp_text = exp_section
        elif intern_section:
            combined_exp_text = intern_section

        if not combined_exp_text:
            return [], [], []

        lines = [line.strip() for line in combined_exp_text.split("\n") if line.strip()]
        all_entries: List[ExperienceEntry] = []
        nested_projects: List[ProjectEntry] = []

        current_title: Optional[str] = None
        current_company: Optional[str] = None
        current_start: Optional[str] = None
        current_end: Optional[str] = None
        current_resp: List[str] = []
        current_nested_proj: Optional[Dict[str, Any]] = None

        def commit_nested_proj():
            nonlocal current_nested_proj
            if current_nested_proj and current_nested_proj.get("title"):
                b_list = current_nested_proj.get("bullets", [])
                nested_projects.append(ProjectEntry(
                    title=current_nested_proj["title"],
                    description=" \n".join(b_list) if b_list else "",
                    bullets=b_list,
                    is_nested=True,
                    parent_context=current_nested_proj.get("parent_context"),
                ))
            current_nested_proj = None

        def save_current_entry():
            nonlocal current_title, current_company, current_start, current_end, current_resp
            commit_nested_proj()
            if current_title:
                all_entries.append(ExperienceEntry(
                    job_title=current_title,
                    company=current_company,
                    start_date=current_start,
                    end_date=current_end,
                    responsibilities=current_resp,
                ))
            current_title = None
            current_company = None
            current_start = None
            current_end = None
            current_resp = []

        for idx, line in enumerate(lines):
            date_m = cls.DATE_RANGE_PATTERN.search(line)
            is_bullet = bool(re.match(r"^[\s•\*\-\–\—\u2022]|^(?:\d+\.|\([a-z0-9]+\)|\[\d+\])\s+", line))

            is_job_title_candidate = (
                not is_bullet
                and len(line) < 90
                and not re.match(r"(?i)^project(?:\s+name)?\s*[:\-]", line)
                and any(kw in line.lower() for kw in (
                    "intern", "engineer", "analyst", "developer", "specialist",
                    "consultant", "manager", "lead", "administrator", "officer",
                    "technician", "director", "associate", "researcher", "assistant"
                ))
            )
            next_is_date = (idx + 1 < len(lines) and bool(cls.DATE_RANGE_PATTERN.search(lines[idx + 1])))

            if (is_job_title_candidate and (next_is_date or date_m or "—" in line or "-" in line or "|" in line or "," in line)) or (date_m and not is_bullet and not current_title):
                save_current_entry()

                title, company, start_date, end_date = line, None, None, None
                if date_m:
                    raw_dates = date_m.group(0)
                    date_parts = re.split(r"\s*[-–—]\s*|\s+to\s+", raw_dates)
                    start_date = date_parts[0].strip() if len(date_parts) > 0 else None
                    end_date = date_parts[1].strip() if len(date_parts) > 1 else "Present"
                    line_no_date = line.replace(raw_dates, "").strip(" |•-–—")
                    if line_no_date:
                        title = line_no_date

                for sep in ["—", "–", "|", " at ", ","]:
                    if sep in title:
                        parts = [p.strip() for p in title.split(sep, 1)]
                        if len(parts) == 2 and len(parts[0]) > 2 and len(parts[1]) > 1:
                            title, company = parts[0], parts[1]
                            break

                current_title = title
                current_company = company
                current_start = start_date
                current_end = end_date
                continue

            if date_m and current_title and not current_start and not is_bullet:
                raw_dates = date_m.group(0)
                date_parts = re.split(r"\s*[-–—]\s*|\s+to\s+", raw_dates)
                current_start = date_parts[0].strip() if len(date_parts) > 0 else None
                current_end = date_parts[1].strip() if len(date_parts) > 1 else "Present"
                continue

            proj_m = re.match(r"(?i)^project(?:\s+name)?\s*[:\-]\s*(.*)$", line)
            if proj_m:
                commit_nested_proj()
                p_title = proj_m.group(1).strip()
                comp_suffix = f" at {current_company}" if current_company else ""
                parent_ctx = f"{current_title or 'Experience'}{comp_suffix}"
                current_nested_proj = {
                    "title": p_title,
                    "parent_context": parent_ctx,
                    "bullets": [],
                }
                continue

            cleaned_bullet = re.sub(r"^[\s•\*\-\–\—\u2022]+", "", line).strip()
            if cleaned_bullet:
                if current_nested_proj:
                    current_nested_proj["bullets"].append(cleaned_bullet)
                if current_title:
                    current_resp.append(cleaned_bullet)

        save_current_entry()

        internships = [e for e in all_entries if "intern" in e.job_title.lower()]
        employment = [e for e in all_entries if "intern" not in e.job_title.lower()]

        if intern_section and not internships:
            intern_raw_entries = cls._extract_experience(intern_section)
            internships.extend(intern_raw_entries)

        return employment, internships, nested_projects

    @classmethod
    def _extract_experience(cls, exp_section: str) -> List[ExperienceEntry]:
        """Extracts employment experiences with robust date, company, and title handling."""
        if not exp_section:
            return []

        entries: List[ExperienceEntry] = []
        lines = [line.strip() for line in exp_section.split("\n") if line.strip()]

        current_title = None
        current_company = None
        current_start = None
        current_end = None
        current_resp: List[str] = []

        def save_current():
            nonlocal current_title, current_company, current_start, current_end, current_resp
            if current_title:
                entries.append(ExperienceEntry(
                    job_title=current_title,
                    company=current_company,
                    start_date=current_start,
                    end_date=current_end,
                    responsibilities=current_resp,
                ))
            current_title = None
            current_company = None
            current_start = None
            current_end = None
            current_resp = []

        idx = 0
        while idx < len(lines):
            line = lines[idx]

            # 1. Check if line contains a date range
            date_m = cls.DATE_RANGE_PATTERN.search(line)
            is_bullet = line.startswith(("-", "•", "*"))

            if not is_bullet and (date_m or (len(line) < 60 and any(kw in line.lower() for kw in ("developer", "engineer", "analyst", "intern", "specialist", "administrator", "consultant")))):
                # Potential new experience block
                if current_title:
                    save_current()

                # Case A: Date range is in this line
                if date_m:
                    raw_dates = date_m.group(0)
                    date_parts = re.split(r"[-–—to]+", raw_dates)
                    current_start = date_parts[0].strip()
                    current_end = date_parts[1].strip() if len(date_parts) > 1 else "Present"

                    # Check what else is on this line or adjacent lines
                    remaining_line = line.replace(raw_dates, "").strip(" |•-–—")
                    if remaining_line and len(remaining_line) > 2:
                        current_title = remaining_line
                    else:
                        # Inspect adjacent line for company or title
                        if idx + 1 < len(lines) and not lines[idx + 1].startswith(("-", "•", "*")):
                            current_company = lines[idx + 1]
                            idx += 1
                        if idx + 1 < len(lines) and not lines[idx + 1].startswith(("-", "•", "*")):
                            current_title = lines[idx + 1]
                            idx += 1
                        if not current_title and current_company:
                            current_title = current_company
                            current_company = None
                else:
                    # Line is job title
                    if "|" in line:
                        parts = [p.strip() for p in line.split("|")]
                        current_title = parts[0]
                        current_company = parts[1] if len(parts) > 1 else None
                    else:
                        current_title = line
                        if idx + 1 < len(lines) and not lines[idx + 1].startswith(("-", "•", "*")):
                            next_line = lines[idx + 1]
                            if not cls.DATE_RANGE_PATTERN.search(next_line):
                                current_company = next_line
                                idx += 1

                idx += 1
                continue

            # Regular responsibility bullet or sentence
            cleaned = re.sub(r"^[\s•\*\-]+", "", line).strip()
            if cleaned:
                # If this line is a continuation of the previous bullet
                if current_resp and (not is_bullet and not cleaned[0].isupper() or current_resp[-1].endswith("-")):
                    if current_resp[-1].endswith("-"):
                        current_resp[-1] = current_resp[-1][:-1] + cleaned
                    else:
                        current_resp[-1] = current_resp[-1] + " " + cleaned
                else:
                    current_resp.append(cleaned)

            idx += 1

        save_current()
        return entries

    @classmethod
    def _extract_languages(cls, lang_section: str, full_text: str) -> List[str]:
        """Extracts candidate languages known."""
        languages: List[str] = []
        source = lang_section if lang_section else ""
        if not source:
            m = re.search(r"(?i)\b(?:languages(?:\s+known)?|linguistic\s+skills)\s*[:\-]\s*(.*)", full_text)
            if m:
                source = m.group(1).split("\n")[0]

        if source:
            tokens = re.split(r"[,|•\*\n;/]", source)
            for token in tokens:
                cleaned = re.sub(r"^[\s•\*\-\–\—\u2022]+|[.:\s]+$", "", token).strip()
                cleaned = re.sub(r"\s*\([^)]*\)", "", cleaned).strip()
                if cleaned and len(cleaned) <= 25 and not re.match(r"(?i)^(?:languages|known|fluent|native|proficient|basic)\b", cleaned):
                    if cleaned not in languages:
                        languages.append(cleaned)

        return languages

    @classmethod
    def _extract_soft_skills(cls, skills_section: str, soft_skills_section: str = "") -> List[str]:
        """Extracts soft / interpersonal skills."""
        soft_skills: List[str] = []
        source = soft_skills_section
        if not source and skills_section:
            m = re.search(r"(?i)\bsoft\s+skills?\s*[:\-]\s*(.*)", skills_section)
            if m:
                source = m.group(1).split("\n")[0]

        if source:
            tokens = re.split(r"[,|•\*\n;/]", source)
            for token in tokens:
                cleaned = re.sub(r"^[\s•\*\-\–\—\u2022]+|[.:\s]+$", "", token).strip()
                if cleaned and len(cleaned) <= 35 and not re.match(r"(?i)^soft\s+skills?\b", cleaned):
                    if cleaned not in soft_skills:
                        soft_skills.append(cleaned)

        return soft_skills

    @classmethod
    def _extract_list_items(cls, section_text: str) -> List[str]:
        if not section_text:
            return []
        items = []
        for line in section_text.split("\n"):
            cleaned = re.sub(r"^[\s•\*\-]+", "", line).strip()
            if cleaned:
                items.append(cleaned)
        return items
