# ContentForge AI - Operations Runbook

> Incident response procedures and operational guidelines for the ContentForge AI platform.

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Incident Severity Levels](#incident-severity-levels)
3. [Emergency Contacts](#emergency-contacts)
4. [Monitoring Dashboards](#monitoring-dashboards)
5. [Common Incidents](#common-incidents)
6. [Runbook Procedures](#runbook-procedures)
7. [Deployment Procedures](#deployment-procedures)
8. [Backup and Recovery](#backup-and-recovery)
9. [Security Incidents](#security-incidents)

---

## Quick Reference

### Service URLs

| Service | Staging | Production |
|---------|---------|------------|
| Frontend | `https://contentforge-ai-staging.vercel.app` | `https://contentforge-ai.vercel.app` |
| Backend API | `https://contentforge-ai-api-staging.onrender.com` | `https://contentforge-ai-api.onrender.com` |
| Health Check | `/api/v1/health` | `/api/v1/health` |
| API Docs | `/docs` | `/docs` |

### Critical Commands

```bash
# Check service health
curl https://contentforge-ai-api.onrender.com/api/v1/health
curl https://contentforge-ai-api.onrender.com/api/v1/health/detailed

# View recent errors (admin only)
curl -H "Authorization: Bearer $TOKEN" \
  https://contentforge-ai-api.onrender.com/api/v1/admin/errors

# Check webhook logs (admin only)
curl -H "Authorization: Bearer $TOKEN" \
  https://contentforge-ai-api.onrender.com/api/v1/webhooks/logs

# Trigger backup manually
./scripts/backup-database.sh --daily
./scripts/backup-database.sh --weekly
```

---

## Incident Severity Levels

### P0 - Critical (Immediate Response Required)
- Complete system outage
- Data loss or corruption
- Security breach
- Payment processing failure
- Database connection failures

**Response Time:** 15 minutes  
**Communication:** All stakeholders immediately

### P1 - High (Response Within 1 Hour)
- Major feature degradation
- Performance severely impacted (>5s response times)
- Significant error rate (>5%)
- Stripe webhook failures
- AI generation failures

**Response Time:** 1 hour  
**Communication:** Engineering team, stakeholders

### P2 - Medium (Response Within 4 Hours)
- Minor feature issues
- Non-critical performance degradation
- Minor UI/UX issues
- Documentation errors

**Response Time:** 4 hours  
**Communication:** Engineering team

### P3 - Low (Next Business Day)
- Cosmetic issues
- Feature requests
- Documentation improvements

**Response Time:** Next business day  
**Communication:** Backlog

---

## Emergency Contacts

| Role | Name | Contact |
|------|------|---------|
| Executive Agent | Neo DevOrg | @neo-me-no-bot:matrix.org |
| On-Call Engineer | TBD | TBD |
| Stripe Support | - | https://support.stripe.com |
| Supabase Support | - | https://supabase.com/support |
| Render Support | - | https://render.com/support |
| Vercel Support | - | https://vercel.com/support |

---

## Monitoring Dashboards

### Sentry (Error Tracking)
- **URL:** https://sentry.io/organizations/YOUR_ORG/projects/contentforge-ai/
- **Alerts:** Real-time error notifications
- **Performance:** Transaction tracing

### Vercel Analytics (Frontend)
- **URL:** https://vercel.com/dashboard
- **Metrics:** Web Vitals, Core Web Vitals
- **Real User Monitoring:** Page load times

### Render Dashboard (Backend)
- **URL:** https://dashboard.render.com/
- **Metrics:** CPU, memory, request logs
- **Services:** Web, Redis, Workers

### Supabase Dashboard (Database)
- **URL:** https://app.supabase.com/project/YOUR_PROJECT
- **Metrics:** Connection pool, query performance
- **Logs:** Database queries

---

## Common Incidents

### API Down / Health Check Failing

**Symptoms:**
- Health endpoint returns 503
- Users cannot access the application

**Diagnosis:**
```bash
# Check basic health
curl -v https://contentforge-ai-api.onrender.com/api/v1/health

# Check detailed health
curl https://contentforge-ai-api.onrender.com/api/v1/health/detailed

# View Render logs
render logs --service contentforge-ai-api --tail
```

**Resolution:**
1. Check Render dashboard for service status
2. Review recent deployments for breaking changes
3. Check database connectivity
4. Verify environment variables are set
5. Restart service if necessary: Render Dashboard → Service → Manual Deploy

**Prevention:**
- Automated health checks before deployment
- Staged rollout strategy
- Database connection pooling

---

### Database Connection Failures

**Symptoms:**
- Health check shows database as "unhealthy"
- Errors: "connection refused", "pool timeout"
- Users cannot log in or save data

**Diagnosis:**
```bash
# Check database connectivity
curl https://contentforge-ai-api.onrender.com/api/v1/health/detailed | jq '.components.database'

# Check Supabase status
# Visit https://status.supabase.com/
```

**Resolution:**
1. Check Supabase status page for outages
2. Verify connection string and credentials
3. Check connection pool size in Supabase dashboard
4. Restart application to reset connections
5. Scale up database resources if needed

**Prevention:**
- Connection pooling configured
- Health checks with early detection
- Supabase read replicas for high load

---

### High Error Rate

**Symptoms:**
- Sentry alerts firing
- Users reporting failures
- Error rate > 5%

**Diagnosis:**
```bash
# View recent errors in Sentry
# Visit Sentry dashboard → Issues

# Query error summary (admin only)
curl -H "Authorization: Bearer $TOKEN" \
  https://contentforge-ai-api.onrender.com/api/v1/admin/errors/summary
```

**Resolution:**
1. Identify error patterns in Sentry
2. Check for recent deployments that might have introduced bugs
3. Check external API status (Groq, Stripe)
4. Rollback to previous version if needed
5. Apply hotfix for critical issues

**Prevention:**
- Automated error rate alerting
- Staged deployments with monitoring
- Comprehensive testing

---

### Groq API Failures

**Symptoms:**
- AI content generation failing
- Error messages: "Groq API error", "Rate limit exceeded"
- Queue backing up

**Diagnosis:**
```bash
# Check Groq status
curl https://contentforge-ai-api.onrender.com/api/v1/health/detailed | jq '.components.groq'

# Check Groq status page
# Visit https://status.groq.com/
```

**Resolution:**
1. Check Groq status page
2. Verify API key is valid
3. Check rate limit usage in Groq dashboard
4. Implement exponential backoff in code
5. Consider fallback to other AI providers

**Prevention:**
- Rate limiting monitoring
- Circuit breaker pattern
- Multiple AI provider support

---

### Stripe Webhook Failures

**Symptoms:**
- Payments not processing
- Subscription status not updating
- Webhook logs showing failures

**Diagnosis:**
```bash
# Check Stripe status
curl https://contentforge-ai-api.onrender.com/api/v1/health/detailed | jq '.components.stripe'

# View webhook logs (admin only)
curl -H "Authorization: Bearer $TOKEN" \
  https://contentforge-ai-api.onrender.com/api/v1/webhooks/logs?webhook_type=stripe
```

**Resolution:**
1. Check Stripe dashboard webhook logs
2. Verify webhook endpoint is accessible
3. Check webhook signature verification
4. Replay failed webhooks from Stripe dashboard
5. Update webhook secret if rotated

**Prevention:**
- Webhook signature verification
- Idempotency key handling
- Retry with exponential backoff
- Webhook event logging

---

### Disk Space Critical

**Symptoms:**
- Health check shows disk as "unhealthy"
- File uploads failing
- "No space left on device" errors

**Diagnosis:**
```bash
# Check disk usage
curl https://contentforge-ai-api.onrender.com/api/v1/health/detailed | jq '.components.disk'

# Check Render service metrics
render metrics --service contentforge-ai-api
```

**Resolution:**
1. Check what is consuming disk space
2. Clear temporary files and logs
3. Scale up disk on Render
4. Implement log rotation
5. Archive old backups

**Prevention:**
- Automated disk monitoring
- Log rotation policies
- Automated cleanup of old backups

---

## Runbook Procedures

### Database Backup Recovery

**When to Use:**
- Data corruption detected
- Accidental data deletion
- Migration rollback needed

**Steps:**

1. **Identify the backup to restore:**
   ```bash
   # List available backups
   aws s3 ls s3://$R2_BUCKET_NAME/backups/ \
     --endpoint-url https://$R2_ACCOUNT_ID.r2.cloudflarestorage.com
   ```

2. **Restore from backup:**
   ```bash
   # Download backup
   aws s3 cp s3://$R2_BUCKET_NAME/backups/weekly/2026-04-12/export_weekly_xxx.tar.gz \
     ./restore.tar.gz \
     --endpoint-url https://$R2_ACCOUNT_ID.r2.cloudflarestorage.com
   
   # Extract and restore (requires Supabase CLI or manual SQL)
   # Contact Supabase support for assistance
   ```

3. **Verify restoration:**
   ```bash
   # Check data integrity
   curl https://contentforge-ai-api.onrender.com/api/v1/health/detailed
   ```

**Recovery Time:** 30-60 minutes

---

### Rolling Back a Deployment

**When to Use:**
- Critical bug introduced in new deployment
- Performance regression
- Breaking change not caught in staging

**Steps:**

1. **Frontend Rollback (Vercel):**
   ```bash
   # List deployments
   vercel ls
   
   # Rollback to specific deployment
   vercel rollback [deployment-url]
   ```

2. **Backend Rollback (Render):**
   - Go to Render Dashboard
   - Select the service
   - Click "Manual Deploy" → "Deploy a specific commit"
   - Select the last known good commit
   - Click "Deploy"

3. **Verify Rollback:**
   ```bash
   # Check health
   curl https://contentforge-ai-api.onrender.com/api/v1/health
   
   # Check error rates in Sentry
   ```

**Recovery Time:** 5-10 minutes

---

### Scaling for High Load

**When to Use:**
- Traffic spike expected
- Performance degradation under load
- Queue depth increasing

**Steps:**

1. **Vertical Scaling (Immediate):**
   - Render Dashboard → Service → Settings
   - Increase instance type
   - Redeploy

2. **Horizontal Scaling:**
   - Enable auto-scaling in Render
   - Configure min/max instances
   - Set scaling triggers (CPU, memory)

3. **Database Scaling:**
   - Supabase Dashboard → Database → Settings
   - Increase compute add-ons
   - Enable read replicas

4. **CDN/Cache:**
   - Verify Cloudflare caching
   - Enable Redis for session caching

---

## Deployment Procedures

### Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Staging deployment verified
- [ ] Database migrations reviewed
- [ ] Environment variables documented
- [ ] Rollback plan prepared
- [ ] Monitoring alerts configured
- [ ] On-call engineer notified

### Deployment Steps

1. **Create deployment tag:**
   ```bash
   git tag -a v1.0.1 -m "Release v1.0.1"
   git push origin v1.0.1
   ```

2. **Deploy to Staging:**
   ```bash
   ./scripts/deploy-backend.sh
   ./scripts/deploy-frontend.sh
   ```

3. **Verify Staging:**
   - Run smoke tests
   - Check health endpoints
   - Verify critical user journeys

4. **Deploy to Production:**
   ```bash
   ./scripts/deploy-backend.sh --prod
   ./scripts/deploy-frontend.sh --prod
   ```

5. **Post-Deployment Verification:**
   - Monitor Sentry for new errors
   - Check health endpoints
   - Verify error rates

---

## Backup and Recovery

### Automated Backups

- **Daily backups:** 2:00 AM UTC
- **Weekly backups:** Sunday 3:00 AM UTC
- **Retention:** 30 days
- **Storage:** Cloudflare R2

### Manual Backup

```bash
# Daily backup
./scripts/backup-database.sh --daily

# Weekly full backup
./scripts/backup-database.sh --weekly

# Verify backup integrity
./scripts/backup-database.sh --verify
```

### Backup Monitoring

- **Alert Email:** Configured in environment variables
- **Failure Notifications:** Automatic via Resend
- **Backup Logs:** Stored in `logs/` directory

---

## Security Incidents

### API Key Compromise

**Symptoms:**
- Unauthorized API usage
- Unusual traffic patterns
- Unexpected charges

**Immediate Actions:**
1. Revoke compromised keys in respective dashboards
2. Rotate all API keys
3. Update environment variables
4. Redeploy services
5. Review access logs for impact assessment

**Notification:**
- Notify users if data potentially accessed
- File incident report
- Review security policies

### DDoS Attack

**Symptoms:**
- Traffic spike from single source
- Service unavailable
- Elevated error rates

**Immediate Actions:**
1. Enable Cloudflare "Under Attack" mode
2. Enable rate limiting (already configured)
3. Contact hosting provider (Vercel, Render)
4. Implement IP blocking if needed

### Data Breach

**Immediate Actions:**
1. Isolate affected systems
2. Revoke all sessions
3. Force password resets
4. Audit access logs
5. Notify affected users within 72 hours (GDPR)
6. File security incident report

---

## Appendix

### Environment Variables Reference

```bash
# Required
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_SERVICE_ROLE_KEY=
GROQ_API_KEY=

# Monitoring
SENTRY_DSN=
SENTRY_ENVIRONMENT=
ALERT_EMAIL=

# Backups
R2_BUCKET_NAME=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_ACCOUNT_ID=
BACKUP_RETENTION_DAYS=30

# Webhooks
N8N_WEBHOOK_SECRET=
STRIPE_WEBHOOK_SECRET=
```

### Useful Queries

```sql
-- Check recent webhook failures
SELECT webhook_type, status, COUNT(*) 
FROM webhook_logs 
WHERE status = 'failed' 
  AND created_at > NOW() - INTERVAL '1 hour'
GROUP BY webhook_type, status;

-- Check error rates by endpoint
SELECT path, status_code, COUNT(*)
FROM error_logs
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY path, status_code;
```

---

*Last updated: 2026-04-13*  
*Version: 1.0*  
*Owner: Neo DevOrg DevOps Team*