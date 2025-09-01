"""
Serializers for Jobs app.
"""

from rest_framework import serializers
from .models import Job, JobSource, JobSearch, JobSearchResult
from apps.companies.serializers import CompanySerializer


class JobSourceSerializer(serializers.ModelSerializer):
    """Serializer for JobSource model."""
    
    job_count = serializers.SerializerMethodField()
    
    class Meta:
        model = JobSource
        fields = [
            'id', 'name', 'base_url', 'is_active', 
            'job_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_job_count(self, obj):
        return obj.jobs.count()


class JobSerializer(serializers.ModelSerializer):
    """Serializer for Job model."""
    
    company = CompanySerializer(read_only=True)
    company_id = serializers.IntegerField(write_only=True)
    source = JobSourceSerializer(read_only=True)
    source_id = serializers.IntegerField(write_only=True)
    salary_range = serializers.ReadOnlyField()
    is_recent = serializers.ReadOnlyField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company', 'company_id', 'location', 
            'description', 'source_url', 'source', 'source_id',
            'status', 'salary_min', 'salary_max', 'salary_currency',
            'employment_type', 'experience_level', 'remote_allowed',
            'posted_date', 'scraped_at', 'updated_at', 'salary_range', 'is_recent'
        ]
        read_only_fields = ['id', 'scraped_at', 'updated_at']


class JobSearchSerializer(serializers.ModelSerializer):
    """Serializer for JobSearch model."""
    
    sources = JobSourceSerializer(many=True, read_only=True)
    source_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    result_count = serializers.SerializerMethodField()
    
    class Meta:
        model = JobSearch
        fields = [
            'id', 'query', 'location', 'max_results', 'sources',
            'source_ids', 'is_active', 'result_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_result_count(self, obj):
        return obj.results.count()
    
    def create(self, validated_data):
        source_ids = validated_data.pop('source_ids', [])
        job_search = JobSearch.objects.create(**validated_data)
        if source_ids:
            job_search.sources.set(source_ids)
        return job_search
    
    def update(self, instance, validated_data):
        source_ids = validated_data.pop('source_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if source_ids is not None:
            instance.sources.set(source_ids)
        return instance


class JobSearchResultSerializer(serializers.ModelSerializer):
    """Serializer for JobSearchResult model."""
    
    job = JobSerializer(read_only=True)
    
    class Meta:
        model = JobSearchResult
        fields = ['id', 'search', 'job', 'created_at']
        read_only_fields = ['id', 'created_at']


class JobSearchRequestSerializer(serializers.Serializer):
    """Serializer for job search requests."""
    
    query = serializers.CharField(max_length=200)
    location = serializers.CharField(max_length=200, required=False, allow_blank=True)
    max_results = serializers.IntegerField(min_value=1, max_value=1000, default=50)
    source_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    
    def validate_source_ids(self, value):
        """Validate that all source IDs exist and are active."""
        if value:
            from .models import JobSource
            active_sources = JobSource.objects.filter(id__in=value, is_active=True)
            if len(active_sources) != len(value):
                raise serializers.ValidationError("Some source IDs are invalid or inactive.")
        return value
