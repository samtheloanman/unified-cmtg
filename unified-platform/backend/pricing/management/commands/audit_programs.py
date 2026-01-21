from django.core.management.base import BaseCommand
from pricing.models import ProgramType, LoanProgram, Lender
from cms.models.programs import ProgramPage

class Command(BaseCommand):
    help = 'Audit all loan programs in the system (Legacy, New, and CMS Pages)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("=== 1. New Program Types (pricing.ProgramType) ==="))
        programs = ProgramType.objects.all().order_by('name')
        if programs.exists():
            for p in programs:
                status = "ACTIVE" if p.is_active else "INACTIVE"
                self.stdout.write(f"- [ID: {p.id}] {p.name} ({p.get_category_display()}) [{status}]")
                # List offerings
                offerings = p.offerings.all()
                if offerings:
                    lenders = ", ".join([o.lender.company_name for o in offerings])
                    self.stdout.write(f"    Link: Offerings from: {lenders}")
        else:
            self.stdout.write("  None found.")

        self.stdout.write(self.style.WARNING("\n=== 2. Legacy Loan Programs (pricing.LoanProgram) ==="))
        legacy_programs = LoanProgram.objects.all().order_by('name')
        if legacy_programs.exists():
            for lp in legacy_programs:
                lender_name = lp.lender.company_name if lp.lender else "No Lender"
                self.stdout.write(f"- [ID: {lp.id}] {lp.name} (Lender: {lender_name})")
        else:
            self.stdout.write("  None found.")

        self.stdout.write(self.style.WARNING("\n=== 3. CMS Program Pages (cms.ProgramPage) ==="))
        try:
            pages = ProgramPage.objects.all()
            if pages.exists():
                for page in pages:
                    status = "LIVE" if page.live else "DRAFT"
                    linked = page.linked_program_type.name if page.linked_program_type else "UNLINKED"
                    self.stdout.write(f"- [ID: {page.id}] {page.title} (Status: {status}) (Linked to: {linked})")
            else:
                self.stdout.write("  None found.")
        except Exception as e:
             self.stdout.write(f"  Error accessing CMS pages: {e}")
