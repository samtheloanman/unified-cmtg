from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField

# =============================================================================
# LEGACY RECREATED PAGES (Mirror of production)
# =============================================================================
class LegacyIndexPage(Page):
    """Container for legacy recreated pages"""
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    subpage_types = ['cms.LegacyRecreatedPage']
    max_count = 1


class LegacyRecreatedPage(Page):
    """
    Pages recreated from production site for comparison.
    Stored under /legacy/recreated/ hierarchy.
    """
    original_url = models.URLField(help_text="Original URL from custommortgageinc.com")
    original_title = models.CharField(max_length=500)
    body = RichTextField(blank=True)
    raw_html = models.TextField(blank=True, help_text="Original HTML content")
    last_scraped = models.DateTimeField(auto_now=True)

    content_panels = Page.content_panels + [
        FieldPanel('original_url'),
        FieldPanel('original_title'),
        FieldPanel('body'),
    ]

    api_fields = [
        APIField('original_url'),
        APIField('original_title'),
        APIField('body'),
    ]

    parent_page_types = ['cms.LegacyIndexPage']
