#!/bin/bash

# Job Scraper Dashboard Setup Script
# This script sets up the development environment for the Job Scraper Dashboard

set -e

echo "🚀 Setting up Job Scraper Dashboard..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if .env file exists
check_env() {
    print_status "Checking environment configuration..."
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        cp env.example .env
        print_success ".env file created from template"
        print_warning "Please edit .env file with your configuration before continuing"
    else
        print_success ".env file found"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs
    mkdir -p data/postgres
    mkdir -p data/redis
    print_success "Directories created"
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    docker-compose build --no-cache
    print_success "Docker images built"
}

# Start services
start_services() {
    print_status "Starting services..."
    docker-compose up -d db redis
    print_status "Waiting for database to be ready..."
    sleep 10
    print_success "Services started"
}

# Run migrations
run_migrations() {
    print_status "Running database migrations..."
    docker-compose exec -T web python manage.py migrate
    print_success "Migrations completed"
}

# Create superuser
create_superuser() {
    print_status "Creating superuser account..."
    echo "Please enter details for the admin account:"
    docker-compose exec web python manage.py createsuperuser
    print_success "Superuser created"
}

# Initialize job sources
init_sources() {
    print_status "Initializing job sources..."
    docker-compose exec -T web python manage.py init_sources
    print_success "Job sources initialized"
}

# Collect static files
collect_static() {
    print_status "Collecting static files..."
    docker-compose exec -T web python manage.py collectstatic --noinput
    print_success "Static files collected"
}

# Start the application
start_application() {
    print_status "Starting the application..."
    docker-compose up -d
    print_success "Application started"
}

# Show final instructions
show_instructions() {
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Access the dashboard: http://localhost:8000"
    echo "2. Access the admin panel: http://localhost:8000/admin"
    echo "3. View API documentation: http://localhost:8000/api/"
    echo ""
    echo "🔧 Useful commands:"
    echo "- View logs: docker-compose logs -f"
    echo "- Stop services: docker-compose down"
    echo "- Restart services: docker-compose restart"
    echo "- Access shell: docker-compose exec web bash"
    echo ""
    echo "📚 Documentation:"
    echo "- README.md for detailed setup instructions"
    echo "- API documentation available at /api/"
    echo ""
}

# Main setup function
main() {
    echo "Job Scraper Dashboard Setup"
    echo "=========================="
    echo ""
    
    check_docker
    check_env
    create_directories
    build_images
    start_services
    run_migrations
    
    # Ask if user wants to create superuser
    read -p "Do you want to create a superuser account? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_superuser
    fi
    
    init_sources
    collect_static
    start_application
    show_instructions
}

# Run main function
main "$@"