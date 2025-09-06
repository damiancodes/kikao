"""
Adzuna API client for job search.
Free tier: 1000 requests/month
"""

import requests
import logging
from typing import List, Dict, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class AdzunaAPI:
    """Adzuna API client for job search."""
    
    BASE_URL = "https://api.adzuna.com/v1/api/jobs"
    
    def __init__(self, app_id: str = None, app_key: str = None):
        self.app_id = app_id or getattr(settings, 'ADZUNA_APP_ID', '')
        self.app_key = app_key or getattr(settings, 'ADZUNA_APP_KEY', '')
        
        if not self.app_id or not self.app_key:
            logger.warning("Adzuna API credentials not configured")
    
    def search_jobs(self, query: str, location: str = '', max_results: int = 50) -> List[Dict]:
        """Search for jobs using Adzuna API."""
        if not self.app_id or not self.app_key:
            logger.error("Adzuna API credentials not configured")
            return []
        
        jobs = []
        
        try:
            # Search in multiple countries including Kenya
            countries = ['us', 'gb', 'ca', 'au', 'ke'] if not location else ['us']
            
            # If location contains Kenya, search in Kenya
            if location and 'kenya' in location.lower():
                countries = ['ke']
            
            for country in countries:
                if len(jobs) >= max_results:
                    break
                    
                params = {
                    'app_id': self.app_id,
                    'app_key': self.app_key,
                    'what': query,
                    'where': location or 'United States',
                    'results_per_page': min(50, max_results - len(jobs))
                }
                
                headers = {
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(f"{self.BASE_URL}/{country}/search/1", params=params, headers=headers, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                country_jobs = data.get('results', [])
                
                for job in country_jobs:
                    if len(jobs) >= max_results:
                        break
                        
                    processed_job = self._process_job(job, country)
                    if processed_job:
                        jobs.append(processed_job)
                
                logger.info(f"Found {len(country_jobs)} jobs from Adzuna {country}")
            
            logger.info(f"Total jobs found from Adzuna: {len(jobs)}")
            return jobs
            
        except Exception as e:
            logger.error(f"Error searching Adzuna API: {str(e)}")
            return []
    
    def _process_job(self, job: Dict, country: str) -> Optional[Dict]:
        """Process a job from Adzuna API."""
        try:
            # Extract salary information
            salary_min = None
            salary_max = None
            salary_currency = 'USD'
            
            salary_info = job.get('salary_min') or job.get('salary_max')
            if salary_info:
                salary_min = job.get('salary_min')
                salary_max = job.get('salary_max')
                salary_currency = job.get('salary_currency', 'USD')
            
            # Determine employment type
            employment_type = 'Full-time'
            contract_type = job.get('contract_type', '').lower()
            if 'part' in contract_type:
                employment_type = 'Part-time'
            elif 'contract' in contract_type:
                employment_type = 'Contract'
            elif 'intern' in contract_type:
                employment_type = 'Internship'
            
            # Check if remote
            remote_allowed = False
            title_desc = f"{job.get('title', '')} {job.get('description', '')}".lower()
            remote_keywords = ['remote', 'work from home', 'wfh', 'virtual', 'distributed']
            remote_allowed = any(keyword in title_desc for keyword in remote_keywords)
            
            return {
                'title': job.get('title', ''),
                'company_name': job.get('company', {}).get('display_name', 'Unknown Company'),
                'location': job.get('location', {}).get('display_name', ''),
                'description': job.get('description', ''),
                'source_url': job.get('redirect_url', ''),
                'salary_min': salary_min,
                'salary_max': salary_max,
                'salary_currency': salary_currency,
                'employment_type': employment_type,
                'experience_level': self._extract_experience_level(job.get('title', '')),
                'remote_allowed': remote_allowed,
                'posted_date': job.get('created', ''),
                'source': 'Adzuna',
                'country': country
            }
            
        except Exception as e:
            logger.error(f"Error processing Adzuna job: {str(e)}")
            return None
    
    def _extract_experience_level(self, title: str) -> str:
        """Extract experience level from job title."""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['senior', 'lead', 'principal', 'staff']):
            return 'Senior'
        elif any(word in title_lower for word in ['junior', 'entry', 'associate']):
            return 'Junior'
        elif any(word in title_lower for word in ['mid', 'intermediate']):
            return 'Mid-level'
        elif any(word in title_lower for word in ['intern', 'internship']):
            return 'Intern'
        
        return 'Mid-level'  # Default
