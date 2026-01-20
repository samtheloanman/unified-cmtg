# Unified CMTG Platform - Project Milestones

**Status**: Active Development  
**Last Updated**: 2026-01-19 00:21 PST
**Source**: `unified-platform/conductor/tasks.md`

This document tracks the high-level milestones for the Unified CMTG Platform v2.0, aligned with the Conductor task list.

---

## ✅ Milestone 1: Foundation & Legacy Verification
**Goal**: Establish project structure and verify legacy assets.

*   [x] **Repo Setup**: Initialize `unified-platform` structure
*   [x] **Frontend Init**: Initialize Next.js 14 + Tailwind
*   [x] **Backend Init**: Django + Wagtail in Docker
*   [x] **Health API**: `/api/v1/health/` endpoint
*   [x] **Jules Automation System**: Ralph-loop infrastructure
*   [x] **Legacy cmtgdirect**: Verify running on port 8000
*   [x] **Frontend Connectivity**: Next.js fetches from Django
*   [x] **Superuser**: Create Wagtail admin user

---

## 📅 Milestone 2: Core Pricing Engine
**Goal**: Port `cmtgdirect` matching logic to the new Django backend.

*   [ ] **Port Models**: `Lender`, `LoanProgram`, `BaseLoan` from cmtgdirect
*   [ ] **Port Logic**: `QualifyView` matching to `pricing/services.py`
*   [ ] **Rate Adjustment**: FICO × LTV grids
*   [ ] **Pricing API**: `/api/v1/quote` endpoint

---

## ✅ Milestone 3: Content Migration
**Goal**: Replace WordPress with Wagtail + Next.js for high-performance SEO.

*   [x] **ProgramPage Model**: 64 ACF fields in Wagtail
*   [x] **Office Model**: GPS coordinates for proximity
*   [x] **WP Extraction**: Dump WordPress content to JSON
*   [x] **Import Command**: Ingest JSON into Wagtail
*   [x] **URL Verification**: URLs match WordPress 1:1
*   [x] **Firecrawl Integration**: Refined content extraction source

---

## 📅 Milestone 3a: Programmatic SEO
**Goal**: F.5A - F.5E Infrastructure and Content.

*   [ ] **City Model**: `models/cities.py` with priority/launched_at
*   [ ] **SEOContentCache**: `models/seo.py` with expanded schema fields
*   [ ] **ProximityService**: Caching + Haversine
*   [ ] **SchemaGenerator**: Extended JSON-LD support
*   [ ] **SEOResolver**: Defensive slug parsing
*   [ ] **Import Pilot Cities**: Top 5 only
*   [ ] **Office Mapping**: Verify Physical Offices
*   [ ] **Generate Power 5**: Create 25 perfect pages
*   [ ] **Verify Content**: Manual QA
*   [ ] **Dynamic Router**: API Endpoint
*   [ ] **Launch**: Active Pilot

---

## 📅 Milestone 4: Rate Sheet Agent
**Goal**: Automate ingestion of lender PDF rate sheets.

*   [ ] **Ingestion Script**: Read `Ratesheet List.csv`
*   [ ] **Pipeline Class**: `IngestionPipeline` logic
*   [ ] **PDF Extraction**: Gemini 1.5 Pro → JSON
*   [ ] **Review UI**: Admin dashboard

---

## 📅 Milestone 5: Frontend Finish & Polish
**Goal**: F.7 Next.js CMS Integration and UI Polish.

*   [x] **Program Pages**: Dynamic routing `/programs/[slug]`
*   [x] **Blog Pages**: Dynamic routing `/blog/[slug]`
*   [ ] **Home Page**: Connect CMS fields to Next.js Hero/Features
*   [ ] **Quote Wizard**: Complete multi-step form logic
*   [ ] **Quote Results**: Display API results from Pricing Engine
*   [ ] **Local SEO Pages**: Flat URL format `/program-city-state/`
*   [ ] **Styling Policy**: Verify consistent Tailwind branding
*   [ ] **Mobile Responsiveness**: Verify layouts on mobile

---

## 📅 Milestone 6: Production Readiness
**Goal**: Go-live at `custommortgageinc.com`.

*   [ ] **Security Audit**: Verify `DEBUG=False`, secrets management
*   [ ] **Docker Optimization**: Multi-stage builds for minimal images
*   [ ] **Error Handling**: Global error boundaries (404/500)
*   [ ] **SEO Verification**: Meta tags, Sitemap.xml, Robots.txt
*   [ ] **Staging Deployment**: Deploy to staging environment
