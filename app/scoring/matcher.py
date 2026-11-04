"""Skill matching and evidence normalization module for cybersecurity roles.

Performs deterministic exact matching and alias normalization against Neon database skills.
Identifies matched skills, semantic/project evidence, and skills not demonstrated.
Never assumes candidate possesses skills absent from the resume.
"""

import re
from typing import List, Dict, Any, Set, Tuple
from pydantic import BaseModel, Field


class SkillMatchResult(BaseModel):
    skill_name: str
    importance: str  # core, preferred, additional
    status: str  # matched, not_demonstrated
    matched_in_sections: List[str] = Field(default_factory=list)
    evidence_snippet: str | None = None
    confidence: float = 0.0  # 1.0 for exact, 0.85 for alias/evidence


class EvidenceMatchReport(BaseModel):
    role_id: int
    role_name: str
    total_role_skills: int
    matched_skills: List[SkillMatchResult] = Field(default_factory=list)
    unmatched_skills: List[SkillMatchResult] = Field(default_factory=list)
    matched_core_count: int = 0
    total_core_count: int = 0
    matched_preferred_count: int = 0
    total_preferred_count: int = 0
    matched_additional_count: int = 0
    total_additional_count: int = 0


class SkillMatcher:
    """Matches candidate resume content against database role requirements and skills."""

    # Cybersecurity skill alias dictionary (canonical -> list of synonyms/aliases/tools)
    CYBER_ALIASES: Dict[str, List[str]] = {
        "penetration testing": ["pentesting", "pen testing", "ethical hacking", "red teaming", "offensive security", "metasploit"],
        "vulnerability assessment": ["vulnerability scanning", "vulnerability management", "vuln assessment", "nessus", "qualys", "openvas"],
        "network security": ["firewall", "ids", "ips", "snort", "suricata", "palo alto", "fortinet", "cisco", "network monitoring"],
        "siem": ["splunk", "qradar", "arcsight", "log analysis", "security information and event management", "sentinel", "elk stack"],
        "incident response": ["incident handling", "dfir", "digital forensics", "computer forensics", "triage", "threat mitigation"],
        "web application security": ["owasp", "owasp top 10", "burp suite", "sql injection", "xss", "csrf", "appsec"],
        "cloud security": ["aws security", "azure security", "gcp security", "cloud compliance", "iam", "cloudwatch", "guardduty"],
        "threat intelligence": ["cti", "mitre att&ck", "threat hunting", "ioc", "yara", "threat modeling", "stride"],
        "cryptography": ["pki", "tls", "ssl", "aes", "rsa", "encryption", "hashing", "key management"],
        "endpoint security": ["edr", "crowdstrike", "sentinelone", "carbon black", "antivirus", "endpoint detection"],
        "python": ["python3", "py", "scapy", "sockets"],
        "scripting": ["bash", "shell scripting", "powershell", "python", "automation"],
        "linux": ["kali linux", "ubuntu", "debian", "red hat", "centos", "unix"],
        "wireshark": ["packet analysis", "network traffic analysis", "pcap", "tshark"],
        "active directory": ["azure ad", "entra id", "domain controller", "ldap", "kerberos"],
        "compliance": ["iso 27001", "nist", "soc 2", "pci dss", "hipaa", "gdpr", "cis benchmarks"],
        "identity and access management": ["iam", "sso", "mfa", "saml", "oauth", "okta"],
        "reverse engineering": ["ghidra", "ida pro", "x64dbg", "malware analysis", "disassembly"],
        "soc operations": ["security operations center", "tier 1", "tier 2", "alert triage", "soc analyst"],
    }

    @classmethod
    def normalize_term(cls, term: str) -> str:
        """Normalizes skill term by stripping punctuation and lowercasing."""
        cleaned = re.sub(r"[^a-zA-Z0-9\s\+\#\./\-]", "", term).strip().lower()
        return cleaned

    @classmethod
    def match_skills(
        cls,
        role_skills: List[Dict[str, Any]],
        resume_skills: List[str],
        resume_full_text: str,
        resume_projects: List[Any],
        resume_experience: List[Any],
        role_id: int,
        role_name: str,
    ) -> EvidenceMatchReport:
        """Compares resume evidence against database role skills."""
        matched: List[SkillMatchResult] = []
        unmatched: List[SkillMatchResult] = []

        norm_resume_skills = {cls.normalize_term(s) for s in resume_skills if s}
        full_text_lower = resume_full_text.lower()

        core_total = 0
        core_matched = 0
        pref_total = 0
        pref_matched = 0
        add_total = 0
        add_matched = 0

        for r_skill in role_skills:
            skill_name = r_skill["skill_name"]
            importance = r_skill.get("importance", "preferred").lower()

            if importance == "core":
                core_total += 1
            elif importance == "preferred":
                pref_total += 1
            elif importance == "additional":
                add_total += 1

            norm_db_skill = cls.normalize_term(skill_name)
            sections_found: Set[str] = set()
            evidence_snip: str | None = None
            is_matched = False
            confidence = 0.0

            # 1. Exact or partial match in extracted technical skills
            if norm_db_skill in norm_resume_skills or any(norm_db_skill in s for s in norm_resume_skills):
                is_matched = True
                confidence = 1.0
                sections_found.add("Technical Skills")
                evidence_snip = f"Directly listed in Technical Skills: '{skill_name}'"

            # 2. Match in full text using whole word boundary regex
            if not is_matched:
                pattern = re.compile(rf"\b{re.escape(norm_db_skill)}\b", re.IGNORECASE)
                match = pattern.search(full_text_lower)
                if match:
                    is_matched = True
                    confidence = 0.95
                    # Extract surrounding snippet
                    start = max(0, match.start() - 30)
                    end = min(len(resume_full_text), match.end() + 30)
                    evidence_snip = f"...{resume_full_text[start:end].strip()}..."
                    sections_found.add("Resume Text")

            # 3. Alias / Synonym search
            if not is_matched:
                aliases = cls._get_aliases_for(norm_db_skill)
                for alias in aliases:
                    alias_norm = cls.normalize_term(alias)
                    if alias_norm in norm_resume_skills:
                        is_matched = True
                        confidence = 0.85
                        sections_found.add("Technical Skills (via alias)")
                        evidence_snip = f"Demonstrated via related tool/term: '{alias}' for '{skill_name}'"
                        break
                    # Search projects
                    for proj in resume_projects:
                        p_desc = (getattr(proj, "description", "") or "").lower()
                        p_title = (getattr(proj, "title", "") or "").lower()
                        if alias_norm in p_desc or alias_norm in p_title or norm_db_skill in p_desc:
                            is_matched = True
                            confidence = 0.85
                            sections_found.add("Projects")
                            evidence_snip = f"Applied in project '{getattr(proj, 'title', '')}'"
                            break
                    if is_matched:
                        break

            # 4. Search work experience responsibilities
            if not is_matched:
                for exp in resume_experience:
                    resp_text = " ".join(getattr(exp, "responsibilities", [])).lower()
                    if norm_db_skill in resp_text:
                        is_matched = True
                        confidence = 0.90
                        sections_found.add("Work Experience")
                        evidence_snip = f"Demonstrated in role '{getattr(exp, 'job_title', '')}'"
                        break

            # Record result
            if is_matched:
                res = SkillMatchResult(
                    skill_name=skill_name,
                    importance=importance,
                    status="matched",
                    matched_in_sections=list(sections_found),
                    evidence_snippet=evidence_snip,
                    confidence=confidence,
                )
                matched.append(res)
                if importance == "core":
                    core_matched += 1
                elif importance == "preferred":
                    pref_matched += 1
                elif importance == "additional":
                    add_matched += 1
            else:
                res = SkillMatchResult(
                    skill_name=skill_name,
                    importance=importance,
                    status="not_demonstrated",
                    matched_in_sections=[],
                    evidence_snippet="No direct or semantic evidence found in resume",
                    confidence=0.0,
                )
                unmatched.append(res)

        return EvidenceMatchReport(
            role_id=role_id,
            role_name=role_name,
            total_role_skills=len(role_skills),
            matched_skills=matched,
            unmatched_skills=unmatched,
            matched_core_count=core_matched,
            total_core_count=core_total,
            matched_preferred_count=pref_matched,
            total_preferred_count=pref_total,
            matched_additional_count=add_matched,
            total_additional_count=add_total,
        )

    @classmethod
    def _get_aliases_for(cls, term: str) -> List[str]:
        """Retrieves synonyms and aliases for a normalized skill."""
        aliases = []
        for canonical, syns in cls.CYBER_ALIASES.items():
            if term == canonical or term in syns or canonical in term:
                aliases.extend(syns)
                aliases.append(canonical)
        return list(set(aliases))
