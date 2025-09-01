"""
Serializers for Companies app.
"""

from rest_framework import serializers
from .models import Company, CompanyContact


class CompanyContactSerializer(serializers.ModelSerializer):
    """Serializer for CompanyContact model."""
    
    class Meta:
        model = CompanyContact
        fields = [
            'id', 'contact_type', 'value', 'is_primary', 
            'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Company model."""
    
    contacts = CompanyContactSerializer(many=True, read_only=True)
    job_count = serializers.ReadOnlyField()
    recent_jobs_count = serializers.ReadOnlyField()
    has_contact_info = serializers.ReadOnlyField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'website', 'email', 'description', 'industry',
            'size', 'location', 'founded_year', 'logo_url', 'linkedin_url',
            'is_verified', 'job_count', 'recent_jobs_count', 'has_contact_info',
            'contacts', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CompanyListSerializer(serializers.ModelSerializer):
    """Simplified serializer for company lists."""
    
    job_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'website', 'industry', 'size', 
            'location', 'job_count', 'is_verified'
        ]
