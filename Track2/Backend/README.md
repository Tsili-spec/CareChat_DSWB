# Healthcare Chat System - Deployment & Collaboration Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL (for production) or SQLite (for development)
- Google AI API key (for Gemini 2.0-flash)

### Local Development Setup

1. **Clone and Setup Environment**
```bash
cd Backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

2. **Environment Configuration**
Create `.env` file in Backend directory:
```env
# AI Configuration
GOOGLE_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-2.0-flash

# Database (for development)
DATABASE_URL=sqlite:///./carechat.db

# JWT Security
SECRET_KEY=your-super-secret-jwt-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional: Production Database
# DATABASE_URL=postgresql://user:password@localhost/carechat_db
```

3. **Initialize and Start**
```bash
# Database setup (automatic)
uvicorn app.main:app --reload

# Server will start on http://localhost:8000
# RAG system will initialize automatically on first run
```

## 🧠 RAG System Overview

This system includes **Retrieval-Augmented Generation (RAG)** for clinically-informed responses:

- **Dataset**: 50,000 clinical summaries (COVID-19, Malaria, Typhoid, Anemia, Dengue, Hepatitis)
- **Test Dataset**: 1,000 cases for faster development
- **Technology**: Sentence-transformers + FAISS vector search
- **Caching**: Intelligent embedding cache (rebuilds only when data changes)

**First Run**: Takes 30-60 seconds to generate embeddings
**Subsequent Runs**: 2-3 seconds (loads from cache)

For detailed RAG documentation, see [`RAG_README.md`](./RAG_README.md)

## 📁 Project Structure

```
Backend/
├── app/
│   ├── main.py                 # FastAPI application entry
│   ├── api/                    # API endpoints
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── chatbot.py         # Chat API with RAG integration
│   │   ├── patient.py         # Patient management
│   │   └── feedback.py        # Feedback system
│   ├── core/                  # Core configurations
│   │   ├── config.py          # App settings
│   │   └── jwt_auth.py        # JWT authentication
│   ├── db/                    # Database
│   │   └── database.py        # Database connection
│   ├── models/                # SQLAlchemy models
│   │   ├── user.py           # User model
│   │   ├── conversation.py   # Chat conversation model
│   │   └── feedback.py       # Feedback model
│   ├── schemas/              # Pydantic schemas
│   │   ├── user.py          # User schemas
│   │   ├── chat.py          # Chat schemas
│   │   └── conversation.py  # Conversation schemas
│   └── services/            # Business logic
│       ├── llm_service.py   # AI model service (Gemini 2.0-flash)
│       ├── rag_service.py   # RAG implementation
│       └── conversation_service.py  # Chat memory management
├── Data/                    # RAG datasets and cache
│   ├── clinical_summaries.csv          # Full dataset (50K)
│   ├── clinical_summaries_test.csv     # Test dataset (1K)
│   ├── embeddings_test.pkl             # Cached embeddings
│   ├── faiss_index_test.bin            # Cached search index
│   └── processed_clinical_data_test.pkl # Cached processed data
└── requirements.txt         # Python dependencies
```

## 🔧 Key Features

### 1. RAG-Enhanced Healthcare Chat
- **Smart Context Retrieval**: Automatically finds relevant clinical cases
- **Medical Keyword Detection**: Triggers RAG for medical queries
- **Conversation Memory**: Maintains context across multiple exchanges
- **Clinical Grounding**: Responses based on real medical case data

### 2. User Management & Authentication
- **JWT-based Authentication**: Secure token-based auth
- **User Registration/Login**: Complete user management
- **Password Security**: Hashed passwords with bcrypt

### 3. Conversation Management
- **Persistent Chat History**: All conversations saved with user context
- **Memory System**: Intelligent context management for long conversations
- **Multiple Conversations**: Users can have multiple chat sessions

### 4. Feedback System
- **Response Rating**: Users can rate AI responses
- **Feedback Collection**: Detailed feedback for system improvement
- **Analytics Ready**: Structured feedback data for analysis

## 🌐 Deployment Options

### Option 1: Render (Recommended for Demo)

1. **Prepare for Render**
```bash
# Ensure requirements.txt includes all dependencies
pip freeze > requirements.txt

# Create render.yaml (optional)
```

2. **Environment Variables on Render**
```
GOOGLE_API_KEY=your_gemini_api_key
MODEL_NAME=gemini-2.0-flash
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://render_db_url  # Render provides this
```

3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Option 2: Docker Deployment

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Option 3: Traditional VPS

1. Install Python 3.8+, PostgreSQL
2. Clone repository and install dependencies
3. Configure environment variables
4. Use systemd/supervisor for process management
5. Set up nginx as reverse proxy

## 🧪 Testing the System

### Basic Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "rag_service": "operational"}
```

### Test Chat with RAG
```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the symptoms of malaria?"}'
```

### Test User Authentication
```bash
# Register user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123"}'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

## 🔍 Monitoring & Debugging

### RAG System Status
- Check logs for "✅ RAG service initialized successfully"
- Embedding cache files should be created in `Data/` directory
- First run takes longer due to embedding generation

### Common Issues
1. **Slow Startup**: Normal on first run (generating embeddings)
2. **Missing API Key**: Check `.env` file for `GOOGLE_API_KEY`
3. **Database Issues**: Ensure database URL is correct
4. **RAG Not Working**: Check if `clinical_summaries_test.csv` exists

### Performance Monitoring
- Monitor embedding cache hit rates
- Track RAG trigger frequency
- Monitor token usage for Gemini API

## 👥 Team Collaboration

### Git Workflow
1. Create feature branches from `main`
2. Test locally before pushing
3. Include environment setup in PR descriptions
4. Document any new dependencies

### Adding New Medical Data
1. Add new cases to `clinical_summaries.csv`
2. Delete cache files to force rebuild
3. Test with relevant medical queries
4. Update documentation if new conditions added

### API Extensions
- New endpoints in `app/api/`
- New models in `app/models/`
- New schemas in `app/schemas/`
- New business logic in `app/services/`

## 📊 Production Considerations

### Scaling RAG System
- **Full Dataset**: Switch to `clinical_summaries.csv` (50K cases) for production
- **GPU Support**: Use `faiss-gpu` for larger datasets
- **Index Updates**: Implement incremental updates for new clinical data

### Security Checklist
- [ ] Change default `SECRET_KEY` in production
- [ ] Use PostgreSQL for production database
- [ ] Enable CORS properly for frontend domain
- [ ] Implement rate limiting for API endpoints
- [ ] Monitor API usage and costs

### Backup Strategy
- Regular database backups
- Backup RAG embedding cache
- Version control for clinical datasets
- Monitor API key usage limits

## 🤝 Contributing

1. **Setup Development Environment**: Follow local setup instructions
2. **Test RAG System**: Ensure it works with sample medical queries
3. **Make Changes**: Follow existing code patterns
4. **Test Thoroughly**: Include both API and RAG functionality
5. **Document Changes**: Update README if adding new features

## 📞 Support & Resources

- **RAG Documentation**: [`RAG_README.md`](./RAG_README.md)
- **API Documentation**: Available at `http://localhost:8000/docs` when running
- **Chat API Details**: [`CHAT_API_DOCUMENTATION.md`](./CHAT_API_DOCUMENTATION.md)
- **Deployment Guide**: [`DEPLOYMENT_GUIDE.md`](./DEPLOYMENT_GUIDE.md)

---

## ⚡ Quick Test Commands

```bash
# Start development server
uvicorn app.main:app --reload

# Test RAG system
curl -X POST "http://localhost:8000/chat/" -H "Content-Type: application/json" -d '{"message": "What is malaria?"}'

# Check health
curl http://localhost:8000/health

# View API docs
# Open browser to http://localhost:8000/docs
```

Your healthcare chat system is now ready for team collaboration and deployment! 🎉
