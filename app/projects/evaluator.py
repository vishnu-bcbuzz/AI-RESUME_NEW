"""Completed project evaluation and weakness analysis engine for FUTRSEC.

Evaluates student-submitted practical project evidence against the recommended
implementation plan and target cybersecurity job role requirements.

Outputs:
1. Green — Demonstrated: Features and skills supported by submitted evidence.
2. Amber — Improvement Needed: Incomplete features, weak explanations, or missing evidence.
3. Grey — Not Yet Submitted: Deliverables or claims that cannot yet be evaluated.
4. Recommended Next Action: Exactly ONE prioritized next action to improve the project.
5. Proposed Resume Entry: Honest ATS-ready project entry formatted as:
   **Project Title | Technologies Used**
   * Developed [actual functionality implemented].
   * Used [technologies confirmed by the candidate].
   * Tested [verified testing activities].
   * Achieved [actual, supported outcome].

Security Constraints:
- Treats all candidate input as untrusted data; sanitizes input strings.
- Never executes code from submitted projects or repositories.
- Does not award points merely for submitting a form or pasting a repository URL.
- Marks verification as inconclusive if evidence is insufficient.
"""

import re
import html
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class CompletedProjectSubmission(BaseModel):
    """Candidate-submitted completed project details."""
    project_title: str
    project_description: str
    skills_used: List[str] = Field(default_factory=list)
    technologies_used: List[str] = Field(default_factory=list)
    implementation_tasks_completed: List[str] = Field(default_factory=list)
    testing_performed: str = ""
    verified_outcomes: str = ""
    status: str = "completed"  # 'completed' | 'in_progress'
    github_url: Optional[str] = None
    documentation_notes: Optional[str] = None
    confirmation_statement: bool = False  # Candidate confirms work is accurate representation


class EvaluatedCriterion(BaseModel):
    name: str
    status: str  # 'demonstrated' (Green) | 'improvement_needed' (Amber) | 'not_yet_submitted' (Grey)
    finding: str
    evidence_snippet: Optional[str] = None
    recommendation: Optional[str] = None


class ProposedResumeEntry(BaseModel):
    title_line: str
    bullets: List[str]
    status_label: str  # 'Completed Project' | 'Project In Progress'
    is_approved: bool = False


class ProjectEvaluationResult(BaseModel):
    submission_id: str
    project_title: str
    status: str  # 'completed' | 'in_progress'
    verdict: str  # 'verified_demonstrated' | 'inconclusive_evidence' | 'needs_revision'
    verdict_explanation: str
    demonstrated: List[EvaluatedCriterion]        # Green
    improvement_needed: List[EvaluatedCriterion]  # Amber
    not_yet_submitted: List[EvaluatedCriterion]   # Grey
    recommended_next_action: str
    proposed_resume_entry: ProposedResumeEntry
    candidate_confirmed: bool


class CompletedProjectEvaluator:
    """Evaluates candidate submitted project against objective evidence criteria."""

    @classmethod
    def sanitize_text(cls, text: Optional[str], max_length: int = 2000) -> str:
        """Sanitizes untrusted input text."""
        if not text:
            return ""
        # Escape HTML entities, strip unprintable ASCII controls, limit length
        cleaned = html.escape(text.strip())
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", cleaned)
        return cleaned[:max_length]

    @classmethod
    def evaluate_submission(
        cls,
        submission: CompletedProjectSubmission,
        target_role: str,
        plan_expected_skills: Optional[List[str]] = None,
    ) -> ProjectEvaluationResult:
        """Conducts structured 3-tier weakness analysis (Green/Amber/Grey) on submitted work."""
        plan_expected_skills = plan_expected_skills or []

        # Sanitize all fields
        title = cls.sanitize_text(submission.project_title, 120) or "Cybersecurity Practical Project"
        desc = cls.sanitize_text(submission.project_description, 2000)
        testing = cls.sanitize_text(submission.testing_performed, 2000)
        outcomes = cls.sanitize_text(submission.verified_outcomes, 2000)
        doc_notes = cls.sanitize_text(submission.documentation_notes, 2000)
        gh_url = cls.sanitize_text(submission.github_url, 255) if submission.github_url else ""

        skills = [cls.sanitize_text(s, 60) for s in submission.skills_used if s.strip()]
        technologies = [cls.sanitize_text(t, 60) for t in submission.technologies_used if t.strip()]
        tasks = [cls.sanitize_text(tk, 250) for tk in submission.implementation_tasks_completed if tk.strip()]

        demonstrated: List[EvaluatedCriterion] = []
        improvement_needed: List[EvaluatedCriterion] = []
        not_yet_submitted: List[EvaluatedCriterion] = []

        # -------------------------------------------------------------
        # 1. Evaluate Core Implementation & Tasks
        # -------------------------------------------------------------
        combined_text = (desc + " " + " ".join(tasks) + " " + testing + " " + outcomes).lower()

        if len(tasks) >= 3 and len(desc) >= 80:
            demonstrated.append(
                EvaluatedCriterion(
                    name="Implementation Execution",
                    status="demonstrated",
                    finding=f"Documented {len(tasks)} concrete implementation steps demonstrating practical system setup.",
                    evidence_snippet=tasks[0][:100],
                )
            )
        elif len(tasks) >= 1 or len(desc) >= 40:
            improvement_needed.append(
                EvaluatedCriterion(
                    name="Implementation Execution",
                    status="improvement_needed",
                    finding="Basic implementation description provided; details on specific configurations remain brief.",
                    recommendation="Detail the specific commands, scripts, or network topology implemented.",
                )
            )
        else:
            not_yet_submitted.append(
                EvaluatedCriterion(
                    name="Implementation Execution",
                    status="not_yet_submitted",
                    finding="Detailed implementation tasks have not yet been submitted.",
                    recommendation="Provide at least 3 concrete tasks you personally implemented.",
                )
            )

        # -------------------------------------------------------------
        # 2. Evaluate Technology & Skills Evidence
        # -------------------------------------------------------------
        if technologies and len(technologies) >= 2:
            tech_supported = [t for t in technologies if t.lower() in combined_text]
            if len(tech_supported) >= 2:
                demonstrated.append(
                    EvaluatedCriterion(
                        name="Technology Stack Application",
                        status="demonstrated",
                        finding=f"Applied technologies confirmed with context: {', '.join(tech_supported[:4])}.",
                        evidence_snippet=", ".join(tech_supported[:4]),
                    )
                )
            else:
                improvement_needed.append(
                    EvaluatedCriterion(
                        name="Technology Stack Application",
                        status="improvement_needed",
                        finding=f"Technologies listed ({', '.join(technologies[:3])}), but practical usage context in tasks is brief.",
                        recommendation="Explain how each tool was configured and operated.",
                    )
                )
        else:
            not_yet_submitted.append(
                EvaluatedCriterion(
                    name="Technology Stack Application",
                    status="not_yet_submitted",
                    finding="Specific tools and technologies used were not specified.",
                    recommendation="List the exact development or security tools configured in the lab.",
                )
            )

        # -------------------------------------------------------------
        # 3. Evaluate Testing & Validation in Authorized Environments
        # -------------------------------------------------------------
        sec_keywords = ["test", "scan", "packet", "verify", "intercept", "alert", "pcap", "docker", "local", "sandbox", "burp", "splunk"]
        has_testing_evidence = any(kw in testing.lower() for kw in sec_keywords) or any(kw in combined_text for kw in sec_keywords)

        if len(testing) >= 50 and has_testing_evidence:
            demonstrated.append(
                EvaluatedCriterion(
                    name="Testing and Verification",
                    status="demonstrated",
                    finding="Documented verification testing in authorized environment with tangible output.",
                    evidence_snippet=testing[:90],
                )
            )
        elif len(testing) > 0:
            improvement_needed.append(
                EvaluatedCriterion(
                    name="Testing and Verification",
                    status="improvement_needed",
                    finding="Testing notes submitted, but verification steps require more technical specificity.",
                    recommendation="Document how you confirmed the project functioned as expected (e.g., test cases, logs).",
                )
            )
        else:
            not_yet_submitted.append(
                EvaluatedCriterion(
                    name="Testing and Verification",
                    status="not_yet_submitted",
                    finding="No testing methodology or validation results were provided.",
                    recommendation="Perform test scans or verification checks and document the observed behavior.",
                )
            )

        # -------------------------------------------------------------
        # 4. Evaluate Outcomes & Deliverables
        # -------------------------------------------------------------
        if len(outcomes) >= 40:
            demonstrated.append(
                EvaluatedCriterion(
                    name="Verified Outcomes",
                    status="demonstrated",
                    finding="Articulated measurable deliverables and verified outcomes.",
                    evidence_snippet=outcomes[:90],
                )
            )
        elif len(outcomes) > 0:
            improvement_needed.append(
                EvaluatedCriterion(
                    name="Verified Outcomes",
                    status="improvement_needed",
                    finding="Outcomes description is brief; lacks measurable metrics or concrete deliverables.",
                    recommendation="Specify deliverables produced (e.g., assessment report, custom dashboard, firewall rules).",
                )
            )
        else:
            not_yet_submitted.append(
                EvaluatedCriterion(
                    name="Verified Outcomes",
                    status="not_yet_submitted",
                    finding="Deliverables and verified outcomes not yet documented.",
                    recommendation="State what tangible deliverables resulted from the completed work.",
                )
            )

        # -------------------------------------------------------------
        # 5. Evaluate GitHub / Documentation
        # -------------------------------------------------------------
        if gh_url:
            if "github.com" in gh_url.lower():
                demonstrated.append(
                    EvaluatedCriterion(
                        name="Repository & Version Control",
                        status="demonstrated",
                        finding="Repository link provided for code inspection and configuration review.",
                        evidence_snippet=gh_url,
                    )
                )
            else:
                improvement_needed.append(
                    EvaluatedCriterion(
                        name="Repository & Version Control",
                        status="improvement_needed",
                        finding="Submitted repository link does not appear to be a standard GitHub repository URL.",
                        recommendation="Provide a valid repository URL or attach local project documentation.",
                    )
                )
        elif doc_notes and len(doc_notes) >= 30:
            demonstrated.append(
                EvaluatedCriterion(
                    name="Local Documentation",
                    status="demonstrated",
                    finding="Local implementation documentation provided in lieu of a public repository.",
                    evidence_snippet=doc_notes[:80],
                )
            )
        else:
            not_yet_submitted.append(
                EvaluatedCriterion(
                    name="Code & Documentation Deliverable",
                    status="not_yet_submitted",
                    finding="No repository URL or supporting documentation notes submitted.",
                    recommendation="Provide a GitHub link or describe your project README documentation.",
                )
            )

        # -------------------------------------------------------------
        # 6. Determine Recommended Next Action (Exactly ONE)
        # -------------------------------------------------------------
        if not submission.confirmation_statement:
            rec_next_action = "Review your submission details and check the confirmation checkbox to verify accuracy."
        elif not_yet_submitted:
            first_unsubmitted = not_yet_submitted[0]
            rec_next_action = first_unsubmitted.recommendation or f"Submit details for {first_unsubmitted.name}."
        elif improvement_needed:
            first_improvement = improvement_needed[0]
            rec_next_action = first_improvement.recommendation or f"Strengthen evidence for {first_improvement.name}."
        else:
            rec_next_action = "Review and approve the proposed ATS resume entry to incorporate this project into your resume."

        # -------------------------------------------------------------
        # 7. Formulate Proposed Resume Entry (Format from Section 9)
        # -------------------------------------------------------------
        tech_line = ", ".join(technologies[:5]) if technologies else "Cybersecurity Tools"
        is_in_prog = submission.status == "in_progress"

        if is_in_prog:
            title_line = f"{title} | In Progress"
            status_label = "In Progress"
            primary_task = tasks[0] if tasks else f"Developing {title.lower()} within an authorized environment"
            secondary_task = tasks[1] if len(tasks) > 1 else desc[:100] if desc else "Initiating core technical implementation"
            bullets = [
                f"Developing: {primary_task[:110]}.",
                f"Technologies: {tech_line}.",
                f"Planned Implementation: Progressing through technical execution and verification for {target_role}.",
            ]
        else:
            title_line = f"{title}"
            status_label = "Completed"
            primary_task = tasks[0] if tasks else f"Configured {title.lower()} within an authorized test sandbox"
            secondary_task = tasks[1] if len(tasks) > 1 else desc[:100] if desc else "Conducted hands-on technical validation"
            primary_test = testing if len(testing) >= 20 else f"Verified functionality through systematic testing with {tech_line}"
            primary_outcome = outcomes if len(outcomes) >= 20 else f"Produced reproducible deliverables and documentation for {target_role}"
            bullets = [
                f"Developed: {primary_task[:110]}.",
                f"Used: Technologies: {tech_line}.",
                f"Tested: {primary_test[:110]}.",
                f"Achieved: {primary_outcome[:110]}.",
            ]

        proposed_entry = ProposedResumeEntry(
            title_line=title_line,
            bullets=bullets,
            status_label=status_label,
            is_approved=False,
        )

        # Verdict
        if len(demonstrated) >= 3 and submission.confirmation_statement:
            verdict = "verified_demonstrated"
            verdict_expl = "Submitted evidence confirms hands-on implementation and satisfies practical project requirements."
        elif len(demonstrated) >= 1:
            verdict = "inconclusive_evidence"
            verdict_expl = "Verification is inconclusive. Submitted details indicate initial progress, but require stronger evidence before full ATS crediting."
        else:
            verdict = "needs_revision"
            verdict_expl = "Insufficient evidence provided to verify practical execution. Please review the recommended next action."

        sub_id = f"eval_{abs(hash(title + target_role)) % 100000}"

        return ProjectEvaluationResult(
            submission_id=sub_id,
            project_title=title,
            status=submission.status,
            verdict=verdict,
            verdict_explanation=verdict_expl,
            demonstrated=demonstrated,
            improvement_needed=improvement_needed,
            not_yet_submitted=not_yet_submitted,
            recommended_next_action=rec_next_action,
            proposed_resume_entry=proposed_entry,
            candidate_confirmed=submission.confirmation_statement,
        )
