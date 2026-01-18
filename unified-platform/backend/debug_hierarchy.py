#!/usr/bin/env python
"""Debug script for page hierarchy"""
from wagtail.models import Site, Page
from cms.models import ProgramIndexPage, ProgramPage, HomePage
from collections import defaultdict

print("="*70)
print("WAGTAIL PAGE HIERARCHY DEBUG")
print("="*70)

# 1. Site root
site = Site.objects.get(is_default_site=True)
print(f"\n1. SITE ROOT:")
print(f"   ID: {site.root_page.id}")
print(f"   Title: {site.root_page.title}")
print(f"   Type: {site.root_page.content_type}")
print(f"   Depth: {site.root_page.depth}")

# 2. All HomePage instances
print(f"\n2. HOME PAGES ({HomePage.objects.count()}):")
for hp in HomePage.objects.all():
    print(f"   - {hp.title} (ID: {hp.id}, Depth: {hp.depth})")
    print(f"     Parent: {hp.get_parent().title} (ID: {hp.get_parent().id})")
    print(f"     Is site root: {hp.id == site.root_page.id}")

# 3. All ProgramIndexPage instances
print(f"\n3. PROGRAM INDEX PAGES ({ProgramIndexPage.objects.count()}):")
for idx in ProgramIndexPage.objects.all():
    child_count = ProgramPage.objects.child_of(idx).count()
    under_root = idx.is_descendant_of(site.root_page)
    print(f"   - {idx.title} (ID: {idx.id}, Slug: {idx.slug})")
    print(f"     Depth: {idx.depth}")
    print(f"     Parent: {idx.get_parent().title} (ID: {idx.get_parent().id})")
    print(f"     Under site root: {under_root}")
    print(f"     Child programs: {child_count}")
    if child_count > 0:
        samples = ProgramPage.objects.child_of(idx)[:3]
        for prog in samples:
            print(f"       • {prog.title[:50]}")

# 4. Group all programs by parent
print(f"\n4. ALL PROGRAMS BY PARENT:")
all_programs = ProgramPage.objects.all()
print(f"   Total programs: {all_programs.count()}")

parent_groups = defaultdict(list)
for prog in all_programs:
    parent = prog.get_parent()
    parent_groups[parent.id].append(prog)

for parent_id, programs in sorted(parent_groups.items()):
    parent = Page.objects.get(id=parent_id)
    under_root = parent.is_descendant_of(site.root_page)
    print(f"\n   Parent: {parent.title} (ID: {parent_id})")
    print(f"   Type: {parent.content_type}")
    print(f"   Under site root: {under_root}")
    print(f"   Programs: {len(programs)}")
    for prog in programs[:5]:
        print(f"     • {prog.title[:60]}")
    if len(programs) > 5:
        print(f"     ... and {len(programs) - 5} more")

# 5. API accessibility summary
print(f"\n5. API ACCESSIBILITY SUMMARY:")
accessible = sum(1 for p in all_programs if p.is_descendant_of(site.root_page))
print(f"   Programs accessible via API: {accessible}")
print(f"   Programs NOT accessible: {all_programs.count() - accessible}")

if accessible < all_programs.count():
    print(f"\n   ⚠️  WARNING: {all_programs.count() - accessible} programs are orphaned!")
    print(f"   These programs exist but won't appear in the API.")

print("\n" + "="*70)
