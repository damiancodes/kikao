#!/bin/bash

# Job Scraper Setup Script

echo "Setting up Job Scraper Dashboard..."

echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements/dev.txt

# Create environment file
echo "Creating environment file..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "Please edit .env file with your configuration"
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p media
mkdir -p staticfiles

# Run Django migrations
echo "Running Django migrations..."
cd backend
python manage.py makemigrations
python manage.py migrate

# Create superuser
echo "Creating superuser..."
python manage.py createsuperuser

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create initial data
echo "Creating initial data..."
python manage.py shell << EOF
from apps.jobs.models import JobSource

# Create job sources
sources = [
    {'name': 'LinkedIn', 'base_url': 'https://www.linkedin.com/jobs/search'},
    {'name': 'Indeed', 'base_url': 'https://www.indeed.com/jobs'},
    {'name': 'Glassdoor', 'base_url': 'https://www.glassdoor.com/Job/jobs.htm'},
    {'name': 'RemoteOK', 'base_url': 'https://remoteok.com/api'},
]

for source_data in sources:
    JobSource.objects.get_or_create(
        name=source_data['name'],
        defaults={'base_url': source_data['base_url']}
    )

print("Initial data created successfully!")
EOF

cd ..

echo "Setup completed successfully!"
echo ""
echo "To start the development server:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start Django server: cd backend && python manage.py runserver"
echo "3. Start Celery worker: celery -A config worker --loglevel=info"
echo "4. Start Celery beat: celery -A config beat --loglevel=info"
echo ""
echo "To start with Docker:"
echo "docker-compose up --build"





