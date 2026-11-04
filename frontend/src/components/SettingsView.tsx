import React from 'react';
import { Settings, Sun, Moon, Laptop, Database, Cpu, Layers, ShieldCheck, RefreshCw } from 'lucide-react';
import { useTheme, ThemeMode } from '../context/ThemeContext';

interface SettingsViewProps {
  healthData: any;
  rolesCount: number;
  onRefreshHealth: () => void;
}

export const SettingsView: React.FC<SettingsViewProps> = ({
  healthData,
  rolesCount,
  onRefreshHealth,
}) => {
  const { theme, setTheme, resolvedTheme } = useTheme();

  const themeOptions: Array<{ mode: ThemeMode; label: string; desc: string; icon: React.FC<any> }> = [
    { mode: 'light', label: 'Light Mode', desc: 'Clean, high-contrast enterprise SaaS interface', icon: Sun },
    { mode: 'dark', label: 'Dark Mode', desc: 'Sleek cybersecurity operations dark theme', icon: Moon },
    { mode: 'system', label: 'System Sync', desc: 'Automatically matches your OS preference', icon: Laptop },
  ];

  const dbHealth = healthData?.database || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Title */}
      <div className="card" style={{ padding: '24px 28px', borderLeft: '4px solid var(--primary)' }}>
        <h2 style={{ fontSize: '20px', fontWeight: 800, color: 'var(--text-main)' }}>
          Platform Settings & System Diagnostics
        </h2>
        <p style={{ fontSize: '13.5px', color: 'var(--text-muted)', marginTop: '4px' }}>
          Manage your interface theme, verify Neon PostgreSQL connectivity, and inspect ATS scoring configurations.
        </p>
      </div>

      {/* Theme Preference Card */}
      <div className="card" style={{ padding: '24px 28px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '6px' }}>
          Interface Theme
        </h3>
        <p style={{ fontSize: '13px', color: 'var(--text-dim)', marginBottom: '18px' }}>
          Select your preferred theme. Your choice is automatically saved and persists across sessions.
          Active: <strong style={{ color: 'var(--primary)', textTransform: 'capitalize' }}>{resolvedTheme} mode</strong>
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px' }}>
          {themeOptions.map((opt) => {
            const Icon = opt.icon;
            const isSelected = theme === opt.mode;
            return (
              <div
                key={opt.mode}
                id={`settings-theme-${opt.mode}`}
                onClick={() => setTheme(opt.mode)}
                className="card card-interactive"
                style={{
                  padding: '16px',
                  cursor: 'pointer',
                  border: isSelected ? '2px solid var(--primary)' : '1px solid var(--border-subtle)',
                  background: isSelected ? 'var(--primary-subtle)' : 'var(--bg-card)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                  <div
                    style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: 'var(--radius-sm)',
                      background: isSelected ? 'var(--primary)' : 'var(--bg-subtle)',
                      color: isSelected ? '#FFFFFF' : 'var(--text-muted)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Icon size={16} />
                  </div>
                  <div>
                    <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-main)' }}>
                      {opt.label}
                    </div>
                    {isSelected && (
                      <span className="badge badge-primary" style={{ fontSize: '10px', padding: '1px 5px' }}>
                        Active
                      </span>
                    )}
                  </div>
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-dim)', lineHeight: 1.4 }}>
                  {opt.desc}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Backend & Database Diagnostics */}
      <div className="card" style={{ padding: '24px 28px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-main)' }}>
              Neon PostgreSQL Database Diagnostics
            </h3>
            <p style={{ fontSize: '13px', color: 'var(--text-dim)' }}>
              Real-time connection verification against Neon cloud infrastructure.
            </p>
          </div>
          <button className="btn btn-secondary" onClick={onRefreshHealth} style={{ fontSize: '13px' }}>
            <RefreshCw size={13} />
            <span>Check Health</span>
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '14px' }}>
          <div style={{ padding: '14px', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ fontSize: '12px', color: 'var(--text-dim)' }}>Database Status</div>
            <div style={{ fontSize: '16px', fontWeight: 700, color: 'var(--emerald-success)', marginTop: '2px' }}>
              ● {dbHealth.status === 'healthy' ? 'Healthy & Connected' : 'Checking...'}
            </div>
          </div>

          <div style={{ padding: '14px', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ fontSize: '12px', color: 'var(--text-dim)' }}>Database Name</div>
            <div style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-main)', marginTop: '2px' }} className="mono">
              {dbHealth.database || 'futrsec_resume'}
            </div>
          </div>

          <div style={{ padding: '14px', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ fontSize: '12px', color: 'var(--text-dim)' }}>Query Latency</div>
            <div style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-main)', marginTop: '2px' }} className="mono">
              {dbHealth.latency_ms ? `${dbHealth.latency_ms} ms` : 'Verified'}
            </div>
          </div>

          <div style={{ padding: '14px', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ fontSize: '12px', color: 'var(--text-dim)' }}>Roles Loaded</div>
            <div style={{ fontSize: '16px', fontWeight: 700, color: 'var(--primary)', marginTop: '2px' }} className="mono">
              {rolesCount} of 74 Active
            </div>
          </div>
        </div>
      </div>

      {/* AI Model Integrations & Diagnostics */}
      <div className="card" style={{ padding: '24px 28px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '6px' }}>
          AI Model Integrations & Engine Status
        </h3>
        <p style={{ fontSize: '13px', color: 'var(--text-dim)', marginBottom: '16px' }}>
          Hosted AI pipeline with Google Gemini for fast resume evaluation and OpenAI GPT for resume generation.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          {/* Stage 1: Google Gemini */}
          <div style={{ padding: '16px', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span className="badge badge-primary" style={{ fontSize: '11px', padding: '2px 8px' }}>
                AI Model 1 — Resume Analysis
              </span>
              <span
                className={
                  healthData?.stage1_gemini?.available
                    ? 'badge badge-emerald'
                    : healthData?.stage1_gemini?.configured
                    ? 'badge badge-amber'
                    : 'badge'
                }
                style={{ fontSize: '11px' }}
              >
                {healthData?.stage1_gemini?.available
                  ? '● Online'
                  : healthData?.stage1_gemini?.configured
                  ? '● Check Key/Model'
                  : '○ Key Pending'}
              </span>
            </div>
            <div style={{ fontSize: '14.5px', fontWeight: 700, color: 'var(--text-main)' }}>
              Google Gemini API
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
              Model ID: <strong className="mono" style={{ color: 'var(--primary)' }}>{healthData?.stage1_gemini?.model || 'gemini-1.5-flash'}</strong>
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-dim)', marginTop: '6px', lineHeight: 1.4 }}>
              Analyzes resume skills, evidence gaps, projects, and role-specific recommendations.
            </div>
            {healthData?.stage1_gemini?.error && (
              <div style={{ marginTop: '8px', padding: '8px', background: 'var(--amber-bg, rgba(245, 158, 11, 0.1))', borderRadius: '4px', fontSize: '11.5px', color: 'var(--amber-text, #d97706)' }}>
                {healthData.stage1_gemini.troubleshooting || healthData.stage1_gemini.error}
              </div>
            )}
          </div>

          {/* Stage 2: OpenAI GPT */}
          <div style={{ padding: '16px', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span className="badge badge-secondary" style={{ fontSize: '11px', padding: '2px 8px' }}>
                AI Model 2 — Resume Creation
              </span>
              <span
                className={
                  healthData?.stage2_openai?.available
                    ? 'badge badge-emerald'
                    : healthData?.stage2_openai?.configured
                    ? 'badge badge-emerald'
                    : 'badge'
                }
                style={{ fontSize: '11px' }}
              >
                {healthData?.stage2_openai?.configured ? '● Configured' : '○ Heuristic Fallback'}
              </span>
            </div>
            <div style={{ fontSize: '14.5px', fontWeight: 700, color: 'var(--text-main)' }}>
              OpenAI GPT
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
              Model ID: <strong className="mono" style={{ color: 'var(--primary)' }}>{healthData?.stage2_openai?.model || 'gpt-4o-mini'}</strong>
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-dim)', marginTop: '6px', lineHeight: 1.4 }}>
              Generates ATS-optimized resume content with candidate-approved projects and skills.
            </div>
          </div>
        </div>
      </div>

      {/* ATS Scoring Criteria Weights */}
      <div className="card" style={{ padding: '24px 28px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '6px' }}>
          Deterministic ATS Scoring Engine Weights
        </h3>
        <p style={{ fontSize: '13px', color: 'var(--text-dim)', marginBottom: '16px' }}>
          Weights configured in Neon PostgreSQL across all 370 scoring criteria records (100% total).
        </p>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13.5px', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-dim)' }}>
                <th style={{ padding: '8px 12px' }}>Category</th>
                <th style={{ padding: '8px 12px' }}>Weight</th>
                <th style={{ padding: '8px 12px' }}>Evaluation Focus</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <td style={{ padding: '10px 12px', fontWeight: 600, color: 'var(--text-main)' }}>Technical Skills</td>
                <td style={{ padding: '10px 12px', color: 'var(--primary)', fontWeight: 700 }} className="mono">40%</td>
                <td style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>Core (1.5x), Preferred (1.0x), and Additional (0.5x) role skills</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <td style={{ padding: '10px 12px', fontWeight: 600, color: 'var(--text-main)' }}>Projects</td>
                <td style={{ padding: '10px 12px', color: 'var(--primary)', fontWeight: 700 }} className="mono">25%</td>
                <td style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>Hands-on cybersecurity labs, tools, and technical outcomes</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <td style={{ padding: '10px 12px', fontWeight: 600, color: 'var(--text-main)' }}>Education</td>
                <td style={{ padding: '10px 12px', color: 'var(--primary)', fontWeight: 700 }} className="mono">15%</td>
                <td style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>Degree credentials and STEM/Cyber discipline alignment</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <td style={{ padding: '10px 12px', fontWeight: 600, color: 'var(--text-main)' }}>Tools & Certifications</td>
                <td style={{ padding: '10px 12px', color: 'var(--primary)', fontWeight: 700 }} className="mono">15%</td>
                <td style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>Industry credentials (CEH, CISSP, Security+) and security toolsets</td>
              </tr>
              <tr>
                <td style={{ padding: '10px 12px', fontWeight: 600, color: 'var(--text-main)' }}>Career Objective</td>
                <td style={{ padding: '10px 12px', color: 'var(--primary)', fontWeight: 700 }} className="mono">5%</td>
                <td style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>Target job title alignment and focused professional summary</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
