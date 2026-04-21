# CONTEXT.md — ContentForge AI

> **Single source of truth.** Update after every material change. Commit + push immediately.
> If >8KB → compact. Archive resolved items to daily notes.

## Project Overview

- **Name:** ContentForge AI — AI content creation & management platform
- **GitHub:** `jdev-bot/contentforge-ai` (SSH)
- **Phase:** Staging — performance + bug fixes deployed, E2E v2 passing 99.4%
- **Tech:** FastAPI (Python) + Next.js 16 (TypeScript) + Supabase (PostgreSQL + Auth)

## Infrastructure

| Provider | Purpose | Key Info |
|----------|---------|---------|
| **Render** | Backend API | `srv-d7fhaif7f7vs73a168a0`, **Free tier**, cold starts ~30s, auto-deploy from main |
| **Vercel** | Frontend + proxy | `prj_LG8wzPFJVaSDwueFnorflBBwHAOc`, Next.js 16.2.3, deploy from `src/frontend/` |
| **Supabase** | DB + Auth | `zwbbmcbhrhlnoharfzdt`, 93 tables, all RLS enabled |

- **Backend URL:** `https://contentforge-ai-api.onrender.com`
- **Frontend URL:** `https://frontend-theta-seven-65.vercel.app`
- **API Proxy:** `/api/v1/*` → Render (via Vercel rewrites)
- **Deploy command:** `cd src/frontend && vercel --prod`

## Test Account

| Field | Value |
|-------|-------|
| Email | `test@neo.dev` |
| Password | `Test1234!` |
| User ID | `9b2538b0-99e2-4e1e-8864-36ae7e6289a1` |

## Performance Fixes (commit `8b269cf`, deployed 2026-04-21)

| Fix | Impact |
|-----|--------|
| Removed duplicate `get_user()` in ErrorTrackingMiddleware | ~400ms/request saved |
| Per-request auth caching (`request_context.py`) | Eliminates redundant Supabase calls |
| Batch `/api/v1/init` endpoint | 5-call waterfall → 1 call (60% faster) |
| Client-side stale-while-revalidate cache | Instant tab switches |
| ETag on `/init` | Conditional 304 responses |

## E2E Test Suite v2 (commit `024089a`, 163/164 pass = 99.4%)

- **16 spec files**, ~164 tests, Playwright 1.59.1
- **1 skip:** Content creation (monthly usage limit 10/10)
- Local Chromium libs: `/home/claw/.local/lib/playwright-libs/usr/lib/x86_64-linux-gnu/`

## Bug Fixes Deployed (commit `0e44d2e`, 2026-04-21)

| Bug | Fix |
|-----|-----|
| Dashboard ignores `?tab=` URL params | Added `useSearchParams` + `router.replace` on tab change |
| Project delete uses browser `confirm()` | Replaced with modal dialog (Cancel / Yes Delete) |
| E2E quality-scoring test wrong endpoint | Fixed to `POST /quality-scoring/batch` |

## Mock → Real API Wiring (commit `e82d9a9`, deployed 2026-04-21)

| Component | Status |
|-----------|--------|
| AlertsCenter | ✅ API: getAlerts, getUnreadAlertCount, acknowledge, resolve |
| AuditLogs | ✅ Already wired (getAuditLogs, getAuditLogStats) |
| SentimentDashboard | ✅ Already wired (analyzeSentiment, getSentiment, getSentimentTrend) |
| QualityDashboard | ✅ Already wired (batchAnalyzeQuality, getQualityScore) |
| IntegrationsPanel | ✅ API: listIntegrations |
| CompetitorAnalysis | ✅ API: getCompetitors (mock fallback) |
| TrendingTopics | ✅ API: getTrendingTopics, generateFromTrend |
| TeamCalendar | 🔶 Demo Data badge (no backend) |
| EngagementPrediction | 🔶 Demo Data badge (no backend) |

Added: PageHeader `badge` prop, alerts + competitors API functions in api.ts

## Pending Issues

| Issue | Priority | Status |
|-------|----------|--------|
| `POST /admin/reset-usage/{user_id}` — deployed to git, waiting for Render | P3 | Pending Render deploy |
| Test user at 10/10 monthly usage | P3 | Reset endpoint pending deploy |
| GROQ_API_KEY placeholder | Low | User to provide |
| Render Free tier cold starts | Low | Needs paid plan ($7/mo) |
| Custom Vercel domain | Low | Future |

## Git HEAD

- **Local/Remote:** `e82d9a9` (synced)
- **Render live:** Pending (auto-deploy from main)
- **Vercel:** Deployed 2026-04-21 ~18:20 UTC

---

*Last updated: 2026-04-21 18:25 UTC*