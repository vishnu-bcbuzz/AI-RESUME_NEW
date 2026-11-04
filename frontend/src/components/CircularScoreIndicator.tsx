import React from 'react';

export interface ScoreColorConfig {
  stroke: string;        // Hex or CSS variable for the circular progress ring
  bgSubtle: string;      // Background tint for badge
  border: string;        // Border tint for badge
  badgeClass: string;    // FUTRSEC badge CSS class
  statusLabel: 'Improvement Required' | 'Good Score';
  colorName: 'red' | 'orange' | 'blue' | 'green';
}

/**
 * Returns dynamic color configuration based on ATS score specifications:
 * - 0–39: Red
 * - 40–69: Orange
 * - 70–84: Blue or green (using FUTRSEC primary blue #2563EB)
 * - 85–100: Green (using FUTRSEC emerald #059669)
 */
export const getScoreColorConfig = (score: number): ScoreColorConfig => {
  const s = Number(score) || 0;
  if (s < 40) {
    return {
      stroke: 'var(--rose-danger, #E11D48)',
      bgSubtle: 'var(--rose-subtle, #FFF1F2)',
      border: 'var(--rose-border, #FECDD3)',
      badgeClass: 'badge-rose',
      statusLabel: 'Improvement Required',
      colorName: 'red',
    };
  } else if (s < 70) {
    return {
      stroke: 'var(--amber-warn, #D97706)',
      bgSubtle: 'var(--amber-subtle, #FFFBEB)',
      border: 'var(--amber-border, #FDE68A)',
      badgeClass: 'badge-amber',
      statusLabel: 'Improvement Required',
      colorName: 'orange',
    };
  } else if (s < 85) {
    return {
      stroke: 'var(--primary, #2563EB)',
      bgSubtle: 'var(--primary-subtle, #EFF6FF)',
      border: 'var(--primary-border, #BFDBFE)',
      badgeClass: 'badge-primary',
      statusLabel: 'Good Score',
      colorName: 'blue',
    };
  } else {
    return {
      stroke: 'var(--emerald-success, #059669)',
      bgSubtle: 'var(--emerald-subtle, #ECFDF5)',
      border: 'var(--emerald-border, #A7F3D0)',
      badgeClass: 'badge-emerald',
      statusLabel: 'Good Score',
      colorName: 'green',
    };
  }
};

export interface CircularScoreIndicatorProps {
  score: number;
  size?: number;          // Diameter in pixels (default 92)
  strokeWidth?: number;   // Progress ring thickness in pixels (default 7)
  className?: string;
  style?: React.CSSProperties;
}

export const CircularScoreIndicator: React.FC<CircularScoreIndicatorProps> = ({
  score,
  size = 92,
  strokeWidth = 7,
  className = '',
  style = {},
}) => {
  const numericScore = typeof score === 'number' ? score : Number(score) || 0;
  const clampedScore = Math.min(100, Math.max(0, numericScore));
  const colorConfig = getScoreColorConfig(clampedScore);

  // SVG circular geometry
  const center = size / 2;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (clampedScore / 100) * circumference;

  // Format score: integer if whole number (e.g. 25, 75, 92), decimal if fractional (e.g. 40.2)
  const formattedScore =
    numericScore % 1 === 0 ? numericScore.toString() : numericScore.toFixed(1);

  return (
    <div
      className={`circular-score-indicator ${className}`}
      style={{
        position: 'relative',
        width: `${size}px`,
        height: `${size}px`,
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
        borderRadius: '50%',
        ...style,
      }}
      aria-label={`ATS Score: ${formattedScore} out of 100. Status: ${colorConfig.statusLabel}`}
      role="progressbar"
      aria-valuenow={numericScore}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        style={{ transform: 'rotate(-90deg)', overflow: 'visible' }}
      >
        {/* Subtle Background Circle & Track */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="var(--bg-card, #FFFFFF)"
          stroke="var(--border-subtle, #E2E8F0)"
          strokeWidth={strokeWidth}
          style={{ opacity: 0.85 }}
        />

        {/* Dynamic Progress Ring */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="transparent"
          stroke={colorConfig.stroke}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          style={{
            transition: 'stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.3s ease',
          }}
        />
      </svg>

      {/* Center Score & Denominator: perfectly centered horizontally and vertically */}
      <div
        className="circular-score-center"
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          pointerEvents: 'none',
          lineHeight: 1,
        }}
      >
        <span
          className="mono circular-score-number"
          style={{
            fontSize: size >= 90 ? '24px' : '20px',
            fontWeight: 800,
            color: 'var(--text-main, #0F172A)',
            letterSpacing: '-0.02em',
          }}
        >
          {formattedScore}
        </span>
        <span
          className="circular-score-denominator"
          style={{
            fontSize: size >= 90 ? '11px' : '9.5px',
            fontWeight: 700,
            color: 'var(--text-dim, #64748B)',
            marginTop: '3px',
            letterSpacing: '0.02em',
          }}
        >
          /100
        </span>
      </div>
    </div>
  );
};

