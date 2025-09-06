# Job Scraper Dashboard Setup Script for Windows
# This script sets up the development environment for the Job Scraper Dashboard

param(
    [switch]$SkipSuperuser,
    [switch]$Help
)

if ($Help) {
    Write-Host "Job Scraper Dashboard Setup Script" -ForegroundColor Blue
    Write-Host "Usage: .\scripts\setup.ps1 [-SkipSuperuser] [-Help]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Green
    Write-Host "  -SkipSuperuser    Skip creating superuser account" -ForegroundColor White
    Write-Host "  -Help             Show this help message" -ForegroundColor White
    exit 0
}

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if Docker is installed
function Test-Docker {
    Write-Status "Checking Docker installation..."
    
    try {
        $dockerVersion = docker --version
        $composeVersion = docker-compose --version
        Write-Success "Docker and Docker Compose are installed"
        Write-Host "  Docker: $dockerVersion" -ForegroundColor Gray
        Write-Host "  Compose: $composeVersion" -ForegroundColor Gray
    }
    catch {
        Write-Error "Docker or Docker Compose is not installed. Please install Docker Desktop first."
        exit 1
    }
}

# Check if .env file exists
function Test-EnvFile {
    Write-Status "Checking environment configuration..."
    
    if (-not (Test-Path ".env")) {
        Write-Warning ".env file not found. Creating from template..."
        Copy-Item "env.example" ".env"
        Write-Success ".env file created from template"
        Write-Warning "Please edit .env file with your configuration before continuing"
    }
    else {
        Write-Success ".env file found"
    }
}

# Create necessary directories
function New-Directories {
    Write-Status "Creating necessary directories..."
    
    $directories = @("logs", "data\postgres", "data\redis")
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Write-Success "Directories created"
}

# Build Docker images
function Build-Images {
    Write-Status "Building Docker images..."
    docker-compose build --no-cache
    Write-Success "Docker images built"
}

# Start services
function Start-Services {
    Write-Status "Starting services..."
    docker-compose up -d db redis
    Write-Status "Waiting for database to be ready..."
    Start-Sleep -Seconds 10
    Write-Success "Services started"
}

# Run migrations
function Invoke-Migrations {
    Write-Status "Running database migrations..."
    docker-compose exec -T web python manage.py migrate
    Write-Success "Migrations completed"
}

# Create superuser
function New-Superuser {
    Write-Status "Creating superuser account..."
    Write-Host "Please enter details for the admin account:" -ForegroundColor Yellow
    docker-compose exec web python manage.py createsuperuser
    Write-Success "Superuser created"
}

# Initialize job sources
function Initialize-Sources {
    Write-Status "Initializing job sources..."
    docker-compose exec -T web python manage.py init_sources
    Write-Success "Job sources initialized"
}

# Collect static files
function Collect-StaticFiles {
    Write-Status "Collecting static files..."
    docker-compose exec -T web python manage.py collectstatic --noinput
    Write-Success "Static files collected"
}

# Start the application
function Start-Application {
    Write-Status "Starting the application..."
    docker-compose up -d
    Write-Success "Application started"
}

# Show final instructions
function Show-Instructions {
    Write-Host ""
    Write-Host "🎉 Setup completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next steps:" -ForegroundColor Blue
    Write-Host "1. Access the dashboard: http://localhost:8000" -ForegroundColor White
    Write-Host "2. Access the admin panel: http://localhost:8000/admin" -ForegroundColor White
    Write-Host "3. View API documentation: http://localhost:8000/api/" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Useful commands:" -ForegroundColor Blue
    Write-Host "- View logs: docker-compose logs -f" -ForegroundColor White
    Write-Host "- Stop services: docker-compose down" -ForegroundColor White
    Write-Host "- Restart services: docker-compose restart" -ForegroundColor White
    Write-Host "- Access shell: docker-compose exec web bash" -ForegroundColor White
    Write-Host ""
    Write-Host "📚 Documentation:" -ForegroundColor Blue
    Write-Host "- README.md for detailed setup instructions" -ForegroundColor White
    Write-Host "- API documentation available at /api/" -ForegroundColor White
    Write-Host ""
}

# Main setup function
function Main {
    Write-Host "Job Scraper Dashboard Setup" -ForegroundColor Blue
    Write-Host "==========================" -ForegroundColor Blue
    Write-Host ""
    
    Test-Docker
    Test-EnvFile
    New-Directories
    Build-Images
    Start-Services
    Invoke-Migrations
    
    if (-not $SkipSuperuser) {
        $createSuperuser = Read-Host "Do you want to create a superuser account? (y/n)"
        if ($createSuperuser -eq "y" -or $createSuperuser -eq "Y") {
            New-Superuser
        }
    }
    
    Initialize-Sources
    Collect-StaticFiles
    Start-Application
    Show-Instructions
}

# Run main function
Main
