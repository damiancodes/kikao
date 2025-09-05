"""
Scraping models for the Job Scraper application.
"""

from django.db import models
from django.utils import timezone


class ScrapingSession(models.Model):
    """Model representing a scraping session."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    query = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    max_results = models.PositiveIntegerField(default=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    jobs_found = models.PositiveIntegerField(default=0)
    jobs_processed = models.PositiveIntegerField(default=0)
    jobs_created = models.PositiveIntegerField(default=0)
    jobs_updated = models.PositiveIntegerField(default=0)
    errors_count = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Scraping Session'
        verbose_name_plural = 'Scraping Sessions'
    
    def __str__(self):
        location_str = f" in {self.location}" if self.location else ""
        return f"{self.query}{location_str} - {self.status}"
    
    @property
    def duration(self):
        """Calculate session duration."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return timezone.now() - self.started_at
        return None
    
    @property
    def success_rate(self):
        """Calculate success rate."""
        if self.jobs_processed == 0:
            return 0
        return (self.jobs_created + self.jobs_updated) / self.jobs_processed * 100


class ScrapingError(models.Model):
    """Model representing scraping errors."""
    
    ERROR_TYPES = [
        ('network', 'Network Error'),
        ('parsing', 'Parsing Error'),
        ('timeout', 'Timeout Error'),
        ('blocked', 'Blocked/Forbidden'),
        ('not_found', 'Not Found'),
        ('other', 'Other'),
    ]
    
    session = models.ForeignKey(ScrapingSession, on_delete=models.CASCADE, related_name='errors')
    error_type = models.CharField(max_length=20, choices=ERROR_TYPES)
    message = models.TextField()
    url = models.URLField(blank=True)
    source = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Scraping Error'
        verbose_name_plural = 'Scraping Errors'
    
    def __str__(self):
        return f"{self.session} - {self.error_type}: {self.message[:50]}"


class ScrapingLog(models.Model):
    """Model representing scraping logs."""
    
    LOG_LEVELS = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    session = models.ForeignKey(ScrapingSession, on_delete=models.CASCADE, related_name='logs')
    level = models.CharField(max_length=20, choices=LOG_LEVELS)
    message = models.TextField()
    source = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Scraping Log'
        verbose_name_plural = 'Scraping Logs'
    
    def __str__(self):
        return f"{self.session} - {self.level}: {self.message[:50]}"



