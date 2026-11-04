import React, { useState, useEffect } from 'react';
import { Sidebar, NavView } from './components/Sidebar';
import { TopNav } from './components/TopNav';
import { DashboardView } from './components/DashboardView';
import { JobSelectionView } from './components/JobSelectionView';
import { ResumeUpload } from './components/ResumeUpload';
import { AnalysisResults } from './components/AnalysisResults';
import { ImprovementView } from './components/ImprovementView';
import { RescoreComparison } from './components/RescoreComparison';
import { HistoryView, HistoryItem } from './components/HistoryView';
import { SettingsView } from './components/SettingsView';
import { TemplateGalleryView } from './components/TemplateGalleryView';
import { ProjectTrackingDashboard } from './components/ProjectTrackingDashboard';
import {
  fetchRoles,
  fetchHealth,
  analyzeResume,
  improveResume,
  acceptAndRescore,
} from './api';
import {
  JobRole,
  AnalysisResponse,
  ImprovementResponse,
  RescoreResponse,
} from './types';
import { AlertCircle, ArrowLeft } from 'lucide-react';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<NavView>('dashboard');
  const [roles, setRoles] = useState<JobRole[]>([]);
  const [selectedRole, setSelectedRole] = useState<JobRole | null>(null);
  const [healthData, setHealthData] = useState<any>(null);

  const [isRolesLoading, setIsRolesLoading] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isImproving, setIsImproving] = useState(false);
  const [isRescoring, setIsRescoring] = useState(false);

  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [improvementResult, setImprovementResult] = useState<ImprovementResponse | null>(null);
  const [rescoreResult, setRescoreResult] = useState<RescoreResponse | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [rolesError, setRolesError] = useState<string | null>(null);

  // Load system health and cybersecurity roles on startup
  const loadInitialData = async () => {
    try {
      setIsRolesLoading(true);
      setRolesError(null);
      const [rolesList, health] = await Promise.all([
        fetchRoles(),
        fetchHealth().catch(() => null),
      ]);
      setRoles(rolesList);
      setHealthData(health);
      if (rolesList.length > 0 && !selectedRole) {
        // Default select Role 1 (Ethical Hacker) or first
        const defaultRole = rolesList.find((r) => r.role_id === 1) || rolesList[0];
        setSelectedRole(defaultRole);
      }
    } catch (err: any) {
      const msg = err.message || 'Failed to connect to FUTRSEC backend.';
      setRolesError(msg);
      setErrorMessage(msg);
    } finally {
      setIsRolesLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  // Handle Resume Analysis
  const handleAnalyze = async (file: File) => {
    if (!selectedRole) {
      setErrorMessage('Please select a target cybersecurity role first.');
      setCurrentView('jobs');
      return;
    }
    try {
      setIsAnalyzing(true);
      setErrorMessage(null);
      const result = await analyzeResume(file, selectedRole.role_id);
      setAnalysisResult(result);
      setImprovementResult(null);
      setRescoreResult(null);

      // Record to session history
      const historyRecord: HistoryItem = {
        id: result.analysis_id,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        analysis: result,
      };
      setHistory((prev) => [historyRecord, ...prev]);

      fetchHealth().then(setHealthData).catch(() => null);
    } catch (err: any) {
      setErrorMessage(err.message || 'Error occurred during resume analysis.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Handle Resume Improvement (Round Robin Generation & Immediate Re-scoring)
  const handleTriggerImprovement = async (attemptNumber: number = 1, notes?: string) => {
    if (!analysisResult) return;
    try {
      setIsImproving(true);
      setErrorMessage(null);
      const result = await improveResume(analysisResult.analysis_id, attemptNumber, notes);
      setImprovementResult(result);
      fetchHealth().then(setHealthData).catch(() => null);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to generate improved resume.');
    } finally {
      setIsImproving(false);
    }
  };

  // Handle Acceptance and Re-Scoring
  const handleAcceptAndRescore = async () => {
    if (!analysisResult) return;
    try {
      setIsRescoring(true);
      setErrorMessage(null);
      const result = await acceptAndRescore(analysisResult.analysis_id);
      setRescoreResult(result);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to recalculate score.');
    } finally {
      setIsRescoring(false);
    }
  };

  const handleStartNew = () => {
    setAnalysisResult(null);
    setImprovementResult(null);
    setRescoreResult(null);
    setErrorMessage(null);
    setCurrentView('analyze');
  };

  const handleSelectHistoryItem = (item: HistoryItem) => {
    setAnalysisResult(item.analysis);
    const matchedRole = roles.find((r) => r.role_id === item.analysis.role_id);
    if (matchedRole) setSelectedRole(matchedRole);
    setImprovementResult(null);
    setRescoreResult(null);
    setCurrentView('analyze');
  };

  const latestScore = history.length > 0 ? history[0].analysis.score_result.final_score : null;

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-app)' }}>
      {/* Enterprise Sidebar Navigation */}
      <Sidebar
        currentView={currentView}
        onNavigate={(view) => {
          setErrorMessage(null);
          setCurrentView(view);
        }}
        rolesCount={roles.length}
        hasAnalysis={!!analysisResult}
        hasImprovement={!!improvementResult}
        historyCount={history.length}
        selectedRoleTitle={selectedRole?.role_name}
      />

      {/* Main Content Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <TopNav
          currentView={currentView}
          selectedRoleTitle={selectedRole?.role_name}
          rolesCount={roles.length}
          dbStatus={healthData?.database?.status || (roles.length > 0 ? 'healthy' : 'disconnected')}
        />

        <main style={{ padding: '28px 32px', flex: 1, maxWidth: '1280px', width: '100%', margin: '0 auto' }}>
          {/* Global Error Banner */}
          {errorMessage && (
            <div
              className="card"
              style={{
                padding: '12px 18px',
                background: 'var(--rose-subtle)',
                borderColor: 'var(--rose-border)',
                color: 'var(--rose-danger)',
                fontSize: '13.5px',
                marginBottom: '20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '12px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertCircle size={16} />
                <span>{errorMessage}</span>
              </div>
              <button
                onClick={() => setErrorMessage(null)}
                style={{ background: 'none', border: 'none', color: 'var(--rose-danger)', cursor: 'pointer', fontSize: '15px' }}
                aria-label="Dismiss error"
              >
                ✕
              </button>
            </div>
          )}

          {/* View Routing */}
          {currentView === 'dashboard' && (
            <DashboardView
              rolesCount={roles.length}
              selectedRole={selectedRole}
              historyCount={history.length}
              latestScore={latestScore}
              onNavigate={setCurrentView}
              onSelectRole={setSelectedRole}
              sampleRoles={roles}
            />
          )}

          {currentView === 'jobs' && (
            <JobSelectionView
              roles={roles}
              selectedRole={selectedRole}
              onSelectRole={setSelectedRole}
              onProceedToAnalyze={() => setCurrentView('analyze')}
              isLoading={isRolesLoading}
              onRetry={loadInitialData}
              error={rolesError}
            />
          )}

          {currentView === 'analyze' && (
            <div>
              {analysisResult ? (
                <div>
                  <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <button className="btn btn-secondary" onClick={() => setAnalysisResult(null)}>
                      <ArrowLeft size={15} />
                      <span>Upload Another Resume</span>
                    </button>
                    <div style={{ fontSize: '13px', color: 'var(--text-dim)' }}>
                      Evaluating against: <strong style={{ color: 'var(--primary)' }}>{analysisResult.role_name}</strong>
                    </div>
                  </div>
                  <AnalysisResults
                    analysis={analysisResult}
                    onTriggerImprovement={handleTriggerImprovement}
                    isImproving={isImproving}
                    onStartNew={handleStartNew}
                    initialImprovement={improvementResult}
                  />
                </div>
              ) : (
                <ResumeUpload
                  onAnalyze={handleAnalyze}
                  isAnalyzing={isAnalyzing}
                  selectedRole={selectedRole}
                  onNavigateToJobs={() => setCurrentView('jobs')}
                />
              )}
            </div>
          )}

          {currentView === 'improvement' && (
            <div>
              {rescoreResult && improvementResult ? (
                <div>
                  <div style={{ marginBottom: '16px' }}>
                    <button className="btn btn-secondary" onClick={() => setRescoreResult(null)}>
                      <ArrowLeft size={15} />
                      <span>Back to Template Preview</span>
                    </button>
                  </div>
                  <RescoreComparison
                    rescore={rescoreResult}
                    roleName={selectedRole?.role_name || 'Cybersecurity Role'}
                    docxUrl={improvementResult.documents.docx_url}
                    pdfUrl={improvementResult.documents.pdf_url}
                    onStartNew={handleStartNew}
                  />
                </div>
              ) : improvementResult ? (
                <ImprovementView
                  improvement={improvementResult}
                  onAcceptAndRescore={handleAcceptAndRescore}
                  isRescoring={isRescoring}
                />
              ) : (
                <div className="card" style={{ padding: '48px 24px', textAlign: 'center' }}>
                  <h3 style={{ fontSize: '17px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '8px' }}>
                    No Active Resume Improvement Job
                  </h3>
                  <p style={{ fontSize: '13.5px', color: 'var(--text-muted)', marginBottom: '18px', maxWidth: '520px', margin: '0 auto 18px' }}>
                    Evaluate your resume against a target role. If your score is below 80, the Round Robin resume generator will automatically assign a template and optimize your content.
                  </p>
                  <button className="btn btn-primary" onClick={() => setCurrentView('analyze')}>
                    <span>Go to Resume Analysis</span>
                  </button>
                </div>
              )}
            </div>
          )}

          {currentView === 'tracking' && (
            <ProjectTrackingDashboard
              selectedRole={selectedRole}
              candidateId={analysisResult?.parsed_resume?.contact_info?.email || 'candidate_primary'}
              candidateName={analysisResult?.parsed_resume?.candidate_name || 'Cybersecurity Candidate'}
              candidateEmail={analysisResult?.parsed_resume?.contact_info?.email}
              onNavigateToAnalyze={() => setCurrentView('analyze')}
            />
          )}

          {currentView === 'history' && (
            <HistoryView
              history={history}
              onSelectHistory={handleSelectHistoryItem}
              onStartNew={handleStartNew}
            />
          )}

          {currentView === 'templates' && (
            <TemplateGalleryView onBackToDashboard={() => setCurrentView('dashboard')} />
          )}

          {currentView === 'settings' && (
            <SettingsView
              healthData={healthData}
              rolesCount={roles.length}
              onRefreshHealth={() => fetchHealth().then(setHealthData).catch(() => null)}
            />
          )}
        </main>
      </div>
    </div>
  );
};
