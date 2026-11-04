import React, { useState, useEffect, useMemo } from 'react';
import {
  CheckCircle,
  XCircle,
  Edit3,
  HelpCircle,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Shield,
  Award,
  BookOpen,
  FolderGit2,
  Briefcase,
  GraduationCap,
  Wrench,
  CheckCircle2,
  ArrowRight,
  Info,
  ExternalLink,
  Layers,
  Flame,
  Check,
  RotateCcw,
  Download,
  Lock,
  BarChart3,
  FileText,
  Clock,
  Eye,
  X,
  Target,
  Trash2,
  Plus,
  CheckSquare,
  Square,
  Code,
  FileCode,
  GitFork,
  AlignLeft,
  AlignCenter,
  Search,
  RefreshCw,
} from 'lucide-react';
import {
  ImprovementPlanItem,
  ResumeImprovementPlan,
  ConfirmedSkillItem,
  WeakCategoryEvaluation,
  MatchReport,
  ImprovementResponse,
  PracticalProjectTemplate,
  CompletedProjectSubmission,
  ProjectEvaluationResult,
  ProposedResumeEntry,
  CandidateExistingProject,
  ResumeTemplate,
} from '../types';
import { submitCompletedProject, approveProjectForResume, fetchTemplates, fetchTemplatePreview } from '../api';
import { ResumeImprovementResults } from './ResumeImprovementResults';
import { LoadingOverlay } from './LoadingOverlay';
import { ProjectFlowDiagramModal } from './ProjectFlowDiagramModal';
import { CircularScoreIndicator, getScoreColorConfig } from './CircularScoreIndicator';

interface ImprovementPlanViewProps {
  plan: ResumeImprovementPlan;
  roleName: string;
  initialScore: number;
  analysisId?: string;
  onApplyImprovements: (
    approvedItems: ImprovementPlanItem[],
    confirmedSkills: ConfirmedSkillItem[],
    approvedCompletedProject?: ProposedResumeEntry | null,
    approvedCompletedProjects?: ProposedResumeEntry[],
    selectionMode?: 'automatic' | 'manual',
    templateId?: string
  ) => void;
  isApplying: boolean;
  onSkipAll?: () => void;
  matchReport?: MatchReport;
  improvement?: ImprovementResponse | null;
  onProceedToNextStage?: () => void;
  isProceeding?: boolean;
}

export const ImprovementPlanView: React.FC<ImprovementPlanViewProps> = ({
  plan,
  roleName,
  initialScore,
  analysisId = '',
  onApplyImprovements,
  isApplying,
  matchReport,
  improvement = null,
  onProceedToNextStage,
  isProceeding = false,
}) => {
  // Local state for all recommendation items
  const [items, setItems] = useState<ImprovementPlanItem[]>(() => {
    return (plan.items || []).map((item) => ({
      ...item,
      status: item.status || 'pending',
      candidate_response: item.candidate_response || {},
    }));
  });

  // Active skill filter: 'all' | 'high' | 'medium' | 'low'
  const [skillFilter, setSkillFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');

  // Future learning roadmap set (skills marked "No Experience Yet")
  const [futureLearningSkills, setFutureLearningSkills] = useState<Set<string>>(new Set());

  // Collapsible toggle for category breakdown
  const [showCategoryBreakdown, setShowCategoryBreakdown] = useState(false);
  const [expandedCategoryKey, setExpandedCategoryKey] = useState<string | null>(null);

  // Active Full Project Plan Modal (Phases A–J)
  const [activePlanModal, setActivePlanModal] = useState<any | null>(null);

  // PDF Viewer Modal State
  const [pdfViewerModal, setPdfViewerModal] = useState<{
    isOpen: boolean;
    planId: string;
    title: string;
    pdfUrl: string;
  } | null>(null);
  const [isPdfLoading, setIsPdfLoading] = useState(true);
  const [pdfLoadError, setPdfLoadError] = useState<string | null>(null);

  // =========================================================================
  // OPTIONAL TEMPLATE SELECTION STATE
  // =========================================================================
  const [templateSelectionMode, setTemplateSelectionMode] = useState<'automatic' | 'manual'>('automatic');
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | null>(null);
  const [availableTemplates, setAvailableTemplates] = useState<ResumeTemplate[]>([]);
  const [isLoadingTemplates, setIsLoadingTemplates] = useState(false);
  const [templateSearchQuery, setTemplateSearchQuery] = useState('');
  const [templateAlignmentFilter, setTemplateAlignmentFilter] = useState<'all' | 'left' | 'center'>('all');

  // Preview Template Modal State
  const [previewTemplateModal, setPreviewTemplateModal] = useState<ResumeTemplate | null>(null);
  const [previewTemplateData, setPreviewTemplateData] = useState<any | null>(null);
  const [isPreviewTemplateLoading, setIsPreviewTemplateLoading] = useState(false);
  const [previewTemplateError, setPreviewTemplateError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    setIsLoadingTemplates(true);
    fetchTemplates()
      .then((data) => {
        if (isMounted && data) {
          setAvailableTemplates(data);
        }
      })
      .catch((err) => {
        console.warn('Could not load template registry', err);
      })
      .finally(() => {
        if (isMounted) setIsLoadingTemplates(false);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const handleOpenTemplatePreview = async (tmpl: ResumeTemplate) => {
    setPreviewTemplateModal(tmpl);
    setIsPreviewTemplateLoading(true);
    setPreviewTemplateError(null);
    try {
      const data = await fetchTemplatePreview(tmpl.template_id);
      setPreviewTemplateData(data);
    } catch (err: any) {
      setPreviewTemplateError(err.message || `Failed to load preview for ${tmpl.template_id}`);
    } finally {
      setIsPreviewTemplateLoading(false);
    }
  };

  const handleCloseTemplatePreview = () => {
    setPreviewTemplateModal(null);
    setPreviewTemplateData(null);
    setPreviewTemplateError(null);
  };

  const filteredTemplates = useMemo(() => {
    return availableTemplates.filter((t) => {
      const q = templateSearchQuery.toLowerCase().trim();
      const matchSearch =
        !q ||
        t.template_id.toLowerCase().includes(q) ||
        t.template_name.toLowerCase().includes(q) ||
        t.description.toLowerCase().includes(q);

      const align = t.style_config?.header_alignment || 'left';
      const matchAlign =
        templateAlignmentFilter === 'all' ||
        (templateAlignmentFilter === 'left' && align === 'left') ||
        (templateAlignmentFilter === 'center' && align === 'center');

      return matchSearch && matchAlign;
    });
  }, [availableTemplates, templateSearchQuery, templateAlignmentFilter]);

  // =========================================================================
  // EXISTING PROJECTS STATE (Requirement 2)
  // =========================================================================
  const [existingProjects, setExistingProjects] = useState<CandidateExistingProject[]>([]);
  const [isProjectFormOpen, setIsProjectFormOpen] = useState(false);
  const [editingProjectId, setEditingProjectId] = useState<string | null>(null);
  const [projectFormError, setProjectFormError] = useState<string | null>(null);
  const [evaluatingProjectId, setEvaluatingProjectId] = useState<string | null>(null);
  const [deleteConfirmationId, setDeleteConfirmationId] = useState<string | null>(null);

  const [projectForm, setProjectForm] = useState({
    title: '',
    description: '',
    githubUrl: '',
    technologies: '',
    status: 'completed' as 'completed' | 'in_progress',
  });

  // Modal State: Ask candidate whether to add saved project to resume
  const [offerAddToResumeModal, setOfferAddToResumeModal] = useState<{
    isOpen: boolean;
    project: CandidateExistingProject;
  } | null>(null);

  // Modal State: Review proposed resume entry before adding to resume
  const [proposedEntryReviewModal, setProposedEntryReviewModal] = useState<{
    isOpen: boolean;
    project: CandidateExistingProject;
    proposedEntry: ProposedResumeEntry;
    isRecommended?: boolean;
  } | null>(null);

  // Modal State: Confirmation of intent to start recommended project
  const [confirmStartRecommendedModal, setConfirmStartRecommendedModal] = useState(false);

  // Modal State: View Project Workflow Diagram
  const [activeFlowDiagramProject, setActiveFlowDiagramProject] = useState<any | null>(null);

  // Recommended project user response status
  const [recommendedProjectStatus, setRecommendedProjectStatus] = useState<
    'initial' | 'added_in_progress' | 'in_learning_plan' | 'dismissed'
  >('initial');

  // Validation warning state
  const [validationError, setValidationError] = useState<string | null>(null);

  // Primary project recommendation extraction
  const primaryProjectPlan = plan.primary_project_plan || null;
  const projectItem = items.find((i) => i.item_type === 'project_recommendation' || !!i.project_recommendation);
  const primaryProjTemplate: PracticalProjectTemplate | null =
    projectItem?.project_recommendation ||
    (primaryProjectPlan
      ? {
          project_title: primaryProjectPlan.overview?.project_title || 'Cybersecurity Practical Project',
          target_role: roleName,
          level: primaryProjectPlan.overview?.difficulty || 'Intermediate',
          skills_demonstrated: primaryProjectPlan.skills?.all_targeted_skills || [],
          proposed_technologies: primaryProjectPlan.technology_stack || [],
          project_objective: primaryProjectPlan.overview?.project_objective || '',
          suggested_implementation_tasks: (primaryProjectPlan.phases || []).map((p: any) => p.title),
          expected_deliverables: (primaryProjectPlan.final_deliverables || []).join('; '),
          suggested_resume_bullet: primaryProjectPlan.resume_documentation_guide?.sample_bullets?.[0] || '',
          is_future_project: true,
          plan_id: primaryProjectPlan.plan_id || 'plan_default',
          docx_download_url: `/api/projects/download-plan/${primaryProjectPlan.plan_id}/docx`,
          pdf_download_url: `/api/projects/download-plan/${primaryProjectPlan.plan_id}/pdf`,
          weaknesses_addressed: primaryProjectPlan.overview?.weaknesses_addressed || [],
        }
      : null);

  // =========================================================================
  // EXTRACT ALL SKILLS TO DISPLAY IN COMPACT GRID (Requirement 1)
  // =========================================================================
  // Collect all skills from plan items and role match report
  interface CleanSkillCardData {
    id: string;
    itemId?: string;
    skillName: string;
    priority: 'HIGH PRIORITY' | 'MEDIUM PRIORITY' | 'LOW PRIORITY';
    priorityLevel: 'high' | 'medium' | 'low';
    currentProficiency: 'beginner' | 'intermediate' | 'advanced' | 'not_yet' | null;
  }

  const cleanSkillsList: CleanSkillCardData[] = React.useMemo(() => {
    const list: CleanSkillCardData[] = [];
    const seen = new Set<string>();

    // 1. From item skill cards
    items.forEach((item) => {
      const sDetail = item.skill_details;
      const sName = sDetail?.skill_name || (item.category_key === 'technical_skills' && item.title ? item.title.replace('Core Skill:', '').replace('Additional Skill:', '').trim() : null);

      if (sName && !seen.has(sName.toLowerCase())) {
        seen.add(sName.toLowerCase());
        const qId = `skill_${sName.toLowerCase().replace(/[\s/]+/g, '_')}`;
        const rawProf = item.candidate_response?.[qId] || item.candidate_response?.[`${qId}_proficiency`];

        let prof: 'beginner' | 'intermediate' | 'advanced' | 'not_yet' | null = null;
        if (rawProf === 'beginner' || rawProf === 'basic_familiarity') prof = 'beginner';
        else if (rawProf === 'intermediate') prof = 'intermediate';
        else if (rawProf === 'advanced' || rawProf === 'hands_on') prof = 'advanced';
        else if (rawProf === 'not_yet' || rawProf === 'not_used') prof = 'not_yet';

        const prio = item.priority === 'high' ? 'high' : item.priority === 'medium' ? 'medium' : 'low';
        list.push({
          id: item.item_id,
          itemId: item.item_id,
          skillName: sName,
          priority: prio === 'high' ? 'HIGH PRIORITY' : prio === 'medium' ? 'MEDIUM PRIORITY' : 'LOW PRIORITY',
          priorityLevel: prio,
          currentProficiency: prof,
        });
      }
    });

    // 2. Supplement from matched_skills if not already in list
    if (matchReport?.matched_skills) {
      matchReport.matched_skills.forEach((m, idx) => {
        if (!seen.has(m.skill_name.toLowerCase())) {
          seen.add(m.skill_name.toLowerCase());
          const prio = m.importance === 'core' ? 'high' : m.importance === 'preferred' ? 'medium' : 'low';
          list.push({
            id: `matched_sk_${idx}`,
            skillName: m.skill_name,
            priority: prio === 'high' ? 'HIGH PRIORITY' : prio === 'medium' ? 'MEDIUM PRIORITY' : 'LOW PRIORITY',
            priorityLevel: prio,
            currentProficiency: 'intermediate', // Verified in resume
          });
        }
      });
    }

    // Sort by Priority: High first, then Medium, then Low
    return list.sort((a, b) => {
      const pOrder = { high: 1, medium: 2, low: 3 };
      return pOrder[a.priorityLevel] - pOrder[b.priorityLevel];
    });
  }, [items, matchReport]);

  // Filter skills by active filter tab
  const displayedSkills = React.useMemo(() => {
    if (skillFilter === 'all') return cleanSkillsList;
    return cleanSkillsList.filter((s) => s.priorityLevel === skillFilter);
  }, [cleanSkillsList, skillFilter]);

  // Skill Proficiency Selector Handler: Beginner | Intermediate | Advanced | No Experience Yet
  const handleSelectSkillProficiency = (
    skillName: string,
    level: 'beginner' | 'intermediate' | 'advanced' | 'not_yet',
    itemId?: string
  ) => {
    setValidationError(null);
    const qId = `skill_${skillName.toLowerCase().replace(/[\s/]+/g, '_')}`;

    if (level === 'not_yet') {
      setFutureLearningSkills((prev) => new Set(prev).add(skillName));
    } else {
      setFutureLearningSkills((prev) => {
        const next = new Set(prev);
        next.delete(skillName);
        return next;
      });
    }

    setItems((prev) => {
      const match = prev.find((it) => it.item_id === itemId || it.skill_details?.skill_name.toLowerCase() === skillName.toLowerCase());
      if (match) {
        return prev.map((it) => {
          if (it.item_id === match.item_id) {
            const resp = { ...(it.candidate_response || {}) };
            const isNotYet = level === 'not_yet';
            resp[qId] = isNotYet ? 'not_used' : level;
            resp[`${qId}_proficiency`] = level;

            return {
              ...it,
              status: isNotYet ? 'skipped' : 'approved',
              candidate_response: resp,
            };
          }
          return it;
        });
      } else {
        // Create virtual approved plan item so submission includes it
        const isNotYet = level === 'not_yet';
        const newItem: ImprovementPlanItem = {
          item_id: `custom_sk_${skillName.toLowerCase().replace(/[\s/]+/g, '_')}`,
          category: 'Technical Skills',
          category_key: 'technical_skills',
          title: skillName,
          current_issue: `Skill ${skillName} declared by candidate.`,
          recommended_change: `Incorporate verified capability with ${skillName}.`,
          relevance_reason: `Targeted technical requirement for ${roleName}.`,
          required_info: 'Candidate confirmed proficiency.',
          expected_improvement: 'Demonstrates practical qualification.',
          action_type: 'skills_confirmation',
          status: isNotYet ? 'skipped' : 'approved',
          candidate_response: {
            [qId]: isNotYet ? 'not_used' : level,
            [`${qId}_proficiency`]: level,
            context_source: 'Practical Experience',
          },
        };
        return [...prev, newItem];
      }
    });
  };

  // =========================================================================
  // EXISTING PROJECTS HANDLERS (Requirement 2 & 5)
  // =========================================================================
  const handleOpenAddProject = () => {
    setEditingProjectId(null);
    setProjectForm({
      title: '',
      description: '',
      githubUrl: '',
      technologies: '',
      status: 'completed',
    });
    setProjectFormError(null);
    setIsProjectFormOpen(true);
  };

  const handleOpenEditProject = (proj: CandidateExistingProject) => {
    setEditingProjectId(proj.id);
    setProjectForm({
      title: proj.project_title,
      description: proj.project_description,
      githubUrl: proj.github_url || '',
      technologies: proj.technologies_used.join(', '),
      status: proj.status,
    });
    setProjectFormError(null);
    setIsProjectFormOpen(true);
  };

  const handleSaveProject = (e: React.FormEvent) => {
    e.preventDefault();
    setProjectFormError(null);

    if (!projectForm.title.trim()) {
      setProjectFormError('Please enter a project title.');
      return;
    }
    if (!projectForm.description.trim()) {
      setProjectFormError('Please describe what the project does and your contribution.');
      return;
    }

    // Validate GitHub URL format if supplied
    if (projectForm.githubUrl.trim()) {
      const urlPattern = /^(https?:\/\/)?(www\.)?github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+(\/.*)?$/i;
      const genericUrlPattern = /^https?:\/\/.+/i;
      if (!urlPattern.test(projectForm.githubUrl.trim()) && !genericUrlPattern.test(projectForm.githubUrl.trim())) {
        setProjectFormError('Please enter a valid repository URL (e.g. https://github.com/username/project) or leave empty if developed locally.');
        return;
      }
    }

    const techArray = projectForm.technologies
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean);

    let savedProj: CandidateExistingProject;
    if (editingProjectId) {
      savedProj = {
        id: editingProjectId,
        project_title: projectForm.title.trim(),
        project_description: projectForm.description.trim(),
        github_url: projectForm.githubUrl.trim() || undefined,
        technologies_used: techArray,
        status: projectForm.status,
        evaluation: null,
        is_approved_for_resume: false,
        approved_entry: null,
      };
      setExistingProjects((prev) =>
        prev.map((p) => (p.id === editingProjectId ? savedProj : p))
      );
    } else {
      savedProj = {
        id: `proj_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
        project_title: projectForm.title.trim(),
        project_description: projectForm.description.trim(),
        github_url: projectForm.githubUrl.trim() || undefined,
        technologies_used: techArray,
        status: projectForm.status,
      };
      setExistingProjects((prev) => [...prev, savedProj]);
    }

    setIsProjectFormOpen(false);
    setEditingProjectId(null);

    // Prompt candidate immediately via confirmation dialog:
    // Add this project to your resume? Project: [Actual title]
    setOfferAddToResumeModal({
      isOpen: true,
      project: savedProj,
    });
  };

  const handleOfferYesAddToResume = (proj: CandidateExistingProject) => {
    setOfferAddToResumeModal(null);

    const isInProgress = proj.status === 'in_progress';
    const techLine = proj.technologies_used.length > 0 ? proj.technologies_used.join(', ') : 'Security toolchain';

    // Format title according to strict rule:
    // If in progress: "PROJECT TITLE | In Progress"
    // If completed: "PROJECT TITLE" (NO "In Progress" label)
    const titleLine = isInProgress ? `${proj.project_title} | In Progress` : proj.project_title;
    const statusLabel = isInProgress ? 'In Progress' : 'Completed';

    let bullets: string[];
    if (isInProgress) {
      bullets = [
        `Developing: ${proj.project_description.slice(0, 150)}.`,
        `Technologies: ${techLine}.`,
        `Planned Implementation: Progressing through technical development and security verification for ${roleName}.`,
      ];
    } else {
      bullets = [
        `Developed: ${proj.project_description.slice(0, 150)}.`,
        `Technologies: ${techLine}.`,
        `Tested: Local functional verification and testing completed in authorized lab environment.`,
        `Achieved: Delivered functional cybersecurity components satisfying ${roleName} criteria.`,
      ];
      if (proj.github_url) {
        bullets.push(`Repository: ${proj.github_url}`);
      }
    }

    const proposedEntry: ProposedResumeEntry = {
      title_line: titleLine,
      bullets,
      status_label: statusLabel,
      is_approved: false,
    };

    setProposedEntryReviewModal({
      isOpen: true,
      project: proj,
      proposedEntry,
      isRecommended: false,
    });
  };

  const handleConfirmProposedEntry = async (
    proj: CandidateExistingProject,
    entry: ProposedResumeEntry,
    isRecommended?: boolean
  ) => {
    try {
      const confirmedEntry: ProposedResumeEntry = {
        ...entry,
        is_approved: true,
      };

      if (analysisId) {
        await approveProjectForResume(analysisId, confirmedEntry, true);
      }

      setExistingProjects((prev) => {
        const exists = prev.some((p) => p.id === proj.id);
        if (exists) {
          return prev.map((p) =>
            p.id === proj.id
              ? { ...p, is_approved_for_resume: true, approved_entry: confirmedEntry }
              : p
          );
        } else {
          return [
            ...prev,
            { ...proj, is_approved_for_resume: true, approved_entry: confirmedEntry },
          ];
        }
      });

      if (isRecommended) {
        setRecommendedProjectStatus('added_in_progress');
      }
    } catch (err: any) {
      setValidationError(err.message || 'Failed to record project approval.');
    } finally {
      setProposedEntryReviewModal(null);
    }
  };

  const handleExecuteStartRecommendedProject = () => {
    if (!primaryProjTemplate) return;
    setConfirmStartRecommendedModal(false);

    const titleLine = `${primaryProjTemplate.project_title} | In Progress`;
    const techList = primaryProjTemplate.proposed_technologies || [];
    const techLine = techList.length > 0 ? techList.join(', ') : 'Cybersecurity toolchain';
    const skillsTargeted = (primaryProjTemplate.skills_demonstrated || []).slice(0, 3).join(', ');

    const bullets = [
      `Developing: Planning and initiating implementation of ${primaryProjTemplate.project_title} to develop practical competencies in ${skillsTargeted}.`,
      `Technologies: ${techLine}.`,
      `Planned Implementation: Following structured phases including environment setup, security controls, and verification testing for ${roleName}.`,
    ];

    const recProj: CandidateExistingProject = {
      id: `rec_${primaryProjTemplate.plan_id || 'proj'}_${Date.now()}`,
      project_title: primaryProjTemplate.project_title,
      project_description: primaryProjTemplate.project_objective,
      technologies_used: techList,
      status: 'in_progress',
    };

    const proposedEntry: ProposedResumeEntry = {
      title_line: titleLine,
      bullets,
      status_label: 'In Progress',
      is_approved: false,
    };

    setProposedEntryReviewModal({
      isOpen: true,
      project: recProj,
      proposedEntry,
      isRecommended: true,
    });
  };

  const handleDeleteProject = (projId: string) => {
    setExistingProjects((prev) => prev.filter((p) => p.id !== projId));
    setDeleteConfirmationId(null);
  };

  const handleEvaluateExistingProject = async (proj: CandidateExistingProject) => {
    try {
      setEvaluatingProjectId(proj.id);
      const submission: CompletedProjectSubmission = {
        analysis_id: analysisId,
        project_title: proj.project_title,
        project_description: proj.project_description,
        skills_used: proj.technologies_used,
        technologies_used: proj.technologies_used,
        implementation_tasks_completed: [proj.project_description],
        testing_performed: 'Local functional testing & verification',
        verified_outcomes: 'Functional practical implementation',
        status: proj.status,
        github_url: proj.github_url,
        confirmation_statement: true,
      };

      const evalResult = await submitCompletedProject(submission);
      setExistingProjects((prev) =>
        prev.map((p) => {
          if (p.id === proj.id) {
            return {
              ...p,
              evaluation: evalResult,
            };
          }
          return p;
        })
      );
      // Immediately offer the proposed entry review modal
      handleOfferYesAddToResume(proj);
    } catch (err: any) {
      setValidationError(err.message || 'Failed to evaluate project evidence.');
    } finally {
      setEvaluatingProjectId(null);
    }
  };

  const handleApproveExistingProjectForResume = async (proj: CandidateExistingProject) => {
    if (!proj.evaluation?.proposed_resume_entry) return;
    try {
      const entry: ProposedResumeEntry = {
        ...proj.evaluation.proposed_resume_entry,
        is_approved: true,
      };
      await approveProjectForResume(analysisId, entry, true);
      setExistingProjects((prev) =>
        prev.map((p) => {
          if (p.id === proj.id) {
            return {
              ...p,
              is_approved_for_resume: true,
              approved_entry: entry,
            };
          }
          return p;
        })
      );
    } catch (err: any) {
      setValidationError(err.message || 'Failed to approve project for resume.');
    }
  };

  // =========================================================================
  // PDF VIEWER HANDLERS (Requirement 4)
  // =========================================================================
  const handleOpenPdfViewer = (planId: string, title: string) => {
    setIsPdfLoading(true);
    setPdfLoadError(null);
    setPdfViewerModal({
      isOpen: true,
      planId,
      title,
      pdfUrl: `/api/projects/view-plan/${planId}`,
    });
  };

  // =========================================================================
  // SUBMISSION TO IMPROVE RESUME (Requirement 6)
  // =========================================================================
  const handleSubmit = () => {
    const approvedList = items.filter((i) => i.status === 'approved' || i.status === 'edited');
    const approvedExistingProjects = existingProjects
      .filter((p) => p.is_approved_for_resume && p.approved_entry)
      .map((p) => p.approved_entry as ProposedResumeEntry);

    const hasConfirmedSkills = cleanSkillsList.some(
      (s) => s.currentProficiency && s.currentProficiency !== 'not_yet'
    );

    if (approvedList.length === 0 && approvedExistingProjects.length === 0 && !hasConfirmedSkills) {
      setValidationError('Please select your proficiency for at least one skill or approve a project before generating your improved resume.');
      window.scrollTo({ top: 350, behavior: 'smooth' });
      return;
    }

    setValidationError(null);
    const confirmedSkillsList: ConfirmedSkillItem[] = [];

    // Collect confirmed skills from cleanSkillsList
    cleanSkillsList.forEach((sk) => {
      if (sk.currentProficiency && sk.currentProficiency !== 'not_yet') {
        confirmedSkillsList.push({
          skill_name: sk.skillName,
          proficiency: sk.currentProficiency,
          context_source: 'Candidate Confirmation',
          tasks_performed: `Verified proficiency: ${sk.currentProficiency} for ${sk.skillName}`,
        });
      }
    });

    if (templateSelectionMode === 'manual' && !selectedTemplateId) {
      setValidationError('Please select a resume template from the gallery below or switch back to automatic selection.');
      const elem = document.getElementById('template-selection-section');
      if (elem) elem.scrollIntoView({ behavior: 'smooth' });
      return;
    }

    const primaryApprovedProject = approvedExistingProjects.length > 0 ? approvedExistingProjects[0] : null;
    onApplyImprovements(
      approvedList,
      confirmedSkillsList,
      primaryApprovedProject,
      approvedExistingProjects,
      templateSelectionMode,
      templateSelectionMode === 'manual' ? selectedTemplateId || undefined : undefined
    );
  };

  // Counts
  const confirmedCount = cleanSkillsList.filter((s) => s.currentProficiency && s.currentProficiency !== 'not_yet').length;
  const roadmapCount = cleanSkillsList.filter((s) => s.currentProficiency === 'not_yet').length;
  const approvedProjectsCount = existingProjects.filter((p) => p.is_approved_for_resume).length;

  const pointsNeeded = Math.max(0, Math.round((80.0 - initialScore) * 10) / 10);
  const isPassing = initialScore >= 80.0;
  const scoreConfig = getScoreColorConfig(initialScore);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
      {/* =========================================================================
          SECTION 1: STICKY ACTION BAR
          ========================================================================= */}
      <div className="sticky-action-bar" id="sticky-resume-action-bar">
        <div className="sticky-action-bar-left">
          <div className="sticky-action-bar-title">
            <Sparkles size={18} color="var(--primary)" />
            <span>Resume Improvement Plan</span>
            <span className="badge badge-primary" style={{ fontSize: '11px', padding: '2px 8px' }}>
              Cutoff: 80.0 / 100
            </span>
          </div>

          <div className="sticky-action-bar-stats">
            <span className="sticky-stat-item">
              <strong>{cleanSkillsList.length}</strong> role skills
            </span>
            <span className="sticky-stat-item approved">
              <CheckCircle2 size={13} />
              <strong>{confirmedCount}</strong> confirmed
            </span>
            {roadmapCount > 0 && (
              <span className="sticky-stat-item" style={{ color: 'var(--text-dim)' }}>
                <strong>{roadmapCount}</strong> on learning roadmap
              </span>
            )}
            {existingProjects.length > 0 && (
              <span className="sticky-stat-item" style={{ color: 'var(--emerald-success)', fontWeight: 700 }}>
                <FolderGit2 size={13} />
                <strong>{existingProjects.length}</strong> my projects ({approvedProjectsCount} approved)
              </span>
            )}
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {validationError && (
            <span style={{ fontSize: '12px', color: 'var(--rose-danger)', fontWeight: 600 }}>
              {validationError}
            </span>
          )}

          <button
            id="sticky-generate-resume-btn"
            className="btn btn-primary"
            onClick={handleSubmit}
            disabled={isApplying}
            style={{
              padding: '10px 22px',
              fontSize: '13.5px',
              fontWeight: 700,
              boxShadow: confirmedCount > 0 ? '0 2px 12px rgba(37, 99, 235, 0.35)' : 'none',
            }}
          >
            {isApplying ? (
              <>
                <div
                  className="spin"
                  style={{
                    width: '14px',
                    height: '14px',
                    border: '2px solid #FFFFFF',
                    borderTopColor: 'transparent',
                    borderRadius: '50%',
                  }}
                />
                <span>Generating Resume...</span>
              </>
            ) : (
              <>
                <span>Generate Improved Resume</span>
                <ArrowRight size={15} />
              </>
            )}
          </button>
        </div>
      </div>

      {/* =========================================================================
          SCORE HEADLINE & OPTIONAL WEAKNESS BREAKDOWN
          ========================================================================= */}
      <div className="ats-score-header-card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', gap: '20px', flexWrap: 'wrap' }} className="ats-score-header-row">
          <div className="ats-score-header-main">
            {/* LEFT: Circular ATS score indicator */}
            <div className="ats-score-left">
              <CircularScoreIndicator score={initialScore} size={92} strokeWidth={7} />
            </div>

            {/* RIGHT: Badges, Heading, Description */}
            <div className="ats-score-right">
              <div className="ats-score-badges-row">
                <span
                  className={`badge ${scoreConfig.badgeClass}`}
                  style={{ fontSize: '11.5px', padding: '3px 10px', fontWeight: 700 }}
                >
                  {initialScore < 70 ? <AlertTriangle size={12} /> : <CheckCircle size={12} />}
                  <span>{scoreConfig.statusLabel}</span>
                </span>
                <span className="badge badge-primary" style={{ fontSize: '11.5px', padding: '3px 10px' }}>
                  Target Role: {roleName}
                </span>
                <span className="badge badge-subtle" style={{ fontSize: '11px', padding: '3px 8px' }}>
                  Cutoff: {plan.threshold || 80}.0 pts
                </span>
              </div>

              <h2 className="ats-score-heading">
                Optimize Your Resume for {roleName}
              </h2>

              <p className="ats-score-description">
                {initialScore >= 70
                  ? `Baseline score ${initialScore}/100 demonstrates strong role alignment. Review the recommendations below to further optimize formatting and keyword alignment.`
                  : `Your resume is ${pointsNeeded} points below cutoff. Confirm genuine skills below, add your existing projects, and generate an ATS-ready resume.`}
              </p>
            </div>
          </div>

          <div className="ats-score-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setShowCategoryBreakdown(!showCategoryBreakdown)}
              style={{ fontSize: '12px', padding: '7px 13px', whiteSpace: 'nowrap' }}
            >
              <BarChart3 size={14} />
              <span>{showCategoryBreakdown ? 'Hide Weakness Breakdown' : 'Inspect 8 Scoring Categories'}</span>
              {showCategoryBreakdown ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
          </div>
        </div>

        {/* Collapsible 8-Category Evaluation Table */}
        {showCategoryBreakdown && plan.category_evaluations && plan.category_evaluations.length > 0 && (
          <div style={{ width: '100%', marginTop: '4px', paddingTop: '16px', borderTop: '1px solid var(--border-subtle)' }}>
            <div className="cat-score-table-wrap">
              <div className="cat-score-row cat-score-header">
                <span>Category</span>
                <span>Score / Max</span>
                <span>Status</span>
                <span>Main Identified Weakness</span>
                <span style={{ textAlign: 'right' }}>Action</span>
              </div>

              {plan.category_evaluations.map((cat: WeakCategoryEvaluation) => {
                const statusLabel =
                  cat.percentage >= 80 ? 'Satisfactory' : cat.percentage >= 60 ? 'Review Recommended' : 'Needs Improvement';
                const statusClass =
                  cat.percentage >= 80 ? 'badge-emerald' : cat.percentage >= 60 ? 'badge-primary' : 'badge-amber';
                const isCatExpanded = expandedCategoryKey === cat.category_key;

                return (
                  <div key={cat.category_key} style={{ display: 'flex', flexDirection: 'column' }}>
                    <div
                      className="cat-score-row"
                      style={{ cursor: 'pointer', background: isCatExpanded ? 'var(--bg-subtle)' : undefined }}
                      onClick={() => setExpandedCategoryKey(isCatExpanded ? null : cat.category_key)}
                    >
                      <span style={{ fontWeight: 700, color: 'var(--text-main)' }}>{cat.category_name}</span>
                      <span className="mono" style={{ fontWeight: 700, color: 'var(--text-main)' }}>
                        {cat.current_score} <span style={{ color: 'var(--text-dim)', fontWeight: 500 }}>/ {cat.max_score}</span>
                      </span>
                      <span>
                        <span className={`badge ${statusClass}`} style={{ fontSize: '10.5px' }}>{statusLabel}</span>
                      </span>
                      <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                        {cat.what_is_missing.length > 100 ? `${cat.what_is_missing.slice(0, 98)}...` : cat.what_is_missing}
                      </span>
                      <span style={{ textAlign: 'right' }}>
                        <button
                          className="btn btn-secondary"
                          onClick={(e) => {
                            e.stopPropagation();
                            setExpandedCategoryKey(isCatExpanded ? null : cat.category_key);
                          }}
                          style={{ fontSize: '11px', padding: '3px 8px' }}
                        >
                          {isCatExpanded ? 'Hide' : 'Details'}
                        </button>
                      </span>
                    </div>

                    {isCatExpanded && (
                      <div style={{ padding: '12px 18px', background: 'var(--bg-subtle)', borderLeft: '3px solid var(--primary)', fontSize: '12px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '10px' }}>
                        <div>
                          <strong style={{ color: 'var(--primary)', display: 'block' }}>Role Relevance:</strong>
                          <span style={{ color: 'var(--text-muted)' }}>{cat.role_relevance_reason}</span>
                        </div>
                        <div>
                          <strong style={{ color: 'var(--emerald-success)', display: 'block' }}>Recommended Action:</strong>
                          <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>{cat.recommended_next_action}</span>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* =========================================================================
          TASK 1: SIMPLIFIED SKILL PROFICIENCY SELECTION (Requirement 1)
          ========================================================================= */}
      <div className="card" style={{ padding: '22px 24px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px', marginBottom: '14px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="badge badge-primary" style={{ fontSize: '11.5px', fontWeight: 800 }}>Task 1</span>
              <h3 style={{ fontSize: '16.5px', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
                Confirm Skill Proficiency
              </h3>
            </div>
            <p style={{ fontSize: '12.5px', color: 'var(--text-muted)', margin: '4px 0 0' }}>
              Select your genuine proficiency for each role skill. If you have not used a tool yet, choose <strong>No Experience Yet</strong> to save it for future learning without misrepresenting capability.
            </p>
          </div>

          {/* Quick Filter Tabs */}
          <div className="filter-tabs" style={{ margin: 0 }}>
            <button
              className={`filter-tab-btn ${skillFilter === 'all' ? 'active' : ''}`}
              onClick={() => setSkillFilter('all')}
              style={{ fontSize: '11.5px', padding: '5px 10px' }}
            >
              All Skills ({cleanSkillsList.length})
            </button>
            <button
              className={`filter-tab-btn ${skillFilter === 'high' ? 'active' : ''}`}
              onClick={() => setSkillFilter('high')}
              style={{ fontSize: '11.5px', padding: '5px 10px' }}
            >
              High Priority ({cleanSkillsList.filter((s) => s.priorityLevel === 'high').length})
            </button>
            <button
              className={`filter-tab-btn ${skillFilter === 'medium' ? 'active' : ''}`}
              onClick={() => setSkillFilter('medium')}
              style={{ fontSize: '11.5px', padding: '5px 10px' }}
            >
              Medium Priority ({cleanSkillsList.filter((s) => s.priorityLevel === 'medium').length})
            </button>
            <button
              className={`filter-tab-btn ${skillFilter === 'low' ? 'active' : ''}`}
              onClick={() => setSkillFilter('low')}
              style={{ fontSize: '11.5px', padding: '5px 10px' }}
            >
              Additional ({cleanSkillsList.filter((s) => s.priorityLevel === 'low').length})
            </button>
          </div>
        </div>

        {/* Responsive Grid of Compact Skill Cards */}
        <div className="compact-skill-grid">
          {displayedSkills.map((sk) => {
            const current = sk.currentProficiency;
            const cardSelectedClass =
              current === 'beginner'
                ? 'selected-beginner'
                : current === 'intermediate'
                ? 'selected-intermediate'
                : current === 'advanced'
                ? 'selected-advanced'
                : current === 'not_yet'
                ? 'selected-not_yet'
                : '';

            return (
              <div key={sk.id} className={`compact-skill-card ${cardSelectedClass}`}>
                {/* Header: Skill Name & Priority Badge */}
                <div className="compact-skill-header">
                  <span className="compact-skill-name">{sk.skillName}</span>
                  <span
                    className={
                      sk.priorityLevel === 'high'
                        ? 'badge badge-rose'
                        : sk.priorityLevel === 'medium'
                        ? 'badge badge-primary'
                        : 'badge badge-subtle'
                    }
                    style={{ fontSize: '9.5px', padding: '2px 6px', fontWeight: 700 }}
                  >
                    {sk.priority}
                  </span>
                </div>

                {/* 4 Mutually Exclusive Proficiency Buttons */}
                <div className="pill-group" style={{ width: '100%', justifyContent: 'space-between' }}>
                  <button
                    type="button"
                    className={`pill-btn ${current === 'beginner' ? 'active-primary' : ''}`}
                    onClick={() => handleSelectSkillProficiency(sk.skillName, 'beginner', sk.itemId)}
                    style={{ flex: 1, padding: '4px 6px', fontSize: '10.5px' }}
                    title="Basic familiarity or coursework"
                  >
                    <span>Beginner</span>
                  </button>

                  <button
                    type="button"
                    className={`pill-btn ${current === 'intermediate' ? 'active-emerald' : ''}`}
                    onClick={() => handleSelectSkillProficiency(sk.skillName, 'intermediate', sk.itemId)}
                    style={{ flex: 1, padding: '4px 6px', fontSize: '10.5px' }}
                    title="Hands-on laboratory or practical projects"
                  >
                    <span>Intermediate</span>
                  </button>

                  <button
                    type="button"
                    className={`pill-btn ${current === 'advanced' ? 'active-emerald' : ''}`}
                    onClick={() => handleSelectSkillProficiency(sk.skillName, 'advanced', sk.itemId)}
                    style={{ flex: 1, padding: '4px 6px', fontSize: '10.5px' }}
                    title="Deep hands-on implementation & problem solving"
                  >
                    <span>Advanced</span>
                  </button>

                  <button
                    type="button"
                    className={`pill-btn ${current === 'not_yet' ? 'active-dim' : ''}`}
                    onClick={() => handleSelectSkillProficiency(sk.skillName, 'not_yet', sk.itemId)}
                    style={{ flex: 1, padding: '4px 6px', fontSize: '10.5px' }}
                    title="Mark for future learning without adding to resume"
                  >
                    <span>No Experience Yet</span>
                  </button>
                </div>

                {/* Selected Status Indicator Bar */}
                {current && (
                  <div style={{ fontSize: '10.5px', color: current === 'not_yet' ? 'var(--text-dim)' : 'var(--emerald-success)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                    {current === 'not_yet' ? (
                      <span>• Saved to learning roadmap (Not added to resume)</span>
                    ) : (
                      <span>✓ {current.charAt(0).toUpperCase() + current.slice(1)} selected</span>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* =========================================================================
          TASK 2: PROJECTS & PRACTICAL EXPERIENCE (Requirements 2, 3 & 4)
          ========================================================================= */}
      <div className="card" style={{ padding: '22px 24px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <span className="badge badge-primary" style={{ fontSize: '11.5px', fontWeight: 800 }}>Task 2</span>
          <h3 style={{ fontSize: '16.5px', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
            Projects & Practical Experience
          </h3>
        </div>
        <p style={{ fontSize: '12.5px', color: 'var(--text-muted)', margin: '0 0 18px' }}>
          Tangible project evidence is the highest-weighted factor for cybersecurity hiring managers. Review the role recommendation below or add your existing projects.
        </p>

        {/* ---------------------------------------------------------------------
            AREA A: RECOMMENDED PROJECT (COMPACT)
            --------------------------------------------------------------------- */}
        {primaryProjTemplate && (
          <div
            style={{
              padding: '16px 18px',
              borderRadius: 'var(--radius-sm)',
              background: 'var(--bg-subtle)',
              border: '1px solid var(--border-subtle)',
              marginBottom: '22px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px', marginBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="badge badge-emerald" style={{ fontSize: '10.5px' }}>Recommended Practical Blueprint</span>
                <span className="badge badge-subtle" style={{ fontSize: '10.5px' }}>Difficulty: {primaryProjTemplate.level || 'Intermediate'}</span>
                <span className="badge badge-primary" style={{ fontSize: '10.5px' }}>Role: {roleName}</span>
              </div>
            </div>

            <h4 style={{ fontSize: '15px', fontWeight: 800, color: 'var(--text-main)', margin: '0 0 4px' }}>
              {primaryProjTemplate.project_title}
            </h4>
            <p style={{ fontSize: '12.5px', color: 'var(--text-muted)', margin: '0 0 10px', lineHeight: 1.4 }}>
              {primaryProjTemplate.project_objective}
            </p>

            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap', marginBottom: '12px' }}>
              <strong style={{ fontSize: '11px', color: 'var(--text-dim)' }}>Skills Targeted:</strong>
              {(primaryProjTemplate.skills_demonstrated || []).map((sk, idx) => (
                <span key={idx} className="badge badge-subtle" style={{ fontSize: '10.5px' }}>{sk}</span>
              ))}
            </div>

            {/* Action Buttons: View Implementation Plan, Download DOCX, View PDF, Download PDF, Add to Learning Plan */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', marginBottom: '14px' }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setActivePlanModal(primaryProjectPlan || primaryProjTemplate)}
                style={{ fontSize: '12px', padding: '6px 12px' }}
              >
                <Eye size={13} />
                <span>View Implementation Plan</span>
              </button>

              <a
                href={primaryProjTemplate.docx_download_url || `/api/projects/download-plan/${primaryProjTemplate.plan_id}/docx`}
                download
                className="btn btn-secondary"
                style={{ fontSize: '12px', padding: '6px 12px', textDecoration: 'none' }}
              >
                <Download size={13} />
                <span>Download DOCX</span>
              </a>

              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => handleOpenPdfViewer(primaryProjTemplate.plan_id || 'plan_default', primaryProjTemplate.project_title)}
                style={{ fontSize: '12px', padding: '6px 12px' }}
              >
                <FileCode size={13} />
                <span>View PDF</span>
              </button>

              <a
                href={`/api/projects/download-plan/${primaryProjTemplate.plan_id || 'plan_default'}/pdf`}
                download
                className="btn btn-secondary"
                style={{ fontSize: '12px', padding: '6px 12px', textDecoration: 'none' }}
              >
                <Download size={13} />
                <span>Download PDF</span>
              </a>

              <button
                type="button"
                id="view-flow-diagram-btn"
                className="btn btn-secondary"
                onClick={() => setActiveFlowDiagramProject(primaryProjectPlan || primaryProjTemplate)}
                style={{ fontSize: '12px', padding: '6px 12px' }}
                title="View browser-rendered visual workflow diagram"
              >
                <GitFork size={13} />
                <span>View Flow Diagram</span>
              </button>

              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => {
                  setFutureLearningSkills((prev) => new Set(prev).add(primaryProjTemplate.project_title));
                  setValidationError(null);
                }}
                style={{ fontSize: '12px', padding: '6px 12px', color: 'var(--text-dim)' }}
              >
                <BookOpen size={13} />
                <span>{futureLearningSkills.has(primaryProjTemplate.project_title) ? '✓ In Learning Plan' : 'Add to Learning Plan'}</span>
              </button>
            </div>

            {/* Dedicated Question & 3 Action Buttons */}
            {recommendedProjectStatus !== 'dismissed' && (
              <div
                style={{
                  padding: '14px 16px',
                  background: 'var(--bg-card)',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-subtle)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '10px',
                }}
              >
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-main)' }}>
                    Would you like to include this project in your resume as In Progress?
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
                    If you intend to build this project to satisfy role requirements, FUTRSEC will truthfully document it on your resume.
                  </div>
                </div>

                {recommendedProjectStatus === 'added_in_progress' ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--emerald-success)', fontSize: '12.5px', fontWeight: 600 }}>
                    <CheckCircle2 size={14} />
                    <span>✓ Recommended project added to your resume as In Progress.</span>
                  </div>
                ) : recommendedProjectStatus === 'in_learning_plan' ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-dim)', fontSize: '12px' }}>
                    <BookOpen size={14} />
                    <span>✓ Project added to your Learning Plan. Your resume remains unchanged.</span>
                  </div>
                ) : (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                    <button
                      type="button"
                      className="btn btn-primary"
                      onClick={() => setConfirmStartRecommendedModal(true)}
                      style={{ fontSize: '12px', padding: '6px 14px', fontWeight: 700 }}
                    >
                      <Plus size={13} />
                      <span>Yes, Add as In Progress</span>
                    </button>

                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => {
                        setFutureLearningSkills((prev) => new Set(prev).add(primaryProjTemplate.project_title));
                        setRecommendedProjectStatus('in_learning_plan');
                      }}
                      style={{ fontSize: '12px', padding: '6px 14px' }}
                    >
                      <span>Start Project Without Adding to Resume</span>
                    </button>

                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => setRecommendedProjectStatus('dismissed')}
                      style={{ fontSize: '12px', padding: '6px 12px', color: 'var(--text-dim)' }}
                    >
                      <span>Not Interested</span>
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* ---------------------------------------------------------------------
            AREA B: MY EXISTING PROJECTS (Requirement 2)
            --------------------------------------------------------------------- */}
        <div style={{ marginTop: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px', marginBottom: '8px' }}>
            <div>
              <h4 style={{ fontSize: '15px', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
                My Existing Projects
              </h4>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)', margin: '2px 0 0' }}>
                Add your completed or ongoing projects to help FUTRSEC understand your practical experience and improve your resume.
              </p>
            </div>

            {!isProjectFormOpen && (
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleOpenAddProject}
                style={{ fontSize: '12px', padding: '6px 14px' }}
              >
                <Plus size={13} />
                <span>Add Existing Project</span>
              </button>
            )}
          </div>

          {/* Inline Project Entry Form */}
          {isProjectFormOpen && (
            <form
              onSubmit={handleSaveProject}
              style={{
                marginTop: '12px',
                marginBottom: '16px',
                padding: '16px 20px',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--bg-subtle)',
                border: '1px solid var(--primary-border)',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <strong style={{ fontSize: '13.5px', color: 'var(--text-main)' }}>
                  {editingProjectId ? 'Edit Project Details' : 'Add New Project'}
                </strong>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setIsProjectFormOpen(false)}
                  style={{ padding: '4px', border: 'none', background: 'transparent' }}
                >
                  <X size={16} />
                </button>
              </div>

              {projectFormError && (
                <div style={{ fontSize: '12px', color: 'var(--rose-danger)', fontWeight: 600 }}>
                  {projectFormError}
                </div>
              )}

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '10px' }}>
                <div>
                  <label style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-dim)', display: 'block', marginBottom: '3px' }}>
                    PROJECT TITLE *
                  </label>
                  <input
                    type="text"
                    className="input-control"
                    value={projectForm.title}
                    onChange={(e) => setProjectForm({ ...projectForm, title: e.target.value })}
                    placeholder="Enter your project title"
                    required
                  />
                </div>

                <div>
                  <label style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-dim)', display: 'block', marginBottom: '3px' }}>
                    PROJECT STATUS *
                  </label>
                  <div className="pill-group" style={{ marginTop: '2px' }}>
                    <button
                      type="button"
                      className={`pill-btn ${projectForm.status === 'completed' ? 'active-emerald' : ''}`}
                      onClick={() => setProjectForm({ ...projectForm, status: 'completed' })}
                    >
                      <CheckCircle size={12} />
                      <span>Completed</span>
                    </button>
                    <button
                      type="button"
                      className={`pill-btn ${projectForm.status === 'in_progress' ? 'active-primary' : ''}`}
                      onClick={() => setProjectForm({ ...projectForm, status: 'in_progress' })}
                    >
                      <Clock size={12} />
                      <span>In Progress</span>
                    </button>
                  </div>
                </div>
              </div>

              <div>
                <label style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-dim)', display: 'block', marginBottom: '3px' }}>
                  PROJECT DESCRIPTION *
                </label>
                <textarea
                  rows={2}
                  className="input-control"
                  value={projectForm.description}
                  onChange={(e) => setProjectForm({ ...projectForm, description: e.target.value })}
                  placeholder="Explain what the project does, what you implemented, and your contribution."
                  required
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '10px' }}>
                <div>
                  <label style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-dim)', display: 'block', marginBottom: '3px' }}>
                    TECHNOLOGIES AND SKILLS USED
                  </label>
                  <input
                    type="text"
                    className="input-control"
                    value={projectForm.technologies}
                    onChange={(e) => setProjectForm({ ...projectForm, technologies: e.target.value })}
                    placeholder="Python, PostgreSQL, FastAPI, React"
                  />
                </div>

                <div>
                  <label style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-dim)', display: 'block', marginBottom: '3px' }}>
                    GITHUB REPOSITORY URL (OPTIONAL)
                  </label>
                  <input
                    type="url"
                    className="input-control"
                    value={projectForm.githubUrl}
                    onChange={(e) => setProjectForm({ ...projectForm, githubUrl: e.target.value })}
                    placeholder="https://github.com/username/project"
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '4px' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setIsProjectFormOpen(false)}
                  style={{ fontSize: '12px', padding: '6px 14px' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  style={{ fontSize: '12px', padding: '6px 18px' }}
                >
                  Save Project
                </button>
              </div>
            </form>
          )}

          {/* List of Saved Existing Projects */}
          {existingProjects.length === 0 ? (
            <div style={{ padding: '16px', borderRadius: 'var(--radius-xs)', background: 'var(--bg-subtle)', textAlign: 'center', color: 'var(--text-dim)', fontSize: '12.5px' }}>
              No custom projects added yet. Click <strong>Add Existing Project</strong> to document projects you've already built.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '10px' }}>
              {existingProjects.map((proj) => {
                const isEvaluating = evaluatingProjectId === proj.id;
                const evalData = proj.evaluation;

                return (
                  <div key={proj.id} className="existing-project-card">
                    {/* Top Row: Title, Status, GitHub, Actions */}
                    <div className="existing-project-header">
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                        <span className="existing-project-title">{proj.project_title}</span>
                        <span className={proj.status === 'completed' ? 'badge badge-emerald' : 'badge badge-amber'} style={{ fontSize: '10px' }}>
                          {proj.status === 'completed' ? 'Completed' : 'In Progress'}
                        </span>
                        {proj.github_url && (
                          <a
                            href={proj.github_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{ display: 'flex', alignItems: 'center', gap: '3px', fontSize: '11px', color: 'var(--primary)', textDecoration: 'none' }}
                          >
                            <Code size={11} />
                            <span>Repository</span>
                            <ExternalLink size={10} />
                          </a>
                        )}
                        {proj.is_approved_for_resume && (
                          <span className="badge badge-emerald" style={{ fontSize: '10.5px' }}>
                            ✓ Approved for Resume
                          </span>
                        )}
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <button
                          type="button"
                          className="btn btn-secondary"
                          onClick={() => handleOpenEditProject(proj)}
                          style={{ fontSize: '11.5px', padding: '4px 10px' }}
                        >
                          <Edit3 size={12} />
                          <span>Edit</span>
                        </button>

                        <button
                          type="button"
                          className="btn btn-secondary"
                          onClick={() => setDeleteConfirmationId(proj.id)}
                          style={{ fontSize: '11.5px', padding: '4px 10px', color: 'var(--rose-danger)' }}
                        >
                          <Trash2 size={12} />
                          <span>Delete</span>
                        </button>

                        {!proj.is_approved_for_resume && (
                          <button
                            type="button"
                            className="btn btn-primary"
                            onClick={() => handleEvaluateExistingProject(proj)}
                            disabled={isEvaluating}
                            style={{ fontSize: '11.5px', padding: '4px 12px' }}
                          >
                            {isEvaluating ? 'Evaluating...' : 'Evaluate & Add to Resume'}
                          </button>
                        )}
                      </div>
                    </div>

                    <p style={{ margin: 0, fontSize: '12.5px', color: 'var(--text-muted)', lineHeight: 1.45 }}>
                      {proj.project_description}
                    </p>

                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                      {proj.technologies_used.map((t, idx) => (
                        <span key={idx} className="badge badge-subtle" style={{ fontSize: '10px' }}>{t}</span>
                      ))}
                    </div>

                    {/* Delete Confirmation Prompt */}
                    {deleteConfirmationId === proj.id && (
                      <div style={{ padding: '8px 12px', background: 'var(--rose-subtle)', borderRadius: 'var(--radius-xs)', border: '1px solid var(--rose-border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px', fontSize: '12px' }}>
                        <span style={{ color: 'var(--rose-danger)', fontWeight: 600 }}>Confirm deleting "{proj.project_title}"?</span>
                        <div style={{ display: 'flex', gap: '6px' }}>
                          <button className="btn btn-secondary" onClick={() => setDeleteConfirmationId(null)} style={{ fontSize: '11px', padding: '3px 8px' }}>Cancel</button>
                          <button className="btn btn-primary" onClick={() => handleDeleteProject(proj.id)} style={{ fontSize: '11px', padding: '3px 10px', background: 'var(--rose-danger)', borderColor: 'var(--rose-danger)' }}>Delete</button>
                        </div>
                      </div>
                    )}

                    {/* Concise Evaluation Results: Demonstrated / Improvement Needed / Not Yet Verified */}
                    {evalData && (
                      <div style={{ marginTop: '6px', paddingTop: '10px', borderTop: '1px solid var(--border-subtle)', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '8px' }}>
                          {/* 1. Demonstrated */}
                          <div style={{ padding: '8px 10px', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-xs)', borderLeft: '3px solid var(--emerald-success)' }}>
                            <strong style={{ color: 'var(--emerald-success)', display: 'block', marginBottom: '3px' }}>
                              Demonstrated ({evalData.demonstrated.length})
                            </strong>
                            {evalData.demonstrated.map((d, i) => (
                              <div key={i} style={{ color: 'var(--text-main)', fontSize: '11.5px' }}>• {d.name}: {d.finding}</div>
                            ))}
                          </div>

                          {/* 2. Improvement Needed */}
                          <div style={{ padding: '8px 10px', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-xs)', borderLeft: '3px solid var(--amber-warn)' }}>
                            <strong style={{ color: 'var(--amber-warn)', display: 'block', marginBottom: '3px' }}>
                              Improvement Needed ({evalData.improvement_needed.length})
                            </strong>
                            {evalData.improvement_needed.length === 0 ? (
                              <span style={{ color: 'var(--text-dim)', fontSize: '11.5px' }}>No major gaps.</span>
                            ) : (
                              evalData.improvement_needed.map((imp, i) => (
                                <div key={i} style={{ color: 'var(--text-main)', fontSize: '11.5px' }}>• {imp.name}: {imp.finding}</div>
                              ))
                            )}
                          </div>

                          {/* 3. Not Yet Verified */}
                          <div style={{ padding: '8px 10px', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-xs)', borderLeft: '3px solid var(--text-dim)' }}>
                            <strong style={{ color: 'var(--text-dim)', display: 'block', marginBottom: '3px' }}>
                              Not Yet Verified ({evalData.not_yet_submitted.length})
                            </strong>
                            {evalData.not_yet_submitted.length === 0 ? (
                              <span style={{ color: 'var(--text-dim)', fontSize: '11.5px' }}>All claims accounted for.</span>
                            ) : (
                              evalData.not_yet_submitted.map((nyv, i) => (
                                <div key={i} style={{ color: 'var(--text-dim)', fontSize: '11.5px' }}>• {nyv.name}</div>
                              ))
                            )}
                          </div>
                        </div>

                        {/* Proposed Resume Entry with Approval */}
                        {evalData.proposed_resume_entry && !proj.is_approved_for_resume && (
                          <div style={{ marginTop: '6px', padding: '10px 14px', background: 'var(--primary-subtle)', borderRadius: 'var(--radius-xs)', border: '1px solid var(--primary-border)' }}>
                            <div style={{ fontWeight: 700, color: 'var(--primary)', marginBottom: '4px' }}>
                              Proposed Resume Entry:
                            </div>
                            <div className="mono" style={{ fontSize: '11.5px', background: 'var(--bg-card)', padding: '8px', borderRadius: 'var(--radius-xs)', marginBottom: '8px', lineHeight: 1.4 }}>
                              <strong>{evalData.proposed_resume_entry.title_line}</strong><br />
                              {(evalData.proposed_resume_entry.bullets || []).map((b, idx) => (
                                <span key={idx}>• {b}<br /></span>
                              ))}
                            </div>

                            <button
                              type="button"
                              className="btn btn-primary"
                              onClick={() => handleApproveExistingProjectForResume(proj)}
                              style={{ fontSize: '11.5px', padding: '5px 14px' }}
                            >
                              <CheckCircle size={12} />
                              <span>Approve Project Entry for Resume</span>
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* =========================================================================
          CHOOSE YOUR RESUME TEMPLATE (OPTIONAL)
          ========================================================================= */}
      <div
        id="template-selection-section"
        className="card"
        style={{
          padding: '24px 28px',
          background: 'var(--bg-card)',
          border: '1px solid var(--border-strong)',
          borderRadius: 'var(--radius-md)',
          marginBottom: '24px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px', marginBottom: '18px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Layers size={18} color="var(--primary)" />
              <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
                Choose Your Resume Template (Optional)
              </h3>
              <span className="badge badge-subtle" style={{ fontSize: '11px', padding: '2px 8px' }}>
                30 ATS-Friendly Designs
              </span>
            </div>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
              Selecting a template is completely optional. Automatic Round Robin remains the default recommendation.
            </p>
          </div>

          {templateSelectionMode === 'manual' && (
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => {
                setTemplateSelectionMode('automatic');
                setSelectedTemplateId(null);
              }}
              style={{ fontSize: '12px', padding: '6px 14px', display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <RotateCcw size={13} />
              <span>Switch back to Auto-select</span>
            </button>
          )}
        </div>

        {/* The Two Option Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginBottom: '18px' }}>
          {/* OPTION 1: AUTOMATIC SELECTION (DEFAULT) */}
          <div
            id="template-option-auto"
            onClick={() => {
              setTemplateSelectionMode('automatic');
              setSelectedTemplateId(null);
            }}
            style={{
              padding: '16px 20px',
              borderRadius: 'var(--radius-sm)',
              border: templateSelectionMode === 'automatic' ? '2px solid var(--primary)' : '1px solid var(--border-subtle)',
              background: templateSelectionMode === 'automatic' ? 'var(--primary-subtle)' : 'var(--bg-subtle)',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <input
                  type="radio"
                  name="template_selection_mode"
                  id="mode_automatic"
                  checked={templateSelectionMode === 'automatic'}
                  onChange={() => {
                    setTemplateSelectionMode('automatic');
                    setSelectedTemplateId(null);
                  }}
                  style={{ accentColor: 'var(--primary)', cursor: 'pointer', width: '16px', height: '16px' }}
                />
                <label htmlFor="mode_automatic" style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-main)', cursor: 'pointer' }}>
                  Auto-select a template for me.
                </label>
              </div>
              <span className="badge badge-primary" style={{ fontSize: '10px', padding: '2px 6px' }}>
                Default (Recommended)
              </span>
            </div>
            <p style={{ fontSize: '12.5px', color: 'var(--text-muted)', margin: '2px 0 0 26px', lineHeight: 1.45 }}>
              FUTRSEC automatically assigns your resume template using its intelligent Round Robin system.
            </p>
          </div>

          {/* OPTION 2: MANUAL TEMPLATE SELECTION */}
          <div
            id="template-option-manual"
            onClick={() => {
              setTemplateSelectionMode('manual');
              if (!selectedTemplateId && availableTemplates.length > 0) {
                setSelectedTemplateId(availableTemplates[0].template_id);
              }
            }}
            style={{
              padding: '16px 20px',
              borderRadius: 'var(--radius-sm)',
              border: templateSelectionMode === 'manual' ? '2px solid var(--primary)' : '1px solid var(--border-subtle)',
              background: templateSelectionMode === 'manual' ? 'var(--primary-subtle)' : 'var(--bg-subtle)',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <input
                  type="radio"
                  name="template_selection_mode"
                  id="mode_manual"
                  checked={templateSelectionMode === 'manual'}
                  onChange={() => {
                    setTemplateSelectionMode('manual');
                    if (!selectedTemplateId && availableTemplates.length > 0) {
                      setSelectedTemplateId(availableTemplates[0].template_id);
                    }
                  }}
                  style={{ accentColor: 'var(--primary)', cursor: 'pointer', width: '16px', height: '16px' }}
                />
                <label htmlFor="mode_manual" style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-main)', cursor: 'pointer' }}>
                  Choose my own template.
                </label>
              </div>
              <span className="badge badge-subtle" style={{ fontSize: '10px', padding: '2px 6px' }}>
                Manual Selection
              </span>
            </div>
            <p style={{ fontSize: '12.5px', color: 'var(--text-muted)', margin: '2px 0 0 26px', lineHeight: 1.45 }}>
              Browse and select your preferred resume design from 30 available ATS-friendly templates.
            </p>
          </div>
        </div>

        {/* When Automatic Selection is active: show the exact required message */}
        {templateSelectionMode === 'automatic' && (
          <div
            style={{
              padding: '14px 18px',
              background: 'var(--bg-subtle)',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
            }}
          >
            <RefreshCw size={18} color="var(--primary)" style={{ flexShrink: 0 }} />
            <div style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: 1.45 }}>
              <strong style={{ color: 'var(--text-main)' }}>Automatic Selection Active:</strong> FUTRSEC will automatically choose the next available ATS-friendly template for your resume.
            </div>
          </div>
        )}

        {/* When Manual Selection is active: show Template Gallery */}
        {templateSelectionMode === 'manual' && (
          <div style={{ marginTop: '20px', borderTop: '1px solid var(--border-subtle)', paddingTop: '20px' }}>
            {/* Filter & Search Bar */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: '1', minWidth: '240px' }}>
                <div style={{ position: 'relative', width: '100%', maxWidth: '320px' }}>
                  <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-dim)' }} />
                  <input
                    type="text"
                    value={templateSearchQuery}
                    onChange={(e) => setTemplateSearchQuery(e.target.value)}
                    placeholder="Search templates (e.g. T15, Classic, Minimal)..."
                    className="input"
                    style={{ paddingLeft: '32px', fontSize: '12.5px', height: '34px' }}
                  />
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <button
                    type="button"
                    className={`btn ${templateAlignmentFilter === 'all' ? 'btn-primary' : 'btn-secondary'}`}
                    onClick={() => setTemplateAlignmentFilter('all')}
                    style={{ fontSize: '11px', padding: '4px 8px' }}
                  >
                    All (30)
                  </button>
                  <button
                    type="button"
                    className={`btn ${templateAlignmentFilter === 'left' ? 'btn-primary' : 'btn-secondary'}`}
                    onClick={() => setTemplateAlignmentFilter('left')}
                    style={{ fontSize: '11px', padding: '4px 8px' }}
                  >
                    <AlignLeft size={12} /> Left
                  </button>
                  <button
                    type="button"
                    className={`btn ${templateAlignmentFilter === 'center' ? 'btn-primary' : 'btn-secondary'}`}
                    onClick={() => setTemplateAlignmentFilter('center')}
                    style={{ fontSize: '11px', padding: '4px 8px' }}
                  >
                    <AlignCenter size={12} /> Centered
                  </button>
                </div>
              </div>

              {selectedTemplateId && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>Currently Selected:</span>
                  <span className="badge badge-success" style={{ fontWeight: 800, fontSize: '12px', padding: '3px 10px' }}>
                    <CheckCircle2 size={13} /> {selectedTemplateId} - {availableTemplates.find(t => t.template_id === selectedTemplateId)?.template_name || 'Selected'}
                  </span>
                </div>
              )}
            </div>

            {/* Template Cards Grid */}
            {isLoadingTemplates ? (
              <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
                <div className="spin" style={{ width: '24px', height: '24px', border: '2px solid var(--primary)', borderTopColor: 'transparent', borderRadius: '50%', margin: '0 auto 12px' }} />
                <span>Loading 30 ATS templates...</span>
              </div>
            ) : filteredTemplates.length === 0 ? (
              <div style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)' }}>
                No templates match your search.
              </div>
            ) : (
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                  gap: '16px',
                  maxHeight: '520px',
                  overflowY: 'auto',
                  paddingRight: '6px',
                }}
              >
                {filteredTemplates.map((template) => {
                  const isSelected = selectedTemplateId === template.template_id;
                  const font = template.style_config?.font_family || 'Calibri';
                  const align = template.style_config?.header_alignment || 'left';
                  const divider = template.style_config?.divider_style || 'solid';
                  const order: string[] = template.style_config?.section_order || [];

                  return (
                    <div
                      key={template.template_id}
                      id={`template-card-${template.template_id}`}
                      className="card"
                      style={{
                        padding: '16px',
                        borderRadius: 'var(--radius-sm)',
                        border: isSelected ? '2px solid var(--primary)' : '1px solid var(--border-subtle)',
                        background: isSelected ? 'var(--primary-subtle)' : 'var(--bg-card)',
                        boxShadow: isSelected ? '0 0 0 2px rgba(37, 99, 235, 0.25)' : 'none',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '10px',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease',
                      }}
                      onClick={() => setSelectedTemplateId(template.template_id)}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <span
                            style={{
                              background: isSelected ? 'var(--primary)' : 'var(--bg-subtle)',
                              color: isSelected ? '#FFFFFF' : 'var(--text-main)',
                              fontWeight: 800,
                              fontSize: '11px',
                              padding: '2px 8px',
                              borderRadius: '4px',
                            }}
                          >
                            {template.template_id}
                          </span>
                          <span className="badge badge-subtle" style={{ fontSize: '10px' }}>
                            {font}
                          </span>
                        </div>

                        {isSelected ? (
                          <span className="badge badge-success" style={{ fontSize: '10.5px', fontWeight: 700 }}>
                            <CheckCircle2 size={11} /> SELECTED
                          </span>
                        ) : (
                          <span className="badge badge-subtle" style={{ fontSize: '10px' }}>
                            {align === 'center' ? 'Centered' : 'Left'}
                          </span>
                        )}
                      </div>

                      <div>
                        <h4 style={{ fontSize: '14.5px', fontWeight: 800, color: 'var(--text-main)', margin: '0 0 4px 0' }}>
                          {template.template_name}
                        </h4>
                        <p style={{ fontSize: '12px', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                          {template.description}
                        </p>
                      </div>

                      {/* Miniature Layout Preview */}
                      <div
                        style={{
                          padding: '10px',
                          background: '#FFFFFF',
                          borderRadius: '4px',
                          border: '1px solid #E2E8F0',
                          boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.03)',
                        }}
                      >
                        <div
                          style={{
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: align === 'center' ? 'center' : 'flex-start',
                            marginBottom: '6px',
                            paddingBottom: '4px',
                            borderBottom: divider === 'none' ? 'none' : '1px solid #CBD5E1',
                          }}
                        >
                          <div style={{ width: '40%', height: '5px', background: '#0F172A', borderRadius: '1px', marginBottom: '3px' }} />
                          <div style={{ width: '65%', height: '3px', background: '#94A3B8', borderRadius: '1px' }} />
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                          {order.slice(0, 3).map((sec, sIdx) => (
                            <div key={sIdx} style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                              <span style={{ fontSize: '8px', fontWeight: 700, color: '#2563EB', textTransform: 'uppercase' }}>
                                {sec}
                              </span>
                              <div style={{ width: '100%', height: '2.5px', background: '#E2E8F0', borderRadius: '1px' }} />
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Action buttons */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: 'auto' }}>
                        <button
                          type="button"
                          className="btn btn-secondary"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleOpenTemplatePreview(template);
                          }}
                          style={{ flex: 1, fontSize: '11.5px', padding: '6px 10px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '4px' }}
                        >
                          <Eye size={12} />
                          <span>Preview</span>
                        </button>
                        <button
                          type="button"
                          className={`btn ${isSelected ? 'btn-primary' : 'btn-secondary'}`}
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedTemplateId(template.template_id);
                          }}
                          style={{ flex: 1.2, fontSize: '11.5px', padding: '6px 10px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '4px', fontWeight: isSelected ? 800 : 600 }}
                        >
                          {isSelected ? (
                            <>
                              <Check size={12} />
                              <span>Selected</span>
                            </>
                          ) : (
                            <span>Select Template</span>
                          )}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>

      {/* =========================================================================
          TASK 3: GENERATE IMPROVED RESUME (Requirement 6)
          ========================================================================= */}
      <div
        className="card"
        style={{
          padding: '22px 28px',
          background: 'var(--bg-card)',
          border: '1px solid var(--border-strong)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '16px',
          marginBottom: '28px',
        }}
      >
        <div>
          <div style={{ fontSize: '15px', fontWeight: 800, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span>Task 3: Ready to Generate Your Improved ATS Resume?</span>
            <span className="badge badge-primary">Round Robin Template Scheduler</span>
          </div>
          <p style={{ fontSize: '12.5px', color: 'var(--text-muted)', marginTop: '4px', maxWidth: '640px', lineHeight: 1.5 }}>
            Applying <strong style={{ color: 'var(--emerald-success)' }}>{confirmedCount} confirmed skills</strong> and{' '}
            <strong style={{ color: 'var(--emerald-success)' }}>{approvedProjectsCount} approved projects</strong>. Your resume will be formatted into standard ATS templates and deterministically re-scored.
          </p>
        </div>

        <button
          id="bottom-generate-resume-btn"
          className="btn btn-primary"
          onClick={handleSubmit}
          disabled={isApplying}
          style={{ padding: '12px 26px', fontSize: '14px', fontWeight: 700 }}
        >
          {isApplying ? (
            <>
              <div
                className="spin"
                style={{
                  width: '15px',
                  height: '15px',
                  border: '2px solid #FFFFFF',
                  borderTopColor: 'transparent',
                  borderRadius: '50%',
                }}
              />
              <span>Generating ATS Resume & Re-Scoring...</span>
            </>
          ) : (
            <>
              <span>Generate Improved Resume</span>
              <ArrowRight size={16} />
            </>
          )}
        </button>
      </div>

      {/* =========================================================================
          MODAL 1: PDF PROJECT IMPLEMENTATION-PLAN VIEWER (Requirement 4)
          ========================================================================= */}
      {pdfViewerModal && pdfViewerModal.isOpen && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.8)',
            zIndex: 1100,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '16px',
          }}
          onClick={() => setPdfViewerModal(null)}
        >
          <div
            className="card"
            style={{
              maxWidth: '960px',
              width: '100%',
              height: '92vh',
              display: 'flex',
              flexDirection: 'column',
              background: 'var(--bg-card)',
              position: 'relative',
              boxShadow: 'var(--shadow-lg)',
              overflow: 'hidden',
              padding: 0,
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Top Toolbar */}
            <div
              style={{
                padding: '14px 20px',
                borderBottom: '1px solid var(--border-subtle)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: 'var(--bg-surface)',
                flexWrap: 'wrap',
                gap: '10px',
              }}
            >
              <div>
                <span className="badge badge-emerald" style={{ fontSize: '10.5px', marginBottom: '2px' }}>
                  FUTRSEC PDF Plan Viewer
                </span>
                <h4 style={{ fontSize: '15px', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
                  {pdfViewerModal.title}
                </h4>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <a
                  href={pdfViewerModal.pdfUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-secondary"
                  style={{ fontSize: '12px', padding: '6px 12px', textDecoration: 'none' }}
                >
                  <ExternalLink size={13} />
                  <span>Open in Tab</span>
                </a>

                <a
                  href={`/api/projects/download-plan/${pdfViewerModal.planId}/pdf`}
                  download
                  className="btn btn-secondary"
                  style={{ fontSize: '12px', padding: '6px 12px', textDecoration: 'none' }}
                >
                  <Download size={13} />
                  <span>Download PDF</span>
                </a>

                <button
                  className="btn btn-secondary"
                  onClick={() => setPdfViewerModal(null)}
                  style={{ padding: '6px', borderRadius: '50%', border: 'none' }}
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            {/* Viewer Body: Embedded PDF IFrame with Loading & Error Fallback */}
            <div style={{ flex: 1, position: 'relative', background: '#525659' }}>
              {isPdfLoading && (
                <div
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '10px',
                    color: '#FFFFFF',
                    background: 'var(--bg-card)',
                    zIndex: 2,
                  }}
                >
                  <div
                    className="spin"
                    style={{
                      width: '28px',
                      height: '28px',
                      border: '3px solid var(--primary)',
                      borderTopColor: 'transparent',
                      borderRadius: '50%',
                    }}
                  />
                  <span style={{ fontSize: '13px', fontWeight: 600 }}>Loading Implementation Plan PDF...</span>
                </div>
              )}

              {pdfLoadError ? (
                <div
                  style={{
                    padding: '32px',
                    textAlign: 'center',
                    color: 'var(--rose-danger)',
                    background: 'var(--bg-card)',
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '12px',
                  }}
                >
                  <AlertTriangle size={32} />
                  <div style={{ fontSize: '15px', fontWeight: 700 }}>Unable to render inline PDF preview</div>
                  <p style={{ fontSize: '12.5px', color: 'var(--text-muted)', maxWidth: '420px', margin: 0 }}>
                    {pdfLoadError}
                  </p>
                  <a
                    href={`/api/projects/download-plan/${pdfViewerModal.planId}/pdf`}
                    download
                    className="btn btn-primary"
                    style={{ fontSize: '13px', padding: '8px 20px', textDecoration: 'none' }}
                  >
                    <Download size={14} />
                    <span>Download PDF Directly</span>
                  </a>
                </div>
              ) : (
                <iframe
                  src={pdfViewerModal.pdfUrl}
                  title={`Project Implementation Plan - ${pdfViewerModal.title}`}
                  style={{ width: '100%', height: '100%', border: 'none' }}
                  onLoad={() => setIsPdfLoading(false)}
                  onError={() => {
                    setIsPdfLoading(false);
                    setPdfLoadError('The browser could not load the PDF stream. Use the download button below.');
                  }}
                />
              )}
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          MODAL 2: DETAILED IMPLEMENTATION PLAN TEXT (PHASES A TO J)
          ========================================================================= */}
      {activePlanModal && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.75)',
            zIndex: 1050,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
          }}
          onClick={() => setActivePlanModal(null)}
        >
          <div
            className="card"
            style={{
              maxWidth: '820px',
              width: '100%',
              maxHeight: '90vh',
              overflowY: 'auto',
              padding: '26px',
              background: 'var(--bg-card)',
              position: 'relative',
              boxShadow: 'var(--shadow-lg)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '12px', marginBottom: '14px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '12px' }}>
              <div>
                <span className="badge badge-emerald" style={{ fontSize: '10.5px', marginBottom: '4px' }}>
                  Project Implementation Plan Blueprint
                </span>
                <h3 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
                  {activePlanModal.overview?.project_title || activePlanModal.project_title}
                </h3>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <button
                  className="btn btn-secondary"
                  onClick={() => {
                    const pId = activePlanModal.plan_id || 'plan_default';
                    const title = activePlanModal.overview?.project_title || activePlanModal.project_title;
                    setActivePlanModal(null);
                    handleOpenPdfViewer(pId, title);
                  }}
                  style={{ fontSize: '11.5px', padding: '5px 10px' }}
                >
                  <FileCode size={12} />
                  <span>View PDF</span>
                </button>

                <button
                  className="btn btn-secondary"
                  onClick={() => {
                    const targetProj = activePlanModal;
                    setActivePlanModal(null);
                    setActiveFlowDiagramProject(targetProj);
                  }}
                  style={{ fontSize: '11.5px', padding: '5px 10px' }}
                  title="View browser-rendered visual workflow diagram"
                >
                  <GitFork size={12} />
                  <span>View Flow Diagram</span>
                </button>

                <a
                  href={`/api/projects/download-plan/${activePlanModal.plan_id || 'plan_default'}/docx`}
                  download
                  className="btn btn-secondary"
                  style={{ fontSize: '11.5px', padding: '5px 10px', textDecoration: 'none' }}
                >
                  <Download size={12} />
                  <span>DOCX</span>
                </a>

                <button
                  className="btn btn-secondary"
                  onClick={() => setActivePlanModal(null)}
                  style={{ padding: '6px', borderRadius: '50%', border: 'none' }}
                >
                  <X size={16} />
                </button>
              </div>
            </div>

            {/* Sections A to J Body */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', fontSize: '12.5px', lineHeight: 1.5 }}>
              <div>
                <strong style={{ color: 'var(--primary)', display: 'block', fontSize: '13px' }}>A. Project Overview</strong>
                <p style={{ margin: '3px 0', color: 'var(--text-muted)' }}>
                  {activePlanModal.overview?.project_objective || activePlanModal.project_objective}
                </p>
              </div>

              <div>
                <strong style={{ color: 'var(--primary)', display: 'block', fontSize: '13px' }}>B. Skills to Be Demonstrated</strong>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '3px' }}>
                  {(activePlanModal.skills?.all_targeted_skills || activePlanModal.skills_demonstrated || []).map((s: string, i: number) => (
                    <span key={i} className="badge badge-emerald" style={{ fontSize: '10.5px' }}>{s}</span>
                  ))}
                </div>
              </div>

              <div>
                <strong style={{ color: 'var(--primary)', display: 'block', fontSize: '13px' }}>C. Technology Stack</strong>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '3px' }}>
                  {(activePlanModal.technology_stack || activePlanModal.proposed_technologies || []).map((t: string, i: number) => (
                    <span key={i} className="badge badge-subtle" style={{ fontSize: '10.5px' }}>{t}</span>
                  ))}
                </div>
              </div>

              <div>
                <strong style={{ color: 'var(--primary)', display: 'block', fontSize: '13px' }}>D. Implementation Phases</strong>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '4px' }}>
                  {(activePlanModal.phases || [
                    { title: 'Environment & Tooling Setup', objective: 'Configure hypervisor and testing tools.' },
                    { title: 'Core Security Testing Execution', objective: 'Execute testing against authorized mock targets.' },
                    { title: 'Verification & Remediation Documentation', objective: 'Document verified outcomes.' },
                  ]).map((p: any, i: number) => (
                    <div key={i} style={{ padding: '8px 12px', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-xs)', borderLeft: '3px solid var(--primary)' }}>
                      <strong>Phase {p.phase_number || i + 1}: {p.title}</strong>
                      <p style={{ margin: '2px 0 0', color: 'var(--text-muted)', fontSize: '12px' }}>{p.objective}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <strong style={{ color: 'var(--primary)', display: 'block', fontSize: '13px' }}>Resume Documentation Structure</strong>
                <div className="mono" style={{ padding: '8px 12px', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-xs)', fontSize: '11.5px', marginTop: '3px' }}>
                  • Developed and configured laboratory environment simulating real-world security scenarios.<br />
                  • Executed testing and validated security outcomes using confirmed open-source utilities.<br />
                  • Documented verified findings and published remediation notes.
                </div>
              </div>
            </div>

            <div style={{ marginTop: '18px', display: 'flex', justifyContent: 'flex-end' }}>
              <button className="btn btn-primary" onClick={() => setActivePlanModal(null)} style={{ fontSize: '12px', padding: '6px 16px' }}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          MODAL 3: OFFER TO ADD SAVED PROJECT TO RESUME DIALOG (Requirement 1)
          ========================================================================= */}
      {offerAddToResumeModal && offerAddToResumeModal.isOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(15, 23, 42, 0.65)',
            backdropFilter: 'blur(4px)',
            WebkitBackdropFilter: 'blur(4px)',
            zIndex: 1200,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
            animation: 'fadeIn 0.15s ease-out',
          }}
          onClick={() => setOfferAddToResumeModal(null)}
        >
          <div
            className="card"
            style={{
              maxWidth: '480px',
              width: '100%',
              padding: '26px 30px',
              background: 'var(--bg-card)',
              borderRadius: 'var(--radius-lg)',
              boxShadow: 'var(--shadow-lg)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <Sparkles size={20} color="var(--primary)" />
              <h3 style={{ fontSize: '17px', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
                Add this project to your resume?
              </h3>
            </div>

            <div
              style={{
                padding: '12px 14px',
                background: 'var(--bg-subtle)',
                borderRadius: 'var(--radius-sm)',
                marginBottom: '14px',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                Project
              </div>
              <div style={{ fontSize: '14.5px', fontWeight: 700, color: 'var(--text-main)', marginTop: '2px' }}>
                {offerAddToResumeModal.project.project_title}
              </div>
              <div
                style={{
                  fontSize: '11.5px',
                  color: offerAddToResumeModal.project.status === 'in_progress' ? 'var(--amber-warn)' : 'var(--emerald-success)',
                  fontWeight: 600,
                  marginTop: '3px',
                }}
              >
                Status: {offerAddToResumeModal.project.status === 'in_progress' ? 'In Progress' : 'Completed'}
              </div>
            </div>

            <p style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: 1.5, marginBottom: '22px' }}>
              Would you like to include this project in your resume for the selected cybersecurity role?
            </p>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setOfferAddToResumeModal(null)}
                style={{ fontSize: '13px', padding: '8px 18px' }}
              >
                Not Now
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => handleOfferYesAddToResume(offerAddToResumeModal.project)}
                style={{ fontSize: '13px', padding: '8px 20px', fontWeight: 700 }}
              >
                Yes, Add to Resume
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          MODAL 4: PROPOSED RESUME ENTRY REVIEW & CONFIRMATION (Requirement 1 & 2)
          ========================================================================= */}
      {proposedEntryReviewModal && proposedEntryReviewModal.isOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(15, 23, 42, 0.65)',
            backdropFilter: 'blur(4px)',
            WebkitBackdropFilter: 'blur(4px)',
            zIndex: 1250,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
            animation: 'fadeIn 0.15s ease-out',
          }}
          onClick={() => setProposedEntryReviewModal(null)}
        >
          <div
            className="card"
            style={{
              maxWidth: '560px',
              width: '100%',
              padding: '26px 30px',
              background: 'var(--bg-card)',
              borderRadius: 'var(--radius-lg)',
              boxShadow: 'var(--shadow-lg)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <h3 style={{ fontSize: '17px', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
                Review Proposed Resume Entry
              </h3>
              <span
                className={
                  proposedEntryReviewModal.proposedEntry.status_label === 'In Progress'
                    ? 'badge badge-amber'
                    : 'badge badge-emerald'
                }
                style={{ fontSize: '11px' }}
              >
                {proposedEntryReviewModal.proposedEntry.status_label === 'In Progress' ? 'In Progress' : 'Completed'}
              </span>
            </div>

            <p style={{ fontSize: '12.5px', color: 'var(--text-muted)', lineHeight: 1.45, marginBottom: '14px' }}>
              Review the proposed wording tailored to the <strong>{roleName}</strong> role. Only factual details and confirmed progress are included.
            </p>

            {/* Formatted Proposed Entry Preview */}
            <div
              style={{
                padding: '16px',
                background: 'var(--bg-subtle)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-subtle)',
                marginBottom: '16px',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
              }}
            >
              <div style={{ fontSize: '14.5px', fontWeight: 800, color: 'var(--text-main)' }}>
                {proposedEntryReviewModal.proposedEntry.title_line}
              </div>

              {proposedEntryReviewModal.project.technologies_used.length > 0 && (
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                  <strong>Technologies:</strong> {proposedEntryReviewModal.project.technologies_used.join(', ')}
                </div>
              )}

              <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', marginTop: '4px' }}>
                {proposedEntryReviewModal.proposedEntry.bullets.map((b, idx) => (
                  <div key={idx} style={{ fontSize: '12px', color: 'var(--text-main)', lineHeight: 1.45 }}>
                    • {b}
                  </div>
                ))}
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '10px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '11px', color: 'var(--text-dim)', maxWidth: '280px' }}>
                {proposedEntryReviewModal.proposedEntry.status_label === 'In Progress'
                  ? '✓ Truthful entry: Unfinished features are not claimed as completed.'
                  : '✓ Verified completed entry with candidate-reported technologies.'}
              </span>

              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setProposedEntryReviewModal(null)}
                  style={{ fontSize: '12.5px', padding: '7px 16px' }}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() =>
                    handleConfirmProposedEntry(
                      proposedEntryReviewModal.project,
                      proposedEntryReviewModal.proposedEntry,
                      proposedEntryReviewModal.isRecommended
                    )
                  }
                  style={{ fontSize: '12.5px', padding: '7px 18px', fontWeight: 700 }}
                >
                  <CheckCircle size={13} />
                  <span>Confirm & Add to Resume</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          MODAL 5: CONFIRMATION TO START RECOMMENDED PROJECT (Requirement 2)
          ========================================================================= */}
      {confirmStartRecommendedModal && primaryProjTemplate && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(15, 23, 42, 0.65)',
            backdropFilter: 'blur(4px)',
            WebkitBackdropFilter: 'blur(4px)',
            zIndex: 1200,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
            animation: 'fadeIn 0.15s ease-out',
          }}
          onClick={() => setConfirmStartRecommendedModal(false)}
        >
          <div
            className="card"
            style={{
              maxWidth: '480px',
              width: '100%',
              padding: '26px 30px',
              background: 'var(--bg-card)',
              borderRadius: 'var(--radius-lg)',
              boxShadow: 'var(--shadow-lg)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <Target size={20} color="var(--primary)" />
              <h3 style={{ fontSize: '17px', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
                Confirm Intent to Start Project
              </h3>
            </div>

            <p style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: 1.5, marginBottom: '14px' }}>
              Do you intend to start this recommended project: <strong>{primaryProjTemplate.project_title}</strong>?
            </p>

            <div
              style={{
                padding: '10px 14px',
                background: 'var(--bg-subtle)',
                borderRadius: 'var(--radius-sm)',
                borderLeft: '3px solid var(--primary)',
                marginBottom: '18px',
                fontSize: '12px',
                color: 'var(--text-dim)',
                lineHeight: 1.45,
              }}
            >
              By confirming, this project will be saved with status <strong>In Progress</strong>. FUTRSEC will formulate a truthful entry describing planned and initialized work. It will never claim completed functionality or unperformed test results.
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setConfirmStartRecommendedModal(false)}
                style={{ fontSize: '12.5px', padding: '7px 16px' }}
              >
                Cancel
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleExecuteStartRecommendedProject}
                style={{ fontSize: '12.5px', padding: '7px 20px', fontWeight: 700 }}
              >
                Yes, I Intend to Start This Project
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Enterprise SaaS Loading Experience for Resume Generation */}
      <LoadingOverlay
        isOpen={isApplying}
        operationType="create_resume"
      />

      {/* Dedicated Project Flow Diagram Modal */}
      {activeFlowDiagramProject && (
        <ProjectFlowDiagramModal
          projectTitle={activeFlowDiagramProject.overview?.project_title || activeFlowDiagramProject.project_title || 'Project Workflow'}
          domain={activeFlowDiagramProject.domain || 'Cybersecurity'}
          rawWorkflow={activeFlowDiagramProject.project_workflow}
          planPhases={activeFlowDiagramProject.phases}
          onClose={() => setActiveFlowDiagramProject(null)}
        />
      )}

      {/* Dedicated Template Preview Modal */}
      {previewTemplateModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(15, 23, 42, 0.7)',
            backdropFilter: 'blur(4px)',
            zIndex: 1300,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
          }}
          onClick={handleCloseTemplatePreview}
        >
          <div
            className="card"
            style={{
              maxWidth: '820px',
              width: '100%',
              maxHeight: '90vh',
              overflowY: 'auto',
              padding: '24px 28px',
              background: 'var(--bg-card)',
              borderRadius: 'var(--radius-lg)',
              boxShadow: 'var(--shadow-lg)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span className="badge badge-primary" style={{ fontSize: '12px', padding: '3px 8px' }}>
                  {previewTemplateModal.template_id}
                </span>
                <h3 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
                  {previewTemplateModal.template_name}
                </h3>
              </div>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleCloseTemplatePreview}
                style={{ padding: '6px 10px' }}
              >
                <X size={16} />
              </button>
            </div>

            <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '16px' }}>
              {previewTemplateModal.description}
            </p>

            {isPreviewTemplateLoading ? (
              <div style={{ padding: '60px', textAlign: 'center' }}>
                <div className="spin" style={{ width: '28px', height: '28px', border: '3px solid var(--primary)', borderTopColor: 'transparent', borderRadius: '50%', margin: '0 auto 16px' }} />
                <span>Generating live template preview...</span>
              </div>
            ) : previewTemplateError ? (
              <div style={{ padding: '30px', textAlign: 'center', color: 'var(--rose-danger)' }}>
                {previewTemplateError}
              </div>
            ) : previewTemplateData ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                <div
                  style={{
                    background: '#FFFFFF',
                    color: '#0F172A',
                    padding: '28px 36px',
                    borderRadius: '6px',
                    border: '1px solid #CBD5E1',
                    boxShadow: '0 4px 16px rgba(0,0,0,0.06)',
                    fontFamily: previewTemplateModal.style_config?.font_family || 'Calibri',
                    fontSize: '12px',
                    lineHeight: 1.4,
                  }}
                >
                  <div style={{ textAlign: previewTemplateModal.style_config?.header_alignment || 'left', marginBottom: '16px', borderBottom: '1px solid #CBD5E1', paddingBottom: '10px' }}>
                    <div style={{ fontSize: '20px', fontWeight: 800, color: '#0F172A' }}>
                      {previewTemplateData.sample_content?.candidate_name || 'ALEXANDER CHEN'}
                    </div>
                    <div style={{ fontSize: '11px', color: '#475569', marginTop: '4px' }}>
                      {previewTemplateData.sample_content?.contact_header || 'alexander@example.com | +1 (555) 345-6789 | Austin, TX'}
                    </div>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div>
                      <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: '#1E293B', borderBottom: '1px solid #E2E8F0', paddingBottom: '2px', marginBottom: '4px' }}>
                        PROFESSIONAL SUMMARY
                      </div>
                      <p style={{ margin: 0, color: '#334155' }}>
                        {previewTemplateData.sample_content?.professional_summary}
                      </p>
                    </div>

                    <div>
                      <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: '#1E293B', borderBottom: '1px solid #E2E8F0', paddingBottom: '2px', marginBottom: '4px' }}>
                        TECHNICAL SKILLS
                      </div>
                      <div style={{ color: '#334155' }}>
                        {Object.entries(previewTemplateData.sample_content?.technical_skills_grouped || {}).slice(0, 3).map(([cat, skills]: any) => (
                          <div key={cat} style={{ marginBottom: '2px' }}>
                            <strong>{cat}:</strong> {Array.isArray(skills) ? skills.join(', ') : skills}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '8px' }}>
                  <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>
                    Sample candidate data displayed. Your actual resume facts and projects will be populated upon generation.
                  </span>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={handleCloseTemplatePreview}
                    >
                      Close Preview
                    </button>
                    <button
                      type="button"
                      className="btn btn-primary"
                      onClick={() => {
                        setSelectedTemplateId(previewTemplateModal.template_id);
                        setTemplateSelectionMode('manual');
                        handleCloseTemplatePreview();
                      }}
                      style={{ fontWeight: 700 }}
                    >
                      Select This Template ({previewTemplateModal.template_id})
                    </button>
                  </div>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
};
