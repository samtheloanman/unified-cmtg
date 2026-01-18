from django.core.management.base import BaseCommand
from wagtail.models import Site, Page
from cms.models import ProgramIndexPage, ProgramPage, HomePage
from collections import defaultdict


class Command(BaseCommand):
    help = 'Debug page hierarchy to find why programs are not accessible via API'

    def handle(self, *args, **options):
        self.stdout.write("="*70)
        self.stdout.write("WAGTAIL PAGE HIERARCHY DEBUG")
        self.stdout.write("="*70)

        # 1. Site root
        site = Site.objects.get(is_default_site=True)
        self.stdout.write(f"\n1. SITE ROOT:")
        self.stdout.write(f"   ID: {site.root_page.id}")
        self.stdout.write(f"   Title: {site.root_page.title}")
        self.stdout.write(f"   Type: {site.root_page.content_type}")
        self.stdout.write(f"   Depth: {site.root_page.depth}")

        # 2. All HomePage instances
        self.stdout.write(f"\n2. HOME PAGES ({HomePage.objects.count()}):")
        for hp in HomePage.objects.all():
            self.stdout.write(f"   - {hp.title} (ID: {hp.id}, Depth: {hp.depth})")
            self.stdout.write(f"     Parent: {hp.get_parent().title} (ID: {hp.get_parent().id})")
            self.stdout.write(f"     Is site root: {hp.id == site.root_page.id}")

        # 3. All ProgramIndexPage instances
        self.stdout.write(f"\n3. PROGRAM INDEX PAGES ({ProgramIndexPage.objects.count()}):")
        for idx in ProgramIndexPage.objects.all():
            child_count = ProgramPage.objects.child_of(idx).count()
            under_root = idx.is_descendant_of(site.root_page)
            self.stdout.write(f"   - {idx.title} (ID: {idx.id}, Slug: {idx.slug})")
            self.stdout.write(f"     Depth: {idx.depth}")
            self.stdout.write(f"     Parent: {idx.get_parent().title} (ID: {idx.get_parent().id})")
            self.stdout.write(f"     Under site root: {under_root}")
            self.stdout.write(f"     Child programs: {child_count}")
            if child_count > 0:
                samples = ProgramPage.objects.child_of(idx)[:3]
                for prog in samples:
                    self.stdout.write(f"       • {prog.title[:50]}")

        # 4. Group all programs by parent
        self.stdout.write(f"\n4. ALL PROGRAMS BY PARENT:")
        all_programs = ProgramPage.objects.all()
        self.stdout.write(f"   Total programs: {all_programs.count()}")

        parent_groups = defaultdict(list)
        for prog in all_programs:
            parent = prog.get_parent()
            parent_groups[parent.id].append(prog)

        for parent_id, programs in sorted(parent_groups.items()):
            parent = Page.objects.get(id=parent_id)
            under_root = parent.is_descendant_of(site.root_page)
            self.stdout.write(f"\n   Parent: {parent.title} (ID: {parent_id})")
            self.stdout.write(f"   Type: {parent.content_type}")
            self.stdout.write(f"   Under site root: {under_root}")
            self.stdout.write(f"   Programs: {len(programs)}")
            for prog in programs[:5]:
                self.stdout.write(f"     • {prog.title[:60]}")
            if len(programs) > 5:
                self.stdout.write(f"     ... and {len(programs) - 5} more")

        # 5. API accessibility summary
        self.stdout.write(f"\n5. API ACCESSIBILITY SUMMARY:")
        accessible = sum(1 for p in all_programs if p.is_descendant_of(site.root_page))
        self.stdout.write(f"   Programs accessible via API: {accessible}")
        self.stdout.write(f"   Programs NOT accessible: {all_programs.count() - accessible}")

        if accessible < all_programs.count():
            self.stdout.write(self.style.WARNING(f"\n   ⚠️  WARNING: {all_programs.count() - accessible} programs are orphaned!"))
            self.stdout.write(self.style.WARNING(f"   These programs exist but won't appear in the API."))

        self.stdout.write("\n" + "="*70)
