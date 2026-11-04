"""Standardized sample candidate data for ATS resume template previews.

Provides realistic, verifiable cybersecurity profile data used exclusively for
previewing resume layouts in the Template Gallery without modifying live candidate state.
"""

from typing import Dict, Any, List
from app.projects.generator import EnhancedResumeContent


SAMPLE_PREVIEW_CONTENT = EnhancedResumeContent(
    candidate_name="Jordan Hayes",
    contact_header="jordan.hayes@cybersec.io | +1 (555) 438-9201 | San Francisco, CA | linkedin.com/in/jordanhayes-sec | github.com/jordanhayes",
    contact_details={
        "email": "jordan.hayes@cybersec.io",
        "phone": "+1 (555) 438-9201",
        "location": "San Francisco, CA",
        "linkedin": "https://linkedin.com/in/jordanhayes-sec",
        "github": "https://github.com/jordanhayes",
    },
    professional_headline="Cybersecurity Specialist & Network Defense Engineer",
    professional_summary=(
        "Results-driven Cybersecurity Specialist with hands-on experience in vulnerability assessment, "
        "network penetration testing, and enterprise host hardening. Proficient in automated network "
        "reconnaissance with Nmap, protocol packet analysis via Wireshark, and defensive firewall engineering. "
        "Proven track record eliminating critical misconfigurations across Linux and cloud environments."
    ),
    technical_skills_grouped={
        "Cybersecurity Tools": ["Wireshark", "Nmap", "Burp Suite", "Metasploit", "OpenVAS", "Nessus", "OWASP ZAP", "Snort"],
        "Security Concepts": ["Network Security", "Application Security", "Penetration Testing", "Vulnerability Assessment", "Incident Response"],
        "Programming Languages": ["Python", "Bash", "SQL", "C/C++", "PowerShell"],
        "Operating Systems": ["Linux", "Ubuntu", "Windows Server", "Kali Linux"],
        "Frameworks & Libraries": ["FastAPI", "React.js", "Scapy", "Paramiko", "Flask"],
        "Databases": ["PostgreSQL", "Redis", "MySQL"],
        "Cloud & DevOps": ["Docker", "Kubernetes", "AWS", "Terraform", "Git", "CI/CD"],
        "Networking Technologies": ["TCP/IP", "DNS", "TLS/SSL", "VLAN Segmentation", "Firewall Filtering"],
    },
    experience=[
        {
            "job_title": "Security Operations & Vulnerability Analyst",
            "company": "Vanguard Cyber Defense Corp",
            "location": "San Francisco, CA",
            "start_date": "June 2022",
            "end_date": "Present",
            "responsibilities": [
                "Conducted systematic vulnerability assessments across 60+ internal network endpoints using Nmap and OpenVAS.",
                "Triaged security alerts and analyzed packet captures in Wireshark to investigate anomalous protocol traffic flows.",
                "Configured stateful Linux host firewalls with UFW and iptables, reducing unauthorized exposure by 75%.",
                "Automated log parsing and threat notification pipelines using custom Python and Bash scripts.",
            ],
        },
        {
            "job_title": "Junior Systems & Network Administrator",
            "company": "Pacific Infrastructure Solutions",
            "location": "San Jose, CA",
            "start_date": "August 2020",
            "end_date": "May 2022",
            "responsibilities": [
                "Administered 25+ Ubuntu Linux and Windows server nodes, enforcing SSH key-only authentication and patch updates.",
                "Monitored internal subnet connectivity, routing tables, and VLAN segmentation in testing environments.",
                "Documented standard operating procedures for incident escalation and server backup validation.",
            ],
        },
    ],
    internships=[],
    projects=[
        {
            "title": "Enterprise Network Hardening & Vulnerability Remediation Lab",
            "status": "Completed",
            "technologies": ["VirtualBox", "Ubuntu Server", "Nmap", "OpenVAS", "UFW", "Wireshark"],
            "github_url": "https://github.com/jordanhayes/network-hardening-lab",
            "bullets": [
                "Deployed isolated multi-node virtual environment simulating enterprise subnet topologies and host services.",
                "Conducted automated network port scans with Nmap and vulnerability auditing via OpenVAS to establish security baselines.",
                "Enforced least-privilege host defense by configuring stateful UFW firewall rules, eliminating vulnerable service exposures.",
                "Validated remediation effectiveness through post-hardening verification scans and Wireshark protocol packet capture analysis.",
            ],
            "description": "Configured an isolated multi-node virtual lab to execute systematic port discovery with Nmap and OpenVAS, enforcing least-privilege host defense.",
            "outcomes": "Remediated critical misconfigurations, enforced stateful firewall filtering, and verified attack surface elimination via post-hardening scans.",
        },
        {
            "title": "Web Application Security Testing & Automated Scanner",
            "status": "Completed",
            "technologies": ["Python", "Burp Suite", "OWASP Juice Shop", "Docker", "Requests"],
            "github_url": "https://github.com/jordanhayes/web-security-scanner",
            "bullets": [
                "Engineered modular Python scanning script evaluating web endpoints against OWASP Top 10 vulnerabilities.",
                "Configured Burp Suite upstream proxies to intercept and fuzz HTTP request parameters in containerized test environments.",
                "Identified and verified SQL Injection and IDOR vulnerabilities across authentication workflows and API routes.",
                "Authored structured remediation documentation detailing CVSS v3.1 severity scores and mitigation code samples.",
            ],
            "description": "Engineered an automated Python scanning tool evaluating web application endpoints against OWASP Top 10 vulnerabilities.",
            "outcomes": "Detected and verified SQL Injection and IDOR vulnerabilities, authoring comprehensive CVSS v3.1 severity reports.",
        },
    ],
    education=[
        {
            "degree": "Bachelor of Science in Computer Science & Information Security",
            "institution": "California State University",
            "graduation_year": "2020",
            "field_of_study": "Computer Science",
            "location": "Long Beach, CA",
        }
    ],
    certifications=[
        "CompTIA Security+ (SY0-601)",
        "Certified Ethical Hacker (CEH v12)",
        "AWS Certified Cloud Practitioner",
    ],
    achievements=[
        "1st Place Winner - Regional Collegiate Cyber Defense Competition (CCDC) 2020",
        "Dean's Honor List for Academic Excellence (4 Consecutive Semesters)",
    ],
    confirmed_skills_included=["Nmap", "Wireshark", "Burp Suite", "Linux/Ubuntu", "Python"],
    unverified_skills_excluded=[],
    pursuing_certifications=[],
    approved_improvements_applied=[
        "Formatted technical skills into prioritized ATS categories",
        "Enhanced project bullets with verifiable metrics and tools",
    ],
    sections_rewritten=["Professional Summary", "Technical Skills", "Key Projects"],
    future_learning_recommendations=[],
    pending_confirmations=[],
    generator_mode="preview_generator",
    attempt_number=1,
)

