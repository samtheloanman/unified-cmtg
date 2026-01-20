from django.db import models

class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    state_name = models.CharField(max_length=100)
    
    # GPS for proximity
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    # Demographics (optional, for AI content)
    population = models.IntegerField(null=True, blank=True)
    median_income = models.IntegerField(null=True, blank=True)
    
    # SEO
    slug = models.SlugField()
    
    # Phased Rollout
    priority = models.IntegerField(default=999, help_text="Lower number = higher priority")
    launched_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Cities"
        unique_together = ('slug', 'state')
        indexes = [
            models.Index(fields=['state', 'slug']),
            models.Index(fields=['priority']),
        ]

    def __str__(self):
        return f"{self.name}, {self.state}"
    
    @property
    def is_launched(self):
        return self.launched_at is not None
