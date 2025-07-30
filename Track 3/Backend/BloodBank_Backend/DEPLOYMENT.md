# 🚀 Blood Bank Management System - Deployment Guide

## 📋 Table of Contents

1. [Development Setup](#development-setup)
2. [Production Deployment](#production-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Database Migration](#database-migration)
5. [Environment Configuration](#environment-configuration)
6. [Security Checklist](#security-checklist)
7. [Monitoring & Logging](#monitoring--logging)
8. [Backup & Recovery](#backup--recovery)

## 🛠️ Development Setup

### **Quick Start (Linux/macOS)**
```bash
# Clone the repository
git clone <repository-url>
cd BloodBank_Backend

# Run the start script
./start.sh
```

### **Quick Start (Windows)**
```cmd
# Clone the repository
git clone <repository-url>
cd BloodBank_Backend

# Run the start script
start.bat
```

### **Manual Setup**
```bash
# 1. Create virtual environment
python -m venv bloodbank_env
source bloodbank_env/bin/activate  # On Windows: bloodbank_env\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your configurations

# 4. Initialize database
python scripts/init_db.py

# 5. Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 Production Deployment

### **1. Server Requirements**

#### **Minimum System Requirements**
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **OS**: Ubuntu 20.04 LTS or newer
- **Python**: 3.8+
- **PostgreSQL**: 12+

#### **Recommended System Requirements**
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 50GB SSD
- **Load Balancer**: Nginx
- **SSL**: Let's Encrypt certificate

### **2. Production Environment Setup**

#### **System Dependencies**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv postgresql-client nginx -y

# Install system packages
sudo apt install build-essential libpq-dev python3-dev -y
```

#### **Application Setup**
```bash
# Create application user
sudo useradd -m -s /bin/bash bloodbank
sudo su - bloodbank

# Clone application
git clone <repository-url> /home/bloodbank/app
cd /home/bloodbank/app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install production server
pip install gunicorn

# Create production environment file
cp .env.example .env
```

#### **Production Environment Variables**
```env
# .env for production
DEBUG=False
SECRET_KEY=your-super-secure-production-secret-key-minimum-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database (Production PostgreSQL)
POSTGRES_SERVER=your-production-db-host
POSTGRES_USER=bloodbank_prod_user
POSTGRES_PASSWORD=super-secure-production-password
POSTGRES_DB=bloodbank_production
POSTGRES_PORT=5432

# CORS (Update with your frontend domains)
BACKEND_CORS_ORIGINS=["https://yourdomain.com","https://app.yourdomain.com"]

# Optional: Email configuration
SMTP_HOST=smtp.yourdomain.com
SMTP_PORT=587
SMTP_USER=noreply@yourdomain.com
SMTP_PASSWORD=email-password
```

### **3. Systemd Service Configuration**

#### **Create Service File**
```bash
sudo nano /etc/systemd/system/bloodbank.service
```

```ini
[Unit]
Description=Blood Bank Management System
After=network.target postgresql.service

[Service]
Type=exec
User=bloodbank
Group=bloodbank
WorkingDirectory=/home/bloodbank/app
Environment=PATH=/home/bloodbank/app/venv/bin
ExecStart=/home/bloodbank/app/venv/bin/gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

#### **Enable and Start Service**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable bloodbank

# Start service
sudo systemctl start bloodbank

# Check status
sudo systemctl status bloodbank

# View logs
sudo journalctl -u bloodbank -f
```

### **4. Nginx Configuration**

#### **Create Nginx Configuration**
```bash
sudo nano /etc/nginx/sites-available/bloodbank
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/m;
    limit_req zone=api burst=20 nodelay;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API documentation (optional, disable in production)
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Restrict access (optional)
        # allow 192.168.1.0/24;
        # deny all;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
```

#### **Enable Site**
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/bloodbank /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Enable Nginx
sudo systemctl enable nginx
```

### **5. SSL Certificate (Let's Encrypt)**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (already configured by certbot)
sudo systemctl status certbot.timer
```

## 🐳 Docker Deployment

### **1. Docker Configuration**

#### **Dockerfile**
```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/venv/bin:$PATH"

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv venv

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' bloodbank
RUN chown -R bloodbank:bloodbank /app
USER bloodbank

# Initialize database (will be overridden in production)
RUN venv/bin/python scripts/init_db.py

# Expose port
EXPOSE 8000

# Start application
CMD ["venv/bin/gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

#### **docker-compose.yml**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - POSTGRES_SERVER=db
      - POSTGRES_USER=bloodbank_user
      - POSTGRES_PASSWORD=secure_password
      - POSTGRES_DB=bloodbank_db
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=bloodbank_user
      - POSTGRES_PASSWORD=secure_password
      - POSTGRES_DB=bloodbank_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

#### **Docker Production Environment**
```env
# .env.docker
DEBUG=False
SECRET_KEY=your-docker-production-secret-key
POSTGRES_SERVER=db
POSTGRES_USER=bloodbank_user
POSTGRES_PASSWORD=secure_docker_password
POSTGRES_DB=bloodbank_db
REDIS_URL=redis://redis:6379/0
```

### **2. Docker Deployment Commands**

```bash
# Build and start services
docker-compose up -d --build

# View logs
docker-compose logs -f web

# Scale web service
docker-compose up -d --scale web=3

# Update application
docker-compose pull
docker-compose up -d --build

# Backup database
docker-compose exec db pg_dump -U bloodbank_user bloodbank_db > backup.sql

# Restore database
docker-compose exec -T db psql -U bloodbank_user bloodbank_db < backup.sql
```

## 🔄 Database Migration

### **Using Alembic**

#### **Initialize Alembic**
```bash
# Initialize migration repository
alembic init alembic

# Create first migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

#### **Migration Script Example**
```python
# alembic/versions/001_initial_migration.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('email', sa.String(100), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(100), nullable=False),
        sa.Column('role', sa.String(50), default='staff'),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table('users')
```

### **Database Backup Strategy**

#### **Automated Backup Script**
```bash
#!/bin/bash
# backup_db.sh

DB_NAME="bloodbank_db"
DB_USER="bloodbank_user"
DB_HOST="localhost"
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/bloodbank_$DATE.sql.gz

# Remove backups older than 30 days
find $BACKUP_DIR -name "bloodbank_*.sql.gz" -mtime +30 -delete

echo "Backup completed: bloodbank_$DATE.sql.gz"
```

#### **Cron Job for Daily Backups**
```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /path/to/backup_db.sh
```

## 🔒 Security Checklist

### **Production Security**

- [ ] **Environment Variables**
  - [ ] Strong SECRET_KEY (32+ characters)
  - [ ] DEBUG=False in production
  - [ ] Secure database credentials
  - [ ] Environment-specific CORS origins

- [ ] **Database Security**
  - [ ] Use dedicated database user with limited permissions
  - [ ] Enable SSL/TLS for database connections
  - [ ] Regular security updates
  - [ ] Database firewall rules

- [ ] **Application Security**
  - [ ] HTTPS enforcement
  - [ ] Security headers (HSTS, CSP, etc.)
  - [ ] Rate limiting
  - [ ] Input validation
  - [ ] SQL injection protection

- [ ] **Authentication Security**
  - [ ] Strong password requirements
  - [ ] Account lockout mechanism
  - [ ] Token expiration (15-30 minutes in production)
  - [ ] Secure session management

- [ ] **Network Security**
  - [ ] Firewall configuration
  - [ ] VPN access for admin functions
  - [ ] IP whitelisting for sensitive endpoints
  - [ ] DDoS protection

## 📊 Monitoring & Logging

### **Application Monitoring**

#### **Health Check Endpoint**
```python
@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    checks = {
        "database": await check_database_health(),
        "redis": await check_redis_health(),
        "disk_space": check_disk_space(),
        "memory": check_memory_usage(),
    }
    
    status = "healthy" if all(checks.values()) else "unhealthy"
    
    return {
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks,
        "version": settings.VERSION
    }
```

#### **Prometheus Metrics**
```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
request_count = Counter('app_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('app_request_duration_seconds', 'Request duration')
active_users = Gauge('app_active_users', 'Active users')

@app.middleware("http")
async def add_prometheus_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    request_count.labels(request.method, request.url.path).inc()
    request_duration.observe(duration)
    
    return response
```

### **Logging Configuration**

#### **Structured Logging**
```python
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Usage
logger = structlog.get_logger()
logger.info("User login", user_id=123, username="admin", ip_address="192.168.1.1")
```

### **Log Aggregation (ELK Stack)**

#### **Filebeat Configuration**
```yaml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/bloodbank/*.log
  fields:
    service: bloodbank-api
    environment: production

output.elasticsearch:
  hosts: ["elasticsearch:9200"]

setup.kibana:
  host: "kibana:5601"
```

## 🔄 Backup & Recovery

### **Database Backup**

#### **Full Backup**
```bash
# Create full backup
pg_dump -h localhost -U bloodbank_user -W bloodbank_db > bloodbank_full_backup.sql

# Compressed backup
pg_dump -h localhost -U bloodbank_user -W bloodbank_db | gzip > bloodbank_backup.sql.gz
```

#### **Incremental Backup (WAL)**
```bash
# Enable WAL archiving in postgresql.conf
archive_mode = on
archive_command = 'cp %p /archive/%f'

# Base backup
pg_basebackup -D /backup/base -Ft -z -P -U bloodbank_user

# Point-in-time recovery
pg_ctl stop -D /data
rm -rf /data/*
tar -xzf /backup/base/base.tar.gz -C /data
# Configure recovery.conf and start
```

### **Application Backup**

#### **File System Backup**
```bash
#!/bin/bash
# backup_app.sh

APP_DIR="/home/bloodbank/app"
BACKUP_DIR="/backups/app"
DATE=$(date +%Y%m%d_%H%M%S)

# Create application backup
tar -czf $BACKUP_DIR/bloodbank_app_$DATE.tar.gz -C $APP_DIR .

# Upload to cloud storage (optional)
aws s3 cp $BACKUP_DIR/bloodbank_app_$DATE.tar.gz s3://your-bucket/backups/

echo "Application backup completed: bloodbank_app_$DATE.tar.gz"
```

### **Disaster Recovery Plan**

#### **Recovery Procedures**

1. **Database Recovery**
```bash
# Stop application
sudo systemctl stop bloodbank

# Restore database
psql -h localhost -U bloodbank_user -d bloodbank_db < backup.sql

# Start application
sudo systemctl start bloodbank
```

2. **Application Recovery**
```bash
# Extract application backup
tar -xzf bloodbank_app_backup.tar.gz -C /home/bloodbank/app

# Restore permissions
chown -R bloodbank:bloodbank /home/bloodbank/app

# Restart services
sudo systemctl restart bloodbank nginx
```

3. **Configuration Recovery**
```bash
# Restore environment variables
cp .env.backup .env

# Update configuration
sudo systemctl daemon-reload
sudo systemctl restart bloodbank
```

## 📋 Deployment Checklist

### **Pre-Deployment**
- [ ] Code review completed
- [ ] All tests passing
- [ ] Security scan completed
- [ ] Database migrations tested
- [ ] Backup strategy verified
- [ ] Monitoring configured
- [ ] SSL certificate ready

### **Deployment**
- [ ] Deploy to staging environment
- [ ] Run integration tests
- [ ] Database migration applied
- [ ] Configuration updated
- [ ] Services restarted
- [ ] Health checks passing
- [ ] Monitoring alerts configured

### **Post-Deployment**
- [ ] Application health verified
- [ ] Performance monitoring active
- [ ] Error tracking enabled
- [ ] Backup verification
- [ ] Documentation updated
- [ ] Team notification sent

---

**🩸 Blood Bank Management System** - Secure, scalable, and reliable healthcare deployment.

*Last updated: January 29, 2025*
