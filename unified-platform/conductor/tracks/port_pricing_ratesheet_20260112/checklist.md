# Track Checklist: Port Pricing & Rate Sheet MVP

**Track ID**: `port_pricing_ratesheet_20260112`  
**Last Updated**: 2026-01-13 01:22 PST

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
- [x] Claude - PDF download/parsing service (PdfPlumber Base / Google Gemini SDK) ✅
- [ ] Claude - Data extraction to models (Pending Gemini Logic)
- [ ] Claude - Integrate with LoanProgram
- [ ] Ralph - Integration tests (Gemini Verification Pending)

---

## Phase 4: Frontend Integration & MVP Demo

- [ ] Claude - Next.js components for loan programs
- [ ] Claude - Connect frontend to pricing API
- [ ] Claude - Rate sheet upload UI
- [ ] Conductor - End-to-end MVP review

---

## Agent Assignments

| Agent | Current Task |
|:---|:---|
| Jules | RateSheet models (Phase 3) |
| Claude | PDF Parsing (Phase 3) |
| Ralph | Integration Tests (Phase 3) |
| Antigravity | Orchestration |
