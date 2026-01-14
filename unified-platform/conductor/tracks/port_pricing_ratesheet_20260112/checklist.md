# Track Checklist: Port Pricing & Rate Sheet MVP

**Track ID**: `port_pricing_ratesheet_20260112`  
**Last Updated**: 2026-01-13 22:16 PST

---

## Phase 1: Environment Setup & Legacy Code Analysis

- [x] Jules - Set up Django/Wagtail backend (`unified-platform/backend/`)
- [x] Jules - Set up Next.js frontend (`unified-platform/frontend/`)
- [x] Claude/Gemini - Copy legacy cmtgdirect to `backend/legacy_cmtgdirect/`
- [x] Claude/Gemini - Analyze legacy models (`legacy_pricing_models_analysis.md`)
- [ ] Claude - Analyze legacy pricing logic (`legacy_pricing_logic_analysis.md`)
- [ ] Conductor - Manual verification of Phase 1

---

## Phase 2: Pricing Engine Porting

- [x] Claude - Generate `Lender` model
- [x] Claude - Generate `LoanProgram` model  
- [x] Ralph - Unit tests for models
- [x] Claude - Port `get_matched_loan_programs_for_qual()` logic
- [x] Ralph - Unit tests for pricing logic
- [x] Claude - Create DRF API endpoints
- [ ] Ralph - Integration tests

---

## Phase 3: Rate Sheet Ingestion MVP

- [x] Jules - Create `ratesheets` app infrastructure ✅
- [x] Claude - Generate `RateSheet` and `RateAdjustment` models ✅
- [x] Ralph - Unit tests for models ✅
- [x] Jules - Configure Celery + Redis ✅
- [x] Claude - PDF parsing service (PdfPlumber + Gemini AI) ✅
- [x] Claude - Ingestion service (JSON → DB) ✅
- [x] Antigravity - QuoteView real data integration ✅
- [ ] Ralph - Integration tests

---

## Phase 3.5: Browser-Testable State ✅ COMPLETE

- [x] Jules - Created PR with fixes (URL routing, seed data, frontend)
- [x] Antigravity - Fixed brand colors (Navy/Gold → Cyan/Gray)
- [x] Antigravity - Verified frontend build (no errors)
- [x] Antigravity - Verified backend API health
- [x] Antigravity - Browser test verification (see ANTIGRAVITY_VERIFICATION.md)

---

## Phase 4: Frontend Integration & MVP Demo (NEXT)

- [ ] Claude - Refactor Quote Wizard to multi-step flow
- [ ] Claude - Enhance results display with comparison table
- [ ] Claude - Add loading and error states
- [ ] Claude - Component testing (>80% coverage)
- [ ] Conductor - End-to-end MVP review

---

## Agent Assignments

| Agent | Current Task |
|:---|:---|
| Claude Code | **Phase 4**: Multi-step Quote Wizard |
| Antigravity | Documentation sync, oversight |
| Ralph | Integration tests (pending) |
| Jules | Standby |

---

## Current Status

**Phase 3.5**: ✅ COMPLETE  
**Next Phase**: Phase 4 - Frontend Integration  
**See**: `ANTIGRAVITY_VERIFICATION.md` for Phase 3.5 completion details  
**See**: [claude_prompt.md](file:///home/samalabam/.gemini/antigravity/brain/969d8981-5a6e-4d06-a2dc-6044e954466b/claude_prompt.md) for Phase 4 instructions
