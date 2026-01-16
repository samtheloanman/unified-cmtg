# Jules Prompt: Phase F.3 - Content Import & URL Migration

**Track**: `finalization_20260114`  
**Phase**: F.3  
**Priority**: HIGH  
**Estimated Time**: 4-6 hours  
**Dependencies**: F.2 (WordPress extraction must be complete)

---

## MISSION

Import WordPress content from JSON exports into Wagtail CMS. Ensure 100% URL parity for SEO.

## CONTEXT

- F.2 has exported: `wp_export/programs.json`, `blogs.json`, `funded_loans.json`
- Target models created in F.1: ProgramPage, BlogPage, FundedLoanPage
- Must preserve WordPress URL structure exactly
- Antigravity will verify URL parity after import

## REFERENCE FILES

- Exported data: `backend/wp_export/programs.json`
- Target models: `backend/cms/models/programs.py`
- Field mapping: See F.1 ProgramPage model

## TASKS

### 1. Create Import Management Command

**File**: `backend/cms/management/commands/import_wordpress.py`

```python
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
            default='wp_export',
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
        input_dir = Path(options['input_dir'])
        dry_run = options['dry_run']
        content_type = options['content_type']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved'))
        
        # Get or create index pages
        home = Page.objects.get(slug='home')
        
        if content_type in ['programs', 'all']:
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
        
        for wp_program in programs:
            slug = wp_program.get('slug')
            acf = wp_program.get('acf', {})
            
            # Check if already exists
            if ProgramPage.objects.filter(slug=slug).exists():
                self.stdout.write(f'  Skipping existing: {slug}')
                continue
            
            # Map WordPress fields to Wagtail
            program = ProgramPage(
                title=self._get_rendered_text(wp_program.get('title', {})),
                slug=slug,
                
                # Program Info
                program_type=acf.get('program_type', ''),
                min_loan_amount=self._parse_decimal(acf.get('minimum_loan_amount', acf.get('min_loan_amount', 75000))),
                max_loan_amount=self._parse_decimal(acf.get('maximum_loan_amount', acf.get('max_loan_amount', 2000000))),
                min_credit_score=self._parse_int(acf.get('min_credit_score', acf.get('minimum_credit_score', 620))),
                
                # Financial Terms
                interest_rate_min=self._parse_float(acf.get('interest_rate_min', acf.get('interest_rates_min'))),
                interest_rate_max=self._parse_float(acf.get('interest_rate_max', acf.get('interest_rates_max'))),
                max_ltv=self._parse_float(acf.get('max_ltv', 80)),
                min_dscr=self._parse_float(acf.get('min_dscr')),
                points_range=acf.get('points_range', ''),
                prepayment_terms=acf.get('prepayment_terms', ''),
                
                # Rich Content
                program_description=acf.get('details_about_mortgage_loan_program', acf.get('program_description', '')),
                requirements=acf.get('requirements', ''),
                highlights=acf.get('mortgage_program_highlights', acf.get('highlights', '')),
                
                # Property & Loan
                property_types=self._parse_array(acf.get('property_types', acf.get('property_types_residential', []))),
                occupancy_types=self._parse_array(acf.get('occupancy_types', acf.get('occupancy', []))),
                loan_purposes=self._parse_array(acf.get('loan_purposes', acf.get('purpose', []))),
                
                # SEO
                search_description=self._get_yoast_description(wp_program),
            )
            
            if dry_run:
                self.stdout.write(f'  Would create: {slug}')
            else:
                try:
                    parent.add_child(instance=program)
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
        
        for wp_post in posts:
            slug = wp_post.get('slug')
            
            if BlogPage.objects.filter(slug=slug).exists():
                self.stdout.write(f'  Skipping existing: {slug}')
                continue
            
            blog = BlogPage(
                title=self._get_rendered_text(wp_post.get('title', {})),
                slug=slug,
                date=wp_post.get('date', ''),
                author=self._get_author_name(wp_post),
                intro=self._get_rendered_text(wp_post.get('excerpt', {})),
                body=self._get_rendered_text(wp_post.get('content', {})),
            )
            
            if dry_run:
                self.stdout.write(f'  Would create: {slug}')
            else:
                try:
                    parent.add_child(instance=blog)
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
        
        for wp_loan in loans:
            slug = wp_loan.get('slug')
            acf = wp_loan.get('acf', {})
            
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
                closing_date=acf.get('closing_date'),
                description=acf.get('description', ''),
            )
            
            if dry_run:
                self.stdout.write(f'  Would create: {slug}')
            else:
                try:
                    parent.add_child(instance=loan)
                    self.stdout.write(self.style.SUCCESS(f'  Created: {slug}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  Error creating {slug}: {e}'))
    
    # Helper methods
    def _get_rendered_text(self, field):
        """Extract rendered text from WordPress field."""
        if isinstance(field, dict):
            return field.get('rendered', '')
        return str(field) if field else ''
    
    def _get_yoast_description(self, wp_post):
        """Extract Yoast SEO description."""
        yoast = wp_post.get('yoast_head_json', {})
        return yoast.get('description', '')
    
    def _get_author_name(self, wp_post):
        """Get author name from post."""
        # Try to get from embedded data first
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
            return float(str(value).replace(',', '').replace('$', ''))
        except (ValueError, AttributeError):
            return 0
    
    def _parse_int(self, value):
        """Safely parse integer."""
        if value is None:
            return 0
        try:
            return int(float(str(value).replace(',', '')))
        except (ValueError, AttributeError):
            return 0
    
    def _parse_float(self, value):
        """Safely parse float."""
        if value is None:
            return None
        try:
            return float(str(value).replace(',', '').replace('%', ''))
        except (ValueError, AttributeError):
            return None
    
    def _parse_array(self, value):
        """Parse array field."""
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [v.strip() for v in value.split(',') if v.strip()]
        return []
```

### 2. Run Import (Dry Run First)

```bash
cd unified-platform/backend

# Dry run to preview
python manage.py import_wordpress --dry-run

# Review output, check for errors

# Import programs only (test)
python manage.py import_wordpress --content-type programs

# Check result
python manage.py shell
>>> from cms.models import ProgramPage
>>> ProgramPage.objects.count()
>>> ProgramPage.objects.first().title

# If successful, import all
python manage.py import_wordpress --content-type all
```

### 3. Create URL Verification Script

**File**: `backend/scripts/verify_url_parity.py`

```python
import requests
from cms.models import ProgramPage, BlogPage
from bs4 import BeautifulSoup

def get_wordpress_urls():
    """Fetch URLs from WordPress sitemap."""
    sitemap_url = "https://custommortgageinc.com/sitemap.xml"
    response = requests.get(sitemap_url)
    soup = BeautifulSoup(response.content, 'xml')
    
    urls = set()
    for loc in soup.find_all('loc'):
        url = loc.text
        if '/programs/' in url or '/blog/' in url:
            # Extract path only
            path = url.replace('https://custommortgageinc.com', '')
            urls.add(path)
    
    return urls

def get_wagtail_urls():
    """Get URLs from Wagtail pages."""
    urls = set()
    
    for page in ProgramPage.objects.live():
        urls.add(page.url)
    
    for page in BlogPage.objects.live():
        urls.add(page.url)
    
    return urls

def compare_urls():
    """Compare WordPress and Wagtail URLs."""
    wp_urls = get_wordpress_urls()
    wt_urls = get_wagtail_urls()
    
    missing = wp_urls - wt_urls
    extra = wt_urls - wp_urls
    
    print(f"WordPress URLs: {len(wp_urls)}")
    print(f"Wagtail URLs: {len(wt_urls)}")
    print(f"\nMissing from Wagtail: {len(missing)}")
    for url in sorted(missing)[:10]:
        print(f"  - {url}")
    
    print(f"\nExtra in Wagtail: {len(extra)}")
    for url in sorted(extra)[:10]:
        print(f"  + {url}")
    
    if not missing and not extra:
        print("\n✅ 100% URL PARITY ACHIEVED!")
        return True
    else:
        print(f"\n❌ URL mismatch: {len(missing)} missing, {len(extra)} extra")
        return False

if __name__ == '__main__':
    compare_urls()
```

### 4. Run URL Verification

```bash
python scripts/verify_url_parity.py
```

### 5. Fix Any Mismatches

If URLs don't match:
- Check slug mapping
- Verify index page URLs
- Update page slugs if needed
- Re-run verification

## SUCCESS CRITERIA

- [ ] `import_wordpress` command runs without errors
- [ ] `ProgramPage.objects.count()` >= 75
- [ ] `BlogPage.objects.count()` > 0
- [ ] URL verification script shows 100% parity
- [ ] All pages visible in Wagtail admin
- [ ] Random page test: content displays correctly

## HANDOFF

After completion, write to `conductor/handoffs/gemini/inbox.md`:
```
F.3 Complete: Imported [X] programs, [Y] blogs, [Z] funded loans.
URL parity: [100%/issues found].
All content visible in Wagtail admin.
Ready for F.5 (Programmatic SEO Infrastructure).
```

Commit: `git commit -m "feat(cms): F.3 WordPress content import with URL parity"`
