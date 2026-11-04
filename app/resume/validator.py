"""Resume content validation and structural integrity module for FUTRSEC.

Enforces strict separation of sections, prevents artificial project fabrication
from skill confirmations, eliminates duplicate or misplaced category labels,
ensures factual fidelity, and removes invalid placeholders before document rendering.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel, Field

from app.resume.skills_taxonomy import (
    structure_and_classify_skills,
    is_valid_technical_skill,
    classify_skill,
    normalize_skill_name,
)

logger = logging.getLogger("futrsec.validator")


class ResumeValidationError(Exception):
    """Raised when resume content fails fundamental structural or factual validation."""
    pass


class ValidationIssue(BaseModel):
    section: str
    issue_type: str
    message: str
    auto_corrected: bool = False


class ValidationReport(BaseModel):
    is_valid: bool = True
    issues: List[ValidationIssue] = Field(default_factory=list)
    corrections_applied: List[str] = Field(default_factory=list)


class ResumeContentValidator:
    """Validates and cleans structured resume content prior to DOCX and PDF rendering."""

    # Prohibited placeholder strings that must never appear in final documents
    PROHIBITED_PLACEHOLDERS = [
        "accredited institution",
        "organization",
        "host organization",
        "[insert",
        "[company",
        "[project",
        "[technologies",
        "candidate confirmation",
        "practical implementation (candidate confirmation)",
    ]

    # Category prefixes that must never appear as skill entries
    CATEGORY_PREFIXES = [
        r"^(?:programming\s+languages?|languages?)\s*[:\-]\s*",
        r"^(?:databases?|dbms|tools(?:\s*(?:/|&|and)\s*databases?)?)\s*[:\-]\s*",
        r"^(?:cloud(?:\s*(?:&|and)\s*infrastructure)?|cloud\s+computing)\s*[:\-]\s*",
        r"^(?:frameworks?(?:\s*(?:&|and)\s*libraries?)?|libraries?|technologies(?:\s*(?:/|&|and)\s*frameworks?)?)\s*[:\-]\s*",
        r"^(?:security\s+tools?|tools?|developer\s+tools?|development\s+tools?|tools(?:\s*(?:/|&|and)\s*(?:technologies?|platforms?|databases?))?)\s*[:\-]\s*",
        r"^(?:operating\s+systems?|os)\s*[:\-]\s*",
        r"^(?:core\s+competencies?|technical\s+skills?|key\s+skills?|competencies?)\s*[:\-]\s*",
        r"^(?:web\s+technologies?|web\s+development|networking)\s*[:\-]\s*",
        r"^(?:version\s+control)\s*[:\-]\s*",
        r"^(?:computer\s+science\s+fundamentals?)\s*[:\-]\s*",
        r"^(?:relevant\s+coursework|course\s*work)\s*[:\-]\s*",
    ]

    # Platforms and non-certification profiles that must never be classified as earned industry certifications
    NON_CERTIFICATION_PATTERNS = [
        r"(?i)\b(?:leetcode|hackerrank|codechef|geeksforgeeks|kaggle|codeforces|github|topcoder|hackerearth|atcoder|coding\s+profiles?)\b",
    ]

    @classmethod
    def validate_and_sanitize(cls, content: Any) -> Tuple[Any, ValidationReport]:
        """Validates all sections of an EnhancedResumeContent object and applies deterministic sanitization.

        Returns (sanitized_content, report).
        Raises ResumeValidationError if fatal unrecoverable issues are found.
        """
        report = ValidationReport()

        if not content:
            raise ResumeValidationError("Resume content object is null or empty.")

        # 1. Candidate Name & Contact Validation
        cls._validate_contact_info(content, report)

        # 2. Professional Summary Validation & Sanitization
        cls._validate_and_sanitize_summary(content, report)

        # 3. Technical Skills Validation & Sanitization
        cls._validate_and_sanitize_skills(content, report)

        # 4. Projects Validation & Separation (Strictly No Skill Confirmation Projects)
        cls._validate_and_sanitize_projects(content, report)

        # 5. Work Experience Validation
        cls._validate_and_sanitize_experience(content, report)

        # 6. Education Validation
        cls._validate_and_sanitize_education(content, report)

        # 7. Certifications Validation
        cls._validate_and_sanitize_certifications(content, report)

        # 8. Check for any remaining prohibited placeholders across all text fields
        cls._check_placeholders(content, report)

        return content, report

    @classmethod
    def _validate_contact_info(cls, content: Any, report: ValidationReport) -> None:
        name = getattr(content, "candidate_name", "").strip()
        if not name or len(name) < 2:
            report.issues.append(ValidationIssue(
                section="contact_info",
                issue_type="missing_name",
                message="Candidate name is missing or invalid.",
                auto_corrected=False,
            ))
            setattr(content, "candidate_name", "Cybersecurity Candidate")
            report.corrections_applied.append("Set default candidate name 'Cybersecurity Candidate'")

    @classmethod
    def _validate_and_sanitize_summary(cls, content: Any, report: ValidationReport) -> None:
        summary = getattr(content, "professional_summary", "") or ""
        if not summary:
            return

        original_summary = summary
        has_raw_labels = False

        # Strip model evaluation metrics and statistics if accidentally leaked into summary
        metric_pattern = re.compile(
            r"(?i)\b(?:eda|mae|rmse|mse|r2|r²|r-squared|auc|roc|accuracy|loss|p-value|confusion\s+matrix|exploratory\s+data\s+analysis)\b[,;\s]*"
        )
        if metric_pattern.search(summary):
            summary = metric_pattern.sub("", summary)
            has_raw_labels = True

        # Check for raw category prefixes leaked into summary
        for pref in cls.CATEGORY_PREFIXES:
            if re.search(pref, summary, re.IGNORECASE):
                has_raw_labels = True
                summary = re.sub(pref, "", summary, flags=re.IGNORECASE)

        # Clean unclosed parentheses or malformed comma sequences
        if "(" in summary and ")" not in summary:
            has_raw_labels = True
            # Strip dangling unclosed parenthesis
            summary = re.sub(r"\([^)]*$", "", summary)

        # Remove double spaces or awkward punctuation left over
        summary = re.sub(r"\s+,", ",", summary)
        summary = re.sub(r",\s*,+", ",", summary)
        summary = re.sub(r"\s{2,}", " ", summary).strip()

        if has_raw_labels or summary != original_summary:
            setattr(content, "professional_summary", summary)
            report.issues.append(ValidationIssue(
                section="summary",
                issue_type="raw_labels_in_summary",
                message="Removed raw technology category labels, evaluation metrics, or unclosed syntax from professional summary.",
                auto_corrected=True,
            ))
            report.corrections_applied.append("Cleaned raw technology labels and syntax from professional summary")

    @classmethod
    def _validate_and_sanitize_skills(cls, content: Any, report: ValidationReport) -> None:
        raw_grouped = getattr(content, "technical_skills_grouped", {}) or {}
        candidate_name = getattr(content, "candidate_name", None)
        contact_info = getattr(content, "contact_details", None)
        headline = getattr(content, "professional_headline", "") or ""

        # Gather all raw skills across groups
        all_raw_skills: List[str] = []
        foundational_items: List[str] = []

        for group_name, skills_list in raw_grouped.items():
            if "Foundational Knowledge" in group_name:
                foundational_items.extend(skills_list if isinstance(skills_list, list) else [str(skills_list)])
                continue
            if isinstance(skills_list, list):
                all_raw_skills.extend(skills_list)
            elif isinstance(skills_list, str):
                all_raw_skills.extend(re.split(r"[,;\n]", skills_list))

        cleaned_grouped = structure_and_classify_skills(
            raw_skills=all_raw_skills,
            candidate_name=candidate_name,
            contact_info=contact_info,
            target_role_name=headline,
        )

        if foundational_items:
            cleaned_grouped["Foundational Knowledge & Coursework Exposure"] = foundational_items

        setattr(content, "technical_skills_grouped", cleaned_grouped)
        report.corrections_applied.append(f"Sanitized and categorized technical skills into {len(cleaned_grouped)} clean categories")

    @classmethod
    def _categorize_skill(cls, skill: str, original_group: str = "") -> str:
        cat = classify_skill(skill)
        return cat or "Cybersecurity Tools"

    @classmethod
    def _validate_and_sanitize_projects(cls, content: Any, report: ValidationReport) -> None:
        """CRITICAL: Ensures skill confirmations are NEVER converted into project entries."""
        projects = getattr(content, "projects", []) or []
        sanitized_projects: List[Dict[str, Any]] = []

        for p in projects:
            title = p.get("title", "").strip()

            # Rule: Skill confirmations must NEVER become project entries
            if re.search(r"(?:candidate\s+confirmation|practical\s+implementation\s*\()", title, re.IGNORECASE):
                report.issues.append(ValidationIssue(
                    section="projects",
                    issue_type="skill_confirmation_as_project",
                    message=f"Removed artificial project created from skill confirmation: '{title}'",
                    auto_corrected=True,
                ))
                report.corrections_applied.append(f"Excluded artificial skill confirmation project '{title}'")
                continue

            # Must have a real title
            if not title or len(title) < 3 or title.lower() in ("project", "technical project", "key technical projects"):
                report.issues.append(ValidationIssue(
                    section="projects",
                    issue_type="invalid_project_title",
                    message=f"Skipped project with empty or generic placeholder title '{title}'",
                    auto_corrected=True,
                ))
                continue

            # Clean technologies list
            raw_techs = p.get("technologies", [])
            cleaned_techs = []
            if isinstance(raw_techs, list):
                for t in raw_techs:
                    t_str = str(t).strip()
                    for pref in cls.CATEGORY_PREFIXES:
                        t_str = re.sub(pref, "", t_str, flags=re.IGNORECASE).strip()
                    t_str = re.sub(r"^[(\[\-:\s]+|[)\]\-:\s]+$", "", t_str).strip()
                    if t_str and t_str not in cleaned_techs:
                        cleaned_techs.append(t_str)

            p["technologies"] = cleaned_techs

            # Clean description
            desc = p.get("description", "").strip()
            # De-hyphenate words in description
            desc = re.sub(r"(\b[A-Za-z]+)-\s*\n\s*([a-z]+)", r"\1\2", desc)
            p["description"] = desc

            sanitized_projects.append(p)

        setattr(content, "projects", sanitized_projects)

    @classmethod
    def _validate_and_sanitize_experience(cls, content: Any, report: ValidationReport) -> None:
        experience = getattr(content, "experience", []) or []
        for exp in experience:
            # Check company placeholder
            comp = exp.get("company", "")
            if comp and comp.strip().lower() in ("organization", "host organization", "[organization]"):
                exp["company"] = None
                report.corrections_applied.append("Removed placeholder 'Organization' from experience entry")

            # Check job title
            title = exp.get("job_title", "").strip()
            # If job title looks like a pure date range (e.g. "15 May 2025 - 25 April 2026")
            if re.match(r"^\d{1,2}\s+[A-Za-z]+\s+\d{4}\s*[-–—]\s*\d{1,2}\s+[A-Za-z]+\s+\d{4}$", title):
                # Swap date and look for title in responsibilities
                dates = title.split("-") if "-" in title else title.split("–")
                exp["start_date"] = dates[0].strip()
                exp["end_date"] = dates[1].strip() if len(dates) > 1 else "Present"

                # Check if first responsibility is actually the company or job title
                resps = exp.get("responsibilities", [])
                if len(resps) >= 2:
                    possible_comp = resps[0].rstrip(".")
                    possible_title = resps[1].rstrip(".")
                    if len(possible_comp.split()) <= 4 and len(possible_title.split()) <= 4:
                        exp["company"] = possible_comp
                        exp["job_title"] = possible_title
                        exp["responsibilities"] = resps[2:]
                        report.corrections_applied.append(f"Corrected misparsed job title '{possible_title}' and company '{possible_comp}'")
                elif resps:
                    exp["job_title"] = resps[0].rstrip(".")
                    exp["responsibilities"] = resps[1:]

            # Clean broken hyphens in responsibilities
            clean_resps = []
            for r in exp.get("responsibilities", []):
                # Dehyphenate broken words like "Lan-. Guage Model" or "authenti- cation"
                r_clean = re.sub(r"(\b[A-Za-z]+)-\s*\.?\s*([a-z]+)", r"\1\2", r)
                # Remove orphan bullet fragments
                if len(r_clean.strip()) > 3:
                    clean_resps.append(r_clean.strip())
            exp["responsibilities"] = clean_resps

    @classmethod
    def _validate_and_sanitize_education(cls, content: Any, report: ValidationReport) -> None:
        education = getattr(content, "education", []) or []
        for edu in education:
            inst = edu.get("institution", "")
            if inst and inst.strip().lower() in ("accredited institution", "[accredited institution]", "institution"):
                edu["institution"] = None
                report.corrections_applied.append("Removed placeholder 'Accredited Institution' from education entry")

            deg = edu.get("degree", "").strip()
            # If degree is just "Bachelor", try to preserve field of study if present in raw_text
            if deg.lower() == "bachelor" and edu.get("raw_text"):
                raw = edu.get("raw_text")
                m = re.search(r"\b(Bachelor\s+of\s+[A-Za-z\s]+)\b", raw, re.IGNORECASE)
                if m:
                    edu["degree"] = m.group(1).strip()
                    report.corrections_applied.append(f"Restored full degree name '{edu['degree']}'")

    @classmethod
    def _validate_and_sanitize_certifications(cls, content: Any, report: ValidationReport) -> None:
        certs = getattr(content, "certifications", []) or []
        clean_certs = []
        clean_structured = []

        for c in certs:
            if not c:
                continue
            if isinstance(c, str):
                c_str = c.strip()
            elif isinstance(c, dict):
                c_str = (c.get("certification_name") or c.get("name") or "").strip()
            elif hasattr(c, "certification_name") and c.certification_name:
                c_str = c.certification_name.strip()
            elif hasattr(c, "name") and c.name:
                c_str = c.name.strip()
            else:
                c_str = str(c).strip()

            if not c_str:
                continue

            # Rule: Coding platforms and coding profiles must NOT be in certifications
            is_non_cert = False
            for pat in cls.NON_CERTIFICATION_PATTERNS:
                if re.search(pat, c_str):
                    is_non_cert = True
                    break

            if is_non_cert:
                report.issues.append(ValidationIssue(
                    section="certifications",
                    issue_type="course_or_platform_as_certification",
                    message=f"Excluded non-certification item '{c_str}' from earned credentials",
                    auto_corrected=True,
                ))
                report.corrections_applied.append(f"Excluded '{c_str}' from certifications")
                continue

            # Strip section header text if captured as certification
            if c_str.lower() in ("certifications", "licenses & certifications", "credentials", "coding profiles"):
                continue

            if c_str not in clean_certs:
                clean_certs.append(c_str)
                from app.resume.extractor import CertificationEntry
                if isinstance(c, CertificationEntry):
                    clean_structured.append(c)
                elif isinstance(c, dict):
                    clean_structured.append(CertificationEntry(**c))
                else:
                    clean_structured.append(CertificationEntry(name=c_str, certification_name=c_str))

        setattr(content, "certifications", clean_certs)
        if hasattr(content, "structured_certifications"):
            setattr(content, "structured_certifications", clean_structured)

    @classmethod
    def _check_placeholders(cls, content: Any, report: ValidationReport) -> None:
        """Deep inspection for prohibited literal placeholder strings."""
        summary = getattr(content, "professional_summary", "")
        for ph in cls.PROHIBITED_PLACEHOLDERS:
            if ph in summary.lower():
                report.issues.append(ValidationIssue(
                    section="summary",
                    issue_type="prohibited_placeholder",
                    message=f"Found prohibited placeholder '{ph}' in professional summary.",
                    auto_corrected=False,
                ))
