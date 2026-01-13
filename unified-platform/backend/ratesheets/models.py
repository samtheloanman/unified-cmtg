from django.db import models
from common.models import TimestampedModel

class RateSheet(TimestampedModel):
    # Lender foreign key - using string reference.
    # Note: Migration will fail if pricing.Lender doesn't exist.
    # For now, we assume Phase 2 will land soon, or we can make it nullable/temporary.
    # Given the strict instruction, I will include it.
    lender = models.ForeignKey('pricing.Lender', on_delete=models.CASCADE, related_name='rate_sheets')

    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='rate_sheets/%Y/%m/')

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('PROCESSED', 'Processed'),
        ('FAILED', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    processed_at = models.DateTimeField(null=True, blank=True)
    log = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.status})"
