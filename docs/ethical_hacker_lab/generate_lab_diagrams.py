"""Generates professional 300-DPI technical diagrams specifically for the project report:
'Web Application Security Testing Lab & Vulnerability Remediation'
Target Role: Ethical Hacker | Domain: Cybersecurity

Diagrams:
1. fig1_project_workflow_flowchart.png: The required complete project lifecycle with Decision Node & Reconnect.
2. fig2_system_architecture_lab.png: Component architecture (Tester, Host, Docker, Target, Burp, Nmap, Python, CVSS, Reports).
3. fig3_vulnerability_verification_cycle.png: Vulnerability discovery, evidence collection, and verification flow.
"""

import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

out_dir = Path("docs/ethical_hacker_lab")
out_dir.mkdir(parents=True, exist_ok=True)

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'


def generate_flowchart():
    fig, ax = plt.subplots(figsize=(12, 14), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 14)
    ax.axis('off')

    # Styles
    box_start = dict(boxstyle="round,pad=0.5", facecolor="#E2E8F0", edgecolor="#334155", linewidth=2.0)
    box_phase = dict(boxstyle="round,pad=0.5", facecolor="#EFF6FF", edgecolor="#1D4ED8", linewidth=1.8)
    box_recon = dict(boxstyle="round,pad=0.5", facecolor="#F0FDF4", edgecolor="#15803D", linewidth=1.8)
    box_vuln = dict(boxstyle="round,pad=0.5", facecolor="#FEF2F2", edgecolor="#B91C1C", linewidth=1.8)
    box_decision = dict(boxstyle="sawtooth,pad=0.5", facecolor="#FEF3C7", edgecolor="#D97706", linewidth=1.8)
    box_review = dict(boxstyle="round,pad=0.5", facecolor="#FFFBEB", edgecolor="#B45309", linewidth=1.6)
    box_report = dict(boxstyle="round,pad=0.5", facecolor="#F5F3FF", edgecolor="#6D28D9", linewidth=1.8)
    box_deliverables = dict(boxstyle="round,pad=0.5", facecolor="#ECFDF5", edgecolor="#047857", linewidth=2.0)

    arrow = dict(arrowstyle="->", color="#1E293B", linewidth=2.0, mutation_scale=15)
    arrow_red = dict(arrowstyle="->", color="#DC2626", linewidth=2.0, mutation_scale=15)
    arrow_green = dict(arrowstyle="->", color="#16A34A", linewidth=2.0, mutation_scale=15)

    # 1. START
    ax.text(6.0, 13.5, "START", ha="center", va="center", bbox=box_start, fontsize=11, weight="bold", color="#0F172A")

    # 2. PHASE 1
    p1_text = (
        "PHASE 1: LAB SETUP AND TARGET ISOLATION\n"
        "• Configure Docker Desktop on local workstation\n"
        "• Deploy authorized vulnerable target (OWASP Juice Shop / DVWA)\n"
        "• Verify local target accessibility on localhost port (e.g. 3000 / 80)"
    )
    ax.text(6.0, 12.0, p1_text, ha="center", va="center", bbox=box_phase, fontsize=9.5)

    # 3. PHASE 2
    p2_text = (
        "PHASE 2: RECONNAISSANCE AND ATTACK SURFACE MAPPING\n"
        "• Scan authorized local target using Nmap (service discovery, open ports)\n"
        "• Map web application endpoints via Burp Suite proxy and manual browser navigation\n"
        "• Document application routes, inputs, query parameters, and form fields"
    )
    ax.text(6.0, 10.1, p2_text, ha="center", va="center", bbox=box_recon, fontsize=9.5)

    # 4. PHASE 3
    p3_text = (
        "PHASE 3: VULNERABILITY DISCOVERY AND VERIFICATION\n"
        "• Assess SQL Injection (SQLi) in authentication and search parameters\n"
        "• Test for Cross-Site Scripting (XSS) (Reflected and Stored vectors)\n"
        "• Assess Insecure Direct Object References (IDOR) on user resources\n"
        "• Collect relevant request/response evidence and HTTP transaction logs"
    )
    ax.text(6.0, 8.1, p3_text, ha="center", va="center", bbox=box_vuln, fontsize=9.5)

    # 5. DECISION
    ax.text(6.0, 6.2, "DECISION:\nWAS THE VULNERABILITY VERIFIED?", ha="center", va="center", bbox=box_decision, fontsize=10.5, weight="bold")

    # NO Branch -> Review Box
    review_text = (
        "NO: Evidence Review &\nTest Refinement\n"
        "• Review request/response\n"
        "• Check WAF/encoding\n"
        "• Refine payload within\n  authorized lab target"
    )
    ax.text(1.8, 6.2, review_text, ha="center", va="center", bbox=box_review, fontsize=8.5)

    # 6. PHASE 4
    p4_text = (
        "PHASE 4: REMEDIATION ANALYSIS AND REPORTING\n"
        "• Assess verified findings using CVSS v3.1 base metrics\n"
        "• Assign appropriate severity ratings (Critical, High, Medium, Low)\n"
        "• Formulate developer remediation recommendations (code-level fixes)\n"
        "• Compile formal Security Assessment Report"
    )
    ax.text(6.0, 4.2, p4_text, ha="center", va="center", bbox=box_report, fontsize=9.5)

    # 7. FINAL DELIVERABLES
    deliv_text = (
        "FINAL DELIVERABLES\n"
        "1. Isolated Local Security Testing Environment (Dockerized Target)\n"
        "2. Python Verification Scripts (Deterministic Proof-of-Concept)\n"
        "3. Vulnerability Evidence Package (HTTP Request/Response Artifacts)\n"
        "4. Professional Security Assessment Report (Executive & Technical)\n"
        "5. Developer Remediation Recommendations (Security Guidance)"
    )
    ax.text(6.0, 2.1, deliv_text, ha="center", va="center", bbox=box_deliverables, fontsize=9.5, weight="bold")

    # 8. END
    ax.text(6.0, 0.7, "END", ha="center", va="center", bbox=box_start, fontsize=11, weight="bold", color="#0F172A")

    # Connectors
    ax.annotate("", xy=(6.0, 12.8), xytext=(6.0, 13.2), arrowprops=arrow)
    ax.annotate("", xy=(6.0, 10.9), xytext=(6.0, 11.2), arrowprops=arrow)
    ax.annotate("", xy=(6.0, 8.9), xytext=(6.0, 9.3), arrowprops=arrow)
    ax.annotate("", xy=(6.0, 6.9), xytext=(6.0, 7.3), arrowprops=arrow)

    # Decision branches
    # YES Branch (Down)
    ax.annotate("", xy=(6.0, 4.9), xytext=(6.0, 5.5), arrowprops=arrow_green)
    ax.text(6.2, 5.2, "YES (Verified)", ha="left", va="center", fontsize=9.5, color="#15803D", weight="bold")

    # NO Branch (Left to Review Box)
    ax.annotate("", xy=(3.3, 6.2), xytext=(4.3, 6.2), arrowprops=arrow_red)
    ax.text(3.8, 6.4, "NO", ha="center", va="bottom", fontsize=9.5, color="#DC2626", weight="bold")

    # Loop back from Review Box to Phase 3
    ax.annotate("", xy=(1.8, 8.1), xytext=(1.8, 7.2), arrowprops=dict(arrowstyle="-", color="#B45309", linewidth=1.6, linestyle="--"))
    ax.annotate("", xy=(3.2, 8.1), xytext=(1.8, 8.1), arrowprops=dict(arrowstyle="->", color="#B45309", linewidth=1.6, linestyle="--", mutation_scale=12))
    ax.text(1.9, 7.7, "Refine Test", ha="left", va="center", fontsize=8.5, color="#B45309", style="italic")

    # Phase 4 to Deliverables & End
    ax.annotate("", xy=(6.0, 3.1), xytext=(6.0, 3.5), arrowprops=arrow)
    ax.annotate("", xy=(6.0, 1.1), xytext=(6.0, 1.4), arrowprops=arrow)

    plt.tight_layout()
    plt.savefig(out_dir / "fig1_project_workflow_flowchart.png", dpi=300)
    plt.close()
    print("Generated fig1_project_workflow_flowchart.png")


def generate_architecture():
    fig, ax = plt.subplots(figsize=(13, 9), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 9)
    ax.axis('off')

    # Outer containers
    host_patch = patches.FancyBboxPatch((0.5, 3.0), 12.0, 5.5, boxstyle="round,pad=0.3", facecolor="#F8FAFC", edgecolor="#334155", linewidth=2.0)
    docker_patch = patches.FancyBboxPatch((7.8, 3.4), 4.4, 3.8, boxstyle="round,pad=0.3", facecolor="#F0FDF4", edgecolor="#16A34A", linewidth=1.8, linestyle="--")
    report_tier = patches.FancyBboxPatch((0.5, 0.4), 12.0, 2.1, boxstyle="round,pad=0.3", facecolor="#F5F3FF", edgecolor="#6D28D9", linewidth=1.8)

    ax.add_patch(host_patch)
    ax.add_patch(docker_patch)
    ax.add_patch(report_tier)

    ax.text(0.8, 8.2, "LOCAL WORKSTATION HOST (Testing Environment)", fontsize=11, weight="bold", color="#1E293B")
    ax.text(8.0, 6.9, "DOCKER DESKTOP ISOLATION", fontsize=9.5, weight="bold", color="#15803D")
    ax.text(0.8, 2.2, "ASSESSMENT, REMEDIATION & REPORTING DELIVERABLES", fontsize=11, weight="bold", color="#5B21B6")

    # Components
    b_tester = dict(boxstyle="round,pad=0.4", facecolor="#FFFFFF", edgecolor="#2563EB", linewidth=1.6)
    b_tool = dict(boxstyle="round,pad=0.4", facecolor="#FFFFFF", edgecolor="#0284C7", linewidth=1.6)
    b_target = dict(boxstyle="round,pad=0.5", facecolor="#DCFCE7", edgecolor="#15803D", linewidth=1.8)
    b_report = dict(boxstyle="round,pad=0.4", facecolor="#FFFFFF", edgecolor="#7C3AED", linewidth=1.6)
    arrow = dict(arrowstyle="<->", color="#334155", linewidth=1.8, mutation_scale=12)
    arrow_fwd = dict(arrowstyle="->", color="#1E293B", linewidth=1.8, mutation_scale=12)

    # Host Tools
    ax.text(2.0, 6.8, "Ethical Hacker\n(Manual Tester)", ha="center", va="center", bbox=b_tester, fontsize=9.5, weight="bold")
    ax.text(2.0, 5.0, "Chromium Browser\n(Proxy Config: 127.0.0.1:8080)", ha="center", va="center", bbox=b_tool, fontsize=9)
    ax.text(5.0, 5.0, "Burp Suite Community\n• Intercepting Proxy\n• Repeater & Decoder\n• Target Site Map", ha="center", va="center", bbox=b_tool, fontsize=8.5, weight="bold")
    ax.text(5.0, 7.0, "Nmap Security Scanner\n(Service & Port Discovery\n`nmap -sV -sC -p- 127.0.0.1`)", ha="center", va="center", bbox=b_tool, fontsize=8.5)
    ax.text(2.0, 3.6, "Python 3 Verification Scripts\n(Deterministic HTTP Proof-of-Concepts)", ha="center", va="center", bbox=b_tool, fontsize=8.5)

    # Docker Target
    ax.text(10.0, 5.2, "Authorized Local Target\nOWASP Juice Shop / DVWA\n(Isolated Container Engine)\nBound to localhost:3000 / localhost:80\nNo External Network Exposure", ha="center", va="center", bbox=b_target, fontsize=9.5, weight="bold")

    # Connectors Host to Docker
    ax.annotate("", xy=(2.0, 5.6), xytext=(2.0, 6.2), arrowprops=arrow)
    ax.annotate("", xy=(3.6, 5.0), xytext=(2.9, 5.0), arrowprops=arrow)
    ax.annotate("", xy=(7.9, 5.2), xytext=(6.5, 5.2), arrowprops=arrow)
    ax.text(7.2, 5.4, "HTTP Traffic", ha="center", va="bottom", fontsize=8.5, color="#1E293B", weight="bold")
    ax.annotate("", xy=(7.9, 6.2), xytext=(6.4, 7.0), arrowprops=arrow_fwd)
    ax.annotate("", xy=(7.9, 4.4), xytext=(3.8, 3.6), arrowprops=arrow_fwd)

    # Report Layer
    ax.text(2.0, 1.2, "Vulnerability Evidence\n(HTTP Requests/Responses,\nScreenshots & Server Logs)", ha="center", va="center", bbox=b_report, fontsize=8.5)
    ax.text(5.0, 1.2, "CVSS v3.1 Severity Scoring\n(Base Metrics: AV, AC, PR,\nUI, Scope, CIA Impact)", ha="center", va="center", bbox=b_report, fontsize=8.5)
    ax.text(8.0, 1.2, "Remediation Guidance\n(Prepared Statements, Contextual\nEscaping, Access Control Checks)", ha="center", va="center", bbox=b_report, fontsize=8.5)
    ax.text(11.0, 1.2, "Final Assessment Report\n(Executive Summary, Detailed\nFindings & Developer Fixes)", ha="center", va="center", bbox=b_report, fontsize=8.5, weight="bold")

    # Connectors from Tools to Deliverables
    ax.annotate("", xy=(2.0, 1.8), xytext=(2.0, 3.1), arrowprops=arrow_fwd)
    ax.annotate("", xy=(5.0, 1.8), xytext=(5.0, 3.0), arrowprops=arrow_fwd)
    ax.annotate("", xy=(8.0, 1.8), xytext=(8.0, 3.0), arrowprops=arrow_fwd)
    ax.annotate("", xy=(11.0, 1.8), xytext=(11.0, 3.0), arrowprops=arrow_fwd)

    plt.tight_layout()
    plt.savefig(out_dir / "fig2_system_architecture_lab.png", dpi=300)
    plt.close()
    print("Generated fig2_system_architecture_lab.png")


def generate_vuln_diagram():
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')

    b_step = dict(boxstyle="round,pad=0.4", facecolor="#F8FAFC", edgecolor="#334155", linewidth=1.5)
    b_verify = dict(boxstyle="round,pad=0.4", facecolor="#FEF2F2", edgecolor="#B91C1C", linewidth=1.8)
    b_cvss = dict(boxstyle="round,pad=0.4", facecolor="#FEF3C7", edgecolor="#D97706", linewidth=1.8)
    b_fix = dict(boxstyle="round,pad=0.4", facecolor="#ECFDF5", edgecolor="#047857", linewidth=1.8)
    arrow = dict(arrowstyle="->", color="#1E293B", linewidth=1.8, mutation_scale=12)

    ax.text(1.2, 2.5, "1. Attack Surface\nReconnaissance\n(Nmap / Route Discovery)", ha="center", va="center", bbox=b_step, fontsize=8.5)
    ax.text(3.7, 2.5, "2. Vulnerability Probe\n(SQLi, XSS, IDOR\nvia Burp Repeater)", ha="center", va="center", bbox=b_step, fontsize=8.5)
    ax.text(6.2, 2.5, "3. PoC Verification\n(Python Script &\nEvidence Logging)", ha="center", va="center", bbox=b_verify, fontsize=8.5, weight="bold")
    ax.text(8.7, 3.6, "4a. CVSS v3.1 Scoring\n& Risk Rating", ha="center", va="center", bbox=b_cvss, fontsize=8.5)
    ax.text(8.7, 1.4, "4b. Actionable Code\nRemediation Guidance", ha="center", va="center", bbox=b_fix, fontsize=8.5)

    ax.annotate("", xy=(2.4, 2.5), xytext=(2.0, 2.5), arrowprops=arrow)
    ax.annotate("", xy=(4.9, 2.5), xytext=(4.5, 2.5), arrowprops=arrow)
    ax.annotate("", xy=(7.4, 3.3), xytext=(7.1, 2.7), arrowprops=arrow)
    ax.annotate("", xy=(7.4, 1.7), xytext=(7.1, 2.3), arrowprops=arrow)

    ax.text(5.0, 4.5, "Structured Vulnerability Assessment and Remediation Cycle", ha="center", va="center", fontsize=10.5, weight="bold", color="#0F172A")
    ax.text(5.0, 0.4, "Strict adherence to authorized local environment boundaries; zero testing on unauthorized external networks.", ha="center", va="center", fontsize=8.0, style="italic", color="#64748B")

    plt.tight_layout()
    plt.savefig(out_dir / "fig3_vulnerability_verification_cycle.png", dpi=300)
    plt.close()
    print("Generated fig3_vulnerability_verification_cycle.png")


if __name__ == "__main__":
    generate_flowchart()
    generate_architecture()
    generate_vuln_diagram()
    print("All ethical hacker lab diagrams generated successfully.")

