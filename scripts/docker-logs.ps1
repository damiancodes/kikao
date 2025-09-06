# PowerShell script to view Docker logs for the Job Scraper application

param(
    [Parameter(Position=0)]
    [string]$Service = "",
    [switch]$All,
    [switch]$Web,
    [switch]$Celery,
    [switch]$Beat,
    [switch]$Db,
    [switch]$Redis,
    [switch]$Timestamps,
    [switch]$Follow,
    [switch]$Help
)

function Show-Logs {
    param(
        [string]$ServiceName,
        [switch]$WithTimestamps,
        [switch]$FollowLogs
    )
    
    $logArgs = @()
    
    if ($WithTimestamps) {
        $logArgs += "--timestamps"
    }
    
    if ($FollowLogs) {
        $logArgs += "-f"
    } else {
        $logArgs += "--tail=50"
    }
    
    if ($ServiceName) {
        Write-Host "=== $ServiceName logs ===" -ForegroundColor Green
        docker-compose logs $logArgs $ServiceName
    } else {
        Write-Host "=== All services logs ===" -ForegroundColor Green
        docker-compose logs $logArgs
    }
}

function Show-Help {
    Write-Host "Job Scraper Docker Logs Viewer" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\scripts\docker-logs.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -All              Show logs for all services"
    Write-Host "  -Web              Show logs for web service"
    Write-Host "  -Celery           Show logs for celery service"
    Write-Host "  -Beat             Show logs for celery-beat service"
    Write-Host "  -Db               Show logs for database service"
    Write-Host "  -Redis            Show logs for redis service"
    Write-Host "  -Timestamps       Show logs with timestamps"
    Write-Host "  -Follow           Follow logs in real-time"
    Write-Host "  -Help             Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\scripts\docker-logs.ps1 -Web                    # Show web service logs"
    Write-Host "  .\scripts\docker-logs.ps1 -All                    # Show all services logs"
    Write-Host "  .\scripts\docker-logs.ps1 -Web -Timestamps        # Show web logs with timestamps"
    Write-Host "  .\scripts\docker-logs.ps1 -Follow                 # Follow all logs in real-time"
    Write-Host ""
    Write-Host "Available services: web, celery, celery-beat, db, redis"
}

# Main logic
if ($Help) {
    Show-Help
    exit 0
}

if ($All -or $Service -eq "") {
    Show-Logs -WithTimestamps:$Timestamps -FollowLogs:$Follow
} elseif ($Web) {
    Show-Logs -ServiceName "web" -WithTimestamps:$Timestamps -FollowLogs:$Follow
} elseif ($Celery) {
    Show-Logs -ServiceName "celery" -WithTimestamps:$Timestamps -FollowLogs:$Follow
} elseif ($Beat) {
    Show-Logs -ServiceName "celery-beat" -WithTimestamps:$Timestamps -FollowLogs:$Follow
} elseif ($Db) {
    Show-Logs -ServiceName "db" -WithTimestamps:$Timestamps -FollowLogs:$Follow
} elseif ($Redis) {
    Show-Logs -ServiceName "redis" -WithTimestamps:$Timestamps -FollowLogs:$Follow
} elseif ($Service) {
    Show-Logs -ServiceName $Service -WithTimestamps:$Timestamps -FollowLogs:$Follow
} else {
    Write-Host "No option specified. Use -Help for help." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Quick start:"
    Write-Host "  .\scripts\docker-logs.ps1 -Web    # View web service logs"
    Write-Host "  .\scripts\docker-logs.ps1 -All    # View all service logs"
}
