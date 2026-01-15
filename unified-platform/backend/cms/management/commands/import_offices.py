from django.core.management.base import BaseCommand
import csv
from pathlib import Path
from cms.models import Office

class Command(BaseCommand):
    help = 'Import office locations from CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            help='Path to offices CSV file'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview import without saving'
        )

    def handle(self, *args, **options):
        csv_path = options.get('csv')
        dry_run = options['dry_run']

        if csv_path:
            self.import_from_csv(csv_path, dry_run)
        else:
            self.create_sample_offices(dry_run)

    def import_from_csv(self, csv_path: str, dry_run: bool):
        """Import offices from CSV file."""
        with open(csv_path, newline='') as f:
            reader = csv.DictReader(f)
            count = 0

            for row in reader:
                if dry_run:
                    self.stdout.write(f"Would create: {row.get('name', row.get('Name'))}")
                    count += 1
                    continue

                office, created = Office.objects.update_or_create(
                    name=row.get('name', row.get('Name', '')),
                    city=row.get('city', row.get('City', '')),
                    state=row.get('state', row.get('State', '')),
                    defaults={
                        'address': row.get('address', row.get('Address', '')),
                        'zipcode': row.get('zipcode', row.get('Zipcode', row.get('Zip', ''))),
                        'phone': row.get('phone', row.get('Phone', '')),
                        'latitude': float(row.get('latitude', row.get('Latitude', 0))),
                        'longitude': float(row.get('longitude', row.get('Longitude', 0))),
                        'is_active': True,
                    }
                )

                action = "Created" if created else "Updated"
                self.stdout.write(self.style.SUCCESS(f"{action}: {office}"))
                count += 1

        self.stdout.write(f"\nProcessed {count} offices")

    def create_sample_offices(self, dry_run: bool):
        """Create sample offices for testing."""
        offices = [
            {
                'name': 'CMRE Headquarters',
                'address': '15910 Ventura Blvd Suite 1610',
                'city': 'Encino',
                'state': 'CA',
                'zipcode': '91436',
                'phone': '(877) 976-5663',
                'latitude': 34.1545,
                'longitude': -118.4953,
                'is_headquarters': True,
            },
            {
                'name': 'CMRE Los Angeles',
                'address': '123 Main Street',
                'city': 'Los Angeles',
                'state': 'CA',
                'zipcode': '90001',
                'phone': '(213) 555-0100',
                'latitude': 34.0522,
                'longitude': -118.2437,
                'is_headquarters': False,
            },
            {
                'name': 'CMRE San Diego',
                'address': '456 Harbor Drive',
                'city': 'San Diego',
                'state': 'CA',
                'zipcode': '92101',
                'phone': '(619) 555-0200',
                'latitude': 32.7157,
                'longitude': -117.1611,
                'is_headquarters': False,
            },
            {
                'name': 'CMRE Phoenix',
                'address': '789 Desert Road',
                'city': 'Phoenix',
                'state': 'AZ',
                'zipcode': '85001',
                'phone': '(602) 555-0300',
                'latitude': 33.4484,
                'longitude': -112.0740,
                'is_headquarters': False,
            },
            {
                'name': 'CMRE Houston',
                'address': '321 Texas Ave',
                'city': 'Houston',
                'state': 'TX',
                'zipcode': '77001',
                'phone': '(713) 555-0400',
                'latitude': 29.7604,
                'longitude': -95.3698,
                'is_headquarters': False,
            },
        ]

        for office_data in offices:
            if dry_run:
                self.stdout.write(f"Would create: {office_data['name']}")
            else:
                office, created = Office.objects.update_or_create(
                    name=office_data['name'],
                    defaults=office_data
                )
                self.stdout.write(self.style.SUCCESS(f"Created: {office}"))

        self.stdout.write(f"\nCreated {len(offices)} sample offices")
