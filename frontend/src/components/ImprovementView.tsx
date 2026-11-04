import React from 'react';
import {
  FileText,
  Download,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  ArrowRight,
} from 'lucide-react';
import { ImprovementResponse } from '../types';

interface ImprovementViewProps {
  improvement: ImprovementResponse;
  onAcceptAndRescore: () => void;
  isRescoring: boolean;
}

export const ImprovementView: React.FC<ImprovementViewProps> = ({
  improvement,
  onAcceptAndRescore,
  isRescoring,
}) => {
  const { assigned_template, enhanced_content, documents, original_score, role_name } = improvement;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Template Assignment Banner */}
      <div
        className="card"
        style={{
          padding: '24px 28px',
          background: 'var(--primary-subtle)',
          borderColor: 'var(--primary-border)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span className="badge badge-primary">
                {improvement.selection_mode === 'manual' ? (
                  <>
                    <CheckCircle2 size={12} /> CANDIDATE-SELECTED TEMPLATE
                  </>
                ) : (
                  <>
                    <RefreshCw size={12} /> ROUND ROBIN TEMPLATE SELECTION
                  </>
                )}
              </span>
              <span className="badge badge-subtle">{assigned_template.template_id}</span>
            </div>
            <h2 style={{ fontSize: '22px', fontWeight: 800, color: 'var(--text-main)' }}>
              Assigned Template: {assigned_template.template_name}
            </h2>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px', maxWidth: '600px' }}>
              {assigned_template.description}
            </p>
          </div>

          {/* Download Buttons */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
            <a
              id="download-docx-btn"
              href={documents.docx_url}
              download
              className="btn btn-primary"
              style={{ padding: '10px 18px' }}
            >
              <Download size={15} />
              <span>Download DOCX (Editable)</span>
            </a>

            {documents.pdf_url ? (
              <a
                id="download-pdf-btn"
                href={documents.pdf_url}
                download
                className="btn btn-secondary"
                style={{ padding: '10px 18px' }}
              >
                <Download size={15} />
                <span>Download PDF</span>
              </a>
            ) : (
              <span className="badge badge-subtle" title={documents.pdf_status_note}>
                DOCX primary (PDF limitation noted)
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Confirmation & Pending Checks */}
      {enhanced_content.pending_confirmations.length > 0 && (
        <div
          className="card"
          style={{
            padding: '16px 20px',
            background: 'var(--amber-subtle)',
            borderColor: 'var(--amber-border)',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '12px',
          }}
        >
          <AlertCircle size={20} color="var(--amber-warn)" style={{ marginTop: '2px', flexShrink: 0 }} />
          <div>
            <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--amber-warn)', marginBottom: '4px' }}>
              Factual Integrity Notice & Candidate Confirmations
            </div>
            <ul style={{ fontSize: '13px', color: 'var(--text-muted)', paddingLeft: '18px', lineHeight: 1.5 }}>
              {enhanced_content.pending_confirmations.map((note, idx) => (
                <li key={idx}>{note}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Preview of Enhanced ATS Resume Content */}
      <div className="card" style={{ padding: '28px' }}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px',
            borderBottom: '1px solid var(--border-subtle)',
            paddingBottom: '16px',
            flexWrap: 'wrap',
            gap: '14px',
          }}
        >
          <div>
            <h3 style={{ fontSize: '17px', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileText size={18} color="var(--primary)" />
              Enhanced ATS Resume Content Preview
            </h3>
            <p style={{ fontSize: '12.5px', color: 'var(--text-dim)' }}>
              Optimized via {enhanced_content.generator_mode} • Single-column ATS structure
            </p>
          </div>

          {/* Accept & Rescore CTA Button */}
          <button
            id="accept-and-rescore-btn"
            className="btn btn-success"
            onClick={onAcceptAndRescore}
            disabled={isRescoring}
            style={{ padding: '11px 22px', fontSize: '14px' }}
          >
            <CheckCircle2 size={17} />
            <span>{isRescoring ? 'Recalculating Score...' : 'Accept Improvements & Recalculate Score'}</span>
            <ArrowRight size={15} />
          </button>
        </div>

        {/* Formatted Content Card */}
        <div
          style={{
            background: 'var(--bg-subtle)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            padding: '24px',
            fontFamily: assigned_template.style_config?.font_family || 'var(--font-body)',
          }}
        >
          {/* Header */}
          <div style={{ textAlign: assigned_template.style_config?.header_alignment === 'center' ? 'center' : 'left', marginBottom: '18px' }}>
            <h1 style={{ fontSize: '22px', fontWeight: 800, color: 'var(--text-main)' }}>{enhanced_content.candidate_name}</h1>
            <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
              {enhanced_content.contact_header}
            </div>
          </div>

          {/* Professional Summary */}
          {enhanced_content.professional_summary && (
            <div style={{ marginBottom: '18px' }}>
              <div style={{ fontSize: '13.5px', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', marginBottom: '6px' }}>
                Professional Summary
              </div>
              <p style={{ fontSize: '13.5px', color: 'var(--text-main)', lineHeight: 1.6 }}>
                {enhanced_content.professional_summary}
              </p>
            </div>
          )}

          {/* Technical Skills Grouped */}
          {Object.keys(enhanced_content.technical_skills_grouped).length > 0 && (
            <div style={{ marginBottom: '16px' }}>
              <div style={{ fontSize: '13.5px', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', marginBottom: '6px' }}>
                Technical Skills & Competencies
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '3px', fontSize: '13px', lineHeight: 1.3 }}>
                {Object.entries(enhanced_content.technical_skills_grouped).map(([grp, items]) => {
                  const skillList = Array.isArray(items) ? items : [];
                  if (skillList.length === 0) return null;
                  return (
                    <div key={grp} style={{ textAlign: 'left', color: 'var(--text-main)' }}>
                      <strong style={{ fontWeight: 700, color: 'var(--text-main)' }}>{grp}: </strong>
                      <span style={{ color: 'var(--text-muted)' }}>{skillList.join(', ')}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Experience */}
          {enhanced_content.experience.length > 0 && (
            <div style={{ marginBottom: '18px' }}>
              <div style={{ fontSize: '13.5px', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', marginBottom: '8px' }}>
                Professional Experience
              </div>
              {enhanced_content.experience.map((exp, i) => (
                <div key={i} style={{ marginBottom: '12px' }}>
                  <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-main)' }}>
                    {exp.job_title} <span style={{ color: 'var(--text-dim)', fontWeight: 400 }}>| {exp.company}</span>
                  </div>
                  <ul style={{ paddingLeft: '18px', marginTop: '4px', fontSize: '13px', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                    {exp.responsibilities?.map((r: string, idx: number) => (
                      <li key={idx}>{r}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}

          {/* Projects */}
          {enhanced_content.projects.length > 0 && (
            <div style={{ marginBottom: '18px' }}>
              <div style={{ fontSize: '13.5px', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', marginBottom: '8px' }}>
                Technical Projects
              </div>
              {enhanced_content.projects.map((proj, i) => (
                <div key={i} style={{ marginBottom: '10px' }}>
                  <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-main)' }}>
                    {proj.title}
                    {proj.technologies?.length > 0 && (
                      <span style={{ fontSize: '12px', color: 'var(--primary)', marginLeft: '8px' }}>
                        [{proj.technologies.join(', ')}]
                      </span>
                    )}
                  </div>
                  <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '2px', lineHeight: 1.5 }}>
                    {proj.description}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* Certifications */}
          {enhanced_content.certifications?.length > 0 && (
            <div>
              <div style={{ fontSize: '13.5px', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', marginBottom: '4px' }}>
                Certifications & Credentials
              </div>
              <p style={{ fontSize: '13px', color: 'var(--text-main)' }}>
                {enhanced_content.certifications.join(' • ')}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
