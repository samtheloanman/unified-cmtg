# Legacy Pricing Models Analysis

**Track:** `port_pricing_ratesheet_20260112`
**Analyst:** The Generator (L2 Agent)
**Date:** 2026-01-13
**Source:** `legacy/cmtgdirect/loans/models/`

---

## Executive Summary

The legacy cmtgdirect pricing engine uses a **dual-architecture** approach:

1. **Legacy System** (`LoanProgram` model) - Original monolithic model with 50+ fields per program
2. **Modern System** (`ProgramType` + `LenderProgramOffering`) - Normalized architecture separating canonical program types from lender-specific offerings

The modern system is currently in use, as evidenced by `queries.py` which queries `LenderProgramOffering` objects exclusively. The legacy `LoanProgram` model appears deprecated but remains in the codebase for reference.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    LEGACY ARCHITECTURE                           │
│  (Deprecated - kept for reference)                              │
└─────────────────────────────────────────────────────────────────┘
Lender (1) ───────▶ LoanProgram (N)
                    │
                    └── Contains ALL fields:
                        - Eligibility criteria
                        - Rates and fees
                        - Property restrictions
                        - Credit requirements
                        - ~50+ fields per record


┌─────────────────────────────────────────────────────────────────┐
│                    MODERN ARCHITECTURE                           │
│  (Currently Active)                                             │
└─────────────────────────────────────────────────────────────────┘
Lender (1) ───────▶ LenderProgramOffering (N)
                    │
                    ├── Lender-specific:
                    │   - Rates (min/max)
                    │   - Points (min/max)
                    │   - Lender fees
                    │   - Overlays (stricter requirements)
                    │   - Rate sheet URL
                    │
                    └── ProgramType (N:1)
                        │
                        └── Canonical program:
                            - Base eligibility
                            - Property types
                            - Occupancy types
                            - Documentation level
                            - Income type


┌─────────────────────────────────────────────────────────────────┐
│                  RATE SHEET ARCHITECTURE                         │
│  (Parser and storage system)                                    │
└─────────────────────────────────────────────────────────────────┘
RateSheetLender (1) ───▶ RateSheet (N) ───▶ RateProgram (N)
                                         │
                                         └── RateAdjustment (N)
                                             (LLPAs/price adjustments)
```

---

## Model Details

### 1. Lender Model
**Location:** `legacy/cmtgdirect/loans/models/programs.py:254-269`

Basic lender information model - shared by both legacy and modern systems.

#### Fields
| Field | Type | Description |
|-------|------|-------------|
| `company_name` | CharField(500) | Lender company name |
| `include_states` | ChoiceArrayField | States where programs are available |
| `company_website` | URLField | Optional website |
| `company_phone` | PhoneNumberField | Optional phone |
| `company_fax` | PhoneNumberField | Optional fax |
| `company_email` | EmailField | Optional email |
| `company_notes` | TextField | Internal notes |

#### Relationships
- **Outbound:** None
- **Inbound:**
  - `LoanProgram.lender` (legacy, ForeignKey)
  - `LenderProgramOffering.lender` (modern, ForeignKey)
  - `LenderContact.lender` (ForeignKey)

#### Key Characteristics
- Simple contact/metadata model
- `include_states` uses array field for multi-state support
- No rate/pricing information (delegated to program models)

---

### 2. LoanProgram Model (LEGACY - Deprecated)
**Location:** `legacy/cmtgdirect/loans/models/programs.py:209-235`
**Base Class:** `BaseLoan` (abstract model with 50+ fields)

Monolithic model containing ALL loan program details. **No longer actively queried** - `queries.py:62` returns `LoanProgram.objects.none()`.

#### Key Fields from BaseLoan (programs.py:48-207)

**Basic Info:**
- `name` - Program name
- `lender` - FK to Lender
- `loan_type` - Conventional, FHA, VA, etc.
- `income_type` - Full doc, stated, bank statement, etc.

**Eligibility Arrays (ChoiceArrayField):**
- `occupancy` - Primary, investment, second home
- `property_types` - Residential, commercial
- `property_sub_categories` - SFR, condo, multi-unit, etc.
- `property_conditions` - Appraisal condition ratings
- `recourse` - Full recourse, non-recourse
- `amortization_terms` - Fixed, ARM, IO, etc.
- `entity_type` - Individual, LLC, trust, etc.
- `employment` - W2, self-employed, retired, etc.
- `purpose` - Purchase, refinance

**Numeric Limits:**
- `min_loan_amount` / `max_loan_amount` - Decimal(14,2)
- `max_loan_to_value` - Decimal(14,2)
- `min_credit` - 300-850 FICO
- `reserve_requirement` - Months of reserves
- `min_acreage` / `max_acreage` - Property size limits
- `max_properties_financed` - Portfolio size limit
- `max_dti` - Debt-to-income ratio

**Credit History:**
- `bk_allowed` / `time_since_bk` - Bankruptcy seasoning
- `foreclosure_allowed` / `time_since_foreclosure`
- `short_sales_allowed` / `time_since_short_sale`
- `nod_allowed` / `time_since_nod` - Notice of Default
- `nos_allowed` / `time_since_nos` - Notice of Sale

**Rates & Fees:**
- `potential_rate_min` / `potential_rate_max` - Float (0-100%)
- `potential_cost_min` / `potential_cost_max` - Points/lender fees
- `lender_fee` - Decimal(14,2)
- `ysp_available` / `max_ysp` - Yield spread premium
- `max_compensation` - Broker compensation limit
- `prepayment_penalty` / `prepayment_cost`

**Additional Fields:**
- `io_offered` / `p_and_i_offered` - Payment types
- `lien_position` - 1st, 2nd, other
- `refinance_seasoning` - Months before cash-out refi
- `max_cash_out` - Max cash-out amount
- `rate_lock_available` / `rate_lock_terms`

#### LoanProgram-Specific Fields (beyond BaseLoan)
Construction/rehab-specific LTV calculations:
- `max_ltv_on_purchase_price` - Float, LTV on land value
- `max_ltv_on_arv` - Float, LTV on after-repair value
- `max_ltv_on_cost` - Float, loan-to-cost
- `max_ltv_on_rehab` - Float, rehab money financed
- `min_borrower_contribution` - Float, required borrower equity
- `min_dscr` - Float, debt service coverage ratio

#### Why It Was Deprecated
1. **Duplication:** Every lender offering required copying all 50+ fields
2. **Maintenance burden:** Changes to program types required updating hundreds of records
3. **No normalization:** Canonical program definitions mixed with lender-specific rates
4. **Rate sheet sync:** Difficult to update rates from PDFs

---

### 3. ProgramType Model (MODERN - Active)
**Location:** `legacy/cmtgdirect/loans/models/program_types.py:49-116`

Canonical loan program definition (e.g., "DSCR Investor", "FHA Purchase", "Fix and Flip").

#### Fields
| Field | Type | Description |
|-------|------|-------------|
| `name` | CharField(100) | Program name (unique) |
| `slug` | SlugField(100) | URL-safe identifier |
| `category` | CharField(20) | agency, non_qm, hard_money, commercial |
| `loan_type` | CharField(15) | Maps to `choices.LOAN_TYPE_CHOICES` |
| `property_types` | ChoiceArrayField | Residential, commercial |
| `income_type` | CharField(30) | Full doc, stated, bank statement, etc. |
| `documentation_level` | CharField(20) | full, lite, no_doc, bank_statement, dscr, asset |
| `base_min_fico` | PositiveSmallIntegerField | Base minimum credit score (300-850) |
| `base_max_ltv` | Float | Base maximum LTV (0-100%) |
| `base_min_dscr` | Float | Base minimum DSCR for rental programs |
| `occupancy` | ChoiceArrayField | Primary, investment, second home |
| `entity_types` | ChoiceArrayField | Individual, LLC, trust, etc. |
| `purposes` | ChoiceArrayField | Purchase, refinance |
| `description` | TextField | Guidelines summary |
| `is_active` | Boolean | Program availability flag |
| `sort_order` | PositiveSmallIntegerField | Display ordering |

#### Categories
```python
CATEGORY_AGENCY = 'agency'           # Conventional, FHA, VA, USDA
CATEGORY_NON_QM = 'non_qm'           # Bank statement, DSCR, asset depletion
CATEGORY_HARD_MONEY = 'hard_money'   # Fix-and-flip, bridge loans
CATEGORY_COMMERCIAL = 'commercial'   # Multi-family, retail, office
```

#### Documentation Levels
```python
DOC_FULL = 'full'                    # Traditional W2/tax returns
DOC_LITE = 'lite'                    # Limited documentation
DOC_NO_DOC = 'no_doc'                # No income verification
DOC_BANK_STATEMENT = 'bank_statement' # Bank statement only
DOC_DSCR = 'dscr'                    # DSCR calculation only
DOC_ASSET = 'asset'                  # Asset depletion
```

#### Relationships
- **Outbound:** None (canonical definition)
- **Inbound:** `LenderProgramOffering.program_type` (FK)

#### Methods
- `lender_count` property - Returns count of active lender offerings
- `save()` override - Auto-generates slug from name

---

### 4. LenderProgramOffering Model (MODERN - Active)
**Location:** `legacy/cmtgdirect/loans/models/program_types.py:118-194`

Represents a specific lender's offering of a canonical program type. Contains lender-specific rates, fees, and overlays (stricter requirements than the base program).

#### Fields
| Field | Type | Description |
|-------|------|-------------|
| **Foreign Keys** | | |
| `lender` | FK(Lender) | Which lender offers this |
| `program_type` | FK(ProgramType) | Which program type |
| **Rates & Fees** | | |
| `min_rate` | Float | Minimum interest rate (%) |
| `max_rate` | Float | Maximum interest rate (%) |
| `min_points` | Float | Minimum origination points |
| `max_points` | Float | Maximum origination points |
| `lender_fee` | Decimal(10,2) | Lender underwriting fee |
| **Overlays (Lender Restrictions)** | | |
| `min_fico` | PositiveSmallIntegerField | Lender's min FICO (≥ program base) |
| `max_ltv` | Float | Lender's max LTV (≤ program base) |
| `min_dscr` | Float | Lender's min DSCR |
| **Loan Limits** | | |
| `min_loan` | Decimal(14,2) | Minimum loan amount |
| `max_loan` | Decimal(14,2) | Maximum loan amount |
| **Rate Sheet Tracking** | | |
| `rate_sheet_url` | URLField | Link to current PDF |
| `last_rate_update` | DateTimeField | Last rate sync timestamp |
| **Status** | | |
| `is_active` | Boolean | Offering availability |
| `notes` | TextField | Internal notes |

#### Constraints
- **Unique Together:** `(lender, program_type)` - One offering per lender per program type

#### Properties
- `rate_range` - Formatted string: "6.500% - 7.250%"
- `points_range` - Formatted string: "0.00 - 2.00"

#### Key Design Characteristics

**Lender Overlays:**
Lenders can impose stricter requirements than the base `ProgramType`:
- `min_fico` must be ≥ `program_type.base_min_fico`
- `max_ltv` must be ≤ `program_type.base_max_ltv`
- Example: Base program allows 620 FICO, but lender requires 640

**Rate Sheet Integration:**
- `rate_sheet_url` points to lender's current rate sheet PDF
- `last_rate_update` tracks when rates were last synced
- Supports automated rate updates from PDF parsing

---

## Rate Sheet System

### RateSheet Models Overview
**Location:** `legacy/cmtgdirect/loans/models/ratesheets.py`

System for parsing and storing rate sheet data from lender PDFs. Replaces external pricing engines like Lenderprice.

### Key Models

#### RateSheetLender (lines 66-118)
Lender profile for rate sheet management.
- Links to main `Lender` model
- Stores TPO portal credentials
- Tracks rate sheet source URLs
- Priority ranking based on funded loan volume

#### RateSheet (lines 120-184)
Individual rate sheet document.
- Links to `RateSheetLender`
- Stores PDF file and source URL
- Tracks effective/expiration dates
- Parsing status: pending, parsing, parsed, failed, expired
- Raw extracted text for debugging

#### RateProgram (lines 186-329)
Specific loan product extracted from rate sheet.
- Base rate and price (e.g., 6.875% @ 100.000 points)
- FICO/LTV/loan amount ranges
- Lock period (30/45/60 days)
- Program type (conventional, FHA, DSCR, etc.)
- Property type, occupancy, purpose filters
- DSCR requirements

#### RateAdjustment (lines 331-414)
Loan-level price adjustments (LLPAs).
- Categories: LTV, FICO, loan amount, property type, occupancy, purpose, lock period, state
- Condition ranges (numeric) or values (categorical)
- Rate adjustments (+ = higher rate)
- Price adjustments (- = worse pricing)

#### LenderScenario (lines 416-486)
For lenders without rate sheets (private lenders, hard money).
- Stores historical pricing estimates
- Rate ranges based on manual quotes
- Tracks verification date

---

## Matching Logic

### Query Function: `get_matched_loan_programs_for_qual()`
**Location:** `legacy/cmtgdirect/loans/queries.py:41-50`

Finds matching `LenderProgramOffering` objects for a qualification.

#### Input
`QualifyingInfo` object with:
- `property_type` - Residential or commercial
- `entity_type` - Individual, LLC, trust, etc.
- `purpose` - Purchase or refinance
- `occupancy` - Primary, investment, second home
- `state` - US state code
- `loan_amount` - Loan amount in dollars
- `ltv` - Loan-to-value ratio (decimal)
- `estimated_credit_score` - FICO score

#### Filters Applied
```python
filters = dict(
    # ProgramType fields (via FK)
    program_type__property_types__contains=[qi.property_type],
    program_type__entity_types__contains=[qi.entity_type],
    program_type__purposes__contains=[qi.purpose],
    program_type__occupancy__contains=[qi.occupancy],

    # Lender fields (via FK)
    lender__include_states__contains=[qi.state],

    # LenderProgramOffering numeric limits
    min_loan__lte=qi.loan_amount,           # Loan amount ≥ min
    max_loan__gte=qi.loan_amount,           # Loan amount ≤ max
    max_ltv__gte=qi.ltv,                    # LTV ≤ lender max
    min_fico__lte=qi.estimated_credit_score, # FICO ≥ lender min

    # Active only
    is_active=True
)
```

#### Ordering
Results ordered by `min_rate` ascending (cheapest rates first).

#### Legacy Note
```python
# Note from queries.py:34-36:
# Legacy logic for property_sub_categories, cost_of_rehab, etc.
# needs to be migrated to ProgramType/LenderProgramOffering if critical.
# For now, we rely on the main filters above.
```

---

## Choice Constants

### Key Choice Fields
**Location:** `legacy/cmtgdirect/loans/choices.py`

#### Loan Purpose
```python
PURPOSE_PURCHASE = 'purchase'
PURPOSE_REFINANCE = 'refinance'
```

#### Property Types
```python
PROPERTY_TYPE_RESIDENTIAL = 'residential'
PROPERTY_TYPE_COMMERCIAL = 'commercial'
```

#### Property Sub-Categories (Sample)
**Residential:**
- `single family` - Single-family residence
- `2-4 unit residential` - 2-4 unit properties
- `condo townhomes` - Condos and townhomes
- `non-warrantable condo` - Non-warrantable condos
- `manufactured` - Mobile/manufactured homes

**Commercial:**
- `5+ units` - Multi-family apartment buildings
- `office` - Office buildings
- `industrial` - Industrial properties
- `retail` - Retail properties
- `self storage` - Self-storage facilities
- `hospitality` - Hotels, motels
- `medical` - Medical office buildings

#### Occupancy Types
```python
OCCUPANCY_PRIMARY = 'primary'           # Primary residence
OCCUPANCY_INVESTMENT = 'investment'     # Rental property
OCCUPANCY_SECOND = 'second'             # Second home/vacation
```

#### Entity Types
```python
ENTITY_TYPE_INDIVIDUAL = 'individual'
ENTITY_TYPE_LLC = 'llc'
ENTITY_TYPE_TRUST = 'trust'
ENTITY_TYPE_CORPORATION = 'corporation'
# ... etc
```

#### Loan Types
```python
LOAN_TYPE_CONVENTIONAL = 'conventional'
LOAN_TYPE_FHA = 'fha'
LOAN_TYPE_VA = 'va'
LOAN_TYPE_USDA = 'usda'
LOAN_TYPE_JUMBO = 'jumbo'
LOAN_TYPE_COMMERCIAL = 'commercial'
LOAN_TYPE_HARD_MONEY = 'hard_money'
LOAN_TYPE_ALT_A = 'alt_a'
```

---

## Migration Recommendations

### From Legacy to Modern System

#### 1. Data Migration Path
```
LoanProgram (deprecated)
    ↓
Split into:
    ↓
ProgramType (canonical program definition)
    +
LenderProgramOffering (lender-specific rates/overlays)
```

#### 2. Critical Fields to Preserve

**From LoanProgram → ProgramType:**
- Base eligibility criteria (FICO, LTV, DSCR)
- Property type restrictions
- Occupancy and purpose allowances
- Income/documentation requirements
- Entity type restrictions

**From LoanProgram → LenderProgramOffering:**
- Rate ranges (potential_rate_min/max → min_rate/max_rate)
- Points/cost ranges (potential_cost_min/max → min_points/max_points)
- Lender fee
- Loan amount limits
- Lender overlays (stricter FICO/LTV requirements)

#### 3. Fields That May Be Lost
The following `BaseLoan` fields are NOT in `ProgramType` or `LenderProgramOffering`:
- `property_conditions` - Appraisal condition ratings (C1-C6)
- `recourse` - Full recourse vs non-recourse
- `employment` restrictions
- `percent_ownership` requirements
- `max_cash_out` limits
- Credit history fields (BK, foreclosure, short sale seasoning)
- `max_acreage` / `min_acreage`
- `max_properties_financed`
- `refinance_seasoning`
- `ysp_available` / `max_ysp`
- `max_compensation` (broker comp limits)
- `processing_fee_allowed`
- `max_dti`
- `prepayment_penalty` / `prepayment_cost`
- `rate_lock_available` / `rate_lock_terms`

**Decision Required:** Determine if these fields are:
1. **Critical** → Add to `ProgramType` or `LenderProgramOffering`
2. **Nice-to-have** → Store in JSON field or notes
3. **Obsolete** → Can be dropped

---

## Rate Sheet Integration Strategy

### Current State
- `RateSheetLender` tracks lender rate sheet sources
- `RateSheet` stores individual PDF documents
- `RateProgram` contains parsed program data
- `RateAdjustment` stores LLPAs (price adjustments)

### Integration Points

#### Option A: Direct Mapping
```
RateProgram → LenderProgramOffering
    - Parse PDF rates into LenderProgramOffering records
    - Update rates daily/weekly from rate sheets
    - Deprecate RateProgram entirely
```

**Pros:**
- Single source of truth
- Simplified architecture
- No duplicate data

**Cons:**
- Lose historical rate data
- Parsing errors directly affect pricing
- No audit trail of rate changes

#### Option B: Dual System (Recommended)
```
RateProgram (parsed data) → LenderProgramOffering (production data)
    - RateProgram stores raw parsed data
    - Manual review before promoting to LenderProgramOffering
    - Audit trail of rate changes
```

**Pros:**
- Safety net for parsing errors
- Historical rate tracking
- Manual review capability

**Cons:**
- More complexity
- Manual promotion step
- Data duplication

---

## Technical Debt & Cleanup

### Files to Remove/Archive
1. `LoanProgram` model - Mark as deprecated, remove queries
2. `Alt_ALoan` model - Not used in queries.py
3. `get_not_matched_loan_programs_for_qual()` - Returns `.none()`
4. `get_quals_for_loan_program()` - Returns `.none()`

### Database Migration Strategy
```sql
-- Phase 1: Mark legacy data
ALTER TABLE loans_loanprogram ADD COLUMN is_migrated BOOLEAN DEFAULT FALSE;

-- Phase 2: Extract canonical programs
INSERT INTO loans_programtype (name, category, loan_type, ...)
SELECT DISTINCT name, loan_type, ...
FROM loans_loanprogram
WHERE is_active = TRUE;

-- Phase 3: Create lender offerings
INSERT INTO loans_lenderprogramoffering (lender_id, program_type_id, ...)
SELECT lp.lender_id, pt.id, lp.potential_rate_min, lp.potential_rate_max, ...
FROM loans_loanprogram lp
JOIN loans_programtype pt ON pt.name = lp.name
WHERE lp.is_active = TRUE;

-- Phase 4: Mark as migrated
UPDATE loans_loanprogram SET is_migrated = TRUE;

-- Phase 5: Archive (do NOT drop - keep for reference)
-- Rename table instead of dropping
ALTER TABLE loans_loanprogram RENAME TO loans_loanprogram_archived;
```

---

## Appendix: Model Relationships Diagram

```
┌──────────────────┐
│  Lender          │
│  - company_name  │
│  - states[]      │
│  - contact info  │
└────────┬─────────┘
         │
         │ 1:N
         │
         ▼
┌──────────────────────────────────┐
│  LenderProgramOffering           │
│  - min_rate / max_rate           │
│  - min_points / max_points       │
│  - lender_fee                    │
│  - min_fico (overlay)            │◀──┐
│  - max_ltv (overlay)             │   │
│  - min_loan / max_loan           │   │
│  - rate_sheet_url                │   │
│  - last_rate_update              │   │ N:1
└──────────────────────────────────┘   │
                                       │
                                       │
                          ┌────────────┴──────────────┐
                          │  ProgramType              │
                          │  - name (e.g., "DSCR")    │
                          │  - category               │
                          │  - loan_type              │
                          │  - property_types[]       │
                          │  - base_min_fico          │
                          │  - base_max_ltv           │
                          │  - base_min_dscr          │
                          │  - occupancy[]            │
                          │  - entity_types[]         │
                          │  - purposes[]             │
                          └───────────────────────────┘


┌──────────────────────────────────────────────────────────────┐
│                  RATE SHEET SYSTEM                            │
└──────────────────────────────────────────────────────────────┘

┌──────────────────┐
│RateSheetLender   │
│ - name           │
│ - lender (FK)    │◀─── Optional link to main Lender
│ - ratesheet_url  │
│ - portal creds   │
└────────┬─────────┘
         │ 1:N
         ▼
┌──────────────────┐
│  RateSheet       │
│  - source_file   │
│  - effective_date│
│  - status        │
│  - raw_text      │
└────────┬─────────┘
         │ 1:N
         ▼
┌──────────────────┐
│  RateProgram     │
│  - program_name  │
│  - base_rate     │
│  - base_price    │
│  - min_fico/ltv  │
│  - loan amounts  │
└────────┬─────────┘
         │ 1:N
         ▼
┌──────────────────┐
│ RateAdjustment   │
│ - category       │
│ - condition      │
│ - rate_adj       │
│ - price_adj      │
└──────────────────┘
```

---

## Next Steps for Port to Unified Platform

### Phase 1: Schema Port ✅ (Ready)
- [x] Copy models to `unified-platform/backend/api/models/`
- [x] Update imports and dependencies
- [x] Create Django migrations
- [ ] Run migrations on dev database

### Phase 2: Data Migration
- [ ] Export production data from cmtgdirect
- [ ] Transform data to new schema
- [ ] Import into unified-platform database
- [ ] Validate data integrity

### Phase 3: API Implementation
- [ ] Create DRF serializers for models
- [ ] Implement `/api/v1/pricing/match/` endpoint
- [ ] Port matching logic from `queries.py`
- [ ] Add unit tests

### Phase 4: Rate Sheet Parser
- [ ] Implement PDF extraction (PyPDF2/pdfplumber)
- [ ] Create parsing logic for common rate sheet formats
- [ ] Build rate sync Celery tasks
- [ ] Add admin interface for manual review

### Phase 5: Testing & Validation
- [ ] Unit tests for models
- [ ] Integration tests for matching logic
- [ ] Compare results with legacy cmtgdirect API
- [ ] Load testing with production data volumes

### Phase 6: Deprecation
- [ ] Run dual systems in parallel (1-2 months)
- [ ] Monitor for discrepancies
- [ ] Migrate production traffic
- [ ] Archive legacy cmtgdirect

---

## Questions for L1 Orchestrator (Gemini)

1. **Field Priority:** Which `BaseLoan` fields not in modern system are critical? (See "Fields That May Be Lost" section)

2. **Rate Sheet Strategy:** Approve Option B (dual system) or prefer Option A (direct mapping)?

3. **Migration Timeline:** How much legacy data history to preserve? (All historical rates vs. current only)

4. **Testing Requirements:** Acceptable error rate for rate matching vs. legacy system? (e.g., 99% match threshold)

5. **Rate Update Frequency:** Daily auto-updates from rate sheets, or manual review required?

---

## Handoff to Ralph (The Closer)

### Verification Tasks

#### Code Review
- [ ] Review model field types and constraints
- [ ] Check foreign key relationships and cascades
- [ ] Validate unique constraints
- [ ] Review indexes for query performance

#### Data Validation
- [ ] Export sample data from legacy cmtgdirect
- [ ] Transform to new schema
- [ ] Verify no data loss in critical fields
- [ ] Check for duplicate records

#### Functional Testing
- [ ] Port matching logic to new models
- [ ] Test with 100 sample qualifications
- [ ] Compare results with legacy API
- [ ] Document any discrepancies

#### Performance Testing
- [ ] Benchmark query performance
- [ ] Test with 10k+ LenderProgramOffering records
- [ ] Verify index usage in EXPLAIN queries
- [ ] Check for N+1 query problems

---

**Analysis Complete.**
**Status:** Ready for L1 review and Phase 2 planning.
**Generated by:** The Generator (L2 Agent)
**Date:** 2026-01-13
