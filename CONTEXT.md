# CONTEXT.md — ContentForge AI

> **Single source of truth.** Update after every material change. Commit + push immediately.
> If >8KB → compact. Archive resolved items to daily notes.

## Project Overview

- **Name:** ContentForge AI — AI content creation & management platform
- **GitHub:** `jdev-bot/contentforge-ai` (SSH)
- **Phase:** Staging — BYOK feature complete, awaiting Google AI key
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

## BYOK (Bring Your Own Key) — New Feature

**Commit:** `c287993` — Per-user encrypted API keys for AI providers

### Architecture
- **Migration 029:** `api_keys` table — RLS, unique `(user_id, provider)`, encrypted at rest
- **Encryption:** AES-256-GCM via `ENCRYPTION_KEY` (falls back to `SECRET_KEY`)
- **Router:** `POST/GET/DELETE /api/v1/api-keys`, `POST .../validate` — live key validation on save
- **Middleware:** `BYOKMiddleware` extracts JWT → resolves user key → sets context var
- **Shim:** `groq_service` delegates to context var per-request; zero changes to existing service code
- **Frontend:** `APIKeysTab` component in Settings → add, validate, delete keys
- **Providers:** Google, Groq, Cerebras, OpenRouter, custom (any OpenAI-compatible)

### How It Works
1. User adds API key in Settings → "API Keys" tab
2. Key is validated live against provider's `/models` endpoint
3. Stored AES-256-GCM encrypted in Supabase, masked on read (`sk-abc...xyz`)
4. Every API request: BYOK middleware decodes JWT → resolves user's key → context var
5. All LLM calls transparently route through user's key (or fall back to platform default)

## Test Account

| Field | Value |
|-------|-------|
| Email | `test@neo.dev` |
| Password | `Test1234!` |
| User ID | `9b2538b0-99e2-4e1e-8864-36ae7e6289a1` |

## Performance & Quality Status

- ✅ Backend tests: 49 pass (encryption + BYOK + LLM presets + shim context var)
- ✅ TypeScript: Zero errors (frontend compiles clean)
- ✅ Security: Keys encrypted at rest, never returned unmasked, RLS enforced
- ✅ All existing service/router code works unchanged via context var shim

## What's Next — Prioritized

| # | Item | Priority | Notes |
|---|------|----------|-------|
| 1 | **AI_API_KEY** — set Google AI Studio key in Render env vars | High | Platform default until users add their own |
| 2 | **ENCRYPTION_KEY** — set a dedicated key in Render env vars | High | Falls back to SECRET_KEY but should be separate |
| 3 | **Custom Vercel domain** | Low | |
| 4 | **Render paid plan** — eliminate 30s cold starts | Low | $7/mo |
| 5 | **Webhooks/API Keys CRUD backend** | Low | IntegrationsPanel shows empty state |

## Git HEAD

- **Local/Remote:** `c287993` (synced, pushed)
- **Render:** Auto-deploy from main
- **Vercel:** Auto-deploy from main

---

*Last updated: 2026-04-25 15:45 UTC*