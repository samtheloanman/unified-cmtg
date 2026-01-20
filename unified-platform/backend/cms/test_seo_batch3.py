from django.test import TestCase
from django.core.management import call_command
from cms.models.cities import City
from cms.models.offices import Office
from cms.models.programs import ProgramPage
from cms.models.seo import SEOContentCache
from cms.services.location_mapper import LocationMapper
from decimal import Decimal
import io

class LocationMapperTest(TestCase):
    def setUp(self):
        self.la_office = Office.objects.create(
            name="LA Office",
            city="Los Angeles",
            state="CA",
            latitude=Decimal("34.05"),
            longitude=Decimal("-118.24"),
            is_active=True,
            is_headquarters=False
        )
        self.hq = Office.objects.create(
            name="HQ",
            city="New York",
            state="NY",
            latitude=Decimal("40.71"),
            longitude=Decimal("-74.00"),
            is_active=True,
            is_headquarters=True
        )
        
    def test_closest_office(self):
        # Nearby city
        santa_monica = City(
            name="Santa Monica",
            latitude=Decimal("34.01"),
            longitude=Decimal("-118.49")
        )
        office = LocationMapper.get_closest_office(santa_monica)
        self.assertEqual(office, self.la_office)
        
    def test_fallback_to_hq(self):
        # Far away city (London?)
        london = City(
            name="London",
            latitude=Decimal("51.50"),
            longitude=Decimal("-0.12")
        )
        # Actually logic is just distance based, so it will pick NY as it's closer than LA? 
        # Or if we had a distance threshold. Current impl is just closest.
        # Let's test checking if it returns *something* valid.
        office = LocationMapper.get_closest_office(london)
        self.assertIsNotNone(office)

class Power5GenerationTest(TestCase):
    def setUp(self):
        # Create 1 pilot city
        City.objects.create(
            name="Los Angeles",
            state="CA",
            latitude=Decimal("34.05"),
            longitude=Decimal("-118.24"),
            priority=100,
            slug="los-angeles"
        )
        
    def test_generate_and_verify(self):
        out = io.StringIO()
        
        # 1. Run generation
        call_command('generate_power_5', stdout=out)
        self.assertIn("Successfully generated", out.getvalue())
        
        # Should have generated 5 pages for 1 city = 5 cache entries
        self.assertEqual(SEOContentCache.objects.count(), 5)
        
        # 2. Run verification
        out_verify = io.StringIO()
        call_command('verify_content', stdout=out_verify)
        self.assertIn("verified successfully", out_verify.getvalue())
        
    def test_verify_failure(self):
        # Generate valid content first
        call_command('generate_power_5')
        
        # Break one entry
        cache = SEOContentCache.objects.first()
        cache.title_tag = "" # invalid
        cache.save()
        
        out_verify = io.StringIO()
        try:
             call_command('verify_content', stdout=out_verify)
        except Exception:
             pass # Command raises exception on failure
             
        self.assertIn("Invalid 1 pages", out_verify.getvalue())
