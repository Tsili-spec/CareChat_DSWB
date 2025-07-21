# CareChat Backend - Docker Setup

This guide will help you containerize and run the CareChat backend using Docker.

## 🐋 Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)

## 📁 Project Structure

```
CareChat_DSWB/Backend/
├── app/                        # FastAPI application
├── Dockerfile                  # Development Docker image
├── Dockerfile.prod            # Production Docker image  
├── docker-compose.yml         # Development setup
├── docker-compose.prod.yml    # Production setup
├── .dockerignore              # Files to exclude from build
├── env.example                # Environment variables example
├── requirements.txt           # Python dependencies
└── README_Docker.md          # This file
```

## 🚀 Quick Start (Development)

### 1. Clone and Navigate
```bash
cd CareChat_DSWB/Backend
```

### 2. Set Up Environment Variables
```bash
# Copy the example environment file
cp env.example .env

# Edit .env with your configuration
nano .env
```

### 3. Start the Services
```bash
# Start backend + database
docker-compose up -d

# Or start with pgAdmin for database management
docker-compose --profile admin up -d
```

### 4. Access the Application
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432
- **pgAdmin** (if started): http://localhost:8080

## 🏭 Production Deployment

### 1. Set Environment Variables
```bash
# Create production environment file
export DB_PASSWORD="your_secure_db_password"
export JWT_SECRET_KEY="your_super_secret_jwt_key"
export JWT_REFRESH_SECRET_KEY="your_super_secret_refresh_key"
export CORS_ORIGINS='["https://yourdomain.com"]'
```

### 2. Deploy with Production Configuration
```bash
# Start production services
docker-compose -f docker-compose.prod.yml up -d

# With Nginx reverse proxy
docker-compose -f docker-compose.prod.yml --profile nginx up -d

# With Redis caching
docker-compose -f docker-compose.prod.yml --profile cache up -d
```

## 🛠 Docker Commands

### Build Commands
```bash
# Build development image
docker build -t carechat-backend .

# Build production image
docker build -f Dockerfile.prod -t carechat-backend:prod .
```

### Container Management
```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs db

# Follow logs in real-time
docker-compose logs -f backend

# Restart services
docker-compose restart backend

# Stop services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v
```

### Database Operations
```bash
# Access database directly
docker exec -it carechat_db psql -U carechat_user -d carechat_db

# Run database migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "your_migration_name"

# Backup database
docker exec carechat_db pg_dump -U carechat_user carechat_db > backup.sql

# Restore database
docker exec -i carechat_db psql -U carechat_user -d carechat_db < backup.sql
```

## 🔧 Environment Variables

Create a `.env` file based on `env.example`:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@db:5432/dbname` |
| `JWT_SECRET_KEY` | JWT signing key | `your_secret_key_here` |
| `JWT_REFRESH_SECRET_KEY` | JWT refresh key | `your_refresh_key_here` |
| `CORS_ORIGINS` | Allowed CORS origins | `["*"]` or `["https://yourdomain.com"]` |

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Connection Error
```bash
# Check if database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

#### 2. Port Already in Use
```bash
# Check what's using the port
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use different host port
```

#### 3. Permission Denied
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

#### 4. Build Cache Issues
```bash
# Force rebuild without cache
docker-compose build --no-cache

# Remove all images and rebuild
docker system prune -a
docker-compose up --build
```

## 📊 Health Checks

The containers include health checks:

```bash
# Check container health
docker inspect carechat_backend | grep -A 10 "Health"

# Manual health check
curl http://localhost:8000/
```

## 🔒 Security Notes

### Development vs Production

**Development** (`Dockerfile`):
- Includes volume mounts for live code reloading
- Runs with `--reload` flag
- More verbose logging
- Includes development tools

**Production** (`Dockerfile.prod`):
- Multi-stage build for smaller image size
- No volume mounts
- Runs with multiple workers
- Optimized for performance
- Security hardening

### Production Security Checklist

- [ ] Change default passwords
- [ ] Use strong JWT secrets
- [ ] Restrict CORS origins
- [ ] Use HTTPS with SSL certificates
- [ ] Enable database connection encryption
- [ ] Regular security updates
- [ ] Monitor container logs
- [ ] Backup database regularly

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Build and Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and deploy
        run: |
          docker build -f Dockerfile.prod -t carechat-backend:latest .
          docker-compose -f docker-compose.prod.yml up -d
```

## 📈 Monitoring

### Container Stats
```bash
# Real-time container stats
docker stats

# Container resource usage
docker-compose exec backend top
```

### Database Monitoring
```bash
# Database connections
docker-compose exec db psql -U carechat_user -d carechat_db -c "SELECT * FROM pg_stat_activity;"

# Database size
docker-compose exec db psql -U carechat_user -d carechat_db -c "SELECT pg_size_pretty(pg_database_size('carechat_db'));"
```

## 🆘 Support

If you encounter issues:

1. Check the logs: `docker-compose logs backend`
2. Verify environment variables: `docker-compose config`
3. Test database connection: `docker-compose exec backend python -c "from app.db.database import engine; print('DB OK' if engine else 'DB FAIL')"`
4. Restart services: `docker-compose restart`

## 💡 Tips

- Use `docker-compose.override.yml` for local customizations
- Keep production secrets in environment variables, not in files
- Regular backups: `docker exec carechat_db pg_dump -U carechat_user carechat_db > backup_$(date +%Y%m%d).sql`
- Monitor disk usage: `docker system df`
- Clean up regularly: `docker system prune`

---

**Currency Note**: As per user preferences, all financial amounts in the application use FCFA currency. 💰 