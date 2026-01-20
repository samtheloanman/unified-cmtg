from django.db import models
from wagtail.models import TranslatableMixin
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

class LinkBlock(blocks.StructBlock):
    link_text = blocks.CharBlock(required=True, help_text="Text to display for the link")
    link_url = blocks.CharBlock(required=False, help_text="External URL (e.g., https://google.com)")
    link_page = blocks.PageChooserBlock(required=False, help_text="Internal Page Link")
    open_in_new_tab = blocks.BooleanBlock(required=False, default=False)
    
    class Meta:
        icon = "link"
        label = "Link"

class SubMenuBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True)
    items = blocks.ListBlock(LinkBlock())

    class Meta:
        icon = "list-ul"
        label = "Sub Menu"

@register_snippet
class NavigationMenu(TranslatableMixin, models.Model):
    name = models.CharField(max_length=255)
    items = StreamField([
        ('link', LinkBlock()),
        ('sub_menu', SubMenuBlock()),
    ], use_json_field=True)

    raw_html = models.TextField(blank=True, help_text="Override authentication items with raw HTML. Takes precedence over items.")

    panels = [
        FieldPanel('name'),
        FieldPanel('items'),
        FieldPanel('raw_html'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Navigation Menu"
        constraints = [
            models.UniqueConstraint(fields=['translation_key', 'locale'], name='unique_translation_key_locale_cms_navigationmenu')
        ]

@register_snippet
class SiteConfiguration(TranslatableMixin, models.Model):
    site_name = models.CharField(max_length=255, default="Custom Mortgage")
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    # Contact Info
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    # Social Links
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    
    # Raw HTML Footer Override
    footer_raw_html = models.TextField(blank=True, help_text="Override entire footer with raw HTML.")

    panels = [
        FieldPanel('site_name'),
        FieldPanel('logo'),
        MultiFieldPanel([
            FieldPanel('phone_number'),
            FieldPanel('email'),
            FieldPanel('address'),
        ], heading="Contact Information"),
        MultiFieldPanel([
            FieldPanel('facebook'),
            FieldPanel('twitter'),
            FieldPanel('linkedin'),
            FieldPanel('instagram'),
        ], heading="Social Media"),
        FieldPanel('footer_raw_html'),
    ]

    def __str__(self):
        return self.site_name

    class Meta:
        verbose_name = "Site Configuration"
        constraints = [
            models.UniqueConstraint(fields=['translation_key', 'locale'], name='unique_translation_key_locale_cms_siteconfiguration')
        ]
