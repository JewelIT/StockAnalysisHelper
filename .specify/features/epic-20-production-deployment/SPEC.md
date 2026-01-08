# Epic 20: Production Deployment & Infrastructure

**Epic ID**: Epic 20  
**Status**: PLANNED  
**Priority**: P0 (Critical - Production readiness)  
**Dependencies**: Epic 1 (Auth), Epic 2 (Security), Epic 7 (Resilience), Epic 18 (Monitoring)  
**Estimated Effort**: 3-4 weeks  
**Business Value**: Enable production launch, ensure scalability and reliability

---

## 📋 Overview

### Problem Statement
The application currently runs on Flask development server, which is unsuitable for production. No production-grade WSGI server, no reverse proxy, no database optimization, no containerization strategy, and no CI/CD pipeline.

**Current State:**
- Flask development server (`python run.py`)
- SQLite database (not suitable for multi-user production)
- No reverse proxy (Nginx/Apache)
- No process management (systemd/supervisor)
- No environment-based configuration
- Manual deployment process
- No SSL/TLS termination
- No load balancing

**Desired State:**
- Gunicorn WSGI server with multiple workers
- PostgreSQL database (ACID-compliant, concurrent access)
- Nginx reverse proxy with SSL/TLS
- Systemd service for process management
- Environment-based configuration (dev/staging/prod)
- Automated CI/CD pipeline (GitHub Actions)
- Docker containerization
- Horizontal scalability (multiple app instances)

### Business Impact
- **Reliability**: 99.9% uptime SLA
- **Scalability**: Support 1000+ concurrent users
- **Security**: HTTPS, secure headers, firewall rules
- **Speed**: Faster deployments (manual → automated CI/CD)

---

## 🎯 User Stories

### **US20.1: As a developer, I want to deploy the app with a production WSGI server** ⭐ P0
**Priority**: P0 (Must-have)  
**Effort**: 3 days  
**Business Value**: Production-grade performance and stability

**Acceptance Criteria:**
1. Gunicorn replaces Flask development server
2. Gunicorn configured with 4 worker processes (adjustable)
3. Worker class: sync (default) or gevent for async
4. Timeout: 30 seconds (prevents hung workers)
5. Graceful restart: workers reload without downtime
6. Systemd service manages Gunicorn process
7. Auto-restart on failure

**Technical Notes:**
- Worker count formula: `(2 x $num_cores) + 1`
- Use gevent workers for I/O-bound tasks (API calls)
- Enable access logging to `/var/log/vestor/access.log`
- Enable error logging to `/var/log/vestor/error.log`

**Example gunicorn.conf.py:**
```python
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"  # Async worker for API calls
timeout = 30
keepalive = 2
errorlog = "/var/log/vestor/gunicorn-error.log"
accesslog = "/var/log/vestor/gunicorn-access.log"
loglevel = "info"
```

**Systemd Service (vestor.service):**
```ini
[Unit]
Description=Vestor Stock Analysis App
After=network.target

[Service]
User=vestor
Group=vestor
WorkingDirectory=/opt/vestor
Environment="PATH=/opt/vestor/venv/bin"
ExecStart=/opt/vestor/venv/bin/gunicorn -c gunicorn.conf.py run:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

### **US20.2: As a developer, I want to use PostgreSQL for production** ⭐ P0
**Priority**: P0 (Must-have)  
**Effort**: 4 days  
**Business Value**: Support concurrent users, data integrity

**Acceptance Criteria:**
1. PostgreSQL database replaces SQLite in production
2. Database connection pooling configured (max 20 connections)
3. Database migrations automated (Alembic or Flask-Migrate)
4. Database backups scheduled daily (pg_dump)
5. Read replicas for analytics queries (stretch goal)
6. Database credentials stored in environment variables
7. Connection retry logic on failure

**Technical Notes:**
- Use SQLAlchemy with PostgreSQL adapter (`psycopg2`)
- Enable connection pooling: `pool_size=10, max_overflow=10`
- Backup strategy: Daily full backup + hourly incremental (pg_basebackup)
- Restore testing: Monthly restore drills

**Database Configuration:**
```python
# config.py
import os

class ProductionConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://vestor:password@localhost/vestor_prod'
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 10,
        'pool_recycle': 3600,  # Recycle connections every hour
        'pool_pre_ping': True  # Test connections before use
    }
```

**Migration Commands:**
```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Add users table"

# Apply migration
flask db upgrade

# Rollback
flask db downgrade
```

---

### **US20.3: As a developer, I want Nginx as a reverse proxy** ⭐ P0
**Priority**: P0 (Must-have)  
**Effort**: 2 days  
**Business Value**: SSL termination, static file serving, load balancing

**Acceptance Criteria:**
1. Nginx proxies requests to Gunicorn (127.0.0.1:8000)
2. Nginx serves static files directly (faster than app server)
3. SSL/TLS enabled with Let's Encrypt certificate
4. HTTP → HTTPS redirect enforced
5. Security headers configured (CSP, HSTS, X-Frame-Options)
6. Gzip compression enabled for responses
7. Rate limiting configured (100 req/min per IP)

**Nginx Configuration:**
```nginx
upstream vestor_app {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name vestor.ai www.vestor.ai;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name vestor.ai www.vestor.ai;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/vestor.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vestor.ai/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'" always;

    # Gzip Compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
    limit_req zone=api burst=20;

    # Static Files
    location /static/ {
        alias /opt/vestor/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://vestor_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

---

### **US20.4: As a developer, I want environment-based configuration** ⭐ P1
**Priority**: P1 (High)  
**Effort**: 2 days  
**Business Value**: Separate dev/staging/prod configs, improve security

**Acceptance Criteria:**
1. Configuration loaded from environment variables
2. Default values for development environment
3. Separate configs for dev, staging, production
4. Secrets loaded from `.env` file (never committed)
5. Configuration validation on startup (fail fast if missing required vars)
6. Support for environment-specific feature flags

**Environment Variables:**
```bash
# .env.production (not committed to git)
FLASK_ENV=production
SECRET_KEY=<random-secret-key>
DATABASE_URL=postgresql://vestor:password@db.vestor.ai/vestor_prod
REDIS_URL=redis://localhost:6379/0
STRIPE_SECRET_KEY=sk_live_...
SENTRY_DSN=https://...@sentry.io/...
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<sendgrid-api-key>
```

**Configuration Classes:**
```python
# config.py
import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    
    def __init__(self):
        # Validate required env vars
        required = ['DATABASE_URL', 'SECRET_KEY', 'STRIPE_SECRET_KEY']
        missing = [var for var in required if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required env vars: {missing}")

# Load config based on FLASK_ENV
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
```

---

### **US20.5: As a developer, I want automated CI/CD pipeline** ⭐ P1
**Priority**: P1 (High)  
**Effort**: 4 days  
**Business Value**: Faster deployments, reduce human error

**Acceptance Criteria:**
1. GitHub Actions workflow runs on every push to main
2. CI pipeline: lint (flake8), test (pytest), security scan (bandit)
3. CD pipeline: build Docker image, push to registry, deploy to production
4. Automated database migrations run before deployment
5. Rollback mechanism if deployment fails
6. Slack notification on deployment success/failure
7. Deployment approvals for production (manual gate)

**GitHub Actions Workflow:**
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install flake8 pytest bandit
      - name: Lint
        run: flake8 src/
      - name: Security scan
        run: bandit -r src/
      - name: Run tests
        run: pytest tests/ --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t vestor:${{ github.sha }} .
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker tag vestor:${{ github.sha }} vestor/vestor:latest
          docker push vestor/vestor:latest
      - name: Deploy to production
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/vestor
            docker-compose pull
            docker-compose up -d
            docker-compose exec -T web flask db upgrade
      - name: Notify Slack
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Deployment to production ${{ job.status }}'
        if: always()
```

---

## 🔧 Functional Requirements

### WSGI Server
1. **Gunicorn**: Production WSGI server with gevent workers
2. **Worker Count**: `(2 x CPU cores) + 1`
3. **Timeout**: 30 seconds per request
4. **Graceful Restart**: Zero-downtime deployments
5. **Logging**: Access and error logs to `/var/log/vestor/`

### Database
6. **PostgreSQL**: Production database with connection pooling
7. **Migrations**: Automated schema changes via Alembic
8. **Backups**: Daily full backups, 30-day retention
9. **Restore Testing**: Monthly restore drills
10. **Read Replicas**: For analytics queries (stretch goal)

### Reverse Proxy
11. **Nginx**: SSL termination, static file serving, load balancing
12. **HTTPS**: Let's Encrypt SSL certificate with auto-renewal
13. **Security Headers**: HSTS, CSP, X-Frame-Options
14. **Rate Limiting**: 100 req/min per IP
15. **Gzip Compression**: For all text-based responses

### Configuration
16. **Environment Variables**: All secrets in env vars, never hardcoded
17. **Config Classes**: Separate configs for dev, staging, prod
18. **Validation**: Fail fast on missing required env vars
19. **Feature Flags**: Environment-specific feature toggles

### CI/CD
20. **Automated Testing**: Run tests on every PR
21. **Security Scanning**: bandit + safety checks
22. **Automated Deployment**: Deploy to production on main branch merge
23. **Database Migrations**: Auto-run migrations before deployment
24. **Rollback**: Automated rollback on deployment failure
25. **Notifications**: Slack alerts on deployment events

---

## 🏗️ Non-Functional Requirements

### Performance
1. **Response Time**: P95 latency <2 seconds
2. **Concurrency**: Support 1000+ concurrent users
3. **Static Assets**: Served with 1-year cache headers
4. **Database Queries**: Connection pooling prevents exhaustion

### Reliability
5. **Uptime**: 99.9% SLA (43 minutes downtime/month max)
6. **Auto-Restart**: Systemd restarts crashed processes
7. **Health Checks**: `/health` endpoint for load balancer
8. **Graceful Shutdown**: Workers finish current requests before restart

### Security
9. **HTTPS Only**: HTTP → HTTPS redirect enforced
10. **TLS 1.2+**: Modern TLS protocols only
11. **Security Headers**: HSTS, CSP, X-Frame-Options
12. **Firewall**: Only ports 80, 443 open to internet

### Scalability
13. **Horizontal Scaling**: Add app instances behind load balancer
14. **Database Scaling**: PostgreSQL read replicas for analytics
15. **Caching**: Redis for session storage and API response cache
16. **CDN**: Serve static assets via CDN (Cloudflare, AWS CloudFront)

### Compliance
17. **Data Residency**: Database hosted in US/EU (GDPR compliance)
18. **Backup Encryption**: Backups encrypted at rest
19. **Audit Logging**: All deployments and config changes logged

---

## 🧪 Testing Requirements

### Infrastructure Tests
- Test Gunicorn can start and handle requests
- Test Nginx proxies requests correctly
- Test SSL certificate is valid and auto-renews
- Test database migrations apply successfully

### Load Tests
- 1000 concurrent users (Locust or k6)
- Verify P95 latency <2 seconds under load
- Verify no connection pool exhaustion
- Verify Nginx rate limiting works

### Disaster Recovery Tests
- Test database backup restore
- Test rollback deployment
- Test systemd auto-restart on crash
- Test graceful shutdown (no dropped requests)

### Security Tests
- Test HTTPS redirect works
- Test security headers present
- Test rate limiting prevents abuse
- Test firewall rules block unauthorized ports

---

## 📊 Success Metrics

### Reliability
- **Uptime**: 99.9% (target: 43 minutes downtime/month max)
- **MTTR**: <15 minutes (mean time to recovery)
- **Failed Deployments**: <1% of deployments fail

### Performance
- **Response Time**: P95 <2 seconds
- **Concurrent Users**: Support 1000+ users
- **Database Connections**: No pool exhaustion

### Deployment Efficiency
- **Deployment Frequency**: Daily (or on-demand)
- **Deployment Time**: <5 minutes (build → deploy)
- **Rollback Time**: <2 minutes

---

## 🔗 Dependencies

### Infrastructure
- **Server**: Ubuntu 22.04 LTS (4 CPU, 8GB RAM minimum)
- **Domain**: vestor.ai (DNS configured)
- **SSL**: Let's Encrypt certificate (certbot)

### Software
- **WSGI Server**: Gunicorn 20.1+
- **Reverse Proxy**: Nginx 1.22+
- **Database**: PostgreSQL 14+
- **Process Manager**: systemd (built into Ubuntu)
- **Python**: 3.10+

### Services
- **Docker Registry**: Docker Hub or GitHub Container Registry
- **CI/CD**: GitHub Actions (free for public repos)
- **Monitoring**: Sentry, Prometheus, Grafana (from Epic 18)

---

## 🚀 Implementation Phases

### Phase 1: WSGI Server & Process Management (Week 1)
- Install and configure Gunicorn
- Create systemd service for Gunicorn
- Test graceful restart and auto-recovery
- Configure logging

### Phase 2: Database Migration (Week 1-2)
- Install PostgreSQL
- Create production database and user
- Migrate data from SQLite to PostgreSQL
- Test database backups and restore
- Configure connection pooling

### Phase 3: Nginx & SSL (Week 2)
- Install and configure Nginx
- Obtain Let's Encrypt SSL certificate
- Configure HTTPS redirect and security headers
- Test static file serving and rate limiting

### Phase 4: Configuration & Secrets (Week 2)
- Implement environment-based configuration
- Move secrets to `.env` file
- Test config validation on startup
- Document required environment variables

### Phase 5: CI/CD Pipeline (Week 3)
- Create GitHub Actions workflow
- Implement automated testing (lint, test, security scan)
- Implement automated deployment
- Test rollback mechanism
- Configure Slack notifications

### Phase 6: Load Testing & Optimization (Week 3-4)
- Run load tests (1000 concurrent users)
- Optimize database queries
- Tune Gunicorn worker count
- Configure CDN for static assets
- Final security audit

---

## 🎯 Definition of Done

### Infrastructure Complete
- [ ] Gunicorn WSGI server running with 4+ workers
- [ ] PostgreSQL database with connection pooling
- [ ] Nginx reverse proxy with SSL/TLS
- [ ] Systemd service manages app process
- [ ] Firewall configured (only 80, 443 open)

### Configuration Complete
- [ ] Environment variables for all secrets
- [ ] Separate configs for dev/staging/prod
- [ ] Config validation on startup
- [ ] Documentation for required env vars

### CI/CD Complete
- [ ] GitHub Actions workflow runs on every push
- [ ] Automated testing (lint, test, security)
- [ ] Automated deployment to production
- [ ] Database migrations auto-applied
- [ ] Rollback mechanism tested

### Testing Complete
- [ ] Load tests pass (1000 concurrent users)
- [ ] P95 latency <2 seconds under load
- [ ] Database backup/restore tested
- [ ] Security audit passed

### Documentation Complete
- [ ] Deployment guide (step-by-step)
- [ ] Environment variable reference
- [ ] Disaster recovery playbook
- [ ] Rollback procedure documented

---

## 🚧 Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Database migration data loss | CRITICAL | Test migration on staging first, full backup before prod |
| SSL certificate expiry | HIGH | Automated renewal via certbot cron job, monitoring alerts |
| Deployment downtime | MEDIUM | Graceful restart, blue-green deployment strategy |
| CI/CD pipeline failure | MEDIUM | Rollback mechanism, manual deployment fallback |
| PostgreSQL connection exhaustion | MEDIUM | Connection pooling, monitor pool usage |
| Let's Encrypt rate limits | LOW | Obtain cert in staging first, use DNS challenge for retries |

---

## 📚 Resources

### Documentation
- [Gunicorn Deployment](https://docs.gunicorn.org/en/stable/deploy.html)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Nginx SSL Configuration](https://nginx.org/en/docs/http/configuring_https_servers.html)
- [Flask Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)

### Tutorials
- [Deploying Flask with Gunicorn and Nginx](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-22-04)
- [GitHub Actions for Python](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)
- [Let's Encrypt with Nginx](https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal)

---

**Epic Status**: PLANNED  
**Next Step**: Complete Epic 1-2-7-18, then begin infrastructure setup  
**Owner**: TBD  
**Last Updated**: 2026-01-08