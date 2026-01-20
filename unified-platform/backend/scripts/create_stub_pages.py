import os
import sys
import django

# Add the project root to sys.path
sys.path.append('/app')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from wagtail.models import Page
from cms.models import ProgramPage # Using ProgramPage as a generic stub container if needed

def create_stubs():
    home = Page.objects.get(slug='cmtg-home')
    
    stubs = [
        {'title': 'About Us', 'slug': 'about-us-cmre', 'body': '<h1>About Custom Mortgage</h1><p>We are a fintech real estate and finance agency providing precision lending solutions.</p>'},
        {'title': 'Contact Us', 'slug': 'contact-us', 'body': '<h1>Contact Us</h1><p>Call us at (877) 976-5669 or visit our headquarters.</p>'},
        {'title': 'Terms of Use', 'slug': 'terms-of-use', 'body': '<h1>Terms of Use</h1><p>Standard terms and conditions apply.</p>'},
        {'title': 'Careers', 'slug': 'careers', 'body': '<h1>Careers</h1><p>Join our team of mortgage experts.</p>'},
        {'title': 'Licensing', 'slug': 'disclosures-licenses', 'body': '<h1>Licensing</h1><p>Custom MTG Inc. NMLS # 1556995</p>'},
    ]

    for stub in stubs:
        if not Page.objects.filter(slug=stub['slug']).exists():
            print(f"Creating stub: {stub['title']}")
            # Using ProgramPage as a temporary container just to have the fields "body" or similar
            # Ideally we'd have a GenericPage, but let's see if we can use ProgramPage with minimal fields
            new_page = ProgramPage(
                title=stub['title'],
                slug=stub['slug'],
                mortgage_program_highlights=stub['body'], # Mapping body to a rich text field
                program_type='residential'
            )
            home.add_child(instance=new_page)
            new_page.save_revision().publish()
        else:
            print(f"Stub already exists: {stub['slug']}")

if __name__ == "__main__":
    create_stubs()
