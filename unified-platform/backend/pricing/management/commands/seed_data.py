from django.core.management.base import BaseCommand
from pricing.models import Lender, ProgramType, LenderProgramOffering, RateAdjustment

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Create lender
        lender, _ = Lender.objects.get_or_create(
            company_name="Acra Lending",
            defaults={'include_states': ['CA','TX','FL'], 'is_active': True}
        )

        # Create program
        program, _ = ProgramType.objects.get_or_create(
            name="DSCR 30-Year Fixed",
            defaults={
                'category': 'non_qm',
                'property_types': ['residential'],
                'entity_types': ['individual'],
                'purposes': ['purchase'],
                'occupancy': ['investment'],
                'base_min_fico': 660,
                'base_max_ltv': 80.0
            }
        )

        # Create offering
        offering, _ = LenderProgramOffering.objects.get_or_create(
            lender=lender, program_type=program,
            defaults={
                'min_rate': 7.25, 'max_rate': 8.5,
                'min_fico': 660, 'max_ltv': 80.0,
                'min_loan': 75000, 'max_loan': 2000000,
                'is_active': True
            }
        )

        self.stdout.write(self.style.SUCCESS('Seed data created!'))
