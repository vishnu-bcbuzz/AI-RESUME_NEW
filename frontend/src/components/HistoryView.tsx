import React from 'react';
import { History, FileText, CheckCircle, AlertTriangle, ArrowRight, RotateCcw } from 'lucide-react';
import { AnalysisResponse } from '../types';

export interface HistoryItem {
  id: string;
  timestamp: string;
  analysis: AnalysisResponse;
}

interface HistoryViewProps {
  history: HistoryItem[];
  onSelectHistory: (item: HistoryItem) => void;
  onStartNew: () => void;
}

export const HistoryView: React.FC<HistoryViewProps> = ({
  history,
  onSelectHistory,
  onStartNew,
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div className="card" style={{ padding: '24px 28px', borderLeft: '4px solid var(--primary)' }}>
        <h2 style={{ fontSize: '20px', fontWeight: 800, color: 'var(--text-main)' }}>
          Resume Analysis Session History
        </h2>
        <p style={{ fontSize: '13.5px', color: 'var(--text-muted)', marginTop: '4px' }}>
          Review previously evaluated resumes and scores conducted during this session.
        </p>
      </div>

      {history.length === 0 ? (
        <div className="card" style={{ padding: '48px 24px', textAlign: 'center' }}>
          <History size={40} color="var(--text-dim)" style={{ margin: '0 auto 12px' }} />
          <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '6px' }}>
            No Resume Analyses Recorded Yet
          </h3>
          <p style={{ fontSize: '13px', color: 'var(--text-dim)', marginBottom: '18px' }}>
            Upload a resume and evaluate it against any of the 74 cybersecurity roles to generate your first report.
          </p>
          <button className="btn btn-primary" onClick={onStartNew}>
            <span>Start Resume Analysis</span>
            <ArrowRight size={15} />
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {history.map((item) => {
            const res = item.analysis.score_result;
            const isPassing = res.meets_threshold;
            return (
              <div
                key={item.id}
                className="card card-interactive"
                onClick={() => onSelectHistory(item)}
                style={{
                  padding: '18px 22px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  cursor: 'pointer',
                  flexWrap: 'wrap',
                  gap: '14px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div
                    style={{
                      width: '44px',
                      height: '44px',
                      borderRadius: 'var(--radius-sm)',
                      background: isPassing ? 'var(--emerald-subtle)' : 'var(--amber-subtle)',
                      color: isPassing ? 'var(--emerald-success)' : 'var(--amber-warn)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 800,
                      fontSize: '15px',
                    }}
                    className="mono"
                  >
                    {res.final_score}
                  </div>

                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-main)' }}>
                        {item.analysis.role_name}
                      </span>
                      <span className={isPassing ? 'badge badge-emerald' : 'badge badge-amber'} style={{ fontSize: '11px' }}>
                        {isPassing ? 'Eligible' : 'Improvement Recommended'}
                      </span>
                    </div>
                    <div style={{ fontSize: '12.5px', color: 'var(--text-dim)', marginTop: '2px' }}>
                      File: <strong>{item.analysis.filename}</strong> • Evaluated on {item.timestamp}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '13px', color: 'var(--primary)', fontWeight: 600 }}>View Full Report</span>
                  <ArrowRight size={15} color="var(--primary)" />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
