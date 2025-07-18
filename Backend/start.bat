@echo off
setlocal enabledelayedexpansion

REM CareChat Backend Docker Startup Script for Windows

echo 🚀 CareChat Backend Docker Setup
echo =================================

REM Set command (default to start)
set "command=%1"
if "%command%"=="" set "command=start"

REM Function to check if Docker is running
:check_docker
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker and try again.
    exit /b 1
)
echo ✅ Docker is running
goto :eof

REM Function to check if docker-compose is available
:check_docker_compose
docker-compose version >nul 2>&1
if errorlevel 1 (
    echo ❌ docker-compose not found. Please install docker-compose.
    exit /b 1
)
echo ✅ docker-compose is available
goto :eof

REM Function to create .env file if it doesn't exist
:setup_env
if not exist ".env" (
    echo 📄 Creating .env file from template...
    copy env.example .env >nul
    echo ⚠️  Please edit .env file with your configuration before running in production!
) else (
    echo ✅ .env file exists
)
goto :eof

REM Function to start services
:start_services
set "mode=%1"
if "%mode%"=="prod" (
    echo 🏭 Starting production services...
    docker-compose -f docker-compose.prod.yml up -d
) else (
    echo 🛠️  Starting development services...
    docker-compose up -d
)
goto :eof

REM Function to show service status
:show_status
echo.
echo 📊 Service Status:
docker-compose ps
echo.
echo 🌐 Access URLs:
echo   - API: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo   - Database: localhost:5432
docker-compose ps | findstr pgadmin >nul 2>&1
if not errorlevel 1 (
    echo   - pgAdmin: http://localhost:8080
)
goto :eof

REM Function to show logs
:show_logs
echo 📋 Recent logs:
docker-compose logs --tail=10 backend
goto :eof

REM Main execution
if "%command%"=="start" goto start_dev
if "%command%"=="up" goto start_dev
if "%command%"=="prod" goto start_prod
if "%command%"=="stop" goto stop_services
if "%command%"=="down" goto stop_services
if "%command%"=="restart" goto restart_services
if "%command%"=="logs" goto logs_only
if "%command%"=="status" goto status_only
if "%command%"=="clean" goto clean_all
if "%command%"=="help" goto show_help
if "%command%"=="-h" goto show_help
if "%command%"=="--help" goto show_help

echo ❌ Unknown command: %command%
echo Use '%0 help' for available commands
exit /b 1

:start_dev
call :check_docker
call :check_docker_compose
call :setup_env
call :start_services dev
call :show_status
goto :end

:start_prod
call :check_docker
call :check_docker_compose
call :setup_env
call :start_services prod
call :show_status
goto :end

:stop_services
echo 🛑 Stopping services...
docker-compose down
goto :end

:restart_services
echo 🔄 Restarting services...
docker-compose restart
call :show_status
goto :end

:logs_only
call :show_logs
goto :end

:status_only
call :show_status
goto :end

:clean_all
echo 🧹 Cleaning up Docker resources...
docker-compose down -v
docker system prune -f
goto :end

:show_help
echo Usage: %0 [command]
echo.
echo Commands:
echo   start, up    Start development services (default)
echo   prod         Start production services
echo   stop, down   Stop all services
echo   restart      Restart all services
echo   logs         Show recent logs
echo   status       Show service status
echo   clean        Stop services and clean Docker resources
echo   help         Show this help message
goto :end

:end
pause 