from django.db import models

class SEOContentCache(models.Model):
    """
    Cache for AI-generated SEO content to prevent regeneration loops 
    and store metadata for programmatic pages.
    """
    url_path = models.CharField(max_length=255, unique=True, db_index=True)
    title_tag = models.CharField(max_length=255)
    meta_description = models.TextField()
    h1_header = models.CharField(max_length=255)
    
    # Content storage
    content_body = models.TextField(help_text="HTML or Markdown content")
    schema_json = models.JSONField(default=dict, blank=True)
    
    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    generation_params = models.JSONField(default=dict, blank=True, help_text="Parameters used to generate this content")

    class Meta:
        indexes = [
            models.Index(fields=['url_path']),
        ]
        verbose_name_plural = "SEO Content Caches"

    def __str__(self):
        return f"Cache for {self.url_path} ({self.last_updated.strftime('%Y-%m-%d')})"
