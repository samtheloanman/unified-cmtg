from django.urls import path
from .views import health_check, QuoteView

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('quote/', QuoteView.as_view(), name='quote'),
]
