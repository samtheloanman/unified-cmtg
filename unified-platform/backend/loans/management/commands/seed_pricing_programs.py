from django.core.management.base import BaseCommand
from loans.models import LoanProgram, Lender
from loans import choices
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seeds the database with sample pricing programs for MVP'

    def handle(self, *args, **options):
        self.stdout.write("Seeding pricing programs...")

        # 1. Create Sample Lender
        lender, _ = Lender.objects.get_or_create(
            company_name="Sample Wholesale Lender",
            defaults={
                'include_states': ['CA', 'TX', 'FL', 'NY', 'AZ'],
                'company_notes': 'MVP Sample Data'
            }
        )
        lender.include_states = ['CA', 'TX', 'FL', 'NY', 'AZ'] # Ensure states match
        lender.save()

        # 2. Create Conventional 30 Fixed
        Program1, _ = LoanProgram.objects.get_or_create(
            name="MVP Conventional 30 Fixed",
            lender=lender,
            defaults={
                'loan_type': choices.LOAN_TYPE_CONVENTIONAL,
                'min_loan_amount': Decimal('100000.00'),
                'max_loan_amount': Decimal('766550.00'),
                'min_credit': 620,
                'max_loan_to_value': Decimal('97.00'),
                'reserve_requirement': 0,
                'max_compensation': 2,
                'lender_fee': Decimal('1295.00'),
                'prepayment_penalty': choices.PPP_NONE,
                'prepayment_cost': 'none',
                'potential_rate_min': 6.50,
                'potential_rate_max': 7.50,
                'potential_cost_min': 0.0,
                'potential_cost_max': 2.0,
                'min_dscr': 0.0,
                'refinance_seasoning': 'none',
                
                # Arrays
                'occupancy': [choices.OCCUPANCY_OWNER_OCCUPIED, choices.OCCUPANCY_SECOND_HOME],
                'property_types': [choices.PROPERTY_TYPE_RESIDENTIAL],
                'purpose': [choices.LOAN_PURPOSE_PURCHASE, choices.LOAN_PURPOSE_REFINANCE],
                'amortization_terms': [choices.AMORTIZATION_TERM_30],
                'income_type': choices.INCOME_TYPE_FULL_DOC,
                
                # Required Defaults from BaseLoan
                'property_sub_categories': [],
                'property_conditions': [],
                'recourse': [],
                'entity_type': [choices.BORROWING_ENTITY_TYPE_INDIVIDUAL],
                'employment': [choices.EMPLOYMENT_W2, choices.EMPLOYMENT_SELF],
            }
        )

        # 3. Create Jumbo 30 Fixed
        Program2, _ = LoanProgram.objects.get_or_create(
            name="MVP Jumbo 30 Fixed",
            lender=lender,
            defaults={
                'loan_type': choices.LOAN_TYPE_CONVENTIONAL, # Often classified as conventional but non-conforming
                'min_loan_amount': Decimal('766551.00'),
                'max_loan_amount': Decimal('3000000.00'),
                'min_credit': 700,
                'max_loan_to_value': Decimal('80.00'),
                'reserve_requirement': 6,
                'max_compensation': 2,
                'lender_fee': Decimal('1495.00'),
                'prepayment_penalty': choices.PPP_NONE,
                'prepayment_cost': 'none',
                'potential_rate_min': 6.875,
                'potential_rate_max': 7.875,
                'potential_cost_min': 0.0,
                'potential_cost_max': 1.0,
                'min_dscr': 0.0,
                'refinance_seasoning': '6 mo',
                
                'occupancy': [choices.OCCUPANCY_OWNER_OCCUPIED],
                'property_types': [choices.PROPERTY_TYPE_RESIDENTIAL],
                'purpose': [choices.LOAN_PURPOSE_PURCHASE, choices.LOAN_PURPOSE_REFINANCE],
                'amortization_terms': [choices.AMORTIZATION_TERM_30],
                'income_type': choices.INCOME_TYPE_FULL_DOC,
                'entity_type': [choices.BORROWING_ENTITY_TYPE_INDIVIDUAL],
                'employment': [choices.EMPLOYMENT_W2, choices.EMPLOYMENT_SELF],
            }
        )

        # 4. Create DSCR Investment
        Program3, _ = LoanProgram.objects.get_or_create(
            name="MVP DSCR Investment",
            lender=lender,
            defaults={
                'loan_type': choices.LOAN_TYPE_ALT_A, 
                'min_loan_amount': Decimal('150000.00'),
                'max_loan_amount': Decimal('2000000.00'),
                'min_credit': 640,
                'max_loan_to_value': Decimal('80.00'),
                'reserve_requirement': 6,
                'max_compensation': 2,
                'lender_fee': Decimal('1995.00'),
                'prepayment_penalty': '3 yr', # choices.PPP_3YR if defined, simplified here
                'prepayment_cost': '5%',
                'potential_rate_min': 7.50,
                'potential_rate_max': 8.99,
                'potential_cost_min': 0.0,
                'potential_cost_max': 3.0,
                'min_dscr': 1.0,
                'refinance_seasoning': 'none',
                
                'occupancy': [choices.OCCUPANCY_INVESTMENT],
                'property_types': [choices.PROPERTY_TYPE_RESIDENTIAL, choices.PROPERTY_TYPE_COMMERCIAL],
                'purpose': [choices.LOAN_PURPOSE_PURCHASE, choices.LOAN_PURPOSE_REFINANCE],
                'amortization_terms': [choices.AMORTIZATION_TERM_30],
                'income_type': choices.INCOME_TYPE_STATED, # Or DSCR logic
                'entity_type': [choices.BORROWING_ENTITY_TYPE_INDIVIDUAL, choices.BORROWING_ENTITY_TYPE_LLC],
                'employment': [choices.EMPLOYMENT_SELF],
            }
        )

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded 3 programs for lender '{lender.company_name}'"))
