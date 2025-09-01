"""
Filters for Jobs app.
"""

import django_filters
from django.db.models import Q
from .models import Job, JobSource


class JobFilter(django_filters.FilterSet):
    """Filter for Job model."""
    
    title = django_filters.CharFilter(lookup_expr='icontains')
    company_name = django_filters.CharFilter(field_name='company__name', lookup_expr='icontains')
    location = django_filters.CharFilter(lookup_expr='icontains')
    source = django_filters.ModelChoiceFilter(queryset=JobSource.objects.filter(is_active=True))
    status = django_filters.ChoiceFilter(choices=Job.STATUS_CHOICES)
    employment_type = django_filters.CharFilter(lookup_expr='icontains')
    experience_level = django_filters.CharFilter(lookup_expr='icontains')
    remote_allowed = django_filters.BooleanFilter()
    
    # Salary filters
    salary_min = django_filters.NumberFilter(field_name='salary_min', lookup_expr='gte')
    salary_max = django_filters.NumberFilter(field_name='salary_max', lookup_expr='lte')
    
    # Date filters
    posted_after = django_filters.DateTimeFilter(field_name='posted_date', lookup_expr='gte')
    posted_before = django_filters.DateTimeFilter(field_name='posted_date', lookup_expr='lte')
    scraped_after = django_filters.DateTimeFilter(field_name='scraped_at', lookup_expr='gte')
    scraped_before = django_filters.DateTimeFilter(field_name='scraped_at', lookup_expr='lte')
    
    # Combined search
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Job
        fields = [
            'title', 'company_name', 'location', 'source', 'status',
            'employment_type', 'experience_level', 'remote_allowed',
            'salary_min', 'salary_max', 'posted_after', 'posted_before',
            'scraped_after', 'scraped_before', 'search'
        ]
    
    def filter_search(self, queryset, name, value):
        """Filter by search term across multiple fields."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(title__icontains=value) |
            Q(company__name__icontains=value) |
            Q(location__icontains=value) |
            Q(description__icontains=value)
        )
