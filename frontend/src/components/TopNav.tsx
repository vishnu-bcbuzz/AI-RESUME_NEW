import React from 'react';
import {
  Sun,
  Moon,
  Laptop,
  Database,
  Shield,
  Menu,
} from 'lucide-react';
import { useTheme, ThemeMode } from '../context/ThemeContext';
import { NavView } from './Sidebar';

interface TopNavProps {
  currentView: NavView;
  selectedRoleTitle?: string;
  rolesCount: number;
  dbStatus: string;
  onToggleMobileSidebar?: () => void;
}

export const TopNav: React.FC<TopNavProps> = ({
  currentView,
  selectedRoleTitle,
  rolesCount,
  dbStatus,
  onToggleMobileSidebar,
}) => {
  const { theme, setTheme } = useTheme();

  const viewTitles: Record<NavView, string> = {
    dashboard: 'Platform Dashboard',
    jobs: 'Cybersecurity Job Roles',
    analyze: 'Resume Analysis Studio',
    improvement: 'ATS Resume Improvement',
    tracking: 'Project Completion Tracker',
    history: 'Analysis History',
    templates: 'Resume Template Gallery',
    settings: 'Platform Settings & Diagnostics',
  };

  const themeOptions: Array<{ mode: ThemeMode; label: string; icon: React.FC<any> }> = [
    { mode: 'light', label: 'Light', icon: Sun },
    { mode: 'dark', label: 'Dark', icon: Moon },
    { mode: 'system', label: 'System', icon: Laptop },
  ];

  return (
    <header
      style={{
        height: '64px',
        background: 'var(--bg-topbar)',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 28px',
        position: 'sticky',
        top: 0,
        zIndex: 30,
        backdropFilter: 'blur(8px)',
        transition: 'background-color var(--transition-fast)',
      }}
    >
      {/* Left: Mobile Toggle & Breadcrumbs */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {onToggleMobileSidebar && (
          <button
            onClick={onToggleMobileSidebar}
            className="btn btn-secondary"
            style={{ padding: '6px', display: 'none' }}
            aria-label="Toggle Navigation"
          >
            <Menu size={18} />
          </button>
        )}

        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: 'var(--text-dim)' }}>
            <span>FUTRSEC</span>
            <span>/</span>
            <span style={{ color: 'var(--text-muted)' }}>{viewTitles[currentView]}</span>
            {selectedRoleTitle && currentView !== 'jobs' && (
              <>
                <span>/</span>
                <span style={{ color: 'var(--primary)', fontWeight: 600 }}>{selectedRoleTitle}</span>
              </>
            )}
          </div>
          <h1 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-main)', marginTop: '1px' }}>
            {viewTitles[currentView]}
          </h1>
        </div>
      </div>

      {/* Right: DB Status & Light/Dark Theme Switcher */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Neon Database Status Badge */}
        <div
          className={dbStatus === 'healthy' ? 'badge badge-emerald' : 'badge badge-amber'}
          title="Neon Serverless PostgreSQL connection"
          style={{ padding: '5px 10px', fontSize: '12px' }}
        >
          <Database size={13} />
          <span>Neon DB: {rolesCount} Roles</span>
        </div>

        {/* Theme Switcher Segmented Control */}
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            background: 'var(--bg-subtle)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            padding: '3px',
            gap: '2px',
          }}
          role="radiogroup"
          aria-label="Theme selection"
        >
          {themeOptions.map((opt) => {
            const Icon = opt.icon;
            const isSelected = theme === opt.mode;
            return (
              <button
                key={opt.mode}
                id={`theme-btn-${opt.mode}`}
                role="radio"
                aria-checked={isSelected}
                onClick={() => setTheme(opt.mode)}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '5px 9px',
                  fontSize: '12px',
                  fontWeight: isSelected ? 600 : 500,
                  borderRadius: 'var(--radius-xs)',
                  border: 'none',
                  background: isSelected ? 'var(--bg-card)' : 'transparent',
                  color: isSelected ? 'var(--primary)' : 'var(--text-dim)',
                  boxShadow: isSelected ? 'var(--shadow-sm)' : 'none',
                  cursor: 'pointer',
                  transition: 'all var(--transition-fast)',
                }}
              >
                <Icon size={13} />
                <span>{opt.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
