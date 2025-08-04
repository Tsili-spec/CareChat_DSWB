#!/bin/bash

# Test script for the Transcription API endpoints
# This script demonstrates how to test all transcription endpoints

echo "🎵 CareChat Transcription API Test Script"
echo "========================================="

# Base URL
BASE_URL="http://localhost:8000/api"

# Check if server is running
echo "1. Checking if server is running..."
curl -s "$BASE_URL/../health/llm" > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Server is running"
else
    echo "❌ Server is not running. Please start with: uvicorn app.main:app --reload"
    echo "   Run from the Backend directory: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    exit 1
fi

# Test supported formats endpoint
echo ""
echo "2. Testing supported formats endpoint..."
curl -s -X GET "$BASE_URL/transcribe/supported-formats/" | python3 -m json.tool

# Check if test audio file exists
TEST_AUDIO_FILE="upload/test_audio.mp3"
if [ ! -f "$TEST_AUDIO_FILE" ]; then
    echo ""
    echo "ℹ️ No test audio file found at $TEST_AUDIO_FILE"
    echo "   To test with actual audio, place an audio file at $TEST_AUDIO_FILE"
    echo "   You can download a test file or record a short audio clip."
    echo ""
    echo "🎵 Basic API structure tests completed successfully!"
    exit 0
fi

# Test simple transcription
echo ""
echo "3. Testing simple transcription..."
curl -s -X POST "$BASE_URL/transcribe/simple/" \
    -F "audio=@$TEST_AUDIO_FILE" | python3 -m json.tool

# Test main transcription endpoint
echo ""
echo "4. Testing main transcription endpoint..."
curl -s -X POST "$BASE_URL/transcribe/" \
    -F "audio=@$TEST_AUDIO_FILE" | python3 -m json.tool

echo ""
echo "🎵 All transcription API tests completed!"
