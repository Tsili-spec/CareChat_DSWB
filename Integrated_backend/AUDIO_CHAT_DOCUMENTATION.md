# Audio Chat Endpoint Documentation

## Overview
The audio chat endpoint allows users to send voice messages that are automatically transcribed and processed through the same intelligent chat system as text messages.

## Endpoint
- **URL**: `/chat/audio`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`

## Features
- 🎤 **Audio Transcription**: Uses OpenAI Whisper for accurate speech-to-text
- 🧠 **RAG Integration**: Same medical knowledge retrieval as text chat
- 💬 **Conversation Memory**: Maintains context across messages
- 🌍 **Language Detection**: Automatically detects spoken language
- 📊 **Confidence Scoring**: Provides transcription confidence metrics

## Request Parameters

### Form Data
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `audio` | File | Yes | Audio file (WAV, MP3, M4A, FLAC, OGG) |
| `user_id` | string | Yes | Patient ID |
| `conversation_id` | string | No | Existing conversation ID (null for new) |
| `provider` | string | No | LLM provider ("groq" or "gemini") |

### Audio File Requirements
- **Maximum size**: 25MB
- **Supported formats**: WAV, MP3, M4A, FLAC, OGG
- **Recommended**: WAV or FLAC for best quality
- **Duration**: No specific limit, but shorter clips (< 5 minutes) work best

## Response Format

```json
{
    "conversation_id": "string",
    "transcribed_text": "What are the symptoms of diabetes?",
    "detected_language": "en",
    "transcription_confidence": 0.95,
    "user_message": {
        "message_id": "string",
        "role": "user", 
        "content": "What are the symptoms of diabetes?",
        "timestamp": "2025-08-07T10:30:00Z",
        "model_used": null
    },
    "assistant_message": {
        "message_id": "string",
        "role": "assistant",
        "content": "Diabetes symptoms include increased thirst, frequent urination...",
        "timestamp": "2025-08-07T10:30:05Z", 
        "model_used": "gemma2-9b-it"
    },
    "provider": "groq"
}
```

## How It Works

1. **Audio Upload**: Frontend sends audio file via multipart form
2. **Transcription**: Whisper converts speech to text
3. **Validation**: Checks transcription quality and content
4. **Chat Processing**: Text flows through same pipeline as text chat:
   - Conversation context retrieval
   - RAG enhancement for medical queries
   - LLM response generation
   - Memory storage
5. **Response**: Returns both transcription and chat data

## Integration Examples

### Frontend JavaScript (FormData)
```javascript
async function sendAudioMessage(audioBlob, userId, provider = 'groq') {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    formData.append('user_id', userId);
    formData.append('provider', provider);
    
    const response = await fetch('/chat/audio', {
        method: 'POST',
        body: formData
    });
    
    return await response.json();
}
```

### Python Client
```python
import requests

def send_audio_message(audio_file_path, user_id, provider='groq'):
    with open(audio_file_path, 'rb') as audio_file:
        files = {'audio': audio_file}
        data = {
            'user_id': user_id,
            'provider': provider
        }
        response = requests.post(
            'http://localhost:8000/chat/audio', 
            files=files, 
            data=data
        )
        return response.json()
```

### cURL
```bash
curl -X POST "http://localhost:8000/chat/audio" \
  -F "audio=@recording.wav" \
  -F "user_id=patient_123" \
  -F "provider=groq"
```

## Error Handling

### Common Errors
- **400**: Invalid audio file, file too large, or transcription failed
- **404**: Patient not found
- **500**: Internal server error

### Error Response Example
```json
{
    "detail": "Could not transcribe audio or audio is silent"
}
```

## Best Practices

1. **Audio Quality**: Use good microphone, minimize background noise
2. **File Size**: Keep under 25MB for faster processing
3. **Duration**: Shorter clips (30 seconds - 2 minutes) work best
4. **Language**: System auto-detects language but works best with English
5. **Error Handling**: Always check transcription confidence before processing

## Medical RAG Integration

The audio endpoint uses the same RAG (Retrieval-Augmented Generation) system as text chat:

- **Trigger Keywords**: Medical terms activate RAG retrieval
- **Clinical Data**: 50,000+ real clinical summaries
- **Context Enhancement**: Relevant cases added to AI prompt
- **Accurate Responses**: Evidence-based medical information

## Performance

- **Transcription**: 2-5 seconds for typical voice messages
- **Total Response**: 5-15 seconds end-to-end
- **Accuracy**: 95%+ for clear audio in supported languages
- **Concurrent Users**: Supports multiple simultaneous requests
