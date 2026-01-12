# Phase 3: Content Migration (WordPress → Wagtail)

> **Goal**: Migrate all content from WordPress (custommortgage) into Wagtail CMS while preserving URL structure for SEO parity.

---

## 📋 Task Breakdown

### Task 3.1: Create Wagtail Page Models

**Agent**: Wagtail Expert  
**Priority**: P0 - Critical  
**Estimated Time**: 4-5 hours

#### Context
WordPress uses Advanced Custom Fields (ACF) with 64 fields across 6 tabs. We need to model these in Wagtail using a combination of standard fields and StreamFields.

#### ACF Field Structure (from custommortgage)

**Tab 1: Location (23 fields)** - For local landing pages
- city, county, state, zip_code
- local_headline, local_description
- local_image, map_embed
- ... (used for city-specific pages like "/los-angeles-hard-money-loans/")

**Tab 2: Program Info (8 fields)** - Core program data
- program_name, program_type
- min_loan_amount, max_loan_amount
- min_credit_score
- available_states

**Tab 3: Financial Terms (7 fields)**
- interest_rate_min, interest_rate_max
- max_ltv, min_dscr
- points_range
- prepayment_terms

**Tab 4: Program Details (7 fields)** - Rich content
- details_about_mortgage_loan_program (WYSIWYG)
- requirements (WYSIWYG)
- mortgage_program_highlights (WYSIWYG)
- Program_FAQ (Repeater field)

**Tab 5: Property & Loan (8 fields)**
- property_types_residential (Checkbox group)
- property_types_commercial (Checkbox group)
- occupancy_types (Checkbox group)
- loan_purposes (Checkbox group)

**Tab 6: Borrower Details (4 fields)**
- borrower_type (Individual/Entity)
- experience_required
- reserve_requirements

#### Instructions

1. **Create the ProgramPage model**
   ```python
   # cms/models/programs.py
   
   from wagtail.models import Page
   from wagtail.fields import StreamField, RichTextField
   from wagtail.admin.panels import FieldPanel, MultiFieldPanel, TabbedInterface, ObjectList
   from wagtail.api import APIField
   
   class ProgramPage(Page):
       """
       Wagtail page model for loan program pages.
       
       Replaces WordPress ACF "Programs" post type.
       URL pattern: /programs/{slug}/
       """
       
       # === Program Info Tab ===
       program_type = models.CharField(
           max_length=50,
           choices=PROGRAM_TYPE_CHOICES,
           help_text="Primary program category"
       )
       min_loan_amount = models.DecimalField(
           max_digits=12, decimal_places=2,
           default=75000
       )
       max_loan_amount = models.DecimalField(
           max_digits=12, decimal_places=2,
           default=2000000
       )
       min_credit_score = models.PositiveSmallIntegerField(default=620)
       available_states = ArrayField(
           models.CharField(max_length=2),
           default=list,
           help_text="Two-letter state codes"
       )
       
       # === Financial Terms Tab ===
       interest_rate_min = models.FloatField(null=True, blank=True)
       interest_rate_max = models.FloatField(null=True, blank=True)
       max_ltv = models.FloatField(default=80)
       min_dscr = models.FloatField(null=True, blank=True)
       points_range = models.CharField(max_length=50, blank=True)
       prepayment_terms = models.CharField(max_length=100, blank=True)
       
       # === Program Details Tab (Rich Content) ===
       program_description = RichTextField(
           blank=True,
           help_text="Main program description (replaces ACF details_about_mortgage_loan_program)"
       )
       requirements = RichTextField(blank=True)
       highlights = RichTextField(blank=True)
       
       # FAQ as StreamField
       faq = StreamField([
           ('faq_item', blocks.StructBlock([
               ('question', blocks.CharBlock()),
               ('answer', blocks.RichTextBlock()),
           ]))
       ], blank=True, use_json_field=True)
       
       # === Property & Loan Tab ===
       property_types = ArrayField(
           models.CharField(max_length=50),
           default=list
       )
       occupancy_types = ArrayField(
           models.CharField(max_length=50),
           default=list
       )
       loan_purposes = ArrayField(
           models.CharField(max_length=50),
           default=list
       )
       
       # === SEO Fields (Wagtail built-in + custom) ===
       meta_description = models.CharField(max_length=300, blank=True)
       
       # === Link to Pricing Data ===
       linked_program_type = models.ForeignKey(
           'pricing.ProgramType',
           on_delete=models.SET_NULL,
           null=True, blank=True,
           help_text="Link to pricing engine program type"
       )
       
       # === Admin Panel Configuration ===
       program_info_panels = [
           FieldPanel('program_type'),
           FieldPanel('min_loan_amount'),
           FieldPanel('max_loan_amount'),
           FieldPanel('min_credit_score'),
           FieldPanel('available_states'),
       ]
       
       financial_panels = [
           FieldPanel('interest_rate_min'),
           FieldPanel('interest_rate_max'),
           FieldPanel('max_ltv'),
           FieldPanel('min_dscr'),
           FieldPanel('points_range'),
       ]
       
       content_panels = Page.content_panels + [
           FieldPanel('program_description'),
           FieldPanel('requirements'),
           FieldPanel('highlights'),
           FieldPanel('faq'),
       ]
       
       edit_handler = TabbedInterface([
           ObjectList(content_panels, heading='Content'),
           ObjectList(program_info_panels, heading='Program Info'),
           ObjectList(financial_panels, heading='Financial Terms'),
           ObjectList(Page.promote_panels, heading='SEO'),
       ])
       
       # === API Configuration ===
       api_fields = [
           APIField('program_type'),
           APIField('min_loan_amount'),
           APIField('max_loan_amount'),
           APIField('program_description'),
           APIField('faq'),
       ]
       
       class Meta:
           verbose_name = "Program Page"
   ```

2. **Create FundedLoanPage model**
   ```python
   class FundedLoanPage(Page):
       """Showcase of completed loans."""
       loan_type = models.CharField(max_length=100)
       loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
       location = models.CharField(max_length=200)
       property_type = models.CharField(max_length=100)
       closing_date = models.DateField()
       image = models.ForeignKey(
           'wagtailimages.Image',
           on_delete=models.SET_NULL,
           null=True, blank=True
       )
       description = RichTextField(blank=True)
   ```

3. **Create BlogPage model**
   ```python
   class BlogPage(Page):
       """Blog posts / news articles."""
       date = models.DateField()
       author = models.CharField(max_length=100)
       intro = models.TextField()
       body = RichTextField()
       featured_image = models.ForeignKey(
           'wagtailimages.Image',
           on_delete=models.SET_NULL,
           null=True, blank=True
       )
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations cms
   python manage.py migrate
   ```

#### Success Criteria
- [ ] ProgramPage matches all 64 ACF fields (grouped logically)
- [ ] TabbedInterface mirrors WordPress admin experience
- [ ] API fields exposed for headless consumption
- [ ] FundedLoanPage and BlogPage created
- [ ] Migrations run cleanly

---

### Task 3.2: Build WordPress Content Extractor

**Agent**: Wagtail Expert  
**Priority**: P0 - Critical  
**Estimated Time**: 3-4 hours

#### Context
We need to extract content from the live WordPress site using its REST API and save it as JSON for import into Wagtail.

#### Instructions

1. **Update agent_tools.py for content extraction**
   ```python
   # scripts/wp_extractor.py
   
   import requests
   import json
   from pathlib import Path
   
   WP_API_BASE = "https://custommortgageinc.com/wp-json"
   
   class WordPressExtractor:
       """Extract content from WordPress REST API."""
       
       def __init__(self, base_url=WP_API_BASE):
           self.base_url = base_url
           self.session = requests.Session()
       
       def get_programs(self) -> list:
           """Fetch all program posts with ACF data."""
           programs = []
           page = 1
           
           while True:
               response = self.session.get(
                   f"{self.base_url}/wp/v2/programs",
                   params={
                       'page': page,
                       'per_page': 100,
                       'acf_format': 'standard',  # Get full ACF data
                   }
               )
               
               if response.status_code == 400:  # No more pages
                   break
               
               data = response.json()
               if not data:
                   break
               
               programs.extend(data)
               page += 1
           
           return programs
       
       def get_funded_loans(self) -> list:
           """Fetch all funded loan posts."""
           # Similar implementation
           pass
       
       def get_blogs(self) -> list:
           """Fetch all blog posts."""
           # Similar implementation
           pass
       
       def export_all(self, output_dir: Path):
           """Export all content to JSON files."""
           output_dir.mkdir(parents=True, exist_ok=True)
           
           # Programs
           programs = self.get_programs()
           with open(output_dir / 'programs.json', 'w') as f:
               json.dump(programs, f, indent=2)
           print(f"Exported {len(programs)} programs")
           
           # Funded Loans
           funded = self.get_funded_loans()
           with open(output_dir / 'funded_loans.json', 'w') as f:
               json.dump(funded, f, indent=2)
           print(f"Exported {len(funded)} funded loans")
           
           # Blogs
           blogs = self.get_blogs()
           with open(output_dir / 'blogs.json', 'w') as f:
               json.dump(blogs, f, indent=2)
           print(f"Exported {len(blogs)} blog posts")
   
   
   if __name__ == '__main__':
       extractor = WordPressExtractor()
       extractor.export_all(Path('./wp_export'))
   ```

2. **Run the extraction**
   ```bash
   cd ~/code/unified-cmtg/unified-platform/scripts
   python wp_extractor.py
   ```

3. **Verify the output**
   - Check `wp_export/programs.json` has all programs
   - Verify ACF fields are included
   - Note any missing data

#### Success Criteria
- [ ] Extractor fetches all programs from WP REST API
- [ ] ACF custom fields are included in export
- [ ] JSON files created for programs, funded loans, blogs
- [ ] Extraction is idempotent (can run multiple times)

---

### Task 3.3: Create Wagtail Import Command

**Agent**: Wagtail Expert  
**Priority**: P0 - Critical  
**Estimated Time**: 3-4 hours

#### Context
With JSON exports from WordPress, we need a Django management command to import them into Wagtail.

#### Instructions

1. **Create the management command**
   ```python
   # cms/management/commands/import_wordpress.py
   
   from django.core.management.base import BaseCommand
   from wagtail.models import Page
   from cms.models import ProgramPage, FundedLoanPage, BlogPage
   import json
   from pathlib import Path
   
   class Command(BaseCommand):
       help = 'Import WordPress content from JSON exports'
       
       def add_arguments(self, parser):
           parser.add_argument(
               '--input-dir',
               type=str,
               default='./wp_export',
               help='Directory containing JSON exports'
           )
           parser.add_argument(
               '--dry-run',
               action='store_true',
               help='Preview import without saving'
           )
       
       def handle(self, *args, **options):
           input_dir = Path(options['input_dir'])
           dry_run = options['dry_run']
           
           # Get or create parent pages
           home = Page.objects.get(slug='home')
           programs_index = self._get_or_create_index(home, 'programs', 'Programs')
           
           # Import programs
           self._import_programs(input_dir / 'programs.json', programs_index, dry_run)
       
       def _get_or_create_index(self, parent, slug, title):
           """Get or create an index page."""
           try:
               return Page.objects.get(slug=slug)
           except Page.DoesNotExist:
               index = Page(title=title, slug=slug)
               parent.add_child(instance=index)
               return index
       
       def _import_programs(self, json_path, parent, dry_run):
           """Import program pages from JSON."""
           with open(json_path) as f:
               programs = json.load(f)
           
           for wp_program in programs:
               slug = wp_program.get('slug')
               acf = wp_program.get('acf', {})
               
               # Check if already exists
               if ProgramPage.objects.filter(slug=slug).exists():
                   self.stdout.write(f"Skipping existing: {slug}")
                   continue
               
               # Map WordPress fields to Wagtail
               program = ProgramPage(
                   title=wp_program.get('title', {}).get('rendered', ''),
                   slug=slug,
                   
                   # Program Info
                   program_type=acf.get('program_type', ''),
                   min_loan_amount=acf.get('minimum_loan_amount', 75000),
                   max_loan_amount=acf.get('maximum_loan_amount', 2000000),
                   min_credit_score=acf.get('min_credit_score', 620),
                   
                   # Financial
                   interest_rate_min=self._parse_float(acf.get('interest_rates_min')),
                   interest_rate_max=self._parse_float(acf.get('interest_rates_max')),
                   max_ltv=self._parse_float(acf.get('max_ltv', 80)),
                   
                   # Content
                   program_description=acf.get('details_about_mortgage_loan_program', ''),
                   requirements=acf.get('requirements', ''),
                   highlights=acf.get('mortgage_program_highlights', ''),
                   
                   # SEO
                   meta_description=wp_program.get('yoast_head_json', {}).get('description', ''),
               )
               
               if dry_run:
                   self.stdout.write(f"Would create: {slug}")
               else:
                   parent.add_child(instance=program)
                   self.stdout.write(self.style.SUCCESS(f"Created: {slug}"))
       
       def _parse_float(self, value):
           """Safely parse float from various formats."""
           if value is None:
               return None
           try:
               return float(str(value).replace(',', '').replace('%', ''))
           except ValueError:
               return None
   ```

2. **Run the import (dry-run first)**
   ```bash
   python manage.py import_wordpress --dry-run
   python manage.py import_wordpress
   ```

3. **Verify URLs match**
   ```bash
   python manage.py shell
   >>> from cms.models import ProgramPage
   >>> for p in ProgramPage.objects.all()[:10]:
   ...     print(p.url)
   ```

#### Success Criteria
- [ ] Management command imports all programs
- [ ] URLs match WordPress structure (`/programs/{slug}/`)
- [ ] Rich content (WYSIWYG) preserved
- [ ] Dry-run mode works correctly
- [ ] Idempotent (skips existing pages)

---

### Task 3.4: Verify URL Parity

**Agent**: QA Tester  
**Priority**: P0 - Critical  
**Estimated Time**: 2 hours

#### Context
SEO requires that all URLs on the new platform match the old WordPress URLs exactly.

#### Instructions

1. **Generate URL comparison report**
   ```python
   # scripts/verify_urls.py
   
   import requests
   from cms.models import ProgramPage
   
   WP_SITEMAP = "https://custommortgageinc.com/sitemap.xml"
   
   def get_wp_urls():
       """Parse WordPress sitemap for program URLs."""
       # Implementation
       pass
   
   def get_wagtail_urls():
       """Get all Wagtail program URLs."""
       return [p.url for p in ProgramPage.objects.live()]
   
   def compare():
       wp_urls = set(get_wp_urls())
       wt_urls = set(get_wagtail_urls())
       
       missing = wp_urls - wt_urls
       extra = wt_urls - wp_urls
       
       print(f"Missing from Wagtail: {len(missing)}")
       for url in sorted(missing)[:10]:
           print(f"  - {url}")
       
       print(f"Extra in Wagtail: {len(extra)}")
       for url in sorted(extra)[:10]:
           print(f"  + {url}")
   ```

2. **Run comparison**
   ```bash
   python scripts/verify_urls.py
   ```

3. **Fix any discrepancies**

#### Success Criteria
- [ ] 100% of WordPress program URLs exist in Wagtail
- [ ] No broken internal links
- [ ] Redirects configured for any URL changes

---

## 📊 Progress Tracking

| Task | Status | Blocker | Notes |
|------|--------|---------|-------|
| 3.1 Wagtail Models | ⏳ | Phase 2 | - |
| 3.2 WP Extractor | ⏳ | - | - |
| 3.3 Import Command | ⏳ | 3.1, 3.2 | - |
| 3.4 URL Verification | ⏳ | 3.3 | - |

---

*Last Updated: 2026-01-11*
