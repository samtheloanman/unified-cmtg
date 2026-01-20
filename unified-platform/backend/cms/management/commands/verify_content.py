from django.core.management.base import BaseCommand
from cms.models.seo import SEOContentCache
from cms.models.programs import ProgramPage
from cms.models.cities import City
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Verifies content integrity for Power 5 Pilot'

    def handle(self, *args, **kwargs):
        programs = ProgramPage.objects.all()
        cities = City.objects.filter(priority=100)
        
        missing = []
        invalid = []
        checked = 0
        
        if not programs.exists() or not cities.exists():
             self.stdout.write(self.style.ERROR("Programs or Pilot Cities missing. Cannot verify."))
             return

        for program in programs:
            if program.slug not in ['jumbo-loans', 'conventional-loans', 'fha-loans', 'va-loans', 'dscr-loans']:
                continue
                
            for city in cities:
                city_part = slugify(f"{city.name}-{city.state}")
                path = f"/{program.slug}/in-{city_part}/"
                checked += 1
                
                try:
                    cache = SEOContentCache.objects.get(url_path=path)
                    
                    # Validation Checks
                    if not cache.title_tag:
                        invalid.append(f"{path} (Missing Title)")
                    if not cache.h1_header:
                        invalid.append(f"{path} (Missing H1)")
                    if not cache.schema_json:
                        invalid.append(f"{path} (Missing Schema)")
                        
                except SEOContentCache.DoesNotExist:
                    missing.append(path)
                    
        if missing:
            self.stdout.write(self.style.ERROR(f"Missing {len(missing)} pages:"))
            for p in missing:
                self.stdout.write(f"- {p}")
                
        if invalid:
            self.stdout.write(self.style.ERROR(f"Invalid {len(invalid)} pages:"))
            for p in invalid:
                self.stdout.write(f"- {p}")
                
        if not missing and not invalid:
            self.stdout.write(self.style.SUCCESS(f"All {checked} pages verified successfully!"))
        else:
            raise Exception("Verification Failed")
