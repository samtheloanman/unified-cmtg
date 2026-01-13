# Agent Prompts - 2026-01-13 01:29 PST (Phase 2)

## 📊 Current State
- **Main**: `0b36fe3` (all fixes pushed)
- **Phase 1**: ✅ Complete
- **Phase 2**: Starting

---

## 🔴 Verbose Prompt for Jules (Builder)

```
# MISSION: Run Phase 2 Migrations
# ROLE: Senior DevOps & Backend Engineer (The Builder)
# CONTEXT:
Phase 1 is complete. All services are running.
Claude is generating new pricing models for Phase 2.
Your job is to run migrations once models are ready.

# PREREQUISITES (Wait for these):
- Claude must complete: `unified-platform/backend/pricing/models/` files
- Files to watch for:
  - pricing/models/programs.py
  - pricing/models/program_types.py
  - pricing/models/adjustments.py

# YOUR TASKS:

## 1. Sync with latest main
cd ~/code/unified-cmtg
git pull origin main
cd unified-platform

## 2. Rebuild and restart services
docker compose build backend
docker compose up -d

## 3. Run migrations
docker compose exec backend python manage.py makemigrations pricing
docker compose exec backend python manage.py migrate

## 4. Verify migrations
docker compose exec backend python manage.py showmigrations pricing
# Expected: All migrations should show [X] applied

## 5. (Optional) Load fixtures if provided
docker compose exec backend python manage.py loaddata fixtures/sample_lenders.json

# SUCCESS CRITERIA:
- [ ] `makemigrations pricing` creates migration files
- [ ] `migrate` applies without errors
- [ ] `showmigrations` shows all applied
- [ ] Backend still responds 200 on `/api/v1/health/`

# HANDOFF:
When complete, update conductor/current.md and signal to L1 Orchestrator.
```

---

## 🟢 Verbose Prompt for Claude (Generator)

```
# MISSION: Complete Phase 2 - Pricing Engine Porting
# ROLE: Senior Python Developer (The Generator)
# CONTEXT:
Phase 1 is complete. You are now porting the pricing engine from legacy cmtgdirect.

# COMPLETED WORK:
- Legacy analysis created: conductor/tracks/port_pricing_ratesheet_20260112/legacy_pricing_models_analysis.md
- Legacy code copied: unified-platform/backend/legacy_cmtgdirect/

# YOUR TASKS (In Order):

## Task 2.1: Port Core Models
Create these files in `unified-platform/backend/pricing/`:

### models/__init__.py
```python
from .programs import Lender, BaseLoan, LoanProgram
from .program_types import ProgramType, LenderProgramOffering
from .adjustments import RateAdjustment
```

### models/programs.py
Port from: legacy_cmtgdirect/loans/models/programs.py
- Lender model (company_name, include_states, contacts)
- BaseLoan abstract model (all eligibility fields)
- LoanProgram model (inherits BaseLoan)
Changes needed:
- Update imports: `from loans.` → `from pricing.`
- Keep `common.fields.ChoiceArrayField` or replace with Django ArrayField

### models/program_types.py
Port from: legacy_cmtgdirect/loans/models/program_types.py
- ProgramType model (canonical program definitions)
- LenderProgramOffering model (lender-specific pricing/overlays)

### models/adjustments.py (NEW)
Create the RateAdjustment model:
```python
from django.db import models
from .program_types import LenderProgramOffering

class RateAdjustment(models.Model):
    offering = models.ForeignKey(LenderProgramOffering, on_delete=models.CASCADE, related_name='adjustments')
    adjustment_type = models.CharField(max_length=20, choices=[
        ('fico_ltv', 'Credit Score × LTV Grid'),
        ('purpose', 'Loan Purpose'),
        ('occupancy', 'Occupancy Type'),
        ('property_type', 'Property Type'),
        ('loan_amount', 'Loan Amount Tier'),
    ])
    # For 1D lookups
    value_key = models.CharField(max_length=50, blank=True)
    # For 2D grids (FICO × LTV)
    row_min = models.FloatField(null=True, blank=True)
    row_max = models.FloatField(null=True, blank=True)
    col_min = models.FloatField(null=True, blank=True)
    col_max = models.FloatField(null=True, blank=True)
    # Adjustment value
    adjustment_points = models.FloatField()
    
    class Meta:
        ordering = ['adjustment_type', 'row_min', 'col_min']
```

## Task 2.2: Port Matching Logic
### services/matching.py
Port from: legacy_cmtgdirect/loans/queries.py
Create LoanMatchingService class wrapping `get_matched_loan_programs_for_qual()`

## Task 2.3: Create Quote API
### Update api/views.py
Add QuoteView that uses LoanMatchingService

### Update api/urls.py
Add: `path('v1/quote/', QuoteView.as_view(), name='quote'),`

# STYLEGUIDE:
Follow: unified-platform/conductor/code_styleguides/python.md

# SUCCESS CRITERIA:
- [ ] All models created without syntax errors
- [ ] Imports updated to `pricing.` namespace
- [ ] No circular imports
- [ ] Ready for `makemigrations`

# HANDOFF:
When models are complete, signal to Jules to run migrations.
Then continue with services/matching.py and Quote API.
```

---

## 🟡 Verbose Prompt for Gemini CLI (Verifier)

```
# MISSION: Verify Phase 2 Progress
# ROLE: Verification Agent (Ralph-lite)
# CONTEXT:
You are the verification agent. You run tests and report results.
You do NOT fix issues - you report them to Antigravity.

# SYNC FIRST:
cd ~/code/unified-cmtg
git pull origin main
cd unified-platform
docker compose build frontend
docker compose up -d

# VERIFICATION TASKS:

## 1. Verify Services Running
docker compose ps
# Expected: All 4 services running (backend, frontend, db, redis)

## 2. Verify Backend Health
curl http://localhost:8001/api/v1/health/
# Expected: {"status": "ok"}

## 3. Verify Frontend
curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/
# Expected: 200

## 4. Verify Migrations (after Jules runs them)
docker compose exec backend python manage.py showmigrations pricing
# Expected: All [X] applied

## 5. Verify Quote API (after Claude completes it)
curl -X POST http://localhost:8001/api/v1/quote/ \
  -H "Content-Type: application/json" \
  -d '{"property_state": "CA", "loan_amount": 500000, "credit_score": 720, "property_value": 650000, "property_type": "sfr", "loan_purpose": "purchase", "occupancy": "primary"}'
# Expected: JSON response with quotes array

# REPORTING:
For each check, report:
- ✅ PASS: [description]
- ❌ FAIL: [description] + [error message]

If FAIL, do NOT attempt to fix. Report to Antigravity for resolution.
```

---

## 🔵 Verbose Prompt for Antigravity (Orchestrator)

```
# MISSION: Orchestrate Phase 2 Execution
# ROLE: L1 Orchestrator + Fixer
# CONTEXT:
You are coordinating all agents for Phase 2.

# CURRENT STATUS:
| Agent | Current Task | Status |
|:---|:---|:---|
| Claude | Port pricing models | 🔄 Working |
| Jules | Standby for migrations | ⏳ Waiting |
| Gemini CLI | Sync and verify | 🔄 Pending |

# MONITORING TASKS:

## 1. Track Claude's Progress
Watch for files being created:
- unified-platform/backend/pricing/models/programs.py
- unified-platform/backend/pricing/models/program_types.py
- unified-platform/backend/pricing/models/adjustments.py

## 2. Signal Jules When Ready
Once Claude commits models, tell Jules to run migrations.

## 3. Coordinate Verification
After Jules migrates, have Gemini CLI verify.

## 4. Fix Issues
If Gemini CLI reports failures, diagnose and fix.

## 5. Update Conductor Files
- conductor/current.md
- conductor/tracks/port_pricing_ratesheet_20260112/checklist.md

# COMMIT PROTOCOL:
After each major milestone:
git add -A && git commit -m "[phase2] <description>" && git push origin main
```

---

## 📋 Execution Order

1. **Claude**: Port models → commit
2. **Antigravity**: Signal Jules
3. **Jules**: Run migrations → commit
4. **Claude**: Create services + API → commit
5. **Gemini CLI**: Verify all components
6. **Antigravity**: Update checklist, proceed to Phase 3
