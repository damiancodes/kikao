"""
Admin configuration for Companies app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Company, CompanyContact


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'industry', 'size', 'location', 'job_count', 
        'has_contact_info', 'is_verified', 'created_at'
    ]
    list_filter = [
        'industry', 'size', 'is_verified', 'created_at'
    ]
    search_fields = ['name', 'industry', 'location', 'description']
    readonly_fields = ['created_at', 'updated_at', 'job_count', 'recent_jobs_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'industry', 'size', 'location', 'founded_year')
        }),
        ('Contact Information', {
            'fields': ('website', 'email', 'linkedin_url', 'logo_url')
        }),
        ('Verification', {
            'fields': ('is_verified',)
        }),
        ('Statistics', {
            'fields': ('job_count', 'recent_jobs_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def job_count(self, obj):
        return obj.job_count
    job_count.short_description = 'Active Jobs'
    
    def has_contact_info(self, obj):
        return obj.has_contact_info
    has_contact_info.boolean = True
    has_contact_info.short_description = 'Has Contact Info'


@admin.register(CompanyContact)
class CompanyContactAdmin(admin.ModelAdmin):
    list_display = [
        'company', 'contact_type', 'value', 'is_primary', 
        'is_verified', 'created_at'
    ]
    list_filter = [
        'contact_type', 'is_primary', 'is_verified', 'created_at'
    ]
    search_fields = ['company__name', 'value']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['company']
