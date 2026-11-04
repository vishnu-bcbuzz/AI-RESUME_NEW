import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.projects.catalog import ALL_CATALOG_PROJECTS, SUPPORTED_DOMAINS

projects_json = json.dumps(ALL_CATALOG_PROJECTS, indent=2)
domains_json = json.dumps(SUPPORTED_DOMAINS, indent=2)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FUTRSEC - Domain-Based Project Recommendations & Flow Diagrams</title>
  <style>
    :root {{
      --bg: #F8FAFC;
      --card-bg: #FFFFFF;
      --text-main: #0F172A;
      --text-muted: #475569;
      --border: #E2E8F0;
      --primary: #1E40AF;
      --primary-light: #EFF6FF;
      --primary-hover: #1D4ED8;
      --accent: #2563EB;
      --success: #15803D;
      --warning: #B45309;
      --danger: #B91C1C;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text-main);
      line-height: 1.5;
      padding-bottom: 60px;
    }}

    header {{
      background: #FFFFFF;
      border-bottom: 1px solid var(--border);
      padding: 24px 32px;
      margin-bottom: 32px;
    }}

    .header-content {{
      max-width: 1200px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }}

    .brand h1 {{
      font-size: 24px;
      font-weight: 700;
      color: var(--primary);
      letter-spacing: -0.5px;
    }}

    .brand p {{
      font-size: 14px;
      color: var(--text-muted);
      margin-top: 4px;
    }}

    .container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 24px;
    }}

    /* Domain Selector */
    .domain-selector-wrapper {{
      background: #FFFFFF;
      padding: 20px 24px;
      border-radius: 12px;
      border: 1px solid var(--border);
      margin-bottom: 32px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }}

    .domain-selector-label {{
      font-size: 13px;
      text-transform: uppercase;
      font-weight: 700;
      letter-spacing: 0.5px;
      color: var(--text-muted);
      margin-bottom: 12px;
    }}

    .domain-pills {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }}

    .domain-pill {{
      background: var(--bg);
      color: var(--text-main);
      border: 1px solid var(--border);
      padding: 10px 18px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease-in-out;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .domain-pill:hover {{
      background: #E2E8F0;
      border-color: #CBD5E1;
    }}

    .domain-pill.active {{
      background: var(--primary);
      color: #FFFFFF;
      border-color: var(--primary);
      box-shadow: 0 2px 4px rgba(30, 64, 175, 0.2);
    }}

    .domain-pill .badge {{
      background: rgba(0, 0, 0, 0.08);
      padding: 2px 8px;
      border-radius: 9999px;
      font-size: 12px;
    }}

    .domain-pill.active .badge {{
      background: rgba(255, 255, 255, 0.25);
      color: #FFFFFF;
    }}

    /* Projects Grid View */
    .section-title {{
      font-size: 20px;
      font-weight: 700;
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .projects-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 24px;
    }}

    .project-card {{
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.15s ease, box-shadow 0.15s ease;
      box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }}

    .project-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(0,0,0,0.06);
      border-color: #CBD5E1;
    }}

    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
      margin-bottom: 12px;
    }}

    .project-id {{
      font-size: 12px;
      font-family: monospace;
      font-weight: 700;
      color: var(--primary);
      background: var(--primary-light);
      padding: 3px 8px;
      border-radius: 4px;
    }}

    .difficulty-badge {{
      font-size: 12px;
      font-weight: 600;
      padding: 3px 8px;
      border-radius: 4px;
    }}

    .difficulty-Beginner {{ background: #ECFDF5; color: #065F46; }}
    .difficulty-Intermediate {{ background: #EFF6FF; color: #1E40AF; }}
    .difficulty-Advanced {{ background: #FEF3C7; color: #92400E; }}

    .project-title {{
      font-size: 17px;
      font-weight: 700;
      color: var(--text-main);
      margin-bottom: 10px;
      line-height: 1.35;
    }}

    .project-desc {{
      font-size: 14px;
      color: var(--text-muted);
      margin-bottom: 18px;
      flex-grow: 1;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}

    .tech-tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 20px;
    }}

    .tech-tag {{
      background: var(--bg);
      color: #334155;
      font-size: 12px;
      padding: 3px 8px;
      border-radius: 4px;
      border: 1px solid #E2E8F0;
    }}

    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 10px 18px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.15s ease;
      text-decoration: none;
      border: none;
    }}

    .btn-primary {{
      background: var(--primary);
      color: #FFFFFF;
      width: 100%;
    }}

    .btn-primary:hover {{
      background: var(--primary-hover);
    }}

    .btn-outline {{
      background: #FFFFFF;
      border: 1px solid var(--border);
      color: var(--text-main);
    }}

    .btn-outline:hover {{
      background: var(--bg);
    }}

    .btn-secondary {{
      background: #EFF6FF;
      border: 1px solid #BFDBFE;
      color: #1D4ED8;
    }}

    .btn-secondary:hover {{
      background: #DBEAFE;
    }}

    /* Workflow Detail View */
    .workflow-view {{
      display: none;
    }}

    .workflow-header {{
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 24px;
    }}

    .back-nav {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      color: var(--primary);
      font-weight: 600;
      font-size: 14px;
      cursor: pointer;
      margin-bottom: 16px;
      border: none;
      background: none;
    }}

    .back-nav:hover {{
      text-decoration: underline;
    }}

    .wf-title-row {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      flex-wrap: wrap;
      gap: 16px;
      margin-bottom: 16px;
    }}

    .wf-title-row h2 {{
      font-size: 22px;
      font-weight: 700;
      color: var(--text-main);
    }}

    .actions-row {{
      display: flex;
      gap: 12px;
    }}

    .meta-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 16px;
      margin-top: 20px;
      padding-top: 20px;
      border-top: 1px solid var(--border);
    }}

    .meta-item h4 {{
      font-size: 12px;
      text-transform: uppercase;
      font-weight: 700;
      color: var(--text-muted);
      margin-bottom: 4px;
    }}

    .meta-item p {{
      font-size: 14px;
      color: var(--text-main);
    }}

    /* Flowchart Canvas */
    .flowchart-section {{
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 32px 24px;
      margin-bottom: 24px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }}

    .flowchart-section h3 {{
      font-size: 18px;
      font-weight: 700;
      color: var(--text-main);
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .flowchart-container {{
      width: 100%;
      overflow-x: auto;
      display: flex;
      justify-content: center;
      padding: 10px 0;
    }}

    /* Detail Tabs & Information Cards */
    .detail-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
    }}

    .info-card {{
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px;
    }}

    .info-card h4 {{
      font-size: 16px;
      font-weight: 700;
      color: var(--text-main);
      margin-bottom: 14px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 8px;
    }}

    .info-list {{
      list-style-type: none;
    }}

    .info-list li {{
      font-size: 14px;
      color: #334155;
      padding: 6px 0;
      display: flex;
      align-items: flex-start;
      gap: 8px;
    }}

    .info-list li::before {{
      content: "•";
      color: var(--primary);
      font-weight: bold;
      font-size: 18px;
      line-height: 1;
    }}

    /* Print Optimization */
    @media print {{
      body {{
        background: #FFFFFF;
        padding: 0;
      }}

      header, .domain-selector-wrapper, .back-nav, .actions-row, .projects-grid {{
        display: none !important;
      }}

      .workflow-view {{
        display: block !important;
      }}

      .workflow-header, .flowchart-section, .info-card {{
        border: 1px solid #CCCCCC;
        box-shadow: none;
        page-break-inside: avoid;
        margin-bottom: 16px;
      }}

      .flowchart-container svg {{
        max-width: 100% !important;
        height: auto !important;
      }}
    }}
  </style>
</head>
<body>

  <header>
    <div class="header-content">
      <div class="brand">
        <h1>FUTRSEC Domain Project Catalog &amp; Flowcharts</h1>
        <p>Interactive Architecture &amp; Workflow Specifications for Verified Technical Projects</p>
      </div>
      <div class="header-actions">
        <a href="/" class="btn btn-outline">Back to Resume Analyzer</a>
      </div>
    </div>
  </header>

  <main class="container">

    <!-- Domain Selector Bar -->
    <div class="domain-selector-wrapper" id="domainSelectorArea">
      <div class="domain-selector-label">Select Engineering Domain (5 Projects per Domain)</div>
      <div class="domain-pills" id="domainPills"></div>
    </div>

    <!-- Project List View (5 Projects) -->
    <div id="projectsListView">
      <div class="section-title">
        <span id="currentDomainTitle">Projects</span>
        <span style="font-size: 13px; font-weight: normal; color: var(--text-muted);" id="projectCountSubtitle">5 Verified Project Blueprints</span>
      </div>
      <div class="projects-grid" id="projectsGrid"></div>
    </div>

    <!-- Single Project Workflow View -->
    <div id="workflowView" class="workflow-view">
      <div class="workflow-header">
        <button class="back-nav" id="backToProjectsBtn">
          ← Back to <span id="backDomainName">Domain</span> Projects
        </button>
        <div class="wf-title-row">
          <div>
            <span class="project-id" id="wfProjectId">ID</span>
            <span class="difficulty-badge" id="wfDifficulty">Level</span>
            <h2 id="wfTitle" style="margin-top: 8px;">Project Title</h2>
          </div>
          <div class="actions-row">
            <button class="btn btn-primary" onclick="downloadWorkflowSVG()" style="width: auto;">Download SVG</button>
            <button class="btn btn-secondary" onclick="downloadWorkflowPNG()" style="width: auto;">Download PNG</button>
            <button class="btn btn-outline" onclick="window.print()">Print / Save PDF</button>
          </div>
        </div>
        <p id="wfDesc" style="font-size: 14.5px; color: var(--text-muted); line-height: 1.6;"></p>

        <div class="meta-grid">
          <div class="meta-item">
            <h4>Domain</h4>
            <p id="wfDomain">Domain</p>
          </div>
          <div class="meta-item">
            <h4>Primary Technologies</h4>
            <p id="wfTechs">Technologies</p>
          </div>
          <div class="meta-item">
            <h4>Prerequisites</h4>
            <p id="wfPrereqs">Prerequisites</p>
          </div>
        </div>
      </div>

      <!-- Flowchart SVG Canvas -->
      <div class="flowchart-section">
        <h3>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="3" y1="9" x2="21" y2="9"></line>
            <line x1="9" y1="21" x2="9" y2="9"></line>
          </svg>
          Implementation Workflow Flowchart
        </h3>
        <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 20px;">
          Vector flowchart describing sequential engineering phases, validation checkpoints, and decision branches.
        </p>
        <div class="flowchart-container" id="svgContainer">
          <!-- Rendered SVG will be placed here -->
        </div>
      </div>

      <!-- Detailed Specifications Grid -->
      <div class="detail-grid">
        <div class="info-card">
          <h4>Learning Objectives</h4>
          <ul class="info-list" id="wfObjectives"></ul>
        </div>
        <div class="info-card">
          <h4>Expected Deliverables</h4>
          <ul class="info-list" id="wfDeliverables"></ul>
        </div>
        <div class="info-card">
          <h4>Implementation Phases</h4>
          <ul class="info-list" id="wfPhases"></ul>
        </div>
        <div class="info-card">
          <h4>Testing &amp; Validation Plan</h4>
          <ul class="info-list" id="wfTesting"></ul>
        </div>
      </div>
    </div>

  </main>

  <script>
    // Embedded Catalog Data (Works 100% locally and offline)
    const CATALOG_DATA = {projects_json};
    const SUPPORTED_DOMAINS = {domains_json};

    let selectedDomain = "Cybersecurity";
    let selectedProjectId = null;

    // Initialize UI
    function init() {{
      renderDomainPills();
      renderProjectsGrid();

      // Check URL parameters if any
      const urlParams = new URLSearchParams(window.location.search);
      const urlDomain = urlParams.get("domain");
      const urlProject = urlParams.get("project_id");

      if (urlDomain && SUPPORTED_DOMAINS.includes(urlDomain)) {{
        selectedDomain = urlDomain;
        renderDomainPills();
        renderProjectsGrid();
      }}

      if (urlProject) {{
        viewProjectWorkflow(urlProject);
      }}

      document.getElementById("backToProjectsBtn").addEventListener("click", () => {{
        closeWorkflowView();
      }});
    }}

    // Render Domain Selector Pills
    function renderDomainPills() {{
      const container = document.getElementById("domainPills");
      container.innerHTML = "";

      SUPPORTED_DOMAINS.forEach(dom => {{
        const count = CATALOG_DATA.filter(p => p.domain === dom).length;
        const pill = document.createElement("button");
        pill.className = "domain-pill" + (dom === selectedDomain ? " active" : "");
        pill.innerHTML = `<span>${{dom}}</span><span class="badge">${{count}}</span>`;
        pill.onclick = () => selectDomain(dom);
        container.appendChild(pill);
      }});
    }}

    function selectDomain(domain) {{
      selectedDomain = domain;
      selectedProjectId = null;
      renderDomainPills();
      renderProjectsGrid();
      closeWorkflowView();
    }}

    // Render the 5 Project Cards for Selected Domain
    function renderProjectsGrid() {{
      const grid = document.getElementById("projectsGrid");
      grid.innerHTML = "";

      document.getElementById("currentDomainTitle").innerText = selectedDomain + " Projects";
      const domainProjects = CATALOG_DATA.filter(p => p.domain === selectedDomain).slice(0, 5);

      domainProjects.forEach(proj => {{
        const card = document.createElement("div");
        card.className = "project-card";

        const techSpans = proj.required_technologies.slice(0, 4)
          .map(t => `<span class="tech-tag">${{t}}</span>`).join("");

        card.innerHTML = `
          <div>
            <div class="card-header">
              <span class="project-id">${{proj.project_id}}</span>
              <span class="difficulty-badge difficulty-${{proj.difficulty_level.split(" ")[0]}}">${{proj.difficulty_level}}</span>
            </div>
            <h3 class="project-title">${{proj.project_title}}</h3>
            <p class="project-desc">${{proj.description}}</p>
          </div>
          <div>
            <div class="tech-tags">${{techSpans}}</div>
            <button class="btn btn-primary" onclick="viewProjectWorkflow('${{proj.project_id}}')">
              View Project Flow →
            </button>
          </div>
        `;
        grid.appendChild(card);
      }});
    }}

    // View Detailed Workflow and Flowchart
    function viewProjectWorkflow(projectId) {{
      const proj = CATALOG_DATA.find(p => p.project_id === projectId);
      if (!proj) return;

      selectedProjectId = projectId;
      selectedDomain = proj.domain;
      renderDomainPills();

      document.getElementById("projectsListView").style.display = "none";
      document.getElementById("domainSelectorArea").style.display = "none";
      const wfView = document.getElementById("workflowView");
      wfView.style.display = "block";

      // Populate Header Metadata
      document.getElementById("backDomainName").innerText = proj.domain;
      document.getElementById("wfProjectId").innerText = proj.project_id;
      document.getElementById("wfDifficulty").innerText = proj.difficulty_level;
      document.getElementById("wfDifficulty").className = "difficulty-badge difficulty-" + proj.difficulty_level.split(" ")[0];
      document.getElementById("wfTitle").innerText = proj.project_title;
      document.getElementById("wfDesc").innerText = proj.description;
      document.getElementById("wfDomain").innerText = proj.domain;
      document.getElementById("wfTechs").innerText = proj.required_technologies.join(", ");
      document.getElementById("wfPrereqs").innerText = proj.prerequisites.join(" • ");

      // Populate Detail Lists
      populateList("wfObjectives", proj.learning_objectives);
      populateList("wfDeliverables", proj.expected_deliverables);
      populateList("wfTesting", proj.testing_validation_plan);

      const phasesList = document.getElementById("wfPhases");
      phasesList.innerHTML = "";
      proj.implementation_phases.forEach(ph => {{
        const li = document.createElement("li");
        li.innerHTML = `<strong>Phase ${{ph.phase_number}}: ${{ph.title}}</strong> — ${{ph.objective}}`;
        phasesList.appendChild(li);
      }});

      // Render Inline SVG Flowchart
      renderSVGDiagram(proj);
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function populateList(elementId, items) {{
      const el = document.getElementById(elementId);
      el.innerHTML = "";
      items.forEach(it => {{
        const li = document.createElement("li");
        li.innerText = it;
        el.appendChild(li);
      }});
    }}

    function closeWorkflowView() {{
      document.getElementById("workflowView").style.display = "none";
      document.getElementById("projectsListView").style.display = "block";
      document.getElementById("domainSelectorArea").style.display = "block";
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    // =========================================================================
    // HIGH-QUALITY INLINE SVG FLOWCHART RENDERING ENGINE
    // =========================================================================
    function wrapTextLines(text, maxChars) {{
      if (!text) return [];
      const words = text.trim().split(/[ \t\r\n]+/);
      const lines = [];
      let cur = "";
      for (const w of words) {{
        if (!cur) {{
          cur = w;
        }} else if ((cur + " " + w).length <= maxChars) {{
          cur += " " + w;
        }} else {{
          lines.push(cur);
          cur = w;
        }}
      }}
      if (cur) lines.push(cur);
      return lines.length > 0 ? lines : [text];
    }}

    function renderSVGDiagram(project) {{
      const container = document.getElementById("svgContainer");
      const workflow = project.project_workflow || [];

      if (!workflow || workflow.length === 0) {{
        container.innerHTML = "<p>No workflow nodes specified for this project.</p>";
        return;
      }}

      const svgWidth = 860;
      const nodeWidth = 400;
      const centerX = 360;
      const leftX = centerX - (nodeWidth / 2);

      let currentY = 30;
      const nodeElements = [];
      const connectionElements = [];
      const nodeCoordMap = {{}};

      workflow.forEach((node, idx) => {{
        const type = node.type || "process";
        let nodeH = 56;
        let labelLines = wrapTextLines(node.label, 36);
        let descLines = node.description ? wrapTextLines(node.description, 44) : [];

        if (type === "decision") {{
          nodeH = 120;
          labelLines = wrapTextLines(node.label, 24);
          descLines = node.description ? wrapTextLines(node.description, 26) : [];
        }} else if (type === "start" || type === "end") {{
          nodeH = 44;
          labelLines = [node.label];
          descLines = [];
        }} else {{
          nodeH = Math.max(58, (labelLines.length + descLines.length) * 18 + 24);
        }}

        const coord = {{
          x: leftX,
          y: currentY,
          w: nodeWidth,
          h: nodeH,
          cx: centerX,
          cy: currentY + (nodeH / 2),
          type: type,
          node: node,
          labelLines: labelLines,
          descLines: descLines
        }};
        nodeCoordMap[node.id] = coord;

        currentY += nodeH + 46; // Spacing for arrow & connectors
      }});

      const svgHeight = currentY + 24;

      // Draw Connectors & Arrows first (so they sit underneath nodes)
      workflow.forEach((node, idx) => {{
        const fromCoord = nodeCoordMap[node.id];

        if (node.type === "decision") {{
          // Decision branches: YES (downward solid) and NO (side loop-back dashed)
          const yesNextCoord = nodeCoordMap[node.yes_next];
          const noNextCoord = nodeCoordMap[node.no_next];

          // 1. YES Branch (Downward)
          if (yesNextCoord) {{
            const startY = fromCoord.y + fromCoord.h;
            const endY = yesNextCoord.y;
            connectionElements.push(`
              <line x1="${{fromCoord.cx}}" y1="${{startY}}" x2="${{fromCoord.cx}}" y2="${{endY}}" stroke="#15803D" stroke-width="2.5" marker-end="url(#arrowGreen)"/>
              <rect x="${{fromCoord.cx + 12}}" y="${{startY + 10}}" width="120" height="22" rx="4" fill="#DCFCE7" stroke="#16A34A" stroke-width="1"/>
              <text x="${{fromCoord.cx + 72}}" y="${{startY + 25}}" text-anchor="middle" font-size="11" font-weight="700" fill="#15803D">
                ${{node.yes_label || "YES: VERIFIED"}}
              </text>
            `);
          }}

          // 2. NO Branch (Side routing to review/refine node)
          if (noNextCoord) {{
            const branchStartX = fromCoord.cx + 170;
            const branchStartY = fromCoord.cy;
            const loopX = fromCoord.cx + 250;
            const targetY = noNextCoord.cy;
            const targetEntryX = fromCoord.cx + (fromCoord.w / 2);

            connectionElements.push(`
              <path d="M ${{branchStartX}} ${{branchStartY}} L ${{loopX}} ${{branchStartY}} L ${{loopX}} ${{targetY}} L ${{targetEntryX + 2}} ${{targetY}}"
                    fill="none" stroke="#D97706" stroke-width="2" stroke-dasharray="5,4" marker-end="url(#arrowAmber)"/>
              <rect x="${{loopX - 45}}" y="${{branchStartY - 24}}" width="90" height="18" rx="4" fill="#FEF3C7" stroke="#D97706" stroke-width="1"/>
              <text x="${{loopX}}" y="${{branchStartY - 11}}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#92400E">
                ${{node.no_label || "NO: REFINE"}}
              </text>
            `);
          }}

        }} else if (node.next_node && nodeCoordMap[node.next_node]) {{
          // Standard Sequential Downward Arrow
          const toCoord = nodeCoordMap[node.next_node];
          const startY = fromCoord.y + fromCoord.h;
          const endY = toCoord.y;

          connectionElements.push(`
            <line x1="${{fromCoord.cx}}" y1="${{startY}}" x2="${{fromCoord.cx}}" y2="${{endY}}" stroke="#475569" stroke-width="2" marker-end="url(#arrowDark)"/>
          `);
        }}
      }});

      // Draw Nodes
      workflow.forEach((node) => {{
        const c = nodeCoordMap[node.id];
        const type = node.type || "process";

        if (type === "start" || type === "end") {{
          const isStart = type === "start";
          const strokeColor = isStart ? "#1E40AF" : "#0F172A";
          const fillColor = isStart ? "#EFF6FF" : "#F1F5F9";
          nodeElements.push(`
            <g id="${{node.id}}">
              <rect x="${{c.cx - 100}}" y="${{c.y}}" width="200" height="${{c.h}}" rx="22" ry="22"
                    fill="${{fillColor}}" stroke="${{strokeColor}}" stroke-width="2.5" />
              <text x="${{c.cx}}" y="${{c.y + 27}}" text-anchor="middle" font-size="13" font-weight="800" fill="${{strokeColor}}" letter-spacing="1">
                ${{escapeXML(node.label)}}
              </text>
            </g>
          `);

        }} else if (type === "decision") {{
          // Diamond Decision Node
          const midX = c.cx;
          const midY = c.cy;
          const halfW = 170;
          const halfH = c.h / 2;
          const points = `${{midX}},${{midY - halfH}} ${{midX + halfW}},${{midY}} ${{midX}},${{midY + halfH}} ${{midX - halfW}},${{midY}}`;

          const tspans = c.labelLines.map((line, idx) =>
            `<tspan x="${{midX}}" dy="${{idx === 0 ? 0 : 16}}">${{escapeXML(line)}}</tspan>`
          ).join("");

          nodeElements.push(`
            <g id="${{node.id}}">
              <polygon points="${{points}}" fill="#FFFBEB" stroke="#D97706" stroke-width="2.5" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.05))"/>
              <text x="${{midX}}" y="${{midY - (c.labelLines.length * 8) + 4}}" text-anchor="middle" font-size="12" font-weight="800" fill="#92400E" letter-spacing="0.5">
                ${{tspans}}
              </text>
              ${{c.descLines.length > 0 ? `
              <text x="${{midX}}" y="${{midY + (c.labelLines.length * 8) + 12}}" text-anchor="middle" font-size="10.5" fill="#B45309">
                ${{escapeXML(c.descLines[0])}}
              </text>` : ""}}
            </g>
          `);

        }} else {{
          // Standard Process Node with multi-line wrapped text
          const tspans = c.labelLines.map((line, idx) =>
            `<tspan x="${{c.x + 18}}" dy="${{idx === 0 ? 0 : 16}}">${{escapeXML(line)}}</tspan>`
          ).join("");

          const descTspans = c.descLines.map((line, idx) =>
            `<tspan x="${{c.x + 18}}" dy="${{idx === 0 ? 0 : 15}}">${{escapeXML(line)}}</tspan>`
          ).join("");

          nodeElements.push(`
            <g id="${{node.id}}">
              <rect x="${{c.x}}" y="${{c.y}}" width="${{c.w}}" height="${{c.h}}" rx="8"
                    fill="#FFFFFF" stroke="#2563EB" stroke-width="1.75" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.04))"/>
              <rect x="${{c.x}}" y="${{c.y}}" width="6" height="${{c.h}}" rx="3" fill="#2563EB"/>
              <text x="${{c.x + 18}}" y="${{c.y + 22}}" font-size="12.5" font-weight="700" fill="#0F172A">
                ${{tspans}}
              </text>
              ${{c.descLines.length > 0 ? `
              <text x="${{c.x + 18}}" y="${{c.y + 24 + (c.labelLines.length * 16)}}" font-size="11" fill="#475569">
                ${{descTspans}}
              </text>` : ""}}
            </g>
          `);
        }}
      }});

      const svgMarkup = `
        <svg id="workflowSvgElement" width="100%" height="${{svgHeight}}" viewBox="0 0 ${{svgWidth}} ${{svgHeight}}" xmlns="http://www.w3.org/2000/svg" style="max-width: 860px;">
          <defs>
            <marker id="arrowDark" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#475569" />
            </marker>
            <marker id="arrowGreen" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#15803D" />
            </marker>
            <marker id="arrowAmber" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#D97706" />
            </marker>
          </defs>
          ${{connectionElements.join("")}}
          ${{nodeElements.join("")}}
        </svg>
      `;

      container.innerHTML = svgMarkup;
    }}

    function downloadWorkflowSVG() {{
      const svgEl = document.getElementById("workflowSvgElement");
      if (!svgEl) return;
      let source = new XMLSerializer().serializeToString(svgEl);
      if (!source.includes('xmlns="http://www.w3.org/2000/svg"')) {{
        source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
      }}
      source = '<?xml version="1.0" encoding="utf-8" standalone="no"?>\r\n' + source;
      const blob = new Blob([source], {{ type: 'image/svg+xml;charset=utf-8' }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = (selectedProjectId || "Project") + "_Flowchart.svg";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }}

    function downloadWorkflowPNG() {{
      const svgEl = document.getElementById("workflowSvgElement");
      if (!svgEl) return;
      let source = new XMLSerializer().serializeToString(svgEl);
      if (!source.includes('xmlns="http://www.w3.org/2000/svg"')) {{
        source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
      }}
      const svgBlob = new Blob([source], {{ type: 'image/svg+xml;charset=utf-8' }});
      const blobURL = URL.createObjectURL(svgBlob);
      const image = new Image();
      image.onload = () => {{
        const scale = 2;
        const canvas = document.createElement("canvas");
        const w = (svgEl.viewBox.baseVal && svgEl.viewBox.baseVal.width) || 860;
        const h = (svgEl.viewBox.baseVal && svgEl.viewBox.baseVal.height) || 900;
        canvas.width = w * scale;
        canvas.height = h * scale;
        const ctx = canvas.getContext("2d");
        if (ctx) {{
          ctx.fillStyle = "#FFFFFF";
          ctx.fillRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
          const pngURL = canvas.toDataURL("image/png");
          const a = document.createElement("a");
          a.href = pngURL;
          a.download = (selectedProjectId || "Project") + "_Flowchart.png";
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
        }}
        URL.revokeObjectURL(blobURL);
      }};
      image.src = blobURL;
    }}

    function escapeXML(str) {{
      if (!str) return "";
      return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }}

    function truncate(str, maxLen) {{
      if (!str) return "";
      return str.length > maxLen ? str.substring(0, maxLen - 3) + "..." : str;
    }}

    // Boot
    window.addEventListener("DOMContentLoaded", init);
  </script>
</body>
</html>
"""

output_path = Path("project-flow-diagrams.html")
output_path.write_text(html_content, encoding="utf-8")
print(f"Generated standalone HTML interface at {output_path.resolve()} ({len(html_content)} bytes)")

