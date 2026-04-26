# ContentForge AI - Admin Guide

> Deployment, configuration, and operational documentation for administrators.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Deployment Guide](#deployment-guide)
3. [Configuration](#configuration)
4. [SSO / SAML Configuration](#sso--saml-configuration)
5. [Plugin Management](#plugin-management)
6. [Data Retention Policies](#data-retention-policies)
7. [SLA Monitoring Setup](#sla-monitoring-setup)
8. [Marketplace Management](#marketplace-management)
9. [Monitoring](#monitoring)
10. [Troubleshooting](#troubleshooting)
11. [Security](#security)
12. [Maintenance](#maintenance)

---

## System Requirements

### Current Production Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.13 | Backend runtime |
| Node.js | v22.22.2 | Frontend runtime |
| FastAPI | Latest | Backend API framework |
| Next.js | 14 | Frontend framework |
| AIService (provider-agnostic) | — | AI content generation |
| Supabase | — | PostgreSQL + Auth |
| Redis | — | Caching + Celery queue |

### Infrastructure

| Component | Platform | Notes |
|-----------|----------|-------|
| Frontend | Vercel | Next.js deployment |
| Backend API | Render | FastAPI web service |
| Workers | Render | Celery background workers |
| Redis | Render | Queue + caching |
| Database | Supabase | Managed PostgreSQL |
| Storage | Cloudflare R2 | File uploads |
| CI/CD | Self-hosted runner | srv1503460 |

### Resource Requirements

| Service | Min CPU | Min RAM | Storage |
|---------|---------|---------|---------|
| API Server | 1 vCPU | 512MB | 10GB |
| Celery Worker | 1 vCPU | 512MB | 10GB |
| Redis | — | 256MB | 1GB |
| Database | Supabase managed | — | — |

---

## Deployment Guide

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

#### Blueprint Deployment (Recommended)

1. Fork the ContentForge AI repository
2. Go to [Render Dashboard](https://dashboard.render.com/blueprints)
3. Click **"New Blueprint Instance"**
4. Connect your GitHub repository
5. Render reads `render.yaml` and creates all services

#### Manual Service Creation

**Web Service:**
```yaml
Name: contentforge-ai-api
Runtime: Docker
Dockerfile Path: ./infra/docker/Dockerfile.backend
Port: 8000
```

**Worker:**
```yaml
Name: contentforge-ai-worker
Runtime: Docker
Dockerfile Path: ./infra/docker/Dockerfile.backend
Start Command: celery -A app.core.celery_app worker --loglevel=info
```

**Redis:**
```yaml
Name: contentforge-ai-redis
```

### Frontend Deployment (Vercel)

1. Push code to GitHub
2. Import project in Vercel Dashboard
3. Configure:
   ```
   Framework: Next.js
   Root Directory: src/frontend
   Build Command: npm run build
   Output Directory: .next
   ```
4. Add environment variables
5. Deploy

### Database Setup (Supabase)

1. Create new Supabase project
2. Run migrations via SQL Editor or CLI
3. Configure authentication settings
4. Enable Row Level Security
5. Copy API keys (URL, anon key, service role key)

### Storage Setup (Cloudflare R2)

1. Create bucket: `contentforge-uploads`
2. Configure CORS for frontend domain
3. Create API token with R2 permissions
4. Save credentials (Access Key ID, Secret Access Key, Endpoint URL)

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

# Redis (Celery + Caching)
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

# SSO / SAML
SSO_ENABLED=true
SAML_ENABLED=true
SAML_SP_ENTITY_ID=contentforge-ai
SAML_SP_ACS_URL=https://your-api.onrender.com/api/v1/saml/acs
SAML_SP_METADATA_URL=https://your-api.onrender.com/api/v1/saml/metadata

# Data Retention
RETENTION_ENABLED=true
RETENTION_DEFAULT_DAYS=365
RETENTION_AUDIT_LOG_DAYS=730

# SLA Monitoring
SLA_MONITORING_ENABLED=true
SLA_DEFAULT_UPTIME_TARGET=99.9
SLA_DEFAULT_RESPONSE_TIME_MS=2000

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
NEXT_PUBLIC_API_URL=https://contentforge-ai-api.onrender.com
NEXT_PUBLIC_API_VERSION=v1
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_your_key
```

### Celery Configuration

```bash
# Standard worker
celery -A app.core.celery_app worker --loglevel=info --concurrency=4

# Beat scheduler
celery -A app.core.celery_app beat --loglevel=info
```

#### Task Routing

```python
task_routes = {
    'app.tasks.email.*': {'queue': 'email'},
    'app.tasks.rss.*': {'queue': 'rss'},
    'app.tasks.competitors.*': {'queue': 'analysis'},
}
```

---

## SSO / SAML Configuration

### OIDC (OpenID Connect) Setup

1. **Navigate to Admin → Authentication → SSO**
2. Click **"Add OIDC Provider"**
3. Configure:
   - **Provider Name**: e.g., "Okta", "Auth0"
   - **Client ID**: From your IdP
   - **Client Secret**: From your IdP
   - **Authorization URL**: IdP authorization endpoint
   - **Token URL**: IdP token endpoint
   - **User Info URL**: IdP userinfo endpoint
   - **Scopes**: `openid profile email` (default)
   - **Domain/Issuer**: Your IdP domain
4. Click **"Test Connection"** to verify
5. Enable the provider

**API Configuration:**
```bash
POST /api/v1/sso/configure
{
  "provider_name": "Okta",
  "client_id": "...",
  "client_secret": "...",
  "authorization_url": "https://your-okta.okta.com/oauth2/v1/authorize",
  "token_url": "https://your-okta.okta.com/oauth2/v1/token",
  "userinfo_url": "https://your-okta.okta.com/oauth2/v1/userinfo",
  "scopes": ["openid", "profile", "email"]
}
```

### SAML 2.0 Setup

1. **Navigate to Admin → Authentication → SAML**
2. Download SP Metadata: `GET /api/v1/saml/metadata`
3. Upload SP metadata to your IdP
4. Configure in ContentForge:
   - **IdP Entity ID**: From your IdP
   - **IdP SSO URL**: Login redirect URL
   - **IdP SLO URL**: Logout redirect URL (optional)
   - **IdP Certificate**: X.509 certificate
   - **Attribute Mapping**: Email, name, groups
5. Click **"Test Connection"**
6. Enable the provider

**API Configuration:**
```bash
POST /api/v1/saml/configure
{
  "provider_name": "Azure AD",
  "idp_entity_id": "https://sts.windows.net/...",
  "idp_sso_url": "https://login.microsoftonline.com/.../saml2",
  "idp_certificate": "-----BEGIN CERTIFICATE-----\n...",
  "attribute_mapping": {
    "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
    "name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",
    "groups": "http://schemas.xmlsoap.org/claims/Group"
  }
}
```

### Group/Role Mapping

After configuring SSO/SAML, map IdP groups to ContentForge roles:

1. Navigate to Admin → Authentication → Role Mapping
2. Map each IdP group to a ContentForge role (admin, editor, viewer)
3. Users are auto-assigned roles on first login

### Multiple Providers

OIDC and SAML providers can coexist. Users select their provider on the login page. Each provider can serve different user populations (e.g., employees via SAML, contractors via OIDC).

---

## Plugin Management

### Overview

The Plugin System allows administrators to extend ContentForge with custom functionality. Plugins can add routes, modify content pipelines, and integrate external services.

### Installing a Plugin

**Via API:**
```bash
POST /api/v1/plugins/install
{
  "source": "marketplace",
  "plugin_id": "slack-notifications"
}
```

**Via Admin UI:**
1. Navigate to Admin → Plugins
2. Browse marketplace or upload plugin package
3. Click **"Install"**
4. Review requested permissions
5. Approve installation

### Managing Plugins

| Action | API | UI |
|--------|-----|----|
| List plugins | `GET /api/v1/plugins` | Admin → Plugins |
| Enable | `PATCH /api/v1/plugins/{id}/enable` | Toggle switch |
| Disable | `PATCH /api/v1/plugins/{id}/disable` | Toggle switch |
| Configure | `PATCH /api/v1/plugins/{id}/config` | Settings panel |
| Uninstall | `DELETE /api/v1/plugins/{id}` | Uninstall button |

### Plugin Permissions

Plugins declare required permissions on install. Review carefully:

| Permission | Description |
|-----------|-------------|
| `content.read` | Read content items |
| `content.write` | Create/edit content |
| `user.read` | Read user profiles |
| `webhook.send` | Send outgoing webhooks |
| `notification.send` | Send notifications |
| `api.route` | Register custom API routes |

### Developing Custom Plugins

Use the ContentForge SDK to build custom plugins:

```python
from contentforge_sdk import Plugin, route

class MyPlugin(Plugin):
    name = "my-custom-plugin"
    version = "1.0.0"
    permissions = ["content.read", "webhook.send"]

    @route("/my-plugin/data", methods=["GET"])
    async def get_data(self, request):
        return {"data": "hello"}
```

---

## Data Retention Policies

### Overview

Data retention policies control how long different data types are stored before automatic cleanup. Essential for GDPR compliance and data governance.

### Default Policies

| Data Type | Default Retention | Notes |
|-----------|-------------------|-------|
| Content | 365 days | Configurable per project |
| Audit Logs | 730 days | Compliance requirement |
| Analytics | 365 days | Aggregated data kept indefinitely |
| Webhook Logs | 90 days | Debugging window |
| Error Logs | 30 days | Rotated by log management |
| Trashed Items | 30 days | Before permanent deletion |
| Comments | Same as parent content | Inherited |
| Notifications | 90 days | Read notifications |

### Configuring Retention

**Via API:**
```bash
POST /api/v1/retention/policies
{
  "data_type": "webhook_logs",
  "retention_days": 60,
  "action": "delete",
  "description": "Webhook delivery logs - 60 day retention"
}
```

**Via Admin UI:**
1. Navigate to Admin → Data Retention
2. Select data type
3. Set retention period (days)
4. Choose action: delete or archive
5. Save policy

### Enforcement

- Policies are enforced automatically via scheduled cron jobs
- Manual enforcement: `POST /api/v1/retention/apply`
- Retention status: `GET /api/v1/retention/status`
- Data follows the trash system before permanent deletion

---

## SLA Monitoring Setup

### Overview

SLA monitoring tracks compliance with defined service level targets. Configure targets, receive breach alerts, and generate compliance reports.

### Default SLA Targets

| Metric | Default Target | Description |
|--------|----------------|-------------|
| API Uptime | 99.9% | Monthly availability |
| Response Time (p95) | 2000ms | 95th percentile response time |
| Error Rate | <1% | 5xx error percentage |
| Queue Processing | <5 min | Time from queue to completion |
| AI Generation | <30s | Content generation latency |

### Configuring SLA Targets

**Via API:**
```bash
POST /api/v1/sla/define
{
  "name": "API Response Time",
  "metric": "response_time_p95",
  "target": 2000,
  "unit": "ms",
  "window": "5m",
  "alert_on_breach": true
}
```

**Via Admin UI:**
1. Navigate to Admin → SLA Monitoring
2. Click **"Add SLA Target"**
3. Configure metric, target, window, and alerting
4. Save

### Monitoring & Alerts

- SLA compliance dashboard: `GET /api/v1/sla/compliance`
- Breach history: `GET /api/v1/sla/breaches`
- Scheduled reports: `GET /api/v1/sla/report`
- Breach alerts integrate with the existing alerts system and can route to email, Slack, or PagerDuty

---

## Marketplace Management

### Overview

As an administrator, you manage which marketplace items are available to your organization, curate featured items, and control publishing permissions.

### Browsing & Installing

Users can browse the marketplace at Admin → Marketplace or via `GET /api/v1/marketplace`. Installation is one-click, with admin approval (if configured).

### Admin Controls

| Action | Description |
|--------|-------------|
| Feature item | Pin to marketplace homepage |
| Restrict item | Block installation in your org |
| Review submissions | Approve/reject community submissions |
| Set install permissions | Allow all / admin-only / specific roles |

### Publishing to Marketplace

Organization members can publish templates and plugins:

```bash
POST /api/v1/marketplace/publish
{
  "type": "plugin",
  "name": "Custom Analytics Dashboard",
  "description": "...",
  "version": "1.0.0",
  "package_url": "..."
}
```

Published items go through a review queue before becoming publicly visible.

---

## Monitoring

### Application Monitoring

#### Health Checks

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/health` | Basic health status |
| `GET /api/v1/health/detailed` | Component-level health |

**Example Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-14T10:00:00Z",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "redis": "connected",
    "ai_service": "connected"
  }
}
```

#### Performance Monitoring

- **X-Response-Time header** on all API responses
- Slow request logging (requests > 1s logged automatically)
- 9 endpoints with Redis + in-memory caching
- Parallel query execution for data-heavy endpoints
- N+1 query fixes applied across services
- ETag support for conditional requests

#### Metrics to Monitor

| Metric | Warning | Critical |
|--------|---------|----------|
| Response Time | >500ms | >2000ms |
| Error Rate | >1% | >5% |
| Queue Depth | >100 | >500 |
| CPU Usage | >70% | >90% |
| Memory Usage | >80% | >95% |
| DB Connections | >80% | >95% |

### Cache Management

The platform uses a dual-layer caching strategy:

| Layer | Technology | Use Case | TTL |
|-------|-----------|----------|-----|
| L1 | In-memory (per-process) | Hot data, session state | 60s |
| L2 | Redis | Shared data, query results | 300s |

**Cached Endpoints (9):**
- Analytics dashboard
- Performance overview
- Quality dashboard
- Sentiment dashboard
- Freshness dashboard
- SLA compliance
- Integration health
- Content search
- Trend discovery

**Cache Invalidation:**
- Automatic on content mutation (write-through)
- Manual: `DELETE /api/v1/admin/cache/{key}`
- Bulk: `POST /api/v1/admin/cache/flush`

### Monitoring Tools

| Layer | Tool | Purpose |
|-------|------|---------|
| APM | Datadog / New Relic | Performance monitoring |
| Logs | Papertrail / LogDNA | Log aggregation |
| Errors | Sentry | Error tracking |
| Uptime | Pingdom / UptimeRobot | Availability monitoring |
| DB | Supabase Dashboard | Query performance |
| CI | GitHub Actions | Pipeline monitoring |

### Alerting

```yaml
Alert: High Response Time
Condition: p95 response time > 1000ms for 5 minutes
Action: Send Slack notification, page on-call

Alert: High Error Rate
Condition: Error rate > 2% for 2 minutes
Action: Send email to dev team

Alert: SLA Breach
Condition: Any SLA target breached
Action: Alert admin team, create incident
```

---

## Troubleshooting

### Common Issues

#### API Returns 500 Errors

1. Check database and Redis connectivity
2. Review recent deployments for breaking changes
3. Check external service status (Groq, Stripe)
4. View logs: `render logs --service contentforge-ai-api --tail`

#### Slow Response Times

1. Check cache hit rates (Redis + in-memory)
2. Review slow query logs in Supabase Dashboard
3. Check for N+1 query patterns
4. Scale workers if queue depth is high
5. Verify ETag utilization (conditional requests reduce payload)

#### Queue Backlog

```bash
celery -A app.core.celery_app inspect active
celery -A app.core.celery_app inspect scheduled
# Scale workers or increase concurrency
```

#### SSO Login Failures

1. Verify IdP configuration (client ID, secret, URLs)
2. Check callback URLs match
3. Test connection: `GET /api/v1/sso/test/{provider}`
4. Review audit logs for auth errors
5. Verify clock sync between SP and IdP

#### SAML Assertion Errors

1. Download SP metadata: `GET /api/v1/saml/metadata`
2. Verify IdP configuration matches SP metadata
3. Check certificate validity
4. Test connection: `GET /api/v1/saml/test/{provider}`
5. Review SAML assertion attributes vs configured mapping

#### Plugin Installation Failures

1. Check plugin compatibility with current platform version
2. Verify permissions are sufficient
3. Review plugin logs in admin panel
4. Try disabling conflicting plugins

---

## Security

### Authentication Security

- JWT with HS256, 30-minute token expiry
- Supabase Row Level Security enabled
- Rate limiting: 100 requests/hour (configurable)
- CORS restricted to configured origins

### Security Status

- **9/9 HIGH/CRITICAL findings** remediated
- Security pipeline: 8/13 scans pass, 5 expected infra failures
- SARIF results uploaded to GitHub Security tab
- Dependency scanning (pip-audit, npm audit, OSV Scanner)

### Compliance

- GDPR: Data export, right to deletion, consent management
- SOC 2: Audit logs, access controls, encryption
- Data retention policies enforce data minimization
- SSO/SAML supports enterprise identity governance

### Security Checklist

- [x] HTTPS enforced
- [x] Secure headers configured
- [x] Rate limiting enabled
- [x] SQL injection prevention (parameterized queries)
- [x] XSS prevention
- [x] CSRF tokens
- [x] Security headers
- [x] Dependency scanning
- [x] All HIGH/CRITICAL findings fixed
- [x] Audit logging enabled
- [x] SSO/SAML for enterprise auth

---

## Maintenance

### Regular Tasks

#### Daily
- [ ] Check error logs (Sentry)
- [ ] Review failed jobs
- [ ] Monitor queue depth
- [ ] Check SLA compliance

#### Weekly
- [ ] Review performance metrics
- [ ] Check database size
- [ ] Verify backup completion
- [ ] Review plugin health
- [ ] Check retention policy enforcement

#### Monthly
- [ ] Security updates
- [ ] Dependency updates
- [ ] Performance review (cache hit rates, slow queries)
- [ ] Cost optimization
- [ ] Access review
- [ ] SLA compliance report

#### Quarterly
- [ ] Disaster recovery test
- [ ] Security audit
- [ ] Architecture review
- [ ] Documentation updates
- [ ] Plugin compatibility review

### Updates

```bash
# Backend dependencies
pip install -r requirements.txt --upgrade
pytest  # 530 tests

# Frontend dependencies
npm update
npm test

# Deploy via CI/CD (self-hosted runner)
git push origin main
```

### Database Migrations

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1  # Rollback
```

### Scaling

| Approach | When to Use |
|----------|-------------|
| Add API instances | Traffic spike |
| Increase worker count | Queue backlog |
| Add read replicas | DB read pressure |
| CDN for static assets | Global audience |
| Increase Redis memory | Cache eviction rate high |

---

## Support

- **Documentation**: https://docs.contentforge.ai
- **Status Page**: https://status.contentforge.ai
- **Email**: support@contentforge.ai
- **Emergency**: ops@contentforge.ai

---

**Document Version**: 2.0.0  
**Last Updated**: 2026-04-14  
**CI**: 4/4 green (srv1503460) | **Tests**: 530 passing | **Security**: 9/9 fixed