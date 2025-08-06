# CareChat Track2 Backend - Chat System with Memory Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [File Structure and Components](#file-structure-and-components)
4. [Authentication System](#authentication-system)
5. [Chat System Implementation](#chat-system-implementation)
6. [Memory Management](#memory-management)
7. [RAG Integration](#rag-integration)
8. [API Endpoints](#api-endpoints)
9. [Database Schema](#database-schema)
10. [Setup and Configuration](#setup-and-configuration)
11. [Code Examples](#code-examples)

## Overview

CareChat Track2 Backend is a FastAPI-based healthcare chatbot system designed for Douala General Hospital in Cameroon. The system provides:

- **Multi-language support** (English/French)
- **Conversational memory** - maintains context across messages
- **Multi-LLM support** - Gemini and Groq providers
- **RAG (Retrieval-Augmented Generation)** - enhanced responses using clinical data
- **JWT-based authentication** - secure user sessions
- **PostgreSQL database** - persistent storage for users and conversations

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Frontend     │────│   FastAPI       │────│   PostgreSQL    │
│   (Flutter)     │    │   Backend       │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                    ┌─────────┼─────────┐
                    │         │         │
            ┌───────▼───┐ ┌───▼───┐ ┌───▼───┐
            │  Gemini   │ │ Groq  │ │  RAG  │
            │    API    │ │  API  │ │Service│
            └───────────┘ └───────┘ └───────┘
```

## File Structure and Components

### Backend Directory Structure

```
Backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # API route handlers
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── chatbot.py         # Chat endpoints with memory
│   │   ├── patient.py         # Patient profile management
│   │   ├── transcription.py   # Audio transcription
│   │   ├── feedback.py        # User feedback collection
│   │   ├── genemini.py        # Legacy Gemini endpoint
│   │   └── protected.py       # Protected route examples
│   ├── core/                  # Core configuration and utilities
│   │   ├── config.py          # Environment variables and settings
│   │   ├── auth.py            # Authentication middleware
│   │   └── jwt_auth.py        # JWT token management
│   ├── db/                    # Database configuration
│   │   └── database.py        # SQLAlchemy setup and session management
│   ├── models/                # SQLAlchemy ORM models
│   │   ├── user.py            # User/Patient model
│   │   ├── conversation.py    # Conversation and ChatMessage models
│   │   └── feedback.py        # Feedback model
│   ├── schemas/               # Pydantic schemas for API validation
│   │   ├── user.py            # User-related schemas
│   │   ├── conversation.py    # Chat and conversation schemas
│   │   ├── chat.py            # Chat message schemas
│   │   └── feedback.py        # Feedback schemas
│   └── services/              # Business logic services
│       ├── conversation_service.py  # Memory management service
│       ├── llm_service.py          # Multi-LLM provider service
│       ├── rag_service.py          # RAG implementation
│       ├── transcription.py       # Audio transcription service
│       ├── translation.py         # Language translation
│       └── transcription_translation.py
├── Data/                      # Clinical data for RAG
│   ├── clinical_summaries.csv
│   ├── clinical_summaries_test.csv
│   ├── embeddings.pkl
│   ├── embeddings_test.pkl
│   ├── faiss_index.bin
│   ├── faiss_index_test.bin
│   ├── processed_clinical_data.pkl
│   └── processed_clinical_data_test.pkl
├── requirements.txt           # Python dependencies
├── alembic.ini               # Database migration configuration
└── README.md                 # Backend documentation
```

## File-by-File Code Analysis

### 1. `app/main.py` - Application Entry Point

```python
from fastapi import FastAPI
from app.api import chatbot, feedback, patient, transcription
from app.core.jwt_auth import create_access_token, verify_token
from app.db.database import create_tables, check_database_connection
from app.services.llm_service import llm_service
from app.models import user, conversation

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Initialize database and RAG service on startup"""
    try:
        print("Initializing database...")
        create_tables()
        print("✅ Database tables created/verified successfully")
        
        print("Initializing RAG service...")
        await llm_service.initialize_rag()
        print("✅ RAG service initialized successfully")
        
    except Exception as e:
        print(f"❌ Initialization error: {e}")

@app.get("/")
async def root():
    return {"message": "Welcome to CareChat Track2 Backend!"}

@app.get("/health/llm")
async def llm_health():
    """Get health status of all LLM providers"""
    from app.services.llm_service import llm_service
    return llm_service.get_health_status()

# Include API routers
app.include_router(chatbot.router)
app.include_router(feedback.router)
app.include_router(patient.router, prefix="/api", tags=["Patient"])
app.include_router(transcription.router, prefix="/api", tags=["Transcription"])
```

**Function:** Main FastAPI application that:
- Initializes database tables on startup
- Initializes RAG service for enhanced responses
- Includes all API routers
- Provides health check endpoints

### 2. `app/api/auth.py` - Authentication System

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserSignup, UserLogin, UserResponse, LoginResponse, 
    TokenRefresh, TokenResponse, UserCreate, UserOut
)
from app.core.jwt_auth import create_access_token, create_refresh_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.auth import get_current_patient
from passlib.context import CryptContext
from datetime import timedelta
from typing import Optional
import logging

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)

@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    """Register new patient account using phone number as unique identifier"""
    # Implementation details in full file above

@router.post("/login", response_model=LoginResponse)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate patient using phone number and password"""
    # Implementation details in full file above

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """Generate new access token using refresh token"""
    # Implementation details in full file above

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_patient: User = Depends(get_current_patient)):
    """Get current authenticated patient profile"""
    # Implementation details in full file above
```

**Function:** Handles user authentication including:
- User registration with phone number and email validation
- Password hashing using bcrypt
- JWT token generation and refresh
- User profile retrieval
- Legacy endpoints for backward compatibility

### 3. `app/api/chatbot.py` - Chat System with Memory

```python
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.llm_service import llm_service
from app.services.conversation_service import conversation_memory
from app.schemas.conversation import ChatMessageCreate, ChatResponse, ConversationHistoryResponse, ConversationResponse
from app.db.database import get_db
import logging
from typing import List

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/", response_model=ChatResponse)
async def chat_with_memory(request: ChatMessageCreate, db: Session = Depends(get_db)):
    """Send a message to AI with conversational memory"""
    # 1. Get or create conversation
    # 2. Get conversation context (previous messages)
    # 3. Add user message to conversation
    # 4. Format context for LLM
    # 5. Generate response using specified LLM provider
    # 6. Add assistant message to conversation
    # 7. Return structured response

@router.get("/conversations/{user_id}", response_model=List[ConversationResponse])
async def get_user_conversations(user_id: str, db: Session = Depends(get_db)):
    """Get all conversations for a user"""

@router.get("/conversations/{user_id}/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(user_id: str, conversation_id: str, db: Session = Depends(get_db)):
    """Get full conversation history"""

@router.delete("/conversations/{user_id}/{conversation_id}")
async def delete_conversation(user_id: str, conversation_id: str, db: Session = Depends(get_db)):
    """Delete a specific conversation and all its messages"""

@router.delete("/messages/{user_id}/{message_id}")
async def delete_message(user_id: str, message_id: str, db: Session = Depends(get_db)):
    """Delete a specific message from a conversation"""
```

**Function:** Main chat interface that:
- Manages conversational memory across messages
- Supports multiple LLM providers (Gemini, Groq)
- Automatically generates conversation titles
- Provides conversation history management
- Implements secure message and conversation deletion

### 4. `app/services/conversation_service.py` - Memory Management

```python
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import UUID
import logging
from app.models.conversation import Conversation, ChatMessage
from app.models.user import User

class ConversationMemoryService:
    def __init__(self, max_context_messages: int = 5):
        self.max_context_messages = max_context_messages
    
    def get_or_create_conversation(self, db: Session, user_id: UUID, conversation_id: Optional[UUID] = None) -> Conversation:
        """Get existing conversation or create a new one"""
        
    def add_message(self, db: Session, conversation_id: UUID, role: str, content: str, model_used: Optional[str] = None) -> ChatMessage:
        """Add a message to the conversation"""
        
    def get_conversation_context(self, db: Session, conversation_id: UUID) -> List[ChatMessage]:
        """Get recent messages from a conversation for context"""
        
    def format_context_for_llm(self, messages: List[ChatMessage]) -> str:
        """Format conversation history for LLM context with healthcare system instructions"""
        # Implements smart truncation and summarization for longer conversations
        # Includes specialized healthcare instructions for Douala General Hospital
        
    def get_user_conversations(self, db: Session, user_id: UUID, limit: int = 20) -> List[Conversation]:
        """Get all conversations for a user"""
        
    def delete_conversation(self, db: Session, conversation_id: UUID, user_id: UUID) -> dict:
        """Delete a conversation and all its messages"""
        
    def auto_generate_title(self, first_message: str, max_length: int = 50) -> str:
        """Auto-generate conversation title from first message"""

# Global instance
conversation_memory = ConversationMemoryService()
```

**Function:** Core memory management service that:
- Maintains conversation context across messages
- Implements smart context truncation for long conversations
- Provides healthcare-specific system instructions
- Manages conversation lifecycle (create, update, delete)
- Auto-generates meaningful conversation titles

### 5. `app/services/llm_service.py` - Multi-LLM Provider Service

```python
import httpx
import json
from typing import Dict, Any, Optional, Literal
from fastapi import HTTPException
from app.core.config import GEMINI_API_KEY, GROQ_API_KEY

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None

LLMProvider = Literal["gemini", "groq"]

class MultiLLMService:
    def __init__(self):
        self.timeout = 30.0
        self.rag_service = None
        self.groq_client = None
        
        if GROQ_AVAILABLE and GROQ_API_KEY:
            self.groq_client = Groq(api_key=GROQ_API_KEY)
    
    async def initialize_rag(self):
        """Initialize RAG service for enhanced responses"""
        
    async def generate_response(
        self, 
        prompt: str, 
        provider: LLMProvider = "groq",
        use_rag: bool = True, 
        **kwargs
    ) -> str:
        """Generate response from specified LLM provider with optional RAG enhancement"""
        
    async def _groq_request(self, prompt: str, **kwargs) -> str:
        """Handle Groq API requests"""
        
    async def _gemini_request(self, prompt: str, **kwargs) -> str:
        """Handle Gemini API requests"""
        
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all LLM providers"""

# Global instance
llm_service = MultiLLMService()
```

**Function:** Manages multiple LLM providers:
- Supports both Gemini and Groq APIs
- Implements fallback mechanisms
- Integrates with RAG service for enhanced responses
- Provides health monitoring
- Handles rate limiting and error recovery

### 6. `app/services/rag_service.py` - RAG Implementation

```python
import pandas as pd
import numpy as np
import faiss
import logging
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
from pathlib import Path
import pickle
import os
from sklearn.metrics.pairwise import cosine_similarity

class HealthcareRAGService:
    def __init__(self, data_path: str = None, model_name: str = "all-MiniLM-L6-v2"):
        # Auto-detect project root and data directory
        # Set data paths for clinical summaries
        # Initialize medical keywords for RAG trigger
        
    async def initialize(self):
        """Initialize the RAG system - load model, data, and embeddings"""
        
    async def _load_clinical_data(self):
        """Load and preprocess clinical summaries dataset"""
        
    async def _load_or_create_embeddings(self):
        """Load existing embeddings or create new ones"""
        
    def should_use_rag(self, query: str) -> bool:
        """Determine if RAG should be used based on query content"""
        
    async def get_rag_enhanced_prompt(self, user_query: str, original_prompt: str, top_k: int = 3) -> str:
        """Get RAG-enhanced prompt with relevant clinical context"""
        
    def _search_similar_content(self, query_embedding: np.ndarray, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar content using FAISS index"""

# Global instance
rag_service = HealthcareRAGService()
```

**Function:** Implements Retrieval-Augmented Generation:
- Uses clinical summaries dataset for context
- Implements FAISS vector search for similarity matching
- Provides medical keyword-based RAG triggering
- Enhances responses with relevant clinical information
- Supports both test and production datasets

### 7. Database Models

#### `app/models/user.py` - User Model

```python
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.db.database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy import TIMESTAMP, func

class User(Base):
    __tablename__ = 'users'
    patient_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(200))
    phone_number = Column(String(20), unique=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    preferred_language = Column(String(10), default="en")
    created_at = Column(TIMESTAMP, server_default=func.now())
    password_hash = Column(String(255))
```

#### `app/models/conversation.py` - Conversation Models

```python
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import uuid

class Conversation(Base):
    __tablename__ = "conversations"
    
    conversation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.patient_id"), nullable=False)
    title = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.conversation_id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    model_used = Column(String(50), nullable=True)
    token_count = Column(Integer, nullable=True)
```

### 8. Configuration Files

#### `app/core/config.py` - Environment Configuration

```python
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY')

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "refreshsecret")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# LLM Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
```

#### `app/core/jwt_auth.py` - JWT Token Management

```python
import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional, Dict, Any

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""

def create_refresh_token(data: dict):
    """Create JWT refresh token"""

def verify_token(token: str, token_type: str = "access") -> Optional[Dict[Any, Any]]:
    """Verify and decode JWT token"""
```

#### `app/core/auth.py` - Authentication Middleware

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.models.user import User
from app.core.jwt_auth import verify_token

async def get_current_patient(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Required authentication - raises 401 if not authenticated"""

async def get_current_patient_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Optional authentication - returns None if not authenticated"""
```

## Authentication System

### User Registration Flow

1. **Input Validation**: Phone number and email uniqueness check
2. **Password Hashing**: Using bcrypt for secure password storage
3. **User Creation**: Store user in PostgreSQL with UUID patient_id
4. **Response**: Return user profile without password

### Login Flow

1. **Credential Verification**: Check phone number and password
2. **Token Generation**: Create access token (30 min) and refresh token (7 days)
3. **Response**: Return tokens and user profile

### Token Management

- **Access Tokens**: Short-lived (30 minutes) for API access
- **Refresh Tokens**: Long-lived (7 days) for token renewal
- **JWT Claims**: Include user ID, token type, and expiration

## Chat System Implementation

### Message Flow

1. **Authentication**: Verify user token
2. **Conversation Management**: Get or create conversation
3. **Context Retrieval**: Get recent messages for context
4. **Message Storage**: Add user message to database
5. **Context Formatting**: Format conversation history for LLM
6. **RAG Enhancement**: Optionally enhance with clinical data
7. **LLM Request**: Send to selected provider (Gemini/Groq)
8. **Response Storage**: Add assistant response to database
9. **Return Response**: Structured response with conversation data

### Key Features

- **Conversation Continuity**: Maintains context across sessions
- **Multi-LLM Support**: Choose between Gemini and Groq
- **Smart Context Management**: Automatic context truncation
- **RAG Integration**: Enhanced responses with clinical data
- **Healthcare Focus**: Specialized for Douala General Hospital

## Memory Management

### Context Strategy

The system implements intelligent memory management:

1. **Recent Message Limit**: Keeps last 5 messages in context
2. **Smart Truncation**: Summarizes older messages when context gets long
3. **Healthcare Instructions**: Includes specialized medical guidance
4. **Language Support**: Maintains context in English or French

### Context Formatting

```python
def format_context_for_llm(self, messages: List[ChatMessage]) -> str:
    # For longer conversations (>5 messages)
    if len(messages) > 5:
        system_instructions = """You are a multilingual healthcare professional assistant working for Douala General Hospital..."""
        # Summarize older messages, keep recent ones in full
        
    # For shorter conversations
    else:
        system_instructions = """Full detailed healthcare instructions..."""
        # Include all messages in context
```

## RAG Integration

### Clinical Data Enhancement

The RAG service enhances responses using clinical summaries:

1. **Medical Keyword Detection**: Identifies health-related queries
2. **Semantic Search**: Uses FAISS for similarity matching
3. **Context Enhancement**: Adds relevant clinical information
4. **Response Improvement**: Provides more accurate medical guidance

### RAG Workflow

```python
async def get_rag_enhanced_prompt(self, user_query: str, original_prompt: str, top_k: int = 3) -> str:
    # 1. Check if RAG should be used
    if not self.should_use_rag(user_query):
        return original_prompt
    
    # 2. Generate query embedding
    query_embedding = self.embedding_model.encode([user_query])
    
    # 3. Search similar clinical content
    similar_docs = self._search_similar_content(query_embedding[0], top_k)
    
    # 4. Format enhanced prompt with clinical context
    return enhanced_prompt
```

## API Endpoints

### Authentication Endpoints

- `POST /signup` - User registration
- `POST /login` - User authentication
- `POST /refresh` - Token refresh
- `GET /me` - Get user profile

### Chat Endpoints

- `POST /chat/` - Send message with memory
- `GET /chat/conversations/{user_id}` - Get user conversations
- `GET /chat/conversations/{user_id}/{conversation_id}` - Get conversation history
- `DELETE /chat/conversations/{user_id}/{conversation_id}` - Delete conversation
- `DELETE /chat/messages/{user_id}/{message_id}` - Delete message

### System Endpoints

- `GET /` - Health check
- `GET /health/llm` - LLM provider status

## Database Schema

### Tables

1. **users**: Patient information and authentication
2. **conversations**: Chat conversation metadata
3. **chat_messages**: Individual messages in conversations

### Relationships

- User (1) → Conversations (Many)
- Conversation (1) → Messages (Many)

### Key Features

- **UUID Primary Keys**: For security and scalability
- **Soft Deletes**: Conversation and message deletion tracking
- **Timestamps**: Automatic creation and update tracking
- **Indexing**: Optimized queries on frequently accessed fields

## Setup and Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/carechat

# JWT Security
JWT_SECRET_KEY=your-secret-key
JWT_REFRESH_SECRET_KEY=your-refresh-secret

# LLM APIs
GEMINI_API_KEY=your-gemini-key
GROQ_API_KEY=your-groq-key
```

### Dependencies

```bash
pip install -r requirements.txt
```

Key packages:
- `fastapi` - Web framework
- `sqlalchemy` - ORM
- `psycopg2-binary` - PostgreSQL adapter
- `passlib[bcrypt]` - Password hashing
- `python-jose[cryptography]` - JWT handling
- `sentence-transformers` - RAG embeddings
- `faiss-cpu` - Vector similarity search
- `groq` - Groq API client

### Database Setup

```python
# Create tables
from app.db.database import create_tables
create_tables()
```

### Running the Application

```bash
uvicorn app.main:app --reload
```

## Code Examples

### 1. Creating a User Account

```python
import requests

signup_data = {
    "full_name": "John Doe",
    "phone_number": "+237123456789",
    "email": "john@example.com",
    "preferred_language": "en",
    "password": "securepassword123"
}

response = requests.post("http://localhost:8000/signup", json=signup_data)
user_data = response.json()
print(f"Created user: {user_data['patient_id']}")
```

### 2. User Login

```python
login_data = {
    "phone_number": "+237123456789",
    "password": "securepassword123"
}

response = requests.post("http://localhost:8000/login", json=login_data)
auth_data = response.json()

access_token = auth_data['access_token']
headers = {"Authorization": f"Bearer {access_token}"}
```

### 3. Starting a Chat Conversation

```python
chat_data = {
    "user_id": "patient-uuid-here",
    "message": "I have been experiencing headaches for the past week",
    "conversation_id": None,  # null for new conversation
    "provider": "groq"
}

response = requests.post(
    "http://localhost:8000/chat/", 
    json=chat_data,
    headers=headers
)

chat_response = response.json()
conversation_id = chat_response['conversation_id']
assistant_message = chat_response['assistant_message']['content']
```

### 4. Continuing a Conversation

```python
followup_data = {
    "user_id": "patient-uuid-here",
    "message": "The headaches are worse in the morning",
    "conversation_id": conversation_id,  # Use existing conversation
    "provider": "groq"
}

response = requests.post(
    "http://localhost:8000/chat/", 
    json=followup_data,
    headers=headers
)
```

### 5. Getting Conversation History

```python
user_id = "patient-uuid-here"
response = requests.get(
    f"http://localhost:8000/chat/conversations/{user_id}",
    headers=headers
)

conversations = response.json()
for conv in conversations:
    print(f"Conversation: {conv['title']} ({conv['message_count']} messages)")
```

### 6. Retrieving Full Conversation

```python
response = requests.get(
    f"http://localhost:8000/chat/conversations/{user_id}/{conversation_id}",
    headers=headers
)

conversation = response.json()
for message in conversation['messages']:
    role = message['role']
    content = message['content']
    print(f"{role}: {content}")
```

## Security Features

### Authentication Security
- **Password Hashing**: Bcrypt with salting
- **JWT Tokens**: Signed with secret keys
- **Token Expiration**: Short-lived access tokens
- **Refresh Mechanism**: Secure token renewal

### API Security
- **Input Validation**: Pydantic schemas for all inputs
- **SQL Injection Protection**: SQLAlchemy ORM
- **Rate Limiting**: Configurable request limits
- **CORS Protection**: Configurable origins

### Data Security
- **UUID Identifiers**: Non-sequential, secure IDs
- **Conversation Isolation**: Users can only access their own data
- **Secure Deletion**: Proper cleanup of conversation data
- **Database SSL**: Encrypted database connections

## Error Handling

The system implements comprehensive error handling:

### HTTP Status Codes
- **200**: Success
- **400**: Bad Request (validation errors)
- **401**: Unauthorized (authentication required)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found (resource doesn't exist)
- **500**: Internal Server Error

### Error Response Format
```json
{
    "detail": "Error description",
    "status_code": 400,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

## Performance Optimization

### Database Optimization
- **Connection Pooling**: SQLAlchemy connection management
- **Query Optimization**: Indexed foreign keys
- **Pagination**: Limited result sets for large queries

### Memory Optimization
- **Context Limiting**: Maximum 5 messages in context
- **Smart Truncation**: Automatic summarization of long conversations
- **Caching**: RAG embeddings and FAISS index caching

### API Optimization
- **Async Operations**: Non-blocking request handling
- **Connection Reuse**: HTTP client connection pooling
- **Timeout Management**: Configurable request timeouts

## Monitoring and Logging

### Logging Configuration
```python
import logging

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### Key Metrics
- **Response Time**: API endpoint performance
- **Error Rate**: Failed request tracking
- **Token Usage**: LLM API consumption
- **Database Performance**: Query execution time

### Health Checks
- **Database Connectivity**: Connection status
- **LLM Provider Status**: API availability
- **RAG Service Health**: Embedding model status

This comprehensive documentation provides a complete guide to implementing and understanding the CareChat Track2 Backend chat system with memory, including all authentication, conversation management, and RAG integration features.
