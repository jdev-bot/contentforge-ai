# CONTEXT.md — ContentForge AI

> **Single source of truth.** Update after every material change. Commit + push immediately.
> If >8KB → compact. Archive resolved items to daily notes.

## Project Overview

- **Name:** ContentForge AI — AI content creation & management platform
- **GitHub:** `jdev-bot/contentforge-ai` (SSH)
- **Phase:** Staging — BYOK-only mode (no platform AI key)
- **Tech:** FastAPI (Python 3.13) + Next.js 14 (TypeScript) + Supabase (PostgreSQL + Auth)

## Infrastructure

| Provider | Purpose | Key Info |
|----------|---------|---------|
| **Render** | Backend API | `srv-d7fhaif7f7vs73a168a0`, **Free tier**, cold starts ~30s, auto-deploy from main |
| **Vercel** | Frontend + proxy | `prj_LG8wzPFJVaSDwueFnorflBBwHAOc`, Next.js, deploy from `src/frontend/` |
| **Supabase** | DB + Auth | `zwbbmcbhrhlnoharfzdt`, 96 tables (incl. api_keys), all RLS enabled |

- **Backend URL:** `https://contentforge-ai-api.onrender.com`
- **Frontend URL:** `https://frontend-theta-seven-65.vercel.app`
- **API Proxy:** `/api/v1/*` → Render (via Vercel rewrites)

## BYOK (Bring Your Own Key) — Architecture

**Mode:** BYOK-only — no platform fallback AI key. AI features only work with user-provided keys.

### Flow
1. User adds API key in Settings → "AI Provider Keys" tab
2. Key validated live against provider `/models` endpoint
3. Stored AES-256-GCM encrypted in Supabase, masked on read (`sk-abc...xyz`)
4. Every API request: BYOK middleware decodes JWT → resolves user's key → context var
5. If no user key → `NoAPIKeyConfigured` exception → 403 with `NO_API_KEY` code
6. Frontend shows: "Add your API key in Settings → AI Provider Keys"

### Key Components
- **Migration 029:** `api_keys` table with RLS, unique `(user_id, provider)`
- **Encryption:** AES-256-GCM, auto-generated key persisted to `.encryption_key` (dev) or `ENCRYPTION_KEY` env var (prod)
- **Router:** `/api/v1/api-keys` — CRUD + validate (5 endpoints)
- **Middleware:** `BYOKMiddleware` — JWT → user key lookup → context var
- **Service:** `AIService` (renamed from `AIService`) — delegates to context var; raises `NoAPIKeyConfigured` when no user key
- **Exception handler:** Returns 403 `{detail, code: "NO_API_KEY", action}` for AI calls without a key
- **Frontend:** `APIKeysTab` component — add/validate/delete with provider cards, `showHeader` prop
- **Frontend:** `SettingsClient.tsx` (standalone) + `SettingsTab.tsx` (dashboard tab) — both integrate APIKeysTab
- **Providers:** Google, Groq, Cerebras, OpenRouter, custom
- **UI:** No Groq-specific branding — generic "AI Provider Keys" labeling

### No Platform Key Needed
- `AI_API_KEY` env var is optional (not required)
- `LLMService` singleton no longer requires valid `base_url`
- Health check shows `mode: "byok"` when no platform key configured
- All AI calls require user's own key — zero AI cost for product owner

## Settings UI — Recent Fixes (2026-04-26)

- **Button text wrapping:** Fixed globally — `whitespace-nowrap` on Button component, inner span `inline-flex items-center whitespace-nowrap`, global CSS `button { white-space: nowrap; }` and `button svg { flex-shrink: 0; }`. Removed `overflow-hidden` from Button that was clipping content.
- **Mobile responsive layouts:** Subscription/Plan, Export Data, Delete Account sections stack vertically on mobile (`space-y-3 sm:flex`).
- **API key cards:** Stack vertically on mobile, badges `flex-wrap`, masked key `break-all`.
- **Double header fix:** `APIKeysTab` has `showHeader` prop; Settings pages pass `showHeader={false}` to avoid duplicate headers.

## Test Account

| Field | Value |
|-------|-------|
| Email | `test@neo.dev` |
| Password | `Test1234!` |
| User ID | `9b2538b0-99e2-4e1e-8864-36ae7e6289a1` |

## Bug Fix Verification (2026-04-28)

All 3 bugs from Apr 27 are **fixed and verified** on staging:

| Bug | Fix Commit | Verified |
|-----|-----------|----------|
| AI Condense missing await | `963204a` | ✅ No more coroutine error |
| agency→enterprise enum | `963204a` | ✅ tier=pro, limit=1000, enum valid |
| Engagement prediction wrong arity | `d483b9f` | ✅ 200 OK, score=61 |

E2E: 12/16 pass. 4 failures are Google API 429 rate limits (external, not our bug).

## What's Next — Prioritized

| # | Item | Priority | Notes |
|---|------|----------|-------|
| 1 | **Re-run E2E after Google rate limit cools** | Medium | 4 endpoints hit 429 |
| 2 | **Custom Vercel domain** | Low | |
| 3 | **Render paid plan** — eliminate 30s cold starts | Low | $7/mo |
| 4 | **Webhooks/API Keys CRUD backend** | Low | IntegrationsPanel shows empty state |

## Code Metrics (Current)

| Metric | Count |
|--------|-------|
| Total commits | 298 |
| API routes | 427 (211 GET · 144 POST · 16 PUT · 17 PATCH · 39 DELETE) |
| Router modules | 54 |
| Backend services | 36 |
| Migrations | 20 (incl. 029_api_keys) |
| Backend Python LOC | ~48,500 |
| Frontend TS/TSX LOC | ~48,000 |
| Frontend components | 59 (top-level) |
| Frontend pages | 16 |
| Backend test files | 30 |

## Git HEAD

- **Local/Remote:** `d483b9f` (synced, pushed)
- **Render:** Auto-deploy from main
- **Vercel:** Auto-deploy from main

---

*Last updated: 2026-04-28 06:15 UTC*