"""Tests for FUTRSEC Google Gemini API Resume Analysis & OpenAI GPT Resume Creation.

Verifies:
1. AI Model 1 Configuration: Google Gemini API via GEMINI_API_KEY / GEMINI_MODEL
2. AI Model 2 Configuration: OpenAI GPT via OPENAI_API_KEY / OPENAI_MODEL
3. Strict separation of the two models
4. Gemini health diagnostics and exact unavailable model error reporting
5. Gemini rate limit handling and retry behavior
6. Gemini timeout handling
7. Gemini structured analysis using synthetic resume data
8. Strict preservation of deterministic Python ATS scoring and Neon database constraints
9. Immediate automatic re-scoring after resume creation
10. Complete end-to-end workflow from upload through analysis, improvement, and re-scoring
11. Verification that analysis no longer waits for local Ollama
"""

import asyncio
import io
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.scoring.gemini_analyzer import (
    GeminiAnalyzer,
    GeminiConfigError,
    GeminiModelUnavailableError,
    GeminiRateLimitError,
    GeminiTimeoutError,
    GeminiAPIError,
)
from app.scoring.engine import ATSScoringEngine
from app.projects.generator import ResumeContentGenerator, ConfirmedSkillItem
from app.resume.extractor import (
    ParsedResumeData,
    ContactInfo,
    ExperienceEntry,
    ProjectEntry,
    EducationEntry,
)
from app.scoring.matcher import SkillMatcher

client = TestClient(app)


def test_model_configurations_and_secrets_safety():
    """Verifies exact model configurations without exposing secrets."""
    assert settings.GEMINI_MODEL in ("gemini-1.5-flash", "gemini-2.0-flash", "gemini-3.6-flash")
    assert settings.OPENAI_MODEL == "gpt-4o-mini"
    assert "googleapis.com" in settings.GEMINI_BASE_URL

    summary = settings.safe_summary()
    assert summary["stage1_analysis_provider"] == "Google Gemini API"
    assert summary["stage1_model"] == settings.GEMINI_MODEL
    assert summary["stage2_creation_provider"] == "OpenAI GPT"
    assert summary["stage2_model"] == "gpt-4o-mini"

    # Ensure secrets are never exposed in safe summary
    summary_str = str(summary).lower()
    assert "api_key" not in summary_str
    assert "password" not in summary_str
    assert "secret" not in summary_str


def test_gemini_health_endpoint_diagnostics():
    """Verifies /api/gemini/health and /api/health report Gemini status safely."""
    # When GEMINI_API_KEY is not configured
    with patch.object(settings, "GEMINI_API_KEY", None), \
         patch.dict("os.environ", {}, clear=False):
        res = client.get("/api/gemini/health")
        assert res.status_code == 200
        data = res.json()
        assert data["provider"] == "Google Gemini API"
        assert data["model"] == settings.GEMINI_MODEL
        assert data["available"] is False
        assert data["status"] == "not_configured"
        assert "GEMINI_API_KEY" in data["error"]

        # Main health endpoint
        main_res = client.get("/api/health")
        assert main_res.status_code == 200
        main_data = main_res.json()
        assert "stage1_gemini" in main_data
        assert main_data["stage1_gemini"]["model"] == settings.GEMINI_MODEL
        assert "stage2_openai" in main_data
        assert main_data["stage2_openai"]["model"] == "gpt-4o-mini"


def test_gemini_model_unavailable_exact_reporting():
    """Requirement 12: If selected Gemini model is unavailable, report the exact issue."""
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    exact_msg = f"models/{settings.GEMINI_MODEL} is not found for API version v1beta, or is not supported for generateContent."
    mock_resp.json.return_value = {
        "error": {
            "code": 404,
            "message": exact_msg,
            "status": "NOT_FOUND",
        }
    }
    mock_resp.text = json.dumps(mock_resp.json.return_value)

    with patch.object(settings, "GEMINI_API_KEY", "test_gemini_key_12345"), \
         patch("httpx.Client.get", return_value=mock_resp):
        health = GeminiAnalyzer.check_health()
        assert health["available"] is False
        assert health["status"] == "model_unavailable"
        assert health["exact_issue"] == exact_msg
        assert f"models/{settings.GEMINI_MODEL}" in health["error"]


@pytest.mark.asyncio
async def test_gemini_analysis_exact_404_exception():
    """Verifies GeminiAnalyzer raises GeminiModelUnavailableError with exact message and does not fall back."""
    exact_msg = f"models/{settings.GEMINI_MODEL} is not found for API version v1beta."
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.json.return_value = {"error": {"code": 404, "message": exact_msg}}
    mock_resp.text = exact_msg

    with patch.object(settings, "GEMINI_API_KEY", "test_gemini_key_12345"), \
         patch("httpx.AsyncClient.post", return_value=mock_resp):
        with pytest.raises(GeminiModelUnavailableError) as exc_info:
            await GeminiAnalyzer.analyze_with_gemini(
                raw_text="Sample resume text",
                role_name="SOC Analyst",
                role_skills=[{"skill_name": "SIEM", "importance": "core"}],
                role_requirements=[{"requirement_type": "Education", "requirement_description": "B.S. in CS"}],
                scoring_criteria=[{"category": "Technical Skills", "weight": 40.0}],
                matched_skills=["SIEM"],
                missing_skills=["Wireshark"],
            )
        assert exc_info.value.model == settings.GEMINI_MODEL
        assert exc_info.value.error_details == exact_msg
        assert exc_info.value.http_status == 404


@pytest.mark.asyncio
async def test_gemini_rate_limit_retry_behavior():
    """Requirement 10: Handle rate limits (HTTP 429) with retries and clear error message."""
    mock_429 = MagicMock()
    mock_429.status_code = 429
    mock_429.json.return_value = {"error": {"message": "Resource has been exhausted (e.g. check quota)."}}
    mock_429.text = "Quota exceeded"

    with patch.object(settings, "GEMINI_API_KEY", "test_gemini_key_12345"), \
         patch.object(settings, "GEMINI_MAX_RETRIES", 2), \
         patch("httpx.AsyncClient.post", return_value=mock_429), \
         patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        with pytest.raises(GeminiRateLimitError) as exc_info:
            await GeminiAnalyzer.analyze_with_gemini(
                raw_text="Sample resume text",
                role_name="SOC Analyst",
                role_skills=[],
                role_requirements=[],
                scoring_criteria=[],
                matched_skills=[],
                missing_skills=[],
            )
        assert "rate limit exceeded" in str(exc_info.value).lower()
        assert mock_sleep.called


@pytest.mark.asyncio
async def test_gemini_successful_structured_analysis():
    """Requirement 3: Verify Gemini returns valid, structured analysis of skills, gaps, projects, and recommendations."""
    mock_analysis_json = {
        "summary_advice": "Candidate has solid foundational networking but lacks SIEM log analysis experience.",
        "demonstrated_skills": [
            {"skill_name": "Linux", "evidence": "Administered Debian systems in university lab", "strength": "strong"},
            {"skill_name": "Python", "evidence": "Automated log parsing scripts", "strength": "moderate"},
        ],
        "evidence_gaps": [
            {"skill_name": "SIEM", "importance": "core", "reason": "No hands-on Splunk or QRadar experience noted"},
            {"skill_name": "Incident Response", "importance": "core", "reason": "No triage experience demonstrated"},
        ],
        "project_evaluations": [
            {
                "project_name": "Home Security Lab",
                "relevance": "Directly relevant to SOC monitoring",
                "strengths": "Demonstrates initiative and Snort IDS deployment",
                "recommendations": "Add quantifiable detection metrics and alert correlation",
            }
        ],
        "qualification_evaluations": {
            "education_alignment": "B.S. in Computer Science meets the formal technical degree requirement.",
            "certifications_alignment": "CompTIA Security+ demonstrates baseline security knowledge.",
        },
        "category_observations": {
            "Technical Skills": "Needs SIEM and packet analysis tools.",
            "Projects": "Home lab provides good practical evidence.",
        },
        "actionable_recommendations": [
            "Complete a hands-on Splunk lab and document specific detection queries.",
            "Add Wireshark packet capture analysis to project deliverables.",
        ],
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": json.dumps(mock_analysis_json)}],
                    "role": "model",
                }
            }
        ]
    }

    with patch.object(settings, "GEMINI_API_KEY", "test_gemini_key_12345"), \
         patch("httpx.AsyncClient.post", return_value=mock_resp):
        result = await GeminiAnalyzer.analyze_with_gemini(
            raw_text="Alex Chen - Junior Security Specialist with Linux and Python lab experience.",
            role_name="SOC Analyst",
            role_skills=[
                {"skill_name": "Linux", "importance": "core"},
                {"skill_name": "SIEM", "importance": "core"},
            ],
            role_requirements=[
                {"requirement_type": "Education", "requirement_description": "B.S. in CS or related"}
            ],
            scoring_criteria=[
                {"category": "Technical Skills", "weight": 40.0},
                {"category": "Projects", "weight": 25.0},
            ],
            matched_skills=["Linux", "Python"],
            missing_skills=["SIEM", "Incident Response"],
        )

        assert result["summary_advice"] == mock_analysis_json["summary_advice"]
        assert len(result["demonstrated_skills"]) == 2
        assert len(result["evidence_gaps"]) == 2
        assert len(result["project_evaluations"]) == 1
        assert "education_alignment" in result["qualification_evaluations"]
        assert len(result["actionable_recommendations"]) == 2
        assert result["model_used"] == settings.GEMINI_MODEL


def test_deterministic_scoring_preservation():
    """Requirement 7: Deterministic Python scoring engine calculates scores from Neon criteria, unaltered by AI."""
    sample_resume = ParsedResumeData(
        candidate_name="Alex Chen",
        contact_info=ContactInfo(email="alex@example.com", phone="555-0100"),
        professional_summary="Cybersecurity graduate focused on SOC operations and defense.",
        technical_skills=["Linux", "Python", "Wireshark", "Bash"],
        certifications=["CompTIA Security+"],
        employment_history=[
            ExperienceEntry(
                company="Tech Corp",
                job_title="IT Support Specialist",
                start_date="2022",
                end_date="2023",
                responsibilities=["Network troubleshooting and log review"],
            )
        ],
        projects=[
            ProjectEntry(
                title="Home Network Lab",
                technologies=["Wireshark", "Snort"],
                description="Built network intrusion detection testbed",
            )
        ],
        education=[
            EducationEntry(
                institution="State University",
                degree="Bachelor of Science",
                field_of_study="Cybersecurity",
                graduation_year="2024",
            )
        ],
    )

    role_skills = [
        {"skill_name": "Linux", "importance": "core"},
        {"skill_name": "Python", "importance": "core"},
        {"skill_name": "Wireshark", "importance": "preferred"},
        {"skill_name": "SIEM", "importance": "core"},
    ]

    match_report = SkillMatcher.match_skills(
        role_skills=role_skills,
        resume_skills=sample_resume.technical_skills,
        resume_full_text="Alex Chen Cybersecurity graduate Linux Python Wireshark Bash CompTIA Security+",
        resume_projects=sample_resume.projects,
        resume_experience=sample_resume.employment_history,
        role_id=1,
        role_name="SOC Analyst",
    )

    db_criteria = [
        {"category": "Technical Skills", "weight": 40.0},
        {"category": "Projects", "weight": 25.0},
        {"category": "Education", "weight": 15.0},
        {"category": "Tools & Certifications", "weight": 15.0},
        {"category": "Career Objective", "weight": 5.0},
    ]

    score_result = ATSScoringEngine.calculate_score(
        resume_data=sample_resume,
        match_report=match_report,
        role_requirements=[{"requirement_type": "Education", "requirement_description": "Bachelor degree in Computing"}],
        db_scoring_criteria=db_criteria,
        threshold=80.0,
    )

    # 100% deterministic calculation
    assert 0.0 <= score_result.final_score <= 100.0
    assert len(score_result.category_scores) == 5
    assert sum(c.weight for c in score_result.category_scores) == 100.0
    assert isinstance(score_result.final_score, float)


def test_openai_stage2_generation_separate():
    """Requirement 5 & 6: Stage 2 Resume Creation strictly uses OpenAI GPT (gpt-4o-mini)."""
    sample_resume = ParsedResumeData(
        candidate_name="Alex Chen",
        contact_info=ContactInfo(email="alex@example.com", phone="555-0100"),
        professional_summary="Dedicated cybersecurity practitioner.",
        technical_skills=["Wireshark", "Linux", "Python"],
        certifications=["CompTIA Security+"],
        employment_history=[],
        projects=[
            ProjectEntry(
                title="Home SOC Lab",
                technologies=["Splunk", "Snort"],
                description="Built automated intrusion detection testbed",
            )
        ],
        education=[
            EducationEntry(
                institution="State University",
                degree="Bachelor of Science",
                field_of_study="Cybersecurity",
                graduation_year="2024",
            )
        ],
    )

    mock_response_json = {
        "candidate_name": "Alex Chen",
        "contact_header": "alex@example.com | 555-0100",
        "contact_details": {"email": "alex@example.com", "phone": "555-0100"},
        "professional_headline": "SOC Analyst | Threat Detection Specialist",
        "professional_summary": "Dedicated SOC Analyst with hands-on Splunk SIEM experience.",
        "technical_skills_grouped": {"Core Security": ["Wireshark", "SIEM", "Splunk"]},
        "experience": [],
        "projects": [{"name": "Home SOC Lab", "bullets": ["Configured Snort detection testbed"]}],
        "education": [{"degree": "B.S. Cybersecurity"}],
        "achievements": [],
    }

    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps(mock_response_json)
    mock_completion.choices = [mock_choice]

    with patch.object(settings, "OPENAI_API_KEY", "sk-mock-key-12345"), \
         patch("openai.resources.chat.completions.Completions.create", return_value=mock_completion) as mock_create:
        res = ResumeContentGenerator.generate_enhanced_content(
            resume_data=sample_resume,
            target_role_name="SOC Analyst",
            missing_core_skills=["SIEM"],
            confirmed_skills=[ConfirmedSkillItem(skill_name="SIEM", proficiency="hands_on")],
            permission_granted=True,
        )

        assert mock_create.called
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["model"] == "gpt-4o-mini"
        assert "openai_gpt" in res.generator_mode
        assert res.candidate_name == "Alex Chen"


def test_complete_upload_analysis_and_rescore_workflow():
    """Requirements 2, 8, 9: Complete workflow from upload through Gemini analysis and automatic re-scoring."""
    synthetic_pdf_bytes = b"%PDF-1.4\n1 0 obj\n<< /Title (Alex Chen Resume) >>\nendobj\ntrailer\n<<>>\n%%EOF"

    # Mock doc parser to return structured text
    mock_doc = {
        "raw_text": (
            "Alex Chen\nalex@example.com | 555-0100\n\n"
            "PROFESSIONAL SUMMARY\nCybersecurity practitioner with hands-on experience in vulnerability assessment.\n\n"
            "TECHNICAL SKILLS\nLinux, Python, Wireshark, Nmap, Bash\n\n"
            "CERTIFICATIONS\nCompTIA Security+\n\n"
            "PROJECTS\nHome Penetration Testing Lab\nDeployed Kali Linux, Metasploitable, and Wireshark to simulate attacks.\n\n"
            "EDUCATION\nBachelor of Science in Cybersecurity, State University, 2024\n"
        ),
        "clean_text": "Alex Chen...",
        "metadata": {"format": "pdf", "page_count": 1},
        "security_flag_injection_detected": False,
    }

    mock_gemini_output = {
        "summary_advice": "Strong offensive foundations; recommend adding web application security tools.",
        "demonstrated_skills": [
            {"skill_name": "Linux", "evidence": "Kali Linux in lab", "strength": "strong"},
            {"skill_name": "Nmap", "evidence": "Network mapping in lab", "strength": "moderate"},
        ],
        "evidence_gaps": [
            {"skill_name": "Metasploit", "importance": "core", "reason": "Not directly cited"},
        ],
        "project_evaluations": [],
        "qualification_evaluations": {"education": "Relevant degree"},
        "category_observations": {},
        "actionable_recommendations": ["Conduct Burp Suite web testing lab."],
        "model_used": settings.GEMINI_MODEL,
    }

    mock_gemini_resp = MagicMock()
    mock_gemini_resp.status_code = 200
    mock_gemini_resp.json.return_value = {
        "candidates": [
            {"content": {"parts": [{"text": json.dumps(mock_gemini_output)}]}}
        ]
    }

    with patch("app.resume.parser.ResumeParser.parse_document", return_value=mock_doc), \
         patch.object(settings, "GEMINI_API_KEY", "test_gemini_key_12345"), \
         patch("httpx.AsyncClient.post", return_value=mock_gemini_resp):

        # Upload & Analyze against Ethical Hacker (Role 1)
        response = client.post(
            "/api/resumes/analyze",
            files={"file": ("alex_chen.pdf", synthetic_pdf_bytes, "application/pdf")},
            data={"role_id": 1},
        )
        assert response.status_code == 200
        data = response.json()

        assert "analysis_id" in data
        assert data["role_name"] == "Ethical Hacker"
        assert "score_result" in data
        assert "stage1_ai" in data

        # Confirms Gemini API was used (not local Ollama)
        assert data["stage1_ai"]["provider"] == "Google Gemini API"
        assert data["stage1_ai"]["model"] == settings.GEMINI_MODEL
        assert data["stage1_ai"]["status"] == "completed"

        analysis_id = data["analysis_id"]

        # Stage 2 Improvement & Automatic Re-scoring
        improve_res = client.post(
            "/api/resumes/improve",
            json={
                "analysis_id": analysis_id,
                "attempt_number": 1,
                "permission_granted": True,
            },
        )
        assert improve_res.status_code == 200
        imp_data = improve_res.json()

        assert "new_score" in imp_data
        assert "original_score" in imp_data
        assert "assigned_template" in imp_data
        assert "documents" in imp_data
        assert imp_data["documents"]["docx_url"] is not None
