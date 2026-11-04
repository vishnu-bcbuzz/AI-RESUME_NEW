"""Role-tailored project recommendation and implementation plan generator for FUTRSEC.

Generates exactly ONE primary project recommendation tailored to:
1. Target cybersecurity job role requirements from Neon PostgreSQL.
2. Candidate's declared skill proficiency, missing core skills, and education.
3. Identified project-related evidence weaknesses.

Produces a comprehensive, structured implementation plan covering Sections A through J:
A. Project Overview
B. Skills to Be Demonstrated (distinguishing existing vs skills to learn)
C. Technology Stack (free and accessible tools)
D. Implementation Phases (Objective, Tasks, Technologies, Expected Output, Verification)
E. Project Structure (Custom folder structure & file explanations)
F. Final Deliverables
G. Testing & Validation (Authorized, safe laboratory environments)
H. Expected Learning Outcomes
I. Resume Documentation Guide (Truthful bullet templates with clearly labeled examples)
J. GitHub and Presentation (Professional repository organization, zero sensitive credentials)
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ImplementationPhase(BaseModel):
    phase_number: int
    title: str
    objective: str
    tasks: List[str]
    technologies_used: List[str]
    expected_output: str
    verification_method: str


class ProjectOverview(BaseModel):
    project_title: str
    target_role: str
    difficulty: str  # 'Beginner' | 'Intermediate' | 'Advanced'
    problem_statement: str
    project_objective: str
    relevance_to_role: str
    weaknesses_addressed: List[str]


class SkillsBreakdown(BaseModel):
    existing_skills_applied: List[str]
    skills_to_be_learned: List[str]
    all_targeted_skills: List[str]


class ProjectStructureItem(BaseModel):
    path: str
    description: str


class ResumeBulletGuide(BaseModel):
    framework: str
    sample_bullets: List[str]
    guidance_notes: str


class ProjectImplementationPlan(BaseModel):
    plan_id: str
    generated_date: str
    overview: ProjectOverview
    skills: SkillsBreakdown
    technology_stack: List[str]
    technology_details: Dict[str, str]
    phases: List[ImplementationPhase]
    project_structure: List[ProjectStructureItem]
    final_deliverables: List[str]
    testing_and_validation: List[str]
    learning_outcomes: List[str]
    resume_documentation_guide: ResumeBulletGuide
    github_and_presentation: List[str]
    project_workflow: Optional[List[Dict[str, Any]]] = None


class PrimaryProjectPlanGenerator:
    """Generates a single personalized primary project recommendation and implementation plan."""

    @classmethod
    def generate_single_plan(
        cls,
        role_name: str,
        unmatched_skills: List[str],
        matched_skills: List[str],
        declared_proficiencies: Optional[Dict[str, str]] = None,
        existing_projects_count: int = 0,
        plan_id: Optional[str] = None,
    ) -> ProjectImplementationPlan:
        """Selects exactly ONE project tailored to role and candidate profile, then builds full plan."""
        declared_proficiencies = declared_proficiencies or {}
        role_lower = role_name.lower()
        now_str = datetime.now().strftime("%B %d, %Y")
        p_id = plan_id or f"plan_{int(datetime.now().timestamp())}"

        has_no_exp_flags = any(v in ("no_experience", "no experience yet", "none") for v in declared_proficiencies.values())

        # Determine candidate level:
        if "cloud" in role_lower:
            candidate_level = "Advanced"
        elif "soc" in role_lower or "analyst" in role_lower or "incident" in role_lower or "monitoring" in role_lower:
            candidate_level = "Beginner / Intermediate"
        elif "penetration" in role_lower or "ethical" in role_lower or "red team" in role_lower:
            candidate_level = "Intermediate"
        elif existing_projects_count == 0 or has_no_exp_flags:
            candidate_level = "Beginner"
        elif existing_projects_count >= 2 and any(v == "advanced" for v in declared_proficiencies.values()):
            candidate_level = "Advanced"
        else:
            candidate_level = "Intermediate"

        # Select role-tailored primary project blueprint
        if "ethical" in role_lower or "penetration" in role_lower or "red team" in role_lower:
            return cls._build_ethical_hacker_plan(
                p_id, now_str, role_name, candidate_level, unmatched_skills, matched_skills
            )
        elif "soc" in role_lower or "incident" in role_lower or "monitoring" in role_lower or "analyst" in role_lower:
            return cls._build_soc_analyst_plan(
                p_id, now_str, role_name, candidate_level, unmatched_skills, matched_skills
            )
        elif "cloud" in role_lower:
            return cls._build_cloud_security_plan(
                p_id, now_str, role_name, candidate_level, unmatched_skills, matched_skills
            )
        elif "application" in role_lower or "appsec" in role_lower or "software" in role_lower:
            return cls._build_appsec_plan(
                p_id, now_str, role_name, candidate_level, unmatched_skills, matched_skills
            )
        else:
            return cls._build_network_security_plan(
                p_id, now_str, role_name, candidate_level, unmatched_skills, matched_skills
            )

    @classmethod
    def _build_ethical_hacker_plan(
        cls,
        plan_id: str,
        generated_date: str,
        role_name: str,
        difficulty: str,
        unmatched_skills: List[str],
        matched_skills: List[str],
    ) -> ProjectImplementationPlan:
        """Ethical Hacker / Penetration Tester primary project."""
        project_title = "Web Application Security Testing Lab & Vulnerability Remediation"
        target_skills = ["Burp Suite", "OWASP Top 10", "Nmap", "Vulnerability Assessment", "Python Scripting", "Report Writing"]

        existing = [s for s in matched_skills if s in target_skills]
        to_learn = [s for s in target_skills if s not in existing]
        if not to_learn:
            to_learn = ["Advanced Burp Repeater", "Automated Security Reporting"]

        overview = ProjectOverview(
            project_title=project_title,
            target_role=role_name,
            difficulty=difficulty,
            problem_statement=(
                "Organizations face frequent security breaches due to web application flaws (such as SQL Injection, "
                "Cross-Site Scripting, and Insecure Direct Object References). Junior ethical hackers must demonstrate "
                "hands-on ability to discover vulnerabilities within authorized test scopes and author actionable remediation reports."
            ),
            project_objective=(
                "Deploy an authorized local security testing environment, conduct structured black-box and gray-box "
                "assessments against OWASP Top 10 vulnerabilities, author automated verification scripts, and deliver a "
                "professional penetration testing report with CVSS severity scoring."
            ),
            relevance_to_role=(
                f"Essential for {role_name}. Hiring teams require verifiable proof that you can operate intercepting "
                f"proxies, understand modern web application attack vectors, and articulate clear developer remediation steps."
            ),
            weaknesses_addressed=[
                "Insufficient hands-on web application assessment deliverables on resume.",
                f"Missing or unverified evidence for core skills: {', '.join(unmatched_skills[:3]) if unmatched_skills else 'Burp Suite, OWASP Top 10'}.",
                "Need for measurable cybersecurity deliverables with CVSS vulnerability classifications.",
            ],
        )

        skills = SkillsBreakdown(
            existing_skills_applied=existing or ["Basic Networking Concepts", "Linux Basics"],
            skills_to_be_learned=to_learn,
            all_targeted_skills=target_skills,
        )

        tech_stack = ["Burp Suite Community Edition", "OWASP Juice Shop / DVWA", "Nmap", "Python 3", "Docker", "Git"]
        tech_details = {
            "Burp Suite Community Edition": "Industry-standard intercepting HTTP proxy for request inspection, fuzzing, and manual vulnerability testing.",
            "OWASP Juice Shop / DVWA": "Freely available, intentionally vulnerable web application environments for authorized security practice.",
            "Nmap": "Open-source network scanner used for initial port discovery and web service fingerprinting.",
            "Python 3": "Scripting language for authoring reproducible proof-of-concept verification scripts.",
            "Docker": "Containerization platform to host test targets locally in an isolated, secure network sandbox.",
            "Git & GitHub": "Version control system for organizing documentation, scripts, and non-sensitive configurations.",
        }

        phases = [
            ImplementationPhase(
                phase_number=1,
                title="Lab Setup & Target Isolation",
                objective="Create a secure, isolated local lab running OWASP Juice Shop or DVWA via Docker.",
                tasks=[
                    "Install Docker Desktop on host machine.",
                    "Pull and run the official OWASP Juice Shop container: `docker run -d -p 3000:3000 bkimminich/juice-shop`.",
                    "Verify target accessibility strictly via localhost (`http://127.0.0.1:3000`).",
                    "Configure Burp Suite Community as the browser HTTP/HTTPS proxy and install PortSwigger CA certificate.",
                ],
                technologies_used=["Docker", "OWASP Juice Shop", "Burp Suite"],
                expected_output="Working local sandbox with browser proxying HTTP requests cleanly through Burp Suite.",
                verification_method="Browse to target; confirm HTTP traffic intercept and history logs in Burp Suite Proxy tab.",
            ),
            ImplementationPhase(
                phase_number=2,
                title="Reconnaissance & Attack Surface Mapping",
                objective="Systematically identify web application endpoints, inputs, and exposed functionality.",
                tasks=[
                    "Execute Nmap service scan against local target port (`nmap -sV -p 3000 127.0.0.1`).",
                    "Map application sitemap using Burp Target Scope and manual site navigation.",
                    "Identify hidden administrative endpoints, authentication workflows, and API routes.",
                    "Document all user input fields (search boxes, login forms, profile uploads).",
                ],
                technologies_used=["Nmap", "Burp Suite Target", "Browser DevTools"],
                expected_output="Structured attack surface inventory document listing all exposed routes and parameters.",
                verification_method="Review Burp Target site map for complete endpoint enumeration.",
            ),
            ImplementationPhase(
                phase_number=3,
                title="Vulnerability Discovery & Exploitation (OWASP Top 10)",
                objective="Identify, exploit, and verify 3 distinct vulnerabilities from the OWASP Top 10.",
                tasks=[
                    "Assess authentication and search parameters for SQL Injection vulnerabilities; capture raw HTTP request.",
                    "Test reflective and DOM-based input fields for Cross-Site Scripting (XSS).",
                    "Identify Insecure Direct Object Reference (IDOR) by manipulating user IDs or basket identifiers in Burp Repeater.",
                    "Write a Python script (`verify_exploit.py`) to reproducibly confirm one flaw safely.",
                ],
                technologies_used=["Burp Suite Repeater", "Burp Intruder", "Python 3"],
                expected_output="Proof-of-concept evidence for 3 distinct vulnerabilities including raw HTTP payloads.",
                verification_method="Reproduce each finding through Burp Repeater; confirm payload execution without service disruption.",
            ),
            ImplementationPhase(
                phase_number=4,
                title="Remediation Analysis & Professional Reporting",
                objective="Develop developer remediation guidance and compile an executive-ready assessment report.",
                tasks=[
                    "Assign CVSS v3.1 base metrics and severity ratings to each identified vulnerability.",
                    "Formulate defense-in-depth developer remediation advice (parameterized queries, input sanitization, strict RBAC).",
                    "Compile findings into a professional markdown or PDF Penetration Testing Report.",
                    "Perform post-remediation verification testing to confirm how developer patches resolve flaws.",
                ],
                technologies_used=["CVSS v3.1 Calculator", "Markdown / Pandoc", "Git"],
                expected_output="Completed Security Assessment Report with executive summary and technical appendices.",
                verification_method="Review report against industry standard penetration test reporting checklists.",
            ),
        ]

        structure = [
            ProjectStructureItem(path="README.md", description="Project overview, setup instructions, architecture diagram, and summary of findings."),
            ProjectStructureItem(path="docs/scope_of_work.md", description="Authorized testing boundaries, target IP, rules of engagement, and disclaimers."),
            ProjectStructureItem(path="docs/vulnerability_report.md", description="Formal assessment findings, CVSS scoring, reproduction steps, and remediation guidance."),
            ProjectStructureItem(path="docker/docker-compose.yml", description="Container configuration for running target web applications locally."),
            ProjectStructureItem(path="scripts/poc_verification.py", description="Safe, automated Python script to verify target vulnerability status."),
            ProjectStructureItem(path="evidence/screenshots/", description="Screenshots of Burp Repeater payloads and verified test outputs."),
            ProjectStructureItem(path=".gitignore", description="Excludes sensitive local logs, system files, and private credentials."),
        ]

        deliverables = [
            "Complete local test environment configuration via Docker Compose.",
            "Detailed Security Assessment Report with executive summary, CVSS v3.1 ratings, and technical evidence.",
            "Automated Python verification script demonstrating safe proof-of-concept testing.",
            "Step-by-step developer remediation recommendations for each vulnerability class.",
            "Well-organized GitHub repository with clear setup guide, architecture diagram, and MIT/Apache license.",
            "Project limitations and future improvements section (e.g., automated CI/CD security scanning).",
        ]

        testing_and_validation = [
            "Test exclusively against authorized local sandboxes (OWASP Juice Shop / DVWA). Never assess unauthorized internet targets.",
            "Verify all HTTP payloads through Burp Suite Repeater in an isolated container network.",
            "Execute Python proof-of-concept scripts in safe dry-run mode before live execution.",
            "Validate that security testing does not cause denial of service or target container corruption.",
        ]

        outcomes = [
            "Proficiency in operating Burp Suite Community as an intercepting proxy for web traffic analysis.",
            "Deep understanding of OWASP Top 10 vulnerabilities (SQLi, XSS, Broken Access Control) and their root causes.",
            "Ability to assign CVSS v3.1 scores to security flaws based on attack complexity and impact.",
            "Practical experience authoring professional, executive-ready cybersecurity assessment reports.",
        ]

        resume_guide = ResumeBulletGuide(
            framework="Action Verb + What You Implemented + Tools/Methodology + Measurable Outcome",
            sample_bullets=[
                "Configured an isolated web application security testing lab utilizing Docker and OWASP Juice Shop to assess OWASP Top 10 vulnerabilities.",
                "Conducted black-box security assessments with Burp Suite and Nmap, identifying 5 vulnerabilities including SQLi and Broken Access Control.",
                "Authored reproducible Python verification scripts and compiled a formal penetration testing report with CVSS v3.1 severity scores and developer remediation steps.",
            ],
            guidance_notes=(
                "Only list these bullets AFTER you have actually implemented the lab and verified the findings. "
                "Never claim project completion or fabricate numbers before performing the work."
            ),
        )

        github = [
            "Include a professional README.md with clear headings: Project Overview, Architecture, Prerequisites, Setup, Findings Summary, and Safe Lab Disclaimer.",
            "Add an architecture diagram illustrating the browser -> Burp proxy -> Docker container flow.",
            "SECURITY WARNING: Never commit passwords, API keys, session tokens, or confidential data into GitHub.",
            "Include an explicit disclaimer: 'This project was performed in a strictly authorized local laboratory environment for educational purposes.'",
        ]

        workflow = [
            {"step": 1, "type": "start", "label": "START"},
            {"step": 2, "type": "phase", "label": "Lab Setup (Docker & Juice Shop/DVWA)"},
            {"step": 3, "type": "phase", "label": "Reconnaissance & Attack Surface Mapping (Nmap & Burp Suite)"},
            {"step": 4, "type": "phase", "label": "Vulnerability Testing (SQL Injection, XSS, IDOR)", "is_loop_target": True},
            {
                "step": 5,
                "type": "decision",
                "label": "Was vulnerability verified?",
                "no_action": "Review evidence and refine testing in authorized environment.",
                "no_target_step": 4,
                "yes_action": "Record verified finding and proceed to assessment.",
            },
            {"step": 6, "type": "phase", "label": "Severity Assessment & Remediation Guidance (CVSS v3.1)"},
            {"step": 7, "type": "phase", "label": "Generate Security Assessment Report"},
            {"step": 8, "type": "end", "label": "END"},
        ]

        return ProjectImplementationPlan(
            plan_id=plan_id,
            generated_date=generated_date,
            overview=overview,
            skills=skills,
            technology_stack=tech_stack,
            technology_details=tech_details,
            phases=phases,
            project_structure=structure,
            final_deliverables=deliverables,
            testing_and_validation=testing_and_validation,
            learning_outcomes=outcomes,
            resume_documentation_guide=resume_guide,
            github_and_presentation=github,
            project_workflow=workflow,
        )

    @classmethod
    def _build_soc_analyst_plan(
        cls,
        plan_id: str,
        generated_date: str,
        role_name: str,
        difficulty: str,
        unmatched_skills: List[str],
        matched_skills: List[str],
    ) -> ProjectImplementationPlan:
        """SOC Analyst / Security Monitoring primary project."""
        project_title = "Home SOC & Threat Detection Pipeline (Splunk, Sysmon & Snort)"
        target_skills = ["Splunk", "Snort", "Log Analysis", "SIEM", "Wireshark", "Incident Triage", "MITRE ATT&CK"]

        existing = [s for s in matched_skills if s in target_skills]
        to_learn = [s for s in target_skills if s not in existing]
        if not to_learn:
            to_learn = ["Splunk SPL Query Optimization", "Sysmon Event ID Analysis"]

        overview = ProjectOverview(
            project_title=project_title,
            target_role=role_name,
            difficulty=difficulty,
            problem_statement=(
                "Security Operations Centers must detect, correlate, and triage hundreds of thousands of events "
                "to spot active adversary intrusion attempts. Candidates frequently lack hands-on experience "
                "configuring actual SIEM ingestion pipelines, writing alert logic, and investigating real telemetry."
            ),
            project_objective=(
                "Build an end-to-end security operations center pipeline ingesting Windows Event Logs (via Sysmon) "
                "and network telemetry into a centralized Splunk instance, map alerts to the MITRE ATT&CK framework, "
                "and triage simulated adversary attacks in real time."
            ),
            relevance_to_role=(
                f"Directly relevant to {role_name}. Hiring managers look for proven capability in parsing log telemetry, "
                f"authoring custom SIEM detection rules, and differentiating false positives from genuine security incidents."
            ),
            weaknesses_addressed=[
                "Lack of hands-on SIEM and security monitoring project deliverables.",
                f"Missing or unverified evidence for role skills: {', '.join(unmatched_skills[:3]) if unmatched_skills else 'Splunk, Log Analysis'}.",
                "Need for concrete incident triage and telemetry correlation evidence.",
            ],
        )

        skills = SkillsBreakdown(
            existing_skills_applied=existing or ["Operating System Fundamentals", "Basic Networking"],
            skills_to_be_learned=to_learn,
            all_targeted_skills=target_skills,
        )

        tech_stack = ["Splunk Enterprise (Free 500MB/day)", "Sysmon (Microsoft)", "Snort NIDS", "Wireshark", "VirtualBox / Ubuntu Server", "Atomic Red Team"]
        tech_details = {
            "Splunk Enterprise (Free)": "Industry-leading SIEM platform utilized for log indexing, searching, and alert dashboard creation.",
            "Sysmon (System Monitor)": "Microsoft Sysinternals utility providing granular endpoint telemetry (Process creation, Network connections, File changes).",
            "Snort NIDS": "Open-source network intrusion detection system inspecting packet streams for known attack patterns.",
            "Wireshark": "Packet inspection tool used to analyze anomalous network traffic and verify intrusion alerts.",
            "Atomic Red Team": "Open-source attack simulation library mapped to MITRE ATT&CK used to safely trigger test alerts.",
            "VirtualBox": "Free hypervisor platform for running isolated client and server virtual machines.",
        }

        phases = [
            ImplementationPhase(
                phase_number=1,
                title="Telemetry Infrastructure & Virtual Environment Setup",
                objective="Deploy virtual machines running Ubuntu Server (Splunk host) and Windows 10/11 client.",
                tasks=[
                    "Install VirtualBox and configure a private Host-Only network adapter (`192.168.56.0/24`).",
                    "Install Ubuntu Server VM and deploy Splunk Enterprise with default web interface on port 8000.",
                    "Install Windows VM and deploy Microsoft Sysmon with the SwiftOnSecurity modular configuration.",
                    "Install Splunk Universal Forwarder on the Windows VM pointing to the Ubuntu Splunk receiver on port 9997.",
                ],
                technologies_used=["VirtualBox", "Ubuntu Server", "Splunk Enterprise", "Sysmon"],
                expected_output="Live endpoint forwarding Windows security and Sysmon telemetry into Splunk index.",
                verification_method="Run Splunk search `index=* sourcetype=*` and confirm live ingestion of EventCode 1 (Process Creation).",
            ),
            ImplementationPhase(
                phase_number=2,
                title="Network Intrusion Detection Deployment",
                objective="Deploy Snort NIDS to monitor network traffic between virtual machines.",
                tasks=[
                    "Install and configure Snort 3 on the Linux gateway machine.",
                    "Download and configure community detection rules for port scanning and exploit detection.",
                    "Configure Snort alert log forwarding into the Splunk SIEM pipeline.",
                    "Simulate an authorized port scan (`nmap -sS`) and verify Snort alert generation.",
                ],
                technologies_used=["Snort NIDS", "Nmap", "Wireshark"],
                expected_output="Snort actively generating alerts upon detecting network anomalies and forwarding to SIEM.",
                verification_method="Inspect `/var/log/snort/alert` and confirm alert events visible in Splunk dashboard.",
            ),
            ImplementationPhase(
                phase_number=3,
                title="Detection Engineering & MITRE ATT&CK Mapping",
                objective="Author custom Splunk search queries (SPL) and map detection rules to MITRE ATT&CK techniques.",
                tasks=[
                    "Safely execute Atomic Red Team tests (e.g., T1059.001 PowerShell execution, T1087 Account Discovery).",
                    "Author custom SPL queries to detect suspicious PowerShell obfuscation and encoded command lines.",
                    "Build an alert for brute-force logon failures (EventCode 4625 threshold > 5 within 2 minutes).",
                    "Map all authored alerts to corresponding MITRE ATT&CK tactics and techniques.",
                ],
                technologies_used=["Splunk SPL", "Atomic Red Team", "MITRE ATT&CK Navigator"],
                expected_output="Set of 4 verified custom detection rules with documented triggers and false-positive filtering.",
                verification_method="Re-run simulated attack script; verify automatic trigger of custom Splunk alerts within 60 seconds.",
            ),
            ImplementationPhase(
                phase_number=4,
                title="SOC Dashboard Construction & Incident Triage Runbook",
                objective="Build an interactive SOC operations dashboard and draft standard incident response triage playbooks.",
                tasks=[
                    "Construct an operational Splunk dashboard visualizing authentication spikes, top alert categories, and attacked hosts.",
                    "Write an Incident Response Playbook (`playbooks/unauthorized_powershell_triage.md`).",
                    "Extract packet captures using Wireshark for an alert and document key artifacts (source IP, command payload).",
                    "Compile project documentation and sanitize all private hostnames and local IP configurations.",
                ],
                technologies_used=["Splunk Dashboard Studio", "Wireshark", "Markdown"],
                expected_output="Live visual SOC dashboard and actionable step-by-step incident triage runbook.",
                verification_method="Walk through playbook against a simulated alert; verify all triage steps are clear and reproducible.",
            ),
        ]

        structure = [
            ProjectStructureItem(path="README.md", description="Project overview, network topology diagram, telemetry pipeline, and alert summaries."),
            ProjectStructureItem(path="configs/sysmonconfig-export.xml", description="SwiftOnSecurity modular Sysmon configuration used for endpoint telemetry."),
            ProjectStructureItem(path="configs/snort.lua", description="Snort 3 intrusion detection rules and network monitoring parameters."),
            ProjectStructureItem(path="splunk/queries.spl", description="Documented Splunk Search Processing Language queries with performance notes."),
            ProjectStructureItem(path="splunk/dashboards/soc_overview.xml", description="Exported XML definition of the custom Splunk SOC operational dashboard."),
            ProjectStructureItem(path="playbooks/triage_runbook.md", description="Step-by-step analyst triage guide for investigating alerts and isolating endpoints."),
            ProjectStructureItem(path="evidence/simulations/", description="Sanitized logs of Atomic Red Team tests and corresponding Splunk alert triggers."),
        ]

        deliverables = [
            "End-to-end working telemetry pipeline running in isolated virtual machines.",
            "Custom Splunk dashboard visualizing real-time security events and MITRE ATT&CK categories.",
            "Documented library of 4+ custom SPL detection queries with false-positive tuning notes.",
            "Comprehensive Incident Triage Runbook covering verification, containment, and eradication.",
            "Sanitized packet capture analysis illustrating malicious traffic reconstruction in Wireshark.",
            "Professional GitHub repository with network topology diagram and setup instructions.",
        ]

        testing_and_validation = [
            "Execute threat simulations strictly in an isolated host-only virtual network with zero external internet access.",
            "Use Atomic Red Team benign testing commands (such as harmless PowerShell discovery commands).",
            "Validate that log ingestion stays well within Splunk Free 500MB/day quota by filtering noisy events.",
            "Verify all detection queries return zero false positives during normal baseline workstation usage.",
        ]

        outcomes = [
            "Practical mastery of Splunk architecture, indexing, forwarding, and Search Processing Language (SPL).",
            "In-depth comprehension of Windows Event IDs (4624, 4625, 4688) and Sysmon EventCodes (1, 3, 7, 11).",
            "Practical ability to author network intrusion detection rules in Snort.",
            "Real-world experience implementing SOC alert triage procedures aligned with the MITRE ATT&CK framework.",
        ]

        resume_guide = ResumeBulletGuide(
            framework="Action Verb + What You Built + Scale/Technologies + Verifiable Operational Outcome",
            sample_bullets=[
                "Architected a virtualized Security Operations Center pipeline utilizing Splunk Enterprise, Sysmon, and Snort to ingest and correlate multi-source telemetry.",
                "Authored 5 custom Splunk SPL detection rules mapped to MITRE ATT&CK, successfully alerting on brute-force attempts and obfuscated PowerShell execution.",
                "Developed an operational SOC dashboard and analyst triage playbooks, reducing simulated incident triage time and documenting packet-level PCAP analysis with Wireshark.",
            ],
            guidance_notes=(
                "Include these bullets on your resume only once you have configured the forwarder and verified alerts. "
                "Highlight the specific event codes and tools you personally configured."
            ),
        )

        github = [
            "Include a network architecture diagram showing how VMs, Forwarders, and Splunk connect.",
            "Organize queries logically into separate files with descriptive comment headers.",
            "SECURITY WARNING: Exclude real domain credentials, private hostnames, or corporate identifiers.",
            "Include an open-source educational disclaimer.",
        ]

        workflow = [
            {"step": 1, "type": "start", "label": "START"},
            {"step": 2, "type": "phase", "label": "Deploy SIEM Lab & Telemetry Collectors (Splunk/Elasticsearch)"},
            {"step": 3, "type": "phase", "label": "Ingest & Parse System Logs and Network PCAPs"},
            {"step": 4, "type": "phase", "label": "Execute Threat Hunting Queries and Sigma Detection Rules", "is_loop_target": True},
            {
                "step": 5,
                "type": "decision",
                "label": "Was malicious threat activity detected?",
                "no_action": "Adjust detection threshold and refine query filters.",
                "no_target_step": 4,
                "yes_action": "Isolate event telemetry and catalog verified IOCs.",
            },
            {"step": 6, "type": "phase", "label": "Incident Triage & Mitigation Strategy Development"},
            {"step": 7, "type": "phase", "label": "Generate SOC Incident Investigation Report"},
            {"step": 8, "type": "end", "label": "END"},
        ]

        return ProjectImplementationPlan(
            plan_id=plan_id,
            generated_date=generated_date,
            overview=overview,
            skills=skills,
            technology_stack=tech_stack,
            technology_details=tech_details,
            phases=phases,
            project_structure=structure,
            final_deliverables=deliverables,
            testing_and_validation=testing_and_validation,
            learning_outcomes=outcomes,
            resume_documentation_guide=resume_guide,
            github_and_presentation=github,
            project_workflow=workflow,
        )

    @classmethod
    def _build_cloud_security_plan(
        cls,
        plan_id: str,
        generated_date: str,
        role_name: str,
        difficulty: str,
        unmatched_skills: List[str],
        matched_skills: List[str],
    ) -> ProjectImplementationPlan:
        """Cloud Security Engineer primary project."""
        project_title = "Automated Cloud Security Posture & IAM Hardening Assessment"
        target_skills = ["Cloud Security", "AWS / Azure", "IAM Hardening", "Terraform", "Python", "Compliance Audit"]

        existing = [s for s in matched_skills if s in target_skills]
        to_learn = [s for s in target_skills if s not in existing]
        if not to_learn:
            to_learn = ["Prowler CIS Benchmarks", "Terraform Least-Privilege IAM"]

        overview = ProjectOverview(
            project_title=project_title,
            target_role=role_name,
            difficulty=difficulty,
            problem_statement=(
                "Misconfigured Identity and Access Management (IAM) permissions and exposed storage buckets are "
                "leading causes of cloud breaches. Cloud security professionals must be able to audit cloud infrastructure "
                "against CIS Benchmarks and automate least-privilege policy remediation."
            ),
            project_objective=(
                "Deploy a baseline multi-tier cloud infrastructure using Terraform (or LocalStack free cloud emulator), "
                "execute automated CIS benchmark security audits using Prowler, and implement automated Python policy enforcement "
                "to remediate wildcard permissions."
            ),
            relevance_to_role=(
                f"Directly satisfies requirements for {role_name}. Hiring teams require practical demonstration "
                f"of Infrastructure as Code (IaC) security, cloud posture assessment, and IAM zero-trust policy design."
            ),
            weaknesses_addressed=[
                "Insufficient cloud-native security evidence on resume.",
                f"Missing or unverified evidence for role skills: {', '.join(unmatched_skills[:3]) if unmatched_skills else 'Cloud Security, IAM'}.",
                "Need for verifiable automation and Infrastructure as Code deliverables.",
            ],
        )

        skills = SkillsBreakdown(
            existing_skills_applied=existing or ["Linux Administration", "Python Basics"],
            skills_to_be_learned=to_learn,
            all_targeted_skills=target_skills,
        )

        tech_stack = ["LocalStack (Free Local AWS Emulator)", "Terraform", "Prowler (Open Source)", "Python 3 / Boto3", "Git"]
        tech_details = {
            "LocalStack": "Fully functional local cloud emulator allowing complete AWS security testing without incurring cloud fees.",
            "Terraform": "Industry-standard Infrastructure as Code tool to declaratively deploy and modify cloud resources.",
            "Prowler": "Open-source security tool for AWS/Azure security assessments against CIS Foundations Benchmarks.",
            "Python 3 / Boto3": "AWS SDK for Python used to author automated policy auditing and remediation scripts.",
            "Git": "Version control for managing Infrastructure as Code templates and audit reports.",
        }

        phases = [
            ImplementationPhase(
                phase_number=1,
                title="Infrastructure Deployment & Local Cloud Emulation",
                objective="Deploy simulated cloud resources (IAM roles, S3 buckets, VPC) locally via LocalStack and Terraform.",
                tasks=[
                    "Install and launch LocalStack via Docker (`docker run -d -p 4566:4566 localstack/localstack`).",
                    "Write Terraform configuration deploying 3 IAM roles (intentionally overprivileged) and 2 S3 buckets.",
                    "Apply Terraform against LocalStack endpoint: `terraform apply`.",
                    "Verify emulated cloud resources via AWS CLI pointing to localhost endpoint.",
                ],
                technologies_used=["LocalStack", "Terraform", "Docker"],
                expected_output="Emulated cloud environment containing baseline infrastructure ready for security auditing.",
                verification_method="Execute `aws --endpoint-url=http://localhost:4566 iam list-roles` to confirm live resource state.",
            ),
            ImplementationPhase(
                phase_number=2,
                title="Automated Security Posture Audit against CIS Benchmarks",
                objective="Execute Prowler scans to identify misconfigurations, wildcard IAM permissions, and unencrypted assets.",
                tasks=[
                    "Configure Prowler to evaluate local cloud environment against CIS AWS Foundations Benchmark.",
                    "Execute full automated assessment; export findings to JSON and HTML formats.",
                    "Categorize findings by severity (Critical, High, Medium, Low).",
                    "Identify specific policy violations (e.g., `s3:GetObject` with `Resource: *`, lack of bucket encryption).",
                ],
                technologies_used=["Prowler", "Bash", "Python"],
                expected_output="Comprehensive cloud posture audit report detailing all failing CIS benchmark controls.",
                verification_method="Review Prowler HTML dashboard; confirm identified vulnerabilities match configured misconfigurations.",
            ),
            ImplementationPhase(
                phase_number=3,
                title="Automated Policy Remediation with Python & Boto3",
                objective="Author automated Python scripts to parse Prowler outputs and enforce least-privilege policies.",
                tasks=[
                    "Write Python script (`remediate_iam.py`) using Boto3 to inspect attached role policies.",
                    "Identify and replace wildcard `\"Action\": \"*\"` statements with scoped, role-specific action lists.",
                    "Enforce default server-side encryption (SSE-S3) and public access blocking on all storage buckets.",
                    "Implement pre-commit git hook checking Terraform templates for security regressions using `tfsec`.",
                ],
                technologies_used=["Python 3", "Boto3", "tfsec"],
                expected_output="Automated remediation script and hardened Terraform templates eliminating all high-severity findings.",
                verification_method="Run remediation script; re-run Prowler and verify 100% resolution of target misconfigurations.",
            ),
            ImplementationPhase(
                phase_number=4,
                title="Audit Reporting & Documentation",
                objective="Draft an executive cloud compliance audit summary and technical remediation report.",
                tasks=[
                    "Document Before vs. After security metrics (e.g., initial compliance: 42% -> post-remediation: 96%).",
                    "Compile technical remediation guide for cloud infrastructure engineers.",
                    "Clean up and commit reusable, secure Terraform modules to GitHub repository.",
                ],
                technologies_used=["Markdown", "Git"],
                expected_output="Professional Cloud Compliance Report with Before/After score comparison and code repository.",
                verification_method="Verify documentation accuracy and ensure zero hardcoded API keys or secret credentials.",
            ),
        ]

        structure = [
            ProjectStructureItem(path="README.md", description="Project overview, architecture diagram, CIS benchmark summary, and setup instructions."),
            ProjectStructureItem(path="terraform/baseline_infrastructure.tf", description="Terraform configuration deploying initial test cloud resources."),
            ProjectStructureItem(path="terraform/hardened_modules/", description="Remediated, reusable least-privilege Terraform modules."),
            ProjectStructureItem(path="scripts/audit_prowler.sh", description="Automated shell script executing Prowler security scans."),
            ProjectStructureItem(path="scripts/remediate_iam.py", description="Python Boto3 script enforcing zero-trust IAM boundaries automatically."),
            ProjectStructureItem(path="reports/cis_benchmark_initial.json", description="Initial scan results showing identified cloud misconfigurations."),
            ProjectStructureItem(path="reports/cis_benchmark_post_remediation.json", description="Post-remediation scan results verifying 100% compliance."),
            ProjectStructureItem(path=".gitignore", description="Ensures no AWS credentials, state files, or local keys are committed."),
        ]

        deliverables = [
            "Modular Terraform code deploying both baseline and hardened cloud infrastructure.",
            "Automated Python remediation script utilizing Boto3 for IAM and S3 hardening.",
            "Comprehensive CIS Benchmark Audit Report showing measurable compliance improvement.",
            "Pre-commit security verification integration using tfsec.",
            "Professional GitHub repository with complete documentation and architecture overview.",
        ]

        testing_and_validation = [
            "Test exclusively against LocalStack emulator or dedicated sandbox cloud account with billing alerts set to $0.",
            "Verify all Boto3 remediation scripts in dry-run mode before executing live state modifications.",
            "Confirm that hardened IAM policies still allow required legitimate application operations without errors.",
        ]

        outcomes = [
            "Deep practical experience with AWS IAM policy structure, resource boundaries, and least-privilege design.",
            "Mastery of Infrastructure as Code security using Terraform and static analysis scanners (tfsec).",
            "Proficiency in cloud security assessment tools including Prowler and CIS Foundations Benchmarks.",
            "Hands-on Python automation for continuous cloud security compliance and remediation.",
        ]

        resume_guide = ResumeBulletGuide(
            framework="Action Verb + What You Hardened + Tools Used + Quantifiable Compliance Metric",
            sample_bullets=[
                "Engineered automated cloud compliance audits utilizing Prowler and LocalStack, evaluating cloud infrastructure against CIS AWS Benchmarks.",
                "Authored Python Boto3 automation to remediate 15 overprivileged IAM policies and enforce least-privilege role boundaries.",
                "Hardened multi-tier Terraform modules by integrating tfsec static analysis, achieving a 96% compliance score on post-audit verification.",
            ],
            guidance_notes=(
                "Document actual results achieved. Be ready to explain how your Boto3 scripts resolved wildcard permissions in an interview."
            ),
        )

        github = [
            "Provide detailed instructions for replicating the test environment using free LocalStack (zero cloud costs).",
            "Include before/after terminal screenshots showing Prowler audit results.",
            "STRICT CAUTION: Never publish real AWS Access Keys, Secret Keys, or Account IDs.",
        ]

        workflow = [
            {"step": 1, "type": "start", "label": "START"},
            {"step": 2, "type": "phase", "label": "Provision Isolated Cloud Environment (Terraform / LocalStack)"},
            {"step": 3, "type": "phase", "label": "Execute Automated Security Audits (ScoutSuite / Prowler)"},
            {"step": 4, "type": "phase", "label": "Implement Cloud Hardening & Least-Privilege IAM Policies", "is_loop_target": True},
            {
                "step": 5,
                "type": "decision",
                "label": "Are cloud security posture benchmarks satisfied?",
                "no_action": "Review compliance gaps and remediate configuration drift.",
                "no_target_step": 4,
                "yes_action": "Verify zero high-risk findings and establish baseline.",
            },
            {"step": 6, "type": "phase", "label": "Configure CloudTrail & GuardDuty Monitoring Guardrails"},
            {"step": 7, "type": "phase", "label": "Generate Cloud Security Assessment & Audit Report"},
            {"step": 8, "type": "end", "label": "END"},
        ]

        return ProjectImplementationPlan(
            plan_id=plan_id,
            generated_date=generated_date,
            overview=overview,
            skills=skills,
            technology_stack=tech_stack,
            technology_details=tech_details,
            phases=phases,
            project_structure=structure,
            final_deliverables=deliverables,
            testing_and_validation=testing_and_validation,
            learning_outcomes=outcomes,
            resume_documentation_guide=resume_guide,
            github_and_presentation=github,
            project_workflow=workflow,
        )

    @classmethod
    def _build_appsec_plan(
        cls,
        plan_id: str,
        generated_date: str,
        role_name: str,
        difficulty: str,
        unmatched_skills: List[str],
        matched_skills: List[str],
    ) -> ProjectImplementationPlan:
        """Application Security Engineer primary project."""
        project_title = "Automated DevSecOps Pipeline & Secure Code Review Lab"
        target_skills = ["Application Security", "SAST / DAST", "OWASP Top 10", "Python", "CI/CD Security", "Vulnerability Remediation"]

        existing = [s for s in matched_skills if s in target_skills]
        to_learn = [s for s in target_skills if s not in existing]
        if not to_learn:
            to_learn = ["Semgrep SAST Rule Writing", "ZAP Baseline Scanning"]

        overview = ProjectOverview(
            project_title=project_title,
            target_role=role_name,
            difficulty=difficulty,
            problem_statement=(
                "Vulnerabilities introduced during software development are costly to patch in production. "
                "Application security engineers must be able to integrate automated security scanning (SAST/DAST/SCA) "
                "into development pipelines and collaborate with software engineers to implement secure coding practices."
            ),
            project_objective=(
                "Build a complete automated CI/CD DevSecOps pipeline using GitHub Actions, Semgrep (SAST), "
                "Trivy (SCA/Container scanning), and OWASP ZAP (DAST), identify vulnerabilities in a sample web API, "
                "and patch root causes in source code."
            ),
            relevance_to_role=(
                f"Essential for {role_name}. Hiring teams require practical evidence that you can shift security left "
                f"by embedding automated gates and providing developer-friendly vulnerability remediation."
            ),
            weaknesses_addressed=[
                "Missing practical DevSecOps and automated code review evidence on resume.",
                f"Missing or unverified evidence for role skills: {', '.join(unmatched_skills[:3]) if unmatched_skills else 'SAST, DevSecOps'}.",
                "Need for verifiable source-code patching and pipeline automation deliverables.",
            ],
        )

        skills = SkillsBreakdown(
            existing_skills_applied=existing or ["Python Basics", "Git Version Control"],
            skills_to_be_learned=to_learn,
            all_targeted_skills=target_skills,
        )

        tech_stack = ["GitHub Actions", "Semgrep (Open Source SAST)", "Trivy (Container & Dependency Scanner)", "OWASP ZAP", "Python / FastAPI", "Docker"]
        tech_details = {
            "Semgrep": "Fast, lightweight open-source static analysis engine for finding bugs and enforcing security standards.",
            "Trivy": "Comprehensive security scanner for vulnerabilities in container images, file systems, and Git repositories.",
            "OWASP ZAP": "Open-source web application security scanner for automated dynamic application security testing.",
            "GitHub Actions": "CI/CD automation platform for executing security testing jobs on every code push or pull request.",
            "FastAPI / Python": "Modern web framework used to build and secure a RESTful API test target.",
        }

        phases = [
            ImplementationPhase(
                phase_number=1,
                title="Target API Construction & Vulnerability Seeding",
                objective="Deploy a sample Python FastAPI web application containing known OWASP vulnerabilities for testing.",
                tasks=[
                    "Build a lightweight FastAPI application with SQLite database backend.",
                    "Incorporate realistic intentional security flaws (raw SQL queries, hardcoded dummy secrets, outdated dependencies).",
                    "Containerize the application using Docker.",
                    "Verify target API functionality using curl or Postman on localhost.",
                ],
                technologies_used=["Python", "FastAPI", "Docker", "SQLite"],
                expected_output="Working containerized API with predictable vulnerability test cases.",
                verification_method="Query endpoints and confirm responses and logging in local terminal.",
            ),
            ImplementationPhase(
                phase_number=2,
                title="SAST & SCA Pipeline Integration",
                objective="Configure automated static analysis and dependency vulnerability scanning in GitHub Actions.",
                tasks=[
                    "Create `.github/workflows/security_pipeline.yml` to trigger on every pull request.",
                    "Add Semgrep SAST step scanning Python source code for SQL injection and unsafe deserialization.",
                    "Add Trivy step scanning `requirements.txt` for known vulnerable package versions (CVEs).",
                    "Configure pipeline to fail build if Critical or High severity flaws are detected.",
                ],
                technologies_used=["GitHub Actions", "Semgrep", "Trivy"],
                expected_output="Automated CI/CD security gate blocking pull requests containing high-severity vulnerabilities.",
                verification_method="Push unpatched code; verify GitHub Action fails and generates detailed vulnerability report.",
            ),
            ImplementationPhase(
                phase_number=3,
                title="Vulnerability Remediation & Secure Coding Implementation",
                objective="Remediate identified flaws in source code using secure coding best practices.",
                tasks=[
                    "Refactor raw SQL strings to use parameterized queries and SQLAlchemy ORM.",
                    "Migrate hardcoded configuration values to environment variables loaded via Pydantic settings.",
                    "Update vulnerable Python packages in `requirements.txt` to patched versions.",
                    "Author custom Semgrep rules (`rules/custom_security.yml`) preventing future regressions.",
                ],
                technologies_used=["Python", "SQLAlchemy", "Semgrep Rule Engine"],
                expected_output="Remediated source code passing all SAST and SCA scanning gates with 0 High/Critical findings.",
                verification_method="Push patched code; confirm GitHub Action runs cleanly and passes all security checks.",
            ),
            ImplementationPhase(
                phase_number=4,
                title="DAST Scanning & DevSecOps Documentation",
                objective="Execute dynamic security testing with OWASP ZAP and compile DevSecOps implementation guide.",
                tasks=[
                    "Configure OWASP ZAP baseline scan against running container in CI pipeline.",
                    "Document developer guidelines for writing secure REST APIs.",
                    "Draft comprehensive project summary highlighting vulnerability detection rate and resolution process.",
                ],
                technologies_used=["OWASP ZAP", "Markdown", "Git"],
                expected_output="Clean DAST scan report and comprehensive developer security guidelines.",
                verification_method="Review final pipeline run logs; verify end-to-end automated security verification passes.",
            ),
        ]

        structure = [
            ProjectStructureItem(path="README.md", description="Project overview, DevSecOps pipeline architecture diagram, and setup instructions."),
            ProjectStructureItem(path=".github/workflows/security.yml", description="GitHub Actions workflow file automating Semgrep, Trivy, and ZAP scanning."),
            ProjectStructureItem(path="app/main.py", description="Hardened FastAPI application implementing secure coding standards."),
            ProjectStructureItem(path="rules/custom_semgrep.yml", description="Custom SAST rules authored to enforce organization security policies."),
            ProjectStructureItem(path="docs/remediation_log.md", description="Detailed log of identified vulnerabilities, CVE IDs, and applied code fixes."),
            ProjectStructureItem(path="docs/developer_security_guidelines.md", description="Actionable security guide for development teams."),
            ProjectStructureItem(path=".gitignore", description="Excludes local databases, virtual environments, and sensitive test logs."),
        ]

        deliverables = [
            "Functional GitHub Actions CI/CD security workflow automating SAST, SCA, and DAST.",
            "Hardened Python FastAPI codebase demonstrating secure coding patterns.",
            "Custom Semgrep rule definitions authored to catch project-specific security risks.",
            "Comprehensive Vulnerability Remediation Log detailing before/after code snippets.",
            "Professional GitHub repository showcasing automated security testing gates.",
        ]

        testing_and_validation = [
            "Run all SAST and dependency tests locally using Semgrep and Trivy CLI before pushing to GitHub.",
            "Ensure simulated vulnerabilities are strictly isolated in non-production test repositories.",
            "Verify that custom Semgrep rules trigger accurately without generating false-positive alerts on clean code.",
        ]

        outcomes = [
            "Practical mastery of DevSecOps pipeline construction and automated security gating in GitHub Actions.",
            "Hands-on expertise conducting Static Application Security Testing (SAST) and authoring Semgrep rules.",
            "In-depth understanding of Software Composition Analysis (SCA) and container image scanning with Trivy.",
            "Ability to refactor vulnerable code into secure, defensive implementations in Python.",
        ]

        resume_guide = ResumeBulletGuide(
            framework="Action Verb + What You Built + Scanning Tools + Security Metric / Outcome",
            sample_bullets=[
                "Constructed an automated DevSecOps CI/CD pipeline using GitHub Actions, Semgrep (SAST), and Trivy (SCA) to enforce security gates on code commits.",
                "Authored custom Semgrep rules to detect SQL injection and hardcoded secrets, automatically blocking high-severity vulnerabilities before deployment.",
                "Remediated 8 application security vulnerabilities by refactoring source code to parameterized queries and updating vulnerable dependencies.",
            ],
            guidance_notes=(
                "Only list these bullets once your GitHub Actions workflow is successfully passing on your personal repository."
            ),
        )

        github = [
            "Include a pipeline diagram showing code commit -> GitHub Actions -> Semgrep/Trivy -> passing build.",
            "Add badges to your README showing passing security workflow status.",
            "STRICT CAUTION: Never include real API tokens, production credentials, or confidential code.",
        ]

        workflow = [
            {"step": 1, "type": "start", "label": "START"},
            {"step": 2, "type": "phase", "label": "Configure CI/CD Pipeline & GitHub Actions Runner"},
            {"step": 3, "type": "phase", "label": "Integrate SAST and Dependency Vulnerability Scanners (Semgrep, Snyk)"},
            {"step": 4, "type": "phase", "label": "Execute Dynamic Security Testing & Container Scanning (ZAP, Trivy)", "is_loop_target": True},
            {
                "step": 5,
                "type": "decision",
                "label": "Did build satisfy security quality gates?",
                "no_action": "Break pipeline build, alert engineer, and patch vulnerabilities.",
                "no_target_step": 4,
                "yes_action": "Approve build artifact promotion to secure registry.",
            },
            {"step": 6, "type": "phase", "label": "Implement Automated Vulnerability Remediation Workflows"},
            {"step": 7, "type": "phase", "label": "Generate DevSecOps Pipeline Security Verification Report"},
            {"step": 8, "type": "end", "label": "END"},
        ]

        return ProjectImplementationPlan(
            plan_id=plan_id,
            generated_date=generated_date,
            overview=overview,
            skills=skills,
            technology_stack=tech_stack,
            technology_details=tech_details,
            phases=phases,
            project_structure=structure,
            final_deliverables=deliverables,
            testing_and_validation=testing_and_validation,
            learning_outcomes=outcomes,
            resume_documentation_guide=resume_guide,
            github_and_presentation=github,
            project_workflow=workflow,
        )

    @classmethod
    def _build_network_security_plan(
        cls,
        plan_id: str,
        generated_date: str,
        role_name: str,
        difficulty: str,
        unmatched_skills: List[str],
        matched_skills: List[str],
    ) -> ProjectImplementationPlan:
        """Network Security / General Cybersecurity primary project."""
        project_title = "Enterprise Network Hardening & Vulnerability Remediation Lab"
        target_skills = ["Network Security", "Vulnerability Assessment", "Linux Hardening", "Nmap", "Wireshark", "iptables/Firewall"]

        existing = [s for s in matched_skills if s in target_skills]
        to_learn = [s for s in target_skills if s not in existing]
        if not to_learn:
            to_learn = ["Stateful Firewall Configuration", "OpenVAS / Greenbone Assessment"]

        overview = ProjectOverview(
            project_title=project_title,
            target_role=role_name,
            difficulty=difficulty,
            problem_statement=(
                "Default system configurations and unmonitored network ports expose critical infrastructure to lateral "
                "movement and unauthorized access. Network security engineers must be able to discover network services, "
                "evaluate vulnerabilities, and configure stateful firewall rules to enforce defense-in-depth."
            ),
            project_objective=(
                "Configure an isolated multi-node virtual network, execute comprehensive port and vulnerability scanning "
                "using Nmap and OpenVAS/Nessus, implement defensive host hardening (UFW/iptables, SSH key authentication), "
                "and verify post-remediation security posture."
            ),
            relevance_to_role=(
                f"Directly relevant to {role_name}. Validates foundational network engineering, protocol analysis, "
                f"vulnerability assessment, and hands-on Linux system defense."
            ),
            weaknesses_addressed=[
                "Insufficient hands-on network defense and vulnerability assessment evidence.",
                f"Missing or unverified evidence for role skills: {', '.join(unmatched_skills[:3]) if unmatched_skills else 'Network Security, Nmap'}.",
                "Need for verifiable firewall configuration and network traffic analysis deliverables.",
            ],
        )

        skills = SkillsBreakdown(
            existing_skills_applied=existing or ["TCP/IP Fundamentals", "Basic Command Line"],
            skills_to_be_learned=to_learn,
            all_targeted_skills=target_skills,
        )

        tech_stack = ["VirtualBox", "Ubuntu Server / Debian", "Nmap", "Wireshark", "iptables / UFW", "OpenVAS / Greenbone Community"]
        tech_details = {
            "VirtualBox": "Free hypervisor platform used to host isolated virtual internal networks.",
            "Ubuntu Server": "Enterprise Linux distribution configured as target host and bastion gateway.",
            "Nmap": "Network discovery and vulnerability scanning tool used for port scanning and OS detection.",
            "Wireshark": "Network protocol analyzer used to inspect packet flows and verify encryption.",
            "UFW / iptables": "Linux stateful packet inspection firewall used to enforce ingress/egress filtering.",
            "OpenVAS": "Open-source vulnerability scanner evaluating systems against known CVE vulnerability databases.",
        }

        phases = [
            ImplementationPhase(
                phase_number=1,
                title="Virtual Network Topology & Host Deployment",
                objective="Construct an isolated virtual network containing a gateway firewall and two internal server nodes.",
                tasks=[
                    "Create an internal virtual network in VirtualBox (`10.0.10.0/24`).",
                    "Deploy two Ubuntu Server VMs: Node-A (Web/SSH) and Node-B (Internal Database).",
                    "Configure static IP addressing and verify intra-node network connectivity via ping.",
                    "Establish baseline traffic captures with Wireshark to verify packet flow.",
                ],
                technologies_used=["VirtualBox", "Ubuntu Server", "Wireshark"],
                expected_output="Configured virtual network with documented IP allocation and network connectivity.",
                verification_method="Verify end-to-end ping and inspect packet headers in Wireshark.",
            ),
            ImplementationPhase(
                phase_number=2,
                title="Network Enumeration & Vulnerability Baseline",
                objective="Execute systematic port and vulnerability scanning to document open attack vectors.",
                tasks=[
                    "Run Nmap SYN scan (`nmap -sS -sV -O -p- 10.0.10.0/24`) to discover active services.",
                    "Execute Nmap Vulnerability Scripts (`nmap --script vuln`) against discovered web services.",
                    "Deploy OpenVAS/Greenbone scanner to generate an initial vulnerability baseline report.",
                    "Catalog identified risks: open Telnet/FTP ports, plaintext HTTP, and weak SSH cipher suites.",
                ],
                technologies_used=["Nmap", "OpenVAS", "Bash"],
                expected_output="Pre-remediation vulnerability inventory detailing all unencrypted and unhardened ports.",
                verification_method="Inspect Nmap XML export and OpenVAS findings report.",
            ),
            ImplementationPhase(
                phase_number=3,
                title="Defense-in-Depth Hardening & Firewall Enforcement",
                objective="Remediate identified vulnerabilities by disabling insecure services and configuring stateful firewall rules.",
                tasks=[
                    "Disable legacy insecure protocols (Telnet, FTP, rsh) and enforce SSHv2 with Ed25519 key authentication only.",
                    "Configure UFW/iptables to deny all incoming traffic by default, permitting only authorized ports (`22`, `443`).",
                    "Implement rate-limiting on SSH port to prevent automated brute-force attempts.",
                    "Harden Linux kernel network parameters via `/etc/sysctl.conf` (disable IP forwarding, protect against SYN flood).",
                ],
                technologies_used=["UFW", "iptables", "sysctl", "SSH"],
                expected_output="Hardened host configurations enforcing zero unnecessary open ports and strict firewall boundaries.",
                verification_method="Verify firewall rules with `sudo ufw status verbose` and test connection drops from unauthorized hosts.",
            ),
            ImplementationPhase(
                phase_number=4,
                title="Validation Scanning & Security Assessment Report",
                objective="Perform post-remediation validation scanning to prove measurable risk reduction.",
                tasks=[
                    "Re-scan network with Nmap to confirm all unneeded ports are now closed or filtered.",
                    "Capture network traffic in Wireshark to verify all management sessions are encrypted (SSH).",
                    "Draft formal Network Security Assessment and Hardening Report.",
                    "Compile reusable hardening scripts into GitHub repository.",
                ],
                technologies_used=["Nmap", "Wireshark", "Markdown", "Git"],
                expected_output="Comprehensive assessment report with Before vs After port status and firewall configuration scripts.",
                verification_method="Verify post-remediation scan reveals zero high-risk unencrypted protocols.",
            ),
        ]

        structure = [
            ProjectStructureItem(path="README.md", description="Project overview, network topology diagram, hardening summary, and test instructions."),
            ProjectStructureItem(path="scripts/setup_network.sh", description="Shell script setting up static IP parameters and routing in virtual lab."),
            ProjectStructureItem(path="scripts/apply_hardening.sh", description="Automated Linux hardening script configuring UFW, SSH, and sysctl."),
            ProjectStructureItem(path="configs/ufw_rules.txt", description="Documented stateful firewall rules with rationale for each permitted port."),
            ProjectStructureItem(path="configs/sshd_config", description="Hardened SSH daemon configuration enforcing key-only authentication."),
            ProjectStructureItem(path="reports/nmap_baseline_scan.txt", description="Initial Nmap scan results showing vulnerable open services."),
            ProjectStructureItem(path="reports/nmap_post_hardening_scan.txt", description="Post-hardening scan results proving verified port closure."),
            ProjectStructureItem(path=".gitignore", description="Excludes local private keys, PCAP captures with private data, and temp logs."),
        ]

        deliverables = [
            "Complete network architecture documentation and VirtualBox topology specification.",
            "Automated Linux hardening shell script implementing defense-in-depth controls.",
            "Documented stateful firewall ruleset enforcing least-privilege traffic flow.",
            "Before-and-after vulnerability reports proving closure of security gaps.",
            "Professional GitHub repository with clean README and network topology diagram.",
        ]

        testing_and_validation = [
            "Execute all port and vulnerability scans strictly within the isolated VirtualBox host-only network.",
            "Verify that firewall rule modifications do not permanently lock out management SSH access before saving.",
            "Confirm that SSH key authentication strictly rejects password-based login attempts.",
        ]

        outcomes = [
            "Hands-on expertise configuring stateful Linux host firewalls with iptables and UFW.",
            "Practical mastery of network discovery and vulnerability scanning with Nmap and OpenVAS.",
            "Deep comprehension of TCP/IP handshakes, packet headers, and encrypted protocols in Wireshark.",
            "Experience authoring professional network hardening documentation and automation scripts.",
        ]

        resume_guide = ResumeBulletGuide(
            framework="Action Verb + Network Area Hardened + Security Tools Used + Verifiable Defense Metric",
            sample_bullets=[
                "Configured a multi-node virtualized network environment in VirtualBox, conducting systematic port discovery and vulnerability scanning with Nmap.",
                "Enforced defense-in-depth Linux host hardening across 2 servers, disabling legacy services and deploying stateful UFW firewall rules.",
                "Hardened SSH daemon configurations with Ed25519 key authentication and SYN-flood protection, verifying complete attack surface reduction via post-hardening Nmap scans.",
            ],
            guidance_notes=(
                "Only list these bullets once you have verified the post-hardening Nmap scans on your personal lab."
            ),
        )

        github = [
            "Include an ASCII or visual diagram illustrating the virtual network topology.",
            "Document step-by-step commands for running the hardening script safely in an Ubuntu VM.",
            "STRICT CAUTION: Never commit private SSH keys (`id_ed25519`) or confidential passwords.",
        ]

        workflow = [
            {"step": 1, "type": "start", "label": "START"},
            {"step": 2, "type": "phase", "label": "Virtual Network Setup"},
            {"step": 3, "type": "phase", "label": "Deploy Ubuntu Server VMs"},
            {"step": 4, "type": "phase", "label": "Configure Network and Verify Connectivity"},
            {"step": 5, "type": "phase", "label": "Nmap Reconnaissance"},
            {"step": 6, "type": "phase", "label": "OpenVAS Vulnerability Assessment"},
            {"step": 7, "type": "phase", "label": "Linux Hardening and Firewall Configuration", "is_loop_target": True},
            {"step": 8, "type": "phase", "label": "Post-Hardening Security Validation"},
            {
                "step": 9,
                "type": "decision",
                "label": "Are security requirements satisfied?",
                "no_action": "Review findings and perform further hardening.",
                "no_target_step": 7,
                "yes_action": "Document verified results.",
            },
            {"step": 10, "type": "phase", "label": "Generate Security Assessment Report"},
            {"step": 11, "type": "end", "label": "END"},
        ]

        return ProjectImplementationPlan(
            plan_id=plan_id,
            generated_date=generated_date,
            overview=overview,
            skills=skills,
            technology_stack=tech_stack,
            technology_details=tech_details,
            phases=phases,
            project_structure=structure,
            final_deliverables=deliverables,
            testing_and_validation=testing_and_validation,
            learning_outcomes=outcomes,
            resume_documentation_guide=resume_guide,
            github_and_presentation=github,
            project_workflow=workflow,
        )
