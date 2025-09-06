# Development Guide

This guide provides detailed instructions for setting up a development environment and contributing to the Job Scraper Dashboard project.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Code Standards](#code-standards)
- [Adding New Features](#adding-new-features)
- [Testing](#testing)
- [Debugging](#debugging)
- [Contributing](#contributing)

## Prerequisites

### Required Software
- **Python 3.11+** - Programming language
- **Docker & Docker Compose** - Containerization
- **Git** - Version control
- **Chrome/Chromium** - For Selenium scraping
- **PostgreSQL** (optional) - Database for local development

### Recommended Tools
- **VS Code** or **PyCharm** - Code editor
- **Postman** or **Insomnia** - API testing
- **pgAdmin** or **DBeaver** - Database management

## Development Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd job-scraper-dashboard
```

### 2. Environment Configuration
```bash
# Copy environment template
cp env.example .env

# Edit configuration
nano .env  # or use your preferred editor
```

### 3. Docker Development Setup
```bash
# Start services
docker-compose up -d db redis

# Build and run application
docker-compose up --build

# Or run in background
docker-compose up -d
```

### 4. Local Python Development (Alternative)
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements/dev.txt

# Set up database
python backend/manage.py migrate
python backend/manage.py createsuperuser
python backend/manage.py init_sources

# Run development server
python backend/manage.py runserver

# Run Celery worker (separate terminal)
celery -A backend.config worker --loglevel=info

# Run Celery beat (separate terminal)
celery -A backend.config beat --loglevel=info
```

## Project Structure

### Backend Structure
```
backend/
├── apps/                    # Django applications
│   ├── jobs/               # Job management
│   │   ├── models.py       # Job and search models
│   │   ├── views.py        # API and web views
│   │   ├── serializers.py  # API serializers
│   │   ├── filters.py      # Query filtering
│   │   ├── urls.py         # URL routing
│   │   └── admin.py        # Admin interface
│   ├── companies/          # Company management
│   └── scraping/           # Web scraping engine
│       ├── scrapers/       # Individual scrapers
│       ├── api_clients/    # External API clients
│       ├── tasks.py        # Celery tasks
│       └── models.py       # Scraping models
├── config/                 # Django configuration
│   ├── settings/          # Environment settings
│   ├── urls.py            # Main URL config
│   └── celery.py          # Celery configuration
└── requirements/           # Python dependencies
```

### Frontend Structure
```
frontend/
├── static/                 # Static assets
│   ├── css/               # Stylesheets
│   └── js/                # JavaScript files
└── templates/             # Django templates
    ├── base.html          # Base template
    └── jobs/              # Job-related templates
```

## Code Standards

### Python Code Style
- Follow **PEP 8** guidelines
- Use **Black** for code formatting
- Use **flake8** for linting
- Maximum line length: 88 characters
- Use type hints where appropriate

### Django Best Practices
- Use **Django REST Framework** for APIs
- Follow **Django's naming conventions**
- Use **Django's built-in features** when possible
- Write **comprehensive docstrings**
- Use **Django's admin interface** effectively

### Frontend Standards
- Use **Bootstrap 5** for styling
- Follow **responsive design** principles
- Use **semantic HTML**
- Write **clean, maintainable CSS**
- Use **jQuery** for JavaScript interactions

### Git Workflow
- Use **descriptive commit messages**
- Create **feature branches** for new features
- Use **pull requests** for code review
- Keep **commits atomic** and focused

## Adding New Features

### 1. Adding a New Job Source

#### Step 1: Create Scraper Class
```python
# backend/apps/scraping/scrapers/new_source.py
from .base import BaseScraper

class NewSourceScraper(BaseScraper):
    """Scraper for New Job Source."""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://newsource.com"
        self.name = "New Source"
    
    def scrape_jobs(self, query, location=None, max_results=50):
        """Scrape jobs from New Source."""
        # Implementation here
        pass
    
    def _extract_job_data(self, job_element):
        """Extract job data from HTML element."""
        # Implementation here
        pass
```

#### Step 2: Add to Tasks
```python
# backend/apps/scraping/tasks.py
from .scrapers.new_source import NewSourceScraper

# Add to scrapers dictionary
scrapers = {
    # ... existing scrapers
    'newsource': NewSourceScraper(),
}
```

#### Step 3: Create Database Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Step 4: Add Tests
```python
# backend/apps/scraping/tests/test_new_source.py
from django.test import TestCase
from .scrapers.new_source import NewSourceScraper

class NewSourceScraperTest(TestCase):
    def test_scrape_jobs(self):
        scraper = NewSourceScraper()
        jobs = scraper.scrape_jobs("python developer")
        self.assertIsInstance(jobs, list)
```

### 2. Adding a New API Endpoint

#### Step 1: Create View
```python
# backend/apps/jobs/views.py
from rest_framework.decorators import action
from rest_framework.response import Response

class JobViewSet(viewsets.ModelViewSet):
    # ... existing code
    
    @action(detail=False, methods=['get'])
    def custom_endpoint(self, request):
        """Custom endpoint for specific functionality."""
        # Implementation here
        return Response({'message': 'Success'})
```

#### Step 2: Add URL Route
```python
# backend/apps/jobs/urls.py
urlpatterns = [
    # ... existing patterns
    path('custom/', views.JobViewSet.as_view({'get': 'custom_endpoint'})),
]
```

#### Step 3: Add Documentation
Update the API documentation in `docs/API.md` with the new endpoint.

### 3. Adding Frontend Features

#### Step 1: Create Template
```html
<!-- frontend/templates/jobs/new_feature.html -->
{% extends 'base.html' %}

{% block content %}
<div class="container">
    <h1>New Feature</h1>
    <!-- Implementation here -->
</div>
{% endblock %}
```

#### Step 2: Add View
```python
# backend/apps/jobs/views.py
def new_feature_view(request):
    """View for new frontend feature."""
    return render(request, 'jobs/new_feature.html')
```

#### Step 3: Add URL Route
```python
# backend/apps/jobs/urls.py
urlpatterns = [
    # ... existing patterns
    path('new-feature/', views.new_feature_view, name='new_feature'),
]
```

## Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.jobs

# Run specific test
python manage.py test apps.jobs.tests.test_models.JobModelTest

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Writing Tests

#### Model Tests
```python
from django.test import TestCase
from apps.jobs.models import Job

class JobModelTest(TestCase):
    def setUp(self):
        self.job = Job.objects.create(
            title="Test Job",
            company_name="Test Company",
            location="Test Location"
        )
    
    def test_job_creation(self):
        self.assertEqual(self.job.title, "Test Job")
        self.assertTrue(self.job.created_at)
```

#### View Tests
```python
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

class JobAPITest(APITestCase):
    def test_list_jobs(self):
        url = reverse('job-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
```

#### Scraper Tests
```python
from unittest.mock import patch, MagicMock
from apps.scraping.scrapers.indeed import IndeedScraper

class IndeedScraperTest(TestCase):
    @patch('apps.scraping.scrapers.base.webdriver.Chrome')
    def test_scrape_jobs(self, mock_chrome):
        scraper = IndeedScraper()
        # Mock WebDriver behavior
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        # Test scraping logic
```

## Debugging

### Django Debugging
```python
# Use Django Debug Toolbar
pip install django-debug-toolbar

# Add to settings
INSTALLED_APPS = [
    'debug_toolbar',
]

# Add to URLs
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
```

### Scraping Debugging
```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use non-headless mode
scraper = IndeedScraper()
scraper.setup_driver(headless=False)

# Add breakpoints
import pdb; pdb.set_trace()
```

### Database Debugging
```python
# Enable SQL logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Docker Debugging
```bash
# View logs
docker-compose logs -f web

# Access container
docker-compose exec web bash

# Check database
docker-compose exec web python manage.py dbshell

# Run management commands
docker-compose exec web python manage.py shell
```

## Contributing

### 1. Fork and Clone
```bash
git clone https://github.com/yourusername/job-scraper-dashboard.git
cd job-scraper-dashboard
```

### 2. Create Feature Branch
```bash
git checkout -b feature/new-feature
```

### 3. Make Changes
- Write code following project standards
- Add tests for new functionality
- Update documentation
- Ensure all tests pass

### 4. Commit Changes
```bash
git add .
git commit -m "Add new feature: description"
```

### 5. Push and Create Pull Request
```bash
git push origin feature/new-feature
# Create pull request on GitHub
```

### Pull Request Guidelines
- Provide clear description of changes
- Include screenshots for UI changes
- Ensure all tests pass
- Update documentation
- Follow code style guidelines

## Common Issues and Solutions

### Issue: Docker Build Fails
**Solution:**
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

### Issue: Database Connection Error
**Solution:**
```bash
# Check database service
docker-compose ps db

# Restart database
docker-compose restart db

# Check logs
docker-compose logs db
```

### Issue: Scraping Fails
**Solution:**
- Check internet connectivity
- Verify target websites are accessible
- Update Chrome WebDriver
- Check anti-detection measures

### Issue: Static Files Not Loading
**Solution:**
```bash
# Collect static files
python manage.py collectstatic

# Check static file configuration
# Verify web server configuration
```

## Performance Optimization

### Database Optimization
- Add proper indexes
- Use `select_related` and `prefetch_related`
- Implement database connection pooling
- Use database query optimization

### Caching
- Implement Redis caching
- Use template fragment caching
- Cache API responses
- Use browser caching

### Scraping Optimization
- Implement concurrent scraping
- Use headless browser mode
- Optimize selectors and parsing
- Implement rate limiting

## Security Considerations

### API Security
- Implement proper authentication
- Use HTTPS in production
- Implement rate limiting
- Validate input data

### Scraping Security
- Respect robots.txt
- Implement respectful scraping
- Use proper user agents
- Handle errors gracefully

### Database Security
- Use environment variables for credentials
- Implement proper access controls
- Regular security updates
- Backup strategies

## Monitoring and Logging

### Application Monitoring
- Implement health checks
- Use application performance monitoring
- Set up error tracking
- Monitor resource usage

### Logging
- Use structured logging
- Implement log rotation
- Set appropriate log levels
- Monitor log files

## Deployment

### Production Checklist
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Static files collected
- [ ] Security settings enabled
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] SSL certificates configured
- [ ] Performance optimized

### Environment-Specific Settings
- **Development**: Debug enabled, local database
- **Staging**: Debug disabled, production-like setup
- **Production**: Full security, monitoring, backups

---

For more information, refer to the main README.md and API documentation.
