# Quote API Testing Guide

**Endpoint:** `POST /api/v1/quote/`
**Status:** Ready for testing (after migrations complete)
**Authentication:** None required (AllowAny)

---

## Test Cases

### Test 1: Basic Quote Request (All Required Fields)

```bash
curl -X POST http://localhost:8000/api/v1/quote/ \
  -H "Content-Type: application/json" \
  -d '{
    "property_state": "CA",
    "loan_amount": 500000,
    "credit_score": 720,
    "property_value": 650000
  }'
```

**Expected Response:**
```json
{
  "quotes": [
    {
      "lender": "Example Lender",
      "program": "DSCR Investor",
      "rate_range": "6.500% - 7.250%",
      "points_range": "0.00 - 2.00",
      "min_loan": 75000.00,
      "max_loan": 2000000.00,
      "lender_fee": 995.00
    }
  ],
  "ltv": 76.92,
  "loan_amount": 500000,
  "property_value": 650000,
  "matches_found": 1
}
```

---

### Test 2: Quote with Optional Fields

```bash
curl -X POST http://localhost:8000/api/v1/quote/ \
  -H "Content-Type: application/json" \
  -d '{
    "property_state": "TX",
    "loan_amount": 750000,
    "credit_score": 680,
    "property_value": 1000000,
    "property_type": "commercial",
    "entity_type": "LLC",
    "loan_purpose": "refinance",
    "occupancy": "investment"
  }'
```

**Expected Response:**
- Similar structure as Test 1
- May return different programs based on commercial + LLC criteria
- LTV: 75.00

---

### Test 3: Low Credit Score (Edge Case)

```bash
curl -X POST http://localhost:8000/api/v1/quote/ \
  -H "Content-Type: application/json" \
  -d '{
    "property_state": "FL",
    "loan_amount": 300000,
    "credit_score": 580,
    "property_value": 400000
  }'
```

**Expected Response:**
- Fewer matches (or empty quotes array)
- `matches_found`: 0 or low number
- LTV: 75.00

---

### Test 4: High LTV (Edge Case)

```bash
curl -X POST http://localhost:8000/api/v1/quote/ \
  -H "Content-Type: application/json" \
  -d '{
    "property_state": "NY",
    "loan_amount": 900000,
    "credit_score": 740,
    "property_value": 1000000
  }'
```

**Expected Response:**
- Fewer matches due to high LTV (90%)
- Programs with max_ltv < 90 will be filtered out
- LTV: 90.00

---

### Test 5: Missing Required Field (Error Case)

```bash
curl -X POST http://localhost:8000/api/v1/quote/ \
  -H "Content-Type: application/json" \
  -d '{
    "property_state": "CA",
    "loan_amount": 500000,
    "credit_score": 720
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "error": "Missing required fields",
  "missing": ["property_value"]
}
```

---

### Test 6: Invalid Numeric Value (Error Case)

```bash
curl -X POST http://localhost:8000/api/v1/quote/ \
  -H "Content-Type: application/json" \
  -d '{
    "property_state": "CA",
    "loan_amount": "not-a-number",
    "credit_score": 720,
    "property_value": 650000
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "error": "Invalid numeric values: ..."
}
```

---

### Test 7: Zero Property Value (Error Case)

```bash
curl -X POST http://localhost:8000/api/v1/quote/ \
  -H "Content-Type: application/json" \
  -d '{
    "property_state": "CA",
    "loan_amount": 500000,
    "credit_score": 720,
    "property_value": 0
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "error": "Invalid numeric values: division by zero"
}
```

---

## Testing with Sample Data

**Prerequisites:**
1. Migrations must be complete
2. At least one Lender must exist in database
3. At least one ProgramType must exist
4. At least one LenderProgramOffering must exist

**To create sample data:**

```bash
docker compose exec backend python manage.py shell
```

```python
from pricing.models import Lender, ProgramType, LenderProgramOffering

# Create Lender
lender = Lender.objects.create(
    company_name="Test Lender Inc",
    include_states=["CA", "TX", "FL"],
    company_email="test@lender.com"
)

# Create Program Type
program = ProgramType.objects.create(
    name="DSCR Investor",
    slug="dscr-investor",
    category="non_qm",
    loan_type="conventional",
    property_types=["residential"],
    income_type="stated",
    documentation_level="dscr",
    base_min_fico=620,
    base_max_ltv=80.0,
    base_min_dscr=1.0,
    occupancy=["investment"],
    entity_types=["individual", "LLC"],
    purposes=["purchase", "refinance"]
)

# Create Lender Offering
offering = LenderProgramOffering.objects.create(
    lender=lender,
    program_type=program,
    min_rate=6.5,
    max_rate=7.25,
    min_points=0,
    max_points=2,
    lender_fee=995.00,
    min_fico=640,
    max_ltv=75.0,
    min_dscr=1.0,
    min_loan=75000,
    max_loan=2000000
)

print("Sample data created!")
```

---

## Troubleshooting

### Issue: Empty quotes array
**Cause:** No matching programs in database
**Solution:** Create sample data as shown above

### Issue: 500 Internal Server Error
**Cause:** Database connection issue or missing migrations
**Solution:**
1. Check migrations: `docker compose exec backend python manage.py showmigrations pricing`
2. Run migrations if needed: `docker compose exec backend python manage.py migrate`

### Issue: ImportError for pricing.services.matching
**Cause:** Models not imported correctly
**Solution:** Check that `pricing/services/__init__.py` exists

---

## Success Criteria

✅ **API responds with 200 OK for valid requests**
✅ **Returns quotes array with lender program matches**
✅ **Calculates LTV correctly**
✅ **Validates required fields and returns 400 for missing data**
✅ **Handles numeric conversion errors gracefully**
✅ **Returns empty quotes array when no matches found (not an error)**

---

**Generated by:** The Generator (L2 Agent)
**Date:** 2026-01-13
**Track:** port_pricing_ratesheet_20260112
