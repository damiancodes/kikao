"""
Utility functions for web scraping.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import logging
from django.db.models import Q
from apps.jobs.models import Job
from apps.companies.models import Company

logger = logging.getLogger(__name__)


def extract_company_info(company_name):
    """
    Extract company information using Google search.
    
    Args:
        company_name (str): Name of the company
        
    Returns:
        dict: Company information including website and email
    """
    try:
        # Search for company website
        search_query = f"{company_name} official website"
        search_url = f"https://www.google.com/search?q={search_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the first non-sponsored result
        results = soup.find_all('div', class_='g')
        website = None
        
        for result in results:
            link = result.find('a')
            if link and link.get('href'):
                href = link.get('href')
                if href.startswith('/url?q='):
                    href = href.split('/url?q=')[1].split('&')[0]
                
                # Skip social media and information sites
                if not _is_social_or_info_site(href):
                    website = href
                    break
        
        # Extract email from company website
        email = None
        if website:
            email = _extract_email_from_website(website)
        
        return {
            'website': website or '',
            'email': email or ''
        }
        
    except Exception as e:
        logger.error(f"Error extracting company info for {company_name}: {str(e)}")
        return {'website': '', 'email': ''}


def _is_social_or_info_site(url):
    """Check if URL is a social media or information site."""
    social_domains = [
        'linkedin.com', 'facebook.com', 'twitter.com', 'instagram.com',
        'youtube.com', 'quora.com', 'wikipedia.org', 'crunchbase.com',
        'glassdoor.com', 'indeed.com', 'monster.com', 'ziprecruiter.com'
    ]
    
    try:
        domain = urlparse(url).netloc.lower()
        return any(social_domain in domain for social_domain in social_domains)
    except:
        return False


def _extract_email_from_website(website_url):
    """Extract email address from company website."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(website_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for email in contact/about pages
        contact_links = soup.find_all('a', href=re.compile(r'contact|about', re.I))
        
        for link in contact_links:
            href = link.get('href')
            if href:
                if not href.startswith('http'):
                    href = urljoin(website_url, href)
                
                try:
                    contact_response = requests.get(href, headers=headers, timeout=10)
                    contact_soup = BeautifulSoup(contact_response.text, 'html.parser')
                    
                    # Find email in contact page
                    email = _find_email_in_text(contact_soup.get_text())
                    if email:
                        return email
                except:
                    continue
        
        # Look for email in main page
        email = _find_email_in_text(soup.get_text())
        return email
        
    except Exception as e:
        logger.error(f"Error extracting email from {website_url}: {str(e)}")
        return None


def _find_email_in_text(text):
    """Find email address in text."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    
    # Filter out common non-contact emails
    filtered_emails = []
    for email in emails:
        if not any(domain in email.lower() for domain in ['noreply', 'no-reply', 'donotreply']):
            filtered_emails.append(email)
    
    return filtered_emails[0] if filtered_emails else None


def merge_duplicate_jobs():
    """
    Merge duplicate jobs from different sources.
    
    Returns:
        int: Number of duplicates merged
    """
    try:
        # Find potential duplicates based on title and company
        jobs = Job.objects.all().order_by('title', 'company', 'scraped_at')
        
        merged_count = 0
        current_job = None
        
        for job in jobs:
            if current_job is None:
                current_job = job
                continue
            
            # Check if jobs are similar
            if _are_jobs_similar(current_job, job):
                # Merge the jobs
                _merge_jobs(current_job, job)
                merged_count += 1
            else:
                current_job = job
        
        logger.info(f"Merged {merged_count} duplicate jobs")
        return merged_count
        
    except Exception as e:
        logger.error(f"Error merging duplicate jobs: {str(e)}")
        return 0


def _are_jobs_similar(job1, job2):
    """Check if two jobs are similar enough to be considered duplicates."""
    # Same title and company
    if (job1.title.lower() == job2.title.lower() and 
        job1.company.name.lower() == job2.company.name.lower()):
        return True
    
    # Similar title and same company
    if (job1.company.name.lower() == job2.company.name.lower() and
        _calculate_similarity(job1.title, job2.title) > 0.8):
        return True
    
    return False


def _calculate_similarity(text1, text2):
    """Calculate similarity between two texts."""
    from difflib import SequenceMatcher
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def _merge_jobs(primary_job, secondary_job):
    """Merge secondary job into primary job."""
    try:
        # Note: Job model has a single source field, not many-to-many
        # We'll keep the primary job's source and just merge other data
        
        # Update description if primary is shorter
        if len(primary_job.description) < len(secondary_job.description):
            primary_job.description = secondary_job.description
        
        # Update other fields if primary is missing
        if not primary_job.location and secondary_job.location:
            primary_job.location = secondary_job.location
        
        if not primary_job.salary_min and secondary_job.salary_min:
            primary_job.salary_min = secondary_job.salary_min
        
        if not primary_job.salary_max and secondary_job.salary_max:
            primary_job.salary_max = secondary_job.salary_max
        
        if not primary_job.employment_type and secondary_job.employment_type:
            primary_job.employment_type = secondary_job.employment_type
        
        if not primary_job.experience_level and secondary_job.experience_level:
            primary_job.experience_level = secondary_job.experience_level
        
        if not primary_job.remote_allowed and secondary_job.remote_allowed:
            primary_job.remote_allowed = secondary_job.remote_allowed
        
        primary_job.save()
        
        # Delete secondary job
        secondary_job.delete()
        
    except Exception as e:
        logger.error(f"Error merging jobs: {str(e)}")


def clean_job_data(job_data):
    """Clean and normalize job data."""
    if not job_data:
        return job_data
    
    # Clean text fields
    text_fields = ['title', 'company_name', 'location', 'description', 'employment_type', 'experience_level']
    for field in text_fields:
        if field in job_data and job_data[field]:
            job_data[field] = ' '.join(job_data[field].split())
    
    # Clean URL
    if 'source_url' in job_data and job_data['source_url']:
        job_data['source_url'] = job_data['source_url'].strip()
    
    # Clean salary fields
    if 'salary_min' in job_data and job_data['salary_min']:
        try:
            job_data['salary_min'] = float(job_data['salary_min'])
        except (ValueError, TypeError):
            job_data['salary_min'] = None
    
    if 'salary_max' in job_data and job_data['salary_max']:
        try:
            job_data['salary_max'] = float(job_data['salary_max'])
        except (ValueError, TypeError):
            job_data['salary_max'] = None
    
    # Clean boolean fields
    if 'remote_allowed' in job_data:
        job_data['remote_allowed'] = bool(job_data['remote_allowed'])
    
    return job_data
