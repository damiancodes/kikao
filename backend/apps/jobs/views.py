"""
Views for Jobs app.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Job, JobSource, JobSearch, JobSearchResult
from .serializers import (
    JobSerializer, JobSourceSerializer, JobSearchSerializer,
    JobSearchResultSerializer, JobSearchRequestSerializer
)
from .filters import JobFilter
from apps.scraping.tasks import scrape_jobs_task


class JobSourceViewSet(viewsets.ModelViewSet):
    """ViewSet for JobSource model."""
    
    queryset = JobSource.objects.all()
    serializer_class = JobSourceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'base_url']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class JobViewSet(viewsets.ModelViewSet):
    """ViewSet for Job model."""
    
    queryset = Job.objects.select_related('company', 'source').all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = JobFilter
    search_fields = ['title', 'company__name', 'location', 'description']
    ordering_fields = ['title', 'scraped_at', 'posted_date', 'salary_min', 'salary_max']
    ordering = ['-scraped_at']
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent jobs (posted within last 7 days)."""
        recent_jobs = self.queryset.filter(
            posted_date__gte=timezone.now() - timezone.timedelta(days=7)
        )
        serializer = self.get_serializer(recent_jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_company(self, request):
        """Get jobs grouped by company."""
        company_id = request.query_params.get('company_id')
        if company_id:
            jobs = self.queryset.filter(company_id=company_id)
            serializer = self.get_serializer(jobs, many=True)
            return Response(serializer.data)
        return Response({'error': 'company_id parameter required'}, status=400)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get job statistics."""
        stats = {
            'total_jobs': self.queryset.count(),
            'active_jobs': self.queryset.filter(status='active').count(),
            'recent_jobs': self.queryset.filter(
                posted_date__gte=timezone.now() - timezone.timedelta(days=7)
            ).count(),
            'companies_count': self.queryset.values('company').distinct().count(),
            'sources_count': self.queryset.values('source').distinct().count(),
            'remote_jobs': self.queryset.filter(remote_allowed=True).count(),
        }
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export jobs to CSV."""
        from django.http import HttpResponse
        import csv
        import io
        
        # Get filtered jobs
        jobs = self.filter_queryset(self.get_queryset())
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="jobs_export.csv"'
        
        writer = csv.writer(response)
        
        # Write headers
        writer.writerow([
            'Title', 'Company', 'Location', 'Source', 'Type', 'Status', 
            'Salary Min', 'Salary Max', 'Currency', 'Remote', 'Posted Date', 'URL'
        ])
        
        # Write job data
        for job in jobs:
            writer.writerow([
                job.title,
                job.company.name if job.company else 'N/A',
                job.location,
                job.source.name if job.source else 'N/A',
                job.employment_type,
                job.status,
                job.salary_min or '',
                job.salary_max or '',
                job.salary_currency,
                'Yes' if job.remote_allowed else 'No',
                job.posted_date.strftime('%Y-%m-%d') if job.posted_date else '',
                job.source_url
            ])
        
        return response


class JobSearchViewSet(viewsets.ModelViewSet):
    """ViewSet for JobSearch model."""
    
    queryset = JobSearch.objects.prefetch_related('sources').all()
    serializer_class = JobSearchSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['query', 'location']
    ordering_fields = ['query', 'created_at']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a job search by triggering scraping."""
        job_search = self.get_object()
        
        try:
            # Run scraping synchronously for now (without Celery)
            result = scrape_jobs_task(
                query=job_search.query,
                location=job_search.location,
                max_results=job_search.max_results,
                source_ids=list(job_search.sources.values_list('id', flat=True))
            )
            
            return Response({
                'message': 'Job search completed successfully',
                'search_id': job_search.id,
                'jobs_found': result.get('jobs_found', 0),
                'jobs_created': result.get('jobs_created', 0)
            })
        except Exception as e:
            return Response({
                'error': f'Job search failed: {str(e)}'
            }, status=500)
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get results for a job search."""
        job_search = self.get_object()
        results = JobSearchResult.objects.filter(search=job_search).select_related('job')
        serializer = JobSearchResultSerializer(results, many=True)
        return Response(serializer.data)


class JobSearchResultViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for JobSearchResult model."""
    
    queryset = JobSearchResult.objects.select_related('search', 'job').all()
    serializer_class = JobSearchResultSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['search']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


def dashboard_view(request):
    """Main dashboard view."""
    context = {
        'total_jobs': Job.objects.count(),
        'active_jobs': Job.objects.filter(status='active').count(),
        'companies_count': Job.objects.values('company').distinct().count(),
        'sources_count': JobSource.objects.filter(is_active=True).count(),
    }
    return render(request, 'jobs/dashboard.html', context)


def job_list_view(request):
    """Job list view for the dashboard."""
    jobs = Job.objects.select_related('company', 'source').all()[:50]
    context = {'jobs': jobs}
    return render(request, 'jobs/job_list.html', context)
