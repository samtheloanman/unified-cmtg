import os
import django
import sys

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from wagtail.models import Page, Site
from cms.models import ProgramPage, ProgramIndexPage, NavigationMenu, City

def run_sanity_check():
    """
    Verifies that the core site structure and content are present in the LIVE database.
    """
    print("--- Site Integrity Sanity Check ---")
    errors = []

    # 1. Check for Program Index
    program_index = ProgramIndexPage.objects.first()
    if not program_index:
        errors.append("❌ ProgramIndexPage is missing!")
    else:
        print("✅ ProgramIndexPage exists.")

    # 2. Check for defaults
    site = Site.objects.filter(is_default_site=True).first()
    if not site:
        errors.append("❌ Default Wagtail Site is missing!")
    else:
        print(f"✅ Default Site exists: {site.hostname}")

    # 3. Check for Main Header menu
    menu = NavigationMenu.objects.filter(name="Main Header").first()
    if not menu:
        errors.append("❌ Main Header NavigationMenu is missing!")
    elif len(menu.items) < 5:
        errors.append(f"❌ Main Header menu has too few items ({len(menu.items)}). Re-run populate_navigation.")
    else:
        print(f"✅ Main Header menu is populated ({len(menu.items)} items).")

    # 4. Verify program counts
    count = ProgramPage.objects.count()
    if count < 75:
        errors.append(f"❌ Unexpectedly low program count: {count} (Expected 75+)")
    else:
        print(f"✅ Program count is healthy: {count}")

    # 5. Verify SEO data
    city_count = City.objects.count()
    if city_count < 30:
        errors.append(f"❌ City SEO data is missing ({city_count}). Re-run seed_sample_cities.")
    else:
        print(f"✅ City SEO data is healthy: {city_count}")

    if errors:
        print("\n--- 🛑 INTEGRITY ERRORS FOUND ---")
        for err in errors:
            print(err)
        sys.exit(1)
    else:
        print("\n--- ✨ SITE INTEGRITY VESTED ---")
        sys.exit(0)

if __name__ == "__main__":
    run_sanity_check()
