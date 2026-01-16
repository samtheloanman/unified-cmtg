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

from .models import City, LocalProgramPage

class CityViewSet(SnippetViewSet):
    model = City
    menu_label = 'Cities'
    menu_icon = 'globe'
    menu_order = 205
    add_to_settings_menu = False
    list_display = ('name', 'state', 'population', 'median_income')
    list_filter = ('state',)
    search_fields = ('name', 'state', 'slug')

register_snippet(CityViewSet)

class LocalPageViewSet(SnippetViewSet):
    model = LocalProgramPage
    menu_label = 'Local Pages'
    menu_icon = 'doc-full-inverse'
    menu_order = 150 # Near Pages
    list_display = ('title', 'program', 'city', 'assigned_office')
    list_filter = ('program', 'city__state')
    search_fields = ('title', 'program__title', 'city__name')

register_snippet(LocalPageViewSet)
