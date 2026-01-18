"""
Test Pricing Engine Loan Matching Service
P0: Critical - Ensures loan matching logic works correctly for quote generation
"""
import pytest
from decimal import Decimal

from pricing.models import Lender, ProgramType, LenderProgramOffering, RateAdjustment
from pricing.services.matching import (
    QualifyingInfo,
    _get_filters_for_loan_program_match_by_qual,
    get_matched_loan_programs_for_qual,
    LoanMatchingService
)


@pytest.fixture
def lender_ca(db):
    """Create a California-licensed lender"""
    return Lender.objects.create(
        company_name="California Lending Co",
        include_states=["CA", "NV"],
        company_website="https://example.com"
    )


@pytest.fixture
def lender_nationwide(db):
    """Create a nationwide lender"""
    return Lender.objects.create(
        company_name="National Mortgage Corp",
        include_states=["CA", "TX", "FL", "NY", "AZ"],
        company_website="https://example.com"
    )


@pytest.fixture
def dscr_program_type(db):
    """Create DSCR program type"""
    return ProgramType.objects.create(
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
        entity_types=["individual", "llc"],
        purposes=["purchase", "refinance"],
        is_active=True
    )


@pytest.fixture
def conventional_program_type(db):
    """Create conventional program type"""
    return ProgramType.objects.create(
        name="Conventional",
        slug="conventional",
        category="agency",
        loan_type="conventional",
        property_types=["residential"],
        income_type="full_doc",
        documentation_level="full",
        base_min_fico=580,
        base_max_ltv=97.0,
        occupancy=["primary", "secondary"],
        entity_types=["individual"],
        purposes=["purchase", "refinance"],
        is_active=True
    )


@pytest.fixture
def dscr_offering_ca(db, lender_ca, dscr_program_type):
    """Create DSCR offering from California lender"""
    return LenderProgramOffering.objects.create(
        lender=lender_ca,
        program_type=dscr_program_type,
        min_rate=7.0,
        max_rate=9.5,
        min_points=0.0,
        max_points=2.0,
        lender_fee=Decimal("995.00"),
        min_fico=620,
        max_ltv=75.0,
        min_dscr=1.0,
        min_loan=Decimal("100000.00"),
        max_loan=Decimal("3000000.00"),
        is_active=True
    )


@pytest.fixture
def dscr_offering_nationwide(db, lender_nationwide, dscr_program_type):
    """Create DSCR offering from nationwide lender with better rates"""
    return LenderProgramOffering.objects.create(
        lender=lender_nationwide,
        program_type=dscr_program_type,
        min_rate=6.5,  # Better rate
        max_rate=9.0,
        min_points=0.0,
        max_points=2.5,
        lender_fee=Decimal("1295.00"),
        min_fico=640,  # Stricter FICO
        max_ltv=80.0,  # Higher LTV
        min_dscr=1.1,  # Stricter DSCR
        min_loan=Decimal("150000.00"),
        max_loan=Decimal("5000000.00"),
        is_active=True
    )


@pytest.fixture
def conventional_offering(db, lender_nationwide, conventional_program_type):
    """Create conventional offering"""
    return LenderProgramOffering.objects.create(
        lender=lender_nationwide,
        program_type=conventional_program_type,
        min_rate=5.5,
        max_rate=7.5,
        min_points=0.0,
        max_points=1.0,
        lender_fee=Decimal("795.00"),
        min_fico=580,
        max_ltv=97.0,
        min_loan=Decimal("50000.00"),
        max_loan=Decimal("766550.00"),
        is_active=True
    )


@pytest.fixture
def rate_adjustment_fico_ltv(db, dscr_offering_ca):
    """Create FICO×LTV rate adjustments"""
    adjustments = [
        # FICO 620-679, LTV 0-60%: -0.5 points (lender credit)
        RateAdjustment.objects.create(
            offering=dscr_offering_ca,
            adjustment_type=RateAdjustment.ADJUSTMENT_TYPE_FICO_LTV,
            row_min=620,
            row_max=679,
            col_min=0,
            col_max=60,
            adjustment_points=-0.5
        ),
        # FICO 620-679, LTV 60.01-75%: +0.25 points (cost)
        RateAdjustment.objects.create(
            offering=dscr_offering_ca,
            adjustment_type=RateAdjustment.ADJUSTMENT_TYPE_FICO_LTV,
            row_min=620,
            row_max=679,
            col_min=60.01,
            col_max=75,
            adjustment_points=0.25
        ),
        # FICO 680-739, LTV 0-60%: -0.75 points (larger credit)
        RateAdjustment.objects.create(
            offering=dscr_offering_ca,
            adjustment_type=RateAdjustment.ADJUSTMENT_TYPE_FICO_LTV,
            row_min=680,
            row_max=739,
            col_min=0,
            col_max=60,
            adjustment_points=-0.75
        ),
        # FICO 680-739, LTV 60.01-75%: +0.125 points
        RateAdjustment.objects.create(
            offering=dscr_offering_ca,
            adjustment_type=RateAdjustment.ADJUSTMENT_TYPE_FICO_LTV,
            row_min=680,
            row_max=739,
            col_min=60.01,
            col_max=75,
            adjustment_points=0.125
        ),
        # FICO 740+, LTV 0-75%: -1.0 points (best pricing)
        RateAdjustment.objects.create(
            offering=dscr_offering_ca,
            adjustment_type=RateAdjustment.ADJUSTMENT_TYPE_FICO_LTV,
            row_min=740,
            row_max=850,
            col_min=0,
            col_max=75,
            adjustment_points=-1.0
        ),
    ]
    return adjustments


@pytest.mark.integration
class TestQualifyingInfo:
    """Test QualifyingInfo data class"""

    def test_qualifying_info_initialization(self):
        """Test that QualifyingInfo initializes correctly"""
        qi = QualifyingInfo(
            property_type="residential",
            entity_type="individual",
            purpose="purchase",
            occupancy="investment",
            state="CA",
            loan_amount=500000.0,
            ltv=75.0,
            estimated_credit_score=680
        )

        assert qi.property_type == "residential"
        assert qi.entity_type == "individual"
        assert qi.purpose == "purchase"
        assert qi.occupancy == "investment"
        assert qi.state == "CA"
        assert qi.loan_amount == 500000.0
        assert qi.ltv == 75.0
        assert qi.estimated_credit_score == 680


@pytest.mark.integration
class TestFilterGeneration:
    """Test filter generation for loan matching"""

    def test_get_filters_for_qualification(self):
        """Test that filters are correctly generated from QualifyingInfo"""
        qi = QualifyingInfo(
            property_type="residential",
            entity_type="individual",
            purpose="purchase",
            occupancy="investment",
            state="CA",
            loan_amount=500000.0,
            ltv=75.0,
            estimated_credit_score=680
        )

        filters = _get_filters_for_loan_program_match_by_qual(qi)

        # Check filter structure
        assert filters['program_type__property_types__contains'] == ['residential']
        assert filters['program_type__entity_types__contains'] == ['individual']
        assert filters['program_type__purposes__contains'] == ['purchase']
        assert filters['program_type__occupancy__contains'] == ['investment']
        assert filters['lender__include_states__contains'] == ['CA']
        assert filters['min_loan__lte'] == 500000.0
        assert filters['max_loan__gte'] == 500000.0
        assert filters['max_ltv__gte'] == 75.0
        assert filters['min_fico__lte'] == 680
        assert filters['is_active'] is True


@pytest.mark.integration
class TestLoanMatching:
    """Test loan matching logic"""

    def test_match_programs_basic(self, dscr_offering_ca, dscr_offering_nationwide):
        """Test basic program matching with qualifying borrower"""
        qi = QualifyingInfo(
            property_type="residential",
            entity_type="individual",
            purpose="purchase",
            occupancy="investment",
            state="CA",
            loan_amount=500000.0,
            ltv=70.0,
            estimated_credit_score=680
        )

        matches = get_matched_loan_programs_for_qual(qi)

        # Should match both offerings (CA lender and nationwide)
        assert matches.count() == 2
        # Should be ordered by lowest rate (nationwide is 6.5%, CA is 7.0%)
        assert matches[0].lender.company_name == "National Mortgage Corp"
        assert matches[1].lender.company_name == "California Lending Co"

    def test_match_programs_fico_boundary(self, dscr_offering_ca, dscr_offering_nationwide):
        """Test FICO boundary matching (640 required for nationwide)"""
        # FICO 640 - should match both
        qi_640 = QualifyingInfo(
            property_type="residential",
            entity_type="individual",
            purpose="purchase",
            occupancy="investment",
            state="CA",
            loan_amount=500000.0,
            ltv=70.0,
            estimated_credit_score=640
        )
        matches_640 = get_matched_loan_programs_for_qual(qi_640)
        assert matches_640.count() == 2

        # FICO 639 - should match only CA lender (min 620)
        qi_639 = QualifyingInfo(
            property_type="residential",
            entity_type="individual",
            purpose="purchase",
            occupancy="investment",
            state="CA",
            loan_amount=500000.0,
            ltv=70.0,
            estimated_credit_score=639
        )
        matches_639 = get_matched_loan_programs_for_qual(qi_639)
        assert matches_639.count() == 1
        assert matches_639[0].lender.company_name == "California Lending Co"

        # FICO 619 - should match nothing
        qi_619 = QualifyingInfo(
            property_type="residential",
            entity_type="individual",
            purpose="purchase",
            occupancy="investment",
            state="CA",
            loan_amount=500000.0,
            ltv=70.0,
            estimated_credit_score=619
        )
        matches_619 = get_matched_loan_programs_for_qual(qi_619)
        assert matches_619.count() == 0

    def test_match_programs_ltv_boundary(self, dscr_offering_ca, dscr_offering_nationwide):
        """Test LTV boundary matching"""
        # LTV 75% - should match both (CA max 75%, nationwide max 80%)
        qi_75 = QualifyingInfo(
            property_type="residential",
            entity_type="individual",
            purpose="purchase",
            occupancy="investment",
            state="CA",
            loan_amount=500000.0,
            ltv=75.0,
            estimated_credit_score=680
        )
        matches_75 = get_matched_loan_programs_for_qual(qi_75)
        assert matches_75.count() == 2

        # LTV 76% - should match only nationwide (max 80%)
        qi_76 = QualifyingInfo(
            property_type="residential",
            entity_type="individual",
            purpose="purchase",
            occupancy="investment",
            state="CA",
            loan_amount=500000.0,
            ltv=76.0,
            estimated_credit_score=680
        )
        matches_76 = get_matched_loan_programs_for_qual(qi_76)
        assert matches_76.count() == 1
        assert matches_76[0].lender.company_name == "National Mortgage Corp"

        # LTV 81% - should match nothing
        qi_81 = QualifyingInfo(
            property_type="residential",
            entity_type="individual",
            purpose="purchase",
            occupancy="investment",
            state="CA",
            loan_amount=500000.0,
            ltv=81.0,
            estimated_credit_score=680
        )
        matches_81 = get_matched_loan_programs_for_qual(qi_81)
        assert matches_81.count() == 0

    def test_match_programs_loan_amount_boundary(self, dscr_offering_ca, dscr_offering_nationwide):
        """Test loan amount boundary matching"""
        # $150,000 - should match both (CA min $100k, nationwide min $150k)
        qi_150k = QualifyingInfo(
            property_type="residential",
            entity_type="individual",
            purpose="purchase",
            occupancy="investment",
            state="CA",
            loan_amount=150000.0,
            ltv=70.0,
            estimated_credit_score=680
        )
        matches_150k = get_matched_loan_programs_for_qual(qi_150k)
        assert matches_150k.count() == 2

        # $149,999 - should match only CA lender (min $100k)
        qi_149k = QualifyingInfo(
            property_type="residential",
            entity_type="individual",
            purpose="purchase",
            occupancy="investment",
            state="CA",
            loan_amount=149999.0,
            ltv=70.0,
            estimated_credit_score=680
        )
        matches_149k = get_matched_loan_programs_for_qual(qi_149k)
        assert matches_149k.count() == 1
        assert matches_149k[0].lender.company_name == "California Lending Co"

        # $99,999 - should match nothing
        qi_99k = QualifyingInfo(
            property_type="residential",
            entity_type="individual",
            purpose="purchase",
            occupancy="investment",
            state="CA",
            loan_amount=99999.0,
            ltv=70.0,
            estimated_credit_score=680
        )
        matches_99k = get_matched_loan_programs_for_qual(qi_99k)
        assert matches_99k.count() == 0

    def test_match_programs_state_filtering(self, dscr_offering_ca, dscr_offering_nationwide):
        """Test state availability filtering"""
        # CA - should match both lenders
        qi_ca = QualifyingInfo(
            property_type="residential",
            entity_type="individual",
            purpose="purchase",
            occupancy="investment",
            state="CA",
            loan_amount=500000.0,
            ltv=70.0,
            estimated_credit_score=680
        )
        matches_ca = get_matched_loan_programs_for_qual(qi_ca)
        assert matches_ca.count() == 2

        # TX - should match only nationwide lender
        qi_tx = QualifyingInfo(
            property_type="residential",
            entity_type="individual",
            purpose="purchase",
            occupancy="investment",
            state="TX",
            loan_amount=500000.0,
            ltv=70.0,
            estimated_credit_score=680
        )
        matches_tx = get_matched_loan_programs_for_qual(qi_tx)
        assert matches_tx.count() == 1
        assert matches_tx[0].lender.company_name == "National Mortgage Corp"

        # WA - should match nothing (neither lender licensed)
        qi_wa = QualifyingInfo(
            property_type="residential",
            entity_type="individual",
            purpose="purchase",
            occupancy="investment",
            state="WA",
            loan_amount=500000.0,
            ltv=70.0,
            estimated_credit_score=680
        )
        matches_wa = get_matched_loan_programs_for_qual(qi_wa)
        assert matches_wa.count() == 0

    def test_match_programs_property_type_filtering(self, dscr_offering_ca, dscr_offering_nationwide, conventional_offering):
        """Test property type and occupancy filtering"""
        # Investment property - should match DSCR only
        qi_investment = QualifyingInfo(
            property_type="residential",
            entity_type="individual",
            purpose="purchase",
            occupancy="investment",
            state="CA",
            loan_amount=500000.0,
            ltv=70.0,
            estimated_credit_score=680
        )
        matches_investment = get_matched_loan_programs_for_qual(qi_investment)
        assert matches_investment.count() == 2  # Both DSCR lenders
        assert all('DSCR' in m.program_type.name for m in matches_investment)

        # Primary residence - should match conventional only
        qi_primary = QualifyingInfo(
            property_type="residential",
            entity_type="individual",
            purpose="purchase",
            occupancy="primary",
            state="CA",
            loan_amount=400000.0,
            ltv=90.0,
            estimated_credit_score=620
        )
        matches_primary = get_matched_loan_programs_for_qual(qi_primary)
        assert matches_primary.count() == 1
        assert matches_primary[0].program_type.name == "Conventional"


@pytest.mark.integration
class TestLoanMatchingService:
    """Test LoanMatchingService interface"""

    def test_match_programs_with_dict(self, dscr_offering_ca, dscr_offering_nationwide):
        """Test match_programs with qualification dictionary"""
        qualification_data = {
            'property_type': 'residential',
            'entity_type': 'individual',
            'purpose': 'purchase',
            'occupancy': 'investment',
            'state': 'CA',
            'loan_amount': 500000.0,
            'ltv': 70.0,
            'estimated_credit_score': 680
        }

        matches = LoanMatchingService.match_programs(qualification_data)

        assert matches.count() == 2
        assert matches[0].lender.company_name == "National Mortgage Corp"

    def test_get_best_rates_limit(self, dscr_offering_ca, dscr_offering_nationwide, conventional_offering):
        """Test get_best_rates with limit"""
        qualification_data = {
            'property_type': 'residential',
            'entity_type': 'individual',
            'purpose': 'purchase',
            'occupancy': 'investment',
            'state': 'CA',
            'loan_amount': 500000.0,
            'ltv': 70.0,
            'estimated_credit_score': 680
        }

        # Get top 1
        best_1 = LoanMatchingService.get_best_rates(qualification_data, limit=1)
        assert len(best_1) == 1
        assert best_1[0].lender.company_name == "National Mortgage Corp"

        # Get top 2
        best_2 = LoanMatchingService.get_best_rates(qualification_data, limit=2)
        assert len(best_2) == 2


@pytest.mark.integration
class TestRateAdjustments:
    """Test FICO×LTV rate adjustment calculations"""

    def test_get_adjusted_rate_low_fico_high_ltv(self, dscr_offering_ca, rate_adjustment_fico_ltv):
        """Test adjustment for FICO 620-679, LTV 60.01-75%"""
        adjusted = LoanMatchingService.get_adjusted_rate(
            offering=dscr_offering_ca,
            fico=650,
            ltv=70.0
        )

        assert adjusted['base_rate'] == 7.0
        assert adjusted['total_points'] == 0.25  # Cost
        assert adjusted['adjustments_applied'] == 1

    def test_get_adjusted_rate_low_fico_low_ltv(self, dscr_offering_ca, rate_adjustment_fico_ltv):
        """Test adjustment for FICO 620-679, LTV 0-60%"""
        adjusted = LoanMatchingService.get_adjusted_rate(
            offering=dscr_offering_ca,
            fico=650,
            ltv=55.0
        )

        assert adjusted['base_rate'] == 7.0
        assert adjusted['total_points'] == -0.5  # Credit
        assert adjusted['adjustments_applied'] == 1

    def test_get_adjusted_rate_mid_fico(self, dscr_offering_ca, rate_adjustment_fico_ltv):
        """Test adjustment for FICO 680-739, LTV 0-60%"""
        adjusted = LoanMatchingService.get_adjusted_rate(
            offering=dscr_offering_ca,
            fico=700,
            ltv=55.0
        )

        assert adjusted['base_rate'] == 7.0
        assert adjusted['total_points'] == -0.75  # Larger credit
        assert adjusted['adjustments_applied'] == 1

    def test_get_adjusted_rate_high_fico(self, dscr_offering_ca, rate_adjustment_fico_ltv):
        """Test adjustment for FICO 740+"""
        adjusted = LoanMatchingService.get_adjusted_rate(
            offering=dscr_offering_ca,
            fico=780,
            ltv=70.0
        )

        assert adjusted['base_rate'] == 7.0
        assert adjusted['total_points'] == -1.0  # Best pricing
        assert adjusted['adjustments_applied'] == 1

    def test_get_adjusted_rate_no_adjustments(self, dscr_offering_ca):
        """Test rate with no matching adjustments"""
        # No adjustments created for this scenario
        adjusted = LoanMatchingService.get_adjusted_rate(
            offering=dscr_offering_ca,
            fico=620,
            ltv=76.0  # Outside adjustment grid
        )

        assert adjusted['base_rate'] == 7.0
        assert adjusted['total_points'] == 0.0
        assert adjusted['adjustments_applied'] == 0


@pytest.mark.integration
class TestQuoteGeneration:
    """Test full quote generation with adjustments"""

    def test_get_quotes_with_adjustments(self, dscr_offering_ca, dscr_offering_nationwide, rate_adjustment_fico_ltv):
        """Test complete quote generation"""
        qualification_data = {
            'property_type': 'residential',
            'entity_type': 'individual',
            'purpose': 'purchase',
            'occupancy': 'investment',
            'state': 'CA',
            'loan_amount': 500000.0,
            'ltv': 70.0,
            'estimated_credit_score': 680
        }

        quotes = LoanMatchingService.get_quotes_with_adjustments(qualification_data, limit=10)

        # Should have 2 quotes
        assert len(quotes) == 2

        # Check first quote structure (nationwide lender, lowest rate)
        quote_1 = quotes[0]
        assert quote_1['lender'] == "National Mortgage Corp"
        assert quote_1['program'] == "DSCR Investor"
        assert quote_1['base_rate'] == 6.5
        assert quote_1['min_loan'] == 150000.0
        assert quote_1['max_loan'] == 5000000.0

        # Check second quote (CA lender with adjustment)
        quote_2 = quotes[1]
        assert quote_2['lender'] == "California Lending Co"
        assert quote_2['program'] == "DSCR Investor"
        assert quote_2['base_rate'] == 7.0
        assert quote_2['points'] == 0.125  # Has FICO/LTV adjustment (FICO 680, LTV 70%)
        assert quote_2['adjustments_applied'] == 1

    def test_get_quotes_high_fico_borrower(self, dscr_offering_ca, rate_adjustment_fico_ltv):
        """Test quotes for high FICO borrower get better pricing"""
        qualification_data = {
            'property_type': 'residential',
            'entity_type': 'individual',
            'purpose': 'purchase',
            'occupancy': 'investment',
            'state': 'CA',
            'loan_amount': 500000.0,
            'ltv': 60.0,
            'estimated_credit_score': 760
        }

        quotes = LoanMatchingService.get_quotes_with_adjustments(qualification_data, limit=10)

        # Find CA lender quote
        ca_quote = next(q for q in quotes if q['lender'] == "California Lending Co")

        # Should have -1.0 points (lender credit for high FICO)
        assert ca_quote['points'] == -1.0
        assert ca_quote['adjustments_applied'] == 1


@pytest.mark.integration
class TestInactiveOfferings:
    """Test that inactive offerings are not returned"""

    def test_inactive_offering_not_matched(self, dscr_offering_ca, dscr_offering_nationwide):
        """Test that inactive offerings are excluded from matches"""
        # Make nationwide offering inactive
        dscr_offering_nationwide.is_active = False
        dscr_offering_nationwide.save()

        qualification_data = {
            'property_type': 'residential',
            'entity_type': 'individual',
            'purpose': 'purchase',
            'occupancy': 'investment',
            'state': 'CA',
            'loan_amount': 500000.0,
            'ltv': 70.0,
            'estimated_credit_score': 680
        }

        matches = LoanMatchingService.match_programs(qualification_data)

        # Should only match CA lender now
        assert matches.count() == 1
        assert matches[0].lender.company_name == "California Lending Co"
