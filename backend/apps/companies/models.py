"""
Company models for the Job Scraper application.
"""

from django.db import models
from django.core.validators import URLValidator, EmailValidator
from django.utils import timezone


class Company(models.Model):
    """Model representing a company."""
    
    SIZE_CHOICES = [
        ('startup', 'Startup (1-10)'),
        ('small', 'Small (11-50)'),
        ('medium', 'Medium (51-200)'),
        ('large', 'Large (201-1000)'),
        ('enterprise', 'Enterprise (1000+)'),
        ('unknown', 'Unknown'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    website = models.URLField(validators=[URLValidator()], blank=True)
    email = models.EmailField(validators=[EmailValidator()], blank=True)
    description = models.TextField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, default='unknown')
    location = models.CharField(max_length=200, blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    logo_url = models.URLField(validators=[URLValidator()], blank=True)
    linkedin_url = models.URLField(validators=[URLValidator()], blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
    
    def __str__(self):
        return self.name
    
    @property
    def job_count(self):
        """Return the number of active jobs for this company."""
        return self.jobs.filter(status='active').count()
    
    @property
    def recent_jobs_count(self):
        """Return the number of jobs posted in the last 30 days."""
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        return self.jobs.filter(
            posted_date__gte=thirty_days_ago,
            status='active'
        ).count()
    
    @property
    def has_contact_info(self):
        """Check if company has contact information."""
        return bool(self.email or self.website)


class CompanyContact(models.Model):
    """Model representing company contact information."""
    
    CONTACT_TYPES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
        ('facebook', 'Facebook'),
        ('other', 'Other'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='contacts')
    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPES)
    value = models.CharField(max_length=200)
    is_primary = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_primary', 'contact_type']
        verbose_name = 'Company Contact'
        verbose_name_plural = 'Company Contacts'
        unique_together = ['company', 'contact_type', 'value']
    
    def __str__(self):
        return f"{self.company.name} - {self.contact_type}: {self.value}"



