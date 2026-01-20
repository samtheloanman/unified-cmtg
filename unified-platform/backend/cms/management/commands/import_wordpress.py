import json
import os
import re
from datetime import datetime
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from wagtail.models import Page
from wagtail.images.models import Image
from cms.models import (
    ProgramIndexPage, ProgramPage,
    FundedLoanIndexPage, FundedLoanPage,
    BlogIndexPage, BlogPage
)
from django.conf import settings

class Command(BaseCommand):
    help = 'Imports extracted WordPress content into Wagtail'

    def add_arguments(self, parser):
        parser.add_argument('--wipe', action='store_true', help='Wipe existing content before import')
        parser.add_argument('--input-dir', default='wp_export', help='Directory containing exported JSON')

    def handle(self, *args, **options):
        self.export_dir = Path(options['input_dir'])

        # Get the site root (should be HomePage)
        from wagtail.models import Site
        site = Site.objects.get(is_default_site=True)
        self.home_page = site.root_page

        self.stdout.write(f"Using site root as Home Page: {self.home_page.title} (ID: {self.home_page.id})")

        # Verify it's a HomePage
        from cms.models import HomePage
        if not isinstance(self.home_page.specific, HomePage):
            self.stdout.write(self.style.WARNING(f"Warning: Site root is not a HomePage, it's {type(self.home_page.specific).__name__}"))

        if options['wipe']:
            self.stdout.write("Wiping existing content...")
            slugs = ['programs', 'funded-loans', 'blog']
            for slug in slugs:
                page = Page.objects.child_of(self.home_page).filter(slug=slug).first()
                if page:
                    self.stdout.write(f"Deleting existing index: {slug}")
                    page.delete()
            
            self.home_page.refresh_from_db()

        # Load media manifest
        self.media_map = {}
        manifest_path = self.export_dir / 'media_manifest.json'
        if manifest_path.exists():
            with open(manifest_path) as f:
                self.media_map = json.load(f)

        # 1. Setup Index Pages
        self.program_index = self.get_or_create_index(ProgramIndexPage, "Loan Programs", "programs", self.home_page)
        self.loan_index = self.get_or_create_index(FundedLoanIndexPage, "Funded Loans", "funded-loans", self.home_page)
        self.blog_index = self.get_or_create_index(BlogIndexPage, "Blog", "blog", self.home_page)

        # 2. Import Content
        self.import_programs()
        self.import_funded_loans()
        self.import_blogs()
        self.import_pages()
        
        self.stdout.write(self.style.SUCCESS('Import complete!'))

    def get_or_create_index(self, model, title, slug, parent):
        existing = model.objects.child_of(parent).filter(slug=slug).first()
        if existing:
            self.stdout.write(f"Found existing index: {title}")
            return existing
        
        self.stdout.write(f"Creating index: {title}")
        page = model(title=title, slug=slug)
        parent.add_child(instance=page)
        page.save_revision().publish()
        return page

    def _get_image(self, item):
        """Find local image for item based on _embedded featured media"""
        if '_embedded' not in item: return None
        if 'wp:featuredmedia' not in item['_embedded']: return None
        
        media_list = item['_embedded']['wp:featuredmedia']
        if not media_list or not isinstance(media_list, list): return None
        
        media_data = media_list[0]
        source_url = media_data.get('source_url')
        if not source_url: return None
        
        # Look up in manifest
        local_path = self.media_map.get(source_url)
        if not local_path: return None
        
        filename = Path(local_path).name
        relative_path = f"wp_import/{filename}"
        
        full_path = os.path.join(settings.MEDIA_ROOT, 'wp_import', filename)
        if not os.path.exists(full_path):
            return None
            
        # Try to find existing Image
        img = Image.objects.filter(title=filename).first()
        if img: return img
        
        # Create new
        img = Image(title=filename)
        img.file.name = relative_path
        # Set dummy dimensions to avoid IntegrityError if image file isn't physically read by Wagtail
        img.width = 800
        img.height = 600
        img.save()
        return img

    def _parse_faq(self, html):
        """Parse H3/P pairs into Wagtail StreamField blocks"""
        if not html: return []
        items = []
        # Find all H3 and following content until next H3 or end
        # This matches the pattern observed in Super Jumbo program
        matches = re.findall(r'<h3>(.*?)</h3>\s*(.*?)(?=<h3>|$)', html, re.DOTALL)
        for q, a in matches:
            q_text = re.sub(r'<[^>]+>', '', q).strip()
            if q_text:
                items.append({
                    'type': 'faq_item',
                    'value': {
                        'question': q_text,
                        'answer': a.strip()
                    }
                })
        return items

    def _create_program_page(self, item, parent):
        """Unified helper to create a ProgramPage from WP item (Program, Page, or Blog)"""
        title = item['title']['rendered']
        slug = item['slug']
        
        # Check if already exists
        page = ProgramPage.objects.filter(slug=slug).first()
        is_new = False
        if not page:
            is_new = True
            page = ProgramPage(title=title, slug=slug)

        acf = item.get('acf', {}) or {}
        
        # Determine program type from ACF or slug
        raw_type = acf.get('program_type')
        if not raw_type:
            # Try to guess from slug/title if it's coming from a Page or Blog
            if 'commercial' in slug or 'commercial' in title.lower(): raw_type = 'commercial'
            elif 'hard-money' in slug or 'hard money' in title.lower(): raw_type = 'hard_money'
            elif 'reverse' in slug: raw_type = 'reverse_mortgage'
            elif 'non-qm' in slug or 'stated' in slug: raw_type = 'nonqm'

        # Update fields
        page.title = title
        page.first_published_at = make_aware(datetime.strptime(item['date'], "%Y-%m-%dT%H:%M:%S"))
        page.featured_image = self._get_image(item)
        page.source_url = item.get('link', '')
        
        # Core Info
        page.program_type = self._map_program_type(raw_type)
        page.minimum_loan_amount = self._clean_decimal(acf.get('minimum_loan_amount'))
        page.maximum_loan_amount = self._clean_decimal(acf.get('maximum_loan_amount'))
        page.min_credit_score = self._clean_int(acf.get('min_credit_score'))
        
        # Details
        page.mortgage_program_highlights = acf.get('mortgage_program_highlights', '')
        page.what_are = acf.get('what_are', '')
        page.details_about_mortgage_loan_program = acf.get('details_about_mortgage_loan_program', '')
        page.benefits_of = acf.get('benefits_of', '')
        page.requirements = acf.get('requirements', '')
        page.how_to_qualify_for = acf.get('how_to_qualify_for', '')
        page.why_us = acf.get('why_us', '')
        page.faq = self._parse_faq(acf.get('Program_FAQ', ''))
        
        # Financial
        page.interest_rates = str(acf.get('interest_rates', ''))[:100]
        page.max_ltv = str(acf.get('max_ltv', ''))[:20]
        page.max_debt_to_income_ratio = self._clean_float(acf.get('max_debt_to_income_ratio'))
        page.min_dscr = self._clean_float(acf.get('min_dscr'))
        
        # Location
        page.is_local_variation = bool(acf.get('is_local_variation', False))
        page.target_city = acf.get('city_name', '')
        page.target_state = acf.get('region_code', '') 
        page.target_region = acf.get('region_name', '')
        
        # Arrays
        page.property_types = acf.get('property_types_residential') or []
        page.occupancy_types = acf.get('occupancy') or []
        page.lien_position = acf.get('lien_position') or []
        page.amortization_terms = acf.get('amortization_terms') or []
        page.purpose_of_mortgage = acf.get('purpose_of_mortgage') or []
        page.refinance_types = acf.get('refinance_mortgage') or []
        page.income_documentation_type = acf.get('income_documentation_type') or []
        page.borrower_types = acf.get('borrower_type') or []
        page.citizenship_requirements = acf.get('citizenship') or []
        
        if is_new:
            parent.add_child(instance=page)
        else:
            page.save()
            
        page.save_revision().publish()
        return page

    def import_programs(self):
        self.stdout.write("\nImporting Programs...")
        path = self.export_dir / 'programs.json'
        if not path.exists():
            return

        with open(path) as f:
            items = json.load(f)

        count = 0
        for item in items:
            self._create_program_page(item, self.program_index)
            count += 1
            
        self.stdout.write(f"Imported {count} programs from programs.json.")

    def import_funded_loans(self):
        self.stdout.write("\nImporting Funded Loans...")
        path = self.export_dir / 'funded_loans.json'
        if not path.exists():
            return

        with open(path) as f:
            items = json.load(f)
            
        count = 0
        for item in items:
            title = item['title']['rendered']
            slug = item['slug']
            content = item['content']['rendered']
            # Clean shortcodes
            content = re.sub(r'\[acf field="[^"]+"\]', '', content)
            
            page = FundedLoanPage(
                title=title,
                slug=slug,
                first_published_at=make_aware(datetime.strptime(item['date'], "%Y-%m-%dT%H:%M:%S")),
                description=content,
                featured_image=self._get_image(item)
            )
            self.loan_index.add_child(instance=page)
            page.save_revision().publish()
            count += 1
        
        self.stdout.write(f"Imported {count} funded loans.")

    def import_blogs(self):
        self.stdout.write("\nImporting Blogs...")
        path = self.export_dir / 'blogs.json'
        if not path.exists():
            return

        with open(path) as f:
            items = json.load(f)
            
        count = 0
        for item in items:
            title = item['title']['rendered']
            slug = item['slug']
            content = item['content']['rendered']
            excerpt = item['excerpt']['rendered']
            
            # Heuristic: Check if this "Blog" is actually a Program
            program_keywords = ['stated-income', 'super-jumbo', 'loan-program', 'mortgage-program']
            if any(kw in slug.lower() for kw in program_keywords):
                self.stdout.write(f"  - Reclassifying Blog as Program: {slug}")
                self._create_program_page(item, self.program_index)
                continue
            
            # Author
            author_name = "Custom Mortgage Team"
            if '_embedded' in item and 'author' in item['_embedded']:
                 authors = item['_embedded']['author']
                 if authors:
                     author_name = authors[0].get('name', author_name)
            
            pub_date = datetime.strptime(item['date'], "%Y-%m-%dT%H:%M:%S").date()
            
            page = BlogPage(
                title=title,
                slug=slug,
                first_published_at=make_aware(datetime.strptime(item['date'], "%Y-%m-%dT%H:%M:%S")),
                date=pub_date,
                author=author_name,
                body=content,
                intro=excerpt,
                featured_image=self._get_image(item)
            )
            self.blog_index.add_child(instance=page)
            page.save_revision().publish()
            count += 1
            
        self.stdout.write(f"Imported {count} blogs.")

    def import_pages(self):
        """Standard pages might actually be programs in the legacy site"""
        self.stdout.write("\nImporting Pages (scanning for programs)...")
        path = self.export_dir / 'pages.json'
        if not path.exists():
            return

        with open(path) as f:
            items = json.load(f)
            
        count = 0
        program_keywords = [
            'loan', 'mortgage', 'financing', 'stated', 'jumbo', 
            'hard money', 'fha', 'va', 'reverse', 'construction'
        ]
        
        for item in items:
            title = item['title']['rendered'].lower()
            slug = item['slug'].lower()
            acf = item.get('acf', {}) or {}
            
            # Heuristic: If it has program-specific ACF data or matches keywords
            is_program = any(kw in title or kw in slug for kw in program_keywords)
            # If it has specific program ACF fields filled
            if acf.get('program_type') or acf.get('minimum_loan_amount') or acf.get('Program_FAQ'):
                is_program = True
            
            if is_program:
                self.stdout.write(f"  - Found program in Pages: {item['slug']}")
                self._create_program_page(item, self.program_index)
                count += 1
        
        self.stdout.write(f"Imported {count} programs from pages.json.")

    def _map_program_type(self, val):
        if not val: return 'residential'
        val = str(val).lower()
        if 'commercial' in val: return 'commercial'
        if 'hard money' in val: return 'hard_money'
        if 'nonqm' in val: return 'nonqm'
        if 'reverse' in val: return 'reverse_mortgage'
        return 'residential'

    def _clean_decimal(self, val):
        if not val: return None
        try:
            v = str(val)
            v = re.sub(r'<[^>]+>', '', v)
            v = v.replace(',', '').replace('$', '').strip()
             # If empty after strip
            if not v: return None
            return v 
        except:
             return None

    def _clean_int(self, val):
        if not val: return None
        try:
            v = str(val)
            v = re.sub(r'<[^>]+>', '', v)
            v = v.replace(',', '').replace('$', '').strip()
            if not v: return None
            return int(float(v))
        except:
             return None

    def _clean_float(self, val):
        if not val: return None
        try:
            v = str(val)
            v = re.sub(r'<[^>]+>', '', v)
            v = v.replace(',', '').replace('%', '').strip()
            if not v: return None
            return float(v)
        except:
             return None
