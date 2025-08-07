# CareChat Project Architecture & Implementation Documentation

## Table of Contents
1. [Project Architecture](#project-architecture)
2. [Implementation Methods](#implementation-methods)
3. [Tools and Technologies](#tools-and-technologies)
4. [Data Flow](#data-flow)
5. [Security Architecture](#security-architecture)
6. [Deployment Architecture](#deployment-architecture)

---

## 1. Project Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CareChat System                         │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (Web/Mobile)                                          │
│  ├── React/Flutter Application                                  │
│  ├── Audio Recording Interface                                  │
│  └── Real-time Chat Interface                                   │
├─────────────────────────────────────────────────────────────────┤
│  API Gateway Layer (FastAPI)                                    │
│  ├── Authentication Middleware                                  │
│  ├── CORS & Security Headers                                    │
│  ├── Rate Limiting                                              │
│  └── Request/Response Validation                                │
├─────────────────────────────────────────────────────────────────┤
│  Business Logic Layer                                           │
│  ├── Chat Service (Text + Audio)                               │
│  ├── RAG Service (Medical Knowledge)                           │
│  ├── Patient Management                                         │
│  ├── Reminder System                                            │
│  ├── Feedback Analysis                                          │
│  └── SMS Notification Service                                   │
├─────────────────────────────────────────────────────────────────┤
│  Data Processing Layer                                          │
│  ├── Audio Transcription (Whisper)                             │
│  ├── Text Translation                                           │
│  ├── Sentiment Analysis                                         │
│  ├── Medical Context Retrieval (FAISS)                         │
│  └── LLM Integration (Groq/Gemini)                             │
├─────────────────────────────────────────────────────────────────┤
│  Data Storage Layer                                             │
│  ├── MongoDB (Primary Database)                                │
│  ├── FAISS Vector Database                                      │
│  ├── File Storage (Audio/Documents)                            │
│  └── Cache Layer (Embeddings)                                   │
├─────────────────────────────────────────────────────────────────┤
│  External Services                                              │
│  ├── Twilio (SMS)                                               │
│  ├── Groq API (LLM)                                             │
│  ├── Google Gemini API (LLM)                                    │
│  └── HuggingFace (Embeddings)                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Microservices Architecture

The project follows a modular monolithic architecture with clear service boundaries:

#### Core Services
- **Authentication Service**: JWT-based authentication and user management
- **Chat Service**: Conversational AI with memory and context
- **RAG Service**: Medical knowledge retrieval and enhancement
- **Transcription Service**: Audio-to-text conversion
- **Translation Service**: Multi-language support
- **Reminder Service**: Medication and appointment reminders
- **Feedback Service**: Patient feedback collection and analysis
- **SMS Service**: Notification delivery via Twilio

#### Support Services
- **Logging Service**: Centralized logging and monitoring
- **Configuration Service**: Environment and settings management
- **Database Service**: MongoDB connection and ODM
- **Scheduler Service**: Background task management

### 1.3 Database Architecture

#### MongoDB Collections
```
carechat_db/
├── patients/           # Patient profiles and authentication
├── conversations/      # Chat conversations with AI
├── chat_messages/      # Individual messages in conversations
├── feedback/          # Patient feedback and analysis
├── reminders/         # Medication and appointment reminders
├── reminder_delivery/ # SMS delivery tracking
└── system_logs/       # Application logs and audit trail
```

#### Data Relationships
```
Patient (1) ──→ (N) Conversations
Conversation (1) ──→ (N) ChatMessages
Patient (1) ──→ (N) Feedback
Patient (1) ──→ (N) Reminders
Reminder (1) ──→ (N) ReminderDelivery
```

---

## 2. Implementation Methods

### 2.1 API Design Pattern

**RESTful API with FastAPI**
- Follows REST principles for resource-based URLs
- Uses HTTP methods appropriately (GET, POST, PUT, DELETE)
- Implements proper status codes and error responses
- Supports both JSON and multipart/form-data content types

**Endpoint Structure:**
```
/api/auth/*           # Authentication endpoints
/api/chat/*           # Chat and conversation management
/api/feedback/*       # Feedback collection and analysis
/api/reminder/*       # Reminder management
/api/patient/*        # Patient profile management
/api/dashboard/*      # Analytics and reporting
```

### 2.2 Authentication & Authorization

**JWT-Based Authentication**
```python
# Dual token system
access_token: 30 minutes expiry
refresh_token: 7 days expiry

# Token payload structure
{
    "sub": "patient_id",
    "exp": timestamp,
    "iat": timestamp,
    "type": "access" | "refresh"
}
```

**Security Implementation:**
- Password hashing with bcrypt
- Token-based stateless authentication
- Secure HTTP headers (CORS, CSP, etc.)
- Input validation and sanitization

### 2.3 RAG (Retrieval-Augmented Generation) Implementation

**Medical Knowledge System:**
```python
# Data Pipeline
Clinical CSV → Preprocessing → Embeddings → FAISS Index → Retrieval

# Components
1. Data Ingestion: 50,000+ clinical summaries
2. Text Processing: Cleaning and normalization
3. Embedding Generation: SentenceTransformers
4. Vector Storage: FAISS index for similarity search
5. Context Retrieval: Top-k relevant documents
6. Prompt Enhancement: Contextual information injection
```

**RAG Workflow:**
1. User query analysis for medical keywords
2. Query embedding generation
3. Similarity search in FAISS index
4. Relevant clinical context retrieval
5. Prompt enhancement with medical context
6. LLM response generation with context

### 2.4 Audio Processing Pipeline

**Speech-to-Text Workflow:**
```python
Audio Upload → Validation → Whisper Transcription → Language Detection → Text Processing → Chat Pipeline

# Implementation Details
- Supported formats: WAV, MP3, M4A, FLAC, OGG
- Maximum file size: 25MB
- Automatic language detection
- Confidence scoring
- Error handling and fallback
```

### 2.5 Conversation Memory System

**Context Management:**
```python
# Conversation Structure
Conversation {
    id: ObjectId,
    user_id: String,
    title: String,
    created_at: DateTime,
    updated_at: DateTime
}

ChatMessage {
    id: ObjectId,
    conversation_id: ObjectId,
    role: "user" | "assistant",
    content: String,
    timestamp: DateTime,
    model_used: String
}
```

**Memory Implementation:**
- Persistent conversation storage
- Context window management
- Automatic title generation
- Message threading and ordering

### 2.6 Multilingual Support

**Translation Pipeline:**
```python
# Language Detection → Translation → Processing → Response Translation

# Supported Languages
- English (primary)
- French (Cameroon official language)
- Local languages (via deep-translator)
```

### 2.7 Feedback Analysis System

**NLP Analysis Pipeline:**
```python
Feedback Text → Preprocessing → Feature Extraction → Analysis

# Analysis Components
1. Sentiment Analysis (TextBlob)
2. Topic Extraction (spaCy + keyword matching)
3. Urgency Detection (keyword-based scoring)
4. Language Detection
5. Translation (if needed)
```

### 2.8 Reminder Scheduling System

**Scheduler Architecture:**
```python
# Background Scheduler
APScheduler → Database Query → SMS Delivery → Status Tracking

# Reminder Types
- One-time reminders
- Recurring reminders (daily, weekly, monthly)
- Custom scheduling patterns
```

---

## 3. Tools and Technologies

### 3.1 Core Framework

**FastAPI Framework**
```python
# Why FastAPI?
- High performance (async/await support)
- Automatic API documentation (Swagger/OpenAPI)
- Built-in data validation (Pydantic)
- Modern Python type hints
- Easy testing and development
```

**Uvicorn ASGI Server**
- Production-ready async server
- Hot reload for development
- Multiple worker support
- HTTP/2 and WebSocket support

### 3.2 Database Technologies

**MongoDB with Beanie ODM**
```python
# Database Features
- NoSQL document database
- Flexible schema design
- Horizontal scaling capability
- Rich query capabilities
- Aggregation pipeline

# Beanie ODM Benefits
- Async/await support
- Pydantic integration
- Type safety
- Migration support
```

**FAISS Vector Database**
```python
# Vector Search Engine
- Facebook AI Similarity Search
- High-performance similarity search
- Multiple index types (Flat, IVF, HNSW)
- GPU acceleration support
- Scalable to billions of vectors
```

### 3.3 AI/ML Technologies

**Large Language Models**
```python
# Groq API
- Fast inference (hardware acceleration)
- Llama and Gemma model families
- Cost-effective pricing
- Low latency responses

# Google Gemini API
- Multimodal capabilities
- High-quality responses
- Google's latest AI technology
- Production-ready scaling
```

**Embedding Models**
```python
# SentenceTransformers
- all-MiniLM-L6-v2 model
- 384-dimensional embeddings
- Multilingual support
- Fast inference
- Good balance of speed/quality
```

**Audio Processing**
```python
# OpenAI Whisper
- State-of-the-art speech recognition
- Multilingual support (99 languages)
- Robust to accents and noise
- Multiple model sizes
- Local inference capability
```

**Natural Language Processing**
```python
# spaCy
- Industrial-strength NLP
- Named entity recognition
- Part-of-speech tagging
- Dependency parsing
- Multiple language models

# TextBlob
- Simple sentiment analysis
- Language detection
- Text processing utilities
- Easy integration
```

### 3.4 External APIs

**Twilio Communication Platform**
```python
# SMS Services
- Global SMS delivery
- Delivery status tracking
- Phone number validation
- Rich messaging support
- Webhook notifications
```

**Translation Services**
```python
# deep-translator
- Multiple translation providers
- Google Translate integration
- Batch translation support
- Language auto-detection
- Error handling and fallback
```

### 3.5 Development Tools

**Testing Framework**
```python
# pytest
- Async testing support
- Fixture system
- Parametrized testing
- Coverage reporting
- Plugin ecosystem

# httpx
- Async HTTP client
- API testing capabilities
- Mock server support
```

**Code Quality Tools**
```python
# black - Code formatting
# isort - Import sorting
# flake8 - Linting
# mypy - Type checking
```

**Documentation Tools**
```python
# FastAPI automatic docs
- Swagger UI (/docs)
- ReDoc (/redoc)
- OpenAPI schema generation
- Interactive API testing
```

### 3.6 Infrastructure Tools

**Process Management**
```python
# APScheduler
- Background task scheduling
- Multiple job stores
- Clustered deployments
- Persistent job storage
```

**Logging and Monitoring**
```python
# Python logging
- Structured logging
- Multiple handlers
- Log rotation
- Error tracking
```

**Environment Management**
```python
# python-dotenv
- Environment variable management
- Configuration separation
- Development/production configs
```

### 3.7 Security Tools

**Authentication & Security**
```python
# python-jose
- JWT token handling
- Cryptographic operations
- Token validation

# passlib + bcrypt
- Password hashing
- Salt generation
- Secure password verification

# python-multipart
- File upload handling
- Form data processing
- Security validation
```

---

## 4. Data Flow

### 4.1 Text Chat Flow
```
User Input → Authentication → Conversation Context → RAG Enhancement → LLM Processing → Response Storage → User Response
```

### 4.2 Audio Chat Flow
```
Audio Upload → Validation → Whisper Transcription → Language Detection → Text Chat Flow → Audio Response Metadata
```

### 4.3 RAG Enhancement Flow
```
User Query → Medical Keyword Detection → Embedding Generation → FAISS Search → Context Retrieval → Prompt Enhancement → LLM Input
```

### 4.4 Reminder Flow
```
Reminder Creation → Scheduling → Background Processing → SMS Delivery → Status Tracking → Delivery Confirmation
```

---

## 5. Security Architecture

### 5.1 Authentication Security
- JWT tokens with short expiry times
- Secure password hashing (bcrypt)
- Token blacklisting capability
- HTTPS enforcement

### 5.2 Data Security
- Input validation and sanitization
- SQL injection prevention (NoSQL)
- File upload validation
- Data encryption at rest

### 5.3 API Security
- CORS configuration
- Rate limiting
- Request size limits
- Security headers

---

## 6. Deployment Architecture

### 6.1 Production Deployment
```
Load Balancer → API Gateway → FastAPI Application → Database Cluster
```

### 6.2 Scaling Strategy
- Horizontal scaling with multiple API instances
- Database replica sets
- CDN for static assets
- Caching layer for frequent queries

### 6.3 Monitoring & Logging
- Application performance monitoring
- Error tracking and alerting
- Log aggregation and analysis
- Health check endpoints

---

## Conclusion

The CareChat project implements a sophisticated healthcare communication system using modern technologies and best practices. The architecture is designed for scalability, maintainability, and security, with a focus on providing accurate medical information through AI-powered conversations enhanced with real clinical data.

The modular design allows for easy testing, development, and future enhancements, while the comprehensive toolchain ensures high code quality and reliable operation in production environments.
