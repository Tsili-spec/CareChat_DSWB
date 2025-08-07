# CareChat Backend - FastAPI with MongoDB Implementation

This is a complete FastAPI implementation of the CareChat backend system with MongoDB, featuring authentication, account creation, and feedback systems exactly as described in the original documentation.

## Features

- **JWT-based Authentication**: Secure token-based authentication with access and refresh tokens
- **Account Management**: Complete patient registration and profile management
- **Multilingual Feedback**: Support for text and audio feedback in multiple languages
- **AI-Powered Analysis**: Sentiment analysis, topic extraction, and urgency detection
- **SMS Integration**: Twilio-based SMS notifications for reminders
- **MongoDB Integration**: Using Beanie ODM for elegant MongoDB operations
- **Intelligent Chat System**: AI-powered conversational chat with RAG (Retrieval-Augmented Generation)
- **Audio Chat Support**: Voice message transcription and processing through Whisper
- **Medical Knowledge RAG**: 50,000+ clinical summaries for context-aware medical responses

## Quick Start

### 1. Install Dependencies

```bash
# Make the start script executable
chmod +x start.sh

# Run the start script (this will create venv, install dependencies, and start the server)
./start.sh
```

### 2. Manual Installation (Alternative)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spacy model
python -m spacy download en_core_web_md

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Environment Configuration

The application uses the MongoDB connection string provided:
`mongodb://stercytambong:w23N0S5Qb6kMUwTi@217.65.144.32:27017/carechat`

You can modify the `.env` file to configure:

```env
# Database
DATABASE_URL=mongodb://stercytambong:w23N0S5Qb6kMUwTi@217.65.144.32:27017/carechat

# JWT Settings
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_REFRESH_SECRET_KEY=your-super-secret-refresh-key-change-in-production

# Twilio (Optional - for SMS reminders)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_NUMBER=your_twilio_phone_number
MY_NUMBER=your_phone_number_for_testing
```

## API Endpoints

### Chat Endpoints

- `POST /api/chat/` - Send text message to AI with conversational memory
- `POST /api/chat/audio` - Send audio message (transcribed and processed as text)
- `GET /api/chat/conversations/{user_id}` - Get all conversations for a user
- `GET /api/chat/conversations/{conversation_id}/history` - Get conversation history
- `DELETE /api/chat/conversations/{conversation_id}` - Delete conversation

### Authentication Endpoints

- `POST /api/signup` - Register a new patient
- `POST /api/login` - Patient login
- `POST /api/refresh` - Refresh access token

### Patient Management

- `GET /api/me?patient_id={id}` - Get patient profile by query parameter
- `GET /api/patient/{patient_id}` - Get patient by path parameter
- `GET /api/patient/` - List all patients with pagination
- `DELETE /api/patient/{patient_id}` - Delete patient account

### Feedback System

- `POST /api/feedback/` - Submit text feedback
- `POST /api/feedback/audio/` - Submit audio feedback
- `GET /api/feedback/{feedback_id}` - Get specific feedback
- `GET /api/feedback/` - List all feedback
- `DELETE /api/feedback/{feedback_id}` - Delete feedback

### Reminder System

- `POST /api/reminder/` - Create reminder
- `GET /api/reminder/{reminder_id}` - Get specific reminder
- `GET /api/reminder/patient/{patient_id}` - Get patient reminders
- `GET /api/reminder/` - List all reminders
- `PUT /api/reminder/{reminder_id}/status` - Update reminder status
- `DELETE /api/reminder/{reminder_id}` - Delete reminder
- `POST /api/reminder/{reminder_id}/send` - Send reminder notification
- `GET /api/reminder/{reminder_id}/deliveries` - Get delivery history

### Scheduler Management

- `POST /api/reminder/start-scheduler` - Start automated scheduler
- `POST /api/reminder/stop-scheduler` - Stop automated scheduler
- `GET /api/reminder/scheduler-status` - Get scheduler status

### Dashboard

- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/recent-activity` - Get recent activity
- `GET /api/dashboard/feedback-analytics` - Get feedback analytics
- `GET /api/dashboard/system-health` - Get system health status

## Architecture

### File Structure

```
app/
├── __init__.py
├── main.py                           # FastAPI application entry point
├── api/                             # API route handlers
│   ├── dashboard.py                 # Dashboard endpoints
│   ├── feedback.py                  # Feedback endpoints
│   ├── patient.py                   # Patient/authentication endpoints
│   └── reminder.py                  # Reminder endpoints
├── core/                            # Core application components
│   ├── auth.py                      # Authentication dependencies
│   ├── config.py                    # Application configuration
│   └── logging_config.py            # Logging configuration
├── db/                              # Database components
│   ├── __init__.py
│   └── database.py                  # MongoDB connection with Beanie
├── models/                          # Database models
│   └── models.py                    # Beanie ODM models
├── schemas/                         # Pydantic schemas
│   ├── feedback.py                  # Feedback validation schemas
│   ├── patient.py                   # Patient validation schemas
│   └── reminder.py                  # Reminder validation schemas
└── services/                        # Business logic services
    ├── analysis.py                  # Feedback analysis
    ├── patient_service.py           # Patient authentication
    ├── reminder_scheduler.py        # Reminder scheduling
    ├── reminder_service.py          # Reminder management
    ├── sms_service.py               # SMS notifications
    ├── transcription.py             # Audio transcription
    ├── transcription_translation.py # Combined transcription/translation
    └── translation.py               # Text translation
```

### Database Models

#### Patient
- Stores patient information with authentication data
- Uses phone number as unique identifier for login
- Supports email for recovery and notifications

#### Feedback
- Stores both text and audio feedback
- Includes sentiment analysis, topic extraction, and urgency detection
- Supports multilingual feedback with translation

#### Reminder
- Stores reminder information with scheduling data
- Supports one-time and recurring reminders
- Tracks reminder status and delivery

#### ReminderDelivery
- Tracks SMS delivery attempts and status
- Stores provider responses for debugging

### Key Features

#### Authentication
- JWT-based with dual tokens (access + refresh)
- Secure password hashing with bcrypt
- Token expiration and refresh mechanism

#### Feedback Analysis
- Sentiment analysis using TextBlob
- Topic extraction using spaCy and keyword matching
- Urgency detection based on keyword analysis
- Multilingual support with automatic translation

#### Audio Processing
- Audio transcription using OpenAI Whisper
- Automatic language detection
- Translation pipeline for non-English audio

#### SMS Integration
- Twilio integration for reminder notifications
- Delivery status tracking
- Configurable SMS templates

#### Reminder Scheduling
- Automated scheduler for reminder delivery
- Configurable delivery times and frequencies
- Manual reminder sending capability

## Example Usage

### 1. Register a Patient

```bash
curl -X POST "http://localhost:8000/api/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "phone_number": "+237123456789",
    "email": "john.doe@example.com",
    "preferred_language": "en",
    "password": "SecurePass123"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+237123456789",
    "password": "SecurePass123"
  }'
```

### 3. Submit Feedback

```bash
curl -X POST "http://localhost:8000/api/feedback/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "patient_id=YOUR_PATIENT_ID" \
  -F "feedback_text=The service was excellent!" \
  -F "rating=5" \
  -F "language=en"
```

### 4. Create Reminder

```bash
curl -X POST "http://localhost:8000/api/reminder/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "YOUR_PATIENT_ID",
    "title": "Take Morning Medication",
    "message": "Please take your morning medication with breakfast",
    "scheduled_time": ["2024-01-15T08:00:00Z"],
    "days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
    "status": "active"
  }'
```

### 5. Send Audio Message

```bash
curl -X POST "http://localhost:8000/api/chat/audio" \
  -F "audio=@recording.wav" \
  -F "user_id=YOUR_PATIENT_ID" \
  -F "provider=groq"
```

### 6. Send Text Chat Message

```bash
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "YOUR_PATIENT_ID",
    "message": "What are the symptoms of diabetes?",
    "provider": "groq"
  }'
```

## Dependencies

### Core Framework
- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI applications

### Database
- **Motor**: Async MongoDB driver
- **Beanie**: Async MongoDB ODM based on Pydantic

### Authentication & Security
- **python-jose**: JWT token handling
- **passlib**: Password hashing
- **bcrypt**: Secure password hashing algorithm

### AI & Analysis
- **spaCy**: Natural language processing
- **TextBlob**: Sentiment analysis
- **scikit-learn**: Machine learning utilities
- **openai-whisper**: Audio transcription
- **deep-translator**: Text translation

### SMS Integration
- **twilio**: SMS notification service

### Other Utilities
- **pydantic**: Data validation and serialization
- **python-multipart**: File upload support
- **python-dotenv**: Environment variable management

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Style
```bash
# Install formatting tools
pip install black isort flake8

# Format code
black app/
isort app/

# Check style
flake8 app/
```

## Production Deployment

### Environment Variables
Ensure all production environment variables are set:

```env
DATABASE_URL=mongodb://production-connection-string
JWT_SECRET_KEY=very-secure-random-key
JWT_REFRESH_SECRET_KEY=very-secure-random-refresh-key
TWILIO_ACCOUNT_SID=production-twilio-sid
TWILIO_AUTH_TOKEN=production-twilio-token
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_md

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Security Considerations
- Change default JWT secret keys
- Use HTTPS in production
- Implement rate limiting
- Set up proper CORS policies
- Enable security headers
- Regular dependency updates

## Support

This implementation exactly matches the original FastAPI system but uses MongoDB instead of PostgreSQL. All endpoints, authentication mechanisms, and analysis features are preserved.

For issues or questions, refer to the API documentation at `/docs` endpoint.
