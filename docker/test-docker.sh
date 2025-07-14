#!/bin/bash

# Test script for Stock API Docker container

echo "Testing Stock API Docker container..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    exit 1
fi

# Change to docker directory
cd "$(dirname "$0")"

# Build and start the container
echo "Building and starting container..."
docker-compose up --build -d

# Wait for the container to be ready
echo "Waiting for container to be ready..."
sleep 30

# Test the API endpoints
echo "Testing API endpoints..."

# Test root endpoint
echo "Testing root endpoint..."
curl -f http://localhost:8000/ || echo "Root endpoint failed"

# Test health check
echo "Testing health check..."
docker-compose exec stock-api curl -f http://localhost:8000/ || echo "Health check failed"

echo "Container is running. You can access the API at http://localhost:8000"
echo "To stop the container, run: docker-compose down"
echo "To view logs, run: docker-compose logs -f stock-api"
