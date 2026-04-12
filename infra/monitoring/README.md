# ContentForge AI - Monitoring & Observability

This directory contains monitoring configuration and observability setup for ContentForge AI.

## Overview

Monitoring stack includes:
- **Error Tracking**: Sentry for real-time error monitoring
- **Performance Monitoring**: Sentry Performance + Custom metrics
- **Health Checks**: Built-in FastAPI health endpoints
- **Logging**: Structured logging with JSON format

## Sentry Integration

### Backend (FastAPI)

Sentry is configured in `src/backend/app/main.py`:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://your-dsn@sentry.io/project-id",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1,
    environment="production",
    release="contentforge-ai@1.0.0",
)
```

### Frontend (Next.js)

Sentry is configured in `src/frontend/sentry.client.config.js`:

```javascript
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT || 'development',
  release: process.env.NEXT_PUBLIC_RELEASE || 'contentforge-ai@dev',
  tracesSampleRate: 0.1,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  integrations: [
    Sentry.replayIntegration({
      maskAllText: false,
      blockAllMedia: false,
    }),
  ],
});
```

### Environment Variables

Add to your deployment platform:

```bash
# Backend
SENTRY_DSN=https://your-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
SENTRY_RELEASE=contentforge-ai@1.0.0

# Frontend
NEXT_PUBLIC_SENTRY_DSN=https://your-dsn@sentry.io/project-id
NEXT_PUBLIC_ENVIRONMENT=production
NEXT_PUBLIC_RELEASE=contentforge-ai@1.0.0
```

## Recommended Monitoring Tools

### Error Tracking
- **Sentry**: Primary error tracking (configured)
- **LogRocket**: User session replay (optional)

### Performance Monitoring
- **Sentry Performance**: API latency, database queries
- **Vercel Analytics**: Frontend Web Vitals (automatic on Vercel)
- **Render Metrics**: Backend metrics on Render.com

### Infrastructure Monitoring
- **Upptime**: GitHub Actions-based uptime monitoring (free)
- **Better Uptime**: External uptime monitoring with status page
- **Pingdom**: Commercial uptime monitoring

### Database Monitoring
- **Supabase Dashboard**: Query performance, connection pool
- **pg_stat_statements**: Query analysis (if self-hosted)

### AI/LLM Monitoring
- **LangSmith**: OpenAI/Anthropic API monitoring (recommended)
- **LangFuse**: Open-source LLM observability
- **Helicone**: LLM API cost and performance tracking

## Alerting Recommendations

### Critical Alerts (Immediate)
- API downtime > 1 minute
- Error rate > 5%
- Database connection failures
- n8n webhook failures

### Warning Alerts (Within 1 hour)
- Response time > 2 seconds (95th percentile)
- Queue depth > 100 items
- Memory usage > 80%

### Info Alerts (Daily digest)
- Daily error counts
- Usage statistics
- Cost thresholds

## Health Check Endpoints

Backend exposes health endpoints:

```
GET /health          - Basic liveness check
GET /health/ready    - Readiness check (includes DB connectivity)
GET /health/deep     - Deep health check (all dependencies)
```

## Setting Up Sentry

1. Create a Sentry account at https://sentry.io
2. Create a new project for "contentforge-ai"
3. Copy the DSN from Project Settings > SDK Setup
4. Add the DSN to your environment variables
5. Deploy and verify events are being captured

## Custom Metrics

Track business metrics:

```python
# Backend example
from sentry_sdk import metrics

metrics.incr("content.generated", tags={"content_type": "blog"})
metrics.timing("ai.generation.time", duration_ms)
metrics.gauge("queue.depth", queue_size)
```

## Dashboard Recommendations

### Sentry Dashboard
- Top issues by frequency
- Issues by release
- Performance by endpoint
- User impact analysis

### Vercel Dashboard
- Build status
- Deployment frequency
- Edge function metrics

### Render Dashboard
- Service health
- Resource utilization
- Deploy logs

## Runbooks

### High Error Rate
1. Check Sentry for new issues
2. Review recent deployments
3. Check dependency status (OpenAI, Supabase)
4. Scale up if under load

### Performance Degradation
1. Identify slow endpoints in Sentry Performance
2. Check database query times
3. Review AI API latency
4. Consider rate limiting adjustments

## Security Monitoring

- Monitor for API key abuse
- Track unusual content generation patterns
- Set up alerts for authentication failures
- Review audit logs weekly
