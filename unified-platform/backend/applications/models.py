"""
Application Models

Stores loan applications synced from Floify for borrower dashboard display.
"""

from django.db import models
from common.models import TimestampedModel


class Application(TimestampedModel):
    """
    Loan application synced from Floify.

    Stores application status and key data for borrower dashboard.
    The full Floify application data is stored in the floify_data JSON field
    for debugging and future reference.

    Attributes:
        floify_id: Unique Floify prospect ID
        floify_loan_id: Floify loan ID (when converted from prospect)
        borrower_email: Primary email address
        borrower_first_name: First name
        borrower_last_name: Last name
        loan_amount: Requested loan amount
        property_address: Subject property address
        loan_purpose: purchase, refinance, cash_out, etc.
        status: Current application status
        floify_data: Raw Floify JSON data
    """

    STATUS_CHOICES = [
        ('created', 'Created'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('processing', 'Processing'),
        ('underwriting', 'Underwriting'),
        ('approved', 'Approved'),
        ('clear_to_close', 'Clear to Close'),
        ('funded', 'Funded'),
        ('denied', 'Denied'),
        ('withdrawn', 'Withdrawn'),
    ]

    # Floify identifiers
    floify_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Floify prospect ID"
    )
    floify_loan_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="Floify loan ID (when prospect converts to loan)"
    )

    # Borrower info
    borrower_email = models.EmailField(
        db_index=True,
        help_text="Primary borrower email address"
    )
    borrower_first_name = models.CharField(max_length=100)
    borrower_last_name = models.CharField(max_length=100)
    borrower_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Mobile phone number"
    )

    # Loan details
    loan_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Requested loan amount"
    )
    property_address = models.TextField(
        blank=True,
        help_text="Subject property address"
    )
    property_state = models.CharField(
        max_length=2,
        blank=True,
        help_text="Property state abbreviation"
    )
    loan_purpose = models.CharField(
        max_length=50,
        blank=True,
        help_text="purchase, refinance, cash_out, construction"
    )
    property_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="residential, commercial, multi-family"
    )

    # Selected program (from quote wizard)
    selected_program = models.CharField(
        max_length=255,
        blank=True,
        help_text="Loan program selected by borrower"
    )
    selected_lender = models.CharField(
        max_length=255,
        blank=True,
        help_text="Lender selected by borrower"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='created',
        db_index=True
    )
    status_updated_at = models.DateTimeField(auto_now=True)

    # Raw Floify data (for debugging and future features)
    floify_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Complete Floify API response"
    )

    # Metadata
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about this application"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['borrower_email', 'status']),
            models.Index(fields=['floify_id']),
        ]
        app_label = 'applications'

    def __str__(self):
        return f"{self.borrower_last_name}, {self.borrower_first_name} - ${self.loan_amount or 0:,.0f}"

    @property
    def full_name(self):
        """Return borrower's full name."""
        return f"{self.borrower_first_name} {self.borrower_last_name}"

    @property
    def status_display_color(self):
        """Return Bootstrap color class for status badge."""
        color_map = {
            'created': 'secondary',
            'in_progress': 'primary',
            'submitted': 'info',
            'processing': 'info',
            'underwriting': 'warning',
            'approved': 'success',
            'clear_to_close': 'success',
            'funded': 'success',
            'denied': 'danger',
            'withdrawn': 'secondary',
        }
        return color_map.get(self.status, 'secondary')

    def update_from_floify(self, floify_data: dict):
        """
        Update application fields from Floify API response.

        Args:
            floify_data: Dict from Floify API
        """
        self.borrower_email = floify_data.get('email', self.borrower_email)
        self.borrower_first_name = floify_data.get('firstName', self.borrower_first_name)
        self.borrower_last_name = floify_data.get('lastName', self.borrower_last_name)
        self.borrower_phone = floify_data.get('mobilePhoneNumber', self.borrower_phone)
        self.loan_amount = floify_data.get('loanAmount', self.loan_amount)
        self.property_address = floify_data.get('subjectPropertyAddress', self.property_address)
        self.loan_purpose = floify_data.get('loanPurpose', self.loan_purpose)
        self.floify_loan_id = floify_data.get('loanId', self.floify_loan_id)
        self.floify_data = floify_data
