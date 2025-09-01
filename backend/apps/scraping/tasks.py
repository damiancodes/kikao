"""
Celery tasks for web scraping.
"""

from celery import shared_task
from django.utils import timezone
from django.db import transaction
from .models import ScrapingSession, ScrapingError, ScrapingLog
from apps.jobs.models import Job, JobSource, JobSearchResult
from apps.companies.models import Company
from .scrapers.linkedin import LinkedInScraper
from .scrapers.indeed import IndeedScraper
from .scrapers.glassdoor import GlassdoorScraper
from .scrapers.remoteok import RemoteOKScraper
from .utils import extract_company_info, merge_duplicate_jobs
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def scrape_jobs_task(self, query, location='', max_results=50, source_ids=None):
    """
    Main task for scraping jobs from multiple sources.
    
    Args:
        query (str): Job search query
        location (str): Location filter
        max_results (int): Maximum number of results to scrape
        source_ids (list): List of source IDs to scrape from
    
    Returns:
        dict: Task result with statistics
    """
    # Create scraping session
    session = ScrapingSession.objects.create(
        query=query,
        location=location,
        max_results=max_results,
        status='running',
        started_at=timezone.now()
    )
    
    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'session_id': session.id, 'status': 'Starting scraping...'}
        )
        
        # Get active sources
        if source_ids:
            sources = JobSource.objects.filter(id__in=source_ids, is_active=True)
        else:
            sources = JobSource.objects.filter(is_active=True)
        
        if not sources.exists():
            raise ValueError("No active sources found")
        
        # Initialize scrapers
        scrapers = {
            'linkedin': LinkedInScraper(),
            'indeed': IndeedScraper(),
            'glassdoor': GlassdoorScraper(),
            'remoteok': RemoteOKScraper(),
        }
        
        total_jobs_found = 0
        total_jobs_processed = 0
        total_jobs_created = 0
        total_jobs_updated = 0
        total_errors = 0
        
        # Scrape from each source
        for source in sources:
            try:
                scraper_name = source.name.lower().replace(' ', '')
                if scraper_name not in scrapers:
                    continue
                
                scraper = scrapers[scraper_name]
                
                # Update progress
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'session_id': session.id,
                        'status': f'Scraping from {source.name}...',
                        'current_source': source.name
                    }
                )
                
                # Scrape jobs
                jobs_data = scraper.scrape_jobs(
                    query=query,
                    location=location,
                    max_results=max_results // len(sources)
                )
                
                total_jobs_found += len(jobs_data)
                
                # Process each job
                for job_data in jobs_data:
                    try:
                        with transaction.atomic():
                            # Get or create company
                            company, created = Company.objects.get_or_create(
                                name=job_data.get('company_name', 'Unknown Company'),
                                defaults={
                                    'website': job_data.get('company_website', ''),
                                    'email': job_data.get('company_email', ''),
                                    'location': job_data.get('company_location', ''),
                                    'industry': job_data.get('company_industry', ''),
                                }
                            )
                            
                            # Extract additional company info if needed
                            if not company.website and company.name != 'Unknown Company':
                                company_info = extract_company_info(company.name)
                                if company_info:
                                    company.website = company_info.get('website', '')
                                    company.email = company_info.get('email', '')
                                    company.save()
                            
                            # Create or update job
                            job, job_created = Job.objects.get_or_create(
                                title=job_data.get('title', ''),
                                company=company,
                                source_url=job_data.get('source_url', ''),
                                defaults={
                                    'location': job_data.get('location', ''),
                                    'description': job_data.get('description', ''),
                                    'source': source,
                                    'status': 'active',
                                    'salary_min': job_data.get('salary_min'),
                                    'salary_max': job_data.get('salary_max'),
                                    'salary_currency': job_data.get('salary_currency', 'USD'),
                                    'employment_type': job_data.get('employment_type', ''),
                                    'experience_level': job_data.get('experience_level', ''),
                                    'remote_allowed': job_data.get('remote_allowed', False),
                                    'posted_date': job_data.get('posted_date'),
                                }
                            )
                            
                            if job_created:
                                total_jobs_created += 1
                            else:
                                # Update existing job if needed
                                job.updated_at = timezone.now()
                                job.save()
                                total_jobs_updated += 1
                            
                            total_jobs_processed += 1
                            
                    except Exception as e:
                        logger.error(f"Error processing job: {str(e)}")
                        ScrapingError.objects.create(
                            session=session,
                            error_type='parsing',
                            message=str(e),
                            url=job_data.get('source_url', ''),
                            source=source.name
                        )
                        total_errors += 1
                
                # Log success
                ScrapingLog.objects.create(
                    session=session,
                    level='info',
                    message=f"Successfully scraped {len(jobs_data)} jobs from {source.name}",
                    source=source.name
                )
                
            except Exception as e:
                logger.error(f"Error scraping from {source.name}: {str(e)}")
                ScrapingError.objects.create(
                    session=session,
                    error_type='network',
                    message=str(e),
                    source=source.name
                )
                total_errors += 1
        
        # Merge duplicate jobs
        duplicate_count = merge_duplicate_jobs()
        
        # Update session
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.jobs_found = total_jobs_found
        session.jobs_processed = total_jobs_processed
        session.jobs_created = total_jobs_created
        session.jobs_updated = total_jobs_updated
        session.errors_count = total_errors
        session.save()
        
        # Log completion
        ScrapingLog.objects.create(
            session=session,
            level='info',
            message=f"Scraping completed. Found: {total_jobs_found}, Created: {total_jobs_created}, Updated: {total_jobs_updated}, Errors: {total_errors}, Duplicates merged: {duplicate_count}"
        )
        
        return {
            'session_id': session.id,
            'status': 'completed',
            'jobs_found': total_jobs_found,
            'jobs_created': total_jobs_created,
            'jobs_updated': total_jobs_updated,
            'errors': total_errors,
            'duplicates_merged': duplicate_count
        }
        
    except Exception as e:
        logger.error(f"Scraping task failed: {str(e)}")
        
        # Update session with error
        session.status = 'failed'
        session.completed_at = timezone.now()
        session.errors_count += 1
        session.save()
        
        # Log error
        ScrapingError.objects.create(
            session=session,
            error_type='other',
            message=str(e)
        )
        
        raise self.retry(exc=e, countdown=60, max_retries=3)


@shared_task
def cleanup_old_sessions():
    """Clean up old scraping sessions and logs."""
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=30)
    
    # Delete old sessions
    old_sessions = ScrapingSession.objects.filter(created_at__lt=cutoff_date)
    count = old_sessions.count()
    old_sessions.delete()
    
    logger.info(f"Cleaned up {count} old scraping sessions")
    return f"Cleaned up {count} old scraping sessions"


@shared_task
def update_job_statuses():
    """Update job statuses based on age and other criteria."""
    from datetime import timedelta
    
    # Mark old jobs as expired
    old_date = timezone.now() - timedelta(days=30)
    expired_jobs = Job.objects.filter(
        status='active',
        posted_date__lt=old_date
    )
    
    count = expired_jobs.update(status='expired')
    logger.info(f"Marked {count} jobs as expired")
    
    return f"Updated {count} job statuses"
