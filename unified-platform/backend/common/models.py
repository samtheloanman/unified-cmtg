from django.db import models

class TimestampedModel(models.Model):
<<<<<<< HEAD
    """
    Abstract base model with created_at and updated_at fields.
    """
=======
>>>>>>> origin/jules/phase1-foundation-10297780927730413954
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
