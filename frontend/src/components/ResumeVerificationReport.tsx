import React, { useState } from 'react';
import {
  GraduationCap,
  Award,
  Trophy,
  Languages,
  Terminal,
  FolderGit2,
  Briefcase,
  FileText,
  UserCheck,
  Users,
  BookOpen,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  FileCheck2,
  AlertCircle,
  Sparkles,
  LucideIcon,
} from 'lucide-react';
import { CandidateVerificationReport, SectionVerificationResult } from '../types';

interface ResumeVerificationReportProps {
  report?: CandidateVerificationReport;
}

interface SectionMeta {
  name: string;
  icon: LucideIcon;
  itemLabelSingular: string;
  itemLabelPlural: string;
}

const SECTION_METADATA: Record<string, SectionMeta> = {
  education: {
    name: 'Education',
    icon: GraduationCap,
    itemLabelSingular: 'Item Extracted',
    itemLabelPlural: 'Items Extracted',
  },
  certifications: {
    name: 'Licenses & Certifications',
    icon: Award,
    itemLabelSingular: 'Certification Extracted',
    itemLabelPlural: 'Certifications Extracted',
  },
  achievements: {
    name: 'Honors & Achievements',
    icon: Trophy,
    itemLabelSingular: 'Achievement Extracted',
    itemLabelPlural: 'Achievements Extracted',
  },
  languages: {
    name: 'Languages Known',
    icon: Languages,
    itemLabelSingular: 'Language Extracted',
    itemLabelPlural: 'Languages Extracted',
  },
  technical_skills: {
    name: 'Technical Skills',
    icon: Terminal,
    itemLabelSingular: 'Skill Extracted',
    itemLabelPlural: 'Skills Extracted',
  },
  projects: {
    name: 'Projects',
    icon: FolderGit2,
    itemLabelSingular: 'Project Extracted',
    itemLabelPlural: 'Projects Extracted',
  },
  experience: {
    name: 'Work Experience & Internships',
    icon: Briefcase,
    itemLabelSingular: 'Role Extracted',
    itemLabelPlural: 'Roles Extracted',
  },
  summary: {
    name: 'Professional Summary',
    icon: FileText,
    itemLabelSingular: 'Summary Extracted',
    itemLabelPlural: 'Summaries Extracted',
  },
  contact_info: {
    name: 'Contact Information',
    icon: UserCheck,
    itemLabelSingular: 'Field Extracted',
    itemLabelPlural: 'Fields Extracted',
  },
  soft_skills: {
    name: 'Soft Skills',
    icon: Users,
    itemLabelSingular: 'Skill Extracted',
    itemLabelPlural: 'Skills Extracted',
  },
  publications: {
    name: 'Publications & Research',
    icon: BookOpen,
    itemLabelSingular: 'Publication Extracted',
    itemLabelPlural: 'Publications Extracted',
  },
};

const ORDERED_SECTION_KEYS = [
  'education',
  'certifications',
  'achievements',
  'languages',
  'technical_skills',
  'projects',
  'experience',
  'summary',
  'contact_info',
  'soft_skills',
  'publications',
];

const getConfidenceColor = (confPct: number): string => {
  if (confPct >= 85) return 'var(--emerald-success)';
  if (confPct >= 70) return 'var(--primary)';
  if (confPct >= 50) return 'var(--amber-warn)';
  return 'var(--rose-danger)';
};

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'extracted':
      return (
        <span className="verification-badge verification-badge-verified">
          <CheckCircle2 size={12} />
          ✓ Verified
        </span>
      );
    case 'partially_extracted':
      return (
        <span className="verification-badge verification-badge-review">
          <AlertTriangle size={12} />
          Review Needed
        </span>
      );
    case 'extraction_failed':
      return (
        <span className="verification-badge verification-badge-failed">
          <XCircle size={12} />
          Failed
        </span>
      );
    case 'genuinely_absent':
    default:
      return (
        <span className="verification-badge verification-badge-absent">
          <HelpCircle size={12} />
          Not in Resume
        </span>
      );
  }
};

interface VerificationCardProps {
  sectionKey: string;
  secResult: SectionVerificationResult;
}

const VerificationCard: React.FC<VerificationCardProps> = ({ sectionKey, secResult }) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(false);

  const meta = SECTION_METADATA[sectionKey] || {
    name: sectionKey.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
    icon: FileText,
    itemLabelSingular: 'Item Extracted',
    itemLabelPlural: 'Items Extracted',
  };

  const IconComponent = meta.icon;
  const confPct = Math.round(secResult.confidence * 100);
  const confColor = getConfidenceColor(confPct);
  const rawSnippet = secResult.sample_snippet?.trim() || '';

  // Render Sample Content Body based on section type
  const renderSampleContent = () => {
    if (secResult.status === 'genuinely_absent' || (!rawSnippet && secResult.item_count === 0)) {
      return (
        <div className="verification-snippet-container" style={{ fontStyle: 'italic', color: 'var(--text-dim)' }}>
          Section genuinely absent from resume.
        </div>
      );
    }

    if (secResult.status === 'extraction_failed' || !rawSnippet) {
      return (
        <div className="verification-snippet-container" style={{ fontStyle: 'italic', color: 'var(--rose-danger)' }}>
          No content could be extracted from this section.
        </div>
      );
    }

    // 1. Education Section: Exact Layout Matching "Degree - Specialization \n Institution"
    if (sectionKey === 'education') {
      const eduEntries = rawSnippet.split(/\s*;\s*/).filter(Boolean);
      const visibleEntries = isExpanded ? eduEntries : eduEntries.slice(0, 1);

      return (
        <div className="verification-snippet-container">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {visibleEntries.map((entry, idx) => {
              // Check if entry contains (Institution)
              const match = entry.match(/^([^(]+)(?:\(([^)]+)\))?$/);
              const degree = match ? match[1].trim() : entry;
              const institution = match && match[2] ? match[2].trim() : null;

              return (
                <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                  <div className="verification-education-primary">{degree}</div>
                  {institution && institution !== 'N/A' && (
                    <div className="verification-education-secondary">{institution}</div>
                  )}
                </div>
              );
            })}
          </div>

          {eduEntries.length > 1 && (
            <button
              type="button"
              className="verification-expand-btn"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? (
                <>
                  <ChevronUp size={13} />
                  <span>Show less</span>
                </>
              ) : (
                <>
                  <ChevronDown size={13} />
                  <span>+{eduEntries.length - 1} more degree{eduEntries.length > 2 ? 's' : ''}</span>
                </>
              )}
            </button>
          )}
        </div>
      );
    }

    // 2. Languages Known: Clean Inline Tags
    if (sectionKey === 'languages') {
      const langs = rawSnippet.split(/,\s*/).map((l) => l.trim()).filter(Boolean);
      return (
        <div className="verification-snippet-container">
          <div className="verification-tags-wrap">
            {langs.map((lang, idx) => (
              <span key={idx} className="verification-tag-pill">
                {lang}
              </span>
            ))}
          </div>
        </div>
      );
    }

    // 3. Technical Skills: Tag Pills with Expand/Collapse
    if (sectionKey === 'technical_skills' || sectionKey === 'soft_skills') {
      const skills = rawSnippet.split(/,\s*/).map((s) => s.trim()).filter(Boolean);
      const visibleSkills = isExpanded ? skills : skills.slice(0, 5);

      return (
        <div className="verification-snippet-container">
          <div className="verification-tags-wrap">
            {visibleSkills.map((sk, idx) => (
              <span key={idx} className="verification-tag-pill">
                {sk}
              </span>
            ))}
          </div>
          {skills.length > 5 && (
            <button
              type="button"
              className="verification-expand-btn"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? (
                <>
                  <ChevronUp size={13} />
                  <span>Show less</span>
                </>
              ) : (
                <>
                  <ChevronDown size={13} />
                  <span>+{skills.length - 5} more skills</span>
                </>
              )}
            </button>
          )}
        </div>
      );
    }

    // 4. Semicolon-Separated Sections (Certifications, Achievements, Projects, Experience)
    if (['certifications', 'achievements', 'projects', 'experience'].includes(sectionKey)) {
      const items = rawSnippet.split(/\s*;\s*/).map((i) => i.trim()).filter(Boolean);
      const visibleItems = isExpanded ? items : items.slice(0, 2);

      return (
        <div className="verification-snippet-container">
          <div className="verification-snippet-list">
            {visibleItems.map((item, idx) => (
              <div key={idx} className="verification-snippet-list-item">
                <span className="verification-snippet-bullet">•</span>
                <span>{item}</span>
              </div>
            ))}
          </div>

          {items.length > 2 && (
            <button
              type="button"
              className="verification-expand-btn"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? (
                <>
                  <ChevronUp size={13} />
                  <span>Show less</span>
                </>
              ) : (
                <>
                  <ChevronDown size={13} />
                  <span>
                    +{items.length - 2} more{' '}
                    {sectionKey === 'certifications'
                      ? 'certifications'
                      : sectionKey === 'achievements'
                      ? 'achievements'
                      : sectionKey === 'projects'
                      ? 'projects'
                      : 'entries'}
                  </span>
                </>
              )}
            </button>
          )}
        </div>
      );
    }

    // 5. Professional Summary / Contact / Default Prose Text
    const isLongText = rawSnippet.length > 100;
    const displayText = isLongText && !isExpanded ? `${rawSnippet.slice(0, 95)}...` : rawSnippet;

    return (
      <div className="verification-snippet-container">
        <div className="verification-snippet-content">
          "{displayText}"
        </div>
        {isLongText && (
          <button
            type="button"
            className="verification-expand-btn"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? (
              <>
                <ChevronUp size={13} />
                <span>Show less</span>
              </>
            ) : (
              <>
                <ChevronDown size={13} />
                <span>Show full summary</span>
              </>
            )}
          </button>
        )}
      </div>
    );
  };

  return (
    <div className="verification-card">
      <div>
        {/* Card Header: Icon + Name + Verified Badge */}
        <div className="verification-card-header">
          <div className="verification-card-title-group">
            <div className="verification-card-icon-wrap">
              <IconComponent size={16} />
            </div>
            <h4 className="verification-card-title" title={meta.name}>
              {meta.name}
            </h4>
          </div>
          {getStatusBadge(secResult.status)}
        </div>

        {/* Card Body: Items Extracted + Confidence Percentage */}
        <div className="verification-card-metrics">
          <span className="verification-metric-items">
            {secResult.item_count}{' '}
            {secResult.item_count === 1 ? meta.itemLabelSingular : meta.itemLabelPlural}
          </span>
          <span className="verification-metric-confidence" style={{ color: confColor }}>
            {confPct}% Confidence
          </span>
        </div>

        {/* Confidence Progress Bar */}
        <div className="verification-card-progress">
          <div
            className="verification-card-progress-bar"
            style={{
              width: `${confPct}%`,
              backgroundColor: confColor,
            }}
          />
        </div>

        {/* Sample Content */}
        {renderSampleContent()}
      </div>

      {/* Validation Warning Strip if applicable */}
      {secResult.validation_warnings && secResult.validation_warnings.length > 0 && (
        <div className="verification-card-warning">
          <AlertCircle size={13} style={{ flexShrink: 0, marginTop: '2px' }} />
          <span>{secResult.validation_warnings[0]}</span>
        </div>
      )}
    </div>
  );
};

export const ResumeVerificationReport: React.FC<ResumeVerificationReportProps> = ({ report }) => {
  const [isReportExpanded, setIsReportExpanded] = useState<boolean>(true);

  if (!report || !report.sections || Object.keys(report.sections).length === 0) {
    return null;
  }

  const { overall_quality_score, is_extraction_reliable, sections, critical_warnings = [] } = report;

  // Order sections according to standard resume sequence
  const presentKeys = Object.keys(sections);
  const orderedKeys = [
    ...ORDERED_SECTION_KEYS.filter((k) => presentKeys.includes(k)),
    ...presentKeys.filter((k) => !ORDERED_SECTION_KEYS.includes(k)),
  ];

  const qualityColor = getConfidenceColor(overall_quality_score);

  return (
    <div className="verification-section-container">
      {/* Top Header Bar */}
      <div
        className="verification-header"
        onClick={() => setIsReportExpanded(!isReportExpanded)}
        role="button"
        tabIndex={0}
        aria-expanded={isReportExpanded}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            setIsReportExpanded(!isReportExpanded);
          }
        }}
      >
        <div className="verification-header-left">
          <div className="verification-header-icon-box">
            <FileCheck2 size={22} />
          </div>
          <div className="verification-header-title-wrap">
            <div className="verification-header-title-row">
              <h3 className="verification-header-title">
                Universal Resume Extraction & Verification Report
              </h3>
              {is_extraction_reliable ? (
                <span className="badge badge-emerald">
                  <ShieldCheck size={12} /> Verified Document
                </span>
              ) : (
                <span className="badge badge-rose">
                  <AlertCircle size={12} /> Discrepancies Flagged
                </span>
              )}
            </div>
            <p className="verification-header-desc">
              Transparent multi-point audit verifying all sections extracted from your uploaded file
            </p>
          </div>
        </div>

        <div className="verification-header-right">
          <div className="verification-quality-score-box">
            <span className="verification-quality-label">Extraction Quality</span>
            <span className="verification-quality-score" style={{ color: qualityColor }}>
              {overall_quality_score}%
            </span>
          </div>
          <button
            type="button"
            className="verification-toggle-btn"
            aria-label={isReportExpanded ? 'Collapse verification report' : 'Expand verification report'}
            onClick={(e) => {
              e.stopPropagation();
              setIsReportExpanded(!isReportExpanded);
            }}
          >
            {isReportExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>
        </div>
      </div>

      {/* Expanded Report Content */}
      {isReportExpanded && (
        <div className="verification-content">
          {/* Critical Warnings Banner */}
          {critical_warnings.length > 0 && (
            <div className="verification-warnings-box">
              <div className="verification-warnings-title">
                <AlertTriangle size={15} />
                <span>Parsing Discrepancy Warnings</span>
              </div>
              <ul className="verification-warnings-list">
                {critical_warnings.map((warn, idx) => (
                  <li key={idx}>{warn}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Cards Grid: 3 cards per row desktop, 2 tablet, 1 mobile */}
          <div className="verification-grid">
            {orderedKeys.map((secKey) => (
              <VerificationCard
                key={secKey}
                sectionKey={secKey}
                secResult={sections[secKey]}
              />
            ))}
          </div>

          {/* Footer Audit Note */}
          <div className="verification-footer-note">
            <Sparkles size={14} color="var(--primary)" />
            <span>
              All sections parsed deterministically by layout analysis and verified against the uploaded file text.
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
