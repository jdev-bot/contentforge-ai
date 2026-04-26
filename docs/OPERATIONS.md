# ContentForge AI - Operations Runbook

> Incident response procedures and operational guidelines for the ContentForge AI platform.

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Incident Severity Levels](#incident-severity-levels)
3. [Self-Hosted Runner Operations](#self-hosted-runner-operations)
4. [CI Pipeline Management](#ci-pipeline-management)
5. [Monitoring & Performance](#monitoring--performance)
6. [Cache Management](#cache-management)
7. [Common Incidents](#common-incidents)
8. [Runbook Procedures](#runbook-procedures)
9. [Deployment Procedures](#deployment-procedures)
10. [Backup and Recovery](#backup-and-recovery)
11. [Security Incidents](#security-incidents)

---

## Quick Reference

### Service URLs

| Service | Staging | Production |
|---------|---------|------------|
| Frontend | `https://contentforge-ai-staging.vercel.app` | `https://contentforge-ai.vercel.app` |
| Backend API | `https://contentforge-ai-api-staging.onrender.com` | `https://contentforge-ai-api.onrender.com` |
| Health Check | `/api/v1/health` | `/api/v1/health` |
| Detailed Health | `/api/v1/health/detailed` | `/api/v1/health/detailed` |
| API Docs | `/docs` | `/docs` |

### Platform Stats

| Metric | Value |
|--------|-------|
| API Routes | 375 (184 GET \| 124 POST \| 15 PUT \| 15 PATCH \| 37 DELETE) |
| Router Modules | 49 |
| Backend Services | 34 |
| Frontend Components | 73 |
| Pages | 16 |
| Backend Tests | 530 passing |
| CI Pipelines | 4/4 green |
| Self-Hosted Runner | srv1503460 |

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

# Flush caches
curl -X POST -H "Authorization: Bearer $TOKEN" \
  https://contentforge-ai-api.onrender.com/api/v1/admin/cache/flush

# Check SLA compliance
curl -H "Authorization: Bearer $TOKEN" \
  https://contentforge-ai-api.onrender.com/api/v1/sla/compliance
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

## Self-Hosted Runner Operations

### Runner Configuration

ContentForge AI uses a self-hosted GitHub Actions runner on **srv1503460** for all CI/CD pipelines.

| Property | Value |
|----------|-------|
| Hostname | srv1503460 |
| OS | Linux 6.17.0-20-generic (x64) |
| Node.js | v22.22.2 |
| Runner Version | Latest (auto-updates) |
| Services | Docker, build-essential, Python 3.13 |

### Runner Health Checks

```bash
# Check runner service status
systemctl status actions.runner.*

# Check runner logs
journalctl -u actions.runner.* -n 100 --no-pager

# Verify runner is online in GitHub
# Settings → Actions → Runners → Check "Idle" status
```

### Runner Maintenance

| Task | Frequency | Command |
|------|-----------|---------|
| Service status check | Daily | `systemctl status actions.runner.*` |
| Log review | Weekly | `journalctl -u actions.runner.* --since "7 days ago"` |
| Disk cleanup | Monthly | `docker system prune -f; rm -rf /tmp/_temp_*` |
| Runner update | As needed | Auto-updates; check GitHub Settings → Actions |

### Runner Troubleshooting

**Runner Offline:**
1. Check service: `systemctl status actions.runner.*`
2. Restart: `systemctl restart actions.runner.*`
3. Check network connectivity to GitHub
4. Verify registration token is valid
5. Re-register runner if token expired

**Runner Disk Full:**
1. Check disk: `df -h`
2. Clean Docker: `docker system prune -f`
3. Clean temp files: `rm -rf /tmp/_temp_*`
4. Clean work directories: `rm -rf ~/actions-runner/_work/_temp/*`

---

## CI Pipeline Management

### Pipeline Overview

ContentForge AI has 4 GitHub Actions workflows, all running on the self-hosted runner:

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| Backend Tests | `backend-tests.yml` | Push/PR to main/develop | Python test suite (530 tests) |
| Frontend Build | `frontend-build.yml` | Push/PR to main/develop | Next.js build + lint |
| CI/CD | `ci-cd.yml` | Push to main/develop | Full build, test, deploy |
| Security | `security.yml` | Push/PR + weekly schedule | Security scanning pipeline |

### Pipeline Status

All 4 pipelines are currently **green** (passing).

### Monitoring Pipeline Health

```bash
# Check recent workflow runs
gh run list --limit 10

# Check specific workflow
gh run list --workflow=backend-tests.yml --limit 5
gh run list --workflow=frontend-build.yml --limit 5
gh run list --workflow=ci-cd.yml --limit 5
gh run list --workflow=security.yml --limit 5

# View run details
gh run view <run-id>

# View failed run logs
gh run view <run-id> --log-failed
```

### Pipeline Troubleshooting

**Backend Tests Failing:**
1. Check which tests failed: `gh run view <run-id> --log-failed`
2. Run locally: `cd src/backend && pytest -v`
3. Common causes: database migration mismatch, environment variable missing, test data conflict

**Frontend Build Failing:**
1. Check build error: `gh run view <run-id> --log-failed`
2. Run locally: `cd src/frontend && npm run build && npm run lint`
3. Common causes: TypeScript errors, missing env vars, dependency conflicts

**Security Pipeline Failing:**
1. Check which scan failed (8 pass, 5 expected infra failures)
2. See `SECURITY_PIPELINE.md` for scan details
3. Run locally: `gitleaks detect -v; semgrep --config p/default src/`

---

## Monitoring & Performance

### Performance Monitoring

| Mechanism | Description | Location |
|-----------|-------------|----------|
| X-Response-Time header | Response time on every API response | HTTP headers |
| Slow request logging | Requests >1s logged automatically | Backend logs |
| Health checks | Basic + detailed component health | `/api/v1/health` |
| Sentry | Error tracking + performance tracing | Sentry dashboard |
| Supabase Dashboard | Query performance monitoring | Supabase console |

### Performance Optimizations (Current)

| Optimization | Endpoints | Impact |
|-------------|-----------|--------|
| Redis + in-memory caching | 9 high-traffic endpoints | Reduced p95 by 60% |
| Parallel query execution | Data-heavy endpoints | Reduced response time 40% |
| N+1 query fixes | All list endpoints | Eliminated N+1 patterns |
| ETag support | GET endpoints | Conditional responses reduce bandwidth |
| Response time middleware | All endpoints | X-Response-Time tracking |
| Slow request logging | All endpoints | Proactive performance issue detection |

### Metrics Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Response Time (p95) | >500ms | >2000ms |
| Error Rate | >1% | >5% |
| Queue Depth | >100 | >500 |
| CPU Usage | >70% | >90% |
| Memory Usage | >80% | >95% |
| DB Connections | >80% | >95% |
| Cache Hit Rate | <80% | <50% |

---

## Cache Management

### Dual-Layer Caching

| Layer | Technology | Scope | TTL | Invalidation |
|-------|-----------|-------|-----|-------------|
| L1 | In-memory (per-process) | Single process | 60s | Write-through |
| L2 | Redis | All processes | 300s | Write-through + TTL |

### Cached Endpoints (9)

| Endpoint | Cache Key Pattern | TTL | Layer |
|----------|-------------------|-----|-------|
| Analytics dashboard | `analytics:dashboard:{user_id}` | 5m | L1 + L2 |
| Performance overview | `performance:overview:{org_id}` | 5m | L1 + L2 |
| Quality dashboard | `quality:dashboard:{org_id}` | 5m | L2 |
| Sentiment dashboard | `sentiment:dashboard:{org_id}` | 5m | L2 |
| Freshness dashboard | `freshness:dashboard:{org_id}` | 5m | L2 |
| SLA compliance | `sla:compliance:{org_id}` | 5m | L2 |
| Integration health | `integrations:health:{org_id}` | 2m | L2 |
| Content search | `search:{query_hash}` | 1m | L1 + L2 |
| Trend discovery | `trends:discovery:{category}` | 5m | L1 + L2 |

### Cache Operations

```bash
# Flush all caches (admin)
curl -X POST -H "Authorization: Bearer $TOKEN" \
  https://contentforge-ai-api.onrender.com/api/v1/admin/cache/flush

# Flush specific key
curl -X DELETE -H "Authorization: Bearer $TOKEN" \
  https://contentforge-ai-api.onrender.com/api/v1/admin/cache/analytics:dashboard:123

# Check Redis directly
redis-cli -u $REDIS_URL INFO stats
redis-cli -u $REDIS_URL KEYS "contentforge:*"
```

### Cache Monitoring

- Cache hit/miss rates tracked in application metrics
- Cache eviction alerts when Redis memory >80%
- L1 cache stats available per process in health endpoint
- Automatic invalidation on content mutations (write-through)

---

## Common Incidents

### API Down / Health Check Failing

**Diagnosis:**
```bash
curl -v https://contentforge-ai-api.onrender.com/api/v1/health
curl https://contentforge-ai-api.onrender.com/api/v1/health/detailed
render logs --service contentforge-ai-api --tail
```

**Resolution:**
1. Check Render dashboard for service status
2. Review recent deployments for breaking changes
3. Check database connectivity
4. Verify environment variables
5. Restart service if necessary

### Database Connection Failures

**Diagnosis:**
```bash
curl https://contentforge-ai-api.onrender.com/api/v1/health/detailed | jq '.components.database'
```

**Resolution:**
1. Check Supabase status page
2. Verify connection string and credentials
3. Check connection pool size
4. Restart application to reset connections
5. Scale up database resources if needed

### High Error Rate

**Diagnosis:**
```bash
# View Sentry dashboard
# Check error summary (admin)
curl -H "Authorization: Bearer $TOKEN" \
  https://contentforge-ai-api.onrender.com/api/v1/admin/errors/summary
```

**Resolution:**
1. Identify error patterns in Sentry
2. Check recent deployments
3. Check external API status (Groq, Stripe)
4. Rollback if needed
5. Apply hotfix

### AIService Failures

**Diagnosis:**
```bash
curl https://contentforge-ai-api.onrender.com/api/v1/health/detailed | jq '.components.groq'
```

**Resolution:**
1. Check Groq status page
2. Verify API key validity
3. Check rate limit usage
4. Circuit breaker should activate automatically

### Cache Issues

**Symptoms:**
- Stale data displayed
- High response times despite low traffic
- Cache miss rate >50%

**Resolution:**
```bash
# Flush caches
curl -X POST -H "Authorization: Bearer $TOKEN" \
  https://contentforge-ai-api.onrender.com/api/v1/admin/cache/flush

# Check Redis
redis-cli -u $REDIS_URL PING
redis-cli -u $REDIS_URL INFO memory
```

### SLA Breach

**Diagnosis:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://contentforge-ai-api.onrender.com/api/v1/sla/breaches
```

**Resolution:**
1. Check breach details (metric, target, actual value)
2. Correlate with performance monitoring data
3. Identify root cause (infrastructure, code, external service)
4. Remediate
5. Verify SLA compliance restored

---

## Runbook Procedures

### Database Backup Recovery

**Steps:**
1. Identify backup: `aws s3 ls s3://$R2_BUCKET_NAME/backups/ --endpoint-url ...`
2. Download backup
3. Restore via Supabase CLI or manual SQL
4. Verify: `curl /api/v1/health/detailed`

**Recovery Time:** 30–60 minutes

### Rolling Back a Deployment

**Frontend (Vercel):**
```bash
vercel ls
vercel rollback [deployment-url]
```

**Backend (Render):**
- Manual Deploy → Deploy a specific commit → Select last known good

**Verify:**
```bash
curl https://contentforge-ai-api.onrender.com/api/v1/health
```

**Recovery Time:** 5–10 minutes

### Scaling for High Load

| Approach | When |
|----------|------|
| Increase Render instance type | Immediate CPU/memory pressure |
| Enable auto-scaling | Sustained traffic growth |
| Add read replicas | DB read pressure |
| Increase Redis memory | Cache eviction rate high |
| CDN optimization | Global latency issues |

---

## Deployment Procedures

### Pre-Deployment Checklist

- [ ] All tests passing (530 backend)
- [ ] CI pipelines green (4/4)
- [ ] Staging deployment verified
- [ ] Database migrations reviewed
- [ ] Environment variables documented
- [ ] Rollback plan prepared
- [ ] Caches ready to flush if needed

### Deployment Steps

1. **Create deployment tag:**
   ```bash
   git tag -a v1.x.x -m "Release v1.x.x"
   git push origin v1.x.x
   ```

2. **CI/CD runs automatically** on self-hosted runner (srv1503460):
   - Backend tests (530 tests)
   - Frontend build + lint
   - Security scanning
   - Deploy on push to main

3. **Post-Deployment Verification:**
   - Monitor Sentry for new errors
   - Check health endpoints
   - Verify cache hit rates
   - Check SLA compliance
   - Monitor slow request logs

---

## Backup and Recovery

### Automated Backups

| Backup Type | Schedule | Retention | Storage |
|-------------|----------|-----------|---------|
| Daily incremental | 2:00 AM UTC | 30 days | Cloudflare R2 |
| Weekly full | Sunday 3:00 AM UTC | 90 days | Cloudflare R2 |
| Backup cleanup | Monday 4:00 AM UTC | Per retention policy | — |

### Manual Backup

```bash
./scripts/backup-database.sh --daily
./scripts/backup-database.sh --weekly
./scripts/backup-database.sh --verify
```

### Backup Monitoring

- Failure notifications via Resend email
- Backup logs in `logs/` directory
- Integrity verification via `--verify` flag
- Cron job monitoring (see CRON_JOBS.md)

---

## Security Incidents

### Current Security Status

- **9/9 HIGH/CRITICAL findings** remediated
- Security pipeline: 8 scans pass, 5 expected infra failures
- All SARIF results uploaded to GitHub Security tab
- See `SECURITY_PIPELINE.md` for full details

### API Key Compromise

1. Revoke compromised keys
2. Rotate all API keys
3. Update environment variables
4. Redeploy services
5. Review access logs

### DDoS Attack

1. Enable Cloudflare "Under Attack" mode
2. Verify rate limiting is active
3. Contact hosting provider
4. Implement IP blocking if needed

### Data Breach

1. Isolate affected systems
2. Revoke all sessions
3. Force password resets
4. Audit access logs
5. Notify affected users within 72 hours (GDPR)

---

## Emergency Contacts

| Role | Contact |
|------|---------|
| Executive Agent | @neo-me-no-bot:matrix.org |
| On-Call Engineer | TBD |
| Stripe Support | https://support.stripe.com |
| Supabase Support | https://supabase.com/support |
| Render Support | https://render.com/support |
| Vercel Support | https://vercel.com/support |

---

## Appendix

### Environment Variables Reference

```bash
# Core
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_SERVICE_ROLE_KEY=
GROQ_API_KEY=
REDIS_URL=

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

---

*Last updated: 2026-04-14*  
*Version: 2.0*  
*CI: 4/4 green (srv1503460) | Tests: 530 | Caches: 9 endpoints*