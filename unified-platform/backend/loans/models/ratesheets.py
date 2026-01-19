from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from common.models import TimestampedModel

class RateProgram(TimestampedModel):
    # (Simplified for brevity, includes min_fico, max_ltv, base_rate etc.)
    base_rate = models.DecimalField(max_digits=6, decimal_places=3)
    # ...

    class Meta:
        app_label = 'loans'

class RateAdjustment(TimestampedModel):
    """
    Rate/price adjustments that apply to a program based on loan characteristics.
    These are the LLPA (Loan Level Price Adjustments) from the rate sheet.
    """
    rate_program = models.ForeignKey(RateProgram, on_delete=models.CASCADE, related_name='adjustments')
    
    ADJUSTMENT_CATEGORY_LTV = 'ltv'
    ADJUSTMENT_CATEGORY_FICO = 'fico'
    ADJUSTMENT_CATEGORY_CHOICES = (
        (ADJUSTMENT_CATEGORY_LTV, 'LTV'),
        (ADJUSTMENT_CATEGORY_FICO, 'FICO'),
    )
    
    category = models.CharField(max_length=20, choices=ADJUSTMENT_CATEGORY_CHOICES)
    
    condition_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    condition_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    condition_value = models.CharField(max_length=100, blank=True, null=True)
    
    rate_adjustment = models.DecimalField(max_digits=6, decimal_places=3, default=Decimal('0.000'))
    price_adjustment = models.DecimalField(max_digits=6, decimal_places=3, default=Decimal('0.000'))

    class Meta:
        app_label = 'loans'
