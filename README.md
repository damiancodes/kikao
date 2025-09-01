# Job Scraper & Dashboard

A multi-platform job aggregator that scrapes job listings from LinkedIn, Glassdoor, Indeed, and other job sites. Built with Django, Selenium, and Docker for production deployment.

## Features

- Multi-platform job scraping (LinkedIn, Glassdoor, Indeed)
- Company website and email extraction
- Duplicate job detection and merging
- REST API for data consumption
- Web dashboard for job management
- CSV/Excel export functionality
- Scheduled scraping with Celery
- Docker containerization

## Tech Stack

- **Backend**: Django + Django REST Framework
- **Scraping**: Selenium + BeautifulSoup + requests
- **Database**: PostgreSQL (production) / SQLite (development)
- **Task Queue**: Celery + Redis
- **Frontend**: Django templates + HTML/CSS/JavaScript
- **Containerization**: Docker + Docker Compose

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd job-scraper-dashboard

# Build and run with Docker
docker-compose up --build

# Access the application
# Dashboard: http://localhost:8000
# API: http://localhost:8000/api/
```

## Project Structure

```
job-scraper-dashboard/
├── backend/                 # Django backend application
│   ├── apps/               # Django apps
│   │   ├── jobs/          # Job management app
│   │   ├── companies/     # Company management app
│   │   └── scraping/      # Web scraping engine
│   ├── config/            # Django settings and configuration
│   ├── requirements/      # Python dependencies
│   └── manage.py
├── frontend/              # Static files and templates
│   ├── static/           # CSS, JS, images
│   └── templates/        # Django templates
├── docker/               # Docker configuration files
├── scripts/              # Utility scripts
├── tests/                # Test files
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile           # Docker image definition
└── README.md
```

## Development

```bash
# Install dependencies
pip install -r backend/requirements/dev.txt

# Run migrations
python backend/manage.py migrate

# Create superuser
python backend/manage.py createsuperuser

# Run development server
python backend/manage.py runserver
```

## API Documentation

The API endpoints are available at `/api/` with the following main resources:

- `/api/jobs/` - Job listings
- `/api/companies/` - Company information
- `/api/sources/` - Job sources

## License

MIT License
