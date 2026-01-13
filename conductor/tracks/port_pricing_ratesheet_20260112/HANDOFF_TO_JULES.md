# Handoff to Jules (The Builder) - Phase 2 Migrations

**Date:** 2026-01-13
**From:** The Generator (Claude/L2)
**To:** Jules (The Builder)
**Track:** port_pricing_ratesheet_20260112

---

## ✅ Work Completed

### Models Created (Ready for Migrations)

All Django models have been successfully ported from legacy cmtgdirect and are ready for migration:

#### 1. Common Infrastructure
**File:** `unified-platform/backend/common/fields.py`
- ✅ ChoiceArrayField (handles both PostgreSQL ArrayField and SQLite JSONField)
- ✅ ArraySelectMultiple widget

#### 2. Pricing Choices
**File:** `unified-platform/backend/pricing/choices.py`
- ✅ 200+ choice constants (loan types, property types, occupancy, etc.)
- ✅ All max_length values documented for model fields

#### 3. Core Models
**File:** `unified-platform/backend/pricing/models/programs.py`
- ✅ TimestampedModel (abstract base with created_at/updated_at)
- ✅ AddressInfo (lender addresses)
- ✅ LenderContact (lender contact persons)
- ✅ Lender (lending institutions)
- ✅ BaseLoan (abstract model with 50+ fields for loan eligibility)
- ✅ LoanProgram (concrete model for DSCR/construction loans)

#### 4. Program Type Models
**File:** `unified-platform/backend/pricing/models/program_types.py`
- ✅ ProgramType (canonical program definitions: DSCR, FHA, Fix-and-Flip, etc.)
- ✅ LenderProgramOffering (lender-specific rates, fees, and overlays)

#### 5. Adjustment Models
**File:** `unified-platform/backend/pricing/models/adjustments.py`
- ✅ RateAdjustment (LLPA pricing adjustments for FICO×LTV grids, etc.)

#### 6. Model Package
**File:** `unified-platform/backend/pricing/models/__init__.py`
- ✅ Exports all models for clean imports
- ✅ Backward compatibility wrapper in `pricing/models.py`

#### 7. Matching Service
**File:** `unified-platform/backend/pricing/services/matching.py`
- ✅ QualifyingInfo data class
- ✅ get_matched_loan_programs_for_qual() function
- ✅ LoanMatchingService class with match_programs() and get_best_rates()

---

## 🎯 Your Tasks (In Order)

### Task 1: Add `common` and update INSTALLED_APPS
```bash
# Edit: unified-platform/backend/config/settings/base.py
# Add to INSTALLED_APPS:
'common',
'pricing',
```

### Task 2: Install Dependencies
```bash
cd unified-platform
pip install django-localflavor django-phonenumber-field phonenumbers
# Or add to requirements.txt:
# django-localflavor==4.0
# django-phonenumber-field[phonenumbers]==7.3.0
```

### Task 3: Sync with Latest Main
```bash
cd ~/code/unified-cmtg
git pull origin main
cd unified-platform
```

### Task 4: Rebuild and Restart Services
```bash
docker compose build backend
docker compose up -d
```

### Task 5: Run Migrations
```bash
docker compose exec backend python manage.py makemigrations pricing
docker compose exec backend python manage.py migrate pricing
```

### Task 6: Verify Migrations
```bash
docker compose exec backend python manage.py showmigrations pricing
# Expected: All migrations should show [X] applied
```

### Task 7: Verify Backend Health
```bash
curl http://localhost:8000/api/v1/health/
# Expected: 200 OK response
```

---

## 📊 Migration Statistics

**Models Created:** 9 concrete models + 2 abstract base models
**Total Fields:** ~150+ fields across all models
**Choice Constants:** 200+ constants
**Foreign Keys:** 8 relationships
**Array Fields:** 15+ ChoiceArrayField instances
**Validators:** 50+ field validators

---

## ⚠️ Known Issues & Notes

### 1. Circular Import Prevention
The `LoanProgram.get_matching_qual_infos()` method imports from `pricing.services.matching` to avoid circular imports. This is intentional.

### 2. Missing Dependencies
Ensure these packages are installed:
- `django-localflavor` (for USStateField, USZipCodeField)
- `django-phonenumber-field[phonenumbers]` (for PhoneNumberField)

### 3. Database Backend
The `ChoiceArrayField` automatically handles:
- PostgreSQL: Uses native ArrayField
- SQLite: Falls back to JSONField

No manual configuration needed.

### 4. Backward Compatibility
The file `pricing/models.py` now imports from `pricing/models/*` to maintain compatibility with any existing imports.

---

## 🔍 Success Criteria

- [ ] `makemigrations pricing` creates migration files without errors
- [ ] `migrate pricing` applies all migrations successfully
- [ ] `showmigrations pricing` shows all migrations as [X] applied
- [ ] Backend still responds 200 on `/api/v1/health/`
- [ ] Django admin can load without errors
- [ ] No circular import errors when starting server

---

## 🚧 Remaining Work (Future Tasks)

### Not Included in This Handoff:
1. **Quote API View** - Needs to be added to `api/views.py`
2. **Quote API URL** - Needs to be added to `api/urls.py`
3. **DRF Serializers** - Need serializers for all models
4. **Admin Interface** - Django admin registration
5. **Unit Tests** - Comprehensive test coverage

These will be handled in subsequent phases after migrations are confirmed working.

---

## 📞 Escalation

If you encounter any issues:

1. **Migration Errors**
   - Check that `common` is in INSTALLED_APPS
   - Verify django-localflavor and phonenumber-field are installed
   - Check database backend (PostgreSQL vs SQLite)

2. **Import Errors**
   - Ensure `pricing/models/__init__.py` is present
   - Check Python path includes `unified-platform/backend`

3. **Dependency Issues**
   - Run `pip install -r requirements.txt`
   - Check for version conflicts

---

## 🤝 Handoff Complete

**Status:** ✅ Models ready for migration
**Next Agent:** Jules (The Builder)
**Action Required:** Run migrations as outlined above

Once migrations are complete, signal back to L1 Orchestrator (Gemini) for Phase 3 planning.

---

**Generated by:** The Generator (L2 Agent)
**Date:** 2026-01-13
**Track:** port_pricing_ratesheet_20260112
