# Track Specification: Production Finalization

**Track ID**: `finalization_20260114`  
**Created**: 2026-01-14  
**Status**: Pending

---

## Overview

This track completes the unified-cmtg platform for production launch at `cmre.c-mtg.com`. It focuses on two critical components:

1. **Content Migration** - Migrate 75+ program pages from WordPress (custommortgageinc.com) to Wagtail CMS
2. **Programmatic SEO Engine** - Build infrastructure for 10,000+ city-specific landing pages with flat URL hierarchy

## Scope

### In Scope
- ✅ WordPress → Wagtail content migration (programs, blogs, funded loans)
- ✅ Programmatic SEO infrastructure (City model, LocalProgramPage, proximity mapping)
- ✅ AI content generation (OpenAI integration for unique city content)
- ✅ Next.js CMS integration (headless API consumption)
- ✅ Floify integration completion
- ✅ Security audit and production hardening
- ✅ Staging and production deployment

### Out of Scope
- ❌ Phase 7: AI Blog (NotebookLM) - Post-launch
- ❌ Phase 8: Affiliate Program - Post-launch
- ❌ Phase 9: Investment/Forum - Deferred

## Execution Strategy

**Jules-Centric**: Maximum use of Jules (cloud concurrent execution) for backend tasks.

**Concurrent Waves**:
- Wave 1: F.1 (Wagtail Models) - Foundation
- Wave 2: F.2 (WP Extraction) + F.4 (Office Import) - Parallel
- Wave 3: F.3 (Content Import) + F.5 (SEO Infrastructure) + F.7 (Next.js) + F.8 (Floify) - All parallel
- Wave 4: F.6 (AI Content) - After F.5
- Wave 5: F.9 (Testing) + F.10 (Deployment) - Sequential

## Success Criteria

1. **Content Parity**: All 75+ WordPress programs migrated to Wagtail
2. **URL Parity**: 100% URL match with WordPress for SEO
3. **Programmatic SEO**: Infrastructure ready to generate 10,000+ pages
4. **Production Ready**: Security audit passed, staging tested
5. **Launch Ready**: `cmre.c-mtg.com` deployed and functional

## Dependencies

- Existing work: Phase 1-4 complete (Foundation, Pricing Engine, Rate Sheets, Frontend)
- Phase 5 Floify: Partially complete (needs testing)
- WordPress access: API available at custommortgageinc.com
- OpenAI API key: For content generation
- Staging environment: For pre-production testing

## Risks

1. **WordPress data quality** - ACF fields may have inconsistencies
2. **OpenAI costs** - Generating 10K+ pages with GPT-4 (estimate: $500-1000)
3. **URL migration** - Must maintain SEO without breaking links
4. **Timeline pressure** - Significant scope, need parallel execution

## Mitigation

- Start with small batch imports (10-20 pages) to validate
- Implement content caching to avoid regeneration
- Create comprehensive URL mapping before migration
- Use Jules concurrency to compress timeline
