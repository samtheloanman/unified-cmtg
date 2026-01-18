from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Nuclear option: Delete all content pages using raw SQL'

    def add_arguments(self, parser):
        parser.add_argument('--confirm', action='store_true', help='Confirm deletion')

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(self.style.WARNING("⚠️  NUCLEAR OPTION - This will delete ALL content!"))
            self.stdout.write("Run with --confirm to proceed")
            return

        with connection.cursor() as cursor:
            # Get IDs of pages to keep (Root and HomePage)
            cursor.execute("SELECT id FROM wagtailcore_page WHERE id IN (1, 2, 3)")
            keep_ids = [row[0] for row in cursor.fetchall()]

            self.stdout.write(f"Preserving pages: {keep_ids}")

            # Count pages to delete
            cursor.execute(f"SELECT COUNT(*) FROM wagtailcore_page WHERE id NOT IN ({','.join(map(str, keep_ids))})")
            count = cursor.fetchone()[0]

            self.stdout.write(f"Will delete {count} pages...")

            # Delete from specific page type tables first
            tables = [
                'cms_programpage',
                'cms_fundedloanpage',
                'cms_blogpage',
                'cms_localprogrampage',
                'cms_programindexpage',
                'cms_fundedloanindexpage',
                'cms_blogindexpage',
                'cms_standardpage',
                'cms_legacyindexpage',
                'cms_legacyrecreatedpage',
            ]

            for table in tables:
                try:
                    cursor.execute(f"DELETE FROM {table}")
                    self.stdout.write(f"  Cleared {table}")
                except Exception as e:
                    self.stdout.write(f"  Skipped {table}: {str(e)}")

            # Delete from main page table
            cursor.execute(f"DELETE FROM wagtailcore_page WHERE id NOT IN ({','.join(map(str, keep_ids))})")
            deleted = cursor.rowcount

            self.stdout.write(self.style.SUCCESS(f"\n✅ Deleted {deleted} pages from wagtailcore_page"))
            self.stdout.write("\nRun 'python manage.py import_wordpress' to re-import content.")
