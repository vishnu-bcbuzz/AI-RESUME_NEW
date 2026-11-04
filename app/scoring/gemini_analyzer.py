"""Google Gemini API Stage 1 Resume Analysis Module for FUTRSEC.

Performs hosted inference via Google Gemini API (model: gemini-3.6-flash).
Analyzes candidate resumes against cybersecurity job role requirements retrieved from Neon PostgreSQL.
Identifies demonstrated skills, evidence gaps, evaluates projects and qualifications,
and produces role-specific improvement recommendations.

Strictly preserves the deterministic Python ATS scoring engine.
Does not fall back to Ollama or other models silently.
Reports exact error messages if the selected model is unavailable for the API key.
"""

import asyncio
import json
import logging
import re
import time
from typing import Dict, Any, List, Optional
import httpx
from pydantic import BaseModel, Field

from app.config import settings

logger = logging.getLogger("futrsec.gemini")


class GeminiConfigError(Exception):
    """Raised when GEMINI_API_KEY is missing or invalid in configuration."""
    pass


class GeminiModelUnavailableError(Exception):
    """Raised when the selected Gemini model is unavailable for the API key."""

    def __init__(self, model: str, error_details: str, http_status: int = 404):
        self.model = model
        self.error_details = error_details
        self.http_status = http_status
        super().__init__(
            f"Google Gemini model '{model}' is unavailable for this API key "
            f"(HTTP {http_status}): {error_details}"
        )


class GeminiRateLimitError(Exception):
    """Raised when Gemini API rate limit or quota is exceeded."""

    def __init__(self, model: str, error_details: str, retry_after: Optional[float] = None):
        self.model = model
        self.error_details = error_details
        self.retry_after = retry_after
        super().__init__(
            f"Google Gemini rate limit exceeded for model '{model}': {error_details}"
        )


class GeminiTimeoutError(Exception):
    """Raised when Gemini API request times out."""
    pass


class GeminiAPIError(Exception):
    """Raised for unexpected Gemini API responses."""

    def __init__(self, status_code: int, message: str, details: Optional[Dict[str, Any]] = None):
        self.status_code = status_code
        self.details = details or {}
        super().__init__(f"Gemini API error (HTTP {status_code}): {message}")


class GeminiAnalysisResult(BaseModel):
    """Structured response model for Gemini Stage 1 resume evaluation."""
    summary_advice: str
    demonstrated_skills: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_gaps: List[Dict[str, Any]] = Field(default_factory=list)
    project_evaluations: List[Dict[str, Any]] = Field(default_factory=list)
    qualification_evaluations: Dict[str, Any] = Field(default_factory=dict)
    category_observations: Dict[str, str] = Field(default_factory=dict)
    actionable_recommendations: List[str] = Field(default_factory=list)
    model_used: str = "gemini-3.6-flash"
    execution_time_sec: float = 0.0


class GeminiAnalyzer:
    """Handles hosted inference with Google Gemini API for Stage 1 resume analysis."""

    @classmethod
    def check_health(cls) -> Dict[str, Any]:
        """Diagnostic check for Google Gemini API credentials and model availability.
        
        Never logs or exposes secret keys.
        Reports exact issue if the configured model is unavailable.
        """
        api_key = settings.effective_gemini_key
        model = settings.GEMINI_MODEL
        base_url = settings.GEMINI_BASE_URL.rstrip("/")

        if not api_key:
            return {
                "available": False,
                "configured": False,
                "provider": "Google Gemini API",
                "model": model,
                "status": "not_configured",
                "error": "GEMINI_API_KEY environment variable is not configured.",
                "troubleshooting": (
                    "Add GEMINI_API_KEY to your .env file or environment variables "
                    "to enable Google Gemini resume analysis."
                ),
            }

        endpoint = f"{base_url}/models/{model}"
        try:
            with httpx.Client(timeout=8.0) as client:
                resp = client.get(f"{endpoint}?key={api_key}")
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "available": True,
                        "configured": True,
                        "provider": "Google Gemini API",
                        "model": model,
                        "status": "online",
                        "display_name": data.get("displayName", model),
                        "supported_generation_methods": data.get("supportedGenerationMethods", []),
                        "troubleshooting": None,
                    }

                err_body = {}
                try:
                    err_body = resp.json()
                except Exception:
                    pass

                exact_error = err_body.get("error", {}).get("message") or resp.text[:300]

                if resp.status_code == 404:
                    return {
                        "available": False,
                        "configured": True,
                        "provider": "Google Gemini API",
                        "model": model,
                        "status": "model_unavailable",
                        "http_status": 404,
                        "error": f"Selected model '{model}' is not available for this API key: {exact_error}",
                        "exact_issue": exact_error,
                        "troubleshooting": (
                            f"Model '{model}' was not found or is unsupported for generateContent on this API key. "
                            f"Exact error from Gemini API: {exact_error}"
                        ),
                    }
                elif resp.status_code in (400, 401, 403):
                    return {
                        "available": False,
                        "configured": True,
                        "provider": "Google Gemini API",
                        "model": model,
                        "status": "auth_error",
                        "http_status": resp.status_code,
                        "error": f"Gemini API authentication failed ({resp.status_code}): {exact_error}",
                        "exact_issue": exact_error,
                        "troubleshooting": (
                            "Please verify that GEMINI_API_KEY in .env is valid and has "
                            "the Generative Language API enabled in Google Cloud Console."
                        ),
                    }
                elif resp.status_code == 429:
                    return {
                        "available": False,
                        "configured": True,
                        "provider": "Google Gemini API",
                        "model": model,
                        "status": "rate_limited",
                        "http_status": 429,
                        "error": f"Gemini API rate limit exceeded: {exact_error}",
                        "exact_issue": exact_error,
                        "troubleshooting": "Google Gemini API quota reached. Please wait or check your tier quotas.",
                    }
                else:
                    return {
                        "available": False,
                        "configured": True,
                        "provider": "Google Gemini API",
                        "model": model,
                        "status": f"http_{resp.status_code}",
                        "http_status": resp.status_code,
                        "error": f"Gemini API responded with status {resp.status_code}: {exact_error}",
                        "exact_issue": exact_error,
                        "troubleshooting": "Check Gemini API service status or network connectivity.",
                    }
        except httpx.TimeoutException:
            return {
                "available": False,
                "configured": True,
                "provider": "Google Gemini API",
                "model": model,
                "status": "timeout",
                "error": f"Health check timed out contacting Gemini API at {base_url}.",
                "troubleshooting": "Ensure network connectivity to Google Gemini endpoints.",
            }
        except Exception as exc:
            logger.warning("Gemini API health check failed with exception: %s", exc)
            return {
                "available": False,
                "configured": True,
                "provider": "Google Gemini API",
                "model": model,
                "status": "connection_error",
                "error": str(exc),
                "troubleshooting": f"Could not connect to Google Gemini API: {exc}",
            }

    @classmethod
    async def analyze_with_gemini(
        cls,
        raw_text: str,
        role_name: str,
        role_skills: List[Dict[str, Any]],
        role_requirements: List[Dict[str, Any]],
        scoring_criteria: List[Dict[str, Any]],
        matched_skills: List[str],
        missing_skills: List[str],
        resume_data: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Analyzes a candidate resume against target role requirements using Google Gemini API.
        
        Args:
            raw_text: Raw parsed resume text.
            role_name: Target cybersecurity role name.
            role_skills: Skills associated with role from Neon DB.
            role_requirements: Requirements associated with role from Neon DB.
            scoring_criteria: Scoring weights from Neon DB.
            matched_skills: Skills matched by deterministic parser.
            missing_skills: Skills unmatched by deterministic parser.
            resume_data: Structured ParsedResumeData if available.

        Returns:
            Dict[str, Any] with structured analysis, demonstrated skills, evidence gaps,
            project evaluations, qualification assessments, and recommendations.

        Raises:
            GeminiConfigError: When GEMINI_API_KEY is not configured.
            GeminiModelUnavailableError: When model is unavailable (HTTP 404).
            GeminiRateLimitError: When rate limit is exceeded after retries (HTTP 429).
            GeminiTimeoutError: When requests repeatedly time out.
            GeminiAPIError: On other API errors.
        """
        api_key = settings.effective_gemini_key
        model = settings.GEMINI_MODEL
        base_url = settings.GEMINI_BASE_URL.rstrip("/")
        timeout_sec = getattr(settings, "GEMINI_TIMEOUT_SEC", 60.0)
        max_retries = getattr(settings, "GEMINI_MAX_RETRIES", 3)

        if not api_key:
            raise GeminiConfigError(
                "GEMINI_API_KEY is not configured. Please supply a valid Google Gemini API key in .env."
            )

        system_instruction = (
            "You are FUTRSEC AI Stage 1 Resume Evaluator, powered by Google Gemini API. "
            "Your task is to analyze candidate cybersecurity resumes against authoritative job role "
            "requirements from our database.\n\n"
            "STRICT FACTUAL ACCURACY RULES:\n"
            "1. NEVER invent, assume, or hallucinate skills, degrees, certifications, companies, or metrics "
            "not explicitly stated in the candidate's resume.\n"
            "2. Identify genuinely demonstrated skills and extract exact supporting evidence snippets.\n"
            "3. Identify evidence gaps (missing core and preferred skills needed for the role).\n"
            "4. Rigorously evaluate candidate technical projects for cybersecurity depth and relevance.\n"
            "5. Evaluate qualifications (degrees, fields of study, industry certifications) against requirements.\n"
            "6. Formulate role-specific, actionable improvement recommendations prioritized by importance.\n"
            "7. Return strictly valid JSON matching the exact schema."
        )

        user_payload = {
            "target_role": role_name,
            "autoritative_role_requirements": [
                {
                    "type": r.get("requirement_type", "General"),
                    "description": r.get("requirement_description", ""),
                    "importance": r.get("importance", "mandatory"),
                }
                for r in role_requirements[:15]
            ],
            "role_skills": [
                {
                    "skill_name": s.get("skill_name"),
                    "importance": s.get("importance", "core"),
                }
                for s in role_skills[:30]
            ],
            "scoring_weights": [
                {"category": c.get("category"), "weight": c.get("weight")}
                for c in scoring_criteria
            ],
            "deterministic_match_summary": {
                "matched_skills": matched_skills,
                "missing_skills": missing_skills[:20],
            },
            "candidate_resume": {
                "candidate_name": getattr(resume_data, "candidate_name", None) if resume_data else None,
                "professional_summary": getattr(resume_data, "professional_summary", "") if resume_data else "",
                "technical_skills": getattr(resume_data, "technical_skills", []) if resume_data else [],
                "certifications": getattr(resume_data, "certifications", []) if resume_data else [],
                "projects": [
                    {
                        "title": getattr(p, "title", ""),
                        "technologies": getattr(p, "technologies", []),
                        "description": getattr(p, "description", ""),
                    }
                    for p in getattr(resume_data, "projects", [])
                ] if resume_data else [],
                "education": [
                    {
                        "degree": getattr(ed, "degree", ""),
                        "field": getattr(ed, "field_of_study", ""),
                        "institution": getattr(ed, "institution", ""),
                    }
                    for ed in getattr(resume_data, "education", [])
                ] if resume_data else [],
                "raw_text_excerpt": raw_text[:8000],
            },
        }

        request_body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": (
                                f"Analyze this resume against the '{role_name}' cybersecurity requirements. "
                                f"Return strictly valid JSON with keys: "
                                f"'summary_advice', 'demonstrated_skills', 'evidence_gaps', "
                                f"'project_evaluations', 'qualification_evaluations', "
                                f"'category_observations', 'actionable_recommendations'.\n\n"
                                f"Context Payload:\n{json.dumps(user_payload)}"
                            )
                        }
                    ],
                }
            ],
            "systemInstruction": {
                "parts": [{"text": system_instruction}]
            },
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
            },
        }

        endpoint_url = f"{base_url}/models/{model}:generateContent?key={api_key}"
        start_time = time.time()
        timeout = httpx.Timeout(timeout_sec, connect=10.0)

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    "Executing Stage 1 Gemini resume analysis (model: %s, attempt %d/%d)...",
                    model, attempt, max_retries
                )
                async with httpx.AsyncClient(timeout=timeout) as client:
                    resp = await client.post(endpoint_url, json=request_body)

                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if not candidates:
                            raise GeminiAPIError(200, "Gemini API returned no response candidates.")

                        content_parts = candidates[0].get("content", {}).get("parts", [])
                        if not content_parts:
                            raise GeminiAPIError(200, "Gemini API response candidate contained no text parts.")

                        raw_content = content_parts[0].get("text", "{}")
                        from app.ai.json_utils import safe_json_loads
                        parsed = safe_json_loads(raw_content, default={})
                        if not isinstance(parsed, dict):
                            parsed = {}

                        exec_time = round(time.time() - start_time, 2)
                        logger.info("Gemini resume analysis completed in %.2fs using %s", exec_time, model)

                        # Standardize and guarantee top-level keys
                        return {
                            "summary_advice": parsed.get(
                                "summary_advice",
                                f"Comprehensive resume evaluation against {role_name} cybersecurity requirements."
                            ),
                            "demonstrated_skills": parsed.get("demonstrated_skills") or [
                                {"skill_name": s, "evidence": "Detected in resume"} for s in matched_skills
                            ],
                            "evidence_gaps": parsed.get("evidence_gaps") or [
                                {"skill_name": s, "importance": "core"} for s in missing_skills[:10]
                            ],
                            "project_evaluations": parsed.get("project_evaluations", []),
                            "qualification_evaluations": parsed.get("qualification_evaluations", {}),
                            "category_observations": parsed.get("category_observations", {}),
                            "actionable_recommendations": parsed.get("actionable_recommendations", []),
                            "model_used": model,
                            "execution_time_sec": exec_time,
                        }

                    # Non-200 handling
                    err_json = {}
                    try:
                        err_json = resp.json()
                    except Exception:
                        pass
                    err_msg = err_json.get("error", {}).get("message") or resp.text[:400]

                    # 404: Model not found / unavailable -> DO NOT retry, report exact issue immediately
                    if resp.status_code == 404:
                        logger.error(
                            "Gemini model '%s' is unavailable (HTTP 404): %s",
                            model, err_msg
                        )
                        raise GeminiModelUnavailableError(
                            model=model,
                            error_details=err_msg,
                            http_status=404,
                        )

                    # 429: Rate limit / quota exceeded -> Retry with exponential backoff
                    if resp.status_code == 429:
                        if attempt < max_retries:
                            backoff = min(12.0, 1.5 * (2 ** (attempt - 1)))
                            logger.warning(
                                "Gemini rate limit (429) hit. Retrying in %.1fs (attempt %d/%d)...",
                                backoff, attempt, max_retries
                            )
                            await asyncio.sleep(backoff)
                            continue
                        raise GeminiRateLimitError(
                            model=model,
                            error_details=err_msg,
                        )

                    # 503 / 500: Server transient error -> Retry
                    if resp.status_code in (500, 503) and attempt < max_retries:
                        backoff = 2.0 * attempt
                        logger.warning(
                            "Gemini server error (%d). Retrying in %.1fs...",
                            resp.status_code, backoff
                        )
                        await asyncio.sleep(backoff)
                        continue

                    # Other HTTP error (e.g. 400, 401, 403) -> DO NOT retry
                    raise GeminiAPIError(resp.status_code, err_msg, details=err_json)

            except httpx.TimeoutException:
                if attempt < max_retries:
                    logger.warning(
                        "Gemini request timed out after %.1fs. Retrying (attempt %d/%d)...",
                        timeout_sec, attempt, max_retries
                    )
                    await asyncio.sleep(2.0)
                    continue
                raise GeminiTimeoutError(
                    f"Google Gemini API request timed out after {timeout_sec}s for model '{model}'."
                )

        raise GeminiAPIError(500, "Gemini resume analysis failed after maximum retries.")
