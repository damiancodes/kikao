"""
RemoteOK job scraper.
"""

from .base import BaseScraper
import requests
import logging
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class RemoteOKScraper(BaseScraper):
    """RemoteOK job scraper."""
    
    BASE_URL = "https://remoteok.com/api"
    
    def scrape_jobs(self, query, location='', max_results=50):
        """Scrape jobs from RemoteOK."""
        jobs = []
        
        try:
            # RemoteOK has a simple API
            response = self.session.get(self.BASE_URL, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Filter jobs based on query
            filtered_jobs = []
            for job in data:
                if self._matches_query(job, query):
                    filtered_jobs.append(job)
            
            # Limit results
            filtered_jobs = filtered_jobs[:max_results]
            
            for job in filtered_jobs:
                try:
                    job_data = self._extract_job_data(job)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    logger.error(f"Error extracting job: {str(e)}")
                    continue
            
            logger.info(f"Successfully scraped {len(jobs)} jobs from RemoteOK")
            
        except Exception as e:
            logger.error(f"Error scraping RemoteOK: {str(e)}")
        
        return jobs
    
    def _matches_query(self, job, query):
        """Check if job matches the search query."""
        if not query:
            return True
        
        query_lower = query.lower()
        job_text = f"{job.get('position', '')} {job.get('company', '')} {job.get('description', '')}".lower()
        
        return query_lower in job_text
    
    def _extract_job_data(self, job):
        """Extract job data from RemoteOK job object."""
        try:
            title = job.get('position', '')
            company_name = job.get('company', '')
            location = job.get('location', '')
            description = job.get('description', '')
            job_url = job.get('url', '')
            
            # Extract salary if available
            salary_text = job.get('salary', '')
            salary_min, salary_max, currency = self.extract_salary(salary_text)
            
            # Extract employment type
            employment_type = self._extract_employment_type(description)
            
            # Extract experience level
            experience_level = self._extract_experience_level(description)
            
            # RemoteOK jobs are typically remote
            remote_allowed = True
            
            if not title or not company_name:
                return None
            
            return {
                'title': self.clean_text(title),
                'company_name': self.clean_text(company_name),
                'location': self.clean_text(location),
                'description': self.clean_text(description),
                'source_url': job_url,
                'salary_min': salary_min,
                'salary_max': salary_max,
                'salary_currency': currency,
                'employment_type': employment_type,
                'experience_level': experience_level,
                'remote_allowed': remote_allowed,
                'posted_date': None,  # RemoteOK doesn't always show this
            }
            
        except Exception as e:
            logger.error(f"Error extracting job data: {str(e)}")
            return None
    
    def _extract_employment_type(self, description):
        """Extract employment type from description."""
        if not description:
            return ''
        
        description_lower = description.lower()
        
        if 'full-time' in description_lower or 'full time' in description_lower:
            return 'Full-time'
        elif 'part-time' in description_lower or 'part time' in description_lower:
            return 'Part-time'
        elif 'contract' in description_lower:
            return 'Contract'
        elif 'internship' in description_lower:
            return 'Internship'
        elif 'freelance' in description_lower:
            return 'Freelance'
        
        return 'Full-time'  # Default assumption
    
    def _extract_experience_level(self, description):
        """Extract experience level from description."""
        if not description:
            return ''
        
        description_lower = description.lower()
        
        if 'senior' in description_lower or 'lead' in description_lower:
            return 'Senior'
        elif 'junior' in description_lower or 'entry' in description_lower:
            return 'Junior'
        elif 'mid' in description_lower or 'intermediate' in description_lower:
            return 'Mid-level'
        elif 'intern' in description_lower or 'internship' in description_lower:
            return 'Intern'
        
        return ''  # Unknown



