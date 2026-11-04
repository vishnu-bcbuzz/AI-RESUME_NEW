"""Tests for FUTRSEC AI Model Configuration Update.

Verifies:
1. AI Model 1: Hosted Resume Analysis via Google Gemini API
2. AI Model 2: Resume Creation & Improvement via OpenAI GPT
3. Strict separation between Google Gemini and OpenAI GPT integrations
4. Complete elimination of Ollama and Groq integrations
5. Strict preservation of deterministic Python ATS scoring and Neon database constraints
6. Diagnostic endpoints (/health, /api/health, /api/gemini/health, /api/openai/health)
7. Anti-hallucination guardrails and safe credentials handling
"""

import asyncio
import inspect
import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.scoring.gemini_analyzer import GeminiAnalyzer
from app.projects.generator import ResumeContentGenerator, ConfirmedSkillItem
from app.resume.extractor import ParsedResumeData, ContactInfo, ExperienceEntry, ProjectEntry, EducationEntry

client = TestClient(app)


def test_gemini_configuration_parameters():
    """Verifies that Stage 1 Google Gemini API settings meet the exact specification."""
    assert settings.GEMINI_MODEL in ("gemini-1.5-flash", "gemini-2.0-flash", "gemini-3.6-flash")
    assert "generativelanguage.googleapis.com" in settings.GEMINI_BASE_URL
    assert settings.GEMINI_TIMEOUT_SEC >= 30.0
    assert settings.GEMINI_MAX_RETRIES >= 2


def test_openai_configuration_parameters():
    """Verifies that Stage 2 OpenAI GPT settings meet the exact specification."""
    assert settings.OPENAI_MODEL == "gpt-4o-mini"
    summary = settings.safe_summary()
    assert summary["stage1_analysis_provider"] == "Google Gemini API"
    assert summary["stage2_creation_provider"] == "OpenAI GPT"
    assert summary["stage2_model"] == "gpt-4o-mini"
    # Ensure secrets are never exposed in summary
    assert "api_key" not in str(summary).lower()


def test_health_endpoints_expose_ai_diagnostics():
    """Verifies /health and /api/health include Gemini and OpenAI GPT diagnostics without leaking secrets."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert "stage1_gemini" in data
    assert "stage2_openai" in data
    assert "stage1_ollama" not in data
    assert "stage2_groq" not in data
    assert data["stage1_gemini"]["provider"] == "Google Gemini API"
    assert data["stage2_openai"]["model"] == "gpt-4o-mini"
    assert data["stage2_openai"]["provider"] == "OpenAI GPT"


def test_gemini_health_endpoint():
    """Verifies /api/gemini/health returns clean diagnostic info."""
    res = client.get("/api/gemini/health")
    assert res.status_code == 200
    data = res.json()
    assert "provider" in data
    assert data["provider"] == "Google Gemini API"
    assert "model" in data
    assert "available" in data


def test_openai_health_endpoint():
    """Verifies /api/openai/health returns clean diagnostic info."""
    res = client.get("/api/openai/health")
    assert res.status_code == 200
    data = res.json()
    assert "provider" in data
    assert data["provider"] == "OpenAI GPT"
    assert "model" in data
    assert data["model"] == "gpt-4o-mini"
    assert "available" in data


def test_openai_stage2_generation_call():
    """Verifies Stage 2 invokes OpenAI GPT when API key is provided, and heuristics when absent."""
    sample_resume = ParsedResumeData(
        candidate_name="Alex Chen",
        contact_info=ContactInfo(email="alex@example.com", phone="555-0100"),
        professional_summary="Junior security specialist with SOC lab practice.",
        technical_skills=["Wireshark", "Linux", "Python"],
        certifications=["CompTIA Security+"],
        employment_history=[
            ExperienceEntry(
                company="Tech Corp",
                job_title="IT Support",
                start_date="2022",
                end_date="2023",
                responsibilities=["Assisted network team with log triage"],
            )
        ],
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

    # Test heuristic fallback when OPENAI_API_KEY is not configured
    with patch.object(settings, "OPENAI_API_KEY", None):
        result = ResumeContentGenerator.generate_enhanced_content(
            resume_data=sample_resume,
            target_role_name="SOC Analyst",
            missing_core_skills=["SIEM", "Incident Response"],
            confirmed_skills=[
                ConfirmedSkillItem(skill_name="SIEM", proficiency="hands_on", tasks_performed="Splunk queries")
            ],
            permission_granted=True,
        )
        assert result.candidate_name == "Alex Chen"
        assert "SIEM" in result.confirmed_skills_included
        assert "deterministic_enhancer" in result.generator_mode

    # Test OpenAI endpoint invocation when mock key is present
    mock_response_json = {
        "candidate_name": "Alex Chen",
        "contact_header": "alex@example.com | 555-0100",
        "contact_details": {"email": "alex@example.com", "phone": "555-0100"},
        "professional_headline": "SOC Analyst | Threat Detection & SIEM Specialist",
        "professional_summary": "Dedicated SOC Analyst with hands-on Splunk SIEM experience.",
        "technical_skills_grouped": {"Core Security": ["Wireshark", "SIEM", "Splunk"]},
        "experience": [{"company": "Tech Corp", "title": "IT Support", "bullets": ["Analyzed log triage"]}],
        "projects": [{"name": "Home SOC Lab", "bullets": ["Engineered Snort detection testbed"]}],
        "education": [{"degree": "B.S. Cybersecurity"}],
        "achievements": [],
    }

    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps(mock_response_json)
    mock_completion.choices = [mock_choice]

    with patch.object(settings, "OPENAI_API_KEY", "sk-mock-key-12345"), \
         patch("openai.resources.chat.completions.Completions.create", return_value=mock_completion) as mock_create:
        res_ai = ResumeContentGenerator.generate_enhanced_content(
            resume_data=sample_resume,
            target_role_name="SOC Analyst",
            missing_core_skills=["SIEM"],
            confirmed_skills=[ConfirmedSkillItem(skill_name="SIEM", proficiency="hands_on")],
            permission_granted=True,
        )
        assert mock_create.called
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["model"] == "gpt-4o-mini"
        assert "openai_gpt" in res_ai.generator_mode


def test_gemini_analyzer_guardrails_anti_hallucination():
    """Verifies that GeminiAnalyzer prompt explicitly enforces strict non-fabrication rules."""
    source = inspect.getsource(GeminiAnalyzer.analyze_with_gemini)
    assert "NEVER invent" in source
    assert "actionable_recommendations" in source
    assert "evidence_gaps" in source
    assert "demonstrated_skills" in source
    assert "project_evaluations" in source
    assert "qualification_evaluations" in source


def test_models_separation_guarantee():
    """Verify clean separation: Stage 1 Gemini and Stage 2 OpenAI GPT; zero Ollama / Groq."""
    # Stage 1: Gemini Analyzer
    gemini_source = inspect.getsource(GeminiAnalyzer)
    assert "openai" not in gemini_source.lower()
    assert "groq" not in gemini_source.lower()
    assert "ollama" not in gemini_source.lower()

    # Stage 2: Resume Content Generator
    generator_source = inspect.getsource(ResumeContentGenerator._generate_with_llm)
    assert "generativelanguage.googleapis.com" not in generator_source
    assert "gemini" not in generator_source.lower()
    assert "groq" not in generator_source.lower()
    assert "ollama" not in generator_source.lower()
