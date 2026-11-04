"""Resume Extraction Verification Engine for FUTRSEC.

Performs deterministic multi-point verification on extracted resume sections.
Determines whether each section was successfully extracted, partially extracted,
failed extraction despite being present, or genuinely absent from the candidate's document.
Never fabricates missing data and generates actionable validation warnings.
"""

import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class SectionVerificationResult(BaseModel):
    """Detailed verification audit for an individual resume section."""
    section_name: str
    status: str  # "extracted" | "partially_extracted" | "extraction_failed" | "genuinely_absent"
    detected_in_raw_text: bool = False
    heading_found: Optional[str] = None
    item_count: int = 0
    confidence: float = 0.0  # 0.0 to 1.0
    sample_snippet: Optional[str] = None
    validation_warnings: List[str] = Field(default_factory=list)


class CandidateVerificationReport(BaseModel):
    """Comprehensive resume extraction verification report."""
    overall_quality_score: float = 0.0  # 0 to 100
    is_extraction_reliable: bool = True
    sections: Dict[str, SectionVerificationResult] = Field(default_factory=dict)
    critical_warnings: List[str] = Field(default_factory=list)
    extraction_notes: List[str] = Field(default_factory=list)


class ResumeVerificationEngine:
    """Deterministic verification engine for candidate resume extraction."""

    # Keywords that suggest a section is present even if standard heading formatting varies
    SECTION_SIGNATURES: Dict[str, List[re.Pattern]] = {
        "summary": [
            re.compile(r"(?i)\b(?:professional\s+summary|career\s+objective|about\s+me|profile\s+summary|executive\s+summary)\b"),
        ],
        "skills": [
            re.compile(r"(?i)\b(?:technical\s+skills|core\s+competencies|key\s+skills|skills\s*(?:&|and)\s*tools|technologies|programming\s+languages)\b"),
        ],
        "experience": [
            re.compile(r"(?i)\b(?:work\s+experience|professional\s+experience|employment\s+history|career\s+history)\b"),
        ],
        "internships": [
            re.compile(r"(?i)\b(?:internships?|internship\s+experience|industrial\s+training|practicum)\b"),
        ],
        "projects": [
            re.compile(r"(?i)\b(?:academic\s+projects|personal\s+projects|key\s+projects|technical\s+projects|project\s+experience)\b"),
            re.compile(r"(?i)\bproject\s*[:\-]\s*[A-Z]"),
        ],
        "education": [
            re.compile(r"(?i)\b(?:education|academic\s+background|academic\s+qualifications|educational\s+background)\b"),
            re.compile(r"(?i)\b(?:bachelor|b\.?tech|b\.?e\.|master|m\.?tech|ph\.?d)\b"),
        ],
        "certifications": [
            re.compile(r"(?i)\b(?:certifications?|licenses\s*(?:&|and)\s*certifications|professional\s+credentials|certificates)\b"),
        ],
        "achievements": [
            re.compile(r"(?i)\b(?:achievements?|honors\s*(?:&|and)\s*awards|awards|hackathons?|ctf\b)\b"),
        ],
        "languages": [
            re.compile(r"(?i)\b(?:languages?|languages\s+known|linguistic\s+skills|language\s+proficiencies)\b"),
        ],
        "soft_skills": [
            re.compile(r"(?i)\b(?:soft\s+skills|interpersonal\s+skills|personal\s+skills)\b"),
        ],
        "publications": [
            re.compile(r"(?i)\b(?:publications?|research\s+papers?|published\s+works?)\b"),
        ],
    }

    @classmethod
    def verify(
        cls,
        raw_text: str,
        parsed_resume: Any,
        raw_sections: Optional[Dict[str, str]] = None,
    ) -> CandidateVerificationReport:
        """Audits extracted resume fields against raw document content."""
        sections_report: Dict[str, SectionVerificationResult] = {}
        critical_warnings: List[str] = []
        notes: List[str] = []
        raw_sections = raw_sections or {}

        # 1. Contact Info Verification
        contact = getattr(parsed_resume, "contact_info", None)
        contact_items = 0
        contact_warnings = []
        if contact:
            if contact.email:
                contact_items += 1
            else:
                contact_warnings.append("No email address detected.")
            if contact.phone:
                contact_items += 1
            else:
                contact_warnings.append("No phone number detected.")
            if contact.linkedin:
                contact_items += 1
            if contact.github:
                contact_items += 1

        contact_status = (
            "extracted" if contact_items >= 3
            else ("partially_extracted" if contact_items >= 1 else "extraction_failed")
        )
        contact_conf = 1.0 if contact_items >= 3 else (0.70 if contact_items >= 1 else 0.20)
        sections_report["contact_info"] = SectionVerificationResult(
            section_name="contact_info",
            status=contact_status,
            detected_in_raw_text=True,
            item_count=contact_items,
            confidence=contact_conf,
            validation_warnings=contact_warnings,
        )

        # 2. Summary / Objective
        summary = getattr(parsed_resume, "professional_summary", None) or getattr(parsed_resume, "career_objective", None)
        summary_raw = raw_sections.get("summary") or raw_sections.get("objective") or ""
        sum_detected = bool(summary_raw.strip()) or any(p.search(raw_text) for p in cls.SECTION_SIGNATURES["summary"])
        if summary and len(summary.strip()) >= 50:
            sum_status = "extracted"
            sum_conf = 1.0
            sum_warn = []
        elif summary:
            sum_status = "partially_extracted"
            sum_conf = 0.70
            sum_warn = ["Professional summary is very brief (less than 50 characters)."]
        elif sum_detected:
            sum_status = "extraction_failed"
            sum_conf = 0.30
            sum_warn = ["Summary/Objective section heading was detected but no body text was extracted."]
            critical_warnings.append("Professional Summary heading detected but content could not be extracted.")
        else:
            sum_status = "genuinely_absent"
            sum_conf = 1.0
            sum_warn = []

        sections_report["summary"] = SectionVerificationResult(
            section_name="summary",
            status=sum_status,
            detected_in_raw_text=sum_detected,
            heading_found="Summary / Objective" if sum_detected else None,
            item_count=1 if summary else 0,
            confidence=sum_conf,
            sample_snippet=summary[:120] if summary else None,
            validation_warnings=sum_warn,
        )

        # 3. Technical Skills
        skills = getattr(parsed_resume, "technical_skills", [])
        skills_raw = raw_sections.get("skills", "")
        skills_detected = bool(skills_raw.strip()) or any(p.search(raw_text) for p in cls.SECTION_SIGNATURES["skills"])
        if len(skills) >= 5:
            sk_status = "extracted"
            sk_conf = 1.0
            sk_warn = []
        elif len(skills) > 0:
            sk_status = "partially_extracted"
            sk_conf = 0.75
            sk_warn = [f"Only {len(skills)} technical skills identified."]
        elif skills_detected:
            sk_status = "extraction_failed"
            sk_conf = 0.20
            sk_warn = ["Skills heading was detected in text, but 0 technical skills were parsed."]
            critical_warnings.append("Skills section detected in resume but 0 technical skills were extracted.")
        else:
            sk_status = "genuinely_absent"
            sk_conf = 1.0
            sk_warn = ["No technical skills section found in resume."]

        sections_report["technical_skills"] = SectionVerificationResult(
            section_name="technical_skills",
            status=sk_status,
            detected_in_raw_text=skills_detected,
            heading_found="Skills" if skills_detected else None,
            item_count=len(skills),
            confidence=sk_conf,
            sample_snippet=", ".join(skills[:8]) if skills else None,
            validation_warnings=sk_warn,
        )

        # 4. Projects (Including standalone & nested projects)
        projects = getattr(parsed_resume, "projects", [])
        proj_raw = raw_sections.get("projects", "")
        proj_detected = bool(proj_raw.strip()) or any(p.search(raw_text) for p in cls.SECTION_SIGNATURES["projects"])
        if len(projects) >= 2:
            pr_status = "extracted"
            pr_conf = 1.0
            pr_warn = []
        elif len(projects) == 1:
            pr_status = "extracted"
            pr_conf = 0.85
            pr_warn = ["Only 1 project extracted. Candidate may have additional projects."]
        elif proj_detected:
            pr_status = "extraction_failed"
            pr_conf = 0.25
            pr_warn = ["Project section heading was detected but no project entries were successfully extracted."]
            critical_warnings.append("Projects detected in resume text but 0 project entries were parsed.")
        else:
            pr_status = "genuinely_absent"
            pr_conf = 1.0
            pr_warn = []

        sections_report["projects"] = SectionVerificationResult(
            section_name="projects",
            status=pr_status,
            detected_in_raw_text=proj_detected,
            heading_found="Projects" if proj_detected else None,
            item_count=len(projects),
            confidence=pr_conf,
            sample_snippet="; ".join(p.title for p in projects[:3]) if projects else None,
            validation_warnings=pr_warn,
        )

        # 5. Experience & Internships
        exp_entries = getattr(parsed_resume, "employment_history", [])
        intern_entries = getattr(parsed_resume, "internships", [])
        total_work = len(exp_entries) + len(intern_entries)
        exp_raw = raw_sections.get("experience", "") or raw_sections.get("internships", "")
        exp_detected = bool(exp_raw.strip()) or any(p.search(raw_text) for p in cls.SECTION_SIGNATURES["experience"] + cls.SECTION_SIGNATURES["internships"])

        if total_work >= 1:
            exp_status = "extracted"
            exp_conf = 1.0
            exp_warn = []
            # Check for missing dates in any entry
            missing_dates = [e.job_title for e in (exp_entries + intern_entries) if not e.start_date]
            if missing_dates:
                exp_warn.append(f"Dates missing for: {', '.join(missing_dates[:2])}")
        elif exp_detected:
            exp_status = "extraction_failed"
            exp_conf = 0.25
            exp_warn = ["Experience heading detected, but 0 employment or internship entries were parsed."]
            critical_warnings.append("Experience section detected in resume but no employment entries could be parsed.")
        else:
            exp_status = "genuinely_absent"
            exp_conf = 1.0
            exp_warn = []

        sections_report["experience"] = SectionVerificationResult(
            section_name="experience",
            status=exp_status,
            detected_in_raw_text=exp_detected,
            heading_found="Experience" if exp_detected else None,
            item_count=total_work,
            confidence=exp_conf,
            sample_snippet="; ".join(f"{e.job_title} ({e.company})" for e in (exp_entries + intern_entries)[:3]) if total_work else None,
            validation_warnings=exp_warn,
        )

        # 6. Education
        education = getattr(parsed_resume, "education", [])
        edu_raw = raw_sections.get("education", "")
        edu_detected = bool(edu_raw.strip()) or any(p.search(raw_text) for p in cls.SECTION_SIGNATURES["education"])
        if len(education) >= 1:
            ed_status = "extracted"
            ed_conf = 1.0
            ed_warn = []
            # Check if any entry has GPA / CGPA
            has_gpa = any(getattr(e, "gpa", None) or getattr(e, "cgpa", None) for e in education)
            if not has_gpa:
                ed_warn.append("No GPA or CGPA extracted from education entries.")
            if not any(e.institution for e in education):
                ed_status = "partially_extracted"
                ed_conf = 0.75
                ed_warn.append("Educational institution name could not be fully identified.")
        elif edu_detected:
            ed_status = "extraction_failed"
            ed_conf = 0.20
            ed_warn = ["Education heading detected, but no degree entries were parsed."]
            critical_warnings.append("Education section detected in resume but 0 degrees were parsed.")
        else:
            ed_status = "genuinely_absent"
            ed_conf = 1.0
            ed_warn = ["No education section found in resume."]

        sections_report["education"] = SectionVerificationResult(
            section_name="education",
            status=ed_status,
            detected_in_raw_text=edu_detected,
            heading_found="Education" if edu_detected else None,
            item_count=len(education),
            confidence=ed_conf,
            sample_snippet="; ".join(f"{e.degree} ({e.institution or 'N/A'})" for e in education[:2]) if education else None,
            validation_warnings=ed_warn,
        )

        # 7. Certifications
        certs = getattr(parsed_resume, "certifications", [])
        cert_raw = raw_sections.get("certifications", "")
        cert_detected = bool(cert_raw.strip()) or any(p.search(raw_text) for p in cls.SECTION_SIGNATURES["certifications"])
        if len(certs) >= 1:
            cr_status = "extracted"
            cr_conf = 1.0
            cr_warn = []
        elif cert_detected:
            cr_status = "extraction_failed"
            cr_conf = 0.30
            cr_warn = ["Certifications heading detected, but no certifications were extracted."]
            critical_warnings.append("Certifications section detected in resume but 0 certifications were parsed.")
        else:
            cr_status = "genuinely_absent"
            cr_conf = 1.0
            cr_warn = []

        sections_report["certifications"] = SectionVerificationResult(
            section_name="certifications",
            status=cr_status,
            detected_in_raw_text=cert_detected,
            heading_found="Certifications" if cert_detected else None,
            item_count=len(certs),
            confidence=cr_conf,
            sample_snippet="; ".join(certs[:4]) if certs else None,
            validation_warnings=cr_warn,
        )

        # 8. Achievements
        achievements = getattr(parsed_resume, "achievements", [])
        ach_raw = raw_sections.get("achievements", "")
        ach_detected = bool(ach_raw.strip()) or any(p.search(raw_text) for p in cls.SECTION_SIGNATURES["achievements"])
        if len(achievements) >= 1:
            ac_status = "extracted"
            ac_conf = 1.0
            ac_warn = []
        elif ach_detected:
            ac_status = "extraction_failed"
            ac_conf = 0.35
            ac_warn = ["Achievements heading detected, but items could not be parsed."]
        else:
            ac_status = "genuinely_absent"
            ac_conf = 1.0
            ac_warn = []

        sections_report["achievements"] = SectionVerificationResult(
            section_name="achievements",
            status=ac_status,
            detected_in_raw_text=ach_detected,
            heading_found="Achievements" if ach_detected else None,
            item_count=len(achievements),
            confidence=ac_conf,
            sample_snippet="; ".join(achievements[:2]) if achievements else None,
            validation_warnings=ac_warn,
        )

        # 9. Languages
        languages = getattr(parsed_resume, "languages", [])
        lang_raw = raw_sections.get("languages", "")
        lang_detected = bool(lang_raw.strip()) or any(p.search(raw_text) for p in cls.SECTION_SIGNATURES["languages"])
        if len(languages) >= 1:
            lg_status = "extracted"
            lg_conf = 1.0
            lg_warn = []
        elif lang_detected:
            lg_status = "extraction_failed"
            lg_conf = 0.35
            lg_warn = ["Languages heading detected, but no language items parsed."]
        else:
            lg_status = "genuinely_absent"
            lg_conf = 1.0
            lg_warn = []

        sections_report["languages"] = SectionVerificationResult(
            section_name="languages",
            status=lg_status,
            detected_in_raw_text=lang_detected,
            heading_found="Languages" if lang_detected else None,
            item_count=len(languages),
            confidence=lg_conf,
            sample_snippet=", ".join(languages[:4]) if languages else None,
            validation_warnings=lg_warn,
        )

        # Calculate Overall Quality Score
        # Weights for core sections: Skills (25), Projects (25), Experience (20), Education (15), Summary (10), Contact (5)
        core_weights = {
            "technical_skills": 25.0,
            "projects": 25.0,
            "experience": 20.0,
            "education": 15.0,
            "summary": 10.0,
            "contact_info": 5.0,
        }

        weighted_score = 0.0
        total_possible = 0.0
        for sec_name, weight in core_weights.items():
            res = sections_report.get(sec_name)
            if not res:
                continue
            total_possible += weight
            if res.status == "extracted":
                weighted_score += weight * res.confidence
            elif res.status == "partially_extracted":
                weighted_score += weight * 0.65 * res.confidence
            elif res.status == "genuinely_absent":
                # For summary or projects in freshers, small neutral deduction
                weighted_score += weight * 0.30
            # extraction_failed gets 0 credit

        quality_pct = round((weighted_score / total_possible) * 100.0, 1) if total_possible > 0 else 0.0
        is_reliable = len(critical_warnings) == 0 and quality_pct >= 60.0

        if not is_reliable:
            notes.append("Extraction audit flagged potential parsing discrepancies. Please review flagged sections.")

        return CandidateVerificationReport(
            overall_quality_score=quality_pct,
            is_extraction_reliable=is_reliable,
            sections=sections_report,
            critical_warnings=critical_warnings,
            extraction_notes=notes,
        )

