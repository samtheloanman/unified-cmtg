"""
LocationPage - Standalone location pages for SEO

URL: /locations/{city-state}/
Example: /locations/new-york-ny/

Each location represents a city where CMRE has virtual office presence.
"""

from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.search import index
from cms.services.proximity import ProximityService


class LocationIndexPage(Page):
    """
    Parent page for all locations: /locations/
    """
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]
    
    subpage_types = ['cms.LocationPage']
    max_count = 1  # Only one location index

    def get_context(self, request):
        context = super().get_context(request)
        context['locations'] = LocationPage.objects.live().order_by('city', 'state')
        return context


class LocationPage(Page):
    """
    Individual location page for SEO.
    
    URL: /locations/{city-state}/
    Example: /locations/los-angeles-ca/
    """
    
    # Location details
    address = models.CharField(max_length=300)
    second_address = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    state_name = models.CharField(max_length=100, blank=True)
    zipcode = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=100, default='USA')
    
    # Contact
    phone = models.CharField(max_length=20, default='866-976-5669')
    
    # GPS coordinates for proximity/maps
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        null=True, 
        blank=True,
        help_text="GPS latitude for maps and proximity"
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        null=True, 
        blank=True,
        help_text="GPS longitude for maps and proximity"
    )
    
    # Link to nearest Office (auto-assigned)
    nearest_office = models.ForeignKey(
        'cms.Office',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='location_pages'
    )
    
    # Content
    intro = RichTextField(
        blank=True,
        help_text="Introductory paragraph for this location"
    )
    
    # Search
    search_fields = Page.search_fields + [
        index.SearchField('city'),
        index.SearchField('state'),
        index.SearchField('address'),
    ]
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('address'),
            FieldPanel('second_address'),
            FieldPanel('city'),
            FieldPanel('state'),
            FieldPanel('zipcode'),
            FieldPanel('phone'),
        ], heading="Location Details"),
        MultiFieldPanel([
            FieldPanel('latitude'),
            FieldPanel('longitude'),
            FieldPanel('nearest_office'),
        ], heading="GPS & Office Assignment"),
        FieldPanel('intro'),
    ]
    
    parent_page_types = ['cms.LocationIndexPage']
    subpage_types = []  # No children

    class Meta:
        verbose_name = "Location Page"
        verbose_name_plural = "Location Pages"

    def __str__(self):
        return f"{self.city}, {self.state}"
    
    @property
    def full_address(self):
        parts = [self.address]
        if self.second_address:
            parts.append(self.second_address)
        parts.append(f"{self.city}, {self.state} {self.zipcode}")
        return ", ".join(parts)
    
    @property
    def google_maps_url(self):
        """Generate Google Maps directions URL."""
        address = self.full_address.replace(' ', '+').replace(',', '%2C')
        return f"https://www.google.com/maps/dir/?api=1&destination={address}"
    
    def save(self, *args, **kwargs):
        # Auto-generate slug if missing
        if not self.slug:
            self.slug = f"{self.city.lower().replace(' ', '-')}-{self.state.lower()}"
        
        # Auto-generate title if missing  
        if not self.title:
            self.title = f"{self.city}, {self.state}"
        
        super().save(*args, **kwargs)
    
    def get_schema_org(self):
        """Generate Schema.org LocalBusiness JSON-LD."""
        return {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": f"Custom Mortgage - {self.city}, {self.state}",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": self.address,
                "addressLocality": self.city,
                "addressRegion": self.state,
                "postalCode": self.zipcode,
                "addressCountry": self.country
            },
            "telephone": self.phone,
            "url": self.full_url,
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": float(self.latitude) if self.latitude else None,
                "longitude": float(self.longitude) if self.longitude else None
            } if self.latitude and self.longitude else None
        }
