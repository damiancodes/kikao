# Railway CLI Setup Script for Job Scraper Dashboard (Windows)
# This script helps set up Railway CLI and deploy the project

param(
    [switch]$SkipLogin,
    [switch]$Help
)

if ($Help) {
    Write-Host "Railway CLI Setup Script" -ForegroundColor Blue
    Write-Host "Usage: .\scripts\railway-setup.ps1 [-SkipLogin] [-Help]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Green
    Write-Host "  -SkipLogin    Skip Railway login step" -ForegroundColor White
    Write-Host "  -Help         Show this help message" -ForegroundColor White
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

# Check if Railway CLI is installed
function Test-RailwayCLI {
    Write-Status "Checking Railway CLI installation..."
    
    try {
        $version = railway --version
        Write-Success "Railway CLI is already installed"
        Write-Host "  Version: $version" -ForegroundColor Gray
        return $true
    }
    catch {
        Write-Warning "Railway CLI not found. Installing..."
        return $false
    }
}

# Install Railway CLI
function Install-RailwayCLI {
    Write-Status "Installing Railway CLI..."
    
    # Check if npm is available
    try {
        $npmVersion = npm --version
        Write-Status "Installing via npm (version: $npmVersion)..."
        npm install -g @railway/cli
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Railway CLI installed successfully"
            return $true
        } else {
            Write-Error "Failed to install Railway CLI via npm"
            return $false
        }
    }
    catch {
        Write-Error "npm not found. Please install Node.js first or install Railway CLI manually."
        Write-Status "Manual installation: https://github.com/railwayapp/cli/releases"
        return $false
    }
}

# Login to Railway
function Connect-Railway {
    if ($SkipLogin) {
        Write-Warning "Skipping Railway login"
        return $true
    }
    
    Write-Status "Logging into Railway..."
    railway login
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Successfully logged into Railway"
        return $true
    } else {
        Write-Error "Failed to login to Railway"
        return $false
    }
}

# Initialize Railway project
function Initialize-RailwayProject {
    Write-Status "Initializing Railway project..."
    
    # Check if already linked
    if (Test-Path ".railway/project.json") {
        Write-Warning "Project already linked to Railway"
        railway status
    } else {
        Write-Status "Linking to Railway project..."
        railway init
    }
}

# Set up environment variables
function Set-EnvironmentVariables {
    Write-Status "Setting up environment variables..."
    
    # Required variables
    $requiredVars = @(
        "DEBUG=False",
        "SECRET_KEY=$(([System.Web.Security.Membership]::GeneratePassword(32, 0)))",
        "ALLOWED_HOSTS=*.railway.app"
    )
    
    # Optional variables (user can set these manually)
    $optionalVars = @(
        "ADZUNA_APP_ID",
        "ADZUNA_APP_KEY",
        "LOG_LEVEL=INFO"
    )
    
    Write-Status "Setting required environment variables..."
    foreach ($var in $requiredVars) {
        railway variables set $var
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Set: $var"
        } else {
            Write-Warning "Failed to set: $var"
        }
    }
    
    Write-Warning "Please set the following optional variables manually:"
    foreach ($var in $optionalVars) {
        Write-Host "  railway variables set $var=your-value" -ForegroundColor Yellow
    }
}

# Deploy the project
function Deploy-Project {
    Write-Status "Deploying project to Railway..."
    
    # Deploy web service
    Write-Status "Deploying web service..."
    railway up --service web
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Web service deployed successfully"
        return $true
    } else {
        Write-Error "Failed to deploy web service"
        return $false
    }
}

# Run post-deployment setup
function Invoke-PostDeployment {
    Write-Status "Running post-deployment setup..."
    
    # Run migrations
    Write-Status "Running database migrations..."
    railway run python manage.py migrate
    
    # Collect static files
    Write-Status "Collecting static files..."
    railway run python manage.py collectstatic --noinput
    
    # Initialize job sources
    Write-Status "Initializing job sources..."
    railway run python manage.py init_sources
    
    Write-Success "Post-deployment setup completed"
}

# Show deployment info
function Show-DeploymentInfo {
    Write-Status "Getting deployment information..."
    
    Write-Host ""
    Write-Success "🎉 Deployment completed successfully!"
    Write-Host ""
    Write-Status "📋 Next steps:"
    Write-Host "1. Get your app URL:"
    Write-Host "   railway domain" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Create superuser account:"
    Write-Host "   railway run python manage.py createsuperuser" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. View logs:"
    Write-Host "   railway logs --follow" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. Set additional environment variables:"
    Write-Host "   railway variables set ADZUNA_APP_ID=your-id" -ForegroundColor Gray
    Write-Host "   railway variables set ADZUNA_APP_KEY=your-key" -ForegroundColor Gray
    Write-Host ""
    Write-Status "🔧 Useful commands:"
    Write-Host "- View status: railway status" -ForegroundColor Gray
    Write-Host "- View logs: railway logs" -ForegroundColor Gray
    Write-Host "- Connect to DB: railway connect postgres" -ForegroundColor Gray
    Write-Host "- Run commands: railway run python manage.py <command>" -ForegroundColor Gray
    Write-Host ""
}

# Main function
function Main {
    Write-Host "Railway CLI Setup for Job Scraper Dashboard" -ForegroundColor Blue
    Write-Host "===========================================" -ForegroundColor Blue
    Write-Host ""
    
    if (-not (Test-RailwayCLI)) {
        if (-not (Install-RailwayCLI)) {
            exit 1
        }
    }
    
    if (-not (Connect-Railway)) {
        exit 1
    }
    
    Initialize-RailwayProject
    Set-EnvironmentVariables
    
    if (Deploy-Project) {
        Invoke-PostDeployment
        Show-DeploymentInfo
    } else {
        Write-Error "Deployment failed"
        exit 1
    }
}

# Run main function
Main
