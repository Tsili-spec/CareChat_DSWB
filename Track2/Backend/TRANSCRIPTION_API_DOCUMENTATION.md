# Enhanced Audio Transcription + Chat API Documentation

## Overview

The CareChat Track2 Backend includes a comprehensive audio transcription system that converts spoken audio into text using OpenAI's Whisper model, and then processes the transcribed text through the AI chat system to provide intelligent healthcare responses. This creates a complete voice-to-AI conversation experience.

## API Endpoints

### Base URL
All transcription endpoints are available under the `/api` prefix:
- Base: `http://localhost:8000/api`

### 1. Enhanced Transcription + Chat Endpoint

**`POST /api/transcribe/`**

Full-featured transcription endpoint that transcribes audio and processes it through the chat system.

#### Parameters
- `audio` (required): Audio file upload (multipart/form-data)
- `user_id` (required): User's patient ID (UUID format)
- `conversation_id` (optional): Existing conversation ID to continue a conversation
- `provider` (optional): LLM provider ("gemini" or "groq", default: "groq")

#### Supported Audio Formats
- MP3, WAV, M4A, FLAC, OGG, WebM
- Maximum file size: 25MB

#### Example Request (cURL)
```bash
# New conversation
curl -X POST "http://localhost:8000/api/transcribe/" \
  -H "Content-Type: multipart/form-data" \
  -F "audio=@path/to/audio.mp3" \
  -F "user_id=123e4567-e89b-12d3-a456-426614174000" \
  -F "provider=groq"

# Continue existing conversation
curl -X POST "http://localhost:8000/api/transcribe/" \
  -H "Content-Type: multipart/form-data" \
  -F "audio=@path/to/audio.mp3" \
  -F "user_id=123e4567-e89b-12d3-a456-426614174000" \
  -F "conversation_id=456e7890-e12b-34d5-a678-901234567890" \
  -F "provider=gemini"
```

#### Example Response
```json
{
  "status": "success",
  "filename": "audio.mp3",
  "file_size_bytes": 1048576,
  "transcription": {
    "text": "What are the symptoms of diabetes?",
    "detected_language": "en",
    "confidence": 0.94,
    "segments": [...]
  },
  "chat_response": {
    "conversation_id": "789e0123-e45f-67g8-a901-234567890123",
    "user_message": {
      "message_id": "abc12345-6789-def0-1234-567890abcdef",
      "role": "user",
      "content": "What are the symptoms of diabetes?",
      "timestamp": "2025-08-04T10:30:00.000Z",
      "model_used": null
    },
    "assistant_message": {
      "message_id": "def67890-1234-5678-90ab-cdef01234567",
      "role": "assistant",
      "content": "Diabetes symptoms include frequent urination, excessive thirst, unexplained weight loss, fatigue, blurred vision, and slow-healing wounds. Type 1 diabetes symptoms often develop quickly, while Type 2 symptoms may develop gradually. If you're experiencing these symptoms, it's important to consult with a healthcare provider for proper testing and diagnosis.",
      "timestamp": "2025-08-04T10:30:05.000Z",
      "model_used": "llama-4-maverick-17b"
    },
    "provider": "groq"
  }
}
```

### 2. Simple Transcription Endpoint

**`POST /api/transcribe/simple/`**

Simplified endpoint that returns only essential transcription data.

#### Parameters
- `audio` (required): Audio file upload

#### Example Request
```bash
curl -X POST "http://localhost:8000/api/transcribe/simple/" \
  -H "Content-Type: multipart/form-data" \
  -F "audio=@path/to/audio.mp3"
```

#### Example Response
```json
{
  "transcribed_text": "Hello, how are you today?",
  "detected_language": "en",
  "confidence": 0.92
}
```

### 3. Supported Formats Information

**`GET /api/transcribe/supported-formats/`**

Get information about supported audio formats and system capabilities.

#### Example Response
```json
{
  "supported_formats": [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".webm"],
  "max_file_size_mb": 25,
  "supported_languages": "99+ languages (auto-detected by Whisper)",
  "transcription_model": "OpenAI Whisper (base)"
}
```

## Technical Implementation

### Architecture Components

1. **Whisper Engine** (`app/services/transcription.py`)
   - Core transcription using OpenAI Whisper model
   - Audio preprocessing and format conversion
   - Confidence score calculation

2. **Pipeline Service** (`app/services/transcription_translation.py`)
   - Simple transcription workflows
   - Language detection
   - Response formatting

### Audio Processing Pipeline

### Enhanced Audio Processing Pipeline

1. **Upload**: Audio file received via multipart upload
2. **Validation**: File format and size validation
3. **Conversion**: Audio converted to 16kHz mono format
4. **Transcription**: Processed through Whisper model
5. **Chat Processing**: Transcribed text sent to AI chat system
6. **AI Response**: Healthcare-focused response generated
7. **Conversation Storage**: Messages saved with conversation context
8. **Response**: Combined transcription and chat results returned

## Workflow Examples

### Voice-to-AI Healthcare Consultation

1. **Patient speaks**: "I've been having headaches for the past week, what could be causing them?"
2. **Audio transcription**: Text extracted with 94% confidence
3. **AI processing**: Question processed through healthcare-trained LLM
4. **Response**: Detailed explanation of possible headache causes and recommendations
5. **Conversation storage**: Exchange saved for future reference and continuity

### Continuing a Conversation

1. **Follow-up question**: "What can I do to prevent these headaches?"
2. **Context awareness**: AI remembers previous headache discussion
3. **Personalized response**: Tailored prevention advice based on conversation history

## Integration with Healthcare Workflow

The enhanced transcription API integrates seamlessly into healthcare applications:

1. **Voice Consultations**: Patients can ask questions by speaking
2. **Multilingual Support**: Automatic language detection and transcription
3. **AI-Powered Responses**: Healthcare-focused answers and recommendations
4. **Conversation Memory**: Context maintained across multiple interactions
5. **Provider Dashboard**: Healthcare providers can review patient conversations

- **Model**: Whisper "tiny" for fast processing
- **Speed**: ~32x real-time processing
- **Memory**: Low memory footprint (~39MB model)
- **Languages**: 99+ languages auto-detected
- **Accuracy**: Optimized for clear speech and medical terminology

## Installation and Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Key dependencies for transcription:
- `openai-whisper`
- `torch`
- `pydub`

### 2. System Requirements

- **FFmpeg**: Required for audio format conversion
- **Python 3.8+**: Core runtime
- **CUDA** (optional): GPU acceleration for faster processing

### 3. Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Usage Examples

### Python Client Example

```python
import requests
import json

# Simple transcription
def transcribe_audio(audio_file_path):
    url = "http://localhost:8000/api/transcribe/simple/"
    
    with open(audio_file_path, 'rb') as audio_file:
        files = {'audio': audio_file}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Transcribed text: {result['transcribed_text']}")
        print(f"Language: {result['detected_language']}")
        print(f"Confidence: {result['confidence']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# Full transcription with detailed response
def transcribe_detailed(audio_file_path):
    url = "http://localhost:8000/api/transcribe/"
    
    with open(audio_file_path, 'rb') as audio_file:
        files = {'audio': audio_file}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Status: {result['status']}")
        print(f"Filename: {result['filename']}")
        print(f"File size: {result['file_size_bytes']} bytes")
        print(f"Text: {result['transcription']['text']}")
        print(f"Language: {result['transcription']['detected_language']}")
        print(f"Confidence: {result['transcription']['confidence']}")

# Usage
transcribe_audio("path/to/audio.mp3")
transcribe_detailed("path/to/audio.mp3")
```

### JavaScript Client Example

```javascript
async function transcribeAudio(audioFile) {
    const formData = new FormData();
    formData.append('audio', audioFile);
    
    try {
        const response = await fetch('http://localhost:8000/api/transcribe/simple/', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Transcription:', result.transcribed_text);
            console.log('Language:', result.detected_language);
            console.log('Confidence:', result.confidence);
        } else {
            console.error('Transcription failed:', response.statusText);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Usage with file input
document.getElementById('audioInput').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        transcribeAudio(file);
    }
});
```

## Error Handling

### Common Error Responses

```json
{
  "detail": "No audio file provided"
}
```

```json
{
  "detail": "Unsupported audio format. Allowed formats: .mp3, .wav, .m4a, .flac, .ogg, .webm"
}
```

```json
{
  "detail": "Audio file too large. Maximum size is 25MB"
}
```

```json
{
  "detail": "Transcription failed: [error details]"
}
```

### Error Codes
- `400`: Bad Request (invalid file, format, or size)
- `500`: Internal Server Error (transcription processing failed)

## Testing

### Run Tests

```bash
# Test transcription imports and basic functionality
python test_transcription.py

# Test with sample audio (if available)
curl -X POST "http://localhost:8000/api/transcribe/simple/" \
  -F "audio=@upload/sample_audio.mp3"
```

### Test Files

Place test audio files in the `upload/` directory:
- `upload/test_audio.mp3`
- `upload/test_audio.wav`

## Integration with Healthcare Workflow

The transcription API can be integrated into healthcare applications for:

1. **Patient Feedback Processing**
   - Convert voice feedback to text
   - Automatic language detection and translation
   - Sentiment analysis of transcribed content

2. **Medical Consultations**
   - Transcribe patient-doctor conversations
   - Multi-language support for diverse patient populations
   - Real-time transcription capabilities

3. **Voice Notes and Documentation**
   - Convert audio notes to text
   - Integration with electronic health records
   - Searchable audio content

## Security and Privacy

- **Local Processing**: All transcription happens locally (no external API calls for Whisper)
- **Translation Privacy**: Google Translate used for translation (consider privacy implications)
- **File Storage**: Temporary file storage in `upload/` directory
- **Data Retention**: Audio files can be deleted after processing

## Deployment Considerations

### Production Setup
- **GPU Support**: Enable CUDA for faster processing
- **File Storage**: Consider cloud storage for audio files
- **Load Balancing**: Multiple worker processes for concurrent requests
- **Monitoring**: Track transcription success rates and processing times

### Scalability
- **Async Processing**: Implement background task queues for large files
- **Model Optimization**: Consider larger Whisper models for better accuracy
- **Caching**: Cache transcription results for repeated audio content

## Conclusion

The CareChat Track2 transcription API provides a robust, multilingual solution for converting audio feedback into actionable text data. The system balances performance, accuracy, and ease of use, making it suitable for healthcare applications requiring reliable speech-to-text capabilities.
