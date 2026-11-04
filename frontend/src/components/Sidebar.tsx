import React from 'react';
import {
  LayoutDashboard,
  Briefcase,
  FileText,
  Sparkles,
  History,
  Settings,
  Shield,
  CheckCircle,
  Layers,
  CheckSquare,
} from 'lucide-react';

export type NavView = 'dashboard' | 'jobs' | 'analyze' | 'improvement' | 'tracking' | 'history' | 'templates' | 'settings';

interface SidebarProps {
  currentView: NavView;
  onNavigate: (view: NavView) => void;
  rolesCount: number;
  hasAnalysis: boolean;
  hasImprovement: boolean;
  historyCount: number;
  selectedRoleTitle?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentView,
  onNavigate,
  rolesCount,
  hasAnalysis,
  hasImprovement,
  historyCount,
  selectedRoleTitle,
}) => {
  const navItems = [
    {
      id: 'dashboard' as NavView,
      label: 'Dashboard',
      icon: LayoutDashboard,
      badge: undefined,
    },
    {
      id: 'jobs' as NavView,
      label: 'Cybersecurity Jobs',
      icon: Briefcase,
      badge: rolesCount > 0 ? `${rolesCount}` : undefined,
    },
    {
      id: 'analyze' as NavView,
      label: 'Analyze Resume',
      icon: FileText,
      badge: hasAnalysis ? 'Active' : undefined,
    },
    {
      id: 'improvement' as NavView,
      label: 'Resume Improvement',
      icon: Sparkles,
      badge: hasImprovement ? 'Ready' : undefined,
    },
    {
      id: 'tracking' as NavView,
      label: 'Project Tracker',
      icon: CheckSquare,
      badge: 'Active',
    },
    {
      id: 'history' as NavView,
      label: 'Analysis History',
      icon: History,
      badge: historyCount > 0 ? `${historyCount}` : undefined,
    },
    {
      id: 'templates' as NavView,
      label: 'Template Gallery',
      icon: Layers,
      badge: '30',
    },
    {
      id: 'settings' as NavView,
      label: 'Settings',
      icon: Settings,
      badge: undefined,
    },
  ];

  return (
    <aside
      style={{
        width: '260px',
        background: 'var(--bg-sidebar)',
        borderRight: '1px solid var(--border-subtle)',
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        position: 'sticky',
        top: 0,
        zIndex: 40,
        flexShrink: 0,
        transition: 'background-color var(--transition-fast)',
      }}
    >
      {/* Brand Header */}
      <div
        style={{
          padding: '20px 20px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
        }}
      >
        <div
          style={{
            width: '38px',
            height: '38px',
            borderRadius: 'var(--radius-sm)',
            background: 'var(--primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#FFFFFF',
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          <Shield size={22} strokeWidth={2.5} />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span
              style={{
                fontFamily: 'var(--font-heading)',
                fontSize: '19px',
                fontWeight: 800,
                color: 'var(--text-main)',
                letterSpacing: '-0.02em',
              }}
            >
              FUTRSEC
            </span>
            <span className="badge badge-primary" style={{ fontSize: '10px', padding: '1px 5px' }}>
              PRO
            </span>
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', fontWeight: 500 }}>
            Cybersecurity Career AI
          </div>
        </div>
      </div>

      {/* Navigation Menu */}
      <nav style={{ padding: '16px 12px', flex: 1, overflowY: 'auto' }}>
        <div
          style={{
            fontSize: '11px',
            fontWeight: 700,
            textTransform: 'uppercase',
            color: 'var(--text-dim)',
            letterSpacing: '0.05em',
            padding: '4px 10px 10px',
          }}
        >
          Core Platform
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;
            return (
              <button
                key={item.id}
                id={`sidebar-nav-${item.id}`}
                onClick={() => onNavigate(item.id)}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '9px 12px',
                  borderRadius: 'var(--radius-sm)',
                  border: 'none',
                  background: isActive ? 'var(--primary-subtle)' : 'transparent',
                  color: isActive ? 'var(--primary)' : 'var(--text-muted)',
                  fontWeight: isActive ? 600 : 500,
                  fontSize: '13.5px',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all var(--transition-fast)',
                }}
                onMouseEnter={(e) => {
                  if (!isActive) e.currentTarget.style.background = 'var(--bg-card-hover)';
                }}
                onMouseLeave={(e) => {
                  if (!isActive) e.currentTarget.style.background = 'transparent';
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Icon size={18} strokeWidth={isActive ? 2.5 : 2} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span
                    className={
                      item.badge === 'Active' || item.badge === 'Ready'
                        ? 'badge badge-emerald'
                        : 'badge badge-subtle'
                    }
                    style={{ fontSize: '11px' }}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </nav>

      {/* Selected Role Quick Status Footer */}
      <div
        style={{
          padding: '16px',
          borderTop: '1px solid var(--border-subtle)',
          background: 'var(--bg-subtle)',
        }}
      >
        <div style={{ fontSize: '11px', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase' }}>
          Target Job Role
        </div>
        <div
          style={{
            fontSize: '13px',
            fontWeight: 600,
            color: 'var(--text-main)',
            marginTop: '3px',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}
          title={selectedRoleTitle || 'None Selected'}
        >
          {selectedRoleTitle ? (
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <CheckCircle size={14} color="var(--emerald-success)" />
              {selectedRoleTitle}
            </span>
          ) : (
            <span style={{ color: 'var(--text-dim)' }}>Select in Jobs Menu</span>
          )}
        </div>
      </div>
    </aside>
  );
};
