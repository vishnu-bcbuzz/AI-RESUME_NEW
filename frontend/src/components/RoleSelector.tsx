import React, { useState, useMemo } from 'react';
import { Search, Shield, Check, ChevronRight } from 'lucide-react';
import { JobRole } from '../types';

interface RoleSelectorProps {
  roles: JobRole[];
  selectedRole: JobRole | null;
  onSelectRole: (role: JobRole) => void;
  isLoading?: boolean;
}

export const RoleSelector: React.FC<RoleSelectorProps> = ({
  roles,
  selectedRole,
  onSelectRole,
  isLoading = false,
}) => {
  const [search, setSearch] = useState('');

  const filteredRoles = useMemo(() => {
    if (!search.trim()) return roles;
    const term = search.toLowerCase();
    return roles.filter(
      (r) =>
        r.role_name.toLowerCase().includes(term) ||
        (r.role_description && r.role_description.toLowerCase().includes(term))
    );
  }, [roles, search]);

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Shield size={20} color="var(--cyan-primary)" />
            Step 1: Select Target Cybersecurity Role
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
            Choose from all {roles.length} verified cybersecurity roles loaded live from Neon PostgreSQL.
          </p>
        </div>

        {selectedRole && (
          <div className="badge badge-cyan" style={{ fontSize: '13px', padding: '6px 14px' }}>
            <Check size={14} /> Selected: {selectedRole.role_name}
          </div>
        )}
      </div>

      {/* Search Input */}
      <div style={{ position: 'relative', marginBottom: '16px' }}>
        <Search
          size={18}
          color="var(--text-dim)"
          style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)' }}
        />
        <input
          id="role-search-input"
          type="text"
          placeholder="Search by role title (e.g. Ethical Hacker, SOC Analyst, Cloud Security, Penetration Tester)..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            width: '100%',
            padding: '12px 16px 12px 42px',
            background: 'rgba(255, 255, 255, 0.04)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            color: '#FFFFFF',
            fontSize: '14px',
            outline: 'none',
            transition: 'border-color 0.2s',
          }}
          onFocus={(e) => (e.target.style.borderColor = 'var(--cyan-primary)')}
          onBlur={(e) => (e.target.style.borderColor = 'var(--border-subtle)')}
        />
      </div>

      {/* Roles Grid */}
      {isLoading ? (
        <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
          Loading cybersecurity roles from Neon PostgreSQL...
        </div>
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
            gap: '10px',
            maxHeight: '300px',
            overflowY: 'auto',
            paddingRight: '6px',
          }}
        >
          {filteredRoles.map((role) => {
            const isSelected = selectedRole?.role_id === role.role_id;
            return (
              <button
                key={role.role_id}
                id={`role-btn-${role.role_id}`}
                onClick={() => onSelectRole(role)}
                style={{
                  textAlign: 'left',
                  padding: '12px 14px',
                  borderRadius: 'var(--radius-sm)',
                  background: isSelected
                    ? 'linear-gradient(135deg, rgba(6, 182, 212, 0.2) 0%, rgba(59, 130, 246, 0.15) 100%)'
                    : 'rgba(255, 255, 255, 0.03)',
                  border: isSelected ? '1px solid var(--cyan-primary)' : '1px solid var(--border-subtle)',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  boxShadow: isSelected ? '0 0 15px rgba(6, 182, 212, 0.25)' : 'none',
                }}
              >
                <div>
                  <div style={{ fontSize: '13.5px', fontWeight: 600, color: isSelected ? '#38BDF8' : '#F1F5F9' }}>
                    {role.role_name}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>
                    Role ID: {role.role_id}
                  </div>
                </div>
                {isSelected ? (
                  <Check size={16} color="var(--cyan-primary)" />
                ) : (
                  <ChevronRight size={14} color="var(--text-dim)" />
                )}
              </button>
            );
          })}
          {filteredRoles.length === 0 && (
            <div style={{ gridColumn: '1 / -1', padding: '24px', textAlign: 'center', color: 'var(--text-dim)' }}>
              No roles match "{search}". Try searching for 'Hacker', 'Analyst', or 'Engineer'.
            </div>
          )}
        </div>
      )}
    </div>
  );
};
