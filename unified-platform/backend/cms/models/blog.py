from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.images.models import Image
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

# =============================================================================
# BLOG
# =============================================================================

class BlogIndexPage(Page):
    """Index page for blog posts"""
    intro = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    subpage_types = ['cms.BlogPage']
    max_count = 1

    def get_context(self, request):
        context = super().get_context(request)
        context['posts'] = BlogPage.objects.child_of(self).live().order_by('-date')
        return context

    api_fields = [
        APIField('intro'),
    ]


class BlogPage(Page):
    """Standard blog post"""
    date = models.DateField("Post date")
    author = models.CharField(max_length=255, blank=True)

    body = StreamField([
        ('heading', blocks.CharBlock(form_classname="title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
    ], use_json_field=True)

    featured_image = models.ForeignKey(
        Image, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('author'),
        FieldPanel('featured_image'),
        FieldPanel('body'),
    ]

    api_fields = [
        APIField('date'),
        APIField('author'),
        APIField('body'),
        APIField('featured_image'),
    ]

    parent_page_types = ['cms.BlogIndexPage']
