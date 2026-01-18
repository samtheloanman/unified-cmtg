from django.urls import path
from . import views

urlpatterns = [
    # Health check
    path('health/', views.health_check, name='health_check'),

    # Locations
    path('locations/', views.location_list, name='location_list'),
    path('locations/nearest/', views.location_nearest, name='location_nearest'),
    path('locations/<slug:slug>/', views.location_detail, name='location_detail'),

    # Pricing & quotes
    path('quote/', views.QuoteView.as_view(), name='quote'),

    # Lead submission (Floify integration)
    path('leads/', views.LeadSubmitView.as_view(), name='lead_submit'),

    # Floify webhooks
    path('webhooks/floify/', views.floify_webhook, name='floify_webhook'),
]
