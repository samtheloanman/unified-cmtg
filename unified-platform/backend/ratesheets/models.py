from django.db import models
from common.models import TimestampedModel
<<<<<<< HEAD

class RateSheet(TimestampedModel):
    """
    Represents a lender's rate sheet file (PDF/CSV/Excel).
    Tracks the processing status and results of ingestion.
    """
    
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_PROCESSED = 'processed'
    STATUS_FAILED = 'failed'
    
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_PROCESSED, 'Processed'),
        (STATUS_FAILED, 'Failed'),
    )
    
    lender = models.ForeignKey(
        'pricing.Lender',
        on_delete=models.CASCADE,
        related_name='rate_sheets',
        help_text="Lender this rate sheet belongs to"
    )
    name = models.CharField(
        max_length=255,
        help_text="Descriptive name (e.g. 'Jan 2026 Sheet')"
    )
    file = models.FileField(
        upload_to='rate_sheets/%Y/%m/',
        help_text="Upload rate sheet file (PDF, CSV, XLSX)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        help_text="Current processing status"
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when processing completed"
    )
    log = models.TextField(
        blank=True,
        help_text="Processing logs and errors"
    )
    
    def __str__(self):
        return f"{self.lender} - {self.name} ({self.get_status_display()})"

=======

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
>>>>>>> origin/jules/phase1-foundation-10297780927730413954
