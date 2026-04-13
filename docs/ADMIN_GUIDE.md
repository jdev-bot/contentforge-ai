# ContentForge AI - Admin Guide

> Deployment, configuration, and operational documentation

---

## Table of Contents

1. [Deployment Guide](#deployment-guide)
2. [Configuration](#configuration)
3. [Monitoring](#monitoring)
4. [Troubleshooting](#troubleshooting)
5. [Security](#security)
6. [Maintenance](#maintenance)

---

## Deployment Guide

### Prerequisites

**Required Accounts:**
- Vercel account (for frontend)
- Render account (for backend)
- Supabase account (database + auth)
- Cloudflare account (R2 storage)

**Required API Keys:**
- Groq API key (AI generation)
- Resend API key (email)
- Stripe API keys (payments)

**Development Tools:**
- Node.js 18+ (frontend)
- Python 3.11+ (backend)
- Git
- Docker (optional)

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                         Vercel                          │
│                    Next.js Frontend                     │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                         Render                          │
│  ┌──────────────┐  ┌──────────┐  ┌────────────────┐  │
│  │  FastAPI     │  │  Celery  │  │  Redis Queue   │  │
│  │  API Server  │  │  Worker  │  │  Scheduler     │  │
│  └──────────────┘  └──────────┘  └────────────────┘  │
└─────────────────────────┬───────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐   ┌──────────┐    ┌──────────────┐
│   Supabase   │   │   Groq   │    │ Cloudflare   │
│  PostgreSQL  │   │   API    │    │     R2       │
│     Auth     │   │          │    │   Storage    │
└──────────────┘   └──────────┘    └──────────────┘
```

### Backend Deployment (Render)

#### Option 1: Blueprint Deployment (Recommended)

1. Fork the ContentForge AI repository
2. Go to [Render Dashboard](https://dashboard.render.com/blueprints)
3. Click **"New Blueprint Instance"**
4. Connect your GitHub repository
5. Render reads `render.yaml` and creates:
   - Web Service (FastAPI)
   - Worker (Celery)
   - Redis (Queue)
   - Scheduler (Cron)

#### Option 2: Manual Service Creation

**Create Web Service:**

1. Go to Render Dashboard > New > Web Service
2. Connect repository
3. Configure:

```yaml
Name: contentforge-ai-api
Runtime: Docker
Dockerfile Path: ./infra/docker/Dockerfile.backend
Port: 8000
```

4. Add environment variables (see [Environment Variables](#environment-variables))
5. Create service

**Create Worker:**

1. New > Background Worker
2. Same repository
3. Configure:

```yaml
Name: contentforge-ai-worker
Runtime: Docker
Dockerfile Path: ./infra/docker/Dockerfile.backend
Start Command: celery -A app.core.celery_app worker --loglevel=info
```

**Create Redis:**

1. New > Redis
2. Name: `contentforge-ai-redis`
3. Create and copy connection URL

### Frontend Deployment (Vercel)

#### Option 1: Git Integration

1. Push code to GitHub
2. Go to [Vercel Dashboard](https://vercel.com)
3. Import project
4. Configure:

```
Framework: Next.js
Root Directory: src/frontend
Build Command: npm run build
Output Directory: .next
```

5. Add environment variables
6. Deploy

#### Option 2: CLI Deployment

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

#### Option 3: Deploy Script

```bash
# From project root
./scripts/deploy-frontend.sh

# Production
./scripts/deploy-frontend.sh --prod
```

### Database Setup (Supabase)

#### Create Project

1. Go to [Supabase](https://supabase.com)
2. Create new project
3. Choose region closest to users
4. Save database password securely

#### Run Migrations

```bash
# Connect to Supabase
psql "postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres" -f src/backend/supabase/migrations/001_initial_schema.sql
```

Or use Supabase Dashboard > SQL Editor

#### Configure Auth

1. Go to Authentication > Settings
2. Configure:
   - Site URL: Your frontend URL
   - Redirect URLs: `https://your-app.com/auth/callback`
3. Enable email provider
4. Configure email templates (optional)

#### Get API Keys

1. Go to Project Settings > API
2. Copy:
   - Project URL
   - `anon` public key
   - `service_role` secret key

### Storage Setup (Cloudflare R2)

#### Create Bucket

1. Go to Cloudflare Dashboard > R2
2. Create bucket: `contentforge-uploads`
3. Configure CORS:

```json
[
  {
    "AllowedOrigins": ["https://your-app.com"],
    "AllowedMethods": ["GET", "PUT", "POST"],
    "AllowedHeaders": ["*"]
  }
]
```

#### Create API Token

1. Go to My Profile > API Tokens
2. Create token with R2 permissions
3. Save:
   - Access Key ID
   - Secret Access Key
   - Endpoint URL
   - Bucket name

---

## Configuration

### Environment Variables

#### Backend (.env.production)

```bash
# Application
APP_NAME=ContentForge AI
APP_ENV=production
DEBUG=false

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Groq (AI)
GROQ_API_KEY=gsk_your_api_key

# Redis (Celery)
REDIS_URL=redis://redis:6379/0

# Cloudflare R2
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_ENDPOINT_URL=https://your-account.r2.cloudflarestorage.com
R2_BUCKET_NAME=contentforge-uploads

# Email (Resend)
RESEND_API_KEY=re_your_api_key
FROM_EMAIL=noreply@contentforge.ai

# Stripe (Payments)
STRIPE_SECRET_KEY=sk_live_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_secret

# Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100/hour

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

#### Frontend (.env.local)

```bash
# API
NEXT_PUBLIC_API_URL=https://contentforge-ai-api.onrender.com
NEXT_PUBLIC_API_VERSION=v1

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# Stripe
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_your_key
```

### Database Configuration

#### Connection Pooling

Supabase automatically handles connection pooling. For self-hosted PostgreSQL:

```python
# Add to database connection
pool_size=20
max_overflow=10
pool_pre_ping=True
```

#### Backup Strategy

**Daily Backups:**
- Supabase: Automated daily backups
- Point-in-time recovery enabled
- Test restore monthly

**Manual Backup:**
```bash
pg_dump "postgresql://user:pass@host/db" > backup.sql
```

### Celery Configuration

#### Worker Options

```bash
# Standard worker
celery -A app.core.celery_app worker --loglevel=info --concurrency=4

# With auto-reload (development)
celery -A app.core.celery_app worker --loglevel=info --autoreload

# Beat scheduler
celery -A app.core.celery_app beat --loglevel=info
```

#### Task Routing

```python
# Prioritize queues
task_routes = {
    'app.tasks.email.*': {'queue': 'email'},
    'app.tasks.rss.*': {'queue': 'rss'},
    'app.tasks.competitors.*': {'queue': 'analysis'},
}
```

---

## Monitoring

### Application Monitoring

#### Health Checks

**Endpoint:** `GET /api/v1/health`

```json
{
  "status": "healthy",
  "timestamp": "2026-04-13T10:00:00Z",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "redis": "connected",
    "ai_service": "connected"
  }
}
```

#### Metrics to Monitor

| Metric | Warning Threshold | Critical Threshold |
|--------|-------------------|---------------------|
| Response Time | >500ms | >2000ms |
| Error Rate | >1% | >5% |
| Queue Depth | >100 | >500 |
| CPU Usage | >70% | >90% |
| Memory Usage | >80% | >95% |
| DB Connections | >80% | >95% |

### Logging

#### Log Levels

```python
# Production
LOG_LEVEL=INFO

# Development
LOG_LEVEL=DEBUG
```

#### Log Format

```python
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

#### Log Aggregation

Recommended tools:
- Datadog
- Splunk
- ELK Stack
- Papertrail (Render)

### Alerting

#### Configure Alerts

**Uptime Monitoring:**
- Ping health endpoint every minute
- Alert if down >2 minutes
- Check from multiple regions

**Performance Alerts:**
```yaml
Alert: High Response Time
Condition: p95 response time > 1000ms for 5 minutes
Action: Send Slack notification, page on-call

Alert: High Error Rate
Condition: Error rate > 2% for 2 minutes
Action: Send email to dev team
```

### Monitoring Tools

#### Recommended Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| APM | Datadog / New Relic | Performance monitoring |
| Logs | Papertrail / LogDNA | Log aggregation |
| Errors | Sentry | Error tracking |
| Uptime | Pingdom / UptimeRobot | Availability monitoring |
| DB | Supabase Dashboard | Query performance |

---

## Troubleshooting

### Common Issues

#### API Returns 500 Errors

**Check:**
1. Database connection
2. Redis connection
3. Supabase service status
4. Recent deployments

**Commands:**
```bash
# Check database connectivity
python -c "from app.core.supabase import get_supabase_client; print('OK')"

# Check Redis
celery -A app.core.celery_app inspect ping

# View logs
render logs --service contentforge-ai-api --tail
```

#### Slow Response Times

**Investigate:**
1. Database query performance
2. Slow API calls (Groq, etc.)
3. Redis queue backup
4. Resource constraints

**Fixes:**
```bash
# Check slow queries in Supabase Dashboard
# Add database indexes for common queries
# Scale up Redis/Worker instances
```

#### Queue Backlog

**Symptom:** Tasks not processing

**Solutions:**
1. Scale workers horizontally
2. Increase worker concurrency
3. Check for stuck tasks
4. Restart workers

```bash
# Check queue depth
celery -A app.core.celery_app inspect active
celery -A app.core.celery_app inspect scheduled
celery -A app.core.celery_app inspect reserved

# Purge queue (careful!)
celery -A app.core.celery_app purge
```

#### Authentication Failures

**Check:**
1. Supabase auth settings
2. JWT secret matches
3. Token expiry configuration
4. CORS settings

#### Rate Limiting

**Symptoms:** 429 errors

**Solutions:**
1. Check rate limit configuration
2. Review usage patterns
3. Adjust limits if needed
4. Implement client-side backoff

### Debug Mode

Enable debug logging:

```python
# In environment
DEBUG=true
LOG_LEVEL=DEBUG
```

---

## Security

### Authentication Security

#### JWT Configuration

```python
# Strong secret
SECRET_KEY = secrets.token_urlsafe(32)

# Reasonable expiry
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Algorithm
ALGORITHM = "HS256"
```

#### API Security

```python
# CORS origins
cors_origins = ["https://your-app.com"]

# Rate limiting
rate_limit = "100/hour"

# Request validation
max_request_size = "10MB"
```

### Data Security

#### Encryption

- At rest: Supabase encrypts data
- In transit: HTTPS/TLS 1.3
- Secrets: Environment variables only

#### Access Control

```python
# Database row-level security
enable_rls = True

# API endpoint authentication
require_auth = True
```

#### Audit Logging

Log security events:
- Login attempts
- Permission changes
- Data exports
- Failed access attempts

### Compliance

#### GDPR Considerations

- User data export
- Right to deletion
- Consent management
- Data processing agreements

#### Security Checklist

- [ ] HTTPS enforced
- [ ] Secure headers configured
- [ ] Rate limiting enabled
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF tokens
- [ ] Security headers
- [ ] Dependency scanning
- [ ] Regular security audits

---

## Maintenance

### Regular Tasks

#### Daily

- [ ] Check error logs
- [ ] Review failed jobs
- [ ] Monitor queue depth
- [ ] Check disk space

#### Weekly

- [ ] Review performance metrics
- [ ] Check database size
- [ ] Verify backup completion
- [ ] Update dependencies (review)

#### Monthly

- [ ] Security updates
- [ ] Dependency updates
- [ ] Performance review
- [ ] Cost optimization
- [ ] Access review

#### Quarterly

- [ ] Disaster recovery test
- [ ] Security audit
- [ ] Architecture review
- [ ] Documentation updates

### Updates

#### Updating Dependencies

```bash
# Backend
pip install -r requirements.txt --upgrade

# Frontend
npm update

# Test
pytest
npm test

# Deploy
# Follow deployment process
```

#### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback (if needed)
alembic downgrade -1
```

### Scaling

#### Horizontal Scaling

- Add more API instances
- Increase worker count
- Add read replicas
- Use CDN for static assets

#### Vertical Scaling

- Upgrade instance sizes
- Increase memory
- More CPU cores
- Faster storage

#### Database Scaling

```sql
-- Add indexes
CREATE INDEX CONCURRENTLY idx_content_user_id ON content(user_id);

-- Partition large tables
-- Consider read replicas
```

---

## Support

### Getting Help

- **Documentation**: https://docs.contentforge.ai
- **Status Page**: https://status.contentforge.ai
- **Email**: support@contentforge.ai
- **Emergency**: ops@contentforge.ai

### On-Call Procedures

1. Acknowledge alert
2. Assess severity
3. Follow runbook
4. Escalate if needed
5. Document resolution

### Incident Response

1. Detect → Alert fires
2. Assess → Determine impact
3. Mitigate → Fix immediate issue
4. Resolve → Restore service
5. Review → Post-mortem

---

**Document Version**: 1.0.0  
**Last Updated**: 2026-04-13
