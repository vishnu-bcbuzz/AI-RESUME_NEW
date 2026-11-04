"""Standardized Technical Skills Taxonomy, Normalization, and Extraction Pipeline.

Provides rigorous classification, non-skill filtering, canonical name normalization,
and structured categorization for ATS-compliant resumes across all career tracks.
Strictly excludes personal info, company names, job titles, education, project descriptions,
dates, certifications, and model evaluation metrics from technical skills.
"""

import re
from typing import Dict, List, Set, Optional, Tuple, Any

# Standard ATS Category Names
CATEGORY_CYBER_TOOLS = "Cybersecurity Tools"
CATEGORY_SEC_CONCEPTS = "Security Concepts"
CATEGORY_PROG_LANGUAGES = "Programming Languages"
CATEGORY_OPERATING_SYSTEMS = "Operating Systems"
CATEGORY_FRAMEWORKS = "Frameworks & Libraries"
CATEGORY_DATABASES = "Databases"
CATEGORY_CLOUD_DEVOPS = "Cloud & DevOps"
CATEGORY_DATA_SCIENCE = "Data Science & Machine Learning"
CATEGORY_NETWORKING = "Networking Technologies"

STANDARD_CATEGORIES: List[str] = [
    CATEGORY_CYBER_TOOLS,
    CATEGORY_SEC_CONCEPTS,
    CATEGORY_PROG_LANGUAGES,
    CATEGORY_OPERATING_SYSTEMS,
    CATEGORY_FRAMEWORKS,
    CATEGORY_DATABASES,
    CATEGORY_CLOUD_DEVOPS,
    CATEGORY_DATA_SCIENCE,
    CATEGORY_NETWORKING,
]

# Canonical normalization map (aliases / case variants -> canonical display name)
NORMALIZATION_MAP: Dict[str, str] = {
    # Databases
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "postgre sql": "PostgreSQL",
    "psql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "mysql": "MySQL",
    "mssql": "Microsoft SQL Server",
    "ms sql": "Microsoft SQL Server",
    "sql server": "Microsoft SQL Server",
    "sqlite": "SQLite",
    "redis": "Redis",
    "elasticsearch": "Elasticsearch",
    "elastic search": "Elasticsearch",
    "cassandra": "Cassandra",
    "dynamodb": "DynamoDB",
    "mariadb": "MariaDB",
    "neo4j": "Neo4j",
    "couchdb": "CouchDB",
    "firebase": "Firebase",
    "chromadb": "ChromaDB",
    "chroma": "ChromaDB",
    "pgvector": "PGVector",

    # Programming Languages
    "python": "Python",
    "py": "Python",
    "python3": "Python",
    "java": "Java",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "c++": "C++",
    "cpp": "C++",
    "c plus plus": "C++",
    "c#": "C#",
    "csharp": "C#",
    "c sharp": "C#",
    "golang": "Go",
    "go": "Go",
    "rust": "Rust",
    "php": "PHP",
    "ruby": "Ruby",
    "bash": "Bash",
    "shell": "Shell Scripting",
    "powershell": "PowerShell",
    "pwsh": "PowerShell",
    "sql": "SQL",
    "r": "R",
    "scala": "Scala",
    "solidity": "Solidity",
    "perl": "Perl",
    "kotlin": "Kotlin",
    "swift": "Swift",
    "html": "HTML5",
    "html5": "HTML5",
    "css": "CSS3",
    "css3": "CSS3",
    "assembly": "Assembly (x86/x64)",

    # Frameworks & Libraries
    "react": "React.js",
    "reactjs": "React.js",
    "react.js": "React.js",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "express.js": "Express.js",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "spring": "Spring Boot",
    "spring boot": "Spring Boot",
    "angular": "Angular",
    "angularjs": "Angular",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "next": "Next.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "nest": "NestJS",
    "nestjs": "NestJS",
    "nest.js": "NestJS",
    "langchain": "LangChain",
    "bootstrap": "Bootstrap",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "scapy": "Scapy",
    "paramiko": "Paramiko",
    "requests": "Requests",

    # Cloud & DevOps
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Microsoft Azure",
    "ms azure": "Microsoft Azure",
    "microsoft azure": "Microsoft Azure",
    "gcp": "Google Cloud Platform (GCP)",
    "google cloud": "Google Cloud Platform (GCP)",
    "google cloud platform": "Google Cloud Platform (GCP)",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "bitbucket": "Bitbucket",
    "jenkins": "Jenkins",
    "ci/cd": "CI/CD",
    "ci cd": "CI/CD",
    "vagrant": "Vagrant",
    "helm": "Helm",
    "prometheus": "Prometheus",
    "grafana": "Grafana",
    "virtualbox": "VirtualBox",
    "vmware": "VMware",

    # Operating Systems
    "linux": "Linux",
    "ubuntu": "Ubuntu",
    "debian": "Debian",
    "kali linux": "Kali Linux",
    "kali": "Kali Linux",
    "red hat": "Red Hat Enterprise Linux (RHEL)",
    "rhel": "Red Hat Enterprise Linux (RHEL)",
    "centos": "CentOS",
    "windows server": "Windows Server",
    "windows": "Windows",
    "macos": "macOS",
    "unix": "Unix",

    # Cybersecurity Tools
    "burp": "Burp Suite",
    "burp suite": "Burp Suite",
    "burpsuite": "Burp Suite",
    "nmap": "Nmap",
    "wireshark": "Wireshark",
    "metasploit": "Metasploit",
    "openvas": "OpenVAS",
    "nessus": "Nessus",
    "owasp zap": "OWASP ZAP",
    "zap": "OWASP ZAP",
    "snort": "Snort",
    "suricata": "Suricata",
    "splunk": "Splunk",
    "qualys": "Qualys",
    "crowdstrike": "CrowdStrike Falcon",
    "qradar": "IBM QRadar",
    "sentinel": "Microsoft Sentinel",
    "aircrack": "Aircrack-ng",
    "aircrack-ng": "Aircrack-ng",
    "john the ripper": "John the Ripper",
    "hashcat": "Hashcat",
    "sqlmap": "SQLmap",
    "nikto": "Nikto",
    "hydra": "THC-Hydra",
    "zeek": "Zeek (Bro)",
    "bro": "Zeek (Bro)",
    "sysmon": "Sysmon",
    "autopsy": "Autopsy",
    "volatility": "Volatility",
    "mimikatz": "Mimikatz",
    "ghidra": "Ghidra",
    "ida pro": "IDA Pro",
    "radare2": "Radare2",
    "yara": "YARA",
    "tcpdump": "Tcpdump",
    "osquery": "OSQuery",
    "wazuh": "Wazuh",
    "security onion": "Security Onion",

    # Security Concepts
    "network security": "Network Security",
    "vulnerability assessment": "Vulnerability Assessment",
    "penetration testing": "Penetration Testing",
    "pentesting": "Penetration Testing",
    "pen testing": "Penetration Testing",
    "vapt": "Vulnerability Assessment & Penetration Testing (VAPT)",
    "owasp top 10": "OWASP Top 10",
    "owasp": "OWASP Top 10",
    "threat modeling": "Threat Modeling",
    "incident response": "Incident Response",
    "incident handling": "Incident Handling",
    "cryptography": "Cryptography & Encryption",
    "encryption": "Cryptography & Encryption",
    "public key infrastructure": "Public Key Infrastructure (PKI)",
    "pki": "Public Key Infrastructure (PKI)",
    "identity and access management": "Identity & Access Management (IAM)",
    "identity & access management": "Identity & Access Management (IAM)",
    "iam": "Identity & Access Management (IAM)",
    "zero trust": "Zero Trust Architecture",
    "cloud security": "Cloud Security",
    "malware analysis": "Malware Analysis",
    "reverse engineering": "Reverse Engineering",
    "soc": "Security Operations Center (SOC)",
    "siem": "Security Information & Event Management (SIEM)",
    "digital forensics": "Digital Forensics (DFIR)",
    "dfir": "Digital Forensics (DFIR)",
    "threat intelligence": "Threat Intelligence",
    "host hardening": "Host Hardening & Defense",
    "application security": "Application Security (AppSec)",
    "appsec": "Application Security (AppSec)",
    "endpoint security": "Endpoint Security",
    "stateful firewalls": "Stateful Firewalls & Packet Filtering",
    "access control": "Access Control (RBAC/ABAC)",
    "packet analysis": "Packet Analysis & Deep Packet Inspection",

    # Networking Technologies
    "tcp/ip": "TCP/IP",
    "tcp ip": "TCP/IP",
    "tcp/ip protocol suite": "TCP/IP",
    "dns": "DNS",
    "dhcp": "DHCP",
    "vpn": "VPN",
    "vlan": "VLAN Segmentation",
    "firewalls": "Firewall Configuration",
    "firewall": "Firewall Configuration",
    "ufw": "UFW Firewall",
    "iptables": "iptables",
    "routing": "Routing & Switching",
    "tls": "TLS/SSL",
    "ssl": "TLS/SSL",
    "tls/ssl": "TLS/SSL",
    "ssh": "SSH",
    "http/https": "HTTP/HTTPS Protocols",

    # Data Science & Machine Learning
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "nlp": "Natural Language Processing (NLP)",
    "natural language processing": "Natural Language Processing (NLP)",
    "computer vision": "Computer Vision",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "scikit-learn": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "matplotlib": "Matplotlib",
    "seaborn": "Seaborn",
    "keras": "Keras",
    "tableau": "Tableau",
    "power bi": "Power BI",
    "powerbi": "Power BI",
}

# Categorization mapping for normalized display names and known keywords
CATEGORY_MAPPING: Dict[str, str] = {
    # Cybersecurity Tools
    "Burp Suite": CATEGORY_CYBER_TOOLS,
    "Nmap": CATEGORY_CYBER_TOOLS,
    "Wireshark": CATEGORY_CYBER_TOOLS,
    "Metasploit": CATEGORY_CYBER_TOOLS,
    "OpenVAS": CATEGORY_CYBER_TOOLS,
    "Nessus": CATEGORY_CYBER_TOOLS,
    "OWASP ZAP": CATEGORY_CYBER_TOOLS,
    "Snort": CATEGORY_CYBER_TOOLS,
    "Suricata": CATEGORY_CYBER_TOOLS,
    "Splunk": CATEGORY_CYBER_TOOLS,
    "Qualys": CATEGORY_CYBER_TOOLS,
    "CrowdStrike Falcon": CATEGORY_CYBER_TOOLS,
    "IBM QRadar": CATEGORY_CYBER_TOOLS,
    "Microsoft Sentinel": CATEGORY_CYBER_TOOLS,
    "Aircrack-ng": CATEGORY_CYBER_TOOLS,
    "John the Ripper": CATEGORY_CYBER_TOOLS,
    "Hashcat": CATEGORY_CYBER_TOOLS,
    "SQLmap": CATEGORY_CYBER_TOOLS,
    "Nikto": CATEGORY_CYBER_TOOLS,
    "THC-Hydra": CATEGORY_CYBER_TOOLS,
    "Zeek (Bro)": CATEGORY_CYBER_TOOLS,
    "Sysmon": CATEGORY_CYBER_TOOLS,
    "Autopsy": CATEGORY_CYBER_TOOLS,
    "Volatility": CATEGORY_CYBER_TOOLS,
    "Mimikatz": CATEGORY_CYBER_TOOLS,
    "Ghidra": CATEGORY_CYBER_TOOLS,
    "IDA Pro": CATEGORY_CYBER_TOOLS,
    "Radare2": CATEGORY_CYBER_TOOLS,
    "YARA": CATEGORY_CYBER_TOOLS,
    "Tcpdump": CATEGORY_CYBER_TOOLS,
    "OSQuery": CATEGORY_CYBER_TOOLS,
    "Wazuh": CATEGORY_CYBER_TOOLS,
    "Security Onion": CATEGORY_CYBER_TOOLS,

    # Security Concepts
    "Network Security": CATEGORY_SEC_CONCEPTS,
    "Vulnerability Assessment": CATEGORY_SEC_CONCEPTS,
    "Penetration Testing": CATEGORY_SEC_CONCEPTS,
    "Vulnerability Assessment & Penetration Testing (VAPT)": CATEGORY_SEC_CONCEPTS,
    "OWASP Top 10": CATEGORY_SEC_CONCEPTS,
    "Threat Modeling": CATEGORY_SEC_CONCEPTS,
    "Incident Response": CATEGORY_SEC_CONCEPTS,
    "Incident Handling": CATEGORY_SEC_CONCEPTS,
    "Cryptography & Encryption": CATEGORY_SEC_CONCEPTS,
    "Public Key Infrastructure (PKI)": CATEGORY_SEC_CONCEPTS,
    "Identity & Access Management (IAM)": CATEGORY_SEC_CONCEPTS,
    "Zero Trust Architecture": CATEGORY_SEC_CONCEPTS,
    "Cloud Security": CATEGORY_SEC_CONCEPTS,
    "Malware Analysis": CATEGORY_SEC_CONCEPTS,
    "Reverse Engineering": CATEGORY_SEC_CONCEPTS,
    "Security Operations Center (SOC)": CATEGORY_SEC_CONCEPTS,
    "Security Information & Event Management (SIEM)": CATEGORY_SEC_CONCEPTS,
    "Digital Forensics (DFIR)": CATEGORY_SEC_CONCEPTS,
    "Threat Intelligence": CATEGORY_SEC_CONCEPTS,
    "Host Hardening & Defense": CATEGORY_SEC_CONCEPTS,
    "Application Security (AppSec)": CATEGORY_SEC_CONCEPTS,
    "Endpoint Security": CATEGORY_SEC_CONCEPTS,
    "Stateful Firewalls & Packet Filtering": CATEGORY_SEC_CONCEPTS,
    "Access Control (RBAC/ABAC)": CATEGORY_SEC_CONCEPTS,
    "Packet Analysis & Deep Packet Inspection": CATEGORY_SEC_CONCEPTS,

    # Programming Languages
    "Python": CATEGORY_PROG_LANGUAGES,
    "Java": CATEGORY_PROG_LANGUAGES,
    "JavaScript": CATEGORY_PROG_LANGUAGES,
    "TypeScript": CATEGORY_PROG_LANGUAGES,
    "C": CATEGORY_PROG_LANGUAGES,
    "C++": CATEGORY_PROG_LANGUAGES,
    "C#": CATEGORY_PROG_LANGUAGES,
    "Go": CATEGORY_PROG_LANGUAGES,
    "Rust": CATEGORY_PROG_LANGUAGES,
    "PHP": CATEGORY_PROG_LANGUAGES,
    "Ruby": CATEGORY_PROG_LANGUAGES,
    "SQL": CATEGORY_PROG_LANGUAGES,
    "Bash": CATEGORY_PROG_LANGUAGES,
    "Shell Scripting": CATEGORY_PROG_LANGUAGES,
    "PowerShell": CATEGORY_PROG_LANGUAGES,
    "R": CATEGORY_PROG_LANGUAGES,
    "Scala": CATEGORY_PROG_LANGUAGES,
    "Solidity": CATEGORY_PROG_LANGUAGES,
    "Perl": CATEGORY_PROG_LANGUAGES,
    "Kotlin": CATEGORY_PROG_LANGUAGES,
    "Swift": CATEGORY_PROG_LANGUAGES,
    "HTML5": CATEGORY_PROG_LANGUAGES,
    "CSS3": CATEGORY_PROG_LANGUAGES,
    "Assembly (x86/x64)": CATEGORY_PROG_LANGUAGES,

    # Operating Systems
    "Linux": CATEGORY_OPERATING_SYSTEMS,
    "Ubuntu": CATEGORY_OPERATING_SYSTEMS,
    "Debian": CATEGORY_OPERATING_SYSTEMS,
    "Kali Linux": CATEGORY_OPERATING_SYSTEMS,
    "Red Hat Enterprise Linux (RHEL)": CATEGORY_OPERATING_SYSTEMS,
    "CentOS": CATEGORY_OPERATING_SYSTEMS,
    "Windows Server": CATEGORY_OPERATING_SYSTEMS,
    "Windows": CATEGORY_OPERATING_SYSTEMS,
    "macOS": CATEGORY_OPERATING_SYSTEMS,
    "Unix": CATEGORY_OPERATING_SYSTEMS,

    # Frameworks & Libraries
    "FastAPI": CATEGORY_FRAMEWORKS,
    "LangChain": CATEGORY_FRAMEWORKS,
    "React.js": CATEGORY_FRAMEWORKS,
    "Node.js": CATEGORY_FRAMEWORKS,
    "Express.js": CATEGORY_FRAMEWORKS,
    "Flask": CATEGORY_FRAMEWORKS,
    "Django": CATEGORY_FRAMEWORKS,
    "Spring Boot": CATEGORY_FRAMEWORKS,
    "Angular": CATEGORY_FRAMEWORKS,
    "Vue.js": CATEGORY_FRAMEWORKS,
    "Next.js": CATEGORY_FRAMEWORKS,
    "NestJS": CATEGORY_FRAMEWORKS,
    "Bootstrap": CATEGORY_FRAMEWORKS,
    "Tailwind CSS": CATEGORY_FRAMEWORKS,
    "Scapy": CATEGORY_FRAMEWORKS,
    "Paramiko": CATEGORY_FRAMEWORKS,
    "Requests": CATEGORY_FRAMEWORKS,

    # Databases
    "PostgreSQL": CATEGORY_DATABASES,
    "MySQL": CATEGORY_DATABASES,
    "MongoDB": CATEGORY_DATABASES,
    "Redis": CATEGORY_DATABASES,
    "SQLite": CATEGORY_DATABASES,
    "Microsoft SQL Server": CATEGORY_DATABASES,
    "Oracle Database": CATEGORY_DATABASES,
    "Elasticsearch": CATEGORY_DATABASES,
    "Cassandra": CATEGORY_DATABASES,
    "DynamoDB": CATEGORY_DATABASES,
    "MariaDB": CATEGORY_DATABASES,
    "Neo4j": CATEGORY_DATABASES,
    "ChromaDB": CATEGORY_DATABASES,
    "PGVector": CATEGORY_DATABASES,

    # Cloud & DevOps
    "AWS": CATEGORY_CLOUD_DEVOPS,
    "Microsoft Azure": CATEGORY_CLOUD_DEVOPS,
    "Google Cloud Platform (GCP)": CATEGORY_CLOUD_DEVOPS,
    "Docker": CATEGORY_CLOUD_DEVOPS,
    "Kubernetes": CATEGORY_CLOUD_DEVOPS,
    "Terraform": CATEGORY_CLOUD_DEVOPS,
    "Ansible": CATEGORY_CLOUD_DEVOPS,
    "Git": CATEGORY_CLOUD_DEVOPS,
    "GitHub": CATEGORY_CLOUD_DEVOPS,
    "GitLab": CATEGORY_CLOUD_DEVOPS,
    "Bitbucket": CATEGORY_CLOUD_DEVOPS,
    "Jenkins": CATEGORY_CLOUD_DEVOPS,
    "CI/CD": CATEGORY_CLOUD_DEVOPS,
    "Vagrant": CATEGORY_CLOUD_DEVOPS,
    "Helm": CATEGORY_CLOUD_DEVOPS,
    "Prometheus": CATEGORY_CLOUD_DEVOPS,
    "Grafana": CATEGORY_CLOUD_DEVOPS,
    "VirtualBox": CATEGORY_CLOUD_DEVOPS,
    "VMware": CATEGORY_CLOUD_DEVOPS,

    # Data Science & Machine Learning
    "Machine Learning": CATEGORY_DATA_SCIENCE,
    "Deep Learning": CATEGORY_DATA_SCIENCE,
    "Natural Language Processing (NLP)": CATEGORY_DATA_SCIENCE,
    "Computer Vision": CATEGORY_DATA_SCIENCE,
    "PyTorch": CATEGORY_DATA_SCIENCE,
    "TensorFlow": CATEGORY_DATA_SCIENCE,
    "Scikit-learn": CATEGORY_DATA_SCIENCE,
    "Pandas": CATEGORY_DATA_SCIENCE,
    "NumPy": CATEGORY_DATA_SCIENCE,
    "Matplotlib": CATEGORY_DATA_SCIENCE,
    "Seaborn": CATEGORY_DATA_SCIENCE,
    "Keras": CATEGORY_DATA_SCIENCE,
    "Tableau": CATEGORY_DATA_SCIENCE,
    "Power BI": CATEGORY_DATA_SCIENCE,

    # Networking Technologies
    "TCP/IP": CATEGORY_NETWORKING,
    "TCP/IP Protocol Suite": CATEGORY_NETWORKING,
    "DNS": CATEGORY_NETWORKING,
    "DNS Security & Resolution": CATEGORY_NETWORKING,
    "DHCP": CATEGORY_NETWORKING,
    "VPN": CATEGORY_NETWORKING,
    "VPN & Tunneling (IPsec/WireGuard)": CATEGORY_NETWORKING,
    "VLAN Segmentation": CATEGORY_NETWORKING,
    "Firewalls (UFW/iptables/pfsense)": CATEGORY_NETWORKING,
    "Firewall Configuration": CATEGORY_NETWORKING,
    "Packet Analysis": CATEGORY_NETWORKING,
    "UFW Firewall": CATEGORY_NETWORKING,
    "iptables": CATEGORY_NETWORKING,
    "Routing & Switching": CATEGORY_NETWORKING,
    "TLS/SSL": CATEGORY_NETWORKING,
    "TLS/SSL Protocols": CATEGORY_NETWORKING,
    "SSH": CATEGORY_NETWORKING,
    "SSH Secure Remote Access": CATEGORY_NETWORKING,
    "HTTP/HTTPS Protocols": CATEGORY_NETWORKING,
}


# =========================================================================
# RIGOROUS PROHIBITED PATTERNS (Must NEVER appear as Technical Skills)
# =========================================================================

# 1. Contact Info & URLs
PAT_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PAT_PHONE = re.compile(r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}")
PAT_URL = re.compile(r"(?:https?://|www\.|linkedin\.com|github\.com|\.com\b|\.org\b|\.edu\b|\.io\b|\.net\b)", re.IGNORECASE)
PAT_LOCATION = re.compile(
    r"(?i)\b(?:[A-Za-z\s]+,\s*[A-Z]{2}\b|[A-Za-z\s]+,\s*(?:USA|India|UK|Canada|California|Karnataka|Texas|New York)\b|"
    r"san francisco|new york|boston|bengaluru|bangalore|london|chicago|seattle|austin|los angeles)\b"
)

# 2. Dates & Date Ranges (e.g., "June 2022 - Present", "2020", "2019 – 2023", "Aug 2021", "3 years", "Current", "Present")
PAT_DATE = re.compile(
    r"(?i)\b(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*|\d{1,2})?\s*(?:19|20)\d{2}\s*"
    r"(?:[-–—to]+\s*(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*|\d{1,2})?\s*(?:(?:19|20)\d{2}|present|current))?\b|"
    r"\b(?:19|20)\d{2}\b|\b\d+\+?\s*(?:years?|yrs?|months?|mos?)\b|\b(?:present|current|ongoing|expected)\b"
)

# 3. Employment & Company Indicators
PAT_EMPLOYMENT = re.compile(
    r"(?i)\b(?:corp|corporation|inc|llc|solutions|technologies|company|ltd|pvt|co|enterprises|"
    r"employer|client|organization|host\s+organization|employee|full[- ]time|part[- ]time|contract|freelance|trainee)\b"
)

# 4. Job Titles (Strictly avoid job titles unless part of known skills like 'Reverse Engineering')
PAT_JOB_TITLES = re.compile(
    r"(?i)\b(?:engineer|analyst|developer|administrator|specialist|intern|internship|trainee|"
    r"manager|consultant|architect|director|lead|officer|associate|fellow|student|practitioner)\b"
)

# 5. Education & Degree Indicators
PAT_EDUCATION = re.compile(
    r"(?i)\b(?:bachelor|master|b\.?s\.?|b\.?sc\.?|b\.?tech\.?|b\.?e\.?|m\.?s\.?|m\.?tech\.?|m\.?e\.?|"
    r"ph\.?d\.?|doctorate|associate|diploma|university|college|school|institute|campus|gpa|cgpa|"
    r"grade|score|dean['’]?s\s+(?:honor\s+)?list|honor\s+roll|academic|coursework|graduated|graduation|"
    r"cum\s+laude|magna\s+cum\s+laude|summa\s+cum\s+laude|high\s+school|mit|stanford|harvard|caltech|oxford|cambridge|iit|nit|bits)\b"
)

# 6. Project & Work Experience Phrases / Action Verbs
PAT_PROJECT_PHRASES = re.compile(
    r"(?i)\b(?:project|remediation\s+lab|hardening\s+lab|automated\s+scanner|testing\s+lab|simulation|"
    r"developed|engineered|configured|implemented|conducted|tested|simulating|enforcing|validated|"
    r"monitored|reducing|authoring|administering|triaged|analyzed|responsibilities|deliverables|outcomes)\b"
)

# 7. Known Certifications (Must be stored under certifications, NOT skills)
PAT_CERTIFICATIONS = re.compile(
    r"(?i)\b(?:comptia|security\+|cysa\+|network\+|pentest\+|casp\+|cissp|ceh|oscp|cism|cisa|crisc|"
    r"ccsp|gsec|gcih|gcfa|gpen|gxpn|aws\s+certified|certified\s+ethical\s+hacker|certified\s+in\s+cybersecurity|"
    r"lead\s+auditor|cloud\s+practitioner)\b"
)

# 8. Model Evaluation Metrics and Academic Statistics
PAT_METRICS = re.compile(
    r"(?i)\b(?:eda|mae|rmse|mse|r2|r²|r-squared|auc|roc|accuracy|precision|recall|f1[- ]score|loss|"
    r"p-value|confusion\s+matrix|model\s+evaluation|exploratory\s+data\s+analysis|mean\s+absolute\s+error|"
    r"root\s+mean\s+square)\b"
)

# 9. Generic Soft Skills & Filler Words
PAT_GENERIC_WORDS = re.compile(
    r"(?i)^(?:leadership|communication|teamwork|problem\s+solving|critical\s+thinking|time\s+management|"
    r"work\s+ethic|adaptability|collaboration|presentation|interpersonal|responsibilities|summary|"
    r"objective|experience|profile|key\s+skills|overview|highlights|details|various|multiple|hands-on|practical)$"
)


def is_valid_technical_skill(
    token: str,
    candidate_name: Optional[str] = None,
    contact_info: Optional[Any] = None,
) -> bool:
    """Strictly evaluates if a token is a legitimate technical skill, tool, language, or concept.

    Rejects personal details, contact info, companies, job titles, education,
    project descriptions, dates, certs, and generic filler words.
    """
    if not token or not isinstance(token, str):
        return False

    raw = token.strip()
    if len(raw) < 2 or len(raw) > 50:
        return False

    # Check for sentence punctuation (skills do not contain full stops, semicolons, or sentence syntax)
    if raw.endswith(".") or ";" in raw or "!" in raw or "?" in raw:
        return False

    # Max word count for a skill name is 4 words
    words = raw.split()
    if len(words) > 4:
        return False

    low = raw.lower()

    # 1. Reject Emails, Phones, URLs
    if PAT_EMAIL.search(raw) or PAT_PHONE.search(raw) or PAT_URL.search(raw):
        return False

    # 2. Reject Candidate Name match
    if candidate_name:
        cand_clean = candidate_name.strip().lower()
        if cand_clean and (cand_clean in low or low in cand_clean):
            return False
        # Reject candidate's individual name parts (e.g. "Jordan", "Hayes")
        name_parts = [p.lower() for p in cand_clean.split() if len(p) > 2]
        if any(p == low for p in name_parts):
            return False

    # 3. Reject Contact Details match (phone, email, location)
    if contact_info:
        loc = getattr(contact_info, "location", None) if not isinstance(contact_info, dict) else contact_info.get("location")
        if loc:
            loc_clean = loc.strip().lower()
            if loc_clean in low or low in loc_clean:
                return False
            loc_parts = [p.strip().lower() for p in re.split(r"[,/]", loc) if len(p.strip()) > 2]
            if any(p in low or low in p for p in loc_parts):
                return False
        email = getattr(contact_info, "email", None) if not isinstance(contact_info, dict) else contact_info.get("email")
        if email and email.strip().lower() in low:
            return False

    # 4. Reject Location Patterns (e.g. "San Francisco, CA", "New York, NY", "London")
    if PAT_LOCATION.search(raw):
        return False

    # 5. Reject Dates & Date Ranges (e.g., "June 2022 - Present", "2020", "3 years")
    if PAT_DATE.search(raw):
        return False

    # Check against known normalized skills (allow known skills even if they contain words like 'Security')
    if low in NORMALIZATION_MAP or raw in CATEGORY_MAPPING:
        return True

    # 5. Reject Pure Numbers or numeric strings
    if re.match(r"^[\d\s.,/\\-]+$", raw):
        return False

    # 6. Reject Certifications (belong in Certifications section)
    if PAT_CERTIFICATIONS.search(raw):
        return False

    # 7. Reject Evaluation Metrics
    if PAT_METRICS.search(raw):
        return False

    # 8. Reject Generic Soft Skills / Section Names
    if PAT_GENERIC_WORDS.match(raw):
        return False

    # 9. Reject Education Words (Universities, Degrees, GPA)
    if PAT_EDUCATION.search(raw):
        return False

    # 10. Reject Company & Employer Words
    if PAT_EMPLOYMENT.search(raw):
        return False

    # 11. Reject Job Titles unless explicit concept like "Reverse Engineering"
    if PAT_JOB_TITLES.search(raw):
        if not any(k in low for k in ("reverse engineering", "social engineering", "security engineering")):
            return False

    # 12. Reject Project phrases and action verbs
    if PAT_PROJECT_PHRASES.search(raw):
        if not any(k in low for k in ("gitlab", "jupyterlab", "burp suite", "wireshark", "testing")):
            return False

    # 13. Reject English sentence connectors like "in", "with", "for", "using", "at", "from"
    lower_words = set(low.split())
    sentence_prepositions = {"at", "with", "from", "into", "through", "across", "during", "using", "responsible"}
    if sentence_prepositions.intersection(lower_words):
        return False

    return True


def normalize_skill_name(raw_skill: str) -> str:
    """Normalizes skill aliases to canonical professional naming."""
    clean = re.sub(r"^[(\[\-:\s•*]+|[)\]\-:\s]+$", "", raw_skill).strip()
    low = clean.lower()

    if low in NORMALIZATION_MAP:
        return NORMALIZATION_MAP[low]

    # Look for partial matches in normalization map
    for alias, canonical in NORMALIZATION_MAP.items():
        if low == alias:
            return canonical

    # If already Title-cased or uppercase acronym, preserve formatting
    if clean.isupper() and len(clean) <= 6:
        return clean
    if clean and clean[0].isupper():
        return clean

    return clean.title()


def classify_skill(normalized_skill: str, original_context: Optional[str] = None) -> Optional[str]:
    """Classifies a normalized skill into one of the 9 standard ATS categories.

    Returns None if the skill cannot be reliably classified as a technical skill.
    """
    # 1. Exact match in CATEGORY_MAPPING
    if normalized_skill in CATEGORY_MAPPING:
        return CATEGORY_MAPPING[normalized_skill]

    s_low = normalized_skill.lower()

    # 2. Fallback keyword inspection against standard categories
    # Cybersecurity Tools
    sec_tools_kw = {
        "burp", "nmap", "wireshark", "metasploit", "openvas", "nessus", "zap", "snort",
        "suricata", "splunk", "qualys", "crowdstrike", "qradar", "sentinel", "aircrack",
        "hashcat", "sqlmap", "nikto", "hydra", "zeek", "sysmon", "autopsy", "volatility",
        "mimikatz", "ghidra", "yara", "radare", "wazuh", "osquery", "tcpdump"
    }
    if any(k in s_low for k in sec_tools_kw) or "tool" in (original_context or "").lower():
        return CATEGORY_CYBER_TOOLS

    # Security Concepts
    sec_concepts_kw = {
        "security", "vulnerability", "penetration", "vapt", "owasp", "threat", "incident",
        "cryptograph", "encryption", "pki", "iam", "zero trust", "malware", "reverse engineering",
        "soc", "siem", "forensic", "hardening", "firewall", "defense", "exploit", "appsec"
    }
    if any(k in s_low for k in sec_concepts_kw) or "concept" in (original_context or "").lower():
        return CATEGORY_SEC_CONCEPTS

    # Operating Systems
    os_kw = {"linux", "ubuntu", "debian", "kali", "rhel", "centos", "windows server", "macos", "unix"}
    if any(k in s_low for k in os_kw) or "operating" in (original_context or "").lower():
        return CATEGORY_OPERATING_SYSTEMS

    # Programming Languages
    langs_kw = {
        "python", "java", "javascript", "typescript", "c++", "c#", "golang", "rust", "php",
        "ruby", "sql", "bash", "powershell", "scala", "solidity", "perl", "kotlin", "swift",
        "html", "css", "assembly"
    }
    if any(k == s_low or k in s_low.split() for k in langs_kw) or "language" in (original_context or "").lower():
        return CATEGORY_PROG_LANGUAGES

    # Databases
    db_kw = {
        "postgres", "mysql", "mongodb", "redis", "sqlite", "oracle", "elasticsearch", "cassandra",
        "dynamodb", "mariadb", "neo4j", "database", "dbms"
    }
    if any(k in s_low for k in db_kw) or "database" in (original_context or "").lower():
        return CATEGORY_DATABASES

    # Cloud & DevOps
    cloud_kw = {
        "aws", "azure", "gcp", "docker", "kubernetes", "k8s", "terraform", "ansible", "git",
        "github", "gitlab", "jenkins", "ci/cd", "ci cd", "cloud", "devops", "helm", "virtualbox", "vmware"
    }
    if any(k in s_low for k in cloud_kw) or "cloud" in (original_context or "").lower():
        return CATEGORY_CLOUD_DEVOPS

    # Networking Technologies
    net_tokens = set(re.split(r"[\s/\-_]+", s_low))
    net_kw = {"tcp", "ip", "dns", "dhcp", "vpn", "vlan", "routing", "switching", "tls", "ssl", "ssh", "network", "protocol", "packet", "firewall"}
    if net_tokens.intersection(net_kw) or any(k in s_low for k in ("tcp/ip", "packet analysis", "firewall")) or "network" in (original_context or "").lower():
        return CATEGORY_NETWORKING

    # Frameworks & Libraries
    framework_kw = {
        "fastapi", "flask", "django", "react", "node", "express", "angular", "vue", "next",
        "spring", "langchain", "bootstrap", "tailwind", "framework", "library", "scapy", "requests"
    }
    if any(k in s_low for k in framework_kw) or "framework" in (original_context or "").lower():
        return CATEGORY_FRAMEWORKS

    # Data Science & Machine Learning
    ds_kw = {"machine learning", "deep learning", "nlp", "pytorch", "tensorflow", "scikit", "pandas", "numpy", "tableau"}
    if any(k in s_low for k in ds_kw) or "data" in (original_context or "").lower():
        return CATEGORY_DATA_SCIENCE

    # Context-based fallback
    if original_context:
        ctx_low = original_context.lower()
        if "tool" in ctx_low:
            return CATEGORY_CYBER_TOOLS
        if "security" in ctx_low or "domain" in ctx_low or "concept" in ctx_low:
            return CATEGORY_SEC_CONCEPTS
        if "language" in ctx_low or "programming" in ctx_low:
            return CATEGORY_PROG_LANGUAGES
        if "cloud" in ctx_low or "devops" in ctx_low:
            return CATEGORY_CLOUD_DEVOPS
        if "framework" in ctx_low:
            return CATEGORY_FRAMEWORKS
        if "database" in ctx_low:
            return CATEGORY_DATABASES
        if "network" in ctx_low:
            return CATEGORY_NETWORKING

    # If it cannot be reliably classified, return None so it is discarded rather than polluting the resume
    return None


def structure_and_classify_skills(
    raw_skills: List[str],
    candidate_name: Optional[str] = None,
    contact_info: Optional[Any] = None,
    target_role_name: Optional[str] = None,
) -> Dict[str, List[str]]:
    """Transforms a raw list of candidate skills into cleaned, categorized, deduplicated structured data.

    Returns a dictionary mapping standard categories to lists of individual skill names.
    Empty categories are omitted.
    """
    grouped: Dict[str, List[str]] = {cat: [] for cat in STANDARD_CATEGORIES}
    seen_normalized: Set[str] = set()

    for item in raw_skills:
        if not item or not isinstance(item, str):
            continue

        # If item has commas or slashes, break it down
        sub_tokens = re.split(r"[,;•\*\n|]\s*", item)
        for token in sub_tokens:
            token_clean = token.strip()
            if not token_clean:
                continue

            # Strip leading category labels like "Programming Languages: Python"
            token_clean = re.sub(
                r"^(?:programming\s+languages?|languages?|core\s+competencies?|security\s+tools?|tools?|"
                r"developer\s+tools?|databases?|dbms|technologies|cloud|frameworks?|operating\s+systems?|"
                r"security\s+concepts?|security\s+domains?|networking)\s*[:\-]\s*",
                "",
                token_clean,
                flags=re.IGNORECASE
            ).strip()

            if not is_valid_technical_skill(token_clean, candidate_name, contact_info):
                continue

            norm_name = normalize_skill_name(token_clean)
            norm_key = norm_name.lower()

            if norm_key in seen_normalized:
                continue
            seen_normalized.add(norm_key)

            cat = classify_skill(norm_name)
            if cat and cat in grouped:
                grouped[cat].append(norm_name)

    # Dynamic ordering: prioritize Cybersecurity Tools & Security Concepts for security roles
    is_sec = True
    if target_role_name:
        role_low = target_role_name.lower()
        is_sec = any(t in role_low for t in ("security", "hacker", "pentest", "soc", "analyst", "forensic", "vapt", "threat", "cyber", "incident", "iam", "grc"))

    if is_sec:
        ordered_keys = [
            CATEGORY_CYBER_TOOLS,
            CATEGORY_SEC_CONCEPTS,
            CATEGORY_PROG_LANGUAGES,
            CATEGORY_OPERATING_SYSTEMS,
            CATEGORY_FRAMEWORKS,
            CATEGORY_DATABASES,
            CATEGORY_CLOUD_DEVOPS,
            CATEGORY_NETWORKING,
            CATEGORY_DATA_SCIENCE,
        ]
    else:
        ordered_keys = [
            CATEGORY_PROG_LANGUAGES,
            CATEGORY_FRAMEWORKS,
            CATEGORY_DATABASES,
            CATEGORY_CLOUD_DEVOPS,
            CATEGORY_OPERATING_SYSTEMS,
            CATEGORY_CYBER_TOOLS,
            CATEGORY_SEC_CONCEPTS,
            CATEGORY_NETWORKING,
            CATEGORY_DATA_SCIENCE,
        ]

    # Return only populated categories in prioritized order
    return {k: grouped[k] for k in ordered_keys if grouped.get(k)}
