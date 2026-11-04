import React from 'react';
import { Shield, Database, Cpu, RefreshCw } from 'lucide-react';

interface HeaderProps {
  dbStatus?: string;
  rolesCount?: number;
  rrCursor?: number;
}

export const Header: React.FC<HeaderProps> = ({
  dbStatus = 'healthy',
  rolesCount = 74,
  rrCursor = 0,
}) => {
  return (
    <header style={{
      borderBottom: '1px solid var(--border-subtle)',
      background: 'rgba(9, 13, 22, 0.85)',
      backdropFilter: 'blur(12px)',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      padding: '16px 32px',
    }}>
      <div style={{
        maxWidth: '1280px',
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px',
      }}>
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 20px rgba(6, 182, 212, 0.4)',
          }}>
            <Shield size={24} color="#FFFFFF" strokeWidth={2.5} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{
                fontFamily: 'var(--font-heading)',
                fontSize: '22px',
                fontWeight: 800,
                letterSpacing: '-0.03em',
                background: 'linear-gradient(to right, #FFFFFF, #94A3B8)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}>
                FUTRSEC
              </span>
              <span className="badge badge-cyan" style={{ fontSize: '10px', padding: '2px 6px' }}>
                AI ENGINE
              </span>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-dim)', margin: 0 }}>
              Cybersecurity ATS Matcher & Resume Studio
            </p>
          </div>
        </div>

        {/* Live System Indicators */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          <div className="badge badge-emerald" title="Connected to Neon PostgreSQL">
            <Database size={13} />
            <span>Neon DB ({rolesCount} Roles)</span>
          </div>

          <div className="badge badge-cyan" title="Deterministic ATS Engine Active">
            <Cpu size={13} />
            <span>Deterministic Scoring</span>
          </div>

          <div className="badge badge-subtle" title="Round Robin Template Cursor">
            <RefreshCw size={13} />
            <span>RR Cursor: {rrCursor}</span>
          </div>
        </div>
      </div>
    </header>
  );
};
