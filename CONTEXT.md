# CONTEXT.md — ContentForge AI Project Context

> **This file is the single source of truth for project context.**
> Update it whenever infrastructure, credentials, status, or key decisions change.
> Commit and push after every update. This file must never be stale.

---

## Project Overview

- **Name:** ContentForge AI
- **Type:** AI-powered content creation & management platform
- **GitHub:** https://github.com/jdev-bot/contentforge-ai (SSH: `git@github.com:jdev-bot/contentforge-ai.git`)
- **Current Phase:** Staging — bug hunting & full functionality verification
- **Started:** 2026-04-11
- **Tech Stack:** FastAPI (Python) backend + Next.js (TypeScript) frontend + Supabase (PostgreSQL + Auth)

---

## Infrastructure

### Hosting Providers

All three providers have **authenticated CLIs installed on this machine (srv1503460)**.

| Provider | Purpose | CLI | Version |
|----------|---------|-----|---------|
| **Render** | Backend API hosting | `render` | v2.15.1 |
| **Vercel** | Frontend hosting + API proxy | `vercel` | 51.2.1 |
| **Supabase** | Database + Auth | `npx supabase` | linked project |

### Render

- **Service ID:** `srv-d7fhaif7f7vs73a168a0`
- **Service Name:** `contentforge-ai-api`
- **Type:** Web Service (Python)
- **Plan:** Free
- **Backend URL:** `https://contentforge-ai-api.onrender.com`
- **Health Check:** `/api/v1/health`
- **Auto-deploy:** Yes (on push to `main`)
- **Branch:** `main`
- **Note:** Free tier → cold starts (~30s after 15min idle)

### Vercel

- **Project ID:** `prj_LG8wzPFJVaSDwueFnorflBBwHAOc`
- **Frontend URL:** `https://frontend-theta-seven-65.vercel.app`
- **Region:** `iad1`
- **Framework:** Next.js
- **API Proxy:** `/api/v1/*` → `https://contentforge-ai-api.onrender.com/api/v1/*` (via `vercel.json` rewrites)
- **GitHub Integration:** Enabled (auto-deploy on push)

### Supabase

- **Project Name:** `contentforge-ai-staging`
- **Reference ID:** `zwbbmcbhrhlnoharfzdt`
- **Organization ID:** `nccabfbceqppywibuvpj`
- **Region:** West EU (Ireland)
- **URL:** `https://zwbbmcbhrhlnoharfzdt.supabase.co`
- **Tables:** 51 created (all with RLS enabled, permissive staging policies)
- **Linked via:** `npx supabase db query --linked`
- **DB Access:** Via Supabase CLI (no psql directly)

### Self-Hosted Services (srv1503460)

The backend also runs locally as a fallback/alternative to Render:

| Service | Type | Port/URL | Status |
|---------|------|----------|--------|
| `contentforge-backend.service` | systemd user service | `localhost:8000` | ✅ Active (enabled) |
| `cloudflared-tunnel.service` | Cloudflare Quick Tunnel | Random URL (changes on restart) | ✅ Active (enabled) |

- **Backend config:** `.env.staging` (not in git — in `.gitignore`)
- **Memory:** ~150MB
- **Tunnel URL update script:** `scripts/update-tunnel-url.sh`
- **⚠️ Known issue:** Cloudflare Quick Tunnel URL changes on every restart — need Named Tunnel for stability

---

## Test Accounts & Credentials

### Staging Application Login

| Field | Value |
|-------|-------|
| **Frontend URL** | `https://frontend-theta-seven-65.vercel.app` |
| **Email** | `test@neo.dev` |
| **Password** | `Test1234!` |
| **User ID** | `9b2538b0-99e2-4e1e-8864-36ae7e6289a1` |

### Supabase

- Self-signup **disabled** (invite-only)
- `NEXT_PUBLIC_SIGNUP_ENABLED=false`

---

## Testing Infrastructure

### Headless Browser

- **Browser:** Chromium (snap) — `/snap/bin/chromium`
- **Version:** 146.0.7680.164
- **Puppeteer:** Available (requires `LD_LIBRARY_PATH` hack for snap chromium)
- **Required env for Puppeteer:**
  ```
  LD_LIBRARY_PATH=/snap/mesa-2404/1165/usr/lib/x86_64-linux-gnu
  CHROMIUM_PATH=/snap/bin/chromium
  ```
- **Prior E2E test scripts:** `/tmp/cf-e2e-v3/`, `/tmp/cf-full-e2e/`, `/tmp/cf-e2e-deep/`
- **Prior screenshots:** Login, Dashboard, all tabs, content creation, settings, mobile/tablet views

### Backend Tests

- **Framework:** pytest
- **Location:** `src/backend/tests/`
- **Current:** 530/530 passing, 41 skipped, 0 failing
- **Deep system test:** 163/164 (99.4%)
- **Run:** `cd src/backend && python -m pytest`

### CI/CD

- **4 GitHub Actions workflows** — all GREEN
- **Self-hosted runner:** srv1503460
- **Security pipeline:** All 9 HIGH/CRITICAL findings resolved

---

## API Status

### Current Endpoint Health (as of 2026-04-15 12:40 UTC)

**34/43 endpoints passing (79%)** — 0 real 500 bugs remaining.

| Status | Count | Details |
|--------|-------|---------|
| ✅ 200 | 34 | All core endpoints working |
| ❌ Test errors | 7 | Wrong paths, UUID test-id, user/account=DELETE-only |
| ❌ Real bugs | 0 | Zero remaining real bugs |

### Key Working Endpoints

`health`, `user/deletion-status`, `content` (list), `projects`, `stripe/config`, `stripe/subscription`, `usage/summary`, `trends`

### Known Non-Critical Issues

1. **GROQ_API_KEY is placeholder** → AI content generation won't work (user will provide later)
2. **Stripe/R2/Resend keys not set** → payments, storage, email non-functional (user will provide later)
3. **Render free tier cold starts** ~30s after 15min idle
4. **Redis unavailable on Render** → in-memory cache fallback
5. **No custom Vercel domain** yet
6. **`error_logs` RLS blocks inserts** → errors can't be logged to DB
7. **Cloudflare Quick Tunnel URL changes** on restart → need Named Tunnel

### Deployed But Not Yet Pushed (local fixes)

- `status` → `http_status` rename in 6 router files (alerts, automation, content, distributions, rss, search) — **needs commit & push**

---

## Project Structure

```
contentforge-ai/
├── src/
│   ├── backend/          # FastAPI Python backend
│   │   ├── app/          # Main application
│   │   ├── venv/         # Python virtualenv
│   │   └── tests/        # pytest tests (530 passing)
│   └── frontend/         # Next.js TypeScript frontend
│       ├── src/
│       │   ├── app/       # Next.js App Router pages
│       │   ├── components/ # React components (73+)
│       │   └── middleware.ts # Auth gate + staging banner
│       └── package.json
├── supabase/             # Supabase config & migrations
├── .github/workflows/    # CI/CD (4 pipelines)
├── docs/                 # Documentation
├── scripts/              # Utility scripts
├── infra/                # Infrastructure configs
├── render.yaml           # Render blueprint
├── vercel.json           # Vercel config + API proxy rewrites
├── Dockerfile            # Docker build for backend
└── docker-compose.yml    # Local development stack
```

### Key Stats

- **375 routes**, **49 routers**, **34 services**
- **530 backend tests**, **73 components**, **16 pages**
- **8 middleware** (Performance, RequestID, ETag, CORS, etc.)
- **9 cached endpoints** (Redis/in-memory, TTLs 60-300s)

---

## Current Work Focus

**Phase: Staging Bug Hunting & Full Functionality Verification**

We are systematically testing every page, feature, and API endpoint of the deployed staging application using the headless browser and API calls. The goal is to find and fix all bugs, verify all functionality is reachable, and ensure the UI is polished and complete.

### Completed Testing
- ✅ Desktop E2E: login, dashboard, all sidebar tabs, settings, content creation
- ✅ Mobile E2E: dashboard, menu, navigation
- ✅ Tablet E2E: viewport testing
- ✅ API testing: 34/43 endpoints verified
- ✅ Security audit: all findings resolved
- ✅ UI polish: dark mode, empty states, error styling, sidebar collapsible groups

### Pending Work
1. Deploy `status` → `http_status` fix (6 router files, local only)
2. Continue deep functional testing of all features
3. Verify AI content generation once GROQ_API_KEY provided
4. Verify Stripe/payment flow once Stripe account provided
5. Set up Cloudflare Named Tunnel for stable URL
6. Custom Vercel domain
7. Performance: SELECT optimizations, Redis for production

---

## Key Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-12 | No-GO for immediate monetization | 6-8 weeks to revenue-ready |
| 2026-04-13 | P0-P3 features complete, P4 planned | All launch gaps filled |
| 2026-04-13 | Multi-language → EN+DE only | Scope reduction |
| 2026-04-14 | Pivot from Render to self-hosted | Render deploy failures |
| 2026-04-15 | Pivot back to Render + self-hosted fallback | Both working now |
| 2026-04-15 | Graceful PGRST205 error handling | Return empty results vs 500 for missing tables |
| 2026-04-15 | Separate staging/production infrastructure | Same codebase, different env vars/domains |

---

## Environment Variables (Non-Secret)

| Variable | Staging Value | Notes |
|----------|--------------|-------|
| `APP_ENV` | `staging` | Controls staging banner, auth gate, robots |
| `NEXT_PUBLIC_APP_ENV` | `staging` | Frontend staging mode |
| `NEXT_PUBLIC_SIGNUP_ENABLED` | `false` | Invite-only |
| `NEXT_PUBLIC_API_URL` | `/api/v1` | Relative URL → Vercel proxy (avoids CORS) |
| `NEXT_PUBLIC_SUPABASE_URL` | `https://zwbbmcbhrhlnoharfzdt.supabase.co` | Staging DB |
| `GROQ_API_KEY` | Placeholder | User will provide later |
| `STRIPE_*` | Not set | User will provide later |

---

## How to Update This File

1. After any infrastructure change, credential update, or status shift → update relevant section
2. Commit: `git add CONTEXT.md && git commit -m "docs: update CONTEXT.md — <reason>"`
3. Push: `git push origin main`
4. This file is our memory — if it's not here, it's not known.

---

*Last updated: 2026-04-15 18:17 UTC*