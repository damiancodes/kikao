"""
URL configuration for Jobs app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'sources', views.JobSourceViewSet)
router.register(r'jobs', views.JobViewSet)
router.register(r'searches', views.JobSearchViewSet)
router.register(r'search-results', views.JobSearchResultViewSet)


urlpatterns = [
    # Dashboard views
    path('', views.dashboard_view, name='dashboard'),
    path('jobs/', views.job_list_view, name='job_list'),
    
    # API endpoints
    path('api/', include(router.urls)),
]
