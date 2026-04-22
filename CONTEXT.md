# CONTEXT.md — ContentForge AI

> **Single source of truth.** Update after every material change. Commit + push immediately.
> If >8KB → compact. Archive resolved items to daily notes.

## Project Overview

- **Name:** ContentForge AI — AI content creation & management platform
- **GitHub:** `jdev-bot/contentforge-ai` (SSH)
- **Phase:** Staging — all platforms synced at HEAD, ready for next feature work
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
| Usage | **Reset to 0** (2026-04-22) |

## Deploy Fix (commit `685f1e0`, deployed 2026-04-22)

- **Bug:** `NameError: name 'UsageStats' is not defined` in `rate_limit.py` — class used in module-level annotation before definition
- **Fix:** Added `from __future__ import annotations` — makes all annotations lazy
- **Impact:** Render was stuck at `8b269cf` (3 commits behind). Now fully synced at `685f1e0`

## Performance & Quality Status

- ✅ Auth caching, batch `/init`, stale-while-revalidate, ETag (commit `8b269cf`)
- ✅ E2E v2: 163/164 pass (99.4%) — 1 skip (content creation, now unblocked by usage reset)
- ✅ Backend tests: 530/530
- ✅ TypeScript: Zero errors
- ✅ Security audit: All 9 HIGH/CRITICAL findings fixed
- ✅ 334 API routes live on Render
- ✅ Test user usage reset to 0

## Mock → Real API Wiring Status

| Component | Status |
|-----------|--------|
| AlertsCenter | ✅ Real API |
| AuditLogs | ✅ Real API |
| SentimentDashboard | ✅ Real API |
| QualityDashboard | ✅ Real API |
| IntegrationsPanel | ✅ Real API |
| CompetitorAnalysis | ✅ Real API (mock fallback) |
| TrendingTopics | ✅ Real API |
| TeamCalendar | 🔶 Demo Data (no backend) |
| EngagementPrediction | 🔶 Demo Data (no backend) |

## What's Next — Prioritized

| # | Item | Priority | Notes |
|---|------|----------|-------|
| 1 | **GROQ_API_KEY** — provide real key for AI content generation | High | Currently placeholder; AI features non-functional without it |
| 2 | ~~PageHeader rollout~~ | ~~Medium~~ | ✅ **Done** — 36/42 components (6 skipped: Dashboard, SmartEditor, ContentCreatePanel, ContentDetailPanel, ScheduleCalendar, ScheduleModal) |
| 3 | ~~Mobile QA~~ | ~~Medium~~ | ✅ **Done** — safe-area, touch targets, 16 responsive grid fixes, viewport config |
| 4 | ~~TeamCalendar backend~~ | ~~Medium~~ | ✅ **Done** — 6 API endpoints, real data integration |
| 5 | **EngagementPrediction backend** — build API endpoints | Medium | Currently demo data only |
| 6 | **Custom Vercel domain** | Low | |
| 7 | **Render paid plan** — eliminate 30s cold starts | Low | $7/mo |

## Git HEAD

- **Local/Remote:** `304436e` (synced)
- **Render:** `304436e` (deployed 2026-04-22 18:16 UTC, TeamCalendar backend)
- **Vercel:** `304436e` (deployed 2026-04-22, TeamCalendar frontend + mobile fixes)

---

*Last updated: 2026-04-22 18:20 UTC*