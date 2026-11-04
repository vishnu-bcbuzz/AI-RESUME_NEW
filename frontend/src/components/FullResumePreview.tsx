import React from 'react';
import {
  Download,
  FileText,
  RotateCcw,
  CheckCircle,
  AlertTriangle,
  Award,
  Layers,
  Sparkles,
  ExternalLink,
  ShieldAlert,
} from 'lucide-react';
import { ImprovementResponse } from '../types';

interface FullResumePreviewProps {
  improvement: ImprovementResponse;
  roleName: string;
  onReturnToConfirmation: () => void;
  onAccept: () => void;
  isAccepting?: boolean;
}

export const FullResumePreview: React.FC<FullResumePreviewProps> = ({
  improvement,
  roleName,
  onReturnToConfirmation,
  onAccept,
  isAccepting = false,
}) => {
  const {
    assigned_template,
    enhanced_content,
    documents,
    confirmed_skills_included = [],
    unverified_skills_excluded = [],
    sections_rewritten = [],
    future_learning_recommendations = [],
  } = improvement;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* METADATA & REWRITE SUMMARY BANNER */}
      <div
        className="card"
        style={{
          padding: '20px 24px',
          background: 'var(--bg-card)',
          borderColor: 'var(--border-subtle)',
          boxShadow: 'var(--shadow-sm)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px', marginBottom: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span className="badge badge-primary">Round Robin Assigned</span>
              <span className="badge badge-subtle">Target Role: {roleName}</span>
            </div>
            <h3 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
              {assigned_template.template_name}
            </h3>
            <div style={{ fontSize: '12.5px', color: 'var(--text-muted)', marginTop: '2px' }}>
              {assigned_template.description}
            </div>
          </div>

          {/* DOWNLOAD & EDIT ACTIONS */}
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
            <button
              className="btn btn-secondary"
              onClick={onReturnToConfirmation}
              style={{ padding: '9px 16px', fontSize: '13px' }}
            >
              <RotateCcw size={14} />
              <span>Edit Confirmed Skills</span>
            </button>

            {documents.docx_url && (
              <a
                href={documents.docx_url}
                download
                className="btn btn-secondary"
                style={{ padding: '9px 16px', fontSize: '13px' }}
              >
                <Download size={14} />
                <span>Download DOCX</span>
              </a>
            )}

            {documents.pdf_url && (
              <a
                href={documents.pdf_url}
                download
                className="btn btn-secondary"
                style={{ padding: '9px 16px', fontSize: '13px' }}
              >
                <Download size={14} />
                <span>Download PDF</span>
              </a>
            )}
          </div>
        </div>

        {/* VERIFICATION & EXCLUSION BADGES */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '12px', paddingTop: '14px', borderTop: '1px solid var(--border-subtle)' }}>
          {/* Confirmed Skills Included */}
          <div style={{ background: 'var(--emerald-subtle)', padding: '12px 14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--emerald-border)' }}>
            <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--emerald-success)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '4px' }}>
              Confirmed Skills Included ({confirmed_skills_included.length})
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {confirmed_skills_included.length > 0 ? (
                confirmed_skills_included.map((s) => (
                  <span key={s} className="badge badge-emerald" style={{ fontSize: '11px' }}>
                    ✓ {s}
                  </span>
                ))
              ) : (
                <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>Original resume competencies preserved</span>
              )}
            </div>
          </div>

          {/* Substantially Rewritten Sections */}
          <div style={{ background: 'var(--primary-subtle)', padding: '12px 14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--primary-border)' }}>
            <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '4px' }}>
              Sections Substantially Rewritten ({sections_rewritten.length})
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {sections_rewritten.map((sec) => (
                <span key={sec} className="badge badge-primary" style={{ fontSize: '11px' }}>
                  {sec}
                </span>
              ))}
            </div>
          </div>

          {/* Unverified Skills Excluded */}
          <div style={{ background: 'var(--amber-subtle)', padding: '12px 14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--amber-border)' }}>
            <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--amber-warn)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '4px' }}>
              Deliberately Excluded (Unverified) ({unverified_skills_excluded.length})
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {unverified_skills_excluded.length > 0 ? (
                unverified_skills_excluded.map((s) => (
                  <span key={s} className="badge badge-amber" style={{ fontSize: '11px' }}>
                    ✕ {s}
                  </span>
                ))
              ) : (
                <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>No unverified skills excluded</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* RENDERED DOCUMENT PREVIEW SHEET (ATS FORMAT) */}
      <div
        className="card"
        style={{
          background: 'var(--bg-card)',
          borderColor: 'var(--border-subtle)',
          boxShadow: 'var(--shadow-md)',
          padding: '48px 56px',
          maxWidth: '850px',
          width: '100%',
          margin: '0 auto',
          fontFamily: assigned_template.style_config?.font_family || 'Calibri, sans-serif',
          lineHeight: 1.5,
          color: 'var(--text-main)',
        }}
      >
        {/* RESUME HEADER */}
        <div style={{ textAlign: assigned_template.style_config?.header_alignment === 'center' ? 'center' : 'left', marginBottom: '20px', borderBottom: '1.5px solid var(--border-subtle)', paddingBottom: '16px' }}>
          <h1 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--primary)', margin: 0, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            {enhanced_content.candidate_name}
          </h1>

          {enhanced_content.professional_headline && (
            <div style={{ fontSize: '13.5px', fontWeight: 700, color: 'var(--text-muted)', marginTop: '4px' }}>
              {enhanced_content.professional_headline}
            </div>
          )}

          <div style={{ fontSize: '12px', color: 'var(--text-dim)', marginTop: '6px' }}>
            {enhanced_content.contact_header}
          </div>
        </div>

        {/* PROFESSIONAL SUMMARY */}
        {enhanced_content.professional_summary && (
          <div style={{ marginBottom: '20px' }}>
            <div style={{ fontSize: '12px', fontWeight: 800, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '4px', marginBottom: '8px' }}>
              Professional Summary
            </div>
            <p style={{ fontSize: '13px', color: 'var(--text-main)', margin: 0, lineHeight: 1.6 }}>
              {enhanced_content.professional_summary}
            </p>
          </div>
        )}

        {/* TECHNICAL SKILLS */}
        {enhanced_content.technical_skills_grouped && Object.keys(enhanced_content.technical_skills_grouped).length > 0 && (
          <div style={{ marginBottom: '18px' }}>
            <div style={{ fontSize: '12px', fontWeight: 800, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '4px', marginBottom: '8px' }}>
              Technical Skills
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '3px', fontSize: '13px', lineHeight: 1.3 }}>
              {Object.entries(enhanced_content.technical_skills_grouped).map(([group, skills]) => {
                const skillList = Array.isArray(skills) ? skills : [];
                if (skillList.length === 0) return null;
                return (
                  <div key={group} style={{ textAlign: 'left' }}>
                    <strong style={{ fontWeight: 700, color: 'var(--text-main)' }}>{group}: </strong>
                    <span style={{ color: 'var(--text-muted)' }}>{skillList.join(', ')}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* PROJECTS */}
        {enhanced_content.projects && enhanced_content.projects.length > 0 && (
          <div style={{ marginBottom: '20px' }}>
            <div style={{ fontSize: '12px', fontWeight: 800, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '4px', marginBottom: '10px' }}>
              Projects
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {enhanced_content.projects.map((p, idx) => (
                <div key={idx}>
                  <div style={{ fontSize: '13.5px', fontWeight: 700, color: 'var(--text-main)' }}>
                    {p.title}
                  </div>
                  <p style={{ fontSize: '12.5px', color: 'var(--text-muted)', margin: '4px 0 2px 0', lineHeight: 1.5 }}>
                    {p.description}
                  </p>
                  {p.technologies && p.technologies.length > 0 && (
                    <div style={{ fontSize: '11.5px', color: 'var(--text-dim)', fontStyle: 'italic' }}>
                      Technologies: {p.technologies.join(', ')}
                    </div>
                  )}
                  {p.outcomes && (
                    <div style={{ fontSize: '12px', color: 'var(--emerald-success)', fontWeight: 600, marginTop: '2px' }}>
                      Outcome / Evidence: {p.outcomes}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* PROFESSIONAL EXPERIENCE */}
        {enhanced_content.experience && enhanced_content.experience.length > 0 && (
          <div style={{ marginBottom: '20px' }}>
            <div style={{ fontSize: '12px', fontWeight: 800, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '4px', marginBottom: '10px' }}>
              Professional Experience
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {enhanced_content.experience.map((exp, idx) => (
                <div key={idx}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
                    <span style={{ fontSize: '13.5px', fontWeight: 700, color: 'var(--text-main)' }}>
                      {exp.job_title} | {exp.company}
                    </span>
                    {exp.start_date && (
                      <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>
                        {exp.start_date} - {exp.end_date || 'Present'}
                      </span>
                    )}
                  </div>
                  <ul style={{ margin: '6px 0 0 18px', padding: 0, fontSize: '12.5px', color: 'var(--text-muted)' }}>
                    {exp.responsibilities?.map((r: string, rIdx: number) => (
                      <li key={rIdx} style={{ marginBottom: '3px' }}>
                        {r}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* EDUCATION & QUALIFICATIONS */}
        {enhanced_content.education && enhanced_content.education.length > 0 && (
          <div style={{ marginBottom: '20px' }}>
            <div style={{ fontSize: '12px', fontWeight: 800, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '4px', marginBottom: '8px' }}>
              Education & Academic Credentials
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '13px' }}>
              {enhanced_content.education.map((edu, idx) => (
                <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <strong style={{ color: 'var(--text-main)' }}>{edu.degree}</strong>
                    {edu.field_of_study && <span> in {edu.field_of_study}</span>}
                    <span style={{ color: 'var(--text-muted)' }}> — {edu.institution}</span>
                  </div>
                  {edu.graduation_year && (
                    <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>
                      {edu.graduation_year}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CERTIFICATIONS */}
        {enhanced_content.certifications && enhanced_content.certifications.length > 0 && (
          <div style={{ marginBottom: '14px' }}>
            <div style={{ fontSize: '12px', fontWeight: 800, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '4px', marginBottom: '8px' }}>
              Earned Industry Certifications
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {enhanced_content.certifications.map((c) => (
                <span key={c} className="badge badge-emerald" style={{ fontSize: '12px' }}>
                  <Award size={13} />
                  {c}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
