#!/bin/bash

# Test script for the Enhanced Transcription + Chat API endpoint
# This script demonstrates how to test the transcription with chat functionality

echo "🎵 CareChat Enhanced Transcription + Chat API Test Script"
echo "========================================================="

# Base URL
BASE_URL="http://localhost:8000/api"

# Check if server is running
echo "1. Checking if server is running..."
curl -s "$BASE_URL/../health/llm" > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Server is running"
else
    echo "❌ Server is not running. Please start with: uvicorn app.main:app --reload"
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

# Test simple transcription (unchanged)
echo ""
echo "3. Testing simple transcription..."
curl -s -X POST "$BASE_URL/transcribe/simple/" \
    -F "audio=@$TEST_AUDIO_FILE" | python3 -m json.tool

# Test enhanced transcription with chat
echo ""
echo "4. Testing enhanced transcription + chat..."
echo "   Note: You'll need a valid user_id (UUID format)"
echo "   Example user_id: 123e4567-e89b-12d3-a456-426614174000"

# Example with dummy UUID (replace with real user ID)
USER_ID="123e4567-e89b-12d3-a456-426614174000"

curl -s -X POST "$BASE_URL/transcribe/" \
    -F "audio=@$TEST_AUDIO_FILE" \
    -F "user_id=$USER_ID" \
    -F "provider=groq" | python3 -m json.tool

echo ""
echo "🎵 All transcription + chat API tests completed!"
echo ""
echo "📝 Usage Notes:"
echo "   - The main /transcribe/ endpoint now includes chat functionality"
echo "   - Requires user_id (UUID format) for conversation tracking"
echo "   - Optional conversation_id to continue existing conversations"
echo "   - Optional provider (gemini or groq) for LLM selection"
echo "   - Returns both transcription results and AI chat response"
