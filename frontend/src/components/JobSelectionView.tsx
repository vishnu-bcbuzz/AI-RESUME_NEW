import React, { useState, useMemo } from 'react';
import {
  Search,
  X,
  Briefcase,
  Check,
  ChevronRight,
  Shield,
  RefreshCw,
  AlertCircle,
  ArrowRight,
  Layers,
  Award,
} from 'lucide-react';
import { JobRole } from '../types';

interface JobSelectionViewProps {
  roles: JobRole[];
  selectedRole: JobRole | null;
  onSelectRole: (role: JobRole) => void;
  onProceedToAnalyze: () => void;
  isLoading: boolean;
  onRetry: () => void;
  error?: string | null;
}

// Categorization helper mapping cybersecurity job roles to professional domains
export function getRoleCategory(title: string): string {
  const lower = title.toLowerCase();
  if (lower.includes('soc') || lower.includes('siem') || lower.includes('monitoring') || lower.includes('cyber defense')) {
    return 'Security Operations (SOC)';
  }
  if (lower.includes('penetration') || lower.includes('ethical hacker') || lower.includes('red team') || lower.includes('vapt') || lower.includes('bug bounty') || lower.includes('vulnerability')) {
    return 'Offensive Security';
  }
  if (lower.includes('cloud') || lower.includes('application security') || lower.includes('product security') || lower.includes('devsecops')) {
    return 'Cloud & AppSec';
  }
  if (lower.includes('grc') || lower.includes('compliance') || lower.includes('auditor') || lower.includes('risk') || lower.includes('privacy') || lower.includes('data protection') || lower.includes('data loss')) {
    return 'GRC & Privacy';
  }
  if (lower.includes('incident response') || lower.includes('threat intelligence') || lower.includes('threat hunter') || lower.includes('detection') || lower.includes('malware') || lower.includes('forensic')) {
    return 'IR & Threat Intel';
  }
  if (lower.includes('iam') || lower.includes('pam') || lower.includes('cryptograph')) {
    return 'Identity & Cryptography';
  }
  if (lower.includes('ciso') || lower.includes('manager') || lower.includes('lead')) {
    return 'Security Leadership';
  }
  return 'Security Engineering & Architecture';
}

export const JobSelectionView: React.FC<JobSelectionViewProps> = ({
  roles,
  selectedRole,
  onSelectRole,
  onProceedToAnalyze,
  isLoading,
  onRetry,
  error,
}) => {
  const [search, setSearch] = useState('');
  const [activeCategory, setActiveCategory] = useState<string>('All');

  // Compute category counts
  const categories = useMemo(() => {
    const set = new Set<string>();
    roles.forEach((r) => set.add(getRoleCategory(r.role_name)));
    return ['All', ...Array.from(set).sort()];
  }, [roles]);

  // Filtered roles
  const filteredRoles = useMemo(() => {
    return roles.filter((role) => {
      const matchesSearch =
        !search.trim() ||
        role.role_name.toLowerCase().includes(search.toLowerCase()) ||
        (role.role_description && role.role_description.toLowerCase().includes(search.toLowerCase()));

      const category = getRoleCategory(role.role_name);
      const matchesCategory = activeCategory === 'All' || category === activeCategory;

      return matchesSearch && matchesCategory;
    });
  }, [roles, search, activeCategory]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header Banner */}
      <div
        className="card"
        style={{
          padding: '28px 32px',
          background: 'var(--bg-card)',
          borderLeft: '4px solid var(--primary)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span className="badge badge-primary">CAREER TAXONOMY</span>
              {!isLoading && (
                <span className="badge badge-emerald">
                  {roles.length} Cybersecurity Roles Available
                </span>
              )}
            </div>
            <h2 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-main)' }}>
              Choose Your Cybersecurity Career Path
            </h2>
            <p style={{ fontSize: '14px', color: 'var(--text-muted)', marginTop: '4px', maxWidth: '640px' }}>
              Select a role to evaluate your resume against its skills, requirements, and qualifications.
            </p>
          </div>

          {/* Quick Selection Status Indicator */}
          {selectedRole && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px 18px',
                background: 'var(--primary-subtle)',
                border: '1px solid var(--primary-border)',
                borderRadius: 'var(--radius-sm)',
              }}
            >
              <div>
                <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--primary)', textTransform: 'uppercase' }}>
                  Selected Target Role
                </div>
                <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-main)' }}>
                  {selectedRole.role_name}
                </div>
              </div>
              <button
                id="proceed-to-analyze-btn"
                className="btn btn-primary"
                onClick={onProceedToAnalyze}
                style={{ padding: '8px 14px', fontSize: '13px' }}
              >
                <span>Analyze My Resume</span>
                <ArrowRight size={14} />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Error State with Retry Button */}
      {error && (
        <div
          className="card"
          style={{
            padding: '20px 24px',
            background: 'var(--rose-subtle)',
            borderColor: 'var(--rose-border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '16px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <AlertCircle size={22} color="var(--rose-danger)" />
            <div>
              <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--rose-danger)' }}>
                Unable to load cybersecurity job roles from backend
              </div>
              <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{error}</div>
            </div>
          </div>
          <button className="btn btn-secondary" onClick={onRetry}>
            <RefreshCw size={14} />
            <span>Retry Connection</span>
          </button>
        </div>
      )}

      {/* Search Bar & Category Filters */}
      <div className="card" style={{ padding: '20px' }}>
        {/* Search Control */}
        <div style={{ position: 'relative', marginBottom: '16px' }}>
          <Search
            size={18}
            color="var(--text-dim)"
            style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)' }}
          />
          <input
            id="job-search-input"
            type="text"
            className="input-control"
            placeholder="Search all 74 roles (e.g. SOC Analyst, Penetration Tester, Cloud Security, Incident Response)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ paddingLeft: '40px', paddingRight: search ? '40px' : '14px', height: '42px', fontSize: '14px' }}
          />
          {search && (
            <button
              onClick={() => setSearch('')}
              style={{
                position: 'absolute',
                right: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'none',
                border: 'none',
                color: 'var(--text-dim)',
                cursor: 'pointer',
                padding: '4px',
              }}
              title="Clear search"
            >
              <X size={16} />
            </button>
          )}
        </div>

        {/* Category Filter Pills */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '8px',
          }}
          role="tablist"
          aria-label="Role category filter"
        >
          {categories.map((cat) => {
            const isSelected = activeCategory === cat;
            const count =
              cat === 'All'
                ? roles.length
                : roles.filter((r) => getRoleCategory(r.role_name) === cat).length;

            return (
              <button
                key={cat}
                role="tab"
                aria-selected={isSelected}
                onClick={() => setActiveCategory(cat)}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '6px 12px',
                  borderRadius: 'var(--radius-full)',
                  fontSize: '12.5px',
                  fontWeight: isSelected ? 600 : 500,
                  border: isSelected ? '1px solid var(--primary)' : '1px solid var(--border-subtle)',
                  background: isSelected ? 'var(--primary-subtle)' : 'var(--bg-subtle)',
                  color: isSelected ? 'var(--primary)' : 'var(--text-muted)',
                  cursor: 'pointer',
                  transition: 'all var(--transition-fast)',
                }}
              >
                <span>{cat}</span>
                <span
                  style={{
                    fontSize: '11px',
                    padding: '1px 6px',
                    borderRadius: 'var(--radius-full)',
                    background: isSelected ? 'var(--primary)' : 'var(--border-strong)',
                    color: isSelected ? '#FFFFFF' : 'var(--text-dim)',
                  }}
                >
                  {count}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Grid: Job Cards */}
      {isLoading ? (
        <div
          className="card"
          style={{
            padding: '60px',
            textAlign: 'center',
            color: 'var(--text-muted)',
          }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
            <RefreshCw size={28} color="var(--primary)" className="pulse" />
            <div style={{ fontSize: '15px', fontWeight: 600 }}>Loading 74 Cybersecurity Roles from Neon...</div>
            <div style={{ fontSize: '12px', color: 'var(--text-dim)' }}>Retrieving verified industry requirements</div>
          </div>
        </div>
      ) : (
        <div>
          {/* Results Summary Bar */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '14px',
              padding: '0 4px',
              fontSize: '13px',
              color: 'var(--text-dim)',
            }}
          >
            <div>
              Showing <strong style={{ color: 'var(--text-main)' }}>{filteredRoles.length}</strong> of{' '}
              <strong style={{ color: 'var(--text-main)' }}>{roles.length}</strong> roles
              {search && <span> matching "{search}"</span>}
              {activeCategory !== 'All' && <span> in {activeCategory}</span>}
            </div>
            {selectedRole && (
              <div style={{ color: 'var(--emerald-success)', fontWeight: 600 }}>
                ✓ {selectedRole.role_name} selected
              </div>
            )}
          </div>

          {/* Cards Grid */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
              gap: '14px',
            }}
          >
            {filteredRoles.map((role) => {
              const isSelected = selectedRole?.role_id === role.role_id;
              const category = getRoleCategory(role.role_name);

              return (
                <div
                  key={role.role_id}
                  id={`role-card-${role.role_id}`}
                  onClick={() => onSelectRole(role)}
                  className="card card-interactive"
                  style={{
                    padding: '18px 20px',
                    cursor: 'pointer',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    border: isSelected ? '2px solid var(--primary)' : '1px solid var(--border-subtle)',
                    background: isSelected ? 'var(--primary-subtle)' : 'var(--bg-card)',
                    position: 'relative',
                  }}
                >
                  <div>
                    {/* Category & Selection Pill */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                      <span className="badge badge-subtle" style={{ fontSize: '11px' }}>
                        {category}
                      </span>
                      {isSelected ? (
                        <span className="badge badge-emerald" style={{ fontSize: '11px' }}>
                          <Check size={12} /> Selected
                        </span>
                      ) : (
                        <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
                          ID: {role.role_id}
                        </span>
                      )}
                    </div>

                    {/* Job Title */}
                    <h3
                      style={{
                        fontSize: '16px',
                        fontWeight: 700,
                        color: isSelected ? 'var(--primary)' : 'var(--text-main)',
                        marginBottom: '6px',
                      }}
                    >
                      {role.role_name}
                    </h3>

                    {/* Short Description */}
                    <p
                      style={{
                        fontSize: '12.5px',
                        color: 'var(--text-muted)',
                        lineHeight: 1.45,
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                        minHeight: '36px',
                      }}
                    >
                      {role.role_description ||
                        `Cybersecurity career path evaluated against verified Neon skills and ATS scoring criteria.`}
                    </p>
                  </div>

                  {/* Card Bottom Action */}
                  <div
                    style={{
                      marginTop: '14px',
                      paddingTop: '12px',
                      borderTop: '1px solid var(--border-subtle)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      fontSize: '12px',
                    }}
                  >
                    <span style={{ color: 'var(--text-dim)' }}>Click to target this role</span>
                    <span
                      style={{
                        color: isSelected ? 'var(--primary)' : 'var(--text-muted)',
                        fontWeight: 600,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                      }}
                    >
                      {isSelected ? 'Ready for Analysis' : 'Select'}
                      <ChevronRight size={14} />
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* No Results Fallback */}
          {filteredRoles.length === 0 && (
            <div
              className="card"
              style={{
                padding: '48px 24px',
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '6px' }}>
                No cybersecurity roles match "{search}"
              </div>
              <p style={{ fontSize: '13px', color: 'var(--text-dim)', marginBottom: '16px' }}>
                Try searching for 'SOC', 'Penetration', 'Analyst', 'Engineer', or reset your search filter.
              </p>
              <button
                className="btn btn-secondary"
                onClick={() => {
                  setSearch('');
                  setActiveCategory('All');
                }}
              >
                Clear Search & Filters
              </button>
            </div>
          )}
        </div>
      )}

      {/* Confirmation Sticky Bottom Panel */}
      {selectedRole && (
        <div
          className="card"
          style={{
            padding: '20px 24px',
            background: 'var(--bg-card)',
            borderTop: '3px solid var(--primary)',
            boxShadow: 'var(--shadow-lg)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '16px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--primary-subtle)',
                color: 'var(--primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Shield size={24} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="badge badge-primary">ACTIVE TARGET ROLE</span>
                <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>ID: {selectedRole.role_id}</span>
              </div>
              <div style={{ fontSize: '17px', fontWeight: 700, color: 'var(--text-main)', marginTop: '2px' }}>
                {selectedRole.role_name}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <button
              className="btn btn-secondary"
              onClick={() => {
                const nextIdx = (roles.findIndex((r) => r.role_id === selectedRole.role_id) + 1) % roles.length;
                onSelectRole(roles[nextIdx]);
              }}
              style={{ fontSize: '13px' }}
            >
              Change Role
            </button>
            <button
              id="confirm-role-and-analyze-btn"
              className="btn btn-primary"
              onClick={onProceedToAnalyze}
              style={{ padding: '10px 22px', fontSize: '14px' }}
            >
              <span>Analyze My Resume Against This Role</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
