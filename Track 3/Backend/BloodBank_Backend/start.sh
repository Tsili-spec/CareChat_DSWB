#!/bin/bash

# Blood Bank Management System - Start Script

echo "🩸 Starting Blood Bank Management System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Use the configured Python environment
PYTHON_CMD="/home/asongna/Desktop/Carechat/Track 3/Backend/BloodBank_Backend/bloodbank_env/bin/python"

# Install/Update dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
"$PYTHON_CMD" -m pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${RED}⚠️  Please edit .env file with your configurations before running the server${NC}"
    exit 1
fi

# Initialize database
echo -e "${BLUE}Initializing database...${NC}"
"$PYTHON_CMD" scripts/init_db.py

# Set PYTHONPATH
export PYTHONPATH="/home/asongna/Desktop/Carechat/Track 3/Backend/BloodBank_Backend:$PYTHONPATH"

# Start the server
echo -e "${GREEN}🚀 Starting FastAPI server...${NC}"
echo -e "${GREEN}📊 API Documentation: http://localhost:8000/docs${NC}"
echo -e "${GREEN}🔍 Alternative Docs: http://localhost:8000/redoc${NC}"
echo -e "${GREEN}❤️  Health Check: http://localhost:8000/health${NC}"
echo -e "${GREEN}🔒 Protected Route: http://localhost:8000/protected${NC}"
echo ""
echo -e "${YELLOW}Default Admin Credentials:${NC}"
echo -e "${YELLOW}Username: admin${NC}"
echo -e "${YELLOW}Password: Admin123!${NC}"
echo ""

"$PYTHON_CMD" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
