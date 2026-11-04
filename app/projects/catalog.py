"""Authoritative Domain-Based Project Recommendation Catalog and Workflow Specifications for FUTRSEC.

Provides exactly five distinct, industry-grade practical projects for each supported domain:
1. Cybersecurity
2. Data Science & Machine Learning
3. Cloud & DevOps
4. Full Stack Web Development

Each project is accompanied by its comprehensive metadata, prerequisites, learning objectives,
implementation phases, testing plans, deliverables, and a complete node-and-branch workflow definition.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import json
import logging
from app.database.connection import db_manager

logger = logging.getLogger("futrsec.catalog")


class WorkflowNode(BaseModel):
    id: str
    label: str
    type: str  # 'start' | 'process' | 'decision' | 'end'
    description: str
    detail: Optional[str] = None
    next_node: Optional[str] = None
    yes_next: Optional[str] = None
    no_next: Optional[str] = None
    yes_label: Optional[str] = "YES"
    no_label: Optional[str] = "NO"


class ProjectCatalogItem(BaseModel):
    project_id: str
    domain: str
    project_title: str
    difficulty_level: str  # 'Beginner' | 'Intermediate' | 'Advanced'
    description: str
    learning_objectives: List[str]
    required_technologies: List[str]
    prerequisites: List[str]
    implementation_phases: List[Dict[str, Any]]
    expected_deliverables: List[str]
    testing_validation_plan: List[str]
    project_workflow: List[Dict[str, Any]]
    skills_demonstrated: List[str]


# ==============================================================================
# 1. CYBERSECURITY DOMAIN (5 DISTINCT PROJECTS)
# ==============================================================================

CYBERSECURITY_PROJECTS: List[Dict[str, Any]] = [
    {
        "project_id": "CS-01",
        "domain": "Cybersecurity",
        "project_title": "Web Application Security Testing Lab & Vulnerability Remediation",
        "difficulty_level": "Intermediate",
        "description": "Deploy an isolated local web security testing environment using Docker to assess OWASP Top 10 vulnerabilities (SQLi, XSS, Broken Access Control), author automated proof-of-concept exploits, and compile an executive penetration testing report with CVSS v3.1 scoring and remediation guidance.",
        "learning_objectives": [
            "Master intercepting HTTP proxy operation with Burp Suite Community Edition",
            "Identify and safely exploit OWASP Top 10 vulnerabilities within an authorized scope",
            "Apply CVSS v3.1 severity metrics to calculate realistic vulnerability impact",
            "Author reproducible Python proof-of-concept verification scripts",
            "Formulate actionable developer mitigation recommendations and executive summaries"
        ],
        "required_technologies": ["Burp Suite Community", "OWASP Juice Shop / DVWA", "Docker Desktop", "Nmap", "Python 3", "Markdown / HTML"],
        "prerequisites": ["Basic HTTP/S protocol knowledge", "Familiarity with Linux command line", "Fundamental Python syntax"],
        "implementation_phases": [
            {
                "phase_number": 1,
                "title": "Lab Setup & Target Isolation",
                "objective": "Deploy intentionally vulnerable web target in an isolated local container network.",
                "tasks": ["Install Docker Desktop and pull OWASP Juice Shop container", "Configure private bridge network (172.28.0.0/16)", "Validate target isolation from host and public networks"],
                "technologies_used": ["Docker", "Linux CLI"],
                "expected_output": "Target application responding exclusively on isolated local loopback port."
            },
            {
                "phase_number": 2,
                "title": "Reconnaissance & Attack Surface Mapping",
                "objective": "Map exposed endpoints, API routes, and parameter handling structures.",
                "tasks": ["Perform service banner enumeration with Nmap", "Configure Burp Suite browser proxy with trusted CA certificate", "Spider target to generate comprehensive endpoint sitemap"],
                "technologies_used": ["Nmap", "Burp Suite"],
                "expected_output": "Complete attack surface map documenting 15+ interactive parameters."
            },
            {
                "phase_number": 3,
                "title": "Structured Vulnerability Assessment",
                "objective": "Systematically evaluate SQL Injection, Cross-Site Scripting, and IDOR flaws.",
                "tasks": ["Fuzz search parameters for SQLi authentication bypass", "Inject contextual XSS payloads into user profile and review fields", "Test horizontal privilege escalation via parameter manipulation"],
                "technologies_used": ["Burp Repeater", "Burp Intruder", "Python 3"],
                "expected_output": "Documented evidence of verified vulnerabilities with request/response logs."
            },
            {
                "phase_number": 4,
                "title": "CVSS Scoring & Remediation Advisory",
                "objective": "Calculate base scores and draft precise code-level remediation steps.",
                "tasks": ["Calculate CVSS v3.1 vector strings for each finding", "Draft parameterized query recommendations for SQLi", "Author comprehensive security assessment deliverable"],
                "technologies_used": ["CVSS Calculator", "Markdown"],
                "expected_output": "Final security report with executive summary and technical appendices."
            }
        ],
        "expected_deliverables": [
            "Formal Penetration Testing Report (PDF/HTML) with executive summary and CVSS v3.1 ratings",
            "Automated Python Proof-of-Concept (PoC) verification scripts",
            "Raw sanitized HTTP request/response logs demonstrating exploit verification",
            "Developer Remediation Guide with secure coding code snippets"
        ],
        "testing_validation_plan": [
            "Verify all testing occurs strictly against local container loopback (127.0.0.1)",
            "Validate that PoC scripts successfully demonstrate the vulnerability without crashing the container",
            "Confirm that simulated developer patches resolve the security flaw and re-test"
        ],
        "skills_demonstrated": ["Web Application Penetration Testing", "Burp Suite", "OWASP Top 10", "CVSS v3.1 Scoring", "Python Automation", "Technical Security Writing"],
        "project_workflow": [
            {"id": "node_1", "label": "START", "type": "start", "description": "Initiate project setup", "next_node": "node_2"},
            {"id": "node_2", "label": "PHASE 1: LAB SETUP & ISOLATION", "type": "process", "description": "Deploy Docker Desktop & isolated OWASP Juice Shop container", "next_node": "node_3"},
            {"id": "node_3", "label": "PHASE 2: RECON & ATTACK SURFACE MAPPING", "type": "process", "description": "Run Nmap port discovery and map HTTP endpoints with Burp Suite", "next_node": "node_4"},
            {"id": "node_4", "label": "PHASE 3: VULNERABILITY TESTING", "type": "process", "description": "Execute targeted tests for SQL Injection, XSS, and IDOR", "next_node": "node_5"},
            {"id": "node_5", "label": "WAS VULNERABILITY VERIFIED?", "type": "decision", "description": "Confirm reproducible exploit evidence and technical impact", "yes_next": "node_6", "no_next": "node_4", "yes_label": "YES: Finding Verified", "no_label": "NO: Refine Scope & Payloads"},
            {"id": "node_6", "label": "PHASE 4: SEVERITY RATING & REMEDIATION", "type": "process", "description": "Calculate CVSS v3.1 scores and formulate developer remediation guidance", "next_node": "node_7"},
            {"id": "node_7", "label": "FINAL SECURITY REPORT", "type": "process", "description": "Compile executive summary, technical findings, and PoC documentation", "next_node": "node_8"},
            {"id": "node_8", "label": "END", "type": "end", "description": "Project successfully verified and published"}
        ]
    },
    {
        "project_id": "CS-02",
        "domain": "Cybersecurity",
        "project_title": "Network Monitoring and Anomaly Detection",
        "difficulty_level": "Intermediate",
        "description": "Construct an automated network intrusion monitoring system utilizing Snort NIDS, Zeek telemetry, and Python Scapy packet analysis to establish baseline network metrics, detect malicious traffic anomalies, and generate defensive alerting.",
        "learning_objectives": [
            "Configure network tap and promiscuous mode monitoring in an isolated virtual network",
            "Write custom Snort 3 signature rules to detect port scanning, ICMP tunneling, and brute force attempts",
            "Parse protocol headers and extract payload telemetry using Python and Scapy",
            "Establish statistical network traffic baselines to flag anomalous volume spikes",
            "Produce actionable incident containment recommendations for security operations"
        ],
        "required_technologies": ["Snort 3 NIDS", "Zeek Network Security Monitor", "Wireshark", "Python 3 (Scapy)", "Ubuntu Linux", "TCPOffload"],
        "prerequisites": ["TCP/IP protocol architecture knowledge", "Understanding of OSI model and packet headers", "Basic Linux administration"],
        "implementation_phases": [
            {
                "phase_number": 1,
                "title": "Sensor Deployment & Interface Configuration",
                "objective": "Deploy network monitoring virtual machine with promiscuous capture interface.",
                "tasks": ["Set up Ubuntu Server VM with dual NICs in Host-Only mode", "Configure promiscuous packet capture using tcpdump", "Install and configure Snort 3 and Zeek engines"],
                "technologies_used": ["Ubuntu Linux", "tcpdump", "Snort 3"],
                "expected_output": "Operational sensor receiving mirror packets with zero packet drop."
            },
            {
                "phase_number": 2,
                "title": "Baseline Traffic Profiling",
                "objective": "Collect and analyze legitimate traffic to establish normal baseline behaviors.",
                "tasks": ["Generate normal web, DNS, and SSH traffic for 24 hours", "Extract statistical packet distributions (bytes/sec, packet sizes, protocol breakdown)", "Document baseline operational metrics in SQLite"],
                "technologies_used": ["Zeek", "Python 3", "SQLite"],
                "expected_output": "Statistical baseline thresholds for connection counts and protocol distribution."
            },
            {
                "phase_number": 3,
                "title": "Anomaly Detection & Signature Rule Engineering",
                "objective": "Author custom rules for SYN flood, stealth scanning, and DNS exfiltration.",
                "tasks": ["Author Snort 3 local rules for Nmap SYN scan detection", "Implement Python Scapy script to flag DNS queries exceeding entropy threshold", "Simulate controlled benign traffic alongside attack traffic"],
                "technologies_used": ["Snort Rules", "Python Scapy", "Nmap"],
                "expected_output": "Validated signature and anomaly detection engine with documented trigger criteria."
            },
            {
                "phase_number": 4,
                "title": "Alerting Pipeline & Hardening Advisory",
                "objective": "Route high-fidelity alerts to a unified log and compile defensive firewall rules.",
                "tasks": ["Format alerts as structured JSON syslog messages", "Generate automated iptables / pfSense containment recommendations", "Author final Network Defense Monitoring Technical Report"],
                "technologies_used": ["Python", "JSON Syslog", "iptables"],
                "expected_output": "Automated alert stream and network defense hardening guide."
            }
        ],
        "expected_deliverables": [
            "Custom Snort 3 Rule Pack (`local.rules`) for targeted attack detection",
            "Python Network Anomaly Detection Daemon script using Scapy",
            "Wireshark Packet Analysis Case Study (PCAP files and dissection walkthroughs)",
            "Network Hardening and Firewall Configuration Guide"
        ],
        "testing_validation_plan": [
            "Execute authorized Nmap -sS, -sU, and -sN scans to verify Snort alert triggering",
            "Transmit base64 data over DNS queries to validate entropy anomaly threshold",
            "Measure false-positive alert rates during normal background traffic runs"
        ],
        "skills_demonstrated": ["Network Intrusion Detection", "Packet Analysis (Wireshark/Scapy)", "Snort Rule Authoring", "Traffic Baselining", "Linux Systems Administration"],
        "project_workflow": [
            {"id": "node_1", "label": "START", "type": "start", "description": "Initialize network monitoring project", "next_node": "node_2"},
            {"id": "node_2", "label": "PHASE 1: SENSOR & CAPTURE CONFIGURATION", "type": "process", "description": "Configure promiscuous capture interface and deploy Snort 3 & Zeek", "next_node": "node_3"},
            {"id": "node_3", "label": "PHASE 2: TRAFFIC BASELINING", "type": "process", "description": "Profile normal network traffic parameters, volume, and protocol distributions", "next_node": "node_4"},
            {"id": "node_4", "label": "PHASE 3: SIMULATED INTRUSION & ANOMALY INJECTION", "type": "process", "description": "Generate authorized stealth scans, DNS tunneling, and connection floods", "next_node": "node_5"},
            {"id": "node_5", "label": "WAS ANOMALY DETECTED?", "type": "decision", "description": "Evaluate if signature or statistical threshold generated an alert", "yes_next": "node_6", "no_next": "node_4", "yes_label": "YES: Alert Triggered", "no_label": "NO: Calibrate Thresholds & Rules"},
            {"id": "node_6", "label": "PHASE 4: PACKET DISSECTION & LOGGING", "type": "process", "description": "Capture PCAP evidence, decode malicious payloads, and log alert metadata", "next_node": "node_7"},
            {"id": "node_7", "label": "DEFENSIVE HARDENING REPORT", "type": "process", "description": "Produce firewall mitigation rules and network architecture hardening guide", "next_node": "node_8"},
            {"id": "node_8", "label": "END", "type": "end", "description": "Network anomaly detection pipeline operational"}
        ]
    },
    {
        "project_id": "CS-03",
        "domain": "Cybersecurity",
        "project_title": "Phishing Email Detection and Security Analysis",
        "difficulty_level": "Beginner / Intermediate",
        "description": "Develop an automated security analysis pipeline that ingests suspicious raw email files (RFC 822 / .eml), verifies email authentication records (SPF, DKIM, DMARC), extracts and inspects embedded URLs and attachment hashes, and maps findings to MITRE ATT&CK tactics.",
        "learning_objectives": [
            "Deconstruct raw email headers, MIME structures, and authentication protocols (SPF, DKIM, DMARC)",
            "Extract obfuscated URLs, analyze homoglyph domains, and evaluate redirect chains",
            "Compute cryptographic hashes (SHA-256) of attachments and query threat intelligence APIs",
            "Map malicious campaign characteristics to MITRE ATT&CK Initial Access techniques (T1566)",
            "Formulate security awareness training indicators and defensive mail gateway rules"
        ],
        "required_technologies": ["Python 3", "Beautiful Soup", "EML Parser", "VirusTotal Public API", "URLScan.io API", "Docker Sandbox"],
        "prerequisites": ["Basic Python scripting", "Fundamental understanding of DNS and SMTP email routing"],
        "implementation_phases": [
            {
                "phase_number": 1,
                "title": "Email Parsing & Header Authentication Analysis",
                "objective": "Extract authentication headers and evaluate sender legitimacy.",
                "tasks": ["Parse RFC 822 .eml files into structured JSON", "Extract and evaluate Authentication-Results header (SPF pass/fail, DKIM signature verification, DMARC policy)", "Detect spoofed sender display names vs envelope From headers"],
                "technologies_used": ["Python email module", "dnspython"],
                "expected_output": "JSON summary of header legitimacy and SPF/DKIM/DMARC status."
            },
            {
                "phase_number": 2,
                "title": "Body Extraction & URL Inspection",
                "objective": "Harvest embedded links and analyze landing page characteristics.",
                "tasks": ["Extract plain-text and HTML body components using Beautiful Soup", "De-obfuscate shortened and URL-encoded links", "Check for homoglyph / typosquatting domains using Levenshtein distance"],
                "technologies_used": ["Beautiful Soup", "urllib", "Levenshtein"],
                "expected_output": "Comprehensive list of unique domains, resolved IPs, and redirect targets."
            },
            {
                "phase_number": 3,
                "title": "Attachment Analysis & Threat Intel Enrichment",
                "objective": "Hash attachments and query reputation APIs safely without execution.",
                "tasks": ["Compute SHA-256 and MD5 hashes of all embedded attachments", "Query VirusTotal API for known malware signatures", "Query URLScan.io for landing page screenshots and DOM artifacts"],
                "technologies_used": ["hashlib", "VirusTotal API", "URLScan API"],
                "expected_output": "Threat intelligence score and known malware classification report."
            },
            {
                "phase_number": 4,
                "title": "Threat Classification & Gateway Rule Export",
                "objective": "Score overall email threat level and generate defensive filter rules.",
                "tasks": ["Implement weighted heuristic scoring algorithm (0-100 Phishing Score)", "Generate YARA and Postfix / Microsoft 365 transport rule definitions", "Author technical phishing analysis case study"],
                "technologies_used": ["Python", "YARA", "Markdown"],
                "expected_output": "Interactive CLI tool, threat scoring report, and exportable mail gateway rules."
            }
        ],
        "expected_deliverables": [
            "Automated Python Phishing Analyzer CLI tool (`phish_analyzer.py`)",
            "Curated dataset of 10 sanitized sample phishing emails (.eml) with ground-truth labels",
            "Threat Intelligence Enrichment module with rate-limited API integration",
            "Defensive Mail Gateway Rule Pack (YARA rules, blocklists, and DMARC enforcement guide)"
        ],
        "testing_validation_plan": [
            "Execute analyzer against 10 known phishing samples and 10 legitimate notification emails",
            "Verify 100% detection of spoofed SPF/DKIM headers in test corpus",
            "Validate that attachment hashing generates correct SHA-256 strings without touching disk execution"
        ],
        "skills_demonstrated": ["Email Security Architecture", "Header Analysis (SPF/DKIM/DMARC)", "Threat Intelligence Integration", "Python Automation", "Malware Triaging Basics"],
        "project_workflow": [
            {"id": "node_1", "label": "START", "type": "start", "description": "Initialize email security analysis", "next_node": "node_2"},
            {"id": "node_2", "label": "PHASE 1: RAW EMAIL INGESTION & HEADER AUDIT", "type": "process", "description": "Parse .eml file and verify SPF, DKIM, and DMARC alignment", "next_node": "node_3"},
            {"id": "node_3", "label": "PHASE 2: BODY & HYPERLINK DE-OBFUSCATION", "type": "process", "description": "Extract links, inspect redirect chains, and check typosquatting domains", "next_node": "node_4"},
            {"id": "node_4", "label": "PHASE 3: ATTACHMENT HASHING & THREAT INTEL", "type": "process", "description": "Compute SHA-256 hashes and query VirusTotal / URLScan APIs", "next_node": "node_5"},
            {"id": "node_5", "label": "IS EMAIL FLAGGED AS PHISHING?", "type": "decision", "description": "Evaluate cumulative heuristic threat score against threshold (Score >= 70)", "yes_next": "node_6", "no_next": "node_7", "yes_label": "YES: Malicious / Suspicious", "no_label": "NO: Benign / Safe"},
            {"id": "node_6", "label": "PHASE 4: IOC EXTRACTION & MITRE MAPPING", "type": "process", "description": "Catalog Indicators of Compromise and map to MITRE ATT&CK T1566", "next_node": "node_8"},
            {"id": "node_7", "label": "RECORD BENIGN BASELINE", "type": "process", "description": "Log legitimate sender profile and store verified safe indicators", "next_node": "node_8"},
            {"id": "node_8", "label": "SECURITY INCIDENT ADVISORY & MAIL RULES", "type": "process", "description": "Generate YARA rules, tenant blocklists, and security awareness advisory", "next_node": "node_9"},
            {"id": "node_9", "label": "END", "type": "end", "description": "Analysis pipeline execution complete"}
        ]
    },
    {
        "project_id": "CS-04",
        "domain": "Cybersecurity",
        "project_title": "Security Log Analysis and Threat Detection",
        "difficulty_level": "Intermediate / Advanced",
        "description": "Construct an end-to-end security operations center pipeline ingesting Windows Event Logs (via Sysmon) and Linux authentication logs into a centralized Splunk / Elastic SIEM instance, author custom correlation rules mapped to MITRE ATT&CK, and investigate simulated adversary intrusions.",
        "learning_objectives": [
            "Configure Sysmon and Universal Forwarder for granular Windows endpoint telemetry",
            "Ingest and normalize heterogeneous log sources (Windows Security, Sysmon, Auth.log, Web logs)",
            "Author advanced Search Processing Language (SPL) queries for threat hunting",
            "Build custom detection rules for privilege escalation, process injection, and lateral movement",
            "Construct operational SOC dashboards and document step-by-step incident response playbooks"
        ],
        "required_technologies": ["Splunk Enterprise (Free) / Elastic SIEM", "Microsoft Sysmon", "Ubuntu Linux Server", "Atomic Red Team", "PowerShell", "Wireshark"],
        "prerequisites": ["Understanding of Windows Security Event IDs (4624, 4625, 4688)", "Familiarity with MITRE ATT&CK Matrix", "Basic SQL / query syntax experience"],
        "implementation_phases": [
            {
                "phase_number": 1,
                "title": "Telemetry Pipeline & Forwarder Configuration",
                "objective": "Deploy centralized SIEM instance and forward endpoint telemetry.",
                "tasks": ["Deploy Splunk Enterprise on Ubuntu Server VM", "Install Sysmon with SwiftOnSecurity modular configuration on Windows VM", "Configure Universal Forwarder on port 9997 with secure tokens"],
                "technologies_used": ["Splunk", "Sysmon", "Ubuntu", "Windows"],
                "expected_output": "Live continuous log stream indexing Event IDs 1, 3, 7, 10, and 4625."
            },
            {
                "phase_number": 2,
                "title": "Attack Simulation & Telemetry Verification",
                "objective": "Execute authorized attack techniques to generate realistic security telemetry.",
                "tasks": ["Execute Atomic Red Team T1059.001 (PowerShell encoded execution)", "Execute T1003 (OS Credential Dumping simulation via procdump)", "Execute T1087 (Account Discovery) in isolated sandbox"],
                "technologies_used": ["Atomic Red Team", "PowerShell"],
                "expected_output": "Rich adversary telemetry indexed in SIEM with clear timestamps."
            },
            {
                "phase_number": 3,
                "title": "Detection Engineering & SPL Authoring",
                "objective": "Write correlation rules with low false-positive rates.",
                "tasks": ["Write SPL query for encoded PowerShell command lines (`-enc`, `-encodedcommand`)", "Write SPL correlation for brute force logon bursts (>5 failures in 2 minutes followed by success)", "Write SPL rule detecting unsigned DLL loads into system processes"],
                "technologies_used": ["Splunk SPL", "MITRE ATT&CK"],
                "expected_output": "Suite of 5 custom correlation rules generating automated alerts."
            },
            {
                "phase_number": 4,
                "title": "SOC Dashboard Studio & Incident Playbooks",
                "objective": "Build operational visualizations and draft triage guides.",
                "tasks": ["Design interactive SOC overview dashboard (top targets, active alerts, MITRE heatmap)", "Author standard incident response triage playbook for compromised accounts", "Compile sanitized export package without private network credentials"],
                "technologies_used": ["Splunk Dashboard Studio", "Markdown"],
                "expected_output": "Production-ready dashboard XML and analyst runbook."
            }
        ],
        "expected_deliverables": [
            "Complete Splunk / Elastic Detection Rule Pack (`queries.spl` with 5+ validated rules)",
            "SwiftOnSecurity Sysmon XML Configuration customized for high-value detection",
            "Interactive SOC Dashboard XML / JSON definition",
            "Incident Response Triage Playbook (`account_compromise_playbook.md`)"
        ],
        "testing_validation_plan": [
            "Run automated adversary simulation script and verify all 5 rules fire within 60 seconds",
            "Perform regression testing with 24 hours of normal user activity to verify zero false positives",
            "Audit dashboard rendering across multiple screen resolutions"
        ],
        "skills_demonstrated": ["SIEM Administration (Splunk)", "Detection Engineering", "Sysmon Event ID Telemetry", "MITRE ATT&CK Mapping", "Incident Triage Playbook Writing"],
        "project_workflow": [
            {"id": "node_1", "label": "START", "type": "start", "description": "Initiate SIEM and log analysis setup", "next_node": "node_2"},
            {"id": "node_2", "label": "PHASE 1: SIEM & SYSMON FORWARDER SETUP", "type": "process", "description": "Configure Splunk receiver and deploy Sysmon endpoint agent", "next_node": "node_3"},
            {"id": "node_3", "label": "PHASE 2: CONTROLLED ATTACK SIMULATION", "type": "process", "description": "Execute Atomic Red Team techniques (T1059, T1003, T1087) in sandbox", "next_node": "node_4"},
            {"id": "node_4", "label": "PHASE 3: DETECTION RULE EVALUATION", "type": "process", "description": "Run SPL correlation queries against incoming telemetry index", "next_node": "node_5"},
            {"id": "node_5", "label": "DID CORRELATION RULE TRIGGER ALERT?", "type": "decision", "description": "Verify alert trigger accuracy and check false-positive threshold", "yes_next": "node_6", "no_next": "node_4", "yes_label": "YES: Alert Fired Accurately", "no_label": "NO: Tune SPL & Logic Filters"},
            {"id": "node_6", "label": "PHASE 4: DASHBOARD & MITRE ATT&CK INTEGRATION", "type": "process", "description": "Publish alert to SOC dashboard and map to MITRE ATT&CK tactics", "next_node": "node_7"},
            {"id": "node_7", "label": "INCIDENT TRIAGE RUNBOOK", "type": "process", "description": "Document analyst step-by-step containment and remediation playbook", "next_node": "node_8"},
            {"id": "node_8", "label": "END", "type": "end", "description": "Security log pipeline and detection suite fully deployed"}
        ]
    },
    {
        "project_id": "CS-05",
        "domain": "Cybersecurity",
        "project_title": "File Integrity Monitoring and Security Alerting",
        "difficulty_level": "Intermediate",
        "description": "Design and build a lightweight, cross-platform File Integrity Monitoring (FIM) daemon in Python that maintains a secure cryptographic baseline of critical system files, listens for real-time filesystem events, evaluates unauthorized modifications, and delivers instant security alerting.",
        "learning_objectives": [
            "Implement high-performance cryptographic hashing (SHA-256) of filesystem structures",
            "Harness OS-level kernel filesystem event APIs (Linux inotify / Windows ReadDirectoryChangesW)",
            "Build SQLite tamper-evident state database for baseline verification",
            "Differentiate authorized patch management updates from unauthorized file tampering",
            "Construct real-time alerting integrations via Webhooks, SMTP, and Syslog"
        ],
        "required_technologies": ["Python 3", "SQLite3", "Linux inotify / Windows Watchdog", "SHA-256 / BLAKE2", "SMTP / Discord Webhook", "Bash / PowerShell"],
        "prerequisites": ["Python file I/O and threading concepts", "Understanding of file permissions and integrity controls"],
        "implementation_phases": [
            {
                "phase_number": 1,
                "title": "Baseline Engine & Cryptographic State Storage",
                "objective": "Build initialization scanner that hashes critical system paths.",
                "tasks": ["Recursively scan monitored directories (/etc, /bin, C:\\Windows\\System32\\drivers)", "Calculate SHA-256 hashes and capture metadata (permissions, owner, size, mtime)", "Store state securely in indexed SQLite baseline database"],
                "technologies_used": ["Python 3", "hashlib", "SQLite3"],
                "expected_output": "Clean baseline snapshot database storing 500+ monitored files."
            },
            {
                "phase_number": 2,
                "title": "Real-Time Filesystem Event Monitor",
                "objective": "Implement kernel event listener for create, modify, and delete actions.",
                "tasks": ["Implement Python watchdog / pyinotify event handler", "Buffer rapid file update events to prevent CPU spikes", "Extract actor/PID of modifying process where supported"],
                "technologies_used": ["watchdog", "inotify", "multiprocessing"],
                "expected_output": "Sub-millisecond event detection upon any disk modification."
            },
            {
                "phase_number": 3,
                "title": "Integrity Comparison & Tamper Analysis",
                "objective": "Compare event-triggered files against baseline cryptographic records.",
                "tasks": ["Recompute SHA-256 on modified files and compare against stored hash", "Check against authorized maintenance change window / approved hashes", "Flag unauthorized alterations as High-Severity Security Incidents"],
                "technologies_used": ["Python logic", "SQLite queries"],
                "expected_output": "Accurate differential report highlighting modified byte offsets and new hashes."
            },
            {
                "phase_number": 4,
                "title": "Multi-Channel Alerting & Audit Logging",
                "objective": "Deliver immediate notifications and maintain append-only audit trail.",
                "tasks": ["Implement webhook notification (Discord/Slack/Teams) with incident payload", "Implement SMTP email dispatch with differential details", "Write append-only integrity audit log for compliance validation"],
                "technologies_used": ["requests", "smtplib", "logging"],
                "expected_output": "Automated alert delivery within 2 seconds of unauthorized tampering."
            }
        ],
        "expected_deliverables": [
            "Complete Python FIM Daemon (`fim_daemon.py` with CLI controls: --init, --monitor, --verify)",
            "Configuration file (`fim_config.yaml`) defining monitored directories and alert thresholds",
            "Tamper-evident SQLite database schema with hash verification routines",
            "Technical Compliance Report demonstrating alignment with PCI-DSS Section 11.5 / CIS Controls"
        ],
        "testing_validation_plan": [
            "Simulate unauthorized edit to `/etc/hosts` or system config and confirm alert fires in <2s",
            "Simulate file deletion and new file drop to verify CREATE and DELETE detection",
            "Stress test with 10,000 files to ensure memory footprint remains < 50MB"
        ],
        "skills_demonstrated": ["Cryptographic Integrity Verification", "Systems Programming (Python)", "Kernel Event Monitoring", "PCI-DSS 11.5 Compliance", "Incident Alerting Pipelines"],
        "project_workflow": [
            {"id": "node_1", "label": "START", "type": "start", "description": "Initialize File Integrity Monitor", "next_node": "node_2"},
            {"id": "node_2", "label": "PHASE 1: TARGET DEFINITION & BASELINE HASHING", "type": "process", "description": "Scan monitored directories and calculate SHA-256 cryptographic baselines", "next_node": "node_3"},
            {"id": "node_3", "label": "PHASE 2: REAL-TIME FILESYSTEM LISTENER", "type": "process", "description": "Listen for kernel inotify / watchdog create, modify, or delete events", "next_node": "node_4"},
            {"id": "node_4", "label": "WAS A FILE MODIFIED OR ALTERED?", "type": "decision", "description": "Evaluate incoming filesystem notification event stream", "yes_next": "node_5", "no_next": "node_3", "yes_label": "YES: File Change Detected", "no_label": "NO: Continue Active Polling"},
            {"id": "node_5", "label": "PHASE 3: CRYPTOGRAPHIC HASH RECOMPUTATION", "type": "process", "description": "Recompute SHA-256 hash and compare against SQLite baseline database", "next_node": "node_6"},
            {"id": "node_6", "label": "WAS THE MODIFICATION AUTHORIZED?", "type": "decision", "description": "Verify change against approved maintenance window and hash whitelist", "yes_next": "node_7", "no_next": "node_8", "yes_label": "YES: Authorized Update", "no_label": "NO: Unauthorized Tampering Detected"},
            {"id": "node_7", "label": "UPDATE BASELINE RECORD", "type": "process", "description": "Update SQLite database with approved new hash and maintenance audit note", "next_node": "node_9"},
            {"id": "node_8", "label": "TRIGGER HIGH-SEVERITY SECURITY ALERT", "type": "process", "description": "Dispatch immediate alert via Webhook and SMTP with forensic diff", "next_node": "node_9"},
            {"id": "node_9", "label": "APPEND-ONLY AUDIT LOG", "type": "process", "description": "Record immutable incident record into compliance audit trail", "next_node": "node_10"},
            {"id": "node_10", "label": "END", "type": "end", "description": "FIM daemon cycle completed; continues background monitoring"}
        ]
    }
]


# ==============================================================================
# 2. DATA SCIENCE & MACHINE LEARNING DOMAIN (5 DISTINCT PROJECTS)
# ==============================================================================

DATA_SCIENCE_PROJECTS: List[Dict[str, Any]] = [
    {
        "project_id": "DS-01",
        "domain": "Data Science & Machine Learning",
        "project_title": "Customer Churn Predictive Modeling and Retention Engine",
        "difficulty_level": "Intermediate",
        "description": "Develop an end-to-end churn prediction system utilizing real-world customer telemetry, advanced feature engineering, imbalanced class handling, and XGBoost classification to identify at-risk customers and output explainable feature attributions.",
        "learning_objectives": [
            "Perform rigorous exploratory data analysis (EDA) and identify key churn indicators",
            "Handle skewed distributions and class imbalance utilizing SMOTE and cost-sensitive learning",
            "Train and cross-validate gradient-boosted decision trees (XGBoost / LightGBM)",
            "Generate model interpretability reports utilizing SHAP (SHapley Additive exPlanations)",
            "Deploy an interactive Streamlit inference dashboard for customer retention specialists"
        ],
        "required_technologies": ["Python 3", "Pandas", "Scikit-Learn", "XGBoost", "SHAP", "Streamlit", "Matplotlib"],
        "prerequisites": ["Data manipulation with Pandas", "Basic statistical learning theory", "Familiarity with ROC-AUC metrics"],
        "implementation_phases": [
            {
                "phase_number": 1,
                "title": "Data Validation & Feature Engineering",
                "objective": "Ingest dataset, clean missing fields, and engineer customer engagement ratios.",
                "tasks": ["Validate schema and clean irregular values", "Engineer tenure-to-charge ratios and support ticket frequency features", "Perform one-hot encoding on categorical attributes"],
                "technologies_used": ["Pandas", "NumPy"],
                "expected_output": "Clean, normalized feature matrix ready for modeling."
            },
            {
                "phase_number": 2,
                "title": "Class Balancing & Model Training",
                "objective": "Mitigate class imbalance and train competitive classification models.",
                "tasks": ["Apply SMOTE oversampling on training split only", "Train Logistic Regression baseline, Random Forest, and XGBoost models", "Perform 5-fold stratified cross-validation"],
                "technologies_used": ["Scikit-Learn", "imbalanced-learn", "XGBoost"],
                "expected_output": "Trained XGBoost model achieving ROC-AUC > 0.86 on held-out test data."
            },
            {
                "phase_number": 3,
                "title": "Model Evaluation & Explainability",
                "objective": "Evaluate classification metrics and explain individual predictions.",
                "tasks": ["Compute confusion matrix, precision-recall curve, and optimal threshold", "Calculate SHAP TreeExplainer values for global and local feature importance", "Identify top 3 churn drivers across customer segments"],
                "technologies_used": ["SHAP", "Matplotlib", "Seaborn"],
                "expected_output": "SHAP summary plots and actionable customer risk attributions."
            },
            {
                "phase_number": 4,
                "title": "Interactive Dashboard Deployment",
                "objective": "Deploy customer scoring interface with what-if scenario simulator.",
                "tasks": ["Build Streamlit web interface accepting customer profile inputs", "Display real-time churn probability and dynamic retention recommendation", "Containerize application with Docker"],
                "technologies_used": ["Streamlit", "Docker"],
                "expected_output": "Live interactive web application for marketing retention teams."
            }
        ],
        "expected_deliverables": [
            "Complete Jupyter Notebook with thorough EDA and documented modeling experiments",
            "Serialised Production Model pipeline artifact (`model.joblib`)",
            "SHAP Explainability and Feature Importance Analysis Report",
            "Interactive Streamlit Web Dashboard source code"
        ],
        "testing_validation_plan": [
            "Verify data leakage prevention by fitting preprocessors exclusively on training folds",
            "Validate ROC-AUC and F1-score against dummy baseline on isolated test set",
            "Stress test inference speed to ensure single-record prediction in < 25ms"
        ],
        "skills_demonstrated": ["Exploratory Data Analysis", "Feature Engineering", "Gradient Boosting (XGBoost)", "Imbalanced Learning", "Explainable AI (SHAP)", "Streamlit Prototyping"],
        "project_workflow": [
            {"id": "node_1", "label": "START", "type": "start", "description": "Initiate data science project", "next_node": "node_2"},
            {"id": "node_2", "label": "PHASE 1: DATA INGESTION & VALIDATION", "type": "process", "description": "Ingest customer dataset, validate types, and clean missing values", "next_node": "node_3"},
            {"id": "node_3", "label": "PHASE 2: FEATURE ENGINEERING & SCALING", "type": "process", "description": "Compute usage ratios, encode categoricals, and partition train/test sets", "next_node": "node_4"},
            {"id": "node_4", "label": "PHASE 3: MODEL TRAINING & HYPERPARAMETER TUNING", "type": "process", "description": "Train XGBoost and Random Forest with SMOTE class balancing", "next_node": "node_5"},
            {"id": "node_5", "label": "DOES MODEL MEET ROC-AUC >= 0.85?", "type": "decision", "description": "Evaluate cross-validation discrimination metrics", "yes_next": "node_6", "no_next": "node_3", "yes_label": "YES: Metric Threshold Met", "no_label": "NO: Engineer New Features & Retune"},
            {"id": "node_6", "label": "PHASE 4: SHAP EXPLAINABILITY ANALYSIS", "type": "process", "description": "Generate SHAP feature importance and individual prediction attributions", "next_node": "node_7"},
            {"id": "node_7", "label": "STREAMLIT RETENTION DASHBOARD", "type": "process", "description": "Deploy interactive prediction simulator and retention strategy advisor", "next_node": "node_8"},
            {"id": "node_8", "label": "END", "type": "end", "description": "Predictive model pipeline deployed and operational"}
        ]
    },
    {
        "project_id": "DS-02",
        "domain": "Data Science & Machine Learning",
        "project_title": "End-to-End Sentiment Analysis and Opinion Mining Pipeline",
        "difficulty_level": "Intermediate",
        "description": "Construct an automated natural language processing (NLP) pipeline that harvests customer reviews, performs text preprocessing and tokenization, fine-tunes a DistilBERT transformer classifier, and serves real-time sentiment predictions through a high-performance FastAPI endpoint.",
        "learning_objectives": [
            "Clean and tokenize unstructured text corpora using Hugging Face tokenizers",
            "Fine-tune pre-trained transformer architectures (DistilBERT) using PyTorch",
            "Mitigate overfitting with dropout, weight decay, and learning rate warmup",
            "Export models to ONNX runtime format for low-latency production inference",
            "Construct async REST API endpoints with request validation and rate limiting"
        ],
        "required_technologies": ["Python 3", "PyTorch", "Hugging Face Transformers", "FastAPI", "Uvicorn", "Docker", "ONNX Runtime"],
        "prerequisites": ["Python OOP fundamentals", "Basic neural network / deep learning concepts", "Experience with REST APIs"],
        "implementation_phases": [
            {
                "phase_number": 1,
                "title": "Text Preprocessing & Tokenization",
                "objective": "Normalize raw text reviews and build subword token encodings.",
                "tasks": ["Clean HTML tags, emoji encodings, and invalid characters", "Tokenize text using Hugging Face AutoTokenizer with padding and truncation", "Construct PyTorch DataLoader with dynamic batching"],
                "technologies_used": ["Hugging Face Tokenizers", "PyTorch"],
                "expected_output": "Tokenized input IDs and attention masks mapped to sentiment labels."
            },
            {
                "phase_number": 2,
                "title": "Transformer Model Fine-Tuning",
                "objective": "Fine-tune DistilBERT sequence classification model.",
                "tasks": ["Load pre-trained DistilBERT weights and attach classification head", "Train model with AdamW optimizer, linear warmup, and cross-entropy loss", "Evaluate validation accuracy and macro F1-score across 3 epochs"],
                "technologies_used": ["PyTorch", "Hugging Face Transformers"],
                "expected_output": "Fine-tuned transformer model achieving > 92% validation accuracy."
            },
            {
                "phase_number": 3,
                "title": "ONNX Optimization & Benchmarking",
                "objective": "Convert PyTorch model to ONNX runtime for sub-10ms inference.",
                "tasks": ["Export PyTorch graph to ONNX model format", "Apply dynamic quantization to reduce memory footprint by 4x", "Benchmark latency comparing raw PyTorch vs ONNX Runtime"],
                "technologies_used": ["ONNX", "ONNX Runtime"],
                "expected_output": "Quantized model artifact running inference in < 8ms per review."
            },
            {
                "phase_number": 4,
                "title": "FastAPI Inference Microservice",
                "objective": "Wrap model in production REST API with Swagger documentation.",
                "tasks": ["Build FastAPI app with Pydantic request/response schemas", "Implement batch review prediction endpoint (/predict/batch)", "Package microservice into lean Docker container"],
                "technologies_used": ["FastAPI", "Uvicorn", "Docker"],
                "expected_output": "Production container serving live sentiment inference requests."
            }
        ],
        "expected_deliverables": [
            "Fine-tuning training script (`train_sentiment.py`) with logging",
            "Quantized ONNX model artifact (`sentiment_distilbert.onnx`)",
            "FastAPI Production Microservice application code (`main.py`)",
            "Docker deployment image definition and performance benchmark report"
        ],
        "testing_validation_plan": [
            "Test model against edge-case sarcasm and negations ('not good', 'hardly impressive')",
            "Execute Apache Bench load test verifying throughput of 100 requests/sec",
            "Verify memory stability over 10,000 continuous inference calls"
        ],
        "skills_demonstrated": ["Natural Language Processing (NLP)", "Transformers (DistilBERT)", "PyTorch Fine-Tuning", "ONNX Optimization", "FastAPI Service Deployment"],
        "project_workflow": [
            {"id": "node_1", "label": "START", "type": "start", "description": "Initialize NLP pipeline project", "next_node": "node_2"},
            {"id": "node_2", "label": "PHASE 1: TEXT PREPROCESSING & TOKENIZATION", "type": "process", "description": "Clean raw review text and generate subword token encodings", "next_node": "node_3"},
            {"id": "node_3", "label": "PHASE 2: TRANSFORMER FINE-TUNING", "type": "process", "description": "Fine-tune DistilBERT architecture with learning rate scheduling", "next_node": "node_4"},
            {"id": "node_4", "label": "DOES VALIDATION F1-SCORE EXCEED 0.90?", "type": "decision", "description": "Evaluate multi-class macro F1-score on held-out validation set", "yes_next": "node_5", "no_next": "node_3", "yes_label": "YES: Target Accuracy Met", "no_label": "NO: Adjust Learning Rate & Regularization"},
            {"id": "node_5", "label": "PHASE 3: ONNX QUANTIZATION", "type": "process", "description": "Convert model to ONNX runtime and apply dynamic quantization", "next_node": "node_6"},
            {"id": "node_6", "label": "FASTAPI INFERENCE SERVICE", "type": "process", "description": "Expose REST endpoints with Pydantic schemas and swagger documentation", "next_node": "node_7"},
            {"id": "node_7", "label": "END", "type": "end", "description": "Production NLP microservice fully operational"}
        ]
    },
    {
        "project_id": "DS-03",
        "domain": "Data Science & Machine Learning",
        "project_title": "Financial Fraud Detection with Real-time Scoring",
        "difficulty_level": "Advanced",
        "description": "Architect a high-throughput financial transaction fraud detection engine handling extreme class imbalance (99.8% legitimate vs 0.2% fraud) using Isolation Forests, Autoencoders, and calibrated ensemble classifiers.",
        "learning_objectives": [
            "Model extreme class imbalance using unsupervised and supervised hybrid methods",
            "Implement deep learning Autoencoders for semi-supervised reconstruction error detection",
            "Calibrate probability outputs utilizing Platt scaling and isotonic regression",
            "Optimize classification thresholds based on business financial loss matrix",
            "Streamline feature computation using Redis in-memory lookup caches"
        ],
        "required_technologies": ["Python 3", "TensorFlow / PyTorch", "Scikit-Learn", "Redis", "Kafka (or Simulated Stream)", "FastAPI"],
        "prerequisites": ["Deep learning fundamentals", "Understanding of anomaly detection algorithms", "Experience with probabilistic calibration"],
        "implementation_phases": [
            {
                "phase_number": 1,
                "title": "Transaction Feature Engineering & Scaling",
                "objective": "Extract temporal velocity features and normalize transaction amounts.",
                "tasks": ["Compute rolling transaction velocity (transactions per card in past 10 min)", "Calculate geographic distance between consecutive transactions", "Apply RobustScaler to withstand extreme financial outliers"],
                "technologies_used": ["Pandas", "NumPy", "Scikit-Learn"],
                "expected_output": "High-dimensional feature vectors capturing anomalous behavioral velocity."
            },
            {
                "phase_number": 2,
                "title": "Unsupervised & Semi-Supervised Anomaly Detection",
                "objective": "Train Autoencoder neural network exclusively on legitimate transactions.",
                "tasks": ["Construct Autoencoder with bottleneck compression layer", "Train model to minimize mean squared reconstruction error on normal data", "Flag transactions with reconstruction loss exceeding 99th percentile threshold"],
                "technologies_used": ["TensorFlow / Keras", "PyTorch"],
                "expected_output": "Reconstruction loss distribution with clear anomaly separation."
            },
            {
                "phase_number": 3,
                "title": "Ensemble Classification & Probability Calibration",
                "objective": "Combine tree-based model with reconstruction score for calibrated probability.",
                "tasks": ["Train LightGBM on engineered features + reconstruction loss feature", "Calibrate model probabilities using Isotonic Regression", "Optimize decision threshold based on false-positive customer friction cost"],
                "technologies_used": ["LightGBM", "CalibratedClassifierCV"],
                "expected_output": "Calibrated fraud probability output with financial cost-matrix curve."
            },
            {
                "phase_number": 4,
                "title": "Real-Time Scoring API & Audit Trail",
                "objective": "Deploy streaming scoring service with sub-15ms response latency.",
                "tasks": ["Build FastAPI prediction endpoint reading rolling features from Redis", "Implement asynchronous audit log recording all flagged transactions", "Document system design and operational latency metrics"],
                "technologies_used": ["FastAPI", "Redis", "Docker"],
                "expected_output": "Production fraud scoring microservice handling 500 req/sec."
            }
        ],
        "expected_deliverables": [
            "Complete Fraud Modeling Notebook and experiment tracking logs",
            "Autoencoder and LightGBM serialised model pipeline weights",
            "Financial Cost-Matrix and Precision-Recall Tradeoff Technical Whitepaper",
            "FastAPI Real-Time Scoring Microservice with Redis integration"
        ],
        "testing_validation_plan": [
            "Verify zero test data contamination in Autoencoder training pipeline",
            "Evaluate Precision-Recall AUC (PR-AUC) on severely imbalanced test split",
            "Benchmark concurrent API latency under simulated burst traffic"
        ],
        "skills_demonstrated": ["Extreme Class Imbalance", "Autoencoders & Anomaly Detection", "Probability Calibration", "Cost-Sensitive Machine Learning", "Redis Feature Stores"],
        "project_workflow": [
            {"id": "node_1", "label": "START", "type": "start", "description": "Initiate fraud detection project", "next_node": "node_2"},
            {"id": "node_2", "label": "PHASE 1: FEATURE EXTRACTION & VELOCITY PROFILING", "type": "process", "description": "Compute rolling velocity and geographic distance features", "next_node": "node_3"},
            {"id": "node_3", "label": "PHASE 2: AUTOENCODER ANOMALY DETECTION", "type": "process", "description": "Train semi-supervised Autoencoder on normal transaction stream", "next_node": "node_4"},
            {"id": "node_4", "label": "PHASE 3: ENSEMBLE CLASSIFICATION & CALIBRATION", "type": "process", "description": "Train LightGBM ensemble and apply isotonic probability calibration", "next_node": "node_5"},
            {"id": "node_5", "label": "IS PR-AUC >= 0.80 & LATENCY < 15MS?", "type": "decision", "description": "Verify high-precision detection and sub-15ms inference SLA", "yes_next": "node_6", "no_next": "node_3", "yes_label": "YES: Performance SLA Verified", "no_label": "NO: Optimize Architecture & Thresholds"},
            {"id": "node_6", "label": "FASTAPI & REDIS REAL-TIME SCORING", "type": "process", "description": "Deploy low-latency scoring API connected to Redis feature store", "next_node": "node_7"},
            {"id": "node_7", "label": "END", "type": "end", "description": "Fraud detection engine fully deployed"}
        ]
    },
    {
        "project_id": "DS-04",
        "domain": "Data Science & Machine Learning",
        "project_title": "Healthcare Diagnostic Classification and Explainable AI",
        "difficulty_level": "Advanced",
        "description": "Build an auditable clinical diagnostic classification pipeline for chest X-ray disease detection utilizing transfer learning with EfficientNet, data augmentation, and Grad-CAM visual explainability to highlight pathology regions for clinical practitioners.",
        "learning_objectives": [
            "Implement image data augmentation pipelines robust to clinical variation",
            "Apply transfer learning utilizing state-of-the-art vision backbones (EfficientNet-B4)",
            "Generate visual attribution heatmaps utilizing Grad-CAM to highlight pathology",
            "Evaluate multi-label classification utilizing ROC-AUC and sensitivity benchmarks",
            "Author medical AI safety and bias documentation conforming to health informatics standards"
        ],
        "required_technologies": ["Python 3", "PyTorch", "Torchvision", "Albumentations", "Grad-CAM", "OpenCV", "Streamlit"],
        "prerequisites": ["Computer vision fundamentals", "Convolutional neural network architectures", "Basic PyTorch proficiency"],
        "implementation_phases": [
            {
                "phase_number": 1,
                "title": "Dataset Curation & Clinical Augmentation",
                "objective": "Preprocess medical imaging dataset with domain-appropriate augmentation.",
                "tasks": ["Resize and normalize chest X-ray images (CLAHE contrast enhancement)", "Apply Albumentations (affine transforms, slight rotation, brightness adjustment)", "Ensure patient-level train/val/test splitting to prevent clinical data leakage"],
                "technologies_used": ["OpenCV", "Albumentations", "PyTorch Dataset"],
                "expected_output": "Leakage-free medical image pipeline with contrast normalization."
            },
            {
                "phase_number": 2,
                "title": "Transfer Learning Model Training",
                "objective": "Train EfficientNet-B4 multi-label classification architecture.",
                "tasks": ["Load ImageNet pre-trained EfficientNet backbone with custom classifier head", "Train with Binary Cross-Entropy with Logits loss across 14 diagnostic classes", "Implement mixed-precision training (torch.cuda.amp) for memory optimization"],
                "technologies_used": ["PyTorch", "Torchvision", "CUDA"],
                "expected_output": "Trained vision model achieving mean ROC-AUC > 0.84 across diagnostic classes."
            },
            {
                "phase_number": 3,
                "title": "Grad-CAM Visual Explainability",
                "objective": "Generate visual saliency heatmaps overlaid on original radiography.",
                "tasks": ["Compute gradient-weighted class activation mapping (Grad-CAM) on final convolutional layer", "Generate heatmap overlays highlighting primary anatomical regions of interest", "Validate visual localization accuracy against clinical bounding boxes"],
                "technologies_used": ["Grad-CAM", "Matplotlib", "OpenCV"],
                "expected_output": "Interpretable heatmap overlays confirming model focuses on true pathology."
            },
            {
                "phase_number": 4,
                "title": "Clinical Inspection Dashboard",
                "objective": "Build interactive radiology assistant tool for healthcare evaluation.",
                "tasks": ["Construct Streamlit interface for image upload and multi-label prediction", "Render side-by-side view of original radiograph and Grad-CAM heatmap", "Export diagnostic summary report with confidence intervals"],
                "technologies_used": ["Streamlit", "ReportLab"],
                "expected_output": "Interactive radiology assistant tool for clinical validation."
            }
        ],
        "expected_deliverables": [
            "Complete PyTorch Model Training pipeline (`train_diagnostic.py`)",
            "Grad-CAM Heatmap Generation Module (`explainability.py`)",
            "Clinical Safety and Model Bias Audit Report",
            "Streamlit Radiology Visualizer Web Application"
        ],
        "testing_validation_plan": [
            "Verify patient-level separation: zero overlap of patient IDs between train and test sets",
            "Evaluate model sensitivity at 90% specificity threshold across clinical classes",
            "Conduct visual sanity checks to confirm Grad-CAM does not activate on image border tokens"
        ],
        "skills_demonstrated": ["Computer Vision (PyTorch)", "Transfer Learning (EfficientNet)", "Explainable AI (Grad-CAM)", "Medical Image Augmentation", "Clinical Model Safety"],
        "project_workflow": [
            {"id": "node_1", "label": "START", "type": "start", "description": "Initiate medical imaging AI project", "next_node": "node_2"},
            {"id": "node_2", "label": "PHASE 1: IMAGE PREPROCESSING & AUGMENTATION", "type": "process", "description": "Apply CLAHE contrast adjustment and patient-isolated partitioning", "next_node": "node_3"},
            {"id": "node_3", "label": "PHASE 2: EFFICIENTNET TRANSFER LEARNING", "type": "process", "description": "Train multi-label vision backbone with mixed-precision acceleration", "next_node": "node_4"},
            {"id": "node_4", "label": "DOES MEAN ROC-AUC EXCEED 0.84?", "type": "decision", "description": "Evaluate multi-label clinical diagnostic discrimination metrics", "yes_next": "node_5", "no_next": "node_3", "yes_label": "YES: Diagnostic Benchmark Achieved", "no_label": "NO: Adjust Learning Rate & Augmentation"},
            {"id": "node_5", "label": "PHASE 3: GRAD-CAM HEATMAP GENERATION", "type": "process", "description": "Compute gradient activation heatmaps to highlight anatomical pathology", "next_node": "node_6"},
            {"id": "node_6", "label": "INTERACTIVE RADIOLOGY DASHBOARD", "type": "process", "description": "Deploy side-by-side diagnostic visualizer and clinical summary export", "next_node": "node_7"},
            {"id": "node_7", "label": "END", "type": "end", "description": "Clinical diagnostic assistant pipeline operational"}
        ]
    },
    {
        "project_id": "DS-05",
        "domain": "Data Science & Machine Learning",
        "project_title": "Time-Series Demand Forecasting and Anomaly Detection System",
        "difficulty_level": "Intermediate",
        "description": "Construct an enterprise time-series forecasting and demand anomaly detection engine combining classical statistical models (SARIMAX), Facebook Prophet, and deep temporal architectures (LSTM) to project future trends with calibrated confidence intervals.",
        "learning_objectives": [
            "Deconstruct time series into trend, seasonality, and residual components",
            "Perform Augmented Dickey-Fuller (ADF) stationarity testing and differencing",
            "Train and compare SARIMAX, Facebook Prophet, and LSTM temporal models",
            "Calculate forecast uncertainty intervals and flag volume demand anomalies",
            "Build automated reporting pipelines exporting forward projections to business stakeholders"
        ],
        "required_technologies": ["Python 3", "Pandas", "Statsmodels", "Prophet", "PyTorch / TensorFlow", "Plotly", "Docker"],
        "prerequisites": ["Time-series fundamentals (autocorrelation, seasonality)", "Basic calculus and optimization", "Python data visualization"],
        "implementation_phases": [
            {
                "phase_number": 1,
                "title": "Time-Series Decomposition & Stationarity",
                "objective": "Deconstruct historical trend, seasonal cycles, and verify stationarity.",
                "tasks": ["Resample and impute missing historical timestamps using linear interpolation", "Decompose series into additive/multiplicative components (STL decomposition)", "Execute Augmented Dickey-Fuller (ADF) test and apply first-order differencing"],
                "technologies_used": ["Pandas", "Statsmodels"],
                "expected_output": "Stationary time-series data with documented seasonal period lengths."
            },
            {
                "phase_number": 2,
                "title": "SARIMAX & Prophet Model Fitting",
                "objective": "Fit statistical and additive models with calendar holiday regressors.",
                "tasks": ["Identify optimal (p,d,q)(P,D,Q) orders using AIC grid search", "Fit Facebook Prophet model incorporating custom holiday regressors", "Evaluate rolling walk-forward cross-validation across 12 forecasting horizons"],
                "technologies_used": ["Statsmodels", "Prophet"],
                "expected_output": "Fitted baseline and additive models with quantified MAPE < 8%."
            },
            {
                "phase_number": 3,
                "title": "Deep Learning LSTM Model & Ensemble",
                "objective": "Train sequence-to-sequence LSTM network for non-linear temporal dynamics.",
                "tasks": ["Construct sliding lookback window dataset (past 30 days -> next 7 days)", "Train PyTorch LSTM model with dropout regularization", "Construct weighted blend ensemble combining Prophet and LSTM outputs"],
                "technologies_used": ["PyTorch", "NumPy"],
                "expected_output": "Ensemble forecasting pipeline outperforming individual model baselines."
            },
            {
                "phase_number": 4,
                "title": "Anomaly Spike Detection & Visual Projections",
                "objective": "Detect demand spikes exceeding confidence bands and render projections.",
                "tasks": ["Flag observations falling outside 95% forecast confidence interval as anomalies", "Generate interactive Plotly visualization displaying historical, forecast, and anomaly flags", "Build automated batch job generating weekly PDF executive summary"],
                "technologies_used": ["Plotly", "Docker"],
                "expected_output": "Interactive visualization and automated weekly projection reports."
            }
        ],
        "expected_deliverables": [
            "Complete Time-Series Modeling and Validation Notebook",
            "Ensemble Forecasting Module (`forecaster.py`)",
            "Interactive Plotly Forecast Dashboard application",
            "Executive Demand Forecasting Technical Documentation"
        ],
        "testing_validation_plan": [
            "Execute strict temporal walk-forward backtesting with zero future data leakage",
            "Verify Mean Absolute Percentage Error (MAPE) < 8.5% across test horizons",
            "Validate anomaly detection precision on simulated demand shock events"
        ],
        "skills_demonstrated": ["Time Series Analysis (SARIMAX/Prophet)", "Deep Learning for Sequences (LSTM)", "Stationarity & STL Decomposition", "Anomaly Detection in Time Series", "Plotly Visualization"],
        "project_workflow": [
            {"id": "node_1", "label": "START", "type": "start", "description": "Initiate time-series forecasting project", "next_node": "node_2"},
            {"id": "node_2", "label": "PHASE 1: TEMPORAL DECOMPOSITION & STATIONARITY", "type": "process", "description": "Deconstruct trend/seasonality and execute ADF stationarity test", "next_node": "node_3"},
            {"id": "node_3", "label": "PHASE 2: MODEL TRAINING (PROPHET & SARIMAX)", "type": "process", "description": "Fit additive Prophet model with calendar regressors and ARIMA orders", "next_node": "node_4"},
            {"id": "node_4", "label": "PHASE 3: DEEP LEARNING LSTM ENSEMBLE", "type": "process", "description": "Train sliding-window LSTM network and build weighted ensemble blend", "next_node": "node_5"},
            {"id": "node_5", "label": "DOES FORECAST MAPE REMAIN < 8.5%?", "type": "decision", "description": "Evaluate Mean Absolute Percentage Error on walk-forward backtest", "yes_next": "node_6", "no_next": "node_3", "yes_label": "YES: Accuracy Benchmark Met", "no_label": "NO: Refine Seasonality Orders & Hyperparameters"},
            {"id": "node_6", "label": "PHASE 4: ANOMALY SPIKE DETECTION", "type": "process", "description": "Identify historical and live observations breaching 95% confidence intervals", "next_node": "node_7"},
            {"id": "node_7", "label": "INTERACTIVE FORECAST DASHBOARD", "type": "process", "description": "Deploy Plotly visualizer and automated executive projection export", "next_node": "node_8"},
            {"id": "node_8", "label": "END", "type": "end", "description": "Time-series forecasting pipeline operational"}
        ]
    }
]


# ==============================================================================
# 3. CLOUD & DEVOPS DOMAIN (5 DISTINCT PROJECTS)
# ==============================================================================

CLOUD_DEVOPS_PROJECTS: List[Dict[str, Any]] = [
    {
        "project_id": "CD-01",
        "domain": "Cloud & DevOps",
        "project_title": "Automated Multi-Stage CI/CD Deployment Pipeline with Security Gates",
        "difficulty_level": "Intermediate",
        "description": "Construct an enterprise-grade automated CI/CD pipeline using GitHub Actions, Docker, SonarQube, and Trivy that automatically runs unit tests, executes Static Application Security Testing (SAST), scans container images for CVEs, and deploys to a staging environment upon passing quality gates.",
        "learning_objectives": [
            "Design declarative multi-stage CI/CD workflows using GitHub Actions",
            "Integrate automated SAST and container vulnerability scanning into the pipeline",
            "Implement automated quality gates that halt builds on High/Critical vulnerabilities",
            "Build optimized multi-stage Dockerfiles adhering to least-privilege security",
            "Configure zero-downtime blue/green deployment orchestration"
        ],
        "required_technologies": ["GitHub Actions", "Docker", "Trivy", "SonarQube / SonarCloud", "Linux", "Node.js / Python"],
        "prerequisites": ["Git branching strategies", "Basic Docker containerization", "Familiarity with YAML syntax"],
        "implementation_phases": [
            {"phase_number": 1, "title": "Pipeline Architecture & Unit Testing", "objective": "Set up automated test runner triggered on pull request.", "tasks": ["Configure GitHub Actions workflow triggers", "Execute test runner with code coverage reporting", "Enforce branch protection rules"], "technologies_used": ["GitHub Actions", "Jest / Pytest"], "expected_output": "Automated test validation on every pull request."},
            {"phase_number": 2, "title": "Static Security & Container Scanning", "objective": "Integrate SAST and container image vulnerability scanners.", "tasks": ["Integrate SonarCloud code quality scanner", "Build multi-stage Docker container", "Run Trivy container scan halting on CRITICAL CVEs"], "technologies_used": ["SonarQube", "Trivy", "Docker"], "expected_output": "Automated vulnerability check blocking insecure builds."},
            {"phase_number": 3, "title": "Staging Deployment & Health Probing", "objective": "Deploy verified container to staging environment.", "tasks": ["Push tagged image to GitHub Container Registry", "Deploy container to staging host via SSH action", "Execute automated HTTP synthetic health check"], "technologies_used": ["GHCR", "Docker Compose", "cURL"], "expected_output": "Automated zero-downtime deployment to staging."},
            {"phase_number": 4, "title": "Alerting & Telemetry Integration", "objective": "Notify team of build status and track build metrics.", "tasks": ["Configure Slack/Discord webhook build notifications", "Record deployment metrics in Prometheus", "Compile CI/CD pipeline operational runbook"], "technologies_used": ["Webhooks", "Markdown"], "expected_output": "Real-time deployment alerts and comprehensive documentation."}
        ],
        "expected_deliverables": [
            "Declarative GitHub Actions Workflow definitions (`.github/workflows/deploy.yml`)",
            "Multi-stage secure Dockerfile (`Dockerfile`)",
            "Trivy vulnerability scan report and resolution audit",
            "CI/CD Architecture Diagram and Deployment Runbook"
        ],
        "testing_validation_plan": [
            "Simulate pull request with failing test; verify pipeline halts",
            "Inject known vulnerable npm/pip dependency; verify Trivy gate halts deployment",
            "Verify successful automated deployment when all checks pass"
        ],
        "skills_demonstrated": ["CI/CD Pipeline Design", "DevSecOps (SAST/Trivy)", "Docker Containerization", "GitHub Actions", "Automated Testing Integration"],
        "project_workflow": [
            {"id": "node_1", "label": "START", "type": "start", "description": "Developer pushes code to repository", "next_node": "node_2"},
            {"id": "node_2", "label": "PHASE 1: AUTOMATED UNIT & INTEGRATION TESTING", "type": "process", "description": "Execute automated test suites and verify code coverage threshold", "next_node": "node_3"},
            {"id": "node_3", "label": "PHASE 2: SAST CODE QUALITY SCAN", "type": "process", "description": "Run SonarQube static analysis checking code smells and security bugs", "next_node": "node_4"},
            {"id": "node_4", "label": "PHASE 3: DOCKER BUILD & TRIVY CVE SCAN", "type": "process", "description": "Build multi-stage container image and scan with Trivy", "next_node": "node_5"},
            {"id": "node_5", "label": "DO ALL TESTS & SECURITY GATES PASS?", "type": "decision", "description": "Verify zero test failures and zero Critical/High CVEs", "yes_next": "node_6", "no_next": "node_7", "yes_label": "YES: Gates Passed", "no_label": "NO: Build Halted"},
            {"id": "node_6", "label": "PHASE 4: STAGING DEPLOYMENT & HEALTH CHECK", "type": "process", "description": "Deploy container to staging and verify synthetic health probe", "next_node": "node_8"},
            {"id": "node_7", "label": "DISPATCH FAILURE NOTIFICATION", "type": "process", "description": "Notify developers of security flaw or test failure via webhook", "next_node": "node_9"},
            {"id": "node_8", "label": "DISPATCH SUCCESS NOTIFICATION", "type": "process", "description": "Notify team of successful deployment with commit SHA", "next_node": "node_9"},
            {"id": "node_9", "label": "END", "type": "end", "description": "CI/CD execution completed"}
        ]
    },
    {
        "project_id": "CD-02",
        "domain": "Cloud & DevOps",
        "project_title": "Kubernetes Cluster Provisioning and Microservices Service Mesh",
        "difficulty_level": "Advanced",
        "description": "Deploy an enterprise multi-node Kubernetes cluster utilizing Infrastructure as Code, deploy a containerized microservices application, configure Istio Service Mesh for mutual TLS (mTLS) traffic encryption, and implement canary release routing.",
        "learning_objectives": [
            "Provision and configure multi-node Kubernetes clusters (k3s / Kind / EKS)",
            "Author modular Kubernetes manifests (Deployments, Services, ConfigMaps, Ingress)",
            "Deploy Istio Service Mesh to enforce strict mTLS communication between pods",
            "Configure traffic management for canary deployments (90% v1 / 10% v2)",
            "Implement resource limits, liveness/readiness probes, and horizontal pod autoscaling"
        ],
        "required_technologies": ["Kubernetes (k3s / Kind)", "Istio Service Mesh", "Helm", "kubectl", "Docker", "Prometheus"],
        "prerequisites": ["Docker containerization proficiency", "Linux networking and DNS basics", "YAML syntax fluency"],
        "implementation_phases": [
            {"phase_number": 1, "title": "Cluster Provisioning & Architecture", "objective": "Deploy multi-node local cluster with resource isolation.", "tasks": ["Provision 3-node Kubernetes cluster using Kind/k3s", "Configure namespaces for dev, staging, and production", "Configure metalLB / Ingress-NGINX for external traffic routing"], "technologies_used": ["Kind / k3s", "kubectl"], "expected_output": "Operational 3-node cluster with ready node status."},
            {"phase_number": 2, "title": "Microservices Deployment with Helm", "objective": "Package and deploy multi-tier microservices app.", "tasks": ["Create Helm chart for frontend, API, and worker microservices", "Configure resource requests, limits, and securityContexts", "Implement liveness and readiness health probes"], "technologies_used": ["Helm", "Kubernetes"], "expected_output": "Declarative multi-pod microservices deployment running cleanly."},
            {"phase_number": 3, "title": "Istio Service Mesh & mTLS Enforcement", "objective": "Deploy Istio and mandate zero-trust mutual TLS encryption.", "tasks": ["Install Istio control plane using istioctl", "Enable automatic sidecar injection on microservices namespace", "Apply PeerAuthentication policy mandating STRICT mTLS mode"], "technologies_used": ["Istio", "Envoy Proxy"], "expected_output": "All inter-pod traffic encrypted with mutual TLS."},
            {"phase_number": 4, "title": "Canary Traffic Shifting & Autoscaling", "objective": "Implement intelligent routing and horizontal scaling.", "tasks": ["Configure Istio VirtualService splitting traffic (90% v1 / 10% v2)", "Configure Horizontal Pod Autoscaler (HPA) targeting 70% CPU", "Simulate traffic load and verify automated scaling"], "technologies_used": ["Istio VirtualService", "HPA"], "expected_output": "Validated canary traffic shifting and responsive autoscaling."}
        ],
        "expected_deliverables": [
            "Kubernetes Manifests & Helm Charts (`charts/microservices/`)",
            "Istio Service Mesh Security and Routing Configurations (`istio/`)",
            "Kiali Service Mesh Topology Visualization screenshots",
            "Kubernetes Production Readiness and Security Checklist"
        ],
        "testing_validation_plan": [
            "Execute packet capture between pods to verify plaintext data is invisible (mTLS active)",
            "Run hey/wrk load generator to verify HPA triggers pod replica scale-out",
            "Verify canary deployment directs exactly 10% of HTTP traffic to v2"
        ],
        "skills_demonstrated": ["Kubernetes Administration", "Service Mesh (Istio)", "Helm Package Management", "Canary Deployments", "Mutual TLS Security"],
        "project_workflow": [
            {"id": "node_1", "label": "START", "type": "start", "description": "Initiate Kubernetes cluster deployment", "next_node": "node_2"},
            {"id": "node_2", "label": "PHASE 1: MULTI-NODE CLUSTER SETUP", "type": "process", "description": "Deploy 3-node cluster and configure ingress controller", "next_node": "node_3"},
            {"id": "node_3", "label": "PHASE 2: HELM MICROSERVICES DEPLOYMENT", "type": "process", "description": "Deploy containerized microservices with resource limits and probes", "next_node": "node_4"},
            {"id": "node_4", "label": "PHASE 3: ISTIO SERVICE MESH INJECTION", "type": "process", "description": "Inject Envoy sidecars and enforce STRICT mTLS encryption policy", "next_node": "node_5"},
            {"id": "node_5", "label": "DOES MTLS ENFORCEMENT & HEALTH PROBES PASS?", "type": "decision", "description": "Verify zero plaintext traffic and 100% pod readiness", "yes_next": "node_6", "no_next": "node_3", "yes_label": "YES: Mesh Verified", "no_label": "NO: Fix Manifests & Sidecars"},
            {"id": "node_6", "label": "PHASE 4: CANARY ROUTING & HPA AUTOSCALING", "type": "process", "description": "Configure 90/10 canary traffic shifting and Horizontal Pod Autoscaling", "next_node": "node_7"},
            {"id": "node_7", "label": "END", "type": "end", "description": "Kubernetes service mesh architecture fully operational"}
        ]
    },
    {
        "project_id": "CD-03",
        "domain": "Cloud & DevOps",
        "project_title": "Cloud Infrastructure as Code (IaC) with Terraform & Compliance Guardrails",
        "difficulty_level": "Intermediate",
        "description": "Architect a modular, secure cloud infrastructure stack on AWS / LocalStack using Terraform, incorporating automated policy-as-code security scans (tfsec, Checkov), remote state locking with DynamoDB, and least-privilege IAM configurations.",
        "learning_objectives": [
            "Structure production-grade Terraform modules with variables and outputs",
            "Implement remote backend state storage with S3 and DynamoDB locking",
            "Execute automated policy-as-code static checks using tfsec and Checkov",
            "Provision secure VPC networking (public/private subnets, NAT gateways, security groups)",
            "Enforce least-privilege cloud IAM roles and KMS customer-managed encryption"
        ],
        "required_technologies": ["Terraform", "AWS / LocalStack", "Checkov", "tfsec", "Docker", "Git"],
        "prerequisites": ["Basic cloud infrastructure concepts (VPC, EC2, S3, IAM)", "Understanding of IaC principles"],
        "implementation_phases": [
            {"phase_number": 1, "title": "Terraform Module & Remote Backend Setup", "objective": "Configure modular Terraform structure and secure remote state.", "tasks": ["Create S3 bucket with versioning and encryption for state storage", "Create DynamoDB table for distributed state locking", "Configure Terraform remote backend provider"], "technologies_used": ["Terraform", "AWS S3", "DynamoDB"], "expected_output": "Secure state management with concurrency locking."},
            {"phase_number": 2, "title": "VPC & Network Security Architecture", "objective": "Provision multi-AZ network topology with private subnets.", "tasks": ["Provision VPC across 2 Availability Zones", "Create public and private subnets with route tables and NAT gateways", "Configure granular Security Groups denying all ingress by default"], "technologies_used": ["Terraform AWS Provider"], "expected_output": "Isolated network architecture with zero unneeded public exposure."},
            {"phase_number": 3, "title": "Policy-as-Code Static Analysis & Scanning", "objective": "Validate Terraform code against CIS Benchmark security controls.", "tasks": ["Run tfsec against all Terraform modules", "Run Checkov compliance scans checking for unencrypted storage and wildcards", "Remediate flagged findings and re-scan"], "technologies_used": ["tfsec", "Checkov"], "expected_output": "100% clean security scan with zero High/Critical findings."},
            {"phase_number": 4, "title": "Automated Deployment & Destroy Verification", "objective": "Verify idempotent planning, deployment, and teardown.", "tasks": ["Execute `terraform plan` and verify zero drift", "Execute `terraform apply` deploying verified resources", "Test automated teardown with `terraform destroy`"], "technologies_used": ["Terraform CLI"], "expected_output": "Fully automated, repeatable cloud infrastructure lifecycle."}
        ],
        "expected_deliverables": [
            "Modular Terraform Repository (`modules/vpc`, `modules/compute`, `modules/iam`)",
            "Policy-as-Code scan reports (Checkov & tfsec passing audit logs)",
            "Cloud Architecture Diagram with network flow and security boundaries",
            "Terraform Best Practices and State Management Guide"
        ],
        "testing_validation_plan": [
            "Run Checkov in CI to block any commit introducing 0.0.0.0/0 ingress to port 22",
            "Verify concurrent `terraform apply` commands halt due to DynamoDB state lock",
            "Confirm all S3 buckets enforce KMS encryption and block public access"
        ],
        "skills_demonstrated": ["Infrastructure as Code (Terraform)", "Cloud Security (AWS/LocalStack)", "Policy as Code (Checkov/tfsec)", "VPC Networking", "IAM Hardening"],
        "project_workflow": [
            {"id": "node_1", "label": "START", "type": "start", "description": "Initiate Infrastructure as Code project", "next_node": "node_2"},
            {"id": "node_2", "label": "PHASE 1: MODULE DESIGN & REMOTE BACKEND", "type": "process", "description": "Configure S3 versioned state storage and DynamoDB locking", "next_node": "node_3"},
            {"id": "node_3", "label": "PHASE 2: SECURE VPC ARCHITECTURE", "type": "process", "description": "Define multi-AZ subnets, NAT gateways, and least-privilege security groups", "next_node": "node_4"},
            {"id": "node_4", "label": "PHASE 3: POLICY-AS-CODE SCANNING", "type": "process", "description": "Run Checkov and tfsec static security audits against IaC manifests", "next_node": "node_5"},
            {"id": "node_5", "label": "DO CHECKS PASS WITH ZERO CRITICAL FLAWS?", "type": "decision", "description": "Verify CIS Benchmark compliance and zero exposed secrets", "yes_next": "node_6", "no_next": "node_3", "yes_label": "YES: Security Audit Passed", "no_label": "NO: Fix Misconfigurations & Re-scan"},
            {"id": "node_6", "label": "PHASE 4: TERRAFORM APPLY & VERIFICATION", "type": "process", "description": "Execute idempotent provisioning and audit cloud resources", "next_node": "node_7"},
            {"id": "node_7", "label": "END", "type": "end", "description": "Cloud infrastructure provisioned and verified"}
        ]
    },
    {
        "project_id": "CD-04",
        "domain": "Cloud & DevOps",
        "project_title": "Centralized Observability and Distributed Tracing Stack",
        "difficulty_level": "Intermediate",
        "description": "Deploy an enterprise observability stack integrating Prometheus for metrics scraping, Grafana for real-time visualization dashboards, Loki for centralized log aggregation, and OpenTelemetry / Jaeger for end-to-end distributed transaction tracing.",
        "learning_objectives": [
            "Deploy and configure Prometheus scraping targets and metric relabeling rules",
            "Design actionable operational Grafana dashboards utilizing PromQL queries",
            "Configure Grafana Loki with Promtail for structured container log streaming",
            "Instrument applications with OpenTelemetry SDK for distributed span tracing",
            "Implement automated alert routing with Prometheus Alertmanager"
        ],
        "required_technologies": ["Prometheus", "Grafana", "Loki", "Promtail", "OpenTelemetry", "Jaeger", "Docker Compose"],
        "prerequisites": ["Docker Compose familiarity", "Basic understanding of metrics (counter, gauge, histogram)"],
        "implementation_phases": [
            {"phase_number": 1, "title": "Observability Infrastructure Deployment", "objective": "Deploy Prometheus, Grafana, Loki, and Jaeger via Docker Compose.", "tasks": ["Configure multi-container Docker Compose stack with persistent volumes", "Configure Prometheus scraping parameters (15s scrape interval)", "Configure Grafana datasources for Prometheus, Loki, and Jaeger"], "technologies_used": ["Docker Compose", "Prometheus", "Grafana"], "expected_output": "Operational observability stack accessible on Grafana UI."},
            {"phase_number": 2, "title": "Application Instrumentation & Distributed Tracing", "objective": "Instrument microservices with OpenTelemetry exporter.", "tasks": ["Instrument Python/Node microservices with OpenTelemetry SDK", "Propagate W3C trace context across HTTP service calls", "Export spans to Jaeger receiver and verify trace visualization"], "technologies_used": ["OpenTelemetry", "Jaeger"], "expected_output": "End-to-end distributed trace spans visualizing service latencies."},
            {"phase_number": 3, "title": "Log Aggregation with Grafana Loki", "objective": "Stream container logs into centralized queryable index.", "tasks": ["Deploy Promtail agent to discover and scrape Docker container logs", "Configure parsing labels (service, level, trace_id)", "Link logs to traces in Grafana using trace_id correlation"], "technologies_used": ["Grafana Loki", "Promtail"], "expected_output": "Seamless jump from trace latency spike directly to matching error log."},
            {"phase_number": 4, "title": "PromQL Dashboard Studio & Alerting Rules", "objective": "Build operational dashboards and alert rules.", "tasks": ["Write PromQL queries for p95/p99 latency, error rate, and memory saturation", "Build Golden Signals operational dashboard", "Configure Alertmanager alerting on error rate > 5% for 2 minutes"], "technologies_used": ["PromQL", "Alertmanager"], "expected_output": "Production dashboard and automated incident alerts."}
        ],
        "expected_deliverables": [
            "Docker Compose Observability Stack definition (`docker-compose.monitoring.yml`)",
            "Grafana Operational Dashboard JSON definition (`dashboards/golden_signals.json`)",
            "Prometheus Alertmanager rules (`alertmanager.yml`)",
            "OpenTelemetry Application Instrumentation Guide"
        ],
        "testing_validation_plan": [
            "Simulate HTTP 500 error burst and confirm Alertmanager alert fires within 120s",
            "Verify clicking a trace span in Grafana navigates directly to matching Loki log entry",
            "Validate Prometheus metric retention and disk usage over 48 hours"
        ],
        "skills_demonstrated": ["Site Reliability Engineering (SRE)", "Metrics & Monitoring (Prometheus/PromQL)", "Grafana Dashboard Design", "Log Aggregation (Loki)", "Distributed Tracing (OpenTelemetry/Jaeger)"],
        "project_workflow": [
            {"id": "node_1", "label": "START", "type": "start", "description": "Initiate observability stack deployment", "next_node": "node_2"},
            {"id": "node_2", "label": "PHASE 1: MONITORING INFRASTRUCTURE SETUP", "type": "process", "description": "Deploy Prometheus, Grafana, Loki, and Jaeger containers", "next_node": "node_3"},
            {"id": "node_3", "label": "PHASE 2: OPENTELEMETRY SPAN INSTRUMENTATION", "type": "process", "description": "Instrument microservices to emit distributed trace spans and metrics", "next_node": "node_4"},
            {"id": "node_4", "label": "PHASE 3: LOKI LOG AGGREGATION & TRACE LINKING", "type": "process", "description": "Stream container logs into Loki and link logs with trace IDs", "next_node": "node_5"},
            {"id": "node_5", "label": "DO METRICS, TRACES & LOGS CORRELATE?", "type": "decision", "description": "Verify seamless transition from trace latency spike to matching log", "yes_next": "node_6", "no_next": "node_3", "yes_label": "YES: Telemetry Correlated", "no_label": "NO: Fix Trace Propagation Headers"},
            {"id": "node_6", "label": "PHASE 4: DASHBOARD & ALERTMANAGER CONFIG", "type": "process", "description": "Build Golden Signals PromQL dashboard and configure alert routing", "next_node": "node_7"},
            {"id": "node_7", "label": "END", "type": "end", "description": "Enterprise observability stack fully deployed"}
        ]
    },
    {
        "project_id": "CD-05",
        "domain": "Cloud & DevOps",
        "project_title": "Zero-Trust Cloud Identity and Secrets Management Architecture",
        "difficulty_level": "Advanced",
        "description": "Implement an enterprise zero-trust secrets management architecture using HashiCorp Vault, automatic dynamic database credentials, short-lived PKI certificates, and Kubernetes service account token integration to eliminate static API keys.",
        "learning_objectives": [
            "Deploy and initialize HashiCorp Vault with Shamir secret keys and unsealing",
            "Configure Vault dynamic secrets engine for on-demand PostgreSQL credentials",
            "Set up Vault PKI engine to automatically issue and renew short-lived TLS certificates",
            "Integrate Vault Agent with Kubernetes for seamless pod credential injection",
            "Enforce least-privilege Vault policies and audit device logging"
        ],
        "required_technologies": ["HashiCorp Vault", "PostgreSQL", "Docker", "Kubernetes", "OpenSSL", "Linux"],
        "prerequisites": ["Understanding of public-key cryptography (PKI/TLS)", "Docker and Linux administration skills"],
        "implementation_phases": [
            {"phase_number": 1, "title": "Vault Deployment & Cluster Initialization", "objective": "Deploy Vault server and configure file storage backend.", "tasks": ["Deploy HashiCorp Vault in server mode", "Initialize Vault and securely capture Shamir unseal keys", "Configure Vault audit device writing JSON logs"], "technologies_used": ["HashiCorp Vault", "Docker"], "expected_output": "Operational initialized Vault server with active audit logging."},
            {"phase_number": 2, "title": "Dynamic Database Credentials Engine", "objective": "Eliminate static database passwords using on-demand credentials.", "tasks": ["Mount and configure Vault database secrets engine pointing to PostgreSQL", "Define dynamic role generating ephemeral credentials with 1-hour TTL", "Validate automatic revocation upon TTL expiry"], "technologies_used": ["Vault Database Engine", "PostgreSQL"], "expected_output": "Ephemeral, auto-expiring database users generated on request."},
            {"phase_number": 3, "title": "Automated PKI Secrets Engine", "objective": "Issue short-lived internal TLS certificates on demand.", "tasks": ["Mount Vault PKI secrets engine and generate root CA", "Configure intermediate CA with role for internal microservice domains", "Issue and automatically renew 24-hour leaf certificates"], "technologies_used": ["Vault PKI", "OpenSSL"], "expected_output": "Automated internal certificate authority issuing trusted TLS certs."},
            {"phase_number": 4, "title": "Vault Agent Injection & Policy Hardening", "objective": "Inject credentials into application pods without code changes.", "tasks": ["Configure Vault Kubernetes auth method", "Deploy application pod with Vault Agent sidecar injector", "Verify application reads dynamic credentials without hardcoded secrets"], "technologies_used": ["Vault Agent", "Kubernetes"], "expected_output": "Zero hardcoded credentials in source code or container images."}
        ],
        "expected_deliverables": [
            "Vault Server Configuration and Policy definitions (`vault/policies/`)",
            "Dynamic Database and PKI Automation scripts (`scripts/vault_setup.sh`)",
            "Kubernetes Vault Agent Deployment manifest (`k8s/app_with_vault.yaml`)",
            "Zero-Trust Secrets Management Architecture Whitepaper"
        ],
        "testing_validation_plan": [
            "Verify dynamic PostgreSQL credentials expire and cease access after 1-hour TTL",
            "Audit Vault log files to confirm every secret request is captured with caller identity",
            "Attempt secret access with unauthorized policy; verify strict HTTP 403 denial"
        ],
        "skills_demonstrated": ["Secrets Management (HashiCorp Vault)", "Zero-Trust Architecture", "Dynamic Database Credentials", "PKI & Certificate Authority", "Kubernetes Secret Injection"],
        "project_workflow": [
            {"id": "node_1", "label": "START", "type": "start", "description": "Initiate zero-trust secrets project", "next_node": "node_2"},
            {"id": "node_2", "label": "PHASE 1: VAULT SERVER & AUDIT INITIALIZATION", "type": "process", "description": "Deploy Vault server, configure Shamir unsealing, and enable audit logs", "next_node": "node_3"},
            {"id": "node_3", "label": "PHASE 2: DYNAMIC DATABASE SECRETS ENGINE", "type": "process", "description": "Configure on-demand ephemeral credentials with 1-hour auto-revocation", "next_node": "node_4"},
            {"id": "node_4", "label": "PHASE 3: PKI INTERNAL CERTIFICATE AUTHORITY", "type": "process", "description": "Deploy internal CA issuing short-lived mutual TLS leaf certificates", "next_node": "node_5"},
            {"id": "node_5", "label": "DO EXPIRY & ACCESS CONTROL AUDITS PASS?", "type": "decision", "description": "Verify credentials auto-expire and unauthorized access is blocked", "yes_next": "node_6", "no_next": "node_3", "yes_label": "YES: Zero-Trust Verified", "no_label": "NO: Tighten Policies & Lease TTLs"},
            {"id": "node_6", "label": "PHASE 4: VAULT AGENT SIDECAR INJECTION", "type": "process", "description": "Inject dynamic secrets into application pods without hardcoded keys", "next_node": "node_7"},
            {"id": "node_7", "label": "END", "type": "end", "description": "Zero-trust secrets management architecture operational"}
        ]
    }
]


# ==============================================================================
# 4. FULL STACK WEB DEVELOPMENT DOMAIN (5 DISTINCT PROJECTS)
# ==============================================================================

FULL_STACK_PROJECTS: List[Dict[str, Any]] = [
    {
        "project_id": "FS-01",
        "domain": "Full Stack Web Development",
        "project_title": "Enterprise Inventory Management System with Role-Based Access Control",
        "difficulty_level": "Intermediate",
        "description": "Construct a full-stack enterprise inventory and order tracking web application utilizing React, Node.js / Express, PostgreSQL, and JWT authentication with role-based access control (Admin, Manager, Warehouse Clerk) and transactional stock updates.",
        "learning_objectives": [
            "Design normalized relational database schemas with foreign key integrity and constraints",
            "Implement secure JWT authentication with HTTP-only cookies and role-based middleware",
            "Execute atomic database transactions preventing concurrent inventory overselling",
            "Build responsive, component-driven user interfaces utilizing React and Tailwind CSS",
            "Implement audit trail logging capturing all inventory adjustments with user IDs"
        ],
        "required_technologies": ["React.js", "Node.js", "Express.js", "PostgreSQL", "Tailwind CSS", "Docker", "Jest"],
        "prerequisites": ["JavaScript / ES6+ fundamentals", "Basic relational SQL queries", "Familiarity with React components"],
        "implementation_phases": [
            {"phase_number": 1, "title": "Database Schema & Transactional Layer", "objective": "Model relational database schema with ACID transaction support.", "tasks": ["Design ER diagram for Users, Roles, Products, Categories, and Orders", "Write PostgreSQL migration scripts with foreign key constraints", "Implement stock reduction within serializable database transactions"], "technologies_used": ["PostgreSQL", "pg-promise / Prisma"], "expected_output": "Normalized database schema with zero stock over-allocation risk."},
            {"phase_number": 2, "title": "RESTful API & RBAC Middleware", "objective": "Build backend endpoints secured with granular role checks.", "tasks": ["Implement bcrypt password hashing and JWT token issuance", "Author RBAC middleware verifying permissions per route", "Build CRUD endpoints for inventory, stock adjustments, and supplier tracking"], "technologies_used": ["Node.js", "Express", "JWT"], "expected_output": "Secure REST API with comprehensive role-based authorization."},
            {"phase_number": 3, "title": "React Frontend & State Management", "objective": "Construct modern interactive dashboard interface.", "tasks": ["Build product catalog table with live search, filtering, and pagination", "Build order processing modal with stock availability validation", "Implement role-conditional UI views (e.g., hiding edit buttons from clerks)"], "technologies_used": ["React", "Tailwind CSS", "Axios"], "expected_output": "Responsive single-page application with smooth state updates."},
            {"phase_number": 4, "title": "Audit Logging & Deployment", "objective": "Implement immutable activity logs and containerize application.", "tasks": ["Log all stock adjustments with timestamp, user ID, and delta", "Package frontend and backend into unified Docker Compose stack", "Execute end-to-end integration tests"], "technologies_used": ["Docker Compose", "Jest"], "expected_output": "Production containerized web application with audit logging."}
        ],
        "expected_deliverables": [
            "Full-Stack Monorepo source code (`frontend/` and `backend/`)",
            "PostgreSQL Database Schema Migration scripts (`migrations/`)",
            "Comprehensive API Documentation (Swagger / OpenAPI specification)",
            "Docker Compose Deployment definition (`docker-compose.yml`)"
        ],
        "testing_validation_plan": [
            "Execute concurrent order placement test simulating 20 simultaneous purchases on 1 available item",
            "Verify warehouse clerk token receives HTTP 403 Forbidden when attempting price updates",
            "Audit database transaction rollback upon simulated payment gateway timeout"
        ],
        "skills_demonstrated": ["Full-Stack Architecture (React/Node)", "Relational Database Design (PostgreSQL)", "Role-Based Access Control (RBAC)", "ACID Database Transactions", "Containerized Deployment"],
        "project_workflow": [
            {"id": "node_1", "label": "START", "type": "start", "description": "Initiate full-stack project development", "next_node": "node_2"},
            {"id": "node_2", "label": "PHASE 1: DATABASE SCHEMA & ACID TRANSACTIONS", "type": "process", "description": "Model normalized PostgreSQL schema with foreign keys and stock locks", "next_node": "node_3"},
            {"id": "node_3", "label": "PHASE 2: SECURE REST API & RBAC MIDDLEWARE", "type": "process", "description": "Implement JWT auth in HTTP-only cookies and role authorization gates", "next_node": "node_4"},
            {"id": "node_4", "label": "PHASE 3: REACT DASHBOARD & STATE MANAGEMENT", "type": "process", "description": "Build responsive catalog tables, stock adjustment modals, and role views", "next_node": "node_5"},
            {"id": "node_5", "label": "DO CONCURRENCY & PERMISSION TESTS PASS?", "type": "decision", "description": "Verify zero overselling during race conditions and strict RBAC enforcement", "yes_next": "node_6", "no_next": "node_2", "yes_label": "YES: Tests Verified", "no_label": "NO: Fix Isolation Level & Auth Middleware"},
            {"id": "node_6", "label": "PHASE 4: AUDIT LOGS & DOCKER PACKAGING", "type": "process", "description": "Record immutable stock adjustment trails and package in Docker Compose", "next_node": "node_7"},
            {"id": "node_7", "label": "END", "type": "end", "description": "Enterprise inventory management system deployed"}
        ]
    },
    {
        "project_id": "FS-02",
        "domain": "Full Stack Web Development",
        "project_title": "Real-time Collaborative Document Workspace with WebSockets",
        "difficulty_level": "Advanced",
        "description": "Architect a real-time collaborative document editing application featuring live multi-user cursor presence, operational transformation / CRDT conflict resolution, version history snapshots, and WebSocket reconnection resilience using React, Node.js, and Redis.",
        "learning_objectives": [
            "Implement bi-directional WebSocket communication utilizing Socket.io / ws",
            "Apply Conflict-free Replicated Data Types (CRDTs) or Operational Transformation (OT)",
            "Build real-time remote user cursor presence indicators and color assignments",
            "Design Redis pub/sub backplane to scale WebSocket connections horizontally",
            "Implement periodic snapshotting and document revision history rollbacks"
        ],
        "required_technologies": ["React.js", "Node.js", "Socket.io", "Redis Pub/Sub", "MongoDB / PostgreSQL", "Docker"],
        "prerequisites": ["Asynchronous JavaScript proficiency", "Event-driven programming concepts", "Understanding of WebSockets"],
        "implementation_phases": [
            {"phase_number": 1, "title": "WebSocket Architecture & Real-Time Transport", "objective": "Establish low-latency bi-directional event transport layer.", "tasks": ["Deploy Node.js WebSocket server with heartbeat pings", "Implement room-based document partitioning", "Handle network disconnects and automatic client reconnection"], "technologies_used": ["Node.js", "Socket.io"], "expected_output": "Stable WebSocket connection maintaining < 15ms message roundtrip."},
            {"phase_number": 2, "title": "Collaborative Conflict Resolution Engine", "objective": "Implement CRDT / OT algorithm preventing text overwrite collisions.", "tasks": ["Implement character-level offset tracking for concurrent typing", "Apply operational transforms adjusting remote cursor positions", "Ensure convergent document state across all connected clients"], "technologies_used": ["Yjs / Automerge / Custom OT", "JavaScript"], "expected_output": "100% convergent document text across multiple simultaneous typists."},
            {"phase_number": 3, "title": "Live Presence & Rich Text UI", "objective": "Build interactive document editor with remote user presence.", "tasks": ["Build rich-text editor interface with formatting toolbar", "Render remote user cursors with name tags and distinct colors", "Display active collaborator avatar list with live connection status"], "technologies_used": ["React", "Tailwind CSS"], "expected_output": "Interactive document canvas displaying live remote collaborator cursors."},
            {"phase_number": 4, "title": "Redis Scalability & Revision History", "objective": "Scale horizontally using Redis and capture periodic snapshots.", "tasks": ["Configure Redis Pub/Sub adapter to sync multiple WebSocket server instances", "Persist periodic document snapshots and incremental deltas to database", "Implement revision history viewer allowing document restore to any point"], "technologies_used": ["Redis Pub/Sub", "MongoDB / PostgreSQL"], "expected_output": "Horizontally scalable collaborative platform with version rollback."}
        ],
        "expected_deliverables": [
            "Real-Time Document Collaboration Engine source code",
            "Redis Pub/Sub Multi-Node WebSocket Scaling configuration",
            "Concurrency Benchmark Suite verifying zero data loss with 50 simultaneous typists",
            "Interactive Web Application with document history rollback"
        ],
        "testing_validation_plan": [
            "Simulate 10 automated headless browsers typing concurrently in same sentence; verify no character loss",
            "Sever client network connection for 5 seconds; verify smooth delta synchronization upon reconnect",
            "Audit memory leak stability over 2 hours of continuous WebSocket messaging"
        ],
        "skills_demonstrated": ["Real-Time Systems (WebSockets/Socket.io)", "Distributed State Convergence (CRDTs/OT)", "Redis Pub/Sub Scaling", "React Rich-Text Editing", "Concurrency Testing"],
        "project_workflow": [
            {"id": "node_1", "label": "START", "type": "start", "description": "Initiate collaborative editor development", "next_node": "node_2"},
            {"id": "node_2", "label": "PHASE 1: WEBSOCKET TRANSPORT & ROOMS", "type": "process", "description": "Establish bi-directional event socket connections and room partitioning", "next_node": "node_3"},
            {"id": "node_3", "label": "PHASE 2: CONFLICT RESOLUTION (CRDT / OT)", "type": "process", "description": "Implement operational transformation adjusting character offsets in real time", "next_node": "node_4"},
            {"id": "node_4", "label": "PHASE 3: REMOTE PRESENCE & REACT EDITOR", "type": "process", "description": "Render remote user cursor positions, user tags, and rich text formatting", "next_node": "node_5"},
            {"id": "node_5", "label": "DO CONCURRENT EDITS CONVERGE 100%?", "type": "decision", "description": "Verify simultaneous typing produces identical text on all client screens", "yes_next": "node_6", "no_next": "node_3", "yes_label": "YES: Text Converged", "no_label": "NO: Fix Transform Index Math"},
            {"id": "node_6", "label": "PHASE 4: REDIS PUB/SUB & SNAPSHOT HISTORY", "type": "process", "description": "Scale WebSocket nodes with Redis and save document revision snapshots", "next_node": "node_7"},
            {"id": "node_7", "label": "END", "type": "end", "description": "Real-time collaborative document platform operational"}
        ]
    },
    {
        "project_id": "FS-03",
        "domain": "Full Stack Web Development",
        "project_title": "Microservices-Based E-Commerce Platform with Real-time Order Queue",
        "difficulty_level": "Advanced",
        "description": "Construct a decoupled, distributed microservices e-commerce application comprising Auth, Catalog, Cart, Order, and Notification services communicating asynchronously via RabbitMQ / Redis message queues with an API gateway.",
        "learning_objectives": [
            "Architect decoupled microservices with dedicated databases per service",
            "Implement API Gateway routing with JWT authentication offloading",
            "Coordinate distributed transactions using the Saga pattern or event-driven queues",
            "Implement message durability, acknowledgment, and dead-letter queues (DLQ)",
            "Build responsive checkout interface with real-time order status tracking"
        ],
        "required_technologies": ["Node.js / Express", "React.js", "RabbitMQ / Redis Streams", "PostgreSQL", "MongoDB", "Docker Compose"],
        "prerequisites": ["Microservices architecture concepts", "Asynchronous messaging understanding", "Docker multi-container workflows"],
        "implementation_phases": [
            {"phase_number": 1, "title": "API Gateway & Service Decomposition", "objective": "Establish unified entry point and decoupled service boundaries.", "tasks": ["Configure API Gateway proxying routes to Auth, Catalog, and Order services", "Implement JWT token validation at the gateway boundary", "Deploy discrete PostgreSQL and MongoDB databases for each service"], "technologies_used": ["Express Gateway / NGINX", "Docker"], "expected_output": "Unified gateway routing requests to isolated backend microservices."},
            {"phase_number": 2, "title": "Asynchronous Message Queue & Order Processing", "objective": "Process orders asynchronously using message broker.", "tasks": ["Deploy RabbitMQ / Redis Streams broker", "Publish `order.created` event upon checkout submission", "Consume event in Inventory service to reserve stock asynchronously"], "technologies_used": ["RabbitMQ", "amqplib"], "expected_output": "Decoupled asynchronous order processing with message persistence."},
            {"phase_number": 3, "title": "Dead-Letter Queues & Failure Recovery", "objective": "Handle service failures gracefully without dropping orders.", "tasks": ["Configure Dead-Letter Exchanges (DLX) for unprocessable messages", "Implement retry mechanism with exponential backoff", "Implement compensating transactions if payment verification fails"], "technologies_used": ["RabbitMQ DLQ", "Node.js"], "expected_output": "Resilient message processing with zero lost order transactions."},
            {"phase_number": 4, "title": "React Checkout & Real-Time Status Tracker", "objective": "Build responsive frontend reflecting order progression.", "tasks": ["Build multi-step checkout with cart persistence in localStorage", "Implement Server-Sent Events (SSE) streaming order status updates", "Deploy complete microservices stack via Docker Compose"], "technologies_used": ["React", "SSE", "Docker Compose"], "expected_output": "Full-stack e-commerce platform with live order progress animation."}
        ],
        "expected_deliverables": [
            "Decoupled Microservices Repository (`services/auth`, `services/catalog`, `services/order`)",
            "Message Broker configuration with Dead-Letter Queue handling (`rabbitmq.conf`)",
            "API Gateway routing configuration and Postman integration collection",
            "Docker Compose multi-service deployment definition"
        ],
        "testing_validation_plan": [
            "Stop Inventory Service during order submission; verify message persists in queue and processes upon restart",
            "Submit corrupted payment payload; verify message routes cleanly to Dead-Letter Queue",
            "Execute end-to-end checkout flow from browser and verify stock decrement"
        ],
        "skills_demonstrated": ["Microservices Architecture", "Asynchronous Message Queues (RabbitMQ)", "Event-Driven Distributed Systems", "API Gateway Design", "Resilient Failure Recovery (DLQ)"],
        "project_workflow": [
            {"id": "node_1", "label": "START", "type": "start", "description": "Customer places order on checkout interface", "next_node": "node_2"},
            {"id": "node_2", "label": "PHASE 1: API GATEWAY AUTH & ROUTING", "type": "process", "description": "Validate user JWT at gateway and route to Order Microservice", "next_node": "node_3"},
            {"id": "node_3", "label": "PHASE 2: ASYNCHRONOUS ORDER EVENT PUBLICATION", "type": "process", "description": "Publish order.created event to RabbitMQ message broker exchange", "next_node": "node_4"},
            {"id": "node_4", "label": "PHASE 3: INVENTORY RESERVATION CONSUMER", "type": "process", "description": "Inventory service consumes event and attempts stock allocation", "next_node": "node_5"},
            {"id": "node_5", "label": "IS STOCK RESERVATION SUCCESSFUL?", "type": "decision", "description": "Verify item availability in Inventory database", "yes_next": "node_6", "no_next": "node_7", "yes_label": "YES: Stock Reserved", "no_label": "NO: Out of Stock"},
            {"id": "node_6", "label": "PUBLISH PAYMENT INITIATION EVENT", "type": "process", "description": "Trigger Payment Service and notify client via Server-Sent Events", "next_node": "node_8"},
            {"id": "node_7", "label": "ROUTE TO DEAD-LETTER QUEUE & NOTIFY", "type": "process", "description": "Emit order.failed event, release holds, and push cancellation alert", "next_node": "node_8"},
            {"id": "node_8", "label": "END", "type": "end", "description": "Order processing workflow completed"}
        ]
    },
    {
        "project_id": "FS-04",
        "domain": "Full Stack Web Development",
        "project_title": "Secure Multi-Tenant SaaS Portal with Automated Subscription Billing",
        "difficulty_level": "Advanced",
        "description": "Develop a multi-tenant Software-as-a-Service (SaaS) web platform with schema-based tenant data isolation in PostgreSQL, Stripe automated recurring subscription billing and webhook verification, and tenant-customized domain routing.",
        "learning_objectives": [
            "Implement multi-tenant data isolation patterns (schema-per-tenant or row-level security)",
            "Integrate Stripe Billing API with automated checkout and subscription lifecycle webhooks",
            "Verify cryptographic webhook signatures to prevent forged payment events",
            "Build tenant onboarding workflow with custom subdomains and branding settings",
            "Design usage-based tier quotas and automated feature gating"
        ],
        "required_technologies": ["Next.js / React", "Node.js", "PostgreSQL (Row-Level Security)", "Stripe API", "Tailwind CSS", "Docker"],
        "prerequisites": ["PostgreSQL advanced querying", "React state management", "Experience handling external webhooks"],
        "implementation_phases": [
            {"phase_number": 1, "title": "Multi-Tenant Architecture & Data Isolation", "objective": "Ensure complete data isolation between customer organizations.", "tasks": ["Implement PostgreSQL Row-Level Security (RLS) policies scoped to tenant_id", "Inject tenant context middleware extracting subdomain from incoming host", "Verify cross-tenant data leakage is structurally impossible"], "technologies_used": ["PostgreSQL RLS", "Express middleware"], "expected_output": "Database structurally forbidding access to foreign tenant rows."},
            {"phase_number": 2, "title": "Stripe Subscription & Webhook Pipeline", "objective": "Implement recurring billing and verified payment sync.", "tasks": ["Integrate Stripe Checkout Sessions for monthly and annual tiers", "Configure webhook handler verifying Stripe cryptographic signature", "Automate subscription state transitions (active, past_due, canceled)"], "technologies_used": ["Stripe API", "Node.js crypto"], "expected_output": "Automated subscription lifecycle synchronized with database."},
            {"phase_number": 3, "title": "Feature Gating & Usage Tier Enforcement", "objective": "Restrict premium features based on active subscription tier.", "tasks": ["Implement feature-flagging middleware checking tenant tier allowances", "Build usage tracking counter for API calls and storage quotas", "Render upgrade prompts when tenant approaches tier limitations"], "technologies_used": ["React", "Node.js"], "expected_output": "Strict automated feature gating tied to billing status."},
            {"phase_number": 4, "title": "Tenant Management & Settings Portal", "objective": "Build self-service organization portal with team invites.", "tasks": ["Build organization profile editor with logo upload and color branding", "Implement team member invitation system with email tokens", "Deploy production containerized multi-tenant portal"], "technologies_used": ["Next.js", "Tailwind CSS", "Docker"], "expected_output": "Self-service multi-tenant SaaS application."}
        ],
        "expected_deliverables": [
            "Multi-Tenant SaaS Monorepo (`apps/web`, `apps/api`)",
            "PostgreSQL Row-Level Security configuration scripts (`rls_setup.sql`)",
            "Stripe Webhook Verification test suite",
            "Multi-Tenant Security and Compliance Architecture Documentation"
        ],
        "testing_validation_plan": [
            "Execute SQL query with Tenant A context attempting to select Tenant B records; verify 0 rows returned",
            "Send mock Stripe webhook with forged signature; verify HTTP 400 rejection",
            "Exceed tier user limit; verify system blocks additional team invites until upgrade"
        ],
        "skills_demonstrated": ["Multi-Tenant Architecture", "Database Security (PostgreSQL RLS)", "Payment Processing (Stripe Billing)", "Webhook Cryptographic Verification", "Feature Gating"],
        "project_workflow": [
            {"id": "node_1", "label": "START", "type": "start", "description": "Tenant organization registers on platform", "next_node": "node_2"},
            {"id": "node_2", "label": "PHASE 1: TENANT ONBOARDING & RLS ISOLATION", "type": "process", "description": "Provision tenant record and initialize PostgreSQL Row-Level Security", "next_node": "node_3"},
            {"id": "node_3", "label": "PHASE 2: STRIPE SUBSCRIPTION CHECKOUT", "type": "process", "description": "Redirect tenant to Stripe Checkout Session for subscription selection", "next_node": "node_4"},
            {"id": "node_4", "label": "PHASE 3: VERIFY STRIPE WEBHOOK SIGNATURE", "type": "process", "description": "Verify cryptographic HMAC signature on checkout.session.completed event", "next_node": "node_5"},
            {"id": "node_5", "label": "IS PAYMENT & WEBHOOK VERIFIED?", "type": "decision", "description": "Confirm cryptographic signature validity and payment status", "yes_next": "node_6", "no_next": "node_7", "yes_label": "YES: Payment Verified", "no_label": "NO: Reject & Halt Access"},
            {"id": "node_6", "label": "ACTIVATE TIER & UNLOCK GATED FEATURES", "type": "process", "description": "Provision subscription tier allowances, team seats, and quota limits", "next_node": "node_8"},
            {"id": "node_7", "label": "RECORD BILLING FAILURE & PROMPT RETRY", "type": "process", "description": "Notify customer of failed charge and retain restricted trial status", "next_node": "node_8"},
            {"id": "node_8", "label": "END", "type": "end", "description": "Tenant onboarding and billing sync completed"}
        ]
    },
    {
        "project_id": "FS-05",
        "domain": "Full Stack Web Development",
        "project_title": "High-Performance REST/GraphQL API Gateway with Caching & Rate Limiting",
        "difficulty_level": "Intermediate / Advanced",
        "description": "Construct a high-throughput hybrid REST and GraphQL API Gateway featuring distributed Redis caching, token-bucket rate limiting to prevent denial-of-service, request validation with Zod / Joi, and unified error handling.",
        "learning_objectives": [
            "Build reverse-proxy gateway routing requests across downstream microservices",
            "Implement sliding-window / token-bucket rate limiting using Redis scripts",
            "Design caching layer with Cache-Control headers, ETags, and TTL invalidation",
            "Construct unified GraphQL schema stitching downstream REST microservices",
            "Implement structured JSON request logging and latency analytics"
        ],
        "required_technologies": ["Node.js", "Express / Fastify", "GraphQL / Apollo Server", "Redis", "Docker", "Autocannon (Benchmarking)"],
        "prerequisites": ["REST and GraphQL API fundamentals", "Redis data structures", "Node.js asynchronous event loop"],
        "implementation_phases": [
            {"phase_number": 1, "title": "Gateway Core & Reverse Proxy Routing", "objective": "Construct reverse-proxy routing requests to downstream services.", "tasks": ["Deploy high-performance Fastify / Express gateway instance", "Configure reverse proxy routes forwarding traffic with header preservation", "Implement correlation ID injection for cross-service tracing"], "technologies_used": ["Fastify / Express", "http-proxy-middleware"], "expected_output": "Unified gateway forwarding requests with < 2ms internal overhead."},
            {"phase_number": 2, "title": "Redis Sliding-Window Rate Limiting", "objective": "Prevent abuse with IP and user token rate limiting.", "tasks": ["Write Lua script in Redis implementing atomic sliding-window rate limiting", "Configure rate tiers (e.g., 60 req/min for anonymous, 1000 for authenticated)", "Return HTTP 429 Too Many Requests with Retry-After headers upon breach"], "technologies_used": ["Redis", "Lua"], "expected_output": "Bulletproof rate limiter preventing API abuse and DoS floods."},
            {"phase_number": 3, "title": "Distributed Caching & ETag Validation", "objective": "Reduce downstream load with in-memory response caching.", "tasks": ["Cache idempotent GET query responses in Redis with configurable TTLs", "Generate cryptographic ETag hashes for conditional HTTP 304 responses", "Implement cache invalidation hooks triggered on mutations"], "technologies_used": ["Redis", "crypto"], "expected_output": "80% reduction in downstream database queries for read-heavy routes."},
            {"phase_number": 4, "title": "GraphQL Schema Stitching & Benchmarking", "objective": "Expose flexible unified GraphQL endpoint and benchmark performance.", "tasks": ["Build Apollo Server layer aggregating microservice data into unified graph", "Implement query complexity limits preventing deep nesting DoS attacks", "Execute Autocannon benchmark demonstrating 5,000+ requests/sec"], "technologies_used": ["Apollo Server", "GraphQL", "Autocannon"], "expected_output": "Production API Gateway handling high concurrency with low latency."}
        ],
        "expected_deliverables": [
            "API Gateway Monorepo (`gateway/` with REST and GraphQL configurations)",
            "Redis Lua Rate Limiting and Caching Engine scripts (`scripts/rate_limit.lua`)",
            "Autocannon Performance Benchmark and Latency Distribution Report",
            "Production Docker deployment configuration with health monitoring"
        ],
        "testing_validation_plan": [
            "Bombard endpoint with 120 requests in 30 seconds; verify requests 61-120 return HTTP 429",
            "Execute read query twice; verify second response returns `X-Cache: HIT` in < 3ms",
            "Submit maliciously nested 20-level GraphQL query; verify gateway rejects with complexity error"
        ],
        "skills_demonstrated": ["API Gateway Engineering", "Distributed Caching (Redis)", "Rate Limiting Algorithms (Token Bucket)", "GraphQL Schema Stitching", "High-Concurrency Benchmarking"],
        "project_workflow": [
            {"id": "node_1", "label": "START", "type": "start", "description": "Client sends HTTP request to API Gateway", "next_node": "node_2"},
            {"id": "node_2", "label": "PHASE 1: RATE LIMIT VERIFICATION", "type": "process", "description": "Execute Redis sliding-window check on client IP and token quota", "next_node": "node_3"},
            {"id": "node_3", "label": "IS REQUEST WITHIN ALLOWED QUOTA?", "type": "decision", "description": "Verify client has not exceeded allowed rate limit threshold", "yes_next": "node_4", "no_next": "node_5", "yes_label": "YES: Quota Available", "no_label": "NO: Rate Limit Breached"},
            {"id": "node_4", "label": "PHASE 2: REDIS CACHE LOOKUP", "type": "process", "description": "Check if valid cached response exists for request URI and ETag", "next_node": "node_6"},
            {"id": "node_5", "label": "RETURN HTTP 429 TOO MANY REQUESTS", "type": "process", "description": "Return rate limit exceeded error with Retry-After header", "next_node": "node_8"},
            {"id": "node_6", "label": "IS RESPONSE CACHED (CACHE HIT)?", "type": "decision", "description": "Evaluate cache presence and TTL validity in Redis store", "yes_next": "node_7", "no_next": "node_9", "yes_label": "YES: Cache HIT", "no_label": "NO: Cache MISS"},
            {"id": "node_7", "label": "RETURN CACHED RESPONSE (X-CACHE: HIT)", "type": "process", "description": "Serve in-memory cached payload in < 3ms without downstream call", "next_node": "node_8"},
            {"id": "node_9", "label": "FORWARD TO DOWNSTREAM SERVICE & STORE CACHE", "type": "process", "description": "Proxy request to microservice, write response to Redis, and return", "next_node": "node_8"},
            {"id": "node_8", "label": "END", "type": "end", "description": "Gateway request lifecycle completed"}
        ]
    }
]


# Combine all catalog projects
ALL_CATALOG_PROJECTS: List[Dict[str, Any]] = (
    CYBERSECURITY_PROJECTS + DATA_SCIENCE_PROJECTS + CLOUD_DEVOPS_PROJECTS + FULL_STACK_PROJECTS
)

SUPPORTED_DOMAINS: List[str] = [
    "Cybersecurity",
    "Data Science & Machine Learning",
    "Cloud & DevOps",
    "Full Stack Web Development"
]


class ProjectCatalogRepository:
    """Repository layer for interacting with the Project Catalog in memory and Neon PostgreSQL."""

    def __init__(self, manager=db_manager):
        self.db = manager

    def ensure_table_and_seed(self) -> None:
        """Creates the project_catalog table if missing and seeds all initial projects idempotently."""
        create_sql = """
            CREATE TABLE IF NOT EXISTS public.project_catalog (
                project_id VARCHAR(50) PRIMARY KEY,
                domain VARCHAR(100) NOT NULL,
                project_title VARCHAR(255) NOT NULL,
                difficulty_level VARCHAR(50) NOT NULL,
                description TEXT NOT NULL,
                learning_objectives JSONB NOT NULL,
                required_technologies JSONB NOT NULL,
                prerequisites JSONB NOT NULL,
                implementation_phases JSONB NOT NULL,
                expected_deliverables JSONB NOT NULL,
                testing_validation_plan JSONB NOT NULL,
                project_workflow JSONB NOT NULL,
                skills_demonstrated JSONB NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """
        upsert_sql = """
            INSERT INTO public.project_catalog (
                project_id, domain, project_title, difficulty_level, description,
                learning_objectives, required_technologies, prerequisites,
                implementation_phases, expected_deliverables, testing_validation_plan,
                project_workflow, skills_demonstrated
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (project_id) DO UPDATE SET
                domain = EXCLUDED.domain,
                project_title = EXCLUDED.project_title,
                difficulty_level = EXCLUDED.difficulty_level,
                description = EXCLUDED.description,
                learning_objectives = EXCLUDED.learning_objectives,
                required_technologies = EXCLUDED.required_technologies,
                prerequisites = EXCLUDED.prerequisites,
                implementation_phases = EXCLUDED.implementation_phases,
                expected_deliverables = EXCLUDED.expected_deliverables,
                testing_validation_plan = EXCLUDED.testing_validation_plan,
                project_workflow = EXCLUDED.project_workflow,
                skills_demonstrated = EXCLUDED.skills_demonstrated;
        """
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_sql)
                    for p in ALL_CATALOG_PROJECTS:
                        cur.execute(
                            upsert_sql,
                            (
                                p["project_id"],
                                p["domain"],
                                p["project_title"],
                                p["difficulty_level"],
                                p["description"],
                                json.dumps(p["learning_objectives"]),
                                json.dumps(p["required_technologies"]),
                                json.dumps(p["prerequisites"]),
                                json.dumps(p["implementation_phases"]),
                                json.dumps(p["expected_deliverables"]),
                                json.dumps(p["testing_validation_plan"]),
                                json.dumps(p["project_workflow"]),
                                json.dumps(p["skills_demonstrated"]),
                            ),
                        )
                    conn.commit()
            logger.info("Successfully seeded %d projects across %d domains into Neon PostgreSQL.", len(ALL_CATALOG_PROJECTS), len(SUPPORTED_DOMAINS))
        except Exception as exc:
            logger.warning("Database seeding encountered error (falling back to in-memory catalog): %s", exc)

    def list_domains(self) -> List[Dict[str, Any]]:
        """Returns all supported domains and their project counts."""
        domains = []
        for d in SUPPORTED_DOMAINS:
            count = sum(1 for p in ALL_CATALOG_PROJECTS if p["domain"] == d)
            domains.append({"domain": d, "project_count": count})
        return domains

    def list_projects_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Returns the exactly 5 projects for the specified domain."""
        norm_domain = domain.strip().lower()
        matched = [
            p for p in ALL_CATALOG_PROJECTS
            if p["domain"].lower() == norm_domain or norm_domain in p["domain"].lower()
        ]
        return matched[:5]

    def get_project_by_id(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Returns full project specification and workflow by ID."""
        for p in ALL_CATALOG_PROJECTS:
            if p["project_id"].upper() == project_id.strip().upper():
                return p
        return None


project_catalog_repository = ProjectCatalogRepository()

