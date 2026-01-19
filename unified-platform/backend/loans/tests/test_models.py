from decimal import Decimal
from django.test import TestCase
from loans.models import Lender, LoanProgram
from loans import choices

class LoansModelTest(TestCase):
    def test_create_full_program(self):
        """Test creating a LoanProgram with all required fields."""
        # 1. Lender
        lender = Lender.objects.create(
            company_name="Test Lender",
            include_states=['CA', 'TX']
        )
        
        # 2. Program with ALL required fields to avoid IntegrityError
        program = LoanProgram.objects.create(
            name="Test QM Program",
            lender=lender,
            loan_type=choices.LOAN_TYPE_CONVENTIONAL,
            min_credit=620,
            
            # Decimals
            min_loan_amount=Decimal('100000.00'),
            max_loan_amount=Decimal('2000000.00'),
            max_loan_to_value=Decimal('90.00'),
            
            # ChoiceArrays
            property_types=[choices.PROPERTY_TYPE_RESIDENTIAL],
            occupancy=[choices.OCCUPANCY_OWNER_OCCUPIED],
            purpose=[choices.LOAN_PURPOSE_PURCHASE],
            property_sub_categories=[choices.PROPERTY_TYPE_SUB_CATEGORY_SINGLE_FAMILY],
            property_conditions=[choices.PROPERTY_CONDITION_C1],
            recourse=[choices.RECOURSE_FULL],
            amortization_terms=[choices.AMORTIZATION_TERM_30],
            entity_type=[choices.BORROWING_ENTITY_TYPE_INDIVIDUAL],
            employment=[choices.EMPLOYMENT_W2],
            
            # Required Integers/Floats/Chars
            reserve_requirement=6,
            min_dscr=1.0,
            max_compensation=2,
            max_dti=50,
            
            lender_fee=Decimal('1495.00'),
            prepayment_penalty=choices.PPP_NONE,
            prepayment_cost='none',
            refinance_seasoning='none',
            
            # Rate/Cost Limits
            potential_rate_min=5.5,
            potential_rate_max=8.5,
            potential_cost_min=0.0,
            potential_cost_max=2.0
        )
        
        self.assertEqual(program.name, "Test QM Program")
        self.assertEqual(program.lender.company_name, "Test Lender")
        self.assertEqual(program.potential_rate_min, 5.5)
