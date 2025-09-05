"""
Job models for the Job Scraper application.
"""

from django.db import models
from django.utils import timezone
from django.core.validators import URLValidator
from apps.companies.models import Company


class JobSource(models.Model):
    """Model representing a job source website."""
    
    name = models.CharField(max_length=100, unique=True)
    base_url = models.URLField(validators=[URLValidator()])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Job Source'
        verbose_name_plural = 'Job Sources'
    
    def __str__(self):
        return self.name


class Job(models.Model):
    """Model representing a job posting."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('filled', 'Filled'),
        ('unknown', 'Unknown'),
    ]
    
    title = models.CharField(max_length=200)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    source_url = models.URLField(validators=[URLValidator()])
    source = models.ForeignKey(JobSource, on_delete=models.CASCADE, related_name='jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=3, default='USD')
    employment_type = models.CharField(max_length=50, blank=True)
    experience_level = models.CharField(max_length=50, blank=True)
    remote_allowed = models.BooleanField(default=False)
    posted_date = models.DateTimeField(null=True, blank=True)
    scraped_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scraped_at']
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        unique_together = ['title', 'company', 'source_url']
    
    def __str__(self):
        return f"{self.title} at {self.company.name}"
    
    @property
    def is_recent(self):
        """Check if job was posted within the last 7 days."""
        if not self.posted_date:
            return False
        return (timezone.now() - self.posted_date).days <= 7
    
    @property
    def salary_range(self):
        """Return formatted salary range."""
        if self.salary_min and self.salary_max:
            return f"{self.salary_currency} {self.salary_min:,.0f} - {self.salary_max:,.0f}"
        elif self.salary_min:
            return f"{self.salary_currency} {self.salary_min:,.0f}+"
        elif self.salary_max:
            return f"{self.salary_currency} up to {self.salary_max:,.0f}"
        return "Salary not specified"


class JobSearch(models.Model):
    """Model representing a job search query."""
    
    query = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    max_results = models.PositiveIntegerField(default=50)
    sources = models.ManyToManyField(JobSource, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Job Search'
        verbose_name_plural = 'Job Searches'
    
    def __str__(self):
        location_str = f" in {self.location}" if self.location else ""
        return f"{self.query}{location_str}"


class JobSearchResult(models.Model):
    """Model linking job searches to their results."""
    
    search = models.ForeignKey(JobSearch, on_delete=models.CASCADE, related_name='results')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='search_results')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['search', 'job']
        verbose_name = 'Job Search Result'
        verbose_name_plural = 'Job Search Results'
    
    def __str__(self):
        return f"{self.search} -> {self.job}"

