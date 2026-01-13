"""
Rate adjustment models for loan pricing.

This module contains models for storing rate and price adjustments
(LLPAs - Loan Level Price Adjustments) that modify base pricing based
on loan characteristics.
"""

from django.db import models

from pricing.models.programs import TimestampedModel
from pricing.models.program_types import LenderProgramOffering


class RateAdjustment(TimestampedModel):
    """
    Rate/price adjustment for a lender program offering.

    Represents pricing adjustments based on:
    - 2D grids (FICO × LTV)
    - 1D lookups (purpose, occupancy, property type, loan amount tiers)
    """

    # Adjustment Categories
    ADJUSTMENT_TYPE_FICO_LTV = 'fico_ltv'
    ADJUSTMENT_TYPE_PURPOSE = 'purpose'
    ADJUSTMENT_TYPE_OCCUPANCY = 'occupancy'
    ADJUSTMENT_TYPE_PROPERTY_TYPE = 'property_type'
    ADJUSTMENT_TYPE_LOAN_AMOUNT = 'loan_amount'
    ADJUSTMENT_TYPE_LOCK_PERIOD = 'lock_period'
    ADJUSTMENT_TYPE_STATE = 'state'

    ADJUSTMENT_TYPE_CHOICES = [
        (ADJUSTMENT_TYPE_FICO_LTV, 'Credit Score × LTV Grid'),
        (ADJUSTMENT_TYPE_PURPOSE, 'Loan Purpose'),
        (ADJUSTMENT_TYPE_OCCUPANCY, 'Occupancy Type'),
        (ADJUSTMENT_TYPE_PROPERTY_TYPE, 'Property Type'),
        (ADJUSTMENT_TYPE_LOAN_AMOUNT, 'Loan Amount Tier'),
        (ADJUSTMENT_TYPE_LOCK_PERIOD, 'Rate Lock Period'),
        (ADJUSTMENT_TYPE_STATE, 'State'),
    ]

    # Foreign Key
    offering = models.ForeignKey(
        LenderProgramOffering,
        on_delete=models.CASCADE,
        related_name='adjustments',
        help_text="Lender program offering this adjustment applies to"
    )

    # Adjustment Type
    adjustment_type = models.CharField(
        max_length=20,
        choices=ADJUSTMENT_TYPE_CHOICES,
        help_text="Type of adjustment"
    )

    # For 1D lookups (value key-based)
    value_key = models.CharField(
        max_length=50,
        blank=True,
        help_text="Lookup key for 1D adjustments (e.g., 'purchase', 'CA')"
    )

    # For 2D grids (FICO × LTV) - Row dimension
    row_min = models.FloatField(
        null=True,
        blank=True,
        help_text="Minimum value for row dimension (e.g., min FICO)"
    )
    row_max = models.FloatField(
        null=True,
        blank=True,
        help_text="Maximum value for row dimension (e.g., max FICO)"
    )

    # For 2D grids - Column dimension
    col_min = models.FloatField(
        null=True,
        blank=True,
        help_text="Minimum value for column dimension (e.g., min LTV)"
    )
    col_max = models.FloatField(
        null=True,
        blank=True,
        help_text="Maximum value for column dimension (e.g., max LTV)"
    )

    # Adjustment value (in points/percentage)
    adjustment_points = models.FloatField(
        help_text="Adjustment in points (negative = cost, positive = credit)"
    )

    class Meta:
        verbose_name = "Rate Adjustment"
        verbose_name_plural = "Rate Adjustments"
        ordering = ['offering', 'adjustment_type', 'row_min', 'col_min']

    def __str__(self) -> str:
        if self.value_key:
            return (
                f"{self.offering.lender.company_name} - "
                f"{self.get_adjustment_type_display()}: "
                f"{self.value_key} = {self.adjustment_points:+.3f}pts"
            )
        elif self.row_min is not None and self.col_min is not None:
            return (
                f"{self.offering.lender.company_name} - "
                f"{self.get_adjustment_type_display()}: "
                f"[{self.row_min}-{self.row_max}] × "
                f"[{self.col_min}-{self.col_max}] = "
                f"{self.adjustment_points:+.3f}pts"
            )
        else:
            return (
                f"{self.offering.lender.company_name} - "
                f"{self.get_adjustment_type_display()}: "
                f"{self.adjustment_points:+.3f}pts"
            )
