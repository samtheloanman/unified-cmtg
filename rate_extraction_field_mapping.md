# Rate Sheet Extraction: Field Mapping & Data Model

**Version**: 1.0  
**Last Updated**: 2026-01-11

---

## 1. Scenario Input Fields (From Qualifying Wizard)

These are the fields we collect from borrowers to calculate their quote:

| Field | Source | Used For Pricing |
|-------|--------|------------------|
| `estimated_credit_score` | QualifyingInfo | ✅ FICO LLPA |
| `loan_amount` | QualifyingInfo | ✅ Loan Amount LLPA |
| `estimated_value` | QualifyingInfo | ✅ LTV calculation |
| `LTV` (calculated) | loan_amount / estimated_value | ✅ LTV LLPA |
| `occupancy` | QualifyingInfo | ✅ Occupancy LLPA |
| `property_type` | QualifyingInfo | ✅ Property Type LLPA |
| `property_sub_type` | QualifyingInfo | ✅ Property Sub-Type LLPA |
| `purpose` | QualifyingInfo | ✅ Loan Purpose LLPA |
| `state` | QualifyingInfo | ✅ State availability |
| `entity_type` | QualifyingInfo | ⚠️ Some lenders adjust |
| `desired_term` | QualifyingInfo | ✅ Term selection |
| `lock_period` | NEW - need to add | ✅ Lock Period LLPA |

---

## 2. Data to Extract from Rate Sheets

### 2.1 Program-Level Data (per lender/program)

| Extract Field | Maps To | Model |
|---------------|---------|-------|
| Lender Name | `lender.company_name` | Lender |
| Program Name | `program_type.name` | ProgramType |
| Program Category | `program_type.category` | ProgramType (agency, non_qm, etc.) |
| Min Loan Amount | `min_loan` | LenderProgramOffering |
| Max Loan Amount | `max_loan` | LenderProgramOffering |
| Min FICO | `min_fico` | LenderProgramOffering |
| Max LTV | `max_ltv` | LenderProgramOffering |
| Min DSCR | `min_dscr` | LenderProgramOffering |
| Lender Fee | `lender_fee` | LenderProgramOffering |
| Rate Sheet Date | `last_rate_update` | LenderProgramOffering |

### 2.2 Base Rate Matrix

| Extract Field | Description | Storage |
|---------------|-------------|---------|
| Rate Column | Interest rates (6.500%, 6.625%, etc.) | JSON array |
| Price by Lock Period | 15-day, 30-day, 45-day, 60-day prices | JSON object |

**Proposed JSON Structure**:
```json
{
  "effective_date": "2026-01-10",
  "rates": [
    {"rate": 6.500, "price_15": 100.500, "price_30": 100.250, "price_45": 100.000, "price_60": 99.750},
    {"rate": 6.625, "price_15": 100.750, "price_30": 100.500, "price_45": 100.250, "price_60": 100.000},
    {"rate": 6.750, "price_15": 101.000, "price_30": 100.750, "price_45": 100.500, "price_60": 100.250}
  ]
}
```

### 2.3 LLPA Adjustments to Extract

| Adjustment Type | Dimensions | Common Values | Priority |
|-----------------|------------|---------------|----------|
| **FICO × LTV** | 2D Grid | FICO buckets vs LTV buckets | P0 |
| **Loan Purpose** | 1D | Purchase, Rate/Term Refi, Cash-Out | P0 |
| **Occupancy** | 1D | Owner, Second Home, Investment | P0 |
| **Property Type** | 1D | SFR, Condo, 2-4 Unit, 5+ Unit | P0 |
| **Loan Amount** | 1D | <$100K, $100-200K, $200-500K, etc. | P1 |
| **DSCR** | 1D | ≥1.25, 1.00-1.24, <1.00 | P1 |
| **Prepay Penalty** | 1D | None, 3yr, 5yr | P1 |
| **Lock Period** | 1D | 15, 30, 45, 60 days | P1 |
| **State** | 1D | Some states have add-ons | P2 |
| **Escrow Waiver** | 1D | Yes/No | P2 |
| **Units** | 1D | 1, 2, 3, 4 | P2 |

---

## 3. Proposed Data Model

### 3.1 BaseRateMatrix (NEW)

```python
class BaseRateMatrix(TimestampedModel):
    """
    Stores the base rate/price grid from a rate sheet.
    """
    offering = ForeignKey(LenderProgramOffering, related_name='rate_matrices')
    effective_date = DateField()
    expiry_date = DateField(null=True, blank=True)
    
    # JSON structure: {"rates": [{"rate": 6.5, "price_30": 100.25, ...}]}
    matrix_json = JSONField()
    
    # Lock period columns available
    lock_periods = ArrayField(IntegerField())  # [15, 30, 45, 60]
    
    is_active = BooleanField(default=True)
    source_pdf_url = URLField(blank=True)
```

### 3.2 RateAdjustment (Enhanced)

```python
class RateAdjustment(TimestampedModel):
    """
    LLPA adjustments extracted from rate sheets.
    """
    offering = ForeignKey(LenderProgramOffering, related_name='adjustments')
    effective_date = DateField(null=True, blank=True)
    
    ADJUSTMENT_TYPES = [
        ('fico_ltv', 'Credit Score / LTV'),
        ('purpose', 'Loan Purpose'),
        ('occupancy', 'Occupancy Type'),
        ('property_type', 'Property Type'),
        ('loan_amount', 'Loan Amount'),
        ('dscr', 'DSCR'),
        ('prepay', 'Prepayment Penalty'),
        ('lock', 'Lock Period'),
        ('state', 'State'),
        ('units', 'Number of Units'),
        ('escrow', 'Escrow Waiver'),
    ]
    
    adjustment_type = CharField(max_length=20, choices=ADJUSTMENT_TYPES)
    
    # For 2D grids (FICO × LTV)
    row_label = CharField(max_length=20, blank=True)  # e.g., "720-739"
    row_min = FloatField(null=True, blank=True)
    row_max = FloatField(null=True, blank=True)
    col_label = CharField(max_length=20, blank=True)  # e.g., "70.01-75"
    col_min = FloatField(null=True, blank=True)
    col_max = FloatField(null=True, blank=True)
    
    # For 1D lookups (Purpose, Occupancy, Property Type)
    value_key = CharField(max_length=50, blank=True)  # e.g., "cash_out", "investment"
    
    # The adjustment (PRICE points, not rate)
    adjustment_points = FloatField()  # e.g., -0.75 means 0.75 cost
    
    # Optional: Some lenders show rate adjustment instead
    adjustment_rate = FloatField(null=True, blank=True)  # e.g., +0.125%
    
    class Meta:
        ordering = ['adjustment_type', 'row_min', 'col_min']
```

---

## 4. Quote Calculation Algorithm

```python
def calculate_quote(scenario, target_rate, lock_days=30):
    """
    Calculate final price and cost for a borrower scenario.
    
    Args:
        scenario: QualifyingInfo instance
        target_rate: Desired interest rate (e.g., 7.25)
        lock_days: Lock period in days (default 30)
    
    Returns:
        List of quotes from matching lenders
    """
    # Calculate LTV
    ltv = (scenario.loan_amount / scenario.estimated_value) * 100
    
    # Find matching offerings
    offerings = LenderProgramOffering.objects.filter(
        lender__include_states__contains=[scenario.state],
        min_loan__lte=scenario.loan_amount,
        max_loan__gte=scenario.loan_amount,
        min_fico__lte=scenario.estimated_credit_score,
        max_ltv__gte=ltv,
        is_active=True
    ).prefetch_related('rate_matrices', 'adjustments')
    
    results = []
    
    for offering in offerings:
        # 1. Get base price for target rate
        matrix = offering.rate_matrices.filter(is_active=True).first()
        if not matrix:
            continue
            
        base_price = get_price_from_matrix(matrix, target_rate, lock_days)
        if base_price is None:
            continue
        
        # 2. Calculate total LLPA adjustment
        total_adjustment = 0
        adjustment_details = []
        
        for adj in offering.adjustments.all():
            adj_value = get_adjustment_value(adj, scenario, ltv, lock_days)
            if adj_value != 0:
                total_adjustment += adj_value
                adjustment_details.append({
                    'type': adj.get_adjustment_type_display(),
                    'value': adj_value
                })
        
        # 3. Calculate final price
        final_price = base_price + total_adjustment
        
        # 4. Convert to cost/credit
        cost_points = 100 - final_price  # Positive = cost to borrower
        cost_dollars = (cost_points / 100) * scenario.loan_amount
        
        results.append({
            'lender': offering.lender.company_name,
            'program': offering.program_type.name,
            'rate': target_rate,
            'lock_days': lock_days,
            'base_price': base_price,
            'total_llpa': total_adjustment,
            'final_price': final_price,
            'cost_points': cost_points,
            'cost_dollars': cost_dollars,
            'adjustments': adjustment_details
        })
    
    # Sort by cost (lowest first)
    return sorted(results, key=lambda x: x['cost_dollars'])


def get_adjustment_value(adj, scenario, ltv, lock_days):
    """
    Determine if an adjustment applies and return its value.
    """
    if adj.adjustment_type == 'fico_ltv':
        fico = scenario.estimated_credit_score
        if (adj.row_min <= fico <= adj.row_max and
            adj.col_min <= ltv <= adj.col_max):
            return adj.adjustment_points
    
    elif adj.adjustment_type == 'purpose':
        if adj.value_key == scenario.purpose:
            return adj.adjustment_points
    
    elif adj.adjustment_type == 'occupancy':
        if adj.value_key == scenario.occupancy:
            return adj.adjustment_points
    
    elif adj.adjustment_type == 'property_type':
        if adj.value_key == scenario.property_sub_type:
            return adj.adjustment_points
    
    elif adj.adjustment_type == 'loan_amount':
        if adj.row_min <= scenario.loan_amount <= adj.row_max:
            return adj.adjustment_points
    
    elif adj.adjustment_type == 'lock':
        if adj.row_min <= lock_days <= adj.row_max:
            return adj.adjustment_points
    
    # Add more types as needed...
    
    return 0
```

---

## 5. Example Quote Calculation

**Borrower Scenario**:
- FICO: 720
- Loan Amount: $400,000
- Property Value: $500,000
- LTV: 80%
- Occupancy: Investment
- Property: Condo
- Purpose: Cash-Out Refinance
- Lock: 30 days
- Target Rate: 7.25%

**Calculation**:
| Adjustment | Value |
|------------|-------|
| Base Price (7.25%, 30-day) | 100.500 |
| FICO 720, LTV 80% | -0.625 |
| Occupancy: Investment | -0.750 |
| Property: Condo | -0.250 |
| Purpose: Cash-Out | -0.500 |
| **Final Price** | **98.375** |

**Cost to Borrower**:
- Price Points: 100 - 98.375 = 1.625 points
- Dollar Amount: 1.625% × $400,000 = **$6,500**

---

## 6. Extraction Priority

### Phase 1 (MVP)
1. Base Rate Matrix (rate vs. price by lock)
2. FICO × LTV Grid (most impactful)
3. Loan Purpose adjustments
4. Occupancy adjustments

### Phase 2
5. Property Type adjustments
6. Loan Amount adjustments
7. DSCR adjustments
8. Prepay adjustments

### Phase 3
9. State-specific adjustments
10. Escrow waiver
11. Units
12. Term-based adjustments
