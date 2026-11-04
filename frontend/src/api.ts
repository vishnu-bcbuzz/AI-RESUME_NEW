import {
  JobRole,
  AnalysisResponse,
  ImprovementResponse,
  RescoreResponse,
  ResumeTemplate,
  NextStageResponse,
  ConfirmedSkillItem,
  ImprovementPlanItem,
  CompletedProjectSubmission,
  ProjectEvaluationResult,
  ProposedResumeEntry,
  CandidateProject,
  ProjectMilestone,
  ProjectRecommendation,
  TrackingDashboardStats,
  VerifiedProjectForResume,
} from './types';

const API_BASE = '';

async function extractErrorMessage(res: Response, fallback: string): Promise<string> {
  try {
    const errorData = await res.json();
    if (typeof errorData.detail === 'string' && errorData.detail.trim().length > 0) {
      return errorData.detail;
    }
    if (Array.isArray(errorData.detail) && errorData.detail.length > 0) {
      return errorData.detail
        .map((e: any) => {
          if (typeof e === 'string') return e;
          const loc = Array.isArray(e.loc) ? e.loc.join(' -> ') : '';
          const msg = e.msg || e.message || JSON.stringify(e);
          return loc ? `${loc}: ${msg}` : msg;
        })
        .join('; ');
    }
    if (typeof errorData.message === 'string' && errorData.message.trim().length > 0) {
      return errorData.message;
    }
  } catch {
    // Response was not JSON (e.g. plain text or HTML 500/502/504)
    try {
      const text = await res.text();
      if (text && text.trim().length > 0 && text.length < 300 && !text.includes('<!DOCTYPE')) {
        return `Server error (${res.status}): ${text.trim()}`;
      }
    } catch {
      // Ignore text extraction errors
    }
  }
  return `${fallback} (HTTP ${res.status})`;
}

export async function fetchHealth(): Promise<any> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(await extractErrorMessage(res, 'Health check failed'));
  return res.json();
}

export async function fetchRoles(search?: string): Promise<JobRole[]> {
  const url = search ? `${API_BASE}/api/roles?search=${encodeURIComponent(search)}` : `${API_BASE}/api/roles`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(await extractErrorMessage(res, 'Failed to retrieve cybersecurity job roles'));
  const data = await res.json();
  return data.roles;
}

export async function fetchRoleDetails(roleId: number): Promise<any> {
  const res = await fetch(`${API_BASE}/api/roles/${roleId}`);
  if (!res.ok) throw new Error(await extractErrorMessage(res, `Failed to retrieve role profile for ID ${roleId}`));
  return res.json();
}

export async function fetchTemplates(): Promise<ResumeTemplate[]> {
  const res = await fetch(`${API_BASE}/api/templates`);
  if (!res.ok) throw new Error(await extractErrorMessage(res, 'Failed to retrieve template registry'));
  const data = await res.json();
  return data.templates;
}

export async function fetchTemplatePreview(templateId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/templates/${templateId}/preview`);
  if (!res.ok) throw new Error(await extractErrorMessage(res, `Failed to retrieve preview for template ${templateId}`));
  return res.json();
}

export async function analyzeResume(
  file: File,
  roleId: number,
  timeoutMs: number = 90000
): Promise<AnalysisResponse> {
  if (!file) {
    throw new Error('No resume file selected. Please select a valid PDF or DOCX resume.');
  }
  if (!roleId || isNaN(roleId)) {
    throw new Error('Invalid cybersecurity role selected. Please select a valid role.');
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const formData = new FormData();
  formData.append('file', file, file.name || 'resume.pdf');
  formData.append('role_id', roleId.toString());

  try {
    const res = await fetch(`${API_BASE}/api/resumes/analyze`, {
      method: 'POST',
      body: formData,
      signal: controller.signal,
    });

    if (!res.ok) {
      const errorMsg = await extractErrorMessage(res, 'Resume analysis failed');
      throw new Error(errorMsg);
    }

    return await res.json();
  } catch (err: any) {
    if (err.name === 'AbortError') {
      throw new Error(
        `Resume evaluation request timed out after ${timeoutMs / 1000} seconds. Please verify server connectivity and retry.`
      );
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function improveResume(
  analysisId: string,
  attemptNumber: number = 1,
  candidateNotes?: string,
  confirmedSkills?: ConfirmedSkillItem[],
  permissionGranted: boolean = true,
  approvedPlanItems?: ImprovementPlanItem[],
  approvedCompletedProject?: ProposedResumeEntry | null,
  approvedCompletedProjects?: ProposedResumeEntry[],
  selectionMode: 'automatic' | 'manual' = 'automatic',
  templateId?: string
): Promise<ImprovementResponse> {
  const res = await fetch(`${API_BASE}/api/resumes/improve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      analysis_id: analysisId,
      attempt_number: attemptNumber,
      candidate_notes: candidateNotes || undefined,
      confirmed_skills: confirmedSkills || [],
      approved_plan_items: approvedPlanItems || [],
      approved_completed_project: approvedCompletedProject || undefined,
      approved_completed_projects: approvedCompletedProjects || [],
      permission_granted: permissionGranted,
      selection_mode: selectionMode,
      template_id: selectionMode === 'manual' ? templateId : undefined,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Failed to generate improved resume' }));
    throw new Error(errorData.detail || 'Improvement failed');
  }

  return res.json();
}

export async function submitCompletedProject(
  submission: CompletedProjectSubmission
): Promise<ProjectEvaluationResult> {
  const res = await fetch(`${API_BASE}/api/projects/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(submission),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to evaluate completed project' }));
    throw new Error(err.detail || 'Completed project evaluation failed');
  }

  return res.json();
}

export async function approveProjectForResume(
  analysisId: string,
  entry: ProposedResumeEntry,
  confirmed: boolean = true
): Promise<any> {
  const res = await fetch(`${API_BASE}/api/projects/approve-for-resume`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      analysis_id: analysisId,
      proposed_entry: entry,
      approved_entry: entry,
      confirmed_by_candidate: confirmed,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to approve project for resume' }));
    throw new Error(err.detail || 'Project resume approval failed');
  }

  return res.json();
}

export async function fetchProjectPlan(analysisId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/projects/plan/${encodeURIComponent(analysisId)}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to retrieve project implementation plan' }));
    throw new Error(err.detail || 'Plan retrieval failed');
  }
  return res.json();
}

export async function proceedToNextStage(analysisId: string): Promise<NextStageResponse> {
  const res = await fetch(`${API_BASE}/api/resumes/next-stage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ analysis_id: analysisId }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Failed to advance to next stage' }));
    throw new Error(errorData.detail || 'Next stage transition denied');
  }

  return res.json();
}

export async function acceptAndRescore(analysisId: string): Promise<RescoreResponse> {
  const res = await fetch(`${API_BASE}/api/resumes/accept-and-rescore`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ analysis_id: analysisId }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Failed to recalculate score' }));
    throw new Error(errorData.detail || 'Re-scoring failed');
  }

  return res.json();
}

// ==============================================================================
// PROJECT COMPLETION TRACKING API METHODS
// ==============================================================================

export async function fetchProjectRecommendations(
  roleName: string,
  candidateSkills: string[] = [],
  unmatchedSkills: string[] = []
): Promise<ProjectRecommendation[]> {
  const params = new URLSearchParams();
  params.append('role_name', roleName);
  candidateSkills.forEach((s) => params.append('candidate_skills', s));
  unmatchedSkills.forEach((s) => params.append('unmatched_skills', s));

  const res = await fetch(`${API_BASE}/api/tracking/recommendations?${params.toString()}`);
  if (!res.ok) {
    throw new Error(await extractErrorMessage(res, 'Failed to retrieve project recommendations'));
  }
  return res.json();
}

export async function assignProject(payload: {
  candidate_id: string;
  project_id: string;
  role_name: string;
  candidate_name?: string;
  candidate_email?: string;
  custom_deadline_days?: number;
}): Promise<CandidateProject> {
  const res = await fetch(`${API_BASE}/api/tracking/assign`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(await extractErrorMessage(res, 'Failed to assign project'));
  }
  return res.json();
}

export async function rejectProjectRecommendation(payload: {
  candidate_id: string;
  project_id: string;
  reason?: string;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/api/tracking/reject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(await extractErrorMessage(res, 'Failed to reject recommendation'));
  }
  return res.json();
}

export async function fetchCandidateProjects(candidateId: string): Promise<CandidateProject[]> {
  const res = await fetch(`${API_BASE}/api/tracking/projects/${encodeURIComponent(candidateId)}`);
  if (!res.ok) {
    throw new Error(await extractErrorMessage(res, 'Failed to retrieve candidate projects'));
  }
  return res.json();
}

export async function fetchCandidateProjectDetail(projectId: string): Promise<CandidateProject> {
  const res = await fetch(`${API_BASE}/api/tracking/project/${encodeURIComponent(projectId)}`);
  if (!res.ok) {
    throw new Error(await extractErrorMessage(res, 'Failed to retrieve project detail'));
  }
  return res.json();
}

export async function deleteCandidateProject(candidateProjectId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/tracking/project/${encodeURIComponent(candidateProjectId)}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error(await extractErrorMessage(res, 'Failed to delete candidate project'));
  }
  return res.json();
}

export async function updateCandidateProjectStatus(
  candidateProjectId: string,
  status: string
): Promise<any> {
  const res = await fetch(`${API_BASE}/api/tracking/project/${encodeURIComponent(candidateProjectId)}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) {
    throw new Error(await extractErrorMessage(res, 'Failed to update project status'));
  }
  return res.json();
}

export async function updateTaskProgress(payload: {
  candidate_project_id: string;
  milestone_id: string;
  task_id: string;
  is_completed: boolean;
}): Promise<{
  candidate_project_id: string;
  milestone_id: string;
  task_id: string;
  is_completed: boolean;
  milestone_completed_tasks: number;
  milestone_total_tasks: number;
  milestone_status: string;
  project_completion_percentage: number;
}> {
  const res = await fetch(`${API_BASE}/api/tracking/tasks/update`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(await extractErrorMessage(res, 'Failed to update task progress'));
  }
  return res.json();
}

export async function submitMilestoneEvidence(payload: {
  candidate_project_id: string;
  milestone_id: string;
  evidence_type?: string;
  title?: string;
  github_url?: string;
  report_text?: string;
  file_url?: string;
  notes?: string;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/api/tracking/evidence/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(await extractErrorMessage(res, 'Failed to submit milestone evidence'));
  }
  return res.json();
}

export async function reviewMilestone(payload: {
  candidate_project_id: string;
  milestone_id: string;
  verdict: 'approved' | 'revision_required' | 'rejected' | string;
  score?: number;
  feedback: string;
  revision_instructions?: string;
  reviewer_name?: string;
  reviewer_type?: string;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/api/tracking/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(await extractErrorMessage(res, 'Failed to submit verification review'));
  }
  return res.json();
}

export async function aiVerifyMilestone(payload: {
  candidate_project_id: string;
  milestone_id: string;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/api/tracking/ai-verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(await extractErrorMessage(res, 'AI verification failed'));
  }
  return res.json();
}

export async function fetchTrackingDashboard(candidateId?: string): Promise<TrackingDashboardStats> {
  const url = candidateId
    ? `${API_BASE}/api/tracking/dashboard?candidate_id=${encodeURIComponent(candidateId)}`
    : `${API_BASE}/api/tracking/dashboard`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(await extractErrorMessage(res, 'Failed to load tracking dashboard'));
  }
  return res.json();
}

export async function fetchVerifiedProjectsForResume(candidateId: string): Promise<VerifiedProjectForResume[]> {
  const res = await fetch(`${API_BASE}/api/tracking/verified-for-resume/${encodeURIComponent(candidateId)}`);
  if (!res.ok) {
    throw new Error(await extractErrorMessage(res, 'Failed to retrieve verified projects'));
  }
  return res.json();
}
