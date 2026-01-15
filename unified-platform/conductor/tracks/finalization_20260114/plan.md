# Production Finalization Track - Detailed Plan

**Track ID**: `finalization_20260114`  
**Status**: Ready to Start  
**Primary Agent**: Jules

---

## Phase Breakdown

See `implementation_plan.md` in Antigravity brain for full details.

### F.1: Wagtail CMS Models & Structure (4-6h)
- Agent: Jules
- Create ProgramPage, FundedLoanPage, BlogPage models
- Map 64 ACF fields from WordPress
- Run migrations

### F.2: WordPress Content Extraction (2-3h)
- Agent: Jules
- Build REST API extractor
- Export programs, blogs, media to JSON
- Generate URL mapping CSV

### F.3: Content Import & URL Migration (4-6h)
- Agent: Jules + Antigravity
- Import JSON to Wagtail
- Verify URL parity
- Fix any mismatches

### F.4: Location & Office Data Import (2-3h) ⚡ Parallel
- Agent: Jules
- Create Office model with GPS
- Import 200+ office locations
- Geocode if needed

### F.5: Programmatic SEO Infrastructure (6-8h)
- Agent: Jules
- Create City and LocalProgramPage models
- Build Haversine proximity service
- Import city database (150-500 cities)
- Schema markup generator

### F.6: AI Content Generation Pipeline (4-5h)
- Agent: Gemini CLI
- OpenAI integration for unique content
- Bulk page generation command
- Generate 50-100 test pages

### F.7: Next.js CMS Integration (6-8h) ⚡ Parallel
- Agent: Claude Code
- Wagtail API client
- Dynamic program pages
- Local SEO pages (flat URLs)
- Blog integration

### F.8: Floify Integration Completion (3-4h) ⚡ Parallel
- Agent: Jules
- Test lead submission
- Test webhook handlers
- Fix any integration issues

### F.9: Production Hardening & Testing (8-10h)
- Agent: All (Antigravity orchestration)
- Security audit
- Performance optimization
- E2E testing
- SEO verification
- Load testing

### F.10: Deployment & Cutover (4-6h)
- Agent: Antigravity + Jules
- Staging deployment
- Production deployment
- DNS configuration
- Traffic migration
- Monitoring setup

---

## Execution Timeline

### Week 1: Foundation & Content Migration
- **Days 1-2**: F.1, F.2, F.4 (Jules concurrent)
- **Days 3-4**: F.3, F.5 start (Jules concurrent)

### Week 2: SEO Engine & Frontend
- **Days 1-2**: F.5 complete, F.6 (Gemini + Jules)
- **Days 3-5**: F.7, F.8 (Claude + Jules concurrent)

### Week 3: Testing & Deployment
- **Days 1-3**: F.9 (All agents)
- **Days 4-5**: F.10 (Deployment)

**Total**: ~15 working days with concurrency

---

## Agent Work Distribution

### Jules (29-42 hours)
Majority of backend infrastructure work, optimized for cloud concurrency.

### Gemini CLI (6-7 hours)
AI content generation pipeline, load testing, orchestration.

### Claude Code (6-8 hours)
Frontend CMS integration.

### Antigravity (7-9 hours)
QA, verification, deployment oversight.

---

## Verification Gates

Each phase has explicit success criteria. No phase proceeds without:
1. ✅ Acceptance tests passing
2. ✅ Agent handoff documentation
3. ✅ No blocking errors

---

See `checklist.md` for detailed task tracking.
