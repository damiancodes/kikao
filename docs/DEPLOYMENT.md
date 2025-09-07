# Deployment Guide

This guide covers various deployment options for the Job Scraper Dashboard.

## Table of Contents

- [Railway (Recommended)](#railway-recommended)
- [DigitalOcean App Platform](#digitalocean-app-platform)
- [Heroku](#heroku)
- [AWS/GCP/Azure](#awsgcpazure)
- [Environment Variables](#environment-variables)
- [Post-Deployment](#post-deployment)

## Railway (Recommended)

Railway is the best option for this project due to its Docker support and managed services.

### Prerequisites
- GitHub account
- Railway account (free tier available)

### Deployment Steps

1. **Fork and Connect Repository**
   ```bash
   # Fork this repository to your GitHub account
   # Connect Railway to your GitHub repository
   ```

2. **Set Up Services**
   - **Web Service**: Main Django application
   - **PostgreSQL**: Database service
   - **Redis**: Cache and message broker
   - **Worker Service**: Celery worker (optional)

3. **Configure Environment Variables**
   ```env
   DEBUG=False
   SECRET_KEY=your-production-secret-key
   DATABASE_URL=postgresql://user:password@host:port/dbname
   REDIS_URL=redis://host:port
   ALLOWED_HOSTS=your-domain.railway.app
   ADZUNA_APP_ID=your-adzuna-app-id
   ADZUNA_APP_KEY=your-adzuna-app-key
   ```

4. **Deploy**
   ```bash
   # Railway will automatically deploy from your GitHub repository
   # The railway.json file contains the deployment configuration
   ```

### Railway Configuration

The `railway.json` file contains:
- Docker build configuration
- Health check settings
- Restart policies
- Start command

## DigitalOcean App Platform

### Prerequisites
- DigitalOcean account
- GitHub repository

### Deployment Steps

1. **Create App**
   - Connect to GitHub repository
   - Select "Docker" as source type

2. **Configure Services**
   - **Web Service**: Django application
   - **Database**: Managed PostgreSQL
   - **Redis**: Redis add-on

3. **Environment Variables**
   ```env
   DEBUG=False
   SECRET_KEY=your-production-secret-key
   DATABASE_URL=postgresql://user:password@host:port/dbname
   REDIS_URL=redis://host:port
   ALLOWED_HOSTS=your-app.ondigitalocean.app
   ```

4. **Deploy**
   - DigitalOcean will build and deploy automatically

## Heroku

### Prerequisites
- Heroku CLI
- Heroku account

### Deployment Steps

1. **Install Heroku CLI**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login and Create App**
   ```bash
   heroku login
   heroku create your-app-name
   ```

3. **Add Add-ons**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   heroku addons:create heroku-redis:hobby-dev
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set DEBUG=False
   heroku config:set SECRET_KEY=your-production-secret-key
   heroku config:set ALLOWED_HOSTS=your-app.herokuapp.com
   heroku config:set ADZUNA_APP_ID=your-adzuna-app-id
   heroku config:set ADZUNA_APP_KEY=your-adzuna-app-key
   ```

5. **Deploy**
   ```bash
   git push heroku main
   heroku run python manage.py migrate
   heroku run python manage.py collectstatic
   ```

6. **Scale Workers**
   ```bash
   heroku ps:scale worker=1
   heroku ps:scale beat=1
   ```

## AWS/GCP/Azure

### AWS Elastic Beanstalk

1. **Create Application**
   - Platform: Docker
   - Upload your code

2. **Configure Environment**
   - Set environment variables
   - Configure RDS for PostgreSQL
   - Configure ElastiCache for Redis

3. **Deploy**
   ```bash
   eb init
   eb create production
   eb deploy
   ```

### Google Cloud Run

1. **Build and Push Image**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/job-scraper
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy --image gcr.io/PROJECT-ID/job-scraper
   ```

3. **Configure Services**
   - Cloud SQL for PostgreSQL
   - Memorystore for Redis

### Azure Container Instances

1. **Build and Push Image**
   ```bash
   az acr build --registry myregistry --image job-scraper .
   ```

2. **Deploy Container**
   ```bash
   az container create --resource-group myResourceGroup --name job-scraper
   ```

## Environment Variables

### Required Variables

```env
# Django Settings
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# Redis
REDIS_URL=redis://host:port

# API Keys
ADZUNA_APP_ID=your-adzuna-app-id
ADZUNA_APP_KEY=your-adzuna-app-key

# Scraping Settings
CHROME_HEADLESS=True
SCRAPING_DELAY=2
MAX_CONCURRENT_SCRAPERS=3
```

### Optional Variables

```env
# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Monitoring
SENTRY_DSN=your-sentry-dsn

# Logging
LOG_LEVEL=INFO
```

## Post-Deployment

### 1. Run Migrations
```bash
python manage.py migrate
```

### 2. Create Superuser
```bash
python manage.py createsuperuser
```

### 3. Initialize Job Sources
```bash
python manage.py init_sources
```

### 4. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 5. Start Background Workers
```bash
# For Celery worker
celery -A config worker --loglevel=info

# For Celery beat
celery -A config beat --loglevel=info
```

## Monitoring and Maintenance

### Health Checks
- **Endpoint**: `/health/`
- **Response**: `200 OK` with "healthy" message

### Logs
- Check application logs regularly
- Monitor error rates
- Set up alerts for failures

### Database Maintenance
- Regular backups
- Monitor connection limits
- Optimize queries

### Performance Monitoring
- Monitor response times
- Track memory usage
- Monitor scraping success rates

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check DATABASE_URL format
   - Verify database credentials
   - Ensure database is accessible

2. **Redis Connection Errors**
   - Check REDIS_URL format
   - Verify Redis service is running
   - Check network connectivity

3. **Scraping Failures**
   - Check internet connectivity
   - Verify target websites are accessible
   - Review anti-detection measures

4. **Static Files Not Loading**
   - Run `collectstatic` command
   - Check static file configuration
   - Verify web server configuration

### Debug Commands

```bash
# Check application status
python manage.py check

# View database status
python manage.py dbshell

# Test Redis connection
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value')
>>> cache.get('test')

# Check Celery status
celery -A config inspect active
```

## Security Considerations

### Production Security
- Set `DEBUG=False`
- Use strong `SECRET_KEY`
- Configure `ALLOWED_HOSTS` properly
- Use HTTPS
- Set up proper CORS policies

### Database Security
- Use strong passwords
- Enable SSL connections
- Regular security updates
- Access control

### API Security
- Implement rate limiting
- Add authentication
- Validate input data
- Monitor for abuse

## Scaling

### Horizontal Scaling
- Multiple web instances
- Load balancer
- Database read replicas
- Redis cluster

### Vertical Scaling
- Increase instance size
- More memory for scraping
- Faster CPU for processing

### Caching
- Redis for session storage
- CDN for static files
- Database query caching
- API response caching

---

For more information, refer to the main README.md and development documentation.
