"""Generates high-resolution vector diagrams for the FUTRSEC Project Report.
Specifically tailored to the exact user requirements:

Diagram 1: Project Workflow Flowchart
- START
- PHASE 1: LAB SETUP (Docker Desktop, OWASP Juice Shop / DVWA on 127.0.0.1)
- PHASE 2: RECONNAISSANCE (Nmap & Burp Suite attack surface mapping)
- PHASE 3: VULNERABILITY TESTING (SQLi, XSS, IDOR)
- DECISION (Diamond): WAS THE VULNERABILITY VERIFIED?
  - NO -> Review evidence & refine testing within authorized local environment (reconnecting to testing step)
  - YES -> Record verified finding and proceed to assessment
- PHASE 4: SEVERITY ASSESSMENT AND REMEDIATION (CVSS v3.1 base scoring & developer remediation recommendations)
- FINAL REPORT (Compile security assessment report with evidence, severity ratings, remediation guidance)
- END

Diagram 2: System Architecture Diagram
Planned components:
- Ethical Hacker / Tester
- Host Computer
- Docker Desktop
- Isolated Test Environment (OWASP Juice Shop / DVWA)
Associated tools & workflow:
- Browser traffic inspection through Burp Suite Community
- Local service discovery through Nmap
- Python verification scripts
- Vulnerability evidence collection
- CVSS v3.1 severity assessment
- Developer remediation recommendations
- Final security assessment report
"""

import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUT_DIR = Path("V:/ai_jobagent/docs/final_report_diagrams")
OUT_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'


def generate_flowchart():
    fig, ax = plt.subplots(figsize=(11, 14.5), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 15)
    ax.axis('off')

    # Styles
    box_start = dict(boxstyle="round,pad=0.5", facecolor="#E2E8F0", edgecolor="#1E293B", linewidth=2.0)
    box_phase = dict(boxstyle="round,pad=0.5", facecolor="#EFF6FF", edgecolor="#1D4ED8", linewidth=1.8)
    box_recon = dict(boxstyle="round,pad=0.5", facecolor="#F0FDF4", edgecolor="#16A34A", linewidth=1.8)
    box_test = dict(boxstyle="round,pad=0.5", facecolor="#FEF2F2", edgecolor="#DC2626", linewidth=1.8)
    box_decision = dict(boxstyle="sawtooth,pad=0.6", facecolor="#FEF3C7", edgecolor="#D97706", linewidth=2.0)
    box_review = dict(boxstyle="round,pad=0.5", facecolor="#FFFBEB", edgecolor="#B45309", linewidth=1.8)
    box_assess = dict(boxstyle="round,pad=0.5", facecolor="#F5F3FF", edgecolor="#7C3AED", linewidth=1.8)
    box_report = dict(boxstyle="round,pad=0.5", facecolor="#ECFDF5", edgecolor="#059669", linewidth=2.0)

    arrow = dict(arrowstyle="->", color="#1E293B", linewidth=2.0, mutation_scale=15)
    arrow_green = dict(arrowstyle="->", color="#16A34A", linewidth=2.2, mutation_scale=16)
    arrow_red = dict(arrowstyle="->", color="#DC2626", linewidth=2.2, mutation_scale=16)
    arrow_dash = dict(arrowstyle="->", color="#B45309", linewidth=1.8, linestyle="--", mutation_scale=14)

    # 1. START
    ax.text(5.5, 14.3, "START", ha="center", va="center", bbox=box_start, fontsize=12, weight="bold", color="#0F172A")

    # 2. PHASE 1: LAB SETUP
    p1 = (
        "PHASE 1: LAB SETUP\n"
        "Configure Docker Desktop and deploy OWASP Juice Shop or DVWA\n"
        "in an isolated local environment strictly bound to localhost (127.0.0.1:3000)."
    )
    ax.text(5.5, 12.8, p1, ha="center", va="center", bbox=box_phase, fontsize=9.5)

    # 3. PHASE 2: RECONNAISSANCE
    p2 = (
        "PHASE 2: RECONNAISSANCE\n"
        "Use Nmap and Burp Suite to map the attack surface of the authorized local target.\n"
        "Enumerate open ports, exposed endpoints, API routes, and user input fields."
    )
    ax.text(5.5, 10.9, p2, ha="center", va="center", bbox=box_recon, fontsize=9.5)

    # 4. PHASE 3: VULNERABILITY TESTING
    p3 = (
        "PHASE 3: VULNERABILITY TESTING\n"
        "Assess SQL Injection (SQLi), Cross-Site Scripting (XSS), and IDOR.\n"
        "Execute manual probe requests and evaluate application responses."
    )
    ax.text(5.5, 9.0, p3, ha="center", va="center", bbox=box_test, fontsize=9.5)

    # 5. DECISION DIAMOND
    ax.text(5.5, 6.9, "DECISION:\nWAS THE VULNERABILITY\nVERIFIED?", ha="center", va="center", bbox=box_decision, fontsize=10.5, weight="bold", color="#78350F")

    # NO REVIEW BOX (Left)
    rev_text = (
        "Review evidence and\nrefine testing within the\nauthorized local environment.\n"
        "• Check encoding & WAF\n"
        "• Verify parameters\n"
        "• Refine payload syntax"
    )
    ax.text(1.8, 6.9, rev_text, ha="center", va="center", bbox=box_review, fontsize=8.5)

    # 6. PHASE 4: SEVERITY ASSESSMENT AND REMEDIATION
    p4 = (
        "PHASE 4: SEVERITY ASSESSMENT AND REMEDIATION\n"
        "Apply CVSS v3.1 assessment to verified findings and\n"
        "develop concrete code-level remediation recommendations."
    )
    ax.text(5.5, 4.7, p4, ha="center", va="center", bbox=box_assess, fontsize=9.5)

    # 7. FINAL REPORT
    p5 = (
        "FINAL REPORT\n"
        "Compile the security assessment report with evidence, severity ratings,\n"
        "Python verification scripts, and developer remediation guidance."
    )
    ax.text(5.5, 2.7, p5, ha="center", va="center", bbox=box_report, fontsize=9.5, weight="bold")

    # 8. END
    ax.text(5.5, 1.1, "END", ha="center", va="center", bbox=box_start, fontsize=12, weight="bold", color="#0F172A")

    # Sequential Arrows
    ax.annotate("", xy=(5.5, 13.5), xytext=(5.5, 13.9), arrowprops=arrow)
    ax.annotate("", xy=(5.5, 11.6), xytext=(5.5, 12.0), arrowprops=arrow)
    ax.annotate("", xy=(5.5, 9.7), xytext=(5.5, 10.1), arrowprops=arrow)
    ax.annotate("", xy=(5.5, 7.7), xytext=(5.5, 8.2), arrowprops=arrow)

    # Decision: YES branch (Down to Phase 4)
    ax.annotate("", xy=(5.5, 5.4), xytext=(5.5, 6.1), arrowprops=arrow_green)
    ax.text(5.7, 5.8, "YES (Record verified finding)", ha="left", va="center", fontsize=9.5, color="#15803D", weight="bold")

    # Decision: NO branch (Left to Review Box)
    ax.annotate("", xy=(3.1, 6.9), xytext=(4.1, 6.9), arrowprops=arrow_red)
    ax.text(3.6, 7.1, "NO", ha="center", va="bottom", fontsize=10, color="#DC2626", weight="bold")

    # Loop back from Review Box to Phase 3
    ax.annotate("", xy=(1.8, 9.0), xytext=(1.8, 7.9), arrowprops=dict(arrowstyle="-", color="#B45309", linewidth=1.8, linestyle="--"))
    ax.annotate("", xy=(3.0, 9.0), xytext=(1.8, 9.0), arrowprops=arrow_dash)
    ax.text(1.9, 8.5, "Re-evaluate &\nRefine Payload", ha="left", va="center", fontsize=8.5, color="#B45309", style="italic")

    # Down to Final Report & End
    ax.annotate("", xy=(5.5, 3.4), xytext=(5.5, 4.0), arrowprops=arrow)
    ax.annotate("", xy=(5.5, 1.5), xytext=(5.5, 2.0), arrowprops=arrow)

    # Figure Title
    ax.text(5.5, 14.8, "FIGURE 1: Web Application Security Testing Lab — Execution Workflow Flowchart", ha="center", va="center", fontsize=11, weight="bold", color="#1E293B")

    plt.tight_layout()
    plt.savefig(OUT_DIR / "fig1_workflow_flowchart.png", dpi=300)
    plt.close()
    print("Generated fig1_workflow_flowchart.png in final_report_diagrams/")


def generate_architecture():
    fig, ax = plt.subplots(figsize=(13, 9.5), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Bounding Boxes
    host_patch = patches.FancyBboxPatch((0.5, 3.2), 12.0, 5.8, boxstyle="round,pad=0.3", facecolor="#F8FAFC", edgecolor="#334155", linewidth=2.0)
    docker_patch = patches.FancyBboxPatch((7.6, 3.6), 4.6, 4.4, boxstyle="round,pad=0.3", facecolor="#F0FDF4", edgecolor="#16A34A", linewidth=1.8, linestyle="--")
    report_patch = patches.FancyBboxPatch((0.5, 0.4), 12.0, 2.3, boxstyle="round,pad=0.3", facecolor="#F5F3FF", edgecolor="#6D28D9", linewidth=1.8)

    ax.add_patch(host_patch)
    ax.add_patch(docker_patch)
    ax.add_patch(report_patch)

    ax.text(0.8, 8.7, "HOST COMPUTER (Physical Workstation Environment)", fontsize=11, weight="bold", color="#1E293B")
    ax.text(7.9, 7.6, "DOCKER DESKTOP ISOLATION", fontsize=9.5, weight="bold", color="#15803D")
    ax.text(0.8, 2.3, "ASSESSMENT DELIVERABLES & REPORTING PIPELINE", fontsize=11, weight="bold", color="#5B21B6")

    b_actor = dict(boxstyle="round,pad=0.4", facecolor="#FFFFFF", edgecolor="#1D4ED8", linewidth=1.8)
    b_tool = dict(boxstyle="round,pad=0.4", facecolor="#FFFFFF", edgecolor="#0284C7", linewidth=1.6)
    b_target = dict(boxstyle="round,pad=0.5", facecolor="#DCFCE7", edgecolor="#15803D", linewidth=2.0)
    b_deliv = dict(boxstyle="round,pad=0.4", facecolor="#FFFFFF", edgecolor="#7C3AED", linewidth=1.6)

    arrow_bi = dict(arrowstyle="<->", color="#1E293B", linewidth=1.8, mutation_scale=12)
    arrow_fwd = dict(arrowstyle="->", color="#1E293B", linewidth=1.8, mutation_scale=12)

    # Host Components
    ax.text(2.0, 7.3, "ETHICAL HACKER\n(Security Tester)", ha="center", va="center", bbox=b_actor, fontsize=10, weight="bold")
    ax.text(2.0, 5.2, "Browser (Chromium)\n(Configured Proxy:\n127.0.0.1:8080)", ha="center", va="center", bbox=b_tool, fontsize=9)
    ax.text(5.0, 5.2, "Burp Suite Community\n• HTTP Intercepting Proxy\n• Repeater & Decoder\n• Attack Surface Sitemap", ha="center", va="center", bbox=b_tool, fontsize=8.5, weight="bold")
    ax.text(5.0, 7.4, "Nmap Security Scanner\nLocal service discovery &\nport enumeration on 127.0.0.1", ha="center", va="center", bbox=b_tool, fontsize=8.5)
    ax.text(2.0, 3.8, "Python Verification Scripts\n(Reproducible HTTP Proofs-of-Concept)", ha="center", va="center", bbox=b_tool, fontsize=8.5)

    # Docker Isolated Target
    target_text = (
        "ISOLATED TEST ENVIRONMENT\n"
        "OWASP Juice Shop / DVWA\n"
        "• Containerized web application\n"
        "• Bound strictly to 127.0.0.1:3000\n"
        "• No external network routing\n"
        "• Safe sandbox for SQLi, XSS, IDOR"
    )
    ax.text(9.9, 5.6, target_text, ha="center", va="center", bbox=b_target, fontsize=9.5, weight="bold")

    # Connectors Host to Docker Target
    ax.annotate("", xy=(2.0, 5.9), xytext=(2.0, 6.7), arrowprops=arrow_bi)
    ax.annotate("", xy=(3.6, 5.2), xytext=(2.9, 5.2), arrowprops=arrow_bi)
    ax.annotate("", xy=(7.7, 5.5), xytext=(6.5, 5.5), arrowprops=arrow_bi)
    ax.text(7.1, 5.7, "HTTP Interception", ha="center", va="bottom", fontsize=8.5, weight="bold")

    ax.annotate("", xy=(7.7, 6.5), xytext=(6.4, 7.4), arrowprops=arrow_fwd)
    ax.text(7.1, 7.1, "Nmap Scans", ha="center", va="bottom", fontsize=8, color="#15803D")

    ax.annotate("", xy=(7.7, 4.4), xytext=(3.9, 3.8), arrowprops=arrow_fwd)
    ax.text(5.6, 3.9, "Automated PoC Requests", ha="center", va="bottom", fontsize=8, color="#0284C7")

    # Assessment Deliverables Layer
    ax.text(2.0, 1.3, "Vulnerability Evidence\n(Raw HTTP Requests,\nResponses & Server Logs)", ha="center", va="center", bbox=b_deliv, fontsize=8.5)
    ax.text(5.0, 1.3, "CVSS v3.1 Assessment\n(Base Metrics: AV, AC,\nPR, UI, Scope, CIA Impact)", ha="center", va="center", bbox=b_deliv, fontsize=8.5)
    ax.text(8.0, 1.3, "Developer Remediation\n(Parameterized Queries,\nEncoding, Access Controls)", ha="center", va="center", bbox=b_deliv, fontsize=8.5)
    ax.text(11.0, 1.3, "Final Security Report\n(Comprehensive Technical &\nExecutive Assessment)", ha="center", va="center", bbox=b_deliv, fontsize=8.5, weight="bold")

    # Connectors from Tools to Deliverables
    ax.annotate("", xy=(2.0, 2.0), xytext=(2.0, 3.3), arrowprops=arrow_fwd)
    ax.annotate("", xy=(5.0, 2.0), xytext=(5.0, 3.2), arrowprops=arrow_fwd)
    ax.annotate("", xy=(8.0, 2.0), xytext=(8.0, 3.2), arrowprops=arrow_fwd)
    ax.annotate("", xy=(11.0, 2.0), xytext=(10.5, 3.6), arrowprops=arrow_fwd)

    ax.text(6.5, 9.6, "FIGURE 2: Web Application Security Testing Lab — Planned System Architecture & Assessment Flow", ha="center", va="center", fontsize=11, weight="bold", color="#1E293B")

    plt.tight_layout()
    plt.savefig(OUT_DIR / "fig2_system_architecture.png", dpi=300)
    plt.close()
    print("Generated fig2_system_architecture.png in final_report_diagrams/")


if __name__ == "__main__":
    generate_flowchart()
    generate_architecture()
    print("All final report diagrams generated successfully.")

