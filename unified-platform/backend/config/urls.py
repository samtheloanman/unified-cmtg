from django.contrib import admin
from django.urls import path, include
from api.views import health_check, QuoteView  # Add QuoteView here
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("api/v1/quote/", QuoteView.as_view(), name='quote'),  # ADD THIS LINE BEFORE include
    path("api/v1/", include("api.urls")),
    path("", include(wagtail_urls)),
]
