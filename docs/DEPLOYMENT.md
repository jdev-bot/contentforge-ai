# ContentForge AI - Deployment Guide

> Complete step-by-step deployment guide for staging and production environments.

## Overview

ContentForge AI uses a split deployment architecture:

| Component | Platform | URL Pattern |
|-----------|----------|-------------|
| Frontend | Vercel | `https://contentforge-ai.vercel.app` |
| Backend API | Render | `https://contentforge-ai-api.onrender.com` |
| Redis | Render | Internal service |
| Database | Supabase | Cloud-hosted PostgreSQL |
| File Storage | Cloudflare R2 | Cloud object storage |

**Tech Stack:** Python 3.13 · Node v22.22.2 · FastAPI · Next.js 14

---

## Prerequisites

### System Requirements

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.13+ | Backend runtime |
| Node.js | v22.22.2+ | Frontend build |
| Docker | 20.10+ | Container runtime (local dev) |
| Git | 2.40+ | Source control |

### Accounts Required

1. **Vercel Account** — Sign up at [vercel.com](https://vercel.com)
2. **Render Account** — Sign up at [render.com](https://render.com)
3. **Supabase Project** — Create at [supabase.com](https://supabase.com)
4. **Cloudflare Account** — For R2 storage at [cloudflare.com](https://dash.cloudflare.com)

### API Keys Required

| Key | Source | Purpose |
|-----|--------|---------|
| Groq API key | [console.groq.com](https://console.groq.com) | AI content generation (GLM-5.1) |
| Resend API key | [resend.com](https://resend.com) | Email delivery |
| Stripe API keys | [dashboard.stripe.com](https://dashboard.stripe.com) | Payment processing |
| Stripe Webhook Secret | Stripe dashboard | Webhook verification |

---

## CI/CD Pipeline

### Self-Hosted Runner

All CI/CD workflows run on a **self-hosted GitHub Actions runner**:

| Property | Value |
|----------|-------|
| Runner name | `srv1503460` |
| OS | Ubuntu 25.10 |
| Python | 3.13 (via venv at `/home/claw/actions-runner/venv`) |
| Node.js | v22.22.2 |
| Runner type | Self-hosted, Linux, x64 |

### Pipeline Status: All 4 GREEN ✅

| Workflow | File | Trigger | Description |
|----------|------|---------|-------------|
| Backend Tests | `backend-tests.yml` | `workflow_dispatch` | pytest (530 passed, 41 skipped) |
| Frontend Build | `frontend-build.yml` | `workflow_dispatch` | Next.js build + lint |
| CI/CD | `ci-cd.yml` | `workflow_dispatch` | Combined pipeline |
| Security Scan | `security.yml` | `workflow_dispatch` | TruffleHog, Bandit, pip-audit, npm audit |

### CI Configuration Notes

- All workflows use `runs-on: self-hosted`
- Python venv shared across steps (created once, reused)
- Deep system tests excluded from CI (`--ignore=tests/deep_system_test`)
- Test timeout configured to prevent hung runs
- Security scans for infra-dependent checks are non-blocking
- No `setup-python` or `setup-node` actions (pre-installed on runner)

---

## Staging Deployment

### Step 1: Environment Setup

1. Copy the production environment template:
   ```bash
   cp .env.production .env.staging
   ```

2. Update staging-specific variables in `.env.staging`:
   ```env
   NEXT_PUBLIC_APP_URL=https://contentforge-ai-staging.vercel.app
   APP_URL=https://contentforge-ai-staging.vercel.app
   BACKEND_API_URL=https://contentforge-ai-api-staging.onrender.com
   R2_BUCKET_NAME=contentforge-ai-staging
   ```

### Step 2: Deploy Backend to Render (Staging)

#### Option A: Using Render Blueprint (Recommended)

1. Go to [Render Dashboard Blueprints](https://dashboard.render.com/blueprints)
2. Click **"New Blueprint Instance"**
3. Connect your GitHub repository: `jdev-bot/contentforge-ai`
4. Render will read `render.yaml` and create services automatically

#### Option B: Manual Service Creation

1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `contentforge-ai-api-staging`
   - **Runtime**: Docker
   - **Dockerfile Path**: `./infra/docker/Dockerfile.backend`
   - **Port**: `8000`
4. Set environment variables from `.env.staging`
5. Click **"Create Web Service"**

#### Staging Backend Services

| Service | Type | Purpose | Plan |
|---------|------|---------|------|
| `contentforge-ai-api-staging` | Web Service | FastAPI backend | Free |
| `contentforge-ai-redis-staging` | Redis | Celery task queue | Free |
| `contentforge-ai-worker-staging` | Worker | Background tasks | Free |
| `contentforge-ai-scheduler-staging` | Worker | Scheduled tasks | Free |

### Step 3: Deploy Frontend to Vercel (Staging)

#### Option A: Using Vercel CLI

```bash
# Install Vercel CLI if not already installed
npm install -g vercel

# Login to Vercel
vercel login

# Deploy to staging (preview)
vercel

# Or deploy to production
vercel --prod
```

#### Option B: Git Integration (Recommended)

1. Push code to GitHub repository
2. Go to [Vercel Dashboard](https://vercel.com/dashboard)
3. Click **"Add New..."** → **"Project"**
4. Import your GitHub repository
5. Configure:
   - **Framework**: Next.js
   - **Build Command**: `cd src/frontend && npm run build`
   - **Output Directory**: `src/frontend/.next`
   - **Install Command**: `cd src/frontend && npm install`
6. Add environment variables from `.env.staging`
7. Click **"Deploy"**

---

## Production Deployment

### Step 1: Create Production Environment File

```bash
# Copy and configure production variables
cp .env.production.template .env.production.local
```

Update all `your_*` placeholders with actual values. **Never commit `.env.production.local` to git.**

### Step 2: Deploy Backend (Production)

Follow the same steps as staging, but with production service names:

| Service | Name |
|---------|------|
| Web Service | `contentforge-ai-api` |
| Redis | `contentforge-ai-redis` |
| Worker | `contentforge-ai-worker` |
| Scheduler | `contentforge-ai-scheduler` |

### Step 3: Deploy Frontend (Production)

```bash
# Deploy to production
vercel --prod
```

---

## Required Environment Variables

### Frontend (Vercel)

| Variable | Description | Source |
|----------|-------------|--------|
| `NEXT_PUBLIC_APP_URL` | Public app URL | Vercel dashboard |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | Supabase settings |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key | Supabase settings |

> **Note:** `NEXT_PUBLIC_GROQ_API_KEY` has been removed. Groq API calls are proxied through the backend.

### Backend (Render)

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Supabase project URL | ✅ Yes |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service key | ✅ Yes |
| `GROQ_API_KEY` | Groq API key (GLM-5.1) | ✅ Yes |
| `RESEND_API_KEY` | Resend email API | ⚠️ Email features |
| `STRIPE_SECRET_KEY` | Stripe secret key | ⚠️ Payments |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | ⚠️ Payments |
| `R2_ACCOUNT_ID` | Cloudflare account ID | ✅ Yes |
| `R2_ACCESS_KEY_ID` | R2 access key | ✅ Yes |
| `R2_SECRET_ACCESS_KEY` | R2 secret key | ✅ Yes |
| `R2_BUCKET_NAME` | R2 bucket name | ✅ Yes |
| `R2_PUBLIC_URL` | R2 public URL | ✅ Yes |
| `N8N_WEBHOOK_URL` | n8n webhook URL | ⚠️ Workflows |
| `N8N_API_KEY` | n8n API key | ⚠️ Workflows |
| `REDIS_URL` | Redis connection string (with auth) | ✅ Auto-generated |
| `REDIS_PASSWORD` | Redis authentication password | ✅ Yes |
| `JWT_SECRET_KEY` | JWT signing key | ✅ Auto-generated |
| `ENCRYPTION_KEY` | Data encryption key | ✅ Auto-generated |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | ✅ Yes |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiry | ⚠️ Default: 10080 |

---

## Post-Deployment Verification

### Backend Health Check

```bash
# Check API health
curl https://contentforge-ai-api.onrender.com/api/v1/health

# Expected response:
# {"status":"healthy","timestamp":"...","version":"2.0.0"}
```

### Frontend Verification

```bash
# Check frontend loads
curl -I https://contentforge-ai.vercel.app

# Expected: HTTP 200 OK
```

### Performance Headers Check

```bash
# Verify middleware headers
curl -v https://contentforge-ai-api.onrender.com/api/v1/health 2>&1 | grep -E "X-Response-Time|X-Request-ID|X-RateLimit|ETag"
```

Expected headers:
- `X-Response-Time: <n>ms`
- `X-Request-ID: <uuid>`
- `X-RateLimit-Limit: <n>`
- `X-RateLimit-Remaining: <n>`

### API Documentation

Access interactive API docs at:
- **Swagger UI**: `https://contentforge-ai-api.onrender.com/docs`
- **ReDoc**: `https://contentforge-ai-api.onrender.com/redoc`

> **Note:** API docs are disabled when `DEBUG=false` (production).

---

## Deployment Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `./scripts/deploy-frontend.sh` | Deploy Next.js to Vercel | `./scripts/deploy-frontend.sh [--prod]` |
| `./scripts/deploy-backend.sh` | Deploy FastAPI to Render | `./scripts/deploy-backend.sh [--apply]` |
| `./scripts/backup-database.sh` | Database backup | `./scripts/backup-database.sh` |

---

## Rollback Procedure

### Frontend Rollback (Vercel)

```bash
# List deployments
vercel ls

# Rollback to specific deployment
vercel rollback <deployment-url>
```

Or use Vercel dashboard → Deployments → Click "..." → "Promote to Production"

### Backend Rollback (Render)

1. Go to Render dashboard → Web Service
2. Click **"Manual Deploy"** → **"Deploy a specific commit"**
3. Select the previous working commit
4. Click **"Deploy"**

---

## Security Checklist (Pre-Production)

- [x] All API keys in environment variables (no hardcoded secrets)
- [x] `.env.production` removed from git tracking
- [x] Redis authentication configured
- [x] Groq API key backend-only (not in `NEXT_PUBLIC_` env)
- [x] `pickle` deserialization replaced with JSON
- [x] RSS HTML sanitized with DOMPurify
- [x] `python-jose` replaced with `PyJWT`
- [x] `hashlib.md5` replaced with `hashlib.sha256`
- [x] Docker services use `.env` (no hardcoded credentials)
- [ ] Content Security Policy headers configured
- [ ] CORS origins narrowed to production domains
- [ ] Sentry/error tracking configured
- [ ] Rate limiting middleware activated
- [ ] Database RLS policies verified
- [ ] SSL/TLS certificates verified

---

## Troubleshooting

### Backend Issues

| Issue | Solution |
|-------|----------|
| Build fails | Check `render.yaml` syntax; verify Dockerfile exists |
| Health check fails | Ensure `/api/v1/health` endpoint responds with 200 |
| Environment variables not set | Check Render dashboard → Environment tab |
| Redis connection error | Verify `REDIS_URL` includes password: `redis://:password@host:6379/0` |
| Cache not working | Check Redis availability; in-memory fallback will activate |
| Slow requests logged | Check PerformanceMiddleware warnings (>2s) |

### Frontend Issues

| Issue | Solution |
|-------|----------|
| Build fails | Check `vercel.json` syntax; verify `package.json` exists |
| API calls fail | Verify `BACKEND_API_URL` is correctly set |
| Environment variables undefined | Check Vercel dashboard → Settings → Environment Variables |
| 404 on API routes | Ensure rewrites are configured in `vercel.json` |
| SSO login fails | Check SSO provider configuration and callback URLs |

---

## Service URLs

### Staging
- Frontend: `https://contentforge-ai-staging.vercel.app`
- Backend: `https://contentforge-ai-api-staging.onrender.com`
- API Docs: `https://contentforge-ai-api-staging.onrender.com/docs`

### Production
- Frontend: `https://contentforge-ai.vercel.app`
- Backend: `https://contentforge-ai-api.onrender.com`
- API Docs: `https://contentforge-ai-api.onrender.com/docs`

---

## Monitoring & Logs

### Vercel Logs
```bash
vercel logs --tail
```

### Render Logs
Via Render dashboard → Service → Logs

### Health Monitoring
- Backend: `/api/v1/health`
- Backend (detailed): `/api/v1/health/detailed`
- Frontend: Check Vercel dashboard for analytics

### Performance Monitoring
- `X-Response-Time` header on all API responses
- Slow request logging (>2s) via PerformanceMiddleware
- `X-Request-ID` for distributed request tracing

---

*Last updated: 2026-04-14*