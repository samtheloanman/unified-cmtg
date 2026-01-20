from django.core.management.base import BaseCommand
from cms.models.programs import ProgramPage
from cms.models.cities import City
from cms.models.seo import SEOContentCache
from cms.services.schema_generator import SchemaGenerator
from django.utils.text import slugify
from wagtail.models import Page
import json

class Command(BaseCommand):
    help = 'Generates 25 Perfect Pages for Power 5 Pilot'

    def handle(self, *args, **kwargs):
        # 1. Ensure Programs Exist
        programs_data = [
            ("Jumbo Loans", "jumbo-loans"),
            ("Conventional Loans", "conventional-loans"),
            ("FHA Loans", "fha-loans"),
            ("VA Loans", "va-loans"),
            ("DSCR Loans", "dscr-loans"),
        ]
        
        root = Page.get_first_root_node()
        program_pages = []
        
        for title, slug in programs_data:
            page = ProgramPage.objects.filter(slug=slug).first()
            if not page:
                page = ProgramPage(
                    title=title,
                    slug=slug,
                    minimum_loan_amount=100000,
                    maximum_loan_amount=2000000,
                    interest_rates="Call for Rates"
                )
                root.add_child(instance=page)
                self.stdout.write(f"Created Program: {title}")
            program_pages.append(page)
            
        # 2. Get Pilot Cities (Priority 100)
        cities = City.objects.filter(priority=100)
        if not cities.exists():
            self.stdout.write(self.style.WARNING("No pilot cities found. Run import_pilot_cities first."))
            return

        # 3. Generate SEO Cache Entries
        count = 0
        for program in program_pages:
            for city in cities:
                # Path: /{program-slug}/in-{city}-{state}/
                city_part = slugify(f"{city.name}-{city.state}")
                path = f"/{program.slug}/in-{city_part}/"
                
                title_tag = f"{program.title} in {city.name}, {city.state} | Custom Mortgage"
                h1_header = f"{program.title} in {city.name}"
                meta_desc = f"Find the best {program.title} rates and programs in {city.name}, {city.state}. Local experts ready to help."
                
                # Simple Content Template
                body = f"""
                <div class="program-location-content">
                    <h1>{h1_header}</h1>
                    <p>Looking for <strong>{program.title} in {city.name}</strong>? You've come to the right place.</p>
                    <p>Custom Mortgage offers competitive rates for {city.state_name} borrowers.</p>
                </div>
                """
                
                # Schema
                base_schema = SchemaGenerator.generate_loan_product_schema(program)[0]
                base_schema['areaServed'] = {
                    "@type": "City",
                    "name": city.name,
                    "address": {
                        "@type": "PostalAddress",
                        "addressRegion": city.state
                    }
                }
                
                SEOContentCache.objects.update_or_create(
                    url_path=path,
                    defaults={
                        'title_tag': title_tag,
                        'h1_header': h1_header,
                        'meta_description': meta_desc,
                        'content_body': body,
                        'schema_json': base_schema,
                        'generation_params': {'pilot': 'power_5'}
                    }
                )
                count += 1
                
        self.stdout.write(self.style.SUCCESS(f"Successfully generated {count} Power 5 pages."))
