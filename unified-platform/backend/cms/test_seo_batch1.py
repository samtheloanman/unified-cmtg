from django.test import TestCase
from cms.models.cities import City
from cms.models.seo import SEOContentCache
from cms.services.proximity import ProximityService
from decimal import Decimal

class CityModelTest(TestCase):
    def test_phased_rollout_fields(self):
        city = City.objects.create(
            name="Test City",
            state="TC",
            state_name="Test Country",
            latitude=Decimal("10.0"),
            longitude=Decimal("10.0"),
            slug="test-city",
            priority=10,
            launched_at="2024-01-01 00:00:00+00:00"
        )
        self.assertEqual(city.priority, 10)
        self.assertIsNotNone(city.launched_at)
        self.assertEqual(str(city), "Test City, TC")

class SEOContentCacheTest(TestCase):
    def test_cache_creation(self):
        cache = SEOContentCache.objects.create(
            url_path="/test-path",
            title_tag="Test Title",
            meta_description="Test Description",
            h1_header="Test Header",
            content_body="<p>Test Content</p>",
            generation_params={"model": "claude-3-opus"}
        )
        self.assertEqual(str(cache), f"Cache for /test-path ({cache.last_updated.strftime('%Y-%m-%d')})")
        
    def test_unique_url_path(self):
        SEOContentCache.objects.create(
            url_path="/unique-path",
            title_tag="A", meta_description="B", h1_header="C", content_body="D"
        )
        with self.assertRaises(Exception):
            SEOContentCache.objects.create(
                url_path="/unique-path",
                title_tag="A", meta_description="B", h1_header="C", content_body="D"
            )

class ProximityServiceTest(TestCase):
    def setUp(self):
        self.city1 = City.objects.create(
            name="City 1", state="S1", state_name="State 1", slug="c1",
            latitude=Decimal("34.0522"), longitude=Decimal("-118.2437") # Los Angeles
        )
        self.city2 = City.objects.create(
            name="City 2", state="S2", state_name="State 2", slug="c2",
            latitude=Decimal("36.1699"), longitude=Decimal("-115.1398") # Las Vegas (~220 miles)
        )
        self.city3 = City.objects.create(
            name="City 3", state="S3", state_name="State 3", slug="c3",
            latitude=Decimal("40.7128"), longitude=Decimal("-74.0060") # New York (~2400 miles)
        )

    def test_get_nearest_cities(self):
        # Test from near LA
        target_lat = 34.0000
        target_lon = -118.0000
        
        nearest = ProximityService.get_nearest_cities(target_lat, target_lon, limit=2)
        
        self.assertEqual(len(nearest), 2)
        self.assertEqual(nearest[0], self.city1)
        self.assertEqual(nearest[1], self.city2)
        
    def test_haversine_distance(self):
        dist = ProximityService.haversine_distance(34.0522, -118.2437, 36.1699, -115.1398)
        # Distance LA to Vegas is roughly 220-230 miles direct
        self.assertTrue(200 < dist < 300)
