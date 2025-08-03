#!/bin/bash

# Blood Bank Management System - English Locale Startup Script

echo "🩸 Starting Blood Bank Management System with English Locale..."

# Set environment variables for English locale
export FASTAPI_AMIS_ADMIN_LANGUAGE=en_US
export FASTAPI_AMIS_ADMIN_LOCALE=en_US
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Navigate to project directory
cd /home/asongna/Desktop/Carechat/Track3/Backend

echo "📋 Environment Variables Set:"
echo "   FASTAPI_AMIS_ADMIN_LANGUAGE: $FASTAPI_AMIS_ADMIN_LANGUAGE"
echo "   FASTAPI_AMIS_ADMIN_LOCALE: $FASTAPI_AMIS_ADMIN_LOCALE"
echo "   LANG: $LANG"
echo "   LC_ALL: $LC_ALL"

echo ""
echo "🚀 Starting server on http://localhost:8001"
echo "📊 Admin interface: http://localhost:8001/admin/"
echo "📖 API docs: http://localhost:8001/docs"
echo ""
echo "⚠️  If you see Chinese text in the admin interface:"
echo "   1. Clear your browser cache (Ctrl+Shift+Delete)"
echo "   2. Or use Incognito/Private browsing mode"
echo "   3. Force refresh with Ctrl+F5"
echo ""

# Start the server
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
