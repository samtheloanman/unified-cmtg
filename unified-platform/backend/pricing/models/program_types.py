"""
Program type models - normalized loan program architecture.

This module contains the modern program type models that separate canonical
program definitions from lender-specific offerings.

Models:
- ProgramType: Canonical loan program type (e.g., DSCR, FHA, Fix-and-Flip)
- LenderProgramOffering: Lender's specific offering with rates and overlays
"""

from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify

from common.fields import ChoiceArrayField
from common.models import TimestampedModel
from pricing import choices


# Program Categories
CATEGORY_AGENCY = 'agency'
CATEGORY_NON_QM = 'non_qm'
CATEGORY_HARD_MONEY = 'hard_money'
CATEGORY_COMMERCIAL = 'commercial'

PROGRAM_CATEGORY_CHOICES = (
    (CATEGORY_AGENCY, 'Agency/Conventional'),
    (CATEGORY_NON_QM, 'Non-QM'),
    (CATEGORY_HARD_MONEY, 'Hard Money/Bridge'),
    (CATEGORY_COMMERCIAL, 'Commercial'),
)

# Documentation Levels
DOC_FULL = 'full'
DOC_LITE = 'lite'
DOC_NO_DOC = 'no_doc'
DOC_BANK_STATEMENT = 'bank_statement'
DOC_DSCR = 'dscr'
DOC_ASSET = 'asset'

DOCUMENTATION_CHOICES = (
    (DOC_FULL, 'Full Documentation'),
    (DOC_LITE, 'Lite Documentation'),
    (DOC_NO_DOC, 'No Documentation'),
    (DOC_BANK_STATEMENT, 'Bank Statement'),
    (DOC_DSCR, 'DSCR Only'),
    (DOC_ASSET, 'Asset Depletion'),
)


class ProgramType(TimestampedModel):
    """
    Canonical loan program type.

    Represents a type of loan product that multiple lenders may offer,
    with lender-specific variations tracked in LenderProgramOffering.

    Examples: DSCR Investor, FHA Purchase, Fix-and-Flip
    """

    # Basic Information
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Program name (e.g., 'DSCR Investor', 'FHA')"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="URL-safe identifier"
    )
    category = models.CharField(
        max_length=20,
        choices=PROGRAM_CATEGORY_CHOICES,
        help_text="Program category for grouping"
    )

    # Base Loan Type and Eligibility
    loan_type = models.CharField(
        max_length=15,
        choices=choices.LOAN_TYPE_CHOICES,
        default=choices.LOAN_TYPE_CONVENTIONAL,
        help_text="Type of loan"
    )
    property_types = ChoiceArrayField(
        models.CharField(
            max_length=15,
            choices=choices.PROPERTY_TYPE_CHOICES
        ),
        default=list,
        help_text="Allowed property types"
    )
    income_type = models.CharField(
        max_length=30,
        choices=choices.INCOME_TYPE_CHOICES,
        default=choices.INCOME_TYPE_STATED,
        help_text="Income documentation type"
    )
    documentation_level = models.CharField(
        max_length=20,
        choices=DOCUMENTATION_CHOICES,
        default=DOC_FULL,
        help_text="Documentation level required"
    )

    # Base Eligibility Requirements
    base_min_fico = models.PositiveSmallIntegerField(
        default=620,
        validators=[MinValueValidator(300), MaxValueValidator(850)],
        help_text="Base minimum FICO score"
    )
    base_max_ltv = models.FloatField(
        default=80,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Base maximum LTV percentage"
    )
    base_min_dscr = models.FloatField(
        null=True,
        blank=True,
        help_text="Base minimum DSCR for rental income programs"
    )

    # Property and Borrower
    occupancy = ChoiceArrayField(
        models.CharField(
            max_length=15,
            choices=choices.OCCUPANCY_CHOICES
        ),
        default=list,
        help_text="Allowed occupancy types"
    )
    entity_types = ChoiceArrayField(
        models.CharField(
            max_length=20,
            choices=choices.BORROWING_ENTITY_TYPE_CHOICES
        ),
        default=list,
        help_text="Allowed borrowing entity types"
    )
    purposes = ChoiceArrayField(
        models.CharField(
            max_length=12,
            choices=choices.LOAN_PURPOSE_CHOICES
        ),
        default=list,
        help_text="Allowed loan purposes"
    )

    # Description and Status
    description = models.TextField(
        blank=True,
        help_text="Program guidelines summary"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this program type active?"
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Sort order for display"
    )

    class Meta:
        verbose_name = "Program Type"
        verbose_name_plural = "Program Types"
        ordering = ['category', 'sort_order', 'name']

    def __str__(self) -> str:
        return f"{self.name} ({self.get_category_display()})"

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def lender_count(self):
        """Return number of lenders offering this program."""
        return self.offerings.filter(is_active=True).count()


class LenderProgramOffering(TimestampedModel):
    """
    A lender's specific offering of a program type.

    Contains lender-specific rates, fees, and overlays (stricter
    requirements than the base program type).
    """

    # Foreign Keys
    lender = models.ForeignKey(
        'Lender',
        on_delete=models.CASCADE,
        related_name='program_offerings',
        help_text="Lender offering this program"
    )
    program_type = models.ForeignKey(
        ProgramType,
        on_delete=models.CASCADE,
        related_name='offerings',
        help_text="Program type being offered"
    )

    # Lender-Specific Rates and Fees
    min_rate = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(30)],
        help_text="Minimum interest rate (%)"
    )
    max_rate = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(30)],
        help_text="Maximum interest rate (%)"
    )
    min_points = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Minimum origination points"
    )
    max_points = models.FloatField(
        default=2,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Maximum origination points"
    )
    lender_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('995.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Lender underwriting fee"
    )

    # Lender Overlays (may be stricter than base program)
    min_fico = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(300), MaxValueValidator(850)],
        help_text="Lender's min FICO (may be higher than program base)"
    )
    max_ltv = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Lender's max LTV (may be lower than program base)"
    )
    min_dscr = models.FloatField(
        null=True,
        blank=True,
        help_text="Lender's min DSCR for rental programs"
    )

    # Loan Amount Limits
    min_loan = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('75000.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Minimum loan amount"
    )
    max_loan = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('2000000.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Maximum loan amount"
    )

    # Rate Sheet Information
    rate_sheet_url = models.URLField(
        blank=True,
        help_text="URL to current rate sheet PDF"
    )
    last_rate_update = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When rates were last updated from rate sheet"
    )

    # Status and Notes
    is_active = models.BooleanField(
        default=True,
        help_text="Is this offering active?"
    )
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about this offering"
    )

    class Meta:
        verbose_name = "Lender Program Offering"
        verbose_name_plural = "Lender Program Offerings"
        ordering = ['program_type', 'lender__company_name']
        unique_together = ['lender', 'program_type']

    def __str__(self) -> str:
        return f"{self.lender.company_name} - {self.program_type.name}"

    @property
    def rate_range(self):
        """Format rate range for display."""
        return f"{self.min_rate:.3f}% - {self.max_rate:.3f}%"

    @property
    def points_range(self):
        """Format points range for display."""
        if self.min_points == self.max_points:
            return f"{self.min_points:.2f}"
        return f"{self.min_points:.2f} - {self.max_points:.2f}"
