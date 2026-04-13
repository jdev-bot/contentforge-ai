# ContentForge AI - Production Deployment Checklist

## Deployment Summary

**Version:** v2.0.0 - Feature Complete Release  
**Date:** April 13, 2026  
**Status:** ⏳ READY FOR MANUAL DEPLOYMENT

**Completed:**
- ✅ All code changes pushed to origin/main
- ✅ Release tag v2.0.0 created and pushed
- ✅ Deployment checklist created
- ✅ All configuration files validated

**Next Steps (Manual):**
1. Configure environment variables in Render Dashboard
2. Deploy backend services via Render Blueprint
3. Configure environment variables in Vercel Dashboard  
4. Deploy frontend via Vercel
5. Run smoke tests
6. Monitor error rates

**Estimated Time:** 15-30 minutes for manual deployment

---

**Version:** v2.0.0 - Feature Complete Release  
**Date:** April 13, 2026  
**Status:** IN PROGRESS

---

## 1. Pre-Deployment Checks ✅

### 1.1 Code Repository
- [x] **Branch:** `main`
- [x] **Latest Commit:** `79858a8` - feat: add content performance alerts
- [x] **Commit History:** Reviewed - 20 commits from latest
- [x] **Git Status:** Working tree clean, no uncommitted changes
- [x] **Push Status:** ✅ All commits pushed to origin/main

### 1.2 Project Structure Verification
| Component | Status | Path |
|-----------|--------|------|
| Backend | ✅ Ready | `src/backend/app/main.py` |
| Frontend | ✅ Ready | `src/frontend/` (Next.js 16.2.3) |
| Docker Config | ✅ Ready | `infra/docker/Dockerfile.backend` |
| Render Blueprint | ✅ Ready | `render.yaml` |
| Vercel Config | ✅ Ready | `vercel.json` |
| Tests | ✅ Ready | `tests/` (13 test suites) |
| CI/CD | ✅ Ready | `.github/workflows/` |

### 1.3 Configuration Files Validated
- [x] `render.yaml` - Valid blueprint with web service, Redis, worker, scheduler
- [x] `vercel.json` - Next.js config with API rewrites to backend
- [x] `docker-compose.yml` - Full local development stack
- [x] `.env.production` - Template with all required variables documented

### 1.4 Test Status
- [x] Test suites present (13 test files)
- [x] CI/CD pipeline configured
- [x] Tests require environment variables for local execution
- [ ] Tests pass in CI/CD (requires push to trigger)

---

## 2. Environment Setup 🔄

### 2.1 Production Environment Variables

#### Backend (Render) - Required
| Variable | Status | Source |
|----------|--------|--------|
| SUPABASE_URL | ⚠️ Required | Supabase Dashboard |
| SUPABASE_SERVICE_ROLE_KEY | ⚠️ Required | Supabase Dashboard |
| GROQ_API_KEY | ⚠️ Required | Groq Console |
| RESEND_API_KEY | ⚠️ Required | Resend Dashboard |
| STRIPE_SECRET_KEY | ⚠️ Required | Stripe Dashboard |
| STRIPE_WEBHOOK_SECRET | ⚠️ Required | Stripe Dashboard |
| R2_ACCOUNT_ID | ⚠️ Required | Cloudflare Dashboard |
| R2_ACCESS_KEY_ID | ⚠️ Required | Cloudflare Dashboard |
| R2_SECRET_ACCESS_KEY | ⚠️ Required | Cloudflare Dashboard |
| N8N_WEBHOOK_URL | ⚠️ Required | n8n Instance |
| N8N_API_KEY | ⚠️ Required | n8n Instance |

#### Frontend (Vercel) - Required
| Variable | Status | Source |
|----------|--------|--------|
| NEXT_PUBLIC_APP_URL | ⚠️ Required | Vercel Project URL |
| NEXT_PUBLIC_SUPABASE_URL | ⚠️ Required | Supabase Dashboard |
| NEXT_PUBLIC_SUPABASE_ANON_KEY | ⚠️ Required | Supabase Dashboard |

#### Auto-Generated (Render)
- [x] JWT_SECRET_KEY - Auto-generated
- [x] ENCRYPTION_KEY - Auto-generated
- [x] REDIS_URL - From Redis service

### 2.2 Database Migrations
- [x] Migrations directory: `src/backend/migrations/`
- [x] Supabase schema configured
- [ ] Run migrations on deployment (auto via Render)

### 2.3 Redis Configuration
- [x] Redis service defined in render.yaml
- [x] Celery worker configured
- [x] Celery beat scheduler configured

### 2.4 CDN Setup
- [x] Cloudflare R2 configured for file storage
- [x] R2_PUBLIC_URL configured in .env.production

---

## 3. Deployment Steps 🚀

### 3.1 Pre-Deployment Actions ✅
- [x] Create deployment checklist
- [x] Push commits to origin/main (3 commits pushed: c97bcea..79858a8)
- [x] Create and push git tag v2.0.0
- [ ] Verify GitHub Actions pipeline triggers

### 3.2 Backend Deployment (Render) ⬜ MANUAL DEPLOYMENT REQUIRED

> **Status:** CLI not available. Manual deployment via Render Dashboard required.

#### Render Dashboard Deployment Steps
1. Go to https://dashboard.render.com/blueprints
2. Click "New Blueprint Instance"
3. Connect GitHub repository: `jdev-bot/contentforge-ai`
4. Select `render.yaml` blueprint
5. Configure environment variables in dashboard (see Section 2.1)
6. Click "Apply" to deploy

#### Services to Deploy
| Service | Type | Plan | Health Check | Status |
|---------|------|------|--------------|--------|
| contentforge-ai-api | Web | Free | /api/v1/health | ⬜ Pending |
| contentforge-ai-redis | Redis | Free | - | ⬜ Pending |
| contentforge-ai-worker | Worker | Free | - | ⬜ Pending |
| contentforge-ai-scheduler | Worker | Free | - | ⬜ Pending |

### 3.3 Frontend Deployment (Vercel) ⬜ MANUAL DEPLOYMENT REQUIRED

> **Status:** CLI not available. Manual deployment via Vercel Dashboard required.

#### Vercel Dashboard Deployment Steps
1. Go to https://vercel.com/dashboard
2. Click "Add New Project"
3. Import GitHub repository: `jdev-bot/contentforge-ai`
4. Configure build settings:
   - **Framework Preset:** Next.js
   - **Build Command:** `cd src/frontend && npm run build`
   - **Output Directory:** `src/frontend/.next`
   - **Install Command:** `cd src/frontend && npm install`
5. Add environment variables (see Section 2.1 Frontend vars)
6. Click "Deploy"

#### Expected Vercel Settings
| Setting | Value |
|---------|-------|
| Framework | Next.js |
| Node Version | 20.x |
| Build Command | `cd src/frontend && npm run build` |
| Output Directory | `src/frontend/.next` |
| Install Command | `cd src/frontend && npm install` |

### 3.4 Database Migrations
- [ ] Verify Supabase migrations run automatically
- [ ] Run manual migrations if needed:
  ```bash
  # Connect to Supabase and run migrations
  supabase db push
  ```

### 3.5 Post-Deployment Verification
- [ ] Backend health endpoint: `https://contentforge-ai-api.onrender.com/api/v1/health`
- [ ] API docs: `https://contentforge-ai-api.onrender.com/docs`
- [ ] Frontend: `https://contentforge-ai.vercel.app`
- [ ] Login page: `https://contentforge-ai.vercel.app/login`

---

## 4. Post-Deployment ✅

### 4.1 Smoke Tests

#### API Health Endpoints
```bash
# Basic health check
curl https://contentforge-ai-api.onrender.com/api/v1/health
# Expected: {"status": "healthy", "timestamp": "...", "version": "0.1.0"}

# Detailed health check
curl https://contentforge-ai-api.onrender.com/api/v1/health/detailed
# Expected: Full component status (database, redis, groq, stripe, n8n)

# API Docs
curl https://contentforge-ai-api.onrender.com/docs
# Expected: Swagger UI HTML
```

#### Frontend Tests
```bash
# Login page load test
curl https://contentforge-ai.vercel.app/login
# Expected: HTML with login form

# Dashboard redirect (unauthenticated)
curl https://contentforge-ai.vercel.app/
# Expected: Redirect to /login
```

### 4.2 Feature Verification Checklist
- [ ] User registration/login
- [ ] Content creation and management
- [ ] Project management
- [ ] Distribution scheduling
- [ ] Analytics dashboard
- [ ] AI content generation
- [ ] Trash/Recycle bin
- [ ] Search functionality (Ctrl+K)
- [ ] Keyboard shortcuts
- [ ] Onboarding guide
- [ ] Payment integration (Stripe)
- [ ] Email notifications (Resend)
- [ ] Webhook processing

### 4.3 Performance Metrics
- [ ] Backend response time < 500ms (p95)
- [ ] Frontend First Contentful Paint < 1.5s
- [ ] API error rate < 0.1%
- [ ] Database query time < 100ms (p95)

### 4.4 Error Monitoring
- [ ] Configure Render health check alerts
- [ ] Set up Vercel analytics
- [ ] Add uptime monitoring (UptimeRobot/Pingdom)
- [ ] Configure error tracking (Sentry) - Optional

---

## 5. Rollback Plan 🔄

### 5.1 Rollback Procedure

#### Frontend Rollback (Vercel)
```bash
# Rollback to previous deployment
vercel --rollback

# Or via dashboard:
# 1. Go to https://vercel.com/dashboard
# 2. Select project
# 3. Go to "Deployments" tab
# 4. Find previous working deployment
# 5. Click "..." -> "Promote to Production"
```

#### Backend Rollback (Render)
```bash
# Via Render CLI
render deploy rollback --service contentforge-ai-api

# Or via dashboard:
# 1. Go to https://dashboard.render.com/
# 2. Select service
# 3. Go to "Deploys" tab
# 4. Select previous commit
# 5. Click "Manual Deploy"
```

### 5.2 Database Rollback
- [ ] Supabase point-in-time recovery configured
- [ ] Database backups enabled
- [ ] Migration rollback scripts prepared (if needed)

### 5.3 Emergency Contacts
- Render Support: https://render.com/help
- Vercel Support: https://vercel.com/help
- Supabase Support: https://supabase.com/support

---

## 6. Post-Deployment URLs 📎

| Service | URL | Status |
|---------|-----|--------|
| Production Frontend | https://contentforge-ai.vercel.app | ⬜ Awaiting Deployment |
| Production API | https://contentforge-ai-api.onrender.com | ⬜ Awaiting Deployment |
| API Documentation | https://contentforge-ai-api.onrender.com/docs | ⬜ Awaiting Deployment |
| Health Endpoint | https://contentforge-ai-api.onrender.com/api/v1/health | ⬜ Awaiting Deployment |

---

## 7. Sign-off ✅

| Role | Name | Status | Date |
|------|------|--------|------|
| DevOps Engineer | Agent | ✅ Pre-Deployment Complete | 2026-04-13 |
| QA Engineer | - | ⬜ Pending Deployment | - |
| Product Owner | - | ⬜ Pending Deployment | - |

---

## 8. Notes

### Known Issues / Blockers
1. **Manual Deployment Required:** Render CLI and Vercel CLI require interactive authentication
2. **Environment Variables:** Must be manually configured in platform dashboards
3. **No CI/CD Tokens:** RENDER_API_KEY and VERCEL_TOKEN not configured in GitHub secrets

### Deployment Blockers Status
1. ✅ **RESOLVED:** Commits pushed to origin/main (c97bcea..79858a8)
2. ✅ **RESOLVED:** Release tag v2.0.0 pushed to origin
3. ⏳ **PENDING:** Manual deployment via dashboards (CLI auth not available)
4. ⏳ **PENDING:** Environment variables configuration in Render/Vercel

### CI/CD Improvements for Future
- [ ] Add RENDER_API_KEY to GitHub secrets
- [ ] Add VERCEL_TOKEN to GitHub secrets
- [ ] Add automated smoke tests post-deployment
- [ ] Configure staging/production promotion workflow
- [ ] Add deployment status notifications (Slack/Discord)

---

*Document created by DevOps Engineer Agent*  
*ContentForge AI - Neo DevOrg*
