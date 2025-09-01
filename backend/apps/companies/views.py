"""
Views for Companies app.
"""

from django.db import models
from django.db.models import Count
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Company, CompanyContact
from .serializers import CompanySerializer, CompanyListSerializer, CompanyContactSerializer
from .filters import CompanyFilter


class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet for Company model."""
    
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CompanyFilter
    search_fields = ['name', 'industry', 'location', 'description']
    ordering_fields = ['name', 'created_at', 'founded_year']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Use different serializers for list and detail views."""
        if self.action == 'list':
            return CompanyListSerializer
        return CompanySerializer
    
    @action(detail=True, methods=['get'])
    def jobs(self, request, pk=None):
        """Get jobs for a specific company."""
        company = self.get_object()
        jobs = company.jobs.all()
        from apps.jobs.serializers import JobSerializer
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get company statistics."""
        stats = {
            'total_companies': self.queryset.count(),
            'verified_companies': self.queryset.filter(is_verified=True).count(),
            'companies_with_contact': self.queryset.exclude(
                models.Q(email='') & models.Q(website='')
            ).count(),
            'top_industries': self.queryset.exclude(industry='').values('industry').annotate(
                count=Count('industry')
            ).order_by('-count')[:10],
        }
        return Response(stats)


class CompanyContactViewSet(viewsets.ModelViewSet):
    """ViewSet for CompanyContact model."""
    
    queryset = CompanyContact.objects.select_related('company').all()
    serializer_class = CompanyContactSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['company', 'contact_type', 'is_primary', 'is_verified']
    ordering_fields = ['contact_type', 'created_at']
    ordering = ['-is_primary', 'contact_type']
