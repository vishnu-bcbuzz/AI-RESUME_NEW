import React, { useState } from 'react';
import {
  HelpCircle,
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
  ArrowRight,
  BookOpen,
  Sparkles,
  ChevronDown,
  ChevronUp,
  FileCheck,
  RotateCcw,
} from 'lucide-react';
import { ConfirmedSkillItem, SkillConfirmationQuestion } from '../types';

interface SkillConfirmationPanelProps {
  roleName: string;
  questions: SkillConfirmationQuestion[];
  onConfirm: (confirmedSkills: ConfirmedSkillItem[], permissionGranted: boolean) => void;
  onSkip: () => void;
  isLoading: boolean;
  initialAnswers?: ConfirmedSkillItem[];
}

export const SkillConfirmationPanel: React.FC<SkillConfirmationPanelProps> = ({
  roleName,
  questions,
  onConfirm,
  onSkip,
  isLoading,
  initialAnswers = [],
}) => {
  // Initialize state from initialAnswers or defaults
  const [answers, setAnswers] = useState<Record<string, ConfirmedSkillItem>>(() => {
    const map: Record<string, ConfirmedSkillItem> = {};
    initialAnswers.forEach((ans) => {
      map[ans.skill_name] = ans;
    });
    return map;
  });

  const [permissionGranted, setPermissionGranted] = useState<boolean>(true);
  const [expandedSkill, setExpandedSkill] = useState<string | null>(
    questions.length > 0 ? questions[0].skill_name : null
  );
  const [showReviewModal, setShowReviewModal] = useState<boolean>(false);

  const handleProficiencyChange = (
    skillName: string,
    proficiency: 'hands_on' | 'basic_familiarity' | 'not_used'
  ) => {
    setAnswers((prev) => ({
      ...prev,
      [skillName]: {
        skill_name: skillName,
        proficiency,
        context_source: prev[skillName]?.context_source || 'Academic Project',
        tasks_performed: prev[skillName]?.tasks_performed || '',
        interview_demonstration: prev[skillName]?.interview_demonstration || '',
      },
    }));
  };

  const handleDetailChange = (
    skillName: string,
    field: 'context_source' | 'tasks_performed' | 'interview_demonstration',
    value: string
  ) => {
    setAnswers((prev) => {
      const existing = prev[skillName] || {
        skill_name: skillName,
        proficiency: 'hands_on',
      };
      return {
        ...prev,
        [skillName]: {
          ...existing,
          [field]: value,
        },
      };
    });
  };

  const handleConfirmAndContinue = () => {
    const list = Object.values(answers);
    onConfirm(list, permissionGranted);
  };

  const confirmedCount = Object.values(answers).filter(
    (a) => a.proficiency === 'hands_on' || a.proficiency === 'basic_familiarity'
  ).length;

  const notUsedCount = Object.values(answers).filter(
    (a) => a.proficiency === 'not_used'
  ).length;

  if (questions.length === 0) {
    return null;
  }

  return (
    <div
      className="card"
      style={{
        padding: '28px 32px',
        borderColor: 'var(--primary)',
        background: 'var(--bg-card)',
        boxShadow: 'var(--shadow-md)',
      }}
    >
      {/* HEADER SECTION */}
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '16px', marginBottom: '22px' }}>
        <div
          style={{
            width: '42px',
            height: '42px',
            borderRadius: '10px',
            background: 'var(--primary-subtle)',
            color: 'var(--primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
            border: '1px solid var(--primary-border)',
          }}
        >
          <HelpCircle size={22} />
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            <span className="badge badge-primary">Step 2: Smart Skill-Gap Confirmation</span>
            <span className="badge badge-subtle">
              {questions.length} Role Skills to Verify
            </span>
          </div>
          <h3 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-main)', margin: '6px 0 4px 0' }}>
            Let's improve your resume
          </h3>
          <p style={{ fontSize: '13.5px', color: 'var(--text-muted)', margin: 0, lineHeight: 1.5 }}>
            Your resume is missing evidence for several skills required by the{' '}
            <strong style={{ color: 'var(--text-main)' }}>{roleName}</strong> role. Before creating your improved
            resume, please confirm which skills you actually possess. We will only incorporate skills you truthfully verify.
          </p>
        </div>
      </div>

      {/* SKILL CONFIRMATION CARDS */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '24px' }}>
        {questions.map((q, idx) => {
          const currentAns = answers[q.skill_name];
          const currentProficiency = currentAns?.proficiency;
          const isExpanded = expandedSkill === q.skill_name;
          const hasAnswered = !!currentProficiency;

          return (
            <div
              key={q.skill_name}
              style={{
                border: '1px solid',
                borderColor: hasAnswered
                  ? currentProficiency === 'not_used'
                    ? 'var(--border-subtle)'
                    : 'var(--primary-border)'
                  : 'var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                background: hasAnswered && currentProficiency !== 'not_used'
                  ? 'var(--bg-card)'
                  : 'var(--bg-subtle)',
                overflow: 'hidden',
                transition: 'all 0.2s ease',
              }}
            >
              {/* SKILL CARD TITLE ROW */}
              <div
                onClick={() => setExpandedSkill(isExpanded ? null : q.skill_name)}
                style={{
                  padding: '14px 18px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  cursor: 'pointer',
                  userSelect: 'none',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span
                    style={{
                      width: '26px',
                      height: '26px',
                      borderRadius: '50%',
                      background: hasAnswered
                        ? currentProficiency === 'not_used'
                          ? 'var(--bg-subtle)'
                          : 'var(--primary-subtle)'
                        : 'var(--bg-card)',
                      color: hasAnswered
                        ? currentProficiency === 'not_used'
                          ? 'var(--text-dim)'
                          : 'var(--primary)'
                        : 'var(--text-dim)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '11px',
                      fontWeight: 700,
                      border: '1px solid var(--border-subtle)',
                    }}
                  >
                    {idx + 1}
                  </span>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '14.5px', fontWeight: 700, color: 'var(--text-main)' }}>
                        {q.skill_name}
                      </span>
                      <span
                        className={
                          q.importance === 'core'
                            ? 'badge badge-rose'
                            : q.importance === 'preferred'
                            ? 'badge badge-primary'
                            : 'badge badge-subtle'
                        }
                        style={{ fontSize: '10.5px' }}
                      >
                        {q.importance.toUpperCase()}
                      </span>
                      <span style={{ fontSize: '11.5px', color: 'var(--text-dim)' }}>
                        {q.category}
                      </span>
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  {hasAnswered && (
                    <span
                      className={
                        currentProficiency === 'hands_on'
                          ? 'badge badge-emerald'
                          : currentProficiency === 'basic_familiarity'
                          ? 'badge badge-primary'
                          : 'badge badge-subtle'
                      }
                      style={{ fontSize: '11px' }}
                    >
                      {currentProficiency === 'hands_on'
                        ? 'Hands-on Confirmed'
                        : currentProficiency === 'basic_familiarity'
                        ? 'Basic Familiarity'
                        : 'Not Used Yet'}
                    </span>
                  )}
                  {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </div>
              </div>

              {/* EXPANDED CONFIRMATION CONTROLS */}
              {isExpanded && (
                <div
                  style={{
                    padding: '16px 20px 20px 20px',
                    borderTop: '1px solid var(--border-subtle)',
                    background: 'var(--bg-card)',
                  }}
                >
                  <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '14px' }}>
                    {q.prompt_question}
                  </p>

                  {/* PROFICIENCY CHOICES */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '10px', marginBottom: '16px' }}>
                    {q.options.map((opt) => {
                      const isSelected = currentProficiency === opt.value;
                      return (
                        <label
                          key={opt.value}
                          style={{
                            display: 'flex',
                            alignItems: 'flex-start',
                            gap: '10px',
                            padding: '12px 14px',
                            borderRadius: 'var(--radius-sm)',
                            border: `1.5px solid ${isSelected ? 'var(--primary)' : 'var(--border-subtle)'}`,
                            background: isSelected ? 'var(--primary-subtle)' : 'var(--bg-subtle)',
                            cursor: 'pointer',
                            transition: 'all 0.15s ease',
                          }}
                        >
                          <input
                            type="radio"
                            name={`skill_${q.skill_name}`}
                            value={opt.value}
                            checked={isSelected}
                            onChange={() => handleProficiencyChange(q.skill_name, opt.value as any)}
                            style={{ marginTop: '3px' }}
                          />
                          <div>
                            <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-main)' }}>
                              {opt.label}
                            </div>
                            <div style={{ fontSize: '11.5px', color: 'var(--text-dim)', marginTop: '2px', lineHeight: 1.3 }}>
                              {opt.description}
                            </div>
                          </div>
                        </label>
                      );
                    })}
                  </div>

                  {/* CONDITIONAL SUPPORTING DETAILS (IF HANDS-ON OR FAMILIARITY) */}
                  {(currentProficiency === 'hands_on' || currentProficiency === 'basic_familiarity') && (
                    <div
                      style={{
                        padding: '16px',
                        borderRadius: 'var(--radius-sm)',
                        background: 'var(--bg-subtle)',
                        border: '1px solid var(--border-subtle)',
                        marginTop: '12px',
                      }}
                    >
                      <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                        Supporting Experience Details for {q.skill_name}
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '12px', marginBottom: '12px' }}>
                        <div>
                          <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-main)', display: 'block', marginBottom: '4px' }}>
                            Where did you use it?
                          </label>
                          <select
                            value={currentAns?.context_source || 'Academic Project'}
                            onChange={(e) => handleDetailChange(q.skill_name, 'context_source', e.target.value)}
                            style={{
                              width: '100%',
                              padding: '8px 10px',
                              borderRadius: 'var(--radius-sm)',
                              border: '1px solid var(--border-subtle)',
                              background: 'var(--bg-card)',
                              color: 'var(--text-main)',
                              fontSize: '12.5px',
                            }}
                          >
                            {q.context_options.map((ctx) => (
                              <option key={ctx} value={ctx}>
                                {ctx}
                              </option>
                            ))}
                          </select>
                        </div>

                        <div>
                          <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-main)', display: 'block', marginBottom: '4px' }}>
                            What tasks did you perform?
                          </label>
                          <input
                            type="text"
                            placeholder="e.g. Vulnerability scanning, intercepting HTTP traffic, testing input validation"
                            value={currentAns?.tasks_performed || ''}
                            onChange={(e) => handleDetailChange(q.skill_name, 'tasks_performed', e.target.value)}
                            style={{
                              width: '100%',
                              padding: '8px 10px',
                              borderRadius: 'var(--radius-sm)',
                              border: '1px solid var(--border-subtle)',
                              background: 'var(--bg-card)',
                              color: 'var(--text-main)',
                              fontSize: '12.5px',
                            }}
                          />
                        </div>
                      </div>

                      <div>
                        <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-main)', display: 'block', marginBottom: '4px' }}>
                          What can you explain or demonstrate in an interview?
                        </label>
                        <input
                          type="text"
                          placeholder="e.g. Can demonstrate Repeater tab usage, payload injection, and explaining scan reports"
                          value={currentAns?.interview_demonstration || ''}
                          onChange={(e) => handleDetailChange(q.skill_name, 'interview_demonstration', e.target.value)}
                          style={{
                            width: '100%',
                            padding: '8px 10px',
                            borderRadius: 'var(--radius-sm)',
                            border: '1px solid var(--border-subtle)',
                            background: 'var(--bg-card)',
                            color: 'var(--text-main)',
                            fontSize: '12.5px',
                          }}
                        />
                      </div>
                    </div>
                  )}

                  {/* NOT USED EXPLANATION */}
                  {currentProficiency === 'not_used' && (
                    <div style={{ fontSize: '12.5px', color: 'var(--text-dim)', fontStyle: 'italic', marginTop: '6px' }}>
                      💡 This skill will NOT be added to your resume. It will be recommended as a future learning goal.
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* PERMISSION & CONSENT CHECKBOX */}
      <div
        style={{
          padding: '16px 20px',
          borderRadius: 'var(--radius-sm)',
          background: 'var(--primary-subtle)',
          border: '1px solid var(--primary-border)',
          display: 'flex',
          alignItems: 'center',
          gap: '14px',
          marginBottom: '22px',
        }}
      >
        <ShieldCheck size={24} color="var(--primary)" style={{ flexShrink: 0 }} />
        <div style={{ flex: 1 }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={permissionGranted}
              onChange={(e) => setPermissionGranted(e.target.checked)}
              style={{ width: '16px', height: '16px', cursor: 'pointer' }}
            />
            <span style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-main)' }}>
              Use my confirmed information to improve my resume.
            </span>
          </label>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px', marginLeft: '26px' }}>
            Only skills you confirmed as hands-on or basic familiarity will be incorporated. Unconfirmed skills and unearned certifications are strictly excluded.
          </div>
        </div>
      </div>

      {/* ACTION BUTTONS */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
          <button
            id="confirm-continue-btn"
            className="btn btn-primary"
            onClick={handleConfirmAndContinue}
            disabled={isLoading}
            style={{ padding: '12px 24px', fontSize: '14px' }}
          >
            <Sparkles size={16} />
            <span>Confirm and Continue</span>
            <ArrowRight size={15} />
          </button>

          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => setShowReviewModal(!showReviewModal)}
            style={{ padding: '12px 18px', fontSize: '13.5px' }}
          >
            <FileCheck size={15} />
            <span>Review My Answers ({confirmedCount} Confirmed, {notUsedCount} Excluded)</span>
          </button>
        </div>

        <button
          type="button"
          className="btn btn-secondary"
          onClick={onSkip}
          disabled={isLoading}
          style={{ padding: '12px 18px', fontSize: '13px', color: 'var(--text-dim)' }}
          title="Proceed without adding any unverified skills"
        >
          <span>Skip Unconfirmed Skills</span>
        </button>
      </div>

      {/* REVIEW SUMMARY DRAWER / MODAL */}
      {showReviewModal && (
        <div
          style={{
            marginTop: '20px',
            padding: '18px 22px',
            borderRadius: 'var(--radius-sm)',
            background: 'var(--bg-subtle)',
            border: '1px solid var(--border-subtle)',
          }}
        >
          <div style={{ fontSize: '13.5px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '10px' }}>
            Summary of Confirmed Skills for {roleName}:
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12.5px' }}>
            {Object.values(answers).map((ans) => (
              <div key={ans.skill_name} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{ans.skill_name}</span>
                <span
                  className={
                    ans.proficiency === 'hands_on'
                      ? 'badge badge-emerald'
                      : ans.proficiency === 'basic_familiarity'
                      ? 'badge badge-primary'
                      : 'badge badge-subtle'
                  }
                >
                  {ans.proficiency === 'hands_on'
                    ? `Hands-on (${ans.context_source || 'Project'})`
                    : ans.proficiency === 'basic_familiarity'
                    ? 'Basic Familiarity'
                    : 'Excluded (Not Used)'}
                </span>
              </div>
            ))}
            {Object.keys(answers).length === 0 && (
              <span style={{ color: 'var(--text-dim)' }}>No skills answered yet.</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
