import React, { useState } from 'react';
import {
  Award,
  CheckCircle,
  AlertTriangle,
  Sparkles,
  BarChart3,
  Clock,
  ArrowRight,
  Shield,
  FileText,
  RotateCcw,
  Download,
  Lock,
  ArrowUpRight,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Info,
  CheckCircle2,
  HelpCircle,
  BookOpen,
  Briefcase,
  GraduationCap,
} from 'lucide-react';
import {
  AnalysisResponse,
  ImprovementResponse,
  ImprovementAttempt,
  NextStageResponse,
  ConfirmedSkillItem,
  SkillConfirmationQuestion,
  ImprovementPlanItem,
  ResumeImprovementPlan,
  ProposedResumeEntry,
} from '../types';
import { improveResume, proceedToNextStage } from '../api';
import { SkillConfirmationPanel } from './SkillConfirmationPanel';
import { FullResumePreview } from './FullResumePreview';
import { ImprovementPlanView } from './ImprovementPlanView';
import { ResumeImprovementResults } from './ResumeImprovementResults';
import { LoadingOverlay } from './LoadingOverlay';
import { CircularScoreIndicator, getScoreColorConfig } from './CircularScoreIndicator';
import { ResumeVerificationReport } from './ResumeVerificationReport';

interface AnalysisResultsProps {
  analysis: AnalysisResponse;
  onTriggerImprovement?: () => void;
  isImproving?: boolean;
  onStartNew: () => void;
  initialImprovement?: ImprovementResponse | null;
}

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({
  analysis,
  onStartNew,
  initialImprovement = null,
}) => {
  const {
    score_result,
    match_report,
    gap_analysis,
    role_name,
    analysis_id,
    required_qualifications = [],
    relevant_projects_and_experience,
  } = analysis;

  // Track iterative improvements and re-scoring on the same page
  const [improvement, setImprovement] = useState<ImprovementResponse | null>(initialImprovement);
  const [isImprovingLocal, setIsImprovingLocal] = useState(false);
  const [currentAttempt, setCurrentAttempt] = useState<number>(
    initialImprovement?.attempt_number || 1
  );
  const [candidateNotes, setCandidateNotes] = useState<string>('');
  const [improvementError, setImprovementError] = useState<string | null>(null);

  // Candidate confirmed skills state
  const [confirmedSkills, setConfirmedSkills] = useState<ConfirmedSkillItem[]>([]);
  const [permissionGranted, setPermissionGranted] = useState<boolean>(true);

  // Tab navigation within the single analysis view: 'plan' | 'preview' | 'original' | 'confirmation'
  const [activeWorkflowTab, setActiveWorkflowTab] = useState<'plan' | 'preview' | 'original' | 'confirmation'>(
    initialImprovement ? 'preview' : score_result.final_score >= 80.0 ? 'original' : 'plan'
  );
  const [skillsCategoryTab, setSkillsCategoryTab] = useState<
    'demonstrated' | 'confirmed' | 'confirmation' | 'not_demonstrated' | 'future_learning'
  >('demonstrated');

  // Next-Stage Transition State
  const [isProceeding, setIsProceeding] = useState(false);
  const [nextStageResult, setNextStageResult] = useState<NextStageResponse | null>(null);
  const [nextStageError, setNextStageError] = useState<string | null>(null);
  const [showNextStageModal, setShowNextStageModal] = useState(false);

  // Candidate approval list state from plan
  const [approvedPlanItems, setApprovedPlanItems] = useState<ImprovementPlanItem[]>([]);
  const [approvedProjectsList, setApprovedProjectsList] = useState<ProposedResumeEntry[]>([]);

  // Determine stage qualification status (Post-improvement threshold: 80.0)
  const initialPassed = score_result.final_score >= 80.0;
  const postImprovementPassed = improvement ? improvement.new_score >= 80.0 : false;
  const isStagePassed = improvement ? postImprovementPassed : initialPassed;

  // Active verified score
  const activeScore = improvement ? improvement.new_score : score_result.final_score;
  const scoreConfig = getScoreColorConfig(activeScore);
  const requiredThreshold = 80.0;
  const maxAttempts = improvement?.max_attempts || 3;
  const attemptsCount = improvement?.attempt_number || 0;
  const canRetry = improvement ? improvement.can_retry : attemptsCount < maxAttempts;

  // Handle Candidate Approval & Factual Submission from the Structured Improvement Plan
  const handleApplyImprovementPlan = async (
    approvedItems: ImprovementPlanItem[],
    confirmedSkillsList: ConfirmedSkillItem[],
    approvedProject?: ProposedResumeEntry | null,
    approvedProjects?: ProposedResumeEntry[],
    selectionMode: 'automatic' | 'manual' = 'automatic',
    templateId?: string
  ) => {
    try {
      setIsImprovingLocal(true);
      setImprovementError(null);
      setConfirmedSkills(confirmedSkillsList);
      setApprovedPlanItems(approvedItems);
      if (approvedProjects && approvedProjects.length > 0) {
        setApprovedProjectsList(approvedProjects);
      } else if (approvedProject) {
        setApprovedProjectsList([approvedProject]);
      }

      const result = await improveResume(
        analysis_id,
        currentAttempt,
        candidateNotes.trim() || undefined,
        confirmedSkillsList,
        true,
        approvedItems,
        approvedProject,
        approvedProjects,
        selectionMode,
        templateId
      );
      setImprovement(result);
      setActiveWorkflowTab('preview');
    } catch (err: any) {
      setImprovementError(err.message || 'Failed to generate and re-score improved resume.');
    } finally {
      setIsImprovingLocal(false);
    }
  };

  // Handle Confirmed Skills Submission and Immediate AI Resume Rewriting
  const handleConfirmSkillsAndImprove = async (
    confirmed: ConfirmedSkillItem[],
    permission: boolean
  ) => {
    try {
      setIsImprovingLocal(true);
      setImprovementError(null);
      setConfirmedSkills(confirmed);
      setPermissionGranted(permission);

      const result = await improveResume(
        analysis_id,
        currentAttempt,
        candidateNotes.trim() || undefined,
        confirmed,
        permission,
        approvedPlanItems,
        approvedProjectsList[0] || undefined,
        approvedProjectsList
      );
      setImprovement(result);
      setActiveWorkflowTab('preview');
    } catch (err: any) {
      setImprovementError(err.message || 'Failed to generate and re-score improved resume.');
    } finally {
      setIsImprovingLocal(false);
    }
  };

  // Handle Skipping Unconfirmed Skills (generating strictly with verified resume facts)
  const handleSkipAndImprove = async () => {
    try {
      setIsImprovingLocal(true);
      setImprovementError(null);

      const result = await improveResume(
        analysis_id,
        currentAttempt,
        candidateNotes.trim() || undefined,
        [],
        false,
        approvedPlanItems,
        approvedProjectsList[0] || undefined,
        approvedProjectsList
      );
      setImprovement(result);
      setActiveWorkflowTab('preview');
    } catch (err: any) {
      setImprovementError(err.message || 'Failed to generate and re-score improved resume.');
    } finally {
      setIsImprovingLocal(false);
    }
  };

  // Handle Retry / Next Iteration
  const handleRunNextIteration = async (attemptNum: number) => {
    try {
      setIsImprovingLocal(true);
      setImprovementError(null);
      setCurrentAttempt(attemptNum);

      const result = await improveResume(
        analysis_id,
        attemptNum,
        candidateNotes.trim() || undefined,
        confirmedSkills,
        permissionGranted,
        approvedPlanItems,
        approvedProjectsList[0] || undefined,
        approvedProjectsList
      );
      setImprovement(result);
      setActiveWorkflowTab('preview');
    } catch (err: any) {
      setImprovementError(err.message || 'Failed to execute next improvement iteration.');
    } finally {
      setIsImprovingLocal(false);
    }
  };

  // Handle Backend Next-Stage Verification and Navigation
  const handleProceedToNextStage = async () => {
    try {
      setIsProceeding(true);
      setNextStageError(null);
      const auth = await proceedToNextStage(analysis_id);
      setNextStageResult(auth);
      setShowNextStageModal(true);
    } catch (err: any) {
      setNextStageError(err.message || 'Next stage authorization failed.');
    } finally {
      setIsProceeding(false);
    }
  };

  // Prepare questions for SkillConfirmationPanel
  const confirmationQuestions = gap_analysis.skills_requiring_confirmation || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* GLOBAL NEXT-STAGE SUCCESS MODAL */}
      {showNextStageModal && nextStageResult && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(5px)',
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
          }}
        >
          <div
            className="card"
            style={{
              maxWidth: '560px',
              width: '100%',
              padding: '36px',
              background: 'var(--bg-card)',
              borderColor: 'var(--emerald-border)',
              boxShadow: 'var(--shadow-lg)',
              textAlign: 'center',
            }}
          >
            <div
              style={{
                width: '68px',
                height: '68px',
                borderRadius: '50%',
                background: 'var(--emerald-subtle)',
                color: 'var(--emerald-success)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 18px',
                border: '2px solid var(--emerald-success)',
              }}
            >
              <CheckCircle size={36} />
            </div>

            <div className="badge badge-emerald" style={{ marginBottom: '10px' }}>
              STAGE 1 VERIFIED & PASSED
            </div>

            <h2 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-main)', marginBottom: '8px' }}>
              Resume Requirement Passed
            </h2>

            <p style={{ fontSize: '14px', color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: '24px' }}>
              Backend validation confirmed that your resume compatibility score for{' '}
              <strong style={{ color: 'var(--text-main)' }}>{role_name}</strong> achieved{' '}
              <strong style={{ color: 'var(--emerald-success)' }}>{nextStageResult.final_verified_score}/100</strong>,{' '}
              satisfying the rigorous qualification requirement (threshold: 80.0).
            </p>

            <div
              style={{
                background: 'var(--bg-subtle)',
                padding: '16px',
                borderRadius: 'var(--radius-sm)',
                marginBottom: '24px',
                textAlign: 'left',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Next Hiring Step
              </div>
              <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-main)', marginTop: '4px' }}>
                Stage 2: Technical Assessment & Cybersecurity Defense Scenarios
              </div>
              <div style={{ fontSize: '12.5px', color: 'var(--text-muted)', marginTop: '4px' }}>
                Session ID: <span className="mono">{analysis_id}</span>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button
                className="btn btn-primary"
                onClick={() => alert(`Proceeding to ${nextStageResult.stage}: System ready for candidate evaluation.`)}
                style={{ padding: '12px 24px', fontSize: '14px' }}
              >
                <span>Enter Technical Assessment</span>
                <ArrowRight size={15} />
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => setShowNextStageModal(false)}
                style={{ padding: '12px 18px', fontSize: '14px' }}
              >
                <span>Return to Review</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MULTI-STEP PROGRESS STEPPER (SHOWN ON NON-PLAN TABS) */}
      {activeWorkflowTab !== 'plan' && (
        <>
          <div
            className="card"
        style={{
          padding: '16px 24px',
          background: 'var(--bg-card)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          overflowX: 'auto',
          gap: '12px',
        }}
      >
        {[
          { num: 1, label: 'Analyze Resume', status: 'completed' },
          { num: 2, label: 'Review Skill Gaps', status: 'completed' },
          {
            num: 3,
            label: 'Confirm Skills & Evidence',
            status: improvement ? 'completed' : 'active',
          },
          {
            num: 4,
            label: 'Approve & Rewrite',
            status: improvement ? 'completed' : 'pending',
          },
          {
            num: 5,
            label: 'Full Resume Preview',
            status: improvement ? 'completed' : 'pending',
          },
          {
            num: 6,
            label: 'ATS Re-Score & Compare',
            status: improvement ? 'completed' : 'pending',
          },
          {
            num: 7,
            label: 'Continue to Next Stage',
            status: isStagePassed ? 'active' : 'locked',
          },
        ].map((step, sIdx) => {
          const isDone = step.status === 'completed';
          const isActive = step.status === 'active';
          return (
            <div
              key={step.num}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                flexShrink: 0,
                opacity: step.status === 'locked' ? 0.5 : 1,
              }}
            >
              <div
                style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  background: isDone
                    ? 'var(--emerald-success)'
                    : isActive
                    ? 'var(--primary)'
                    : 'var(--border-subtle)',
                  color: isDone || isActive ? '#FFFFFF' : 'var(--text-dim)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '11px',
                  fontWeight: 700,
                }}
              >
                {isDone ? '✓' : step.num}
              </div>
              <span
                style={{
                  fontSize: '12px',
                  fontWeight: isActive ? 700 : 500,
                  color: isActive ? 'var(--primary)' : isDone ? 'var(--text-main)' : 'var(--text-dim)',
                }}
              >
                {step.label}
              </span>
              {sIdx < 6 && (
                <span style={{ color: 'var(--border-strong)', fontSize: '13px', marginLeft: '6px' }}>
                  →
                </span>
              )}
            </div>
          );
        })}
      </div>

      {/* TOP EVALUATION HERO BANNER */}
      {/* =========================================================================
          TOP BANNER: ATS EVALUATION RESULT & NEXT STAGE CALL TO ACTION
          ========================================================================= */}
      <div
        className="ats-score-header-card"
        style={{
          borderLeft: `4px solid ${scoreConfig.stroke}`,
        }}
      >
        <div className="ats-score-header-main">
          {/* LEFT: Circular ATS score indicator */}
          <div className="ats-score-left">
            <CircularScoreIndicator score={activeScore} size={96} strokeWidth={7} />
          </div>

          {/* RIGHT: Badges, Heading, Description */}
          <div className="ats-score-right">
            <div className="ats-score-badges-row">
              <span
                className={`badge ${scoreConfig.badgeClass}`}
                style={{ fontSize: '11.5px', padding: '3px 10px', fontWeight: 700 }}
              >
                {activeScore < 70 ? <AlertTriangle size={12} /> : <CheckCircle size={12} />}
                <span>{scoreConfig.statusLabel}</span>
              </span>
              <span className="badge badge-primary" style={{ fontSize: '11.5px', padding: '3px 10px' }}>
                Target Role: {role_name}
              </span>
              <span className="badge badge-subtle" style={{ fontSize: '11px', padding: '3px 8px' }}>
                Cutoff: {requiredThreshold}.0 pts
              </span>
              {improvement && (
                <span className="badge badge-subtle" style={{ fontSize: '11px', padding: '3px 8px' }}>
                  Attempt {improvement.attempt_number} of {maxAttempts}
                </span>
              )}
            </div>

            <h2 className="ats-score-heading">
              {isStagePassed ? 'Resume Requirement Passed' : 'Compatibility Threshold Not Met'}
            </h2>

            <p className="ats-score-description">
              {isStagePassed ? (
                improvement ? (
                  <>
                    Smart skill confirmation and full resume rewriting raised your score to{' '}
                    <strong style={{ color: 'var(--emerald-success)' }}>{activeScore}/100</strong>, exceeding the{' '}
                    80.0 qualification threshold for <strong style={{ color: 'var(--text-main)' }}>{role_name}</strong>.
                  </>
                ) : (
                  <>
                    Initial resume achieved <strong style={{ color: 'var(--emerald-success)' }}>{activeScore}/100</strong>,{' '}
                    exceeding the 80.0 qualification requirement. Candidate may proceed directly to the technical assessment.
                  </>
                )
              ) : (
                <>
                  Current score of <strong style={{ color: scoreConfig.stroke }}>{activeScore}/100</strong> is below the{' '}
                  80.0 requirement for <strong style={{ color: 'var(--text-main)' }}>{role_name}</strong>. Complete the{' '}
                  interactive skill confirmation below to improve your resume.
                </>
              )}
            </p>
          </div>
        </div>

        {/* Next Stage Navigation Button */}
        <div className="ats-score-actions" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px' }}>
          <button
            id="continue-next-stage-btn"
            className={isStagePassed ? 'btn btn-primary' : 'btn btn-secondary'}
            disabled={!isStagePassed || isProceeding}
            onClick={handleProceedToNextStage}
            style={{
              padding: '12px 24px',
              fontSize: '13.5px',
              fontWeight: 700,
              opacity: isStagePassed ? 1 : 0.65,
              cursor: isStagePassed ? 'pointer' : 'not-allowed',
              boxShadow: isStagePassed ? '0 0 16px rgba(16, 185, 129, 0.35)' : 'none',
              whiteSpace: 'nowrap',
            }}
            title={isStagePassed ? 'Advance to Stage 2' : `Score must reach ${requiredThreshold}.0 to enable next stage`}
          >
            {isProceeding ? (
              <>
                <div
                  className="spin"
                  style={{
                    width: '14px',
                    height: '14px',
                    border: '2px solid currentColor',
                    borderTopColor: 'transparent',
                    borderRadius: '50%',
                  }}
                />
                <span>Verifying with Backend...</span>
              </>
            ) : isStagePassed ? (
              <>
                <CheckCircle size={15} />
                <span>Continue to Next Stage</span>
                <ArrowRight size={14} />
              </>
            ) : (
              <>
                <Lock size={14} />
                <span>Stage Locked (&lt;80.0)</span>
              </>
            )}
          </button>

          {!isStagePassed && (
            <div style={{ fontSize: '11px', color: 'var(--text-dim)', textAlign: 'right', maxWidth: '280px' }}>
              🔒 Stage locked: score must reach <strong style={{ color: 'var(--text-main)' }}>{requiredThreshold}.0</strong> to proceed.
            </div>
          )}

          {nextStageError && (
            <div style={{ fontSize: '12px', color: 'var(--rose-danger)', textAlign: 'right', maxWidth: '320px' }}>
              {nextStageError}
            </div>
          )}
        </div>
      </div>
    </>
  )}

      {/* UNIVERSAL RESUME EXTRACTION & VERIFICATION REPORT */}
      <ResumeVerificationReport
        report={analysis.verification_report || analysis.parsed_resume?.verification_report}
      />

      {/* ERROR BANNER FOR IMPROVEMENT */}
      {improvementError && (
        <div
          className="card"
          style={{
            padding: '12px 18px',
            background: 'var(--rose-subtle)',
            borderColor: 'var(--rose-border)',
            color: 'var(--rose-danger)',
            fontSize: '13px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertTriangle size={15} />
            <span>{improvementError}</span>
          </div>
          <button
            onClick={() => setImprovementError(null)}
            style={{ background: 'none', border: 'none', color: 'var(--rose-danger)', cursor: 'pointer' }}
          >
            ✕
          </button>
        </div>
      )}

      {/* WORKFLOW VIEW SWITCHER (ALWAYS VISIBLE FOR SAME-PAGE NAVIGATION) */}

      {!isImprovingLocal && (
        <div style={{ display: 'flex', gap: '10px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '10px', flexWrap: 'wrap' }}>
          <button
            className={`btn ${activeWorkflowTab === 'plan' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveWorkflowTab('plan')}
            style={{ fontSize: '13px', padding: '8px 16px' }}
          >
            <Sparkles size={14} />
            <span>Resume Improvement Plan (Approve / Edit / Skip)</span>
          </button>

          {improvement && (
            <button
              className={`btn ${activeWorkflowTab === 'preview' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveWorkflowTab('preview')}
              style={{ fontSize: '13px', padding: '8px 16px' }}
            >
              <FileText size={14} />
              <span>Improved Resume Preview & ATS Score</span>
            </button>
          )}

          <button
            className={`btn ${activeWorkflowTab === 'original' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveWorkflowTab('original')}
            style={{ fontSize: '13px', padding: '8px 16px' }}
          >
            <BarChart3 size={14} />
            <span>Original Analysis & Evidence</span>
          </button>

          <button
            className={`btn ${activeWorkflowTab === 'confirmation' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveWorkflowTab('confirmation')}
            style={{ fontSize: '13px', padding: '8px 16px' }}
          >
            <HelpCircle size={14} />
            <span>Skill Confirmations ({confirmedSkills.length} Verified)</span>
          </button>
        </div>
      )}

      {/* VIEW SECTION 1: APPROVAL-BASED IMPROVEMENT PLAN */}
      {activeWorkflowTab === 'plan' && !isImprovingLocal && (
        <div>
          <ImprovementPlanView
            plan={analysis.improvement_plan || {
              initial_score: score_result.final_score,
              threshold: 80.0,
              meets_threshold: score_result.final_score >= 80.0,
              weak_categories: [],
              items: [],
              summary_advice: ''
            }}
            roleName={role_name}
            initialScore={score_result.final_score}
            analysisId={analysis_id}
            onApplyImprovements={handleApplyImprovementPlan}
            isApplying={isImprovingLocal}
            matchReport={match_report}
            improvement={improvement}
            onProceedToNextStage={handleProceedToNextStage}
            isProceeding={isProceeding}
          />
        </div>
      )}

      {/* VIEW SECTION 2: INTERACTIVE SKILL CONFIRMATION PANEL */}
      {activeWorkflowTab === 'confirmation' && !isImprovingLocal && (
        <div>
          <SkillConfirmationPanel
            roleName={role_name}
            questions={confirmationQuestions}
            onConfirm={handleConfirmSkillsAndImprove}
            onSkip={handleSkipAndImprove}
            isLoading={isImprovingLocal}
            initialAnswers={confirmedSkills}
          />
        </div>
      )}

      {/* VIEW SECTION 2: FULL RESUME PREVIEW & RE-SCORE PROGRESSION */}
      {improvement && activeWorkflowTab === 'preview' && !isImprovingLocal && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* SCORE PROGRESSION TRACKER */}
          <div
            className="card"
            style={{
              padding: '20px 24px',
              background: 'var(--bg-subtle)',
              border: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '16px',
            }}
          >
            <div>
              <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                ATS Score Progression
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '6px', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '13.5px', color: 'var(--text-muted)' }}>
                  Original: <strong style={{ color: 'var(--text-main)' }}>{improvement.initial_score}/100</strong>
                </span>

                {improvement.attempts_history
                  .filter((h) => h.type === 'improvement')
                  .map((h) => (
                    <React.Fragment key={h.attempt}>
                      <ArrowRight size={14} color="var(--text-dim)" />
                      <span
                        className={`badge ${h.score >= 80.0 ? 'badge-emerald' : 'badge-amber'}`}
                        style={{ fontSize: '12.5px', padding: '4px 10px' }}
                      >
                        Attempt {h.attempt}: <strong>{h.score}/100</strong>
                      </span>
                    </React.Fragment>
                  ))}

                <span
                  className={`badge ${improvement.stage_passed ? 'badge-emerald' : 'badge-rose'}`}
                  style={{ fontSize: '12px', marginLeft: '6px' }}
                >
                  Status: {improvement.status}
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                className="btn btn-secondary"
                onClick={() => setActiveWorkflowTab('confirmation')}
                style={{ fontSize: '13px' }}
              >
                <RotateCcw size={14} />
                <span>Adjust Confirmed Skills</span>
              </button>

              {improvement.stage_passed && (
                <button
                  className="btn btn-primary"
                  onClick={handleProceedToNextStage}
                  disabled={isProceeding}
                  style={{ fontSize: '13px' }}
                >
                  <span>Continue to Next Stage</span>
                  <ArrowRight size={14} />
                </button>
              )}
            </div>
          </div>

          {/* APPLIED IMPROVEMENTS RESULTS (GREEN SECTION, SCORE COMPARISON, AMBER REMAINING GAPS, RED SECTION) */}
          <ResumeImprovementResults
            improvement={improvement}
            roleName={role_name}
            onProceedToNextStage={handleProceedToNextStage}
            isProceeding={isProceeding}
            onRetryOrAdjust={() => setActiveWorkflowTab('plan')}
            generationError={improvementError}
          />

          {/* COMPLETE ATS RESUME PREVIEW */}
          <FullResumePreview
            improvement={improvement}
            roleName={role_name}
            onReturnToConfirmation={() => setActiveWorkflowTab('confirmation')}
            onAccept={handleProceedToNextStage}
            isAccepting={isProceeding}
          />

          {/* CATEGORY SCORE COMPARISON & EXPLAINABLE BREAKDOWN */}
          <div className="card" style={{ padding: '24px 28px' }}>
            <h4 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BarChart3 size={18} color="var(--primary)" />
              Explainable Category Score Comparison & Evidence Breakdown
            </h4>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '16px' }}>
              Deterministic scoring comparison evaluated against Neon PostgreSQL role criteria. Improvements reflect verified evidence under established weights.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {improvement.category_comparison.map((cat) => (
                <div
                  key={cat.category}
                  style={{
                    padding: '16px 20px',
                    borderRadius: 'var(--radius-sm)',
                    background: 'var(--bg-subtle)',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px', flexWrap: 'wrap', gap: '8px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '14.5px', fontWeight: 700, color: 'var(--text-main)' }}>{cat.category}</span>
                      <span className="badge badge-subtle">{cat.weight} pts max</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                        Original: <strong style={{ color: 'var(--text-main)' }}>{cat.original_score}</strong> → Updated: <strong style={{ color: 'var(--primary)' }}>{cat.new_score}</strong>
                      </span>
                      <span
                        className={cat.delta > 0 ? 'badge badge-emerald' : cat.delta < 0 ? 'badge badge-rose' : 'badge badge-subtle'}
                        style={{ fontSize: '12px' }}
                      >
                        {cat.delta > 0 ? `+${cat.delta}` : cat.delta} pts
                      </span>
                    </div>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '12px', fontSize: '12.5px', marginTop: '10px', paddingTop: '10px', borderTop: '1px solid var(--border-subtle)' }}>
                    <div>
                      <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>Approved Improvement Applied: </span>
                      <span style={{ color: 'var(--emerald-success)' }}>{cat.approved_improvement_applied || 'Syntax & ATS formatting optimized'}</span>
                    </div>
                    <div>
                      <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>Evidence in Resume: </span>
                      <span style={{ color: 'var(--text-muted)' }}>{cat.evidence_supporting || 'Verified evidence evaluated'}</span>
                    </div>
                    <div>
                      <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>Remaining Gaps: </span>
                      <span style={{ color: 'var(--text-dim)' }}>{cat.remaining_gaps || 'None'}</span>
                    </div>
                    {cat.no_increase_explanation && (
                      <div style={{ gridColumn: '1 / -1', background: 'var(--bg-card)', padding: '8px 12px', borderRadius: '4px', borderLeft: '3px solid var(--primary)', fontSize: '12px', color: 'var(--text-dim)' }}>
                        ℹ️ <strong>Score Integrity:</strong> {cat.no_increase_explanation}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* RETRY ITERATION CONTROLS (IF SCORE < 80 AND CAN RETRY) */}
            {canRetry && !improvement.stage_passed && (
              <div
                style={{
                  marginTop: '20px',
                  padding: '16px 20px',
                  borderRadius: 'var(--radius-sm)',
                  background: 'var(--amber-subtle)',
                  border: '1px solid var(--amber-border)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <AlertTriangle size={16} color="var(--amber-warn)" />
                  <span style={{ fontSize: '13.5px', fontWeight: 700, color: 'var(--text-main)' }}>
                    Score is {improvement.new_score}/100 (Below 80.0 Cutoff). Iteration {attemptsCount + 1} of {maxAttempts} available.
                  </span>
                </div>
                <p style={{ fontSize: '12.5px', color: 'var(--text-muted)', marginBottom: '12px', lineHeight: 1.5 }}>
                  Provide additional verifiable details (coursework labs, home network configurations, tool syntax) to include in your next improvement iteration:
                </p>
                <textarea
                  value={candidateNotes}
                  onChange={(e) => setCandidateNotes(e.target.value)}
                  placeholder="e.g. Configured pfSense firewall in home lab; practiced packet inspection with Wireshark and Snort."
                  rows={2}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-subtle)',
                    background: 'var(--bg-app)',
                    color: 'var(--text-main)',
                    fontSize: '13px',
                    marginBottom: '12px',
                  }}
                />
                <button
                  className="btn btn-primary"
                  onClick={() => handleRunNextIteration(attemptsCount + 1)}
                  disabled={isImprovingLocal}
                  style={{ fontSize: '13px', padding: '9px 18px' }}
                >
                  <Sparkles size={14} />
                  <span>Execute Next Improvement Attempt ({attemptsCount + 1} of {maxAttempts})</span>
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* VIEW SECTION 3: ORIGINAL ANALYSIS & ROLE REQUIREMENTS FROM NEON */}
      <div className="card" style={{ padding: '26px 30px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h3 style={{ fontSize: '17px', fontWeight: 800, color: 'var(--text-main)', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BarChart3 size={19} color="var(--primary)" />
              Original Resume Analysis & Role Requirements Breakdown
            </h3>
            <div style={{ fontSize: '12.5px', color: 'var(--text-dim)', marginTop: '2px' }}>
              Target Role: <strong style={{ color: 'var(--text-main)' }}>{role_name}</strong> • Requirements authoritative from Neon PostgreSQL
            </div>
          </div>
          <span className="badge badge-subtle">Initial Score: {score_result.final_score}/100</span>
        </div>

        {/* CATEGORY SCORES GRID */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '14px', marginBottom: '24px' }}>
          {score_result.category_scores.map((cat) => {
            const ratio = cat.score_earned / (cat.weight || 1);
            return (
              <div
                key={cat.category_name}
                style={{
                  background: 'var(--bg-subtle)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '16px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span style={{ fontSize: '13.5px', fontWeight: 600, color: 'var(--text-main)' }}>{cat.category_name}</span>
                  <span className="mono" style={{ fontSize: '13px', fontWeight: 700, color: 'var(--primary)' }}>
                    {cat.score_earned} / {cat.weight} pts
                  </span>
                </div>

                <div style={{ height: '6px', background: 'var(--border-strong)', borderRadius: '3px', overflow: 'hidden', marginBottom: '8px' }}>
                  <div
                    style={{
                      height: '100%',
                      width: `${Math.min(100, Math.max(0, ratio * 100))}%`,
                      background: ratio >= 0.8 ? 'var(--emerald-success)' : ratio >= 0.5 ? 'var(--primary)' : 'var(--amber-warn)',
                      borderRadius: '3px',
                    }}
                  />
                </div>

                <div style={{ fontSize: '12px', color: 'var(--text-dim)', lineHeight: 1.4 }}>
                  {cat.explanation}
                </div>
              </div>
            );
          })}
        </div>

        {/* ROLE FORMAL REQUIREMENTS FROM NEON DATABASE */}
        {required_qualifications.length > 0 && (
          <div style={{ marginBottom: '24px', background: 'var(--bg-subtle)', padding: '18px 20px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <GraduationCap size={16} color="var(--primary)" />
              Neon PostgreSQL Documented Role Requirements ({required_qualifications.length})
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12.5px' }}>
              {required_qualifications.map((req, idx) => (
                <div key={idx} style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
                  <span className="badge badge-subtle" style={{ flexShrink: 0, textTransform: 'capitalize' }}>
                    {req.requirement_type}
                  </span>
                  <span style={{ color: 'var(--text-muted)', lineHeight: 1.5 }}>
                    {req.requirement_description}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CANDIDATE PROJECTS & EXPERIENCE EVIDENCE EXTRACTED */}
        {relevant_projects_and_experience && (
          <div style={{ marginBottom: '24px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '14px' }}>
            <div style={{ background: 'var(--bg-subtle)', padding: '16px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '12.5px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Briefcase size={15} color="var(--primary)" />
                Demonstrated Projects Evidence ({relevant_projects_and_experience.projects.length})
              </div>
              <ul style={{ margin: '0 0 0 16px', padding: 0, fontSize: '12.5px', color: 'var(--text-muted)' }}>
                {relevant_projects_and_experience.projects.map((p, idx) => (
                  <li key={idx} style={{ marginBottom: '4px' }}>{p}</li>
                ))}
                {relevant_projects_and_experience.projects.length === 0 && (
                  <span style={{ color: 'var(--text-dim)' }}>No projects identified in resume.</span>
                )}
              </ul>
            </div>

            <div style={{ background: 'var(--bg-subtle)', padding: '16px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '12.5px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Clock size={15} color="var(--primary)" />
                Demonstrated Employment Evidence ({relevant_projects_and_experience.experience.length})
              </div>
              <ul style={{ margin: '0 0 0 16px', padding: 0, fontSize: '12.5px', color: 'var(--text-muted)' }}>
                {relevant_projects_and_experience.experience.map((e, idx) => (
                  <li key={idx} style={{ marginBottom: '4px' }}>{e}</li>
                ))}
                {relevant_projects_and_experience.experience.length === 0 && (
                  <span style={{ color: 'var(--text-dim)' }}>No employment history identified in resume.</span>
                )}
              </ul>
            </div>
          </div>
        )}

        {/* 5-CATEGORY SKILLS BREAKDOWN AS REQUIRED BY SPEC */}
        <div>
          <div style={{ fontSize: '13.5px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '12px' }}>
            Detailed Skill Gap Classification for {role_name}:
          </div>

          <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px', marginBottom: '14px', flexWrap: 'wrap' }}>
            <button
              className={`btn ${skillsCategoryTab === 'demonstrated' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setSkillsCategoryTab('demonstrated')}
              style={{ fontSize: '12px', padding: '6px 12px' }}
            >
              A. Demonstrated Skills ({match_report.matched_skills.length})
            </button>
            <button
              className={`btn ${skillsCategoryTab === 'confirmed' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setSkillsCategoryTab('confirmed')}
              style={{ fontSize: '12px', padding: '6px 12px' }}
            >
              B. Candidate-Confirmed ({confirmedSkills.length})
            </button>
            <button
              className={`btn ${skillsCategoryTab === 'confirmation' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setSkillsCategoryTab('confirmation')}
              style={{ fontSize: '12px', padding: '6px 12px' }}
            >
              C. Requiring Confirmation ({confirmationQuestions.length})
            </button>
            <button
              className={`btn ${skillsCategoryTab === 'not_demonstrated' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setSkillsCategoryTab('not_demonstrated')}
              style={{ fontSize: '12px', padding: '6px 12px' }}
            >
              D. Not Demonstrated ({match_report.unmatched_skills.length})
            </button>
            <button
              className={`btn ${skillsCategoryTab === 'future_learning' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setSkillsCategoryTab('future_learning')}
              style={{ fontSize: '12px', padding: '6px 12px' }}
            >
              E. Future Learning ({gap_analysis.future_learning_recommendations?.length || 0})
            </button>
          </div>

          {/* TAB CONTENT: DEMONSTRATED SKILLS */}
          {skillsCategoryTab === 'demonstrated' && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {match_report.matched_skills.map((s) => (
                <span key={s.skill_name} className="badge badge-emerald" style={{ fontSize: '12px' }}>
                  ✓ {s.skill_name} {s.importance === 'core' && '★ Core'}
                </span>
              ))}
              {match_report.matched_skills.length === 0 && (
                <span style={{ fontSize: '13px', color: 'var(--text-dim)' }}>No demonstrated skills detected in resume.</span>
              )}
            </div>
          )}

          {/* TAB CONTENT: CANDIDATE CONFIRMED SKILLS */}
          {skillsCategoryTab === 'confirmed' && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {confirmedSkills.filter(c => c.proficiency !== 'not_used').map((s) => (
                <span key={s.skill_name} className="badge badge-primary" style={{ fontSize: '12px' }}>
                  ★ {s.skill_name} ({s.proficiency === 'hands_on' ? 'Hands-on' : 'Foundational'})
                </span>
              ))}
              {confirmedSkills.filter(c => c.proficiency !== 'not_used').length === 0 && (
                <span style={{ fontSize: '13px', color: 'var(--text-dim)' }}>No skills confirmed by candidate yet.</span>
              )}
            </div>
          )}

          {/* TAB CONTENT: SKILLS REQUIRING CONFIRMATION */}
          {skillsCategoryTab === 'confirmation' && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {confirmationQuestions.map((q) => (
                <span key={q.skill_name} className="badge badge-amber" style={{ fontSize: '12px' }}>
                  ? {q.skill_name} ({q.importance})
                </span>
              ))}
            </div>
          )}

          {/* TAB CONTENT: NOT DEMONSTRATED */}
          {skillsCategoryTab === 'not_demonstrated' && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {match_report.unmatched_skills.map((u) => (
                <span key={u.skill_name} className="badge badge-subtle" style={{ fontSize: '12px' }}>
                  ✕ {u.skill_name}
                </span>
              ))}
            </div>
          )}

          {/* TAB CONTENT: FUTURE LEARNING RECOMMENDATIONS */}
          {skillsCategoryTab === 'future_learning' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {(gap_analysis.future_learning_recommendations || []).map((r, idx) => (
                <div key={idx} style={{ fontSize: '12.5px', color: 'var(--text-muted)' }}>
                  <strong>• {r.title}: </strong> {r.description}
                </div>
              ))}
              {(!gap_analysis.future_learning_recommendations || gap_analysis.future_learning_recommendations.length === 0) && (
                <span style={{ fontSize: '13px', color: 'var(--text-dim)' }}>No future milestones recommended.</span>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Enterprise SaaS Loading Experience for Resume Creation and Re-Scoring */}
      <LoadingOverlay
        isOpen={isImprovingLocal}
        operationType="create_resume"
        error={improvementError}
        onRetry={() => handleApplyImprovementPlan(approvedPlanItems, confirmedSkills)}
        onClose={() => setImprovementError(null)}
      />

      <LoadingOverlay
        isOpen={isProceeding}
        operationType="rescoring"
      />
    </div>
  );
};

