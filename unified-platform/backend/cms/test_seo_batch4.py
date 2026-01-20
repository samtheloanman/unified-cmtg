from django.test import TestCase, RequestFactory
from django.core.management import call_command
from cms.models.cities import City
from cms.models.programs import ProgramPage
from cms.models.seo import SEOContentCache
from cms.models.offices import Office
from cms.views.router_view import resolve_path
from decimal import Decimal
import io
import json

class RouterViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        
        # Setup Data
        self.program = ProgramPage(
            title="Jumbo Loans", slug="jumbo-loans"
        )
        # Hack to skip wagtail tree requirement for model access in view?
        # Ideally we add to tree.
        from wagtail.models import Page
        root = Page.get_first_root_node()
        root.add_child(instance=self.program)

        self.city = City.objects.create(
            name="Los Angeles", state="CA", state_name="California",
            slug="los-angeles", latitude=Decimal("34.05"), longitude=Decimal("-118.24")
        )
        
        self.office = Office.objects.create(
            name="LA Branch", city="Los Angeles", state="CA",
            latitude=Decimal("34.05"), longitude=Decimal("-118.24"),
            is_active=True
        )
        
        # Cache Entry
        self.path = "/jumbo-loans/in-los-angeles-ca/"
        SEOContentCache.objects.create(
            url_path=self.path,
            title_tag="Jumbo Loans in LA",
            h1_header="Jumbo Rates LA",
            meta_description="Best rates",
            content_body="<div>Content</div>",
            schema_json={"@type": "FinancialProduct"}
        )

    def test_resolve_path_success(self):
        request = self.factory.get('/api/v1/router/resolve/', {'path': self.path})
        response = resolve_path(request)
        
        self.assertEqual(response.status_code, 200)
        data = response.data
        
        self.assertEqual(data['type'], 'program_location')
        self.assertEqual(data['data']['program']['slug'], 'jumbo-loans')
        self.assertEqual(data['data']['location']['city'], 'Los Angeles')
        self.assertEqual(data['data']['location']['office']['name'], 'LA Branch')
        self.assertEqual(data['data']['h1'], "Jumbo Rates LA")

    def test_resolve_path_missing(self):
         request = self.factory.get('/api/v1/router/resolve/', {'path': '/invalid/path/'})
         response = resolve_path(request)
         self.assertEqual(response.status_code, 404)

class LaunchPilotTest(TestCase):
    def setUp(self):
        self.city1 = City.objects.create(
            name="C1", priority=100, slug="c1",
            latitude=Decimal("34.0"), longitude=Decimal("-118.0")
        )
        self.city2 = City.objects.create(
            name="C2", priority=50, slug="c2",
            latitude=Decimal("35.0"), longitude=Decimal("-119.0")
        )
        
    def test_launch_command(self):
        out = io.StringIO()
        call_command('launch_pilot', stdout=out)
        
        self.assertIn("Successfully launched 1 cities", out.getvalue())
        
        self.city1.refresh_from_db()
        self.city2.refresh_from_db()
        
        self.assertIsNotNone(self.city1.launched_at)
        self.assertIsNone(self.city2.launched_at)
