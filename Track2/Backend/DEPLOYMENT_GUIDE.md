# CareChat Backend - Deployment Guide

## Environment Variables Configuration

### For Local Development

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your actual values:
```bash
# Database Configuration
DATABASE_URL=sqlite:///./carechat.db  # For development
# DATABASE_URL=postgresql://username:password@host:port/database  # For production

# Application Security
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_REFRESH_SECRET_KEY=your-jwt-refresh-secret-key-change-in-production

# Google Gemini AI API Key
GEMINI_API_KEY=your-gemini-api-key-here
```

### For Render.com Deployment

#### 1. Environment Variables in Render Dashboard

Set the following environment variables in your Render service:

**Database:**
- `DATABASE_URL`: Your PostgreSQL connection string from Render (automatically provided)

**Security Keys:**
- `SECRET_KEY`: Generate a secure random string (32+ characters)
- `JWT_SECRET_KEY`: Generate a secure random string (32+ characters)  
- `JWT_REFRESH_SECRET_KEY`: Generate a secure random string (32+ characters)

**API Keys:**
- `GEMINI_API_KEY`: Your Google AI Studio API key

#### 2. Generate Secure Keys

Use this command to generate secure keys:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 3. PostgreSQL Database

Render automatically provides PostgreSQL connection strings in the format:
```
postgresql://username:password@host:port/database_name
```

This is automatically set as `DATABASE_URL` environment variable.

#### 4. Build Commands for Render

**Build Command:**
```bash
cd Backend && pip install -r requirements.txt
```

**Start Command:**
```bash
cd Backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Getting Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key
5. Set it as `GEMINI_API_KEY` environment variable

### Environment Variable Loading

The application uses the following priority for loading environment variables:

1. **Environment variables** (highest priority)
2. **`.env` file** (local development)
3. **Default values** (where applicable)

The configuration is handled in `app/core/config.py`:

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Load from .env file if present

DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY')
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "refreshsecret")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # No default for security
```

### Security Best Practices

#### ✅ DO:
- Use strong, randomly generated keys for production
- Set `DATABASE_URL` to PostgreSQL for production
- Keep API keys secret and never commit them to version control
- Use different keys for development and production
- Regularly rotate API keys

#### ❌ DON'T:
- Use default values for secret keys in production
- Hardcode API keys in source code
- Commit `.env` files to version control
- Use SQLite for production (use PostgreSQL)
- Share API keys in documentation or chat

### Environment Variable Validation

The application includes validation for critical environment variables:

```python
# In app/services/llm_service.py
if not GEMINI_API_KEY:
    raise HTTPException(status_code=500, detail="Gemini API key not configured")
```

### Troubleshooting

#### Common Issues:

1. **"Gemini API key not configured"**
   - Ensure `GEMINI_API_KEY` is set correctly
   - Check for typos in the environment variable name
   - Verify the API key is valid

2. **Database connection errors**
   - Check `DATABASE_URL` format
   - Ensure PostgreSQL service is running (for production)
   - Verify database credentials

3. **Module import errors**
   - Ensure the start command includes the correct working directory
   - For Render: `cd Backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Testing Environment Configuration

Use the provided test scripts to verify your configuration:

```bash
# Test environment variables
python3 test_env.py

# Test API functionality
python3 test_fixes.py
```

### Render Deployment Checklist

- [ ] PostgreSQL database created and connected
- [ ] All environment variables set in Render dashboard
- [ ] Build command configured: `cd Backend && pip install -r requirements.txt`
- [ ] Start command configured: `cd Backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] `.env` file NOT committed to repository
- [ ] Gemini API key valid and working
- [ ] Database migrations run successfully

### Collaborator Setup

For other developers working on the project:

1. Clone the repository
2. Copy `.env.example` to `.env`
3. Get API keys and database credentials
4. Update `.env` with their values
5. Run `pip install -r requirements.txt`
6. Start the server: `uvicorn app.main:app --reload`

The environment variable configuration is designed to work seamlessly across:
- Local development environments
- Render.com hosting
- Other cloud platforms
- Different operating systems
