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
- **Live Deploy:** `191f7ce` — **current with HEAD**
- **Deploy History:** Latest deploy triggered 2026-04-20T04:39Z, build succeeded
- **Note:** Free tier → cold starts (~30s after 15min idle). Rapid sequential requests hit 429 rate limiting after ~40 endpoints

### Vercel

- **Project ID:** `prj_LG8wzPFJVaSDwueFnorflBBwHAOc`
- **Deployment ID:** `dpl_a1fd2e07u` (latest)
- **Frontend URL:** `https://frontend-theta-seven-65.vercel.app`
- **Aliases:** `frontend-jdevs-projects-ce69c014.vercel.app`, `frontend-jdev-bot-7023-jdevs-projects-ce69c014.vercel.app`
- **Region:** `iad1`
- **Framework:** Next.js 16.2.3 (Turbopack)
- **Status:** ● Ready
- **Deployed:** Sun Apr 20 04:41 UTC (latest deploy)
- **API Proxy:** `/api/v1/*` → `https://contentforge-ai-api.onrender.com/api/v1/*` (via `vercel.json` rewrites)
- **GitHub Integration:** Enabled (auto-deploy on push)
- **Security Headers:** ✅ HSTS, X-Frame-Options: DENY, X-Content-Type-Options: nosniff, Referrer-Policy, X-Robots-Tag: noindex
- **✅ FIXED:** `trailingSlash: false` in `next.config.ts` + FastAPI `redirect_slashes=False` — no more 307 redirects

### Supabase

- **Project Name:** `contentforge-ai-staging`
- **Reference ID:** `zwbbmcbhrhlnoharfzdt`
- **Organization ID:** `nccabfbceqppywibuvpj`
- **Region:** West EU (Ireland)
- **URL:** `https://zwbbmcbhrhlnoharfzdt.supabase.co`
- **Tables existing (with row counts):** profiles(2), projects(2), content(1), error_logs(249), marketplace_templates(0), organizations(0), integrations(0), plugins(0), audit_logs(0), sso_providers(0), rss_feeds(0), dashboards(0), automation_rules(0)
- **Tables now:** 93 tables total (all migration 025 tables created successfully)
- **RLS:** All tables have RLS enabled. Service role key bypasses RLS. Anon key gets 401 on most tables (correct).
- **✅ FIXED:** RLS infinite recursion on `organizations` table (was 42P17 error)

### Self-Hosted Services (srv1503460)

| Service | Type | Purpose | Status |
|---------|------|---------|--------|
| `actions-runner.service` | GitHub Actions Self-Hosted Runner | CI pipeline | ✅ Active |

- **Local dev environment REMOVED** (2026-04-20): Local backend, Cloudflare tunnel, venv, node_modules all deleted
- All testing/deployment now against staging (Render + Vercel + Supabase) only

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

### Full Platform Scan (2026-04-20 04:43 UTC)

| Category | Count | Details |
|----------|-------|---------|
| ✅ 200 | 40 | All core endpoints responding |
| 🔀 Redirect | 0 | No 307s (fixed) |
| 🚫 403 Admin-only | 2 | `/webhooks/logs`, `/admin/errors` (correct — requires admin) |
| ⚠️ 429 Rate-limited | 3 | `/content`, `/suggestions/topics`, `/content/{id}/comments` (Render free tier) |
| ⚠️ 422 Validation | 3 | UUID validation on test paths (expected) |
| ❌ 404 | 0 | All previously-missing routes now served via aliases |

### Supabase Database Status

- **Tables:** 93 total (all migration 025 tables present)
- **RLS:** Enabled on all tables
- **All previously-missing tables created:** webhook_logs, quality_scores, user_profiles, seo_analyses, tone_adjustments, marketplace_installs, marketplace_ratings, marketplace_template_versions, saml_providers, saml_identities, saml_states, auto_suggestions, ai_editor_history, collaboration_edits, presence, comment_mentions, comment_reactions, publishing_queue, automation_logs, webhook_endpoints, assets, analytics, funnels, funnel_events, attribution_touchpoints, sla_policies, sla_metrics, sla_alerts, integration_configs, integration_events, integration_logs, trash, content_freshness_scores, trending_topics, user_topic_interests, trend_content_suggestions, content_topics, in_app_notifications, integrations, webhook_deliveries

### Error Logs Analysis (historical — 249 entries from before fixes)

---

## Bug Inventory (Prioritized)

### 🔴 CRITICAL

| # | Bug | Impact | Status |
|---|-----|--------|--------|
| C1 | **RLS infinite recursion on `organizations`** | Organizations feature broken (42P17) | ✅ Fixed |
| C2 | **Vercel 307 trailing-slash redirect strips Auth headers** | Frontend API calls lose auth → 401 | ✅ Fixed |
| C3 | **Render behind HEAD** | API fixes not deployed | ✅ Fixed (deploy `191f7ce` live) |

### 🟠 HIGH

| # | Bug | Impact | Fix |
|---|-----|--------|-----|
| H1 | **9 missing Supabase tables** | Notifications, comments, SLA, webhooks features all 500/404 | ✅ Fixed — migration 025 created all 35 missing tables |
| H2 | **Marketplace DB schema bugs** | `/marketplace/tags` 500 (no `tags` column), `/marketplace/templates/trending` 500 (`install_count` vs `download_count`) | ✅ `/marketplace/tags` and `/marketplace/templates/trending` now return 200 |
| H3 | **Frontend→Backend route mismatches** | 15 path naming differences + 12 missing routes cause 404s | ✅ Fixed — 7 aliases + 9 missing routes added, deployed |
| H4 | **`/freshness/stale` returns 500** | Freshness monitoring broken | ✅ Fixed — now returns 200 |

### 🟡 MEDIUM

| # | Bug | Impact | Fix |
|---|-----|--------|-----|
| M1 | **3 POST-only endpoints (405 on GET)** | `categorization/categories`, `sla/metrics`, `attribution/touchpoints` | Add GET handlers or update frontend to use existing routes |
| M2 | **`/webhooks/logs` returns 403** | Non-admin users blocked | ✅ Correct — requires admin role |
| M3 | **`status` import shadow in health.py, stripe.py** | Potential status code comparison bugs | Rename `status` → `http_status` |

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

- **Local HEAD:** `48dc458` (fix: Pydantic model for rss bulk-import request body)
- **Remote HEAD:** `48dc458` (in sync)
- **Render live:** `48dc458` (current ✅)
- **Vercel deploy:** latest (deployed 2026-04-20 08:09 UTC ✅)

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

*Last updated: 2026-04-20 08:10 UTC | Route mismatch fixes deployed — 7 aliases + 9 missing routes added*