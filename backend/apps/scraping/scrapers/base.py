"""
Base scraper class for job scraping.
"""

from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import requests
import time
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for all job scrapers."""
    
    def __init__(self):
        self.driver = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def setup_driver(self, headless=True):
        """Setup Chrome driver with options."""
        chrome_options = Options()
        
        if headless or getattr(settings, 'SELENIUM_HEADLESS', True):
            chrome_options.add_argument('--headless')
        
        # Anti-detection options
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Random user agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        import random
        chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(getattr(settings, 'SELENIUM_TIMEOUT', 10))
            
            # Execute stealth script
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return True
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {str(e)}")
            return False
    
    def close_driver(self):
        """Close the Chrome driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def wait_for_element(self, by, value, timeout=10):
        """Wait for an element to be present."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.warning(f"Element not found: {by}={value}")
            return None
    
    def safe_find_element(self, by, value):
        """Safely find an element without throwing exceptions."""
        try:
            return self.driver.find_element(by, value)
        except NoSuchElementException:
            return None
    
    def safe_find_elements(self, by, value):
        """Safely find elements without throwing exceptions."""
        try:
            return self.driver.find_elements(by, value)
        except NoSuchElementException:
            return []
    
    def get_page_source(self, url, wait_time=2):
        """Get page source with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if self.driver:
                    self.driver.get(url)
                    time.sleep(wait_time)
                    return self.driver.page_source
                else:
                    response = self.session.get(url, timeout=30)
                    response.raise_for_status()
                    return response.text
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    raise
    
    def parse_html(self, html):
        """Parse HTML with BeautifulSoup."""
        return BeautifulSoup(html, 'html.parser')
    
    def extract_text(self, element, default=''):
        """Extract text from element safely."""
        if element:
            return element.get_text(strip=True)
        return default
    
    def extract_attribute(self, element, attribute, default=''):
        """Extract attribute from element safely."""
        if element:
            return element.get(attribute, default)
        return default
    
    def clean_text(self, text):
        """Clean and normalize text."""
        if not text:
            return ''
        return ' '.join(text.split())
    
    def extract_salary(self, text):
        """Extract salary information from text."""
        import re
        
        if not text:
            return None, None, 'USD'
        
        # Common salary patterns
        patterns = [
            r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*-\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*to\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*\+',
            r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    try:
                        min_salary = float(groups[0].replace(',', ''))
                        max_salary = float(groups[1].replace(',', ''))
                        return min_salary, max_salary, 'USD'
                    except ValueError:
                        continue
                elif len(groups) == 1:
                    try:
                        salary = float(groups[0].replace(',', ''))
                        return salary, None, 'USD'
                    except ValueError:
                        continue
        
        return None, None, 'USD'
    
    @abstractmethod
    def scrape_jobs(self, query, location='', max_results=50):
        """
        Scrape jobs from the source.
        
        Args:
            query (str): Job search query
            location (str): Location filter
            max_results (int): Maximum number of results
            
        Returns:
            list: List of job dictionaries
        """
        pass
    
    def __enter__(self):
        """Context manager entry."""
        self.setup_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_driver()





