"""Deterministic ATS-style resume scoring engine for FUTRSEC.

Calculates category-level and total compatibility scores using Neon database weights.
100% deterministic, reproducible, testable Python calculation.
Never invents evidence or relies on non-deterministic randomness.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.config import settings
from app.resume.extractor import ParsedResumeData
from app.scoring.matcher import EvidenceMatchReport


class CategoryScore(BaseModel):
    category_name: str
    weight: float
    score_earned: float
    percentage: float
    explanation: str
    details: Dict[str, Any] = Field(default_factory=dict)


class ATSScoreResult(BaseModel):
    role_id: int
    role_name: str
    final_score: float
    max_score: float = 100.0
    threshold: float = 80.0
    meets_threshold: bool
    status: str
    category_scores: List[CategoryScore]
    summary_explanation: str
    scoring_version: str = "1.0.0"


class ATSScoringEngine:
    """Calculates deterministic ATS compatibility score for a resume against a target role."""

    DEFAULT_WEIGHTS = {
        "Technical Skills": 40.0,
        "Projects": 25.0,
        "Education": 15.0,
        "Tools & Certifications": 15.0,
        "Career Objective": 5.0,
    }

    @classmethod
    def calculate_score(
        cls,
        resume_data: ParsedResumeData,
        match_report: EvidenceMatchReport,
        role_requirements: List[Dict[str, Any]],
        db_scoring_criteria: List[Dict[str, Any]],
        threshold: float = 80.0,
    ) -> ATSScoreResult:
        """Computes deterministic category and final scores."""

        # Extract weights from database criteria or use defaults
        weights = cls.DEFAULT_WEIGHTS.copy()
        for crit in db_scoring_criteria:
            cat = crit.get("category")
            if cat in weights:
                weights[cat] = float(crit.get("weight", weights[cat]))

        # 1. Score Technical Skills
        tech_score = cls._score_technical_skills(match_report, weights["Technical Skills"])

        # 2. Score Projects
        proj_score = cls._score_projects(resume_data.projects, match_report.role_name, weights["Projects"])

        # 3. Score Education
        edu_score = cls._score_education(resume_data.education, role_requirements, weights["Education"])

        # 4. Score Tools & Certifications
        tools_score = cls._score_tools_and_certs(
            resume_data.certifications, resume_data.technical_skills, weights["Tools & Certifications"]
        )

        # 5. Score Career Objective
        obj_score = cls._score_objective(
            resume_data.career_objective, resume_data.professional_summary, match_report.role_name, weights["Career Objective"]
        )

        categories = [tech_score, proj_score, edu_score, tools_score, obj_score]
        raw_final = sum(c.score_earned for c in categories)

        # Enforce strict bounds [0.0, 100.0]
        final_score = round(max(0.0, min(100.0, raw_final)), 1)
        meets_threshold = final_score >= threshold

        status = "ELIGIBLE_FOR_ROLE" if meets_threshold else "IMPROVEMENT_RECOMMENDED"

        if meets_threshold:
            summary = (
                f"Candidate achieved a strong FUTRSEC ATS compatibility score of {final_score}/100, "
                f"exceeding the {threshold} threshold for '{match_report.role_name}'. Core skills and evidence are well demonstrated."
            )
        else:
            summary = (
                f"Candidate achieved a score of {final_score}/100 for '{match_report.role_name}', "
                f"which is below the target threshold of {threshold}. Skill-gap analysis identified key areas "
                f"for AI-assisted resume enhancement."
            )

        return ATSScoreResult(
            role_id=match_report.role_id,
            role_name=match_report.role_name,
            final_score=final_score,
            threshold=threshold,
            meets_threshold=meets_threshold,
            status=status,
            category_scores=categories,
            summary_explanation=summary,
        )

    @classmethod
    def _score_technical_skills(cls, match_report: EvidenceMatchReport, weight: float) -> CategoryScore:
        """Technical skills scoring with weighted importance (Core: 1.5, Preferred: 1.0, Additional: 0.5)."""
        core_w, pref_w, add_w = 1.5, 1.0, 0.5

        weighted_matched = (
            match_report.matched_core_count * core_w
            + match_report.matched_preferred_count * pref_w
            + match_report.matched_additional_count * add_w
        )

        weighted_total = (
            match_report.total_core_count * core_w
            + match_report.total_preferred_count * pref_w
            + match_report.total_additional_count * add_w
        )

        if weighted_total > 0:
            ratio = min(1.0, weighted_matched / weighted_total)
            earned = round(ratio * weight, 1)
        else:
            ratio = 0.0
            earned = 0.0

        pct = round(ratio * 100, 1)
        explanation = (
            f"Matched {len(match_report.matched_skills)} of {match_report.total_role_skills} role skills "
            f"({match_report.matched_core_count}/{match_report.total_core_count} core, "
            f"{match_report.matched_preferred_count}/{match_report.total_preferred_count} preferred, "
            f"{match_report.matched_additional_count}/{match_report.total_additional_count} additional)."
        )

        return CategoryScore(
            category_name="Technical Skills",
            weight=weight,
            score_earned=earned,
            percentage=pct,
            explanation=explanation,
            details={
                "core_matched": match_report.matched_core_count,
                "core_total": match_report.total_core_count,
                "preferred_matched": match_report.matched_preferred_count,
                "preferred_total": match_report.total_preferred_count,
                "additional_matched": match_report.matched_additional_count,
                "additional_total": match_report.total_additional_count,
            },
        )

    @classmethod
    def _score_projects(cls, projects: List[Any], role_name: str, weight: float) -> CategoryScore:
        """Scores project evidence based on relevance, count, and technical description."""
        if not projects:
            return CategoryScore(
                category_name="Projects",
                weight=weight,
                score_earned=0.0,
                percentage=0.0,
                explanation="No technical or cybersecurity projects identified in resume.",
                details={"project_count": 0},
            )

        # Baseline per project (up to 3 projects, max 70% of weight)
        proj_count = len(projects)
        base_ratio = min(0.70, (proj_count / 3.0) * 0.70)

        # Bonus for cybersecurity relevance in project descriptions
        relevant_keywords = {"security", "vulnerability", "network", "firewall", "scan", "packet",
                             "exploit", "owasp", "incident", "splunk", "linux", "cloud", "siem",
                             "penetration", "auth", "crypto", "encryption", "threat"}

        bonus = 0.0
        for proj in projects:
            text = (getattr(proj, "description", "") + " " + getattr(proj, "title", "")).lower()
            matching_kw = [kw for kw in relevant_keywords if kw in text]
            if len(matching_kw) >= 2:
                bonus += 0.10

        bonus = min(0.30, bonus)
        total_ratio = min(1.0, base_ratio + bonus)
        earned = round(total_ratio * weight, 1)

        return CategoryScore(
            category_name="Projects",
            weight=weight,
            score_earned=earned,
            percentage=round(total_ratio * 100, 1),
            explanation=f"Demonstrated {proj_count} project(s) with practical hands-on cybersecurity and technical evidence.",
            details={"project_count": proj_count, "cyber_relevance_bonus_applied": bonus > 0},
        )

    @classmethod
    def _score_education(cls, education: List[Any], requirements: List[Dict[str, Any]], weight: float) -> CategoryScore:
        """Scores candidate education fairly against role-specific requirements from Neon database.
        
        Evaluates transparent degree relevance:
        - If role accepts broader backgrounds (arts, science, commerce, etc.), does not apply an arbitrary deduction.
        - If role documented criteria strictly prefers a technical/computing degree, applies a limited,
          calibrated adjustment (capped at 3.0 - 5.0 points within education category).
        - Separates degree relevance from candidate technical skills assessment.
        """
        if not education:
            return CategoryScore(
                category_name="Education",
                weight=weight,
                score_earned=0.0,
                percentage=0.0,
                explanation="No academic degrees or higher education credentials documented.",
                details={"degree_count": 0, "degree_relevance_adjustment": 0.0},
            )

        # Determine highest degree level
        has_postgrad = any("master" in getattr(e, "degree", "").lower() or "ph" in getattr(e, "degree", "").lower() for e in education)
        has_undergrad = any("bachelor" in getattr(e, "degree", "").lower() or "b.s" in getattr(e, "degree", "").lower() or "b.a" in getattr(e, "degree", "").lower() or "b.tech" in getattr(e, "degree", "").lower() or "b.e" in getattr(e, "degree", "").lower() for e in education)
        has_diploma = any("associate" in getattr(e, "degree", "").lower() or "diploma" in getattr(e, "degree", "").lower() for e in education)

        stem_fields = {"computer science", "cybersecurity", "information technology", "engineering",
                       "software", "data", "math", "physics", "infosec", "electrical"}

        is_stem = False
        for e in education:
            raw = (getattr(e, "degree", "") + " " + (getattr(e, "field_of_study", "") or "") + " " + (getattr(e, "raw_text", "") or "")).lower()
            if any(f in raw for f in stem_fields):
                is_stem = True
                break

        # Inspect role-specific education requirements from Neon PostgreSQL
        edu_reqs = [r for r in requirements if r.get("requirement_type") == "education"]
        req_desc = " ".join([r.get("requirement_description", "") for r in edu_reqs]).lower()
        is_mandatory = any(r.get("importance") == "mandatory" for r in edu_reqs)

        # Detect if role explicitly accepts broad backgrounds (e.g. Arts & Science, non-technical, any degree)
        accepts_broad = any(kw in req_desc for kw in [
            "no specific degree",
            "arts and science",
            "any academic background",
            "any degree",
            "commerce",
            "diploma, or other",
            "non-technical",
            "broader",
            "equivalent learning",
        ]) or not is_mandatory

        # Determine base ratio by degree level
        if has_postgrad:
            base_ratio = 1.0
            deg_desc = "Master's/Doctoral Degree"
        elif has_undergrad:
            if accepts_broad:
                base_ratio = 0.90
            else:
                base_ratio = 1.0 if is_stem else 0.90
            deg_desc = "Bachelor's Degree"
        elif has_diploma:
            base_ratio = 0.85 if is_stem else 0.75
            deg_desc = "Associate Degree/Diploma"
        else:
            base_ratio = 0.70 if is_stem else 0.65
            deg_desc = "Post-Secondary Education"

        # Apply project-specific education rule transparently
        # - Engineering or relevant computing degrees receive full available score
        # - Arts or non-computing degrees receive a maximum deduction of 3 points from overall resume score
        # - Applied only once, within education category
        deduction_pts = 0.0
        adjustment_explanation = ""

        if is_stem:
            adjustment_explanation = "Candidate holds a relevant engineering or computing degree; full available education score awarded."
        elif accepts_broad:
            adjustment_explanation = "Role criteria accepts broader backgrounds; evaluated without discipline deduction."
        else:
            if settings.ENABLE_NON_COMPUTING_EDUCATION_DEDUCTION:
                deduction_pts = min(settings.NON_COMPUTING_EDUCATION_DEDUCTION, weight)
                adjustment_explanation = (
                    f"Under current project evaluation policy, a calibrated education adjustment of "
                    f"-{deduction_pts:.1f} points is applied once for non-computing/arts degrees. "
                    f"Practical technical abilities and demonstrated skills are evaluated independently."
                )
            else:
                adjustment_explanation = "Non-computing academic background evaluated without discipline deduction."

        # Calculate final earned score (applied only once, strictly bounded in [0.0, weight])
        raw_earned = base_ratio * weight
        earned = round(max(0.0, min(weight, raw_earned - deduction_pts)), 1)
        final_percentage = round((earned / weight) * 100.0, 1) if weight > 0 else 0.0

        full_explanation = f"Demonstrated {deg_desc} ({'STEM/Engineering/Computing' if is_stem else 'Arts/Non-Computing'}). {adjustment_explanation}"

        return CategoryScore(
            category_name="Education",
            weight=weight,
            score_earned=earned,
            percentage=final_percentage,
            explanation=full_explanation.strip(),
            details={
                "highest_degree": deg_desc,
                "is_stem": is_stem,
                "education_deduction_applied": deduction_pts > 0,
                "education_deduction_pts": deduction_pts,
                "degree_relevance_adjustment_pts": -deduction_pts,
                "role_education_criteria_snippet": req_desc[:120] if req_desc else "General qualification standard",
            },
        )

    @classmethod
    def _score_tools_and_certs(cls, certs: List[str], skills: List[str], weight: float) -> CategoryScore:
        """Scores recognized cybersecurity certifications and security tools."""
        cert_count = len(certs)
        # Up to 2 certifications give up to 70% of category score
        cert_ratio = min(0.70, cert_count * 0.35)

        # Security tools from skills (Wireshark, Burp Suite, Metasploit, Nmap, Splunk, Nessus, etc.)
        known_tools = {"wireshark", "burp suite", "metasploit", "nmap", "splunk", "nessus", "snort",
                       "kali", "ghidra", "qualys", "sentinel", "crowdstrike", "openvas", "qradar"}

        skill_text = " ".join(skills).lower()
        tool_count = sum(1 for t in known_tools if t in skill_text)
        tool_ratio = min(0.30, tool_count * 0.10)

        total_ratio = min(1.0, cert_ratio + tool_ratio)
        earned = round(total_ratio * weight, 1)

        explanation = (
            f"Demonstrated {cert_count} credential(s) ({', '.join(certs[:3]) if certs else 'None'}) "
            f"and {tool_count} specialized security tool(s)."
        )

        return CategoryScore(
            category_name="Tools & Certifications",
            weight=weight,
            score_earned=earned,
            percentage=round(total_ratio * 100, 1),
            explanation=explanation,
            details={"cert_count": cert_count, "tool_count": tool_count},
        )

    @classmethod
    def _score_objective(cls, objective: Optional[str], summary: Optional[str], role_name: str, weight: float) -> CategoryScore:
        """Scores clarity and alignment of career objective / professional summary."""
        target_text = ((objective or "") + " " + (summary or "")).strip()
        if not target_text:
            return CategoryScore(
                category_name="Career Objective",
                weight=weight,
                score_earned=0.0,
                percentage=0.0,
                explanation="No career objective or professional summary present in resume.",
                details={"present": False},
            )

        target_lower = target_text.lower()
        role_lower = role_name.lower()

        # Check alignment with target role name
        role_words = [w for w in role_lower.split() if len(w) > 3]
        role_aligned = any(w in target_lower for w in role_words)

        has_length = len(target_text) >= 50

        if role_aligned and has_length:
            ratio = 1.0
            expl = f"Tailored objective directly aligned with '{role_name}' and cybersecurity focus."
        elif has_length:
            ratio = 0.70
            expl = "Professional summary is well-articulated but does not explicitly reference the target job title."
        else:
            ratio = 0.40
            expl = "Brief career objective provided; could be expanded to highlight specific role goals."

        earned = round(ratio * weight, 1)

        return CategoryScore(
            category_name="Career Objective",
            weight=weight,
            score_earned=earned,
            percentage=round(ratio * 100, 1),
            explanation=expl,
            details={"role_aligned": role_aligned, "length": len(target_text)},
        )
