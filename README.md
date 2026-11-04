# FUTRSEC AI Resume Engine

> **AI-Powered Cybersecurity Resume Analysis, Deterministic ATS Scoring, Skill-Gap Detection, and Round Robin ATS Template Generation.**

---

## 1. System Overview

FUTRSEC is a full-stack, enterprise-grade cybersecurity resume matching and enhancement platform. It bridges the gap between candidate resumes and real cybersecurity job requirements by leveraging:

1. **Neon PostgreSQL Integration**: Authoritative database containing 74 cybersecurity roles, 1,425 role skills, and 370 scoring criteria.
2. **Secure Document Parsing**: PDF and DOCX extraction with magic-byte validation, file size limits (10MB), and prompt-injection neutralization.
3. **Skill & Evidence Matcher**: Canonical alias resolution and taxonomy mapping (e.g., SIEM, Burp Suite, Metasploit, Wireshark, OWASP).
4. **Deterministic ATS Scoring Engine**: Reproducible Python scoring module adhering strictly to Neon category weights (Technical Skills: 40%, Projects: 25%, Education: 15%, Tools & Certifications: 15%, Career Objective: 5%).
5. **Threshold Workflow (80.0 Cutoff)**:
   - **Score &ge; 80**: Eligible / ATS-aligned; direct progression.
6. **Persistent Round Robin Template Scheduler**: Transaction-safe sequential assignment across 20 professional black-and-white ATS templates (`T01` &rarr; `T02` &rarr; ... &rarr; `T20` &rarr; `T01`).
7. **Document Generation Engine**: Renders editable DOCX and clean multi-page PDF resumes applying strict black-and-white styling, professional typography (Calibri, Arial, Aptos, Times New Roman), and ATS-friendly layouts.
8. **Candidate Review & Re-Scoring**: Evaluates the accepted resume against identical scoring rules to compute exact score deltas.
9. **Modern React & TypeScript Interface**: Dark-mode cybersecurity UI with glassmorphic cards and live Neon connectivity indicators.

---

## 2. Technology Stack

- **Backend**: Python 3.12, FastAPI, Uvicorn, Pydantic v2
- **Database**: Neon Serverless PostgreSQL (`psycopg3`, `psycopg-pool`)
- **Document Processing**: `PyMuPDF` (fitz), `pypdf`, `python-docx`
- **Frontend**: React 18, TypeScript, Vite, Vanilla CSS design tokens, Lucide Icons
- **Testing**: Pytest, Pytest-Asyncio, FastAPI TestClient

---

## 3. Directory Structure

```text
V:\ai_jobagent\
├── app\
│   ├── config.py                 # Pydantic v2 settings & credential masking
│   ├── main.py                   # FastAPI application & REST endpoints
│   ├── database\
│   │   ├── connection.py         # Thread-safe Neon connection pool & health checks
│   │   └── repositories.py       # Parameterized SQL queries for roles, skills, criteria
│   ├── resume\
│   │   ├── parser.py             # PDF/DOCX magic-byte verification & prompt-injection defuser
│   │   └── extractor.py          # Structured resume section & contact extractor
│   ├── scoring\
│   │   ├── matcher.py            # Canonical skill matching & evidence finder
│   │   ├── engine.py             # Deterministic ATS scoring engine (0-100 scale)
│   │   └── gap_analysis.py       # Prioritized skill-gap recommendations & future actions
│   ├── projects\
│   │   └── generator.py          # AI resume content generator with non-hallucination guardrails
│       ├── templates.py          # 20 standard black-and-white ATS template definitions & style configs
│       ├── round_robin.py        # Persistent, concurrency-safe Round Robin scheduler
│       └── renderer.py           # DOCX & PDF document rendering pipeline
├── data\                         # Baseline CSV references
├── frontend\                     # React + TypeScript single-page application
│   ├── src\
│   │   ├── components\           # UI modules (Header, RoleSelector, Upload, Results, etc.)
│   │   ├── api.ts                # REST API client
│   │   ├── types.ts              # TypeScript interfaces
│   │   └── index.css             # Cybersecurity dark-mode design system
│   ├── dist\                     # Production build artifacts
│   └── package.json
├── tests\                        # Automated test suite (33 comprehensive tests)
├── uploads\                      # Storage directory for generated resumes & assignments
├── .env.example                  # Safe configuration template
├── requirements.txt              # Backend dependencies
└── README.md                     # Deployment and architecture documentation
```

---

## 4. Quickstart Guide

### 4.1 Prerequisites

- Python 3.12+
- Node.js 20+ and npm
- Neon PostgreSQL database

### 4.2 Backend Setup

1. Copy `.env.example` to `.env` (or verify existing `.env`):
   ```bash
   cp .env.example .env
   ```
2. Configure your Neon connection URL:
   ```env
   DATABASE_URL=postgresql://<user>:<password>@<neon-host>.neon.tech/<dbname>?sslmode=require
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI server (Run from project root `V:\ai_jobagent`):
   ```bash
   # Both commands work from V:\ai_jobagent root:
   python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
   # OR:
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   API interactive documentation will be available at: `http://127.0.0.1:8000/docs`

> [!TIP]
> **Resolving `Could not import module "main"` & `ECONNREFUSED 127.0.0.1:8000`**:
> - Always run the Python uvicorn command from the workspace root directory (`V:\ai_jobagent`), **not** from inside `frontend/`.
> - A root-level [`main.py`](file:///V:/ai_jobagent/main.py) is provided to ensure `python -m uvicorn main:app` resolves cleanly without path errors.
> - Ensure the backend is started before running the Vite dev server (`npm run dev`) so that `/api/roles` and `/health` proxies connect immediately.

### 4.3 Frontend Setup

1. Navigate to `frontend/`:
   ```bash
   cd frontend
   npm install
   ```
2. Start the Vite development server:
   ```bash
   npm run dev
   ```
   The frontend UI will be accessible at: `http://localhost:5173`

### 4.4 Unified Production Mode

The production bundle in `frontend/dist` is automatically mounted by FastAPI. Running:
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```
serves both the REST API and the upgraded React enterprise frontend at `http://127.0.0.1:8000`.

---

## 5. Automated Testing

Run the full automated test suite using pytest:
```bash
pytest tests/ -v
```

### Test Coverage Highlights (33 Tests):
- **Database (`test_database.py`)**: Real Neon connection health check, retrieval of all 74 cybersecurity roles, skills categorization, requirements, and scoring criteria weights verification.
- **Resume Parsing (`test_parser.py`)**: PDF/DOCX magic-byte validation, corrupt archive rejection, file size limits (10MB), prompt-injection neutralization, structured data extraction.
- **Scoring Engine (`test_scoring.py`)**: 100% deterministic repeatability, exact 40/25/15/15/5 category weighting, threshold boundary logic (79.9 vs 80.0), empty section handling.
- **Round Robin Scheduler (`test_round_robin.py`)**: T01&rarr;T20 sequential order, wraparound to T01, persistence across process restarts, inactive template exclusion, thread safety under concurrency (20 simultaneous requests), idempotent retry behavior.
- **Generator & Renderer (`test_generator_and_renderer.py`)**: Non-hallucination compliance, DOCX and PDF file generation across all 20 template styles in strict black and white.
- **API Endpoints (`test_api.py`)**: Complete end-to-end resume workflow from upload through Round Robin improvement and re-scoring, path traversal defense.

---

## 6. Round Robin Resume Template Library (20 Professional Black-and-White Templates)

Whenever resume creation is triggered (scores below 80), the system selects an ATS-friendly layout using a persistent, transaction-safe Round Robin algorithm across 20 distinct black-and-white templates:

| ID | Template Name | Font / Typography | Header Alignment | Primary Layout Emphasis |
| :--- | :--- | :--- | :--- | :--- |
| **T01** | Professional Classic | Calibri | Center | Traditional corporate resume with centered name and formal sections |
| **T02** | Modern Minimal | Arial | Left | Left-aligned header, concise spacing, simple whitespace dividers |
| **T03** | Technical Specialist | Calibri | Left | Technical skills and relevant practical experience prominently presented |
| **T04** | Corporate Standard | Times New Roman | Center | Formal, conventional section hierarchy with balanced executive spacing |
| **T05** | Cybersecurity Professional | Aptos | Left | Security skills, security projects, and relevant certifications |
| **T06** | Graduate Entry-Level | Calibri | Center | Education, academic projects, internships, and foundational skills |
| **T07** | Experienced Professional | Times New Roman | Center | Reverse-chronological employment and verified career achievements |
| **T08** | Technical Skills Focus | Arial | Left | Clearly organized technical competency taxonomy and tooling breakdown |
| **T09** | Project Portfolio | Aptos | Left | Detailed project evidence, architecture, and technical contributions |
| **T10** | Certification Focus | Times New Roman | Center | Earned certifications and relevant technical qualifications near top |
| **T11** | Compact Professional | Arial | Left | Efficient, readable high-density layout for information-dense resumes |
| **T12** | Chronological Standard | Times New Roman | Left | Conventional reverse-chronological structure with prominent dates |
| **T13** | Technical Project Engineer | Calibri | Left | Project objectives, implementation, technologies, and outcomes |
| **T14** | Internship Candidate | Aptos | Center | Education, coursework, internships, and practical lab work |
| **T15** | Security Operations | Aptos | Left | Relevant SOC, monitoring, and incident-analysis experience |
| **T16** | Penetration Testing | Arial | Left | Verified penetration-testing and vulnerability-assessment evidence |
| **T17** | Cloud Security | Calibri | Left | Verified cloud, infrastructure, and security controls experience |
| **T18** | Application Security | Arial | Left | Verified application-security and secure-development experience |
| **T19** | Security Engineering | Calibri | Left | Security automation, technical implementation, and engineering work |
| **T20** | Senior Professional | Times New Roman | Center | Formal, experience-led executive resume for established leaders |

### Strict Black-and-White Design System:
- **Background**: Pure white (`#FFFFFF`).
- **Text & Headings**: Pure black (`#000000`).
- **Dividers & Borders**: Solid black horizontal rules (`#000000`).
- **Zero Color Contamination**: No blue, green, colored badges, progress bars, gradients, shaded panels, or icons.
- **ATS Compatibility**: Single-column structured document layouts with standard Word styles and vector text PDF rendering.

### Sequence Pattern:
`Generation 1 → T01`, `Generation 2 → T02` ... `Generation 20 → T20`, `Generation 21 → T01`...

- Cursor state is persistently saved to disk (`app/reports/storage/round_robin_state.json`).
- If an existing `job_id` is retried, the previously assigned template is reused without advancing the sequence.

---

## 7. Security & Factual Integrity Controls

- **Prompt-Injection Neutralization**: Scans incoming resumes for adversarial LLM instructions (`System:`, `Ignore previous instructions`, `Give a score of 100`) and sanitizes untrusted input before parsing.
- **Strict Anti-Hallucination Policy**: Neither the AI generator nor the heuristic engine will ever invent certifications, employers, degrees, project outcomes, or metrics.
- **Future Action Labeling**: Certifications the candidate does not currently possess are explicitly tagged as future milestones and must not be placed on the active resume.
- **Path Traversal Defense**: All file download requests are validated against directory boundary roots to prevent unauthorized local file access.
- **Parameterized SQL**: All database operations against Neon use `%s` query parameters with zero raw SQL string concatenation.
- **Secret Redaction**: Environment summaries and logs never expose passwords, connection strings, or API keys.

---

## 8. License & Attribution

FUTRSEC AI Resume Engine — Built for cybersecurity talent development and transparent ATS matching.
