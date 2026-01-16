from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel

class LocalProgramPage(Page):
    """
    Programmatic SEO page: /fha-loan-los-angeles-ca/
    
    Combines program + city for localized content.
    """
    # Links
    program = models.ForeignKey('cms.ProgramPage', on_delete=models.PROTECT, related_name='local_pages')
    city = models.ForeignKey('cms.City', on_delete=models.PROTECT, related_name='local_pages')
    assigned_office = models.ForeignKey('cms.Office', on_delete=models.SET_NULL, null=True, blank=True, related_name='local_pages')
    
    # AI-generated content
    local_intro = models.TextField(blank=True, help_text="AI-generated 200-word intro")
    local_faqs = StreamField([
        ('faq', blocks.StructBlock([
            ('question', blocks.CharBlock()),
            ('answer', blocks.RichTextBlock()),
        ]))
    ], blank=True, use_json_field=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('program'),
        FieldPanel('city'),
        FieldPanel('assigned_office'),
        FieldPanel('local_intro'),
        FieldPanel('local_faqs'),
    ]

    # Override URL pattern for flat structure
    def get_url_parts(self, request=None):
        # Return: /program-slug-city-state/
        # This overrides the generated URL, but routing depends on tree location?
        # If this page is effectively root-level in routing, it works.
        # Otherwise, this might be purely cosmetic for sitemaps.
        # Assuming we place these pages in a way that matches, or use custom routing.
        
        site_id, root_url, url_path = super().get_url_parts(request)
        if not site_id:
             return None

        # Construct flat slug
        # Note: ensuring self.slug matches this format is key for standard routing
        flat_slug = f"{self.program.slug}-{self.city.slug}-{self.city.state.lower()}"
        
        # If Wagtail routing is standard, we must ensure the page's actual slug matches this.
        # But get_url_parts allows forcing the returned URL string.
        
        # We'll rely on the slug being set correctly during creation.
        
        return (site_id, root_url, f"/{flat_slug}/")

    def save(self, *args, **kwargs):
        # Auto-generate slug if missing
        if not self.slug and self.program and self.city:
            self.slug = f"{self.program.slug}-{self.city.slug}-{self.city.state.lower()}"
        super().save(*args, **kwargs)
