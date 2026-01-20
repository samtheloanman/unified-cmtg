from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from cms.models import ProgramPage, City, LocalProgramPage, Office
from cms.services.ai_content_generator import AiContentGenerator
from cms.services.proximity import ProximityService
from cms.services.schema_generator import SchemaGenerator
import time
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate localized program pages with AI content'

    def add_arguments(self, parser):
        parser.add_argument(
            '--programs', 
            nargs='+', 
            help='List of program slugs or "all"'
        )
        parser.add_argument(
            '--cities', 
            nargs='+', 
            help='List of city slugs or "top-N" (e.g. top-10)'
        )
        parser.add_argument(
            '--use-openai', 
            action='store_true', 
            help='Use OpenAI instead of Gemini'
        )
        parser.add_argument(
            '--batch-size', 
            type=int, 
            default=5, 
            help='Number of pages to generate before sleeping'
        )
        parser.add_argument(
            '--dry-run', 
            action='store_true', 
            help='Do not save pages'
        )

    def handle(self, *args, **options):
        programs_arg = options['programs']
        cities_arg = options['cities']
        use_openai = options['use_openai']
        batch_size = options['batch_size']
        dry_run = options['dry_run']

        # 1. Resolve Programs
        if not programs_arg or 'all' in programs_arg:
            programs = ProgramPage.objects.live()
        else:
            programs = ProgramPage.objects.filter(slug__in=programs_arg)

        if not programs.exists():
            self.stdout.write(self.style.ERROR("No programs found."))
            return

        # 2. Resolve Cities
        if not cities_arg:
             self.stdout.write(self.style.ERROR("Please specify --cities."))
             return
             
        if any(c.startswith('top-') for c in cities_arg):
             # Extract N from top-N
             limit_str = next(c for c in cities_arg if c.startswith('top-'))
             try:
                 limit = int(limit_str.split('-')[1])
                 # Sort by population desc
                 cities = City.objects.filter(population__isnull=False).order_by('-population')[:limit]
             except ValueError:
                 self.stdout.write(self.style.ERROR("Invalid top-N format. Use top-10, top-50 etc."))
                 return
        else:
            cities = City.objects.filter(slug__in=cities_arg)

        if not cities.exists():
            self.stdout.write(self.style.ERROR("No cities found."))
            return

        self.stdout.write(f"Targets: {programs.count()} Programs x {cities.count()} Cities")

        # Initialize AI Generator
        try:
            ai_generator = AiContentGenerator(use_openai=use_openai)
        except Exception as e:
             self.stdout.write(self.style.ERROR(f"Failed to init AI: {e}"))
             return

        count = 0
        
        # 3. Generate Pages
        for program in programs:
            for city in cities:
                if count > 0 and count % batch_size == 0:
                    self.stdout.write("Sleeping for rate limit...")
                    time.sleep(1)

                self.generate_page(program, city, ai_generator, dry_run)
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Completed! Processed {count} pages."))

    def generate_page(self, program, city, ai_generator, dry_run):
        # slug logic match model
        slug = f"{program.slug}-{city.slug}"
        
        self.stdout.write(f"Processing: {slug}...")

        # Check existing
        if LocalProgramPage.objects.filter(slug=slug).exists():
            self.stdout.write(self.style.WARNING(f"  Skipping: {slug} already exists"))
            return

        try:
            # 1. Proximity
            office = ProximityService.find_nearest_office(city)
            
            # 2. AI Content
            self.stdout.write("  Generating AI content...")
            intro = ai_generator.generate_local_intro(
                program.title, city.name, city.state
            )
            faqs = ai_generator.generate_local_faqs(
                program.title, city.name, city.state
            )
            
            # Format FAQs for StreamField
            faq_stream_data = []
            for faq in faqs:
                faq_stream_data.append({
                    'type': 'faq',
                    'value': {
                        'question': faq.get('question', ''),
                        'answer': faq.get('answer', '') # Simple text for now, could be RichText
                    }
                })

            # 3. Schema
            schema_json = SchemaGenerator.generate_local_schema(program, city, office)

            if dry_run:
                self.stdout.write(self.style.SUCCESS(f"  [DRY RUN] Would create page for {city.name}"))
                return

            # 4. Save Page
            # We need a parent page. Assuming program page is the parent or a flat structure?
            # Model says parent_page_types = ['cms.ProgramIndexPage'] for ProgramPage.
            # LocalProgramPage doesn't have specific parent types defined yet in correct file?
            # Let's assume LocalProgramPage is child of ProgramPage for URL structure or flat?
            # The model's get_url_parts tries to do flat structure.
            # Best practice: Add to ProgramPage as child, but use custom URL routing.
            
            # Let's use ProgramPage as parent
            page = LocalProgramPage(
                title=f"{program.title} in {city.name}, {city.state}",
                slug=slug,
                program=program,
                city=city,
                assigned_office=office,
                local_intro=intro,
                local_faqs=faq_stream_data, # Wagtail might need JSON string or native list depending on usage
                schema_markup=json.loads(schema_json) if schema_json else None
            )
            
            program.add_child(instance=page)
            page.save_revision().publish()
            
            self.stdout.write(self.style.SUCCESS(f"  Created: {page.url}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Failed: {e}"))
            logger.exception("Error generating page")
