# GEMINI.md - Agent Context for Unified CMTG Platform

> **Purpose**: This file provides AI agents with critical context about the project structure, architecture decisions, and current implementation status.

---

## 🎯 Project Mission

Build a **headless, AI-native mortgage platform** at `cmre.c-mtg.com` that unifies:
1. **Content** (from WordPress/custommortgage)
2. **Pricing Logic** (from Django/cmtgdirect)
3. **Agentic Workflows** (Rate Sheet ingestion, Content generation)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         UNIFIED CMTG PLATFORM                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │   Next.js 14    │    │     Django      │    │     Wagtail     │  │
│  │   (Frontend)    │◄───│  (Pricing API)  │◄───│  (Headless CMS) │  │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘  │
│           │                      │                      │            │
│           └──────────────────────┴──────────────────────┘            │
│                                  │                                    │
│  ┌───────────────────────────────┴───────────────────────────────┐  │
│  │                      AI AGENT LAYER                            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐    │  │
│  │  │ Rate Sheet  │  │   Content   │  │   Quote Optimizer   │    │  │
│  │  │   Agent     │  │   Agent     │  │       Agent         │    │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘    │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Directory Structure

```
unified-cmtg/
├── GEMINI.md                    # THIS FILE - Agent context
├── README.md                    # Human-readable project overview
├── PRD.md                       # Product Requirements Document v2
│
├── knowledge-base/              # Reference documentation
│   ├── rate_extraction_field_mapping.md
│   ├── ratesheet_extraction_sop.md
│   └── archive-v1/              # Old v1 documentation (archived)
│
├── unified-platform/            # THE MAIN APPLICATION
│   ├── .agent/                  # Agent definitions and workflows
│   ├── conductor/               # Conductor task orchestration
│   │   └── tracks/              # Workflow track definitions
│   ├── backend/                 # Django + Wagtail backend
│   │   ├── config/              # Django settings
│   │   ├── api/                 # REST API endpoints
│   │   ├── cms/                 # Wagtail page models
│   │   ├── pricing/             # Loan matching logic
│   │   └── ratesheets/          # Rate sheet ingestion
│   ├── frontend/                # Next.js application
│   │   ├── app/                 # App Router pages
│   │   ├── components/          # UI components
│   │   └── lib/                 # API clients
│   └── scripts/                 # Utility scripts
│
├── FLOIFY-API/                  # Floify integration documentation
├── Ratesheet-samples/           # Sample rate sheet PDFs
└── Ratesheet List - Ratesheets.csv  # Lender rate sheet URLs
```

---

## 🔧 Key Components

### 1. Pricing Engine (Port from cmtgdirect)
**Source**: `legacy/cmtgdirect/loans/`
**Target**: `unified-platform/backend/pricing/`

Key files to port:
- `queries.py` → `get_matched_loan_programs_for_qual()` - Program matching logic
- `models/programs.py` → `LoanProgram`, `Lender` models
- `models/program_types.py` → `ProgramType`, `LenderProgramOffering` models
- `api/views.py` → `QualifyView` - Quote API endpoint

### 2. Content Models (Migrate from WordPress ACF)
**Source**: WordPress ACF fields (64 fields in 6 tabs)
**Target**: `unified-platform/backend/cms/`

Key models to create:
- `ProgramPage` - Wagtail page for loan programs
- `FundedLoanPage` - Showcase of completed loans
- `BlogPage` - News and updates

### 3. Rate Sheet Agent
**Location**: `unified-platform/backend/ratesheets/`

Pipeline:
1. **Ingestion** - Read CSV, download PDFs
2. **Extraction** - OCR + LLM parse to JSON
3. **Staging** - Store in staging table for review
4. **Approval** - Human reviews diffs
5. **Publish** - Update `LenderProgramOffering` records

---

## 🤖 Agent Roles

| Agent | Specialty | Context Files |
|-------|-----------|---------------|
| **Pricing Engineer** | Django/Python, loan logic | `pricing/`, `api/` |
| **Wagtail Expert** | CMS modeling, StreamFields | `cms/`, ACF field mapping |
| **Frontend Architect** | Next.js, React, Tailwind | `frontend/` |
| **Rate Sheet Agent** | PDF extraction, data validation | `ratesheets/`, `knowledge-base/` |
| **QA Tester** | pytest, Docker, E2E tests | `tests/`, `docker-compose.yml` |

---

## 🚀 Current Phase

**Phase 1: Foundation & Legacy Verification**

### Completed
- [x] Repository created and pushed to GitHub
- [x] Documentation structure established
- [x] v2 PRD approved

### In Progress
- [ ] Copy cmtgdirect to unified-platform/backend
- [ ] Initialize Django + Wagtail project
- [ ] Verify legacy cmtgdirect runs locally

### Next
- [ ] Port pricing models and logic
- [ ] Create Next.js frontend scaffold

---

## 🔑 Key Decisions

1. **Headless Architecture**: Wagtail as headless CMS, Next.js as frontend
2. **Keep Legacy Logic**: Reuse cmtgdirect's proven matching algorithm
3. **Human-in-the-Loop Rates**: Rate sheet changes require human approval
4. **Dell-Brain as Host**: All development runs on dell-brain server via Tailscale

---

## 📍 Important Paths

| Resource | Location |
|----------|----------|
| Legacy cmtgdirect | `dell-brain:~/code/cmtgdirect` |
| Legacy custommortgage | `dell-brain:~/code/custommortgage` |
| New unified platform | `unified-cmtg/unified-platform/` |
| Rate sheet samples | `unified-cmtg/Ratesheet-samples/` |
| Floify API docs | `unified-cmtg/FLOIFY-API/` |

---

## ⚡ Quick Commands

```bash
# SSH to development server
ssh dell-brain

# Start development containers
cd ~/code/unified-cmtg/unified-platform
docker-compose up -d

# Run Django tests
docker-compose exec backend pytest

# Start Next.js dev server
cd frontend && npm run dev
```

---

## 📞 External Services

| Service | Purpose | Status |
|---------|---------|--------|
| Floify | Loan application processing | API key available |
| WPEngine | Legacy WordPress hosting | Production site |
| Zoho Mail | Rate sheet email ingestion | Needs setup |
| Tailscale | VPN for dell-brain access | Configured |

---

*Last Updated: 2026-01-11*
*Version: 2.0*
