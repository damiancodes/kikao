#!/bin/bash

# Script to view Docker logs for the Job Scraper application

echo "=== Job Scraper Docker Logs ==="
echo ""

# Function to show logs for a specific service
show_logs() {
    local service=$1
    echo "=== $service logs ==="
    docker-compose logs -f --tail=50 $service
}

# Function to show all logs
show_all_logs() {
    echo "=== All services logs ==="
    docker-compose logs -f --tail=50
}

# Function to show logs for specific container
show_container_logs() {
    local container=$1
    echo "=== Container $container logs ==="
    docker logs -f --tail=50 $container
}

# Function to show real-time logs
show_realtime_logs() {
    echo "=== Real-time logs (all services) ==="
    docker-compose logs -f
}

# Function to show logs with timestamps
show_timestamped_logs() {
    local service=$1
    if [ -z "$service" ]; then
        echo "=== All services logs with timestamps ==="
        docker-compose logs -f --timestamps
    else
        echo "=== $service logs with timestamps ==="
        docker-compose logs -f --timestamps $service
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTION] [SERVICE]"
    echo ""
    echo "Options:"
    echo "  -a, --all              Show logs for all services"
    echo "  -w, --web              Show logs for web service"
    echo "  -c, --celery           Show logs for celery service"
    echo "  -b, --beat             Show logs for celery-beat service"
    echo "  -d, --db               Show logs for database service"
    echo "  -r, --redis            Show logs for redis service"
    echo "  -t, --timestamps       Show logs with timestamps"
    echo "  -f, --follow           Follow logs in real-time"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -w                  # Show web service logs"
    echo "  $0 -a                  # Show all services logs"
    echo "  $0 -w -t               # Show web logs with timestamps"
    echo "  $0 -f                  # Follow all logs in real-time"
    echo ""
    echo "Available services: web, celery, celery-beat, db, redis"
}

# Parse command line arguments
case "$1" in
    -a|--all)
        show_all_logs
        ;;
    -w|--web)
        show_logs "web"
        ;;
    -c|--celery)
        show_logs "celery"
        ;;
    -b|--beat)
        show_logs "celery-beat"
        ;;
    -d|--db)
        show_logs "db"
        ;;
    -r|--redis)
        show_logs "redis"
        ;;
    -t|--timestamps)
        show_timestamped_logs "$2"
        ;;
    -f|--follow)
        show_realtime_logs
        ;;
    -h|--help)
        show_help
        ;;
    "")
        echo "No option specified. Use -h for help."
        echo ""
        echo "Quick start:"
        echo "  $0 -w    # View web service logs"
        echo "  $0 -a    # View all service logs"
        ;;
    *)
        echo "Unknown option: $1"
        echo "Use -h for help."
        exit 1
        ;;
esac
