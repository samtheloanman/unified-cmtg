from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.http import JsonResponse
from api.views import health_check, QuoteView  # Add QuoteView here
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

# Wagtail API v2 for headless CMS
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.images.api.v2.views import ImagesAPIViewSet
from wagtail.documents.api.v2.views import DocumentsAPIViewSet

# Create the API router
api_router = WagtailAPIRouter('wagtailapi')
api_router.register_endpoint('pages', PagesAPIViewSet)
api_router.register_endpoint('images', ImagesAPIViewSet)
api_router.register_endpoint('documents', DocumentsAPIViewSet)

# Simple root endpoint for headless setup
def backend_root(request):
    return JsonResponse({
        'message': 'Unified CMTG Platform - Headless CMS Backend',
        'frontend': 'http://localhost:3001',
        'api': {
            'pages': '/api/v2/pages/',
            'images': '/api/v2/images/',
            'documents': '/api/v2/documents/',
            'quote': '/api/v1/quote/',
        },
        'admin': '/admin/',
        'status': 'operational'
    })

urlpatterns = [
    path("", backend_root, name='root'),  # JSON response for root
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("api/v2/", api_router.urls),  # Wagtail headless API
    path("api/v1/quote/", QuoteView.as_view(), name='quote'),
    path("api/v1/", include("api.urls")),
    # Note: Wagtail URLs removed from root to prevent template rendering issues
    # All content is served via API to Next.js frontend
]
