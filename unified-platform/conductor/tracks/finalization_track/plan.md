# Finalization Track (F.1 - F.10)

**Goal**: Complete all remaining feature work for the Unified CMTG Platform v2.0 launch.
**Status**: Active
**Focus**: CMS, Content Migration, Local SEO, and Floify Integration.

---

## 📅 Roadmap

| Phase | Task | Status | Dependencies |
|-------|------|--------|--------------|
| **F.1** | **Wagtail CMS Models** | 🔴 Active | None |
| **F.2** | **WordPress Content Extraction** | ⏳ Pending | F.1 |
| **F.3** | **Content Import & URL Migration** | ⏳ Pending | F.2 |
| **F.4** | **Office Location Import** | ⏳ Pending | F.1 (Parallel) |
| **F.5** | **Programmatic SEO Infrastructure** | ⏳ Pending | F.4 |
| **F.6** | **AI Content Generation** | ⏳ Pending | F.5 |
| **F.7** | **Next.js CMS Integration** | ⏳ Pending | F.1 (Parallel) |
| **F.8** | **Floify Completion** | ⏳ Pending | F.5 (Parallel) |
| **F.9** | **Testing & Hardening** | ⏳ Pending | All above |
| **F.10** | **Production Deployment** | ⏳ Pending | F.9 |

---

## 📝 Phase Details

### F.1: Wagtail CMS Models
**Goal**: Establish the content data structure.
- Refactor `cms/models.py` into `cms/models/` package.
- Implement `ProgramPage` with 64+ ACF fields.
- Implement `BlogPage` for basic blog posts (WordPress import target).
- Implement `FundedLoanPage` for case studies.
- Implement `HomePage` and `StandardPage`.

### F.2: WordPress Content Extraction
**Goal**: Get data out of legacy WordPress.
- Create extractor script/command.
- Output JSON dumps of Programs, Blogs, Funded Loans.

### F.3: Content Import & URL Migration
**Goal**: Populate Wagtail and ensure SEO continuity.
- Import scripts for all content types.
- Verify 1:1 URL mapping.

### F.4: Office Location Import
**Goal**: Import branch locations for Local SEO.
- Import `Office` models from CSV.
- Geocode addresses (Lat/Lon).

### F.5: Programmatic SEO Infrastructure
**Goal**: Engine for generating 10,000+ local pages.
- Implement proximity logic (Haversine).
- Define "Flat URL" routing strategy (`/program-city-state/`).

### F.6: AI Content Generation
**Goal**: Generate unique local content.
- Configure OpenRouter / OpenAI via MCP.
- Implement generation logic for FAQs and Intros.

### F.7: Next.js CMS Integration
**Goal**: Frontend display of CMS content.
- Connect Next.js to Wagtail API v2.
- Build dynamic page templates.

### F.8: Floify Completion
**Goal**: Finish lead capture pipeline.
- Finalize "Apply Now" flow.
- Ensure Webhook processing works.

### F.9: Testing & Hardening
**Goal**: QA before launch.
- E2E Testing (Playwright).
- Security audit.
- Performance tuning.

### F.10: Production Deployment
**Goal**: Go Live.
- Deploy to production environment.
- DNS switchover.
