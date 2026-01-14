from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, TabbedInterface, ObjectList
from wagtail.api import APIField
from wagtail.images.models import Image
from wagtail import blocks

# =============================================================================
# BLOCKS
# =============================================================================

class FAQBlock(blocks.StructBlock):
    question = blocks.CharBlock(required=True, help_text="The question")
    answer = blocks.RichTextBlock(required=True, help_text="The answer")

    class Meta:
        icon = "help"
        label = "FAQ"


# =============================================================================
# PROGRAM PAGES (Loan Programs)
# =============================================================================
class ProgramIndexPage(Page):
    """Container for all program pages"""
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]
    
    api_fields = [
        APIField('intro'),
    ]
    
    subpage_types = ['cms.ProgramPage']
    max_count = 1


class ProgramPage(Page):
    """
    Individual loan program page with 64+ ACF-equivalent fields.
    Organized into tabs matching WordPress ACF structure.
    """
    
    # === PROGRAM INFO TAB (8 fields) ===
    program_type = models.CharField(
        max_length=50,
        choices=[
            ('residential', 'Residential'),
            ('commercial', 'Commercial'),
            ('hard_money', 'Hard Money'),
            ('nonqm', 'NonQM Stated No Doc No Income'),
            ('reverse_mortgage', 'Reverse Mortgage'),
        ],
        default='residential'
    )
    mortgage_program_highlights = RichTextField(blank=True)
    what_are = RichTextField(blank=True, help_text="What are these loans? (e.g., 'What are Super Jumbo Loans?')")
    details_about_mortgage_loan_program = RichTextField(blank=True)
    benefits_of = RichTextField(blank=True)
    requirements = RichTextField(blank=True)
    how_to_qualify_for = RichTextField(blank=True)
    why_us = RichTextField(blank=True)

    # Changed to StreamField as per F.1 spec
    program_faq = StreamField([
        ('faq', FAQBlock()),
    ], use_json_field=True, blank=True)
    
    # === FINANCIAL TERMS TAB (7 fields) ===
    interest_rates = models.CharField(max_length=100, blank=True, help_text="e.g., 5.50-8.25%")
    minimum_loan_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    maximum_loan_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    min_credit_score = models.IntegerField(null=True, blank=True)
    max_ltv = models.CharField(max_length=20, blank=True, help_text="e.g., 96.5%")
    max_debt_to_income_ratio = models.FloatField(null=True, blank=True)
    min_dscr = models.FloatField(null=True, blank=True, help_text="For DSCR programs")
    
    # === PROPERTY & LOAN TAB (8 fields) ===
    property_types = models.JSONField(default=list, blank=True, help_text="List of property types")
    occupancy_types = models.JSONField(default=list, blank=True)
    lien_position = models.JSONField(default=list, blank=True)
    amortization_terms = models.JSONField(default=list, blank=True)
    purpose_of_mortgage = models.JSONField(default=list, blank=True)
    refinance_types = models.JSONField(default=list, blank=True)
    income_documentation_type = models.JSONField(default=list, blank=True)
    prepayment_penalty = models.CharField(max_length=100, blank=True)
    
    # === BORROWER DETAILS TAB (4 fields) ===
    borrower_types = models.JSONField(default=list, blank=True)
    citizenship_requirements = models.JSONField(default=list, blank=True)
    credit_events_allowed = models.JSONField(default=list, blank=True)
    mortgage_lates_allowed = models.JSONField(default=list, blank=True)
    
    # === LOCATION TAB (Core location fields) ===
    is_local_variation = models.BooleanField(default=False)
    target_city = models.CharField(max_length=100, blank=True)
    target_state = models.CharField(max_length=2, blank=True)
    local_office_address = models.TextField(blank=True)
    local_phone = models.CharField(max_length=20, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # === META ===
    featured_image = models.ForeignKey(
        Image, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )
    schema_markup = models.JSONField(null=True, blank=True, help_text="Structured data for SEO")
    source_url = models.URLField(blank=True, help_text="Original WordPress URL for reference")
    
    # === ADMIN PANELS ===
    program_info_panels = [
        FieldPanel('program_type'),
        FieldPanel('mortgage_program_highlights'),
        FieldPanel('what_are'),
        FieldPanel('details_about_mortgage_loan_program'),
        FieldPanel('benefits_of'),
        FieldPanel('requirements'),
        FieldPanel('how_to_qualify_for'),
        FieldPanel('why_us'),
        FieldPanel('program_faq'),
    ]
    
    financial_panels = [
        FieldPanel('interest_rates'),
        FieldPanel('minimum_loan_amount'),
        FieldPanel('maximum_loan_amount'),
        FieldPanel('min_credit_score'),
        FieldPanel('max_ltv'),
        FieldPanel('max_debt_to_income_ratio'),
        FieldPanel('min_dscr'),
    ]
    
    property_panels = [
        FieldPanel('property_types'),
        FieldPanel('occupancy_types'),
        FieldPanel('lien_position'),
        FieldPanel('amortization_terms'),
        FieldPanel('purpose_of_mortgage'),
        FieldPanel('refinance_types'),
        FieldPanel('income_documentation_type'),
        FieldPanel('prepayment_penalty'),
    ]
    
    borrower_panels = [
        FieldPanel('borrower_types'),
        FieldPanel('citizenship_requirements'),
        FieldPanel('credit_events_allowed'),
        FieldPanel('mortgage_lates_allowed'),
    ]
    
    location_panels = [
        FieldPanel('is_local_variation'),
        FieldPanel('target_city'),
        FieldPanel('target_state'),
        FieldPanel('local_office_address'),
        FieldPanel('local_phone'),
        FieldPanel('latitude'),
        FieldPanel('longitude'),
    ]
    
    meta_panels = [
        FieldPanel('featured_image'),
        FieldPanel('schema_markup'),
        FieldPanel('source_url'),
    ]
    
    edit_handler = TabbedInterface([
        ObjectList(Page.content_panels, heading='Title'),
        ObjectList(program_info_panels, heading='Program Info'),
        ObjectList(financial_panels, heading='Financial Terms'),
        ObjectList(property_panels, heading='Property & Loan'),
        ObjectList(borrower_panels, heading='Borrower Details'),
        ObjectList(location_panels, heading='Location'),
        ObjectList(meta_panels, heading='Meta'),
        ObjectList(Page.promote_panels, heading='SEO'),
    ])
    
    api_fields = [
        APIField('program_type'),
        APIField('mortgage_program_highlights'),
        APIField('what_are'),
        APIField('details_about_mortgage_loan_program'),
        APIField('benefits_of'),
        APIField('requirements'),
        APIField('how_to_qualify_for'),
        APIField('why_us'),
        APIField('program_faq'),
        APIField('interest_rates'),
        APIField('minimum_loan_amount'),
        APIField('maximum_loan_amount'),
        APIField('min_credit_score'),
        APIField('max_ltv'),
        APIField('property_types'),
        APIField('is_local_variation'),
        APIField('target_city'),
        APIField('target_state'),
        APIField('source_url'),
    ]
    
    parent_page_types = ['cms.ProgramIndexPage']
