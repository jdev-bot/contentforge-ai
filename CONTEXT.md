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
- **Live Deploy:** `7e4d79c` — **5 commits behind HEAD** (local HEAD = `25ae004`)
- **Deploy History:** 1 Live, 2 Inactive, 8 "Update Failed", 2 more Inactive
- **Note:** Free tier → cold starts (~30s after 15min idle). Rapid sequential requests hit 502 after ~8 endpoints (rate limiting/cold start)

### Vercel

- **Project ID:** `prj_LG8wzPFJVaSDwueFnorflBBwHAOc`
- **Deployment ID:** `dpl_9KB8H42RQXY3FPwWPw48roAtuwYf`
- **Frontend URL:** `https://frontend-theta-seven-65.vercel.app`
- **Aliases:** `frontend-jdevs-projects-ce69c014.vercel.app`, `frontend-jdev-bot-7023-jdevs-projects-ce69c014.vercel.app`
- **Region:** `iad1`
- **Framework:** Next.js
- **Status:** ● Ready
- **Deployed:** Wed Apr 15 06:24 UTC (~13h ago)
- **API Proxy:** `/api/v1/*` → `https://contentforge-ai-api.onrender.com/api/v1/*` (via `vercel.json` rewrites)
- **GitHub Integration:** Enabled (auto-deploy on push)
- **Security Headers:** ✅ HSTS, X-Frame-Options: DENY, X-Content-Type-Options: nosniff, Referrer-Policy, X-Robots-Tag: noindex
- **⚠️ BUG:** No `trailingSlash: false` in `next.config.ts` → Vercel 307 redirects on paths without trailing slash, stripping `Authorization` headers

### Supabase

- **Project Name:** `contentforge-ai-staging`
- **Reference ID:** `zwbbmcbhrhlnoharfzdt`
- **Organization ID:** `nccabfbceqppywibuvpj`
- **Region:** West EU (Ireland)
- **URL:** `https://zwbbmcbhrhlnoharfzdt.supabase.co`
- **Tables existing (with row counts):** profiles(2), projects(2), content(1), error_logs(249), marketplace_templates(0), organizations(0), integrations(0), plugins(0), audit_logs(0), sso_providers(0), rss_feeds(0), dashboards(0), automation_rules(0)
- **Tables MISSING (404 from PostgREST):** marketplace_categories, notifications, webhook_configs, webhook_events, comments, sla_policies, custom_dashboards, scheduler_jobs, webhook_deliveries
- **RLS:** All tables have RLS enabled. Service role key bypasses RLS. Anon key gets 401 on most tables (correct).
- **⚠️ CRITICAL BUG:** RLS infinite recursion on `organizations` table — `organizations` SELECT policy checks `organization_members`, and `organization_members` SELECT policy checks `organizations` → circular reference → 42P17 error

### Self-Hosted Services (srv1503460)

| Service | Type | Port/URL | Uptime | Status |
|---------|------|----------|--------|--------|
| `contentforge-backend.service` | systemd user service | `localhost:8000` | 20h+ | ✅ Active (enabled) |
| `cloudflared-tunnel.service` | Cloudflare Quick Tunnel | Random URL | 20h+ | ✅ Active (enabled) |

- **Backend config:** `.env.staging` (not in git — in `.gitignore`)
- **Memory:** ~150MB
- **⚠️ Known issue:** Cloudflare Quick Tunnel URL changes on every restart — need Named Tunnel for stability

---

## Test Accounts & Credentials

| Field | Value |
|-------|-------|
| **Frontend URL** | `https://frontend-theta-seven-65.vercel.app` |
| **Email** | `test@neo.dev` |
| **Password** | `Test1234!` |
| **User ID** | `9b2538b0-99e2-4e1e-8864-36ae7e6289a1` |

---

## Full Platform Scan Results (2026-04-15 19:00 UTC)

### Render Backend Health

- **Direct health check:** ✅ 200, healthy, uvicorn, x-response-time ~3ms
- **Auth login:** ✅ Works, returns JWT
- **Sequential scan:** First ~8 endpoints return 200, then 502s (Render free tier rate limiting/cold start)
- **Live commit `7e4d79c`:** Missing 5 commits including critical API path fixes

### Local Backend (port 8000) — Full Authenticated Scan (63 endpoints)

| HTTP | Count | Endpoints |
|------|-------|-----------|
| **200** | 35 | health, auth/me, content, projects, analytics/dashboard, analytics/content, dashboards, reports, competitors, alerts, marketplace/templates, rss/feeds, plugins, integrations, schedule, retention/policies, distributions, performance/overview, funnels, audience/growth, stripe/config, stripe/subscription, automation/rules, notifications/preferences, user/deletion-status, audit-logs, sso/providers, usage/summary, categorization/list, attribution/channels, sla/dashboard, sla/policies, integration-framework/configs, health/detailed, health/ready |
| **307** | 1 | /organizations (FastAPI trailing-slash redirect → strips auth headers) |
| **403** | 1 | /admin/errors (requires admin role) |
| **404** | 12 | analytics/overview, quality/scores, suggestions, custom-dashboards, performance/metrics, notifications, version-history, comments, admin/stats, scheduler/jobs, webhooks, webhook-events |
| **405** | 3 | categorization/categories (POST-only), sla/metrics (POST-only), attribution/touchpoints (POST-only) |
| **422** | 2 | content/test-id/comments (invalid UUID), content/test-id/versions (invalid UUID) |
| **500** | 3 | webhooks/logs, freshness/stale, marketplace/tags |

### Supabase Database Status

| Status | Count | Details |
|--------|-------|---------|
| **Exists with data** | 4 | profiles(2), projects(2), content(1), error_logs(249) |
| **Exists, empty** | 10 | marketplace_templates, organizations, integrations, plugins, audit_logs, sso_providers, rss_feeds, dashboards, automation_rules, error_logs |
| **Missing entirely** | 9 | marketplace_categories, notifications, webhook_configs, webhook_events, comments, sla_policies, custom_dashboards, scheduler_jobs, webhook_deliveries |

### Error Logs Analysis (249 entries)

| Error Type | Count |
|------------|-------|
| client_error | 164 |
| server_error | 49 |
| unhandled_exception | 36 |

| Status Code | Count |
|-------------|-------|
| 404 | 103 |
| 500 | 85 |
| 422 | 27 |
| 405 | 21 |
| 401 | 6 |
| 403 | 6 |
| 400 | 1 |

---

## Bug Inventory (Prioritized)

### 🔴 CRITICAL

| # | Bug | Impact | Fix |
|---|-----|--------|-----|
| C1 | **RLS infinite recursion on `organizations`** | Organizations feature completely broken (42P17 error) | Fix circular RLS: organizations policy references org_members, org_members policy references organizations. Break cycle by using `owner_id` check only in one direction. |
| C2 | **Vercel 307 trailing-slash redirect strips Auth headers** | Any frontend API call to path without trailing slash loses auth → 401 errors | Add `trailingSlash: false` to `next.config.ts` |
| C3 | **Render 5 commits behind HEAD** | Critical API path fixes not deployed to staging | Push + trigger Render deploy, or manual deploy |

### 🟠 HIGH

| # | Bug | Impact | Fix |
|---|-----|--------|-----|
| H1 | **9 missing Supabase tables** | Notifications, comments, SLA, webhooks features all 500/404 | Create missing tables via SQL migration |
| H2 | **Marketplace DB schema bugs** | `/marketplace/tags` 500 (no `tags` column), `/marketplace/templates/trending` 500 (`install_count` vs `download_count`) | Add `tags` column to `marketplace_templates`; fix `marketplace_service.py` column name |
| H3 | **64 frontend→backend route mismatches** | Frontend calls routes that don't exist or have different names | Detailed breakdown below |
| H4 | **`/freshness/stale` returns 500** | Freshness monitoring broken | Debug service code |

### 🟡 MEDIUM

| # | Bug | Impact | Fix |
|---|-----|--------|-----|
| M1 | **3 POST-only endpoints (405 on GET)** | `categorization/categories`, `sla/metrics`, `attribution/touchpoints` | Add GET handlers or update frontend to use existing routes |
| M2 | **`/webhooks/logs` returns 500** | Webhook monitoring broken | Debug webhook service |
| M3 | **`status` import shadow in health.py, stripe.py** | Potential status code comparison bugs | Rename `status` → `http_status` |
| M4 | **Cloudflare Quick Tunnel URL changes on restart** | Staging URL instability | Set up Named Tunnel |

### 🔵 LOW / FUTURE

| # | Issue | Notes |
|---|-------|-------|
| L1 | GROQ_API_KEY placeholder | AI content generation not testable yet |
| L2 | Stripe/R2/Resend keys not set | Payments, storage, email non-functional |
| L3 | Render free tier cold starts | ~30s after 15min idle |
| L4 | Redis unavailable on Render | In-memory cache fallback |
| L5 | No custom Vercel domain | Using auto-generated URL |
| L6 | No Supabase management API access token | Can't query DB via CLI |

---

## Frontend→Backend Route Mismatches (64 total, categorized)

### Category 1: Query string normalization (13 — cosmetic, likely work at runtime)

Frontend appends query params that differ from normalized comparison:
- `/analytics/export/json?days={ID}` → backend has `/analytics/export/json`
- `/analytics/export?format=csv&days={ID}` → no CSV export backend route
- `/analytics/usage?days={ID}` → backend has `/analytics/usage`
- `/comments/mentions/lookup?q={ID}` → backend has `/comments/mentions/lookup`
- `/content/comments/{ID}/reactions?emoji={ID}` → backend has `/content/comments/{ID}/reactions`
- etc.

### Category 2: Template literal parsing artifacts (8 — not real bugs)

- Routes like `/audit-logs${params.toString()` — JS template concatenation, works at runtime

### Category 3: Path naming differences (15 — REAL bugs, will 404)

| Frontend calls | Backend has |
|---------------|-------------|
| `/quality-scoring/{ID}` | `/quality/content/{ID}` |
| `/quality-scoring/batch` | `/quality/batch` |
| `/quality-scoring/{ID}/analyze` | `/quality/analyze` |
| `/quality-scoring/{ID}/history` | `/quality/history/{ID}` |
| `/freshness/metrics` | `/freshness/dashboard` |
| `/freshness/bulk-refresh` | `/freshness/bulk-analyze` |
| `/freshness/{ID}/analyze` | `/freshness/analyze/{ID}` |
| `/sentiment/{ID}` | `/sentiment/content/{ID}` |
| `/sentiment/{ID}/analyze` | `/sentiment/analyze` |
| `/sentiment/{ID}/trend` | `/sentiment/trends/{ID}` |
| `/suggestions/{ID}/accept` | `/suggestions/saved/{ID}` |
| `/suggestions/{ID}/dismiss` | No matching route |
| `/distributions/{ID}/publish-now` | `/distributions/{ID}/publish` |
| `/marketplace/featured` | `/marketplace/templates/featured` |
| `/marketplace/trending` | `/marketplace/templates/trending` |

### Category 4: Missing backend routes (12 — backend needs implementation)

| Frontend calls | No backend route |
|---------------|------------------|
| `/organizations` (list) | Only has `/{org_id}` sub-routes (missing root GET) |
| `/organizations/{ID}/invite` | Not implemented |
| `/organizations/{ID}/leave` | Not implemented |
| `/organizations/{ID}/members` | Not implemented |
| `/organizations/{ID}/members/{ID}` | Not implemented |
| `/organizations/{ID}/transfer-ownership` | Not implemented |
| `/schedule/{ID}/cancel` | Not implemented |
| `/schedule/{ID}/duplicate` | Not implemented |
| `/schedule/conflicts` | Not implemented |
| `/rss/entries/bulk-import` | Not implemented |
| `/rss/settings` | Not implemented |
| `/rss/stats` | Not implemented |

### Category 5: SAML route differences (4 — frontend has extra routes)

| Frontend calls | Backend has |
|---------------|-------------|
| `/saml/login/{ID}` | `/saml/login` |
| `/saml/logout/{ID}` | `/saml/logout` |
| `/saml/providers/available` | `/saml/available` |
| `/saml/providers/metadata/fetch` | `/saml/metadata/fetch` |

---

## Codebase Stats

- **Backend routes:** 304 total (255 GET + 49 POST/PUT/DELETE)
- **Frontend API calls:** 187 unique endpoints in `api.ts`
- **49 routers**, **34 services**
- **530 backend tests** (pytest)
- **73 React components**, **16 pages**
- **8 middleware** (Performance, RequestID, ETag, CORS, etc.)

---

## Git Status

- **Local HEAD:** `25ae004` (docs: add CONTEXT.md)
- **Remote HEAD:** `25ae004` (in sync)
- **Render live:** `7e4d79c` (5 commits behind — missing fixes)
- **Vercel deploy:** Based on latest push (should include `25ae004`)

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

*Last updated: 2026-04-15 19:10 UTC | Full tri-platform scan*