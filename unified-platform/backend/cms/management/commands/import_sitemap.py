import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from wagtail.models import Page

from cms.models import (
    HomePage, ProgramIndexPage, ProgramPage, 
    FundedLoanIndexPage, FundedLoanPage, 
    LegacyIndexPage, LegacyRecreatedPage,
    StandardPage
)


class Command(BaseCommand):
    help = 'Import pages from custommortgageinc.com sitemap'
    
    SITEMAP_URLS = {
        'pages': 'https://custommortgageinc.com/page-sitemap.xml',
        'programs': 'https://custommortgageinc.com/loan-programs-sitemap.xml',
        'funded': 'https://custommortgageinc.com/funded-loan-sitemap.xml',
    }
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (compatible; CMTGMigrationBot/1.0)'
    }
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--sitemap',
            choices=['pages', 'programs', 'funded', 'all'],
            default='all',
            help='Which sitemap to import'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without creating pages'
        )
    
    def handle(self, *args, **options):
        # Ensure we have a root page
        root_page = Page.objects.get(depth=1)
        
        # Create or get HomePage
        home_page = HomePage.objects.first()
        if not home_page:
            # Use unique slug to avoid conflict with existing Wagtail welcome page
            slug = "cmtg-home" if Page.objects.filter(slug="home", depth=2).exists() else "home"
            home_page = HomePage(
                title="Custom Mortgage Inc",
                slug=slug,
                hero_title="Nationwide Mortgage Lender",
                hero_cta_url="https://custommortgageinc.com/quote",
            )
            root_page.add_child(instance=home_page)
            self.stdout.write(self.style.SUCCESS(f"Created HomePage with slug '{slug}'"))
        
        # Create index pages
        programs_index = self._ensure_index_page(
            home_page, ProgramIndexPage, 
            "Loan Programs", "loan-programs"
        )
        funded_index = self._ensure_index_page(
            home_page, FundedLoanIndexPage,
            "Funded Loans", "funded-loans"
        )
        legacy_index = self._ensure_index_page(
            home_page, LegacyIndexPage,
            "Legacy Recreated", "legacy-recreated"
        )
        
        # Import from sitemaps
        sitemaps_to_import = (
            self.SITEMAP_URLS.keys() 
            if options['sitemap'] == 'all' 
            else [options['sitemap']]
        )
        
        for sitemap_type in sitemaps_to_import:
            self._import_sitemap(
                sitemap_type, 
                programs_index, 
                funded_index,
                legacy_index,
                options['dry_run']
            )
    
    def _ensure_index_page(self, parent, page_class, title, slug):
        """Create index page if it doesn't exist"""
        existing = page_class.objects.first()
        if existing:
            self.stdout.write(f"  [EXISTS] {title} index page")
            return existing
        
        page = page_class(title=title, slug=slug)
        parent.add_child(instance=page)
        self.stdout.write(self.style.SUCCESS(f"Created {title} index page"))
        return page
    
    def _import_sitemap(self, sitemap_type, programs_index, funded_index, legacy_index, dry_run):
        """Import URLs from a sitemap"""
        url = self.SITEMAP_URLS.get(sitemap_type)
        if not url:
            self.stderr.write(f"Unknown sitemap type: {sitemap_type}")
            return
            
        self.stdout.write(f"\nFetching {url}...")
        
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            self.stderr.write(self.style.ERROR(f"Failed to fetch {url}: {e}"))
            return
        
        # Try lxml-xml first, fall back to xml parser
        try:
            soup = BeautifulSoup(response.content, 'lxml-xml')
        except Exception:
            soup = BeautifulSoup(response.content, 'xml')
        
        urls = soup.find_all('loc')
        
        self.stdout.write(f"Found {len(urls)} URLs in {sitemap_type} sitemap")

        # Determine configuration based on sitemap type
        if sitemap_type == 'programs':
            parent = programs_index
            page_class = ProgramPage
        elif sitemap_type == 'funded':
            parent = funded_index
            page_class = FundedLoanPage
        else:
            parent = legacy_index
            page_class = LegacyRecreatedPage

        # Pre-fetch existing slugs to avoid N+1 queries
        all_slugs = set(Page.objects.values_list('slug', flat=True))
        target_slugs = set(page_class.objects.values_list('slug', flat=True))
        
        imported_count = 0
        skipped_count = 0
        
        for url_elem in urls:
            page_url = url_elem.text.strip()
            result = self._create_page_from_url(
                page_url, 
                sitemap_type, 
                parent,
                page_class,
                all_slugs,
                target_slugs,
                dry_run
            )
            if result == 'created':
                imported_count += 1
            elif result == 'skipped':
                skipped_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f"\n{sitemap_type}: Imported {imported_count}, Skipped {skipped_count}"
        ))
    
    def _create_page_from_url(self, url, sitemap_type, parent, page_class, all_slugs, target_slugs, dry_run):
        """Create a Wagtail page from a sitemap URL"""
        # Extract slug from URL
        path = url.replace('https://custommortgageinc.com/', '').strip('/')
        if not path:
            return 'skipped'  # Skip homepage
        
        # Create a unique slug from the path
        slug = path.split('/')[-1] if '/' in path else path
        slug = slug or path.replace('/', '-')
        
        # Clean the slug
        slug = slug.lower().replace(' ', '-')[:50]  # Limit slug length
        
        title = slug.replace('-', ' ').title()
        
        if dry_run:
            self.stdout.write(f"  [DRY RUN] Would create: {title} ({slug})")
            return 'created'
        
        # Check if page already exists
        if slug in target_slugs:
            self.stdout.write(f"  [SKIP] {title} already exists")
            return 'skipped'

        # Also check other page types for same slug to avoid conflicts
        if slug in all_slugs:
            # Append suffix to make unique
            slug = f"{slug}-{sitemap_type}"
            if slug in all_slugs:
                self.stdout.write(f"  [SKIP] {title} slug conflict")
                return 'skipped'

        # Determine extra fields based on sitemap type
        extra_fields = {}
        if sitemap_type == 'programs':
            # Infer program type from URL
            program_type = 'residential'  # default
            path_lower = path.lower()
            if 'commercial' in path_lower:
                program_type = 'commercial'
            elif 'hard-money' in path_lower or 'hardmoney' in path_lower:
                program_type = 'hard_money'
            elif 'nonqm' in path_lower or 'stated' in path_lower or 'no-doc' in path_lower:
                program_type = 'nonqm'
            elif 'reverse' in path_lower:
                program_type = 'reverse_mortgage'
            
            extra_fields = {
                'program_type': program_type,
                'source_url': url,
            }
        elif sitemap_type == 'funded':
             pass
        else:
            # Regular pages go to legacy index for now
            extra_fields = {
                'original_url': url,
                'original_title': title,
            }
        
        # Create the page
        try:
            page = page_class(
                title=title,
                slug=slug,
                **extra_fields
            )
            parent.add_child(instance=page)

            # Update cache
            all_slugs.add(slug)
            target_slugs.add(slug)

            self.stdout.write(self.style.SUCCESS(f"  [CREATED] {title}"))
            return 'created'
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"  [ERROR] {title}: {e}"))
            return 'skipped'
