import React, { useEffect, useState } from 'react';
import { ShieldCheck, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';

export type LoadingOperationType =
  | 'analyze_resume'
  | 'skill_gap_analysis'
  | 'project_plan'
  | 'create_resume'
  | 'rescoring'
  | 'pdf_generation'
  | 'generic';

interface OperationConfig {
  title: string;
  description: string;
  stages: string[];
}

const OPERATION_CONFIGS: Record<LoadingOperationType, OperationConfig> = {
  analyze_resume: {
    title: 'Analyzing Your Resume',
    description: 'Extracting resume information and evaluating role requirements.',
    stages: [
      'Validating document format and security',
      'Extracting skills, experience, and education',
      'Matching against role requirements',
      'Calculating deterministic ATS score',
      'Preparing evaluation results',
    ],
  },
  skill_gap_analysis: {
    title: 'Identifying Skill Gaps',
    description: 'Comparing your resume evidence with the selected role.',
    stages: [
      'Validating role competency model',
      'Comparing candidate evidence',
      'Categorizing core and preferred skills',
      'Calculating gap severity matrix',
      'Preparing action recommendations',
    ],
  },
  project_plan: {
    title: 'Preparing Your Project Plan',
    description: 'Organizing implementation steps, required technologies, and testing guidance.',
    stages: [
      'Selecting role practical blueprint',
      'Structuring multi-phase tasks',
      'Defining verification and testing criteria',
      'Generating expected deliverables',
      'Rendering DOCX and PDF guides',
    ],
  },
  create_resume: {
    title: 'Creating Your Improved Resume',
    description: 'Applying your approved changes and formatting the resume.',
    stages: [
      'Validating approved candidate changes',
      'Structuring ATS resume sections',
      'Scheduling standard ATS template',
      'Rendering DOCX and PDF documents',
      'Executing deterministic re-score',
    ],
  },
  rescoring: {
    title: 'Re-evaluating Your Resume',
    description: 'Calculating the updated score using the existing scoring criteria.',
    stages: [
      'Parsing updated resume content',
      'Re-evaluating skill matches',
      'Auditing category evidence',
      'Applying established scoring weights',
      'Generating score comparison report',
    ],
  },
  pdf_generation: {
    title: 'Preparing Your PDF',
    description: 'Rendering and validating your document.',
    stages: [
      'Loading document typography and geometry',
      'Laying out ATS section content',
      'Rendering vector text and elements',
      'Validating PDF structure',
      'Preparing download preview',
    ],
  },
  generic: {
    title: 'Processing Request',
    description: 'Please wait while FUTRSEC processes your request.',
    stages: [
      'Validating input',
      'Processing document',
      'Analyzing requirements',
      'Calculating score',
      'Preparing results',
    ],
  },
};

export interface LoadingOverlayProps {
  isOpen: boolean;
  operationType?: LoadingOperationType;
  customTitle?: string;
  customDescription?: string;
  error?: string | null;
  onRetry?: () => void;
  onClose?: () => void;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  isOpen,
  operationType = 'generic',
  customTitle,
  customDescription,
  error = null,
  onRetry,
  onClose,
}) => {
  const config = OPERATION_CONFIGS[operationType] || OPERATION_CONFIGS.generic;
  const title = customTitle || config.title;
  const description = customDescription || config.description;
  const stages = config.stages;

  const [activeStage, setActiveStage] = useState(0);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  // Progressive stage simulation: advance every few seconds without fake percentages
  useEffect(() => {
    if (!isOpen || error) {
      setActiveStage(0);
      setElapsedSeconds(0);
      return;
    }

    const stageTimer = setInterval(() => {
      setActiveStage((prev) => (prev < stages.length - 1 ? prev + 1 : prev));
    }, 2800);

    const elapsedTimer = setInterval(() => {
      setElapsedSeconds((s) => s + 1);
    }, 1000);

    return () => {
      clearInterval(stageTimer);
      clearInterval(elapsedTimer);
    };
  }, [isOpen, error, stages.length]);

  if (!isOpen) return null;

  return (
    <div
      role="status"
      aria-live="polite"
      aria-busy={!error}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px',
        backgroundColor: 'rgba(15, 23, 42, 0.55)',
        backdropFilter: 'blur(4px)',
        WebkitBackdropFilter: 'blur(4px)',
        animation: 'fadeIn 0.2s ease-out',
      }}
    >
      <div
        className="card"
        style={{
          width: '100%',
          maxWidth: '480px',
          background: 'var(--bg-card)',
          borderColor: error ? 'var(--rose-border)' : 'var(--border-strong)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-lg)',
          padding: '28px 32px',
          display: 'flex',
          flexDirection: 'column',
          gap: '18px',
          position: 'relative',
        }}
      >
        {/* Header with FUTRSEC Branding */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div
              style={{
                width: '28px',
                height: '28px',
                borderRadius: 'var(--radius-sm)',
                background: error ? 'var(--rose-subtle)' : 'var(--primary-subtle)',
                color: error ? 'var(--rose-danger)' : 'var(--primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <ShieldCheck size={18} />
            </div>
            <span
              style={{
                fontSize: '11.5px',
                fontWeight: 800,
                letterSpacing: '0.06em',
                color: 'var(--text-dim)',
                textTransform: 'uppercase',
              }}
            >
              FUTRSEC AI RESUME ENGINE
            </span>
          </div>

          <span
            className={`badge ${error ? 'badge-rose' : 'badge-primary'}`}
            style={{ fontSize: '10.5px' }}
          >
            {error ? 'Action Interrupted' : 'Processing'}
          </span>
        </div>

        {/* Center Animation or Error Icon */}
        {!error ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: '14px', paddingTop: '6px' }}>
            {/* Enterprise Restrained Spinner */}
            <div
              className="loading-circular-spinner"
              aria-hidden="true"
              style={{
                width: '46px',
                height: '46px',
                borderRadius: '50%',
                border: '3.5px solid var(--border-subtle)',
                borderTopColor: 'var(--primary)',
                animation: 'futrsecSpin 0.9s cubic-bezier(0.5, 0.1, 0.4, 0.9) infinite',
              }}
            />

            <div>
              <h3
                style={{
                  fontSize: '17px',
                  fontWeight: 800,
                  color: 'var(--text-main)',
                  margin: '0 0 6px',
                }}
              >
                {title}
              </h3>
              <p
                style={{
                  fontSize: '13px',
                  color: 'var(--text-muted)',
                  margin: 0,
                  lineHeight: 1.45,
                }}
              >
                {description}
              </p>
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: '12px', paddingTop: '4px' }}>
            <div
              style={{
                width: '46px',
                height: '46px',
                borderRadius: '50%',
                background: 'var(--rose-subtle)',
                border: '2px solid var(--rose-border)',
                color: 'var(--rose-danger)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <AlertCircle size={26} />
            </div>
            <div>
              <h3
                style={{
                  fontSize: '16.5px',
                  fontWeight: 800,
                  color: 'var(--rose-danger)',
                  margin: '0 0 6px',
                }}
              >
                Operation Failed
              </h3>
              <p
                style={{
                  fontSize: '13px',
                  color: 'var(--text-muted)',
                  margin: 0,
                  lineHeight: 1.45,
                }}
              >
                {error}
              </p>
            </div>
          </div>
        )}

        {/* Progress Stages (Deterministic, no fake percentages) */}
        {!error && (
          <div
            style={{
              background: 'var(--bg-subtle)',
              padding: '12px 14px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px',
            }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                fontSize: '11px',
                fontWeight: 700,
                color: 'var(--text-dim)',
                textTransform: 'uppercase',
                letterSpacing: '0.04em',
              }}
            >
              <span>Current Stage</span>
              <span className="mono" style={{ color: 'var(--primary)' }}>
                {activeStage + 1} of {stages.length}
              </span>
            </div>

            {/* Stages Stack */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {stages.map((stageText, idx) => {
                const isCompleted = idx < activeStage;
                const isCurrent = idx === activeStage;

                return (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      fontSize: '12px',
                      color: isCurrent
                        ? 'var(--text-main)'
                        : isCompleted
                        ? 'var(--emerald-success)'
                        : 'var(--text-dim)',
                      fontWeight: isCurrent ? 700 : 500,
                      opacity: idx > activeStage ? 0.45 : 1,
                      transition: 'all 0.25s ease',
                    }}
                  >
                    {isCompleted ? (
                      <CheckCircle2 size={13} color="var(--emerald-success)" />
                    ) : isCurrent ? (
                      <div
                        style={{
                          width: '8px',
                          height: '8px',
                          borderRadius: '50%',
                          background: 'var(--primary)',
                          boxShadow: '0 0 8px var(--primary)',
                          animation: 'pulse 1.2s infinite',
                        }}
                      />
                    ) : (
                      <div
                        style={{
                          width: '7px',
                          height: '7px',
                          borderRadius: '50%',
                          background: 'var(--border-strong)',
                        }}
                      />
                    )}
                    <span>{stageText}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Helpful Timeout Reassurance Notice if >12 seconds */}
        {!error && elapsedSeconds >= 12 && (
          <div
            style={{
              fontSize: '11.5px',
              color: 'var(--text-dim)',
              textAlign: 'center',
              lineHeight: 1.4,
              padding: '6px 10px',
              borderRadius: 'var(--radius-xs)',
              background: 'var(--bg-card)',
              border: '1px dashed var(--border-subtle)',
            }}
          >
            Deep ATS scoring and document validation in progress. Thank you for your patience...
          </div>
        )}

        {/* Error Actions */}
        {error && (
          <div
            style={{
              display: 'flex',
              justifyContent: 'flex-end',
              gap: '10px',
              marginTop: '4px',
            }}
          >
            {onClose && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={onClose}
                style={{ fontSize: '12.5px', padding: '7px 16px' }}
              >
                Dismiss
              </button>
            )}
            {onRetry && (
              <button
                type="button"
                className="btn btn-primary"
                onClick={onRetry}
                style={{ fontSize: '12.5px', padding: '7px 18px' }}
              >
                <RefreshCw size={13} />
                <span>Retry Operation</span>
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
