# Calculator Suite - Deployment Guide

## 🚀 Production Deployment Guide

This guide covers deploying the Calculator Suite to production environments with proper configuration, monitoring, and scaling considerations.

## 📋 Prerequisites

### System Requirements
- **OS:** Linux (Ubuntu 20.04+ recommended) or Docker
- **Python:** 3.9 or higher
- **Memory:** Minimum 512MB RAM, 2GB+ recommended
- **Storage:** 1GB+ available space
- **Network:** Port 80/443 access for web traffic

### Dependencies
```bash
# Required packages
Flask>=2.3.0
gunicorn>=20.0.0
psycopg2-binary>=2.9.0  # If using PostgreSQL
redis>=4.0.0           # If using Redis cache
```

## 🐳 Docker Deployment (Recommended)

### 1. Create Dockerfile
```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "30", "app_simple_fixed:app"]
```

### 2. Create docker-compose.yml
```yaml
version: '3.8'

services:
  calculator-app:
    build: .
    ports:
      - "80:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:14
    environment:
      - POSTGRES_DB=calculator_suite
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - calculator-app
    restart: unless-stopped

volumes:
  postgres_data:
```

### 3. Environment Configuration
```bash
# .env file
SECRET_KEY=your-super-secret-key-here
DB_USER=calculator_user
DB_PASSWORD=secure-password-here
DATABASE_URL=postgresql://calculator_user:secure-password-here@postgres:5432/calculator_suite
REDIS_URL=redis://redis:6379/0
```

### 4. Deploy with Docker Compose
```bash
# Build and start services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f calculator-app
```

## 🖥️ Traditional Server Deployment

### 1. Server Setup (Ubuntu 20.04)
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv nginx postgresql redis-server

# Create application user
sudo useradd --create-home --shell /bin/bash calculator
sudo mkdir -p /var/www/calculator-suite
sudo chown calculator:calculator /var/www/calculator-suite
```

### 2. Application Setup
```bash
# Switch to application user
sudo su - calculator

# Clone repository
cd /var/www/calculator-suite
git clone <repository-url> .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary redis

# Set environment variables
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
DATABASE_URL=postgresql://calculator_user:password@localhost/calculator_suite
REDIS_URL=redis://localhost:6379/0
EOF
```

### 3. Database Setup
```bash
# PostgreSQL setup
sudo -u postgres psql << EOF
CREATE DATABASE calculator_suite;
CREATE USER calculator_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE calculator_suite TO calculator_user;
\q
EOF

# Redis configuration
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 4. Gunicorn Configuration
```bash
# Create gunicorn config
cat > /var/www/calculator-suite/gunicorn.conf.py << EOF
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
preload_app = True
daemon = False
user = "calculator"
group = "calculator"
pidfile = "/var/run/gunicorn/calculator-suite.pid"
accesslog = "/var/log/calculator-suite/access.log"
errorlog = "/var/log/calculator-suite/error.log"
loglevel = "info"
EOF

# Create directories
sudo mkdir -p /var/run/gunicorn /var/log/calculator-suite
sudo chown calculator:calculator /var/run/gunicorn /var/log/calculator-suite
```

### 5. Systemd Service
```bash
# Create systemd service
sudo cat > /etc/systemd/system/calculator-suite.service << EOF
[Unit]
Description=Calculator Suite Web Application
After=network.target

[Service]
Type=forking
User=calculator
Group=calculator
WorkingDirectory=/var/www/calculator-suite
Environment=PATH=/var/www/calculator-suite/venv/bin
ExecStart=/var/www/calculator-suite/venv/bin/gunicorn --config gunicorn.conf.py app_simple_fixed:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable calculator-suite
sudo systemctl start calculator-suite
```

## 🌐 Nginx Configuration

### 1. SSL Certificate Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com
```

### 2. Nginx Configuration
```nginx
# /etc/nginx/sites-available/calculator-suite
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;

    # Security Headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'";

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=web:10m rate=2r/s;

    # Main Application
    location / {
        limit_req zone=web burst=5 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # API Rate Limiting
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static Files (if separated)
    location /static/ {
        alias /var/www/calculator-suite/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health Check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

### 3. Enable Site
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/calculator-suite /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📊 Monitoring Setup

### 1. Application Monitoring
```python
# Add to app_simple_fixed.py for production monitoring
import logging
from logging.handlers import RotatingFileHandler
import time
from functools import wraps

# Configure logging
if not app.debug:
    file_handler = RotatingFileHandler('/var/log/calculator-suite/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

# Performance monitoring decorator
def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        if execution_time > 1.0:  # Log slow requests
            app.logger.warning(f'Slow request: {func.__name__} took {execution_time:.2f}s')
        
        return result
    return wrapper
```

### 2. System Monitoring (Prometheus + Grafana)
```yaml
# monitoring/docker-compose.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

  node_exporter:
    image: prom/node-exporter
    ports:
      - "9100:9100"

volumes:
  prometheus_data:
  grafana_data:
```

### 3. Log Management
```bash
# Configure logrotate
sudo cat > /etc/logrotate.d/calculator-suite << EOF
/var/log/calculator-suite/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 calculator calculator
    postrotate
        systemctl reload calculator-suite
    endscript
}
EOF
```

## 🔧 Performance Optimization

### 1. Caching Implementation
```python
# Redis caching for expensive calculations
import redis
import json
import hashlib

redis_client = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'))

def cache_calculation(ttl=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function arguments
            cache_key = f"calc:{func.__name__}:{hashlib.md5(json.dumps(kwargs, sort_keys=True).encode()).hexdigest()}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Calculate and cache result
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### 2. Database Optimization
```sql
-- Database indexes for common queries
CREATE INDEX idx_calculation_logs_calculator ON calculation_logs(calculator);
CREATE INDEX idx_calculation_logs_timestamp ON calculation_logs(timestamp);
CREATE INDEX idx_calculation_logs_ip ON calculation_logs(ip_address);

-- Partitioning for large tables
CREATE TABLE calculation_logs_y2024m01 PARTITION OF calculation_logs
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

### 3. CDN Setup (Cloudflare)
```bash
# Configure Cloudflare caching rules
# Cache static content for 1 year
# Cache API responses for 5 minutes
# Cache calculator pages for 1 hour
```

## 🔐 Security Configuration

### 1. Application Security
```python
# Security enhancements for production
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

# Rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Security headers
Talisman(app, force_https=True)

# CSRF protection
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = None
```

### 2. Firewall Configuration
```bash
# UFW firewall setup
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. Security Monitoring
```bash
# Install fail2ban
sudo apt install fail2ban

# Configure fail2ban for nginx
sudo cat > /etc/fail2ban/jail.local << EOF
[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
EOF
```

## 🔄 Backup Strategy

### 1. Database Backup
```bash
#!/bin/bash
# backup.sh - Daily database backup script

BACKUP_DIR="/var/backups/calculator-suite"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
pg_dump calculator_suite | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Backup application files
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz /var/www/calculator-suite --exclude=venv

# Clean old backups (keep 30 days)
find $BACKUP_DIR -type f -mtime +30 -delete

# Upload to S3 (optional)
# aws s3 cp $BACKUP_DIR/db_backup_$DATE.sql.gz s3://your-backup-bucket/
```

### 2. Automated Backup Schedule
```bash
# Add to crontab
0 2 * * * /usr/local/bin/backup.sh >> /var/log/backup.log 2>&1
```

## 📈 Scaling Strategies

### 1. Horizontal Scaling (Load Balancer)
```nginx
# Load balancer configuration
upstream calculator_app {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
}

server {
    location / {
        proxy_pass http://calculator_app;
        # ... other configuration
    }
}
```

### 2. Container Orchestration (Kubernetes)
```yaml
# k8s-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: calculator-suite
spec:
  replicas: 3
  selector:
    matchLabels:
      app: calculator-suite
  template:
    metadata:
      labels:
        app: calculator-suite
    spec:
      containers:
      - name: calculator-suite
        image: calculator-suite:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## 🚨 Troubleshooting

### Common Issues

1. **High Memory Usage**
   ```bash
   # Check memory usage
   free -h
   # Check application memory
   ps aux | grep gunicorn
   # Restart if needed
   sudo systemctl restart calculator-suite
   ```

2. **Database Connection Issues**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   # Check connections
   sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
   ```

3. **SSL Certificate Renewal**
   ```bash
   # Renew certificates
   sudo certbot renew --dry-run
   # Auto-renewal check
   sudo systemctl status certbot.timer
   ```

### Health Checks
```bash
# Application health
curl -f http://localhost:5000/health

# Database health
pg_isready -h localhost -p 5432

# Redis health
redis-cli ping
```

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Environment variables configured
- [ ] SSL certificates obtained
- [ ] Database migrations completed
- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] Security hardening applied

### Post-Deployment
- [ ] Health checks passing
- [ ] Performance metrics within targets
- [ ] Security scan completed
- [ ] Backup verification
- [ ] Documentation updated
- [ ] Team notification sent

---

**Deployment Status:** ✅ Ready for Production  
**Security Level:** High  
**Scalability:** Horizontal scaling ready  
**Monitoring:** Comprehensive coverage