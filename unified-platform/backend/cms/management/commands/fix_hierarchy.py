from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.exceptions import ValidationError
from wagtail.models import Site, Page
from cms.models import ProgramIndexPage, ProgramPage, FundedLoanIndexPage, FundedLoanPage, BlogIndexPage, BlogPage


class Command(BaseCommand):
    help = 'Fix page hierarchy by moving orphaned pages to correct parent under site root'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
        parser.add_argument('--programs-only', action='store_true', help='Only fix programs, skip funded loans and blogs')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        programs_only = options['programs_only']

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))

        self.stdout.write("="*70)
        self.stdout.write("FIXING PAGE HIERARCHY")
        self.stdout.write("="*70)

        # Get site root
        site = Site.objects.get(is_default_site=True)
        site_root = site.root_page
        self.stdout.write(f"\nSite root: {site_root.title} (ID: {site_root.id})")

        # Find the correct index pages (under site root)
        # Must be direct child of site root (HomePage)
        correct_program_index = ProgramIndexPage.objects.filter(
            slug='programs'
        ).child_of(site_root).first()

        correct_loan_index = FundedLoanIndexPage.objects.filter(
            slug='funded-loans'
        ).descendant_of(site_root).first()

        correct_blog_index = BlogIndexPage.objects.filter(
            slug='blog'
        ).descendant_of(site_root).first()

        if not correct_program_index:
            self.stdout.write(self.style.ERROR("Could not find correct ProgramIndexPage under site root!"))
            return

        self.stdout.write(f"\nCorrect ProgramIndexPage: {correct_program_index.title} (ID: {correct_program_index.id})")
        if correct_loan_index:
            self.stdout.write(f"Correct FundedLoanIndexPage: {correct_loan_index.title} (ID: {correct_loan_index.id})")
        if correct_blog_index:
            self.stdout.write(f"Correct BlogIndexPage: {correct_blog_index.title} (ID: {correct_blog_index.id})")

        # Find orphaned programs
        all_programs = ProgramPage.objects.all()
        orphaned_programs = [p for p in all_programs if not p.is_descendant_of(site_root)]

        self.stdout.write(f"\n\nFound {len(orphaned_programs)} orphaned programs")

        if orphaned_programs:
            self.stdout.write("\nMoving orphaned programs to correct parent...")
            success_count = 0
            error_count = 0

            for prog in orphaned_programs:
                old_parent = prog.get_parent()
                self.stdout.write(f"  - {prog.title[:60]}")
                self.stdout.write(f"    From: {old_parent.title} (ID: {old_parent.id})")
                self.stdout.write(f"    To: {correct_program_index.title} (ID: {correct_program_index.id})")

                if not dry_run:
                    try:
                        with transaction.atomic():
                            prog.move(correct_program_index, pos='last-child')
                            prog.save_revision().publish()
                        success_count += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"    ERROR: {str(e)}"))
                        error_count += 1

            if not dry_run:
                self.stdout.write(f"\n  Programs moved: {success_count}, Errors: {error_count}")

        # Find orphaned funded loans
        if correct_loan_index and not programs_only:
            all_loans = FundedLoanPage.objects.all()
            orphaned_loans = [p for p in all_loans if not p.is_descendant_of(site_root)]

            self.stdout.write(f"\n\nFound {len(orphaned_loans)} orphaned funded loans")

            if orphaned_loans:
                self.stdout.write("\nMoving orphaned funded loans to correct parent...")
                for loan in orphaned_loans:
                    old_parent = loan.get_parent()
                    self.stdout.write(f"  - {loan.title[:60]}")

                    if not dry_run:
                        loan.move(correct_loan_index, pos='last-child')
                        loan.save_revision().publish()

        # Find orphaned blogs
        if correct_blog_index and not programs_only:
            all_blogs = BlogPage.objects.all()
            orphaned_blogs = [p for p in all_blogs if not p.is_descendant_of(site_root)]

            self.stdout.write(f"\n\nFound {len(orphaned_blogs)} orphaned blogs")

            if orphaned_blogs:
                self.stdout.write("\nMoving orphaned blogs to correct parent...")
                for blog in orphaned_blogs:
                    old_parent = blog.get_parent()
                    self.stdout.write(f"  - {blog.title[:60]}")

                    if not dry_run:
                        blog.move(correct_blog_index, pos='last-child')
                        blog.save_revision().publish()

        # Clean up orphaned index pages
        self.stdout.write("\n\nCleaning up orphaned index pages...")
        orphaned_indexes = ProgramIndexPage.objects.exclude(id=correct_program_index.id)

        for idx in orphaned_indexes:
            if not idx.is_descendant_of(site_root):
                child_count = ProgramPage.objects.child_of(idx).count()
                self.stdout.write(f"  - Deleting orphaned index: {idx.title} (ID: {idx.id}, {child_count} children)")
                if not dry_run:
                    idx.delete()

        if dry_run:
            self.stdout.write(self.style.WARNING("\nDRY RUN COMPLETE - Run without --dry-run to apply changes"))
        else:
            self.stdout.write(self.style.SUCCESS("\n✅ Hierarchy fixed successfully!"))

            # Verify
            accessible = sum(1 for p in ProgramPage.objects.all() if p.is_descendant_of(site_root))
            total = ProgramPage.objects.count()
            self.stdout.write(f"\nVerification: {accessible}/{total} programs now accessible via API")

        self.stdout.write("="*70)
