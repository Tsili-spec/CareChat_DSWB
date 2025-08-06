#!/bin/bash

# Start the CareChat FastAPI application
echo "🚀 Starting CareChat API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Download spacy model if not exists
echo "🧠 Downloading spacy model..."
python -m spacy download en_core_web_md

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs upload

# Set environment variables if not set
export DATABASE_URL=${DATABASE_URL:-"mongodb://stercytambong:w23N0S5Qb6kMUwTi@217.65.144.32:27017/carechat"}
export JWT_SECRET_KEY=${JWT_SECRET_KEY:-"your-super-secret-jwt-key-change-in-production"}
export JWT_REFRESH_SECRET_KEY=${JWT_REFRESH_SECRET_KEY:-"your-super-secret-refresh-key-change-in-production"}

# Start the application
echo "🎯 Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
