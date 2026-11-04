# FUTRSEC AI Architecture: Google Gemini API & OpenAI GPT Setup

## Overview

The FUTRSEC Resume Engine operates on a high-performance, two-stage cloud AI architecture combining Google Gemini API for rapid, intelligent resume analysis and OpenAI GPT for candidate-approved resume generation:

```
[Candidate Resume Upload]
           │
           ▼
[Document Parser & Regex Extractor]
           │
           ▼
[Neon PostgreSQL Database] ──► (Roles, Skills, Weighted Scoring Criteria)
           │
           ▼
[Deterministic ATS Scoring Engine] ──► (Strict mathematical evaluation, 0-100)
           │
           ▼
[AI Model 1: Google Gemini API Analysis]
  Provider: Google Gemini API
  Model: gemini-1.5-flash
  API Key: GEMINI_API_KEY
  Model Env: GEMINI_MODEL
  Responsibilities: Identify demonstrated skills, evidence gaps, project evaluations,
                   qualification evaluations, and role-specific recommendations
           │
           ▼
[Candidate Approval Studio UI]
  Candidate confirms/rejects skills, clarifies experience, reviews improvement plan
           │
           ▼
[AI Model 2: OpenAI GPT Resume Creation]
  Provider: OpenAI GPT
  Model: gpt-4o-mini
  API Key: OPENAI_API_KEY
  Model Env: OPENAI_MODEL
  Responsibilities: Full ATS resume rewriting with strict anti-hallucination guardrails
           │
           ▼
[Round Robin Template Scheduler] ──► [DOCX / PDF Document Renderer]
           │
           ▼
[Automatic Re-Scoring (Threshold 80.0/100)]
```

---

## AI Model 1 — Resume Analysis (Google Gemini API)

* **Provider**: Google Gemini API
* **Model ID**: `gemini-1.5-flash`
* **API Key Env Var**: `GEMINI_API_KEY`
* **Model Env Var**: `GEMINI_MODEL`
* **Default Base URL**: `https://generativelanguage.googleapis.com/v1beta`
* **Timeout**: `60.0s` (`GEMINI_TIMEOUT_SEC`)

### Responsibilities:
1. Parse and evaluate candidate resume text against target role specifications.
2. Identify genuinely demonstrated skills with exact supporting evidence snippets.
3. Identify evidence gaps (missing core and preferred skills needed for the role).
4. Evaluate technical projects for cybersecurity depth and relevance.
5. Evaluate qualifications (education alignment and industry certifications).
6. Formulate role-specific, actionable improvement recommendations prioritized by importance.
7. Return strictly valid structured JSON without non-deterministic side effects.
8. **Preserve Deterministic ATS Scoring**: Numerical score is calculated 100% deterministically by Python using Neon DB criteria.

### Reliability & Error Handling:
* **Unavailable Model Detection**: If the selected model is unavailable or not supported for the API key, the exact HTTP 404 error from Google API is reported without silently falling back.
* **Rate Limits (HTTP 429)**: Handled with exponential backoff retries (`GEMINI_MAX_RETRIES=3`).
* **Timeouts & Connection Failures**: Clearly reported with diagnostic guidance.
* **No Silent Fallback**: The system does not fall back to legacy local services silently.

---

## AI Model 2 — Resume Creation (OpenAI GPT)

* **Provider**: OpenAI GPT
* **Model ID**: `gpt-4o-mini`
* **API Key Env Var**: `OPENAI_API_KEY`
* **Model Env Var**: `OPENAI_MODEL`
* **Timeout**: `60.0s` (`OPENAI_TIMEOUT_SEC`)

### Responsibilities:
1. Generate ATS-optimized resume phrasing for selected cybersecurity roles.
2. Polish professional summary, technical competencies, and project descriptions.
3. **Strict Truthfulness Constraint**: Only incorporate existing qualifications and candidate-confirmed skills. Never fabricate credentials, employment dates, certifications, metrics, or achievements.
4. **Candidate-Approved Projects**: Preserve and prominently feature verified completed and in-progress projects.
5. If `OPENAI_API_KEY` is unset or OpenAI is unreachable, the system automatically falls back to the deterministic rule-based resume enhancer without failing the user request.

---

## Strict Separation of AI Integrations

* **AI Model 1 (`app/scoring/gemini_analyzer.py`)**: Used exclusively for resume evaluation, gap identification, project appraisal, and improvement planning.
* **AI Model 2 (`app/projects/generator.py`)**: Used exclusively for full resume rewriting and content generation.
* The two integrations maintain independent clients, endpoints, API keys, error handlers, and life cycles.

---

## Health & Diagnostics Endpoints

* `GET /health` and `GET /api/health`: Comprehensive system health report including Neon DB connectivity, Gemini API status (`stage1_gemini`), and OpenAI GPT status (`stage2_openai`).
* `GET /api/gemini/health`: Real-time diagnostic check for Google Gemini API credentials and model availability.
* `GET /api/openai/health`: Real-time diagnostic check for OpenAI GPT API credentials and model readiness.
* **Safe Credentials Guarantee**: All secrets, API keys, and connection strings are masked from public responses and logs.
