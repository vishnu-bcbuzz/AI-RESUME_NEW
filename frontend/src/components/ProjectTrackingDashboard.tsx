import React, { useState, useEffect, useMemo } from 'react';
import {
  Shield,
  CheckCircle2,
  Clock,
  AlertTriangle,
  FileText,
  Github,
  Sparkles,
  Award,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  ExternalLink,
  PlusCircle,
  XCircle,
  CheckSquare,
  Square,
  Search,
  BookOpen,
  ArrowRight,
  TrendingUp,
  Trash2,
  UserCheck,
  Send,
  HelpCircle,
} from 'lucide-react';
import {
  CandidateProject,
  ProjectMilestone,
  ProjectRecommendation,
  TrackingDashboardStats,
  ProjectTrackingStatus,
  JobRole,
} from '../types';
import {
  fetchTrackingDashboard,
  fetchProjectRecommendations,
  assignProject,
  rejectProjectRecommendation,
  deleteCandidateProject,
  updateCandidateProjectStatus,
  updateTaskProgress,
  submitMilestoneEvidence,
  reviewMilestone,
  aiVerifyMilestone,
} from '../api';

interface ProjectTrackingDashboardProps {
  selectedRole: JobRole | null;
  candidateId?: string;
  candidateName?: string;
  candidateEmail?: string;
  onNavigateToAnalyze?: () => void;
}

export const ProjectTrackingDashboard: React.FC<ProjectTrackingDashboardProps> = ({
  selectedRole,
  candidateId = 'candidate_primary',
  candidateName = 'Cybersecurity Candidate',
  candidateEmail,
  onNavigateToAnalyze,
}) => {
  const [activeTab, setActiveTab] = useState<'tracking' | 'explore'>('tracking');
  const [dashboardStats, setDashboardStats] = useState<TrackingDashboardStats | null>(null);
  const [recommendations, setRecommendations] = useState<ProjectRecommendation[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Filter state for assigned projects
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  // Expanded project & milestone cards
  const [expandedProjects, setExpandedProjects] = useState<Record<string, boolean>>({});
  const [expandedMilestones, setExpandedMilestones] = useState<Record<string, boolean>>({});

  // Evidence submission modal state
  const [evidenceModal, setEvidenceModal] = useState<{
    isOpen: boolean;
    projectId: string;
    milestoneId: string;
    milestoneTitle: string;
    githubUrl: string;
    reportText: string;
    notes: string;
  }>({
    isOpen: false,
    projectId: '',
    milestoneId: '',
    milestoneTitle: '',
    githubUrl: '',
    reportText: '',
    notes: '',
  });

  // Admin / Manual Review modal state
  const [reviewModal, setReviewModal] = useState<{
    isOpen: boolean;
    projectId: string;
    milestoneId: string;
    milestoneTitle: string;
    verdict: 'approved' | 'revision_required' | 'rejected';
    score: number;
    feedback: string;
    revisionInstructions: string;
    reviewerName: string;
  }>({
    isOpen: false,
    projectId: '',
    milestoneId: '',
    milestoneTitle: '',
    verdict: 'approved',
    score: 90,
    feedback: '',
    revisionInstructions: '',
    reviewerName: 'Security Lead Auditor',
  });

  // Custom assignment deadline modal
  const [assignmentModal, setAssignmentModal] = useState<{
    isOpen: boolean;
    recommendation: ProjectRecommendation | null;
    deadlineDays: number;
  }>({
    isOpen: false,
    recommendation: null,
    deadlineDays: 30,
  });

  // Load dashboard & recommendations
  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      setErrorMessage(null);
      const stats = await fetchTrackingDashboard(candidateId);
      setDashboardStats(stats);

      // Auto-expand first project if available
      if (stats.projects && stats.projects.length > 0) {
        setExpandedProjects((prev) => ({
          ...prev,
          [stats.projects[0].id]: true,
        }));
      }

      // Fetch recommendations tailored to role
      const roleName = selectedRole?.role_name || 'Ethical Hacker';
      const recs = await fetchProjectRecommendations(roleName);
      setRecommendations(recs);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to load project tracking data.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, [candidateId, selectedRole?.role_name]);

  // Flash message helper
  const showToast = (msg: string, isError = false) => {
    if (isError) {
      setErrorMessage(msg);
      setTimeout(() => setErrorMessage(null), 6000);
    } else {
      setSuccessMessage(msg);
      setTimeout(() => setSuccessMessage(null), 4000);
    }
  };

  // Toggle project expand
  const toggleProject = (projectId: string) => {
    setExpandedProjects((prev) => ({
      ...prev,
      [projectId]: !prev[projectId],
    }));
  };

  // Toggle milestone expand
  const toggleMilestone = (milestoneId: string) => {
    setExpandedMilestones((prev) => ({
      ...prev,
      [milestoneId]: !prev[milestoneId],
    }));
  };

  // 1. Task progress toggle
  const handleTaskToggle = async (
    projectId: string,
    milestoneId: string,
    taskId: string,
    currentStatus: boolean
  ) => {
    try {
      const res = await updateTaskProgress({
        candidate_project_id: projectId,
        milestone_id: milestoneId,
        task_id: taskId,
        is_completed: !currentStatus,
      });

      // Update in local state optimistically
      setDashboardStats((prev) => {
        if (!prev) return prev;
        const updatedProjects = prev.projects.map((proj) => {
          if (proj.id !== projectId) return proj;
          const updatedMilestones = (proj.milestones || []).map((m) => {
            if (m.id !== milestoneId) return m;
            const updatedTasks = m.tasks.map((t) =>
              t.id === taskId ? { ...t, is_completed: !currentStatus } : t
            );
            return {
              ...m,
              tasks: updatedTasks,
              completed_tasks_count: res.milestone_completed_tasks,
              status: res.milestone_status as ProjectTrackingStatus,
            };
          });
          return {
            ...proj,
            milestones: updatedMilestones,
            completion_percentage: res.project_completion_percentage,
          };
        });
        return { ...prev, projects: updatedProjects };
      });
      showToast('Task status updated successfully.');
    } catch (err: any) {
      showToast(err.message || 'Failed to update task progress.', true);
    }
  };

  // 2. Submit milestone evidence
  const handleSubmitEvidence = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!evidenceModal.githubUrl.trim() && !evidenceModal.reportText.trim()) {
      showToast('Please provide a GitHub URL or a written report.', true);
      return;
    }

    try {
      setIsSubmitting(true);
      await submitMilestoneEvidence({
        candidate_project_id: evidenceModal.projectId,
        milestone_id: evidenceModal.milestoneId,
        github_url: evidenceModal.githubUrl.trim() || undefined,
        report_text: evidenceModal.reportText.trim() || undefined,
        notes: evidenceModal.notes.trim() || undefined,
      });

      setEvidenceModal({
        isOpen: false,
        projectId: '',
        milestoneId: '',
        milestoneTitle: '',
        githubUrl: '',
        reportText: '',
        notes: '',
      });
      showToast('Evidence submitted successfully! Milestone status is now "Submitted".');
      await loadDashboardData();
    } catch (err: any) {
      showToast(err.message || 'Evidence submission failed.', true);
    } finally {
      setIsSubmitting(false);
    }
  };

  // 3. Automated AI Verification
  const handleAiVerify = async (projectId: string, milestoneId: string) => {
    try {
      setIsSubmitting(true);
      const result = await aiVerifyMilestone({
        candidate_project_id: projectId,
        milestone_id: milestoneId,
      });

      const verdict = result.verdict === 'approved' ? 'Approved & Completed' : 'Revision Required';
      showToast(`AI Verification Complete: ${verdict} (Score: ${result.score}/100)`);
      await loadDashboardData();
    } catch (err: any) {
      showToast(err.message || 'AI verification failed.', true);
    } finally {
      setIsSubmitting(false);
    }
  };

  // 4. Authorized/Admin Review
  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reviewModal.feedback.trim()) {
      showToast('Please provide evaluative feedback.', true);
      return;
    }

    try {
      setIsSubmitting(true);
      const res = await reviewMilestone({
        candidate_project_id: reviewModal.projectId,
        milestone_id: reviewModal.milestoneId,
        verdict: reviewModal.verdict,
        score: reviewModal.score,
        feedback: reviewModal.feedback.trim(),
        revision_instructions: reviewModal.revisionInstructions.trim() || undefined,
        reviewer_name: reviewModal.reviewerName.trim() || 'Security Administrator',
      });

      setReviewModal({
        isOpen: false,
        projectId: '',
        milestoneId: '',
        milestoneTitle: '',
        verdict: 'approved',
        score: 90,
        feedback: '',
        revisionInstructions: '',
        reviewerName: 'Security Lead Auditor',
      });

      if (res.is_project_fully_verified) {
        showToast('All milestones completed! Project is now verified and eligible for resume inclusion.');
      } else {
        showToast(`Review recorded: Milestone marked as ${res.milestone_status}.`);
      }
      await loadDashboardData();
    } catch (err: any) {
      showToast(err.message || 'Failed to submit review.', true);
    } finally {
      setIsSubmitting(false);
    }
  };

  // 5. Accept recommendation & assign project
  const handleAcceptProject = async () => {
    const rec = assignmentModal.recommendation;
    if (!rec) return;

    try {
      setIsSubmitting(true);
      await assignProject({
        candidate_id: candidateId,
        project_id: rec.project_id,
        role_name: selectedRole?.role_name || 'Cybersecurity Specialist',
        candidate_name: candidateName,
        candidate_email: candidateEmail,
        custom_deadline_days: assignmentModal.deadlineDays,
      });

      setAssignmentModal({ isOpen: false, recommendation: null, deadlineDays: 30 });
      setActiveTab('tracking');
      showToast(`Assigned "${rec.project_title}" with ${rec.total_phases} milestones!`);
      await loadDashboardData();
    } catch (err: any) {
      showToast(err.message || 'Failed to assign project.', true);
    } finally {
      setIsSubmitting(false);
    }
  };

  // 6. Reject project recommendation
  const handleRejectRecommendation = async (projectId: string) => {
    try {
      await rejectProjectRecommendation({
        candidate_id: candidateId,
        project_id: projectId,
        reason: 'Declined by candidate in tracker view',
      });
      setRecommendations((prev) => prev.filter((r) => r.project_id !== projectId));
      showToast('Project recommendation declined.');
    } catch (err: any) {
      showToast(err.message || 'Failed to reject recommendation.', true);
    }
  };

  // 7. Delete project assignment
  const handleDeleteProject = async (projectId: string, title: string) => {
    if (!window.confirm(`Are you sure you want to cancel and remove "${title}"? All submitted evidence will be removed.`)) {
      return;
    }
    try {
      await deleteCandidateProject(projectId);
      showToast(`Removed project assignment "${title}".`);
      await loadDashboardData();
    } catch (err: any) {
      showToast(err.message || 'Failed to remove project.', true);
    }
  };

  // Filter projects
  const filteredProjects = useMemo(() => {
    if (!dashboardStats?.projects) return [];
    if (statusFilter === 'ALL') return dashboardStats.projects;
    return dashboardStats.projects.filter((p) => p.status === statusFilter);
  }, [dashboardStats?.projects, statusFilter]);

  // Status badge styling helper
  const renderStatusBadge = (status: ProjectTrackingStatus) => {
    switch (status) {
      case 'Completed':
        return (
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '5px',
              padding: '3px 10px',
              borderRadius: 'var(--radius-full)',
              fontSize: '12px',
              fontWeight: 700,
              background: 'var(--emerald-subtle)',
              color: 'var(--emerald-success)',
              border: '1px solid var(--emerald-border)',
            }}
          >
            <CheckCircle2 size={13} />
            Completed
          </span>
        );
      case 'Revision Required':
        return (
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '5px',
              padding: '3px 10px',
              borderRadius: 'var(--radius-full)',
              fontSize: '12px',
              fontWeight: 700,
              background: 'var(--amber-subtle)',
              color: 'var(--amber-warn)',
              border: '1px solid var(--amber-border)',
            }}
          >
            <AlertTriangle size={13} />
            Revision Required
          </span>
        );
      case 'Under Review':
        return (
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '5px',
              padding: '3px 10px',
              borderRadius: 'var(--radius-full)',
              fontSize: '12px',
              fontWeight: 700,
              background: '#F3E8FF',
              color: '#7E22CE',
              border: '1px solid #D8B4FE',
            }}
          >
            <Clock size={13} />
            Under Review
          </span>
        );
      case 'Submitted':
        return (
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '5px',
              padding: '3px 10px',
              borderRadius: 'var(--radius-full)',
              fontSize: '12px',
              fontWeight: 700,
              background: '#E0F2FE',
              color: '#0369A1',
              border: '1px solid #BAE6FD',
            }}
          >
            <Send size={13} />
            Submitted
          </span>
        );
      case 'In Progress':
        return (
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '5px',
              padding: '3px 10px',
              borderRadius: 'var(--radius-full)',
              fontSize: '12px',
              fontWeight: 700,
              background: 'var(--primary-subtle)',
              color: 'var(--primary)',
              border: '1px solid var(--primary-border)',
            }}
          >
            <TrendingUp size={13} />
            In Progress
          </span>
        );
      default:
        return (
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '5px',
              padding: '3px 10px',
              borderRadius: 'var(--radius-full)',
              fontSize: '12px',
              fontWeight: 600,
              background: 'var(--bg-subtle)',
              color: 'var(--text-muted)',
              border: '1px solid var(--border-subtle)',
            }}
          >
            <Clock size={13} />
            Not Started
          </span>
        );
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Toast Messages */}
      {errorMessage && (
        <div
          className="card"
          style={{
            padding: '12px 18px',
            background: 'var(--rose-subtle)',
            borderColor: 'var(--rose-border)',
            color: 'var(--rose-danger)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '14px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <AlertTriangle size={18} />
            <span>{errorMessage}</span>
          </div>
          <button
            onClick={() => setErrorMessage(null)}
            style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer' }}
          >
            ✕
          </button>
        </div>
      )}

      {successMessage && (
        <div
          className="card"
          style={{
            padding: '12px 18px',
            background: 'var(--emerald-subtle)',
            borderColor: 'var(--emerald-border)',
            color: 'var(--emerald-success)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '14px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <CheckCircle2 size={18} />
            <span>{successMessage}</span>
          </div>
          <button
            onClick={() => setSuccessMessage(null)}
            style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer' }}
          >
            ✕
          </button>
        </div>
      )}

      {/* Top Banner & Header */}
      <div
        className="card"
        style={{
          padding: '28px 32px',
          background: 'linear-gradient(135deg, var(--bg-card) 0%, var(--bg-subtle) 100%)',
          borderLeft: '4px solid var(--primary)',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span className="badge badge-primary">PRACTICAL SKILL VERIFICATION</span>
              <span className="badge badge-emerald">Truthful ATS Integration</span>
              {selectedRole && (
                <span className="badge badge-slate" style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  Target: {selectedRole.role_name}
                </span>
              )}
            </div>
            <h1 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-main)', margin: '0 0 6px 0' }}>
              Project Completion Tracking System
            </h1>
            <p style={{ fontSize: '14px', color: 'var(--text-muted)', margin: 0, maxWidth: '720px', lineHeight: 1.5 }}>
              Track hands-on cybersecurity projects through structured milestones, deliverable evidence (GitHub repos & reports),
              and verification. Only completed, verified projects are integrated into your ATS resume.
            </p>
          </div>

          <button
            className="btn btn-secondary"
            onClick={loadDashboardData}
            disabled={isLoading}
            style={{ display: 'flex', alignItems: 'center', gap: '7px' }}
          >
            <RefreshCw size={15} className={isLoading ? 'animate-spin' : ''} />
            <span>Refresh Tracker</span>
          </button>
        </div>

        {/* Tab Switcher */}
        <div
          style={{
            display: 'flex',
            gap: '8px',
            borderBottom: '1px solid var(--border-subtle)',
            paddingTop: '16px',
          }}
        >
          <button
            onClick={() => setActiveTab('tracking')}
            style={{
              padding: '10px 18px',
              fontSize: '14px',
              fontWeight: 600,
              background: 'none',
              border: 'none',
              borderBottom: activeTab === 'tracking' ? '3px solid var(--primary)' : '3px solid transparent',
              color: activeTab === 'tracking' ? 'var(--primary)' : 'var(--text-muted)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <CheckSquare size={16} />
            <span>Assigned Projects & Milestones ({dashboardStats?.total_assigned || 0})</span>
          </button>

          <button
            onClick={() => setActiveTab('explore')}
            style={{
              padding: '10px 18px',
              fontSize: '14px',
              fontWeight: 600,
              background: 'none',
              border: 'none',
              borderBottom: activeTab === 'explore' ? '3px solid var(--primary)' : '3px solid transparent',
              color: activeTab === 'explore' ? 'var(--primary)' : 'var(--text-muted)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <Sparkles size={16} />
            <span>Recommended Projects ({recommendations.length})</span>
          </button>
        </div>
      </div>

      {/* DASHBOARD METRICS SUMMARY CARDS */}
      {dashboardStats && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '16px',
          }}
        >
          {/* Total Assigned */}
          <div className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase' }}>
              Total Assigned
            </span>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
              <span style={{ fontSize: '28px', fontWeight: 800, color: 'var(--text-main)' }}>
                {dashboardStats.total_assigned}
              </span>
              <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>projects</span>
            </div>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              {dashboardStats.not_started} not started
            </span>
          </div>

          {/* In Progress */}
          <div className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--primary)', textTransform: 'uppercase' }}>
              In Progress
            </span>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
              <span style={{ fontSize: '28px', fontWeight: 800, color: 'var(--primary)' }}>
                {dashboardStats.in_progress}
              </span>
              <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>active</span>
            </div>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              {dashboardStats.milestone_stats.in_progress} milestones ongoing
            </span>
          </div>

          {/* Pending Submissions / Under Review */}
          <div className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: '#0284C7', textTransform: 'uppercase' }}>
              Pending Review
            </span>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
              <span style={{ fontSize: '28px', fontWeight: 800, color: '#0284C7' }}>
                {dashboardStats.pending_submissions}
              </span>
              <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>submissions</span>
            </div>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              {dashboardStats.milestone_stats.submitted} milestones submitted
            </span>
          </div>

          {/* Revision Required */}
          <div className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--amber-warn)', textTransform: 'uppercase' }}>
              Revision Required
            </span>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
              <span style={{ fontSize: '28px', fontWeight: 800, color: 'var(--amber-warn)' }}>
                {dashboardStats.revision_required}
              </span>
              <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>revisions</span>
            </div>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              {dashboardStats.milestone_stats.revision_required} feedback items
            </span>
          </div>

          {/* Completed & Verified */}
          <div className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--emerald-success)', textTransform: 'uppercase' }}>
              Completed & Verified
            </span>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
              <span style={{ fontSize: '28px', fontWeight: 800, color: 'var(--emerald-success)' }}>
                {dashboardStats.completed}
              </span>
              <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>projects</span>
            </div>
            <span style={{ fontSize: '12px', color: 'var(--emerald-success)', fontWeight: 600 }}>
              Eligible for Resume
            </span>
          </div>

          {/* Overall Completion Percentage */}
          <div
            className="card"
            style={{
              padding: '20px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              background: 'linear-gradient(135deg, var(--bg-card) 0%, var(--primary-subtle) 100%)',
              borderColor: 'var(--primary-border)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase' }}>
                Completion Rate
              </span>
              <Award size={18} color="var(--primary)" />
            </div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', margin: '8px 0' }}>
              <span style={{ fontSize: '32px', fontWeight: 800, color: 'var(--primary)' }}>
                {dashboardStats.overall_completion_percentage}%
              </span>
            </div>
            <div
              style={{
                width: '100%',
                height: '6px',
                background: 'rgba(37, 99, 235, 0.15)',
                borderRadius: '3px',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  width: `${dashboardStats.overall_completion_percentage}%`,
                  height: '100%',
                  background: 'var(--primary)',
                  borderRadius: '3px',
                  transition: 'width 0.4s ease',
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 1: ASSIGNED PROJECTS & MILESTONE TRACKING */}
      {/* ========================================================================= */}
      {activeTab === 'tracking' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Status Filter Bar */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-muted)' }}>Status:</span>
              {['ALL', 'In Progress', 'Submitted', 'Under Review', 'Revision Required', 'Completed'].map((st) => (
                <button
                  key={st}
                  onClick={() => setStatusFilter(st)}
                  className={`btn ${statusFilter === st ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ fontSize: '12px', padding: '5px 12px', borderRadius: 'var(--radius-sm)' }}
                >
                  {st === 'ALL' ? 'All Projects' : st}
                </button>
              ))}
            </div>

            <button
              className="btn btn-primary"
              onClick={() => setActiveTab('explore')}
              style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px' }}
            >
              <PlusCircle size={15} />
              <span>Explore New Projects</span>
            </button>
          </div>

          {/* Assigned Projects List */}
          {filteredProjects.length === 0 ? (
            <div className="card" style={{ padding: '48px 24px', textAlign: 'center' }}>
              <CheckSquare size={36} color="var(--text-dim)" style={{ margin: '0 auto 12px' }} />
              <h3 style={{ fontSize: '17px', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 6px 0' }}>
                No Projects Found {statusFilter !== 'ALL' && `with status "${statusFilter}"`}
              </h3>
              <p style={{ fontSize: '13.5px', color: 'var(--text-muted)', margin: '0 auto 18px', maxWidth: '480px' }}>
                Accept an AI-recommended cybersecurity project to begin milestone tracking, hands-on tasks, and verification.
              </p>
              <button className="btn btn-primary" onClick={() => setActiveTab('explore')}>
                <span>Browse Recommended Projects</span>
              </button>
            </div>
          ) : (
            filteredProjects.map((project) => {
              const isExpanded = !!expandedProjects[project.id];
              const milestones = project.milestones || [];
              const completedMilestones = milestones.filter((m) => m.status === 'Completed').length;

              return (
                <div
                  key={project.id}
                  className="card"
                  style={{
                    padding: '24px',
                    borderLeft: `4px solid ${
                      project.status === 'Completed'
                        ? 'var(--emerald-success)'
                        : project.status === 'Revision Required'
                        ? 'var(--amber-warn)'
                        : 'var(--primary)'
                    }`,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '18px',
                  }}
                >
                  {/* Project Header Row */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                        <h2 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
                          {project.project_title}
                        </h2>
                        {renderStatusBadge(project.status)}
                        <span className="badge badge-slate">{project.domain}</span>
                        <span className="badge badge-slate">{project.difficulty_level}</span>
                      </div>
                      <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                        Target Role: <strong>{project.role_name}</strong> • Project ID: <code>{project.project_id}</code>
                        {project.deadline && (
                          <span> • Deadline: {new Date(project.deadline).toLocaleDateString()}</span>
                        )}
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <button
                        className="btn btn-secondary"
                        onClick={() => toggleProject(project.id)}
                        style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px' }}
                      >
                        <span>{isExpanded ? 'Collapse Milestones' : 'View Milestones'}</span>
                        {isExpanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
                      </button>

                      <button
                        className="btn btn-secondary"
                        onClick={() => handleDeleteProject(project.id, project.project_title)}
                        title="Delete Assignment"
                        style={{ color: 'var(--rose-danger)', borderColor: 'var(--rose-border)', padding: '6px 10px' }}
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </div>

                  {/* Progress & Verification Bar */}
                  <div
                    style={{
                      background: 'var(--bg-subtle)',
                      padding: '14px 18px',
                      borderRadius: 'var(--radius-sm)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '10px',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '13px' }}>
                      <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                        Project Progress: {completedMilestones} of {milestones.length} Milestones Completed ({project.completion_percentage}%)
                      </span>
                      {project.eligible_for_resume ? (
                        <span style={{ color: 'var(--emerald-success)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '5px' }}>
                          <CheckCircle2 size={15} />
                          Verified for ATS Resume
                        </span>
                      ) : (
                        <span style={{ color: 'var(--text-dim)', fontSize: '12px' }}>
                          Complete & verify all milestones to unlock resume inclusion
                        </span>
                      )}
                    </div>

                    {/* Progress Bar */}
                    <div
                      style={{
                        width: '100%',
                        height: '8px',
                        background: 'var(--border-subtle)',
                        borderRadius: '4px',
                        overflow: 'hidden',
                      }}
                    >
                      <div
                        style={{
                          width: `${project.completion_percentage}%`,
                          height: '100%',
                          background:
                            project.status === 'Completed'
                              ? 'var(--emerald-success)'
                              : project.status === 'Revision Required'
                              ? 'var(--amber-warn)'
                              : 'var(--primary)',
                          borderRadius: '4px',
                          transition: 'width 0.4s ease',
                        }}
                      />
                    </div>
                  </div>

                  {/* Resume Inclusion Notice */}
                  {project.eligible_for_resume ? (
                    <div
                      style={{
                        background: 'var(--emerald-subtle)',
                        border: '1px solid var(--emerald-border)',
                        borderRadius: 'var(--radius-sm)',
                        padding: '12px 16px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: '12px',
                        fontSize: '13px',
                        color: 'var(--emerald-success)',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <Award size={18} />
                        <div>
                          <strong>Verified & Eligible for Resume:</strong> This completed cybersecurity project is verified and
                          will be automatically integrated into your improved ATS resume with authoritative technical bullets.
                        </div>
                      </div>
                      {onNavigateToAnalyze && (
                        <button
                          className="btn btn-primary"
                          onClick={onNavigateToAnalyze}
                          style={{ fontSize: '12px', padding: '6px 12px', whiteSpace: 'nowrap' }}
                        >
                          Generate Improved Resume
                        </button>
                      )}
                    </div>
                  ) : (
                    <div
                      style={{
                        background: 'var(--bg-subtle)',
                        border: '1px dashed var(--border-subtle)',
                        borderRadius: 'var(--radius-sm)',
                        padding: '10px 14px',
                        fontSize: '12.5px',
                        color: 'var(--text-dim)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                      }}
                    >
                      <Shield size={14} color="var(--primary)" />
                      <span>
                        <strong>Truthful ATS Rule:</strong> Incomplete or unverified projects are strictly excluded from resume generation
                        until all phases pass technical evaluation.
                      </span>
                    </div>
                  )}

                  {/* Expanded Milestones Breakdown */}
                  {isExpanded && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginTop: '6px' }}>
                      <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-main)', margin: '4px 0 0' }}>
                        Implementation Milestones & Measurable Tasks
                      </h3>

                      {milestones.map((m) => {
                        const isMilestoneExpanded = expandedMilestones[m.id] ?? true;
                        const tasks = m.tasks || [];
                        const completedTasks = tasks.filter((t) => t.is_completed).length;

                        return (
                          <div
                            key={m.id}
                            style={{
                              border: '1px solid var(--border-subtle)',
                              borderRadius: 'var(--radius-sm)',
                              background: 'var(--bg-card)',
                              overflow: 'hidden',
                            }}
                          >
                            {/* Milestone Header */}
                            <div
                              style={{
                                padding: '14px 18px',
                                background: 'var(--bg-subtle)',
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                cursor: 'pointer',
                              }}
                              onClick={() => toggleMilestone(m.id)}
                            >
                              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                                <span style={{ fontWeight: 700, fontSize: '14px', color: 'var(--text-main)' }}>
                                  Phase {m.milestone_number}: {m.title}
                                </span>
                                {renderStatusBadge(m.status)}
                                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                                  ({completedTasks}/{tasks.length} tasks completed)
                                </span>
                              </div>

                              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                {m.deadline && (
                                  <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>
                                    Due: {new Date(m.deadline).toLocaleDateString()}
                                  </span>
                                )}
                                {isMilestoneExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                              </div>
                            </div>

                            {/* Milestone Content */}
                            {isMilestoneExpanded && (
                              <div style={{ padding: '16px 18px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
                                {m.objective && (
                                  <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                                    <strong>Objective:</strong> {m.objective}
                                  </div>
                                )}

                                {m.expected_output && (
                                  <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                                    <strong>Expected Deliverable:</strong> {m.expected_output}
                                  </div>
                                )}

                                {/* Interactive Tasks Checklist */}
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                  <div style={{ fontSize: '12.5px', fontWeight: 700, color: 'var(--text-main)', textTransform: 'uppercase' }}>
                                    Measurable Implementation Tasks:
                                  </div>

                                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                                    {tasks.map((task) => (
                                      <div
                                        key={task.id}
                                        onClick={() => handleTaskToggle(project.id, m.id, task.id, task.is_completed)}
                                        style={{
                                          display: 'flex',
                                          alignItems: 'center',
                                          gap: '10px',
                                          padding: '8px 12px',
                                          borderRadius: 'var(--radius-xs)',
                                          background: task.is_completed ? 'var(--emerald-subtle)' : 'var(--bg-subtle)',
                                          border: `1px solid ${task.is_completed ? 'var(--emerald-border)' : 'var(--border-subtle)'}`,
                                          cursor: 'pointer',
                                          transition: 'all 0.15s ease',
                                        }}
                                      >
                                        {task.is_completed ? (
                                          <CheckSquare size={17} color="var(--emerald-success)" />
                                        ) : (
                                          <Square size={17} color="var(--text-dim)" />
                                        )}
                                        <span
                                          style={{
                                            fontSize: '13px',
                                            color: task.is_completed ? 'var(--text-main)' : 'var(--text-muted)',
                                            textDecoration: task.is_completed ? 'line-through' : 'none',
                                          }}
                                        >
                                          {task.task_text}
                                        </span>
                                      </div>
                                    ))}
                                  </div>
                                </div>

                                {/* Revision Instructions if status is Revision Required */}
                                {m.status === 'Revision Required' && (
                                  <div
                                    style={{
                                      padding: '12px 16px',
                                      background: 'var(--amber-subtle)',
                                      border: '1px solid var(--amber-border)',
                                      borderRadius: 'var(--radius-sm)',
                                      display: 'flex',
                                      flexDirection: 'column',
                                      gap: '6px',
                                    }}
                                  >
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--amber-warn)', fontWeight: 700, fontSize: '13px' }}>
                                      <AlertTriangle size={15} />
                                      <span>Revision Required by Security Reviewer</span>
                                    </div>
                                    {m.verification_history && m.verification_history[0] && (
                                      <div style={{ fontSize: '13px', color: 'var(--text-main)' }}>
                                        <div><strong>Feedback:</strong> {m.verification_history[0].feedback}</div>
                                        {m.verification_history[0].revision_instructions && (
                                          <div style={{ marginTop: '4px' }}>
                                            <strong>Required Changes:</strong> {m.verification_history[0].revision_instructions}
                                          </div>
                                        )}
                                      </div>
                                    )}
                                  </div>
                                )}

                                {/* Submitted Evidence History */}
                                {m.evidence && m.evidence.length > 0 && (
                                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                                    <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-dim)' }}>
                                      Submitted Evidence:
                                    </span>
                                    {m.evidence.map((ev) => (
                                      <div
                                        key={ev.id}
                                        style={{
                                          padding: '10px 12px',
                                          background: 'var(--bg-subtle)',
                                          borderRadius: 'var(--radius-xs)',
                                          fontSize: '12.5px',
                                          display: 'flex',
                                          flexDirection: 'column',
                                          gap: '4px',
                                        }}
                                      >
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                          {ev.github_url ? (
                                            <a
                                              href={ev.github_url}
                                              target="_blank"
                                              rel="noreferrer"
                                              style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--primary)', fontWeight: 600 }}
                                            >
                                              <Github size={14} />
                                              <span>{ev.github_url}</span>
                                              <ExternalLink size={12} />
                                            </a>
                                          ) : (
                                            <span style={{ fontWeight: 600 }}>Written Project Documentation</span>
                                          )}
                                          <span style={{ color: 'var(--text-dim)', fontSize: '11.5px' }}>
                                            {new Date(ev.submitted_at).toLocaleString()}
                                          </span>
                                        </div>
                                        {ev.report_text && (
                                          <div style={{ color: 'var(--text-muted)', fontSize: '12px', whiteSpace: 'pre-wrap' }}>
                                            {ev.report_text}
                                          </div>
                                        )}
                                      </div>
                                    ))}
                                  </div>
                                )}

                                {/* Milestone Action Buttons */}
                                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap', paddingTop: '6px' }}>
                                  {/* Evidence Submission Button */}
                                  <button
                                    className="btn btn-primary"
                                    onClick={() =>
                                      setEvidenceModal({
                                        isOpen: true,
                                        projectId: project.id,
                                        milestoneId: m.id,
                                        milestoneTitle: m.title,
                                        githubUrl: '',
                                        reportText: '',
                                        notes: '',
                                      })
                                    }
                                    style={{ fontSize: '12.5px', padding: '6px 14px', display: 'flex', alignItems: 'center', gap: '6px' }}
                                  >
                                    <Send size={14} />
                                    <span>{m.status === 'Revision Required' ? 'Re-Submit Evidence' : 'Submit Evidence'}</span>
                                  </button>

                                  {/* AI Automated Verification Trigger */}
                                  <button
                                    className="btn btn-secondary"
                                    onClick={() => handleAiVerify(project.id, m.id)}
                                    disabled={isSubmitting}
                                    style={{ fontSize: '12.5px', padding: '6px 14px', display: 'flex', alignItems: 'center', gap: '6px' }}
                                  >
                                    <Sparkles size={14} color="var(--primary)" />
                                    <span>Run AI Verification</span>
                                  </button>

                                  {/* Authorized / Admin Review Button */}
                                  <button
                                    className="btn btn-secondary"
                                    onClick={() =>
                                      setReviewModal({
                                        isOpen: true,
                                        projectId: project.id,
                                        milestoneId: m.id,
                                        milestoneTitle: m.title,
                                        verdict: 'approved',
                                        score: 90,
                                        feedback: 'Deliverables verified against technical specifications.',
                                        revisionInstructions: '',
                                        reviewerName: 'Security Lead Auditor',
                                      })
                                    }
                                    style={{ fontSize: '12.5px', padding: '6px 14px', display: 'flex', alignItems: 'center', gap: '6px' }}
                                  >
                                    <UserCheck size={14} />
                                    <span>Admin Evaluation</span>
                                  </button>
                                </div>
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: EXPLORE & ACCEPT RECOMMENDED PROJECTS */}
      {/* ========================================================================= */}
      {activeTab === 'explore' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <h2 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 4px 0' }}>
                AI-Recommended Practical Projects
              </h2>
              <p style={{ fontSize: '13.5px', color: 'var(--text-muted)', margin: 0 }}>
                Ranked by alignment with <strong>{selectedRole?.role_name || 'Cybersecurity'}</strong> requirements to bridge identified skill gaps.
              </p>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '18px' }}>
            {recommendations.map((rec) => (
              <div
                key={rec.project_id}
                className="card"
                style={{
                  padding: '24px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '16px',
                  borderTop: '3px solid var(--primary)',
                }}
              >
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '10px' }}>
                    <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
                      {rec.project_title}
                    </h3>
                    <span
                      style={{
                        padding: '3px 8px',
                        borderRadius: 'var(--radius-full)',
                        fontSize: '11.5px',
                        fontWeight: 700,
                        background: 'var(--primary-subtle)',
                        color: 'var(--primary)',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {rec.relevance_score}% Match
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                    <span className="badge badge-slate">{rec.domain}</span>
                    <span className="badge badge-slate">{rec.difficulty_level}</span>
                    <span className="badge badge-slate">{rec.total_phases} Phases</span>
                    <span className="badge badge-slate">{rec.total_tasks} Tasks</span>
                  </div>

                  {rec.description && (
                    <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: '4px 0 0', lineHeight: 1.5 }}>
                      {rec.description}
                    </p>
                  )}

                  {/* Match Reasons */}
                  {rec.match_reasons && rec.match_reasons.length > 0 && (
                    <div
                      style={{
                        background: 'var(--bg-subtle)',
                        padding: '10px 12px',
                        borderRadius: 'var(--radius-xs)',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '4px',
                      }}
                    >
                      <span style={{ fontSize: '11.5px', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                        Why this project is recommended:
                      </span>
                      {rec.match_reasons.map((mr, idx) => (
                        <div key={idx} style={{ fontSize: '12px', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <CheckCircle2 size={13} color="var(--primary)" />
                          <span>{mr}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Required Technologies */}
                  {rec.required_technologies && rec.required_technologies.length > 0 && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                      <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>Tools:</span>
                      {rec.required_technologies.slice(0, 5).map((tech) => (
                        <span key={tech} className="badge badge-primary" style={{ fontSize: '11px', padding: '2px 7px' }}>
                          {tech}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Accept or Reject actions */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', paddingTop: '10px', borderTop: '1px solid var(--border-subtle)' }}>
                  <button
                    className="btn btn-primary"
                    onClick={() =>
                      setAssignmentModal({
                        isOpen: true,
                        recommendation: rec,
                        deadlineDays: 30,
                      })
                    }
                    style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', fontSize: '13px' }}
                  >
                    <CheckSquare size={15} />
                    <span>Accept & Assign</span>
                  </button>

                  <button
                    className="btn btn-secondary"
                    onClick={() => handleRejectRecommendation(rec.project_id)}
                    title="Decline this project"
                    style={{ fontSize: '13px', color: 'var(--text-dim)' }}
                  >
                    <XCircle size={15} />
                    <span>Decline</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODAL 1: EVIDENCE SUBMISSION FORM */}
      {/* ========================================================================= */}
      {evidenceModal.isOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
            padding: '16px',
          }}
        >
          <div
            className="card"
            style={{
              width: '100%',
              maxWidth: '560px',
              padding: '28px',
              display: 'flex',
              flexDirection: 'column',
              gap: '18px',
              boxShadow: 'var(--shadow-card)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <h3 style={{ fontSize: '17px', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 4px 0' }}>
                  Submit Milestone Evidence
                </h3>
                <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: 0 }}>
                  {evidenceModal.milestoneTitle}
                </p>
              </div>
              <button
                onClick={() => setEvidenceModal((prev) => ({ ...prev, isOpen: false }))}
                style={{ background: 'none', border: 'none', color: 'var(--text-dim)', fontSize: '18px', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmitEvidence} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '6px' }}>
                  GitHub Repository URL:
                </label>
                <div style={{ position: 'relative' }}>
                  <input
                    type="url"
                    placeholder="https://github.com/username/project-repo"
                    value={evidenceModal.githubUrl}
                    onChange={(e) => setEvidenceModal({ ...evidenceModal, githubUrl: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '10px 12px 10px 36px',
                      borderRadius: 'var(--radius-xs)',
                      border: '1px solid var(--border-subtle)',
                      background: 'var(--bg-input)',
                      color: 'var(--text-main)',
                      fontSize: '13.5px',
                    }}
                  />
                  <Github size={16} style={{ position: 'absolute', left: '12px', top: '12px', color: 'var(--text-dim)' }} />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '6px' }}>
                  Project Report / Implementation Summary:
                </label>
                <textarea
                  rows={4}
                  placeholder="Detail the tools configured, test execution findings, vulnerabilities identified, or defensive configurations..."
                  value={evidenceModal.reportText}
                  onChange={(e) => setEvidenceModal({ ...evidenceModal, reportText: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-xs)',
                    border: '1px solid var(--border-subtle)',
                    background: 'var(--bg-input)',
                    color: 'var(--text-main)',
                    fontSize: '13px',
                    fontFamily: 'inherit',
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '6px' }}>
                  Additional Notes / Verification Criteria:
                </label>
                <input
                  type="text"
                  placeholder="e.g. Docker containerized, tested on Kali Linux with Wireshark trace."
                  value={evidenceModal.notes}
                  onChange={(e) => setEvidenceModal({ ...evidenceModal, notes: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-xs)',
                    border: '1px solid var(--border-subtle)',
                    background: 'var(--bg-input)',
                    color: 'var(--text-main)',
                    fontSize: '13px',
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '10px' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setEvidenceModal((prev) => ({ ...prev, isOpen: false }))}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={isSubmitting}
                  style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
                >
                  <Send size={15} />
                  <span>{isSubmitting ? 'Submitting...' : 'Submit Evidence'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODAL 2: AUTHORIZED / ADMIN REVIEW MODAL */}
      {/* ========================================================================= */}
      {reviewModal.isOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
            padding: '16px',
          }}
        >
          <div
            className="card"
            style={{
              width: '100%',
              maxWidth: '560px',
              padding: '28px',
              display: 'flex',
              flexDirection: 'column',
              gap: '18px',
              boxShadow: 'var(--shadow-card)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <h3 style={{ fontSize: '17px', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 4px 0' }}>
                  Milestone Evaluation & Verification
                </h3>
                <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: 0 }}>
                  {reviewModal.milestoneTitle}
                </p>
              </div>
              <button
                onClick={() => setReviewModal((prev) => ({ ...prev, isOpen: false }))}
                style={{ background: 'none', border: 'none', color: 'var(--text-dim)', fontSize: '18px', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmitReview} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '6px' }}>
                  Evaluation Verdict:
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px' }}>
                  {[
                    { val: 'approved', label: 'Approve', color: 'var(--emerald-success)' },
                    { val: 'revision_required', label: 'Require Revision', color: 'var(--amber-warn)' },
                    { val: 'rejected', label: 'Reject', color: 'var(--rose-danger)' },
                  ].map((item) => (
                    <button
                      key={item.val}
                      type="button"
                      onClick={() => setReviewModal({ ...reviewModal, verdict: item.val as any })}
                      style={{
                        padding: '10px',
                        borderRadius: 'var(--radius-xs)',
                        border: reviewModal.verdict === item.val ? `2px solid ${item.color}` : '1px solid var(--border-subtle)',
                        background: reviewModal.verdict === item.val ? 'var(--bg-subtle)' : 'var(--bg-card)',
                        color: reviewModal.verdict === item.val ? item.color : 'var(--text-muted)',
                        fontWeight: 700,
                        fontSize: '12.5px',
                        cursor: 'pointer',
                      }}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '6px' }}>
                  Evaluator Score (0-100):
                </label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={reviewModal.score}
                  onChange={(e) => setReviewModal({ ...reviewModal, score: parseFloat(e.target.value) || 0 })}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-xs)',
                    border: '1px solid var(--border-subtle)',
                    background: 'var(--bg-input)',
                    color: 'var(--text-main)',
                    fontSize: '13.5px',
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '6px' }}>
                  Evaluative Feedback:
                </label>
                <textarea
                  rows={3}
                  required
                  placeholder="Provide concrete evaluation of the candidate's implementation and security rigor..."
                  value={reviewModal.feedback}
                  onChange={(e) => setReviewModal({ ...reviewModal, feedback: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-xs)',
                    border: '1px solid var(--border-subtle)',
                    background: 'var(--bg-input)',
                    color: 'var(--text-main)',
                    fontSize: '13px',
                    fontFamily: 'inherit',
                  }}
                />
              </div>

              {reviewModal.verdict === 'revision_required' && (
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: 'var(--amber-warn)', marginBottom: '6px' }}>
                    Specific Revision Instructions:
                  </label>
                  <textarea
                    rows={2}
                    placeholder="Explain what specific remediation or evidence is needed before this milestone can pass..."
                    value={reviewModal.revisionInstructions}
                    onChange={(e) => setReviewModal({ ...reviewModal, revisionInstructions: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      borderRadius: 'var(--radius-xs)',
                      border: '1px solid var(--amber-border)',
                      background: 'var(--amber-subtle)',
                      color: 'var(--text-main)',
                      fontSize: '13px',
                      fontFamily: 'inherit',
                    }}
                  />
                </div>
              )}

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '10px' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setReviewModal((prev) => ({ ...prev, isOpen: false }))}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={isSubmitting}
                  style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
                >
                  <UserCheck size={15} />
                  <span>{isSubmitting ? 'Saving Review...' : 'Submit Evaluation'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODAL 3: ASSIGNMENT DEADLINE SELECTION MODAL */}
      {/* ========================================================================= */}
      {assignmentModal.isOpen && assignmentModal.recommendation && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
            padding: '16px',
          }}
        >
          <div
            className="card"
            style={{
              width: '100%',
              maxWidth: '520px',
              padding: '28px',
              display: 'flex',
              flexDirection: 'column',
              gap: '18px',
              boxShadow: 'var(--shadow-card)',
            }}
          >
            <div>
              <h3 style={{ fontSize: '17px', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 6px 0' }}>
                Confirm Project Assignment
              </h3>
              <p style={{ fontSize: '13.5px', color: 'var(--text-muted)', margin: 0 }}>
                Accepting <strong>{assignmentModal.recommendation.project_title}</strong> will automatically generate{' '}
                {assignmentModal.recommendation.total_phases} milestone deliverables with actionable task checklists.
              </p>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '8px' }}>
                Select Target Completion Timeline:
              </label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px' }}>
                {[
                  { days: 14, label: 'Fast Track (14 Days)' },
                  { days: 30, label: 'Standard (30 Days)' },
                  { days: 60, label: 'Deep Lab (60 Days)' },
                ].map((opt) => (
                  <button
                    key={opt.days}
                    type="button"
                    onClick={() => setAssignmentModal({ ...assignmentModal, deadlineDays: opt.days })}
                    style={{
                      padding: '12px 10px',
                      borderRadius: 'var(--radius-xs)',
                      border: assignmentModal.deadlineDays === opt.days ? '2px solid var(--primary)' : '1px solid var(--border-subtle)',
                      background: assignmentModal.deadlineDays === opt.days ? 'var(--primary-subtle)' : 'var(--bg-card)',
                      color: assignmentModal.deadlineDays === opt.days ? 'var(--primary)' : 'var(--text-main)',
                      fontWeight: 700,
                      fontSize: '12px',
                      cursor: 'pointer',
                      textAlign: 'center',
                    }}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '8px' }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setAssignmentModal({ isOpen: false, recommendation: null, deadlineDays: 30 })}
              >
                Cancel
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleAcceptProject}
                disabled={isSubmitting}
                style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
              >
                <CheckSquare size={15} />
                <span>{isSubmitting ? 'Assigning...' : 'Confirm & Start Project'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};