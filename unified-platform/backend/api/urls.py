from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('quote/', views.QuoteView.as_view(), name='quote'),
]
