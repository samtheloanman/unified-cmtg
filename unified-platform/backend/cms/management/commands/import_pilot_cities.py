from django.core.management.base import BaseCommand
from cms.models.cities import City
from decimal import Decimal
from django.utils.text import slugify
from django.utils import timezone

class Command(BaseCommand):
    help = 'Imports top 5 pilot cities with high priority'

    def handle(self, *args, **kwargs):
        pilot_cities = [
            # Name, State, Lat, Lon
            ("Los Angeles", "CA", "34.052235", "-118.243683"),
            ("San Francisco", "CA", "37.774929", "-122.419418"),
            ("San Diego", "CA", "32.715736", "-117.161087"),
            ("Miami", "FL", "25.761681", "-80.191788"),
            ("Austin", "TX", "30.267153", "-97.743057"),
        ]
        
        count = 0
        for name, state, lat, lon in pilot_cities:
            slug = slugify(f"{name}")
            city, created = City.objects.update_or_create(
                slug=slug,
                state=state,
                defaults={
                    'name': name,
                    'state_name': state, # Simplified for now
                    'latitude': Decimal(lat),
                    'longitude': Decimal(lon),
                    'priority': 100,
                    'launched_at': timezone.now()
                }
            )
            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action} {name}, {state}"))
            count += 1
            
        self.stdout.write(self.style.SUCCESS(f"Successfully imported {count} pilot cities"))
