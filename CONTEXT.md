# CONTEXT.md — ContentForge AI

> **Single source of truth.** Update after every material change. Commit + push immediately.
> If >8KB → compact. Archive resolved items to daily notes.

## Project Overview

- **Name:** ContentForge AI — AI content creation & management platform
- **GitHub:** `jdev-bot/contentforge-ai` (SSH)
- **Phase:** Staging — BYOK-only mode (no platform AI key)
- **Tech:** FastAPI (Python) + Next.js 16 (TypeScript) + Supabase (PostgreSQL + Auth)

## Infrastructure

| Provider | Purpose | Key Info |
|----------|---------|---------|
| **Render** | Backend API | `srv-d7fhaif7f7vs73a168a0`, **Free tier**, cold starts ~30s, auto-deploy from main |
| **Vercel** | Frontend + proxy | `prj_LG8wzPFJVaSDwueFnorflBBwHAOc`, Next.js 16.2.3, deploy from `src/frontend/` |
| **Supabase** | DB + Auth | `zwbbmcbhrhlnoharfzdt`, 96 tables (incl. api_keys), all RLS enabled |

- **Backend URL:** `https://contentforge-ai-api.onrender.com`
- **Frontend URL:** `https://frontend-theta-seven-65.vercel.app`
- **API Proxy:** `/api/v1/*` → Render (via Vercel rewrites)

## BYOK (Bring Your Own Key) — Architecture

**Mode:** BYOK-only — no platform fallback AI key. AI features only work with user-provided keys.

### Flow
1. User adds API key in Settings → "API Keys" tab
2. Key validated live against provider `/models` endpoint
3. Stored AES-256-GCM encrypted in Supabase, masked on read (`sk-abc...xyz`)
4. Every API request: BYOK middleware decodes JWT → resolves user's key → context var
5. If no user key → `NoAPIKeyConfigured` exception → 403 with `NO_API_KEY` code
6. Frontend shows: "Add your API key in Settings → API Keys"

### Key Components
- **Migration 029:** `api_keys` table with RLS, unique `(user_id, provider)`
- **Encryption:** AES-256-GCM, auto-generated key persisted to `.encryption_key` (dev) or `ENCRYPTION_KEY` env var (prod)
- **Router:** `/api/v1/api-keys` — CRUD + validate (5 endpoints)
- **Middleware:** `BYOKMiddleware` — JWT → user key lookup → context var
- **Shim:** `groq_service` delegates to context var; raises `NoAPIKeyConfigured` when no user key
- **Exception handler:** Returns 403 `{detail, code: "NO_API_KEY", action}` for AI calls without a key
- **Frontend:** `APIKeysTab` component — add/validate/delete with provider cards
- **Providers:** Google, Groq, Cerebras, OpenRouter, custom

### No Platform Key Needed
- `AI_API_KEY` env var is optional (not required)
- `LLMService` singleton no longer requires valid `base_url`
- Health check shows `mode: "byok"` when no platform key configured
- All AI calls require user's own key — zero AI cost for product owner

## Test Account

| Field | Value |
|-------|-------|
| Email | `test@neo.dev` |
| Password | `Test1234!` |
| User ID | `9b2538b0-99e2-4e1e-8864-36ae7e6289a1` |

## What's Next — Prioritized

| # | Item | Priority | Notes |
|---|------|----------|-------|
| 1 | **ENCRYPTION_KEY** — set a dedicated key in Render env vars | Medium | Falls back to auto-gen in dev; should be explicit in prod |
| 2 | **Custom Vercel domain** | Low | |
| 3 | **Render paid plan** — eliminate 30s cold starts | Low | $7/mo |
| 4 | **Webhooks/API Keys CRUD backend** | Low | IntegrationsPanel shows empty state |

## Git HEAD

- **Local/Remote:** `20a5a52` (synced, pushed)
- **Render:** Auto-deploy from main
- **Vercel:** Auto-deploy from main

---

*Last updated: 2026-04-25 17:30 UTC*