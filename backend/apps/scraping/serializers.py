"""
Serializers for Scraping app.
"""

from rest_framework import serializers
from .models import ScrapingSession, ScrapingError, ScrapingLog


class ScrapingLogSerializer(serializers.ModelSerializer):
    """Serializer for ScrapingLog model."""
    
    class Meta:
        model = ScrapingLog
        fields = [
            'id', 'session', 'level', 'message', 'source', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ScrapingErrorSerializer(serializers.ModelSerializer):
    """Serializer for ScrapingError model."""
    
    class Meta:
        model = ScrapingError
        fields = [
            'id', 'session', 'error_type', 'message', 'url', 'source', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ScrapingSessionSerializer(serializers.ModelSerializer):
    """Serializer for ScrapingSession model."""
    
    errors = ScrapingErrorSerializer(many=True, read_only=True)
    logs = ScrapingLogSerializer(many=True, read_only=True)
    duration = serializers.ReadOnlyField()
    success_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = ScrapingSession
        fields = [
            'id', 'query', 'location', 'max_results', 'status',
            'jobs_found', 'jobs_processed', 'jobs_created', 'jobs_updated',
            'errors_count', 'started_at', 'completed_at', 'created_at',
            'updated_at', 'duration', 'success_rate', 'errors', 'logs'
        ]
        read_only_fields = [
            'id', 'jobs_found', 'jobs_processed', 'jobs_created', 'jobs_updated',
            'errors_count', 'started_at', 'completed_at', 'created_at', 'updated_at'
        ]





