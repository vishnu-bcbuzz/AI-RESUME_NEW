# Comprehensive Integration Analysis: FUTRSEC AI Resume Engine & JobPilot Crawler

**Document Version**: 1.0.0  
**Date**: November 3, 2026  
**Analyzed Projects**:
1. **Project 1 (Resume Engine)**: `V:\ai_jobagent` (Active Workspace)
2. **Project 2 (Job Crawler)**: `V:\jobpilot-crawler` (Git branch: `vishnu`)

---

## 1. Executive Summary & Strategic Value

This report delivers an architectural, code-level analysis for integrating the **FUTRSEC AI Resume Engine** (`V:\ai_jobagent`) with the **JobPilot Verified Cybersecurity Jobs Crawler** (`V:\jobpilot-crawler`). 

### Core Synergies
- **FUTRSEC AI Resume Engine** evaluates candidate resumes against 74 standardized cybersecurity job profiles, scores them via a deterministic 5-category Neon PostgreSQL ATS engine, identifies skill deficiencies, and generates optimized resumes across 30 ATS-friendly templates (T01–T30). However, its job profiles are currently static career models without real-time vacancies or employer application links.
- **JobPilot Crawler** is an automated, production-grade crawler and discovery system that continuously scrapes, cleans, classifies, and deduplicates **live cybersecurity job openings** across 16+ top enterprises in India and globally (e.g., JPMorgan Chase, Reliance Jio, Genpact, TCS, FinStackk, Cognizant, Wipro, Airtel). It validates ATS job feeds (Workday, Taleo, Greenhouse, Lever, Ashby, Crawl4AI) and extracts verified direct application URLs and HR contacts.
- **Strategic Value of Integration**: Integrating these two systems transforms FUTRSEC from an isolated resume optimization tool into an **end-to-end Cybersecurity Career Intelligence Platform**. Candidates will be able to:
  1. Browse verified, live cybersecurity job vacancies directly within FUTRSEC.
  2. Evaluate their uploaded resumes against **real live job openings** (with custom descriptions, requirements, and locations) in addition to generic role profiles.
  3. Generate tailored, ATS-compliant resumes specifically targeted to the exact live job posting they intend to submit.
  4. Access direct employer application URLs and verified recruiter contacts.

---

## 2. Complete Folder Structure Analysis

### 2.1 Project 1: Resume Engine (`V:\ai_jobagent`)

```
V:\ai_jobagent
├── .env                              # Active environment configuration (Neon DB URL)
├── .env.example                      # Configuration template (DB, Gemini, Groq, Ports)
├── check_table.py                    # Database table listing utility
├── db_check.py                       # PostgreSQL connectivity check utility
├── package.json                      # Root workspace scripts (dev, build, preview)
├── requirements.txt                  # Python production & test dependencies
├── run.bat                           # Unified Windows launch script
├── sync_neon.py                      # Neon PostgreSQL schema synchronization script
├── verify_db.py                      # Neon DB connection & role verification
├── verify_neon.py                    # Database connection assertion
├── app/                              # Core Python FastAPI Backend Application
│   ├── config.py                     # Pydantic v2 application settings & environment parser
│   ├── main.py                       # FastAPI REST API router & application lifecycle (22+ routes)
│   ├── ai/
│   │   └── json_utils.py             # Robust JSON extraction & repair utilities for AI outputs
│   ├── database/
│   │   ├── connection.py             # psycopg3 connection pool manager with auto-reconnect
│   │   └── repositories.py           # RoleRepository (roles, skills, requirements, criteria)
│   ├── projects/
│   │   ├── catalog.py                # 20 curated hands-on domain engineering projects
│   │   ├── evaluator.py              # Project submission rubric evaluation
│   │   ├── generator.py              # Resume project enhancements & reconciliation
│   │   ├── plan_generator.py         # Structured milestone implementation plan builder
│   │   └── plan_renderer.py          # Markdown, PDF, and DOCX plan export generator
│   ├── reports/
│   │   ├── renderer.py               # DocumentRenderer: generates PDF and DOCX for T01-T30
│   │   ├── round_robin.py            # Intelligent Round Robin template selector (T01-T30)
│   │   ├── sample_data.py            # Reference candidate data fixtures
│   │   ├── templates.py              # 30 ATS template definitions across 6 layout families
│   │   └── storage/
│   │       ├── assignments.json      # Persistent candidate template assignment log
│   │       └── round_robin_state.json# Global round robin index pointer
│   ├── resume/
│   │   ├── extractor.py              # Universal PDF/DOCX extractor & section classifier
│   │   ├── parser.py                 # Multi-tiered regex & structured candidate data parser
│   │   ├── skills_taxonomy.py        # 10 security subcategories & keyword taxonomy
│   │   └── validator.py              # Content safety, metric filter, & hallucination guard
│   └── scoring/
│       ├── benchmark.py              # Neon database scoring criteria fetcher
│       ├── engine.py                 # Deterministic 5-category ATS scoring engine
│       ├── gap_analysis.py           # Missing core vs preferred skills delta calculator
│       ├── gemini_analyzer.py        # Gemini API qualitative resume evaluation
│       ├── improvement_plan.py       # Actionable gap-remediation & project recommendations
│       ├── matcher.py                # Normalized skill matching & synonym expansion
│       └── ollama_analyzer.py        # Local LLM qualitative analyzer fallback
├── frontend/                         # Modern Single-Page Application (SPA)
│   ├── package.json                  # React 18, Vite 5, Lucide-React dependencies
│   ├── tsconfig.json                 # Strict TypeScript configuration
│   ├── vite.config.ts                # Vite dev server configuration (port 5173, /api proxy)
│   └── src/
│       ├── App.tsx                   # Top-level view routing & global session state
│       ├── api.ts                    # Axios/fetch API client methods
│       ├── types.ts                  # Comprehensive TypeScript interfaces for ATS & resumes
│       ├── context/
│       │   └── ThemeContext.tsx      # Dark / Light / System theme provider
│       └── components/
│           ├── AnalysisResults.tsx   # Detailed ATS evaluation breakdown & score ring
│           ├── DashboardView.tsx     # Enterprise overview, metrics, pipeline visualization
│           ├── FullResumePreview.tsx # Interactive HTML resume preview for 30 templates
│           ├── HistoryView.tsx       # Session analysis history timeline
│           ├── ImprovementPlanView.tsx# Actionable learning plan & interactive workflow modal
│           ├── ImprovementView.tsx   # Optimization studio with Round Robin assignment
│           ├── JobSelectionView.tsx  # Interactive catalog of 74 cybersecurity roles
│           ├── ProjectFlowDiagramModal.tsx # SVG visual workflow flowchart modal
│           ├── RescoreComparison.tsx # Before/after ATS score comparison & downloads
│           ├── ResumeUpload.tsx      # Drag-and-drop document upload (PDF/DOCX)
│           ├── SettingsView.tsx      # Neon DB health, system diagnostics, configuration
│           ├── Sidebar.tsx           # 7-item enterprise navigation sidebar
│           ├── TemplateGalleryView.tsx# Visual browser for all 30 ATS templates (T01-T30)
│           └── TopNav.tsx            # Header bar with breadcrumbs and DB status indicator
└── tests/                            # Comprehensive Automated Test Suite (233 tests)
    ├── test_api.py
    ├── test_automatic_project_transfer.py
    ├── test_certifications_pipeline.py
    ├── test_flow_diagram_button.py
    ├── test_resume_analysis_engine.py
    ├── test_round_robin.py
    ├── test_scoring.py
    ├── test_skills_extraction_pipeline.py
    ├── test_template_gallery.py
    ├── test_universal_resume_extraction.py
    └── test_standalone_workflow_removal.py
```

---

### 2.2 Project 2: Job Crawler (`V:\jobpilot-crawler`)

```
V:\jobpilot-crawler (branch: vishnu)
├── .env.example                      # Crawler configuration template
├── package.json                      # Node.js ESM root, scripts, and dependencies
├── tsconfig.json                     # Root TypeScript build settings
├── vitest.config.ts                  # Vitest runner settings
├── extracted-jobs-after-fix.csv      # Scraped & verified 85 job records dataset
├── finstackk-autonomous-crawl-results.xlsx # Production audit export
├── generate-final-csv.ts             # Dataset compilation & deduplication script
├── data/
│   ├── cybersecurity_roles.csv       # Standard 74 cybersecurity roles catalog
│   ├── india_cybersecurity_roles.csv # India-specific role variants
│   └── seed_employers.csv            # 16+ verified employer registry seeds
├── service-crawl4ai/                 # Python 3.12 Browser-Rendering Microservice (Port 8001)
│   ├── main.py                       # FastAPI loopback service with SSRF protection
│   ├── extractors.py                 # Specialized Playwright scrapers (Jio, Cognizant, Darwinbox)
│   ├── requirements.txt              # crawl4ai 0.9.5, playwright 1.64.1, fastapi, uvicorn
│   └── cli_extract.py                # Standalone extraction test CLI
├── src/                              # Node.js / TypeScript Core Crawler Engine
│   ├── index.ts                      # Multi-source crawl CLI entrypoint
│   ├── worker.ts                     # pg-boss background worker for 48h recurring crawls
│   ├── api/
│   │   ├── server.ts                 # Express 4.21 HTTP server setup (Port 4000)
│   │   ├── routes.ts                 # REST API endpoints & SSE crawl stream (18+ routes)
│   │   └── excel-export.ts           # Multi-sheet Excel report builder (exceljs)
│   ├── cli/
│   │   ├── crawl.ts                  # Manual single/multi-company crawl CLI
│   │   ├── crawl-hr.ts               # Recruiter contact scraper CLI
│   │   └── export-discovery.ts       # Discovered endpoints CSV exporter
│   ├── config/
│   │   └── index.ts                  # Central environment parser & crawler options
│   ├── crawler/
│   │   ├── adapters/                 # ATS & Web Scraping Adapters
│   │   │   ├── base.ts               # BaseAdapter abstract class
│   │   │   ├── ashby.ts              # Ashby ATS API adapter
│   │   │   ├── custom.ts             # Crawl4AI dynamic rendering adapter
│   │   │   ├── finstackk.ts          # FinStackk custom portal adapter
│   │   │   ├── greenhouse.ts         # Greenhouse public API adapter
│   │   │   ├── html-structured.ts    # JSON-LD Schema.org & Next.js __NEXT_DATA__
│   │   │   ├── lever.ts              # Lever public API adapter
│   │   │   ├── taleo.ts              # Oracle Cloud / Taleo Candidate Experience REST API
│   │   │   ├── wipro.ts              # Wipro Careers custom adapter
│   │   │   └── workday.ts            # Workday CXS Direct API adapter (/wday/cxs/...)
│   │   ├── classifier/
│   │   │   ├── catalogue.ts          # Validates & matches against 74 roles catalog
│   │   │   ├── index.ts              # Deterministic multi-factor role classifier
│   │   │   ├── location.ts           # India-only geographic classifier & city/state mapper
│   │   │   └── taxonomy.ts           # Keyword taxonomy & negative exclusion rules
│   │   ├── discovery/
│   │   │   ├── auto-discover.ts      # Deep-scan careers discovery engine (L1 & L2)
│   │   │   ├── candidate-scorer.ts   # Evaluates career page link relevance
│   │   │   ├── careers-discovery.ts  # Root domain hyper-link parser
│   │   │   ├── company-verifier.ts   # Domain & employer reputation validation
│   │   │   ├── discovery-engine.ts   # Multi-threaded discovery orchestrator
│   │   │   ├── dry-run.ts            # Non-persisting discovery dry run
│   │   │   ├── portal-detector.ts    # Detects underlying ATS (Workday, Taleo, etc.)
│   │   │   └── search/               # Search engine API discovery (DuckDuckGo, Serper, Bing)
│   │   ├── fetcher/
│   │   │   ├── crawl4ai-client.ts    # Node.js HTTP client to Python Crawl4AI sidecar
│   │   │   └── safe-fetch.ts         # SSRF-guarded HTTP fetcher with size & timeout caps
│   │   ├── hr/
│   │   │   ├── crawler.ts            # HR contact crawler pipeline
│   │   │   └── extractor.ts          # Regex email parser & recruiter context extractor
│   │   ├── pipeline/
│   │   │   └── crawl-source.ts       # End-to-end pipeline: fetch, extract, clean, dedupe, save
│   │   └── safety/
│   │       ├── hostname.ts           # Hostname whitelisting & SSRF guard
│   │       ├── rate-limiter.ts       # 2,000ms polite rate limiter per domain
│   │       └── robots.ts             # Robots.txt parser and crawl-delay enforcer
│   ├── db/
│   │   ├── migrate.ts                # Idempotent migration runner
│   │   ├── pool.ts                   # pg connection pool wrapper
│   │   └── migrations/               # PostgreSQL DDL migrations
│   │       ├── 001_initial_schema.sql# Core tables: employers, job_sources, crawl_runs, job_listings
│   │       ├── 002_hr_contacts.sql   # Recruiter contacts schema
│   │       ├── 003_add_location_fields_and_dedupe.sql # State, city, experience, location dedupe
│   │       ├── 004_crawl_run_isolation_and_rejected_jobs.sql # Audit tables & rejected job tracking
│   │       └── 005_fetch_inspector.sql# HTTP payload debugging & inspection schema
│   ├── registry/
│   │   ├── approval.ts               # Source review & approval state transitions
│   │   ├── dynamic-source.ts         # Runtime source registration
│   │   ├── import-seed.ts            # CSV seed importer
│   │   └── schema.ts                 # Zod validation schema for employer registries
│   ├── scheduler/
│   │   └── queue.ts                  # pg-boss queue scheduling, retry, and concurrency locks
│   └── types/
│       └── index.ts                  # TypeScript types for jobs, employers, sources, runs
├── frontend/                         # Vanilla TypeScript Dashboard & Inspector
│   ├── vite.config.ts                # Vite dev server (port 5173, targets API on port 4000)
│   └── src/
│       ├── main.ts                   # Vanilla DOM bootstrap & tab orchestrator
│       ├── components/
│       │   ├── ActivityView.ts       # System audit logs & crawl run history
│       │   ├── CrawlerView.ts        # Manual crawl runner, source selector, live progress
│       │   ├── FetchInspectorView.ts # Network payload & header inspection view
│       │   ├── Navbar.ts             # Header navigation bar & backend health badge
│       │   ├── ParticleCanvas.ts     # Canvas 2D background particle effect
│       │   └── ResultsView.ts        # Scraped jobs data table with filters & Excel download
│       ├── services/
│       │   └── crawler-service.ts    # REST & SSE fetch client for Port 4000
│       ├── styles/
│       │   ├── main.css              # Dark theme UI styling
│       │   └── tokens.css            # CSS custom properties
│       └── types/
│           └── index.ts              # Frontend TypeScript models
└── tests/                            # Vitest Test Suite (Adapters, Pipeline, Safety, API)
```

---

## 3. Technology Stack & Dependency Comparison

| Dimension | Project 1: Resume Engine (`ai_jobagent`) | Project 2: Job Crawler (`jobpilot-crawler`) | Compatibility Assessment & Integration Strategy |
|---|---|---|---|
| **Primary Language** | Python 3.12 | TypeScript 5.7 / Node.js (ESM) | Compatible as complementary services. Python handles NLP/parsing/rendering; Node handles high-concurrency I/O crawling. |
| **Secondary Language** | TypeScript 5.6 (Frontend only) | Python 3.12 (`service-crawl4ai` sidecar) | Both environments already support both Python 3.12 and Node.js/TypeScript. |
| **Backend Framework** | FastAPI `>=0.115.0` (ASGI) | Express `^4.21.2` + FastAPI (Sidecar) | Express on port 4000, Resume Engine FastAPI on 8000, Sidecar on 8001. Clean separation or reverse-proxy unification. |
| **Web Server / Process** | Uvicorn `[standard]>=0.30.0` | Node.js process / `tsx` | Run concurrently via process orchestrator or unified startup script. |
| **Frontend Framework** | **React 18.3.1** (Modern Component Architecture) | **Vanilla TypeScript** (Class-based DOM manipulation) | **FUTRSEC React 18 is the clear host**. Crawler components can be ported to React TSX views in FUTRSEC. |
| **Frontend Tooling** | Vite `^5.4.10`, Lucide-React `^0.453.0` | Vite `^5.x`, Canvas 2D | Both use Vite. Porting Vanilla classes to React TSX is straightforward. |
| **Database Engine** | **Neon Serverless PostgreSQL** (Remote AWS `ap-southeast-1`) | **PostgreSQL 16+** (Supports Local or Neon) | **Unified Neon DB**. Both projects can point to the same Neon PostgreSQL instance using distinct, non-overlapping tables. |
| **Database Client** | Python `psycopg3` (`psycopg[binary]`, `psycopg-pool`) | Node `pg` (`^8.13.1`), `pg-boss` (`^10.1.3`) | Compatible. Both support SCRAM-SHA-256 and SSL (`sslmode=require`). |
| **Background Scheduling** | In-process FastAPI background tasks | `pg-boss` PostgreSQL-backed task queue | `pg-boss` handles 48h crawler intervals reliably without extra Redis infrastructure. |
| **AI / LLM Integration** | Google Gemini 2.5 Flash, Groq (`gpt-oss-120b`) | **Zero AI** (100% deterministic rules & taxonomy) | Pure synergy: JobPilot extracts clean factual job data without hallucinations; FUTRSEC applies AI for resume matching. |
| **Scraping / Document Tools** | PyMuPDF `^1.24.0`, `pypdf`, `python-docx` | `cheerio`, `robots-parser`, `crawl4ai`, `playwright` | Completely non-conflicting. Document parsing in Python; web scraping in Node/Playwright. |
| **Data Validation** | Pydantic v2 (`^2.9.0`), `pydantic-settings` | Zod (`^3.24.1`) | Pydantic governs Python API contracts; Zod governs Node API contracts. |
| **Export Formats** | PDF (ReportLab/PyMuPDF), DOCX (`python-docx`) | Excel (`exceljs`), CSV (`csv-stringify`) | Complements candidate outputs: resumes in PDF/DOCX, job batches in Excel/CSV. |
| **Test Runners** | `pytest` `>=8.0.0`, `pytest-asyncio` | `vitest` `^2.1.8` | Independent test runners; both execute cleanly without interference. |

---

## 4. Existing Architectures (As-Is)

### 4.1 Project 1: Resume Engine Architecture

```
                       +----------------------------------+
                       |   Candidate Web Client           |
                       |   (React 18 / Vite - Port 5173)  |
                       +----------------------------------+
                                        |  HTTP /api proxy
                                        v
                       +----------------------------------+
                       |   FUTRSEC FastAPI Backend        |
                       |   (Python 3.12 - Port 8000)      |
                       +----------------------------------+
                                        |
         +------------------------------+------------------------------+
         |                              |                              |
         v                              v                              v
+------------------+          +-------------------+          +------------------+
| Resume Extractor |          | ATS Scoring       |          | DocumentRenderer |
| & Parser (PyPDF, |          | Engine            |          | 30 ATS Templates |
| PyMuPDF, DOCX)   |          | (5 Deterministic  |          | (T01 - T30)      |
+------------------+          | Categories)       |          | PDF & DOCX       |
                              +-------------------+          +------------------+
                                        |                              ^
                                        v                              |
                              +-------------------+          +------------------+
                              | Neon PostgreSQL   |          | Round Robin &    |
                              | - job_roles (74)  |          | Groq AI Resume   |
                              | - role_skills     |          | Content Engine   |
                              | - criteria weights|          +------------------+
                              +-------------------+
```

### 4.2 Project 2: Job Crawler Architecture

```
                                +-----------------------------------+
                                |    JobPilot Admin Dashboard       |
                                |    (Vanilla TS / Vite - Port 5173)|
                                +-----------------------------------+
                                                  |
                                                  | HTTP / SSE Stream
                                                  v
                                +-----------------------------------+
                                |    Express 4.21 API Server        |
                                |    (Node.js / TS - Port 4000)     |
                                +-----------------------------------+
                                                  |
                         +------------------------+------------------------+
                         |                                                 |
                         v                                                 v
           +---------------------------+                     +---------------------------+
           | Direct ATS API Adapters   |                     | Crawl4AI Rendering Sidecar|
           | - Workday CXS Direct API  |                     | (Python FastAPI - P: 8001)|
           | - Oracle HCM / Taleo REST |                     | - Headless Playwright     |
           | - Ashby / Lever / Greenh. |                     | - SSRF & Host Guard       |
           | - Schema.org JSON-LD      |                     | - JavaScript Evaluation   |
           +---------------------------+                     +---------------------------+
                         |                                                 |
                         +------------------------+------------------------+
                                                  |
                                                  v
                                +-----------------------------------+
                                | Deterministic Cleaning Pipeline   |
                                | - Location Classifier (India)     |
                                | - Role Classifier (74 Taxonomy)   |
                                | - External ID & Hash Deduplication|
                                +-----------------------------------+
                                                  |
                                                  v
                                +-----------------------------------+
                                | PostgreSQL Storage Layer          |
                                | - employers, job_sources          |
                                | - job_listings, crawl_runs        |
                                | - pgboss (48h scheduling queue)   |
                                +-----------------------------------+
```

---

## 5. Database Technologies & Schemas

### 5.1 Database Technology Comparison
- **Resume Engine**: Neon Serverless PostgreSQL (`futrsec_resume` database), accessed via Python `psycopg3` pool (`psycopg_pool.ConnectionPool`). Enforces SSL (`sslmode=require`).
- **Job Crawler**: Standard PostgreSQL 16+, accessed via Node `pg.Pool`. Configured by `DATABASE_URL`. Compatible with Neon PostgreSQL.

### 5.2 Schema Analysis & Table Inventory

#### Resume Engine Tables (Already in Neon DB)
1. `job_roles`: Standard cybersecurity career profiles (74 rows).
   - Columns: `role_id` (PK, int), `role_name` (varchar), `role_description` (text), `created_at` (timestamptz).
2. `role_skills`: Authoritative skills required for each role.
   - Columns: `skill_id` (PK, int), `role_id` (FK -> job_roles), `skill_name` (varchar), `importance` (`core`, `preferred`, `additional`).
3. `role_requirements`: Education, degree, and certification requirements.
   - Columns: `requirement_id` (PK), `role_id` (FK), `requirement_type`, `requirement_description`, `importance`.
4. `scoring_criteria`: ATS category weights per role.
   - Columns: `criteria_id` (PK), `role_id` (FK), `category`, `weight` (decimal, summing to 1.0).
5. `project_catalog`: 20 hands-on cybersecurity projects.
   - Columns: `project_id` (varchar), `project_title`, `domain`, `difficulty_level`, `description`, etc.

#### Job Crawler Tables (Ready to migrate to Neon DB)
1. `employers`: Master company registry.
   - Columns: `id` (PK, UUID), `name` (varchar, unique), `domain` (varchar, unique), `category`, `hq_location`, `review_status`, `verified_at`.
2. `job_sources`: Monitored career portals and ATS endpoints.
   - Columns: `id` (PK, UUID), `employer_id` (FK -> employers), `career_url`, `source_type` (`ATS_WORKDAY`, `ATS_TALEO`, `CUSTOM_CRAWL4AI`, etc.), `adapter_config` (jsonb), `approval_status`, `crawl_interval_hours`, `last_crawl_at`.
3. `crawl_runs`: Audit history of each crawl execution.
   - Columns: `id` (PK, UUID), `source_id` (FK -> job_sources), `trigger_type`, `status`, `started_at`, `duration_ms`, `jobs_discovered`, `jobs_new`, `jobs_updated`, `error_message`.
4. `crawl_fetches`: Granular HTTP audit log for debugging.
   - Columns: `id` (PK, UUID), `crawl_run_id` (FK -> crawl_runs), `requested_url`, `http_status`, `duration_ms`, `http_method`, `request_headers`, `response_headers`, `fetch_stage`.
5. `job_listings`: **Verified live job postings**.
   - Columns: `id` (PK, UUID), `employer_id` (FK -> employers), `source_id` (FK -> job_sources), `external_job_id`, `canonical_url`, `application_url`, `title`, `description_text`, `description_hash`, `location`, `country`, `city`, `state`, `work_arrangement`, `cybersecurity_role`, `is_verified`, `first_seen_at`, `last_seen_at`.
6. `crawl_rejected_jobs`: Audit log of jobs discarded as non-security or non-India.
   - Columns: `id` (PK, UUID), `crawl_run_id`, `title`, `job_url`, `location`, `rejection_reason`.
7. `hr_contacts`: Discovered recruiter emails.
   - Columns: `id` (PK, UUID), `employer_id` (FK -> employers), `email`, `contact_name`, `contact_type`, `source_url`.
8. `pgboss.*`: Background job queue tables automatically managed by `pg-boss`.

### 5.3 Schema Compatibility Assessment
- **Zero Table Name Collisions**: Neither project shares any conflicting table names.
- **UUID Extension**: JobPilot relies on `pgcrypto` (`gen_random_uuid()`), which is natively supported on Neon PostgreSQL.
- **Cross-Schema Foreign Key Potential**:
  - In `job_listings`, the column `cybersecurity_role` (varchar, e.g. `'SOC Analyst'`) can be linked directly or mapped via a generated foreign key `matched_role_id INT REFERENCES job_roles(role_id)`.

---

## 6. API Endpoints & Communication Methods

### 6.1 Resume Engine Endpoints (`http://127.0.0.1:8000`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health`, `/api/health` | System status & Neon DB connectivity |
| `GET` | `/api/gemini/health` | Gemini API connectivity check |
| `GET` | `/api/roles` | Lists all 74 cybersecurity career profiles |
| `GET` | `/api/roles/{id}` | Retrieves role detail and description |
| `GET` | `/api/roles/{id}/skills` | Retrieves core, preferred, and additional skills |
| `GET` | `/api/roles/{id}/requirements`| Retrieves formal degree and experience rules |
| `GET` | `/api/roles/{id}/scoring-criteria`| Retrieves deterministic category weights |
| `POST` | `/api/resumes/analyze` | Multipart upload (PDF/DOCX) + role_id -> Full ATS score |
| `GET` | `/api/resumes/analyze/status/{job_id}` | Async analysis polling status |
| `POST` | `/api/resumes/next-stage` | Stage authorization check |
| `POST` | `/api/resumes/improve` | Generates improved resume across T01–T30 via Round Robin |
| `POST` | `/api/resumes/accept-and-rescore`| Re-evaluates optimized resume against role criteria |
| `GET` | `/api/templates` | Lists all 30 ATS templates (T01–T30) |
| `GET` | `/api/templates/{id}` | Template metadata and schema details |
| `GET` | `/api/templates/{id}/preview`| HTML preview snippet for template |
| `GET` | `/api/templates/{id}/preview/pdf` | PDF preview render |
| `GET` | `/api/templates/{id}/preview/docx`| DOCX preview render |
| `GET` | `/api/resumes/download/{file_id}` | Binary stream for generated resume (PDF or DOCX) |
| `GET` | `/api/projects/catalog` | Curated hands-on project recommendations |
| `GET` | `/api/projects/plan/{analysis_id}` | Actionable milestone project plan |
| `GET` | `/api/projects/workflow` | JSON stage specification for flowchart modal |
| `POST` | `/api/projects/approve-for-resume`| Approves completed project for inclusion in resume |

### 6.2 Job Crawler Endpoints (`http://localhost:4000`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | None | Crawler backend health & database version |
| `GET` | `/api/jobs` | None | Filterable live jobs (role, location, city, state, experience, pagination) |
| `GET` | `/api/jobs/:id` | None | Full job specification, raw description, and application URL |
| `GET` | `/api/jobs/metrics` | None | Aggregated counts: verified jobs, employers, cities, roles |
| `GET` | `/api/jobs/export/excel` | None | Multi-sheet Excel workbook download of all verified jobs |
| `GET` | `/api/crawl-runs/:id/export/excel` | None | Crawl-specific 2-sheet Excel audit (Verified + Rejected) |
| `GET` | `/api/crawl-runs` | None | List recent crawl executions and metrics |
| `GET` | `/api/crawl-runs/:id` | None | Granular run statistics, errors, and duration |
| `GET` | `/api/crawl-runs/:id/fetches` | None | Network fetches list for a specific crawl run |
| `GET` | `/api/crawl-fetches/:id` | None | Detailed HTTP headers and body preview for single fetch |
| `GET` | `/api/sources/status` | None | Health status and next scheduled crawl for all sources |
| `GET` | `/api/sources/:id` | None | Detailed configuration of single crawl source |
| `POST` | `/api/sources/:id/approve` | Admin Bearer | Approves source for active crawling (Localhost bypass) |
| `POST` | `/api/sources/:id/disable` | Admin Bearer | Disables source from active crawling (Localhost bypass) |
| `GET` | `/api/employers/:id/contacts` | None | Discovered HR/recruiting contacts for an employer |
| `GET` | `/api/contacts` | None | Global directory of verified recruiter contacts |
| `POST` | `/api/crawl` | None | Triggers ad-hoc crawl for employer or URL |
| `GET` | `/api/crawl/stream` | None | **Server-Sent Events (SSE)** live crawl log & stage stream |

### 6.3 Sidecar Endpoints (`http://127.0.0.1:8001`)
- `GET /health`: Browser rendering health.
- `POST /render`: Headless Playwright page rendering with SSRF checks.
- `POST /extract/cognizant`, `POST /extract/jio`, `POST /extract/darwinbox`: Specialized portal scrapers.

---

## 7. Deep Dive: Resume Engine Modules

### 7.1 Resume Upload
- **Validation**: Enforces 10MB maximum upload limit; validates MIME types (`application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`) and inspects file headers/magic bytes (`%PDF-`, `PK\x03\x04`).
- **Storage**: Uploaded files are streamed to temporary in-memory buffers or unique paths under `uploads/` without leaking credentials.

### 7.2 Resume Parsing
- **Text Extraction**: Uses PyMuPDF (`fitz`) for direct text and tabular layout extraction, with fallback to `pypdf`. Uses `python-docx` for XML paragraph and table extraction from Word documents.
- **Section Parsing**: Universal regex heading detection handles diverse resume conventions (e.g., "Technical Skills", "Competencies", "Work History", "Professional Experience", "Academic Projects", "Certifications").
- **Contact & Skills Extraction**: Normalizes phone numbers, email addresses, LinkedIn, and GitHub URLs; classifies extracted technical skills into 10 cybersecurity domains using `skills_taxonomy.py`.

### 7.3 ATS Scoring Engine
- **Deterministic 5-Category Neon Algorithm**:
  1. *Core Technical Skills* (Weight: ~40%): Matches extracted skills against role's `core` skills.
  2. *Preferred Skills* (Weight: ~20%): Matches against role's `preferred` skills.
  3. *Experience & Trajectory* (Weight: ~15%): Evaluates years of experience, relevant titles, and progression.
  4. *Education & Formal Criteria* (Weight: ~15%): Matches degree levels (B.Tech, M.S., etc.) and domain.
  5. *Certifications & Credentials* (Weight: ~10%): Verifies industry certifications (CEH, OSCP, CISSP, CompTIA Security+).
- **Threshold**: Benchmark threshold is **80.0/100**. Scores `< 80.0` trigger the Round Robin Resume Improvement engine.

### 7.4 Resume Generation
- **30 ATS Templates (T01–T30)**: Templates are organized into 6 distinct design families:
  1. Classic Single Column
  2. Executive Summary
  3. Modern Clean
  4. Skills-Focused
  5. Compact Technical
  6. Chronological Strong
- **Round Robin Engine**: Deterministically assigns templates using state tracking in `round_robin_state.json` or respects candidate manual selection.
- **Factual Integrity Preservation**: Strictly preserves authentic candidate identity, email, phone, education records, verified certifications, authentic employers, job titles, and dates. Rephrases bullet points with active security verbs and incorporates candidate-approved hands-on projects.
- **Rendering**: Generates clean, ATS-scannable documents in both PDF and DOCX format.

### 7.5 Job Matching
- Matches candidate data against the 74 Neon PostgreSQL `job_roles` by querying `RoleRepository.get_role_full_profile(role_id)`. Computes skills gaps between candidate inventory and target requirements.

---

## 8. Deep Dive: Job Crawler Modules

### 8.1 Web Scraping & Safety
- **Direct ATS API Adapters**:
  - `WorkdayAdapter`: Connects directly to `/wday/cxs/{tenant}/{site}/jobs` REST endpoints.
  - `TaleoAdapter`: Connects to Oracle Cloud HCM `/hcmRestApi/resources/latest/recruitingCEJobRequisitionDetails` endpoints.
  - `GreenhouseAdapter`, `LeverAdapter`, `AshbyAdapter`: Query official public JSON endpoints.
- **Dynamic Browser Rendering**: `Crawl4AiClient` delegates JavaScript-heavy portals (Jio, Cognizant, Darwinbox) to the Python Playwright microservice.
- **Crawler Safety Architecture**:
  - SSRF protection via `hostname.ts`: strictly blocks private IPs, RFC 1918 ranges, loopback, and cloud metadata (`169.254.169.254`).
  - Strict `robots.txt` compliance and 2,000ms polite inter-request delay per host.
  - Honest User-Agent: `FUTRSEC-JobsBot/1.0 (+https://futrsec.in/bot; bot@futrsec.in)`.

### 8.2 Job Extraction
- Extracts structured `RawJobPosting` models: external ID, title, canonical URL, direct application URL, raw HTML, text content, location string, department, posted date, and employment type.

### 8.3 Job Cleaning & Deduplication
- **Location Classification (`location.ts`)**: Deterministic geographic classifier for India. Normalizes city and state names across 50+ major IT hubs (Bengaluru, Hyderabad, Pune, Mumbai, Gurugram, Noida, Chennai, etc.). Rejects foreign or ambiguous locations.
- **Role Classification (`index.ts`, `taxonomy.ts`)**: Evaluates title and context keywords against 74 standard cybersecurity roles. Applies strict negative filters to eliminate IT support, sales, marketing, and generic engineering.
- **Deduplication**: Composite unique indexes on `(source_id, external_job_id, location)` and `(source_id, canonical_url, location)`. Computes SHA-256 hashes of descriptions to detect content updates without creating duplicate records.

### 8.4 Job Storage
- Persists verified listings into PostgreSQL `job_listings`, audit records into `crawl_runs` and `crawl_fetches`, and non-compliant postings into `crawl_rejected_jobs`. Provides on-demand multi-tab Excel export via `exceljs`.

---

## 9. Duplicate Functionality & Dependency Conflicts

### 9.1 Port Conflicts (Immediate Runtime Issue)

| Component | Resume Engine (`ai_jobagent`) | Job Crawler (`jobpilot-crawler`) | Conflict Analysis & Resolution |
|---|---|---|---|
| **Frontend Dev Server** | Port **5173** (`vite.config.ts`) | Port **5173** (`frontend/vite.config.ts`) | **Direct Collision**: Both frontends default to Vite port 5173. **Resolution**: Run the unified React frontend on 5173; reassign crawler dev server to 5174 or decommission standalone crawler UI once ported into React. |
| **Backend API** | Port **8000** (FastAPI) | Port **4000** (Express) | **No Collision**: Distinct ports. FastAPI on 8000, Express on 4000. |
| **Rendering Sidecar** | None | Port **8001** (FastAPI / Crawl4AI) | **No Collision**: Sidecar runs isolated on port 8001. |

### 9.2 Functional & Data Duplication
1. **74 Cybersecurity Roles**:
   - `ai_jobagent`: Stored in Neon PostgreSQL table `public.job_roles` (74 rows).
   - `jobpilot-crawler`: Stored in CSV file `data/cybersecurity_roles.csv` (74 rows) and TypeScript rule taxonomy `src/crawler/classifier/taxonomy.ts`.
   - **Resolution**: Establish Neon PostgreSQL `job_roles` as the single authoritative source of truth.
2. **Health Check Endpoints**:
   - Both expose `GET /health`.
   - **Resolution**: Route `/health` on 8000 for Resume Engine; proxy `/api/crawler/health` to Port 4000.
3. **Frontend Views**:
   - Both have separate Vite web dashboards. FUTRSEC has a React 18 production UI; JobPilot has a Vanilla TypeScript dashboard.
   - **Resolution**: Integrate JobPilot's Live Jobs view and Crawler controls directly into FUTRSEC React 18 as first-class views.

---

## 10. Proposed Unified Architecture

```
+----------------------------------------------------------------------------------------------------+
|                                    FUTRSEC UNIFIED PLATFORM                                        |
+----------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
                         +--------------------------------------------------+
                         |       Unified React 18 Frontend (Port 5173)      |
                         |  - Platform Dashboard                            |
                         |  - Cybersecurity Career Roles (74 Profiles)      |
                         |  - [NEW] Live Verified Job Openings (From Crawl) |
                         |  - [NEW] Evaluate Resume Against Live Job        |
                         |  - Resume Analysis Studio & ATS Scoring Ring     |
                         |  - 30-Template Round Robin Resume Studio         |
                         |  - [NEW] Crawler Control Center & Live Logs      |
                         +--------------------------------------------------+
                                                  |
                                                  | HTTP / SSE Proxy
                                                  v
                         +--------------------------------------------------+
                         |      FUTRSEC API Gateway (FastAPI - Port 8000)   |
                         |  - /api/resumes/*        (Resume Engine)         |
                         |  - /api/roles/*          (Role Profiles)         |
                         |  - /api/templates/*      (ATS 30 Templates)      |
                         |  - /api/projects/*       (Hands-on Plans)        |
                         |  - /api/jobs/live/*      (Live Jobs Proxy/Query) |
                         |  - /api/crawler/*        (Crawler Proxy to P4000)|
                         +--------------------------------------------------+
                                         |                      |
                    +--------------------+                      +--------------------+
                    |                                                                |
                    v                                                                v
+----------------------------------------+                      +----------------------------------------+
| FUTRSEC Core Engine (Python 3.12)      |                      | JobPilot Crawler Engine (Node.js ESM)  |
| - PyMuPDF / docx Parser                |                      | - Express 4.21 API Server (Port 4000)  |
| - Deterministic 5-Category ATS Scorer  |                      | - Workday / Taleo Direct Adapters      |
| - 30-Template DocumentRenderer         |                      | - Location & Role Classifiers          |
| - Gemini / Groq AI Content Engine      |                      | - pg-boss 48h Queue & Worker Process   |
+----------------------------------------+                      +----------------------------------------+
                    |                                                                |
                    |                                                                | IPC (Port 8001)
                    |                                                                v
                    |                                           +----------------------------------------+
                    |                                           | Crawl4AI Sidecar (Python Playwright)   |
                    |                                           | - Loopback: http://127.0.0.1:8001      |
                    +--------------------+                      +----------------------------------------+
                                         |                                  |
                                         v                                  v
                         +--------------------------------------------------+
                         |        Unified Neon Serverless PostgreSQL        |
                         |  Resume Tables:                                  |
                         |  - job_roles (74), role_skills, criteria         |
                         |  - project_catalog, assignments                  |
                         |  Crawler Tables:                                 |
                         |  - employers, job_sources, crawl_runs            |
                         |  - job_listings (Live Vacancies with App URLs)   |
                         |  - crawl_fetches, crawl_rejected_jobs            |
                         |  - hr_contacts, pgboss schema                    |
                         +--------------------------------------------------+
```

---

## 11. API Integration Plan

### 11.1 New Unified Endpoints in FastAPI Gateway (`Port 8000`)

```
/api/jobs/live
  GET  /api/jobs/live                  -> Queries public.job_listings (filtered by role, city, state, experience)
  GET  /api/jobs/live/{job_id}         -> Retrieves full job details, full description, and direct application URL
  GET  /api/jobs/live/metrics          -> Returns live market metrics (active openings, verified employers, top roles)
  GET  /api/jobs/live/{job_id}/contacts-> Returns HR/recruiter contact emails for hiring employer

/api/resumes/evaluate-live-job
  POST /api/resumes/evaluate-live-job  -> Evaluates uploaded resume directly against a live job's description & requirements

/api/crawler (Forwarded to Port 4000)
  GET  /api/crawler/sources            -> Reverse-proxied to http://localhost:4000/api/sources/status
  POST /api/crawler/crawl              -> Reverse-proxied to http://localhost:4000/api/crawl
  GET  /api/crawler/stream             -> Proxies Server-Sent Events (SSE) live crawl logs
```

### 11.2 "Evaluate Resume Against Live Job" Contract

```json
POST /api/resumes/evaluate-live-job
Content-Type: multipart/form-data
Body:
  file: <binary resume PDF/DOCX>
  live_job_id: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

Response:
{
  "analysis_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "live_job": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "title": "Lead Security Engineer - Threat modelling, Cloud Security",
    "company": "JPMorgan Chase",
    "location": "Bengaluru, Karnataka, India",
    "application_url": "https://jpmc.fa.oraclecloud.com/..."
  },
  "overall_score": 84.5,
  "passed_threshold": true,
  "category_scores": {
    "core_skills": 88.0,
    "preferred_skills": 80.0,
    "experience": 85.0,
    "education": 90.0,
    "certifications": 75.0
  },
  "matched_skills": ["Threat Modeling", "Cloud Security", "AWS", "Python"],
  "missing_skills": ["STRIDE", "Terraform Security"],
  "direct_application_url": "https://jpmc.fa.oraclecloud.com/.../apply"
}
```

---

## 12. Database Integration Plan

### 12.1 Neon PostgreSQL Migration Sequence
1. Point `V:\jobpilot-crawler`'s `DATABASE_URL` to the active Neon database connection string in `V:\ai_jobagent\.env`.
2. Execute JobPilot migrations against Neon:
   - `001_initial_schema.sql` (Creates `employers`, `job_sources`, `crawl_runs`, `crawl_fetches`, `job_listings`)
   - `002_hr_contacts.sql` (Creates `hr_contacts`)
   - `003_add_location_fields_and_dedupe.sql` (Adds `city`, `state`, `experience`, `posted_date`, location indexes)
   - `004_crawl_run_isolation_and_rejected_jobs.sql` (Adds `crawl_rejected_jobs` and metrics)
   - `005_fetch_inspector.sql` (Adds HTTP debugging columns)
3. Execute foreign key association migration:
   ```sql
   -- Link live crawled jobs to standard FUTRSEC role catalog
   ALTER TABLE public.job_listings
   ADD COLUMN IF NOT EXISTS role_id INTEGER REFERENCES public.job_roles(role_id) ON DELETE SET NULL;

   -- Populate role_id foreign key using deterministic name matching
   UPDATE public.job_listings jl
   SET role_id = jr.role_id
   FROM public.job_roles jr
   WHERE LOWER(TRIM(jl.cybersecurity_role)) = LOWER(TRIM(jr.role_name));
   ```

### 12.2 Connection Pool Sizing
- Neon serverless compute handles 50–100 pooled connections.
- Configure `DB_POOL_MIN_SIZE=2`, `DB_POOL_MAX_SIZE=8` in `ai_jobagent`.
- Configure `max: 5` in `jobpilot-crawler/src/db/pool.ts` to prevent pool exhaustion.

---

## 13. Required File Changes (Implementation Blueprint)

> **REMINDER**: No files are modified during this analysis turn. This section specifies the precise changes required for execution during the subsequent implementation phase.

### In `V:\ai_jobagent` (Resume Engine):
1. **`app/main.py`**:
   - Add routes: `GET /api/jobs/live`, `GET /api/jobs/live/{job_id}`, `GET /api/jobs/live/metrics`, `POST /api/resumes/evaluate-live-job`.
   - Add `httpx` reverse-proxy handler for `/api/crawler/*` targeting `http://localhost:4000`.
2. **`app/database/repositories.py`**:
   - Add `LiveJobRepository` class to query `job_listings`, `employers`, and `hr_contacts` directly via `psycopg3`.
3. **`frontend/src/components/Sidebar.tsx`**:
   - Add navigation item: `Live Openings` (`BriefcaseCheck` icon) with live openings badge count.
   - Add navigation item: `Crawler Center` (`Activity` icon) for system administrators.
4. **`frontend/src/components/LiveJobsView.tsx` (New Component)**:
   - React 18 component displaying live verified openings (company, role, city, state, experience, application URL).
   - Adds one-click action: `"Evaluate My Resume Against This Job"`.
5. **`frontend/src/components/CrawlerAdminView.tsx` (New Component)**:
   - React 18 port of JobPilot's crawler control center, trigger button, and live SSE crawl log stream.

### In `V:\jobpilot-crawler` (Job Crawler):
1. **`frontend/vite.config.ts`**:
   - Update port from `5173` to `5174` to eliminate port collision during independent testing.
2. **`.env`**:
   - Set `DATABASE_URL` to the shared Neon PostgreSQL connection string.
3. **`src/config/index.ts`**:
   - Update default port fallback.

---

## 14. Step-by-Step Integration Sequence

```
+-----------------------------------------------------------------------------------+
| STEP 1: Database Migration                                                        |
| Run JobPilot migrations (001-005) against Neon PostgreSQL to create tables.       |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| STEP 2: Database Role Foreign Key Linking                                         |
| Add role_id column to job_listings and map cybersecurity_role -> job_roles.       |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| STEP 3: Port Deconfliction & Environment Harmonization                            |
| Reconfigure JobPilot standalone UI to port 5174; confirm FastAPI on 8000,         |
| Express on 4000, Crawl4AI on 8001.                                                |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| STEP 4: FastAPI Live Jobs Query Layer                                             |
| Implement LiveJobRepository in app/database/repositories.py.                      |
| Expose GET /api/jobs/live and GET /api/jobs/live/{id} on FastAPI backend.         |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| STEP 5: React 18 "Live Verified Jobs" View                                        |
| Create LiveJobsView.tsx in FUTRSEC frontend. Integrate with sidebar navigation.   |
| Surface live jobs with company logos, verified badges, and direct apply links.    |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| STEP 6: "Evaluate Against Live Job" Cross-Feature Workflow                        |
| Wire ResumeUpload.tsx to accept live_job_id, extract job requirements from        |
| job_listings.description_text, score with ATS engine, and tailor resume.         |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| STEP 7: Comprehensive Regression & End-to-End Verification                        |
| Run all 233 Resume Engine tests + all JobPilot crawler vitest tests.              |
+-----------------------------------------------------------------------------------+
```

---

## 15. Testing & Verification Strategy

### 15.1 Regression Preservation
- All **233 existing backend tests** in `V:\ai_jobagent\tests\` must continue passing with a 100% pass rate.
- All 30 ATS templates (T01–T30), Round Robin assignments, PDF/DOCX downloads, and candidate project extraction mechanisms must remain completely unaffected.
- All existing Vitest suites in `V:\jobpilot-crawler\tests\` (adapters, SSRF safety, location classifier, deduplication) must continue passing.

### 15.2 Integration Test Cases

1. **Database Schema Integrity Test**:
   - Assert all 8 crawler tables coexist with 5 resume tables in Neon DB without schema interference.
   - Assert `role_id` foreign key correctly resolves between `job_listings` and `job_roles`.
2. **Live Job Query Performance Test**:
   - `GET /api/jobs/live` returns paginated jobs within `< 150ms`.
   - Filtering by city (`Bengaluru`, `Hyderabad`, `Pune`) returns accurate, location-verified postings.
3. **Live Job Resume Evaluation Test**:
   - Upload sample candidate resume with target `live_job_id`.
   - Verify deterministic scoring evaluates candidate skills against the specific live job description.
   - Confirm generated PDF/DOCX resume contains authentic candidate records, tailored summary, and verified projects.
4. **Crawl Trigger & Live Stream Test**:
   - Trigger crawl from FUTRSEC React UI via `POST /api/crawler/crawl`.
   - Confirm SSE stream updates live progress events without UI freezes.
5. **Port & Process Isolation Test**:
   - Start all 4 processes simultaneously:
     - FastAPI Resume Engine (`127.0.0.1:8000`)
     - React 18 Frontend (`127.0.0.1:5173`)
     - Express Crawler API (`127.0.0.1:4000`)
     - Python Playwright Sidecar (`127.0.0.1:8001`)
   - Confirm 0 port collisions, clean graceful shutdowns, and stable connection pooling.

