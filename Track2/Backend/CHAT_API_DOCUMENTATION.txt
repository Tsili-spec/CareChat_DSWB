# CareChat Backend - Chat API Documentation

## Overview
The CareChat backend implements a sophisticated conversational memory system that allows users to have persistent, context-aware conversations with Google's Gemini AI. The system maintains conversation history, provides context continuity across sessions, and supports multiple simultaneous conversations per user.

## Architecture Overview

### Core Components
1. **FastAPI Router** (`/app/api/chatbot.py`) - HTTP endpoints for chat functionality
2. **Conversation Service** (`/app/services/conversation_service.py`) - Memory management and context handling
3. **Gemini LLM Service** (`/app/services/llm_service.py`) - AI integration with Google Gemini
4. **Database Models** (`/app/models/`) - Data persistence layer
5. **Pydantic Schemas** (`/app/schemas/conversation.py`) - Request/response validation

## Database Schema

### Tables Created
```sql
-- Users table (existing)
users:
  - patient_id: UUID (Primary Key)
  - full_name: VARCHAR(200)
  - phone_number: VARCHAR(20) (Unique)
  - email: VARCHAR(255) (Unique, Nullable)
  - preferred_language: VARCHAR(10) (Default: 'en')
  - created_at: TIMESTAMP
  - password_hash: VARCHAR(255)

-- Conversations table (new)
conversations:
  - conversation_id: UUID (Primary Key)
  - patient_id: UUID (Foreign Key → users.patient_id)
  - title: VARCHAR(200) (Nullable, auto-generated from first message)
  - created_at: TIMESTAMP (Auto-generated)
  - updated_at: TIMESTAMP (Auto-updated on message addition)

-- Chat Messages table (new)
chat_messages:
  - message_id: UUID (Primary Key)
  - conversation_id: UUID (Foreign Key → conversations.conversation_id)
  - role: VARCHAR(20) ('user' or 'assistant')
  - content: TEXT (Message content)
  - timestamp: TIMESTAMP (Auto-generated)
  - model_used: VARCHAR(50) (e.g., 'gemini-2.0-flash')
  - token_count: INTEGER (Nullable, for future analytics)
```

## API Endpoints

### 1. Main Chat Endpoint
**POST** `/chat/`

**Purpose**: Send a message with conversational memory

**Request Body**:
```json
{
  "user_id": "fe9abe32-2e45-4b30-93eb-03cdaff39d65",
  "message": "Hello! I have a question about high blood pressure.",
  "conversation_id": null  // Optional: null for new conversation, UUID for existing
}
```

**Response**:
```json
{
  "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_message": {
    "message_id": "msg-uuid-1",
    "role": "user",
    "content": "Hello! I have a question about high blood pressure.",
    "timestamp": "2025-07-22T10:30:00Z",
    "model_used": null
  },
  "assistant_message": {
    "message_id": "msg-uuid-2",
    "role": "assistant",
    "content": "High blood pressure (hypertension) is when the force of blood against your artery walls is consistently too high. What specific questions do you have about it?",
    "timestamp": "2025-07-22T10:30:05Z",
    "model_used": "gemini-2.0-flash"
  },
  "provider": "gemini"
}
```

### 2. User Conversations List
**GET** `/chat/conversations/{user_id}`

**Purpose**: Get all conversations for a specific user

**Response**:
```json
[
  {
    "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "title": "Hello! I have a question about high blood press...",
    "created_at": "2025-07-22T10:30:00Z",
    "updated_at": "2025-07-22T10:45:00Z",
    "message_count": 6
  }
]
```

### 3. Conversation History
**GET** `/chat/conversations/{user_id}/{conversation_id}`

**Purpose**: Get full conversation history with all messages

**Response**:
```json
{
  "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Hello! I have a question about high blood press...",
  "messages": [
    {
      "message_id": "msg-uuid-1",
      "role": "user",
      "content": "Hello! I have a question about high blood pressure.",
      "timestamp": "2025-07-22T10:30:00Z",
      "model_used": null
    },
    {
      "message_id": "msg-uuid-2",
      "role": "assistant", 
      "content": "High blood pressure is...",
      "timestamp": "2025-07-22T10:30:05Z",
      "model_used": "gemini-2.0-flash"
    }
  ],
  "created_at": "2025-07-22T10:30:00Z",
  "updated_at": "2025-07-22T10:45:00Z"
}
```

## Conversational Memory Flow

### 1. Request Processing Flow
```
1. User sends message → FastAPI chatbot.py
2. chatbot.py calls conversation_service.get_or_create_conversation()
3. conversation_service queries database for existing conversation
4. If conversation exists: retrieve it | If not: create new conversation
5. conversation_service.get_conversation_context() retrieves last 10 messages
6. conversation_service.format_context_for_llm() formats previous messages
7. Full prompt = context + new message
8. gemini_service.generate_response() sends to Gemini API
9. conversation_service.add_message() stores user message and AI response
10. Response returned to user
```

### 2. Context Management
The system maintains context through the `ConversationMemoryService` class:

**Key Methods**:
- `get_or_create_conversation()`: Manages conversation lifecycle
- `get_conversation_context()`: Retrieves last N messages (default: 10)
- `format_context_for_llm()`: Formats messages for AI consumption
- `add_message()`: Stores messages with metadata
- `auto_generate_title()`: Creates conversation titles from first message

**Context Formatting Example**:
```
Previous conversation context:
Human: Hello! I have a question about high blood pressure.
Assistant: High blood pressure (hypertension) is when the force of blood against your artery walls is consistently too high. What specific questions do you have about it?
Human: What are the symptoms?
Assistant: Common symptoms include headaches, shortness of breath, nosebleeds, and chest pain. However, many people have no symptoms at all.

Current message:
Human: How can I prevent it?
```

### 3. Memory Persistence
- **Session Independence**: Conversations persist across API restarts and user sessions
- **User Isolation**: Each user's conversations are completely separate
- **Conversation Continuity**: Users can continue existing conversations or start new ones
- **Context Window**: Configurable number of previous messages included (default: 10)

## Gemini Integration

### Service Configuration
- **Model**: `gemini-2.0-flash` (Google's latest fast model)
- **API Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent`
- **Authentication**: X-goog-api-key header
- **Timeout**: 30 seconds
- **Error Handling**: Comprehensive error messages and status codes

### Request Format to Gemini
```json
{
  "contents": [
    {
      "parts": [
        {
          "text": "Previous conversation context:\nHuman: Hello...\n\nCurrent message:\nHuman: How can I prevent it?"
        }
      ]
    }
  ]
}
```

### Health Check
The system includes a health check endpoint that verifies:
- Gemini API key configuration
- Service availability
- Model access

## File Structure

```
Backend/
├── app/
│   ├── api/
│   │   └── chatbot.py              # Main chat endpoints
│   ├── models/
│   │   ├── user.py                 # User database model
│   │   └── conversation.py         # Conversation & ChatMessage models
│   ├── schemas/
│   │   └── conversation.py         # Pydantic request/response schemas
│   ├── services/
│   │   ├── llm_service.py          # Gemini AI integration
│   │   └── conversation_service.py # Memory management service
│   ├── core/
│   │   └── config.py               # Configuration (API keys, etc.)
│   ├── db/
│   │   └── database.py             # Database connection & setup
│   └── main.py                     # FastAPI application setup
```

## Key Features Implemented

### ✅ Conversational Memory
- Persistent conversation storage across sessions
- Context-aware responses using conversation history
- Multiple conversations per user
- Automatic conversation title generation

### ✅ Database Integration
- PostgreSQL/SQLite support with automatic fallback
- Proper foreign key relationships
- UUID-based primary keys for security
- Timestamp tracking for analytics

### ✅ Error Handling
- Comprehensive error messages
- HTTP status code compliance
- Graceful degradation for API failures
- Request validation using Pydantic

### ✅ Scalability Features
- Configurable context window size
- Async/await for non-blocking operations
- Database connection pooling
- Modular service architecture

## Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db  # or sqlite:///./carechat.db

# JWT (for authentication)
JWT_SECRET_KEY=your-secret-key
JWT_REFRESH_SECRET_KEY=your-refresh-secret

# Gemini AI
GEMINI_API_KEY=AIzaSyCkokXWCOn23c2Upr1LFQVaOvVOE5ZuW-o
```

### Conversation Service Settings
```python
# In conversation_service.py
max_context_messages = 10  # Number of previous messages to include
```

## Usage Examples

### Starting a New Conversation
```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "fe9abe32-2e45-4b30-93eb-03cdaff39d65",
    "message": "Hello! I have a question about diabetes."
  }'
```

### Continuing an Existing Conversation
```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "fe9abe32-2e45-4b30-93eb-03cdaff39d65",
    "message": "What are the early warning signs?",
    "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }'
```

### Getting User's Conversations
```bash
curl "http://localhost:8000/chat/conversations/fe9abe32-2e45-4b30-93eb-03cdaff39d65"
```

## Technical Decisions

### Why Custom Memory Instead of LangChain?
1. **Full Control**: Exact control over context formatting and database schema
2. **Performance**: Direct database queries without abstraction overhead
3. **Integration**: Perfect integration with existing user authentication system
4. **Simplicity**: Easier to debug, modify, and extend
5. **Database Schema**: Custom schema optimized for healthcare chat use case

### Database Design Choices
1. **UUID Primary Keys**: Enhanced security and distributed system compatibility
2. **Separate Messages Table**: Allows for complex querying and analytics
3. **Soft Relationships**: Removed SQLAlchemy relationships to avoid circular imports
4. **Timestamp Precision**: Full timezone support for global deployment

### API Design Philosophy
1. **RESTful**: Clear, predictable endpoint structure
2. **Stateless**: Each request contains all necessary information
3. **Consistent**: Uniform response formats across all endpoints
4. **Extensible**: Easy to add new features without breaking changes

## Next Steps (Ready for Implementation)

### Step 3: RAG (Retrieval-Augmented Generation)
- Vector database integration for clinical documents
- Semantic search for relevant health information
- Source citation in responses
- Document embedding and retrieval pipeline

### Step 4: Enhanced Personalization
- User profile-based response adaptation
- Medical history integration
- Language and literacy level adjustments

### Step 5: Analytics and Monitoring
- Conversation analytics dashboard
- Response quality metrics
- User engagement tracking
- Performance monitoring

## Testing

### Manual Testing Commands
```bash
# Test conversation creation
python3 -c "
from app.db.database import SessionLocal
from app.models.conversation import Conversation, ChatMessage
db = SessionLocal()
count = db.query(Conversation).count()
print(f'Total conversations: {count}')
db.close()
"

# Test service health
curl http://localhost:8000/chat/health

# Test simple chat (legacy endpoint)
curl -X POST "http://localhost:8000/chat/simple?prompt=Hello"
```

## Security Considerations

### Implemented
- UUID-based IDs prevent enumeration attacks
- Input validation via Pydantic schemas
- SQL injection protection via SQLAlchemy ORM
- API key protection (not exposed in responses)

### Future Enhancements
- Rate limiting per user
- Message content filtering
- Audit logging for compliance
- Encryption at rest for sensitive conversations

---

**Generated**: July 22, 2025  
**Version**: 1.0 - Conversational Memory Implementation  
**Status**: Production Ready  
**Last Updated**: After Step 2 completion - Ready for RAG implementation
