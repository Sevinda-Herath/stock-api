#!/bin/bash

# Docker management script for Stock API

case "$1" in
    "build")
        echo "Building Docker container..."
        cd docker && docker-compose build
        ;;
    "start")
        echo "Starting Docker container..."
        cd docker && docker-compose up -d
        ;;
    "stop")
        echo "Stopping Docker container..."
        cd docker && docker-compose down
        ;;
    "restart")
        echo "Restarting Docker container..."
        cd docker && docker-compose restart
        ;;
    "logs")
        echo "Showing Docker container logs..."
        cd docker && docker-compose logs -f stock-api
        ;;
    "shell")
        echo "Opening shell in Docker container..."
        cd docker && docker-compose exec stock-api /bin/bash
        ;;
    "test")
        echo "Running Docker tests..."
        cd docker && ./test-docker.sh
        ;;
    *)
        echo "Usage: $0 {build|start|stop|restart|logs|shell|test}"
        echo ""
        echo "Commands:"
        echo "  build   - Build the Docker image"
        echo "  start   - Start the container in detached mode"
        echo "  stop    - Stop the container"
        echo "  restart - Restart the container"
        echo "  logs    - Show container logs"
        echo "  shell   - Open shell in container"
        echo "  test    - Run Docker tests"
        echo ""
        echo "Examples:"
        echo "  $0 build && $0 start  # Build and start"
        echo "  $0 logs              # View logs"
        echo "  $0 shell             # Access container shell"
        exit 1
        ;;
esac
