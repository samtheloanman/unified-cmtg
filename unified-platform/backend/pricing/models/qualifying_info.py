from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from localflavor.us.models import USStateField

from common.models import TimestampedModel
from pricing import choices


class QualifyingInfo(TimestampedModel):
    """
    Model storing borrower qualification information for reverse matching.

    This allows us to find which leads (QualifyingInfo records) match
    a newly added or updated loan program.
    """

    # Property Details
    property_type = models.CharField(
        max_length=15,
        choices=choices.PROPERTY_TYPE_CHOICES,
        help_text="Type of property"
    )
    occupancy = models.CharField(
        max_length=15,
        choices=choices.OCCUPANCY_CHOICES,
        help_text="Occupancy type"
    )
    state = USStateField(
        choices=choices.STATE_CHOICES,
        help_text="Property state"
    )

    # Loan Details
    purpose = models.CharField(
        max_length=12,
        choices=choices.LOAN_PURPOSE_CHOICES,
        help_text="Loan purpose"
    )
    loan_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Requested loan amount"
    )
    ltv = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Loan-to-Value ratio (%)"
    )

    # Borrower Details
    entity_type = models.CharField(
        max_length=20,
        choices=choices.BORROWING_ENTITY_TYPE_CHOICES,
        help_text="Borrowing entity type"
    )
    estimated_credit_score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(300), MaxValueValidator(850)],
        help_text="Estimated credit score"
    )

    class Meta:
        verbose_name = "Qualifying Info"
        verbose_name_plural = "Qualifying Infos"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.loan_amount} - {self.estimated_credit_score} - {self.state}"
