#!/bin/bash

# FastAPI Keycloak Application Startup Script

echo "Starting FastAPI Keycloak Application..."

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed or not in PATH"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Function to wait for a service to be ready
wait_for_service() {
    local service_name=$1
    local url=$2
    local max_attempts=${3:-30}
    
    echo "Waiting for $service_name to be ready..."
    
    for i in $(seq 1 $max_attempts); do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo "$service_name is ready!"
            return 0
        fi
        echo "Attempt $i/$max_attempts - $service_name not ready yet..."
        sleep 5
    done
    
    echo "Error: $service_name failed to start within $(($max_attempts * 5)) seconds"
    return 1
}

# Start the services
echo "Starting Docker services..."
docker-compose up -d

# Initialize Keycloak configuration
echo "Initializing Keycloak configuration..."
if command -v python3 &> /dev/null; then
    python3 scripts/init_keycloak.py
elif command -v python &> /dev/null; then
    python scripts/init_keycloak.py
else
    echo "Warning: Python not found. Keycloak initialization skipped."
    echo "Please run the initialization script manually:"
    echo "  python scripts/init_keycloak.py"
fi

# Wait for the FastAPI application to be ready
if ! wait_for_service "FastAPI Application" "http://localhost:8000/health"; then
    echo "Failed to start FastAPI application. Check the logs with: docker-compose logs app"
    exit 1
fi

echo ""
echo "🎉 Application started successfully!"
echo ""
echo "Services available at:"
echo "  🚀 FastAPI Application: http://localhost:8000"
echo "  📚 API Documentation: http://localhost:8000/docs"
echo "  🔐 Keycloak Admin Console: http://localhost:8080"
echo ""
echo "Default Keycloak admin credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "Test users created:"
echo "  • admin / password"
echo "  • testuser / password"
echo ""
echo "To stop the application, run:"
echo "  docker-compose down"
echo ""
echo "To view logs, run:"
echo "  docker-compose logs -f [service_name]"
echo ""

# Optionally keep the script running to show logs
if [[ "${1:-}" == "--logs" ]]; then
    echo "Showing application logs (Ctrl+C to exit):"
    docker-compose logs -f app
fi 