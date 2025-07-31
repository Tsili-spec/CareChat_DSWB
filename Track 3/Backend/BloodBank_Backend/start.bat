@echo off
REM Blood Bank Management System - Start Script (Windows)

echo 🩸 Starting Blood Bank Management System...

REM Check if virtual environment exists
if not exist "bloodbank_env" (
    echo Creating virtual environment...
    python -m venv bloodbank_env
)

REM Activate virtual environment
echo Activating virtual environment...
call bloodbank_env\Scripts\activate

REM Install/Update dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your configurations before running the server
    pause
    exit /b 1
)

REM Initialize database
echo Initializing database...
python scripts\init_db.py

REM Start the server
echo 🚀 Starting FastAPI server...
echo 📊 API Documentation: http://localhost:8000/docs
echo 🔍 Alternative Docs: http://localhost:8000/redoc
echo ❤️  Health Check: http://localhost:8000/health
echo 🔒 Protected Route: http://localhost:8000/protected
echo.
echo Default Admin Credentials:
echo Username: admin
echo Password: Admin123!
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
