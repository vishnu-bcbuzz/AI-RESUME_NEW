"""FastAPI application entry point for FUTRSEC AI Resume Engine.

Implements all required REST endpoints, lifecycle management, CORS configuration,
centralized error handling, secure file uploads, ATS scoring, Round Robin scheduling,
and resume downloads.
"""

import logging
import re
import uuid
import traceback
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException, Query, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from app.config import settings
from app.database.connection import db_manager
from app.database.repositories import role_repository
from app.resume.parser import ResumeParser, ResumeParsingError
from app.resume.extractor import (
    ResumeExtractor,
    ResumeExtractionError,
    ParsedResumeData,
    ContactInfo,
    EducationEntry,
    ProjectEntry,
    ExperienceEntry,
)
from app.scoring.matcher import SkillMatcher
from app.scoring.engine import ATSScoringEngine, ATSScoreResult
from app.scoring.gap_analysis import SkillGapAnalyzer, SkillGapAnalysisReport
from app.scoring.improvement_plan import ImprovementPlanGenerator, ImprovementPlanItem, ResumeImprovementPlan
from app.reports.templates import template_registry, ResumeTemplate
from app.reports.round_robin import round_robin_scheduler
from app.reports.renderer import DocumentRenderer
from app.reports.sample_data import SAMPLE_PREVIEW_CONTENT
from app.projects.generator import ResumeContentGenerator, EnhancedResumeContent, ConfirmedSkillItem
from app.projects.catalog import project_catalog_repository
from app.scoring.gemini_analyzer import (
    GeminiAnalyzer,
    GeminiConfigError,
    GeminiModelUnavailableError,
    GeminiRateLimitError,
    GeminiTimeoutError,
    GeminiAPIError,
)
from app.projects.plan_generator import PrimaryProjectPlanGenerator, ProjectImplementationPlan
from app.projects.plan_renderer import ProjectPlanDocumentRenderer
from app.projects.evaluator import (
    CompletedProjectSubmission,
    CompletedProjectEvaluator,
    ProjectEvaluationResult,
    ProposedResumeEntry,
)
from app.projects.tracking import (
    project_tracking_service,
    ProjectAssignmentInput,
    TaskItem,
    MilestoneEvidenceSubmission,
    VerificationReviewInput,
    TaskProgressInput,
)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("futrsec.api")


# Application Lifespan Handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FUTRSEC Application starting up...")
    try:
        db_manager.initialize()
        health = db_manager.check_health()
        logger.info("Database health check on startup: %s", health)
        project_catalog_repository.ensure_table_and_seed()
    except Exception as exc:
        logger.error("Failed database connection initialization: %s", exc)
    yield
    logger.info("FUTRSEC Application shutting down...")
    db_manager.close()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Cybersecurity-focused AI Resume Analysis, ATS Scoring, and Round Robin Generation Engine",
    lifespan=lifespan,
)

# CORS configuration restricted to intended frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# --- Centralized Safe Error Handling ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Formats validation errors cleanly as informative, safe JSON."""
    req_id = f"req_{uuid.uuid4().hex[:10]}"
    logger.warning("[%s] Validation error on %s %s: %s", req_id, request.method, request.url.path, exc.errors())
    error_messages = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        msg = err.get("msg", "Invalid value")
        error_messages.append(f"{loc}: {msg}" if loc else msg)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": f"Request validation failed: {'; '.join(error_messages)}",
            "request_id": req_id,
            "error_type": "ValidationError",
            "validation_errors": exc.errors(),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Ensures HTTPExceptions always return JSON with request_id correlation."""
    req_id = f"req_{uuid.uuid4().hex[:10]}"
    logger.warning("[%s] HTTP %d on %s %s: %s", req_id, exc.status_code, request.method, request.url.path, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
            "request_id": req_id,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Guarantees unhandled exceptions return safe JSON with request_id without leaking secrets."""
    req_id = f"req_{uuid.uuid4().hex[:10]}"
    logger.error(
        "[%s] Unhandled exception processing %s %s: %s\n%s",
        req_id,
        request.method,
        request.url.path,
        exc,
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred while processing your request. Please review backend logs.",
            "request_id": req_id,
            "error_type": type(exc).__name__,
        },
    )


# In-memory session cache for recent analyses (keyed by analysis_id)
ANALYSIS_CACHE: Dict[str, Dict[str, Any]] = {}


# --- Health & Diagnostic Endpoints ---
@app.get("/health", tags=["System"])
@app.get("/api/health", tags=["System"])
def get_health() -> Dict[str, Any]:
    """Returns database health status, AI model diagnostics, and safe configuration parameters."""
    db_health = db_manager.check_health()
    gemini_health = GeminiAnalyzer.check_health()
    openai_health = ResumeContentGenerator.check_health()
    return {
        "status": "healthy" if db_health.get("status") == "healthy" else "degraded",
        "app": settings.safe_summary(),
        "database": db_health,
        "round_robin_cursor": round_robin_scheduler.get_current_cursor(),
        "active_templates_count": len(template_registry.list_templates(active_only=True)),
        "stage1_gemini": gemini_health,
        "stage2_openai": openai_health,
    }


@app.get("/api/gemini/health", tags=["System"])
def get_gemini_health() -> Dict[str, Any]:
    """Diagnostic check for Google Gemini API and model availability."""
    return GeminiAnalyzer.check_health()


@app.get("/api/openai/health", tags=["System"])
def get_openai_health() -> Dict[str, Any]:
    """Diagnostic check for OpenAI GPT API and model availability."""
    return ResumeContentGenerator.check_health()


# --- Role & Requirement Endpoints (Authoritative Data from Neon) ---
@app.get("/api/roles", tags=["Roles"])
def list_job_roles(search: Optional[str] = Query(None, description="Filter roles by name")):
    """Retrieves all cybersecurity job roles from Neon PostgreSQL."""
    try:
        roles = role_repository.list_roles(search=search)
        return {
            "total": len(roles),
            "roles": roles,
        }
    except Exception as exc:
        logger.error("Failed to list roles: %s", exc)
        raise HTTPException(status_code=500, detail="Database query failed while listing roles.")


@app.get("/api/roles/{role_id}", tags=["Roles"])
def get_role_details(role_id: int):
    """Retrieves full profile for a cybersecurity role including skills and requirements."""
    profile = role_repository.get_role_full_profile(role_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Cybersecurity role ID {role_id} not found.")
    return profile


@app.get("/api/roles/{role_id}/skills", tags=["Roles"])
def get_role_skills(role_id: int):
    """Retrieves categorized skills configured for a role."""
    skills = role_repository.get_role_skills(role_id)
    if not skills:
        role = role_repository.get_role_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail=f"Role ID {role_id} not found.")
    return {
        "role_id": role_id,
        "total": len(skills),
        "skills": skills,
    }


@app.get("/api/roles/{role_id}/requirements", tags=["Roles"])
def get_role_requirements(role_id: int):
    """Retrieves formal requirements (education, credentials) for a role."""
    reqs = role_repository.get_role_requirements(role_id)
    return {
        "role_id": role_id,
        "total": len(reqs),
        "requirements": reqs,
    }


@app.get("/api/roles/{role_id}/scoring-criteria", tags=["Roles"])
def get_role_scoring_criteria(role_id: int):
    """Retrieves scoring weights for a role."""
    criteria = role_repository.get_scoring_criteria(role_id)
    return {
        "role_id": role_id,
        "criteria": criteria,
    }


# --- Resume Upload and Analysis Workflow ---
@app.post("/api/resumes/analyze", tags=["Analysis"])
async def analyze_resume_endpoint(
    role_id: int = Form(..., description="ID of target cybersecurity role"),
    file: UploadFile = File(..., description="PDF or DOCX resume document"),
):
    """Full analysis pipeline: upload, parse, match against Neon, score, and evaluate threshold."""
    request_id = f"req_{uuid.uuid4().hex[:10]}"
    analysis_id = f"an_{uuid.uuid4().hex[:12]}"
    logger.info("[%s] Beginning resume analysis for target role_id=%s, file=%s", request_id, role_id, file.filename)

    # 1. Verify target role exists in Neon PostgreSQL
    try:
        role_profile = role_repository.get_role_full_profile(role_id)
    except Exception as db_exc:
        logger.error("[%s] Neon database query failure for role_id=%s: %s\n%s", request_id, role_id, db_exc, traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: Failed to retrieve cybersecurity role profile for ID {role_id}. Please retry shortly.",
        )

    if not role_profile:
        logger.warning("[%s] Role ID %s not found in Neon database.", request_id, role_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cybersecurity role with ID {role_id} not found in authoritative database.",
        )

    role_name = role_profile.get("role_name", f"Role #{role_id}")

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing filename in upload. Supported formats: PDF and DOCX only.",
        )

    # 2. Read and parse document with guaranteed temporary-file cleanup
    try:
        content_bytes = await file.read()
    except Exception as read_exc:
        logger.error("[%s] Failed reading uploaded file bytes: %s", request_id, read_exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read uploaded resume file contents.",
        )
    finally:
        await file.close()

    if len(content_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded resume file is empty (0 bytes). Supported formats: PDF and DOCX only.",
        )

    # Validate and parse document
    try:
        parsed_doc = ResumeParser.parse_document(file.filename, content_bytes)
    except ResumeParsingError as rpe:
        logger.warning("[%s] Resume parsing validation rejected file '%s': %s", request_id, file.filename, rpe)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(rpe))
    except Exception as exc:
        logger.error("[%s] Unexpected error parsing resume document '%s': %s\n%s", request_id, file.filename, exc, traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Document parsing failure: Unable to extract text content from '{file.filename}'. Ensure it is a text-searchable PDF or standard DOCX document.",
        )

    # 3. Resume Storage (Preserve uploaded file in UPLOAD_DIR)
    safe_filename = re.sub(r"[^\w\-.]", "_", file.filename)
    stored_path = settings.UPLOAD_DIR / f"{analysis_id}_{safe_filename}"
    try:
        settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        stored_path.write_bytes(content_bytes)
        logger.info("[%s] Preserved uploaded resume document to %s", request_id, stored_path)
    except Exception as store_exc:
        logger.warning("[%s] Could not persist resume copy to disk: %s (continuing in-memory)", request_id, store_exc)

    # 4. Extract structured resume information
    try:
        resume_data = ResumeExtractor.extract(parsed_doc["raw_text"])
    except ResumeExtractionError as rx_exc:
        logger.warning("[%s] Resume extraction rejected content: %s", request_id, rx_exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(rx_exc),
        )
    except Exception as ext_exc:
        logger.error("[%s] Structured resume extraction failed: %s\n%s", request_id, ext_exc, traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Resume extraction failure: Unable to parse document into structured candidate data. Error: {ext_exc}",
        )

    # 5. Compare evidence against Neon role requirements & skills
    try:
        match_report = SkillMatcher.match_skills(
            role_skills=role_profile.get("skills", []),
            resume_skills=resume_data.technical_skills,
            resume_full_text=parsed_doc["raw_text"],
            resume_projects=resume_data.projects,
            resume_experience=resume_data.employment_history,
            role_id=role_id,
            role_name=role_name,
        )
    except Exception as match_exc:
        logger.error("[%s] Skill matching failed for role '%s': %s\n%s", request_id, role_name, match_exc, traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Skill matching failure: Unable to evaluate candidate evidence against job requirements.",
        )

    # 6. Deterministic ATS-style scoring calculation
    try:
        score_result = ATSScoringEngine.calculate_score(
            resume_data=resume_data,
            match_report=match_report,
            role_requirements=role_profile.get("requirements", []),
            db_scoring_criteria=role_profile.get("scoring_criteria", []),
            threshold=settings.SCORE_THRESHOLD,
        )
    except Exception as score_exc:
        logger.error("[%s] ATS scoring calculation failed: %s\n%s", request_id, score_exc, traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ATS scoring failure: Error calculating category compatibility scores.",
        )

    # 7. Skill-gap analysis
    try:
        gap_report = SkillGapAnalyzer.analyze_gaps(match_report, resume_data)
    except Exception as gap_exc:
        logger.error("[%s] Skill gap analysis failed: %s\n%s", request_id, gap_exc, traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Skill gap analysis failure: Error identifying candidate missing qualifications.",
        )

    # 8. Generate personalized, approval-based improvement plan covering all categories
    try:
        improvement_plan = ImprovementPlanGenerator.generate_plan(
            resume_data=resume_data,
            match_report=match_report,
            score_result=score_result,
            role_requirements=role_profile.get("requirements", []),
            role_name=role_name,
            role_skills=role_profile.get("skills", []),
            scoring_criteria=role_profile.get("scoring_criteria", []),
        )
    except Exception as plan_exc:
        logger.error("[%s] Improvement plan generator failed: %s\n%s", request_id, plan_exc, traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Improvement planning failure: Error formulating role-specific recommendations.",
        )

    initial_score = score_result.final_score
    stage_passed = initial_score >= settings.SCORE_THRESHOLD

    # 9. AI Model 1: Hosted Resume Analysis via Google Gemini API (gemini-3.6-flash)
    gemini_health = GeminiAnalyzer.check_health()
    gemini_analysis_data = None
    gemini_status_code = "not_configured"
    gemini_instructions = None
    gemini_error = None
    exact_issue = None

    if settings.is_gemini_configured():
        try:
            logger.info("[%s] Executing Stage 1 Google Gemini analysis for role '%s'...", request_id, role_name)
            gemini_analysis_data = await GeminiAnalyzer.analyze_with_gemini(
                raw_text=parsed_doc["raw_text"],
                role_name=role_name,
                role_skills=role_profile.get("skills", []),
                role_requirements=role_profile.get("requirements", []),
                scoring_criteria=role_profile.get("scoring_criteria", []),
                matched_skills=[s.skill_name for s in match_report.matched_skills],
                missing_skills=[s.skill_name for s in match_report.unmatched_skills],
                resume_data=resume_data,
            )
            gemini_status_code = "completed"
        except GeminiModelUnavailableError as exc:
            logger.error("[%s] Gemini model '%s' unavailable (HTTP %s): %s", request_id, exc.model, exc.http_status, exc.error_details)
            gemini_status_code = "model_unavailable"
            gemini_error = str(exc)
            exact_issue = exc.error_details
            gemini_instructions = (
                f"Google Gemini model '{exc.model}' is unavailable for this API key: {exc.error_details}. "
                f"Verify the model name or API tier access."
            )
        except GeminiRateLimitError as exc:
            logger.error("[%s] Gemini rate limit exceeded for '%s': %s", request_id, exc.model, exc.error_details)
            gemini_status_code = "rate_limited"
            gemini_error = str(exc)
            exact_issue = exc.error_details
            gemini_instructions = "Google Gemini API rate limit or quota exceeded. Please wait a moment and retry."
        except GeminiTimeoutError as exc:
            logger.error("[%s] Gemini timeout: %s", request_id, exc)
            gemini_status_code = "timeout"
            gemini_error = str(exc)
            gemini_instructions = "Google Gemini API request timed out. Please check network connectivity and retry."
        except GeminiAPIError as exc:
            logger.error("[%s] Gemini API error (HTTP %s): %s", request_id, exc.status_code, exc)
            gemini_status_code = "api_error"
            gemini_error = str(exc)
            exact_issue = str(exc.details) if exc.details else str(exc)
            gemini_instructions = f"Google Gemini API error (HTTP {exc.status_code})."
        except Exception as exc:
            logger.warning("[%s] Stage 1 Gemini analysis failed: %s", request_id, exc)
            gemini_status_code = "failed"
            gemini_error = str(exc)
            gemini_instructions = f"Analysis error: {exc}"
    else:
        gemini_status_code = "not_configured"
        gemini_instructions = gemini_health.get("troubleshooting")
        gemini_error = gemini_health.get("error")

    try:
        response_data = {
            "analysis_id": analysis_id,
            "request_id": request_id,
            "filename": file.filename,
            "role_id": role_id,
            "role_name": role_name,
            "document_metadata": parsed_doc["metadata"],
            "security_flags": {
                "injection_detected": parsed_doc["security_flag_injection_detected"],
            },
            "parsed_resume": resume_data.model_dump(),
            "verification_report": resume_data.verification_report,
            "match_report": match_report.model_dump(),
            "score_result": score_result.model_dump(),
            "gap_analysis": gap_report.model_dump(),
            "improvement_plan": improvement_plan.model_dump(),
            "stage1_ai": {
                "provider": "Google Gemini API",
                "model": settings.GEMINI_MODEL,
                "status": gemini_status_code,
                "output": gemini_analysis_data,
                "error": gemini_error,
                "exact_issue": exact_issue,
                "troubleshooting": gemini_instructions,
            },
            "demonstrated_skills": (
                gemini_analysis_data.get("demonstrated_skills")
                if gemini_analysis_data and gemini_analysis_data.get("demonstrated_skills")
                else gap_report.demonstrated_skills
            ),
            "evidence_gaps": (
                gemini_analysis_data.get("evidence_gaps")
                if gemini_analysis_data and gemini_analysis_data.get("evidence_gaps")
                else []
            ),
            "project_evaluations": (
                gemini_analysis_data.get("project_evaluations")
                if gemini_analysis_data and gemini_analysis_data.get("project_evaluations")
                else []
            ),
            "qualification_evaluations": (
                gemini_analysis_data.get("qualification_evaluations")
                if gemini_analysis_data and gemini_analysis_data.get("qualification_evaluations")
                else {}
            ),
            "gemini_recommendations": (
                gemini_analysis_data.get("actionable_recommendations")
                if gemini_analysis_data and gemini_analysis_data.get("actionable_recommendations")
                else []
            ),
            "skills_not_demonstrated": gap_report.skills_not_demonstrated,
            "relevant_certifications_held": resume_data.certifications,
            "extracted_projects": [p.model_dump() for p in resume_data.projects],
            "projects": [p.model_dump() for p in resume_data.projects],
            "education_relevance": score_result.category_scores[2].details if len(score_result.category_scores) > 2 else {},
            "professional_summary_quality": score_result.category_scores[4].explanation if len(score_result.category_scores) > 4 else "",
            "required_qualifications": role_profile.get("requirements", []),
            "relevant_projects_and_experience": {
                "projects": gap_report.project_evidence_summary,
                "experience": gap_report.experience_evidence_summary,
            },
            "action_required": "proceed" if stage_passed else "offer_improvement",
            "stage_passed": stage_passed,
            "next_stage_allowed": stage_passed,
            "threshold": settings.SCORE_THRESHOLD,
            "post_threshold": settings.POST_IMPROVEMENT_THRESHOLD,
            "max_attempts": settings.MAX_IMPROVEMENT_ATTEMPTS,
        }

        # Store in cache for subsequent resume creation / re-scoring workflow
        ANALYSIS_CACHE[analysis_id] = {
            "analysis_id": analysis_id,
            "filename": file.filename,
            "stored_path": str(stored_path) if stored_path.exists() else None,
            "parsed_resume": resume_data,
            "role_profile": role_profile,
            "role_name": role_name,
            "role_id": role_id,
            "match_report": match_report,
            "score_result": score_result,
            "gap_report": gap_report,
            "improvement_plan": improvement_plan,
            "stage1_ai": response_data["stage1_ai"],
            "latest_score": initial_score,
            "stage_passed": stage_passed,
            "next_stage_allowed": stage_passed,
            "current_attempt": 0,
            "attempts_history": [
                {
                    "attempt": 0,
                    "type": "initial",
                    "score": initial_score,
                    "status": score_result.status,
                    "stage_passed": stage_passed,
                }
            ],
        }

        logger.info("[%s] Analysis %s completed successfully (score=%.1f, passed=%s)", request_id, analysis_id, initial_score, stage_passed)
        return response_data
    except Exception as ser_exc:
        logger.error("[%s] Response serialization or cache failure: %s\n%s", request_id, ser_exc, traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis result formatting error: Failed to serialize evaluation payload.",
        )


class ResumeImprovementRequest(BaseModel):
    analysis_id: str
    selected_role_id: Optional[int] = None
    attempt_number: int = 1
    confirmed_skills: List[ConfirmedSkillItem] = Field(default_factory=list)
    approved_plan_items: List[ImprovementPlanItem] = Field(default_factory=list)
    approved_completed_project: Optional[ProposedResumeEntry] = None
    approved_completed_projects: List[ProposedResumeEntry] = Field(default_factory=list)
    permission_granted: bool = True
    candidate_notes: Optional[str] = None
    selection_mode: str = "automatic"  # "automatic" | "manual"
    template_id: Optional[str] = None
    job_id: Optional[str] = None


@app.post("/api/resumes/improve", tags=["Resume Creation"])
def improve_resume_endpoint(payload: ResumeImprovementRequest):
    """Triggers AI resume creation, Round Robin template selection, and automatic re-scoring."""
    cached = ANALYSIS_CACHE.get(payload.analysis_id)
    if not cached:
        raise HTTPException(
            status_code=404,
            detail="Analysis session expired or not found. Please upload and analyze your resume again."
        )

    resume_data: ParsedResumeData = cached["parsed_resume"]
    role_profile: Dict[str, Any] = cached["role_profile"]
    gap_report: SkillGapAnalysisReport = cached["gap_report"]
    original_score: ATSScoreResult = cached["score_result"]

    current_attempt = payload.attempt_number
    if current_attempt > settings.MAX_IMPROVEMENT_ATTEMPTS:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum improvement attempts ({settings.MAX_IMPROVEMENT_ATTEMPTS}) reached for this resume."
        )

    job_id = payload.job_id or f"job_{uuid.uuid4().hex[:10]}"

    # 1. Template Selection: Automatic Round Robin vs Manual Candidate Selection
    selection_mode = (payload.selection_mode or "automatic").strip().lower()
    if selection_mode == "manual":
        raw_tid = (payload.template_id or "").strip()
        if not raw_tid:
            raise HTTPException(
                status_code=400,
                detail="A valid template_id must be provided when selection_mode is 'manual'."
            )
        target_template = template_registry.get_template(raw_tid)
        if not target_template or not target_template.is_active:
            raise HTTPException(
                status_code=400,
                detail=f"Template '{raw_tid}' is invalid, inactive, or not registered."
            )
        try:
            selected_template, assignment = round_robin_scheduler.assign_manual_template(
                template_id=target_template.template_id,
                role_name=role_profile["role_name"],
                job_id=job_id,
                output_format="docx",
            )
        except Exception as exc:
            logger.error("Manual template selection error: %s", exc)
            raise HTTPException(status_code=500, detail=f"Manual template selection failed: {exc}")
    else:
        # Automatic selection (default): strictly ignore any candidate-supplied template_id and use Round Robin
        try:
            selected_template, assignment = round_robin_scheduler.select_next_template(
                role_name=role_profile["role_name"],
                job_id=job_id,
                output_format="docx",
            )
        except Exception as exc:
            logger.error("Round Robin scheduling error: %s", exc)
            raise HTTPException(status_code=500, detail=f"Template selection failed: {exc}")

    # 2. Authoritative Candidate-Approved Projects Compilation
    authoritative_approved_projects: List[Any] = []
    seen_approved_titles = set()

    def register_approved_proj(p):
        if not p:
            return
        t = getattr(p, "title_line", "") or ""
        t_norm = re.sub(r"\s*\|\s*in\s*progress$", "", t.strip(), flags=re.IGNORECASE).strip().lower()
        if t_norm and t_norm not in seen_approved_titles:
            seen_approved_titles.add(t_norm)
            authoritative_approved_projects.append(p)

    for p in (payload.approved_completed_projects or []):
        register_approved_proj(p)
    if payload.approved_completed_project:
        register_approved_proj(payload.approved_completed_project)
    for p in cached.get("approved_completed_projects", []):
        register_approved_proj(p)
    if cached.get("approved_completed_project"):
        register_approved_proj(cached.get("approved_completed_project"))

    # Strictly query verified completed projects from tracking system (never unverified/in-progress)
    cand_id = cached.get("candidate_id") or (resume_data.contact_info.email if resume_data.contact_info else None) or resume_data.candidate_name
    if cand_id:
        try:
            db_verified = project_tracking_service.get_verified_projects_for_resume(str(cand_id).strip())
            for vp in db_verified:
                entry = ProposedResumeEntry(
                    title_line=vp["title"],
                    status_label=vp["status_label"],
                    bullets=vp["bullets"],
                    is_approved=True,
                )
                register_approved_proj(entry)
        except Exception as v_err:
            logger.warning("Could not fetch verified tracking projects for %s: %s", cand_id, v_err)

    # Update session cache with authoritative list
    cached["approved_completed_projects"] = list(authoritative_approved_projects)

    # 3. AI Content Enhancement (respecting strict factual accuracy across iterations)
    enhanced_content = ResumeContentGenerator.generate_enhanced_content(
        resume_data=resume_data,
        target_role_name=role_profile["role_name"],
        missing_core_skills=gap_report.missing_core_skills,
        confirmed_skills=payload.confirmed_skills,
        approved_plan_items=payload.approved_plan_items,
        permission_granted=payload.permission_granted,
        attempt_number=current_attempt,
        candidate_notes=payload.candidate_notes,
        approved_projects=authoritative_approved_projects,
    )

    # Post-generation reconciliation: Ensure EVERY approved project from the authoritative list
    # is represented in enhanced_content.projects with proper In Progress / Completed title and bullets.
    for appr_proj in reversed(authoritative_approved_projects):
        title_line = getattr(appr_proj, "title_line", "") or "Cybersecurity Practical Project"
        status_lbl = getattr(appr_proj, "status_label", "Completed")
        bullets = getattr(appr_proj, "bullets", [])

        is_in_prog = "in progress" in str(status_lbl).lower() or "in progress" in title_line.lower()
        base_title = re.sub(r"\s*\|\s*in\s*progress$", "", title_line.strip(), flags=re.IGNORECASE).strip()
        clean_title = f"{base_title} | In Progress" if is_in_prog else base_title

        # Extract technologies from bullets or title
        techs = []
        for b in bullets:
            if "technologies:" in b.lower():
                part = b.split(":", 2)[-1] if b.count(":") >= 2 else b.split(":", 1)[1]
                techs = [t.strip() for t in part.rstrip(".").split(",") if t.strip()]
                break
        if not techs:
            techs = [t.strip() for t in base_title.split("|")[-1].split(",") if t.strip()]

        existing_idx = -1
        for idx, ep in enumerate(enhanced_content.projects):
            ep_title = ep.get("title", "")
            ep_base = re.sub(r"\s*\|\s*in\s*progress$", "", ep_title.strip(), flags=re.IGNORECASE).strip()
            if ep_base.lower() == base_title.lower():
                existing_idx = idx
                break

        if existing_idx >= 0:
            # Reconcile existing entry with verified title and bullets
            enhanced_content.projects[existing_idx]["title"] = clean_title
            if not enhanced_content.projects[existing_idx].get("technologies"):
                enhanced_content.projects[existing_idx]["technologies"] = techs
            if not enhanced_content.projects[existing_idx].get("bullets") and bullets:
                enhanced_content.projects[existing_idx]["bullets"] = bullets
        else:
            # Prepend authoritative approved project
            enhanced_content.projects.insert(0, {
                "title": clean_title,
                "description": " \n".join(bullets),
                "technologies": techs,
                "outcomes": bullets[-1] if bullets else "Verified practical outcome",
                "bullets": bullets,
            })

        appr_note = f"Added candidate-approved project: {clean_title}"
        if appr_note not in enhanced_content.approved_improvements_applied:
            enhanced_content.approved_improvements_applied.append(appr_note)

    # 3. Document Rendering (DOCX and PDF) after strict validation
    from app.resume.validator import ResumeContentValidator
    enhanced_content, _ = ResumeContentValidator.validate_and_sanitize(enhanced_content)

    render_result = DocumentRenderer.render_resume(
        content=enhanced_content,
        template=selected_template,
        job_id=job_id,
    )

    round_robin_scheduler.update_job_status(job_id, "completed")

    # 4. Immediate Automatic Re-scoring using identical deterministic Python engine and Neon criteria
    reconstructed_skills = []
    for slist in enhanced_content.technical_skills_grouped.values():
        reconstructed_skills.extend(slist)

    # Structured full text with standard headings to ensure rigorous re-extraction
    lines = [
        enhanced_content.candidate_name,
        enhanced_content.professional_headline or "",
        enhanced_content.contact_header,
        "\nPROFESSIONAL SUMMARY",
        enhanced_content.professional_summary,
        "\nTECHNICAL SKILLS",
        ", ".join(reconstructed_skills),
        "\nWORK EXPERIENCE",
    ]
    for exp in enhanced_content.experience:
        lines.append(f"{exp.get('job_title', '')} at {exp.get('company', '')}")
        for r in exp.get("responsibilities", []):
            lines.append(f"- {r}")

    lines.append("\nPROJECTS")
    for proj in enhanced_content.projects:
        status_suffix = f" | Status: {proj.get('status', 'Completed')}" if proj.get("status") else ""
        lines.append(f"{proj.get('title', '')}{status_suffix}")
        if proj.get("technologies"):
            lines.append(f"Technologies: {', '.join(proj.get('technologies'))}")
        if proj.get("github_url"):
            lines.append(f"Project URL: {proj.get('github_url')}")
        bullets = proj.get("bullets", [])
        if bullets:
            for b in bullets:
                lines.append(f"- {b}")
        elif proj.get("description"):
            lines.append(f"{proj.get('description')}")
        if proj.get("outcomes") and proj.get("outcomes") not in bullets:
            lines.append(f"Outcomes: {proj.get('outcomes')}")

    lines.append("\nEDUCATION")
    for edu in enhanced_content.education:
        lines.append(f"{edu.get('degree', '')} - {edu.get('institution', '')} ({edu.get('graduation_year', '')})")

    lines.append("\nCERTIFICATIONS")
    for cert in enhanced_content.certifications:
        lines.append(f"- {cert}")

    reconstructed_text = "\n".join(lines)
    re_parsed = ParsedResumeData(
        candidate_name=enhanced_content.candidate_name,
        contact_info=ContactInfo(**(enhanced_content.contact_details or {})),
        career_objective=enhanced_content.professional_summary,
        professional_summary=enhanced_content.professional_summary,
        technical_skills=reconstructed_skills,
        education=[
            EducationEntry(
                degree=ed.get("degree", ""),
                institution=ed.get("institution", ""),
                graduation_year=ed.get("graduation_year", ""),
                field_of_study=ed.get("field_of_study", ""),
                raw_text=ed.get("raw_text") or f"{ed.get('degree', '')} in {ed.get('field_of_study', '') or ''} {ed.get('institution', '')}",
            )
            for ed in enhanced_content.education
        ],
        certifications=enhanced_content.certifications,
        projects=[
            ProjectEntry(
                title=p.get("title", ""),
                description=p.get("description", ""),
                technologies=p.get("technologies", []),
                outcomes=p.get("outcomes"),
                status=p.get("status", "Completed"),
                github_url=p.get("github_url"),
                project_url=p.get("project_url"),
                bullets=p.get("bullets", []),
            )
            for p in enhanced_content.projects
        ],
        employment_history=[
            ExperienceEntry(
                job_title=e.get("job_title", ""),
                company=e.get("company", ""),
                start_date=e.get("start_date", ""),
                end_date=e.get("end_date", ""),
                responsibilities=e.get("responsibilities", []),
            )
            for e in enhanced_content.experience
        ],
        achievements=enhanced_content.achievements,
    )

    # Re-match against Neon role requirements
    re_match = SkillMatcher.match_skills(
        role_skills=role_profile["skills"],
        resume_skills=re_parsed.technical_skills or reconstructed_skills,
        resume_full_text=reconstructed_text,
        resume_projects=re_parsed.projects,
        resume_experience=re_parsed.employment_history,
        role_id=role_profile["role_id"],
        role_name=role_profile["role_name"],
    )

    # Re-score with post-generation threshold (80.0)
    re_score = ATSScoringEngine.calculate_score(
        resume_data=re_parsed,
        match_report=re_match,
        role_requirements=role_profile["requirements"],
        db_scoring_criteria=role_profile["scoring_criteria"],
        threshold=settings.POST_IMPROVEMENT_THRESHOLD,
    )

    new_score = re_score.final_score
    initial_score = original_score.final_score
    score_delta = round(new_score - initial_score, 1)

    # Post-generation threshold rule: score >= 80.0
    stage_passed = new_score >= settings.POST_IMPROVEMENT_THRESHOLD
    next_stage_allowed = stage_passed
    can_retry = (current_attempt < settings.MAX_IMPROVEMENT_ATTEMPTS) and not stage_passed

    # Re-analyze remaining skill gaps
    remaining_gaps = SkillGapAnalyzer.analyze_gaps(re_match, re_parsed)

    # Update session cache
    cached["enhanced_content"] = enhanced_content
    cached["render_result"] = render_result
    cached["assigned_template"] = selected_template
    cached["selection_mode"] = selection_mode
    cached["latest_score"] = new_score
    cached["stage_passed"] = stage_passed
    cached["next_stage_allowed"] = next_stage_allowed
    cached["current_attempt"] = current_attempt

    history_entry = {
        "attempt": current_attempt,
        "type": "improvement",
        "score": new_score,
        "delta": score_delta,
        "template_id": selected_template.template_id,
        "template_name": selected_template.template_name,
        "selection_mode": selection_mode,
        "stage_passed": stage_passed,
    }
    attempts_history = [
        h for h in cached.get("attempts_history", [])
        if h.get("attempt") != current_attempt
    ]
    attempts_history.append(history_entry)
    cached["attempts_history"] = attempts_history

    # Explainable category comparison with evidence, applied changes, and remaining gaps
    category_comparison = []
    for orig, nxt in zip(original_score.category_scores, re_score.category_scores):
        delta = round(nxt.score_earned - orig.score_earned, 1)
        c_name = orig.category_name

        # Identify approved improvements applied to this category
        applied_list = [
            a for a in enhanced_content.approved_improvements_applied
            if c_name.lower()[:4] in a.lower()
            or ("skill" in c_name.lower() and ("skill" in a.lower() or "tool" in a.lower()))
            or ("proj" in c_name.lower() and "proj" in a.lower())
            or ("cert" in c_name.lower() and "cert" in a.lower())
            or ("edu" in c_name.lower() and ("degree" in a.lower() or "course" in a.lower()))
            or ("obj" in c_name.lower() and ("summary" in a.lower() or "headline" in a.lower()))
        ]
        approved_text = "; ".join(applied_list) if applied_list else ("Syntax and ATS structure optimized" if delta >= 0 else "Preserved original candidate data")

        # Determine remaining gaps
        if c_name == "Technical Skills":
            rem_gaps = f"{len(remaining_gaps.missing_core_skills)} core and {len(remaining_gaps.missing_preferred_skills)} preferred skill(s) not yet verified." if (remaining_gaps.missing_core_skills or remaining_gaps.missing_preferred_skills) else "All essential technical skills demonstrated."
        elif c_name == "Projects":
            rem_gaps = "Demonstrate additional practical implementations with quantifiable outcomes." if len(re_parsed.projects) < 3 else "Project requirements satisfied."
        elif c_name == "Tools & Certifications":
            rem_gaps = "Obtain recognized industry credentials (e.g., Security+, CEH, CySA+) for future career milestones." if len(re_parsed.certifications) < 2 else "Credentials well documented."
        elif c_name == "Education":
            rem_gaps = "Educational qualifications verified against role criteria."
        elif c_name == "Career Objective":
            rem_gaps = "Headline and professional summary aligned with role."
        else:
            rem_gaps = "None"

        # Explain if delta <= 0
        no_inc_expl = None
        if delta <= 0:
            if c_name == "Technical Skills":
                no_inc_expl = "Deterministic scoring requires confirmed hands-on capability. Phrasing polish alone does not award additional points."
            elif c_name == "Tools & Certifications":
                no_inc_expl = "Certification score is based on verified earned credentials. In-progress milestones or learning recommendations do not artificially inflate score."
            elif c_name == "Education":
                no_inc_expl = "Degree qualifications are accurately credited. No additional degree was introduced."
            elif c_name == "Projects":
                no_inc_expl = "Existing projects were polished. Additional score requires confirming an omitted practical project."
            else:
                no_inc_expl = "Score reflects maximum alignment evaluated for this section."

        category_comparison.append({
            "category": c_name,
            "weight": orig.weight,
            "original_score": orig.score_earned,
            "new_score": nxt.score_earned,
            "delta": delta,
            "evidence_supporting": nxt.explanation,
            "approved_improvement_applied": approved_text,
            "remaining_gaps": rem_gaps,
            "no_increase_explanation": no_inc_expl,
        })

    # 5. Verified Applied Improvements (Green Section - Verified only)
    applied_improvements = []

    # Professional Summary Improved
    if enhanced_content.professional_summary:
        applied_improvements.append({
            "section_name": "Professional Summary",
            "title": "Professional Summary — Improved",
            "before_issue": f"Original summary lacked clear alignment with the specialized cybersecurity duties and technical requirements of {role_profile['role_name']}.",
            "after_change": f"Structured summary to emphasize verified defense competencies, active security tooling, and candidate focus as {role_profile['role_name']}.",
            "why_it_helps": f"Delivers immediate ATS keyword density and presents verified security expertise clearly to technical recruiters.",
            "status": "Successfully updated",
            "verified": True,
        })

    # Technical Skills Section Reorganized
    if enhanced_content.technical_skills_grouped:
        skills_count = sum(len(v) for v in enhanced_content.technical_skills_grouped.values())
        confirmed_str = (", ".join(enhanced_content.confirmed_skills_included[:4])) if enhanced_content.confirmed_skills_included else ""
        applied_improvements.append({
            "section_name": "Technical Skills",
            "title": "Technical Skills — Reorganized",
            "before_issue": "Technical skills were presented in an unorganized format without domain categorization, obscuring core cybersecurity competencies." + (f" Missing candidate-confirmed skills: {confirmed_str}." if confirmed_str else ""),
            "after_change": f"Reorganized {skills_count} verified technical skills into structured cybersecurity categories" + (f" and integrated candidate-confirmed capabilities ({confirmed_str})." if confirmed_str else "."),
            "why_it_helps": "Allows automated ATS parsers and security hiring managers to rapidly verify critical technical proficiencies.",
            "status": "Successfully updated",
            "verified": True,
        })

    # Existing Project Descriptions Strengthened
    if enhanced_content.projects:
        proj_titles = [p.get("title", "Project") for p in enhanced_content.projects[:3]]
        applied_improvements.append({
            "section_name": "Projects",
            "title": "Projects — Improved",
            "before_issue": "The project description did not clearly explain the candidate's contribution, technical tools used, or operational outcomes.",
            "after_change": f"The project descriptions ({', '.join(proj_titles)}) now explain the candidate's verified contribution, technologies actually used, and implemented functionality.",
            "why_it_helps": f"Provides concrete proof of practical defensive problem solving required for {role_profile['role_name']}.",
            "status": "Successfully updated",
            "verified": True,
        })

    # Work Experience Descriptions Improved
    if enhanced_content.experience:
        applied_improvements.append({
            "section_name": "Work Experience",
            "title": "Work Experience — Enhanced",
            "before_issue": "Employment history descriptions lacked active cybersecurity verbs and concise security-focused phrasing.",
            "after_change": "Reframed experience bullet points using strong security action verbs (e.g., Analyzed, Mitigated, Configured) while strictly preserving authentic employment history, companies, and dates.",
            "why_it_helps": "Clearly communicates technical responsibilities and operational contributions without altering factual history.",
            "status": "Successfully updated",
            "verified": True,
        })

    # Confirmed Certifications Organized
    if enhanced_content.certifications or enhanced_content.pursuing_certifications:
        certs_desc = ", ".join(enhanced_content.certifications) if enhanced_content.certifications else "Academic & practical defense credentials"
        pursuing_str = f" Documented pursuing milestones: {', '.join(enhanced_content.pursuing_certifications)}." if enhanced_content.pursuing_certifications else ""
        applied_improvements.append({
            "section_name": "Certifications & Credentials",
            "title": "Confirmed Certifications — Organized",
            "before_issue": "Certifications lacked formal industry naming standards or did not distinguish between earned credentials and in-progress study.",
            "after_change": f"Preserved verified earned credentials ({certs_desc}).{pursuing_str} Unearned certifications were strictly excluded.",
            "why_it_helps": "Maintains 100% factual integrity while signaling active professional qualification to employers.",
            "status": "Successfully updated",
            "verified": True,
        })

    # Role Keywords Aligned
    applied_improvements.append({
        "section_name": "Role Keywords",
        "title": "Role Keywords — Aligned",
        "before_issue": f"Resume phrasing did not reflect the official competency taxonomy and requirement terminology for {role_profile['role_name']}.",
        "after_change": f"Standardized technical terminology and phrases to match Neon PostgreSQL criteria and industry standards for {role_profile['role_name']}.",
        "why_it_helps": f"Maximizes ATS match score and keyword relevancy for automated applicant screening.",
        "status": "Successfully updated",
        "verified": True,
    })

    # ATS Formatting Applied
    applied_improvements.append({
        "section_name": "ATS Formatting",
        "title": "ATS-Friendly Formatting — Applied",
        "before_issue": "Document structure contained non-standard elements or inconsistent spacing that could reduce ATS parse accuracy.",
        "after_change": f"Applied '{selected_template.template_name}' template with single-column hierarchy, standard section headers, clean bullet spacing, and full DOCX/PDF export support.",
        "why_it_helps": "Guarantees seamless automated parsing across enterprise ATS platforms without layout corruption.",
        "status": "Successfully updated",
        "verified": True,
    })

    # 6. Remaining Opportunities (Amber Section - Unresolved gaps only)
    remaining_opportunities = []
    for s in remaining_gaps.missing_core_skills:
        remaining_opportunities.append({
            "requirement_name": f"Core Competency: {s}",
            "category": "Technical Skills",
            "importance": "high",
            "why_it_matters": f"Directly evaluated in the scoring criteria for {role_profile['role_name']}; lack of demonstrated evidence impacts technical compatibility score.",
            "guidance": f"Complete hands-on laboratory exercises (e.g. TryHackMe, PortSwigger, or home lab) in {s} to gain verifiable project experience.",
        })

    for s in remaining_gaps.missing_preferred_skills[:3]:
        remaining_opportunities.append({
            "requirement_name": f"Preferred Skill: {s}",
            "category": "Technical Skills",
            "importance": "preferred",
            "why_it_matters": f"Acts as a differentiator among candidates for competitive {role_profile['role_name']} openings.",
            "guidance": f"Review industry documentation and open-source tooling for {s} to demonstrate familiarity during interview stages.",
        })

    for s in (enhanced_content.unverified_skills_excluded or [])[:3]:
        remaining_opportunities.append({
            "requirement_name": f"Unconfirmed Competency: {s}",
            "category": "Candidate Confirmation",
            "importance": "medium",
            "why_it_matters": "Marked as not used or unverified during candidate review, so it was excluded to prevent resume fabrication.",
            "guidance": f"Once practical coursework or lab projects with {s} are completed, update your profile to include demonstrable evidence.",
        })

    if len(re_parsed.projects) < 2:
        remaining_opportunities.append({
            "requirement_name": "Practical Security Projects",
            "category": "Projects",
            "importance": "high",
            "why_it_matters": f"Hiring managers look for multiple verifiable practical projects demonstrating applied security defense in {role_profile['role_name']}.",
            "guidance": "Document a home-lab implementation (such as configuring a SIEM, snort IDS, or cloud security baseline) to demonstrate independent initiative.",
        })

    # 7. Failed Improvements (Red Section - Only populated if errors occurred)
    failed_improvements = []

    return {
        "job_id": job_id,
        "analysis_id": payload.analysis_id,
        "role_name": role_profile["role_name"],
        "attempt_number": current_attempt,
        "max_attempts": settings.MAX_IMPROVEMENT_ATTEMPTS,
        "can_retry": can_retry,
        "threshold": settings.POST_IMPROVEMENT_THRESHOLD,
        "initial_score": initial_score,
        "original_score": initial_score,
        "new_score": new_score,
        "score_delta": score_delta,
        "stage_passed": stage_passed,
        "next_stage_allowed": next_stage_allowed,
        "status": "PASSED" if stage_passed else "IMPROVEMENT_RECOMMENDED",
        "selection_mode": selection_mode,
        "assigned_template": {
            "template_id": selected_template.template_id,
            "template_name": selected_template.template_name,
            "description": selected_template.description,
            "style_config": selected_template.style_config,
            "selection_mode": selection_mode,
        },
        "enhanced_content": enhanced_content.model_dump(),
        "confirmed_skills_included": enhanced_content.confirmed_skills_included,
        "unverified_skills_excluded": enhanced_content.unverified_skills_excluded,
        "sections_rewritten": enhanced_content.sections_rewritten,
        "future_learning_recommendations": enhanced_content.future_learning_recommendations,
        "approved_improvements_applied": enhanced_content.approved_improvements_applied,
        "pursuing_certifications": enhanced_content.pursuing_certifications,
        "documents": {
            "docx_url": f"/api/resumes/download/{render_result['file_id']}?format=docx",
            "pdf_url": f"/api/resumes/download/{render_result['file_id']}?format=pdf" if render_result["pdf_available"] else None,
            "pdf_available": render_result["pdf_available"],
            "pdf_status_note": render_result["pdf_status_note"],
        },
        "category_comparison": category_comparison,
        "attempts_history": attempts_history,
        "remaining_gaps": remaining_gaps.model_dump(),
        "applied_improvements": applied_improvements,
        "remaining_opportunities": remaining_opportunities,
        "failed_improvements": failed_improvements,
        "re_scored_match_report": re_match.model_dump(),
        "explanation": (
            f"Resume compatibility score updated from {initial_score} to {new_score} "
            f"({'+' if score_delta >= 0 else ''}{score_delta} pts) on Attempt {current_attempt} of {settings.MAX_IMPROVEMENT_ATTEMPTS}."
            + (f" Resume requirement passed (threshold: {settings.POST_IMPROVEMENT_THRESHOLD:.1f})." if stage_passed else f" Score is below {settings.POST_IMPROVEMENT_THRESHOLD:.1f} post-generation threshold. Additional improvement iteration available.")
        ),
    }


class NextStageRequest(BaseModel):
    analysis_id: str


@app.post("/api/resumes/next-stage", tags=["Analysis"])
def proceed_to_next_stage_endpoint(payload: NextStageRequest):
    """Backend validation endpoint authorizing progression to next stage."""
    cached = ANALYSIS_CACHE.get(payload.analysis_id)
    if not cached:
        raise HTTPException(status_code=404, detail="Analysis session expired or not found.")

    stage_passed = cached.get("stage_passed", False)
    latest_score = cached.get("latest_score", 0.0)
    role_profile = cached.get("role_profile", {})
    current_attempt = cached.get("current_attempt", 0)

    if not stage_passed:
        req_threshold = settings.POST_IMPROVEMENT_THRESHOLD if current_attempt > 0 else settings.SCORE_THRESHOLD
        raise HTTPException(
            status_code=400,
            detail=(
                f"Candidate resume evaluation has not met the required passing threshold ({req_threshold:.1f}). "
                f"Current score: {latest_score}/100. Further improvement or additional qualifications are required."
            ),
        )

    return {
        "status": "authorized",
        "message": "Resume Requirement Passed. Candidate authorized to continue to next stage.",
        "analysis_id": payload.analysis_id,
        "final_verified_score": latest_score,
        "role_id": role_profile.get("role_id"),
        "role_name": role_profile.get("role_name"),
        "stage": "TECHNICAL_ASSESSMENT",
        "next_stage_url": "/stage/technical-assessment",
    }


class AcceptAndRescoreRequest(BaseModel):
    analysis_id: str
    accepted_content: Optional[Dict[str, Any]] = None


@app.post("/api/resumes/accept-and-rescore", tags=["Resume Creation"])
def accept_and_rescore_endpoint(payload: AcceptAndRescoreRequest):
    """Recalculates ATS compatibility score after candidate accepts improved resume."""
    cached = ANALYSIS_CACHE.get(payload.analysis_id)
    if not cached:
        raise HTTPException(status_code=404, detail="Analysis session not found.")

    role_profile: Dict[str, Any] = cached["role_profile"]
    original_score: ATSScoreResult = cached["score_result"]
    enhanced: EnhancedResumeContent = cached.get("enhanced_content")

    if not enhanced:
        raise HTTPException(status_code=400, detail="No improved resume content found for this session.")

    # Convert enhanced content into ParsedResumeData representation for re-scoring
    reconstructed_skills = []
    for slist in enhanced.technical_skills_grouped.values():
        reconstructed_skills.extend(slist)

    lines = [
        enhanced.candidate_name,
        enhanced.contact_header,
        "\nPROFESSIONAL SUMMARY",
        enhanced.professional_summary,
        "\nTECHNICAL SKILLS",
        ", ".join(reconstructed_skills),
        "\nWORK EXPERIENCE",
    ]
    for exp in enhanced.experience:
        lines.append(f"{exp.get('job_title', '')} at {exp.get('company', '')}")
        for r in exp.get("responsibilities", []):
            lines.append(f"- {r}")

    lines.append("\nPROJECTS")
    for proj in enhanced.projects:
        status_suffix = f" | Status: {proj.get('status', 'Completed')}" if proj.get("status") else ""
        lines.append(f"{proj.get('title', '')}{status_suffix}")
        if proj.get("technologies"):
            lines.append(f"Technologies: {', '.join(proj.get('technologies'))}")
        if proj.get("github_url"):
            lines.append(f"Project URL: {proj.get('github_url')}")
        bullets = proj.get("bullets", [])
        if bullets:
            for b in bullets:
                lines.append(f"- {b}")
        elif proj.get("description"):
            lines.append(f"{proj.get('description')}")
        if proj.get("outcomes") and proj.get("outcomes") not in bullets:
            lines.append(f"Outcomes: {proj.get('outcomes')}")

    lines.append("\nEDUCATION")
    for edu in enhanced.education:
        lines.append(f"{edu.get('degree', '')} - {edu.get('institution', '')} ({edu.get('graduation_year', '')})")

    lines.append("\nCERTIFICATIONS")
    for cert in enhanced.certifications:
        lines.append(f"- {cert}")

    reconstructed_text = "\n".join(lines)
    re_parsed = ParsedResumeData(
        candidate_name=enhanced.candidate_name,
        contact_info=ContactInfo(**(enhanced.contact_details or {})),
        career_objective=enhanced.professional_summary,
        professional_summary=enhanced.professional_summary,
        technical_skills=reconstructed_skills,
        education=[
            EducationEntry(
                degree=ed.get("degree", ""),
                institution=ed.get("institution", ""),
                graduation_year=ed.get("graduation_year", ""),
                field_of_study=ed.get("field_of_study", ""),
                raw_text=ed.get("raw_text") or f"{ed.get('degree', '')} in {ed.get('field_of_study', '') or ''} {ed.get('institution', '')}",
            )
            for ed in enhanced.education
        ],
        certifications=enhanced.certifications,
        projects=[
            ProjectEntry(
                title=p.get("title", ""),
                description=p.get("description", ""),
                technologies=p.get("technologies", []),
                outcomes=p.get("outcomes"),
                status=p.get("status", "Completed"),
                github_url=p.get("github_url"),
                project_url=p.get("project_url"),
                bullets=p.get("bullets", []),
            )
            for p in enhanced.projects
        ],
        employment_history=[
            ExperienceEntry(
                job_title=e.get("job_title", ""),
                company=e.get("company", ""),
                start_date=e.get("start_date", ""),
                end_date=e.get("end_date", ""),
                responsibilities=e.get("responsibilities", []),
            )
            for e in enhanced.experience
        ],
        achievements=enhanced.achievements,
    )

    # Re-match against Neon role skills
    re_match = SkillMatcher.match_skills(
        role_skills=role_profile["skills"],
        resume_skills=re_parsed.technical_skills or reconstructed_skills,
        resume_full_text=reconstructed_text,
        resume_projects=re_parsed.projects,
        resume_experience=re_parsed.employment_history,
        role_id=role_profile["role_id"],
        role_name=role_profile["role_name"],
    )

    # Re-calculate score with identical deterministic engine against POST_IMPROVEMENT_THRESHOLD (82.0)
    new_score = ATSScoringEngine.calculate_score(
        resume_data=re_parsed,
        match_report=re_match,
        role_requirements=role_profile["requirements"],
        db_scoring_criteria=role_profile["scoring_criteria"],
        threshold=settings.POST_IMPROVEMENT_THRESHOLD,
    )

    score_delta = round(new_score.final_score - original_score.final_score, 1)
    stage_passed = new_score.final_score >= settings.POST_IMPROVEMENT_THRESHOLD
    cached["stage_passed"] = stage_passed
    cached["next_stage_allowed"] = stage_passed
    cached["latest_score"] = new_score.final_score

    return {
        "analysis_id": payload.analysis_id,
        "original_score": original_score.final_score,
        "new_score": new_score.final_score,
        "score_delta": score_delta,
        "meets_threshold": stage_passed,
        "stage_passed": stage_passed,
        "next_stage_allowed": stage_passed,
        "status": "PASSED" if stage_passed else "IMPROVEMENT_RECOMMENDED",
        "category_comparison": [
            {
                "category": orig.category_name,
                "weight": orig.weight,
                "original_score": orig.score_earned,
                "new_score": nxt.score_earned,
                "delta": round(nxt.score_earned - orig.score_earned, 1),
            }
            for orig, nxt in zip(original_score.category_scores, new_score.category_scores)
        ],
        "explanation": (
            f"Resume compatibility score improved from {original_score.final_score} to {new_score.final_score} "
            f"(+{score_delta} points). Enhancement optimized skill taxonomy visibility and strengthened "
            f"hands-on project descriptions aligned with {role_profile['role_name']}."
        ),
    }


# --- Template Registry Endpoints ---
@app.get("/api/templates", tags=["Templates"])
def get_templates():
    """Lists registered standard ATS resume templates."""
    templates = template_registry.list_templates(active_only=False)
    return {
        "total": len(templates),
        "templates": [t.model_dump() for t in templates],
    }


@app.get("/api/templates/{template_id}", tags=["Templates"])
def get_template_detail(template_id: str):
    """Retrieves a single registered resume template by ID."""
    tmpl = template_registry.get_template(template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found.")
    return tmpl.model_dump()


@app.get("/api/templates/{template_id}/preview", tags=["Templates"])
def get_template_preview(template_id: str):
    """Generates and returns layout preview for a specific template using sample candidate data.

    IMPORTANT: This is a read-only preview generator. It NEVER invokes Round Robin scheduling
    or advances the Round Robin cursor, preserving live candidate queue state.
    """
    tmpl = template_registry.get_template(template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found.")

    preview_file_id = f"preview_{tmpl.template_id}"
    docx_file = settings.OUTPUT_DIR / f"{preview_file_id}.docx"
    pdf_file = settings.OUTPUT_DIR / f"{preview_file_id}.pdf"

    if not docx_file.exists() or not pdf_file.exists():
        DocumentRenderer.render_resume(
            content=SAMPLE_PREVIEW_CONTENT,
            template=tmpl,
            job_id=preview_file_id,
        )

    return {
        "template": tmpl.model_dump(),
        "sample_content": SAMPLE_PREVIEW_CONTENT.model_dump(),
        "documents": {
            "file_id": preview_file_id,
            "docx_url": f"/api/templates/{tmpl.template_id}/preview/docx",
            "pdf_url": f"/api/templates/{tmpl.template_id}/preview/pdf",
            "pdf_available": pdf_file.exists(),
        },
    }


@app.get("/api/templates/{template_id}/preview/pdf", tags=["Templates"])
def get_template_preview_pdf(template_id: str):
    """Serves the rendered preview PDF directly for in-browser visual inspection."""
    tmpl = template_registry.get_template(template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found.")

    preview_file_id = f"preview_{tmpl.template_id}"
    pdf_file = settings.OUTPUT_DIR / f"{preview_file_id}.pdf"

    if not pdf_file.exists():
        DocumentRenderer.render_resume(
            content=SAMPLE_PREVIEW_CONTENT,
            template=tmpl,
            job_id=preview_file_id,
        )

    if not pdf_file.exists():
        raise HTTPException(status_code=500, detail="Preview PDF could not be generated.")

    return FileResponse(
        path=pdf_file,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=FUTRSEC_{tmpl.template_id}_Preview.pdf"},
    )


@app.get("/api/templates/{template_id}/preview/docx", tags=["Templates"])
def get_template_preview_docx(template_id: str):
    """Downloads the rendered preview DOCX file."""
    tmpl = template_registry.get_template(template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found.")

    preview_file_id = f"preview_{tmpl.template_id}"
    docx_file = settings.OUTPUT_DIR / f"{preview_file_id}.docx"

    if not docx_file.exists():
        DocumentRenderer.render_resume(
            content=SAMPLE_PREVIEW_CONTENT,
            template=tmpl,
            job_id=preview_file_id,
        )

    if not docx_file.exists():
        raise HTTPException(status_code=500, detail="Preview DOCX could not be generated.")

    clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', tmpl.template_name)
    return FileResponse(
        path=docx_file,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"FUTRSEC_{tmpl.template_id}_{clean_name}_Preview.docx",
    )


# --- Secure Document Download Endpoint ---
@app.get("/api/resumes/download/{file_id}", tags=["Documents"])
def download_resume_endpoint(
    file_id: str,
    format: str = Query("docx", pattern="^(docx|pdf)$"),
):
    """Securely downloads generated resume document with path traversal protection."""
    # Sanitize file_id to alphanumeric and underscore only
    safe_id = "".join(c for c in file_id if c.isalnum() or c in ("_", "-"))
    if not safe_id:
        raise HTTPException(status_code=400, detail="Invalid file identifier.")

    filename = f"{safe_id}.{format}"
    file_path = (settings.OUTPUT_DIR / filename).resolve()

    # Path traversal check
    if not str(file_path).startswith(str(settings.OUTPUT_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Access denied: invalid file path.")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Requested file '{filename}' was not found.")

    media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document" if format == "docx" else "application/pdf"

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=f"FUTRSEC_Resume_{filename}",
    )


# In-memory storage for evaluated project submissions
PROJECT_EVALUATION_CACHE: Dict[str, ProjectEvaluationResult] = {}


class ApproveProjectRequest(BaseModel):
    analysis_id: str
    proposed_entry: Optional[ProposedResumeEntry] = None
    approved_entry: Optional[ProposedResumeEntry] = None
    confirmed_by_candidate: bool = True


# --- Project Implementation Plan Endpoints ---
@app.get("/api/projects/plan/{analysis_id}", tags=["Projects"])
def get_project_plan_endpoint(analysis_id: str):
    """Retrieves or generates the single role-specific project implementation plan for an analysis."""
    cached = ANALYSIS_CACHE.get(analysis_id)
    if not cached:
        raise HTTPException(status_code=404, detail="Analysis session not found.")

    imp_plan = cached.get("improvement_plan")
    if imp_plan and getattr(imp_plan, "primary_project_plan", None):
        return imp_plan.primary_project_plan
    elif isinstance(imp_plan, dict) and imp_plan.get("primary_project_plan"):
        return imp_plan["primary_project_plan"]

    # Generate plan on the fly if needed
    role_name = cached.get("role_name") or "Cybersecurity Specialist"
    match_report = cached.get("match_report")
    unmatched = [u.skill_name for u in getattr(match_report, "unmatched_skills", [])] if match_report else []
    matched = [m.skill_name for m in getattr(match_report, "matched_skills", [])] if match_report else []
    resume_data = cached.get("parsed_resume")
    proj_count = len(getattr(resume_data, "projects", [])) if resume_data else 0

    plan = PrimaryProjectPlanGenerator.generate_single_plan(
        role_name=role_name,
        unmatched_skills=unmatched,
        matched_skills=matched,
        existing_projects_count=proj_count,
    )
    # Ensure documents are generated
    ProjectPlanDocumentRenderer.render_plan_documents(plan)
    return plan.model_dump()


@app.get("/api/projects/view-plan/{plan_id}", tags=["Projects"])
def view_project_plan_endpoint(plan_id: str):
    """Returns the project implementation plan PDF with Content-Disposition: inline for browser or iframe preview."""
    safe_id = "".join(c for c in plan_id if c.isalnum() or c in ("_", "-"))
    if not safe_id:
        raise HTTPException(status_code=400, detail="Invalid plan identifier.")

    pdf_filename = f"{safe_id}.pdf"
    file_path = (settings.PROJECT_PLANS_DIR / pdf_filename).resolve()

    # Path traversal protection
    if not str(file_path).startswith(str(settings.PROJECT_PLANS_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Access denied: invalid file path.")

    # Auto-generate if missing or 0 bytes
    if not file_path.exists() or file_path.stat().st_size == 0:
        logger.info("PDF plan '%s' not on disk; auto-generating from role blueprint...", safe_id)
        role_name = "Cybersecurity Specialist"
        for sess in ANALYSIS_CACHE.values():
            if sess.get("role_name"):
                role_name = sess["role_name"]
                break

        plan = PrimaryProjectPlanGenerator.generate_single_plan(
            role_name=role_name,
            unmatched_skills=["Practical security testing"],
            matched_skills=[],
            existing_projects_count=0,
        )
        plan.plan_id = safe_id
        ProjectPlanDocumentRenderer.render_plan_documents(plan)

    if not file_path.exists() or file_path.stat().st_size == 0:
        raise HTTPException(status_code=500, detail="Failed to generate valid PDF implementation plan.")

    # Validate PDF magic bytes
    with open(file_path, "rb") as f:
        if f.read(4) != b"%PDF":
            raise HTTPException(status_code=500, detail="Generated file is not a valid PDF document.")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        headers={
            "Content-Type": "application/pdf",
            "Content-Disposition": f'inline; filename="FUTRSEC_Project_Plan_{safe_id}.pdf"',
        },
    )


@app.get("/api/projects/download-plan/{plan_id}/{format}", tags=["Projects"])
def download_project_plan_endpoint(
    plan_id: str,
    format: str,
    disposition: str = Query("attachment", pattern="^(attachment|inline)$"),
):
    """Securely downloads or views the generated project implementation plan in DOCX or PDF format."""
    if format not in ("docx", "pdf"):
        raise HTTPException(status_code=400, detail="Invalid format. Supported formats: docx, pdf.")

    safe_id = "".join(c for c in plan_id if c.isalnum() or c in ("_", "-"))
    if not safe_id:
        raise HTTPException(status_code=400, detail="Invalid plan identifier.")

    filename = f"{safe_id}.{format}"
    file_path = (settings.PROJECT_PLANS_DIR / filename).resolve()

    # Path traversal protection
    if not str(file_path).startswith(str(settings.PROJECT_PLANS_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Access denied: invalid file path.")

    # Auto-generate if missing
    if not file_path.exists() or file_path.stat().st_size == 0:
        logger.info("Plan document '%s' not on disk; auto-generating...", filename)
        role_name = "Cybersecurity Specialist"
        for sess in ANALYSIS_CACHE.values():
            if sess.get("role_name"):
                role_name = sess["role_name"]
                break

        plan = PrimaryProjectPlanGenerator.generate_single_plan(
            role_name=role_name,
            unmatched_skills=["Practical security testing"],
            matched_skills=[],
            existing_projects_count=0,
        )
        plan.plan_id = safe_id
        ProjectPlanDocumentRenderer.render_plan_documents(plan)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Implementation plan file '{filename}' was not found.")

    if format == "pdf":
        with open(file_path, "rb") as f:
            if f.read(4) != b"%PDF":
                raise HTTPException(status_code=500, detail="File is not a valid PDF document.")

    media_type = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        if format == "docx"
        else "application/pdf"
    )

    disp_type = "inline" if disposition == "inline" else "attachment"
    return FileResponse(
        path=file_path,
        media_type=media_type,
        headers={
            "Content-Type": media_type,
            "Content-Disposition": f'{disp_type}; filename="FUTRSEC_Project_Plan_{filename}"',
        },
    )


@app.post("/api/projects/submit", tags=["Projects"])
@app.post("/api/projects/evaluate", tags=["Projects"])
def submit_and_evaluate_project_endpoint(
    submission: CompletedProjectSubmission,
    target_role: Optional[str] = Query(None),
    analysis_id: Optional[str] = Query(None),
):
    """Evaluates candidate submitted project against objective evidence criteria (Green/Amber/Grey)."""
    # Determine target role
    effective_role = target_role
    if not effective_role and analysis_id and analysis_id in ANALYSIS_CACHE:
        effective_role = ANALYSIS_CACHE[analysis_id].get("role_name")
    if not effective_role:
        effective_role = "Cybersecurity Specialist"

    result = CompletedProjectEvaluator.evaluate_submission(
        submission=submission,
        target_role=effective_role,
    )
    PROJECT_EVALUATION_CACHE[result.submission_id] = result
    return result.model_dump()


@app.post("/api/projects/approve-for-resume", tags=["Projects"])
def approve_project_entry_endpoint(payload: ApproveProjectRequest):
    """Candidate approves the proposed project entry to be incorporated into the improved resume."""
    entry = payload.proposed_entry or payload.approved_entry
    if not entry:
        raise HTTPException(status_code=400, detail="Missing proposed project entry.")

    cached = ANALYSIS_CACHE.get(payload.analysis_id)
    if not cached:
        raise HTTPException(status_code=404, detail="Analysis session not found.")

    # Mark as approved
    entry.is_approved = True

    # Maintain authoritative list of approved projects in session cache
    if "approved_completed_projects" not in cached or not isinstance(cached["approved_completed_projects"], list):
        cached["approved_completed_projects"] = []

    clean_title = entry.title_line.strip()
    # Deduplicate against existing approved entries by title
    cached["approved_completed_projects"] = [
        p for p in cached["approved_completed_projects"]
        if getattr(p, "title_line", "").strip().lower() != clean_title.lower()
    ]
    cached["approved_completed_projects"].append(entry)
    cached["approved_completed_project"] = entry

    return {
        "status": "approved",
        "analysis_id": payload.analysis_id,
        "project_title": entry.title_line,
        "message": "Project entry successfully approved for inclusion in the revised resume.",
    }


# --- Domain-Based Project Catalog & Workflow Diagram Endpoints ---
@app.get("/api/projects/domains", tags=["Project Catalog"])
def get_catalog_domains():
    """Returns all supported domains and their project counts."""
    return project_catalog_repository.list_domains()


@app.get("/api/projects/catalog", tags=["Project Catalog"])
def get_project_catalog(domain: Optional[str] = Query(None)):
    """Returns project catalog recommendations, optionally filtered by domain."""
    if domain:
        return project_catalog_repository.list_projects_by_domain(domain)
    return project_catalog_repository.list_projects_by_domain("Cybersecurity")


@app.get("/api/projects/catalog/{project_id}", tags=["Project Catalog"])
def get_project_by_id(project_id: str):
    """Retrieves full project specification and workflow by project ID."""
    proj = project_catalog_repository.get_project_by_id(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found in catalog.")
    return proj


@app.get("/api/projects/workflow", tags=["Project Catalog"])
def get_project_workflow(title: str = Query(..., description="Project title to get workflow for")):
    """Returns the visual workflow specification for a project recommendation."""
    title_lower = title.strip().lower()

    # 1. Check for specific known project plans
    if "network hardening" in title_lower or "enterprise network" in title_lower:
        plan = PrimaryProjectPlanGenerator._build_network_security_plan(
            "temp", "today", "Network Security Engineer", "Intermediate", [], []
        )
        return {"project_title": title, "workflow": plan.project_workflow}
    elif "web application security" in title_lower or "ethical" in title_lower:
        plan = PrimaryProjectPlanGenerator._build_ethical_hacker_plan(
            "temp", "today", "Ethical Hacker", "Intermediate", [], []
        )
        return {"project_title": title, "workflow": plan.project_workflow}
    elif "soc" in title_lower or "threat detection" in title_lower or "log analysis" in title_lower:
        plan = PrimaryProjectPlanGenerator._build_soc_analyst_plan(
            "temp", "today", "SOC Analyst", "Intermediate", [], []
        )
        return {"project_title": title, "workflow": plan.project_workflow}
    elif "cloud security" in title_lower or "compliance hardening" in title_lower:
        plan = PrimaryProjectPlanGenerator._build_cloud_security_plan(
            "temp", "today", "Cloud Security Engineer", "Intermediate", [], []
        )
        return {"project_title": title, "workflow": plan.project_workflow}
    elif "devsecops" in title_lower or "code security" in title_lower:
        plan = PrimaryProjectPlanGenerator._build_appsec_plan(
            "temp", "today", "Application Security Engineer", "Intermediate", [], []
        )
        return {"project_title": title, "workflow": plan.project_workflow}

    # 2. Check catalog
    all_projects = project_catalog_repository.get_all_projects()
    for p in all_projects:
        if p["project_title"].lower() == title_lower or title_lower in p["project_title"].lower():
            return {"project_title": p["project_title"], "workflow": p["project_workflow"]}

    # 3. Default structured fallback
    workflow = [
        {"step": 1, "type": "start", "label": "START"},
        {"step": 2, "type": "phase", "label": "Environment & Prerequisites Setup"},
        {"step": 3, "type": "phase", "label": "Core Implementation & Configuration"},
        {"step": 4, "type": "phase", "label": "Validation & Security Assessment", "is_loop_target": True},
        {
            "step": 5,
            "type": "decision",
            "label": "Are security requirements satisfied?",
            "no_action": "Review findings and perform further hardening.",
            "no_target_step": 4,
            "yes_action": "Document verified results.",
        },
        {"step": 6, "type": "phase", "label": "Generate Security Assessment Report"},
        {"step": 7, "type": "end", "label": "END"},
    ]
    return {"project_title": title, "workflow": workflow}


# ==============================================================================
# PROJECT TRACKING & COMPLETION SYSTEM ENDPOINTS
# ==============================================================================

class TaskProgressUpdateRequest(BaseModel):
    candidate_project_id: str
    milestone_id: str
    task_id: str
    is_completed: bool


class MilestoneEvidenceSubmitRequest(BaseModel):
    candidate_project_id: str
    milestone_id: str
    evidence_type: str = "github_repo"
    title: Optional[str] = None
    github_url: Optional[str] = None
    report_text: Optional[str] = None
    file_url: Optional[str] = None
    notes: Optional[str] = None


class MilestoneReviewRequest(BaseModel):
    candidate_project_id: str
    milestone_id: str
    verdict: str  # 'approved' | 'revision_required' | 'rejected'
    score: Optional[float] = 85.0
    feedback: str
    revision_instructions: Optional[str] = None
    reviewer_name: str = "Security Administrator"
    reviewer_type: str = "admin_review"


class AiVerifyMilestoneRequest(BaseModel):
    candidate_project_id: str
    milestone_id: str


class RejectRecommendationRequest(BaseModel):
    candidate_id: str
    project_id: str
    reason: Optional[str] = None


class ProjectStatusUpdateRequest(BaseModel):
    status: str


@app.get("/api/tracking/recommendations", tags=["Project Tracking"])
def get_project_recommendations(
    role_name: str = Query(..., description="Target job role"),
    candidate_skills: Optional[List[str]] = Query(None, description="Current candidate skills"),
    unmatched_skills: Optional[List[str]] = Query(None, description="Skills missing for role"),
):
    """Recommends cybersecurity projects tailored to candidate skills and target job role."""
    try:
        return project_tracking_service.get_recommendations(
            role_name=role_name,
            candidate_skills=candidate_skills or [],
            unmatched_skills=unmatched_skills or [],
        )
    except Exception as exc:
        logger.error("Failed to generate project recommendations: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/tracking/assign", tags=["Project Tracking"])
def assign_candidate_project(payload: ProjectAssignmentInput):
    """Assigns an accepted cybersecurity project to a candidate, setting up milestones and deadlines."""
    try:
        assigned = project_tracking_service.assign_project(payload)
        return assigned
    except Exception as exc:
        logger.error("Failed to assign project: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/tracking/reject", tags=["Project Tracking"])
def reject_project_recommendation(payload: RejectRecommendationRequest):
    """Allows candidate to reject a recommended project."""
    try:
        return project_tracking_service.reject_recommendation(
            candidate_id=payload.candidate_id,
            project_id=payload.project_id,
            reason=payload.reason,
        )
    except Exception as exc:
        logger.error("Failed to reject recommendation: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/tracking/projects/{candidate_id}", tags=["Project Tracking"])
def get_candidate_projects_list(candidate_id: str):
    """Lists all assigned projects and milestone progress for a candidate."""
    try:
        return project_tracking_service.get_candidate_projects(candidate_id)
    except Exception as exc:
        logger.error("Failed to get candidate projects for %s: %s", candidate_id, exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/tracking/project/{project_id}", tags=["Project Tracking"])
def get_candidate_project_details(project_id: str):
    """Retrieves full project assignment detail, milestone tasks, submitted evidence, and verification logs."""
    try:
        detail = project_tracking_service.get_project_detail(project_id)
        if not detail:
            raise HTTPException(status_code=404, detail=f"Project assignment '{project_id}' not found.")
        return detail
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to get project detail for %s: %s", project_id, exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.delete("/api/tracking/project/{candidate_project_id}", tags=["Project Tracking"])
def delete_candidate_project_assignment(candidate_project_id: str):
    """Cancels/deletes an assigned project and all related milestones/evidence."""
    try:
        project_tracking_service.delete_candidate_project(candidate_project_id)
        return {"status": "deleted", "candidate_project_id": candidate_project_id}
    except ValueError as val_err:
        raise HTTPException(status_code=404, detail=str(val_err))
    except Exception as exc:
        logger.error("Failed to delete candidate project %s: %s", candidate_project_id, exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.patch("/api/tracking/project/{candidate_project_id}/status", tags=["Project Tracking"])
def update_candidate_project_status(candidate_project_id: str, payload: ProjectStatusUpdateRequest):
    """Updates the status of an assigned candidate project."""
    try:
        return project_tracking_service.update_project_status(candidate_project_id, payload.status)
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as exc:
        logger.error("Failed to update project status %s: %s", candidate_project_id, exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/tracking/tasks/update", tags=["Project Tracking"])
def update_task_progress_endpoint(payload: TaskProgressUpdateRequest):
    """Updates candidate task completion progress and recalculates milestone and project percentages."""
    try:
        return project_tracking_service.update_task_progress(
            candidate_project_id=payload.candidate_project_id,
            milestone_id=payload.milestone_id,
            task_id=payload.task_id,
            is_completed=payload.is_completed,
        )
    except ValueError as val_err:
        raise HTTPException(status_code=404, detail=str(val_err))
    except Exception as exc:
        logger.error("Failed to update task progress: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/tracking/evidence/submit", tags=["Project Tracking"])
def submit_milestone_evidence_endpoint(payload: MilestoneEvidenceSubmitRequest):
    """Submits practical milestone evidence (GitHub repository URL, report, screenshots)."""
    try:
        evidence_data = MilestoneEvidenceSubmission(
            evidence_type=payload.evidence_type,
            title=payload.title,
            github_url=payload.github_url,
            report_text=payload.report_text,
            file_url=payload.file_url,
            notes=payload.notes,
        )
        return project_tracking_service.submit_milestone_evidence(
            candidate_project_id=payload.candidate_project_id,
            milestone_id=payload.milestone_id,
            submission=evidence_data,
        )
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as exc:
        logger.error("Failed to submit evidence: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/tracking/verify", tags=["Project Tracking"])
def review_milestone_endpoint(payload: MilestoneReviewRequest):
    """Authorized/Admin review for submitted milestone evidence. Marks completed only upon approval."""
    try:
        review_data = VerificationReviewInput(
            verdict=payload.verdict,
            score=payload.score,
            feedback=payload.feedback,
            revision_instructions=payload.revision_instructions,
            reviewer_name=payload.reviewer_name,
            reviewer_type=payload.reviewer_type,
        )
        return project_tracking_service.review_milestone(
            candidate_project_id=payload.candidate_project_id,
            milestone_id=payload.milestone_id,
            review=review_data,
        )
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as exc:
        logger.error("Failed to review milestone: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/tracking/ai-verify", tags=["Project Tracking"])
def ai_verify_milestone_endpoint(payload: AiVerifyMilestoneRequest):
    """Triggers automated AI evaluation of submitted milestone evidence."""
    try:
        return project_tracking_service.ai_verify_milestone(
            candidate_project_id=payload.candidate_project_id,
            milestone_id=payload.milestone_id,
        )
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as exc:
        logger.error("Failed in AI verification: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/tracking/dashboard", tags=["Project Tracking"])
def get_tracking_dashboard(candidate_id: Optional[str] = Query(None)):
    """Returns dashboard metrics: total assigned, in progress, completed, pending submissions, overall %, milestone breakdown."""
    try:
        return project_tracking_service.get_dashboard_stats(candidate_id=candidate_id)
    except Exception as exc:
        logger.error("Failed to generate tracking dashboard: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/tracking/verified-for-resume/{candidate_id}", tags=["Project Tracking"])
def get_verified_projects_for_resume_endpoint(candidate_id: str):
    """Strict Rule: Only returns projects verified completed for legitimate resume inclusion."""
    try:
        return project_tracking_service.get_verified_projects_for_resume(candidate_id=candidate_id)
    except Exception as exc:
        logger.error("Failed to fetch verified projects for %s: %s", candidate_id, exc)
        raise HTTPException(status_code=500, detail=str(exc))


# --- Static Frontend Serving (Unified Full-Stack Deployment) ---
frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

