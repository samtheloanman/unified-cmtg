from django.core.management.base import BaseCommand
from wagtail.models import Site, Page
from cms.models import (
    HomePage, ProgramIndexPage, ProgramPage,
    FundedLoanIndexPage, FundedLoanPage,
    BlogIndexPage, BlogPage,
    LocalProgramPage, Office, City
)


class Command(BaseCommand):
    help = 'Reset all CMS content pages (preserves HomePage/site root)'

    def add_arguments(self, parser):
        parser.add_argument('--confirm', action='store_true', help='Confirm deletion')

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(self.style.WARNING("This will delete ALL content pages!"))
            self.stdout.write("Run with --confirm to proceed")
            return

        site = Site.objects.get(is_default_site=True)
        home_page = site.root_page

        self.stdout.write(f"Preserving HomePage: {home_page.title} (ID: {home_page.id})")

        # Delete all index pages and their children
        deleted_count = 0

        for index_page in ProgramIndexPage.objects.all():
            count = ProgramPage.objects.child_of(index_page).count()
            self.stdout.write(f"Deleting ProgramIndexPage: {index_page.title} ({count} programs)")
            index_page.delete()
            deleted_count += count + 1

        for index_page in FundedLoanIndexPage.objects.all():
            count = FundedLoanPage.objects.child_of(index_page).count()
            self.stdout.write(f"Deleting FundedLoanIndexPage: {index_page.title} ({count} loans)")
            index_page.delete()
            deleted_count += count + 1

        for index_page in BlogIndexPage.objects.all():
            count = BlogPage.objects.child_of(index_page).count()
            self.stdout.write(f"Deleting BlogIndexPage: {index_page.title} ({count} blogs)")
            index_page.delete()
            deleted_count += count + 1

        # Delete any remaining orphaned pages
        remaining_programs = ProgramPage.objects.count()
        if remaining_programs > 0:
            self.stdout.write(f"Deleting {remaining_programs} orphaned programs")
            ProgramPage.objects.all().delete()
            deleted_count += remaining_programs

        remaining_loans = FundedLoanPage.objects.count()
        if remaining_loans > 0:
            self.stdout.write(f"Deleting {remaining_loans} orphaned funded loans")
            FundedLoanPage.objects.all().delete()
            deleted_count += remaining_loans

        remaining_blogs = BlogPage.objects.count()
        if remaining_blogs > 0:
            self.stdout.write(f"Deleting {remaining_blogs} orphaned blogs")
            BlogPage.objects.all().delete()
            deleted_count += remaining_blogs

        # Delete local SEO pages
        local_count = LocalProgramPage.objects.count()
        if local_count > 0:
            self.stdout.write(f"Deleting {local_count} local SEO pages")
            LocalProgramPage.objects.all().delete()
            deleted_count += local_count

        # Delete orphaned pages under old Wagtail root (ID 2)
        old_root = Page.objects.filter(id=2).first()
        if old_root:
            orphaned = Page.objects.child_of(old_root).exclude(id=home_page.id)
            orphan_count = orphaned.count()
            if orphan_count > 0:
                self.stdout.write(f"Deleting {orphan_count} pages under old Wagtail root")
                for page in orphaned:
                    try:
                        page.delete()
                        deleted_count += 1
                    except:
                        pass

        self.stdout.write(self.style.SUCCESS(f"\n✅ Reset complete! Deleted {deleted_count} pages."))
        self.stdout.write("\nRun 'python manage.py import_wordpress' to re-import content.")
