import React, { useState, useRef } from 'react';
import {
  UploadCloud,
  FileText,
  AlertCircle,
  CheckCircle2,
  RefreshCw,
  X,
  Shield,
  ArrowRight,
} from 'lucide-react';
import { JobRole } from '../types';
import { LoadingOverlay } from './LoadingOverlay';

interface ResumeUploadProps {
  onAnalyze: (file: File) => void;
  isAnalyzing: boolean;
  selectedRole: JobRole | null;
  onNavigateToJobs: () => void;
}

export const ResumeUpload: React.FC<ResumeUploadProps> = ({
  onAnalyze,
  isAnalyzing,
  selectedRole,
  onNavigateToJobs,
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateAndSetFile = (file: File) => {
    setErrorMsg(null);
    const fileName = file.name || '';
    const lastDotIndex = fileName.lastIndexOf('.');
    const ext = lastDotIndex !== -1 ? fileName.slice(lastDotIndex + 1).toLowerCase() : '';

    if (!ext || !['pdf', 'docx'].includes(ext)) {
      if (ext === 'doc') {
        setErrorMsg('Legacy .doc format is not supported. Supported formats: PDF and DOCX only. Please convert your file to .docx or .pdf.');
      } else {
        setErrorMsg(`Unsupported file format "${ext ? `.${ext}` : 'unknown'}". Supported formats: PDF and DOCX only.`);
      }
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      return;
    }

    if (file.size === 0) {
      setErrorMsg('Selected file is empty (0 bytes). Supported formats: PDF and DOCX only.');
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setErrorMsg(`File size (${(file.size / (1024 * 1024)).toFixed(1)}MB) exceeds 10MB limit.`);
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      return;
    }

    setSelectedFile(file);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleRemoveFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedFile(null);
    setErrorMsg(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = () => {
    if (!selectedFile) {
      setErrorMsg('Please select a resume file (PDF or DOCX) to evaluate.');
      return;
    }
    if (!selectedRole) {
      setErrorMsg('Please select a target cybersecurity role before beginning evaluation.');
      return;
    }
    if (selectedFile.size === 0) {
      setErrorMsg('The selected resume file is empty (0 bytes). Please upload a valid document.');
      return;
    }
    setErrorMsg(null);
    onAnalyze(selectedFile);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Target Role Status Card */}
      <div
        className="card"
        style={{
          padding: '20px 24px',
          borderLeft: `4px solid ${selectedRole ? 'var(--primary)' : 'var(--amber-warn)'}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '14px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: 'var(--radius-sm)',
              background: selectedRole ? 'var(--primary-subtle)' : 'var(--amber-subtle)',
              color: selectedRole ? 'var(--primary)' : 'var(--amber-warn)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Shield size={20} />
          </div>
          <div>
            <div style={{ fontSize: '11.5px', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase' }}>
              Evaluation Benchmark
            </div>
            <div style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-main)', marginTop: '2px' }}>
              {selectedRole ? (
                <span>Target Role: <strong style={{ color: 'var(--primary)' }}>{selectedRole.role_name}</strong></span>
              ) : (
                <span style={{ color: 'var(--amber-warn)' }}>No Cybersecurity Role Selected</span>
              )}
            </div>
          </div>
        </div>

        <button
          className="btn btn-secondary"
          onClick={onNavigateToJobs}
          style={{ fontSize: '13px' }}
        >
          <span>{selectedRole ? 'Change Target Role' : 'Select Target Role from 74 Roles'}</span>
          <ArrowRight size={14} />
        </button>
      </div>

      {/* Main Upload Card */}
      <div className="card" style={{ padding: '28px' }}>
        <div style={{ marginBottom: '18px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <UploadCloud size={20} color="var(--primary)" />
            Upload Candidate Resume
          </h2>
          <p style={{ fontSize: '13.5px', color: 'var(--text-muted)', marginTop: '2px' }}>
            Upload your resume document in PDF or DOCX format for deterministic ATS evaluation. Supported formats: PDF and DOCX only.
          </p>
        </div>

        {/* Drop Zone */}
        <div
          id="resume-drop-zone"
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          style={{
            border: `2px dashed ${dragActive ? 'var(--primary)' : selectedFile ? 'var(--emerald-success)' : 'var(--border-strong)'}`,
            borderRadius: 'var(--radius-md)',
            padding: '44px 20px',
            textAlign: 'center',
            background: dragActive ? 'var(--primary-subtle)' : selectedFile ? 'var(--emerald-subtle)' : 'var(--bg-subtle)',
            cursor: isAnalyzing ? 'not-allowed' : 'pointer',
            transition: 'all var(--transition-fast)',
          }}
        >
          <input
            ref={fileInputRef}
            id="resume-file-input"
            type="file"
            accept=".pdf,.docx"
            onChange={handleChange}
            style={{ display: 'none' }}
            disabled={isAnalyzing}
          />

          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: '56px',
                height: '56px',
                borderRadius: '50%',
                background: selectedFile ? 'var(--emerald-subtle)' : 'var(--bg-card)',
                color: selectedFile ? 'var(--emerald-success)' : 'var(--primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: 'var(--shadow-sm)',
              }}
            >
              {selectedFile ? (
                <CheckCircle2 size={30} color="var(--emerald-success)" />
              ) : (
                <FileText size={30} color="var(--primary)" />
              )}
            </div>

            <div>
              <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-main)' }}>
                {selectedFile ? selectedFile.name : 'Drag and drop your resume here, or browse files'}
              </div>
              <div style={{ fontSize: '12.5px', color: 'var(--text-dim)', marginTop: '4px' }}>
                {selectedFile
                  ? `${(selectedFile.size / 1024).toFixed(0)} KB • Ready for ATS evaluation`
                  : 'Supported formats: PDF and DOCX only. (Maximum file size: 10MB)'}
              </div>
            </div>

            {selectedFile && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '6px' }}>
                <span className="badge badge-emerald">Ready for Analysis</span>
                <button
                  onClick={handleRemoveFile}
                  className="btn btn-secondary"
                  style={{ padding: '4px 8px', fontSize: '11px', height: '24px' }}
                  title="Remove file"
                >
                  <X size={12} />
                  <span>Remove</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Error Alert */}
        {errorMsg && (
          <div
            style={{
              marginTop: '16px',
              padding: '12px 16px',
              borderRadius: 'var(--radius-sm)',
              background: 'var(--rose-subtle)',
              border: '1px solid var(--rose-border)',
              color: 'var(--rose-danger)',
              fontSize: '13px',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
            }}
          >
            <AlertCircle size={16} />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Security & Validation Notice */}
        <div
          style={{
            marginTop: '20px',
            padding: '12px 16px',
            background: 'var(--bg-subtle)',
            borderRadius: 'var(--radius-sm)',
            fontSize: '12.5px',
            color: 'var(--text-dim)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '8px',
          }}
        >
          <span>
            🛡️ Content Validation: Magic-byte inspection, prompt-injection defense, and strict credential redaction applied automatically.
          </span>
          <span className="badge badge-subtle">10MB Limit</span>
        </div>

        {/* Submit Action */}
        <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
          <button
            id="start-analysis-submit-btn"
            className="btn btn-primary"
            onClick={handleSubmit}
            disabled={!selectedFile || !selectedRole || isAnalyzing}
            style={{ padding: '12px 28px', fontSize: '14.5px' }}
          >
            {isAnalyzing ? (
              <>
                <div
                  className="loading-circular-spinner"
                  style={{
                    width: '16px',
                    height: '16px',
                    borderRadius: '50%',
                    border: '2px solid rgba(255, 255, 255, 0.3)',
                    borderTopColor: '#FFFFFF',
                    animation: 'futrsecSpin 0.8s linear infinite',
                  }}
                />
                <span>Analyzing Resume...</span>
              </>
            ) : (
              <>
                <CheckCircle2 size={17} />
                <span>
                  {selectedRole
                    ? `Evaluate Against ${selectedRole.role_name}`
                    : 'Select a Role to Begin Analysis'}
                </span>
                <ArrowRight size={15} />
              </>
            )}
          </button>
        </div>
      </div>

      {/* Enterprise SaaS Loading Experience */}
      <LoadingOverlay
        isOpen={isAnalyzing}
        operationType="analyze_resume"
      />
    </div>
  );
};

