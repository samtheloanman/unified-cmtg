from django.core.management.base import BaseCommand
from cms.models import City
import csv
from decimal import Decimal
import os

class Command(BaseCommand):
    help = 'Import US cities from simplemaps CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to us_cities.csv')

    def handle(self, *args, **options):
        csv_path = options['csv_file']
        
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'File not found: {csv_path}'))
            return

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                # SimpleMaps basic columns often: city, state_id, state_name, lat, lng, population, density...
                # Adjust based on actual CSV format. Assuming standard simplemaps free data.
                
                try:
                    name = row.get('city')
                    state = row.get('state_id')
                    state_name = row.get('state_name')
                    lat = row.get('lat')
                    lng = row.get('lng')
                    
                    if not (name and state and lat and lng):
                         continue
                         
                    city, created = City.objects.update_or_create(
                        slug=f"{name.lower().replace(' ', '-')}-{state.lower()}",
                        defaults={
                            'name': name,
                            'state': state,
                            'state_name': state_name,
                            'latitude': Decimal(lat),
                            'longitude': Decimal(lng),
                            'population': int(float(row.get('population', 0) or 0)),
                            # 'median_income' not in simplemaps basic, requires census merge. Left null.
                        }
                    )
                    count += 1
                    if count % 100 == 0:
                        self.stdout.write(f'Processed {count} cities...')
                        
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Error importing row {row}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} cities'))
