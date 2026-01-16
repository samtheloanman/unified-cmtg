from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.images.models import Image

class BlogIndexPage(Page):
    """Container for blog posts"""
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    api_fields = [
        APIField('intro'),
    ]

    subpage_types = ['cms.BlogPage']
    max_count = 1

class BlogPage(Page):
    """Blog posts / news articles."""
    date = models.DateField("Post date")
    author = models.CharField(max_length=100)
    intro = models.TextField(blank=True)
    body = RichTextField(blank=True)
    featured_image = models.ForeignKey(
        Image, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('featured_image'),
        FieldPanel('date'),
        FieldPanel('author'),
        FieldPanel('intro'),
        FieldPanel('body'),
    ]

    api_fields = [
        APIField('date'),
        APIField('author'),
        APIField('intro'),
        APIField('body'),
        APIField('featured_image'),
    ]

    parent_page_types = ['cms.BlogIndexPage']
