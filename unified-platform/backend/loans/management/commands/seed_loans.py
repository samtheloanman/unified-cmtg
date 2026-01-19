from django.core.management.base import BaseCommand
from loans.models import Lender, LoanProgram
from loans import choices
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seeds initial loan programs for testing'

    def handle(self, *args, **options):
        self.stdout.write("Seeding loan data...")

        # 1. Create Lenders
        acra, _ = Lender.objects.get_or_create(
            company_name="Acra Lending",
            defaults={
                'include_states': ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY','DC'],
                # Removed invalid fields from defaults
            }
        )
        
        angel, _ = Lender.objects.get_or_create(
            company_name="Angel Oak",
            defaults={
                'include_states': ['CA','FL','TX','NY'],
            }
        )

        # 2. Create Loan Programs
        # Acra ATR-In-Full (Residential)
        prog_qm, _ = LoanProgram.objects.get_or_create(
            name="Acra ATR-In-Full",
            lender=acra,
            defaults={
                'loan_type': choices.LOAN_TYPE_CONVENTIONAL,
                'min_credit': 660,
                'min_loan_amount': Decimal('100000.00'),
                'max_loan_amount': Decimal('3000000.00'),
                'max_loan_to_value': Decimal('90.00'),
                'property_types': [choices.PROPERTY_TYPE_RESIDENTIAL, choices.PROPERTY_TYPE_COMMERCIAL],
                'occupancy': [choices.OCCUPANCY_OWNER_OCCUPIED, choices.OCCUPANCY_SECOND_HOME, choices.OCCUPANCY_INVESTMENT],
                'purpose': [choices.LOAN_PURPOSE_PURCHASE, choices.LOAN_PURPOSE_REFINANCE],
                
                # Required missing fields
                'property_sub_categories': [choices.PROPERTY_TYPE_SUB_CATEGORY_SINGLE_FAMILY],
                'property_conditions': [choices.PROPERTY_CONDITION_C1],
                'recourse': [choices.RECOURSE_FULL],
                'amortization_terms': [choices.AMORTIZATION_TERM_30],
                'entity_type': [choices.BORROWING_ENTITY_TYPE_INDIVIDUAL],
                'employment': [choices.EMPLOYMENT_W2],
                'reserve_requirement': 6,
                'min_dscr': 1.0,
                'max_compensation': 2,
                'max_dti': 50,
                'lender_fee': Decimal('1495.00'),
                'prepayment_penalty': choices.PPP_NONE,
                'prepayment_cost': 'none',
                'refinance_seasoning': 'none',

                # Rate fields (No base_rate)
                'potential_rate_min': 6.25,
                'potential_rate_max': 7.50,
                'potential_cost_min': 0.0,
                'potential_cost_max': 2.0,
            }
        )

        # Angel Oak Bank Statement (Non-QM)
        prog_nonqm, _ = LoanProgram.objects.get_or_create(
            name="Bank Statement Jumbo",
            lender=angel,
            defaults={
                'loan_type': choices.LOAN_TYPE_ALT_A, # Approx for Non-QM
                'min_credit': 620,
                'min_loan_amount': Decimal('150000.00'),
                'max_loan_amount': Decimal('4000000.00'),
                'max_loan_to_value': Decimal('85.00'),
                'property_types': [choices.PROPERTY_TYPE_RESIDENTIAL],
                'occupancy': [choices.OCCUPANCY_OWNER_OCCUPIED, choices.OCCUPANCY_SECOND_HOME],
                'purpose': [choices.LOAN_PURPOSE_PURCHASE, choices.LOAN_PURPOSE_REFINANCE],
                
                'property_sub_categories': [choices.PROPERTY_TYPE_SUB_CATEGORY_SINGLE_FAMILY],
                'property_conditions': [choices.PROPERTY_CONDITION_C1],
                'recourse': [choices.RECOURSE_FULL],
                'amortization_terms': [choices.AMORTIZATION_TERM_30],
                'entity_type': [choices.BORROWING_ENTITY_TYPE_INDIVIDUAL],
                'employment': [choices.EMPLOYMENT_SELF], # Bank statement implies self emp
                'reserve_requirement': 12, # Higher reserves
                'min_dscr': 1.0,
                'max_compensation': 2,
                'max_dti': 43,
                'lender_fee': Decimal('1695.00'),
                'prepayment_penalty': choices.PPP_NONE,
                'prepayment_cost': 'none',
                'refinance_seasoning': 'none',

                'potential_rate_min': 6.875,
                'potential_rate_max': 8.25,
                'potential_cost_min': 0.0,
                'potential_cost_max': 2.5,
            }
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded loan data'))
