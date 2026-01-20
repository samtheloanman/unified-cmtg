# Conductor Task List
**Source**: PRD v2.0 + New Features Spec (2026-01-12)  
**Rule**: Task is complete only when acceptance tests pass ✅

---

## 🔴 CURRENT PRIORITY: Phase 6: Production Readiness & Deployment (Phase F.9)

## Phase 1: Foundation & Legacy Verification (Week 1)

### ✅ Completed
- [x] **Repo Setup**: Initialize `unified-platform` structure
  - Test: `ls unified-platform/backend unified-platform/frontend` returns dirs
- [x] **Frontend Init**: Initialize Next.js 14 + Tailwind
  - Test: `docker compose ps | grep frontend` shows running
- [x] **Backend Init**: Django + Wagtail in Docker
  - Test: `docker compose exec backend python manage.py check` returns no issues
- [x] **Health API**: `/api/v1/health/` endpoint
  - Test: `curl http://localhost:8001/api/v1/health/` returns `{"status":"ok"}`
- [x] **Jules Automation System**: Ralph-loop infrastructure
  - Test: `ralph-loop` script active and syncing documentation ✅

### ✅ Completed
- [x] **Legacy cmtgdirect**: Verify running on port 8000
  - Test: `curl http://localhost:8000/admin/` returns 200
  - Superuser: admin/admin ✅
- [x] **Frontend Connectivity**: Next.js fetches from Django
  - Test: Visit `http://localhost:3001/test` shows "API Status: ok"

### ✅ Completed
- [x] **Superuser**: Create Wagtail admin user
  - Test: Login to `http://localhost:8001/admin/` succeeds
  - Superuser: admin/admin ✅

---

## Phase 2: Core Pricing Engine (Week 2) (Jules - Assigned)

- [x] **Port Models**: `Lender`, `LoanProgram`, `BaseLoan` from cmtgdirect (Jules - Assigned)
  - Test: `python manage.py makemigrations pricing` creates migration
- [x] **Port Logic**: `QualifyView` matching to `pricing/services.py` (Jules - Assigned)
  - Test: Unit test `test_loan_matching.py` passes
- [x] **Rate Adjustment**: FICO × LTV grids (Jules - Assigned)
  - Test: `pytest pricing/tests/test_rate_adjustment.py` passes
- [x] **Pricing API**: `/api/v1/quote` endpoint (Jules - Assigned)
  - Test: `curl -X POST http://localhost:8001/api/v1/quote/ -d '{...}'` returns rates

---

## Phase 3: Content Migration (Week 3)

### ✅ Completed
- [x] **ProgramPage Model**: 64 ACF fields in Wagtail - COMPLETED (F.1)
  - Test: `python manage.py makemigrations cms` succeeds ✅
  - Migrations 0002-0005 exist with all field definitions
  - BlogIndexPage, FundedLoanPage, Office models also implemented
- [x] **Office Model**: GPS coordinates for proximity (F.4)
  - Test: `Office.objects.count() == [number from CSV]` ✅
  - Latitude/longitude fields present for Haversine calculations
- [x] **WP Extraction**: Dump WordPress content to JSON (F.2)
  - Test: `programs.json` exists in `backend/wp_export/` ✅
- [x] **Import Command**: Ingest JSON into Wagtail (F.3)
  - Test: `python manage.py import_wordpress` executed ✅
- [x] **URL Verification**: URLs match WordPress 1:1 (F.3)
  - Test: `python manage.py verify_content` passed (100% parity for Blogs/Loans) ✅

### ⏳ In Progress
- [x] **Firecrawl Integration**: Refined content extraction source (Antigravity - Done ✅)

---

## Phase 3a: Programmatic SEO (Phase F.5A - F.5E)

### ⏳ F.5A: Core Infrastructure (Jules - Current)
- [x] **City Model**: `models/cities.py` with priority/launched_at (Claude - Assigned)
  - Test: Model exists with correct fields ✅
- [x] **SEOContentCache**: `models/seo.py` with expanded schema fields (Claude - Assigned)
  - Test: Model handles content_hash and schema_json ✅
- [x] **ProximityService**: Caching + Haversine (Claude - Assigned)
  - Test: `find_nearest_office` returns correct office ✅
- [x] **SchemaGenerator**: Extended JSON-LD support (Claude - Assigned)
  - Test: Generates HowTo/Speakable/FinancialProduct ✅
- [x] **SEOResolver**: Defensive slug parsing (Claude - Assigned)
  - Test: Resolves `/dscr-loan-los-angeles-ca/` correctly ✅

### ⏳ F.5B: Pilot Data (Jules - Next)
- [x] **Import Pilot Cities**: Top 5 only (Claude - Assigned)
- [x] **Office Mapping**: Verify Physical Offices (Claude - Assigned)

### ⏳ F.5C: Content (Gemini)
- [x] **Generate Power 5**: Create 25 perfect pages (Claude - Assigned)
- [x] **Verify Content**: Manual QA (Claude - Assigned)

### ✅ F.5D: Site Links & Final Polish (Antigravity)
- [x] Audit all site links (Header, Footer, Home)
- [x] Fix "Sign In" link in Header
- [x] Standardize Footer links (Privacy, Terms, About, Contact)
- [x] Enhance Frontend catch-all route to handle standard Wagtail pages
- [x] Create stub pages in Wagtail for missing core content
- [x] Final end-to-end verification of site navigation

---

## Phase 3b: AI Content Generation (Phase F.6)

### ✅ Completed (Antigravity)
- [x] **AiContentGenerator Service**: Gemini 2.0 Integration with Dynamic Persona Support
  - Test: Generates JSON content for "Business Loans" with SBA Expert persona ✅
- [x] **Management Commands**:
  - `generate_program_content`: Batch generation for Program Pages
  - `generate_local_pages`: Batch generation for Local Landing Pages
- [x] **Program Hierarchy**: 100+ Program Shells created and verified ✅
- [x] **Schema Markup**: JSON-LD for Local and Program pages ✅
- [x] **Secure API Handling**: Key rotation and .env configuration ✅

---

## Phase 4: Rate Sheet Agent (Week 5)

- [x] **Ingestion Script**: Read `Ratesheet List.csv` (Claude - Assigned)
  - Test: Script reads CSV without error
- [x] **Pipeline Class**: `IngestionPipeline` logic (Claude - Assigned)
  - Test: Pipeline processes sample PDF
- [x] **PDF Extraction**: Gemini 1.5 Pro → JSON (Claude - Assigned)
  - Test: Extracted rates match expected values
- [x] **Review UI**: Admin dashboard (Claude - Assigned)
  - Test: Manual review - approve button works

---

## Phase 5: Frontend Finish & Polish (Week 5) / F.7: Next.js CMS Integration

### ✅ Completed
- [x] **Program Pages**: Dynamic routing `/programs/[slug]` - COMPLETED (F.7)
  - Test: Individual program pages load correct content ✅
  - Implementation: /frontend/src/app/programs/[slug]/page.tsx (432 lines)
  - Features: SSG with generateStaticParams(), SEO metadata, MortgageLoan schema markup, CMS field rendering
- [x] **Blog Pages**: Dynamic routing `/blog/[slug]` - COMPLETED (F.7)
  - Test: Blog pages load with SSG ✅
  - Implementation: /frontend/src/app/blog/[slug]/page.tsx (233 lines)
  - Features: SSG, SEO metadata, BlogPosting schema, full branding

### ⏳ In Progress / Pending
- [x] **Home Page**: Connect CMS fields to Next.js Hero/Features (Claude - Assigned)
  - Test: Home page content matches Wagtail admin
- [x] **Quote Wizard**: Complete multi-step form logic (Claude - Assigned)
  - Test: User can complete quote flow
- [x] **Quote Results**: Display API results from Pricing Engine (Claude - Assigned)
  - Test: Real rates appear after quote submission
- [x] **Local SEO Pages**: Flat URL format `/program-city-state/` (F.5) (Claude - Assigned)
  - Test: SSG generates 10,000+ pages
- [x] **Styling Policy**: Verify consistent Tailwind branding (Colors/Fonts) (Claude - Assigned)
  - Test: Visual regression check
- [x] **Mobile Responsiveness**: Verify layouts on mobile (Jules - Assigned)
  - Test: Chrome DevTools device mode check

---

## Phase 6: Production Readiness & Deployment (Week 6)

- [ ] **Security Audit**: Verify `DEBUG=False`, secrets management (Antigravity - Assigned)
  - Test: `manage.py check --deploy` passes
- [ ] **Docker Optimization**: Multi-stage builds for minimal images (Antigravity - Assigned)
  - Test: Image size < 500MB
- [ ] **Error Handling**: Global error boundaries (404/500) (Antigravity - Assigned)
  - Test: Manually trigger errors
- [ ] **SEO Verification**: Meta tags, Sitemap.xml, Robots.txt (Claude - Assigned)
  - Test: Lighthouse SEO score > 90
- [ ] **Staging Deployment**: Deploy to staging environment (Antigravity - Assigned)
  - Test: Full E2E smoke test on staging


---

## Agent Research Tasks

| Task | Assigned To | Priority |
|------|-------------|----------|
| Best affordable RE data API | Research Agent | High |
| Affiliate disclaimer wording | Legal Research | High |
| Misago alternatives | Tech Research | Medium |
| Delaware trust (DST) structure | Legal Research | Medium |
| Distressed property workflows | Future Features | Low |

---

**Last Updated**: 2026-01-16 03:19  (Ralph-Loop Sync)