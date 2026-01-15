from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from .models import Office

class OfficeViewSet(SnippetViewSet):
    model = Office
    menu_label = 'Offices'
    menu_icon = 'site'
    menu_order = 200
    add_to_settings_menu = False
    list_display = ('name', 'city', 'state', 'phone', 'is_headquarters', 'is_active')
    list_filter = ('state', 'is_active', 'is_headquarters')
    search_fields = ('name', 'city', 'address')

register_snippet(OfficeViewSet)
