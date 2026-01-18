from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, TabbedInterface, ObjectList
from wagtail.api import APIField
from wagtail.images.models import Image

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
    linked_program_type = models.ForeignKey(
        'pricing.ProgramType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Link to pricing engine program type"
    )
    available_states = models.JSONField(default=list, blank=True, help_text="List of available state codes")

    # Moved from Financial per spec
    minimum_loan_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    maximum_loan_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    min_credit_score = models.IntegerField(null=True, blank=True)

    # === PROGRAM DETAILS TAB (Rich Content) ===
    mortgage_program_highlights = RichTextField(blank=True)
    what_are = RichTextField(blank=True, help_text="What are these loans? (e.g., 'What are Super Jumbo Loans?')")
    details_about_mortgage_loan_program = RichTextField(blank=True)
    benefits_of = RichTextField(blank=True)
    requirements = RichTextField(blank=True)
    how_to_qualify_for = RichTextField(blank=True)
    why_us = RichTextField(blank=True)

    # FAQ StreamField
    faq = StreamField([
        ('faq_item', blocks.StructBlock([
            ('question', blocks.CharBlock(max_length=200)),
            ('answer', blocks.RichTextBlock()),
        ], icon='help'))
    ], blank=True, use_json_field=True)
    
    # === FINANCIAL TERMS TAB (7 fields) ===
    interest_rates = models.CharField(max_length=100, blank=True, help_text="e.g., 5.50-8.25%")
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
    
    # === LOCATION TAB (Core fields only) ===
    is_local_variation = models.BooleanField(default=False)
    target_city = models.CharField(max_length=100, blank=True)
    target_state = models.CharField(max_length=2, blank=True)
    target_region = models.CharField(max_length=100, blank=True)
    
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
        FieldPanel('linked_program_type'),
        FieldPanel('minimum_loan_amount'),
        FieldPanel('maximum_loan_amount'),
        FieldPanel('min_credit_score'),
        FieldPanel('available_states'),
    ]
    
    financial_panels = [
        FieldPanel('interest_rates'),
        FieldPanel('max_ltv'),
        FieldPanel('max_debt_to_income_ratio'),
        FieldPanel('min_dscr'),
    ]

    program_details_panels = [
        FieldPanel('mortgage_program_highlights'),
        FieldPanel('what_are'),
        FieldPanel('details_about_mortgage_loan_program'),
        FieldPanel('benefits_of'),
        FieldPanel('requirements'),
        FieldPanel('how_to_qualify_for'),
        FieldPanel('why_us'),
        FieldPanel('faq'),
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
        FieldPanel('target_region'),
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
        ObjectList(program_details_panels, heading='Program Details'),
        ObjectList(property_panels, heading='Property & Loan'),
        ObjectList(borrower_panels, heading='Borrower Details'),
        ObjectList(location_panels, heading='Location'),
        ObjectList(meta_panels, heading='Meta'),
        ObjectList(Page.promote_panels, heading='SEO'),
    ])
    
    api_fields = [
        APIField('program_type'),
        APIField('linked_program_type'),
        APIField('available_states'),
        APIField('minimum_loan_amount'),
        APIField('maximum_loan_amount'),
        APIField('min_credit_score'),
        APIField('interest_rates'),
        APIField('max_ltv'),
        APIField('max_debt_to_income_ratio'),
        APIField('min_dscr'),
        APIField('mortgage_program_highlights'),
        APIField('what_are'),
        APIField('details_about_mortgage_loan_program'),
        APIField('benefits_of'),
        APIField('requirements'),
        APIField('how_to_qualify_for'),
        APIField('why_us'),
        APIField('faq'),
        APIField('property_types'),
        APIField('occupancy_types'),
        APIField('lien_position'),
        APIField('amortization_terms'),
        APIField('purpose_of_mortgage'),
        APIField('refinance_types'),
        APIField('income_documentation_type'),
        APIField('prepayment_penalty'),
        APIField('borrower_types'),
        APIField('citizenship_requirements'),
        APIField('credit_events_allowed'),
        APIField('mortgage_lates_allowed'),
        APIField('is_local_variation'),
        APIField('target_city'),
        APIField('target_state'),
        APIField('target_region'),
        APIField('featured_image'),
        APIField('schema_markup'),
        APIField('source_url'),
    ]
    
    parent_page_types = ['cms.ProgramIndexPage']
