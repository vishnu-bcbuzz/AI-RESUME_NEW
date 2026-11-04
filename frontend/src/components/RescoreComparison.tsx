import React from 'react';
import {
  TrendingUp,
  Award,
  CheckCircle,
  RotateCcw,
  Download,
  BarChart2,
} from 'lucide-react';
import { RescoreResponse } from '../types';

interface RescoreComparisonProps {
  rescore: RescoreResponse;
  roleName: string;
  docxUrl?: string;
  pdfUrl?: string | null;
  onStartNew: () => void;
}

export const RescoreComparison: React.FC<RescoreComparisonProps> = ({
  rescore,
  roleName,
  docxUrl,
  pdfUrl,
  onStartNew,
}) => {
  const isPassing = rescore.meets_threshold;

  return (
    <div className="card" style={{ padding: '32px' }}>
      {/* Top Banner */}
      <div style={{ textAlign: 'center', marginBottom: '28px' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
          <span className="badge badge-emerald" style={{ fontSize: '13px', padding: '5px 12px' }}>
            <TrendingUp size={15} /> RE-SCORING VERIFIED
          </span>
          <span className={isPassing ? 'badge badge-emerald' : 'badge badge-amber'}>
            {isPassing ? 'PASSED 80+ THRESHOLD' : 'IMPROVEMENT APPLIED'}
          </span>
        </div>
        <h2 style={{ fontSize: '26px', fontWeight: 800, color: 'var(--text-main)' }}>
          Resume Compatibility Re-Scoring Results
        </h2>
        <p style={{ fontSize: '14px', color: 'var(--text-muted)', maxWidth: '640px', margin: '6px auto 0' }}>
          Evaluated against {roleName} scoring criteria using the exact same deterministic Python engine.
        </p>
      </div>

      {/* Before vs After Score Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '28px' }}>
        {/* Original */}
        <div
          style={{
            background: 'var(--bg-subtle)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            padding: '20px',
            textAlign: 'center',
          }}
        >
          <div style={{ fontSize: '12px', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase' }}>
            Original Score
          </div>
          <div className="mono" style={{ fontSize: '36px', fontWeight: 800, color: 'var(--text-dim)', margin: '6px 0' }}>
            {rescore.original_score}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-dim)' }}>Pre-Optimization</div>
        </div>

        {/* Delta */}
        <div
          style={{
            background: 'var(--emerald-subtle)',
            border: '1px solid var(--emerald-border)',
            borderRadius: 'var(--radius-sm)',
            padding: '20px',
            textAlign: 'center',
          }}
        >
          <div style={{ fontSize: '12px', color: 'var(--emerald-success)', fontWeight: 600, textTransform: 'uppercase' }}>
            Score Delta
          </div>
          <div className="mono" style={{ fontSize: '36px', fontWeight: 800, color: 'var(--emerald-success)', margin: '6px 0' }}>
            +{rescore.score_delta}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--emerald-success)' }}>ATS Evidence Increase</div>
        </div>

        {/* New Score */}
        <div
          style={{
            background: isPassing ? 'var(--emerald-subtle)' : 'var(--primary-subtle)',
            border: `2px solid ${isPassing ? 'var(--emerald-success)' : 'var(--primary)'}`,
            borderRadius: 'var(--radius-sm)',
            padding: '20px',
            textAlign: 'center',
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          <div style={{ fontSize: '12px', color: isPassing ? 'var(--emerald-success)' : 'var(--primary)', fontWeight: 700, textTransform: 'uppercase' }}>
            New Accepted Score
          </div>
          <div className="mono" style={{ fontSize: '42px', fontWeight: 900, color: 'var(--text-main)', margin: '4px 0' }}>
            {rescore.new_score}
          </div>
          <div style={{ fontSize: '12px', color: isPassing ? 'var(--emerald-success)' : 'var(--primary)', fontWeight: 600 }}>
            {isPassing ? '★ Meets 80+ Target Threshold' : 'Improved Compatibility'}
          </div>
        </div>
      </div>

      {/* Category Comparison Table */}
      <div style={{ marginBottom: '28px' }}>
        <h4 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <BarChart2 size={18} color="var(--primary)" />
          Category-by-Category Scoring Breakdown
        </h4>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13.5px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-dim)' }}>
                <th style={{ padding: '10px 14px' }}>Category</th>
                <th style={{ padding: '10px 14px' }}>Max Weight</th>
                <th style={{ padding: '10px 14px' }}>Original</th>
                <th style={{ padding: '10px 14px' }}>New Score</th>
                <th style={{ padding: '10px 14px' }}>Score Change</th>
              </tr>
            </thead>
            <tbody>
              {rescore.category_comparison.map((row) => (
                <tr key={row.category} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <td style={{ padding: '12px 14px', fontWeight: 600, color: 'var(--text-main)' }}>{row.category}</td>
                  <td style={{ padding: '12px 14px', color: 'var(--text-dim)' }}>{row.weight} pts</td>
                  <td style={{ padding: '12px 14px', color: 'var(--text-dim)' }} className="mono">
                    {row.original_score}
                  </td>
                  <td style={{ padding: '12px 14px', color: 'var(--text-main)', fontWeight: 700 }} className="mono">
                    {row.new_score}
                  </td>
                  <td style={{ padding: '12px 14px' }}>
                    <span
                      className="mono"
                      style={{
                        color: row.delta > 0 ? 'var(--emerald-success)' : row.delta === 0 ? 'var(--text-dim)' : 'var(--rose-danger)',
                        fontWeight: 700,
                      }}
                    >
                      {row.delta > 0 ? `+${row.delta}` : row.delta}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Explanation Box */}
      <div
        style={{
          background: 'var(--bg-subtle)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-sm)',
          padding: '18px',
          marginBottom: '28px',
        }}
      >
        <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--primary)', marginBottom: '4px' }}>
          Score Recalculation Rationale
        </div>
        <p style={{ fontSize: '13.5px', color: 'var(--text-muted)', lineHeight: 1.6 }}>
          {rescore.explanation}
        </p>
      </div>

      {/* Action Buttons */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px' }}>
        <button className="btn btn-secondary" onClick={onStartNew}>
          <RotateCcw size={15} />
          <span>Start New Analysis</span>
        </button>

        <div style={{ display: 'flex', gap: '12px' }}>
          {docxUrl && (
            <a href={docxUrl} download className="btn btn-primary">
              <Download size={15} />
              <span>Download Final DOCX</span>
            </a>
          )}
          {pdfUrl && (
            <a href={pdfUrl} download className="btn btn-secondary">
              <Download size={15} />
              <span>Download Final PDF</span>
            </a>
          )}
        </div>
      </div>
    </div>
  );
};
