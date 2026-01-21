import os
import django
import sys

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from django.core.management import call_command
from cms.models import ProgramIndexPage, NavigationMenu

def check_and_seed():
    """Checks if critical content is missing and triggers seeding."""
    print("--- Integrity Check ---")
    
    needs_seeding = False
    
    # 1. Check for Navigation Menu
    if not NavigationMenu.objects.filter(name="Main Header").exists():
        print("⚠️  Main Header missing.")
        needs_seeding = True
    
    # 2. Check for Program Index (core content anchor)
    if not ProgramIndexPage.objects.exists():
        print("⚠️  Program Index Page missing.")
        needs_seeding = True

    if needs_seeding:
        print("🚀 Critical content missing. Initiating auto-recovery...")
        try:
            print("1. Importing WordPress content...")
            call_command('import_wordpress')
            
            print("2. Seeding sample cities...")
            call_command('seed_sample_cities')
            
            print("3. Creating program shells...")
            call_command('create_program_shells')
            
            print("4. Populating home features...")
            call_command('populate_home_features')
            
            print("5. Populating navigation...")
            call_command('populate_navigation')
            
            print("✅ Auto-recovery complete.")
        except Exception as e:
            print(f"❌ Auto-recovery failed: {e}")
            sys.exit(1)
    else:
        print("✅ Core content detected. Skipping auto-seed.")

if __name__ == "__main__":
    check_and_seed()
