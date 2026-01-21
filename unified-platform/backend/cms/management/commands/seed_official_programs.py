from django.core.management.base import BaseCommand
from cms.models import ProgramPage, ProgramIndexPage
from pricing.models import ProgramType
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Seeds the official list of loan programs with legacy IDs and links them.'

    def handle(self, *args, **options):
        # 1. Master List of Programs (ID, Title, Slug, ProgramType Category)
        # TODO: Populate this with the full list from the user/CSV
        OFFICIAL_PROGRAMS = [
            # Residential - General
            (9101, 'Residential', 'residential', 'residential'),
            (9102, 'Conventional Mortgages', 'conventional', 'residential'),
            (9103, 'Conforming Mortgages', 'conforming', 'residential'),
            (9104, 'Conforming Jumbo Mortgages', 'conforming-jumbo', 'residential'),
            (9105, 'Non-Conforming Jumbo Mortgages', 'non-conforming-jumbo', 'residential'),
            (9106, 'Jumbo Mortgages', 'jumbo', 'residential'),
            (9107, 'Super Jumbo Mortgages', 'super-jumbo', 'residential'),
            (9108, 'High Balance Conventional Mortgages', 'high-balance-conventional', 'residential'),
            
            # FHA
            (9109, 'FHA Mortgages', 'fha', 'residential'),
            (9110, 'FHA Purchase 3.5% Down', 'fha-purchase', 'residential'),
            (9111, 'FHA Streamline Mortgages', 'fha-streamline', 'residential'),
            (9112, 'FHA 203k Mortgages', 'fha-203k', 'residential'),
            (9113, 'FHA DPA 100 Down Payment', 'fha-dpa-100', 'residential'),
            (9114, 'FHA High Balance Mortgages', 'fha-high-balance', 'residential'),
            (9115, 'FHA Reverse Mortgages', 'fha-reverse', 'reverse_mortgage'),
            (9116, 'FHA Self-Employed Mortgages', 'fha-self-employed', 'residential'),
            (9117, 'FHA VOE Only Mortgages', 'fha-voe-only', 'residential'),
            
            # VA & USDA
            (9118, 'VA Mortgages', 'va', 'residential'),
            (9119, 'VA Purchase 100% Financing', 'va-100-percent', 'residential'),
            (9120, 'VA IRRRL Mortgages', 'va-irrrl', 'residential'),
            (9121, 'VA Native American Direct', 'va-native-american', 'residential'),
            (9122, 'USDA Direct Mortgages', 'usda-direct', 'residential'),
            (9123, 'USDA Guaranteed Mortgages', 'usda-guaranteed', 'residential'),
            (9124, 'USDA Home Improvement Mortgages', 'usda-improvement', 'residential'),
            
            # Commercial
            (9153, 'Commercial', 'commercial', 'commercial'),
            (9170, 'Commercial Construction Mortgages', 'commercial-construction', 'commercial'),
            (9171, 'Commercial Hard Money', 'commercial-hard-money', 'commercial'),
            (9174, 'Apartment Financing', 'apartment-financing', 'commercial'),
            (9175, 'Hotel Loans', 'hotel-loans', 'commercial'),
            (9176, 'Retail Property Loans', 'retail-property', 'commercial'),
            (9177, 'Office Building Loans', 'office-building', 'commercial'),
            (9178, 'Industrial Property Financing', 'industrial-property', 'commercial'),
            (9181, 'Conduit Loans', 'conduit-loans', 'commercial'),
            (9185, 'Commercial Bridge Loans', 'commercial-bridge', 'commercial'),
            
            # SBA
            (9157, 'SBA Mortgages', 'sba', 'commercial'),
            (9158, 'SBA 7a Mortgages', 'sba-7a', 'commercial'),
            (9160, 'SBA 504 Mortgages', 'sba-504', 'commercial'),
            (9165, 'SBA Express Mortgages', 'sba-express', 'commercial'),
            
            # Hard Money
            (9191, 'Hard Money', 'hard-money', 'hard_money'),
            (9192, 'Fix and Flip Mortgages', 'fix-and-flip', 'hard_money'),
            (9193, 'Construction Hard Money', 'construction-hard-money', 'hard_money'),
            (9197, 'Vacant Land Hard Money', 'vacant-land', 'hard_money'),
            (9198, 'Raw Land Hard Money', 'raw-land', 'hard_money'),
            (9199, 'Residential Hard Money Loans', 'residential-hard-money', 'hard_money'),
            (9201, 'Bridge Loans', 'bridge-loans', 'hard_money'),
            (9264, 'Hard Money Cash Out Refinance', 'hard-money-loan', 'hard_money'),
            
            # NonQM
            (9206, 'NonQM Loans', 'nonqm', 'nonqm'),
            (9207, 'DSCR Mortgages', 'dscr', 'nonqm'),
            (9211, 'Bank Statement Mortgages', 'bank-statement', 'nonqm'),
            (9220, '1-Year Income NonQM', '1-year-income', 'nonqm'),
            (9222, 'Asset Depletion NonQM', 'asset-depletion', 'nonqm'),
            (9224, 'No Income Verification Mortgages', 'no-income-verification', 'nonqm'),
            (9226, 'Foreign National NonQM', 'foreign-national', 'nonqm'),
            (9228, 'NINA Mortgages', 'nina', 'nonqm'),
            
            # Migration leftovers / duplicates (Handling carefully)
             # NOTE: These might collide with above if slugs match. 
             # For now, listing them as requested.
            (9265, 'Apartment Financing (Migrated)', 'apartment-finance-mortgage-loans', 'commercial'),
            (9266, 'Business Loans', 'business-loans', 'commercial'),
            (9267, 'Commercial Construction Mortgage Loans', 'commercial-construction-loans', 'commercial'),
            (9275, 'Conventional Residential Mortgages', 'conventional-residential-mortgages', 'residential'),
            (9276, 'FHA Purchase 3.5% Down (Migrated)', 'fha-purchase-3-5-down', 'residential'),
            (9277, 'FHA Streamline Mortgage Loans', 'fha-streamline-mortgage-loans', 'residential'),
            (9278, 'Fannie Mae 3 Down Program', 'fannie-mae-purchase-3-down', 'residential'),
        ]

        self.stdout.write("Starting program consolidation...")

        # 2. Get Parent Page
        parent = ProgramIndexPage.objects.first()
        if not parent:
            self.stdout.write(self.style.ERROR("ProgramIndexPage not found!"))
            return

        # 3. Process Official Programs
        valid_ids = []
        for legacy_id, title, slug, category in OFFICIAL_PROGRAMS:
            self.stdout.write(f"Processing {legacy_id}: {title}")
            valid_ids.append(legacy_id)

            # A. Create/Get Pricing ProgramType
            pt, _ = ProgramType.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': title,
                    'category': category,
                    'is_active': True
                }
            )

            # B. Create/Update CMS ProgramPage
            # Try to find by legacy_id first, then slug
            page = ProgramPage.objects.filter(legacy_id=legacy_id).first()
            if not page:
                page = ProgramPage.objects.filter(slug=slug).first()
            
            if page:
                page.title = title
                page.legacy_id = legacy_id
                page.linked_program_type = pt
                page.program_type = category
                # Publish updates
                page.save_revision().publish()
                self.stdout.write(f"  Updated existing page: {page.url}")
            else:
                page = ProgramPage(
                    title=title,
                    slug=slug,
                    legacy_id=legacy_id,
                    linked_program_type=pt,
                    program_type=category,
                    what_are=f"<h2>What is {title}?</h2><p>Description coming soon.</p>"
                )
                parent.add_child(instance=page)
                page.save_revision().publish()
                self.stdout.write(self.style.SUCCESS(f"  Created new page: {page.url}"))

        # 4. Cleanup (Optional - ask user before enabling deletion)
        # self.stdout.write("Cleaning up non-official programs...")
        # extra_pages = ProgramPage.objects.exclude(legacy_id__in=valid_ids)
        # count = extra_pages.count()
        # if count > 0:
        #     self.stdout.write(self.style.WARNING(f"Found {count} pages not in master list."))
        #     # Iterate and delete or unpublish
        #     # for p in extra_pages:
        #     #     p.delete()
        #     #     self.stdout.write(f"  Deleted: {p.title}")
        
        self.stdout.write(self.style.SUCCESS(f"Done. Processed {len(OFFICIAL_PROGRAMS)} programs."))
