import logging
from django.core.management.base import BaseCommand
from wagtail.models import Page
from cms.models.navigation import NavigationMenu
from cms.models.programs import ProgramPage
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Populates the Main Header navigation menu with program categories'

    def handle(self, *args, **options):
        self.stdout.write("Populating Main Header navigation...")

        # Get or create the menu
        menu, created = NavigationMenu.objects.get_or_create(
            name="main-header"
        )
        
        # Clear existing items to rebuild
        # Note: In a real prod scenario we might want to update, but for MVP rebuild is safer
        menu.items = [] 

        # Define category mapping and ordering
        categories = [
            {
                'title': 'Residential',
                'program_type': 'residential',
                'icon': 'home'
            },
            {
                'title': 'Non-QM / Self-Employed',
                'program_type': 'nonqm',
                'icon': 'briefcase' 
            },
            {
                'title': 'Commercial',
                'program_type': 'commercial',
                'icon': 'building'
            },
            {
                'title': 'Hard Money & Bridge',
                'program_type': 'hard_money',
                'icon': 'money'
            },
            {
                'title': 'Reverse Mortgage',
                'program_type': 'reverse_mortgage',
                'icon': 'refresh'
            }
        ]

        stream_data = []

        # 1. Add "Home" link
        stream_data.append({
            'type': 'link',
            'value': {
                'link_text': 'Home',
                'link_url': '/',
                'open_in_new_tab': False
            }
        })

        # 2. Build Sub-Menus for each category
        for cat in categories:
            programs = ProgramPage.objects.filter(
                program_type=cat['program_type'],
                live=True
            ).order_by('title')

            if programs.exists():
                link_items = []
                for prog in programs:
                    # Wagtail StreamField expects a Page object for link_page if using PageChooserBlock
                    # But our LinkBlock definition uses PageChooserBlock.
                    # Let's check LinkBlock definition in models/navigation.py
                    # link_page = blocks.PageChooserBlock(required=False)
                    # So we should pass the page PK or the page object depending on how we construct the StreamValue.
                    # When constructing JSON for StreamField, we usually pass the ID for PageChooser.
                    
                    link_items.append({
                        'link_text': prog.title,
                        'link_url': f'/programs/{prog.slug}', # Generating static URL to be safe/faster for now
                        # 'link_page': prog.pk, # Could use this if we want strict linking
                        'open_in_new_tab': False
                    })
                
                # Add "View All" link at bottom
                link_items.append({
                    'link_text': f'View All {cat["title"]}',
                    'link_url': '/programs',
                    'open_in_new_tab': False
                })

                stream_data.append({
                    'type': 'sub_menu',
                    'value': {
                        'title': cat['title'],
                        'items': link_items
                    }
                })

        # 3. Add "Get Quote" link (if not handled by header hardcode)
        # Header.tsx has a hardcoded button, but let's add a "Programs" index link just in case
        stream_data.append({
            'type': 'link',
            'value': {
                'link_text': 'All Programs',
                'link_url': '/programs',
                'open_in_new_tab': False
            }
        })

        menu.items = stream_data
        menu.save()
        self.stdout.write(self.style.SUCCESS(f"Successfully populated 'main-header' with {len(stream_data)} items."))

        # 4. Populate Footer Menu
        self.stdout.write("Populating Footer navigation...")
        footer_menu, _ = NavigationMenu.objects.get_or_create(name="Footer")
        footer_data = [
            {'type': 'link', 'value': {'link_text': 'Home', 'link_url': '/', 'open_in_new_tab': False}},
            {'type': 'link', 'value': {'link_text': 'All Programs', 'link_url': '/programs', 'open_in_new_tab': False}},
            {'type': 'link', 'value': {'link_text': 'Privacy Policy', 'link_url': '/privacy-policy', 'open_in_new_tab': False}},
            {'type': 'link', 'value': {'link_text': 'Terms of Service', 'link_url': '/terms-of-service', 'open_in_new_tab': False}},
        ]
        footer_menu.items = footer_data
        footer_menu.save()
        self.stdout.write(self.style.SUCCESS("Successfully populated 'Footer' menu."))
