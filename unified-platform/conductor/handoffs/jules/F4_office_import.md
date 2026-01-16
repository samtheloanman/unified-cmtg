# Jules Prompt: Phase F.4 - Location & Office Data Import

**Track**: `finalization_20260114`  
**Phase**: F.4  
**Priority**: HIGH  
**Estimated Time**: 2-3 hours  
**Can Run Parallel With**: F.2, F.3

---

## MISSION

Create Office model with GPS coordinates and import 200+ physical office locations for proximity-based programmatic SEO.

## CONTEXT

- Offices are used for city-to-office mapping in LocalProgramPage (F.5)
- Each city page will show nearest office contact info
- Haversine formula requires GPS coordinates (latitude, longitude)
- Fallback: If city > 500 miles from nearest office, assign Encino HQ

## REFERENCE FILES

- PRD: `prd.md` Section 5.3 (Location Assignment Logic)
- Implementation Plan: See F.4 section

## TASKS

### 1. Create Office Model

**File**: `backend/cms/models/offices.py`

```python
from django.db import models

class Office(models.Model):
    """
    Physical CMRE office location for SEO proximity mapping.
    
    Each LocalProgramPage is assigned to the nearest office
    using Haversine distance formula.
    """
    
    # Basic info
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zipcode = models.CharField(max_length=10)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    # GPS coordinates for Haversine distance calculation
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        help_text="GPS latitude for proximity calculations"
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        help_text="GPS longitude for proximity calculations"
    )
    
    # Flags
    is_active = models.BooleanField(default=True)
    is_headquarters = models.BooleanField(
        default=False,
        help_text="Fallback office if city > 500 miles from nearest"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['state', 'city']
        verbose_name = "Office"
        verbose_name_plural = "Offices"
    
    def __str__(self):
        return f"{self.name} - {self.city}, {self.state}"
    
    @property
    def full_address(self):
        return f"{self.address}, {self.city}, {self.state} {self.zipcode}"


class OfficeManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)
    
    def headquarters(self):
        return self.get(is_headquarters=True)
```

### 2. Update cms/models/__init__.py

```python
from .offices import Office
```

### 3. Create Import Command

**File**: `backend/cms/management/commands/import_offices.py`

```python
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
```

### 4. Register in Wagtail Admin

**File**: `backend/cms/wagtail_hooks.py`

```python
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from .models import Office

@modeladmin_register
class OfficeAdmin(ModelAdmin):
    model = Office
    menu_label = 'Offices'
    menu_icon = 'site'
    menu_order = 200
    add_to_settings_menu = False
    list_display = ('name', 'city', 'state', 'phone', 'is_headquarters', 'is_active')
    list_filter = ('state', 'is_active', 'is_headquarters')
    search_fields = ('name', 'city', 'address')
```

### 5. Run Migrations

```bash
python manage.py makemigrations cms
python manage.py migrate
```

### 6. Import Sample Offices (or from CSV)

```bash
# Create sample offices for testing
python manage.py import_offices

# Or import from CSV if available
python manage.py import_offices --csv path/to/offices.csv
```

### 7. Verify

```bash
python manage.py shell
>>> from cms.models import Office
>>> Office.objects.count()
>>> Office.objects.get(is_headquarters=True)
>>> Office.objects.filter(state='CA')
```

## SUCCESS CRITERIA

- [ ] Office model created with GPS fields
- [ ] Migrations run without errors
- [ ] import_offices command works
- [ ] HQ office flagged: `is_headquarters=True`
- [ ] `Office.objects.count()` returns expected count
- [ ] Offices visible in Wagtail admin under "Offices"

## HANDOFF

After completion, write to `conductor/handoffs/gemini/inbox.md`:
```
F.4 Complete: Office model created with GPS coordinates.
Imported [X] offices. HQ flagged (Encino, CA).
Ready for F.5 (Programmatic SEO Infrastructure).
```

Commit: `git commit -m "feat(cms): F.4 Office model with GPS for proximity mapping"`
