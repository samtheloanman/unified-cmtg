"""
Loan program models for the Unified CMTG Platform.

This module contains the core lender and loan program models ported from
legacy cmtgdirect/loans/models/programs.py.

Models:
- Lender: Lending institution that offers loan programs
- AddressInfo: Address information for lenders
- LenderContact: Contact persons at lender institutions
- BaseLoan: Abstract base model for all loan program types
- LoanProgram: Concrete loan program with DSCR-specific fields
"""

from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from localflavor.us.models import USStateField, USZipCodeField
from phonenumber_field.modelfields import PhoneNumberField

from common.fields import ChoiceArrayField
from common.models import TimestampedModel
from pricing import choices


class AddressInfo(TimestampedModel):
    """Physical address information for a lender."""

    name = models.CharField(
        max_length=255,
        help_text="Lender's name for this address"
    )
    street_1 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Street address line 1"
    )
    street_2 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Street address line 2"
    )
    city = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="City"
    )
    state = USStateField(
        blank=True,
        null=True,
        choices=choices.STATE_CHOICES,
        help_text="State"
    )
    zipcode = USZipCodeField(
        blank=True,
        null=True,
        help_text="ZIP code"
    )

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"

    def __str__(self) -> str:
        return self.name


class LenderContact(TimestampedModel):
    """Contact person at a lender institution."""

    lender = models.ForeignKey(
        'Lender',
        related_name="contacts",
        null=True,
        on_delete=models.CASCADE,
        help_text="Lender this contact works for"
    )
    address = models.ForeignKey(
        AddressInfo,
        related_name="lender_contacts",
        null=True,
        on_delete=models.CASCADE,
        help_text="Physical address of this contact"
    )
    contact_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Contact person's name"
    )
    contact_type = models.CharField(
        max_length=25,
        null=True,
        blank=True,
        choices=choices.LENDER_CONTACT_TYPE_CHOICES,
        default=choices.LENDER_CONTACT_TYPE_OWN,
        help_text="Role or position of this contact"
    )
    contact_phone = PhoneNumberField(
        null=True,
        blank=True,
        help_text="Contact's phone number"
    )
    contact_fax = PhoneNumberField(
        null=True,
        blank=True,
        help_text="Contact's fax number"
    )
    contact_email = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Contact's email address"
    )

    class Meta:
        verbose_name = "Lender Contact"
        verbose_name_plural = "Lender Contacts"

    def __str__(self) -> str:
        return self.contact_name or "Unknown Contact"


class Lender(TimestampedModel):
    """Lending institution that offers loan programs."""

    company_name = models.CharField(
        max_length=500,
        help_text="Legal name of the lending company"
    )
    include_states = ChoiceArrayField(
        USStateField(choices=choices.STATE_CHOICES),
        default=list,
        help_text="States where this lender is licensed to operate"
    )
    company_website = models.URLField(
        blank=True,
        null=True,
        help_text="Lender's main website URL"
    )
    company_phone = PhoneNumberField(
        blank=True,
        null=True,
        help_text="Main company phone number"
    )
    company_fax = PhoneNumberField(
        blank=True,
        null=True,
        help_text="Main company fax number"
    )
    company_email = models.EmailField(
        blank=True,
        null=True,
        help_text="General company email address"
    )
    company_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal notes about this lender"
    )

    class Meta:
        verbose_name = "Lender"
        verbose_name_plural = "Lenders"
        ordering = ['company_name']

    def __str__(self) -> str:
        return self.company_name


class BaseLoan(TimestampedModel):
    """
    Abstract base model for all loan program types.

    Contains common eligibility criteria, property restrictions,
    credit requirements, and rate/fee information used across
    all loan program variations.
    """

    lender = models.ForeignKey(
        'Lender',
        on_delete=models.CASCADE,
        help_text="Lender offering this program"
    )
    name = models.CharField(
        max_length=500,
        help_text="Loan program name"
    )

    # Loan Type and Documentation
    loan_type = models.CharField(
        choices=choices.LOAN_TYPE_CHOICES,
        max_length=15,
        default=choices.LOAN_TYPE_CONVENTIONAL,
        help_text="Type of loan program"
    )
    income_type = models.CharField(
        choices=choices.INCOME_TYPE_CHOICES,
        default=choices.INCOME_TYPE_STATED,
        max_length=30,
        help_text="Income documentation required"
    )

    # Property Eligibility
    occupancy = ChoiceArrayField(
        models.CharField(
            choices=choices.OCCUPANCY_CHOICES,
            max_length=15,
            help_text="Occupancy type"
        ),
        default=list,
        help_text="Allowed occupancy types"
    )
    property_types = ChoiceArrayField(
        models.CharField(
            choices=choices.PROPERTY_TYPE_CHOICES,
            max_length=15
        ),
        default=list,
        help_text="Allowed property types (residential, commercial)"
    )
    property_sub_categories = ChoiceArrayField(
        models.CharField(
            max_length=25,
            choices=choices.PROPERTY_TYPE_SUB_CATEGORY_CHOICES
        ),
        default=list,
        help_text="Specific property sub-types allowed"
    )
    property_conditions = ChoiceArrayField(
        models.CharField(
            max_length=2,
            choices=choices.PROPERTY_CONDITION_CHOICES
        ),
        default=list,
        help_text="Appraisal condition ratings allowed (C1-C6)"
    )

    # Loan Structure
    recourse = ChoiceArrayField(
        models.CharField(
            choices=choices.RECOURSE_CHOICES,
            max_length=15
        ),
        default=list,
        help_text="Full recourse or non-recourse"
    )
    amortization_terms = ChoiceArrayField(
        models.CharField(
            max_length=20,
            choices=choices.AMORTIZATION_TERM_CHOICES
        ),
        default=list,
        help_text="Available amortization periods"
    )
    io_offered = models.BooleanField(
        'I/O Offered',
        choices=choices.YES_NO_CHOICES,
        default=choices.YES,
        help_text="Interest-only payment option available"
    )
    p_and_i_offered = models.BooleanField(
        'P&I Offered',
        choices=choices.YES_NO_CHOICES,
        default=choices.YES,
        help_text="Principal and interest payment option available"
    )

    # Borrower Eligibility
    entity_type = ChoiceArrayField(
        models.CharField(
            max_length=20,
            choices=choices.BORROWING_ENTITY_TYPE_CHOICES
        ),
        default=list,
        help_text="Allowed borrowing entity types"
    )
    employment = ChoiceArrayField(
        models.CharField(
            choices=choices.EMPLOYMENT_CHOICES,
            max_length=10,
            help_text="Employment type"
        ),
        default=list,
        help_text="Allowed employment types"
    )
    percent_ownership = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Minimum ownership percentage required"
    )

    # Loan Purpose and Terms
    purpose = ChoiceArrayField(
        models.CharField(
            choices=choices.LOAN_PURPOSE_CHOICES,
            max_length=12
        ),
        default=list,
        help_text="Approved loan purposes"
    )
    max_cash_out = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Maximum cash-out amount"
    )

    # Loan Amount Limits
    min_loan_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Minimum loan amount"
    )
    max_loan_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Maximum loan amount"
    )
    max_loan_to_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        null=True,
        help_text="Maximum loan-to-value ratio"
    )

    # Credit Requirements
    reserve_requirement = models.PositiveSmallIntegerField(
        help_text="Required months of reserves"
    )
    min_credit = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(300), MaxValueValidator(850)],
        default=580,
        help_text="Minimum credit score required"
    )

    # Property Size Limits
    min_acreage = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text="Minimum acreage allowed"
    )
    max_acreage = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text="Maximum acreage allowed (blank = unlimited)"
    )
    max_properties_financed = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Maximum financed properties allowed (blank = unlimited)"
    )

    # Refinance Rules
    refinance_seasoning = models.CharField(
        max_length=5,
        choices=choices.REFINANCE_SEASONING_CHOICES,
        help_text="Months after purchase before refinance allowed"
    )

    # Compensation and Fees
    ysp_available = models.BooleanField(
        'YSP Available',
        choices=choices.YES_NO_CHOICES,
        default=choices.YES,
        help_text="Yield spread premium allowed"
    )
    max_ysp = models.PositiveSmallIntegerField(
        'Max YSP',
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Maximum YSP percentage allowed"
    )
    max_compensation = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Maximum broker compensation percentage"
    )
    processing_fee_allowed = models.BooleanField(
        choices=choices.YES_NO_CHOICES,
        default=choices.YES,
        help_text="Broker processing/admin fee allowed"
    )
    max_dti = models.PositiveIntegerField(
        'Max DTI',
        blank=True,
        null=True,
        help_text="Maximum debt-to-income ratio (blank = none)"
    )
    lender_fee = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Lender underwriting/loan fee"
    )

    # Prepayment Terms
    prepayment_penalty = models.CharField(
        max_length=10,
        choices=choices.PPP_CHOICES,
        help_text="Prepayment penalty options"
    )
    prepayment_cost = models.CharField(
        max_length=4,
        choices=choices.PPP_COST_CHOICES,
        help_text="Prepayment penalty percentage"
    )

    # Rate Lock
    rate_lock_available = models.BooleanField(
        choices=choices.YES_NO_CHOICES,
        default=choices.YES,
        help_text="Rate lock available"
    )
    rate_lock_terms = models.PositiveSmallIntegerField(
        choices=choices.RATE_LOCK_TERMS,
        blank=True,
        null=True,
        help_text="Rate lock period in days"
    )

    # Credit History Requirements
    bk_allowed = models.BooleanField(
        'BK Allowed',
        choices=choices.YES_NO_CHOICES,
        default=choices.YES,
        help_text="Bankruptcy allowed"
    )
    time_since_bk = models.PositiveSmallIntegerField(
        'Time since BK',
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Years since bankruptcy (0-10)"
    )
    foreclosure_allowed = models.BooleanField(
        choices=choices.YES_NO_CHOICES,
        default=choices.YES,
        help_text="Foreclosure allowed"
    )
    time_since_foreclosure = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Years since foreclosure (0-10)"
    )
    short_sales_allowed = models.BooleanField(
        choices=choices.YES_NO_CHOICES,
        default=choices.YES,
        help_text="Short sale allowed"
    )
    time_since_short_sale = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Years since short sale (0-10)"
    )
    nod_allowed = models.BooleanField(
        'NOD Allowed',
        choices=choices.YES_NO_CHOICES,
        default=choices.YES,
        help_text="Notice of Default allowed"
    )
    time_since_nod = models.PositiveSmallIntegerField(
        'Time since NOD',
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Years since Notice of Default (0-10)"
    )
    nos_allowed = models.BooleanField(
        'NOS Allowed',
        choices=choices.YES_NO_CHOICES,
        default=choices.YES,
        help_text="Notice of Sale allowed"
    )
    time_since_nos = models.PositiveSmallIntegerField(
        'Time since NOS',
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Years since Notice of Sale (0-10)"
    )

    # Rate and Cost Ranges
    potential_rate_min = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Approximate minimum interest rate (0-30%)"
    )
    potential_rate_max = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Approximate maximum interest rate"
    )
    potential_cost_min = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Minimum cost in points (lender points)"
    )
    potential_cost_max = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Maximum cost in points (lender points)"
    )

    # Lien Position
    lien_position = models.CharField(
        max_length=5,
        choices=choices.MORTGAGE_NUMBER_CHOICES,
        default=choices.MORTGAGE_NUMBER_OTHER,
        help_text="Trust deed/mortgage lien position"
    )

    class Meta:
        abstract = True
        ordering = ['lender', 'loan_type']

    def __str__(self) -> str:
        return f"{self.lender} - {self.get_loan_type_display()}"


class LoanProgram(BaseLoan):
    """
    Concrete loan program model with DSCR-specific fields.

    Extends BaseLoan with construction and investment property
    specific LTV calculations (purchase price, ARV, LTC, rehab).
    """

    # Construction/Rehab LTV Fields
    max_ltv_on_purchase_price = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Max LTV on Purchase Price (%)",
        help_text="Max LTV on land value for construction loans"
    )
    max_ltv_on_arv = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Max LTV on ARV (%)",
        help_text="Max LTV on after-repair value for construction loans"
    )
    max_ltv_on_cost = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Max LTV on Cost (%)",
        help_text="Max loan-to-cost for construction loans"
    )
    max_ltv_on_rehab = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Max LTV on Rehab Money Financed (%)",
        help_text="Max LTV on construction funds for construction loans"
    )
    min_borrower_contribution = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Minimum borrower contribution as % of LTC"
    )

    # DSCR Requirement
    min_dscr = models.FloatField(
        'Min DSCR',
        help_text="Minimum debt service coverage ratio"
    )

    class Meta:
        verbose_name = "Loan Program"
        verbose_name_plural = "Loan Programs"
        ordering = ['lender', 'loan_type']

    def get_matching_qual_infos(self):
        """Get qualifying info records that match this loan program."""
        from pricing.services.matching import get_quals_for_loan_program
        return get_quals_for_loan_program(self)

    def get_absolute_url(self):
        """Return URL for viewing this loan program detail."""
        return reverse('view_loan', kwargs={'loan_id': self.pk})
