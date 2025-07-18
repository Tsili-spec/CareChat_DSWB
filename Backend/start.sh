#!/bin/bash

# CareChat Backend Docker Startup Script

set -e  # Exit on any error

echo "🚀 CareChat Backend Docker Setup"
echo "================================="

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo "❌ Docker is not running. Please start Docker and try again."
        exit 1
    fi
    echo "✅ Docker is running"
}

# Function to check if docker-compose is available
check_docker_compose() {
    if ! command -v docker-compose >/dev/null 2>&1; then
        echo "❌ docker-compose not found. Please install docker-compose."
        exit 1
    fi
    echo "✅ docker-compose is available"
}

# Function to create .env file if it doesn't exist
setup_env() {
    if [ ! -f .env ]; then
        echo "📄 Creating .env file from template..."
        cp env.example .env
        echo "⚠️  Please edit .env file with your configuration before running in production!"
    else
        echo "✅ .env file exists"
    fi
}

# Function to start services
start_services() {
    local mode=${1:-dev}
    
    if [ "$mode" = "prod" ]; then
        echo "🏭 Starting production services..."
        docker-compose -f docker-compose.prod.yml up -d
    else
        echo "🛠️  Starting development services..."
        docker-compose up -d
    fi
}

# Function to show service status
show_status() {
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    
    echo ""
    echo "🌐 Access URLs:"
    echo "  - API: http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo "  - Database: localhost:5432"
    
    if docker-compose ps | grep -q pgadmin; then
        echo "  - pgAdmin: http://localhost:8080"
    fi
}

# Function to show logs
show_logs() {
    echo "📋 Recent logs:"
    docker-compose logs --tail=10 backend
}

# Main execution
main() {
    local command=${1:-start}
    
    case $command in
        "start"|"up")
            check_docker
            check_docker_compose
            setup_env
            start_services dev
            show_status
            ;;
        "prod")
            check_docker
            check_docker_compose
            setup_env
            start_services prod
            show_status
            ;;
        "stop"|"down")
            echo "🛑 Stopping services..."
            docker-compose down
            ;;
        "restart")
            echo "🔄 Restarting services..."
            docker-compose restart
            show_status
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        "clean")
            echo "🧹 Cleaning up Docker resources..."
            docker-compose down -v
            docker system prune -f
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  start, up    Start development services (default)"
            echo "  prod         Start production services"
            echo "  stop, down   Stop all services"
            echo "  restart      Restart all services"
            echo "  logs         Show recent logs"
            echo "  status       Show service status"
            echo "  clean        Stop services and clean Docker resources"
            echo "  help         Show this help message"
            ;;
        *)
            echo "❌ Unknown command: $command"
            echo "Use '$0 help' for available commands"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 