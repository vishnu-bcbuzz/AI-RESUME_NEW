"""Approval-based resume improvement plan generator for FUTRSEC.

Identifies weak scoring categories (<80% or missing key evidence) across:
- Technical Skills
- Projects
- Education (role-specific evaluation, no arbitrary arts deduction)
- Tools & Certifications (separated: earned vs confirmed omitted vs pursuing vs future learning)
- Professional Summary & Career Objective (role-tailored, aligned with verified background)
- Work Experience & Internships (security duties, active verbs, never invent jobs/dates)
- Relevant Achievements & Supporting Evidence

Evaluates role-specific requirements directly from Neon PostgreSQL (job_roles, role_skills,
role_requirements, scoring_criteria). For every weak category, explains:
1. Current score and maximum possible score
2. What is missing or insufficiently demonstrated
3. Which job requirements are affected
4. Which specific improvements are recommended
5. What information the candidate needs to provide
6. Which resume sections should be updated
7. Why the recommendation is relevant to the selected job role
8. Whether candidate needs to confirm existing experience, improve presentation, or acquire new skills

Generates individual skill recommendation cards, practical project templates,
and certification recommendation cards organized into High-Priority, Medium-Priority,
and Additional Enhancements.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.resume.extractor import ParsedResumeData
from app.scoring.matcher import EvidenceMatchReport
from app.scoring.engine import ATSScoreResult
from app.projects.plan_generator import PrimaryProjectPlanGenerator, ProjectImplementationPlan
from app.projects.plan_renderer import ProjectPlanDocumentRenderer


class WeakCategoryEvaluation(BaseModel):
    """Detailed evaluation of an existing scoring category against role configuration."""
    category_name: str
    category_key: str
    current_score: float
    max_score: float
    percentage: float
    is_weak: bool
    what_is_missing: str
    affected_job_requirements: List[str] = Field(default_factory=list)
    specific_improvements: List[str] = Field(default_factory=list)
    required_candidate_info: str
    resume_sections_to_update: List[str] = Field(default_factory=list)
    role_relevance_reason: str
    action_nature: str  # 'confirm_existing' | 'improve_presentation' | 'acquire_new_skills'
    confirmation_needed: bool = True
    recommended_next_action: str = ""


class SkillRecommendationDetail(BaseModel):
    """Detailed structure for an individual technical skill card."""
    skill_name: str
    requirement_classification: str  # 'mandatory' | 'preferred' | 'additional'
    current_evidence: str
    importance_for_role: str
    gap_explanation: str
    suggested_resume_section: str
    candidate_confirmation_question: str
    recommended_action: str
    if_confirmed: str
    if_basic_exposure: str
    if_never_used: str
    available_actions: List[str] = Field(
        default_factory=lambda: [
            "Confirm Existing Experience",
            "Provide More Details",
            "Recommend Learning Resources",
            "Skip This Recommendation",
        ]
    )
    candidate_action_selected: Optional[str] = None
    skill_state: str = "needs_evidence"  # 'demonstrated' | 'confirmed_needs_representation' | 'needs_evidence' | 'not_possessed' | 'recommended_future_learning'
    learning_resources: List[str] = Field(default_factory=list)


class PracticalProjectTemplate(BaseModel):
    """Structured practical project recommendation for weak project category."""
    project_title: str
    target_role: str
    level: str = "Intermediate"  # 'Beginner' | 'Intermediate' | 'Advanced'
    skills_demonstrated: List[str] = Field(default_factory=list)
    proposed_technologies: List[str] = Field(default_factory=list)
    project_objective: str
    suggested_implementation_tasks: List[str] = Field(default_factory=list)
    expected_deliverables: str
    suggested_resume_bullet: str
    is_future_project: bool = True
    candidate_has_completed_similar: Optional[bool] = None
    plan_id: Optional[str] = None
    docx_download_url: Optional[str] = None
    pdf_download_url: Optional[str] = None
    weaknesses_addressed: List[str] = Field(default_factory=list)
    project_workflow: Optional[List[Dict[str, Any]]] = None


class CertificationRecommendationDetail(BaseModel):
    """Structured certification recommendation."""
    cert_name: str
    relevance_to_role: str
    db_classification: str = "recommended"  # 'required' | 'preferred' | 'recommended'
    capability_demonstrated: str
    candidate_status: str = "not_interested"  # 'already_earned' | 'currently_pursuing' | 'planning_to_pursue' | 'not_interested'
    recommended_next_action: str
    verification_details: Optional[str] = None


class ImprovementPlanItem(BaseModel):
    """Individual category or specific item proposed improvement with candidate approval controls."""
    item_id: str
    priority: str = "medium"  # 'high' | 'medium' | 'low'
    item_type: str = "category_overview"  # 'category_overview' | 'skill_card' | 'project_recommendation' | 'cert_recommendation' | 'section_polish'
    category: str
    category_key: str
    title: str = ""
    current_score: Optional[float] = None
    max_score: Optional[float] = None
    current_issue: str
    recommended_change: str
    relevance_reason: str
    required_info: str
    expected_improvement: str
    action_type: str
    status: str = "pending"  # 'pending', 'approved', 'edited', 'skipped'
    is_weak_category: bool = True
    action_nature: str = "confirm_existing"  # 'confirm_existing' | 'improve_presentation' | 'acquire_new_skills'
    affected_job_requirements: List[str] = Field(default_factory=list)
    resume_sections_to_update: List[str] = Field(default_factory=list)
    skill_details: Optional[SkillRecommendationDetail] = None
    project_recommendation: Optional[PracticalProjectTemplate] = None
    cert_recommendation: Optional[CertificationRecommendationDetail] = None
    follow_up_questions: List[Dict[str, Any]] = Field(default_factory=list)
    candidate_response: Dict[str, Any] = Field(default_factory=dict)


class ResumeImprovementPlan(BaseModel):
    """Structured, personalized improvement plan for candidates below the threshold."""
    initial_score: float
    threshold: float = 80.0
    meets_threshold: bool
    role_name: str = ""
    weak_categories: List[str] = Field(default_factory=list)
    category_evaluations: List[WeakCategoryEvaluation] = Field(default_factory=list)
    high_priority_items: List[ImprovementPlanItem] = Field(default_factory=list)
    medium_priority_items: List[ImprovementPlanItem] = Field(default_factory=list)
    additional_enhancements: List[ImprovementPlanItem] = Field(default_factory=list)
    items: List[ImprovementPlanItem] = Field(default_factory=list)
    summary_advice: str
    primary_project_plan: Optional[Dict[str, Any]] = None


class ImprovementPlanGenerator:
    """Evaluates category-level scores, evidence, and database requirements to build a personalized plan."""

    # Role-specific certification benchmarks
    ROLE_CERT_BENCHMARKS = {
        "penetration": ["OSCP", "CEH", "CompTIA PenTest+", "eJPT"],
        "ethical hacker": ["CEH", "CompTIA PenTest+", "OSCP", "eJPT"],
        "security analyst": ["CompTIA CySA+", "CompTIA Security+", "Microsoft SC-200"],
        "soc": ["CompTIA CySA+", "BTL1", "Splunk Certified Core User", "CompTIA Security+"],
        "incident response": ["GCIH", "EC-Council ECIH", "CompTIA CySA+"],
        "cloud security": ["AWS Certified Security - Specialty", "CCSP", "Azure AZ-500"],
        "security engineer": ["CISSP", "CSSLP", "CompTIA Security+"],
        "compliance": ["CISA", "CRISC", "ISO 27001 Lead Auditor"],
        "application security": ["CSSLP", "GIAC GWEB", "CASE Java/CASE .NET"],
    }

    # Curated learning resources for popular cybersecurity skills
    LEARNING_RESOURCES = {
        "burp suite": [
            "PortSwigger Web Security Academy (Free interactive labs & tutorials)",
            "TryHackMe: Burp Suite Basics, Repeater & Intruder modules",
        ],
        "nmap": [
            "Nmap Network Scanning official guide by Gordon Lyon",
            "TryHackMe: Nmap Room & VulnHub CTF practice",
        ],
        "owasp top 10": [
            "OWASP Foundation Project Documentation (owasp.org)",
            "OWASP Juice Shop & DVWA hands-on vulnerable web app labs",
        ],
        "linux": [
            "OverTheWire: Bandit Wargames (Hands-on Linux command line)",
            "Linux Journey (linuxjourney.com) free systems fundamentals",
        ],
        "kali linux": [
            "Kali Linux Revealed official training book & labs (kali.org)",
            "Offensive Security: Proving Grounds Play labs",
        ],
        "metasploit": [
            "Metasploit Unleashed free ethical hacking course by Offensive Security",
            "TryHackMe: Metasploit Intro & Exploitation rooms",
        ],
        "splunk": [
            "Splunk Fundamentals 1 (Free foundational training)",
            "CyberDefenders: Boss of the SOC (BOTS) SIEM investigation challenges",
        ],
        "snort": [
            "Snort 3 User Manual & Rule Writing Guide (snort.org)",
            "TryHackMe: Snort Rule Writing & Intrusion Detection Lab",
        ],
        "wireshark": [
            "Wireshark Network Analysis by Laura Chappell",
            "Malware-Traffic-Analysis.net packet capture practice scenarios",
        ],
        "python": [
            "Violent Python: A Cookbook for Hackers & Forensic Analysts",
            "Automate the Boring Stuff with Python for Security Automation",
        ],
        "active directory security": [
            "TryHackMe: Attacking & Defending Active Directory",
            "BloodHound & Impacket lab walkthroughs on HackTheBox",
        ],
        "api security": [
            "OWASP API Security Top 10 Documentation",
            "APIsec University (Free certified API security courses)",
        ],
        "siem": [
            "CyberDefenders SIEM Analyst training pathway",
            "Splunk & Elastic Security Hands-On Workshops",
        ],
        "incident response": [
            "SANS Digital Forensics and Incident Response (DFIR) Cheat Sheets",
            "Autopsy & Volatility 3 Memory Forensics case studies",
        ],
    }

    @classmethod
    def generate_plan(
        cls,
        resume_data: ParsedResumeData,
        match_report: EvidenceMatchReport,
        score_result: ATSScoreResult,
        role_requirements: List[Dict[str, Any]],
        role_name: str,
        role_skills: Optional[List[Dict[str, Any]]] = None,
        scoring_criteria: Optional[List[Dict[str, Any]]] = None,
    ) -> ResumeImprovementPlan:
        """Constructs an approval-based improvement plan covering all weak categories."""
        role_skills = role_skills or []
        scoring_criteria = scoring_criteria or []

        # Find category scores for quick lookup
        cat_scores_by_name = {c.category_name: c for c in score_result.category_scores}

        # Extract criteria weights
        weights_map = {
            "Technical Skills": 40.0,
            "Projects": 25.0,
            "Education": 15.0,
            "Tools & Certifications": 15.0,
            "Career Objective": 5.0,
        }
        for crit in scoring_criteria:
            c_cat = crit.get("category")
            if c_cat in weights_map:
                weights_map[c_cat] = float(crit.get("weight", weights_map[c_cat]))

        weak_categories_list: List[str] = []
        category_evaluations: List[WeakCategoryEvaluation] = []

        high_priority_items: List[ImprovementPlanItem] = []
        medium_priority_items: List[ImprovementPlanItem] = []
        additional_enhancements: List[ImprovementPlanItem] = []

        # Build role requirements textual mapping
        edu_reqs = [
            r["requirement_description"]
            for r in role_requirements
            if r.get("requirement_type") == "education"
        ]
        cert_reqs = [
            r["requirement_description"]
            for r in role_requirements
            if r.get("requirement_type") == "certification"
        ]
        exp_reqs = [
            r["requirement_description"]
            for r in role_requirements
            if r.get("requirement_type") in ("experience", "work_experience")
        ]
        gen_reqs = [
            r["requirement_description"]
            for r in role_requirements
            if r.get("requirement_type") not in ("education", "certification", "experience")
        ]

        # ---------------------------------------------------------------------
        # 1. EVALUATION: Technical Skills
        # ---------------------------------------------------------------------
        tech_score = cat_scores_by_name.get("Technical Skills")
        tech_earned = tech_score.score_earned if tech_score else 0.0
        tech_max = weights_map["Technical Skills"]
        tech_pct = (tech_earned / tech_max * 100.0) if tech_max > 0 else 0.0

        missing_core = [u.skill_name for u in match_report.unmatched_skills if u.importance == "core"]
        missing_pref = [u.skill_name for u in match_report.unmatched_skills if u.importance == "preferred"]
        missing_add = [u.skill_name for u in match_report.unmatched_skills if u.importance == "additional"]

        is_tech_weak = tech_pct < 80.0 or len(missing_core) > 0
        if is_tech_weak:
            weak_categories_list.append("Technical Skills")

        tech_affected = [f"Core skill requirement: {s}" for s in missing_core[:4]]
        if not tech_affected:
            tech_affected = [f"Preferred skill requirement: {s}" for s in missing_pref[:3]]

        tech_eval = WeakCategoryEvaluation(
            category_name="Technical Skills",
            category_key="technical_skills",
            current_score=round(tech_earned, 1),
            max_score=round(tech_max, 1),
            percentage=round(tech_pct, 1),
            is_weak=is_tech_weak,
            what_is_missing=(
                f"{len(missing_core)} mandatory core skill(s) ({', '.join(missing_core[:4]) if missing_core else 'None'}) "
                f"and {len(missing_pref)} preferred skill(s) lack substantive evidence in the uploaded resume."
            ),
            affected_job_requirements=tech_affected or ["Demonstrated competency in core role technical skills."],
            specific_improvements=[
                "Confirm hands-on exposure to missing core technical skills used in projects, home labs, or coursework.",
                "Differentiate practical hands-on capability from introductory coursework or basic familiarity.",
                "Retain skills you do not possess as personal future learning recommendations rather than inventing qualifications.",
            ],
            required_candidate_info=(
                "Confirm your factual proficiency (Beginner, Intermediate, Advanced, or No Experience Yet) and the context for each skill."
            ),
            resume_sections_to_update=["Technical Skills", "Projects"],
            role_relevance_reason=(
                f"Hiring teams for {role_name} evaluate direct proof of essential tools and concepts before advancing candidates."
            ),
            action_nature="confirm_existing" if (missing_core or missing_pref) else "improve_presentation",
            confirmation_needed=True,
            recommended_next_action="Confirm your factual proficiency level (Beginner, Intermediate, Advanced, or No Experience Yet) for core skills.",
        )
        category_evaluations.append(tech_eval)

        # ---------------------------------------------------------------------
        # 2. EVALUATION: Projects
        # ---------------------------------------------------------------------
        proj_score = cat_scores_by_name.get("Projects")
        proj_earned = proj_score.score_earned if proj_score else 0.0
        proj_max = weights_map["Projects"]
        proj_pct = (proj_earned / proj_max * 100.0) if proj_max > 0 else 0.0

        is_proj_weak = proj_pct < 80.0 or len(resume_data.projects) < 2
        if is_proj_weak:
            weak_categories_list.append("Projects")

        proj_eval = WeakCategoryEvaluation(
            category_name="Projects",
            category_key="projects",
            current_score=round(proj_earned, 1),
            max_score=round(proj_max, 1),
            percentage=round(proj_pct, 1),
            is_weak=is_proj_weak,
            what_is_missing=(
                f"Resume contains {len(resume_data.projects)} project(s). Evaluators expect detailed practical "
                f"implementations demonstrating tools, methodologies, and verifiable security deliverables."
            ),
            affected_job_requirements=[
                f"Practical implementation evidence demonstrating {role_name} competencies.",
                "Verifiable hands-on security deliverables and tool configurations.",
            ],
            specific_improvements=[
                "Review the primary project recommendation and follow the step-by-step implementation plan.",
                "Structure descriptions with Project Objective, Personal Contribution, Technologies Used, and Verified Results.",
                "Reference role-relevant security frameworks (OWASP, MITRE ATT&CK, NIST) where applicable.",
            ],
            required_candidate_info=(
                "Project title, specific tools configured, your personal contribution, and verifiable outcomes."
            ),
            resume_sections_to_update=["Projects", "Technical Skills"],
            role_relevance_reason=(
                f"Hands-on project deliverables provide concrete evidence that you can perform {role_name} responsibilities independently."
            ),
            action_nature="confirm_existing" if len(resume_data.projects) < 2 else "improve_presentation",
            confirmation_needed=True,
            recommended_next_action="Download the primary project implementation plan and submit completed project deliverables for review.",
        )
        category_evaluations.append(proj_eval)

        # ---------------------------------------------------------------------
        # 3. EVALUATION: Education
        # ---------------------------------------------------------------------
        edu_score = cat_scores_by_name.get("Education")
        edu_earned = edu_score.score_earned if edu_score else 0.0
        edu_max = weights_map["Education"]
        edu_pct = (edu_earned / edu_max * 100.0) if edu_max > 0 else 0.0

        is_edu_weak = edu_pct < 80.0
        if is_edu_weak:
            weak_categories_list.append("Education")

        edu_desc_list = [f"{e.degree} ({e.institution})" for e in resume_data.education if e.degree]
        edu_eval = WeakCategoryEvaluation(
            category_name="Education",
            category_key="education",
            current_score=round(edu_earned, 1),
            max_score=round(edu_max, 1),
            percentage=round(edu_pct, 1),
            is_weak=is_edu_weak,
            what_is_missing=(
                f"Documented education: {', '.join(edu_desc_list) if edu_desc_list else 'No formal degree documented'}. "
                f"Needs clear presentation of relevant coursework, security modules, or academic achievements."
            ),
            affected_job_requirements=edu_reqs or [
                "Education evaluated fairly per role criteria; engineering, IT, computing, and non-engineering backgrounds are eligible."
            ],
            specific_improvements=[
                "Highlight relevant technical and security coursework (e.g. Networks, Cryptography, Systems Security).",
                "Include academic honors, dean's list, or relevant capstone topics if applicable.",
                "Ensure degree presentation adheres to transparent scoring policy without unverified requirements.",
            ],
            required_candidate_info="Relevant coursework modules, academic capstone topic, or honors.",
            resume_sections_to_update=["Education"],
            role_relevance_reason=(
                "Validates foundational academic qualifications and theoretical readiness for technical roles."
            ),
            action_nature="improve_presentation",
            confirmation_needed=False,
            recommended_next_action="Incorporate relevant coursework, security lab modules, or capstone details into your education section.",
        )
        category_evaluations.append(edu_eval)

        # ---------------------------------------------------------------------
        # 4. EVALUATION: Tools and Certifications
        # ---------------------------------------------------------------------
        tools_score = cat_scores_by_name.get("Tools & Certifications")
        tools_earned = tools_score.score_earned if tools_score else 0.0
        tools_max = weights_map["Tools & Certifications"]
        tools_pct = (tools_earned / tools_max * 100.0) if tools_max > 0 else 0.0

        held_certs = resume_data.certifications
        is_tools_weak = tools_pct < 80.0 or len(held_certs) == 0
        if is_tools_weak:
            weak_categories_list.append("Tools & Certifications")

        role_lower = role_name.lower()
        benchmarks: List[str] = []
        for k, v in cls.ROLE_CERT_BENCHMARKS.items():
            if k in role_lower:
                benchmarks.extend(v)
        if not benchmarks:
            benchmarks = ["CompTIA Security+", "CEH", "CompTIA CySA+"]

        unique_benchmarks: List[str] = []
        for b in benchmarks:
            if b not in unique_benchmarks:
                unique_benchmarks.append(b)

        tools_eval = WeakCategoryEvaluation(
            category_name="Tools and Certifications",
            category_key="tools_certs",
            current_score=round(tools_earned, 1),
            max_score=round(tools_max, 1),
            percentage=round(tools_pct, 1),
            is_weak=is_tools_weak,
            what_is_missing=(
                f"Verified credentials documented: {', '.join(held_certs) if held_certs else 'None'}. "
                f"Role benchmarks typically look for credentials such as {', '.join(unique_benchmarks[:3])}."
            ),
            affected_job_requirements=cert_reqs or [
                f"Industry certifications validating standardized technical knowledge for {role_name}."
            ],
            specific_improvements=[
                "Confirm if you have already earned any omitted cybersecurity credentials.",
                "Accurately document in-progress study under 'Pursuing Certifications' without misrepresenting status.",
                "Retain recommended credentials as future career milestones without claiming unearned certifications.",
            ],
            required_candidate_info=(
                "Certification status for relevant credentials (Already Earned, Currently Pursuing, Planning to Pursue, or Not Interested)."
            ),
            resume_sections_to_update=["Certifications", "Pursuing Certifications"],
            role_relevance_reason=(
                "Standardized certifications signal verified baseline competencies and professional commitment to hiring managers."
            ),
            action_nature="confirm_existing" if held_certs else "acquire_new_skills",
            confirmation_needed=True,
            recommended_next_action="Confirm existing earned certifications or specify active study under Pursuing Certifications.",
        )
        category_evaluations.append(tools_eval)

        # ---------------------------------------------------------------------
        # 5. EVALUATION: Professional Summary / Career Objective
        # ---------------------------------------------------------------------
        obj_score = cat_scores_by_name.get("Career Objective")
        obj_earned = obj_score.score_earned if obj_score else 0.0
        obj_max = weights_map["Career Objective"]
        obj_pct = (obj_earned / obj_max * 100.0) if obj_max > 0 else 0.0

        is_obj_weak = obj_pct < 80.0
        if is_obj_weak:
            weak_categories_list.append("Professional Summary")

        summary_eval = WeakCategoryEvaluation(
            category_name="Professional Summary or Career Objective",
            category_key="summary",
            current_score=round(obj_earned, 1),
            max_score=round(obj_max, 1),
            percentage=round(obj_pct, 1),
            is_weak=is_obj_weak,
            what_is_missing=(
                f"The existing summary lacks tight role alignment with '{role_name}' and does not spotlight "
                f"demonstrated technical strengths or target responsibilities."
            ),
            affected_job_requirements=[
                f"Clear professional presentation and role readiness statement for {role_name}."
            ],
            specific_improvements=[
                "Adopt a focused professional headline reflecting target cybersecurity competencies.",
                "Rewrite the summary to highlight verified technical skills, projects, and education.",
                "Ensure professional wording free of generic fluff or unsupported buzzwords.",
            ],
            required_candidate_info="Approval or customized edit of the proposed ATS professional summary.",
            resume_sections_to_update=["Professional Headline", "Professional Summary"],
            role_relevance_reason=(
                "The headline and summary create the critical initial impression for ATS parsers and hiring recruiters."
            ),
            action_nature="improve_presentation",
            confirmation_needed=False,
            recommended_next_action="Adopt an ATS-optimized headline and summary aligned with role competencies.",
        )
        category_evaluations.append(summary_eval)

        # ---------------------------------------------------------------------
        # 6. EVALUATION: Work Experience and Internships
        # ---------------------------------------------------------------------
        has_exp = len(resume_data.employment_history) > 0
        exp_eval = WeakCategoryEvaluation(
            category_name="Work Experience and Internships",
            category_key="experience",
            current_score=10.0 if has_exp else 0.0,
            max_score=10.0,
            percentage=100.0 if has_exp else 0.0,
            is_weak=not has_exp,
            what_is_missing=(
                f"Resume documents {len(resume_data.employment_history)} employment entry/entries. "
                f"Existing bullets may lack active cybersecurity action verbs or explicit security duties."
            ),
            affected_job_requirements=exp_reqs or [
                "Operational technical experience or transferable technical responsibilities."
            ],
            specific_improvements=[
                "Refine bullet points with active cybersecurity verbs (Configured, Hardened, Monitored, Triaged).",
                "Integrate any candidate-confirmed technical internships or security operational duties.",
                "Strictly maintain genuine employment history; never fabricate roles, companies, or dates.",
            ],
            required_candidate_info="Specific security tasks performed, tools configured, or internship details.",
            resume_sections_to_update=["Work Experience", "Internships"],
            role_relevance_reason=(
                "Demonstrates operational capability and professional workplace problem-solving."
            ),
            action_nature="confirm_existing" if not has_exp else "improve_presentation",
            confirmation_needed=has_exp,
            recommended_next_action="Refine role descriptions with measurable security tasks and strong action verbs (Configured, Hardened, Monitored).",
        )
        category_evaluations.append(exp_eval)
        if not has_exp:
            weak_categories_list.append("Work Experience & Internships")

        # ---------------------------------------------------------------------
        # 7. EVALUATION: Relevant Achievements and Supporting Evidence
        # ---------------------------------------------------------------------
        has_achieve = len(resume_data.achievements) > 0
        achieve_eval = WeakCategoryEvaluation(
            category_name="Relevant Achievements and Supporting Evidence",
            category_key="achievements",
            current_score=5.0 if has_achieve else 0.0,
            max_score=5.0,
            percentage=100.0 if has_achieve else 0.0,
            is_weak=not has_achieve,
            what_is_missing=(
                "No distinct professional achievements, CTF completions, bug bounty acknowledgments, or academic honors documented."
            ),
            affected_job_requirements=gen_reqs or [
                "Verifiable evidence of proactive engagement, competitions, or academic excellence."
            ],
            specific_improvements=[
                "Document genuine accomplishments: CTF rankings, academic awards, bug bounty acknowledgments, or certifications.",
                "Never invent unsupported numbers, percentages, or fabricated awards.",
            ],
            required_candidate_info="Genuine technical achievements, CTF participation, or honors.",
            resume_sections_to_update=["Achievements & Awards"],
            role_relevance_reason=(
                "Distinguishes high-performing candidates through verified independent accomplishments."
            ),
            action_nature="confirm_existing",
            confirmation_needed=True,
            recommended_next_action="Document genuine accomplishments, CTF rankings, or academic recognitions.",
        )
        category_evaluations.append(achieve_eval)

        # ---------------------------------------------------------------------
        # 8. EVALUATION: Resume Organization and ATS Readability
        # ---------------------------------------------------------------------
        ats_eval = WeakCategoryEvaluation(
            category_name="Resume Organization and ATS Readability",
            category_key="ats_readability",
            current_score=5.0,
            max_score=5.0,
            percentage=100.0,
            is_weak=False,
            what_is_missing="Standard ATS single-column structure and standard section headings verified.",
            affected_job_requirements=["Standard ATS single-column parseability and readability."],
            specific_improvements=[
                "Maintain clean single-column chronological structure.",
                "Use standard ATS section headings without graphics or multi-column text boxes.",
            ],
            required_candidate_info="No candidate input required; Round Robin templates automatically ensure ATS readability.",
            resume_sections_to_update=["Document Layout"],
            role_relevance_reason="ATS parsers and applicant filters require clean headings without parsing obstacles.",
            action_nature="improve_presentation",
            confirmation_needed=False,
            recommended_next_action="Generate your resume using the automatic Round Robin ATS template scheduler.",
        )
        category_evaluations.append(ats_eval)

        # =====================================================================
        # BUILD DETAILED RECOMMENDATION CARDS (High, Medium, Additional)
        # =====================================================================

        # ---------------------------------------------------------------------
        # A. High-Priority Items: Mandatory Core Skills & Core Project Gaps
        # ---------------------------------------------------------------------
        # 1. Individual Technical Skill Cards for Core Skills
        for skill in missing_core[:5]:
            resources = cls.LEARNING_RESOURCES.get(skill.lower(), [
                f"Explore official documentation and foundational tutorials for '{skill}'.",
                f"Practice hands-on laboratory exercises on platforms like TryHackMe or HackTheBox."
            ])
            s_detail = SkillRecommendationDetail(
                skill_name=skill,
                requirement_classification="mandatory",
                current_evidence=f"The uploaded resume does not provide sufficient evidence of {skill} experience.",
                importance_for_role=f"Classified as a core mandatory requirement for {role_name} in the cybersecurity job database.",
                gap_explanation=(
                    f"ATS parsers and cybersecurity hiring managers specifically scan for {skill} "
                    f"as a non-negotiable requirement for {role_name} candidates."
                ),
                suggested_resume_section="Technical Skills or Projects",
                candidate_confirmation_question=f"Have you used {skill} in a completed project, practical laboratory, internship, or other relevant activity?",
                recommended_action=f"Ask candidate whether they have used {skill}. If confirmed, incorporate accurate details into Technical Skills or Projects.",
                if_confirmed="Ask what functionality was used and what tasks were performed. Incorporate accurate details into Technical Skills or Projects.",
                if_basic_exposure="Describe that experience accurately as basic familiarity or foundational knowledge.",
                if_never_used="Recommend learning resources or a suitable future project. Do not add it as an existing skill.",
                learning_resources=resources,
            )

            q_id = f"skill_{skill.lower().replace(' ', '_').replace('/', '_')}"
            follow_ups = [
                {
                    "id": q_id,
                    "skill_name": skill,
                    "type": "skill_action",
                    "question": f"How should we handle '{skill}' on your resume?",
                    "options": [
                        {"value": "hands_on", "label": "Confirm Existing Experience (Hands-on Lab / Project / Work)"},
                        {"value": "basic_familiarity", "label": "Provide More Details (Basic Familiarity / Coursework)"},
                        {"value": "not_used", "label": "Recommend Learning Resources (Mark for future learning, do not add)"},
                        {"value": "skipped", "label": "Skip This Recommendation (Preserve original resume)"},
                    ],
                    "context_options": [
                        "Hands-on Home Lab / CTF",
                        "Academic Project",
                        "Technical Internship",
                        "University Coursework",
                        "Personal Practice & Development",
                        "Professional Employment",
                    ]
                },
                {
                    "id": f"{q_id}_details",
                    "type": "textarea",
                    "label": f"Details / Tasks performed with {skill}",
                    "placeholder": f"Describe specific tasks, commands, or tools used with {skill}...",
                    "condition": f"{q_id} == hands_on || {q_id} == basic_familiarity",
                }
            ]

            high_priority_items.append(ImprovementPlanItem(
                item_id=f"plan_skill_{skill.lower().replace(' ', '_').replace('/', '_')}",
                priority="high",
                item_type="skill_card",
                category="Technical Skills",
                category_key="technical_skills",
                title=f"Core Skill: {skill}",
                current_score=round(tech_earned, 1),
                max_score=round(tech_max, 1),
                current_issue=f"The uploaded resume does not provide sufficient evidence of {skill} experience.",
                recommended_change=(
                    f"Confirm if you have practical experience with {skill}. If confirmed, it will be added to your "
                    f"Technical Skills or Projects section. If unexperienced, it will be kept as a future learning recommendation."
                ),
                relevance_reason=f"Mandatory requirement: {skill} is essential for {role_name} qualifications.",
                required_info=f"Select your actual experience with {skill} and describe the context.",
                expected_improvement="Demonstrates core role qualification and directly satisfies ATS criteria.",
                action_type="skills_confirmation",
                status="pending",
                is_weak_category=True,
                action_nature="confirm_existing",
                affected_job_requirements=[f"Core skill: {skill}"],
                resume_sections_to_update=["Technical Skills", "Projects"],
                skill_details=s_detail,
                follow_up_questions=follow_ups,
            ))

        # 2. Practical Project Recommendation (Primary project tailored to role & candidate gaps)
        primary_full_plan = PrimaryProjectPlanGenerator.generate_single_plan(
            role_name=role_name,
            unmatched_skills=missing_core or ["Core role competencies"],
            matched_skills=[s.skill_name for s in match_report.matched_skills],
            existing_projects_count=len(resume_data.projects),
        )

        try:
            doc_meta = ProjectPlanDocumentRenderer.render_plan_documents(primary_full_plan)
            docx_url = doc_meta["docx_url"]
            pdf_url = doc_meta["pdf_url"]
        except Exception:
            docx_url = f"/api/projects/download-plan/{primary_full_plan.plan_id}/docx"
            pdf_url = f"/api/projects/download-plan/{primary_full_plan.plan_id}/pdf"

        proj_template = PracticalProjectTemplate(
            project_title=primary_full_plan.overview.project_title,
            target_role=role_name,
            level=primary_full_plan.overview.difficulty,
            skills_demonstrated=primary_full_plan.skills.all_targeted_skills,
            proposed_technologies=primary_full_plan.technology_stack,
            project_objective=primary_full_plan.overview.project_objective,
            suggested_implementation_tasks=[p.tasks[0] for p in primary_full_plan.phases if p.tasks],
            expected_deliverables="; ".join(primary_full_plan.final_deliverables[:3]),
            suggested_resume_bullet=primary_full_plan.resume_documentation_guide.sample_bullets[0] if primary_full_plan.resume_documentation_guide.sample_bullets else "",
            is_future_project=True,
            plan_id=primary_full_plan.plan_id,
            docx_download_url=docx_url,
            pdf_download_url=pdf_url,
            weaknesses_addressed=primary_full_plan.overview.weaknesses_addressed,
        )
        if is_proj_weak:
            p_follow_ups = [
                {
                    "id": "has_omitted_project",
                    "type": "boolean",
                    "question": f"Have you completed a practical project similar to '{proj_template.project_title}'?",
                    "options": [
                        {"value": "yes", "label": "Yes, I have completed a relevant project to incorporate."},
                        {"value": "no", "label": "No, keep this as a future practical laboratory blueprint."}
                    ]
                },
                {
                    "id": "project_title",
                    "type": "text",
                    "label": "Project Title",
                    "placeholder": proj_template.project_title,
                    "condition": "has_omitted_project == yes"
                },
                {
                    "id": "project_technologies",
                    "type": "text",
                    "label": "Technologies & Tools Used",
                    "placeholder": ", ".join(proj_template.proposed_technologies),
                    "condition": "has_omitted_project == yes"
                },
                {
                    "id": "project_contribution",
                    "type": "textarea",
                    "label": "What did you personally implement?",
                    "placeholder": proj_template.suggested_implementation_tasks[0] if proj_template.suggested_implementation_tasks else "Implemented...",
                    "condition": "has_omitted_project == yes"
                },
                {
                    "id": "project_outcomes",
                    "type": "textarea",
                    "label": "Measurable Results / Deliverables",
                    "placeholder": proj_template.expected_deliverables,
                    "condition": "has_omitted_project == yes"
                }
            ]

            high_priority_items.append(ImprovementPlanItem(
                item_id="plan_project_recommendation",
                priority="high",
                item_type="project_recommendation",
                category="Projects",
                category_key="projects",
                title=f"Practical Project: {proj_template.project_title}",
                current_score=round(proj_earned, 1),
                max_score=round(proj_max, 1),
                current_issue=f"Projects score ({round(proj_earned, 1)}/{round(proj_max, 1)}) is below the 80% benchmark.",
                recommended_change=(
                    f"Incorporate verified evidence from a practical project like '{proj_template.project_title}', "
                    f"or polish your existing project descriptions with concrete deliverables."
                ),
                relevance_reason=f"Employers for {role_name} prioritize tangible evidence of hands-on technical problem-solving.",
                required_info="Confirm whether you have completed a similar project, or polish existing project bullets.",
                expected_improvement="Substantially elevates practical evidence and satisfies project scoring criteria.",
                action_type="project_enhancement",
                status="pending",
                is_weak_category=True,
                action_nature="confirm_existing",
                affected_job_requirements=[f"Hands-on project demonstration for {role_name}"],
                resume_sections_to_update=["Projects", "Technical Skills"],
                project_recommendation=proj_template,
                follow_up_questions=p_follow_ups,
            ))

        # ---------------------------------------------------------------------
        # B. Medium-Priority Items: Preferred Skills, Certifications, Experience
        # ---------------------------------------------------------------------
        # 1. Preferred Skills Cards
        for skill in missing_pref[:4]:
            resources = cls.LEARNING_RESOURCES.get(skill.lower(), [
                f"Review foundational concepts and documentation for '{skill}'.",
            ])
            s_detail = SkillRecommendationDetail(
                skill_name=skill,
                requirement_classification="preferred",
                current_evidence=f"Not clearly demonstrated in the uploaded resume.",
                importance_for_role=f"Preferred requirement in the {role_name} job profile.",
                gap_explanation=f"While not mandatory, having {skill} provides a competitive advantage for {role_name} applicants.",
                suggested_resume_section="Technical Skills or Projects",
                candidate_confirmation_question=f"Do you have practical or coursework familiarity with {skill}?",
                recommended_action="Confirm existing experience or coursework exposure; if not used, suggest learning resources.",
                if_confirmed="Add to Technical Skills or Projects with accurate details.",
                if_basic_exposure="Document as foundational knowledge under coursework exposure.",
                if_never_used="Recommend learning resources; do not add as current competency.",
                learning_resources=resources,
            )

            q_id = f"skill_pref_{skill.lower().replace(' ', '_').replace('/', '_')}"
            follow_ups = [
                {
                    "id": q_id,
                    "skill_name": skill,
                    "type": "skill_action",
                    "question": f"How should we handle preferred skill '{skill}'?",
                    "options": [
                        {"value": "hands_on", "label": "Confirm Existing Experience (Hands-on)"},
                        {"value": "basic_familiarity", "label": "Basic Familiarity / Coursework"},
                        {"value": "not_used", "label": "Recommend Learning Resources"},
                        {"value": "skipped", "label": "Skip This Recommendation"},
                    ]
                }
            ]

            medium_priority_items.append(ImprovementPlanItem(
                item_id=f"plan_skill_pref_{skill.lower().replace(' ', '_').replace('/', '_')}",
                priority="medium",
                item_type="skill_card",
                category="Technical Skills",
                category_key="technical_skills",
                title=f"Preferred Skill: {skill}",
                current_score=round(tech_earned, 1),
                max_score=round(tech_max, 1),
                current_issue=f"Preferred skill '{skill}' is not clearly demonstrated in the resume.",
                recommended_change=f"Confirm if you have hands-on or coursework exposure to {skill}.",
                relevance_reason=f"Preferred qualification: adds competitive edge for {role_name}.",
                required_info="Select your proficiency level for this preferred skill.",
                expected_improvement="Improves technical keyword match and demonstrates breadth.",
                action_type="skills_confirmation",
                status="pending",
                is_weak_category=False,
                action_nature="confirm_existing",
                affected_job_requirements=[f"Preferred skill: {skill}"],
                resume_sections_to_update=["Technical Skills"],
                skill_details=s_detail,
                follow_up_questions=follow_ups,
            ))

        # 2. Certification Recommendation Cards
        for c_bench in unique_benchmarks[:3]:
            already_held = any(c_bench.lower() in hc.lower() for hc in held_certs)
            c_detail = CertificationRecommendationDetail(
                cert_name=c_bench,
                relevance_to_role=f"Widely recognized industry certification benchmark for {role_name} roles.",
                db_classification="preferred",
                capability_demonstrated=f"Validates standardized cybersecurity skills and industry compliance for {role_name}.",
                candidate_status="already_earned" if already_held else "not_interested",
                recommended_next_action=(
                    "If already earned, confirm pass date/ID to include on resume. "
                    "If currently studying, describe as in-progress. If planning to pursue, save as future goal."
                ),
            )

            q_id = f"cert_{c_bench.lower().replace('+', 'plus').replace(' ', '_')}"
            c_follow_ups = [
                {
                    "id": q_id,
                    "cert_name": c_bench,
                    "question": f"What is your current status for {c_bench}?",
                    "options": [
                        {"value": "earned_verified", "label": "Already Earned (Include in Completed Certifications)"},
                        {"value": "currently_pursuing", "label": "Currently Pursuing (Describe as In-Progress)"},
                        {"value": "future_learning", "label": "Planning to Pursue (Keep in improvement plan as goal)"},
                        {"value": "not_interested", "label": "Not Interested"},
                    ]
                },
                {
                    "id": f"{q_id}_confirmation",
                    "type": "text",
                    "label": "Issuing Body / Year Earned (Verification)",
                    "placeholder": "e.g., CompTIA, 2023",
                    "condition": f"{q_id} == earned_verified",
                }
            ]

            medium_priority_items.append(ImprovementPlanItem(
                item_id=f"plan_cert_{c_bench.lower().replace('+', 'plus').replace(' ', '_')}",
                priority="medium",
                item_type="cert_recommendation",
                category="Tools & Certifications",
                category_key="certifications",
                title=f"Certification: {c_bench}",
                current_score=round(tools_earned, 1),
                max_score=round(tools_max, 1),
                current_issue=(
                    f"{'Already documented' if already_held else 'Not documented'} in resume. "
                    f"Role benchmarks prioritize credentials like {c_bench}."
                ),
                recommended_change=(
                    f"Confirm if you have already earned {c_bench}, are currently studying, or plan to pursue it in the future."
                ),
                relevance_reason=f"Industry benchmark credential validating practical readiness for {role_name}.",
                required_info="Select your exact certification status.",
                expected_improvement="Transparent credential representation without fabricating unearned designations.",
                action_type="cert_status_confirmation",
                status="pending",
                is_weak_category=is_tools_weak,
                action_nature="confirm_existing" if already_held else "acquire_new_skills",
                affected_job_requirements=[f"Certification benchmark: {c_bench}"],
                resume_sections_to_update=["Certifications", "Pursuing Certifications"],
                cert_recommendation=c_detail,
                follow_up_questions=c_follow_ups,
            ))

        # 3. Work Experience / Operational Duties Polish
        exp_follow_ups = [
            {
                "id": "security_duties_clarification",
                "type": "textarea",
                "label": "Security-Related Duties Performed",
                "placeholder": "Describe any security tasks, monitoring, policy adherence, or system maintenance you performed...",
            },
            {
                "id": "internship_details",
                "type": "text",
                "label": "Relevant Internships (if applicable)",
                "placeholder": "Role, Organization, Duration, Key technical responsibilities",
            }
        ]
        medium_priority_items.append(ImprovementPlanItem(
            item_id="plan_experience",
            priority="medium",
            item_type="section_polish",
            category="Work Experience & Internships",
            category_key="experience",
            title="Work Experience & Security Duties Enhancement",
            current_score=10.0 if has_exp else 0.0,
            max_score=10.0,
            current_issue=(
                f"Resume lists {len(resume_data.employment_history)} employment role(s). "
                f"Descriptions could highlight active cybersecurity responsibilities more effectively."
            ),
            recommended_change=(
                "Polish existing bullet points with active cybersecurity verbs and ask for any omitted security duties or internships."
            ),
            relevance_reason="Translates general IT or software experience into security-relevant operational capabilities.",
            required_info="Specific security duties performed or internship details.",
            expected_improvement="Strengthens professional wording and operational relevance.",
            action_type="experience_clarification",
            status="pending",
            is_weak_category=not has_exp,
            action_nature="improve_presentation",
            affected_job_requirements=["Operational security duties"],
            resume_sections_to_update=["Work Experience", "Internships"],
            follow_up_questions=exp_follow_ups,
        ))

        # ---------------------------------------------------------------------
        # C. Additional Enhancements: Summary, Education, Formatting
        # ---------------------------------------------------------------------
        # 1. Professional Summary Rewrite
        sum_follow_ups = [
            {
                "id": "custom_summary_input",
                "type": "textarea",
                "label": "Review or Customize Proposed Professional Summary",
                "placeholder": (
                    f"Dedicated {role_name} practitioner with hands-on technical proficiency across "
                    f"{', '.join(resume_data.technical_skills[:3]) if resume_data.technical_skills else 'cyber defense'}. "
                    f"Committed to rigorous security assessment, defense-in-depth, and proactive threat remediation."
                ),
            }
        ]
        additional_enhancements.append(ImprovementPlanItem(
            item_id="plan_summary",
            priority="low",
            item_type="section_polish",
            category="Professional Summary & Headline",
            category_key="summary",
            title=f"Professional Headline & Summary Aligned to {role_name}",
            current_score=round(obj_earned, 1),
            max_score=round(obj_max, 1),
            current_issue="Current professional summary or objective lacks tight alignment with the selected cybersecurity role.",
            recommended_change=(
                f"Generate a professional headline and ATS-optimized summary specifically highlighting your verified skills "
                f"and readiness for {role_name} responsibilities."
            ),
            relevance_reason="The headline and summary form the critical first impression for ATS scanners and cybersecurity hiring managers.",
            required_info="Review and approve or customize the proposed professional headline and summary.",
            expected_improvement="Immediately communicates role alignment and technical focus at the top of the resume.",
            action_type="summary_rewrite",
            status="pending",
            is_weak_category=is_obj_weak,
            action_nature="improve_presentation",
            affected_job_requirements=[f"Role alignment for {role_name}"],
            resume_sections_to_update=["Professional Headline", "Professional Summary"],
            follow_up_questions=sum_follow_ups,
        ))

        # 2. Education Relevance
        edu_follow_ups = [
            {
                "id": "relevant_coursework",
                "type": "text",
                "label": "Relevant Coursework or Academic Modules",
                "placeholder": "e.g., Computer Networks, Cryptography, Operating Systems, Database Security",
            },
            {
                "id": "academic_honors",
                "type": "text",
                "label": "Academic Achievements or Honors (Optional)",
                "placeholder": "e.g., Dean's List, First Class with Distinction, Academic Scholar",
            }
        ]
        additional_enhancements.append(ImprovementPlanItem(
            item_id="plan_education",
            priority="low",
            item_type="section_polish",
            category="Education",
            category_key="education",
            title="Education Relevance & Coursework Presentation",
            current_score=round(edu_earned, 1),
            max_score=round(edu_max, 1),
            current_issue="Education presentation could highlight relevant security coursework and academic honors.",
            recommended_change=(
                "Highlight relevant security or technical coursework, academic projects, and honors that demonstrate foundational knowledge."
            ),
            relevance_reason="Verifies educational background while honoring non-engineering disciplines fairly per role specifications.",
            required_info="Relevant academic courses, technical modules, or academic achievements to highlight.",
            expected_improvement="Clarifies academic relevance without imposing arbitrary degree penalties.",
            action_type="education_clarification",
            status="pending",
            is_weak_category=is_edu_weak,
            action_nature="improve_presentation",
            affected_job_requirements=edu_reqs or ["Degree evaluation fair per role criteria"],
            resume_sections_to_update=["Education"],
            follow_up_questions=edu_follow_ups,
        ))

        # 3. Additional Skills (from missing_add)
        for skill in missing_add[:2]:
            s_detail = SkillRecommendationDetail(
                skill_name=skill,
                requirement_classification="additional",
                current_evidence="Not mentioned in resume.",
                importance_for_role=f"Optional / supplementary skill for {role_name}.",
                gap_explanation=f"Optional skill that may provide minor differentiation.",
                suggested_resume_section="Technical Skills",
                candidate_confirmation_question=f"Do you have experience with optional skill '{skill}'?",
                recommended_action="Confirm experience if possessed; otherwise skip.",
                if_confirmed="Include in Technical Skills under appropriate category.",
                if_basic_exposure="Document as foundational knowledge.",
                if_never_used="Skip without penalization.",
            )
            q_id = f"skill_add_{skill.lower().replace(' ', '_').replace('/', '_')}"
            additional_enhancements.append(ImprovementPlanItem(
                item_id=f"plan_skill_add_{skill.lower().replace(' ', '_').replace('/', '_')}",
                priority="low",
                item_type="skill_card",
                category="Technical Skills",
                category_key="technical_skills",
                title=f"Additional Skill: {skill}",
                current_score=round(tech_earned, 1),
                max_score=round(tech_max, 1),
                current_issue=f"Optional skill '{skill}' not listed in resume.",
                recommended_change=f"Confirm if you have exposure to {skill}.",
                relevance_reason=f"Supplementary skill for {role_name}.",
                required_info="Select your proficiency level if applicable.",
                expected_improvement="Optional keyword enrichment.",
                action_type="skills_confirmation",
                status="pending",
                is_weak_category=False,
                action_nature="confirm_existing",
                affected_job_requirements=[f"Additional skill: {skill}"],
                resume_sections_to_update=["Technical Skills"],
                skill_details=s_detail,
                follow_up_questions=[{
                    "id": q_id,
                    "skill_name": skill,
                    "type": "skill_action",
                    "question": f"Do you possess optional skill '{skill}'?",
                    "options": [
                        {"value": "hands_on", "label": "Yes, I have hands-on experience"},
                        {"value": "not_used", "label": "No, skip this optional skill"},
                    ]
                }],
            ))

        # 4. Tools & Technologies Categorization
        known_sec_tools = ["Wireshark", "Burp Suite", "Nmap", "Metasploit", "Splunk", "Nessus", "Snort", "Linux / Kali"]
        tools_questions = []
        for t in known_sec_tools[:5]:
            tools_questions.append({
                "id": f"tool_{t.lower().replace(' ', '_').replace('/', '_')}",
                "tool_name": t,
                "question": f"What is your proficiency level with {t}?",
                "options": [
                    {"value": "hands_on", "label": "Hands-on experience (used in labs, projects, or work)."},
                    {"value": "basic_familiarity", "label": "Basic familiarity / coursework exposure."},
                    {"value": "no_experience", "label": "No previous experience."}
                ]
            })

        additional_enhancements.append(ImprovementPlanItem(
            item_id="plan_tools",
            priority="low",
            item_type="section_polish",
            category="Tools & Technologies",
            category_key="tools",
            title="Security Tools Categorization & Verification",
            current_score=round(tools_earned, 1),
            max_score=round(tools_max, 1),
            is_weak_category=is_tools_weak,
            current_issue="Security toolsets are not explicitly categorized or differentiated by hands-on versus basic familiarity.",
            recommended_change=(
                "Categorize security tools logically into Offensive/Defensive, SIEM & Monitoring, and Operating Systems, "
                "specifying truthful proficiency levels."
            ),
            relevance_reason="Hiring teams need to know which tools you can operate immediately on day one.",
            required_info="Confirm hands-on versus basic familiarity proficiency for essential cybersecurity tools.",
            expected_improvement="Clear, structured categorization of tools with honest proficiency indicators.",
            action_type="tools_confirmation",
            status="pending",
            action_nature="confirm_existing",
            affected_job_requirements=["Explicit technical tool demonstration"],
            resume_sections_to_update=["Tools & Technologies"],
            follow_up_questions=tools_questions,
        ))

        # Combined items list in priority order
        all_items: List[ImprovementPlanItem] = []
        all_items.extend(high_priority_items)
        all_items.extend(medium_priority_items)
        all_items.extend(additional_enhancements)

        initial_score = score_result.final_score
        meets_thresh = initial_score >= 80.0

        if meets_thresh:
            advice = (
                f"Your original resume achieved a strong score of {initial_score}/100, meeting the 80.0 passing threshold "
                f"for {role_name}. You may proceed directly or review optional enhancements."
            )
        else:
            advice = (
                f"Your initial compatibility score is {initial_score}/100 (Threshold: 80.0/100). "
                f"The detailed improvement plan below identifies {len(weak_categories_list)} weak category/categories "
                f"and provides prioritized, role-specific recommendations for {role_name}. "
                f"Approve or edit factual items, answer confirmation questions, and generate an ATS-optimized resume."
            )

        return ResumeImprovementPlan(
            initial_score=initial_score,
            threshold=80.0,
            meets_threshold=meets_thresh,
            role_name=role_name,
            weak_categories=weak_categories_list,
            category_evaluations=category_evaluations,
            high_priority_items=high_priority_items,
            medium_priority_items=medium_priority_items,
            additional_enhancements=additional_enhancements,
            items=all_items,
            summary_advice=advice,
            primary_project_plan=primary_full_plan.model_dump(),
        )

    @classmethod
    def _build_role_project_template(cls, role_name: str) -> PracticalProjectTemplate:
        """Builds a role-tailored practical project blueprint for candidates needing project evidence."""
        plan = PrimaryProjectPlanGenerator.generate_single_plan(
            role_name=role_name,
            unmatched_skills=["Core role competencies"],
            matched_skills=[],
            existing_projects_count=0,
        )
        try:
            doc_meta = ProjectPlanDocumentRenderer.render_plan_documents(plan)
            d_url = doc_meta["docx_url"]
            p_url = doc_meta["pdf_url"]
        except Exception:
            d_url = f"/api/projects/download-plan/{plan.plan_id}/docx"
            p_url = f"/api/projects/download-plan/{plan.plan_id}/pdf"

        return PracticalProjectTemplate(
            project_title=plan.overview.project_title,
            target_role=role_name,
            level=plan.overview.difficulty,
            skills_demonstrated=plan.skills.all_targeted_skills,
            proposed_technologies=plan.technology_stack,
            project_objective=plan.overview.project_objective,
            suggested_implementation_tasks=[p.tasks[0] for p in plan.phases if p.tasks],
            expected_deliverables="; ".join(plan.final_deliverables[:3]),
            suggested_resume_bullet=plan.resume_documentation_guide.sample_bullets[0] if plan.resume_documentation_guide.sample_bullets else "",
            is_future_project=True,
            plan_id=plan.plan_id,
            docx_download_url=d_url,
            pdf_download_url=p_url,
            weaknesses_addressed=plan.overview.weaknesses_addressed,
            project_workflow=plan.project_workflow,
        )
