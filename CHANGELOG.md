# Changelog

All notable changes to ContentForge AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- AI provider updated from Llama 3.3 70B to GLM-5.1 via Groq API
- API route count grew to 375 (184 GET · 124 POST · 15 PUT · 15 PATCH · 37 DELETE)
- Backend test suite expanded to 571 tests (530 passing · 41 skipped · 0 failing)
- Backend codebase grew to 44,101 lines of Python
- Frontend codebase grew to 44,801 lines of TypeScript/TSX

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
- FastAPI backend with 380+ routes across 49 modules
- Next.js 14 frontend with Tailwind CSS
- Supabase Auth + PostgreSQL
- Celery + Redis task queue
- Cloudflare R2 storage
- n8n workflow automation
- Render + Vercel deployment