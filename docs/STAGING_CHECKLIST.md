# ContentForge AI - Staging Deployment Checklist

> Pre-deployment verification checklist for staging environment.

---

## Pre-Deployment: Code Readiness

### Repository Status

- [ ] Code is on `main` branch and pushed to GitHub
- [ ] All tests pass locally: `npm test` (frontend) / `pytest` (backend)
- [ ] No uncommitted changes: `git status` shows clean working tree
- [ ] Latest changes pulled: `git pull origin main` completed

### Configuration Files Check

- [ ] `render.yaml` exists and syntax is valid
- [ ] `vercel.json` exists and syntax is valid
- [ ] `docker-compose.yml` exists for local testing
- [ ] `.env.staging` file created from `.env.production`
- [ ] `.env.staging` has all placeholders replaced with actual values

### Required Files Presence

- [ ] `src/backend/requirements.txt` exists
- [ ] `src/backend/app/main.py` exists
- [ ] `infra/docker/Dockerfile.backend` exists
- [ ] `src/frontend/package.json` exists
- [ ] `src/frontend/next.config.js` or `next.config.ts` exists

---

## Environment Variables Setup

### Frontend (Vercel) - Required

| Variable | Status | Notes |
|----------|--------|-------|
| `NEXT_PUBLIC_APP_URL` | [ ] Set | Staging URL: `https://contentforge-ai-staging.vercel.app` |
| `NEXT_PUBLIC_SUPABASE_URL` | [ ] Set | From Supabase dashboard |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | [ ] Set | From Supabase dashboard |

### Backend (Render) - Required

| Variable | Status | Notes |
|----------|--------|-------|
| `SUPABASE_URL` | [ ] Set | Same as frontend |
| `SUPABASE_SERVICE_ROLE_KEY` | [ ] Set | From Supabase dashboard |
| `GROQ_API_KEY` | [ ] Set | From Groq console |
| `R2_ACCOUNT_ID` | [ ] Set | From Cloudflare dashboard |
| `R2_ACCESS_KEY_ID` | [ ] Set | From Cloudflare R2 |
| `R2_SECRET_ACCESS_KEY` | [ ] Set | From Cloudflare R2 |
| `R2_BUCKET_NAME` | [ ] Set | `contentforge-ai-staging` |
| `R2_PUBLIC_URL` | [ ] Set | R2 bucket public URL |

### Backend (Render) - Optional but Recommended

| Variable | Status | Notes |
|----------|--------|-------|
| `RESEND_API_KEY` | [ ] Set | For email notifications |
| `STRIPE_SECRET_KEY` | [ ] Set | For payment features |
| `STRIPE_WEBHOOK_SECRET` | [ ] Set | For Stripe webhooks |
| `N8N_WEBHOOK_URL` | [ ] Set | For workflow automation |
| `N8N_API_KEY` | [ ] Set | For n8n integration |

### Auto-Generated Variables (Render)

| Variable | Status | Notes |
|----------|--------|-------|
| `REDIS_URL` | [ ] Auto | Render generates from Redis service |
| `JWT_SECRET_KEY` | [ ] Auto | Render generates automatically |
| `ENCRYPTION_KEY` | [ ] Auto | Render generates automatically |

---

## Third-Party Service Setup

### Supabase (Database + Auth)

- [ ] Supabase project created
- [ ] Database schema deployed
- [ ] Authentication enabled
- [ ] Row Level Security (RLS) policies configured
- [ ] API keys copied to environment variables

### Cloudflare R2 (File Storage)

- [ ] R2 bucket created: `contentforge-ai-staging`
- [ ] Access keys generated
- [ ] Public access configured (if needed)
- [ ] CORS rules configured

### Groq (AI Processing)

- [ ] Groq account created
- [ ] API key generated
- [ ] API key added to environment variables

### Resend (Email - Optional)

- [ ] Resend account created
- [ ] API key generated
- [ ] Domain verified (for production)

### Stripe (Payments - Optional)

- [ ] Stripe account created
- [ ] Secret key generated
- [ ] Webhook endpoint configured
- [ ] Webhook secret copied

---

## Backend Deployment Steps

### Pre-Deploy

- [ ] Docker builds locally without errors:
  ```bash
  docker build -f infra/docker/Dockerfile.backend -t contentforge-ai-backend:test .
  ```
- [ ] `render.yaml` syntax validated (use `yq` if available)

### Deploy to Render

- [ ] Go to [Render Dashboard Blueprints](https://dashboard.render.com/blueprints)
- [ ] Click "New Blueprint Instance"
- [ ] Connect GitHub repository: `jdev-bot/contentforge-ai`
- [ ] Render blueprint successfully creates services:
  - [ ] `contentforge-ai-api-staging` (Web Service)
  - [ ] `contentforge-ai-redis-staging` (Redis)
  - [ ] `contentforge-ai-worker-staging` (Worker)
  - [ ] `contentforge-ai-scheduler-staging` (Worker)

### Post-Deploy Backend Verification

- [ ] Web service shows "Live" status
- [ ] Health check passes:
  ```bash
  curl https://contentforge-ai-api-staging.onrender.com/api/v1/health
  ```
- [ ] API documentation loads:
  ```bash
  curl https://contentforge-ai-api-staging.onrender.com/docs
  ```
- [ ] No critical errors in service logs
- [ ] Worker service is running (check logs)

---

## Frontend Deployment Steps

### Pre-Deploy

- [ ] Dependencies install without errors:
  ```bash
  cd src/frontend && npm install
  ```
- [ ] Build completes successfully:
  ```bash
  cd src/frontend && npm run build
  ```
- [ ] Linting passes:
  ```bash
  cd src/frontend && npm run lint
  ```

### Deploy to Vercel

- [ ] Vercel CLI installed: `npm install -g vercel`
- [ ] Logged in to Vercel: `vercel login`
- [ ] Project linked to Vercel (or created new project)
- [ ] Environment variables configured in Vercel dashboard
- [ ] Deployment triggered (via CLI or Git push)

### Post-Deploy Frontend Verification

- [ ] Deployment shows "Ready" status
- [ ] Homepage loads without errors
- [ ] API proxy works (test backend connection)
- [ ] Authentication flows work (if implemented)
- [ ] No console errors in browser developer tools

---

## Integration Tests

### API Connectivity

- [ ] Frontend can reach backend API
- [ ] CORS properly configured (if testing from local)
- [ ] API key authentication works

### Database Connectivity

- [ ] Backend can connect to Supabase
- [ ] Database migrations run successfully
- [ ] Basic CRUD operations work

### External Services

- [ ] Groq API calls succeed
- [ ] R2 file upload/download works
- [ ] Email sending works (if Resend configured)
- [ ] Stripe webhooks receive correctly (if configured)

---

## Security Checks

- [ ] No sensitive data in code (check for API keys in repo)
- [ ] Environment variables marked as secret in Render/Vercel
- [ ] CORS origins restricted to known domains
- [ ] JWT secrets are strong and unique
- [ ] Database has proper access controls
- [ ] R2 bucket has appropriate access policies

---

## Monitoring Setup

- [ ] Health check endpoint responding: `/api/v1/health`
- [ ] Render service alerts configured (if desired)
- [ ] Vercel analytics enabled (optional)
- [ ] Error tracking configured (Sentry - optional)

---

## Documentation

- [ ] `DEPLOYMENT.md` is up to date
- [ ] Service URLs documented
- [ ] Environment variables documented
- [ ] Rollback procedure known

---

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| DevOps Engineer | | | |
| Backend Engineer | | | |
| Frontend Engineer | | | |
| QA Engineer | | | |

---

## Post-Staging: Next Steps

Once staging deployment is verified:

1. [ ] Share staging URLs with team
2. [ ] Run full integration test suite
3. [ ] Performance testing (if applicable)
4. [ ] Prepare production deployment plan
5. [ ] Schedule production deployment window

---

## Staging URLs Reference

| Service | URL |
|---------|-----|
| Frontend | `https://contentforge-ai-staging.vercel.app` |
| Backend API | `https://contentforge-ai-api-staging.onrender.com` |
| API Docs | `https://contentforge-ai-api-staging.onrender.com/docs` |
| Health Check | `https://contentforge-ai-api-staging.onrender.com/api/v1/health` |

---

## Emergency Contacts / Escalation

| Platform | Support Link |
|----------|--------------|
| Vercel | [vercel.com/help](https://vercel.com/help) |
| Render | [render.com/docs](https://render.com/docs) |
| Supabase | [supabase.com/support](https://supabase.com/support) |
| Cloudflare | [support.cloudflare.com](https://support.cloudflare.com) |

---

*Checklist Version: 1.0*  
*Last Updated: 2026-04-12*
