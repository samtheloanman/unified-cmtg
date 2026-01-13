# Agent Prompts - 2026-01-13 01:12 PST (Post-Merge)

## 📊 Current State
- **Main**: `d5dc7d1` (merged Jules PR)
- **Jules PR**: Merged ✅
- **Phase 1**: Complete
- **Phase 4**: Infrastructure scaffolded

---

## 🔴 Prompt for Jules (Next Task)

```
Your PR has been merged into main. Great work on Phase 1 + Phase 4 infrastructure!

COMPLETED:
- Backend scaffolding (Django 5 + Wagtail 6 + split settings)
- Ratesheets app with csv_reader.py and downloader.py
- Health check endpoint

NEXT TASK: Phase 4 Step 2 - RateSheet Models
Reference: unified-platform/conductor/tracks/phase4_ratesheet/plan.md

1. Create RateSheet model in ratesheets/models.py:
   - lender (ForeignKey)
   - program_type (ForeignKey)
   - effective_date
   - pdf_url, pdf_hash
   - extracted_data (JSONField)
   - status (pending, approved, rejected)

2. Create RateAdjustment model:
   - rate_sheet (ForeignKey)
   - adjustment_type (fico, ltv, property_type, etc.)
   - adjustment_grid (JSONField)

3. Run makemigrations and migrate

Follow: unified-platform/conductor/code_styleguides/python.md
```

---

## 🟢 Prompt for Claude Code (Logic Analysis)

```
You are The Generator (L2 Agent) for unified-cmtg.

CONTEXT UPDATE:
- Jules' PR merged - backend now has split settings + ratesheets app
- Legacy code at: unified-platform/backend/legacy_cmtgdirect/ (embedded repo)
- Models analysis complete: conductor/tracks/port_pricing_ratesheet_20260112/legacy_pricing_models_analysis.md

YOUR TASK: Analyze Legacy Pricing LOGIC
Track: port_pricing_ratesheet_20260112

1. Read and analyze:
   - unified-platform/backend/legacy_cmtgdirect/loans/queries.py
   - unified-platform/backend/legacy_cmtgdirect/api/views.py

2. Document the `get_matched_loan_programs_for_qual()` function:
   - Input parameters and their types
   - Filtering/matching criteria
   - Rate adjustment logic
   - Output format

3. Create: unified-platform/conductor/tracks/port_pricing_ratesheet_20260112/legacy_pricing_logic_analysis.md

4. After completing, update track checklist and signal handoff to Ralph.

Follow: unified-platform/conductor/code_styleguides/python.md
```

---

## 🟡 Prompt for Gemini CLI (Verification)

```
ROLE: Verification Agent (test execution only)

CURRENT TASK: Verify frontend connectivity
Prerequisites completed by Antigravity:
- Cleaned ._* files
- Merged Jules PR with backend fixes

STEPS:
1. cd /path/to/unified-cmtg/unified-platform
2. docker compose up -d
3. Wait 30 seconds for services
4. curl http://localhost:3001/test
5. Report: PASS or FAIL

If FAIL, report error and stop. Antigravity will fix.
```

---

## 🔵 Antigravity Status (Orchestrator)

```
COMPLETED:
- Merged Jules PR (d5dc7d1)
- Cleaned 112 ._* files
- Updated agent prompts

MONITORING:
- Claude: Logic analysis
- Gemini CLI: Frontend test
- Jules: RateSheet models

NEXT:
- Create port_pricing_ratesheet checklist.md
- Update conductor/current.md
- Verify frontend when Gemini CLI reports
```
