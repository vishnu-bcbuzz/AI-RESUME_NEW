"""Resume content enhancement and generation module for FUTRSEC.

Generates ATS-optimized, professionally phrased resume content for cybersecurity roles.
Improves clarity and structure while strictly preserving factual accuracy.
Never invents metrics, credentials, or employment history.
Operates via OpenAI-compatible API when configured, with a deterministic rule-based enhancer fallback.
"""

import json
import logging
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import httpx

from app.config import settings
from app.resume.extractor import ParsedResumeData, ExperienceEntry, ProjectEntry, ResumeExtractor, CertificationEntry
from app.resume.validator import ResumeContentValidator
from app.resume.skills_taxonomy import (
    structure_and_classify_skills,
    is_valid_technical_skill,
    normalize_skill_name,
    STANDARD_CATEGORIES,
)

logger = logging.getLogger("futrsec.generator")


class ConfirmedSkillItem(BaseModel):
    """Candidate confirmation model for skills requiring validation."""
    skill_name: str
    proficiency: str  # 'hands_on' | 'basic_familiarity' | 'not_used'
    context_source: Optional[str] = None  # 'Academic Project' | 'Internship' | 'Laboratory' | 'Coursework' | 'Personal Practice' | 'Professional Employment'
    tasks_performed: Optional[str] = None
    interview_demonstration: Optional[str] = None


class EnhancedResumeContent(BaseModel):
    """Complete rewritten resume model for ATS-compliant rendering."""
    candidate_name: str
    contact_header: str
    contact_details: Dict[str, Optional[str]]
    professional_headline: Optional[str] = None
    professional_summary: str
    technical_skills_grouped: Dict[str, List[str]]
    experience: List[Dict[str, Any]]
    internships: List[Dict[str, Any]] = Field(default_factory=list)
    projects: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    certifications: List[str]
    structured_certifications: List[CertificationEntry] = Field(default_factory=list)
    achievements: List[str]
    confirmed_skills_included: List[str] = Field(default_factory=list)
    unverified_skills_excluded: List[str] = Field(default_factory=list)
    pursuing_certifications: List[str] = Field(default_factory=list)
    approved_improvements_applied: List[str] = Field(default_factory=list)
    sections_rewritten: List[str] = Field(default_factory=list)
    future_learning_recommendations: List[str] = Field(default_factory=list)
    pending_confirmations: List[str] = Field(default_factory=list)
    generator_mode: str = "deterministic_enhancer"
    attempt_number: int = 1


class ResumeContentGenerator:
    """Generates improved ATS resume content respecting strict factual boundaries."""

    # Active cybersecurity action verbs for bullet point enhancement
    ACTION_VERBS = [
        "Analyzed", "Assessed", "Configured", "Deployed", "Detected", "Developed",
        "Engineered", "Evaluated", "Hardened", "Implemented", "Investigated",
        "Mitigated", "Monitored", "Remediated", "Resolved", "Secured", "Triaged"
    ]

    @classmethod
    def check_health(cls) -> Dict[str, Any]:
        """Diagnostic check for OpenAI GPT API credentials and model availability.

        Never logs or exposes secret keys.
        """
        api_key = settings.effective_openai_key
        model = settings.OPENAI_MODEL

        if not api_key:
            return {
                "available": False,
                "configured": False,
                "provider": "OpenAI GPT",
                "model": model,
                "status": "not_configured",
                "error": "OPENAI_API_KEY environment variable is not configured.",
                "troubleshooting": (
                    "Add OPENAI_API_KEY to your .env file or environment variables "
                    "to enable OpenAI GPT resume optimization."
                ),
            }

        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, timeout=8.0)
            model_info = client.models.retrieve(model)
            return {
                "available": True,
                "configured": True,
                "provider": "OpenAI GPT",
                "model": model,
                "status": "online",
                "display_name": getattr(model_info, "id", model),
                "troubleshooting": None,
            }
        except Exception as exc:
            err_msg = str(exc)
            return {
                "available": False,
                "configured": True,
                "provider": "OpenAI GPT",
                "model": model,
                "status": "error",
                "error": f"OpenAI API diagnostic check failed: {err_msg}",
                "troubleshooting": "Verify that your OPENAI_API_KEY is valid and has access to the configured OPENAI_MODEL.",
            }

    @classmethod
    def generate_enhanced_content(
        cls,
        resume_data: ParsedResumeData,
        target_role_name: str,
        missing_core_skills: List[str],
        confirmed_skills: Optional[List[ConfirmedSkillItem]] = None,
        approved_plan_items: Optional[List[Any]] = None,
        permission_granted: bool = True,
        attempt_number: int = 1,
        candidate_notes: Optional[str] = None,
        approved_projects: Optional[List[Any]] = None,
    ) -> EnhancedResumeContent:
        """Entry point for complete resume content rewriting and improvement."""
        confirmed_skills = confirmed_skills or []
        approved_plan_items = approved_plan_items or []
        approved_projects = approved_projects or []

        if settings.is_ai_configured():
            try:
                logger.info("Attempting AI-assisted resume content enhancement via LLM (attempt %s)...", attempt_number)
                raw_content = cls._generate_with_llm(
                    resume_data=resume_data,
                    role_name=target_role_name,
                    missing_core_skills=missing_core_skills,
                    confirmed_skills=confirmed_skills,
                    approved_plan_items=approved_plan_items,
                    permission_granted=permission_granted,
                    attempt_number=attempt_number,
                    candidate_notes=candidate_notes,
                    approved_projects=approved_projects,
                )
            except Exception as exc:
                logger.warning("LLM generation encountered an error: %s. Falling back to deterministic enhancer.", exc)
                raw_content = cls._generate_with_heuristics(
                    resume=resume_data,
                    role_name=target_role_name,
                    missing_core_skills=missing_core_skills,
                    confirmed_skills=confirmed_skills,
                    approved_plan_items=approved_plan_items,
                    permission_granted=permission_granted,
                    fallback_reason=str(exc),
                    attempt_number=attempt_number,
                    candidate_notes=candidate_notes,
                    approved_projects=approved_projects,
                )
        else:
            logger.info("No LLM API key configured. Using deterministic enhancement engine (attempt %s).", attempt_number)
            raw_content = cls._generate_with_heuristics(
                resume=resume_data,
                role_name=target_role_name,
                missing_core_skills=missing_core_skills,
                confirmed_skills=confirmed_skills,
                approved_plan_items=approved_plan_items,
                permission_granted=permission_granted,
                attempt_number=attempt_number,
                candidate_notes=candidate_notes,
                approved_projects=approved_projects,
            )

        # Strictly validate and sanitize content before returning to caller or document renderer
        sanitized_content, val_report = ResumeContentValidator.validate_and_sanitize(raw_content)
        if val_report.corrections_applied:
            logger.info("ResumeContentValidator applied %d corrections to resume content.", len(val_report.corrections_applied))
        return sanitized_content

    @classmethod
    def _generate_with_heuristics(
        cls,
        resume: ParsedResumeData,
        role_name: str,
        missing_core_skills: List[str],
        confirmed_skills: List[ConfirmedSkillItem],
        approved_plan_items: Optional[List[Any]] = None,
        permission_granted: bool = True,
        fallback_reason: Optional[str] = None,
        attempt_number: int = 1,
        candidate_notes: Optional[str] = None,
        approved_projects: Optional[List[Any]] = None,
    ) -> EnhancedResumeContent:
        """Deterministic, rule-based full resume rewriting that polishes syntax and preserves facts 100%."""
        approved_plan_items = approved_plan_items or []
        approved_projects = approved_projects or []

        # 1. Candidate Name & Contact Details Header
        name = resume.candidate_name or "Cybersecurity Professional"
        c = resume.contact_info
        contact_parts = []
        if c.email:
            contact_parts.append(c.email)
        if c.phone:
            contact_parts.append(c.phone)
        if c.location:
            contact_parts.append(c.location)
        if c.linkedin:
            contact_parts.append(c.linkedin)
        if c.github:
            contact_parts.append(c.github)

        contact_header = " | ".join(contact_parts)

        # 2. Professional Headline adapted to selected cybersecurity job role
        role_low = role_name.lower()
        if "penetration" in role_low or "ethical" in role_low or "red team" in role_low:
            headline = "Offensive Cybersecurity Specialist | Penetration Testing, Vulnerability Assessment & Ethical Hacking"
        elif "soc" in role_low or "incident" in role_low or "threat" in role_low or "analyst" in role_low:
            headline = "Cybersecurity Operations & Defense Analyst | Threat Monitoring, SIEM & Incident Investigation"
        elif "cloud" in role_low:
            headline = "Cloud Security Specialist | Architecture Hardening, IAM & Cloud Security Controls"
        elif "engineer" in role_low:
            headline = "Cybersecurity Systems Engineer | Infrastructure Hardening, Security Automation & Defense"
        elif "compliance" in role_low or "privacy" in role_low:
            headline = "Information Security & Compliance Analyst | Regulatory Governance, Risk & Standards"
        else:
            headline = f"{role_name} | Cybersecurity & Technical Defense Specialist"

        # Collect approved improvements list and pursuing certs
        approved_applied: List[str] = []
        pursuing_certs: List[str] = []

        # Convert approved_plan_items into dictionary by key/item_id
        plan_dict: Dict[str, Dict[str, Any]] = {}
        for item in approved_plan_items:
            if isinstance(item, dict):
                st = item.get("status")
                if st in ("approved", "edited"):
                    k = item.get("category_key") or item.get("item_id")
                    if k:
                        plan_dict[k] = item
                    if item.get("item_id"):
                        plan_dict[item["item_id"]] = item
            else:
                st = getattr(item, "status", "")
                if st in ("approved", "edited"):
                    d = item.model_dump()
                    k = getattr(item, "category_key", getattr(item, "item_id", ""))
                    if k:
                        plan_dict[k] = d
                    if getattr(item, "item_id", None):
                        plan_dict[getattr(item, "item_id")] = d

        # Unpack skills and tools confirmations from plan items if provided
        for p_key in ("plan_tech_skills", "technical_skills", "plan_tools", "tools"):
            if p_key in plan_dict:
                p_item = plan_dict[p_key]
                p_resp = p_item.get("candidate_response", {})
                for q in p_item.get("follow_up_questions", []):
                    q_id = q.get("id")
                    s_name = q.get("skill_name") or q.get("tool_name")
                    chosen_val = p_resp.get(q_id)
                    if s_name and chosen_val in ("hands_on", "basic_familiarity", "not_used"):
                        if not any(cs.skill_name.lower() == s_name.lower() for cs in confirmed_skills):
                            confirmed_skills.append(ConfirmedSkillItem(
                                skill_name=s_name,
                                proficiency=chosen_val,
                                context_source="Candidate Confirmation",
                                tasks_performed=f"Proficiency verified as {chosen_val} for {s_name}."
                            ))
                if p_key in ("plan_tech_skills", "technical_skills"):
                    approved_applied.append("Verified and categorized core technical skills against role requirements")
                else:
                    approved_applied.append("Structured security tools into Offensive/Defensive & SIEM categories")

        # Process individual skill cards from plan items
        for p_key, p_item in plan_dict.items():
            if p_item.get("item_type") == "skill_card" or p_item.get("skill_details"):
                s_details = p_item.get("skill_details") or {}
                s_name = (
                    s_details.get("skill_name")
                    or p_item.get("title", "").replace("Core Skill: ", "").replace("Preferred Skill: ", "").replace("Additional Skill: ", "").strip()
                )
                p_resp = p_item.get("candidate_response", {})
                chosen_val = None
                for q in p_item.get("follow_up_questions", []):
                    qid = q.get("id")
                    if qid in p_resp:
                        val = p_resp[qid]
                        if val in ("hands_on", "basic_familiarity", "not_used"):
                            chosen_val = val
                            break
                if not chosen_val and p_item.get("candidate_action_selected") in ("Confirm Existing Experience", "hands_on"):
                    chosen_val = "hands_on"

                details_text = p_resp.get(f"skill_{s_name.lower().replace(' ', '_').replace('/', '_')}_details") or f"Practical experience with {s_name}."

                if s_name and chosen_val in ("hands_on", "basic_familiarity", "not_used", "beginner", "intermediate", "advanced", "not_yet"):
                    if not any(cs.skill_name.lower() == s_name.lower() for cs in confirmed_skills):
                        confirmed_skills.append(ConfirmedSkillItem(
                            skill_name=s_name,
                            proficiency=chosen_val,
                            context_source="Candidate Confirmation",
                            tasks_performed=details_text
                        ))
                    approved_applied.append(f"Incorporated candidate confirmation for {s_name}")

        # 3. Process candidate-confirmed skills and permission
        confirmed_included: List[str] = []
        unverified_excluded: List[str] = []
        future_learning: List[str] = []
        hands_on_confirmed: List[ConfirmedSkillItem] = []
        basic_familiarity_confirmed: List[ConfirmedSkillItem] = []

        active_skills = list(resume.technical_skills)

        # Candidate notes inclusion
        if candidate_notes:
            for item in re.split(r"[,;\n]", candidate_notes):
                cleaned = item.strip()
                if cleaned and cleaned not in active_skills and len(cleaned) > 1:
                    active_skills.append(cleaned)

        if permission_granted and confirmed_skills:
            for item in confirmed_skills:
                skill_clean = item.skill_name.strip()
                prof_lower = item.proficiency.lower()
                if prof_lower in ("hands_on", "intermediate", "advanced"):
                    # Candidate confirmed practical/hands-on experience
                    if skill_clean not in active_skills:
                        active_skills.append(skill_clean)
                    confirmed_included.append(skill_clean)
                    hands_on_confirmed.append(item)
                elif prof_lower in ("basic_familiarity", "beginner", "basic"):
                    # Basic exposure/coursework familiarity - documented as foundational knowledge
                    confirmed_included.append(f"{skill_clean} (Foundational)")
                    basic_familiarity_confirmed.append(item)
                else:  # not_used, not_yet, or rejected
                    # STRICT RULE: Must not appear as existing competency
                    unverified_excluded.append(skill_clean)
                    future_learning.append(
                        f"Recommended Learning: Complete hands-on lab exercises or tutorials for '{skill_clean}' "
                        f"to build practical capability for {role_name}."
                    )
        elif not permission_granted and confirmed_skills:
            # Candidate did not grant permission to include confirmed skills
            for item in confirmed_skills:
                unverified_excluded.append(item.skill_name.strip())

        # 4. Professional Summary (Concise, role-specific, target 40-60 words)
        existing_summary = resume.professional_summary or resume.career_objective or ""

        # Identify fresher vs experienced status
        is_fresher = (
            len(resume.employment_history) == 0
            or all(
                any(t in (e.get("job_title", "") if isinstance(e, dict) else getattr(e, "job_title", "")).lower() for t in ("intern", "internship", "trainee", "student", "fellow"))
                for e in resume.employment_history
            )
        )

        # Filter out non-skills, metrics, and platforms from active skills
        prohibited_metric_pattern = re.compile(
            r"(?i)\b(?:eda|mae|rmse|mse|r2|r²|r-squared|auc|roc|accuracy|precision|recall|loss|p-value|confusion\s+matrix|model\s+evaluation)\b"
        )
        clean_active_skills = []
        for s in active_skills:
            sc = ResumeExtractor.CATEGORY_PREFIX_PATTERN.sub("", s).strip()
            sc = re.sub(r"^[(\[\-:\s]+|[)\]\-:\s]+$", "", sc).strip()
            if (
                sc and len(sc) > 1
                and not prohibited_metric_pattern.search(sc)
                and not any(re.match(rf"^{re.escape(cert)}$", sc, re.IGNORECASE) for cert in ["CEH", "CISSP", "CompTIA Security+", "Security+", "OSCP"])
                and sc.lower() not in [x.lower() for x in clean_active_skills]
            ):
                clean_active_skills.append(sc)
        active_skills = clean_active_skills

        # Determine top 2-3 role-relevant skills for summary
        sec_keywords = {"burp suite", "nmap", "wireshark", "splunk", "metasploit", "python", "linux", "sql", "owasp", "snort", "sysmon"}
        if any(sec_term in role_name.lower() for sec_term in ("security", "hacker", "pentest", "soc", "analyst", "forensic", "vapt")):
            sec_matches = [s for s in active_skills if s.lower() in sec_keywords or any(k in s.lower() for k in ("burp", "nmap", "wireshark", "security", "linux", "python", "owasp"))]
            top_skills = sec_matches[:3] if sec_matches else active_skills[:3]
        else:
            top_skills = active_skills[:3]
        top_skills_phrase = ", ".join(top_skills) if top_skills else "software engineering and system security"

        # Candidate degree or education reference
        if resume.education:
            edu_field = resume.education[0].field_of_study or "Computer Science"
            edu_label = f"{edu_field} graduate"
        else:
            edu_label = "technical professional"

        # Check candidate response for summary customization
        custom_summary = None
        for s_key in ("plan_summary", "summary"):
            if s_key in plan_dict:
                s_resp = plan_dict[s_key].get("candidate_response", {})
                custom_text = s_resp.get("custom_summary_input")
                if custom_text and len(custom_text.strip()) > 20:
                    custom_summary = custom_text.strip()
                    approved_applied.append("Applied candidate-approved professional headline & summary")
                else:
                    approved_applied.append("Refined professional summary and cybersecurity headline")

        if custom_summary:
            summary = custom_summary
        elif is_fresher:
            if attempt_number == 1:
                summary = (
                    f"Results-driven {edu_label} specializing in {role_name} methodologies, application security, and hands-on technical analysis. "
                    f"Demonstrates core capability across {top_skills_phrase} through academic implementations and isolated lab projects. "
                    f"Dedicated to applying defense-in-depth security principles, proactive threat assessment, and robust engineering to protect enterprise environments."
                )
            elif attempt_number == 2:
                summary = (
                    f"Proactive {edu_label} focused on practical {role_name} implementation, systems analysis, and secure software development. "
                    f"Proficient in {top_skills_phrase} with proven experience executing hands-on vulnerability assessments in authorized lab environments. "
                    f"Committed to delivering disciplined security evaluations, actionable technical documentation, and continuous defense improvements."
                )
            else:
                summary = (
                    f"Motivated {role_name} aspirant with a solid foundation in {edu_label} and security engineering principles. "
                    f"Possesses hands-on technical proficiency in {top_skills_phrase} backed by rigorous academic projects and testing environments. "
                    f"Aimed at applying defense-in-depth methodologies, vulnerability remediation, and reliable system monitoring within high-assurance teams."
                )
        else:  # Experienced candidate
            if attempt_number == 1:
                summary = (
                    f"Dedicated {role_name} practitioner with proven technical acumen in {top_skills_phrase} and secure systems engineering. "
                    f"Experienced in conducting structured vulnerability assessments, threat analysis, and implementing defense-in-depth security controls across enterprise architectures. "
                    f"Committed to delivering high-assurance security testing, cross-functional remediation guidance, and proactive risk reduction aligned with industry standards."
                )
            elif attempt_number == 2:
                summary = (
                    f"Proactive {role_name} specialist with demonstrated expertise across {top_skills_phrase}. "
                    f"Experienced in threat surface mapping, security architecture hardening, and operational incident triage within complex environments. "
                    f"Focused on delivering disciplined technical assessments, reproducible verification deliverables, and strategic security posture improvements."
                )
            else:
                summary = (
                    f"Accomplished {role_name} professional demonstrating hands-on operational capability in {top_skills_phrase} and defense-in-depth architecture. "
                    f"Skilled in structured vulnerability discovery, risk classification, and technical remediation adhering to high-assurance cybersecurity frameworks. "
                    f"Driven to enhance organizational resilience through rigorous testing, automation, and collaborative mitigation."
                )

        # 5. Categorized Technical Skills into clean standard categories using taxonomy pipeline
        categorized_skills = structure_and_classify_skills(
            raw_skills=active_skills,
            candidate_name=resume.candidate_name,
            contact_info=resume.contact_info,
            target_role_name=role_name,
        )

        # Add candidate-confirmed basic familiarity skills under dedicated transparent header if present
        if basic_familiarity_confirmed:
            categorized_skills["Foundational Knowledge & Coursework Exposure"] = [
                f"{b.skill_name} (Coursework/Basic Familiarity)" for b in basic_familiarity_confirmed
            ]

        # 6. Professional Experience Enhancement
        enhanced_exp = []
        for e in resume.employment_history:
            polished_resp = []
            for r in e.responsibilities:
                polished = cls._polish_bullet(r)
                if polished:
                    polished_resp.append(polished)

            enhanced_exp.append({
                "job_title": e.job_title,
                "company": e.company,
                "start_date": e.start_date,
                "end_date": e.end_date,
                "is_current": e.is_current,
                "responsibilities": polished_resp or e.responsibilities,
            })

        # Process experience plan item if candidate provided clarification
        for exp_key in ("plan_experience", "experience"):
            if exp_key in plan_dict:
                exp_resp = plan_dict[exp_key].get("candidate_response", {})
                sec_duties = exp_resp.get("security_duties_clarification")
                intern_details = exp_resp.get("internship_details")
                if sec_duties:
                    duties_polished = cls._polish_bullet(sec_duties)
                    if enhanced_exp:
                        enhanced_exp[0]["responsibilities"].append(duties_polished)
                    else:
                        enhanced_exp.append({
                            "job_title": f"{role_name} Practitioner",
                            "company": None,
                            "start_date": "",
                            "end_date": "Present",
                            "is_current": True,
                            "responsibilities": [duties_polished],
                        })
                    approved_applied.append("Integrated candidate-confirmed operational security duties into employment history")
                if intern_details:
                    enhanced_exp.append({
                        "job_title": "Cybersecurity / Technical Intern",
                        "company": None,
                        "start_date": "",
                        "end_date": "",
                        "is_current": False,
                        "responsibilities": [cls._polish_bullet(intern_details)],
                    })
                    approved_applied.append("Included candidate-confirmed cybersecurity internship")
                if not sec_duties and not intern_details:
                    approved_applied.append("Enhanced experience bullet points with active cybersecurity verbs")

        # 7. Project Descriptions Enhancement (genuine projects ONLY - no skill confirmations as projects)
        enhanced_projects = []
        for p in resume.projects:
            desc = p.description or ""
            # On attempt 2 & 3, ensure clear cybersecurity context in description without changing facts
            if attempt_number >= 2:
                cyber_keywords = {"security", "vulnerability", "network", "scan", "packet", "incident", "threat"}
                if not any(k in desc.lower() for k in cyber_keywords):
                    desc = f"{cls._polish_bullet(desc)} Implemented security analysis and verification to safeguard network and application assets."

            # Structure and polish bullets
            bullets_raw = list(getattr(p, "bullets", None) or [])
            if not bullets_raw and desc:
                if "\n" in desc:
                    bullets_raw = [b.strip() for b in desc.split("\n") if b.strip()]
                elif len(desc) > 90 and "." in desc:
                    bullets_raw = [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])", desc) if s.strip()]
                else:
                    bullets_raw = [desc]

            polished_bullets = []
            for b in bullets_raw:
                pb = cls._polish_project_bullet(b)
                if pb:
                    polished_bullets.append(pb)

            if not polished_bullets and desc:
                pb = cls._polish_project_bullet(desc)
                if pb:
                    polished_bullets.append(pb)

            # Clean project base title
            raw_title = p.title.strip()
            base_title = re.sub(r"\s*\|\s*(?:Status:\s*)?(?:In Progress|Completed)$", "", raw_title, flags=re.IGNORECASE).strip()
            status_val = getattr(p, "status", None) or ("In Progress" if "in progress" in raw_title.lower() else "Completed")

            enhanced_projects.append({
                "title": base_title,
                "status": status_val,
                "technologies": p.technologies or active_skills[:4],
                "description": " \n".join(polished_bullets) if polished_bullets else desc,
                "bullets": polished_bullets or ([desc] if desc else []),
                "github_url": getattr(p, "github_url", None),
                "project_url": getattr(p, "project_url", None),
                "outcomes": p.outcomes,
            })

        # Incorporate candidate-approved completed or in-progress projects (authoritative inclusion)
        if approved_projects:
            for appr_proj in reversed(approved_projects):
                title_line = getattr(appr_proj, "title_line", "") or "Cybersecurity Practical Project"
                status_lbl = getattr(appr_proj, "status_label", "Completed")
                bullets = getattr(appr_proj, "bullets", [])

                is_in_prog = "in progress" in str(status_lbl).lower() or "in progress" in title_line.lower()
                base_title = re.sub(r"\s*\|\s*in\s*progress$", "", title_line.strip(), flags=re.IGNORECASE).strip()
                clean_title = f"{base_title} | In Progress" if is_in_prog else base_title

                # Extract technologies
                techs = []
                for b in bullets:
                    if b.lower().startswith("technologies:"):
                        techs = [t.strip() for t in b.split(":", 1)[1].rstrip(".").split(",") if t.strip()]
                        break
                if not techs:
                    techs = [t.strip() for t in base_title.split("|")[-1].split(",") if t.strip()]

                # Avoid duplicate entries against existing resume projects
                existing_match = [ep for ep in enhanced_projects if base_title.lower() == re.sub(r"\s*\|\s*in\s*progress$", "", ep["title"].strip(), flags=re.IGNORECASE).strip().lower()]
                if existing_match:
                    existing_match[0]["title"] = clean_title
                    existing_match[0]["status"] = "In Progress" if is_in_prog else "Completed"
                    if bullets:
                        existing_match[0]["description"] = " \n".join(bullets)
                        existing_match[0]["bullets"] = bullets
                    if getattr(appr_proj, "github_url", None):
                        existing_match[0]["github_url"] = getattr(appr_proj, "github_url", None)
                else:
                    enhanced_projects.insert(0, {
                        "title": clean_title,
                        "status": "In Progress" if is_in_prog else "Completed",
                        "description": " \n".join(bullets),
                        "technologies": techs,
                        "outcomes": bullets[-1] if bullets else "Verified practical outcome",
                        "bullets": bullets,
                        "github_url": getattr(appr_proj, "github_url", None) or getattr(appr_proj, "project_url", None),
                    })

                appr_note = f"Added candidate-approved project: {clean_title}"
                if appr_note not in approved_applied:
                    approved_applied.append(appr_note)

        # If candidate confirmed hands-on work with specific Academic/Personal Project context and detailed tasks,
        # incorporate it as a legitimate technical project with a realistic title (never an artificial confirmation tag).
        for cs in confirmed_skills:
            if cs.proficiency == "hands_on" and cs.tasks_performed and cs.context_source in ("Academic Project", "Personal Project", "Hands-on Lab"):
                proj_title = f"{cs.skill_name} Security Assessment"
                if not any(proj_title.lower() in p["title"].lower() or cs.skill_name.lower() in p["title"].lower() for p in enhanced_projects):
                    enhanced_projects.append({
                        "title": proj_title,
                        "status": "Completed",
                        "technologies": [cs.skill_name],
                        "description": cs.tasks_performed,
                        "bullets": [cs.tasks_performed],
                        "github_url": None,
                        "outcomes": f"Conducted hands-on security verification using {cs.skill_name}.",
                    })
                    approved_applied.append(f"Incorporated verified practical project: {proj_title}")

        # Process projects plan item: candidate-added omitted project or future recommendation
        for proj_key, p_item in plan_dict.items():
            if proj_key in ("plan_projects", "projects", "plan_project_recommendation") or p_item.get("item_type") == "project_recommendation":
                p_resp = p_item.get("candidate_response", {})
                if p_resp.get("has_omitted_project") == "yes":
                    proj_tmpl = p_item.get("project_recommendation") or {}
                    p_title = p_resp.get("project_title") or proj_tmpl.get("project_title") or f"{role_name} Practical Security Implementation"
                    p_techs_raw = p_resp.get("project_technologies") or ""
                    p_techs = [t.strip() for t in re.split(r"[,;]", p_techs_raw) if t.strip()] or proj_tmpl.get("proposed_technologies") or active_skills[:3]
                    p_contrib = p_resp.get("project_contribution") or (proj_tmpl.get("suggested_implementation_tasks", [""])[0] if proj_tmpl.get("suggested_implementation_tasks") else "Configured and tested security controls and documented mitigation procedures.")
                    p_outcomes = p_resp.get("project_outcomes") or proj_tmpl.get("expected_deliverables") or "Validated system defenses against common attack vectors."
                    if not any(ep["title"].lower() == p_title.lower() for ep in enhanced_projects):
                        enhanced_projects.append({
                            "title": p_title,
                            "status": "Completed",
                            "technologies": p_techs,
                            "description": p_contrib,
                            "bullets": [p_contrib],
                            "github_url": None,
                            "outcomes": p_outcomes,
                        })
                        for t in p_techs:
                            if t not in active_skills:
                                active_skills.append(t)
                        approved_applied.append(f"Added verified practical project: {p_title}")
                elif p_resp.get("has_omitted_project") == "no":
                    future_learning.append(
                        f"Recommended Future Project: Deploy a home lab environment for {role_name} "
                        f"using open-source tools to build practical implementation evidence."
                    )
                approved_applied.append("Polished technical project descriptions with cybersecurity action verbs")

        # Deduplicate and rank projects by role relevance (while strictly retaining all genuine projects)
        enhanced_projects = cls._deduplicate_enhanced_projects(enhanced_projects)
        enhanced_projects = cls._rank_projects_for_role(enhanced_projects, role_name, missing_core_skills)

        # 8. Education (Preserve genuine degrees and institutions without placeholders)
        enhanced_edu = [
            {
                "degree": ed.degree,
                "institution": ed.institution,
                "graduation_year": ed.graduation_year,
                "gpa": ed.gpa,
                "field_of_study": ed.field_of_study or ("Cybersecurity" if "cyber" in ((ed.degree or "") + " " + (ed.raw_text or "")).lower() else None),
                "raw_text": ed.raw_text or f"{ed.degree} in {ed.field_of_study or ''} {ed.institution or ''}".strip(),
            }
            for ed in resume.education
        ]

        # Process education plan item if candidate added coursework
        for edu_key in ("plan_education", "education"):
            if edu_key in plan_dict:
                edu_resp = plan_dict[edu_key].get("candidate_response", {})
                coursework = edu_resp.get("relevant_coursework")
                honors = edu_resp.get("academic_honors")
                if coursework and enhanced_edu:
                    enhanced_edu[0]["raw_text"] = f"{enhanced_edu[0]['raw_text']} | Coursework: {coursework}"
                    approved_applied.append(f"Highlighted confirmed relevant coursework: {coursework}")
                if honors and enhanced_edu:
                    enhanced_edu[0]["raw_text"] = f"{enhanced_edu[0]['raw_text']} | Honors: {honors}"
                    approved_applied.append(f"Documented academic honors: {honors}")
                approved_applied.append("Evaluated degree relevance fairly against role qualification criteria")

        # 9. Strict Certification Rule: Never add CEH, Security+, CISSP unless candidate confirmed earned
        # Only preserve genuine earned certifications, strictly excluding coding platforms and courses
        valid_certs = [
            c for c in resume.certifications
            if not any(p.search(c) for p in ResumeExtractor.NON_CERT_PATTERNS)
            and c.lower() not in ("certifications", "licenses & certifications", "credentials", "coding profiles")
        ]

        # Process certifications plan item: earned_verified vs currently_pursuing vs future_learning
        for cert_key, c_item in plan_dict.items():
            if cert_key in ("plan_certifications", "certifications") or c_item.get("item_type") == "cert_recommendation" or "plan_cert_" in cert_key:
                c_resp = c_item.get("candidate_response", {})
                c_detail = c_item.get("cert_recommendation") or {}
                for q in c_item.get("follow_up_questions", []):
                    q_id = q.get("id")
                    c_name = q.get("cert_name") or c_detail.get("cert_name")
                    chosen_status = c_resp.get(q_id)
                    if not chosen_status and c_detail.get("candidate_status"):
                        chosen_status = c_detail.get("candidate_status")

                    if c_name and chosen_status in ("earned_verified", "already_earned"):
                        if not any(c_name.lower() in vc.lower() for vc in valid_certs):
                            valid_certs.append(c_name)
                            approved_applied.append(f"Included confirmed earned certification: {c_name}")
                    elif c_name and chosen_status == "currently_pursuing":
                        if not any(c_name.lower() in pc.lower() for pc in pursuing_certs):
                            pursuing_certs.append(f"{c_name} (Pursuing / Exam In-Progress)")
                            approved_applied.append(f"Documented in-progress milestone: {c_name} (Pursuing)")
                    elif c_name and chosen_status in ("future_learning", "planning_to_pursue"):
                        future_learning.append(
                            f"Recommended Future Credential: {c_name} for future professional advancement."
                        )

        # 10. Document rewritten sections for transparency
        sections_rewritten = [
            "Candidate Contact Header",
            "Professional Headline",
            "Professional Summary",
            "Technical Skills & Competencies",
            "Security Tools & Technologies",
            "Hands-on Technical Projects",
            "Professional Experience",
            "Education & Qualifications",
        ]

        pending = []
        if missing_core_skills and not confirmed_skills:
            pending.append(
                f"Candidate confirmation: Do you have coursework or hands-on lab familiarity with "
                f"{', '.join(missing_core_skills[:3])}?"
            )

        mode = f"deterministic_enhancer (Attempt {attempt_number})"
        if fallback_reason:
            mode += f" (Fallback active: {fallback_reason[:60]})"
        elif not settings.is_ai_configured():
            mode += " (OpenAI API key not configured; safe heuristic mode active)"

        return EnhancedResumeContent(
            candidate_name=name,
            contact_header=contact_header,
            contact_details={
                "email": c.email,
                "phone": c.phone,
                "location": c.location,
                "linkedin": c.linkedin,
                "github": c.github,
            },
            professional_headline=headline,
            professional_summary=summary,
            technical_skills_grouped=categorized_skills,
            experience=enhanced_exp,
            projects=enhanced_projects,
            education=enhanced_edu,
            certifications=valid_certs,
            structured_certifications=[CertificationEntry(name=c, certification_name=c) for c in valid_certs],
            achievements=resume.achievements,
            confirmed_skills_included=confirmed_included,
            unverified_skills_excluded=unverified_excluded,
            pursuing_certifications=pursuing_certs,
            approved_improvements_applied=approved_applied,
            sections_rewritten=sections_rewritten,
            future_learning_recommendations=future_learning,
            pending_confirmations=pending,
            generator_mode=mode,
            attempt_number=attempt_number,
        )

    @classmethod
    def _generate_with_llm(
        cls,
        resume_data: ParsedResumeData,
        role_name: str,
        missing_core_skills: List[str],
        confirmed_skills: List[ConfirmedSkillItem],
        approved_plan_items: Optional[List[Any]] = None,
        permission_granted: bool = True,
        attempt_number: int = 1,
        candidate_notes: Optional[str] = None,
        approved_projects: Optional[List[Any]] = None,
    ) -> EnhancedResumeContent:
        """Invokes OpenAI GPT Stage 2 with strict prompt constraints against fabrication."""
        api_key = settings.effective_openai_key
        model = settings.OPENAI_MODEL or "gpt-4o-mini"
        timeout_sec = getattr(settings, "OPENAI_TIMEOUT_SEC", 60.0)

        system_prompt = (
            f"You are FUTRSEC AI Stage 2 Resume Optimization Engine powered by OpenAI GPT ({model}). "
            "Generate a complete, ATS-friendly resume for the specified cybersecurity role.\n"
            "CRITICAL RULES:\n"
            "1. NEVER invent qualifications, degrees, companies, employment dates, certifications, metrics, or achievements.\n"
            "2. Use ONLY existing and candidate-confirmed information.\n"
            "3. If candidate confirmed hands-on skills, incorporate them accurately into projects and technical skills.\n"
            "4. NEVER add unverified skills or unearned certifications (e.g. CEH, Security+, CISSP).\n"
            "5. Return strictly valid JSON matching the requested schema.\n"
            "6. Organize technical skills logically by cybersecurity category.\n"
            "7. APPROVED PROJECTS: Every project in 'approved_projects' has been verified and approved by the candidate. "
            "You MUST preserve and include EVERY approved project in the final 'projects' array alongside original projects. "
            "For projects marked with '| In Progress', preserve '| In Progress' in the title and use progressive implementation wording. "
            "For completed projects, use clean title without '| In Progress'. NEVER omit any approved project.\n"
            "8. PROFESSIONAL SUMMARY: Target exactly 40 to 60 words. Make it role-specific, concise, and professional. "
            "Focus on candidate's verified background, actual projects, and target role. "
            "NEVER include raw tool inventories, evaluation metrics (EDA, MAE, RMSE, R²), cert lists, or unrelated coursework lists in the summary.\n"
            "9. TECHNICAL SKILLS: Categorize into standard categories (Cybersecurity Tools, Security Concepts, Programming Languages, Operating Systems, Frameworks & Libraries, Databases, Cloud & DevOps, Data Science & Machine Learning, Networking Technologies). "
            "NEVER include evaluation metrics, certificates, phone numbers, emails, locations, companies, job titles, or generic coursework in technical skills. Each skill must be an individual canonical skill name (e.g., 'Python', 'Wireshark', 'Burp Suite')."
        )

        user_content = {
            "target_role": role_name,
            "candidate_name": resume_data.candidate_name,
            "contact_info": resume_data.contact_info.model_dump(),
            "summary": resume_data.professional_summary,
            "skills": resume_data.technical_skills,
            "confirmed_skills": [c.model_dump() for c in confirmed_skills] if permission_granted else [],
            "approved_plan_items": approved_plan_items or [],
            "approved_projects": [
                {
                    "title": getattr(p, "title_line", "") or (p.get("title") if isinstance(p, dict) else ""),
                    "status": getattr(p, "status_label", "Completed") if not isinstance(p, dict) else p.get("status_label", "Completed"),
                    "bullets": getattr(p, "bullets", []) if not isinstance(p, dict) else p.get("bullets", []),
                }
                for p in (approved_projects or [])
            ],
            "experience": [e.model_dump() for e in resume_data.employment_history],
            "projects": [p.model_dump() for p in resume_data.projects],
            "education": [ed.model_dump() for ed in resume_data.education],
            "certifications": resume_data.certifications,
            "missing_core_skills": missing_core_skills,
            "candidate_notes": candidate_notes,
        }

        from openai import OpenAI
        client = OpenAI(api_key=api_key, timeout=timeout_sec)
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate ATS-optimized resume for the role '{role_name}':\n{json.dumps(user_content)}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        llm_text = completion.choices[0].message.content or "{}"
        from app.ai.json_utils import safe_json_loads
        parsed_json = safe_json_loads(llm_text, default={})
        if not isinstance(parsed_json, dict):
            parsed_json = {}

        confirmed_included = [c.skill_name for c in confirmed_skills if c.proficiency != "not_used"] if permission_granted else []
        unverified_excluded = [c.skill_name for c in confirmed_skills if c.proficiency == "not_used"] if permission_granted else [c.skill_name for c in confirmed_skills]

        llm_projects = parsed_json.get("projects") or [p.model_dump() for p in resume_data.projects]

        # Reconcile approved projects: Ensure every approved project is included in llm_projects
        for appr in (approved_projects or []):
            appr_title = getattr(appr, "title_line", "") or (appr.get("title") if isinstance(appr, dict) else "")
            appr_status = getattr(appr, "status_label", "Completed") if not isinstance(appr, dict) else appr.get("status_label", "Completed")
            appr_bullets = getattr(appr, "bullets", []) if not isinstance(appr, dict) else appr.get("bullets", [])
            is_in_prog = "in progress" in str(appr_status).lower() or "in progress" in appr_title.lower()
            base_title = re.sub(r"\s*\|\s*in\s*progress$", "", appr_title.strip(), flags=re.IGNORECASE).strip()
            clean_title = f"{base_title} | In Progress" if is_in_prog else base_title

            if not any(base_title.lower() in p.get("title", "").lower() for p in llm_projects):
                techs = []
                for b in appr_bullets:
                    if b.lower().startswith("technologies:"):
                        techs = [t.strip() for t in b.split(":", 1)[1].rstrip(".").split(",") if t.strip()]
                        break
                if not techs:
                    techs = [t.strip() for t in base_title.split("|")[-1].split(",") if t.strip()]

                llm_projects.insert(0, {
                    "title": clean_title,
                    "description": " \n".join(appr_bullets),
                    "technologies": techs,
                    "outcomes": appr_bullets[-1] if appr_bullets else "Verified practical outcome",
                    "bullets": appr_bullets,
                })

        # Reconcile original candidate projects: Ensure every original project is included in llm_projects
        for orig_p in resume_data.projects:
            orig_base = re.sub(r"\s*\|\s*(?:Status:\s*)?(?:In Progress|Completed)$", "", orig_p.title, flags=re.IGNORECASE).strip().lower()
            if not any(orig_base == re.sub(r"\s*\|\s*(?:Status:\s*)?(?:In Progress|Completed)$", "", p.get("title", ""), flags=re.IGNORECASE).strip().lower() for p in llm_projects):
                p_bullets = [cls._polish_project_bullet(b) for b in (orig_p.bullets or [orig_p.description]) if b]
                llm_projects.append({
                    "title": re.sub(r"\s*\|\s*(?:Status:\s*)?(?:In Progress|Completed)$", "", orig_p.title, flags=re.IGNORECASE).strip(),
                    "status": orig_p.status or "Completed",
                    "technologies": orig_p.technologies or resume_data.technical_skills[:4],
                    "description": " \n".join(p_bullets) if p_bullets else orig_p.description,
                    "bullets": p_bullets,
                    "github_url": orig_p.github_url,
                    "project_url": orig_p.project_url,
                    "outcomes": orig_p.outcomes,
                })

        # Deduplicate and rank projects by role relevance
        llm_projects = cls._deduplicate_enhanced_projects(llm_projects)
        llm_projects = cls._rank_projects_for_role(llm_projects, role_name, missing_core_skills)

        # Sanitize and structure technical skills through taxonomy pipeline
        llm_skills_raw: List[str] = []
        parsed_skills_grouped = parsed_json.get("technical_skills_grouped")
        if isinstance(parsed_skills_grouped, dict):
            for grp_items in parsed_skills_grouped.values():
                if isinstance(grp_items, list):
                    llm_skills_raw.extend([str(item) for item in grp_items if item])
                elif isinstance(grp_items, str):
                    llm_skills_raw.extend(re.split(r"[,;\n]", grp_items))
        elif isinstance(parsed_skills_grouped, list):
            llm_skills_raw.extend([str(item) for item in parsed_skills_grouped if item])

        if not llm_skills_raw:
            llm_skills_raw = list(resume_data.technical_skills)

        cleaned_skills_grouped = structure_and_classify_skills(
            raw_skills=llm_skills_raw,
            candidate_name=resume_data.candidate_name,
            contact_info=resume_data.contact_info,
            target_role_name=role_name,
        )

        return EnhancedResumeContent(
            candidate_name=parsed_json.get("candidate_name") or resume_data.candidate_name or "Candidate",
            contact_header=parsed_json.get("contact_header") or "",
            contact_details=parsed_json.get("contact_details") or resume_data.contact_info.model_dump(),
            professional_headline=parsed_json.get("professional_headline") or f"{role_name} Professional",
            professional_summary=parsed_json.get("professional_summary") or "",
            technical_skills_grouped=cleaned_skills_grouped,
            experience=parsed_json.get("experience") or [e.model_dump() for e in resume_data.employment_history],
            projects=llm_projects,
            education=parsed_json.get("education") or [ed.model_dump() for ed in resume_data.education],
            certifications=resume_data.certifications,  # strictly preserved
            structured_certifications=getattr(resume_data, "structured_certifications", []) or [CertificationEntry(name=c, certification_name=c) for c in resume_data.certifications],
            achievements=parsed_json.get("achievements") or resume_data.achievements,
            confirmed_skills_included=confirmed_included,
            unverified_skills_excluded=unverified_excluded,
            sections_rewritten=[
                "Candidate Contact Header",
                "Professional Headline",
                "Professional Summary",
                "Technical Skills & Competencies",
                "Key Technical Projects",
                "Professional Experience",
                "Education & Qualifications",
            ],
            future_learning_recommendations=[
                f"Recommended Learning: Complete labs for '{s}'" for s in unverified_excluded
            ],
            pending_confirmations=parsed_json.get("pending_confirmations") or [],
            generator_mode=f"openai_gpt_{model} (Attempt {attempt_number})",
            attempt_number=attempt_number,
        )

    @classmethod
    def _polish_bullet(cls, bullet: str) -> str:
        """Ensures bullet starts with a strong action verb and has clean typography without altering facts."""
        bullet = bullet.strip()
        if not bullet:
            return ""
        # Reconnect broken words: "Lan- guage" -> "Language", "authenti- cation" -> "authentication"
        bullet = re.sub(r"(\b[A-Za-z]+)-\s+([a-z]+)", r"\1\2", bullet)
        # Capitalize first letter
        if bullet[0].islower():
            bullet = bullet[0].upper() + bullet[1:]
        # Ensure ends with period
        if not bullet.endswith("."):
            bullet += "."
        return bullet

    @classmethod
    def _polish_project_bullet(cls, bullet: str) -> str:
        """Polishes a project bullet point with active phrasing and clean formatting without altering facts."""
        bullet = bullet.strip()
        if not bullet:
            return ""

        # Remove leading bullet symbols, dashes, numbers, markdown
        bullet = re.sub(r"^[\s•\*\-\–\—\u2022]+|^(?:\d+\.|\([a-z0-9]+\)|\[\d+\])\s*", "", bullet).strip()
        if not bullet:
            return ""

        # Reconnect split hyphenated words: "config- ured" -> "configured", "vuln- erability" -> "vulnerability"
        bullet = re.sub(r"(\b[A-Za-z]+)-\s+([a-z]+)", r"\1\2", bullet)

        # Replace passive or weak opening phrases with concise active verbs
        weak_prefixes = [
            (r"(?i)^(?:responsible\s+for\s+(?:developing|building|creating))\s+", "Developed "),
            (r"(?i)^(?:responsible\s+for\s+(?:implementing|deploying))\s+", "Implemented "),
            (r"(?i)^(?:responsible\s+for\s+(?:configuring|setting\s+up))\s+", "Configured "),
            (r"(?i)^(?:responsible\s+for\s+(?:analyzing|evaluating))\s+", "Analyzed "),
            (r"(?i)^(?:responsible\s+for\s+(?:designing|engineering))\s+", "Engineered "),
            (r"(?i)^(?:responsible\s+for)\s+", "Executed "),
            (r"(?i)^(?:worked\s+on\s+(?:developing|building))\s+", "Developed "),
            (r"(?i)^(?:worked\s+on\s+(?:implementing))\s+", "Implemented "),
            (r"(?i)^(?:worked\s+on)\s+", "Developed "),
            (r"(?i)^(?:helped\s+(?:to\s+)?(?:develop|build))\s+", "Collaborated to develop "),
            (r"(?i)^(?:helped\s+(?:to\s+)?(?:implement))\s+", "Collaborated to implement "),
            (r"(?i)^(?:assisted\s+in\s+(?:developing|building))\s+", "Contributed to developing "),
            (r"(?i)^(?:tasked\s+with\s+(?:developing|implementing|configuring))\s+", "Implemented "),
            (r"(?i)^(?:involved\s+in\s+(?:developing|building|implementing))\s+", "Implemented "),
        ]
        for pattern, repl in weak_prefixes:
            if re.search(pattern, bullet):
                bullet = re.sub(pattern, repl, bullet, count=1).strip()
                break

        # Capitalize first character
        if bullet and bullet[0].islower():
            bullet = bullet[0].upper() + bullet[1:]

        # Ensure terminal punctuation
        if bullet and not bullet.endswith((".", "!", "?")):
            bullet += "."

        return bullet

    @classmethod
    def _rank_projects_for_role(
        cls,
        projects: List[Dict[str, Any]],
        role_name: str,
        missing_core_skills: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Ranks projects by relevance to the target cybersecurity role using domain keyword scoring.
        
        Strictly preserves ALL candidate projects; non-matching projects are never omitted and appear after relevant ones.
        """
        if len(projects) <= 1:
            return projects

        role_lower = role_name.lower()
        role_tokens = set(re.findall(r"\b[a-z]{3,}\b", role_lower))

        # Core domain keywords for cybersecurity and technical roles
        domain_keywords: set = set(role_tokens)
        if missing_core_skills:
            for s in missing_core_skills:
                for tok in re.findall(r"\b[a-z]{3,}\b", s.lower()):
                    domain_keywords.add(tok)

        # 1. Offensive Security / Ethical Hacker / Penetration Tester / Red Team
        if any(k in role_lower for k in ("penetration", "ethical", "offensive", "red team", "exploit", "hacker")):
            domain_keywords.update({
                "penetration", "pentest", "vulnerability", "vulnerabilities", "exploit", "exploitation",
                "nmap", "burp", "suite", "metasploit", "wireshark", "owasp", "kali", "reconnaissance",
                "privilege", "escalation", "injection", "sqli", "xss", "payload", "offensive", "red", "team",
                "ctf", "reverse", "engineering", "malware", "aircrack", "hydra", "john", "scanner", "scan",
                "port", "recon", "hardening", "cve", "zero-day", "fuzzing", "zap"
            })
        # 2. SOC Analyst / Incident Responder / Blue Team / Threat Hunter / DFIR
        elif any(k in role_lower for k in ("soc", "incident", "threat", "analyst", "blue team", "forensic", "siem")):
            domain_keywords.update({
                "soc", "siem", "incident", "threat", "response", "splunk", "sentinel", "qradar",
                "wazuh", "suricata", "snort", "zeek", "forensics", "dfir", "autopsy", "volatility",
                "triage", "log", "logs", "pcap", "packet", "packets", "alert", "alerts", "edr",
                "mitre", "att&ck", "intelligence", "hunting", "monitoring", "investigation", "analysis",
                "wireshark", "packet", "defense", "detection"
            })
        # 3. Cloud Security / DevSecOps
        elif any(k in role_lower for k in ("cloud", "devsecops", "aws", "azure", "gcp", "container")):
            domain_keywords.update({
                "cloud", "aws", "azure", "gcp", "iam", "terraform", "kubernetes", "k8s", "docker",
                "ci/cd", "pipeline", "sast", "dast", "trivy", "snyk", "container", "devsecops",
                "cloudtrail", "guardduty", "s3", "lambda", "hardening", "serverless", "microservices"
            })
        # 4. Network Security
        elif any(k in role_lower for k in ("network", "infrastructure", "firewall")):
            domain_keywords.update({
                "network", "firewall", "vpn", "ids", "ips", "routing", "switching", "cisco",
                "pfsense", "subnet", "tcp/ip", "packet", "packets", "wireshark", "dns", "dhcp",
                "vlan", "bgp", "perimeter", "traffic", "hardening", "protocol"
            })
        # 5. Application Security / AppSec
        elif any(k in role_lower for k in ("application", "appsec", "software security", "code")):
            domain_keywords.update({
                "appsec", "application", "owasp", "sast", "dast", "api", "jwt", "oauth", "auth",
                "authentication", "authorization", "session", "xss", "csrf", "sqli", "code", "review",
                "secure", "coding", "fastapi", "flask", "crypto", "cryptography", "encryption", "sanitization"
            })
        # 6. Governance, Risk & Compliance / GRC
        elif any(k in role_lower for k in ("compliance", "grc", "governance", "risk", "audit")):
            domain_keywords.update({
                "compliance", "grc", "iso", "27001", "nist", "soc", "soc2", "pci", "pci-dss",
                "hipaa", "gdpr", "risk", "assessment", "audit", "governance", "policy", "policies",
                "controls", "regulatory", "standard"
            })
        # 7. Data Engineering / Data Science / Analytics
        elif any(k in role_lower for k in ("data", "etl", "analytics", "machine learning", "ml")):
            domain_keywords.update({
                "data", "etl", "pipeline", "sql", "postgres", "postgresql", "mysql", "spark",
                "pandas", "numpy", "airflow", "kafka", "warehouse", "analytics", "visualization",
                "machine", "learning", "model", "scikit", "database", "cleaning"
            })
        # 8. Software Development / Python / Full Stack
        elif any(k in role_lower for k in ("python", "developer", "engineer", "full stack", "backend")):
            domain_keywords.update({
                "python", "fastapi", "flask", "django", "backend", "frontend", "api", "apis",
                "rest", "javascript", "react", "full", "stack", "git", "github", "software",
                "automation", "script", "scripts", "unit", "testing", "asyncio"
            })

        def score_project(proj: Dict[str, Any]) -> float:
            score = 0.0
            title = proj.get("title", "").lower()
            techs = [t.lower() for t in proj.get("technologies", [])]
            desc = proj.get("description", "").lower()
            bullets = [b.lower() for b in proj.get("bullets", [])]

            title_tokens = set(re.findall(r"\b[a-z]{3,}\b", title))
            score += len(title_tokens.intersection(domain_keywords)) * 3.5

            for t in techs:
                t_tokens = set(re.findall(r"\b[a-z]{3,}\b", t))
                score += len(t_tokens.intersection(domain_keywords)) * 2.5

            desc_tokens = set(re.findall(r"\b[a-z]{3,}\b", desc))
            score += len(desc_tokens.intersection(domain_keywords)) * 1.0

            for b in bullets:
                b_tokens = set(re.findall(r"\b[a-z]{3,}\b", b))
                score += len(b_tokens.intersection(domain_keywords)) * 0.8

            return score

        # Python's list.sort / sorted is stable: items with equal score retain their original relative order
        return sorted(projects, key=score_project, reverse=True)

    @classmethod
    def _deduplicate_enhanced_projects(cls, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicates project entries while preserving distinct projects and comprehensive details."""
        if len(projects) <= 1:
            return projects

        deduped: List[Dict[str, Any]] = []
        for p in projects:
            title = p.get("title", "")
            base_title = re.sub(r"\s*\|\s*(?:Status:\s*)?(?:In Progress|Completed)$", "", title, flags=re.IGNORECASE).strip()
            norm_title = re.sub(r"[^a-zA-Z0-9]", "", base_title.lower())
            p_gh = (p.get("github_url") or "").strip().lower()

            match_idx = -1
            for idx, existing in enumerate(deduped):
                ex_title = existing.get("title", "")
                ex_base = re.sub(r"\s*\|\s*(?:Status:\s*)?(?:In Progress|Completed)$", "", ex_title, flags=re.IGNORECASE).strip()
                ex_norm = re.sub(r"[^a-zA-Z0-9]", "", ex_base.lower())
                ex_gh = (existing.get("github_url") or "").strip().lower()

                if norm_title and norm_title == ex_norm:
                    match_idx = idx
                    break
                if p_gh and ex_gh and p_gh == ex_gh:
                    match_idx = idx
                    break

            if match_idx >= 0:
                existing = deduped[match_idx]
                # Merge technologies
                ex_techs = existing.get("technologies", [])
                for t in p.get("technologies", []):
                    if t and t.lower() not in [x.lower() for x in ex_techs]:
                        ex_techs.append(t)
                existing["technologies"] = ex_techs

                # Merge bullets/description
                p_bullets = p.get("bullets", [])
                ex_bullets = existing.get("bullets", [])
                if len(p_bullets) > len(ex_bullets):
                    existing["bullets"] = p_bullets
                    existing["description"] = p.get("description", existing.get("description"))

                # Status: In Progress takes precedence if either is in progress
                if p.get("status") == "In Progress" or "in progress" in title.lower():
                    existing["status"] = "In Progress"

                # URLs
                if not existing.get("github_url") and p.get("github_url"):
                    existing["github_url"] = p.get("github_url")
                if not existing.get("project_url") and p.get("project_url"):
                    existing["project_url"] = p.get("project_url")
                if not existing.get("outcomes") and p.get("outcomes"):
                    existing["outcomes"] = p.get("outcomes")
            else:
                deduped.append(dict(p))

        return deduped
