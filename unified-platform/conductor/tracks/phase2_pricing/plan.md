# Phase 2: Core Pricing Engine

> **Goal**: Port the proven cmtgdirect loan matching logic to the unified platform, enhance with RateAdjustment model for LLPA calculations.

---

## 📋 Task Breakdown

### Task 2.1: Port Core Models

**Agent**: Pricing Engineer  
**Priority**: P0 - Critical  
**Estimated Time**: 3-4 hours

#### Context
The cmtgdirect application contains battle-tested models for Lender, LoanProgram, ProgramType, and LenderProgramOffering. We need to port these to the unified platform's `pricing` app without breaking the proven matching logic.

#### Source Files to Port
```
dell-brain:~/code/cmtgdirect/loans/models/programs.py
dell-brain:~/code/cmtgdirect/loans/models/program_types.py
dell-brain:~/code/cmtgdirect/loans/choices.py
```

#### Instructions

1. **Copy the models verbatim first**
   ```bash
   ssh dell-brain
   cd ~/code/cmtgdirect
   
   # Copy to unified platform
   cp loans/models/programs.py ~/code/unified-cmtg/unified-platform/backend/pricing/models/programs.py
   cp loans/models/program_types.py ~/code/unified-cmtg/unified-platform/backend/pricing/models/program_types.py
   cp loans/choices.py ~/code/unified-cmtg/unified-platform/backend/pricing/choices.py
   ```

2. **Review and refactor imports**
   - Update import paths from `loans.` to `pricing.`
   - Ensure `common.models.TimestampedModel` is available or recreate it
   - Verify `common.fields.ChoiceArrayField` works with PostgreSQL ArrayField

3. **Create models `__init__.py`**
   ```python
   from .programs import Lender, LoanProgram, BaseLoan
   from .program_types import ProgramType, LenderProgramOffering
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations pricing
   python manage.py migrate
   ```

5. **Create fixtures for testing**
   Export sample data from cmtgdirect:
   ```bash
   cd ~/code/cmtgdirect
   python manage.py dumpdata loans.Lender loans.LoanProgram --indent 2 > fixtures.json
   ```

#### Key Models to Preserve

```python
class Lender(TimestampedModel):
    company_name = CharField(max_length=500)
    include_states = ChoiceArrayField(USStateField())
    company_website = URLField()
    company_email = EmailField()

class LoanProgram(BaseLoan):
    lender = ForeignKey(Lender)
    min_credit = PositiveSmallIntegerField()
    max_loan_to_value = FloatField()
    min_dscr = FloatField()
    property_types = ChoiceArrayField(...)
    occupancy = ChoiceArrayField(...)
    purpose = ChoiceArrayField(...)

class LenderProgramOffering(TimestampedModel):
    lender = ForeignKey(Lender)
    program_type = ForeignKey(ProgramType)
    min_rate = FloatField()
    max_rate = FloatField()
    min_fico = PositiveSmallIntegerField()
    max_ltv = FloatField()
```

#### Success Criteria
- [ ] All models ported without modification to field names
- [ ] Migrations run successfully
- [ ] Fixtures load correctly
- [ ] No circular import issues

---

### Task 2.2: Port Matching Logic

**Agent**: Pricing Engineer  
**Priority**: P0 - Critical  
**Estimated Time**: 2-3 hours

#### Context
The `get_matched_loan_programs_for_qual()` function in `cmtgdirect/loans/queries.py` is the heart of the pricing engine. This MUST be ported exactly, then refactored into a clean service layer.

#### Source File
```
dell-brain:~/code/cmtgdirect/loans/queries.py
```

#### Instructions

1. **Copy queries.py verbatim first**
   ```bash
   cp ~/code/cmtgdirect/loans/queries.py ~/code/unified-cmtg/unified-platform/backend/pricing/services/matching.py
   ```

2. **Review the matching filters**
   The current filters are:
   ```python
   filters = dict(
       program_type__property_types__contains=[qi.property_type],
       program_type__entity_types__contains=[qi.entity_type],
       program_type__purposes__contains=[qi.purpose],
       program_type__occupancy__contains=[qi.occupancy],
       lender__include_states__contains=[qi.state],
       min_loan__lte=qi.loan_amount,
       max_loan__gte=qi.loan_amount,
       max_ltv__gte=qi.ltv,
       min_fico__lte=qi.estimated_credit_score,
       is_active=True
   )
   ```

3. **Create a service class wrapper**
   ```python
   # pricing/services/matching.py
   
   class LoanMatchingService:
       """
       Service for matching borrower scenarios to eligible loan programs.
       
       This is a direct port of cmtgdirect's proven matching algorithm.
       DO NOT MODIFY the filter logic without extensive testing.
       """
       
       def __init__(self, scenario: QualifyingInfo):
           self.scenario = scenario
       
       def get_matches(self) -> QuerySet[LenderProgramOffering]:
           """Return matching LenderProgramOffering objects."""
           filters = self._build_filters()
           return LenderProgramOffering.objects.filter(**filters).order_by('min_rate')
       
       def _build_filters(self) -> dict:
           """Build filter dictionary for QuerySet."""
           qi = self.scenario
           return {
               'program_type__property_types__contains': [qi.property_type],
               'program_type__entity_types__contains': [qi.entity_type],
               'program_type__purposes__contains': [qi.purpose],
               'program_type__occupancy__contains': [qi.occupancy],
               'lender__include_states__contains': [qi.state],
               'min_loan__lte': qi.loan_amount,
               'max_loan__gte': qi.loan_amount,
               'max_ltv__gte': qi.ltv,
               'min_fico__lte': qi.estimated_credit_score,
               'is_active': True,
           }
   ```

4. **Write comprehensive tests**
   ```python
   # pricing/tests/test_matching.py
   
   @pytest.mark.django_db
   class TestLoanMatchingService:
       def test_matches_by_state(self, sample_scenario, ca_lender):
           """Verify state filtering works."""
           service = LoanMatchingService(sample_scenario)
           matches = service.get_matches()
           assert all(
               sample_scenario.state in m.lender.include_states 
               for m in matches
           )
   ```

#### Success Criteria
- [ ] Matching logic produces identical results to cmtgdirect
- [ ] Service class is clean and documented
- [ ] Unit tests cover all filter conditions
- [ ] No raw SQL or custom querysets

---

### Task 2.3: Implement RateAdjustment Model

**Agent**: Pricing Engineer  
**Priority**: P1 - High  
**Estimated Time**: 3-4 hours

#### Context
Rate sheets include LLPA (Loan Level Price Adjustments) grids that modify the base rate based on FICO, LTV, property type, etc. We need to model these adjustments.

#### Instructions

1. **Create the RateAdjustment model**
   ```python
   # pricing/models/adjustments.py
   
   class RateAdjustment(TimestampedModel):
       """
       Loan Level Price Adjustments (LLPAs) from rate sheets.
       
       These adjustments are applied to the base rate/price based on
       borrower and loan characteristics.
       
       Example: FICO 720 + LTV 75% = -0.625 points adjustment
       """
       offering = ForeignKey(
           LenderProgramOffering, 
           on_delete=CASCADE,
           related_name='adjustments'
       )
       
       ADJUSTMENT_TYPES = [
           ('fico_ltv', 'Credit Score × LTV Grid'),
           ('purpose', 'Loan Purpose'),
           ('occupancy', 'Occupancy Type'),
           ('property_type', 'Property Type'),
           ('loan_amount', 'Loan Amount Tier'),
           ('dscr', 'DSCR Range'),
           ('prepay', 'Prepayment Penalty'),
           ('lock', 'Lock Period'),
           ('state', 'State-Specific'),
       ]
       
       adjustment_type = CharField(max_length=20, choices=ADJUSTMENT_TYPES)
       
       # For 1D lookups (purpose, occupancy, property_type)
       value_key = CharField(max_length=50, blank=True)
       
       # For 2D grids (FICO × LTV)
       row_label = CharField(max_length=20, blank=True)  # "720-739"
       row_min = FloatField(null=True, blank=True)
       row_max = FloatField(null=True, blank=True)
       col_label = CharField(max_length=20, blank=True)  # "70.01-75"
       col_min = FloatField(null=True, blank=True)
       col_max = FloatField(null=True, blank=True)
       
       # The adjustment value (in points, not rate)
       adjustment_points = FloatField(
           help_text="Points adjustment. Negative = cost to borrower."
       )
       
       # Effective dates
       effective_date = DateField(null=True, blank=True)
       expiry_date = DateField(null=True, blank=True)
       
       class Meta:
           ordering = ['adjustment_type', 'row_min', 'col_min']
           indexes = [
               Index(fields=['offering', 'adjustment_type']),
           ]
   ```

2. **Create adjustment lookup service**
   ```python
   # pricing/services/adjustments.py
   
   class AdjustmentCalculator:
       """Calculate total LLPA for a loan scenario."""
       
       def __init__(self, offering: LenderProgramOffering, scenario):
           self.offering = offering
           self.scenario = scenario
           self.adjustments = offering.adjustments.all()
       
       def calculate_total_adjustment(self) -> float:
           """Sum all applicable adjustments."""
           total = 0.0
           for adj in self.adjustments:
               if self._applies(adj):
                   total += adj.adjustment_points
           return total
       
       def _applies(self, adj: RateAdjustment) -> bool:
           """Check if adjustment applies to this scenario."""
           if adj.adjustment_type == 'fico_ltv':
               return (
                   adj.row_min <= self.scenario.fico <= adj.row_max and
                   adj.col_min <= self.scenario.ltv <= adj.col_max
               )
           elif adj.adjustment_type == 'purpose':
               return adj.value_key == self.scenario.purpose
           # ... more types
   ```

3. **Run migrations and test**

#### Success Criteria
- [ ] RateAdjustment model created with proper indexes
- [ ] AdjustmentCalculator service works
- [ ] Sample LLPA data can be loaded
- [ ] Calculations match manual examples

---

### Task 2.4: Create Quote API Endpoint

**Agent**: Pricing Engineer  
**Priority**: P0 - Critical  
**Estimated Time**: 2 hours

#### Context
Expose the matching and adjustment logic via a REST API endpoint that the Next.js frontend will consume.

#### Instructions

1. **Create serializers**
   ```python
   # api/serializers.py
   
   class QuoteRequestSerializer(Serializer):
       property_state = CharField(max_length=2)
       loan_amount = IntegerField(min_value=50000)
       credit_score = IntegerField(min_value=300, max_value=850)
       property_value = IntegerField(min_value=50000)
       property_type = ChoiceField(choices=PROPERTY_TYPE_CHOICES)
       loan_purpose = ChoiceField(choices=LOAN_PURPOSE_CHOICES)
       occupancy = ChoiceField(choices=OCCUPANCY_CHOICES)
       
   class QuoteResponseSerializer(Serializer):
       # ... response fields
   ```

2. **Create the view**
   ```python
   # api/views.py
   
   class QuoteView(APIView):
       """
       POST /api/v1/quote/
       
       Calculate loan quotes for a borrower scenario.
       Returns matching programs with estimated rates and costs.
       """
       permission_classes = [AllowAny]
       
       def post(self, request):
           serializer = QuoteRequestSerializer(data=request.data)
           serializer.is_valid(raise_exception=True)
           
           # Calculate LTV
           data = serializer.validated_data
           ltv = (data['loan_amount'] / data['property_value']) * 100
           
           # Build scenario
           scenario = QuoteScenario(**data, ltv=ltv)
           
           # Get matches
           service = LoanMatchingService(scenario)
           matches = service.get_matches()[:10]
           
           # Calculate adjustments for each match
           results = []
           for offering in matches:
               calc = AdjustmentCalculator(offering, scenario)
               total_adj = calc.calculate_total_adjustment()
               results.append({
                   'lender': offering.lender.company_name,
                   'program': offering.program_type.name,
                   'rate_range': offering.rate_range,
                   'total_adjustment': total_adj,
               })
           
           return Response({'quotes': results})
   ```

3. **Wire up URL**
   ```python
   # api/urls.py
   urlpatterns = [
       path('v1/quote/', QuoteView.as_view(), name='quote'),
   ]
   ```

#### Success Criteria
- [ ] Endpoint responds to POST requests
- [ ] Returns matching programs with adjustments
- [ ] Error handling for invalid inputs
- [ ] Response format documented

---

## 📊 Progress Tracking

| Task | Status | Blocker | Notes |
|------|--------|---------|-------|
| 2.1 Port Models | ⏳ | Phase 1 | - |
| 2.2 Port Matching | ⏳ | 2.1 | - |
| 2.3 RateAdjustment | ⏳ | 2.1 | - |
| 2.4 Quote API | ⏳ | 2.2, 2.3 | - |

---

*Last Updated: 2026-01-11*
