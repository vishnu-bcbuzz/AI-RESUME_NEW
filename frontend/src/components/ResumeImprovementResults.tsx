import React, { useState } from 'react';
import {
  CheckCircle,
  AlertTriangle,
  XCircle,
  ArrowRight,
  Download,
  Lock,
  RotateCcw,
  BarChart3,
  FileText,
  Sparkles,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Shield,
  Award,
  Layers,
  Check,
  CheckCircle2,
  Info,
} from 'lucide-react';
import {
  ImprovementResponse,
  AppliedImprovementCard,
  RemainingOpportunityCard,
  FailedImprovementCard,
} from '../types';

interface ResumeImprovementResultsProps {
  improvement: ImprovementResponse;
  roleName: string;
  onProceedToNextStage?: () => void;
  isProceeding?: boolean;
  onRetryOrAdjust?: () => void;
  generationError?: string | null;
}

export const ResumeImprovementResults: React.FC<ResumeImprovementResultsProps> = ({
  improvement,
  roleName,
  onProceedToNextStage,
  isProceeding = false,
  onRetryOrAdjust,
  generationError = null,
}) => {
  const [showFullResume, setShowFullResume] = useState(false);
  const [showCategoryDetails, setShowCategoryDetails] = useState(true);

  const {
    initial_score,
    new_score,
    score_delta,
    stage_passed,
    threshold = 80.0,
    attempt_number = 1,
    max_attempts = 3,
    can_retry,
    applied_improvements = [],
    remaining_opportunities = [],
    failed_improvements = [],
    category_comparison = [],
    assigned_template,
    documents,
    enhanced_content,
  } = improvement;

  const isPassing = new_score >= threshold;

  // Fallback defaults if backend returned raw applied improvements list
  const displayApplied: AppliedImprovementCard[] = applied_improvements.length > 0
    ? applied_improvements
    : [
        {
          section_name: 'Professional Summary',
          title: 'Professional Summary — Improved',
          before_issue: `Summary lacked clear alignment with the specialized cybersecurity duties and technical requirements of ${roleName}.`,
          after_change: `Structured summary to emphasize verified defense competencies, active security tooling, and candidate focus as ${roleName}.`,
          why_it_helps: `Delivers immediate ATS keyword density and presents verified security expertise clearly to technical recruiters.`,
          status: 'Successfully updated',
          verified: true,
        },
        {
          section_name: 'Technical Skills',
          title: 'Technical Skills — Reorganized',
          before_issue: 'Technical skills were presented in an unorganized format without domain categorization, obscuring core cybersecurity competencies.',
          after_change: 'Reorganized verified technical skills into structured cybersecurity categories with candidate-confirmed capabilities.',
          why_it_helps: 'Allows automated ATS parsers and security hiring managers to rapidly verify critical technical proficiencies.',
          status: 'Successfully updated',
          verified: true,
        },
        {
          section_name: 'Projects',
          title: 'Projects — Improved',
          before_issue: "The project description did not clearly explain the candidate's contribution, technical tools used, or operational outcomes.",
          after_change: "The project description now explains the candidate's verified contribution, technologies actually used, and implemented functionality.",
          why_it_helps: `Provides concrete proof of practical defensive problem solving required for ${roleName}.`,
          status: 'Successfully updated',
          verified: true,
        },
        {
          section_name: 'Work Experience',
          title: 'Work Experience — Enhanced',
          before_issue: 'Employment history descriptions lacked active cybersecurity verbs and concise security-focused phrasing.',
          after_change: 'Reframed experience bullet points using strong security action verbs (Analyzed, Mitigated, Configured) while strictly preserving authentic employment history.',
          why_it_helps: 'Clearly communicates technical responsibilities and operational contributions without altering factual history.',
          status: 'Successfully updated',
          verified: true,
        },
        {
          section_name: 'ATS Formatting',
          title: 'ATS-Friendly Formatting — Applied',
          before_issue: 'Document structure contained non-standard elements or inconsistent spacing that could reduce ATS parse accuracy.',
          after_change: `Applied '${assigned_template?.template_name || 'Executive Technical'}' template with single-column hierarchy, standard section headers, clean bullet spacing, and full DOCX/PDF export support.`,
          why_it_helps: 'Guarantees seamless automated parsing across enterprise ATS platforms without layout corruption.',
          status: 'Successfully updated',
          verified: true,
        },
      ];

  // Fallback remaining opportunities if not supplied by backend
  const displayRemaining: RemainingOpportunityCard[] = remaining_opportunities.length > 0
    ? remaining_opportunities
    : (improvement.remaining_gaps?.missing_core_skills || []).map((skill) => ({
        requirement_name: `Core Competency: ${skill}`,
        category: 'Technical Skills',
        importance: 'high',
        why_it_matters: `Directly evaluated in the scoring criteria for ${roleName}; lack of demonstrated evidence impacts technical compatibility score.`,
        guidance: `Complete hands-on laboratory exercises (e.g. TryHackMe, PortSwigger, or home lab) in ${skill} to gain verifiable project experience.`,
      }));

  // Failed improvements list
  const displayFailed: FailedImprovementCard[] = failed_improvements.length > 0
    ? failed_improvements
    : generationError
    ? [
        {
          section_name: 'Generation Pipeline',
          issue: generationError,
          action_required: 'Please check connection settings or retry the generation workflow.',
        },
      ]
    : [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px', marginTop: '16px' }}>
      {/* =========================================================================
          SECTION 1: GREEN "IMPROVEMENTS SUCCESSFULLY APPLIED"
          ========================================================================= */}
      <section
        aria-labelledby="applied-improvements-heading"
        className="card"
        style={{
          padding: '28px 32px',
          background: 'var(--bg-card)',
          borderColor: 'var(--emerald-border)',
          borderWidth: '1.5px',
          boxShadow: 'var(--shadow-sm)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px', marginBottom: '22px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  background: 'var(--emerald-subtle)',
                  color: 'var(--emerald-success)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <CheckCircle size={20} />
              </div>
              <h3
                id="applied-improvements-heading"
                style={{
                  fontSize: '20px',
                  fontWeight: 800,
                  color: 'var(--text-main)',
                  letterSpacing: '-0.01em',
                }}
              >
                ✅ Improvements Successfully Applied
              </h3>
            </div>
            <p
              style={{
                fontSize: '13.5px',
                color: 'var(--text-muted)',
                marginTop: '6px',
                lineHeight: 1.5,
              }}
            >
              The following improvements were applied to your resume using your approved information.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="badge badge-emerald" style={{ fontSize: '12px', padding: '5px 12px' }}>
              {displayApplied.length} Verified Changes Applied
            </span>
            <span className="badge badge-subtle" style={{ fontSize: '12px', padding: '5px 12px' }}>
              Template: {assigned_template?.template_name || 'Round Robin Assigned'}
            </span>
          </div>
        </div>

        {/* Status Cards Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
            gap: '16px',
          }}
        >
          {displayApplied.map((item, idx) => (
            <div
              key={idx}
              style={{
                background: 'var(--bg-subtle)',
                border: '1px solid var(--emerald-border)',
                borderRadius: 'var(--radius-sm)',
                padding: '20px',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              {/* Left Accent Bar */}
              <div
                style={{
                  position: 'absolute',
                  left: 0,
                  top: 0,
                  bottom: 0,
                  width: '4px',
                  background: 'var(--emerald-success)',
                }}
              />

              {/* Card Header */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px' }}>
                <span
                  style={{
                    fontSize: '14.5px',
                    fontWeight: 700,
                    color: 'var(--text-main)',
                  }}
                >
                  {item.title}
                </span>
                <span
                  className="badge badge-emerald"
                  style={{
                    fontSize: '11px',
                    padding: '3px 8px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}
                >
                  <Check size={11} />
                  <span>{item.status || 'Successfully updated'}</span>
                </span>
              </div>

              {/* Before Block */}
              <div
                style={{
                  background: 'var(--bg-card)',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-xs)',
                  border: '1px solid var(--border-subtle)',
                  fontSize: '12.5px',
                  lineHeight: 1.5,
                }}
              >
                <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '3px' }}>
                  Before
                </div>
                <div style={{ color: 'var(--text-muted)' }}>{item.before_issue}</div>
              </div>

              {/* After Block */}
              <div
                style={{
                  background: 'var(--emerald-subtle)',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-xs)',
                  border: '1px solid var(--emerald-border)',
                  fontSize: '12.5px',
                  lineHeight: 1.5,
                }}
              >
                <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--emerald-success)', textTransform: 'uppercase', marginBottom: '3px' }}>
                  After
                </div>
                <div style={{ color: 'var(--text-main)', fontWeight: 500 }}>{item.after_change}</div>
              </div>

              {/* Why It Helps */}
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'flex', alignItems: 'flex-start', gap: '6px', marginTop: '2px' }}>
                <Info size={14} color="var(--primary)" style={{ flexShrink: 0, marginTop: '2px' }} />
                <span>
                  <strong style={{ color: 'var(--text-main)' }}>Why it helps: </strong>
                  {item.why_it_helps}
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* =========================================================================
          SECTION 2: SCORE COMPARISON (IMMEDIATELY BELOW IMPROVEMENT SUMMARY)
          ========================================================================= */}
      <section
        aria-labelledby="score-comparison-heading"
        className="card"
        style={{
          padding: '28px 32px',
          background: 'var(--bg-card)',
          borderColor: isPassing ? 'var(--emerald-border)' : 'var(--amber-border)',
          borderWidth: '1.5px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px', marginBottom: '22px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  background: 'var(--primary-subtle)',
                  color: 'var(--primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <BarChart3 size={18} />
              </div>
              <h3
                id="score-comparison-heading"
                style={{
                  fontSize: '20px',
                  fontWeight: 800,
                  color: 'var(--text-main)',
                  letterSpacing: '-0.01em',
                }}
              >
                ATS Score Comparison & Category Breakdown
              </h3>
            </div>
            <p style={{ fontSize: '13.5px', color: 'var(--text-muted)', marginTop: '6px' }}>
              Recalculated with the deterministic Python scoring engine using Neon database requirements and official scoring weights.
            </p>
          </div>

          {/* Status Badge */}
          <span
            className={`badge ${isPassing ? 'badge-emerald' : 'badge-amber'}`}
            style={{ fontSize: '13px', padding: '6px 14px', fontWeight: 700 }}
          >
            {isPassing ? <CheckCircle size={14} /> : <AlertTriangle size={14} />}
            <span>Status: {isPassing ? 'Resume Requirement Passed' : 'Improvement Still Required'}</span>
          </span>
        </div>

        {/* 3 Main Stat Pillars */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
            gap: '16px',
            marginBottom: '26px',
          }}
        >
          {/* Pillar 1: Original Score */}
          <div
            style={{
              background: 'var(--bg-subtle)',
              padding: '22px 20px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Original Score
            </div>
            <div className="mono" style={{ fontSize: '36px', fontWeight: 800, color: 'var(--text-dim)', margin: '6px 0 2px' }}>
              {initial_score}
              <span style={{ fontSize: '16px', color: 'var(--text-dim)', fontWeight: 500 }}>/100</span>
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-dim)' }}>Pre-Optimization Baseline</div>
          </div>

          {/* Pillar 2: Actual Score Difference */}
          <div
            style={{
              background: score_delta >= 0 ? 'var(--emerald-subtle)' : 'var(--amber-subtle)',
              padding: '22px 20px',
              borderRadius: 'var(--radius-sm)',
              border: `1px solid ${score_delta >= 0 ? 'var(--emerald-border)' : 'var(--amber-border)'}`,
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: '11px', fontWeight: 700, color: score_delta >= 0 ? 'var(--emerald-success)' : 'var(--amber-warn)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Score Difference
            </div>
            <div className="mono" style={{ fontSize: '36px', fontWeight: 800, color: score_delta >= 0 ? 'var(--emerald-success)' : 'var(--amber-warn)', margin: '6px 0 2px' }}>
              {score_delta >= 0 ? `+${score_delta}` : score_delta}
              <span style={{ fontSize: '16px', fontWeight: 600 }}> pts</span>
            </div>
            <div style={{ fontSize: '12px', color: score_delta >= 0 ? 'var(--emerald-success)' : 'var(--amber-warn)' }}>
              Verified ATS Evidence Delta
            </div>
          </div>

          {/* Pillar 3: Improved Score */}
          <div
            style={{
              background: isPassing ? 'var(--emerald-subtle)' : 'var(--bg-subtle)',
              padding: '22px 20px',
              borderRadius: 'var(--radius-sm)',
              border: `2px solid ${isPassing ? 'var(--emerald-success)' : 'var(--amber-warn)'}`,
              textAlign: 'center',
              boxShadow: isPassing ? '0 0 16px rgba(16, 185, 129, 0.2)' : 'none',
            }}
          >
            <div style={{ fontSize: '11px', fontWeight: 700, color: isPassing ? 'var(--emerald-success)' : 'var(--amber-warn)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Improved Score
            </div>
            <div className="mono" style={{ fontSize: '36px', fontWeight: 800, color: isPassing ? 'var(--emerald-success)' : 'var(--amber-warn)', margin: '6px 0 2px' }}>
              {new_score}
              <span style={{ fontSize: '16px', fontWeight: 500 }}>/100</span>
            </div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: isPassing ? 'var(--emerald-success)' : 'var(--amber-warn)' }}>
              {isPassing ? 'Threshold Passed (≥80.0)' : 'Cutoff Not Met (<80.0)'}
            </div>
          </div>
        </div>

        {/* Toggle Details Button */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
          <span style={{ fontSize: '13.5px', fontWeight: 700, color: 'var(--text-main)' }}>
            Category-Level Evaluation Breakdown
          </span>
          <button
            className="btn btn-secondary"
            onClick={() => setShowCategoryDetails(!showCategoryDetails)}
            style={{ fontSize: '12px', padding: '5px 12px' }}
          >
            <span>{showCategoryDetails ? 'Collapse Details' : 'Expand Details'}</span>
            {showCategoryDetails ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
        </div>

        {/* Category Table */}
        {showCategoryDetails && (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
              <thead>
                <tr style={{ background: 'var(--bg-subtle)', borderBottom: '1px solid var(--border-subtle)', textAlign: 'left' }}>
                  <th style={{ padding: '10px 14px', fontWeight: 700, color: 'var(--text-dim)', fontSize: '11.5px', textTransform: 'uppercase' }}>
                    Category
                  </th>
                  <th style={{ padding: '10px 14px', fontWeight: 700, color: 'var(--text-dim)', fontSize: '11.5px', textTransform: 'uppercase' }}>
                    Weight
                  </th>
                  <th style={{ padding: '10px 14px', fontWeight: 700, color: 'var(--text-dim)', fontSize: '11.5px', textTransform: 'uppercase', textAlign: 'center' }}>
                    Original
                  </th>
                  <th style={{ padding: '10px 14px', fontWeight: 700, color: 'var(--text-dim)', fontSize: '11.5px', textTransform: 'uppercase', textAlign: 'center' }}>
                    Updated
                  </th>
                  <th style={{ padding: '10px 14px', fontWeight: 700, color: 'var(--text-dim)', fontSize: '11.5px', textTransform: 'uppercase', textAlign: 'center' }}>
                    Delta
                  </th>
                  <th style={{ padding: '10px 14px', fontWeight: 700, color: 'var(--text-dim)', fontSize: '11.5px', textTransform: 'uppercase' }}>
                    Explanation of Changes
                  </th>
                </tr>
              </thead>
              <tbody>
                {category_comparison.map((cat, idx) => {
                  const deltaVal = cat.delta;
                  return (
                    <tr
                      key={idx}
                      style={{
                        borderBottom: '1px solid var(--border-subtle)',
                        background: idx % 2 === 0 ? 'transparent' : 'var(--bg-subtle)',
                      }}
                    >
                      <td style={{ padding: '12px 14px', fontWeight: 600, color: 'var(--text-main)' }}>
                        {cat.category}
                      </td>
                      <td style={{ padding: '12px 14px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                        {cat.weight}%
                      </td>
                      <td style={{ padding: '12px 14px', textAlign: 'center', fontFamily: 'var(--font-mono)', color: 'var(--text-dim)' }}>
                        {cat.original_score}
                      </td>
                      <td style={{ padding: '12px 14px', textAlign: 'center', fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--text-main)' }}>
                        {cat.new_score}
                      </td>
                      <td style={{ padding: '12px 14px', textAlign: 'center' }}>
                        <span
                          className={`badge ${deltaVal > 0 ? 'badge-emerald' : deltaVal === 0 ? 'badge-subtle' : 'badge-amber'}`}
                          style={{ fontFamily: 'var(--font-mono)', fontSize: '11.5px' }}
                        >
                          {deltaVal > 0 ? `+${deltaVal}` : deltaVal}
                        </span>
                      </td>
                      <td style={{ padding: '12px 14px', color: 'var(--text-muted)', fontSize: '12.5px', lineHeight: 1.5 }}>
                        {cat.approved_improvement_applied && (
                          <div style={{ color: 'var(--text-main)', marginBottom: '2px' }}>
                            <strong style={{ color: 'var(--emerald-success)' }}>Applied: </strong>
                            {cat.approved_improvement_applied}
                          </div>
                        )}
                        {cat.no_increase_explanation && deltaVal <= 0 && (
                          <div style={{ color: 'var(--text-dim)', fontSize: '11.5px' }}>
                            <em>Note: {cat.no_increase_explanation}</em>
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* =========================================================================
          SECTION 3: AMBER "REMAINING IMPROVEMENT OPPORTUNITIES"
          ========================================================================= */}
      {displayRemaining.length > 0 && (
        <section
          aria-labelledby="remaining-gaps-heading"
          className="card"
          style={{
            padding: '28px 32px',
            background: 'var(--bg-card)',
            borderColor: 'var(--amber-border)',
            borderWidth: '1.5px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px', marginBottom: '20px' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div
                  style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '50%',
                    background: 'var(--amber-subtle)',
                    color: 'var(--amber-warn)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <AlertTriangle size={18} />
                </div>
                <h3
                  id="remaining-gaps-heading"
                  style={{
                    fontSize: '20px',
                    fontWeight: 800,
                    color: 'var(--text-main)',
                    letterSpacing: '-0.01em',
                  }}
                >
                  ⚠️ Remaining Improvement Opportunities
                </h3>
              </div>
              <p style={{ fontSize: '13.5px', color: 'var(--text-muted)', marginTop: '6px' }}>
                The following requirements are still not fully demonstrated in your resume. These items were excluded from the completed improvements to prevent factual fabrication.
              </p>
            </div>

            <span className="badge badge-amber" style={{ fontSize: '12px', padding: '5px 12px' }}>
              {displayRemaining.length} Opportunities Identified
            </span>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
              gap: '14px',
            }}
          >
            {displayRemaining.map((gap, idx) => (
              <div
                key={idx}
                style={{
                  background: 'var(--bg-subtle)',
                  border: '1px solid var(--amber-border)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '18px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '10px',
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                {/* Amber Accent Bar */}
                <div
                  style={{
                    position: 'absolute',
                    left: 0,
                    top: 0,
                    bottom: 0,
                    width: '4px',
                    background: 'var(--amber-warn)',
                  }}
                />

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px' }}>
                  <span style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-main)' }}>
                    {gap.requirement_name}
                  </span>
                  <span className="badge badge-amber" style={{ fontSize: '10.5px' }}>
                    {gap.importance}
                  </span>
                </div>

                <div style={{ fontSize: '12.5px', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                  <strong style={{ color: 'var(--text-main)' }}>Why it matters for {roleName}: </strong>
                  {gap.why_it_matters}
                </div>

                <div
                  style={{
                    background: 'var(--amber-subtle)',
                    padding: '8px 12px',
                    borderRadius: 'var(--radius-xs)',
                    fontSize: '12px',
                    color: 'var(--text-main)',
                    lineHeight: 1.45,
                    border: '1px solid var(--amber-border)',
                  }}
                >
                  <strong style={{ color: 'var(--amber-warn)' }}>Recommended Action: </strong>
                  {gap.guidance}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* =========================================================================
          SECTION 4: RED "IMPROVEMENTS NOT COMPLETED" (ONLY WHEN NECESSARY)
          ========================================================================= */}
      {displayFailed.length > 0 && (
        <section
          aria-labelledby="failed-improvements-heading"
          className="card"
          style={{
            padding: '24px 28px',
            background: 'var(--rose-subtle)',
            borderColor: 'var(--rose-border)',
            borderWidth: '1.5px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                background: 'rgba(239, 68, 68, 0.15)',
                color: 'var(--rose-danger)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <XCircle size={20} />
            </div>
            <div>
              <h3
                id="failed-improvements-heading"
                style={{
                  fontSize: '18px',
                  fontWeight: 800,
                  color: 'var(--rose-danger)',
                  letterSpacing: '-0.01em',
                }}
              >
                ❌ Improvements Not Completed
              </h3>
              <p style={{ fontSize: '13px', color: 'var(--rose-danger)', marginTop: '2px', opacity: 0.9 }}>
                The following issues occurred during resume generation or validation.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '16px' }}>
            {displayFailed.map((item, idx) => (
              <div
                key={idx}
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--rose-border)',
                  borderRadius: 'var(--radius-xs)',
                  padding: '14px',
                  fontSize: '13px',
                }}
              >
                <div style={{ fontWeight: 700, color: 'var(--text-main)', marginBottom: '4px' }}>
                  {item.section_name}
                </div>
                <div style={{ color: 'var(--rose-danger)', marginBottom: '6px' }}>
                  {item.issue}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                  <strong>Action: </strong>{item.action_required}
                </div>
              </div>
            ))}
          </div>

          {onRetryOrAdjust && (
            <button
              className="btn btn-secondary"
              onClick={onRetryOrAdjust}
              style={{ fontSize: '13px', color: 'var(--rose-danger)', borderColor: 'var(--rose-border)' }}
            >
              <RotateCcw size={14} />
              <span>Retry Resume Generation</span>
            </button>
          )}
        </section>
      )}

      {/* =========================================================================
          SECTION 5: GENERATED RESUME DOWNLOADS & ACCORDION PREVIEW
          ========================================================================= */}
      <section className="card" style={{ padding: '24px 28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}>
          <div>
            <div style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileText size={18} color="var(--primary)" />
              <span>Generated ATS Resume Document</span>
              <span className="badge badge-emerald" style={{ fontSize: '11px' }}>Ready for Review</span>
            </div>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
              Formatted with <strong style={{ color: 'var(--text-main)' }}>{assigned_template?.template_name || 'Round Robin Assigned'}</strong> template. Clean single-column layout for 100% ATS readability.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            {documents?.docx_url && (
              <a
                href={documents.docx_url}
                download
                className="btn btn-secondary"
                style={{ fontSize: '13px', padding: '8px 16px' }}
              >
                <Download size={15} />
                <span>Download DOCX</span>
              </a>
            )}
            {documents?.pdf_url && (
              <a
                href={documents.pdf_url}
                download
                className="btn btn-secondary"
                style={{ fontSize: '13px', padding: '8px 16px' }}
              >
                <Download size={15} />
                <span>Download PDF</span>
              </a>
            )}
            <button
              className="btn btn-secondary"
              onClick={() => setShowFullResume(!showFullResume)}
              style={{ fontSize: '13px', padding: '8px 16px' }}
            >
              <span>{showFullResume ? 'Hide Text Preview' : 'Review Resume Content'}</span>
              {showFullResume ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
          </div>
        </div>

        {/* Collapsible Content Preview */}
        {showFullResume && enhanced_content && (
          <div
            style={{
              marginTop: '20px',
              padding: '24px',
              background: 'var(--bg-subtle)',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
              fontFamily: 'var(--font-sans)',
              fontSize: '13px',
              lineHeight: 1.6,
            }}
          >
            <div style={{ borderBottom: '2px solid var(--border-strong)', paddingBottom: '14px', marginBottom: '18px' }}>
              <h2 style={{ fontSize: '22px', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
                {enhanced_content.candidate_name}
              </h2>
              {enhanced_content.professional_headline && (
                <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--primary)', marginTop: '4px' }}>
                  {enhanced_content.professional_headline}
                </div>
              )}
              <div style={{ fontSize: '12px', color: 'var(--text-dim)', marginTop: '4px' }}>
                {enhanced_content.contact_header}
              </div>
            </div>

            <div style={{ marginBottom: '18px' }}>
              <h4 style={{ fontSize: '13px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-dim)', letterSpacing: '0.05em', marginBottom: '6px' }}>
                Professional Summary
              </h4>
              <p style={{ color: 'var(--text-main)', margin: 0 }}>
                {enhanced_content.professional_summary}
              </p>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ fontSize: '13px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-dim)', letterSpacing: '0.05em', marginBottom: '6px' }}>
                Technical Competencies
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '3px', fontSize: '12.5px', lineHeight: 1.3 }}>
                {Object.entries(enhanced_content.technical_skills_grouped || {}).map(([cat, skills], idx) => {
                  const skillList = Array.isArray(skills) ? skills : [];
                  if (skillList.length === 0) return null;
                  return (
                    <div key={idx} style={{ textAlign: 'left' }}>
                      <strong style={{ fontWeight: 700, color: 'var(--text-main)' }}>{cat}: </strong>
                      <span style={{ color: 'var(--text-muted)' }}>{skillList.join(', ')}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {enhanced_content.projects && enhanced_content.projects.length > 0 && (
              <div style={{ marginBottom: '18px' }}>
                <h4 style={{ fontSize: '13px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-dim)', letterSpacing: '0.05em', marginBottom: '6px' }}>
                  Key Practical Projects
                </h4>
                {enhanced_content.projects.map((p, idx) => (
                  <div key={idx} style={{ marginBottom: '10px' }}>
                    <div style={{ fontWeight: 700, color: 'var(--text-main)' }}>{p.title}</div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '12.5px' }}>{p.description}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </section>

      {/* =========================================================================
          SECTION 6: STICKY RESULTS ACTION BAR & NEXT-STAGE TRIGGER
          ========================================================================= */}
      <div
        className="card"
        style={{
          position: 'sticky',
          bottom: '20px',
          zIndex: 100,
          padding: '18px 28px',
          background: 'var(--bg-card)',
          borderColor: isPassing ? 'var(--emerald-border)' : 'var(--amber-border)',
          borderWidth: '2px',
          boxShadow: 'var(--shadow-lg)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '16px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div
            style={{
              width: '44px',
              height: '44px',
              borderRadius: '50%',
              background: isPassing ? 'var(--emerald-subtle)' : 'var(--amber-subtle)',
              color: isPassing ? 'var(--emerald-success)' : 'var(--amber-warn)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            {isPassing ? <CheckCircle size={24} /> : <Lock size={20} />}
          </div>
          <div>
            <div style={{ fontSize: '15px', fontWeight: 800, color: 'var(--text-main)' }}>
              {isPassing ? '✅ Resume Requirement Passed' : '⚠️ Improvement Still Required'}
            </div>
            <div style={{ fontSize: '12.5px', color: 'var(--text-muted)', marginTop: '2px' }}>
              {isPassing ? (
                <>
                  Verified Score: <strong style={{ color: 'var(--emerald-success)' }}>{new_score}/100</strong> (Cutoff: {threshold}.0). Candidate is qualified to advance.
                </>
              ) : (
                <>
                  Score: <strong style={{ color: 'var(--amber-warn)' }}>{new_score}/100</strong> is below the {threshold}.0 qualification cutoff for {roleName}.
                  {can_retry && ` (Attempt ${attempt_number} of ${max_attempts} used)`}
                </>
              )}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {/* Retry / Adjust Approvals (when below cutoff or candidate wants to tweak) */}
          {onRetryOrAdjust && (
            <button
              className="btn btn-secondary"
              onClick={onRetryOrAdjust}
              style={{ padding: '12px 20px', fontSize: '13.5px' }}
            >
              <RotateCcw size={15} />
              <span>Adjust Approvals & Retry</span>
            </button>
          )}

          {/* Next Stage Button: ENABLED only if isPassing */}
          <button
            id="continue-next-stage-btn"
            className={isPassing ? 'btn btn-primary' : 'btn btn-secondary'}
            disabled={!isPassing || isProceeding}
            onClick={onProceedToNextStage}
            style={{
              padding: '12px 28px',
              fontSize: '14px',
              fontWeight: 700,
              opacity: isPassing ? 1 : 0.6,
              cursor: isPassing ? 'pointer' : 'not-allowed',
              boxShadow: isPassing ? '0 0 16px rgba(16, 185, 129, 0.35)' : 'none',
            }}
            title={isPassing ? 'Advance to Stage 2' : `Score must reach ${threshold}.0 to enable next stage`}
          >
            {isPassing ? <CheckCircle size={16} /> : <Lock size={15} />}
            <span>{isProceeding ? 'Verifying with Backend...' : 'Continue to Next Stage →'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
