from django.core.management.base import BaseCommand
from wagtail.models import Page
from cms.models import HomePage, ProgramPage, FeaturedProgram

class Command(BaseCommand):
    help = 'Populates the Home Page with Featured Programs'

    def handle(self, *args, **options):
        self.stdout.write("Populating Home Page featured programs...")

        # Get Home Page
        try:
            home = HomePage.objects.first()
            if not home:
                self.stdout.write(self.style.ERROR("Home Page not found!"))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error finding Home Page: {e}"))
            return

        # Clear existing
        FeaturedProgram.objects.filter(page=home).delete()

        # Define programs to feature (slugs)
        featured_slugs = [
            'conventional-residential-mortgages', 
            'super-jumbo-residential-mortgage-loans', # Valid
            'dscr', # Short slug for DSCR found in list
            'commercial-mortgag-loans', # typo risk, let's use 'commercial-mortgages' or 'commercial'
            'commercial-mortgages',
            'fha-purchase-3-5-down',
            'va' # Short slug for VA
        ]

        count = 0
        for slug in featured_slugs:
            # Try to find exactly or contains
            prog = ProgramPage.objects.filter(slug__icontains=slug).first()
            if not prog:
                 # Fallback to any program of a type if specific slug fails
                 if 'jumbo' in slug:
                     prog = ProgramPage.objects.filter(program_type='residential', title__icontains='Jumbo').first()
                 elif 'dscr' in slug:
                     prog = ProgramPage.objects.filter(program_type='nonqm', title__icontains='DSCR').first()
            
            if prog:
                FeaturedProgram.objects.create(
                    page=home,
                    program=prog,
                    sort_order=count
                )
                self.stdout.write(f"Added feature: {prog.title}")
                count += 1
            else:
                 self.stdout.write(self.style.WARNING(f"Could not find program for: {slug}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully populated {count} featured programs."))
