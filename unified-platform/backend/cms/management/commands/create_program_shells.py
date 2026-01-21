from django.core.management.base import BaseCommand
from cms.models import ProgramPage, ProgramIndexPage
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Creates missing program page shells based on the Master Hierarchy.'

    def handle(self, *args, **options):
        # 1. Get Parent Page
        try:
            parent = ProgramIndexPage.objects.first()
            if not parent:
                self.stdout.write(self.style.ERROR("ProgramIndexPage not found. Please create one first."))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error finding parent: {e}"))
            return

        # 2. Define Hierarchy
        # Format: (Category, [('Title', 'slug'), ...])
        hierarchy = [
            ('residential', [
                ('Conventional Mortgages', 'conventional'),
                ('Conforming Mortgages', 'conforming'),
                ('High Balance Conventional', 'high-balance-conventional'),
                ('Fannie Mae Purchase 3% Down', 'fannie-mae-purchase-3-down'),
                ('Residential Mortgage Loans', 'residential-mortgage-loans'),
                ('Residential Mortgages', 'home-loans'),
                ('Jumbo Mortgages', 'jumbo'),
                ('Conforming Jumbo Mortgages', 'conforming-jumbo'),
                ('Non-Conforming Jumbo Mortgages', 'non-conforming-jumbo'),
                ('Super Jumbo Mortgages', 'super-jumbo'),
                ('Super Jumbo Residential', 'super-jumbo-residential-mortgage-loans'),
                ('FHA Mortgages', 'fha'),
                ('FHA Purchase 3.5% Down', 'fha-purchase-3-5-down'), 
                # Note: fha-purchase maps to same title, skipping duplicate titles/slugs logic handling below
                ('FHA Streamline Refinance', 'fha-streamline-mortgage-loans'),
                ('FHA 203k Rehab', 'fha-203k'),
                ('FHA DPA 100% Down Payment', 'fha-dpa-100'),
                ('FHA High Balance', 'fha-high-balance'),
                ('FHA VOE Only', 'fha-voe-only'),
                ('FHA Profit and Loss Only', 'fha-profit-loss-only'),
                ('FHA Self-Employed', 'fha-self-employed'),
                ('VA Mortgages', 'va'),
                ('VA Purchase 100% Financing', 'va-purchase-100-financing'),
                ('VA IRRRL Refinance', 'va-irrrl'),
                ('VA Native American Direct', 'va-native-american'),
                ('VA Loans Standard', 'verterain-va-loans'),
                ('USDA Direct Mortgages', 'usda-direct'),
                ('USDA Guaranteed Mortgages', 'usda-guaranteed'),
                ('USDA Home Improvement', 'usda-improvement'),
            ]),
            ('reverse_mortgage', [
                ('Reverse Mortgage Loan Programs', 'reverse-mortgages-loan-programs'),
                ('FHA Reverse Mortgages', 'fha-reverse'),
            ]),
            ('hard_money', [
                ('Hard Money', 'hard-money'),
                ('Residential Hard Money Loans', 'residential-hard-money'),
                ('Commercial Hard Money Loans', 'commercial-hard-money-loans'),
                ('Fix and Flip Mortgages', 'fix-and-flip'),
                ('Fix and Flip Rehab Loans', 'fix-flip-rehab-loan-rehab-mortgage-loans'),
                ('Fix and Hold Loans', 'fix-and-hold-loans'),
                ('Rehab Loans', 'rehab-loans'),
                ('Bridge Loans', 'bridge-loans'),
                ('Residential Bridge Loans', 'residential-bridge'),
                ('Cash-Out Bridge Loans', 'cash-out-bridge'),
                ('Short-Term Rental Program', 'short-term-rental'),
                ('Vacation Rental Program', 'vacation-rental'),
                ('Soft Money Loans', 'soft-money-loans'),
                ('Trust Deed Investing', 'trust-deed-investing-high-returns-on-hard-money-loans'),
            ]),
            ('nonqm', [
                ('NonQM Loans', 'nonqm'),
                ('DSCR Mortgages', 'dscr'),
                ('Bank Statement Mortgages', 'bank-statement'),
                ('Asset Depletion NonQM', 'asset-depletion'),
                ('No Income Verification', 'no-income-verification'),
                ('NINA Mortgages', 'nina'),
                ('1-Year Income NonQM', '1-year-income'),
                ('Foreign National NonQM', 'foreign-national'),
                ('Physician Loans', 'physician-loans'),
                ('Stated Income Residential', 'home-mortgages'),
                ('Stated Income Cash Out', 'stated-income-cash-out-70-ltv'),
                ('Jumbo Stated Income', 'jumbo-stated-income-mortgage-loans'),
                ('Super Jumbo Stated Income Non-QM', 'super-jumbo-stated-income-non-qm'),
                ('DSCR No-Ratio', 'dscr-no-ratio'),
                ('DSCR Platinum', 'dscr-platinum'),
                ('DSCR NOO', 'dscr-noo'),
                ('DSCR Portfolio', 'dscr-portfolio'),
                ('ITIN Mortgages', 'itin-mortgages'),
                ('ITIN Bank Statement', 'itin-bank-statement'),
                ('ITIN DSCR', 'itin-dscr'),
            ]),
            ('commercial', [
                ('Commercial', 'commercial'),
                ('Apartment Financing', 'apartment-finance-mortgage-loans'),
                ('Office Building Loans', 'office-building'),
                ('Retail Property Loans', 'retail-property'),
                ('Industrial Property Financing', 'industrial-property'),
                ('Hotel Loans', 'hotel-loans'),
                ('Gas Station Loans', 'gas-station-loans'),
                ('Commercial Mortgage Loans', 'commercial-mortgage-loans'),
                ('Stated Income Commercial Loans', 'stated-income-commercial-loans'),
                ('Conduit Loans', 'conduit-loans'),
                ('Commercial Bridge Loans', 'commercial-bridge'),
                ('Commercial Construction', 'commercial-construction'),
            ]),
             ('residential', [ # Construction & Land - mixed, putting in residential/commercial based on context. 
                # But to keep it simple, I'll put Construction under residential if not specified.
                ('Construction Loans', 'construction-loans-2'),
                ('Construction Hard Money', 'construction-hard-money'),
                ('Land Loans', 'land-loans'),
                ('Raw Land Hard Money', 'raw-land'),
                ('Vacant Land Hard Money', 'vacant-land'),
            ]),
            ('commercial', [ # Business & SBA
                ('Business Loans', 'business-loans'),
                ('SBA Mortgages', 'sba'),
                ('SBA 7a Mortgages', 'sba-7a'),
                ('SBA 504 Mortgages', 'sba-504'),
                ('SBA Express Mortgages', 'sba-express'),
                ('Stated Income Business', 'stated-income-business-loans'),
                ('Stated Income Business Line of Credit', 'stated-income-business-line-of-credit'),
            ]),
            ('residential', [ # Distressed
                ('Loan Modifications', 'loan-modifications'),
                ('Short Sales', 'short-sales'),
                ('Sub Prime Loans', 'sub-prime-loans'),
            ])
        ]

        created_count = 0
        existing_count = 0

        for category, programs in hierarchy:
            for title, slug in programs:
                # Check if exists
                if ProgramPage.objects.filter(slug=slug).exists():
                    existing_count += 1
                    continue
                
                # Check if slug exists in ANY page (to avoid collision)
                # But here we specifically want a ProgramPage. 
                # If a different page type has this slug, Wagtail might complain on save.
                
                self.stdout.write(f"Creating: {title} ({slug})")
                
                new_page = ProgramPage(
                    title=title,
                    slug=slug,
                    program_type=category,
                    what_are=f"<h2>What are {title}?</h2><p>Coming soon.</p>", # Placeholder content
                )
                
                try:
                    parent.add_child(instance=new_page)
                    new_page.save_revision().publish()
                    created_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to create {slug}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Finished! Created: {created_count}, Existing: {existing_count}"))
