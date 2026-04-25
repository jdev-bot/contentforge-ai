# CONTEXT.md — ContentForge AI

> **Single source of truth.** Update after every material change. Commit + push immediately.
> If >8KB → compact. Archive resolved items to daily notes.

## Project Overview

- **Name:** ContentForge AI — AI content creation & management platform
- **GitHub:** `jdev-bot/contentforge-ai` (SSH)
- **Phase:** Staging — all platforms synced at HEAD, mock data fully purged
- **Tech:** FastAPI (Python) + Next.js 16 (TypeScript) + Supabase (PostgreSQL + Auth)

## Infrastructure

| Provider | Purpose | Key Info |
|----------|---------|---------|
| **Render** | Backend API | `srv-d7fhaif7f7vs73a168a0`, **Free tier**, cold starts ~30s, auto-deploy from main |
| **Vercel** | Frontend + proxy | `prj_LG8wzPFJVaSDwueFnorflBBwHAOc`, Next.js 16.2.3, deploy from `src/frontend/` |
| **Supabase** | DB + Auth | `zwbbmcbhrhlnoharfzdt`, 95 tables, all RLS enabled |

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

## Performance & Quality Status

- ✅ Auth caching, batch `/init`, stale-while-revalidate, ETag (commit `8b269cf`)
- ✅ E2E v2: 163/164 pass (99.4%)
- ✅ Backend tests: 530/530
- ✅ TypeScript: Zero errors
- ✅ Security audit: All 9 HIGH/CRITICAL findings fixed
- ✅ 335+ API routes live on Render
- ✅ Mock data purge: **COMPLETE** — zero mock data across all components

## Mock → Real API Status (COMPLETE)

All 8 target components now use real API:

| Component | Status | Backend Router |
|-----------|--------|----------------|
| AlertsCenter | ✅ Real API | `alerts.py` |
| AuditLogs | ✅ Real API | `audit_logs.py` |
| TrendingTopics | ✅ Real API | `trends.py` |
| IntegrationsPanel | ✅ Real API | `integrations.py` (webhooks/API keys: no backend yet, empty state) |
| ABTestingFramework | ✅ Real API | `ab_testing.py` (new, migration 028) |
| CompetitorAnalysis | ✅ Real API | `competitors.py` |
| QualityDashboard | ✅ Real API | `quality_scoring.py` |
| SentimentDashboard | ✅ Real API | `sentiment.py` |
| TeamCalendar | ✅ Real API | `team_calendar.py` |
| EngagementPrediction | ✅ Real API | `engagement_prediction.py` |

## What's Next — Prioritized

| # | Item | Priority | Notes |
|---|------|----------|-------|
| 1 | **AI_API_KEY** — provide Google AI Studio key for Gemini 2.5 Flash | High | Provider-agnostic layer done (commit aae3e09); set AI_PROVIDER=google + AI_API_KEY in Render |
| 2 | ~~PageHeader rollout~~ | ~~Medium~~ | ✅ **Done** — 36/42 components |
| 3 | ~~Mobile QA~~ | ~~Medium~~ | ✅ **Done** — safe-area, touch targets, 16 responsive grid fixes |
| 4 | ~~TeamCalendar backend~~ | ~~Medium~~ | ✅ **Done** — 6 API endpoints |
| 5 | ~~EngagementPrediction backend~~ | ~~Medium~~ | ✅ **Done** — Rule-based scoring + AI enhancement |
| 6 | ~~Mock data purge~~ | ~~Medium~~ | ✅ **Done** — All 8 components + 2 already-done, ABTesting backend + migration 028 |
| 7 | **Custom Vercel domain** | Low | |
| 8 | **Render paid plan** — eliminate 30s cold starts | Low | $7/mo |
| 9 | **Webhooks/API Keys CRUD backend** | Low | IntegrationsPanel webhooks & API keys tabs show empty state — no backend yet |

## Git HEAD

- **Local/Remote:** `aae3e09` (synced)
- **Render:** Auto-deploy from main
- **Vercel:** Auto-deploy from main

---

*Last updated: 2026-04-25 14:30 UTC*