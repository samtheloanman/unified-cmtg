from django.db import models
from common.models import TimestampedModel

class Lender(TimestampedModel):
    company_name = models.CharField(max_length=500)
    # Changed from ArrayField to JSONField for SQLite compatibility in dev
    include_states = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.company_name

class ProgramType(TimestampedModel):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, blank=True)
    loan_type = models.CharField(max_length=50, blank=True)
    # Changed from ArrayField to JSONField
    property_types = models.JSONField(default=list, blank=True)
    entity_types = models.JSONField(default=list, blank=True)
    purposes = models.JSONField(default=list, blank=True)
    occupancy = models.JSONField(default=list, blank=True)
    base_min_fico = models.IntegerField(default=0)
    base_max_ltv = models.FloatField(default=0.0)

    def __str__(self):
        return self.name

class LenderProgramOffering(TimestampedModel):
    lender = models.ForeignKey(Lender, on_delete=models.CASCADE)
    program_type = models.ForeignKey(ProgramType, on_delete=models.CASCADE)
    min_rate = models.FloatField(default=0.0)
    max_rate = models.FloatField(default=0.0)
    min_points = models.FloatField(default=0.0)
    max_points = models.FloatField(default=0.0)
    min_fico = models.IntegerField(default=0)
    max_ltv = models.FloatField(default=0.0)
    min_loan = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_loan = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.lender} - {self.program_type}"

class RateAdjustment(TimestampedModel):
    offering = models.ForeignKey(LenderProgramOffering, on_delete=models.CASCADE, related_name='adjustments')
    adjustment_type = models.CharField(max_length=50)
    row_min = models.FloatField(null=True, blank=True)
    row_max = models.FloatField(null=True, blank=True)
    col_min = models.FloatField(null=True, blank=True)
    col_max = models.FloatField(null=True, blank=True)
    adjustment_points = models.FloatField(default=0.0)
