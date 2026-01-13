---
name: Dependency Graph Mapper
tier: 1-Comprehension
category: Understanding
priority: High
---

# Dependency Graph Mapper

## Purpose

Understand what depends on what before making changes. Shows import chains, circular dependencies, and impact of modifications. Critical before refactoring or modifying shared components.

## When to Use

- Before refactoring a shared module
- Understanding impact of model changes
- Identifying circular dependencies
- Planning safe refactor sequences
- Assessing risk before changes

## Input Parameters

```
target_file: string
  File or module to analyze (e.g., "backend/api/models.py")

direction: string (default: "both")
  "upstream" = what imports this
  "downstream" = what this imports
  "both" = complete dependency picture

depth: integer (default: 3)
  How many levels to trace

include_test_files: boolean (default: true)
  Include test dependencies?
```

## Output Structure

```markdown
## DEPENDENCY ANALYSIS: [file]

### Upstream Dependencies
(Files that import this)
- Direct importers
- Indirect importers
- Test files using this

### Downstream Dependencies
(Files this imports)
- Direct dependencies
- Transitive dependencies
- External packages

### Circular Dependency Check
- ✓ None detected / ❌ Circular detected

### Impact Analysis
(If I modify this file, what breaks?)
- Files that must be updated
- Tests that must pass
- API contracts affected
- Data structure changes

### Change Risk Assessment
- LOW: Adding new code
- MEDIUM: Modifying existing
- HIGH: Removing/renaming

### Safe Modification Patterns
- What changes are backward compatible
- What requires simultaneous updates
- What needs migration strategy

### Testing Requirements
- Files that must pass tests
- Integration test scenarios
- Edge cases to verify
```

## Example Output

```
## DEPENDENCY ANALYSIS: backend/api/models.py

### Upstream Dependencies
(Who imports models.py?)

```
Core Dependencies:
├── backend/api/serializers.py
│   └── Imports: LoanProgram, RateAdjustment
│       Uses: For ModelSerializer
│
├── backend/api/views.py
│   └── Imports: LoanProgram model
│       Uses: In ViewSet queries
│
├── backend/pricing/calculator.py
│   └── Imports: RateAdjustment model
│       Uses: For rate lookup queries
│
└── backend/tests/
    ├── test_models.py (6 test classes, 47 tests)
    │   └── Tests: Model validation, managers, methods
    │
    ├── test_api.py (API integration tests)
    │   └── Tests: Serialization, endpoint responses
    │
    └── test_pricing.py (pricing logic tests)
        └── Tests: Rate calculations, adjustments
```

### Downstream Dependencies
(What does models.py import?)

```
Standard Library:
├── datetime (for timestamp fields)
└── decimal (for DecimalField values)

Django:
├── django.db.models
│   └── Model, ForeignKey, DecimalField, etc.
│
├── django.core.validators
│   └── MinValueValidator, MaxValueValidator
│
└── django.core.exceptions
    └── ValidationError

Wagtail (for CMS models):
├── wagtail.core.models
│   └── Page (for CMS content pages)
│
└── wagtail.search.index
    └── SearchField (for content search)

Internal:
└── backend.config.settings
    └── Custom validators and constants
```

### Circular Dependency Check

✓ **NONE DETECTED**

Dependency tree is clean:
- No A→B→A patterns
- No A→B→C→A patterns
- Safe for refactoring

### Impact Analysis

**If I modify LoanProgram model:**

**Direct Impact:**
- [ ] backend/api/serializers.py (imports LoanProgram)
  - Action: Verify serializer includes new fields
  - Risk: API response format changes
  - Tests: test_api.py must pass

- [ ] backend/api/views.py (uses LoanProgram.objects)
  - Action: Check query methods still work
  - Risk: Query optimization affected
  - Tests: test_api.py must pass

- [ ] backend/pricing/calculator.py (queries LoanProgram)
  - Action: Verify pricing logic still works
  - Risk: Rate calculations affected
  - Tests: test_pricing.py must pass

**Indirect Impact:**
- [ ] backend/api/urls.py (routes to views that use models)
  - Action: None needed (url config doesn't know about models)

- [ ] frontend/src/api/loan-client.ts (consumes API)
  - Action: Update if API response format changed
  - Risk: Frontend breaks if API contract changes
  - Tests: Frontend integration tests

**Database Impact:**
- [ ] Migrations required (see: backend/api/migrations/)
- [ ] All tests must pass with new schema
- [ ] Rollback migration available

**Breaking vs. Non-Breaking:**

✓ Non-breaking (safe):
- Adding new optional fields
- Adding new methods (no breaking change to existing)
- Adding database indexes
- Adding validation (if existing data passes)

❌ Breaking (requires coordination):
- Removing fields (data loss)
- Renaming fields (API contract break)
- Changing field types (data conversion)
- Making optional field required (validation fails on old data)

### Change Risk Assessment

**Scenario 1: Add new field (interest_rate_override)**
```
Risk Level: LOW ✓
Why: New fields are backwards compatible
Impact:
  - Serializer auto-includes it (need to explicitly exclude if not wanted)
  - Migrations auto-generated
  - No existing code breaks
  - Tests unaffected
Action:
  1. Add field to model
  2. Generate migration
  3. Update tests to exercise new field
  4. Optional: Update serializer if permissions needed
```

**Scenario 2: Change decimal precision (rate: 5,3 → 5,2)**
```
Risk Level: HIGH ❌
Why: Data transformation required, precision loss possible
Impact:
  - Existing values with 3 decimals will be rounded
  - Old data might not fit in new precision
  - Serialization changes
  - Financial data affected (precision matters!)
Impact Files:
  - test_pricing.py (rate calculations change)
  - test_api.py (response values change)
  - Database (migration with data transformation)
Action:
  1. Audit existing data (max precision used?)
  2. Create data migration with transformation
  3. Test on copy of production data first
  4. Update rate calculation tests
  5. Verify no data loss in transformation
```

**Scenario 3: Rename field (is_active → active)**
```
Risk Level: HIGH ❌
Why: API contract break, widespread usage
Impact Files:
  - Serializers: expose 'active' not 'is_active'
  - API responses: field name changes for all clients
  - Frontend code: breaks without update
  - Tests: must expect new name
Action:
  1. Add new field 'active' (FK or boolean)
  2. Copy data from old field
  3. Keep old field during transition
  4. Deprecate old field (warn clients)
  5. After transition period, remove old field
```

### Safe Modification Patterns

**Pattern 1: Adding New Fields**
```python
# ✓ SAFE - Old code still works

class LoanProgram(models.Model):
    # Existing fields still there
    is_active = models.BooleanField()

    # NEW field (don't break old code)
    interest_rate_override = models.DecimalField(null=True, blank=True)
```
- Add as optional (null=True, blank=True)
- Old serializers ignore it automatically
- No migration risks

**Pattern 2: Adding New Methods**
```python
# ✓ SAFE - No existing code affected

class LoanProgram(models.Model):
    # Existing methods unchanged

    # NEW method (doesn't break anything)
    def get_adjusted_rate(self, fico):
        return self.rate_adjustment_set.get_by_fico(fico)
```
- New methods don't affect old code
- Tests only for new method
- Safe to add anytime

**Pattern 3: Adding Database Indexes**
```python
# ✓ SAFE - Query optimizer benefit

class Meta:
    indexes = [
        models.Index(fields=['is_active', '-created_at']),
    ]
```
- Zero impact on code
- Automatic migration
- Purely performance improvement

**Pattern 4: Removing Fields (HIGH RISK)**
```
# ❌ UNSAFE - Breaking changes

# Must coordinate:
1. Deprecation period (6 months?)
2. Warn API clients
3. Provide migration guide
4. Remove field after transition
```

### Testing Requirements

**If I modify models.py, these MUST pass:**

1. **Unit Tests: test_models.py**
   ```bash
   pytest backend/tests/test_models.py -v
   ```
   - Model instantiation
   - Field validation
   - Custom methods
   - Manager queries

2. **API Tests: test_api.py**
   ```bash
   pytest backend/tests/test_api.py -v
   ```
   - Serializer field mapping
   - Endpoint responses
   - Filter/search/ordering
   - Permissions

3. **Pricing Tests: test_pricing.py**
   ```bash
   pytest backend/tests/test_pricing.py -v
   ```
   - Rate calculations
   - Adjustment logic
   - Edge cases

4. **Integration Tests**
   ```bash
   pytest backend/tests/ -v --tb=short
   ```
   - All tests must pass
   - No circular import errors
   - Migrations apply cleanly

5. **Frontend Tests (if API contract changed)**
   ```bash
   npm test -- --testPathPattern=api
   ```
   - API client works
   - Components handle responses
   - Error cases handled

### Migration Checklist

- [ ] Backup production database
- [ ] Create Django migration: `python manage.py makemigrations`
- [ ] Review migration file (data transformations correct?)
- [ ] Test migration on development db
- [ ] Test migration on staging db (full copy of production)
- [ ] Run full test suite
- [ ] Run performance tests (query performance unchanged?)
- [ ] Prepare rollback migration
- [ ] Deploy to production with close monitoring
```

## How I Use This Skill

**Before Refactoring:**
1. Map dependencies of file I'm about to change
2. Identify all files that must be tested
3. Check for circular dependencies
4. Assess risk level of change
5. Plan safe refactoring sequence
6. Execute changes in dependency order

**Example:**
```
Task: Refactor pricing/ module (too large)

Step 1: Map dependencies
  - calculator.py imports models.py, adjustments.py
  - views.py imports calculator.py
  - tests import everything

Step 2: Identify impact
  - Can't change models.py (too many dependents)
  - Can split calculator.py (low impact)
  - Can refactor internals safely

Step 3: Plan safe order
  1. Create new modules
  2. Move code from calculator.py
  3. Update imports
  4. Test after each move
  5. Delete old code

Result: Safe refactoring with no breakage
```

## Quality Checklist

- [ ] Upstream dependencies clearly listed
- [ ] Downstream dependencies clearly listed
- [ ] Circular dependencies checked and reported
- [ ] Impact analysis is accurate
- [ ] Risk assessment for different change types
- [ ] Safe modification patterns identified
- [ ] Testing requirements complete
- [ ] Migration strategy clear

---

**Next Step:** Use dependency map to plan safe changes.
