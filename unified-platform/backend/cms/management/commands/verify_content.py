from django.core.management.base import BaseCommand
from cms.models import ProgramPage, BlogPage, FundedLoanPage
from pathlib import Path
import csv

class Command(BaseCommand):
    help = 'Verify URL parity between WordPress export and Wagtail'

    def handle(self, *args, **options):
        self.stdout.write("Starting URL Parity Verification...")
        
        # Locate url_mapping.csv
        # If in Docker: /app/wp_export/url_mapping.csv
        # If local: unified-platform/backend/wp_export/url_mapping.csv
        
        potential_paths = [
            Path('wp_export/url_mapping.csv'),
            Path('unified-platform/backend/wp_export/url_mapping.csv'),
        ]
        
        mapping_path = None
        for p in potential_paths:
            if p.exists():
                mapping_path = p
                break
        
        if not mapping_path:
            self.stdout.write(self.style.ERROR("Could not find url_mapping.csv"))
            return

        # 1. Load Intended URLs
        intended_programs = set()
        intended_blogs = set()
        intended_loans = set()
        
        with open(mapping_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row['new_url'].strip('/')
                ctype = row.get('content_type', '')
                if ctype == 'program':
                    intended_programs.add(url)
                elif ctype == 'blog':
                    intended_blogs.add(url)
                elif ctype == 'funded-loan':
                    intended_loans.add(url)
        
        # Check Site Config
        from wagtail.models import Site
        site = Site.objects.filter(is_default_site=True).first()
        if not site:
            self.stdout.write(self.style.WARNING("⚠️  No default Wagtail Site configured. URLs may be None."))
        else:
            self.stdout.write(f"Default Site: {site} (Root: {site.root_page})")

        # 2. Load Actual Wagtail URLs
        actual_programs = set()
        for page in ProgramPage.objects.live():
            url = page.url
            if url:
                 actual_programs.add(url.strip('/'))
            else:
                 # Fallback/Error
                 self.stdout.write(self.style.WARNING(f"Program {page.slug} has no URL"))

        actual_blogs = set()
        for page in BlogPage.objects.live():
            url = page.url
            if url:
                actual_blogs.add(url.strip('/'))
            else:
                 self.stdout.write(self.style.WARNING(f"Blog {page.slug} has no URL"))

        actual_loans = set()
        for page in FundedLoanPage.objects.live():
             url = page.url
             if url:
                 actual_loans.add(url.strip('/'))
             else:
                 self.stdout.write(self.style.WARNING(f"Loan {page.slug} has no URL"))

        # 3. Compare
        self.verify_category("Programs", intended_programs, actual_programs)
        self.verify_category("Blogs", intended_blogs, actual_blogs)
        self.verify_category("Funded Loans", intended_loans, actual_loans)

    def verify_category(self, name, intended, actual):
        self.stdout.write(f"\n--- Verifying {name} ---")
        missing = intended - actual
        extra = actual - intended
        
        self.stdout.write(f"Intended: {len(intended)} | Actual: {len(actual)}")
        
        if missing:
            self.stdout.write(self.style.ERROR(f"MISSING ({len(missing)}):"))
            for url in sorted(missing)[:5]:
                self.stdout.write(f" - {url}")
        
        if extra:
            self.stdout.write(self.style.WARNING(f"EXTRA ({len(extra)}):"))
            for url in sorted(extra)[:5]:
                self.stdout.write(f" + {url}")
        
        if not missing:
            self.stdout.write(self.style.SUCCESS(f"✅ {name} Parity Achieved"))
