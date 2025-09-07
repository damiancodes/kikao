#!/bin/bash

# Railway CLI Setup Script for Job Scraper Dashboard
# This script helps set up Railway CLI and deploy the project

set -e

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

# Check if Railway CLI is installed
check_railway_cli() {
    print_status "Checking Railway CLI installation..."
    
    if command -v railway &> /dev/null; then
        print_success "Railway CLI is already installed"
        railway --version
    else
        print_warning "Railway CLI not found. Installing..."
        install_railway_cli
    fi
}

# Install Railway CLI
install_railway_cli() {
    print_status "Installing Railway CLI..."
    
    # Check if npm is available
    if command -v npm &> /dev/null; then
        print_status "Installing via npm..."
        npm install -g @railway/cli
    else
        print_error "npm not found. Please install Node.js first or install Railway CLI manually."
        print_status "Manual installation: https://github.com/railwayapp/cli/releases"
        exit 1
    fi
    
    print_success "Railway CLI installed successfully"
}

# Login to Railway
login_railway() {
    print_status "Logging into Railway..."
    railway login
    
    if [ $? -eq 0 ]; then
        print_success "Successfully logged into Railway"
    else
        print_error "Failed to login to Railway"
        exit 1
    fi
}

# Initialize Railway project
init_railway() {
    print_status "Initializing Railway project..."
    
    # Check if already linked
    if [ -f ".railway/project.json" ]; then
        print_warning "Project already linked to Railway"
        railway status
    else
        print_status "Linking to Railway project..."
        railway init
    fi
}

# Set up environment variables
setup_env_vars() {
    print_status "Setting up environment variables..."
    
    # Required variables
    local vars=(
        "DEBUG=False"
        "SECRET_KEY=$(openssl rand -base64 32)"
        "ALLOWED_HOSTS=*.railway.app"
    )
    
    # Optional variables (user can set these manually)
    local optional_vars=(
        "ADZUNA_APP_ID"
        "ADZUNA_APP_KEY"
        "LOG_LEVEL=INFO"
    )
    
    print_status "Setting required environment variables..."
    for var in "${vars[@]}"; do
        railway variables set "$var"
        print_success "Set: $var"
    done
    
    print_warning "Please set the following optional variables manually:"
    for var in "${optional_vars[@]}"; do
        echo "  railway variables set $var=your-value"
    done
}

# Deploy the project
deploy_project() {
    print_status "Deploying project to Railway..."
    
    # Deploy web service
    print_status "Deploying web service..."
    railway up --service web
    
    if [ $? -eq 0 ]; then
        print_success "Web service deployed successfully"
    else
        print_error "Failed to deploy web service"
        exit 1
    fi
}

# Run post-deployment setup
post_deployment() {
    print_status "Running post-deployment setup..."
    
    # Run migrations
    print_status "Running database migrations..."
    railway run python manage.py migrate
    
    # Collect static files
    print_status "Collecting static files..."
    railway run python manage.py collectstatic --noinput
    
    # Initialize job sources
    print_status "Initializing job sources..."
    railway run python manage.py init_sources
    
    print_success "Post-deployment setup completed"
}

# Show deployment info
show_deployment_info() {
    print_status "Getting deployment information..."
    
    echo ""
    print_success "🎉 Deployment completed successfully!"
    echo ""
    print_status "📋 Next steps:"
    echo "1. Get your app URL:"
    echo "   railway domain"
    echo ""
    echo "2. Create superuser account:"
    echo "   railway run python manage.py createsuperuser"
    echo ""
    echo "3. View logs:"
    echo "   railway logs --follow"
    echo ""
    echo "4. Set additional environment variables:"
    echo "   railway variables set ADZUNA_APP_ID=your-id"
    echo "   railway variables set ADZUNA_APP_KEY=your-key"
    echo ""
    print_status "🔧 Useful commands:"
    echo "- View status: railway status"
    echo "- View logs: railway logs"
    echo "- Connect to DB: railway connect postgres"
    echo "- Run commands: railway run python manage.py <command>"
    echo ""
}

# Main function
main() {
    echo "Railway CLI Setup for Job Scraper Dashboard"
    echo "==========================================="
    echo ""
    
    check_railway_cli
    login_railway
    init_railway
    setup_env_vars
    deploy_project
    post_deployment
    show_deployment_info
}

# Run main function
main "$@"
