# Conductor Task List
**Source**: Finalization Track (2026-01-14)
**Rule**: Task is complete only when acceptance tests pass ✅

---

## 🔴 CURRENT PRIORITY: Finalization Track (F.1 - F.10)

## F.1: Wagtail CMS Models
- [ ] **Refactor Models**: Split `cms/models.py` to package
  - Test: `import cms.models` succeeds
- [ ] **ProgramPage**: Implement with 64 fields + StreamField FAQ
  - Test: Admin page load verified
- [ ] **BlogPage**: Implement basic blog model
  - Test: Create blog post in Admin
- [ ] **FundedLoanPage**: Implement case studies
  - Test: Create funded loan in Admin
- [ ] **Legacy Pages**: Move Home/Standard/LegacyRecreated
  - Test: Existing pages accessible

## F.2: WordPress Content Extraction
- [ ] **Extractor Script**: Export WP to JSON
  - Test: `programs.json` created with data

## F.3: Content Import & URL Migration
- [ ] **Import Command**: Load JSON to Wagtail
  - Test: Pages exist in Wagtail
- [ ] **URL Verify**: URLs match legacy
  - Test: URL mapping check passes

## F.4: Office Location Import
- [ ] **Office Model**: Create with Lat/Lon
  - Test: Model exists
- [ ] **Import CSV**: Load locations
  - Test: `Office.objects.count() > 0`

## F.5: Programmatic SEO Infrastructure
- [ ] **Proximity Logic**: Haversine service
  - Test: Distance calc correct
- [ ] **Flat Routing**: `/program-city-state/`
  - Test: Route resolves

## F.6: AI Content Generation
- [ ] **OpenRouter Setup**: Configure MCP/Key
  - Test: API call succeeds
- [ ] **Generation Service**: Intro/FAQ generator
  - Test: Content generated

## F.7: Next.js CMS Integration
- [ ] **API Client**: Fetch from v2 API
  - Test: Frontend displays content

## F.8: Floify Completion
- [ ] **Webhook**: Handle application events
  - Test: Webhook success 200

## F.9: Testing & Hardening
- [ ] **E2E Tests**: Playwright suite
  - Test: All pass

## F.10: Production Deployment
- [ ] **Deploy**: Go live
  - Test: Site accessible on prod domain

---

**Last Updated**: 2026-01-14
