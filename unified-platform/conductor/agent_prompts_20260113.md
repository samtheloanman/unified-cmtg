# Agent Prompts - 2026-01-13 00:48 PST

## 🔴 Prompt for Jules (Rebase PR)

```
Your PR `jules/phase1-foundation-10297780927730413954` needs to be rebased onto the updated main branch.

Main has received several commits since you branched:
- Phase 1 completion + conductor updates + styleguides
- Add integration-map, legacy code copy, Gemini analysis

TASK:
1. Fetch latest main: `git fetch origin main`
2. Rebase your branch: `git rebase origin/main`
3. Resolve any conflicts, prioritizing:
   - Keep your backend scaffolding (Django 5 + Wagtail 6 + split settings)
   - Keep main's styleguides (python.md, typescript.md)
   - Keep main's integration-map.md
   - Merge docker-compose.yml changes (include ALLOWED_HOSTS fix from main)
4. Force push: `git push -f origin jules/phase1-foundation-10297780927730413954`
5. Update the PR description with conflict resolution notes

Expected conflicts:
- docker-compose.yml
- unified-platform/conductor/tracks.md
- unified-platform/conductor/tracks/phase1_foundation/plan.md
```

---

## 🟢 Prompt for Claude Code (Continue Phase 2)

```
You are resuming work on the unified-cmtg project as The Generator (L2 Agent).

COMPLETED (by Gemini CLI):
- Legacy cmtgdirect copied to unified-platform/backend/legacy_cmtgdirect/
- Pricing models analysis created: conductor/tracks/port_pricing_ratesheet_20260112/legacy_pricing_models_analysis.md

VERIFIED:
- Analysis is accurate against actual legacy code
- Lender, BaseLoan, LoanProgram, LenderProgramOffering models documented
- Recommendation: Use LenderProgramOffering architecture for new platform

NEXT PRIORITY TASK: Analyze Legacy Pricing LOGIC
Track: port_pricing_ratesheet_20260112

1. Analyze `legacy/cmtgdirect/loans/queries.py`
2. Analyze `legacy/cmtgdirect/api/views.py` (especially QualifyView)
3. Document the `get_matched_loan_programs_for_qual()` function:
   - Inputs required
   - Matching criteria logic
   - Output format
   - Rate adjustment calculations

Create output: conductor/tracks/port_pricing_ratesheet_20260112/legacy_pricing_logic_analysis.md

Follow the Python styleguide at unified-platform/conductor/code_styleguides/python.md.
After completing, signal handoff to Ralph for verification.
```

---

## 🟡 Prompt for Gemini CLI (Verification Only)

```
You are Gemini CLI - assigned to VERIFICATION tasks only.

ROLE CHANGE: Orchestration tasks reassigned to Antigravity.
Your focus: Test execution, connectivity checks, simple confirmations.

CURRENT TASK: Verify frontend connectivity
1. Allow the `find` command to clean ._* files (already done by Antigravity)
2. Run: docker compose up -d
3. Test: curl http://localhost:3001/test
4. Report result: PASS or FAIL with details

DO NOT attempt to fix issues. If tests fail, report back and Antigravity will handle fixes.
```

---

## 🔵 Prompt for Antigravity (Orchestrator + Fixer)

```
You are Antigravity - now the primary ORCHESTRATOR for unified-cmtg.

ROLE EXPANDED:
- L1 Orchestrator responsibilities (from Gemini CLI)
- Command execution and fixes
- Conductor tracking updates
- Conflict resolution

COMPLETED THIS SESSION:
- Cleaned 112 ._* macOS metadata files from unified-platform/
- Pushed all changes to main (2d95a05)
- Created agent prompts

CURRENT AGENT STATUS:
| Agent | Task | Status |
|:---|:---|:---|
| Jules | Phase 4: Rate Sheet Infrastructure | 🔄 Working |
| Claude | Standing by for logic analysis prompt | ⏳ Ready |
| Gemini CLI | Frontend verification (after ._* cleanup) | 🔄 Retry |

NEXT TASKS:
1. Monitor Gemini CLI's frontend test result
2. Create checklist.md for port_pricing_ratesheet track
3. Update conductor/current.md with agent status
4. Provide Claude the logic analysis prompt when ready
```

