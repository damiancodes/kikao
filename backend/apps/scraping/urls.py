"""
URL configuration for Scraping app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'sessions', views.ScrapingSessionViewSet)
router.register(r'errors', views.ScrapingErrorViewSet)
router.register(r'logs', views.ScrapingLogViewSet)

# URL patterns
urlpatterns = [
    path('api/', include(router.urls)),
]
