"""Standard ATS-friendly resume template registry for FUTRSEC.

Defines exactly 30 distinct, professional, ATS-compliant black-and-white resume templates.
All 30 templates follow one consistent ATS structure:
HEADER -> PROFESSIONAL SUMMARY -> TECHNICAL SKILLS -> PROJECTS.
Visual styling (fonts, alignments, margins, dividers, and spacing) remains distinct per template.
Strictly black text on pure white background.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ResumeTemplate(BaseModel):
    template_id: str
    template_name: str
    description: str
    is_active: bool = True
    supported_formats: List[str] = Field(default_factory=lambda: ["docx", "pdf"])
    role_category_tags: List[str] = Field(default_factory=list)
    style_config: Dict[str, Any] = Field(default_factory=dict)


# Exactly 30 distinct professional black-and-white ATS-friendly templates (T01 - T30)
# Following one consistent ATS structure: HEADER -> PROFESSIONAL SUMMARY -> TECHNICAL SKILLS -> PROJECTS
STANDARD_TEMPLATES: List[ResumeTemplate] = [
    # T01: Professional Classic
    ResumeTemplate(
        template_id="T01",
        template_name="Professional Classic",
        description="Traditional corporate resume with centered name, clean horizontal rules, and formal section hierarchy.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['general', 'compliance', 'management', 'audit', 'governance'],
        style_config={
            "font_family": 'Calibri',
            "heading_font": 'Calibri',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'center',
            "header_style": 'classic_centered',
            "divider_style": 'solid',
            "margins_in": 0.75,
            "title_font_size_pt": 22.0,
            "heading_font_size_pt": 12.5,
            "body_font_size_pt": 10.5,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 8.0,
            "section_spacing_after_pt": 3.0,
            "item_spacing_pt": 4.0,
            "bullet_spacing_pt": 2.0,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'title_company_line',
            "project_format": 'standard',
        },
    ),

    # T02: Modern Professional
    ResumeTemplate(
        template_id="T02",
        template_name="Modern Professional",
        description="Clean contemporary layout with left-aligned header, subtle whitespace separation, and modern sans-serif typography.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['engineering', 'cloud', 'devsecops', 'general', 'modern'],
        style_config={
            "font_family": 'Arial',
            "heading_font": 'Arial',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'left',
            "header_style": 'minimal_left',
            "divider_style": 'none',
            "margins_in": 0.65,
            "title_font_size_pt": 20.0,
            "heading_font_size_pt": 12.0,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.0,
            "section_spacing_before_pt": 10.0,
            "section_spacing_after_pt": 2.0,
            "item_spacing_pt": 3.5,
            "bullet_spacing_pt": 1.5,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'two_line',
            "project_format": 'compact',
        },
    ),

    # T03: Technical Expert
    ResumeTemplate(
        template_id="T03",
        template_name="Technical Expert",
        description="Technical skills and toolsets emphasized with structured categorized skill matrices and project implementations.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['technical', 'security-engineer', 'infosec', 'analyst'],
        style_config={
            "font_family": 'Calibri',
            "heading_font": 'Calibri',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'left',
            "header_style": 'technical_left',
            "divider_style": 'solid',
            "margins_in": 0.7,
            "title_font_size_pt": 21.0,
            "heading_font_size_pt": 12.0,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 8.0,
            "section_spacing_after_pt": 3.0,
            "item_spacing_pt": 4.0,
            "bullet_spacing_pt": 2.0,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'title_company_line',
            "project_format": 'detailed',
        },
    ),

    # T04: Cybersecurity Specialist
    ResumeTemplate(
        template_id="T04",
        template_name="Cybersecurity Specialist",
        description="Security skills, credentials, and industry certifications prioritized in an executive centered format.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['cybersecurity', 'certifications', 'specialist', 'executive'],
        style_config={
            "font_family": 'Times New Roman',
            "heading_font": 'Times New Roman',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'center',
            "header_style": 'classic_centered',
            "divider_style": 'double',
            "margins_in": 0.8,
            "title_font_size_pt": 23.0,
            "heading_font_size_pt": 13.0,
            "body_font_size_pt": 10.5,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 9.0,
            "section_spacing_after_pt": 3.0,
            "item_spacing_pt": 4.5,
            "bullet_spacing_pt": 2.0,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'two_line',
            "project_format": 'standard',
        },
    ),

    # T05: Executive Minimal
    ResumeTemplate(
        template_id="T05",
        template_name="Executive Minimal",
        description="Contemporary Aptos typography with understated spacing and clean whitespace dividers for consulting and leadership roles.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['executive', 'minimal', 'consulting', 'aptos'],
        style_config={
            "font_family": 'Aptos',
            "heading_font": 'Aptos',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'left',
            "header_style": 'minimal_left',
            "divider_style": 'none',
            "margins_in": 0.7,
            "title_font_size_pt": 21.0,
            "heading_font_size_pt": 12.0,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 9.0,
            "section_spacing_after_pt": 2.5,
            "item_spacing_pt": 4.0,
            "bullet_spacing_pt": 2.0,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'title_company_line',
            "project_format": 'standard',
        },
    ),

    # T06: Fresher Starter
    ResumeTemplate(
        template_id="T06",
        template_name="Fresher Starter",
        description="Education and academic/lab projects prioritized above experience for college graduates, career transitioners, and freshers.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['fresher', 'entry-level', 'graduate', 'internship', 'starter'],
        style_config={
            "font_family": 'Calibri',
            "heading_font": 'Calibri',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'center',
            "header_style": 'modern_centered',
            "divider_style": 'solid',
            "margins_in": 0.75,
            "title_font_size_pt": 21.0,
            "heading_font_size_pt": 12.0,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 8.0,
            "section_spacing_after_pt": 3.0,
            "item_spacing_pt": 3.5,
            "bullet_spacing_pt": 1.5,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'title_company_line',
            "project_format": 'detailed',
        },
    ),

    # T07: SOC Analyst
    ResumeTemplate(
        template_id="T07",
        template_name="SOC Analyst",
        description="Security Operations Center monitoring, SIEM detection, and incident response experience prioritized.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['soc', 'analyst', 'monitoring', 'siem', 'incident-response'],
        style_config={
            "font_family": 'Times New Roman',
            "heading_font": 'Times New Roman',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'center',
            "header_style": 'classic_centered',
            "divider_style": 'solid',
            "margins_in": 0.75,
            "title_font_size_pt": 22.0,
            "heading_font_size_pt": 12.5,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 8.5,
            "section_spacing_after_pt": 3.0,
            "item_spacing_pt": 4.0,
            "bullet_spacing_pt": 2.0,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'two_line',
            "project_format": 'standard',
        },
    ),

    # T08: Ethical Hacker
    ResumeTemplate(
        template_id="T08",
        template_name="Ethical Hacker",
        description="Offensive security, penetration testing toolsets, and vulnerability exploitation projects prioritized.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['offensive-security', 'penetration-testing', 'ethical-hacking', 'red-team', 'appsec'],
        style_config={
            "font_family": 'Arial',
            "heading_font": 'Arial',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'left',
            "header_style": 'technical_left',
            "divider_style": 'thick',
            "margins_in": 0.65,
            "title_font_size_pt": 21.0,
            "heading_font_size_pt": 12.0,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.0,
            "section_spacing_before_pt": 8.0,
            "section_spacing_after_pt": 3.0,
            "item_spacing_pt": 3.5,
            "bullet_spacing_pt": 1.5,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'title_company_line',
            "project_format": 'detailed',
        },
    ),

    # T09: Network Security
    ResumeTemplate(
        template_id="T09",
        template_name="Network Security",
        description="Network infrastructure defense, firewalls, IDS/IPS, protocol inspection, and architecture projects prioritized.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['network-security', 'firewall', 'infrastructure', 'defense', 'systems'],
        style_config={
            "font_family": 'Aptos',
            "heading_font": 'Aptos',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'left',
            "header_style": 'split_left',
            "divider_style": 'solid',
            "margins_in": 0.7,
            "title_font_size_pt": 21.0,
            "heading_font_size_pt": 12.0,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 8.0,
            "section_spacing_after_pt": 2.5,
            "item_spacing_pt": 4.0,
            "bullet_spacing_pt": 2.0,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'title_company_line',
            "project_format": 'detailed',
        },
    ),

    # T10: Cloud Security
    ResumeTemplate(
        template_id="T10",
        template_name="Cloud Security",
        description="Cloud infrastructure (AWS/Azure/GCP), IAM hardening, and cloud-native security certifications prioritized.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['cloud-security', 'aws', 'azure', 'gcp', 'iam', 'devsecops'],
        style_config={
            "font_family": 'Times New Roman',
            "heading_font": 'Times New Roman',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'center',
            "header_style": 'classic_centered',
            "divider_style": 'solid',
            "margins_in": 0.75,
            "title_font_size_pt": 22.0,
            "heading_font_size_pt": 12.5,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 8.5,
            "section_spacing_after_pt": 3.0,
            "item_spacing_pt": 4.0,
            "bullet_spacing_pt": 2.0,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'two_line',
            "project_format": 'standard',
        },
    ),

    # T11: Application Security
    ResumeTemplate(
        template_id="T11",
        template_name="Application Security",
        description="Secure software development, SAST/DAST testing, code review, and OWASP Top 10 mitigation prioritized.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['appsec', 'sast', 'dast', 'owasp', 'software-security', 'developer'],
        style_config={
            "font_family": 'Arial',
            "heading_font": 'Arial',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'left',
            "header_style": 'compact_left',
            "divider_style": 'none',
            "margins_in": 0.6,
            "title_font_size_pt": 19.5,
            "heading_font_size_pt": 11.5,
            "body_font_size_pt": 9.5,
            "contact_font_size_pt": 9.0,
            "section_spacing_before_pt": 7.0,
            "section_spacing_after_pt": 2.0,
            "item_spacing_pt": 3.0,
            "bullet_spacing_pt": 1.5,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'title_company_line',
            "project_format": 'compact',
        },
    ),

    # T12: Digital Forensics
    ResumeTemplate(
        template_id="T12",
        template_name="Digital Forensics",
        description="Digital evidence examination, forensic artifact analysis, chain of custody, and incident investigation prioritized.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['forensics', 'dfir', 'investigation', 'incident-response', 'evidence'],
        style_config={
            "font_family": 'Times New Roman',
            "heading_font": 'Times New Roman',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'left',
            "header_style": 'classic_centered',
            "divider_style": 'solid',
            "margins_in": 0.75,
            "title_font_size_pt": 21.5,
            "heading_font_size_pt": 12.0,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 8.5,
            "section_spacing_after_pt": 3.0,
            "item_spacing_pt": 4.0,
            "bullet_spacing_pt": 2.0,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'two_line',
            "project_format": 'detailed',
        },
    ),

    # T13: Incident Response
    ResumeTemplate(
        template_id="T13",
        template_name="Incident Response",
        description="Threat containment, remediation playbooks, malware triage, and incident handling experience prioritized.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['incident-response', 'dfir', 'threat-containment', 'playbooks', 'soc'],
        style_config={
            "font_family": 'Calibri',
            "heading_font": 'Calibri',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'left',
            "header_style": 'technical_left',
            "divider_style": 'solid',
            "margins_in": 0.7,
            "title_font_size_pt": 21.0,
            "heading_font_size_pt": 12.0,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 8.0,
            "section_spacing_after_pt": 2.5,
            "item_spacing_pt": 4.0,
            "bullet_spacing_pt": 2.0,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'title_company_line',
            "project_format": 'standard',
        },
    ),

    # T14: Vulnerability Analyst
    ResumeTemplate(
        template_id="T14",
        template_name="Vulnerability Analyst",
        description="Vulnerability scanning, CVE/CVSS prioritization, patch tracking, and risk assessment projects prioritized.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['vulnerability-analyst', 'scanning', 'nessus', 'qualys', 'remediation', 'cve'],
        style_config={
            "font_family": 'Aptos',
            "heading_font": 'Aptos',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'center',
            "header_style": 'modern_centered',
            "divider_style": 'solid',
            "margins_in": 0.75,
            "title_font_size_pt": 21.0,
            "heading_font_size_pt": 12.0,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 8.0,
            "section_spacing_after_pt": 3.0,
            "item_spacing_pt": 3.5,
            "bullet_spacing_pt": 1.5,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'title_company_line',
            "project_format": 'standard',
        },
    ),

    # T15: Security Consultant
    ResumeTemplate(
        template_id="T15",
        template_name="Security Consultant",
        description="Client engagements, advisory experience, compliance frameworks, and architecture consulting prioritized.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['consultant', 'advisory', 'engagements', 'risk', 'audit', 'security-consulting'],
        style_config={
            "font_family": 'Calibri',
            "heading_font": 'Calibri',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'left',
            "header_style": 'split_left',
            "divider_style": 'solid',
            "margins_in": 0.75,
            "title_font_size_pt": 21.5,
            "heading_font_size_pt": 12.0,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 8.5,
            "section_spacing_after_pt": 3.0,
            "item_spacing_pt": 4.0,
            "bullet_spacing_pt": 2.0,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'title_company_line',
            "project_format": 'standard',
        },
    ),

    # T16: Academic Technical
    ResumeTemplate(
        template_id="T16",
        template_name="Academic Technical",
        description="Education, technical coursework, hands-on lab projects, and cybersecurity thesis work prioritized.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['academic', 'student', 'coursework', 'labs', 'education-first'],
        style_config={
            "font_family": 'Arial',
            "heading_font": 'Arial',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'left',
            "header_style": 'technical_left',
            "divider_style": 'solid',
            "margins_in": 0.7,
            "title_font_size_pt": 21.0,
            "heading_font_size_pt": 12.0,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.0,
            "section_spacing_before_pt": 8.0,
            "section_spacing_after_pt": 2.5,
            "item_spacing_pt": 3.5,
            "bullet_spacing_pt": 1.5,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'title_company_line',
            "project_format": 'detailed',
        },
    ),

    # T17: Project Focused
    ResumeTemplate(
        template_id="T17",
        template_name="Project Focused",
        description="Major technical cybersecurity projects and hands-on implementations showcased immediately below summary.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['projects', 'portfolio', 'technical', 'hands-on', 'implementations'],
        style_config={
            "font_family": 'Calibri',
            "heading_font": 'Calibri',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'left',
            "header_style": 'technical_left',
            "divider_style": 'solid',
            "margins_in": 0.7,
            "title_font_size_pt": 21.0,
            "heading_font_size_pt": 12.0,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 8.0,
            "section_spacing_after_pt": 3.0,
            "item_spacing_pt": 4.0,
            "bullet_spacing_pt": 2.0,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'title_company_line',
            "project_format": 'detailed',
        },
    ),

    # T18: Skills First
    ResumeTemplate(
        template_id="T18",
        template_name="Skills First",
        description="Comprehensive technical competency matrix prioritized for direct recruiter and ATS keyword matching.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['skills', 'matrix', 'keywords', 'ats-optimized', 'technical'],
        style_config={
            "font_family": 'Arial',
            "heading_font": 'Arial',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'left',
            "header_style": 'compact_left',
            "divider_style": 'thick',
            "margins_in": 0.65,
            "title_font_size_pt": 21.0,
            "heading_font_size_pt": 12.0,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.0,
            "section_spacing_before_pt": 8.0,
            "section_spacing_after_pt": 2.5,
            "item_spacing_pt": 3.5,
            "bullet_spacing_pt": 1.5,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'title_company_line',
            "project_format": 'compact',
        },
    ),

    # T19: Certification Focused
    ResumeTemplate(
        template_id="T19",
        template_name="Certification Focused",
        description="Verified cybersecurity credentials and industry certifications placed directly after summary.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['certifications', 'security-plus', 'ceh', 'cissp', 'oscp', 'credentials'],
        style_config={
            "font_family": 'Calibri',
            "heading_font": 'Calibri',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'left',
            "header_style": 'split_left',
            "divider_style": 'solid',
            "margins_in": 0.7,
            "title_font_size_pt": 21.0,
            "heading_font_size_pt": 12.0,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 8.0,
            "section_spacing_after_pt": 3.0,
            "item_spacing_pt": 4.0,
            "bullet_spacing_pt": 2.0,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'title_company_line',
            "project_format": 'standard',
        },
    ),

    # T20: Experience First
    ResumeTemplate(
        template_id="T20",
        template_name="Experience First",
        description="Reverse chronological professional work history prioritized with executive Times New Roman typography.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['senior', 'lead', 'chronological', 'experience', 'leadership', 'executive'],
        style_config={
            "font_family": 'Times New Roman',
            "heading_font": 'Times New Roman',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'center',
            "header_style": 'classic_centered',
            "divider_style": 'solid',
            "margins_in": 0.8,
            "title_font_size_pt": 23.0,
            "heading_font_size_pt": 13.0,
            "body_font_size_pt": 10.5,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 9.0,
            "section_spacing_after_pt": 3.0,
            "item_spacing_pt": 5.0,
            "bullet_spacing_pt": 2.0,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'two_line',
            "project_format": 'standard',
        },
    ),

    # T21: Modern Compact
    ResumeTemplate(
        template_id="T21",
        template_name="Modern Compact",
        description="Space-efficient single-column layout with compact line heights and tight margins for dense 1-page presentation.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['compact', 'one-page', 'modern', 'space-efficient', 'cybersecurity', 'analyst'],
        style_config={
            "font_family": 'Arial',
            "heading_font": 'Arial',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'left',
            "header_style": 'compact_left',
            "divider_style": 'none',
            "margins_in": 0.6,
            "title_font_size_pt": 19.5,
            "heading_font_size_pt": 11.5,
            "body_font_size_pt": 9.5,
            "contact_font_size_pt": 9.0,
            "section_spacing_before_pt": 6.0,
            "section_spacing_after_pt": 2.0,
            "item_spacing_pt": 3.0,
            "bullet_spacing_pt": 1.5,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'title_company_line',
            "project_format": 'compact',
        },
    ),

    # T22: Technical Research
    ResumeTemplate(
        template_id="T22",
        template_name="Technical Research",
        description="Research credentials, vulnerability disclosures, technical investigations, and academic honors prioritized.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['research', 'academic', 'cryptography', 'threat-research', 'cyber-crime', 'investigation'],
        style_config={
            "font_family": 'Times New Roman',
            "heading_font": 'Times New Roman',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'left',
            "header_style": 'research_serif',
            "divider_style": 'solid',
            "margins_in": 0.75,
            "title_font_size_pt": 22.0,
            "heading_font_size_pt": 12.5,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 9.0,
            "section_spacing_after_pt": 3.0,
            "item_spacing_pt": 4.5,
            "bullet_spacing_pt": 2.0,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'two_line',
            "project_format": 'detailed',
        },
    ),

    # T23: Security Operations
    ResumeTemplate(
        template_id="T23",
        template_name="Security Operations",
        description="SOC operational workflows, alert triage, incident escalation, and SIEM monitoring experience prioritized.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['soc', 'operations', 'monitoring', 'siem', 'incident-response', 'analyst', 'triage'],
        style_config={
            "font_family": 'Calibri',
            "heading_font": 'Calibri',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'left',
            "header_style": 'soc_ops',
            "divider_style": 'solid',
            "margins_in": 0.7,
            "title_font_size_pt": 21.5,
            "heading_font_size_pt": 12.0,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 8.0,
            "section_spacing_after_pt": 2.5,
            "item_spacing_pt": 4.0,
            "bullet_spacing_pt": 2.0,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'title_company_line',
            "project_format": 'standard',
        },
    ),

    # T24: Infrastructure Security
    ResumeTemplate(
        template_id="T24",
        template_name="Infrastructure Security",
        description="Hardened Linux environments, perimeter network security, system administration, and infrastructure defense prioritized.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['infrastructure', 'linux', 'networking', 'hardening', 'firewall', 'systems-admin', 'bastion'],
        style_config={
            "font_family": 'Arial',
            "heading_font": 'Arial',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'left',
            "header_style": 'infrastructure_left',
            "divider_style": 'thick',
            "margins_in": 0.65,
            "title_font_size_pt": 21.0,
            "heading_font_size_pt": 12.0,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.0,
            "section_spacing_before_pt": 8.5,
            "section_spacing_after_pt": 3.0,
            "item_spacing_pt": 4.0,
            "bullet_spacing_pt": 2.0,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'two_line',
            "project_format": 'detailed',
        },
    ),

    # T25: DevSecOps Professional
    ResumeTemplate(
        template_id="T25",
        template_name="DevSecOps Professional",
        description="CI/CD security automation, Infrastructure as Code scanning, container hardening, and modern cloud pipeline defense.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['devsecops', 'automation', 'cicd', 'cloud', 'containers', 'iac', 'security-automation', 'kubernetes'],
        style_config={
            "font_family": 'Aptos',
            "heading_font": 'Aptos',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'left',
            "header_style": 'devsecops_modern',
            "divider_style": 'solid',
            "margins_in": 0.7,
            "title_font_size_pt": 21.0,
            "heading_font_size_pt": 12.0,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 8.0,
            "section_spacing_after_pt": 2.5,
            "item_spacing_pt": 4.0,
            "bullet_spacing_pt": 2.0,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'title_company_line',
            "project_format": 'standard',
        },
    ),

    # T26: GRC Professional
    ResumeTemplate(
        template_id="T26",
        template_name="GRC Professional",
        description="Governance, Risk and Compliance framework alignment (NIST, ISO 27001, SOC 2, HIPAA, PCI-DSS) and audit leadership.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['grc', 'compliance', 'audit', 'governance', 'risk-assessment', 'nist', 'iso27001', 'policy'],
        style_config={
            "font_family": 'Times New Roman',
            "heading_font": 'Times New Roman',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'center',
            "header_style": 'classic_centered',
            "divider_style": 'solid',
            "margins_in": 0.8,
            "title_font_size_pt": 22.5,
            "heading_font_size_pt": 12.5,
            "body_font_size_pt": 10.5,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 9.0,
            "section_spacing_after_pt": 3.0,
            "item_spacing_pt": 4.5,
            "bullet_spacing_pt": 2.0,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'two_line',
            "project_format": 'standard',
        },
    ),

    # T27: Threat Intelligence
    ResumeTemplate(
        template_id="T27",
        template_name="Threat Intelligence",
        description="Cyber Threat Intelligence (CTI), adversary attribution, MITRE ATT&CK mapping, IOC feeds, and OSINT investigation.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['cti', 'threat-intelligence', 'mitre-att&ck', 'adversary', 'osint', 'ioc', 'analyst', 'threat-hunting'],
        style_config={
            "font_family": 'Aptos',
            "heading_font": 'Aptos',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'left',
            "header_style": 'intel_left',
            "divider_style": 'solid',
            "margins_in": 0.7,
            "title_font_size_pt": 21.0,
            "heading_font_size_pt": 12.0,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 8.0,
            "section_spacing_after_pt": 3.0,
            "item_spacing_pt": 4.0,
            "bullet_spacing_pt": 2.0,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'title_company_line',
            "project_format": 'detailed',
        },
    ),

    # T28: IAM Specialist
    ResumeTemplate(
        template_id="T28",
        template_name="IAM Specialist",
        description="Identity & Access Management, Zero Trust architecture, Active Directory/Entra ID, PAM, SSO, and MFA engineering.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['iam', 'identity', 'zero-trust', 'active-directory', 'okta', 'saml', 'pam', 'access-control'],
        style_config={
            "font_family": 'Calibri',
            "heading_font": 'Calibri',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'left',
            "header_style": 'iam_left',
            "divider_style": 'solid',
            "margins_in": 0.7,
            "title_font_size_pt": 21.0,
            "heading_font_size_pt": 12.0,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 8.0,
            "section_spacing_after_pt": 2.5,
            "item_spacing_pt": 4.0,
            "bullet_spacing_pt": 2.0,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'title_company_line',
            "project_format": 'standard',
        },
    ),

    # T29: Security Engineer
    ResumeTemplate(
        template_id="T29",
        template_name="Security Engineer",
        description="Security systems architecture, tooling implementation, defense-in-depth, and enterprise security engineering.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['security-engineer', 'engineering', 'architecture', 'defense', 'systems', 'network-security', 'automation'],
        style_config={
            "font_family": 'Arial',
            "heading_font": 'Arial',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'left',
            "header_style": 'engineer_left',
            "divider_style": 'thick',
            "margins_in": 0.65,
            "title_font_size_pt": 22.0,
            "heading_font_size_pt": 12.0,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 8.5,
            "section_spacing_after_pt": 3.0,
            "item_spacing_pt": 4.0,
            "bullet_spacing_pt": 2.0,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'two_line',
            "project_format": 'detailed',
        },
    ),

    # T30: Universal ATS Professional
    ResumeTemplate(
        template_id="T30",
        template_name="Universal ATS Professional",
        description="Balanced, widely compatible layout suitable across all cybersecurity analyst, engineering, and specialist positions.",
        is_active=True,
        supported_formats=['docx', 'pdf'],
        role_category_tags=['universal', 'general', 'ats', 'analyst', 'engineer', 'balanced', 'cybersecurity'],
        style_config={
            "font_family": 'Calibri',
            "heading_font": 'Calibri',
            "primary_color": '#000000',
            "secondary_color": '#000000',
            "header_alignment": 'center',
            "header_style": 'classic_centered',
            "divider_style": 'solid',
            "margins_in": 0.75,
            "title_font_size_pt": 22.0,
            "heading_font_size_pt": 12.5,
            "body_font_size_pt": 10.0,
            "contact_font_size_pt": 9.5,
            "section_spacing_before_pt": 8.5,
            "section_spacing_after_pt": 3.0,
            "item_spacing_pt": 4.0,
            "bullet_spacing_pt": 2.0,
            "section_order": ['summary', 'skills', 'projects', 'certifications', 'experience', 'education'],
            "section_titles": {'summary': 'Professional Summary', 'skills': 'Technical Skills', 'projects': 'Projects', 'certifications': 'Certifications', 'experience': 'Professional Experience', 'education': 'Education'},
            "experience_format": 'title_company_line',
            "project_format": 'standard',
        },
    ),

]


# Backward compatibility mapping for legacy template IDs and names
LEGACY_TEMPLATE_MAP: Dict[str, str] = {
    "T1_PROFESSIONAL_CLASSIC": "T01",
    "T1": "T01",
    "T2_MODERN_MINIMAL": "T02",
    "T2": "T02",
    "T3_TECHNICAL_RESUME": "T03",
    "T3": "T03",
    "T4_CORPORATE_STANDARD": "T04",
    "T4": "T04",
    "T5_CYBERSECURITY_SPECIALIST": "T05",
    "T5": "T05",
    # Legacy name aliases
    "MODERN MINIMAL": "T02",
    "TECHNICAL SPECIALIST": "T03",
    "CORPORATE STANDARD": "T04",
    "CYBERSECURITY PROFESSIONAL": "T05",
    "GRADUATE ENTRY-LEVEL": "T06",
    "EXPERIENCED PROFESSIONAL": "T07",
    "TECHNICAL SKILLS FOCUS": "T08",
    "PROJECT PORTFOLIO": "T09",
    "CERTIFICATION FOCUS": "T10",
    "COMPACT PROFESSIONAL": "T11",
    "CHRONOLOGICAL STANDARD": "T12",
    "TECHNICAL PROJECT ENGINEER": "T13",
    "INTERNSHIP CANDIDATE": "T14",
    "SECURITY OPERATIONS": "T23",
    "PENETRATION TESTING": "T08",
    "SECURITY ENGINEERING": "T29",
    "SENIOR PROFESSIONAL": "T20",
}


class TemplateRegistry:
    """Manages active resume templates and retrieval."""

    def __init__(self, templates: Optional[List[ResumeTemplate]] = None):
        source = templates if templates is not None else STANDARD_TEMPLATES
        self._templates: Dict[str, ResumeTemplate] = {t.template_id: t for t in source}
        self._names_map: Dict[str, ResumeTemplate] = {t.template_name.upper(): t for t in source}

    def list_templates(self, active_only: bool = True) -> List[ResumeTemplate]:
        """Lists registered templates in sequential order."""
        templates = list(self._templates.values())
        if active_only:
            templates = [t for t in templates if t.is_active]
        return templates

    def get_template(self, template_id: str) -> Optional[ResumeTemplate]:
        """Retrieves a single template by ID or legacy alias fallback."""
        if not template_id:
            return None
        if template_id in self._templates:
            return self._templates[template_id]
        norm = template_id.strip().upper()
        if norm in self._templates:
            return self._templates[norm]
        if norm in self._names_map:
            return self._names_map[norm]
        mapped_id = LEGACY_TEMPLATE_MAP.get(norm)
        if mapped_id and mapped_id in self._templates:
            return self._templates[mapped_id]
        return None

    def get_eligible_templates(self, role_name: Optional[str] = None) -> List[ResumeTemplate]:
        """Returns active templates in sequence for Round Robin scheduling."""
        return [t for t in self._templates.values() if t.is_active]

    def set_template_status(self, template_id: str, is_active: bool) -> bool:
        """Enables or disables a template."""
        tmpl = self.get_template(template_id)
        if tmpl:
            tmpl.is_active = is_active
            return True
        return False


template_registry = TemplateRegistry()
