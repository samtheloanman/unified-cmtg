# Jules Prompt: Phase F.5 - Programmatic SEO Infrastructure

**Track**: `finalization_20260114`  
**Phase**: F.5  
**Priority**: CRITICAL  
**Estimated Time**: 6-8 hours  
**Dependencies**: F.4 (Office model must exist)

---

## MISSION

Build infrastructure for generating 10,000+ city-specific program pages with flat URL hierarchy and proximity-based office assignment.

## CONTEXT

- This is the foundation for programmatic SEO strategy
- Each city × program combination gets a unique page
- URL format: `/dscr-loan-los-angeles-ca/` (flat, not nested)
- Each page assigned to nearest office via Haversine formula
- F.6 will use this infrastructure to generate content with AI

## REFERENCE FILES

- PRD: `prd.md` Section 5.3 (Programmatic SEO Architecture)
- Office model: Created in F.4
- Implementation plan: See F.5 section

## TASKS

### 1. Create City Model

**File**: `backend/cms/models/cities.py`

```python
from django.db import models
from django.utils.text import slugify

class City(models.Model):
    """
    US city for programmatic SEO local pages.
    
    Each city can be combined with multiple programs to create
    LocalProgramPage instances (e.g., /dscr-loan-denver-co/).
    """
    
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=2, help_text="Two-letter state code")
    state_name = models.CharField(max_length=100)
    
    # GPS coordinates for proximity calculations
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    # Demographics (optional, for AI content personalization)
    population = models.IntegerField(null=True, blank=True)
    median_income = models.IntegerField(null=True, blank=True)
    median_home_price = models.IntegerField(null=True, blank=True)
    
    # SEO
    slug = models.SlugField(unique=True, max_length=150)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['state', 'name']
        verbose_name = "City"
        verbose_name_plural = "Cities"
        unique_together = [['name', 'state']]
    
    def __str__(self):
        return f"{self.name}, {self.state}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.state}")
        super().save(*args, **kwargs)
```

### 2. Create LocalProgramPage Model

**File**: `backend/cms/models/local_pages.py`

```python
from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail import blocks

class LocalProgramPage(Page):
    """
    Programmatic SEO page combining program + city.
    
    URL format: /program-slug-city-state/
    Example: /dscr-loan-los-angeles-ca/
    
    Content is AI-generated and unique per combination.
    """
    
    # Links to existing models
    program = models.ForeignKey(
        'cms.ProgramPage',
        on_delete=models.CASCADE,
        related_name='local_pages'
    )
    city = models.ForeignKey(
        'cms.City',
        on_delete=models.CASCADE,
        related_name='local_pages'
    )
    assigned_office = models.ForeignKey(
        'cms.Office',
        on_delete=models.SET_NULL,
        null=True,
        help_text="Nearest office to this city"
    )
    
    # AI-generated localized content
    local_intro = models.TextField(
        blank=True,
        help_text="AI-generated 200-word introduction mentioning local context"
    )
    
    local_faqs = StreamField([
        ('faq', blocks.StructBlock([
            ('question', blocks.CharBlock(max_length=200)),
            ('answer', blocks.RichTextBlock()),
        ], icon='help'))
    ], blank=True, use_json_field=True)
    
    # Metadata
    content_generated_at = models.DateTimeField(null=True, blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('program'),
        FieldPanel('city'),
        FieldPanel('assigned_office'),
        FieldPanel('local_intro'),
        FieldPanel('local_faqs'),
    ]
    
    api_fields = [
        APIField('program'),
        APIField('city'),
        APIField('assigned_office'),
        APIField('local_intro'),
        APIField('local_faqs'),
    ]
    
    class Meta:
        unique_together = [['program', 'city']]
        verbose_name = "Local Program Page"
    
    def get_url_parts(self, request=None):
        """
        Override URL to create flat structure.
        
        Returns: /program-slug-city-state/
        Example: /dscr-loan-los-angeles-ca/
        """
        site_id, root_url, _ = super().get_url_parts(request)
        
        # Build flat URL
        url_path = f"/{self.program.slug}-{self.city.slug}/"
        
        return (site_id, root_url, url_path)
    
    def save(self, *args, **kwargs):
        # Auto-generate title
        if not self.title:
            self.title = f"{self.program.title} in {self.city.name}, {self.city.state}"
        
        # Auto-generate slug for flat URL
        if not self.slug:
            self.slug = f"{self.program.slug}-{self.city.slug}"
        
        super().save(*args, **kwargs)
```

### 3. Create Proximity Service

**File**: `backend/cms/services/proximity.py`

```python
from math import radians, sin, cos, sqrt, asin
from cms.models import Office, City

class ProximityService:
    """
    Calculate distances between cities and offices using Haversine formula.
    
    Used to assign each LocalProgramPage to the nearest physical office.
    """
    
    EARTH_RADIUS_MILES = 3959
    MAX_DISTANCE_MILES = 500  # Fallback to HQ if > 500 miles
    
    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        """
        Calculate great-circle distance between two points on Earth.
        
        Formula from PRD Section 5.3:
        d = 2r × arcsin(√[sin²(Δφ/2) + cosφ₁ × cosφ₂ × sin²(Δλ/2)])
        
        Args:
            lat1, lon1: First point (degrees)
            lat2, lon2: Second point (degrees)
        
        Returns:
            Distance in miles
        """
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        distance = ProximityService.EARTH_RADIUS_MILES * c
        return distance
    
    @classmethod
    def find_nearest_office(cls, city: City) -> Office:
        """
        Find nearest active office to a city.
        
        Rules (from PRD):
        1. Calculate distance to all active offices
        2. Return nearest office
        3. If nearest > 500 miles, return HQ (Encino, CA)
        
        Args:
            city: City instance
        
        Returns:
            Nearest Office instance
        """
        offices = Office.objects.filter(is_active=True)
        hq = Office.objects.get(is_headquarters=True)
        
        nearest_office = None
        min_distance = float('inf')
        
        for office in offices:
            distance = cls.haversine_distance(
                float(city.latitude),
                float(city.longitude),
                float(office.latitude),
                float(office.longitude)
            )
            
            if distance < min_distance:
                min_distance = distance
                nearest_office = office
        
        # Fallback rule: if > 500 miles, use HQ
        if min_distance > cls.MAX_DISTANCE_MILES:
            return hq
        
        return nearest_office if nearest_office else hq
    
    @classmethod
    def get_distance_to_office(cls, city: City, office: Office) -> float:
        """Get distance in miles between city and office."""
        return cls.haversine_distance(
            float(city.latitude),
            float(city.longitude),
            float(office.latitude),
            float(office.longitude)
        )
```

### 4. Create Schema Markup Generator

**File**: `backend/cms/services/schema_generator.py`

```python
import json
from cms.models import LocalProgramPage

class SchemaGenerator:
    """
    Generate JSON-LD schema markup for SEO.
    
    Per PRD Section 5.3: Dual schema (MortgageLoan + LocalBusiness)
    """
    
    @staticmethod
    def generate_local_page_schema(page: LocalProgramPage) -> str:
        """
        Generate dual schema for LocalProgramPage.
        
        Returns JSON-LD string for injection in <head>
        """
        schema = {
            "@context": "https://schema.org",
            "@graph": [
                # MortgageLoan schema
                {
                    "@type": "MortgageLoan",
                    "name": page.program.title,
                    "loanType": page.program.program_type,
                    "amount": {
                        "@type": "MonetaryAmount",
                        "minValue": float(page.program.min_loan_amount),
                        "maxValue": float(page.program.max_loan_amount),
                        "currency": "USD"
                    },
                    "interestRate": {
                        "@type": "QuantitativeValue",
                        "minValue": page.program.interest_rate_min,
                        "maxValue": page.program.interest_rate_max,
                        "unitText": "PERCENT"
                    } if page.program.interest_rate_min else None,
                },
                # LocalBusiness schema
                {
                    "@type": "LocalBusiness",
                    "name": f"Custom Mortgage Inc - {page.city.name}",
                    "address": {
                        "@type": "PostalAddress",
                        "streetAddress": page.assigned_office.address,
                        "addressLocality": page.assigned_office.city,
                        "addressRegion": page.assigned_office.state,
                        "postalCode": page.assigned_office.zipcode,
                        "addressCountry": "US"
                    },
                    "geo": {
                        "@type": "GeoCoordinates",
                        "latitude": float(page.assigned_office.latitude),
                        "longitude": float(page.assigned_office.longitude)
                    },
                    "telephone": page.assigned_office.phone,
                    "url": f"https://cmre.c-mtg.com{page.url}"
                }
            ]
        }
        
        # Remove None values
        schema["@graph"] = [
            {k: v for k, v in item.items() if v is not None}
            for item in schema["@graph"]
        ]
        
        return json.dumps(schema, indent=2)
```

### 5. Create City Import Command

**File**: `backend/cms/management/commands/import_cities.py`

```python
from django.core.management.base import BaseCommand
import csv
from pathlib import Path
from cms.models import City

class Command(BaseCommand):
    help = 'Import cities from CSV'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            help='Path to cities CSV file (SimpleMaps format)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=150,
            help='Number of cities to import (top N by population)'
        )
    
    def handle(self, *args, **options):
        csv_path = options.get('csv')
        limit = options['limit']
        
        if csv_path:
            self.import_from_csv(csv_path, limit)
        else:
            self.create_sample_cities()
    
    def import_from_csv(self, csv_path: str, limit: int):
        """Import cities from SimpleMaps CSV."""
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            cities = list(reader)
        
        # Sort by population, take top N
        cities.sort(key=lambda x: int(x.get('population', 0) or 0), reverse=True)
        cities = cities[:limit]
        
        count = 0
        for row in cities:
            city, created = City.objects.update_or_create(
                name=row['city'],
                state=row['state_id'],
                defaults={
                    'state_name': row['state_name'],
                    'latitude': float(row['lat']),
                    'longitude': float(row['lng']),
                    'population': int(row.get('population', 0) or 0),
                }
            )
            
            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action}: {city}"))
            count += 1
        
        self.stdout.write(f"\nImported {count} cities")
    
    def create_sample_cities(self):
        """Create sample cities for testing."""
        cities = [
            {'name': 'Los Angeles', 'state': 'CA', 'state_name': 'California', 'lat': 34.0522, 'lng': -118.2437, 'pop': 3979576},
            {'name': 'San Diego', 'state': 'CA', 'state_name': 'California', 'lat': 32.7157, 'lng': -117.1611, 'pop': 1423851},
            {'name': 'San Jose', 'state': 'CA', 'state_name': 'California', 'lat': 37.3382, 'lng': -121.8863, 'pop': 1021795},
            {'name': 'Denver', 'state': 'CO', 'state_name': 'Colorado', 'lat': 39.7392, 'lng': -104.9903, 'pop': 727211},
            {'name': 'Phoenix', 'state': 'AZ', 'state_name': 'Arizona', 'lat': 33.4484, 'lng': -112.0740, 'pop': 1680992},
            {'name': 'Houston', 'state': 'TX', 'state_name': 'Texas', 'lat': 29.7604, 'lng': -95.3698, 'pop': 2320268},
            {'name': 'Dallas', 'state': 'TX', 'state_name': 'Texas', 'lat': 32.7767, 'lng': -96.7970, 'pop': 1343573},
            {'name': 'Austin', 'state': 'TX', 'state_name': 'Texas', 'lat': 30.2672, 'lng': -97.7431, 'pop': 978908},
        ]
        
        for city_data in cities:
            city, created = City.objects.update_or_create(
                name=city_data['name'],
                state=city_data['state'],
                defaults={
                    'state_name': city_data['state_name'],
                    'latitude': city_data['lat'],
                    'longitude': city_data['lng'],
                    'population': city_data['pop'],
                }
            )
            self.stdout.write(self.style.SUCCESS(f"Created: {city}"))
```

### 6. Update cms/models/__init__.py

```python
from .cities import City
from .local_pages import LocalProgramPage
```

### 7. Run Migrations

```bash
python manage.py makemigrations cms
python manage.py migrate
```

### 8. Import Cities

```bash
# Create sample cities for testing
python manage.py import_cities

# Or import from SimpleMaps CSV (if available)
# Download from: https://simplemaps.com/data/us-cities
python manage.py import_cities --csv path/to/uscities.csv --limit 150
```

### 9. Test Proximity Service

```bash
python manage.py shell
>>> from cms.models import City, Office
>>> from cms.services.proximity import ProximityService
>>> 
>>> # Test Haversine
>>> city = City.objects.get(name='Denver')
>>> office = ProximityService.find_nearest_office(city)
>>> print(f"Nearest office to Denver: {office}")
>>> 
>>> # Test distance calculation
>>> distance = ProximityService.get_distance_to_office(city, office)
>>> print(f"Distance: {distance:.2f} miles")
```

### 10. Create Test LocalProgramPage

```bash
python manage.py shell
>>> from cms.models import ProgramPage, City, LocalProgramPage
>>> from cms.services.proximity import ProximityService
>>> from wagtail.models import Page
>>> 
>>> # Get program and city
>>> program = ProgramPage.objects.first()
>>> city = City.objects.get(name='Denver')
>>> 
>>> # Find nearest office
>>> office = ProximityService.find_nearest_office(city)
>>> 
>>> # Create local page
>>> home = Page.objects.get(slug='home')
>>> local_page = LocalProgramPage(
...     program=program,
...     city=city,
...     assigned_office=office,
...     local_intro="Test intro for Denver DSCR loan page"
... )
>>> home.add_child(instance=local_page)
>>> 
>>> # Check URL
>>> print(local_page.url)  # Should be: /dscr-loan-denver-co/
```

## SUCCESS CRITERIA

- [ ] City model created and migrated
- [ ] LocalProgramPage model created with flat URL override
- [ ] ProximityService calculates distances correctly
- [ ] Schema generator produces valid JSON-LD
- [ ] 150+ cities imported
- [ ] Test LocalProgramPage created manually
- [ ] URL format verified: `/program-city-state/`
- [ ] Proximity assignment works (nearest office)

## HANDOFF

After completion, write to `conductor/handoffs/gemini/inbox.md`:
```
F.5 Complete: Programmatic SEO infrastructure ready.
- City model: [X] cities imported
- LocalProgramPage model with flat URLs
- ProximityService: Haversine formula working
- Schema generator: Dual schema (MortgageLoan + LocalBusiness)
- Test page created: [URL]
Ready for F.6 (AI Content Generation).
```

Commit: `git commit -m "feat(cms): F.5 Programmatic SEO infrastructure with proximity mapping"`
