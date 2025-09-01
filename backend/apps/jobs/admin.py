"""
Admin configuration for Jobs app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Job, JobSource, JobSearch, JobSearchResult


@admin.register(JobSource)
class JobSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_url', 'is_active', 'job_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'base_url']
    readonly_fields = ['created_at', 'updated_at']
    
    def job_count(self, obj):
        return obj.jobs.count()
    job_count.short_description = 'Jobs Count'


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'company', 'location', 'source', 'status', 
        'salary_range', 'is_recent', 'scraped_at'
    ]
    list_filter = [
        'status', 'source', 'employment_type', 'experience_level',
        'remote_allowed', 'scraped_at', 'posted_date'
    ]
    search_fields = ['title', 'company__name', 'location', 'description']
    readonly_fields = ['scraped_at', 'updated_at']
    raw_id_fields = ['company']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'company', 'location', 'description')
        }),
        ('Source Information', {
            'fields': ('source', 'source_url', 'status')
        }),
        ('Job Details', {
            'fields': (
                'employment_type', 'experience_level', 'remote_allowed',
                'salary_min', 'salary_max', 'salary_currency'
            )
        }),
        ('Timestamps', {
            'fields': ('posted_date', 'scraped_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def salary_range(self, obj):
        return obj.salary_range
    salary_range.short_description = 'Salary Range'


@admin.register(JobSearch)
class JobSearchAdmin(admin.ModelAdmin):
    list_display = ['query', 'location', 'max_results', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['query', 'location']
    filter_horizontal = ['sources']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(JobSearchResult)
class JobSearchResultAdmin(admin.ModelAdmin):
    list_display = ['search', 'job', 'created_at']
    list_filter = ['created_at', 'search']
    search_fields = ['search__query', 'job__title', 'job__company__name']
    readonly_fields = ['created_at']
