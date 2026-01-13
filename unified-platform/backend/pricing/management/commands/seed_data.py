from django.core.management.base import BaseCommand
from pricing.models import Lender, ProgramType, LenderProgramOffering, RateAdjustment

class Command(BaseCommand):
    help = 'Seed initial pricing data'

    def handle(self, *args, **options):
        # Create a lender
        lender, _ = Lender.objects.get_or_create(
            company_name="Acra Lending",
            defaults={
                'include_states': ['CA', 'TX', 'FL', 'NY', 'AZ'],
                'is_active': True
            }
        )
        self.stdout.write(f"Created lender: {lender.company_name}")

        # Create a program type
        program, _ = ProgramType.objects.get_or_create(
            name="DSCR 30-Year Fixed",
            defaults={
                'category': 'non_qm',
                'loan_type': 'dscr',
                'property_types': ['residential', 'multi_family'],
                'entity_types': ['individual', 'llc'],
                'purposes': ['purchase', 'refinance'],
                'occupancy': ['investment'],
                'base_min_fico': 660,
                'base_max_ltv': 80.0
            }
        )
        self.stdout.write(f"Created program: {program.name}")

        # Create offering
        offering, _ = LenderProgramOffering.objects.get_or_create(
            lender=lender,
            program_type=program,
            defaults={
                'min_rate': 7.25,
                'max_rate': 8.50,
                'min_points': 0,
                'max_points': 2,
                'min_fico': 660,
                'max_ltv': 80.0,
                'min_loan': 75000,
                'max_loan': 2000000,
                'is_active': True
            }
        )
        self.stdout.write(f"Created offering: {offering}")

        # Create FICO/LTV adjustments
        fico_ltv_grid = [
            (740, 779, 0, 60, -0.250),
            (740, 779, 60, 70, -0.125),
            (740, 779, 70, 75, 0.000),
            (740, 779, 75, 80, 0.125),
            (700, 739, 0, 60, 0.000),
            (700, 739, 60, 70, 0.125),
            (700, 739, 70, 75, 0.250),
            (700, 739, 75, 80, 0.375),
            (660, 699, 0, 60, 0.250),
            (660, 699, 60, 70, 0.375),
            (660, 699, 70, 75, 0.500),
            (660, 699, 75, 80, 0.750),
        ]

        for min_fico, max_fico, min_ltv, max_ltv, points in fico_ltv_grid:
            RateAdjustment.objects.get_or_create(
                offering=offering,
                adjustment_type='fico_ltv',
                row_min=min_fico,
                row_max=max_fico,
                col_min=min_ltv,
                col_max=max_ltv,
                defaults={'adjustment_points': points}
            )

        self.stdout.write(self.style.SUCCESS(f"Created {len(fico_ltv_grid)} rate adjustments"))
        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
