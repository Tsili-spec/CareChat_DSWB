# CareChat API Gateway Environment Configuration

This FastAPI application uses environment variables for configuration, following the same pattern as other CareChat microservices.

## Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual configuration values:
   ```bash
   nano .env
   ```

3. Start the application:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Required Environment Variables

The following variables must be set in your `.env` file:

### Database Configuration
- `MONGODB_URL` - MongoDB connection string
- `MONGODB_DATABASE` - MongoDB database name
- `TRACK3_DATABASE_URL` - PostgreSQL connection string for Track3

### Microservice URLs
- `TRACK1_SERVICE_URL` - Track1 service endpoint
- `TRACK2_SERVICE_URL` - Track2 service endpoint  
- `TRACK3_SERVICE_URL` - Track3 service endpoint

### Redis Configuration
- `REDIS_URL` - Redis connection string

### Security (Important for Production)
- `SECRET_KEY` - JWT signing secret (change default for production!)

## Optional Environment Variables

### API Configuration
- `APP_NAME` - Application name
- `DEBUG` - Enable debug mode (default: false)
- `ENVIRONMENT` - Environment name (development/production)
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)

### CORS Configuration
- `BACKEND_CORS_ORIGINS` - Comma-separated list of allowed origins

### AI/LLM Configuration
- `GEMINI_API_KEY` - Google Gemini API key
- `GROQ_API_KEY` - Groq API key
- `OPENAI_API_KEY` - OpenAI API key
- `DEFAULT_LLM_PROVIDER` - Default LLM provider (gemini/groq/openai)

### Notification Services
- `TWILIO_ACCOUNT_SID` - Twilio account SID
- `TWILIO_AUTH_TOKEN` - Twilio auth token
- `TWILIO_PHONE_NUMBER` - Twilio phone number

### Email Configuration
- `SMTP_HOST` - SMTP server host
- `SMTP_PORT` - SMTP server port
- `SMTP_USER` - SMTP username
- `SMTP_PASS` - SMTP password
- `SMTP_TLS` - Enable TLS (default: true)

### Rate Limiting
- `RATE_LIMIT_PER_MINUTE` - Requests per minute limit
- `RATE_LIMIT_BURST` - Burst request limit

### Logging
- `LOG_LEVEL` - Logging level (INFO/DEBUG/WARNING/ERROR)
- `LOG_FILE` - Log file path (optional)

## Environment-Specific Configuration

### Development
```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

### Production
```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-super-secure-production-key
BACKEND_CORS_ORIGINS=https://carechat.com,https://www.carechat.com
LOG_LEVEL=INFO
```

## Legacy Compatibility

The following environment variables are automatically set for backward compatibility:
- `TRACK1_BACKEND_URL` (defaults to `TRACK1_SERVICE_URL`)
- `TRACK2_BACKEND_URL` (defaults to `TRACK2_SERVICE_URL`)
- `TRACK3_BACKEND_URL` (defaults to `TRACK3_SERVICE_URL`)

## Configuration Validation

The application will validate all required configuration on startup. If any required variables are missing or invalid, the application will fail to start with a helpful error message.

## Docker Configuration

When running in Docker, you can either:

1. Mount your `.env` file:
   ```bash
   docker run -v $(pwd)/.env:/app/.env carechat-api-gateway
   ```

2. Pass environment variables directly:
   ```bash
   docker run -e MONGODB_URL=... -e SECRET_KEY=... carechat-api-gateway
   ```

## Security Notes

- Always change the default `SECRET_KEY` in production
- Use strong, unique passwords for all database connections
- Enable TLS/SSL for production deployments
- Restrict CORS origins to only necessary domains in production
- Store sensitive credentials in secure secret management systems
