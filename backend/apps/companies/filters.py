"""
Filters for Companies app.
"""

import django_filters
from django.db.models import Q
from .models import Company


class CompanyFilter(django_filters.FilterSet):
    """Filter for Company model."""
    
    name = django_filters.CharFilter(lookup_expr='icontains')
    industry = django_filters.CharFilter(lookup_expr='icontains')
    location = django_filters.CharFilter(lookup_expr='icontains')
    size = django_filters.ChoiceFilter(choices=Company.SIZE_CHOICES)
    is_verified = django_filters.BooleanFilter()
    has_contact_info = django_filters.BooleanFilter(method='filter_has_contact_info')
    
    # Founded year filters
    founded_after = django_filters.NumberFilter(field_name='founded_year', lookup_expr='gte')
    founded_before = django_filters.NumberFilter(field_name='founded_year', lookup_expr='lte')
    
    # Date filters
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Combined search
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Company
        fields = [
            'name', 'industry', 'location', 'size', 'is_verified',
            'has_contact_info', 'founded_after', 'founded_before',
            'created_after', 'created_before', 'search'
        ]
    
    def filter_has_contact_info(self, queryset, name, value):
        """Filter companies that have contact information."""
        if value is True:
            return queryset.exclude(Q(email='') & Q(website=''))
        elif value is False:
            return queryset.filter(Q(email='') & Q(website=''))
        return queryset
    
    def filter_search(self, queryset, name, value):
        """Filter by search term across multiple fields."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(name__icontains=value) |
            Q(industry__icontains=value) |
            Q(location__icontains=value) |
            Q(description__icontains=value)
        )
