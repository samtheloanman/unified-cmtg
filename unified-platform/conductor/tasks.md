# Conductor Task List
**Source**: PRD v2.0 + New Features Spec (2026-01-12)  
**Rule**: Task is complete only when acceptance tests pass ✅

---

## 🔴 CURRENT PRIORITY: Phase 1 Completion

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

### 🔄 In Progress
- [x] **Legacy cmtgdirect**: Verify running on port 8000
  - Test: `curl http://localhost:8000/admin/` returns 200
  - Superuser: admin/admin ✅
- [x] **Frontend Connectivity**: Next.js fetches from Django
  - Test: Visit `http://localhost:3001/test` shows "API Status: ok"

### ⏳ Not Started
- [x] **Superuser**: Create Wagtail admin user
  - Test: Login to `http://localhost:8001/admin/` succeeds
  - Superuser: admin/admin ✅

---

## Phase 2: Core Pricing Engine (Week 2)

- [ ] **Port Models**: `Lender`, `LoanProgram`, `BaseLoan` from cmtgdirect
  - Test: `python manage.py makemigrations pricing` creates migration
- [ ] **Port Logic**: `QualifyView` matching to `pricing/services.py`
  - Test: Unit test `test_loan_matching.py` passes
- [ ] **Rate Adjustment**: FICO × LTV grids
  - Test: `pytest pricing/tests/test_rate_adjustment.py` passes
- [ ] **Pricing API**: `/api/v1/quote` endpoint
  - Test: `curl -X POST http://localhost:8001/api/v1/quote/ -d '{...}'` returns rates

---

## Phase 3: Content Migration (Week 3)

- [x] **ProgramPage Model**: 64 ACF fields in Wagtail
  - Test: `python manage.py makemigrations cms` succeeds
- [ ] **WP Extraction**: Dump WordPress content to JSON
  - Test: `python manage.py export_wp_content --output programs.json` creates file
- [ ] **Import Command**: Ingest JSON into Wagtail
  - Test: `python manage.py import_programs programs.json` imports 75+ pages
- [ ] **URL Verification**: URLs match WordPress 1:1
  - Test: Automated URL comparison script passes

---

## Phase 3a: Programmatic SEO (Week 4)

- [ ] **Office Model**: GPS coordinates for proximity
  - Test: `Office.objects.count() == [number from CSV]`
- [ ] **Location Import**: Import CSV
  - Test: `python manage.py import_offices` completes without error
- [ ] **Proximity Service**: Haversine calculator
  - Test: `pytest cms/tests/test_proximity.py` passes
- [ ] **Demographics**: Import Census data
  - Test: City population data populated
- [ ] **OpenAI Content**: FAQ/intro generation
  - Test: Generated FAQ is unique per city
- [ ] **Page Generator**: Management command
  - Test: `python manage.py generate_local_pages --count 10` creates 10 pages
- [ ] **Flat URLs**: Verify `/program-city-state/` format
  - Test: URL regex matches flat pattern

---

## Phase 4: Rate Sheet Agent (Week 5)

- [ ] **Ingestion Script**: Read `Ratesheet List.csv`
  - Test: Script reads CSV without error
- [ ] **Pipeline Class**: `IngestionPipeline` logic
  - Test: Pipeline processes sample PDF
- [ ] **PDF Extraction**: Gemini 1.5 Pro → JSON
  - Test: Extracted rates match expected values
- [ ] **Review UI**: Admin dashboard
  - Test: Manual review - approve button works

---

## Phase 5: Frontend Finish & Polish (Week 5)

- [ ] **Home Page**: Connect CMS fields to Next.js Hero/Features
  - Test: Home page content matches Wagtail admin
- [ ] **Program Pages**: Dynamic routing `/programs/[slug]`
  - Test: Individual program pages load correct content
- [ ] **Quote Wizard**: Complete multi-step form logic
  - Test: User can complete quote flow
- [ ] **Quote Results**: Display API results from Pricing Engine
  - Test: Real rates appear after quote submission
- [ ] **Styling Policy**: Verify consistent Tailwind branding (Colors/Fonts)
  - Test: Visual regression check
- [ ] **Mobile Responsiveness**: Verify layouts on mobile
  - Test: Chrome DevTools device mode check

---

## Phase 6: Production Readiness & Deployment (Week 6)

- [ ] **Security Audit**: Verify `DEBUG=False`, secrets management
  - Test: `manage.py check --deploy` passes
- [ ] **Docker Optimization**: Multi-stage builds for minimal images
  - Test: Image size < 500MB
- [ ] **Error Handling**: Global error boundaries (404/500)
  - Test: Manually trigger errors
- [ ] **SEO Verification**: Meta tags, Sitemap.xml, Robots.txt
  - Test: Lighthouse SEO score > 90
- [ ] **Staging Deployment**: Deploy to staging environment
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

**Last Updated**: 2026-01-12 01:14 PST
