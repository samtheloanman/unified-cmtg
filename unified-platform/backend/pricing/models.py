from django.db import models
from common.models import TimestampedModel

# Placeholder for Phase 2
class Lender(TimestampedModel):
    company_name = models.CharField(max_length=500)

    def __str__(self):
        return self.company_name
