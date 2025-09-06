"""
Jobright.ai API client for job search.
"""

import requests
import logging
from typing import List, Dict, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class JobrightAPI:
    """Jobright.ai API client for job search."""
    
    BASE_URL = "https://jobright.ai/api"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or getattr(settings, 'JOBRIGHT_API_KEY', '')
        
        if not self.api_key:
            logger.warning("Jobright API key not configured")
    
    def search_jobs(self, query: str, location: str = '', max_results: int = 50) -> List[Dict]:
        """Search for jobs using Jobright API."""
        if not self.api_key:
            logger.error("Jobright API key not configured")
            return []
        
        jobs = []
        
        try:
            # Jobright.ai uses a different API structure
            # This is a placeholder implementation - you'll need to check their actual API docs
            params = {
                'api_key': self.api_key,
                'q': query,
                'location': location or 'United States',
                'limit': min(50, max_results)
            }
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(f"{self.BASE_URL}/jobs/search", params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            job_listings = data.get('jobs', [])
            
            for job in job_listings:
                if len(jobs) >= max_results:
                    break
                    
                processed_job = self._process_job(job)
                if processed_job:
                    jobs.append(processed_job)
            
            logger.info(f"Found {len(jobs)} jobs from Jobright")
            return jobs
            
        except Exception as e:
            logger.error(f"Error searching Jobright API: {str(e)}")
            return []
    
    def _process_job(self, job: Dict) -> Optional[Dict]:
        """Process a job from Jobright API."""
        try:
            return {
                'title': job.get('title', ''),
                'company_name': job.get('company', ''),
                'location': job.get('location', ''),
                'description': job.get('description', ''),
                'source_url': job.get('url', ''),
                'salary_min': job.get('salary_min'),
                'salary_max': job.get('salary_max'),
                'salary_currency': job.get('currency', 'USD'),
                'employment_type': job.get('employment_type', 'Full-time'),
                'experience_level': self._extract_experience_level(job.get('title', '')),
                'remote_allowed': job.get('remote', False),
                'posted_date': job.get('posted_date', ''),
                'source': 'Jobright',
            }
            
        except Exception as e:
            logger.error(f"Error processing Jobright job: {str(e)}")
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
