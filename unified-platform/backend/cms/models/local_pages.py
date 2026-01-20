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
    
    schema_markup = models.JSONField(null=True, blank=True, help_text="Auto-generated JSON-LD schema")
    
    content_panels = Page.content_panels + [
        FieldPanel('program'),
        FieldPanel('city'),
        FieldPanel('assigned_office'),
        FieldPanel('local_intro'),
        FieldPanel('local_faqs'),
        FieldPanel('schema_markup'),
    ]

    # Override URL pattern for flat structure
    def get_url_parts(self, request=None):
        # Return: /program-slug-city-slug/
        # Note: city.slug already includes state (e.g., 'los-angeles-ca')
        # so we don't need to append it again

        site_id, root_url, url_path = super().get_url_parts(request)
        if not site_id:
             return None

        # Construct flat slug: program-slug + city-slug
        # City slug format: city-name-state (e.g., 'los-angeles-ca')
        flat_slug = f"{self.program.slug}-{self.city.slug}"

        return (site_id, root_url, f"/{flat_slug}/")

    def save(self, *args, **kwargs):
        # Auto-generate slug if missing
        # City slug already includes state, so just combine program + city
        if not self.slug and self.program and self.city:
            self.slug = f"{self.program.slug}-{self.city.slug}"
        super().save(*args, **kwargs)
