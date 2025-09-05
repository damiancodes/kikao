"""
URL configuration for Companies app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'companies', views.CompanyViewSet)
router.register(r'company-contacts', views.CompanyContactViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
]
