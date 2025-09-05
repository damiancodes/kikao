"""
Views for Scraping app.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import ScrapingSession, ScrapingError, ScrapingLog
from .serializers import (
    ScrapingSessionSerializer, ScrapingErrorSerializer, ScrapingLogSerializer
)
from .tasks import scrape_jobs_task, cleanup_old_sessions, update_job_statuses


class ScrapingSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for ScrapingSession model."""
    
    queryset = ScrapingSession.objects.all()
    serializer_class = ScrapingSessionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'query', 'location']
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed scraping session."""
        session = self.get_object()
        
        if session.status not in ['failed', 'cancelled']:
            return Response(
                {'error': 'Can only retry failed or cancelled sessions'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Trigger new scraping task
        task = scrape_jobs_task.delay(
            query=session.query,
            location=session.location,
            max_results=session.max_results
        )
        
        return Response({
            'message': 'Scraping session retried',
            'task_id': task.id,
            'session_id': session.id
        })
    
    @action(detail=False, methods=['post'])
    def cleanup(self, request):
        """Clean up old scraping sessions."""
        task = cleanup_old_sessions.delay()
        return Response({
            'message': 'Cleanup task initiated',
            'task_id': task.id
        })
    
    @action(detail=False, methods=['post'])
    def update_statuses(self, request):
        """Update job statuses."""
        task = update_job_statuses.delay()
        return Response({
            'message': 'Job status update task initiated',
            'task_id': task.id
        })


class ScrapingErrorViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ScrapingError model."""
    
    queryset = ScrapingError.objects.select_related('session').all()
    serializer_class = ScrapingErrorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['session', 'error_type', 'source']


class ScrapingLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ScrapingLog model."""
    
    queryset = ScrapingLog.objects.select_related('session').all()
    serializer_class = ScrapingLogSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['session', 'level', 'source']



