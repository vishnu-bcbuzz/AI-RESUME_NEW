"""Skill-gap analysis module for cybersecurity career paths.

Analyzes matched versus missing role requirements from Neon database.
Generates prioritized, actionable improvement recommendations with future-action labeling.
Never assumes unmentioned skills are possessed by the candidate.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from app.scoring.matcher import EvidenceMatchReport, SkillMatchResult
from app.resume.extractor import ParsedResumeData


class GapRecommendation(BaseModel):
    priority: str  # high, medium, low
    category: str  # skill_gap, project_evidence, certification, objective
    title: str
    description: str
    suggested_action: str
    is_future_action: bool = False


class SkillConfirmationQuestion(BaseModel):
    skill_name: str
    importance: str  # core, preferred, additional
    category: str  # Core Competency, Security Tool, Operating System, etc.
    prompt_question: str
    options: List[Dict[str, str]]
    context_options: List[str]


class SkillGapAnalysisReport(BaseModel):
    role_id: int
    role_name: str
    matched_skills_count: int
    not_demonstrated_count: int
    demonstrated_skills: List[Dict[str, Any]]
    skills_requiring_confirmation: List[SkillConfirmationQuestion] = Field(default_factory=list)
    skills_not_demonstrated: List[Dict[str, Any]] = Field(default_factory=list)
    candidate_confirmed_skills: List[Dict[str, Any]] = Field(default_factory=list)
    missing_core_skills: List[str]
    missing_preferred_skills: List[str]
    missing_additional_skills: List[str]
    relevant_certifications_held: List[str]
    project_evidence_summary: List[str]
    experience_evidence_summary: List[str]
    prioritized_recommendations: List[GapRecommendation]
    future_learning_recommendations: List[GapRecommendation] = Field(default_factory=list)


class SkillGapAnalyzer:
    """Produces comprehensive, prioritized skill-gap reports for a candidate and role."""

    # Role-recommended certifications for career growth advice (future actions)
    ROLE_CERT_RECOMMENDATIONS = {
        "penetration": ["OSCP", "CEH", "CompTIA PenTest+", "eJPT"],
        "ethical hacker": ["CEH", "CompTIA PenTest+", "OSCP"],
        "security analyst": ["CompTIA CySA+", "CompTIA Security+", "Microsoft SC-200"],
        "soc": ["CompTIA CySA+", "BTL1", "Splunk Certified Core User"],
        "incident response": ["GCIH", "EC-Council ECIH", "CompTIA CySA+"],
        "cloud security": ["AWS Certified Security - Specialty", "CCSP", "Azure AZ-500"],
        "security engineer": ["CISSP", "CSSLP", "CompTIA Security+"],
        "compliance": ["CISA", "CRISC", "ISO 27001 Lead Auditor"],
    }

    @classmethod
    def analyze_gaps(
        cls,
        match_report: EvidenceMatchReport,
        resume_data: ParsedResumeData,
    ) -> SkillGapAnalysisReport:
        """Analyzes gaps between demonstrated resume evidence and role profile."""
        demonstrated = []
        for m in match_report.matched_skills:
            demonstrated.append({
                "skill_name": m.skill_name,
                "importance": m.importance,
                "sections": m.matched_in_sections,
                "evidence": m.evidence_snippet,
                "status": "demonstrated",
            })

        missing_core = [u.skill_name for u in match_report.unmatched_skills if u.importance == "core"]
        missing_pref = [u.skill_name for u in match_report.unmatched_skills if u.importance == "preferred"]
        missing_add = [u.skill_name for u in match_report.unmatched_skills if u.importance == "additional"]

        not_demonstrated = [
            {
                "skill_name": u.skill_name,
                "importance": u.importance,
                "status": "not_demonstrated",
            }
            for u in match_report.unmatched_skills
        ]

        # Generate role-specific confirmation questions for missing/unconfirmed role skills
        # Prioritize core and preferred skills
        confirmation_questions: List[SkillConfirmationQuestion] = []
        for u in match_report.unmatched_skills:
            # Determine appropriate category
            name_lower = u.skill_name.lower()
            if any(t in name_lower for t in ["wireshark", "burp", "nmap", "metasploit", "splunk", "nessus", "snort", "ghidra", "qualys", "tool"]):
                cat = "Security Tools & Technologies"
                item_label = f"tool '{u.skill_name}'"
            elif any(os_k in name_lower for os_k in ["linux", "windows", "kali", "powershell", "bash", "python"]):
                cat = "Operating Systems & Scripting"
                item_label = f"technology '{u.skill_name}'"
            else:
                cat = "Core Role Competencies"
                item_label = f"competency '{u.skill_name}'"

            q = SkillConfirmationQuestion(
                skill_name=u.skill_name,
                importance=u.importance,
                category=cat,
                prompt_question=f"Do you have practical or academic experience with {item_label} required for {match_report.role_name}?",
                options=[
                    {
                        "value": "hands_on",
                        "label": "Yes, I have hands-on experience.",
                        "description": "Used practically in projects, labs, internships, or production."
                    },
                    {
                        "value": "basic_familiarity",
                        "label": "I have basic familiarity or coursework exposure.",
                        "description": "Understands concepts, foundational knowledge, or coursework exposure."
                    },
                    {
                        "value": "not_used",
                        "label": "I have not used it yet.",
                        "description": "Have not worked with this skill yet; recommend future learning resources."
                    },
                ],
                context_options=[
                    "Academic Project",
                    "Internship",
                    "Hands-on Home Lab / CTF",
                    "University Coursework",
                    "Personal Practice & Development",
                    "Professional Employment",
                ],
            )
            confirmation_questions.append(q)

        # Project summaries
        project_summaries = [
            f"{p.title}: {p.description[:80]}..." if len(p.description) > 80 else f"{p.title}: {p.description}"
            for p in resume_data.projects
        ]

        # Experience summaries
        exp_summaries = [
            f"{e.job_title} ({e.company or 'Organization'})"
            for e in resume_data.employment_history
        ]

        all_recommendations = cls._generate_recommendations(
            role_name=match_report.role_name,
            missing_core=missing_core,
            missing_pref=missing_pref,
            resume_data=resume_data,
        )

        future_recs = [r for r in all_recommendations if r.is_future_action]

        return SkillGapAnalysisReport(
            role_id=match_report.role_id,
            role_name=match_report.role_name,
            matched_skills_count=len(match_report.matched_skills),
            not_demonstrated_count=len(match_report.unmatched_skills),
            demonstrated_skills=demonstrated,
            skills_requiring_confirmation=confirmation_questions,
            skills_not_demonstrated=not_demonstrated,
            candidate_confirmed_skills=[],
            missing_core_skills=missing_core,
            missing_preferred_skills=missing_pref,
            missing_additional_skills=missing_add,
            relevant_certifications_held=resume_data.certifications,
            project_evidence_summary=project_summaries,
            experience_evidence_summary=exp_summaries,
            prioritized_recommendations=all_recommendations,
            future_learning_recommendations=future_recs,
        )

    @classmethod
    def _generate_recommendations(
        cls,
        role_name: str,
        missing_core: List[str],
        missing_pref: List[str],
        resume_data: ParsedResumeData,
    ) -> List[GapRecommendation]:
        """Generates prioritized, factually compliant recommendations."""
        recs: List[GapRecommendation] = []

        # 1. High Priority: Missing Core Skills
        if missing_core:
            top_missing = missing_core[:4]
            recs.append(GapRecommendation(
                priority="high",
                category="skill_gap",
                title=f"Demonstrate Core Skills for {role_name}",
                description=(
                    f"The following foundational core skills are not currently demonstrated in your resume: "
                    f"{', '.join(top_missing)}. If you have practical academic or project experience with these, "
                    f"explicitly detail them."
                ),
                suggested_action=(
                    "If you possess hands-on familiarity, add these skills to your Technical Skills section "
                    "or detail projects where you utilized them. Never claim skills you cannot defend."
                ),
                is_future_action=False,
            ))

        # 2. Medium Priority: Project Evidence
        if len(resume_data.projects) == 0:
            recs.append(GapRecommendation(
                priority="high",
                category="project_evidence",
                title="Add Practical Cybersecurity Project Evidence",
                description=(
                    f"Your resume does not currently list hands-on technical projects. For {role_name}, "
                    f"employers heavily value lab environments, CTF write-ups, or security tools development."
                ),
                suggested_action=(
                    "Document 1-2 home lab or academic projects (e.g., TryHackMe/HackTheBox, network packet analysis, "
                    "or defensive scripting in Python/Bash)."
                ),
                is_future_action=False,
            ))
        elif len(resume_data.projects) < 2:
            recs.append(GapRecommendation(
                priority="medium",
                category="project_evidence",
                title="Expand Project Portfolio with Quantifiable Metrics",
                description="Strengthen your existing project by adding quantifiable outcomes or specific tools used.",
                suggested_action="Mention specific toolsets (e.g., Wireshark, Burp Suite, Nmap) and measurable outcomes.",
                is_future_action=False,
            ))

        # 3. Medium Priority: Future Certification Advice (clearly labeled as future action)
        role_lower = role_name.lower()
        suggested_future_certs = []
        for key, cert_list in cls.ROLE_CERT_RECOMMENDATIONS.items():
            if key in role_lower:
                suggested_future_certs.extend(cert_list)

        unheld_certs = [c for c in suggested_future_certs if c not in resume_data.certifications]
        if unheld_certs:
            top_future_cert = unheld_certs[0]
            recs.append(GapRecommendation(
                priority="medium",
                category="certification",
                title=f"Future Professional Certification: {top_future_cert}",
                description=(
                    f"To enhance long-term career progression for {role_name}, obtaining industry credentials like "
                    f"{top_future_cert} is highly regarded by hiring managers."
                ),
                suggested_action=(
                    f"Consider studying for {top_future_cert} as a future milestone. Do not add this certification "
                    f"to your resume until you have officially passed the exam."
                ),
                is_future_action=True,
            ))

        # 4. Low Priority: Preferred Skills
        if missing_pref:
            recs.append(GapRecommendation(
                priority="low",
                category="skill_gap",
                title="Incorporate Preferred Secondary Skills",
                description=f"Additional preferred skills for this role include: {', '.join(missing_pref[:3])}.",
                suggested_action="Include these if you have had exposure to them in coursework or self-study.",
                is_future_action=False,
            ))

        return recs
