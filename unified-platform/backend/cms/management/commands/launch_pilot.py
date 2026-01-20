from django.core.management.base import BaseCommand
from cms.models.cities import City
from django.utils import timezone

class Command(BaseCommand):
    help = 'Activates the Pilot Launch'

    def handle(self, *args, **kwargs):
        self.stdout.write("Initiating Pilot Launch Sequence...")
        
        # 1. Select Pilot Cities
        cities = City.objects.filter(priority=100)
        count = cities.count()
        
        if count == 0:
            self.stdout.write(self.style.ERROR("No pilot cities found (priority=100). Aborting."))
            return
            
        # 2. Set Launched At
        now = timezone.now()
        updated = cities.update(launched_at=now)
        
        self.stdout.write(self.style.SUCCESS(f"Successfully launched {updated} cities."))
        for city in cities:
            self.stdout.write(f"- {city.name} is LIVE")
