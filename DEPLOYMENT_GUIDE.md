# Deployment Guide

Guide for deploying the ERP System to production environments.

## 📋 Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations up to date
- [ ] SSL certificates obtained
- [ ] Backup strategy in place
- [ ] Monitoring tools configured
- [ ] Security audit completed
- [ ] Performance testing done

## 🚀 Backend Deployment

### Option 1: Deploy on Ubuntu Server with Nginx

#### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+
sudo apt install python3.10 python3.10-venv python3-pip -y

# Install MySQL
sudo apt install mysql-server -y
sudo mysql_secure_installation

# Install Nginx
sudo apt install nginx -y

# Install supervisor (for process management)
sudo apt install supervisor -y
```

#### 2. Setup Application

```bash
# Create application directory
sudo mkdir -p /var/www/erp-backend
cd /var/www/erp-backend

# Clone repository
git clone <your-repo-url> .

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn  # Production server
```

#### 3. Configure Environment

```bash
# Create production .env file
nano .env
```

```env
DATABASE_URL=mysql+pymysql://erp_user:secure_password@localhost:3306/erp_db
SECRET_KEY=your-super-secure-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DEBUG=False
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

#### 4. Setup Database

```bash
# Login to MySQL
sudo mysql -u root -p

# Create database and user
CREATE DATABASE erp_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'erp_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON erp_db.* TO 'erp_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Run migrations
source venv/bin/activate
alembic upgrade head

# Seed database (optional)
python seeds/seed_data.py
```

#### 5. Configure Supervisor

Create supervisor config: `/etc/supervisor/conf.d/erp-backend.conf`

```ini
[program:erp-backend]
directory=/var/www/erp-backend
command=/var/www/erp-backend/venv/bin/gunicorn main_new:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/erp-backend.log
stderr_logfile=/var/log/erp-backend-error.log
environment=PATH="/var/www/erp-backend/venv/bin"
```

Start application:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start erp-backend
sudo supervisorctl status erp-backend
```

#### 6. Configure Nginx

Create Nginx config: `/etc/nginx/sites-available/erp-backend`

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files (if any)
    location /static/ {
        alias /var/www/erp-backend/static/;
        expires 30d;
    }
    
    # Max upload size
    client_max_body_size 10M;
}
```

Enable site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/erp-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 7. Setup SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal (already setup by certbot)
sudo certbot renew --dry-run
```

### Option 2: Deploy with Docker

#### 1. Create Dockerfile

`backend/Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main_new:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Create docker-compose.yml

`docker-compose.yml`:
```yaml
version: '3.8'

services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: erp_db
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_USER: erp_user
      MYSQL_PASSWORD: secure_password
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: mysql+pymysql://erp_user:secure_password@db:3306/erp_db
      SECRET_KEY: your-super-secure-secret-key
      ACCESS_TOKEN_EXPIRE_MINUTES: 1440
      DEBUG: "False"
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: gunicorn main_new:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  mysql_data:
```

#### 3. Deploy

```bash
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f backend

# Run migrations
docker-compose exec backend alembic upgrade head

# Seed database
docker-compose exec backend python seeds/seed_data.py
```

### Option 3: Deploy on Cloud Platform (AWS/GCP/Azure)

#### AWS Elastic Beanstalk

1. Install EB CLI:
```bash
pip install awsebcli
```

2. Initialize EB application:
```bash
cd backend
eb init -p python-3.10 erp-backend
```

3. Create environment:
```bash
eb create erp-production
```

4. Deploy:
```bash
eb deploy
```

#### Google Cloud Platform (Cloud Run)

1. Create `Procfile`:
```
web: gunicorn main_new:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. Deploy:
```bash
gcloud run deploy erp-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🎨 Frontend Deployment

### Option 1: Nginx Static Hosting

```bash
# Build production bundle
cd frontend
npm run build

# Copy to web server
sudo cp -r dist/* /var/www/html/

# Nginx config for React Router
server {
    listen 80;
    server_name yourdomain.com;
    root /var/www/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### Option 2: Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel --prod
```

### Option 3: Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd frontend
netlify deploy --prod --dir=dist
```

### Option 4: Docker

`frontend/Dockerfile`:
```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

`frontend/nginx.conf`:
```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:8000;
    }
}
```

## 🔐 Security Hardening

### 1. Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 2. MySQL Security

```bash
# Disable remote root login
sudo mysql -u root -p

UPDATE mysql.user SET Host='localhost' WHERE User='root' AND Host='%';
DELETE FROM mysql.user WHERE User='';
FLUSH PRIVILEGES;
```

### 3. Environment Variables

Never commit `.env` file. Use secrets management:

**AWS Secrets Manager:**
```python
import boto3
import json

def get_secret():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='erp/production')
    return json.loads(response['SecretString'])
```

### 4. Regular Updates

```bash
# Setup automatic security updates
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

## 📊 Monitoring

### 1. Application Monitoring

Install monitoring tools:
```bash
pip install prometheus-client
pip install sentry-sdk
```

Add to application:
```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

### 2. Server Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop -y

# Check logs
sudo tail -f /var/log/erp-backend.log
sudo journalctl -u nginx -f
```

### 3. Database Monitoring

```sql
-- Check slow queries
SELECT * FROM mysql.slow_log;

-- Monitor connections
SHOW PROCESSLIST;
```

## 💾 Backup Strategy

### 1. Database Backup

Create backup script: `/opt/scripts/backup-db.sh`

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="erp_db_$DATE.sql"

mkdir -p $BACKUP_DIR

mysqldump -u erp_user -p'secure_password' erp_db > "$BACKUP_DIR/$FILENAME"

# Compress
gzip "$BACKUP_DIR/$FILENAME"

# Keep only last 7 days
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: $FILENAME.gz"
```

Setup cron job:
```bash
sudo crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/scripts/backup-db.sh
```

### 2. Application Backup

```bash
# Backup application files
tar -czf erp-backend-$(date +%Y%m%d).tar.gz /var/www/erp-backend

# Upload to S3 (optional)
aws s3 cp erp-backend-$(date +%Y%m%d).tar.gz s3://your-backup-bucket/
```

## 🔄 Zero-Downtime Deployment

### Using Blue-Green Deployment

1. Setup two environments (blue and green)
2. Deploy to inactive environment
3. Test thoroughly
4. Switch traffic using load balancer
5. Keep old version for quick rollback

### Using Supervisor

```bash
# Update code
cd /var/www/erp-backend
git pull origin main

# Install new dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Restart gracefully
sudo supervisorctl restart erp-backend
```

## 📈 Performance Optimization

### 1. Enable Caching

```python
# Use Redis for caching
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)
```

### 2. Database Optimization

```sql
-- Add indexes
CREATE INDEX idx_attendance_student_date ON attendance(student_id, date);
CREATE INDEX idx_attendance_subject_date ON attendance(subject_id, date);

-- Analyze and optimize
ANALYZE TABLE attendance;
OPTIMIZE TABLE attendance;
```

### 3. Gunicorn Workers

```bash
# Calculate optimal workers: (2 * CPU cores) + 1
gunicorn main_new:app -w 9 -k uvicorn.workers.UvicornWorker
```

## 🚨 Troubleshooting

### Application won't start

```bash
# Check logs
sudo tail -f /var/log/erp-backend-error.log
sudo supervisorctl status

# Test manually
cd /var/www/erp-backend
source venv/bin/activate
uvicorn main_new:app --reload
```

### Database connection issues

```bash
# Test connection
mysql -u erp_user -p erp_db

# Check MySQL status
sudo systemctl status mysql

# View MySQL logs
sudo tail -f /var/log/mysql/error.log
```

### High memory usage

```bash
# Check processes
htop

# Restart application
sudo supervisorctl restart erp-backend

# Clear cache
redis-cli FLUSHALL
```

## ✅ Post-Deployment Checklist

- [ ] Application accessible via HTTPS
- [ ] Database connection working
- [ ] All endpoints responding correctly
- [ ] SSL certificate valid
- [ ] Backups running automatically
- [ ] Monitoring active
- [ ] Logs being collected
- [ ] Error tracking configured
- [ ] Performance acceptable
- [ ] Security headers present

---

**Production Deployment Complete! 🎉**

For any issues, check logs and monitoring dashboards.
