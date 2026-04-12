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

---

## Prerequisites

Before deploying, ensure you have:

1. **Vercel Account** - Sign up at [vercel.com](https://vercel.com)
2. **Render Account** - Sign up at [render.com](https://render.com)
3. **Supabase Project** - Create at [supabase.com](https://supabase.com)
4. **Cloudflare Account** - For R2 storage at [cloudflare.com](https://dash.cloudflare.com)
5. **API Keys Ready:**
   - Groq API key ([console.groq.com](https://console.groq.com))
   - Resend API key ([resend.com](https://resend.com))
   - Stripe API keys ([dashboard.stripe.com](https://dashboard.stripe.com))

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

#### Option C: Using Deploy Script

```bash
# Navigate to project root
cd /path/to/contentforge-ai

# Run deployment script
./scripts/deploy-frontend.sh

# For production deployment
./scripts/deploy-frontend.sh --prod
```

---

## Production Deployment

### Step 1: Create Production Environment File

```bash
# Copy and configure production variables
cp .env.production .env.production.local
```

Update all `your_*` placeholders with actual values.

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

Or use the deploy script:
```bash
./scripts/deploy-frontend.sh --prod
```

---

## Required Environment Variables

### Frontend (Vercel)

| Variable | Description | Source |
|----------|-------------|--------|
| `NEXT_PUBLIC_APP_URL` | Public app URL | Vercel dashboard |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | Supabase settings |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key | Supabase settings |

### Backend (Render)

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Supabase project URL | ✅ Yes |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service key | ✅ Yes |
| `GROQ_API_KEY` | Groq API key | ✅ Yes |
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
| `REDIS_URL` | Redis connection string | ✅ Auto-generated |
| `JWT_SECRET_KEY` | JWT signing key | ✅ Auto-generated |
| `ENCRYPTION_KEY` | Data encryption key | ✅ Auto-generated |

---

## Post-Deployment Verification

### Backend Health Check

```bash
# Check API health
curl https://contentforge-ai-api.onrender.com/api/v1/health

# Expected response:
# {"status":"healthy","timestamp":"...","version":"1.0.0"}
```

### Frontend Verification

```bash
# Check frontend loads
curl -I https://contentforge-ai.vercel.app

# Expected: HTTP 200 OK
```

### API Documentation

Access interactive API docs at:
- **Swagger UI**: `https://contentforge-ai-api.onrender.com/docs`
- **ReDoc**: `https://contentforge-ai-api.onrender.com/redoc`

---

## Deployment Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `./scripts/deploy-frontend.sh` | Deploy Next.js to Vercel | `./scripts/deploy-frontend.sh [--prod]` |
| `./scripts/deploy-backend.sh` | Deploy FastAPI to Render | `./scripts/deploy-backend.sh [--apply]` |

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

## Troubleshooting

### Backend Issues

| Issue | Solution |
|-------|----------|
| Build fails | Check `render.yaml` syntax; verify Dockerfile exists |
| Health check fails | Ensure `/api/v1/health` endpoint responds with 200 |
| Environment variables not set | Check Render dashboard → Environment tab |
| Redis connection error | Verify `REDIS_URL` is correctly set from service |

### Frontend Issues

| Issue | Solution |
|-------|----------|
| Build fails | Check `vercel.json` syntax; verify `package.json` exists |
| API calls fail | Verify `BACKEND_API_URL` is correctly set |
| Environment variables undefined | Check Vercel dashboard → Settings → Environment Variables |
| 404 on API routes | Ensure rewrites are configured in `vercel.json` |

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
- Frontend: Check Vercel dashboard for analytics

---

*Last updated: 2026-04-12*
