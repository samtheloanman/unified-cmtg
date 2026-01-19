# Unified CMTG Platform - Project Milestones

**Status**: Active Development  
**Last Updated**: 2026-01-18 21:00 PST

This document tracks the high-level milestones for the Unified CMTG Platform v2.0.

---

## ✅ Milestone 1: Foundation & Legacy Verification
**Goal**: Establish project structure and verify legacy assets.

*   [x] **Repository Setup**: Monorepo for `backend` (Django) and `frontend` (Next.js).
*   [x] **Documentation**: established `GEMINI.md`, `PRD.md`, and agent guidelines.
*   [x] **Legacy Verification**: Verified `cmtgdirect` and WordPress assets.
*   [x] **Docker Infrastructure**: Containerized development environment.

---

## ✅ Milestone 2: Content & SEO Engine
**Goal**: Replace WordPress with Wagtail + Next.js for high-performance SEO.

*   [x] **Headless CMS**: Wagtail installed with API v2 configured.
*   [x] **Data Models**: Created `LocationPage`, `ProgramPage`, `FundedLoanPage`, `BlogPage`.
*   [x] **Content Migration**:
    *   Imported **109** Office Locations (covering top 50 US cities).
    *   Imported **62** Loan Programs with 64+ data fields.
*   [x] **Frontend Architecture**:
    *   Next.js 14 App Router + Tailwind CSS.
    *   Type-safe Wagtail API client (`wagtail-api.ts`).
*   [x] **Programmatic SEO**:
    *   `/locations/` index and detail pages with maps/schema.
    *   `/programs/` index and detail pages with specs/schema.

---

## ✅ Milestone 3: Pricing Engine Core
**Goal**: Port `cmtgdirect` matching logic to the new Django backend.
*   *Legacy Source*: `legacy/cmtgdirect/loans/queries.py`

*   [x] **Model Migration**: Port `LoanProgram`, `Lender`, `ProgramType`, `LenderProgramOffering`.
*   [x] **RateAdjustment Model**: Implemented FICO/LTV grid-based adjustments.
*   [x] **Logic Port**: Re-implemented `get_matched_loan_programs_for_qual` in `backend/pricing/services/matching.py`.
*   [x] **Service Layer**: Created `LoanMatchingService` with rate adjustment calculations.
*   [x] **API Development**: Created `/api/v1/quote/` endpoint (QuoteView in DRF).
*   [x] **Migrations**: Applied `0001_initial` and `0002_qualifyinginfo`.
*   [ ] **Parity Testing**: Verify output matches legacy system 1:1.
*   [ ] **Test Data**: Load sample lenders, program types, and rate sheets.

---

## 📅 Milestone 4: Interactive Features (Quote & Floify)
**Goal**: Enable user interaction and lead processing.

*   [ ] **Quote Wizard UI**: Build React multi-step form for `/quote`.
*   [ ] **Floify Integration**:
    *   Implement `floify_create_prospect` service.
    *   Handle `application.created` webhooks.
*   [ ] **CRM Sync**: Sync leads to backend database.

---

## 📅 Milestone 5: AI Rate Sheet Agent
**Goal**: Automate ingestion of lender PDF rate sheets.

*   [ ] **Ingestion Pipeline**: Service to fetch PDFs from email/CSV.
*   [ ] **Extraction Engine**: Gemini 1.5 Pro integration for PDF->JSON parsing.
*   [ ] **Review Dashboard**: "Human-in-the-Loop" UI for approving rate updates.
*   [ ] **Publishing**: Update `LenderProgramOffering` records automatically.

---

## 📅 Milestone 6: Production Readiness
**Goal**: Go-live at `custommortgageinc.com`.

*   [ ] **Production Infra**: Docker Swarm / Kubernetes setup on `dell-brain`.
*   [ ] **Performance**: Cache tuning (Redis/Varnish) and Lighthouse audit.
*   [ ] **Security**: Audit and penetration testing.
*   [ ] **Cutover**: DNS update to new platform.
