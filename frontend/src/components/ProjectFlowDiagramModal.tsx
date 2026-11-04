import React, { useMemo, useRef } from 'react';
import { X, ArrowLeft, GitFork, ShieldCheck, AlertCircle, Download, FileCode, Image as ImageIcon } from 'lucide-react';

export interface WorkflowNode {
  step: number;
  type: 'start' | 'phase' | 'decision' | 'end';
  label: string;
  isLoopTarget?: boolean;
  noAction?: string;
  noTargetStep?: number;
  yesAction?: string;
}

interface ProjectFlowDiagramModalProps {
  projectTitle: string;
  domain?: string;
  rawWorkflow?: any[];
  planPhases?: any[];
  onClose: () => void;
}

/**
 * Robust word-wrapping utility that breaks long labels into multiple lines without clipping.
 */
function wrapText(text: string, maxCharsPerLine: number): string[] {
  if (!text) return [];
  const words = text.trim().split(/\s+/);
  const lines: string[] = [];
  let currentLine = '';

  for (const word of words) {
    if (!currentLine) {
      currentLine = word;
    } else if ((currentLine + ' ' + word).length <= maxCharsPerLine) {
      currentLine += ' ' + word;
    } else {
      lines.push(currentLine);
      currentLine = word;
    }
  }
  if (currentLine) {
    lines.push(currentLine);
  }
  return lines.length > 0 ? lines : [text];
}

export const ProjectFlowDiagramModal: React.FC<ProjectFlowDiagramModalProps> = ({
  projectTitle,
  domain,
  rawWorkflow,
  planPhases,
  onClose,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);

  // Construct the project's visual workflow
  const workflowNodes: WorkflowNode[] = useMemo(() => {
    const titleLower = projectTitle.trim().toLowerCase();

    // 1. Enterprise Network Hardening & Vulnerability Remediation Lab (Exact User Prompt Specification)
    if (
      titleLower.includes('enterprise network hardening') ||
      titleLower.includes('network hardening & vulnerability remediation') ||
      titleLower.includes('network hardening')
    ) {
      return [
        { step: 1, type: 'start', label: 'START' },
        { step: 2, type: 'phase', label: 'Virtual Network Setup' },
        { step: 3, type: 'phase', label: 'Deploy Ubuntu Server VMs' },
        { step: 4, type: 'phase', label: 'Configure Network and Verify Connectivity' },
        { step: 5, type: 'phase', label: 'Nmap Reconnaissance' },
        { step: 6, type: 'phase', label: 'OpenVAS Vulnerability Assessment' },
        { step: 7, type: 'phase', label: 'Linux Hardening and Firewall Configuration', isLoopTarget: true },
        { step: 8, type: 'phase', label: 'Post-Hardening Security Validation' },
        {
          step: 9,
          type: 'decision',
          label: 'Are security requirements satisfied?',
          noAction: 'Review findings and perform further hardening.',
          noTargetStep: 7,
          yesAction: 'Document verified results.',
        },
        { step: 10, type: 'phase', label: 'Document verified results.' },
        { step: 11, type: 'phase', label: 'Generate Security Assessment Report' },
        { step: 12, type: 'end', label: 'END' },
      ];
    }

    // 2. Web Application Security Testing Lab & Vulnerability Remediation
    if (
      titleLower.includes('web application security') ||
      (titleLower.includes('vulnerability remediation') && titleLower.includes('web'))
    ) {
      return [
        { step: 1, type: 'start', label: 'START' },
        { step: 2, type: 'phase', label: 'Configure Isolated Lab in Docker (Juice Shop / DVWA)' },
        { step: 3, type: 'phase', label: 'Map Attack Surface via Nmap & Burp Suite Proxy' },
        { step: 4, type: 'phase', label: 'Execute Targeted Vulnerability Tests (SQLi, XSS, IDOR)', isLoopTarget: true },
        {
          step: 5,
          type: 'decision',
          label: 'Was the vulnerability verified & reproduced?',
          noAction: 'Review evidence and refine testing in authorized lab.',
          noTargetStep: 4,
          yesAction: 'Record verified findings & exploit proof.',
        },
        { step: 6, type: 'phase', label: 'Record verified findings & exploit proof.' },
        { step: 7, type: 'phase', label: 'Apply CVSS v3.1 Severity Scoring & Remediation Planning' },
        { step: 8, type: 'phase', label: 'Compile Final Security Assessment Report' },
        { step: 9, type: 'end', label: 'END' },
      ];
    }

    // 3. Security Operations Center (SOC) Log Analysis & Threat Hunting Lab / Security Log Analysis
    if (
      titleLower.includes('soc') ||
      titleLower.includes('log analysis') ||
      titleLower.includes('threat detection') ||
      titleLower.includes('threat hunting')
    ) {
      return [
        { step: 1, type: 'start', label: 'START' },
        { step: 2, type: 'phase', label: 'Deploy SIEM Environment & Telemetry Collectors (Splunk / Elastic)' },
        { step: 3, type: 'phase', label: 'Ingest & Parse System Logs and Network PCAPs' },
        { step: 4, type: 'phase', label: 'Execute Threat Hunting Queries & Sigma Detection Rules', isLoopTarget: true },
        {
          step: 5,
          type: 'decision',
          label: 'Was suspicious threat activity identified?',
          noAction: 'Tune detection baseline & refine search query filters.',
          noTargetStep: 4,
          yesAction: 'Isolate alert telemetry and catalog verified IOCs.',
        },
        { step: 6, type: 'phase', label: 'Isolate alert telemetry and catalog verified IOCs.' },
        { step: 7, type: 'phase', label: 'Conduct Incident Triage & Develop Remediation Playbook' },
        { step: 8, type: 'phase', label: 'Generate SOC Incident Investigation Report' },
        { step: 9, type: 'end', label: 'END' },
      ];
    }

    // 4. Cloud Security & Compliance Hardening Lab / Multi-Tier Cloud Deployment
    if (
      titleLower.includes('cloud security') ||
      titleLower.includes('cloud infrastructure') ||
      (titleLower.includes('cloud') && titleLower.includes('hardening'))
    ) {
      return [
        { step: 1, type: 'start', label: 'START' },
        { step: 2, type: 'phase', label: 'Provision Isolated Cloud Environment via Terraform / LocalStack' },
        { step: 3, type: 'phase', label: 'Execute Automated Security Audits (ScoutSuite / Prowler)' },
        { step: 4, type: 'phase', label: 'Apply Least-Privilege IAM Policies & Security Groups', isLoopTarget: true },
        {
          step: 5,
          type: 'decision',
          label: 'Are cloud posture compliance benchmarks satisfied?',
          noAction: 'Remediate misconfigurations & update security policies.',
          noTargetStep: 4,
          yesAction: 'Verify zero high-risk findings and establish baseline.',
        },
        { step: 6, type: 'phase', label: 'Verify zero high-risk findings and establish baseline.' },
        { step: 7, type: 'phase', label: 'Deploy CloudWatch & GuardDuty Monitoring Guardrails' },
        { step: 8, type: 'phase', label: 'Generate Cloud Security Assessment & Audit Report' },
        { step: 9, type: 'end', label: 'END' },
      ];
    }

    // 5. DevSecOps Pipeline & Automated Code Security Scanning Lab
    if (
      titleLower.includes('devsecops') ||
      titleLower.includes('code security') ||
      (titleLower.includes('pipeline') && titleLower.includes('security'))
    ) {
      return [
        { step: 1, type: 'start', label: 'START' },
        { step: 2, type: 'phase', label: 'Configure GitHub Actions CI/CD Pipeline & Runner' },
        { step: 3, type: 'phase', label: 'Integrate SAST and Dependency Scanners (Semgrep & Snyk)' },
        { step: 4, type: 'phase', label: 'Execute Dynamic Security Testing & Container Scanning (ZAP, Trivy)', isLoopTarget: true },
        {
          step: 5,
          type: 'decision',
          label: 'Did build satisfy security quality gates?',
          noAction: 'Break pipeline build, alert engineer, and patch flaws.',
          noTargetStep: 4,
          yesAction: 'Approve artifact promotion to secure container registry.',
        },
        { step: 6, type: 'phase', label: 'Approve artifact promotion to secure container registry.' },
        { step: 7, type: 'phase', label: 'Implement Automated Vulnerability Remediation Workflows' },
        { step: 8, type: 'phase', label: 'Generate DevSecOps Pipeline Security Verification Report' },
        { step: 9, type: 'end', label: 'END' },
      ];
    }

    // 6. Network Monitoring and Anomaly Detection
    if (titleLower.includes('anomaly detection') || titleLower.includes('network monitoring')) {
      return [
        { step: 1, type: 'start', label: 'START' },
        { step: 2, type: 'phase', label: 'Deploy Suricata / Zeek Network Monitoring Sensor' },
        { step: 3, type: 'phase', label: 'Capture Baseline Traffic Flows & Profile Normal Usage' },
        { step: 4, type: 'phase', label: 'Execute Anomaly Detection & Signature Matching', isLoopTarget: true },
        {
          step: 5,
          type: 'decision',
          label: 'Is anomalous or malicious traffic pattern detected?',
          noAction: 'Adjust flow baseline thresholds & filter background noise.',
          noTargetStep: 4,
          yesAction: 'Extract packet telemetry & flag suspicious flow session.',
        },
        { step: 6, type: 'phase', label: 'Extract packet telemetry & flag suspicious flow session.' },
        { step: 7, type: 'phase', label: 'Conduct Deep Packet Inspection & Develop Mitigation Filters' },
        { step: 8, type: 'phase', label: 'Generate Network Traffic & Anomaly Detection Report' },
        { step: 9, type: 'end', label: 'END' },
      ];
    }

    // 7. Phishing Email Detection and Security Analysis
    if (titleLower.includes('phishing')) {
      return [
        { step: 1, type: 'start', label: 'START' },
        { step: 2, type: 'phase', label: 'Ingest Raw Email Corpus & Parse MIME / Header Attributes' },
        { step: 3, type: 'phase', label: 'Extract Threat Signals (SPF/DKIM/DMARC & Embedded URLs)' },
        { step: 4, type: 'phase', label: 'Run Heuristic Scoring & Machine Learning Classification', isLoopTarget: true },
        {
          step: 5,
          type: 'decision',
          label: 'Is suspicious phishing payload verified?',
          noAction: 'Refine feature extraction & retrain classifier weights.',
          noTargetStep: 4,
          yesAction: 'Flag malicious email, quarantine, and document IOCs.',
        },
        { step: 6, type: 'phase', label: 'Flag malicious email, quarantine, and document IOCs.' },
        { step: 7, type: 'phase', label: 'Author Defensive YARA Rules & User Security Advisory' },
        { step: 8, type: 'phase', label: 'Generate Phishing Threat Analysis & Defensive Strategy Report' },
        { step: 9, type: 'end', label: 'END' },
      ];
    }

    // 8. File Integrity Monitoring and Security Alerting
    if (titleLower.includes('file integrity') || titleLower.includes('integrity monitoring')) {
      return [
        { step: 1, type: 'start', label: 'START' },
        { step: 2, type: 'phase', label: 'Deploy Agent & Generate Cryptographic Baseline Hashes (SHA-256)' },
        { step: 3, type: 'phase', label: 'Configure Real-Time File System Event Auditing (Auditd / Inotify)' },
        { step: 4, type: 'phase', label: 'Execute Continuous Integrity Verification Against Baseline', isLoopTarget: true },
        {
          step: 5,
          type: 'decision',
          label: 'Was unauthorized critical file modification detected?',
          noAction: 'Update baseline database for authorized administrative changes.',
          noTargetStep: 4,
          yesAction: 'Trigger real-time security alert & capture forensic snapshot.',
        },
        { step: 6, type: 'phase', label: 'Trigger real-time security alert & capture forensic snapshot.' },
        { step: 7, type: 'phase', label: 'Execute Automated Incident Triage & Host Isolation Routine' },
        { step: 8, type: 'phase', label: 'Generate File Integrity Monitoring Security Report' },
        { step: 9, type: 'end', label: 'END' },
      ];
    }

    // 9. If raw workflow is provided from catalog or backend
    if (rawWorkflow && rawWorkflow.length > 0) {
      return rawWorkflow.map((item, idx) => ({
        step: item.step || idx + 1,
        type: item.type || (idx === 0 ? 'start' : idx === rawWorkflow.length - 1 ? 'end' : 'phase'),
        label: item.label || item.title || `Phase ${idx}`,
        isLoopTarget: item.is_loop_target || item.isLoopTarget,
        noAction: item.no_action || item.noAction,
        noTargetStep: item.no_target_step || item.noTargetStep,
        yesAction: item.yes_action || item.yesAction,
      }));
    }

    // 10. Fallback constructed from planPhases if available
    if (planPhases && planPhases.length > 0) {
      const nodes: WorkflowNode[] = [{ step: 1, type: 'start', label: 'START' }];
      let currentStep = 2;
      planPhases.forEach((p, pIdx) => {
        nodes.push({
          step: currentStep,
          type: 'phase',
          label: p.title || `Phase ${pIdx + 1}: Implementation`,
          isLoopTarget: pIdx === 2 || pIdx === planPhases.length - 2,
        });
        currentStep++;
      });
      nodes.push({
        step: currentStep,
        type: 'decision',
        label: 'Are phase validation & security requirements satisfied?',
        noAction: 'Review findings, tune configuration, and retest.',
        noTargetStep: currentStep - 2,
        yesAction: 'Document verified results and proceed.',
      });
      currentStep++;
      nodes.push({ step: currentStep, type: 'phase', label: 'Document verified results and proceed.' });
      currentStep++;
      nodes.push({ step: currentStep, type: 'phase', label: 'Generate Final Project Assessment Report' });
      currentStep++;
      nodes.push({ step: currentStep, type: 'end', label: 'END' });
      return nodes;
    }

    // 11. Generic clean fallback
    return [
      { step: 1, type: 'start', label: 'START' },
      { step: 2, type: 'phase', label: 'Prerequisites & Environment Setup' },
      { step: 3, type: 'phase', label: 'Core System Implementation & Configuration' },
      { step: 4, type: 'phase', label: 'Testing & Security Validation', isLoopTarget: true },
      {
        step: 5,
        type: 'decision',
        label: 'Are project requirements satisfied?',
        noAction: 'Review findings and perform further refinement.',
        noTargetStep: 4,
        yesAction: 'Document verified deliverables.',
      },
      { step: 6, type: 'phase', label: 'Document verified deliverables.' },
      { step: 7, type: 'phase', label: 'Generate Final Security Assessment Report' },
      { step: 8, type: 'end', label: 'END' },
    ];
  }, [projectTitle, rawWorkflow, planPhases]);

  // Layout calculations for responsive SVG rendering with dynamic text wrapping and heights
  const svgLayout = useMemo(() => {
    const centerX = 340;
    const boxWidth = 420;
    const diamondWidth = 360;
    const diamondHeight = 140;
    const startY = 36;
    const verticalGap = 36;

    let currentY = startY;
    const nodeCoords: Array<{
      node: WorkflowNode;
      x: number;
      y: number;
      width: number;
      height: number;
      centerY: number;
      bottomY: number;
      lines: string[];
    }> = [];

    workflowNodes.forEach((node) => {
      let height = 54;
      let width = boxWidth;
      let lines: string[] = [];

      if (node.type === 'start' || node.type === 'end') {
        height = 44;
        width = 200;
        lines = [node.label];
      } else if (node.type === 'decision') {
        height = diamondHeight;
        width = diamondWidth;
        // Wrap decision question to max 24 chars per line so it fits within inscribed diamond geometry
        lines = wrapText(node.label, 24);
      } else {
        // Wrap process box text to 36 chars per line
        lines = wrapText(node.label, 36);
        if (lines.length === 1) {
          height = 54;
        } else if (lines.length === 2) {
          height = 68;
        } else {
          height = Math.max(76, lines.length * 20 + 26);
        }
      }

      const x = centerX - width / 2;
      const y = currentY;
      const centerY = y + height / 2;
      const bottomY = y + height;

      nodeCoords.push({
        node,
        x,
        y,
        width,
        height,
        centerY,
        bottomY,
        lines,
      });

      currentY += height + verticalGap;
    });

    // Find decision node to compute remediation box and right margin
    const decisionCoord = nodeCoords.find((c) => c.node.type === 'decision');
    let noBoxX = 584;
    let noBoxWidth = 280;
    let noBoxHeight = 76;
    let noBoxY = 0;
    let noBoxLines: string[] = [];

    if (decisionCoord) {
      const decRightX = centerX + diamondWidth / 2;
      noBoxX = decRightX + 64;
      const noActionText = decisionCoord.node.noAction || 'Review findings and perform further hardening.';
      noBoxLines = wrapText(noActionText, 24);
      noBoxHeight = Math.max(74, noBoxLines.length * 19 + 36);
      noBoxY = decisionCoord.centerY - noBoxHeight / 2;
    }

    const svgWidth = Math.max(960, Math.ceil(noBoxX + noBoxWidth + 60));
    const totalHeight = currentY + 36;

    return {
      svgWidth,
      totalHeight,
      centerX,
      boxWidth,
      diamondWidth,
      diamondHeight,
      nodeCoords,
      decisionCoord,
      noBox: {
        x: noBoxX,
        y: noBoxY,
        width: noBoxWidth,
        height: noBoxHeight,
        lines: noBoxLines,
        centerX: noBoxX + noBoxWidth / 2,
      },
    };
  }, [workflowNodes]);

  const decisionCoord = svgLayout.decisionCoord;
  const targetStepNumber = decisionCoord?.node.noTargetStep || 7;
  const loopTargetCoord =
    svgLayout.nodeCoords.find((c) => c.node.step === targetStepNumber) ||
    svgLayout.nodeCoords.find((c) => c.node.isLoopTarget) ||
    svgLayout.nodeCoords[Math.max(1, svgLayout.nodeCoords.length - 4)];

  // Download Handlers
  const handleDownloadSVG = () => {
    const svgEl = svgRef.current;
    if (!svgEl) return;

    const serializer = new XMLSerializer();
    let source = serializer.serializeToString(svgEl);

    // Ensure valid XML namespaces
    if (!source.match(/^<svg[^>]+xmlns="http:\/\/www\.w3\.org\/2000\/svg"/)) {
      source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
    }
    if (!source.match(/^<svg[^>]+"http:\/\/www\.w3\.org\/1999\/xlink"/)) {
      source = source.replace(/^<svg/, '<svg xmlns:xlink="http://www.w3.org/1999/xlink"');
    }

    source = '<?xml version="1.0" encoding="utf-8" standalone="no"?>\r\n' + source;
    const blob = new Blob([source], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const sanitizedTitle = (projectTitle || 'Project').replace(/[^a-zA-Z0-9_-]/g, '_');
    const a = document.createElement('a');
    a.href = url;
    a.download = `${sanitizedTitle}_Flowchart.svg`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleDownloadPNG = () => {
    const svgEl = svgRef.current;
    if (!svgEl) return;

    const serializer = new XMLSerializer();
    let source = serializer.serializeToString(svgEl);

    if (!source.match(/^<svg[^>]+xmlns="http:\/\/www\.w3\.org\/2000\/svg"/)) {
      source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
    }
    if (!source.match(/^<svg[^>]+"http:\/\/www\.w3\.org\/1999\/xlink"/)) {
      source = source.replace(/^<svg/, '<svg xmlns:xlink="http://www.w3.org/1999/xlink"');
    }

    const svgBlob = new Blob([source], { type: 'image/svg+xml;charset=utf-8' });
    const blobURL = URL.createObjectURL(svgBlob);
    const image = new Image();

    image.onload = () => {
      const scale = 2; // 2x high resolution for retina display
      const canvas = document.createElement('canvas');
      canvas.width = svgLayout.svgWidth * scale;
      canvas.height = svgLayout.totalHeight * scale;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.fillStyle = '#FFFFFF';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(image, 0, 0, canvas.width, canvas.height);

        const sanitizedTitle = (projectTitle || 'Project').replace(/[^a-zA-Z0-9_-]/g, '_');
        const pngURL = canvas.toDataURL('image/png');
        const a = document.createElement('a');
        a.href = pngURL;
        a.download = `${sanitizedTitle}_Flowchart.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      }
      URL.revokeObjectURL(blobURL);
    };
    image.src = blobURL;
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(15, 23, 42, 0.78)',
        backdropFilter: 'blur(4px)',
        zIndex: 1100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px',
        animation: 'fadeIn 0.15s ease-out',
      }}
      onClick={onClose}
    >
      <div
        className="card"
        style={{
          maxWidth: '1040px',
          width: '100%',
          maxHeight: '94vh',
          display: 'flex',
          flexDirection: 'column',
          background: '#FFFFFF',
          borderRadius: '12px',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.35)',
          overflow: 'hidden',
          border: '1px solid #CBD5E1',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Top Bar */}
        <div
          style={{
            padding: '16px 24px',
            borderBottom: '1px solid #E2E8F0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '16px',
            background: '#F8FAFC',
            flexWrap: 'wrap',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: '240px', flex: '1 1 auto' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
              style={{
                fontSize: '12.5px',
                padding: '6px 12px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                borderColor: '#CBD5E1',
                color: '#334155',
                background: '#FFFFFF',
              }}
              title="Return to project recommendation card"
            >
              <ArrowLeft size={14} />
              <span>Back to Project</span>
            </button>

            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span
                  style={{
                    background: '#EFF6FF',
                    color: '#2563EB',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    fontSize: '11px',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    border: '1px solid #DBEAFE',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}
                >
                  <GitFork size={12} />
                  <span>Workflow Diagram</span>
                </span>
                {domain && (
                  <span
                    style={{
                      background: '#F1F5F9',
                      color: '#475569',
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '11px',
                      fontWeight: 600,
                    }}
                  >
                    {domain}
                  </span>
                )}
              </div>
              <h2
                style={{
                  fontSize: '16.5px',
                  fontWeight: 800,
                  color: '#0F172A',
                  margin: '4px 0 0',
                  lineHeight: 1.3,
                }}
              >
                {projectTitle}
              </h2>
            </div>
          </div>

          {/* Action Buttons: Download SVG, Download PNG, Close */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleDownloadSVG}
              style={{
                fontSize: '12px',
                padding: '6px 12px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                borderColor: '#CBD5E1',
                color: '#1E293B',
                background: '#FFFFFF',
                fontWeight: 600,
              }}
              title="Download vector SVG file"
            >
              <FileCode size={14} color="#2563EB" />
              <span>Download SVG</span>
            </button>

            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleDownloadPNG}
              style={{
                fontSize: '12px',
                padding: '6px 12px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                borderColor: '#CBD5E1',
                color: '#1E293B',
                background: '#FFFFFF',
                fontWeight: 600,
              }}
              title="Download high-resolution PNG image"
            >
              <ImageIcon size={14} color="#16A34A" />
              <span>Download PNG</span>
            </button>

            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
              style={{
                padding: '6px',
                borderRadius: '50%',
                border: '1px solid #CBD5E1',
                background: '#FFFFFF',
                color: '#64748B',
                cursor: 'pointer',
              }}
              title="Close workflow diagram"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Informational Sub-Banner: Strictly clarifies planned workflow */}
        <div
          style={{
            padding: '10px 24px',
            background: '#F0F9FF',
            borderBottom: '1px solid #BAE6FD',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '12px',
            color: '#0369A1',
            flexWrap: 'wrap',
            gap: '8px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldCheck size={15} color="#0284C7" />
            <span>
              <strong>Planned Implementation Sequence:</strong> Displays the technical milestones, validation gates, and iterative remediation loop for this project.
            </span>
          </div>
          <span style={{ fontSize: '11px', color: '#0284C7', fontWeight: 600 }}>Vector Flowchart • Scalable SVG</span>
        </div>

        {/* Modal Body: Displays the SVG diagram with crisp white background and responsive scroll */}
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            overflowX: 'auto',
            padding: '24px',
            background: '#F8FAFC',
            display: 'flex',
            justifyContent: 'center',
          }}
        >
          <div
            style={{
              width: '100%',
              maxWidth: `${svgLayout.svgWidth}px`,
              minWidth: '720px',
              background: '#FFFFFF',
              borderRadius: '8px',
              border: '1px solid #E2E8F0',
              padding: '20px 10px',
              boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)',
              margin: 'auto',
            }}
          >
            <svg
              ref={svgRef}
              viewBox={`0 0 ${svgLayout.svgWidth} ${svgLayout.totalHeight}`}
              width={svgLayout.svgWidth}
              height={svgLayout.totalHeight}
              style={{
                width: '100%',
                height: 'auto',
                display: 'block',
                margin: '0 auto',
                fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
              }}
            >
              <defs>
                {/* Blue Arrow Marker for standard downward flow */}
                <marker
                  id="flow-arrow-blue"
                  viewBox="0 0 10 10"
                  refX="9"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto"
                >
                  <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#2563EB" />
                </marker>

                {/* Red Arrow Marker for NO decision loop and remediation */}
                <marker
                  id="flow-arrow-red"
                  viewBox="0 0 10 10"
                  refX="9"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto"
                >
                  <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#DC2626" />
                </marker>

                {/* Green Arrow Marker for YES decision branch */}
                <marker
                  id="flow-arrow-green"
                  viewBox="0 0 10 10"
                  refX="9"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto"
                >
                  <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#16A34A" />
                </marker>

                {/* Linear Gradients for professional restrained styling */}
                <linearGradient id="start-end-grad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#EFF6FF" />
                  <stop offset="100%" stopColor="#DBEAFE" />
                </linearGradient>

                <linearGradient id="decision-grad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#FFFFFF" />
                  <stop offset="100%" stopColor="#F8FAFC" />
                </linearGradient>
              </defs>

              {/* 1. Downward Connecting Lines Between Consecutive Nodes */}
              {svgLayout.nodeCoords.map((coord, idx) => {
                if (idx >= svgLayout.nodeCoords.length - 1) return null;
                const nextCoord = svgLayout.nodeCoords[idx + 1];

                const isDecisionDown = coord.node.type === 'decision';
                const strokeColor = isDecisionDown ? '#16A34A' : '#2563EB';
                const strokeWidth = isDecisionDown ? '2.5' : '2';
                const markerUrl = isDecisionDown ? 'url(#flow-arrow-green)' : 'url(#flow-arrow-blue)';

                return (
                  <g key={`arrow-${idx}`}>
                    <line
                      x1={svgLayout.centerX}
                      y1={coord.bottomY}
                      x2={svgLayout.centerX}
                      y2={nextCoord.y - 1}
                      stroke={strokeColor}
                      strokeWidth={strokeWidth}
                      markerEnd={markerUrl}
                    />

                    {/* YES Branch Badge alongside the decision exit arrow */}
                    {isDecisionDown && (
                      <g>
                        <rect
                          x={svgLayout.centerX + 12}
                          y={coord.bottomY + 8}
                          width="46"
                          height="22"
                          rx="4"
                          fill="#DCFCE7"
                          stroke="#16A34A"
                          strokeWidth="1"
                        />
                        <text
                          x={svgLayout.centerX + 35}
                          y={coord.bottomY + 23}
                          textAnchor="middle"
                          fill="#15803D"
                          fontSize="11"
                          fontWeight="800"
                        >
                          YES
                        </text>
                      </g>
                    )}
                  </g>
                );
              })}

              {/* 2. Decision NO Branch, Adaptive Remediation Box & Feedback Loop */}
              {decisionCoord && (
                <g id="no-branch-loop">
                  {(() => {
                    const decRightX = svgLayout.centerX + svgLayout.diamondWidth / 2;
                    const decY = decisionCoord.centerY;
                    const { x: noBoxX, y: noBoxY, width: noBoxW, height: noBoxH, lines: noBoxLines, centerX: noBoxCenterX } = svgLayout.noBox;
                    const targetRightEdgeX = loopTargetCoord.x + loopTargetCoord.width;
                    const targetY = loopTargetCoord.centerY;

                    return (
                      <>
                        {/* Horizontal connector from diamond right vertex to NO box */}
                        <line
                          x1={decRightX}
                          y1={decY}
                          x2={noBoxX - 2}
                          y2={decY}
                          stroke="#DC2626"
                          strokeWidth="2"
                          markerEnd="url(#flow-arrow-red)"
                        />

                        {/* NO Branch Label outside diamond */}
                        <rect
                          x={decRightX + 12}
                          y={decY - 26}
                          width="40"
                          height="20"
                          rx="4"
                          fill="#FEE2E2"
                          stroke="#DC2626"
                          strokeWidth="1"
                        />
                        <text
                          x={decRightX + 32}
                          y={decY - 12}
                          textAnchor="middle"
                          fill="#B91C1C"
                          fontSize="11"
                          fontWeight="800"
                        >
                          NO
                        </text>

                        {/* Adaptive Remediation Process Box */}
                        <rect
                          x={noBoxX}
                          y={noBoxY}
                          width={noBoxW}
                          height={noBoxH}
                          rx="8"
                          fill="#FEF2F2"
                          stroke="#DC2626"
                          strokeWidth="1.75"
                          filter="drop-shadow(0 2px 4px rgba(220, 38, 38, 0.08))"
                        />

                        {/* Remediation Box Header Tag */}
                        <text
                          x={noBoxCenterX}
                          y={noBoxY + 20}
                          textAnchor="middle"
                          fill="#B91C1C"
                          fontSize="10.5"
                          fontWeight="800"
                          letterSpacing="0.8px"
                        >
                          REMEDIATION
                        </text>

                        {/* Remediation Wrapped Action Text */}
                        <text textAnchor="middle" fill="#991B1B" fontSize="12" fontWeight="600">
                          {noBoxLines.map((line, lIdx) => (
                            <tspan key={lIdx} x={noBoxCenterX} y={noBoxY + 38 + lIdx * 18}>
                              {line}
                            </tspan>
                          ))}
                        </text>

                        {/* Return loop line from top of NO box up to target hardening/validation phase */}
                        <path
                          d={`M ${noBoxCenterX} ${noBoxY} L ${noBoxCenterX} ${targetY} L ${targetRightEdgeX + 2} ${targetY}`}
                          fill="none"
                          stroke="#DC2626"
                          strokeWidth="2"
                          strokeDasharray="5,4"
                          markerEnd="url(#flow-arrow-red)"
                        />

                        {/* Reconnecting Loop Label badge in clear space */}
                        <g>
                          <rect
                            x={noBoxCenterX - 74}
                            y={(noBoxY + targetY) / 2 - 12}
                            width="148"
                            height="24"
                            rx="4"
                            fill="#FFFFFF"
                            stroke="#EF4444"
                            strokeWidth="1"
                            filter="drop-shadow(0 1px 2px rgba(239, 68, 68, 0.12))"
                          />
                          <text
                            x={noBoxCenterX}
                            y={(noBoxY + targetY) / 2 + 4.5}
                            textAnchor="middle"
                            fill="#DC2626"
                            fontSize="10.5"
                            fontWeight="700"
                          >
                            Iterative Remediation Loop
                          </text>
                        </g>
                      </>
                    );
                  })()}
                </g>
              )}

              {/* 3. Render Workflow Nodes (Boxes, Diamonds, Start/End) */}
              {svgLayout.nodeCoords.map((coord, idx) => {
                const { node, x, y, width, height, centerY, lines } = coord;

                // Start or End Node
                if (node.type === 'start' || node.type === 'end') {
                  return (
                    <g key={`node-${idx}`}>
                      <rect
                        x={x}
                        y={y}
                        width={width}
                        height={height}
                        rx="22"
                        fill="url(#start-end-grad)"
                        stroke="#2563EB"
                        strokeWidth="2"
                        filter="drop-shadow(0 1px 2px rgba(37, 99, 235, 0.15))"
                      />
                      <text
                        x={svgLayout.centerX}
                        y={centerY + 4.5}
                        textAnchor="middle"
                        fill="#1D4ED8"
                        fontSize="13"
                        fontWeight="800"
                        letterSpacing="1.2px"
                      >
                        {node.label}
                      </text>
                    </g>
                  );
                }

                // Diamond Decision Node: Fully contains wrapped text with zero overflow
                if (node.type === 'decision') {
                  const halfW = width / 2;
                  const halfH = height / 2;
                  const topPt = `${svgLayout.centerX},${centerY - halfH}`;
                  const rightPt = `${svgLayout.centerX + halfW},${centerY}`;
                  const bottomPt = `${svgLayout.centerX},${centerY + halfH}`;
                  const leftPt = `${svgLayout.centerX - halfW},${centerY}`;

                  return (
                    <g key={`node-${idx}`}>
                      <polygon
                        points={`${topPt} ${rightPt} ${bottomPt} ${leftPt}`}
                        fill="url(#decision-grad)"
                        stroke="#2563EB"
                        strokeWidth="2.5"
                        filter="drop-shadow(0 2px 6px rgba(37, 99, 235, 0.12))"
                      />
                      {/* Decision Header */}
                      <text
                        x={svgLayout.centerX}
                        y={centerY - 26}
                        textAnchor="middle"
                        fill="#2563EB"
                        fontSize="11"
                        fontWeight="800"
                        letterSpacing="1.2px"
                      >
                        DECISION
                      </text>
                      {/* Decision Question Wrapped Lines */}
                      <text textAnchor="middle" fill="#0F172A" fontSize="12.5" fontWeight="700">
                        {lines.length === 1 && (
                          <tspan x={svgLayout.centerX} y={centerY + 8}>
                            {lines[0]}
                          </tspan>
                        )}
                        {lines.length === 2 && (
                          <>
                            <tspan x={svgLayout.centerX} y={centerY - 2}>
                              {lines[0]}
                            </tspan>
                            <tspan x={svgLayout.centerX} y={centerY + 18}>
                              {lines[1]}
                            </tspan>
                          </>
                        )}
                        {lines.length >= 3 && (
                          <>
                            <tspan x={svgLayout.centerX} y={centerY - 6}>
                              {lines[0]}
                            </tspan>
                            <tspan x={svgLayout.centerX} y={centerY + 12}>
                              {lines[1]}
                            </tspan>
                            <tspan x={svgLayout.centerX} y={centerY + 30}>
                              {lines[2]}
                            </tspan>
                          </>
                        )}
                      </text>
                    </g>
                  );
                }

                // Rounded Rectangular Process Box: Dynamically sized with wrapped text lines
                const isTarget = node.isLoopTarget;
                const lineHeight = 19;
                const firstLineY = centerY - ((lines.length - 1) * lineHeight) / 2 + 4.5;

                return (
                  <g key={`node-${idx}`}>
                    <rect
                      x={x}
                      y={y}
                      width={width}
                      height={height}
                      rx="8"
                      fill="#FFFFFF"
                      stroke={isTarget ? '#2563EB' : '#3B82F6'}
                      strokeWidth={isTarget ? '2' : '1.5'}
                      filter="drop-shadow(0 1px 3px rgba(0, 0, 0, 0.05))"
                    />

                    {/* Step number marker badge on left inside box */}
                    <rect
                      x={x + 14}
                      y={centerY - 12}
                      width="24"
                      height="24"
                      rx="6"
                      fill="#EFF6FF"
                      stroke="#DBEAFE"
                      strokeWidth="1"
                    />
                    <text
                      x={x + 26}
                      y={centerY + 4}
                      textAnchor="middle"
                      fill="#2563EB"
                      fontSize="11"
                      fontWeight="800"
                    >
                      {node.step}
                    </text>

                    {/* Process Label Text with automatic multi-line wrapping */}
                    <text
                      textAnchor="middle"
                      fill="#0F172A"
                      fontSize={lines.length > 2 ? '12' : '12.5'}
                      fontWeight="600"
                    >
                      {lines.map((line, lIdx) => (
                        <tspan key={lIdx} x={svgLayout.centerX + 12} y={firstLineY + lIdx * lineHeight}>
                          {line}
                        </tspan>
                      ))}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>
        </div>

        {/* Modal Bottom Bar with Close and Download Buttons */}
        <div
          style={{
            padding: '14px 24px',
            borderTop: '1px solid #E2E8F0',
            background: '#F8FAFC',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '12px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: '#64748B' }}>
            <AlertCircle size={14} />
            <span>Preserves selected role and project recommendation upon returning.</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleDownloadSVG}
              style={{
                fontSize: '12px',
                padding: '7px 14px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                borderColor: '#CBD5E1',
                color: '#1E293B',
                background: '#FFFFFF',
                fontWeight: 600,
              }}
            >
              <Download size={14} />
              <span>Download SVG</span>
            </button>

            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleDownloadPNG}
              style={{
                fontSize: '12px',
                padding: '7px 14px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                borderColor: '#CBD5E1',
                color: '#1E293B',
                background: '#FFFFFF',
                fontWeight: 600,
              }}
            >
              <ImageIcon size={14} />
              <span>Download PNG</span>
            </button>

            <button
              type="button"
              className="btn btn-primary"
              onClick={onClose}
              style={{
                fontSize: '12.5px',
                padding: '7px 18px',
                fontWeight: 700,
              }}
            >
              Back to Project
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
