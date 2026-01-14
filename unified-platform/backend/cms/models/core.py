from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.images.models import Image

# =============================================================================
# HOME PAGE
# =============================================================================
class HomePage(Page):
    """Main site homepage"""
    hero_title = models.CharField(max_length=255, blank=True)
    hero_subtitle = RichTextField(blank=True)
    hero_cta_text = models.CharField(max_length=100, blank=True, default="Get Your Quote")
    hero_cta_url = models.URLField(blank=True, default="/quote")

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('hero_title'),
            FieldPanel('hero_subtitle'),
            FieldPanel('hero_cta_text'),
            FieldPanel('hero_cta_url'),
        ], heading="Hero Section"),
    ]

    api_fields = [
        APIField('hero_title'),
        APIField('hero_subtitle'),
        APIField('hero_cta_text'),
        APIField('hero_cta_url'),
    ]

    # Note: Strings 'cms.ModelName' rely on models being exposed in cms.models
    subpage_types = ['cms.ProgramIndexPage', 'cms.StandardPage', 'cms.FundedLoanIndexPage', 'cms.LegacyIndexPage', 'cms.BlogIndexPage']
    max_count = 1


# =============================================================================
# STANDARD PAGE (Generic content pages)
# =============================================================================
class StandardPage(Page):
    """Generic content page for About, Contact, etc."""
    body = RichTextField(blank=True)
    featured_image = models.ForeignKey(
        Image, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('featured_image'),
        FieldPanel('body'),
    ]

    api_fields = [
        APIField('body'),
    ]

    parent_page_types = ['cms.HomePage', 'cms.StandardPage']
