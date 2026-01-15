from django.db import models

class OfficeManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)

    def headquarters(self):
        return self.get(is_headquarters=True)

class Office(models.Model):
    """
    Physical CMRE office location for SEO proximity mapping.

    Each LocalProgramPage is assigned to the nearest office
    using Haversine distance formula.
    """

    # Basic info
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zipcode = models.CharField(max_length=10)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    # GPS coordinates for Haversine distance calculation
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="GPS latitude for proximity calculations"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="GPS longitude for proximity calculations"
    )

    # Flags
    is_active = models.BooleanField(default=True)
    is_headquarters = models.BooleanField(
        default=False,
        help_text="Fallback office if city > 500 miles from nearest"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OfficeManager()

    class Meta:
        ordering = ['state', 'city']
        verbose_name = "Office"
        verbose_name_plural = "Offices"

    def __str__(self):
        return f"{self.name} - {self.city}, {self.state}"

    @property
    def full_address(self):
        return f"{self.address}, {self.city}, {self.state} {self.zipcode}"
