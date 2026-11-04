import React from 'react';
import {
  Shield,
  Briefcase,
  FileText,
  Sparkles,
  ArrowRight,
  Database,
  Layers,
  Award,
  CheckCircle2,
  Clock,
  ChevronRight,
  TrendingUp,
} from 'lucide-react';
import { JobRole } from '../types';
import { NavView } from './Sidebar';

interface DashboardViewProps {
  rolesCount: number;
  selectedRole: JobRole | null;
  historyCount: number;
  latestScore: number | null;
  onNavigate: (view: NavView) => void;
  onSelectRole: (role: JobRole) => void;
  sampleRoles: JobRole[];
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  rolesCount,
  selectedRole,
  historyCount,
  latestScore,
  onNavigate,
  onSelectRole,
  sampleRoles,
}) => {
  const steps = [
    { num: 1, title: 'Select Role', desc: 'Choose from 74 cybersecurity career profiles' },
    { num: 2, title: 'Upload Resume', desc: 'PDF or DOCX document validation & extraction' },
    { num: 3, title: 'ATS Scoring', desc: 'Deterministic 5-category Neon benchmark' },
    { num: 4, title: 'Skill Gaps', desc: 'Prioritized recommendations & future actions' },
    { num: 5, title: 'Round Robin', desc: 'AI resume generation & score re-calculation' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Hero Banner */}
      <div
        className="card"
        style={{
          padding: '36px 40px',
          background: 'linear-gradient(135deg, var(--bg-card) 0%, var(--bg-subtle) 100%)',
          borderLeft: '4px solid var(--primary)',
        }}
      >
        <div style={{ maxWidth: '780px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <span className="badge badge-primary">ENTERPRISE RESUME ENGINE</span>
            <span className="badge badge-emerald">Neon PostgreSQL Powered</span>
          </div>

          <h1 style={{ fontSize: '32px', fontWeight: 800, color: 'var(--text-main)', lineHeight: 1.25 }}>
            Your Cybersecurity Career, Powered by AI
          </h1>

          <p style={{ fontSize: '15px', color: 'var(--text-muted)', marginTop: '8px', lineHeight: 1.6 }}>
            Analyze your resume, identify skill gaps, and improve your alignment with cybersecurity job requirements.
            Benchmark against verified industry criteria with explainable, deterministic ATS scoring.
          </p>

          <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginTop: '24px', flexWrap: 'wrap' }}>
            <button
              id="dashboard-start-analysis-btn"
              className="btn btn-primary"
              onClick={() => onNavigate('analyze')}
              style={{ padding: '11px 22px', fontSize: '14px' }}
            >
              <FileText size={17} />
              <span>Start Resume Analysis</span>
              <ArrowRight size={15} />
            </button>

            <button
              id="dashboard-explore-roles-btn"
              className="btn btn-secondary"
              onClick={() => onNavigate('jobs')}
              style={{ padding: '11px 20px', fontSize: '14px' }}
            >
              <Briefcase size={17} />
              <span>Explore {rolesCount} Cybersecurity Roles</span>
            </button>

            <button
              id="dashboard-track-projects-btn"
              className="btn btn-secondary"
              onClick={() => onNavigate('tracking')}
              style={{ padding: '11px 20px', fontSize: '14px' }}
            >
              <CheckCircle2 size={17} />
              <span>Project Tracker</span>
            </button>
          </div>
        </div>
      </div>

      {/* Real Metric Summary Cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))',
          gap: '16px',
        }}
      >
        {/* Roles Card */}
        <div
          className="card card-interactive"
          onClick={() => onNavigate('jobs')}
          style={{ padding: '20px', cursor: 'pointer' }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase' }}>
              Cybersecurity Roles
            </div>
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--primary-subtle)',
                color: 'var(--primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Briefcase size={16} />
            </div>
          </div>
          <div className="mono" style={{ fontSize: '30px', fontWeight: 800, color: 'var(--text-main)', marginTop: '6px' }}>
            {rolesCount}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--primary)', marginTop: '4px', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span>Verified in Neon DB</span>
            <ChevronRight size={13} />
          </div>
        </div>

        {/* ATS Categories */}
        <div className="card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase' }}>
              Scoring Categories
            </div>
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--emerald-subtle)',
                color: 'var(--emerald-success)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Award size={16} />
            </div>
          </div>
          <div className="mono" style={{ fontSize: '30px', fontWeight: 800, color: 'var(--text-main)', marginTop: '6px' }}>
            5
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-dim)', marginTop: '4px' }}>
            Deterministic weights (100% total)
          </div>
        </div>

        {/* Round Robin Templates */}
        <div
          className="card card-interactive"
          onClick={() => onNavigate('templates')}
          style={{ padding: '20px', cursor: 'pointer' }}
          title="Explore the Resume Template Gallery"
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase' }}>
              Round Robin Templates
            </div>
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--amber-subtle)',
                color: 'var(--amber-warn)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Layers size={16} />
            </div>
          </div>
          <div className="mono" style={{ fontSize: '30px', fontWeight: 800, color: 'var(--text-main)', marginTop: '6px' }}>
            30
          </div>
          <div style={{ fontSize: '12px', color: 'var(--primary)', marginTop: '4px', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span>Explore Template Gallery (T01 &rarr; T30)</span>
            <ChevronRight size={13} />
          </div>
        </div>

        {/* Session Analyses */}
        <div
          className="card card-interactive"
          onClick={() => onNavigate('history')}
          style={{ padding: '20px', cursor: 'pointer' }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase' }}>
              Session Analyses
            </div>
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--primary-subtle)',
                color: 'var(--primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <TrendingUp size={16} />
            </div>
          </div>
          <div className="mono" style={{ fontSize: '30px', fontWeight: 800, color: 'var(--text-main)', marginTop: '6px' }}>
            {historyCount}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--primary)', marginTop: '4px', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span>{latestScore !== null ? `Latest: ${latestScore}/100` : 'View session history'}</span>
            <ChevronRight size={13} />
          </div>
        </div>

        {/* Project Tracking Card */}
        <div
          className="card card-interactive"
          onClick={() => onNavigate('tracking')}
          style={{ padding: '20px', cursor: 'pointer' }}
          title="Track practical project completion"
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase' }}>
              Project Tracker
            </div>
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--emerald-subtle)',
                color: 'var(--emerald-success)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <CheckCircle2 size={16} />
            </div>
          </div>
          <div className="mono" style={{ fontSize: '30px', fontWeight: 800, color: 'var(--text-main)', marginTop: '6px' }}>
            Milestones
          </div>
          <div style={{ fontSize: '12px', color: 'var(--primary)', marginTop: '4px', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span>Practical verification</span>
            <ChevronRight size={13} />
          </div>
        </div>
      </div>

      {/* Workflow Progress Diagram */}
      <div className="card" style={{ padding: '24px 28px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '18px' }}>
          FUTRSEC 5-Step Evaluation & Enhancement Pipeline
        </h3>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '12px',
          }}
        >
          {steps.map((st) => (
            <div
              key={st.num}
              style={{
                padding: '14px',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--bg-subtle)',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <div
                style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  background: 'var(--primary)',
                  color: '#FFFFFF',
                  fontSize: '12px',
                  fontWeight: 700,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '10px',
                }}
              >
                {st.num}
              </div>
              <div style={{ fontSize: '13.5px', fontWeight: 600, color: 'var(--text-main)' }}>{st.title}</div>
              <div style={{ fontSize: '12px', color: 'var(--text-dim)', marginTop: '2px' }}>{st.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Featured Career Paths */}
      <div className="card" style={{ padding: '24px 28px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-main)' }}>
              Popular Cybersecurity Job Profiles
            </h3>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
              Select a target role or explore all {rolesCount} career paths in the Jobs catalog.
            </p>
          </div>
          <button
            className="btn btn-secondary"
            onClick={() => onNavigate('jobs')}
            style={{ fontSize: '13px' }}
          >
            <span>View All {rolesCount} Roles</span>
            <ChevronRight size={14} />
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '12px' }}>
          {sampleRoles.slice(0, 6).map((role) => {
            const isSelected = selectedRole?.role_id === role.role_id;
            return (
              <div
                key={role.role_id}
                onClick={() => {
                  onSelectRole(role);
                  onNavigate('analyze');
                }}
                className="card card-interactive"
                style={{
                  padding: '16px',
                  cursor: 'pointer',
                  border: isSelected ? '2px solid var(--primary)' : '1px solid var(--border-subtle)',
                  background: isSelected ? 'var(--primary-subtle)' : 'var(--bg-card)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span className="badge badge-subtle" style={{ fontSize: '11px' }}>
                    Role ID: {role.role_id}
                  </span>
                  {isSelected && (
                    <span className="badge badge-emerald" style={{ fontSize: '10px' }}>
                      Selected
                    </span>
                  )}
                </div>
                <div style={{ fontSize: '14.5px', fontWeight: 600, color: 'var(--text-main)' }}>
                  {role.role_name}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--primary)', marginTop: '8px', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <span>Target This Role</span>
                  <ArrowRight size={13} />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
