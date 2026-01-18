"""
Import locations from CSV file.

Usage:
    python manage.py import_locations

Creates LocationPage objects under LocationIndexPage.
"""

import csv
from django.core.management.base import BaseCommand
from wagtail.models import Page
from cms.models import LocationIndexPage, LocationPage


class Command(BaseCommand):
    help = 'Import locations from CSV file and create LocationPages'
    
    CSV_PATH = 'legacy/locations_refined.csv'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            default=self.CSV_PATH,
            help='Path to locations CSV file'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without making changes'
        )
    
    def handle(self, *args, **options):
        csv_path = options['csv']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - no changes will be made'))
        
        # Find or create LocationIndexPage
        location_index = self.get_or_create_location_index(dry_run)
        if not location_index:
            return
        
        # Read CSV and create locations
        created = 0
        updated = 0
        skipped = 0
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    city = row.get('City', '').strip()
                    state = row.get('State', '').strip()
                    
                    if not city or not state:
                        skipped += 1
                        continue
                    
                    # Generate slug
                    slug = f"{city.lower().replace(' ', '-')}-{state.lower()}"
                    
                    # Check if exists
                    existing = LocationPage.objects.filter(slug=slug).first()
                    
                    if existing:
                        if not dry_run:
                            # Update existing
                            existing.address = row.get('Address', '')
                            existing.second_address = row.get('Second address', '')
                            existing.zipcode = row.get('Zipcode', '')
                            existing.phone = row.get('Phone', '866-976-5669')
                            existing.save_revision().publish()
                        updated += 1
                        self.stdout.write(f"  Updated: {city}, {state}")
                    else:
                        if not dry_run:
                            # Create new
                            location = LocationPage(
                                title=f"{city}, {state}",
                                slug=slug,
                                address=row.get('Address', ''),
                                second_address=row.get('Second address', ''),
                                city=city,
                                state=state,
                                zipcode=row.get('Zipcode', ''),
                                country=row.get('Country', 'USA'),
                                phone=row.get('Phone', '866-976-5669'),
                            )
                            location_index.add_child(instance=location)
                            location.save_revision().publish()
                        created += 1
                        self.stdout.write(self.style.SUCCESS(f"  Created: {city}, {state}"))
        
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'CSV file not found: {csv_path}'))
            return
        
        # Summary
        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write(f'Created: {created}')
        self.stdout.write(f'Updated: {updated}')
        self.stdout.write(f'Skipped: {skipped}')
        self.stdout.write(f'Total: {created + updated}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - no changes were made'))
        else:
            self.stdout.write(self.style.SUCCESS('Import complete!'))
    
    def get_or_create_location_index(self, dry_run):
        """Get or create the LocationIndexPage under HomePage."""
        # Check if already exists
        existing = LocationIndexPage.objects.first()
        if existing:
            self.stdout.write(f'Using existing LocationIndexPage: {existing.title}')
            return existing
        
        if dry_run:
            self.stdout.write('Would create LocationIndexPage')
            return None
        
        # Find HomePage to be parent
        from cms.models import HomePage
        home = HomePage.objects.first()
        
        if not home:
            self.stdout.write(self.style.ERROR('No HomePage found. Cannot create LocationIndexPage.'))
            return None
        
        # Create LocationIndexPage
        location_index = LocationIndexPage(
            title='Locations',
            slug='locations',
            intro='<p>Find a Custom Mortgage location near you.</p>',
        )
        home.add_child(instance=location_index)
        location_index.save_revision().publish()
        
        self.stdout.write(self.style.SUCCESS('Created LocationIndexPage: /locations/'))
        return location_index
