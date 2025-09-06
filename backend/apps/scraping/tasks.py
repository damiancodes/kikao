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
from .scrapers.brightermonday import BrighterMondayScraper
from .scrapers.fuzu import FuzuScraper
from .api_clients.adzuna import AdzunaAPI
from .api_clients.jobright import JobrightAPI
from .api_clients.kenya_jobs import KenyaJobsAPI
from .utils import extract_company_info, merge_duplicate_jobs
import logging

logger = logging.getLogger(__name__)


def scrape_jobs_task(query, location='', max_results=50, source_ids=None):
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
        # Log start with detailed info - FORCE PRINT TO CONSOLE
        print(f"\n{'='*60}")
        print(f"=== STARTING SCRAPING SESSION {session.id} ===")
        print(f"Query: {query}")
        print(f"Location: {location}")
        print(f"Max Results: {max_results}")
        print(f"Source IDs: {source_ids}")
        print(f"{'='*60}\n")
        
        logger.info(f"=== STARTING SCRAPING SESSION {session.id} ===")
        logger.info(f"Query: {query}")
        logger.info(f"Location: {location}")
        logger.info(f"Max Results: {max_results}")
        logger.info(f"Source IDs: {source_ids}")
        
        # Get active sources
        if source_ids:
            sources = JobSource.objects.filter(id__in=source_ids, is_active=True)
            logger.info(f"Filtered sources by IDs: {list(sources.values_list('name', flat=True))}")
        else:
            sources = JobSource.objects.filter(is_active=True)
            logger.info(f"All active sources: {list(sources.values_list('name', flat=True))}")
        
        if not sources.exists():
            error_msg = "No active sources found"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Found {sources.count()} active sources to scrape from")
        
        # Initialize scrapers and API clients
        scrapers = {
            'linkedin': LinkedInScraper(),
            'indeed': IndeedScraper(),
            'glassdoor': GlassdoorScraper(),
            'remoteok': RemoteOKScraper(),
            'brightermonday': BrighterMondayScraper(),
            'fuzu': FuzuScraper(),
        }
        
        # Initialize API clients
        api_clients = {
            'adzuna': AdzunaAPI(),
            'jobright': JobrightAPI(),
            'kenya_jobs': KenyaJobsAPI(),
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
                
                # Log progress with detailed info - FORCE PRINT TO CONSOLE
                print(f"\n{'='*40}")
                print(f"=== SCRAPING FROM {source.name.upper()} ===")
                print(f"Source name: {source.name}")
                print(f"Scraper name: {scraper_name}")
                print(f"Source ID: {source.id}")
                print(f"Source active: {source.is_active}")
                print(f"{'='*40}\n")
                
                logger.info(f"=== SCRAPING FROM {source.name.upper()} ===")
                logger.info(f"Source name: {source.name}")
                logger.info(f"Scraper name: {scraper_name}")
                logger.info(f"Source ID: {source.id}")
                logger.info(f"Source active: {source.is_active}")
                
                # Start with empty jobs data - we'll try real scraping first
                jobs_data = []
                num_jobs = min(15, max_results // len(sources))  # 15 jobs per source
                logger.info(f"Attempting to scrape {num_jobs} real jobs from {source.name}")
                
                # Create realistic job data (will be used as fallback)
                job_titles = [
                    f"Senior {query}",
                    f"Junior {query}",
                    f"{query} Specialist",
                    f"Lead {query}",
                    f"{query} Manager",
                    f"Data {query}",
                    f"Business {query}",
                    f"Financial {query}",
                    f"Marketing {query}",
                    f"Senior Data {query}",
                    f"Remote {query}",
                    f"{query} Consultant",
                    f"Entry Level {query}",
                    f"Senior {query} Engineer",
                    f"{query} Coordinator"
                ]
                
                companies = [
                    "Microsoft", "Google", "Amazon", "Apple", "Meta", "Tesla", "Netflix", "Uber",
                    "Airbnb", "Spotify", "Twitter", "LinkedIn", "Salesforce", "Oracle", "IBM",
                    "Deloitte", "PwC", "EY", "KPMG", "Accenture", "McKinsey", "BCG", "Bain",
                    "Goldman Sachs", "JPMorgan", "Morgan Stanley", "Wells Fargo", "Bank of America"
                ]
                
                locations_list = [
                    "New York, NY", "San Francisco, CA", "Seattle, WA", "Austin, TX", "Boston, MA",
                    "Chicago, IL", "Los Angeles, CA", "Denver, CO", "Remote", "Hybrid",
                    "Washington, DC", "Miami, FL", "Atlanta, GA", "Dallas, TX", "Portland, OR"
                ]
                
                # Store dummy job data for fallback (don't add to jobs_data yet)
                dummy_jobs = []
                for i in range(num_jobs):
                    # Create clearly dummy URLs that won't mislead users
                    if source.name.lower() == 'linkedin':
                        source_url = f'https://www.linkedin.com/jobs/view/DUMMY-{source.name.upper()}-{i+1}'
                    elif source.name.lower() == 'indeed':
                        source_url = f'https://www.indeed.com/viewjob?jk=DUMMY-{source.name.upper()}-{i+1}'
                    elif source.name.lower() == 'glassdoor':
                        source_url = f'https://www.glassdoor.com/job-listing/DUMMY-{source.name.upper()}-{i+1}'
                    elif source.name.lower() == 'remoteok':
                        source_url = f'https://remoteok.com/remote-jobs/DUMMY-{source.name.upper()}-{i+1}'
                    else:
                        source_url = f'https://{source.name.lower()}.com/job/DUMMY-{i+1}'
                    
                    job_data = {
                        'title': f"[DUMMY] {job_titles[i % len(job_titles)]}",
                        'company_name': companies[i % len(companies)],
                        'location': locations_list[i % len(locations_list)],
                        'description': f"🚨 DUMMY JOB - This is a sample job posting for testing purposes. We are looking for a talented {query} to join our team. This role involves analyzing data, creating reports, and working with stakeholders to drive business insights. You will work with cutting-edge tools and technologies in a fast-paced environment. [This is not a real job posting]",
                        'source_url': source_url,
                        'salary_min': 50000 + (i * 5000),
                        'salary_max': 80000 + (i * 5000),
                        'salary_currency': 'USD',
                        'employment_type': ['Full-time', 'Part-time', 'Contract'][i % 3],
                        'experience_level': ['Entry', 'Mid-level', 'Senior'][i % 3],
                        'remote_allowed': i % 3 == 0,
                        'posted_date': timezone.now().date(),
                    }
                    dummy_jobs.append(job_data)
                
                # Try API client first (more reliable)
                api_used = False
                
                # Special handling for Kenya - use Kenya Jobs API
                if location and 'kenya' in location.lower() and scraper_name in ['brightermonday', 'fuzu', 'jobright']:
                    try:
                        print(f"🇰🇪 USING KENYA JOBS API for {source.name}...")
                        logger.info(f"Using Kenya Jobs API for {source.name}")
                        kenya_api = api_clients['kenya_jobs']
                        real_jobs = kenya_api.search_jobs(
                            query=query,
                            location=location,
                            max_results=10
                        )
                        if real_jobs:
                            jobs_data = real_jobs + jobs_data
                            print(f"✅ KENYA SUCCESS: Found {len(real_jobs)} Kenya jobs")
                            logger.info(f"KENYA SUCCESS: Found {len(real_jobs)} Kenya jobs")
                            api_used = True
                    except Exception as e:
                        print(f"❌ KENYA API FAILED: {str(e)}")
                        logger.error(f"Kenya API failed: {str(e)}")
                
                if not api_used and scraper_name in api_clients:
                    try:
                        print(f"🌐 ATTEMPTING API CLIENT for {source.name}...")
                        logger.info(f"Attempting API client for {source.name}...")
                        api_client = api_clients[scraper_name]
                        real_jobs = api_client.search_jobs(
                            query=query,
                            location=location,
                            max_results=10  # Try to get 10 real jobs
                        )
                        if real_jobs:
                            jobs_data = real_jobs + jobs_data
                            print(f"✅ API SUCCESS: Found {len(real_jobs)} real jobs from {source.name}")
                            logger.info(f"API SUCCESS: Found {len(real_jobs)} real jobs from {source.name}")
                            api_used = True
                        else:
                            print(f"⚠️  API returned empty results for {source.name}")
                            logger.warning(f"API returned empty results for {source.name}")
                    except Exception as e:
                        print(f"❌ API FAILED for {source.name}: {str(e)}")
                        logger.error(f"API FAILED for {source.name}: {str(e)}")
                
                # Try real scraping if API didn't work
                if not api_used and scraper_name in scrapers:
                    try:
                        print(f"🔍 ATTEMPTING REAL SCRAPING for {source.name}...")
                        logger.info(f"Attempting real scraping for {source.name}...")
                        scraper = scrapers[scraper_name]
                        real_jobs = scraper.scrape_jobs(
                            query=query,
                            location=location,
                            max_results=5  # Try to get 5 real jobs
                        )
                        if real_jobs:
                            jobs_data = real_jobs + jobs_data  # Combine real and dummy data
                            print(f"✅ SUCCESS: Found {len(real_jobs)} real jobs from {source.name}")
                            logger.info(f"SUCCESS: Found {len(real_jobs)} real jobs from {source.name}")
                        else:
                            print(f"⚠️  Real scraping returned empty results for {source.name}")
                            logger.warning(f"Real scraping returned empty results for {source.name}")
                    except Exception as e:
                        print(f"❌ REAL SCRAPING FAILED for {source.name}: {str(e)}")
                        print(f"Error type: {type(e).__name__}")
                        logger.error(f"REAL SCRAPING FAILED for {source.name}: {str(e)}")
                        logger.error(f"Error type: {type(e).__name__}")
                        import traceback
                        print(f"Traceback: {traceback.format_exc()}")
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        print(f"🔄 Falling back to dummy data for {source.name}")
                        logger.info(f"Falling back to dummy data for {source.name}")
                elif not api_used:
                    print(f"⚠️  No scraper or API found for {source.name} (scraper_name: {scraper_name})")
                    print(f"Available scrapers: {list(scrapers.keys())}")
                    print(f"Available APIs: {list(api_clients.keys())}")
                    print(f"🔄 Using dummy data for {source.name}")
                    logger.warning(f"No scraper or API found for {source.name} (scraper_name: {scraper_name})")
                    logger.info(f"Available scrapers: {list(scrapers.keys())}")
                    logger.info(f"Available APIs: {list(api_clients.keys())}")
                    logger.info(f"Using dummy data for {source.name}")
                
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
                            
                            # Skip external API calls to avoid rate limiting
                            # if not company.website and company.name != 'Unknown Company':
                            #     company_info = extract_company_info(company.name)
                            #     if company_info:
                            #         company.website = company_info.get('website', '')
                            #         company.email = company_info.get('email', '')
                            #         company.save()
                            
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
                
                # If no real jobs found, use dummy jobs as fallback
                if not jobs_data:
                    print(f"⚠️  No real jobs found, using dummy data for {source.name}")
                    logger.warning(f"No real jobs found, using dummy data for {source.name}")
                    jobs_data = dummy_jobs[:min(5, max_results)]
                
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
        
        # Log completion with detailed summary
        print(f"\n{'='*60}")
        print(f"🎉 SCRAPING COMPLETED SUCCESSFULLY!")
        print(f"📊 SUMMARY:")
        print(f"   • Total Jobs Found: {total_jobs_found}")
        print(f"   • Jobs Created: {total_jobs_created}")
        print(f"   • Jobs Updated: {total_jobs_updated}")
        print(f"   • Errors: {total_errors}")
        print(f"   • Duplicates Merged: {duplicate_count}")
        print(f"{'='*60}\n")
        
        ScrapingLog.objects.create(
            session=session,
            level='info',
            message=f"Scraping completed. Found: {total_jobs_found}, Created: {total_jobs_created}, Updated: {total_jobs_updated}, Errors: {total_errors}, Duplicates merged: {duplicate_count}"
        )
        
        return {
            'session_id': session.id,
            'status': 'completed',
            'jobs_found': total_jobs_created + total_jobs_updated,  # Only count unique jobs
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
        
        raise e


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
