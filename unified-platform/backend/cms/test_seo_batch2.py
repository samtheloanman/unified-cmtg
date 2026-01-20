from django.test import TestCase
from django.core.management import call_command
from cms.models.programs import ProgramPage
from cms.models.cities import City
from cms.services.schema_generator import SchemaGenerator
from cms.services.seo_resolver import SEOResolver
from wagtail.models import Page
from decimal import Decimal
import io

class SchemaGeneratorTest(TestCase):
    def setUp(self):
        root = Page.get_first_root_node()
        self.program = ProgramPage(
            title="Jumbo Loans",
            slug="jumbo-loans",
            minimum_loan_amount=750000,
            maximum_loan_amount=3000000,
            interest_rates="5.5-7.0%"
        )
        root.add_child(instance=self.program)

    def test_schema_generation(self):
        schemas = SchemaGenerator.generate_loan_product_schema(self.program)
        product = schemas[0]
        
        self.assertEqual(product['@type'], 'FinancialProduct')
        self.assertEqual(product['name'], 'Jumbo Loans')
        self.assertEqual(product['amount']['minValue'], 750000.0)
        self.assertEqual(product['amount']['maxValue'], 3000000.0)

class SEOResolverTest(TestCase):
    def setUp(self):
        root = Page.get_first_root_node()
        self.program = ProgramPage(title="Jumbo Loans", slug="jumbo-loans")
        root.add_child(instance=self.program)
        
        self.city = City.objects.create(
            name="Los Angeles", state="CA", state_name="California",
            slug="los-angeles", latitude=Decimal("34.0"), longitude=Decimal("-118.0")
        )

    def test_resolve_valid_path(self):
        # /jumbo-loans/in-los-angeles-ca/
        path = "/jumbo-loans/in-los-angeles-ca/"
        prog, city, state = SEOResolver.resolve_path(path)
        
        self.assertEqual(prog, "jumbo-loans")
        self.assertEqual(city, "los-angeles")
        self.assertEqual(state, "CA")

    def test_resolve_invalid_path(self):
        path = "/invalid-program/in-mars-xx/"
        prog, city, state = SEOResolver.resolve_path(path)
        self.assertIsNone(prog)

class ImportCommandTest(TestCase):
    def test_import_pilot_cities(self):
        out = io.StringIO()
        call_command('import_pilot_cities', stdout=out)
        
        la = City.objects.get(slug='los-angeles')
        self.assertEqual(la.state, 'CA')
        self.assertEqual(la.priority, 100)
        self.assertIn("Successfully imported 5 pilot cities", out.getvalue())
