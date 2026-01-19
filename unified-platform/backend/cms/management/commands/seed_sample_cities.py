from django.core.management.base import BaseCommand
from cms.models import City
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed database with sample major US cities for testing LocalProgramPage'

    def handle(self, *args, **options):
        """Import 30 major US cities with GPS coordinates."""

        cities_data = [
            # California
            {'name': 'Los Angeles', 'state': 'CA', 'state_name': 'California', 'lat': '34.052235', 'lng': '-118.243683', 'population': 3971883},
            {'name': 'San Francisco', 'state': 'CA', 'state_name': 'California', 'lat': '37.774929', 'lng': '-122.419418', 'population': 873965},
            {'name': 'San Diego', 'state': 'CA', 'state_name': 'California', 'lat': '32.715736', 'lng': '-117.161087', 'population': 1425976},
            {'name': 'San Jose', 'state': 'CA', 'state_name': 'California', 'lat': '37.338207', 'lng': '-121.886330', 'population': 1030119},
            {'name': 'Sacramento', 'state': 'CA', 'state_name': 'California', 'lat': '38.581572', 'lng': '-121.494400', 'population': 513624},

            # Texas
            {'name': 'Houston', 'state': 'TX', 'state_name': 'Texas', 'lat': '29.760427', 'lng': '-95.369804', 'population': 2304580},
            {'name': 'Dallas', 'state': 'TX', 'state_name': 'Texas', 'lat': '32.776664', 'lng': '-96.796988', 'population': 1304379},
            {'name': 'Austin', 'state': 'TX', 'state_name': 'Texas', 'lat': '30.267153', 'lng': '-97.743061', 'population': 978908},
            {'name': 'San Antonio', 'state': 'TX', 'state_name': 'Texas', 'lat': '29.424122', 'lng': '-98.493629', 'population': 1547253},

            # New York
            {'name': 'New York', 'state': 'NY', 'state_name': 'New York', 'lat': '40.712776', 'lng': '-74.005974', 'population': 8336817},
            {'name': 'Buffalo', 'state': 'NY', 'state_name': 'New York', 'lat': '42.886447', 'lng': '-78.878372', 'population': 278349},

            # Florida
            {'name': 'Miami', 'state': 'FL', 'state_name': 'Florida', 'lat': '25.761681', 'lng': '-80.191788', 'population': 467963},
            {'name': 'Tampa', 'state': 'FL', 'state_name': 'Florida', 'lat': '27.950575', 'lng': '-82.457176', 'population': 399700},
            {'name': 'Orlando', 'state': 'FL', 'state_name': 'Florida', 'lat': '28.538336', 'lng': '-81.379234', 'population': 307573},
            {'name': 'Jacksonville', 'state': 'FL', 'state_name': 'Florida', 'lat': '30.332184', 'lng': '-81.655651', 'population': 911507},

            # Illinois
            {'name': 'Chicago', 'state': 'IL', 'state_name': 'Illinois', 'lat': '41.878113', 'lng': '-87.629799', 'population': 2746388},

            # Pennsylvania
            {'name': 'Philadelphia', 'state': 'PA', 'state_name': 'Pennsylvania', 'lat': '39.952583', 'lng': '-75.165222', 'population': 1584064},
            {'name': 'Pittsburgh', 'state': 'PA', 'state_name': 'Pennsylvania', 'lat': '40.440624', 'lng': '-79.995888', 'population': 302971},

            # Arizona
            {'name': 'Phoenix', 'state': 'AZ', 'state_name': 'Arizona', 'lat': '33.448376', 'lng': '-112.074036', 'population': 1680992},
            {'name': 'Tucson', 'state': 'AZ', 'state_name': 'Arizona', 'lat': '32.221743', 'lng': '-110.926479', 'population': 548073},

            # Other major cities
            {'name': 'Seattle', 'state': 'WA', 'state_name': 'Washington', 'lat': '47.606209', 'lng': '-122.332069', 'population': 753675},
            {'name': 'Denver', 'state': 'CO', 'state_name': 'Colorado', 'lat': '39.739236', 'lng': '-104.990251', 'population': 727211},
            {'name': 'Boston', 'state': 'MA', 'state_name': 'Massachusetts', 'lat': '42.360082', 'lng': '-71.058880', 'population': 692600},
            {'name': 'Las Vegas', 'state': 'NV', 'state_name': 'Nevada', 'lat': '36.169941', 'lng': '-115.139832', 'population': 641903},
            {'name': 'Portland', 'state': 'OR', 'state_name': 'Oregon', 'lat': '45.515232', 'lng': '-122.678367', 'population': 652503},
            {'name': 'Atlanta', 'state': 'GA', 'state_name': 'Georgia', 'lat': '33.748997', 'lng': '-84.387985', 'population': 498715},
            {'name': 'Nashville', 'state': 'TN', 'state_name': 'Tennessee', 'lat': '36.162664', 'lng': '-86.781602', 'population': 689447},
            {'name': 'Detroit', 'state': 'MI', 'state_name': 'Michigan', 'lat': '42.331429', 'lng': '-83.045753', 'population': 672662},
            {'name': 'Charlotte', 'state': 'NC', 'state_name': 'North Carolina', 'lat': '35.227085', 'lng': '-80.843124', 'population': 885708},
            {'name': 'Columbus', 'state': 'OH', 'state_name': 'Ohio', 'lat': '39.961178', 'lng': '-82.998795', 'population': 898553},
        ]

        count = 0
        skipped = 0

        for city_data in cities_data:
            slug = f"{city_data['name'].lower().replace(' ', '-')}-{city_data['state'].lower()}"

            city, created = City.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': city_data['name'],
                    'state': city_data['state'],
                    'state_name': city_data['state_name'],
                    'latitude': Decimal(city_data['lat']),
                    'longitude': Decimal(city_data['lng']),
                    'population': city_data['population'],
                }
            )

            if created:
                count += 1
                self.stdout.write(f"✓ Created: {city}")
            else:
                skipped += 1
                self.stdout.write(f"⟳ Updated: {city}")

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully processed {count + skipped} cities '
                f'({count} created, {skipped} updated)'
            )
        )
