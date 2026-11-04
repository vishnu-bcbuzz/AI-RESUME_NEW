import React, { useState, useEffect, useMemo } from 'react';
import {
  Layers,
  Eye,
  ArrowLeft,
  Download,
  FileText,
  X,
  Search,
  Filter,
  CheckCircle2,
  Award,
  Sparkles,
  ExternalLink,
  Shield,
  Briefcase,
  GraduationCap,
  FolderGit2,
  AlignLeft,
  AlignCenter,
  FileCode,
} from 'lucide-react';
import { ResumeTemplate } from '../types';
import { fetchTemplates, fetchTemplatePreview } from '../api';

interface TemplateGalleryViewProps {
  onBackToDashboard?: () => void;
}

export const TemplateGalleryView: React.FC<TemplateGalleryViewProps> = ({
  onBackToDashboard,
}) => {
  const [templates, setTemplates] = useState<ResumeTemplate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Search & Filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAlignment, setSelectedAlignment] = useState<'all' | 'left' | 'center'>('all');
  const [selectedFont, setSelectedFont] = useState<string>('all');

  // Preview Modal state
  const [activePreviewTemplate, setActivePreviewTemplate] = useState<ResumeTemplate | null>(null);
  const [previewData, setPreviewData] = useState<any | null>(null);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [previewMode, setPreviewMode] = useState<'sheet' | 'pdf'>('sheet');

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await fetchTemplates();
      setTemplates(data || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load resume templates');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenPreview = async (template: ResumeTemplate) => {
    setActivePreviewTemplate(template);
    setPreviewMode('sheet');
    try {
      setIsPreviewLoading(true);
      setPreviewError(null);
      const data = await fetchTemplatePreview(template.template_id);
      setPreviewData(data);
    } catch (err: any) {
      setPreviewError(err.message || `Failed to generate preview for ${template.template_id}`);
    } finally {
      setIsPreviewLoading(false);
    }
  };

  const handleClosePreview = () => {
    setActivePreviewTemplate(null);
    setPreviewData(null);
    setPreviewError(null);
  };

  // Filter templates
  const filteredTemplates = useMemo(() => {
    return templates.filter((t) => {
      const q = searchQuery.toLowerCase().trim();
      const matchSearch =
        !q ||
        t.template_id.toLowerCase().includes(q) ||
        t.template_name.toLowerCase().includes(q) ||
        t.description.toLowerCase().includes(q) ||
        (t.role_category_tags || []).some((tag) => tag.toLowerCase().includes(q));

      const align = t.style_config?.header_alignment || 'left';
      const matchAlign =
        selectedAlignment === 'all' ||
        (selectedAlignment === 'left' && align === 'left') ||
        (selectedAlignment === 'center' && align === 'center');

      const font = t.style_config?.font_family || 'Calibri';
      const matchFont = selectedFont === 'all' || font.toLowerCase() === selectedFont.toLowerCase();

      return matchSearch && matchAlign && matchFont;
    });
  }, [templates, searchQuery, selectedAlignment, selectedFont]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header Banner */}
      <div
        className="card"
        style={{
          padding: '28px 32px',
          background: 'linear-gradient(135deg, var(--bg-card) 0%, var(--bg-subtle) 100%)',
          borderLeft: '4px solid var(--primary)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span className="badge badge-primary">
                <Layers size={13} />
                <span>TEMPLATE REGISTRY</span>
              </span>
              <span className="badge badge-emerald">{templates.length || 30} Verified ATS Templates</span>
              <span className="badge badge-subtle">Strictly Black & White ATS Layouts</span>
            </div>
            <h1 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-main)', margin: '0 0 6px 0' }}>
              Resume Template Gallery
            </h1>
            <p style={{ fontSize: '13.5px', color: 'var(--text-muted)', margin: 0, maxWidth: '720px', lineHeight: 1.5 }}>
              Explore all 30 production resume templates registered in the FUTRSEC engine (T01 &rarr; T30). Each template enforces clean single-column hierarchy, calibrated font pairings, and verified ATS readability. Previews use the actual DOCX and PyMuPDF rendering pipelines with sample cybersecurity candidate data.
            </p>
          </div>

          <div
            style={{
              padding: '12px 18px',
              background: 'var(--bg-card)',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
              display: 'flex',
              flexDirection: 'column',
              gap: '4px',
              fontSize: '12px',
            }}
          >
            <div style={{ fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Sparkles size={14} color="var(--primary)" />
              <span>Round Robin System</span>
            </div>
            <div style={{ color: 'var(--text-dim)', maxWidth: '240px' }}>
              Candidate resumes are automatically scheduled across these templates. Previewing here is read-only and never advances the queue.
            </div>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div
        className="card"
        style={{
          padding: '18px 24px',
          display: 'flex',
          flexWrap: 'wrap',
          gap: '16px',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        {/* Search */}
        <div style={{ position: 'relative', minWidth: '260px', flex: 1 }}>
          <Search size={15} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-dim)' }} />
          <input
            type="text"
            className="input-field"
            placeholder="Search templates by ID (e.g. T01), name, or keyword..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ paddingLeft: '36px', fontSize: '13px' }}
          />
        </div>

        {/* Alignment Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-dim)', fontWeight: 600 }}>Header:</span>
          <button
            type="button"
            className={`btn ${selectedAlignment === 'all' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setSelectedAlignment('all')}
            style={{ fontSize: '11.5px', padding: '5px 10px' }}
          >
            All
          </button>
          <button
            type="button"
            className={`btn ${selectedAlignment === 'left' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setSelectedAlignment('left')}
            style={{ fontSize: '11.5px', padding: '5px 10px', display: 'flex', alignItems: 'center', gap: '4px' }}
          >
            <AlignLeft size={13} />
            <span>Left-Aligned</span>
          </button>
          <button
            type="button"
            className={`btn ${selectedAlignment === 'center' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setSelectedAlignment('center')}
            style={{ fontSize: '11.5px', padding: '5px 10px', display: 'flex', alignItems: 'center', gap: '4px' }}
          >
            <AlignCenter size={13} />
            <span>Centered</span>
          </button>
        </div>

        {/* Font Family Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-dim)', fontWeight: 600 }}>Font:</span>
          {['all', 'Calibri', 'Arial', 'Times New Roman', 'Aptos'].map((font) => (
            <button
              key={font}
              type="button"
              className={`btn ${selectedFont === font ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setSelectedFont(font)}
              style={{ fontSize: '11.5px', padding: '5px 9px' }}
            >
              {font === 'all' ? 'All' : font}
            </button>
          ))}
        </div>
      </div>

      {/* Templates Count Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0 4px' }}>
        <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-main)' }}>
          Showing {filteredTemplates.length} of {templates.length} ATS Templates
        </div>
        <div style={{ fontSize: '12px', color: 'var(--text-dim)' }}>
          Click <strong>Preview Template</strong> on any card to inspect full layout with sample candidate information.
        </div>
      </div>

      {/* Templates Cards Grid */}
      {isLoading ? (
        <div className="card" style={{ padding: '60px', textAlign: 'center' }}>
          <div className="spin" style={{ width: '28px', height: '28px', border: '3px solid var(--primary)', borderTopColor: 'transparent', borderRadius: '50%', margin: '0 auto 16px' }} />
          <div style={{ fontSize: '14px', color: 'var(--text-muted)' }}>Loading template registry...</div>
        </div>
      ) : error ? (
        <div className="card" style={{ padding: '40px', textAlign: 'center', borderColor: 'var(--amber-border)' }}>
          <div style={{ color: 'var(--amber-warn)', marginBottom: '8px', fontWeight: 700 }}>{error}</div>
          <button className="btn btn-secondary" onClick={loadTemplates}>Retry</button>
        </div>
      ) : filteredTemplates.length === 0 ? (
        <div className="card" style={{ padding: '60px', textAlign: 'center' }}>
          <p style={{ color: 'var(--text-muted)', fontSize: '14px', margin: '0 0 12px 0' }}>
            No templates match the current search or filter criteria.
          </p>
          <button
            className="btn btn-secondary"
            onClick={() => {
              setSearchQuery('');
              setSelectedAlignment('all');
              setSelectedFont('all');
            }}
          >
            Clear Filters
          </button>
        </div>
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
            gap: '20px',
          }}
        >
          {filteredTemplates.map((template) => {
            const font = template.style_config?.font_family || 'Calibri';
            const align = template.style_config?.header_alignment || 'left';
            const divider = template.style_config?.divider_style || 'solid';
            const order: string[] = template.style_config?.section_order || [];

            return (
              <div
                key={template.template_id}
                className="card card-interactive"
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  padding: '20px',
                  background: 'var(--bg-card)',
                  borderColor: 'var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  transition: 'transform var(--transition-fast), box-shadow var(--transition-fast)',
                }}
              >
                {/* Card Top: Template ID & Badges */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span
                      style={{
                        background: 'var(--primary)',
                        color: '#FFFFFF',
                        fontWeight: 800,
                        fontSize: '11px',
                        padding: '3px 8px',
                        borderRadius: '4px',
                        letterSpacing: '0.5px',
                      }}
                    >
                      {template.template_id}
                    </span>
                    <span className="badge badge-subtle" style={{ fontSize: '10.5px' }}>
                      {font}
                    </span>
                  </div>

                  <span
                    className="badge badge-subtle"
                    style={{
                      fontSize: '10.5px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                    }}
                  >
                    {align === 'center' ? <AlignCenter size={11} /> : <AlignLeft size={11} />}
                    <span>{align === 'center' ? 'Centered' : 'Left-Aligned'}</span>
                  </span>
                </div>

                {/* Template Name & Description */}
                <h3
                  style={{
                    fontSize: '16px',
                    fontWeight: 800,
                    color: 'var(--text-main)',
                    margin: '0 0 6px 0',
                  }}
                >
                  {template.template_name}
                </h3>
                <p
                  style={{
                    fontSize: '12.5px',
                    color: 'var(--text-muted)',
                    margin: '0 0 14px 0',
                    lineHeight: 1.45,
                    flex: 1,
                  }}
                >
                  {template.description}
                </p>

                {/* Miniature Layout Preview Wireframe */}
                <div
                  style={{
                    padding: '12px',
                    background: '#FFFFFF',
                    borderRadius: '4px',
                    border: '1px solid #E2E8F0',
                    marginBottom: '14px',
                    boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.03)',
                  }}
                  title={`Visual miniature of ${template.template_name} layout`}
                >
                  {/* Miniature Header */}
                  <div
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: align === 'center' ? 'center' : 'flex-start',
                      marginBottom: '8px',
                      paddingBottom: '6px',
                      borderBottom: divider === 'none' ? 'none' : '1px solid #CBD5E1',
                    }}
                  >
                    <div style={{ width: '45%', height: '7px', background: '#0F172A', borderRadius: '2px', marginBottom: '4px' }} />
                    <div style={{ width: '70%', height: '4px', background: '#94A3B8', borderRadius: '2px' }} />
                  </div>

                  {/* Miniature Section Slices */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                    {order.slice(0, 4).map((sec, sIdx) => (
                      <div key={sIdx} style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                          <span style={{ fontSize: '9px', fontWeight: 700, color: '#2563EB', textTransform: 'uppercase' }}>
                            {sec}
                          </span>
                          <span style={{ fontSize: '8px', color: '#94A3B8' }}>•</span>
                        </div>
                        <div style={{ width: '100%', height: '3px', background: '#E2E8F0', borderRadius: '1px' }} />
                        <div style={{ width: sIdx % 2 === 0 ? '85%' : '70%', height: '3px', background: '#F1F5F9', borderRadius: '1px' }} />
                      </div>
                    ))}
                  </div>
                </div>

                {/* Section Order Tags */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginBottom: '14px' }}>
                  {order.map((sec, idx) => (
                    <span
                      key={idx}
                      style={{
                        fontSize: '10px',
                        padding: '2px 6px',
                        background: 'var(--bg-subtle)',
                        borderRadius: '3px',
                        color: 'var(--text-dim)',
                        border: '1px solid var(--border-subtle)',
                      }}
                    >
                      {idx + 1}. {sec}
                    </span>
                  ))}
                </div>

                {/* Card Action: Preview Button */}
                <button
                  type="button"
                  id={`preview-btn-${template.template_id}`}
                  className="btn btn-primary"
                  onClick={() => handleOpenPreview(template)}
                  style={{
                    width: '100%',
                    padding: '8px 14px',
                    fontSize: '12.5px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '6px',
                    fontWeight: 700,
                  }}
                >
                  <Eye size={14} />
                  <span>Preview Template</span>
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* =========================================================================
          FULL TEMPLATE PREVIEW MODAL / DEDICATED INSPECTION SCREEN
          ========================================================================= */}
      {activePreviewTemplate && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(15, 23, 42, 0.82)',
            backdropFilter: 'blur(4px)',
            zIndex: 1100,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
            animation: 'fadeIn 0.15s ease-out',
          }}
          onClick={handleClosePreview}
        >
          <div
            className="card"
            style={{
              maxWidth: '1000px',
              width: '100%',
              maxHeight: '94vh',
              display: 'flex',
              flexDirection: 'column',
              background: '#FFFFFF',
              borderRadius: '12px',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.4)',
              overflow: 'hidden',
              border: '1px solid #CBD5E1',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Top Bar */}
            <div
              style={{
                padding: '16px 24px',
                borderBottom: '1px solid #E2E8F0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '16px',
                background: '#F8FAFC',
                flexWrap: 'wrap',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleClosePreview}
                  style={{
                    fontSize: '12.5px',
                    padding: '6px 14px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    background: '#FFFFFF',
                    borderColor: '#CBD5E1',
                    color: '#334155',
                  }}
                  title="Return to Template Gallery"
                >
                  <ArrowLeft size={14} />
                  <span>Back to Gallery</span>
                </button>

                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span
                      style={{
                        background: '#2563EB',
                        color: '#FFFFFF',
                        padding: '2px 7px',
                        borderRadius: '4px',
                        fontSize: '11px',
                        fontWeight: 800,
                      }}
                    >
                      {activePreviewTemplate.template_id}
                    </span>
                    <h2 style={{ fontSize: '17px', fontWeight: 800, color: '#0F172A', margin: 0 }}>
                      {activePreviewTemplate.template_name}
                    </h2>
                    <span
                      style={{
                        background: '#EFF6FF',
                        color: '#2563EB',
                        padding: '2px 8px',
                        borderRadius: '4px',
                        fontSize: '11px',
                        fontWeight: 600,
                      }}
                    >
                      Font: {activePreviewTemplate.style_config?.font_family || 'Calibri'}
                    </span>
                  </div>
                  <div style={{ fontSize: '12px', color: '#64748B', marginTop: '2px' }}>
                    {activePreviewTemplate.description}
                  </div>
                </div>
              </div>

              {/* View / Download Actions */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {/* View Mode Switcher */}
                <div style={{ display: 'flex', background: '#E2E8F0', padding: '2px', borderRadius: '6px' }}>
                  <button
                    type="button"
                    onClick={() => setPreviewMode('sheet')}
                    style={{
                      padding: '4px 10px',
                      fontSize: '11.5px',
                      fontWeight: 700,
                      border: 'none',
                      borderRadius: '4px',
                      background: previewMode === 'sheet' ? '#FFFFFF' : 'transparent',
                      color: previewMode === 'sheet' ? '#0F172A' : '#64748B',
                      cursor: 'pointer',
                    }}
                  >
                    Structured Layout
                  </button>
                  <button
                    type="button"
                    onClick={() => setPreviewMode('pdf')}
                    style={{
                      padding: '4px 10px',
                      fontSize: '11.5px',
                      fontWeight: 700,
                      border: 'none',
                      borderRadius: '4px',
                      background: previewMode === 'pdf' ? '#FFFFFF' : 'transparent',
                      color: previewMode === 'pdf' ? '#0F172A' : '#64748B',
                      cursor: 'pointer',
                    }}
                  >
                    Rendered PDF
                  </button>
                </div>

                <a
                  href={`/api/templates/${activePreviewTemplate.template_id}/preview/docx`}
                  download
                  className="btn btn-secondary"
                  style={{
                    fontSize: '12px',
                    padding: '6px 12px',
                    textDecoration: 'none',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '5px',
                    background: '#FFFFFF',
                  }}
                  title="Download actual DOCX generated with this template"
                >
                  <Download size={13} />
                  <span>Download DOCX</span>
                </a>

                <a
                  href={`/api/templates/${activePreviewTemplate.template_id}/preview/pdf`}
                  download
                  className="btn btn-secondary"
                  style={{
                    fontSize: '12px',
                    padding: '6px 12px',
                    textDecoration: 'none',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '5px',
                    background: '#FFFFFF',
                  }}
                  title="Download actual PDF generated with this template"
                >
                  <Download size={13} />
                  <span>Download PDF</span>
                </a>

                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleClosePreview}
                  style={{
                    padding: '6px',
                    borderRadius: '50%',
                    border: '1px solid #CBD5E1',
                    background: '#FFFFFF',
                    color: '#64748B',
                    cursor: 'pointer',
                  }}
                  title="Close preview"
                >
                  <X size={16} />
                </button>
              </div>
            </div>

            {/* Sub-Header Notice */}
            <div
              style={{
                padding: '8px 24px',
                background: '#F0FDF4',
                borderBottom: '1px solid #DCFCE7',
                fontSize: '12px',
                color: '#15803D',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <span>
                ✓ <strong>Authentic Document Pipeline:</strong> Previews the real output of <code>{activePreviewTemplate.template_name}</code> using sample candidate information. Round Robin scheduling and live candidate records remain completely unaffected.
              </span>
              <span style={{ fontSize: '11px', color: '#16A34A', fontWeight: 600 }}>
                ATS Single-Column Format
              </span>
            </div>

            {/* Modal Body */}
            <div
              style={{
                flex: 1,
                overflowY: 'auto',
                padding: previewMode === 'pdf' ? '0' : '28px 20px',
                background: previewMode === 'pdf' ? '#525659' : '#F1F5F9',
                display: 'flex',
                justifyContent: 'center',
              }}
            >
              {isPreviewLoading ? (
                <div style={{ padding: '60px', textAlign: 'center' }}>
                  <div className="spin" style={{ width: '28px', height: '28px', border: '3px solid #2563EB', borderTopColor: 'transparent', borderRadius: '50%', margin: '0 auto 16px' }} />
                  <div style={{ fontSize: '14px', color: '#64748B' }}>Rendering template preview via official document engine...</div>
                </div>
              ) : previewError ? (
                <div style={{ padding: '40px', textAlign: 'center', color: '#DC2626' }}>
                  <strong>{previewError}</strong>
                </div>
              ) : previewMode === 'pdf' ? (
                /* PDF Embed View */
                <iframe
                  src={`/api/templates/${activePreviewTemplate.template_id}/preview/pdf`}
                  title={`Rendered PDF preview for ${activePreviewTemplate.template_name}`}
                  style={{
                    width: '100%',
                    height: '100%',
                    minHeight: '680px',
                    border: 'none',
                  }}
                />
              ) : (
                /* Structured ATS Layout Sheet */
                previewData && (
                  <div
                    style={{
                      background: '#FFFFFF',
                      maxWidth: '850px',
                      width: '100%',
                      padding: `${(activePreviewTemplate.style_config?.margins_in || 0.75) * 60}px ${(activePreviewTemplate.style_config?.margins_in || 0.75) * 64}px`,
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                      fontFamily: activePreviewTemplate.style_config?.font_family || 'Calibri, sans-serif',
                      color: '#000000',
                      lineHeight: 1.45,
                      border: '1px solid #E2E8F0',
                    }}
                  >
                    {/* 1. Header and Contact Details */}
                    <div
                      style={{
                        textAlign: activePreviewTemplate.style_config?.header_alignment === 'center' ? 'center' : 'left',
                        marginBottom: '16px',
                        borderBottom:
                          activePreviewTemplate.style_config?.divider_style === 'solid'
                            ? '1.5px solid #000000'
                            : activePreviewTemplate.style_config?.divider_style === 'double'
                            ? '3px double #000000'
                            : 'none',
                        paddingBottom: '10px',
                      }}
                    >
                      <h1
                        style={{
                          fontSize: `${activePreviewTemplate.style_config?.title_font_size_pt || 22}pt`,
                          fontWeight: 800,
                          margin: 0,
                          color: '#000000',
                          textTransform: 'uppercase',
                          letterSpacing: '0.03em',
                        }}
                      >
                        {previewData.sample_content.candidate_name}
                      </h1>

                      {previewData.sample_content.professional_headline && (
                        <div
                          style={{
                            fontSize: '11pt',
                            fontWeight: 700,
                            color: '#334155',
                            marginTop: '3px',
                          }}
                        >
                          {previewData.sample_content.professional_headline}
                        </div>
                      )}

                      {/* Contact items with blue clickable links */}
                      <div
                        style={{
                          fontSize: `${activePreviewTemplate.style_config?.contact_font_size_pt || 9.5}pt`,
                          color: '#000000',
                          marginTop: '5px',
                        }}
                      >
                        <a href={`mailto:${previewData.sample_content.contact_details.email}`} style={{ color: '#0044CC', textDecoration: 'none' }}>
                          {previewData.sample_content.contact_details.email}
                        </a>
                        {' | '}
                        <span>{previewData.sample_content.contact_details.phone}</span>
                        {' | '}
                        <span>{previewData.sample_content.contact_details.location}</span>
                        {' | '}
                        <a href={previewData.sample_content.contact_details.linkedin} target="_blank" rel="noopener noreferrer" style={{ color: '#0044CC', textDecoration: 'none' }}>
                          linkedin.com/in/jordanhayes-sec
                        </a>
                        {' | '}
                        <a href={previewData.sample_content.contact_details.github} target="_blank" rel="noopener noreferrer" style={{ color: '#0044CC', textDecoration: 'none' }}>
                          github.com/jordanhayes
                        </a>
                      </div>
                    </div>

                    {/* Dynamically Render Sections According to Template's Configured Section Order */}
                    {(activePreviewTemplate.style_config?.section_order || [
                      'summary',
                      'skills',
                      'projects',
                      'experience',
                      'education',
                      'certifications',
                    ]).map((sectionKey: string, sIndex: number) => {
                      const sectionTitles = activePreviewTemplate.style_config?.section_titles || {};

                      // Section Title Element Generator
                      const renderSectionHeader = (title: string) => {
                        const isCenter = activePreviewTemplate.style_config?.header_alignment === 'center';
                        return (
                          <div
                            style={{
                              fontSize: `${activePreviewTemplate.style_config?.heading_font_size_pt || 12.5}pt`,
                              fontWeight: 800,
                              color: '#000000',
                              textTransform: 'uppercase',
                              letterSpacing: '0.04em',
                              textAlign: isCenter ? 'center' : 'left',
                              borderBottom: '1px solid #000000',
                              paddingBottom: '2px',
                              marginBottom: '8px',
                              marginTop: sIndex > 0 ? `${activePreviewTemplate.style_config?.section_spacing_before_pt || 8}pt` : '0',
                            }}
                          >
                            {title}
                          </div>
                        );
                      };

                      // SECTION A: Professional Summary
                      if (sectionKey === 'summary' && previewData.sample_content.professional_summary) {
                        return (
                          <div key="sec-summary" style={{ marginBottom: '14px' }}>
                            {renderSectionHeader(sectionTitles.summary || 'Professional Summary')}
                            <p style={{ margin: 0, fontSize: `${activePreviewTemplate.style_config?.body_font_size_pt || 10}pt`, lineHeight: 1.5, textAlign: 'justify' }}>
                              {previewData.sample_content.professional_summary}
                            </p>
                          </div>
                        );
                      }

                      // SECTION B: Technical Skills (Compact Inline Category + Comma-separated Skills)
                      if (sectionKey === 'skills' && previewData.sample_content.technical_skills_grouped) {
                        const skillsGrouped = previewData.sample_content.technical_skills_grouped;
                        const bodyPt = activePreviewTemplate.style_config?.body_font_size_pt || 10;
                        const fontSizePt = Math.min(Math.max(bodyPt, 10), 10.5);
                        return (
                          <div key="sec-skills" style={{ marginBottom: '12px' }}>
                            {renderSectionHeader(sectionTitles.skills || 'Technical Skills')}
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '3px', fontSize: `${fontSizePt}pt`, lineHeight: 1.25 }}>
                              {Object.entries(skillsGrouped).map(([category, items]: [string, any]) => {
                                const skillList = Array.isArray(items) ? items : [];
                                if (skillList.length === 0) return null;
                                return (
                                  <div key={category} style={{ textAlign: 'left', color: '#000000' }}>
                                    <strong style={{ fontWeight: 700, color: '#000000' }}>{category}: </strong>
                                    <span>{skillList.join(', ')}</span>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        );
                      }

                      // SECTION C: Projects
                      if (sectionKey === 'projects' && previewData.sample_content.projects) {
                        return (
                          <div key="sec-projects" style={{ marginBottom: '14px' }}>
                            {renderSectionHeader(sectionTitles.projects || 'Projects')}
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                              {previewData.sample_content.projects.map((proj: any, pIdx: number) => {
                                const status = proj.status || (proj.title?.toLowerCase().includes('in progress') ? 'In Progress' : 'Completed');
                                const projUrl = proj.github_url || proj.project_url;
                                const bullets = proj.bullets && proj.bullets.length > 0
                                  ? proj.bullets
                                  : (proj.description ? proj.description.split('\n').filter(Boolean) : []);
                                return (
                                  <div key={pIdx} style={{ textAlign: 'left' }}>
                                    <div>
                                      <strong style={{ fontSize: `${(activePreviewTemplate.style_config?.body_font_size_pt || 10) + 0.5}pt`, color: '#000000' }}>
                                        {proj.title} <span style={{ fontWeight: 'normal', fontStyle: 'italic', fontSize: '9pt' }}>| Status: {status}</span>
                                      </strong>
                                    </div>
                                    {proj.technologies && proj.technologies.length > 0 && (
                                      <div style={{ margin: '2px 0 0', fontSize: `${activePreviewTemplate.style_config?.body_font_size_pt || 10}pt`, color: '#000000' }}>
                                        <strong>Technologies: </strong>
                                        <span>{proj.technologies.join(', ')}</span>
                                      </div>
                                    )}
                                    {projUrl && (
                                      <div style={{ margin: '1px 0 0', fontSize: '9pt', color: '#000000' }}>
                                        <strong>Project URL: </strong>
                                        <a href={projUrl.startsWith('http') ? projUrl : `https://${projUrl}`} target="_blank" rel="noreferrer" style={{ color: '#2563eb', textDecoration: 'underline' }}>
                                          {projUrl}
                                        </a>
                                      </div>
                                    )}
                                    {bullets && bullets.length > 0 && (
                                      <ul style={{ margin: '4px 0 0', paddingLeft: '18px', fontSize: `${activePreviewTemplate.style_config?.body_font_size_pt || 10}pt`, color: '#000000', lineHeight: 1.45 }}>
                                        {bullets.slice(0, 4).map((b: string, bIdx: number) => (
                                          <li key={bIdx} style={{ marginBottom: '2px' }}>{b}</li>
                                        ))}
                                      </ul>
                                    )}
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        );
                      }

                      // SECTION D: Work Experience
                      if (sectionKey === 'experience' && previewData.sample_content.experience) {
                        return (
                          <div key="sec-experience" style={{ marginBottom: '14px' }}>
                            {renderSectionHeader(sectionTitles.experience || 'Professional Experience')}
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                              {previewData.sample_content.experience.map((exp: any, eIdx: number) => (
                                <div key={eIdx}>
                                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                                    <strong style={{ fontSize: `${(activePreviewTemplate.style_config?.body_font_size_pt || 10) + 0.5}pt`, color: '#000000' }}>
                                      {exp.job_title} | {exp.company}
                                    </strong>
                                    <span style={{ fontSize: '9pt', color: '#000000' }}>
                                      {exp.start_date} – {exp.end_date}
                                    </span>
                                  </div>
                                  <ul style={{ margin: '3px 0 0 16px', padding: 0, fontSize: `${activePreviewTemplate.style_config?.body_font_size_pt || 10}pt` }}>
                                    {exp.responsibilities?.map((resp: string, rIdx: number) => (
                                      <li key={rIdx} style={{ marginBottom: '2px', lineHeight: 1.4 }}>
                                        {resp}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      }

                      // SECTION E: Education
                      if (sectionKey === 'education' && previewData.sample_content.education) {
                        return (
                          <div key="sec-education" style={{ marginBottom: '14px' }}>
                            {renderSectionHeader(sectionTitles.education || 'Education & Academic Credentials')}
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                              {previewData.sample_content.education.map((edu: any, edIdx: number) => (
                                <div key={edIdx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', fontSize: `${activePreviewTemplate.style_config?.body_font_size_pt || 10}pt` }}>
                                  <div>
                                    <strong style={{ color: '#000000' }}>{edu.degree}</strong>
                                    {edu.field_of_study && <span> in {edu.field_of_study}</span>}
                                    <span> — {edu.institution}</span>
                                  </div>
                                  <span style={{ fontSize: '9pt', color: '#000000' }}>
                                    {edu.graduation_year}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      }

                      // SECTION F: Certifications
                      if (sectionKey === 'certifications' && previewData.sample_content.certifications) {
                        return (
                          <div key="sec-certifications" style={{ marginBottom: '14px' }}>
                            {renderSectionHeader(sectionTitles.certifications || 'Certifications & Industry Credentials')}
                            <div style={{ fontSize: `${activePreviewTemplate.style_config?.body_font_size_pt || 10}pt`, lineHeight: 1.5 }}>
                              {previewData.sample_content.certifications.join('  •  ')}
                            </div>
                          </div>
                        );
                      }

                      // SECTION G: Achievements
                      if (sectionKey === 'achievements' && previewData.sample_content.achievements) {
                        return (
                          <div key="sec-achievements" style={{ marginBottom: '14px' }}>
                            {renderSectionHeader(sectionTitles.achievements || 'Honors & Key Achievements')}
                            <ul style={{ margin: '3px 0 0 16px', padding: 0, fontSize: `${activePreviewTemplate.style_config?.body_font_size_pt || 10}pt` }}>
                              {previewData.sample_content.achievements.map((ach: string, aIdx: number) => (
                                <li key={aIdx} style={{ marginBottom: '2px' }}>{ach}</li>
                              ))}
                            </ul>
                          </div>
                        );
                      }

                      return null;
                    })}
                  </div>
                )
              )}
            </div>

            {/* Modal Bottom Bar */}
            <div
              style={{
                padding: '12px 24px',
                borderTop: '1px solid #E2E8F0',
                background: '#F8FAFC',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#64748B' }}>
                <CheckCircle2 size={14} color="#16A34A" />
                <span>DOCX and Multi-Page PDF render from identical template specifications.</span>
              </div>

              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleClosePreview}
                style={{ fontSize: '12.5px', padding: '6px 16px' }}
              >
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

