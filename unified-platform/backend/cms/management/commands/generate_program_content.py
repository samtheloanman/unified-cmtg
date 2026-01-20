from django.core.management.base import BaseCommand
from cms.models import ProgramPage
from cms.services.ai_content_generator import AiContentGenerator
import time
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate full content for Program Pages using AI'

    def add_arguments(self, parser):
        parser.add_argument(
            '--programs', 
            nargs='+', 
            help='List of program slugs or "all"'
        )
        parser.add_argument(
            '--force', 
            action='store_true', 
            help='Overwrite existing content'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Limit number of pages to process'
        )

    def handle(self, *args, **options):
        programs_arg = options['programs']
        force = options['force']
        limit = options['limit']

        # Resolve Programs
        if not programs_arg or 'all' in programs_arg:
            programs = ProgramPage.objects.live()
        else:
            programs = ProgramPage.objects.filter(slug__in=programs_arg)

        if not programs.exists():
            self.stdout.write(self.style.ERROR("No programs found."))
            return

        self.stdout.write(f"Targets: {programs.count()} Programs")

        # Init AI
        try:
            generator = AiContentGenerator()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to init AI: {e}"))
            return

        count = 0
        for page in programs:
            if limit > 0 and count >= limit:
                break
                
            # Skip if has content and not forced
            # Check if 'what_are' is populated and not just placeholder
            if not force and page.what_are and "Coming soon" not in str(page.what_are):
                self.stdout.write(f"Skipping {page.slug} (already has content)")
                continue

            self.stdout.write(f"Generating content for: {page.title} ({page.slug})...")
            
            try:
                content = generator.generate_program_content(page.title, page.program_type)
                
                # Map fields
                page.mortgage_program_highlights = content.get('mortgage_program_highlights', '')
                page.what_are = content.get('what_are', '')
                page.details_about_mortgage_loan_program = content.get('details_about_mortgage_loan_program', '')
                page.benefits_of = content.get('benefits_of', '')
                page.requirements = content.get('requirements', '')
                page.how_to_qualify_for = content.get('how_to_qualify_for', '')
                page.why_us = content.get('why_us', '')
                page.seo_title = content.get('seo_title', page.title)
                page.search_description = content.get('seo_description', '')
                
                # FAQs
                raw_faqs = content.get('faqs', [])
                formatted_faqs = []
                for item in raw_faqs:
                    formatted_faqs.append({
                        'type': 'faq_item', # Matches model block name
                        'value': {
                            'question': item.get('question', ''),
                            'answer': item.get('answer', '')
                        }
                    })
                page.faq = formatted_faqs
                
                page.save_revision().publish()
                self.stdout.write(self.style.SUCCESS(f"  Updated {page.slug}"))
                count += 1
                
                # Rate limit
                time.sleep(2)
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Failed: {e}"))
                logger.exception("Error generating program content")

        self.stdout.write(self.style.SUCCESS(f"Finished. Processed {count} pages."))
