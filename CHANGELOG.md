# Changelog

All notable changes to ContentForge AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-04-26

### Added — BYOK (Bring Your Own Key) & Settings UI Overhaul
- **BYOK Architecture:** Per-user encrypted API keys (Google, Groq, Cerebras, OpenRouter, Custom)
- **AIService:** Provider-agnostic LLM layer (renamed from AIService)
- **BYOKMiddleware:** JWT → user key lookup → context var for every AI request
- **NoAPIKeyConfigured:** HTTPException(403) with `NO_API_KEY` code when no user key
- **Migration 029:** `api_keys` table with RLS, unique `(user_id, provider)`
- **AES-256-GCM encryption:** Auto-generated key for dev, `ENCRYPTION_KEY` env var for prod
- **API Keys router:** 5 endpoints — CRUD + validate against provider `/models`
- **APIKeysTab component:** Add/validate/delete keys with provider cards, `showHeader` prop
- **SettingsClient:** Standalone `/settings` page with server auth
- **Health check:** Shows `mode: "byok"` when no platform AI key configured

### Changed — Settings UI
- **Removed mock API keys:** No more hardcoded Stripe/Groq fake keys in Settings
- **Generic labeling:** "AI Provider Keys" instead of Groq-specific branding
- **Responsive mobile layouts:** Subscription, Export, Delete sections stack vertically on mobile
- **Button component:** `whitespace-nowrap` + `inline-flex items-center` on content span, removed `overflow-hidden`
- **Global CSS guard:** `button { white-space: nowrap; }` and `button svg { flex-shrink: 0; }`
- **AI provider reference:** All references updated from `ai_service` to `ai_service`, `AIService` to `AIService`

### Fixed
- **Settings page:** Fixed missing `SettingsClient` import, created standalone settings page
- **Double header:** `APIKeysTab` `showHeader={false}` avoids duplicate card headers
- **Button text wrapping:** Icon+text on same line in all buttons, no overflow clipping on mobile
- **NoAPIKeyConfigured:** Properly re-raised as HTTPException(403) in all AI routers
- **AIService singleton:** Fixed instance creation (was referencing `llm_service` instead of `AIService()`)

## [2.1.0] - 2026-04-14

### Added — Performance Optimizations
- **Redis/in-memory caching**: Applied to 9 high-traffic read endpoints for reduced latency
- **Parallel DB queries**: `asyncio.gather` for concurrent data fetching across services
- **N+1 query elimination**: Fixed in 5 endpoints to reduce database round-trips
- **ETag middleware**: HTTP 304 Not Modified support for cacheable responses
- **Performance middleware**: `X-Response-Time` header for request duration visibility
- **Request ID middleware**: `X-Request-ID` header for distributed request tracing
- **Rate limit headers middleware**: `X-RateLimit-*` headers on all rate-limited endpoints
- **Slow request logging**: Structured logging for requests exceeding 2s threshold
- **@lru_cache on Supabase admin client**: Instance reuse to avoid repeated client creation

### Changed
- Python runtime upgraded to 3.13
- Node.js runtime upgraded to v22.22.2
- AI provider updated from Llama 3.3 70B to GLM-5.1 via AIService
- API route count grew to 375 (211 GET · 144 POST · 16 PUT · 17 PATCH · 39 DELETE)
- Backend test suite expanded to 571 tests (530 passing · 41 skipped · 0 failing)
- Backend codebase grew to 48,494 lines of Python
- Frontend codebase grew to 47,992 lines of TypeScript/TSX

## [2.0.1] - 2026-04-14

### Fixed — CI/CD & Infrastructure
- Self-hosted GitHub Actions runner registered on srv1503460 (Ubuntu 25.10)
- All 4 CI/CD pipelines verified green (Backend Tests, Frontend Build, CI/CD, Security Pipeline)
- Deep system test suite: 163/164 pass (99.4%)
- TypeScript: Zero errors
- ESLint: Zero errors
- All 9 HIGH/CRITICAL security audit findings resolved

## [2.0.0] - 2026-04-14

### Added — P4 Features
- **Funnel Tracking**: Content conversion funnel analytics with step-by-step tracking
- **Attribution Modeling**: Channel attribution and ROI tracking across platforms
- **SLA Monitoring**: Service level agreement tracking with alerting
- **Integration Hub Framework**: Unified integration management with Zapier, Make.com, WordPress
- **Version History**: Full content version tracking with diff support
- **Audit Logs**: Comprehensive action logging with CSV/JSON export
- **Quality Scoring**: AI-powered content quality assessment
- **Sentiment Analysis**: Real-time sentiment tracking and analysis
- **Auto-Suggestions**: Smart content improvement recommendations
- **Smart Categorization**: AI-driven content clustering and tagging
- **Performance Analytics**: Deep content performance insights
- **Data Retention**: Configurable retention policies per content type
- **Comments v2**: Threaded comments with resolution tracking
- **SSO/OIDC**: Google, Microsoft, Okta SSO support
- **SAML SSO**: Enterprise SAML 2.0 authentication
- **Plugin System**: Extensible plugin architecture with lifecycle hooks
- **Developer SDK**: Python SDK for programmatic API access
- **WebSocket**: Real-time collaboration with presence tracking
- **Collaboration**: Multi-user real-time editing
- **Marketplace**: Plugin and template marketplace
- **Custom Dashboards**: User-configurable analytics dashboards
- **Report Builder**: Custom report generation with scheduling
- **Team Calendar**: Visual content planning calendar
- **Cookie Consent**: GDPR-compliant cookie consent management

### Changed
- Replaced ALL `datetime.utcnow()` with `datetime.now(timezone.utc)` across 50+ files
- Replaced bare `except:` clauses with `except Exception:` (7 occurrences)
- Removed hardcoded Redis password from config defaults
- Removed all `console.log()` statements from frontend production code
- Updated `_to_utc()` to return timezone-aware datetimes
- Fixed timezone variable shadowing in `update_scheduled_post`
- Updated mock Supabase chain to support `.offset()`, `.like()`, `.ilike()`, `.is_()`, `.not_()`, `.contains()`, `.contained()()`, `.overlap()`

### Fixed
- **schedule_list 500**: Missing `.offset()` on mock Supabase chain broke query chain
- **schedule_create timezone**: `_to_utc` returned naive datetime, comparison with aware datetime failed
- **categorization_cluster**: `_parse_json_response` returned `{}` instead of `[]` for "clusters" key
- **integration_create**: Wrong webhook_url format for Zapier validation
- **comment_create**: Missing defaults for `resolved_at`/`resolved_by` Optional fields
- **version_diff test order**: `version_create` must run before `version_diff`
- **freshness route ordering**: Static paths before parametric `{content_id}` routes
- **analytics timezone**: `datetime.now()` → `datetime.now(timezone.utc)`
- **analytics status shadowing**: Renamed `status` → `item_status`/`dist_status`

## [1.0.0] - 2026-04-11

### Added — P0-P3 Core Features
- Content import from URLs, YouTube, RSS, direct text
- AI-powered content generation via Groq (Llama 3.3 70B)
- Smart content editor (rewrite, expand, condense, optimize)
- Scheduled publishing with timezone support
- Analytics dashboard with KPIs
- Distribution management across platforms
- Full-text search
- Trash/restore with 30-day retention
- Organization management with role-based access
- Automation rules engine
- RSS auto-import
- Competitor analysis
- Audience insights
- Trending topics detection
- Performance alerts
- Webhook support
- Stripe payment integration
- Email notifications via Resend

### Infrastructure
- FastAPI backend with 380+ routes across 54 modules
- Next.js 14 frontend with Tailwind CSS
- Supabase Auth + PostgreSQL
- Celery + Redis task queue
- Cloudflare R2 storage
- n8n workflow automation
- Render + Vercel deployment