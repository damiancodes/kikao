"""
LinkedIn job scraper.
"""

from .base import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging
from urllib.parse import urlencode, urljoin

logger = logging.getLogger(__name__)


class LinkedInScraper(BaseScraper):
    """LinkedIn job scraper."""
    
    BASE_URL = "https://www.linkedin.com/jobs/search"
    
    def scrape_jobs(self, query, location='', max_results=50):
        """Scrape jobs from LinkedIn."""
        jobs = []
        
        try:
            if not self.setup_driver():
                logger.error("Failed to setup driver for LinkedIn scraping")
                return jobs
            
            # Build search URL
            params = {
                'keywords': query,
                'location': location,
                'start': 0
            }
            
            search_url = f"{self.BASE_URL}?{urlencode(params)}"
            logger.info(f"Scraping LinkedIn: {search_url}")
            
            self.driver.get(search_url)
            time.sleep(3)
            
            # Wait for job listings to load
            self.wait_for_element(By.CLASS_NAME, "jobs-search-results-list", timeout=10)
            
            # Scroll to load more jobs
            self._scroll_to_load_jobs(max_results)
            
            # Get job elements
            job_elements = self.safe_find_elements(By.CSS_SELECTOR, ".jobs-search-results__list-item")
            
            for i, job_element in enumerate(job_elements[:max_results]):
                try:
                    job_data = self._extract_job_data(job_element)
                    if job_data:
                        jobs.append(job_data)
                        logger.debug(f"Extracted job {i+1}: {job_data.get('title', 'Unknown')}")
                except Exception as e:
                    logger.error(f"Error extracting job {i+1}: {str(e)}")
                    continue
            
            logger.info(f"Successfully scraped {len(jobs)} jobs from LinkedIn")
            
        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {str(e)}")
        finally:
            self.close_driver()
        
        return jobs
    
    def _scroll_to_load_jobs(self, max_results):
        """Scroll to load more job listings."""
        try:
            # Find the jobs container
            jobs_container = self.wait_for_element(By.CLASS_NAME, "jobs-search-results-list", timeout=10)
            if not jobs_container:
                return
            
            # Scroll down to load more jobs
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scroll_attempts = 10
            
            while scroll_attempts < max_scroll_attempts:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Check if new content loaded
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                
                last_height = new_height
                scroll_attempts += 1
                
                # Check if we have enough jobs
                job_elements = self.safe_find_elements(By.CSS_SELECTOR, ".jobs-search-results__list-item")
                if len(job_elements) >= max_results:
                    break
            
        except Exception as e:
            logger.error(f"Error scrolling to load jobs: {str(e)}")
    
    def _extract_job_data(self, job_element):
        """Extract job data from a job element."""
        try:
            # Click on job to load details
            job_element.click()
            time.sleep(2)
            
            # Extract basic info
            title_element = self.safe_find_element(By.CSS_SELECTOR, ".jobs-unified-top-card__job-title")
            title = self.extract_text(title_element)
            
            company_element = self.safe_find_element(By.CSS_SELECTOR, ".jobs-unified-top-card__company-name")
            company_name = self.extract_text(company_element)
            
            location_element = self.safe_find_element(By.CSS_SELECTOR, ".jobs-unified-top-card__bullet")
            location = self.extract_text(location_element)
            
            # Extract job description
            description_element = self.safe_find_element(By.CSS_SELECTOR, ".jobs-description-content__text")
            description = self.extract_text(description_element)
            
            # Extract salary if available
            salary_element = self.safe_find_element(By.CSS_SELECTOR, ".jobs-unified-top-card__salary")
            salary_text = self.extract_text(salary_element)
            salary_min, salary_max, currency = self.extract_salary(salary_text)
            
            # Extract job URL
            job_link = self.safe_find_element(By.CSS_SELECTOR, ".jobs-unified-top-card__job-title a")
            job_url = self.extract_attribute(job_link, 'href', '')
            
            # Extract employment type
            employment_type = self._extract_employment_type(description)
            
            # Extract experience level
            experience_level = self._extract_experience_level(description)
            
            # Check if remote
            remote_allowed = self._check_remote_allowed(description, title)
            
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
                'posted_date': None,  # LinkedIn doesn't always show this
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
    
    def _check_remote_allowed(self, description, title):
        """Check if remote work is allowed."""
        text = f"{title} {description}".lower()
        
        remote_keywords = [
            'remote', 'work from home', 'wfh', 'virtual', 'distributed',
            'telecommute', 'flexible location', 'anywhere'
        ]
        
        return any(keyword in text for keyword in remote_keywords)



