# Job Scraper Dashboard API Documentation

## Overview

The Job Scraper Dashboard provides a RESTful API for accessing job data, managing scraping sessions, and interacting with the system programmatically.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

Currently, the API uses `AllowAny` permissions for development. For production deployment, implement proper authentication using Django REST Framework's authentication classes.

## Response Format

All API responses are in JSON format with the following structure:

```json
{
    "count": 100,
    "next": "http://localhost:8000/api/jobs/?page=2",
    "previous": null,
    "results": [...]
}
```

## Endpoints

### Jobs

#### List Jobs
```http
GET /api/jobs/
```

**Query Parameters:**
- `search` (string): Search term for job titles and descriptions
- `location` (string): Filter by location
- `company` (string): Filter by company name
- `employment_type` (string): Filter by employment type (Full-time, Part-time, Contract)
- `salary_min` (integer): Minimum salary filter
- `salary_max` (integer): Maximum salary filter
- `source` (string): Filter by job source
- `status` (string): Filter by job status (active, inactive)
- `created_after` (date): Filter jobs created after this date (YYYY-MM-DD)
- `created_before` (date): Filter jobs created before this date (YYYY-MM-DD)
- `ordering` (string): Order results by field (e.g., `-created_at`, `title`)
- `page` (integer): Page number for pagination
- `page_size` (integer): Number of results per page (max 100)

**Example Request:**
```http
GET /api/jobs/?search=python&location=Nairobi&employment_type=Full-time&page=1&page_size=20
```

**Example Response:**
```json
{
    "count": 45,
    "next": "http://localhost:8000/api/jobs/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Senior Python Developer",
            "company_name": "TechCorp Kenya",
            "location": "Nairobi, Kenya",
            "description": "We are looking for a senior Python developer...",
            "source_url": "https://example.com/job/1",
            "salary_min": 150000,
            "salary_max": 200000,
            "salary_currency": "KES",
            "employment_type": "Full-time",
            "experience_level": "Senior",
            "remote_allowed": false,
            "posted_date": "2024-01-15T00:00:00Z",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
            "status": "active",
            "source": {
                "id": 1,
                "name": "Indeed",
                "url": "https://indeed.com"
            }
        }
    ]
}
```

#### Get Job Details
```http
GET /api/jobs/{id}/
```

**Example Response:**
```json
{
    "id": 1,
    "title": "Senior Python Developer",
    "company_name": "TechCorp Kenya",
    "location": "Nairobi, Kenya",
    "description": "We are looking for a senior Python developer...",
    "source_url": "https://example.com/job/1",
    "salary_min": 150000,
    "salary_max": 200000,
    "salary_currency": "KES",
    "employment_type": "Full-time",
    "experience_level": "Senior",
    "remote_allowed": false,
    "posted_date": "2024-01-15T00:00:00Z",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "status": "active",
    "source": {
        "id": 1,
        "name": "Indeed",
        "url": "https://indeed.com"
    }
}
```

#### Get Job Statistics
```http
GET /api/jobs/statistics/
```

**Example Response:**
```json
{
    "total_jobs": 1250,
    "active_jobs": 1180,
    "inactive_jobs": 70,
    "jobs_by_source": {
        "Indeed": 450,
        "Glassdoor": 320,
        "LinkedIn": 280,
        "RemoteOK": 200
    },
    "jobs_by_location": {
        "Nairobi": 400,
        "Mombasa": 150,
        "Remote": 300,
        "New York": 200
    },
    "jobs_by_type": {
        "Full-time": 800,
        "Part-time": 200,
        "Contract": 250
    },
    "average_salary": 180000,
    "salary_currency": "KES"
}
```

#### Export Jobs
```http
GET /api/jobs/export/
```

**Query Parameters:**
- Same filtering parameters as list jobs
- `format` (string): Export format (`csv` or `excel`)

**Example Request:**
```http
GET /api/jobs/export/?search=python&format=csv
```

**Response:** CSV file download

### Companies

#### List Companies
```http
GET /api/companies/
```

**Query Parameters:**
- `search` (string): Search term for company names
- `industry` (string): Filter by industry
- `location` (string): Filter by location
- `size` (string): Filter by company size
- `ordering` (string): Order results by field
- `page` (integer): Page number
- `page_size` (integer): Results per page

**Example Response:**
```json
{
    "count": 50,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "TechCorp Kenya",
            "industry": "Technology",
            "size": "50-200",
            "location": "Nairobi, Kenya",
            "website": "https://techcorp.co.ke",
            "description": "Leading technology company...",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

#### Get Company Details
```http
GET /api/companies/{id}/
```

#### Get Company Statistics
```http
GET /api/companies/statistics/
```

### Scraping Sessions

#### List Scraping Sessions
```http
GET /api/sessions/
```

**Query Parameters:**
- `status` (string): Filter by status (running, completed, failed)
- `query` (string): Filter by search query
- `location` (string): Filter by location
- `created_after` (date): Filter sessions created after this date
- `created_before` (date): Filter sessions created before this date
- `ordering` (string): Order results by field
- `page` (integer): Page number
- `page_size` (integer): Results per page

**Example Response:**
```json
{
    "count": 25,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "query": "Python Developer",
            "location": "Nairobi",
            "max_results": 50,
            "status": "completed",
            "jobs_found": 45,
            "jobs_created": 40,
            "jobs_updated": 5,
            "errors": 0,
            "duplicates_merged": 2,
            "started_at": "2024-01-15T10:30:00Z",
            "completed_at": "2024-01-15T10:35:00Z",
            "duration": "00:05:00",
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

#### Get Scraping Session Details
```http
GET /api/sessions/{id}/
```

#### Execute Scraping Session
```http
POST /api/sessions/{id}/execute/
```

**Example Response:**
```json
{
    "message": "Scraping session started",
    "session_id": 1,
    "status": "running"
}
```

### Job Sources

#### List Job Sources
```http
GET /api/sources/
```

**Example Response:**
```json
{
    "count": 8,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Indeed",
            "url": "https://indeed.com",
            "is_active": true,
            "scraper_type": "selenium",
            "description": "Global job search engine",
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

#### Get Job Source Details
```http
GET /api/sources/{id}/
```

## Error Handling

The API uses standard HTTP status codes and returns error details in the response body.

### Common Error Responses

#### 400 Bad Request
```json
{
    "error": "Invalid request parameters",
    "details": {
        "field_name": ["This field is required."]
    }
}
```

#### 404 Not Found
```json
{
    "error": "Not found",
    "details": "The requested resource was not found."
}
```

#### 500 Internal Server Error
```json
{
    "error": "Internal server error",
    "details": "An unexpected error occurred."
}
```

## Rate Limiting

- **General API endpoints**: 10 requests per second per IP
- **Scraping endpoints**: 1 request per second per IP
- **Export endpoints**: 5 requests per minute per IP

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
X-RateLimit-Reset: 1640995200
```

## Pagination

All list endpoints support pagination with the following parameters:
- `page`: Page number (1-based)
- `page_size`: Number of results per page (max 100, default 20)

Pagination information is included in the response:
```json
{
    "count": 1000,
    "next": "http://localhost:8000/api/jobs/?page=2",
    "previous": null,
    "results": [...]
}
```

## Filtering and Ordering

Most endpoints support filtering and ordering:

### Filtering
Use query parameters to filter results:
```
GET /api/jobs/?search=python&location=Nairobi&employment_type=Full-time
```

### Ordering
Use the `ordering` parameter to sort results:
```
GET /api/jobs/?ordering=-created_at  # Newest first
GET /api/jobs/?ordering=title        # Alphabetical by title
GET /api/jobs/?ordering=-salary_max  # Highest salary first
```

## Examples

### Python Example
```python
import requests
import json

# Base URL
base_url = "http://localhost:8000/api"

# Search for Python jobs in Nairobi
response = requests.get(f"{base_url}/jobs/", params={
    "search": "python",
    "location": "Nairobi",
    "employment_type": "Full-time",
    "page_size": 20
})

if response.status_code == 200:
    data = response.json()
    print(f"Found {data['count']} jobs")
    for job in data['results']:
        print(f"- {job['title']} at {job['company_name']}")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

### JavaScript Example
```javascript
// Search for jobs
async function searchJobs(query, location) {
    try {
        const response = await fetch(`/api/jobs/?search=${query}&location=${location}`);
        const data = await response.json();
        
        if (response.ok) {
            console.log(`Found ${data.count} jobs`);
            return data.results;
        } else {
            console.error('Error:', data.error);
            return [];
        }
    } catch (error) {
        console.error('Network error:', error);
        return [];
    }
}

// Usage
searchJobs('python developer', 'Nairobi').then(jobs => {
    jobs.forEach(job => {
        console.log(`${job.title} at ${job.company_name}`);
    });
});
```

### cURL Examples
```bash
# List all jobs
curl "http://localhost:8000/api/jobs/"

# Search for Python jobs
curl "http://localhost:8000/api/jobs/?search=python&location=Nairobi"

# Get job statistics
curl "http://localhost:8000/api/jobs/statistics/"

# Export jobs to CSV
curl "http://localhost:8000/api/jobs/export/?format=csv" -o jobs.csv

# Execute scraping session
curl -X POST "http://localhost:8000/api/sessions/1/execute/"
```

## SDKs and Libraries

### Python
```python
pip install requests
```

### JavaScript/Node.js
```bash
npm install axios
```

### PHP
```bash
composer require guzzlehttp/guzzle
```

## Support

For API support and questions:
- Check the troubleshooting section in README.md
- Create an issue in the GitHub repository
- Review the Django REST Framework documentation
