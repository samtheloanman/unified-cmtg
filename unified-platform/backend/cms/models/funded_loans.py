from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.images.models import Image

# =============================================================================
# FUNDED LOANS (Case Studies)
# =============================================================================
class FundedLoanIndexPage(Page):
    """Container for funded loan case studies"""
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    api_fields = [
        APIField('intro'),
    ]

    subpage_types = ['cms.FundedLoanPage']
    max_count = 1


class FundedLoanPage(Page):
    """Individual funded loan case study"""
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    loan_type = models.CharField(max_length=100, blank=True)
    property_type = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    close_date = models.DateField(null=True, blank=True)
    description = RichTextField(blank=True)
    featured_image = models.ForeignKey(
        Image, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )
    source_url = models.URLField(blank=True, help_text="Original WordPress URL for reference")

    content_panels = Page.content_panels + [
        FieldPanel('featured_image'),
        FieldPanel('loan_amount'),
        FieldPanel('loan_type'),
        FieldPanel('property_type'),
        FieldPanel('location'),
        FieldPanel('close_date'),
        FieldPanel('description'),
        FieldPanel('source_url'),
    ]

    api_fields = [
        APIField('loan_amount'),
        APIField('loan_type'),
        APIField('property_type'),
        APIField('location'),
        APIField('close_date'),
        APIField('description'),
        APIField('source_url'),
    ]

    parent_page_types = ['cms.FundedLoanIndexPage']
