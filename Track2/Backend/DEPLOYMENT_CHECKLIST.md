# 🚀 Deployment Checklist & Team Setup Guide

## Pre-Deployment Checklist

### ✅ Code Quality & Testing
- [ ] All tests pass locally
- [ ] RAG system initializes successfully 
- [ ] Chat API responds to medical queries with clinical context
- [ ] Authentication endpoints work (register/login)
- [ ] Database migrations run successfully
- [ ] No hardcoded secrets in code

### ✅ Environment Setup
- [ ] `.env.example` file created with required variables
- [ ] All dependencies listed in `requirements.txt`
- [ ] Python version specified (3.8+)
- [ ] Database configuration documented

### ✅ Documentation
- [ ] README.md updated with setup instructions
- [ ] RAG system documented (`RAG_README.md`)
- [ ] API endpoints documented
- [ ] Environment variables documented

### ✅ Security
- [ ] JWT secret key is configurable
- [ ] Database credentials not hardcoded
- [ ] API key not committed to git
- [ ] CORS configured for production

## Render Deployment Steps

### 1. Repository Preparation
```bash
# Create .env.example
cp .env .env.example
# Remove actual secrets, leave placeholders

# Verify requirements.txt is complete
pip freeze > requirements.txt

# Test clean install
python -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt
```

### 2. Render Configuration

**Service Type**: Web Service
**Build Command**: `pip install -r requirements.txt`
**Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Environment Variables**:
```
GOOGLE_API_KEY=your_actual_gemini_api_key
MODEL_NAME=gemini-2.0-flash
SECRET_KEY=your_super_secret_production_key
DATABASE_URL=postgresql://render_generated_url
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Database Setup on Render
1. Create PostgreSQL database service
2. Copy database URL to `DATABASE_URL` environment variable
3. Database tables will be created automatically on first run

### 4. Verification Steps
- [ ] Service builds successfully
- [ ] Health check endpoint responds: `/health`
- [ ] RAG system initializes (check logs for "✅ RAG service initialized")
- [ ] Chat endpoint works: `POST /chat/`
- [ ] Auth endpoints work: `POST /auth/register`, `POST /auth/login`

## Team Collaboration Setup

### New Team Member Onboarding

1. **Clone Repository**
```bash
git clone [repository-url]
cd CareChat/Backend
```

2. **Environment Setup**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

3. **Configuration**
```bash
# Copy environment template
cp .env.example .env

# Get Google AI API key from team lead
# Add to .env file
GOOGLE_API_KEY=your_api_key_here
```

4. **Test Local Setup**
```bash
uvicorn app.main:app --reload
# Should see: "✅ RAG service initialized successfully"

curl http://localhost:8000/health
# Should return: {"status": "healthy", "rag_service": "operational"}
```

### Development Workflow

1. **Feature Development**
```bash
git checkout -b feature/your-feature-name
# Make changes
# Test locally
git add .
git commit -m "feat: describe your changes"
git push origin feature/your-feature-name
```

2. **Testing Changes**
```bash
# Test RAG system
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are symptoms of malaria?"}'

# Test auth system
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123"}'
```

3. **Code Review Checklist**
- [ ] RAG system functionality preserved
- [ ] No breaking changes to API contracts
- [ ] Environment variables properly configured
- [ ] Documentation updated if needed

## Production Monitoring

### Health Checks
- **Application**: `GET /health`
- **Database**: Monitor connection status
- **RAG System**: Check embedding cache status
- **API Usage**: Monitor Gemini API calls

### Performance Metrics
- **Response Time**: Chat endpoints < 2 seconds
- **RAG Performance**: Vector search < 50ms
- **Memory Usage**: Monitor embedding cache size
- **Error Rates**: < 1% for chat endpoints

### Log Monitoring
Look for these key log messages:
- ✅ "RAG service initialized successfully"
- ✅ "Database connected successfully"
- ⚠️ "RAG query failed, falling back to base model"
- ❌ "Failed to load embeddings cache"

## Scaling Considerations

### RAG System Scaling
- **Current**: 1,000 test cases (fast development)
- **Production**: 50,000 full dataset (better accuracy)
- **Future**: Consider GPU acceleration for larger datasets

### Database Scaling
- **Development**: SQLite (included)
- **Production**: PostgreSQL (Render managed)
- **Enterprise**: Consider read replicas for heavy load

### API Scaling
- **Rate Limiting**: Implement for production
- **Caching**: Consider Redis for session storage
- **Load Balancing**: Render handles automatically

## Security Best Practices

### API Security
- [ ] JWT tokens expire appropriately (30 minutes)
- [ ] Passwords hashed with bcrypt
- [ ] CORS configured for frontend domain only
- [ ] Rate limiting on auth endpoints

### Data Security
- [ ] Clinical data anonymized in RAG system
- [ ] No PII in logs
- [ ] Database connections encrypted
- [ ] API keys stored securely

### Deployment Security
- [ ] Environment variables not committed
- [ ] Production secrets differ from development
- [ ] HTTPS enforced in production
- [ ] Database access restricted

## Troubleshooting Common Issues

### RAG System Issues
**Problem**: "RAG service initialization failed"
**Solution**: Check if `clinical_summaries_test.csv` exists, verify file permissions

**Problem**: Slow startup on first run
**Solution**: Normal behavior - generating embeddings takes 30-60 seconds

**Problem**: "No relevant context found"
**Solution**: Check if query contains medical keywords, verify embedding model loaded

### Database Issues
**Problem**: "Database connection failed"
**Solution**: Verify `DATABASE_URL` environment variable, check database service status

**Problem**: "Table doesn't exist"
**Solution**: Database tables created automatically on first run - restart service

### API Issues
**Problem**: "Authentication failed"
**Solution**: Verify `SECRET_KEY` environment variable, check JWT token format

**Problem**: "CORS error from frontend"
**Solution**: Configure CORS in `app/main.py` for frontend domain

## Rollback Procedures

### Quick Rollback
1. Revert to previous working commit
2. Redeploy on Render (auto-deployment)
3. Verify health checks pass
4. Monitor for 15 minutes

### Database Rollback
1. Use Render database backups
2. Restore to previous working state
3. Update application if schema changed
4. Test RAG system functionality

## Team Communication

### Status Updates
- Daily standup: Mention any RAG/deployment issues
- Weekly: Review API usage and performance metrics
- Monthly: Consider dataset updates and model improvements

### Issue Escalation
1. **Development Issues**: Team lead
2. **Deployment Issues**: DevOps contact
3. **RAG/AI Issues**: AI specialist
4. **Database Issues**: Backend lead

---

## Quick Reference Commands

```bash
# Local development
uvicorn app.main:app --reload

# Test health
curl http://localhost:8000/health

# Test chat with RAG
curl -X POST "http://localhost:8000/chat/" -H "Content-Type: application/json" -d '{"message": "What is malaria?"}'

# View logs
tail -f logs/app.log

# Database shell (SQLite)
sqlite3 carechat.db

# Reset RAG cache (force rebuild)
rm Data/embeddings_test.pkl Data/faiss_index_test.bin Data/processed_clinical_data_test.pkl
```

Your deployment is ready! 🎉 Share this checklist with your team for smooth collaboration.
