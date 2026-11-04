"""Generates crisp, high-resolution, professional academic-grade technical diagrams for the FUTRSEC Project Report.

Outputs:
1. fig1_workflow_flowchart.png: End-to-end user and data pipeline.
2. fig2_system_architecture.png: Multi-tier architectural view (Frontend, FastAPI, Neon DB, Stage 1 Gemini, Stage 2 Groq/Heuristic, Rendering).
3. fig3_deterministic_scoring.png: Mathematical category weights and ATS evaluation engine.
4. fig4_round_robin_scheduler.png: Persistent 20-template rotation cycle & concurrency lock.
5. fig5_certification_preservation.png: Strict factual retention and validation pipeline.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

# Ensure output directory exists
out_dir = Path("docs/diagrams")
out_dir.mkdir(parents=True, exist_ok=True)

# Common styling parameters
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'


def generate_workflow_flowchart():
    fig, ax = plt.subplots(figsize=(12, 10), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 11)
    ax.axis('off')

    # Styles
    box_blue = dict(boxstyle="round,pad=0.5", facecolor="#EBF3FB", edgecolor="#1E40AF", linewidth=1.8)
    box_green = dict(boxstyle="round,pad=0.5", facecolor="#ECFDF5", edgecolor="#065F46", linewidth=1.8)
    box_amber = dict(boxstyle="round,pad=0.5", facecolor="#FFFBEB", edgecolor="#B45309", linewidth=1.8)
    box_purple = dict(boxstyle="round,pad=0.5", facecolor="#F5F3FF", edgecolor="#5B21B6", linewidth=1.8)
    box_decision = dict(boxstyle="sawtooth,pad=0.5", facecolor="#FEF3C7", edgecolor="#D97706", linewidth=1.8)
    box_db = dict(boxstyle="round,pad=0.4", facecolor="#F1F5F9", edgecolor="#334155", linewidth=1.8)

    arrow = dict(arrowstyle="->", color="#1E293B", linewidth=2.0, mutation_scale=15)
    arrow_dashed = dict(arrowstyle="->", color="#64748B", linewidth=1.8, linestyle="--", mutation_scale=15)

    # 1. Start / Upload
    ax.text(2.5, 10.2, "1. Candidate Resume Upload\n(PDF / DOCX up to 10MB)", ha="center", va="center", bbox=box_blue, fontsize=10, weight="bold")
    ax.text(8.5, 10.2, "Target Cybersecurity Role\n(Selected from 74 Roles)", ha="center", va="center", bbox=box_blue, fontsize=10, weight="bold")

    # 2. Secure Ingestion & Parsing
    ax.text(2.5, 8.8, "2. Security & Ingestion Defuser\n- Magic-byte verification\n- Prompt-injection neutralizer", ha="center", va="center", bbox=box_amber, fontsize=9.5)
    ax.text(8.5, 8.8, "Neon Serverless PostgreSQL\n- 74 Roles, 1,425 Skills\n- 370 Weighted Criteria", ha="center", va="center", bbox=box_db, fontsize=9.5)

    # 3. Resume Extractor
    ax.text(2.5, 7.3, "3. ResumeExtractor (Deterministic)\n- Contact details & headline\n- Skills, Education & Experience\n- Original Certifications retained", ha="center", va="center", bbox=box_blue, fontsize=9.5)

    # 4. Deterministic Scoring Engine
    ax.text(5.5, 6.0, "4. Deterministic ATS Scoring Engine\nStrict mathematical weighting (0 - 100):\nTechnical Skills (40%) | Projects (25%)\nEducation (15%) | Certs & Tools (15%) | Objective (5%)", ha="center", va="center", bbox=box_green, fontsize=10, weight="bold")

    # 5. Threshold Decision Node
    ax.text(5.5, 4.4, "ATS Score >= 80.0 Cutoff?", ha="center", va="center", bbox=box_decision, fontsize=10.5, weight="bold")

    # Path A: Score >= 80
    ax.text(10.2, 4.4, "PASSED (>= 80)\nDirect Progression to\nInterview / Application", ha="center", va="center", bbox=box_green, fontsize=9.5, weight="bold")

    # Path B: Score < 80 -> AI Improvement Studio
    ax.text(5.5, 2.9, "5. AI Analysis & Candidate Approval Studio\n- Stage 1: Google Gemini 3.6 Flash (Gap identification & project appraisal)\n- Interactive UI: Candidate confirms practical skills & projects\n- Stage 2: GroqCloud (openai/gpt-oss-120b) / Rule-based Enhancer", ha="center", va="center", bbox=box_purple, fontsize=9.5)

    # 6. Template Rotation & Rendering
    ax.text(5.5, 1.4, "6. Persistent Round Robin Template Scheduler & Rendering\n- Atomic sequential selection across 20 black-and-white templates (T01 - T20)\n- Strict factual sanitization (no hallucinated credentials or fake projects)\n- Renders matching editable DOCX and selectable vector PDF", ha="center", va="center", bbox=box_blue, fontsize=9.5, weight="bold")

    # 7. Automatic Rescoring
    ax.text(5.5, 0.25, "7. Automatic Re-Scoring & Score Delta Presentation\nImmediate deterministic re-evaluation against same Neon role criteria", ha="center", va="center", bbox=box_green, fontsize=9.5)

    # Arrows
    ax.annotate("", xy=(2.5, 8.2), xytext=(2.5, 9.6), arrowprops=arrow)
    ax.annotate("", xy=(2.5, 6.6), xytext=(2.5, 7.9), arrowprops=arrow)
    ax.annotate("", xy=(5.5, 5.25), xytext=(2.5, 6.6), arrowprops=arrow)
    ax.annotate("", xy=(5.5, 5.25), xytext=(8.5, 8.2), arrowprops=arrow_dashed)

    ax.annotate("", xy=(5.5, 4.8), xytext=(5.5, 5.35), arrowprops=arrow)
    
    # Decision arrows
    ax.annotate("", xy=(9.0, 4.4), xytext=(7.1, 4.4), arrowprops=arrow)
    ax.text(7.9, 4.6, "Yes (>= 80)", ha="center", va="bottom", fontsize=9, color="#065F46", weight="bold")

    ax.annotate("", xy=(5.5, 3.6), xytext=(5.5, 4.0), arrowprops=arrow)
    ax.text(5.7, 3.8, "No (< 80)", ha="left", va="center", fontsize=9, color="#B45309", weight="bold")

    ax.annotate("", xy=(5.5, 2.05), xytext=(5.5, 2.45), arrowprops=arrow)
    ax.annotate("", xy=(5.5, 0.6), xytext=(5.5, 0.95), arrowprops=arrow)

    # Loop back arrow from automatic rescoring to threshold
    ax.annotate("", xy=(0.8, 4.4), xytext=(0.8, 0.25), arrowprops=dict(arrowstyle="-", color="#64748B", linewidth=1.5, linestyle="--"))
    ax.annotate("", xy=(0.8, 0.25), xytext=(3.1, 0.25), arrowprops=dict(arrowstyle="-", color="#64748B", linewidth=1.5, linestyle="--"))
    ax.annotate("", xy=(4.0, 4.4), xytext=(0.8, 4.4), arrowprops=arrow_dashed)
    ax.text(1.2, 2.5, "Re-evaluation loop\n(Max 3 attempts)", ha="center", va="center", fontsize=8.5, color="#64748B", style="italic")

    plt.tight_layout()
    plt.savefig(out_dir / "fig1_workflow_flowchart.png", dpi=300)
    plt.close()
    print("Generated fig1_workflow_flowchart.png")


def generate_system_architecture():
    fig, ax = plt.subplots(figsize=(13, 9), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 9)
    ax.axis('off')

    # Bounding boxes for tiers
    tier_frontend = patches.FancyBboxPatch((0.5, 6.2), 12.0, 2.4, boxstyle="round,pad=0.3", facecolor="#F8FAFC", edgecolor="#94A3B8", linewidth=1.5, linestyle="--")
    tier_backend = patches.FancyBboxPatch((0.5, 2.6), 12.0, 3.2, boxstyle="round,pad=0.3", facecolor="#F1F5F9", edgecolor="#64748B", linewidth=1.5, linestyle="--")
    tier_data_ai = patches.FancyBboxPatch((0.5, 0.3), 12.0, 2.0, boxstyle="round,pad=0.3", facecolor="#F8FAFC", edgecolor="#94A3B8", linewidth=1.5, linestyle="--")

    ax.add_patch(tier_frontend)
    ax.add_patch(tier_backend)
    ax.add_patch(tier_data_ai)

    ax.text(0.8, 8.3, "PRESENTATION TIER (React 18 + TypeScript + Vite + Dark Mode UI)", fontsize=10.5, weight="bold", color="#1E293B")
    ax.text(0.8, 5.5, "APPLICATION TIER (FastAPI + Python 3.12 Engine)", fontsize=10.5, weight="bold", color="#1E293B")
    ax.text(0.8, 2.0, "DATA & HOSTED AI TIER (Neon PostgreSQL & LLM Providers)", fontsize=10.5, weight="bold", color="#1E293B")

    box_fe = dict(boxstyle="round,pad=0.4", facecolor="#FFFFFF", edgecolor="#3B82F6", linewidth=1.5)
    box_be = dict(boxstyle="round,pad=0.4", facecolor="#FFFFFF", edgecolor="#10B981", linewidth=1.5)
    box_ext = dict(boxstyle="round,pad=0.4", facecolor="#FFFFFF", edgecolor="#8B5CF6", linewidth=1.5)
    arrow = dict(arrowstyle="<->", color="#334155", linewidth=1.6, mutation_scale=12)

    # Frontend components
    ax.text(2.3, 7.2, "Role Selector &\nRequirements View", ha="center", va="center", bbox=box_fe, fontsize=9)
    ax.text(5.0, 7.2, "Resume Upload &\nValidation Dropzone", ha="center", va="center", bbox=box_fe, fontsize=9)
    ax.text(7.7, 7.2, "ATS Score & Skill\nGap Dashboard", ha="center", va="center", bbox=box_fe, fontsize=9)
    ax.text(10.7, 7.2, "Candidate Approval Studio &\nDocument Preview (PDF/DOCX)", ha="center", va="center", bbox=box_fe, fontsize=9)

    # Backend components
    ax.text(2.0, 4.3, "REST API Endpoints\n(/api/roles, /api/resumes/analyze,\n/api/resumes/improve)", ha="center", va="center", bbox=box_be, fontsize=8.5, weight="bold")
    ax.text(4.7, 4.3, "Parsing & Ingestion Engine\n- Magic-byte validator\n- Injection defuser\n- Regex structured extractor", ha="center", va="center", bbox=box_be, fontsize=8.5)
    ax.text(7.6, 4.3, "Scoring & Gap Engine\n- Deterministic Python scorer\n- 5 weighted categories\n- Neon criteria evaluator", ha="center", va="center", bbox=box_be, fontsize=8.5)
    ax.text(10.8, 4.3, "Template & Renderer Engine\n- Persistent Round Robin (T01-T20)\n- python-docx & PyMuPDF (fitz)\n- Strict ATS black & white styling", ha="center", va="center", bbox=box_be, fontsize=8.5)

    ax.text(6.3, 3.2, "ResumeContentValidator: Strict Factual Guardrails, Anti-Hallucination, Certification & Project Reconciliation", ha="center", va="center", bbox=dict(boxstyle="round,pad=0.3", facecolor="#FEF3C7", edgecolor="#D97706", linewidth=1.4), fontsize=8.5, weight="bold")

    # Data & AI components
    ax.text(2.3, 1.1, "Neon PostgreSQL\nServerless Cloud DB\n(74 Roles, 1,425 Skills, 370 Weights)", ha="center", va="center", bbox=box_ext, fontsize=8.5)
    ax.text(5.8, 1.1, "AI Stage 1: Google Gemini API\nModel: gemini-3.6-flash\n(Evidence gaps & project appraisal)", ha="center", va="center", bbox=box_ext, fontsize=8.5)
    ax.text(9.5, 1.1, "AI Stage 2: GroqCloud LLM\nModel: openai/gpt-oss-120b\n(Resume phrasing + Rule-based fallback)", ha="center", va="center", bbox=box_ext, fontsize=8.5)

    # Connecting Arrows
    ax.annotate("", xy=(2.3, 5.0), xytext=(2.3, 6.5), arrowprops=arrow)
    ax.annotate("", xy=(5.0, 5.0), xytext=(5.0, 6.5), arrowprops=arrow)
    ax.annotate("", xy=(7.7, 5.0), xytext=(7.7, 6.5), arrowprops=arrow)
    ax.annotate("", xy=(10.7, 5.0), xytext=(10.7, 6.5), arrowprops=arrow)

    ax.annotate("", xy=(2.3, 1.8), xytext=(2.3, 3.7), arrowprops=arrow)
    ax.annotate("", xy=(5.8, 1.8), xytext=(5.8, 2.8), arrowprops=arrow)
    ax.annotate("", xy=(9.5, 1.8), xytext=(9.5, 2.8), arrowprops=arrow)

    plt.tight_layout()
    plt.savefig(out_dir / "fig2_system_architecture.png", dpi=300)
    plt.close()
    print("Generated fig2_system_architecture.png")


def generate_scoring_pie():
    fig, ax = plt.subplots(figsize=(7, 6), dpi=300)
    
    categories = [
        'Technical Skills & Taxonomy\n(40%)',
        'Practical Security Projects\n(25%)',
        'Academic Education\n(15%)',
        'Certifications & Security Tools\n(15%)',
        'Professional Summary / Objective\n(5%)'
    ]
    weights = [40, 25, 15, 15, 5]
    colors = ['#1E3A8A', '#0D9488', '#2563EB', '#D97706', '#64748B']
    explode = (0.05, 0.03, 0, 0, 0)

    wedges, texts, autotexts = ax.pie(
        weights, 
        explode=explode, 
        labels=categories, 
        autopct='%1.0f%%',
        pctdistance=0.75,
        startangle=140, 
        colors=colors,
        textprops=dict(color="#0F172A", fontsize=9.5, weight="bold")
    )

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_weight('bold')
        autotext.set_fontsize(10)

    ax.set_title("Deterministic ATS Scoring Weight Distribution\n(Authoritative Neon PostgreSQL Criteria)", fontsize=11.5, weight="bold", pad=15)
    plt.tight_layout()
    plt.savefig(out_dir / "fig3_deterministic_scoring.png", dpi=300)
    plt.close()
    print("Generated fig3_deterministic_scoring.png")


def generate_round_robin_diagram():
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.5)
    ax.axis('off')

    # Draw template circular rotation
    center_x, center_y = 5.0, 2.8
    circle = patches.Circle((center_x, center_y), 2.0, fill=False, edgecolor="#0284C7", linewidth=2.5, linestyle=":")
    ax.add_patch(circle)

    # 4 cardinal nodes on rotation
    node_box = dict(boxstyle="round,pad=0.4", facecolor="#F0F9FF", edgecolor="#0284C7", linewidth=1.6)
    ax.text(5.0, 4.9, "T01: Professional Classic\n(Calibri, Centered, Solid Rule)", ha="center", va="center", bbox=node_box, fontsize=8.5, weight="bold")
    ax.text(7.6, 2.8, "T05: Cyber Professional\n(Aptos, Left-Aligned)", ha="center", va="center", bbox=node_box, fontsize=8.5, weight="bold")
    ax.text(5.0, 0.7, "T10: Certification Focus\n(Times New Roman, Centered)", ha="center", va="center", bbox=node_box, fontsize=8.5, weight="bold")
    ax.text(2.4, 2.8, "T20: Senior Professional\n(Wraparound back to T01)", ha="center", va="center", bbox=node_box, fontsize=8.5, weight="bold")

    # Center box explaining persistent state
    center_box = dict(boxstyle="square,pad=0.5", facecolor="#FEF3C7", edgecolor="#D97706", linewidth=1.8)
    ax.text(center_x, center_y, "RoundRobinScheduler\nPersistent Cursor File:\nround_robin_state.json\nThreading RLock Guarded", ha="center", va="center", bbox=center_box, fontsize=8.5, weight="bold")

    # Direction arrows on circle
    ax.annotate("", xy=(6.5, 4.2), xytext=(6.2, 4.4), arrowprops=dict(arrowstyle="->", color="#0284C7", linewidth=2.5, mutation_scale=15))
    ax.annotate("", xy=(7.2, 1.8), xytext=(7.4, 2.1), arrowprops=dict(arrowstyle="->", color="#0284C7", linewidth=2.5, mutation_scale=15))
    ax.annotate("", xy=(3.5, 1.4), xytext=(3.8, 1.2), arrowprops=dict(arrowstyle="->", color="#0284C7", linewidth=2.5, mutation_scale=15))
    ax.annotate("", xy=(2.8, 3.8), xytext=(2.6, 3.5), arrowprops=dict(arrowstyle="->", color="#0284C7", linewidth=2.5, mutation_scale=15))

    ax.text(5.0, 5.35, "20 Distinct Black-and-White ATS Resume Layouts in Sequential Cyclic Rotation", ha="center", va="center", fontsize=10.5, weight="bold", color="#0F172A")

    plt.tight_layout()
    plt.savefig(out_dir / "fig4_round_robin_scheduler.png", dpi=300)
    plt.close()
    print("Generated fig4_round_robin_scheduler.png")


def generate_certification_pipeline():
    fig, ax = plt.subplots(figsize=(11, 4.8), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4.8)
    ax.axis('off')

    b_step = dict(boxstyle="round,pad=0.4", facecolor="#F8FAFC", edgecolor="#334155", linewidth=1.5)
    b_gold = dict(boxstyle="round,pad=0.4", facecolor="#ECFDF5", edgecolor="#059669", linewidth=1.8)
    arrow = dict(arrowstyle="->", color="#1E293B", linewidth=1.8, mutation_scale=12)

    ax.text(1.2, 3.5, "1. Source Resume\n(PDF/DOCX Upload)", ha="center", va="center", bbox=b_step, fontsize=8.5)
    ax.text(3.6, 3.5, "2. Regex & Heading Parser\n(ResumeExtractor._extract_certifications)", ha="center", va="center", bbox=b_step, fontsize=8.5)
    ax.text(6.0, 3.5, "3. Structured Data Model\n(ParsedResumeData.certifications)", ha="center", va="center", bbox=b_gold, fontsize=8.5, weight="bold")
    ax.text(8.5, 3.5, "4. AI Improvement Isolation\n(LLM prohibited from dropping certs)", ha="center", va="center", bbox=b_step, fontsize=8.5)
    ax.text(9.9, 1.6, "5. ResumeContentValidator\n(Strips coding platforms &\ndeduplicates credentials)", ha="center", va="center", bbox=b_step, fontsize=8.5)
    ax.text(5.5, 1.6, "6. EnhancedResumeContent Model\n(Verified original certs strictly passed)", ha="center", va="center", bbox=b_gold, fontsize=8.5, weight="bold")
    ax.text(1.2, 1.6, "7. DOCX & PDF Renderers\n(Appears in 'CERTIFICATIONS'\nsection across all 20 templates)", ha="center", va="center", bbox=b_gold, fontsize=8.5, weight="bold")

    ax.annotate("", xy=(2.3, 3.5), xytext=(4.9, 3.5), arrowprops=arrow)
    ax.annotate("", xy=(4.8, 3.5), xytext=(2.4, 3.5), arrowprops=arrow)
    ax.annotate("", xy=(7.2, 3.5), xytext=(4.8, 3.5), arrowprops=arrow)
    ax.annotate("", xy=(9.4, 3.5), xytext=(7.2, 3.5), arrowprops=arrow)
    ax.annotate("", xy=(9.9, 2.4), xytext=(9.9, 2.8), arrowprops=arrow)
    ax.annotate("", xy=(7.4, 1.6), xytext=(8.7, 1.6), arrowprops=arrow)
    ax.annotate("", xy=(3.0, 1.6), xytext=(3.9, 1.6), arrowprops=arrow)

    ax.text(5.5, 4.4, "End-to-End Original Resume Certification Preservation Pipeline", ha="center", va="center", fontsize=10.5, weight="bold", color="#0F172A")
    ax.text(5.5, 0.4, "Guarantees zero certification loss, zero fabrication, and exact original credential reproduction in final documents.", ha="center", va="center", fontsize=8.5, style="italic", color="#475569")

    plt.tight_layout()
    plt.savefig(out_dir / "fig5_certification_preservation.png", dpi=300)
    plt.close()
    print("Generated fig5_certification_preservation.png")


if __name__ == "__main__":
    generate_workflow_flowchart()
    generate_system_architecture()
    generate_scoring_pie()
    generate_round_robin_diagram()
    generate_certification_pipeline()
    print("All professional report diagrams generated successfully in docs/diagrams/")

