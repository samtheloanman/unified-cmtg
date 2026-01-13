---
name: Legacy Code Mapping Translator
tier: 1-Comprehension
category: Understanding
priority: High
---

# Legacy Code Mapping Translator

## Purpose

Map old code concepts to new framework equivalents. Essential for Phases 2-3 when porting cmtgdirect (Django 2.x) and WordPress/custommortgage to modern stack.

## When to Use

- Phase 2: Porting cmtgdirect pricing engine
- Phase 3: Migrating WordPress content
- Understanding legacy code patterns
- Planning modernization refactors
- Teaching new team members about changes

## Input Parameters

```
legacy_code: string
  The old code snippet or file content

legacy_framework: string
  Original framework/language: ["Django 2.x", "WordPress/PHP", "Custom ORM"]

target_framework: string
  Modern target: ["Django 5.0", "Wagtail 6.0", "Next.js 14"]

context_rules: dict (optional)
  Project-specific conversion rules

show_data_changes: boolean (default: true)
  Include data structure migration notes

show_breaking_changes: boolean (default: true)
  Highlight incompatibilities and gotchas
```

## Output Structure

```markdown
## LEGACY → MODERN MAPPING

### Legacy Code (Original)
[Code block showing old implementation]

### Modern Code (Target)
[Equivalent code in new framework]

### Key Differences
- Conceptual changes
- Syntax changes
- Behavioral changes

### Data Migration
- Schema changes
- Field name changes
- Data type conversions

### Breaking Changes
- What no longer works
- Required migrations
- Risk assessment

### Recommended Refactoring
- Improvements possible during migration
- Modernization opportunities
- Testing strategy
```

## Example Output

```
## LEGACY → MODERN MAPPING: cmtgdirect Pricing Engine

### Legacy Code (Django 2.1, Custom ORM)

```python
# Legacy: cmtgdirect/models.py
class RateAdjustment(object):
    def __init__(self, fico_min, fico_max, ltv_min, ltv_max, rate):
        self.fico_min = fico_min
        self.fico_max = fico_max
        self.ltv_min = ltv_min
        self.ltv_max = ltv_max
        self.rate = rate

    @staticmethod
    def get_by_fico_ltv(fico, ltv):
        # Custom raw SQL query
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT rate FROM rate_adjustments
            WHERE fico_min <= %s AND fico_max >= %s
            AND ltv_min <= %s AND ltv_max >= %s
            LIMIT 1
        """, [fico, fico, ltv, ltv])
        return cursor.fetchone()[0]
```

### Modern Code (Django 5.0, ORM)

```python
# Modern: backend/pricing/models.py
class RateAdjustment(models.Model):
    fico_min = models.IntegerField(validators=[MinValueValidator(300)])
    fico_max = models.IntegerField(validators=[MaxValueValidator(850)])
    ltv_min = models.DecimalField(max_digits=5, decimal_places=2)
    ltv_max = models.DecimalField(max_digits=5, decimal_places=2)
    rate = models.DecimalField(max_digits=5, decimal_places=3)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class RateAdjustmentQuerySet(models.QuerySet):
        def for_fico_ltv(self, fico, ltv):
            return self.filter(
                fico_min__lte=fico,
                fico_max__gte=fico,
                ltv_min__lte=ltv,
                ltv_max__gte=ltv
            ).first()

    objects = RateAdjustmentQuerySet.as_manager()

    def get_rate(self, fico, ltv):
        return RateAdjustment.objects.for_fico_ltv(fico, ltv).rate

    class Meta:
        indexes = [
            models.Index(fields=['fico_min', 'fico_max']),
            models.Index(fields=['ltv_min', 'ltv_max']),
        ]
```

### Key Differences

| Aspect | Legacy (Django 2.1) | Modern (Django 5.0) |
|---|---|---|
| **Class Definition** | Plain Python class | Django Model (ORM-based) |
| **Persistence** | Manual DB connection | Automatic ORM mapping |
| **Queries** | Raw SQL strings | QuerySet API |
| **Validation** | Manual in-code checks | Field validators |
| **Timestamps** | Manual management | auto_now/auto_now_add |
| **Optimization** | No built-in hints | Indexes, select_related, prefetch_related |
| **Testing** | Requires DB setup | Django TestCase handles isolation |
| **Safety** | SQL injection risk | Parameterized queries (automatic) |

### Data Migration

**Schema Changes:**
```sql
-- Legacy table structure
CREATE TABLE rate_adjustments (
    id INT AUTO_INCREMENT,
    fico_min INT,
    fico_max INT,
    ltv_min DECIMAL(10,2),
    ltv_max DECIMAL(10,2),
    rate DECIMAL(10,4)
);

-- Modern table structure (Django creates this)
CREATE TABLE pricing_rateadjustment (
    id BIGINT AUTO_INCREMENT,
    fico_min INT NOT NULL,
    fico_max INT NOT NULL,
    ltv_min DECIMAL(5,2) NOT NULL,
    ltv_max DECIMAL(5,2) NOT NULL,
    rate DECIMAL(5,3) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_fico (fico_min, fico_max),
    INDEX idx_ltv (ltv_min, ltv_max)
);
```

**Field Name Changes:**
- `fico_min` → `fico_min` (no change) ✓
- `ltv_min` → `ltv_min` (no change) ✓
- `rate` → `rate` (no change) ✓
- (NEW) `created_at` - tracks creation timestamp
- (NEW) `updated_at` - tracks updates

**Data Type Changes:**
- DECIMAL(10,4) → DECIMAL(5,3) for rate (smaller precision, fine for percentages)
- No validation on legacy → explicit validators on modern

**Data Migration SQL:**
```sql
-- Migrate data from old table
INSERT INTO pricing_rateadjustment
  (fico_min, fico_max, ltv_min, ltv_max, rate, created_at)
SELECT
  fico_min, fico_max, ltv_min, ltv_max, rate, NOW()
FROM rate_adjustments;
```

### Breaking Changes

**❌ Removed/Changed:**
1. Raw SQL queries no longer needed
   - Code: `cursor.execute("SELECT ...")` → Use ORM
   - Impact: Medium (update query calls)
   - Migration: Gradual (support both initially)

2. Manual connection management gone
   - Code: `get_db_connection()` → Use models.Manager
   - Impact: Low (automatic in Django)
   - Migration: Simple (delete connection code)

3. Validators were optional, now required
   - Code: No `MinValueValidator` on FICO → Must add
   - Impact: High (data integrity)
   - Migration: Add validators, verify data passes

**⚠️ Gotchas:**
- FICO range: Legacy allows any int, modern requires 300-850
  - **Action:** Validate existing data or widen constraints

- LTV precision: Changed from 10,2 to 5,2
  - **Action:** Confirm no values > 99.99%

- Timestamps: No legacy record of creation/update
  - **Action:** Set created_at = NOW() for all migrated records

### Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| Data loss during migration | Critical | Backup before migration, validate row counts |
| Validation fails on old data | High | Pre-migration audit, adjust constraints if needed |
| Query performance regression | Medium | Add indexes, test query plans |
| API contract change | High | Keep old endpoints during transition period |

### Recommended Refactoring

**During Migration, Also Improve:**

1. **Add Query Optimization**
   ```python
   # Modern: Use select_related for related objects
   adjustments = RateAdjustment.objects.filter(...).select_related('loan_program')
   ```

2. **Add Batch Operations**
   ```python
   # Modern: Bulk create/update for performance
   RateAdjustment.objects.bulk_create([...], batch_size=1000)
   ```

3. **Add Caching**
   ```python
   # Modern: Cache rate lookups
   @cached_property
   def adjustment_for_profile(self):
       return self.cache.get_or_set(...)
   ```

4. **Add Async Processing**
   ```python
   # Modern: Celery tasks for heavy operations
   from celery import shared_task

   @shared_task
   def recalculate_all_rates():
       # Heavy operation off main thread
       pass
   ```

### Testing Strategy

**During Migration:**
1. Unit tests on legacy code (establish baseline)
2. Unit tests on modern code (ensure equivalence)
3. Integration tests (full flow works)
4. Data migration tests (no data loss)
5. Performance tests (new version is comparable/better)

**Example:**
```python
# Test: Legacy rate lookup == Modern rate lookup
def test_rate_lookup_equivalence():
    fico, ltv = 750, 85
    legacy_rate = LegacyRateAdjustment.get_by_fico_ltv(fico, ltv)
    modern_rate = RateAdjustment.objects.for_fico_ltv(fico, ltv).rate
    assert legacy_rate == modern_rate, "Rates don't match after migration"
```

## How I Use This Skill

**Phase 2 Porting Example:**

1. **Receive Task:** "Port RateAdjustment model from cmtgdirect"

2. **Map Legacy Code:**
   ```
   /claude map-legacy-code legacy/cmtgdirect/models.py --target Django 5.0
   ```

3. **Understand Differences:**
   - Legacy: raw SQL, manual connection
   - Modern: ORM, automatic persistence

4. **Generate Modern Code:**
   - Same field names where possible
   - Add validation constraints
   - Add timestamps for auditing
   - Add indexes for performance

5. **Plan Migration:**
   - Data mapping clear
   - Breaking changes identified
   - Rollback strategy ready
   - Tests covering equivalence

## Quality Checklist

- [ ] Legacy code clearly shown
- [ ] Modern equivalent generated
- [ ] All key differences documented
- [ ] Data migration strategy clear
- [ ] Breaking changes identified with severity
- [ ] Gotchas listed with mitigations
- [ ] Testing strategy included
- [ ] Risk assessment complete

---

**Next Step:** Use mapping guide to port code and validate with tests.
