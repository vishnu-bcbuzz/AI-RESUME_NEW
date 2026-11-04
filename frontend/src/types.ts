export interface JobRole {
  role_id: number;
  role_name: string;
  role_description?: string;
  created_at?: string;
}

export interface RoleSkill {
  skill_id: number;
  role_id: number;
  skill_name: string;
  importance: 'core' | 'preferred' | 'additional';
}

export interface RoleRequirement {
  requirement_id: number;
  role_id: number;
  requirement_type: string;
  requirement_description: string;
  importance?: string;
}

export interface ScoringCriterion {
  criteria_id: number;
  role_id: number;
  category: string;
  weight: number;
}

export interface CategoryScore {
  category_name: string;
  weight: number;
  score_earned: number;
  percentage: number;
  explanation: string;
  details?: Record<string, any>;
}

export interface ATSScoreResult {
  role_id: number;
  role_name: string;
  final_score: number;
  max_score: number;
  threshold: number;
  meets_threshold: boolean;
  status: string;
  category_scores: CategoryScore[];
  summary_explanation: string;
}

export interface SkillMatch {
  skill_name: string;
  importance: 'core' | 'preferred' | 'additional';
  status: 'matched' | 'not_demonstrated';
  matched_in_sections: string[];
  evidence_snippet?: string;
  confidence: number;
}

export interface MatchReport {
  role_id: number;
  role_name: string;
  total_role_skills: number;
  matched_skills: SkillMatch[];
  unmatched_skills: SkillMatch[];
  matched_core_count: number;
  total_core_count: number;
  matched_preferred_count: number;
  total_preferred_count: number;
  matched_additional_count: number;
  total_additional_count: number;
}

export interface GapRecommendation {
  priority: 'high' | 'medium' | 'low';
  category: string;
  title: string;
  description: string;
  suggested_action: string;
  is_future_action: boolean;
}

export interface ConfirmedSkillItem {
  skill_name: string;
  proficiency: 'hands_on' | 'basic_familiarity' | 'not_used' | 'beginner' | 'intermediate' | 'advanced' | 'not_yet' | string;
  context_source?: string;
  tasks_performed?: string;
  interview_demonstration?: string;
}

export interface SkillConfirmationQuestion {
  skill_name: string;
  importance: 'core' | 'preferred' | 'additional';
  category: string;
  prompt_question: string;
  options: Array<{
    value: 'hands_on' | 'basic_familiarity' | 'not_used';
    label: string;
    description: string;
  }>;
  context_options: string[];
}

export interface GapAnalysisReport {
  role_id: number;
  role_name: string;
  matched_skills_count: number;
  not_demonstrated_count: number;
  demonstrated_skills: Array<{
    skill_name: string;
    importance: string;
    sections: string[];
    evidence?: string;
    status?: string;
  }>;
  skills_requiring_confirmation?: SkillConfirmationQuestion[];
  skills_not_demonstrated?: Array<{
    skill_name: string;
    importance: string;
    status: string;
  }>;
  candidate_confirmed_skills?: Array<{
    skill_name: string;
    proficiency: string;
  }>;
  missing_core_skills: string[];
  missing_preferred_skills: string[];
  missing_additional_skills: string[];
  relevant_certifications_held: string[];
  project_evidence_summary: string[];
  experience_evidence_summary: string[];
  prioritized_recommendations: GapRecommendation[];
  future_learning_recommendations?: GapRecommendation[];
}

export interface WeakCategoryEvaluation {
  category_name: string;
  category_key: string;
  current_score: number;
  max_score: number;
  percentage: number;
  is_weak: boolean;
  what_is_missing: string;
  affected_job_requirements: string[];
  specific_improvements: string[];
  required_candidate_info: string;
  resume_sections_to_update: string[];
  role_relevance_reason: string;
  action_nature: 'confirm_existing' | 'improve_presentation' | 'acquire_new_skills';
  confirmation_needed?: boolean;
  recommended_next_action?: string;
}

export interface SkillRecommendationDetail {
  skill_name: string;
  requirement_classification: 'mandatory' | 'preferred' | 'additional';
  current_evidence: string;
  importance_for_role: string;
  gap_explanation: string;
  suggested_resume_section: string;
  candidate_confirmation_question: string;
  recommended_action: string;
  if_confirmed: string;
  if_basic_exposure: string;
  if_never_used: string;
  available_actions: string[];
  candidate_action_selected?: string;
  skill_state: string;
  learning_resources: string[];
}

export interface PracticalProjectTemplate {
  project_title: string;
  target_role: string;
  level?: 'Beginner' | 'Intermediate' | 'Advanced' | string;
  skills_demonstrated: string[];
  proposed_technologies: string[];
  project_objective: string;
  suggested_implementation_tasks: string[];
  expected_deliverables: string;
  suggested_resume_bullet: string;
  is_future_project: boolean;
  candidate_has_completed_similar?: boolean;
  plan_id?: string;
  docx_download_url?: string;
  pdf_download_url?: string;
  weaknesses_addressed?: string[];
  project_workflow?: any[];
}

export interface CompletedProjectSubmission {
  analysis_id?: string;
  project_title: string;
  project_description: string;
  skills_used: string[];
  technologies_used: string[];
  implementation_tasks_completed: string[];
  testing_performed: string;
  verified_outcomes: string;
  status: 'completed' | 'in_progress';
  github_url?: string;
  documentation_notes?: string;
  confirmation_statement: boolean;
}

export interface CandidateExistingProject {
  id: string;
  project_title: string;
  project_description: string;
  github_url?: string;
  technologies_used: string[];
  status: 'completed' | 'in_progress';
  evaluation?: ProjectEvaluationResult | null;
  is_approved_for_resume?: boolean;
  approved_entry?: ProposedResumeEntry | null;
}

export interface EvaluatedCriterion {
  name: string;
  status: 'demonstrated' | 'improvement_needed' | 'not_yet_submitted';
  finding: string;
  evidence_snippet?: string;
  recommendation?: string;
}

export interface ProposedResumeEntry {
  title_line: string;
  bullets: string[];
  status_label: string;
  is_approved: boolean;
}

export interface ProjectEvaluationResult {
  submission_id: string;
  project_title: string;
  status: 'completed' | 'in_progress';
  verdict: string;
  verdict_explanation: string;
  demonstrated: EvaluatedCriterion[];
  improvement_needed: EvaluatedCriterion[];
  not_yet_submitted: EvaluatedCriterion[];
  recommended_next_action: string;
  proposed_resume_entry: ProposedResumeEntry;
  candidate_confirmed: boolean;
}

export interface CertificationRecommendationDetail {
  cert_name: string;
  relevance_to_role: string;
  db_classification: string;
  capability_demonstrated: string;
  candidate_status: 'already_earned' | 'currently_pursuing' | 'planning_to_pursue' | 'not_interested';
  recommended_next_action: string;
  verification_details?: string;
}

export interface ImprovementPlanItem {
  item_id: string;
  priority?: 'high' | 'medium' | 'low';
  item_type?: 'category_overview' | 'skill_card' | 'project_recommendation' | 'cert_recommendation' | 'section_polish';
  category: string;
  category_key: string;
  title?: string;
  current_score?: number;
  max_score?: number;
  current_issue: string;
  recommended_change: string;
  relevance_reason: string;
  required_info: string;
  expected_improvement: string;
  action_type: string;
  status: 'pending' | 'approved' | 'edited' | 'skipped';
  is_weak_category?: boolean;
  action_nature?: 'confirm_existing' | 'improve_presentation' | 'acquire_new_skills';
  affected_job_requirements?: string[];
  resume_sections_to_update?: string[];
  skill_details?: SkillRecommendationDetail;
  project_recommendation?: PracticalProjectTemplate;
  cert_recommendation?: CertificationRecommendationDetail;
  follow_up_questions?: any[];
  candidate_response?: Record<string, any>;
}

export interface ResumeImprovementPlan {
  initial_score: number;
  threshold: number;
  meets_threshold: boolean;
  role_name?: string;
  weak_categories: string[];
  category_evaluations?: WeakCategoryEvaluation[];
  high_priority_items?: ImprovementPlanItem[];
  medium_priority_items?: ImprovementPlanItem[];
  additional_enhancements?: ImprovementPlanItem[];
  items: ImprovementPlanItem[];
  summary_advice: string;
  primary_project_plan?: any;
}

export interface AnalysisResponse {
  analysis_id: string;
  filename: string;
  role_id: number;
  role_name: string;
  document_metadata: Record<string, any>;
  security_flags: {
    injection_detected: boolean;
  };
  parsed_resume: Record<string, any>;
  match_report: MatchReport;
  score_result: ATSScoreResult;
  gap_analysis: GapAnalysisReport;
  improvement_plan?: ResumeImprovementPlan;
  demonstrated_skills?: any[];
  skills_not_demonstrated?: any[];
  relevant_certifications_held?: string[];
  education_relevance?: Record<string, any>;
  professional_summary_quality?: string;
  required_qualifications?: RoleRequirement[];
  relevant_projects_and_experience?: {
    projects: string[];
    experience: string[];
  };
  stage1_ai?: {
    provider: string;
    model: string;
    status: string;
    output?: any;
    error?: string;
    exact_issue?: string;
    troubleshooting?: string;
  };
  evidence_gaps?: Array<{ skill_name: string; importance?: string; reason?: string }>;
  project_evaluations?: any[];
  qualification_evaluations?: Record<string, any>;
  gemini_recommendations?: string[];
  action_required: 'proceed' | 'offer_improvement';
  stage_passed?: boolean;
  next_stage_allowed?: boolean;
  threshold?: number;
  post_threshold?: number;
  max_attempts?: number;
}

export interface ResumeTemplate {
  template_id: string;
  template_name: string;
  description: string;
  is_active: boolean;
  supported_formats: string[];
  role_category_tags: string[];
  style_config: Record<string, any>;
}

export interface ImprovementAttempt {
  attempt: number;
  type: string;
  score: number;
  delta?: number;
  template_name?: string;
  stage_passed?: boolean;
}

export interface AppliedImprovementCard {
  section_name: string;
  title: string;
  before_issue: string;
  after_change: string;
  why_it_helps: string;
  status: string;
  verified: boolean;
}

export interface RemainingOpportunityCard {
  requirement_name: string;
  category: string;
  importance: string;
  why_it_matters: string;
  guidance: string;
}

export interface FailedImprovementCard {
  section_name: string;
  issue: string;
  action_required: string;
}

export interface ImprovementResponse {
  job_id: string;
  analysis_id: string;
  role_name: string;
  attempt_number: number;
  max_attempts: number;
  can_retry: boolean;
  threshold: number;
  initial_score: number;
  original_score: number;
  new_score: number;
  score_delta: number;
  stage_passed: boolean;
  next_stage_allowed: boolean;
  status: string;
  selection_mode?: 'automatic' | 'manual';
  assigned_template: {
    template_id: string;
    template_name: string;
    description: string;
    style_config: Record<string, any>;
    selection_mode?: 'automatic' | 'manual';
  };
  enhanced_content: {
    candidate_name: string;
    contact_header: string;
    professional_headline?: string;
    professional_summary: string;
    technical_skills_grouped: Record<string, string[]>;
    experience: any[];
    internships?: any[];
    projects: any[];
    education: any[];
    certifications: string[];
    achievements: string[];
    confirmed_skills_included?: string[];
    unverified_skills_excluded?: string[];
    sections_rewritten?: string[];
    future_learning_recommendations?: string[];
    pending_confirmations: string[];
    generator_mode: string;
    attempt_number?: number;
  };
  confirmed_skills_included?: string[];
  unverified_skills_excluded?: string[];
  sections_rewritten?: string[];
  future_learning_recommendations?: string[];
  approved_improvements_applied?: string[];
  pursuing_certifications?: string[];
  documents: {
    docx_url: string;
    pdf_url: string | null;
    pdf_available: boolean;
    pdf_status_note: string;
  };
  category_comparison: Array<{
    category: string;
    weight: number;
    original_score: number;
    new_score: number;
    delta: number;
    evidence_supporting?: string;
    approved_improvement_applied?: string;
    remaining_gaps?: string;
    no_increase_explanation?: string;
  }>;
  attempts_history: ImprovementAttempt[];
  remaining_gaps?: GapAnalysisReport;
  applied_improvements?: AppliedImprovementCard[];
  remaining_opportunities?: RemainingOpportunityCard[];
  failed_improvements?: FailedImprovementCard[];
  re_scored_match_report?: MatchReport;
  explanation?: string;
}

export interface RescoreResponse {
  analysis_id: string;
  original_score: number;
  new_score: number;
  score_delta: number;
  meets_threshold: boolean;
  stage_passed?: boolean;
  next_stage_allowed?: boolean;
  status: string;
  category_comparison: Array<{
    category: string;
    weight: number;
    original_score: number;
    new_score: number;
    delta: number;
  }>;
  explanation: string;
}

export interface NextStageResponse {
  status: string;
  message: string;
  analysis_id: string;
  final_verified_score: number;
  role_id?: number;
  role_name?: string;
  stage: string;
  next_stage_url: string;
}

// ==============================================================================
// PROJECT COMPLETION TRACKING SYSTEM TYPES
// ==============================================================================

export type ProjectTrackingStatus =
  | 'Not Started'
  | 'In Progress'
  | 'Submitted'
  | 'Under Review'
  | 'Revision Required'
  | 'Completed';

export interface MilestoneTask {
  id: string;
  task_text: string;
  is_completed: boolean;
  completed_at?: string | null;
}

export interface MilestoneEvidence {
  id: string;
  milestone_id: string;
  candidate_project_id?: string;
  evidence_type: string;
  title?: string;
  github_url?: string;
  report_text?: string;
  file_url?: string;
  notes?: string;
  submitted_at: string;
}

export interface VerificationHistoryEntry {
  id: string;
  candidate_project_id?: string;
  milestone_id?: string;
  verified_by: string;
  verification_type: string;
  verdict: 'approved' | 'revision_required' | 'rejected' | string;
  score?: number;
  feedback: string;
  revision_instructions?: string;
  created_at: string;
}

export interface ProjectMilestone {
  id: string;
  candidate_project_id: string;
  milestone_number: number;
  title: string;
  objective?: string;
  tasks: MilestoneTask[];
  technologies_used: string[];
  expected_output?: string;
  deadline?: string;
  status: ProjectTrackingStatus;
  completed_tasks_count: number;
  total_tasks_count: number;
  evidence?: MilestoneEvidence[];
  verification_history?: VerificationHistoryEntry[];
  created_at?: string;
  updated_at?: string;
}

export interface CandidateProject {
  id: string;
  candidate_id: string;
  candidate_name?: string;
  candidate_email?: string;
  project_id: string;
  project_title: string;
  role_name: string;
  domain: string;
  difficulty_level: string;
  status: ProjectTrackingStatus;
  deadline?: string;
  started_at?: string;
  completed_at?: string;
  completion_percentage: number;
  is_verified: boolean;
  verified_at?: string;
  verified_by?: string;
  verification_notes?: string;
  eligible_for_resume: boolean;
  added_to_resume: boolean;
  created_at: string;
  milestones?: ProjectMilestone[];
  overall_verification_history?: VerificationHistoryEntry[];
}

export interface ProjectRecommendation {
  project_id: string;
  project_title: string;
  domain: string;
  difficulty_level: string;
  estimated_duration_hours?: number;
  description?: string;
  learning_objectives?: string[];
  required_technologies?: string[];
  skills_demonstrated?: string[];
  total_phases: number;
  total_tasks: number;
  relevance_score: number;
  match_reasons: string[];
  phases_preview: Array<{
    phase_number: number;
    title: string;
    task_count: number;
  }>;
}

export interface TrackingDashboardStats {
  total_assigned: number;
  in_progress: number;
  completed: number;
  pending_submissions: number;
  under_review: number;
  revision_required: number;
  not_started: number;
  overall_completion_percentage: number;
  milestone_stats: {
    total: number;
    completed: number;
    submitted: number;
    revision_required: number;
    in_progress: number;
    not_started: number;
  };
  projects: CandidateProject[];
}

export interface VerifiedProjectForResume {
  candidate_project_id: string;
  project_id: string;
  title: string;
  status: string;
  status_label: string;
  role_name: string;
  technologies: string[];
  bullets: string[];
  verified_at?: string;
  verified_by?: string;
}
