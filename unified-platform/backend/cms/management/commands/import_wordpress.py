from django.core.management.base import BaseCommand
from wagtail.models import Page
from cms.models import ProgramPage, BlogPage, FundedLoanPage
from cms.models import ProgramIndexPage, BlogIndexPage, FundedLoanIndexPage
import json
from pathlib import Path
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Import WordPress content from JSON exports'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--input-dir',
            type=str,
            default='unified-platform/backend/wp_export',
            help='Directory containing JSON exports'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview import without saving'
        )
        parser.add_argument(
            '--content-type',
            type=str,
            choices=['programs', 'blogs', 'funded_loans', 'all'],
            default='all',
            help='Type of content to import'
        )
    
    def handle(self, *args, **options):
        # Adjust input dir path relative to CWD if needed, or use absolute
        # Assuming run from repo root or backend root.
        input_dir = Path(options['input_dir'])
        if not input_dir.is_absolute():
            # If relative, check if existing relative to CWD
            if not input_dir.exists():
                # Try relative to backend
                 # But usually we run from root? command is run via manage.py
                 pass

        dry_run = options['dry_run']
        content_type = options['content_type']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved'))
        
        # Get or create index pages
        from wagtail.models import Site
        site = Site.objects.filter(is_default_site=True).first()
        if not site:
             self.stdout.write(self.style.ERROR('No default site found!'))
             return
        
        home = site.root_page
        
        if content_type in ['programs', 'all']:
            # Check if 'loan-programs' (ID 4) exists and rename/use it?
            # Or just look for 'programs' under home.
            programs_index = self._get_or_create_index(
                home, 'programs', 'Programs', ProgramIndexPage
            )
            self._import_programs(input_dir / 'programs.json', programs_index, dry_run)
        
        if content_type in ['blogs', 'all']:
            blog_index = self._get_or_create_index(
                home, 'blog', 'Blog', BlogIndexPage
            )
            self._import_blogs(input_dir / 'blogs.json', blog_index, dry_run)
        
        if content_type in ['funded_loans', 'all']:
            funded_index = self._get_or_create_index(
                home, 'funded-loans', 'Funded Loans', FundedLoanIndexPage
            )
            self._import_funded_loans(input_dir / 'funded_loans.json', funded_index, dry_run)
    
    def _get_or_create_index(self, parent, slug, title, model_class):
        """Get or create an index page."""
        try:
            return Page.objects.get(slug=slug).specific
        except Page.DoesNotExist:
            index = model_class(title=title, slug=slug)
            parent.add_child(instance=index)
            index.save_revision().publish()
            self.stdout.write(self.style.SUCCESS(f'Created index: {title}'))
            return index
    
    def _import_programs(self, json_path, parent, dry_run):
        """Import program pages from JSON."""
        if not json_path.exists():
            self.stdout.write(self.style.WARNING(f'File not found: {json_path}'))
            return
        
        with open(json_path) as f:
            programs = json.load(f)
        
        self.stdout.write(f'Importing {len(programs)} programs...')
        
        # Refresh parent to avoid MP_Node issues
        parent = Page.objects.get(id=parent.id).specific

        for wp_program in programs:
            slug = wp_program.get('slug')
            acf = wp_program.get('acf', {})
            if isinstance(acf, list):
                acf = {}
            
            # Check if already exists
            if ProgramPage.objects.filter(slug=slug).exists():
                self.stdout.write(f'  Skipping existing: {slug}')
                continue
            
            # Construct interest rates string
            min_rate = self._parse_float(acf.get('interest_rate_min', acf.get('interest_rates_min')))
            max_rate = self._parse_float(acf.get('interest_rate_max', acf.get('interest_rates_max')))
            interest_rates = ""
            if min_rate and max_rate:
                interest_rates = f"{min_rate}% - {max_rate}%"
            elif min_rate:
                interest_rates = f"From {min_rate}%"


                
            # Extract program_type
            pt = acf.get('program_type', 'residential')
            if isinstance(pt, list):
                 pt = pt[0] if pt else 'residential'
            
            # Map WordPress fields to Wagtail
            program = ProgramPage(
                title=self._get_rendered_text(wp_program.get('title', {})),
                slug=slug,
                
                # Program Info
                program_type=pt.lower(), 
                minimum_loan_amount=self._parse_decimal(acf.get('minimum_loan_amount', acf.get('min_loan_amount', 75000))),
                maximum_loan_amount=self._parse_decimal(acf.get('maximum_loan_amount', acf.get('max_loan_amount', 2000000))),
                min_credit_score=self._parse_int(acf.get('min_credit_score', acf.get('minimum_credit_score', 620))),
                
                # Financial Terms
                interest_rates=interest_rates,
                max_ltv=str(self._parse_float(acf.get('max_ltv', 80))) + "%" if acf.get('max_ltv') else "", 
                min_dscr=self._parse_float(acf.get('min_dscr')),
                # points_range -> Not in model
                prepayment_penalty=acf.get('prepayment_terms', ''),
                
                # Rich Content
                details_about_mortgage_loan_program=acf.get('details_about_mortgage_loan_program', acf.get('program_description', '')),
                requirements=acf.get('requirements', ''),
                mortgage_program_highlights=acf.get('mortgage_program_highlights', acf.get('highlights', '')),
                
                # Property & Loan
                property_types=self._parse_array(acf.get('property_types', acf.get('property_types_residential', []))),
                occupancy_types=self._parse_array(acf.get('occupancy_types', acf.get('occupancy', []))),
                purpose_of_mortgage=self._parse_array(acf.get('loan_purposes', acf.get('purpose', []))),
                
                # SEO
                source_url=wp_program.get('link', ''),
            )
            
            if dry_run:
                self.stdout.write(f'  Would create: {slug}')
            else:
                try:
                    parent.add_child(instance=program)
                    program.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS(f'  Created: {slug}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  Error creating {slug}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Imported {len(programs)} programs'))
    
    def _import_blogs(self, json_path, parent, dry_run):
        """Import blog posts from JSON."""
        if not json_path.exists():
            self.stdout.write(self.style.WARNING(f'File not found: {json_path}'))
            return
        
        with open(json_path) as f:
            posts = json.load(f)
        
        self.stdout.write(f'Importing {len(posts)} blog posts...')
        parent = Page.objects.get(id=parent.id).specific
        
        for wp_post in posts:
            slug = wp_post.get('slug')
            
            if BlogPage.objects.filter(slug=slug).exists():
                self.stdout.write(f'  Skipping existing: {slug}')
                continue
            
            blog = BlogPage(
                title=self._get_rendered_text(wp_post.get('title', {})),
                slug=slug,
                date=wp_post.get('date', '').split('T')[0] if wp_post.get('date') else None,
                author=self._get_author_name(wp_post),
                intro=self._get_rendered_text(wp_post.get('excerpt', {})),
                body=self._get_rendered_text(wp_post.get('content', {})),
            )
            
            if dry_run:
                self.stdout.write(f'  Would create: {slug}')
            else:
                try:
                    parent.add_child(instance=blog)
                    blog.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS(f'  Created: {slug}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  Error creating {slug}: {e}'))
    
    def _import_funded_loans(self, json_path, parent, dry_run):
        """Import funded loan posts from JSON."""
        if not json_path.exists():
            self.stdout.write(self.style.WARNING(f'File not found: {json_path}'))
            return
        
        with open(json_path) as f:
            loans = json.load(f)
        
        self.stdout.write(f'Importing {len(loans)} funded loans...')
        parent = Page.objects.get(id=parent.id).specific
        
        for wp_loan in loans:
            slug = wp_loan.get('slug')
            acf = wp_loan.get('acf', {})
            if isinstance(acf, list):
                acf = {}
            
            if FundedLoanPage.objects.filter(slug=slug).exists():
                self.stdout.write(f'  Skipping existing: {slug}')
                continue
            
            loan = FundedLoanPage(
                title=self._get_rendered_text(wp_loan.get('title', {})),
                slug=slug,
                loan_type=acf.get('loan_type', ''),
                loan_amount=self._parse_decimal(acf.get('loan_amount', 0)),
                location=acf.get('location', ''),
                property_type=acf.get('property_type', ''),
                close_date=acf.get('closing_date'), # Model is close_date
                description=acf.get('description', ''),
                source_url=wp_loan.get('link', ''),
            )
            
            if dry_run:
                self.stdout.write(f'  Would create: {slug}')
            else:
                try:
                    parent.add_child(instance=loan)
                    loan.save_revision()
                    self.stdout.write(self.style.SUCCESS(f'  Created: {slug}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  Error creating {slug}: {e}'))
    
    # helper methods
    def _get_rendered_text(self, field):
        """Extract rendered text from WordPress field."""
        if isinstance(field, dict):
            return field.get('rendered', '')
        return str(field) if field else ''
    
    def _get_author_name(self, wp_post):
        """Get author name from post."""
        embedded = wp_post.get('_embedded', {})
        authors = embedded.get('author', [])
        if authors:
            return authors[0].get('name', 'Admin')
        return 'Admin'
    
    def _parse_decimal(self, value):
        """Safely parse decimal."""
        if value is None:
            return 0
        try:
            val_str = str(value).replace(',', '').replace('$', '').strip()
            return float(val_str) if val_str else 0
        except (ValueError, AttributeError):
            return 0
    
    def _parse_int(self, value):
        """Safely parse integer."""
        if value is None:
            return 0
        try:
            val_str = str(value).replace(',', '').strip()
            return int(float(val_str)) if val_str else 0
        except (ValueError, AttributeError):
            return 0
    
    def _parse_float(self, value):
        """Safely parse float."""
        if value is None:
            return None
        try:
            val_str = str(value).replace(',', '').replace('%', '').strip()
            return float(val_str) if val_str else None
        except (ValueError, AttributeError):
            return None
    
    def _parse_array(self, value):
        """Parse array field."""
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            val_str = value.replace('&amp;', '&') # Simple decode
            return [v.strip() for v in val_str.split(',') if v.strip()]
        return []
