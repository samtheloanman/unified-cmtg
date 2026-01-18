from decimal import Decimal
from django.test import TestCase
from pricing.models import (
    Lender,
    ProgramType,
    LenderProgramOffering,
    QualifyingInfo,
)
from pricing import choices
from pricing.services.matching import get_quals_for_loan_program

class ReverseMatchingTests(TestCase):
    def setUp(self):
        # Create Lender
        self.lender = Lender.objects.create(
            company_name="Test Lender",
            include_states=["CA", "TX"]
        )

        # Create ProgramType
        self.program_type = ProgramType.objects.create(
            name="DSCR Investor",
            category="non_qm",
            property_types=[choices.PROPERTY_TYPE_RESIDENTIAL],
            entity_types=[choices.BORROWING_ENTITY_TYPE_LLC],
            purposes=[choices.LOAN_PURPOSE_PURCHASE],
            occupancy=[choices.OCCUPANCY_INVESTMENT]
        )

        # Create Offering
        self.offering = LenderProgramOffering.objects.create(
            lender=self.lender,
            program_type=self.program_type,
            min_rate=5.5,
            max_rate=7.5,
            min_fico=680,
            max_ltv=80.0,
            min_loan=Decimal("100000.00"),
            max_loan=Decimal("1000000.00"),
            is_active=True
        )

    def test_get_quals_for_loan_program_matches(self):
        """Test that get_quals_for_loan_program returns correct matches."""

        # Match
        match = QualifyingInfo.objects.create(
            property_type=choices.PROPERTY_TYPE_RESIDENTIAL,
            entity_type=choices.BORROWING_ENTITY_TYPE_LLC,
            purpose=choices.LOAN_PURPOSE_PURCHASE,
            occupancy=choices.OCCUPANCY_INVESTMENT,
            state="CA",
            loan_amount=Decimal("200000.00"),
            ltv=75.0,
            estimated_credit_score=700
        )

        # No Match - FICO too low
        QualifyingInfo.objects.create(
            property_type=choices.PROPERTY_TYPE_RESIDENTIAL,
            entity_type=choices.BORROWING_ENTITY_TYPE_LLC,
            purpose=choices.LOAN_PURPOSE_PURCHASE,
            occupancy=choices.OCCUPANCY_INVESTMENT,
            state="CA",
            loan_amount=Decimal("200000.00"),
            ltv=75.0,
            estimated_credit_score=600  # < 680
        )

        # No Match - LTV too high
        QualifyingInfo.objects.create(
            property_type=choices.PROPERTY_TYPE_RESIDENTIAL,
            entity_type=choices.BORROWING_ENTITY_TYPE_LLC,
            purpose=choices.LOAN_PURPOSE_PURCHASE,
            occupancy=choices.OCCUPANCY_INVESTMENT,
            state="CA",
            loan_amount=Decimal("200000.00"),
            ltv=85.0,  # > 80
            estimated_credit_score=700
        )

        # No Match - State not in lender states
        QualifyingInfo.objects.create(
            property_type=choices.PROPERTY_TYPE_RESIDENTIAL,
            entity_type=choices.BORROWING_ENTITY_TYPE_LLC,
            purpose=choices.LOAN_PURPOSE_PURCHASE,
            occupancy=choices.OCCUPANCY_INVESTMENT,
            state="NY",  # Not in [CA, TX]
            loan_amount=Decimal("200000.00"),
            ltv=75.0,
            estimated_credit_score=700
        )

        # No Match - Property Type mismatch
        QualifyingInfo.objects.create(
            property_type=choices.PROPERTY_TYPE_COMMERCIAL, # Mismatch
            entity_type=choices.BORROWING_ENTITY_TYPE_LLC,
            purpose=choices.LOAN_PURPOSE_PURCHASE,
            occupancy=choices.OCCUPANCY_INVESTMENT,
            state="CA",
            loan_amount=Decimal("200000.00"),
            ltv=75.0,
            estimated_credit_score=700
        )

        matches = get_quals_for_loan_program(self.offering)

        self.assertEqual(matches.count(), 1)
        self.assertEqual(matches.first(), match)
