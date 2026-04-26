# Neo DevOrg — ContentForge AI Project

## Project Structure

```
contentforge-ai/
├── src/
│   ├── backend/                  # FastAPI backend (Python 3.13)
│   │   └── app/
│   │       ├── main.py           # Application entry point
│   │       ├── routers/          # 54 router modules (427 routes)
│   │       ├── services/        # 36 service modules
│   │       ├── middleware/       # 4 middleware modules
│   │       ├── models/           # Pydantic models
│   │       ├── schemas/          # Request/response schemas
│   │       ├── utils/            # Utility functions
│   │       └── config.py         # Configuration
│   ├── frontend/                 # Next.js 14 frontend (TypeScript)
│   │   └── src/
│   │       ├── app/              # 16 pages (App Router)
│   │       ├── components/       # 59 components
│   │       ├── lib/              # Client libraries
│   │       └── styles/           # Tailwind CSS styles
│   └── workers/                  # Celery background workers
├── docs/                         # Documentation (37 files)
│   ├── API_COMPLETE.md          # Full API reference
│   ├── ARCHITECTURE.md          # System design
│   ├── DEPLOYMENT.md            # Deployment guide
│   ├── FEATURES_GUIDE.md        # Feature documentation
│   ├── PERFORMANCE_OPTIMIZATION.md
│   ├── SECURITY_AUDIT_REPORT.md
│   ├── TUTORIALS/               # 7-part tutorial series
│   └── ...                      # Additional docs
├── sdk/                          # Python Developer SDK
│   └── contentforge/
├── infra/                        # Infrastructure configuration
│   ├── docker/
│   ├── monitoring/
│   ├── n8n/
│   └── supabase/
├── scripts/                      # Utility scripts (9)
│   ├── backup-database.sh
│   ├── capture-screenshots.sh
│   ├── ci-local.sh
│   ├── deploy-backend.sh
│   ├── deploy-frontend.sh
│   ├── dev-setup.sh
│   ├── dev-start.sh
│   └── run-tests.sh
└── tests/                        # Integration & system tests (12)
    ├── conftest.py
    ├── test_analytics.py
    ├── test_auth.py
    ├── test_competitors.py
    ├── test_content.py
    ├── test_edge_cases.py
    ├── test_health.py
    ├── test_integration.py
    ├── test_load.py
    ├── test_organizations.py
    ├── test_security_advanced.py
    ├── test_stripe_webhooks.py
    └── test_subscription_enforcement.py
```

## Router Modules (54)

| # | Module | Key Endpoints |
|---|--------|---------------|
| 1 | `ab_testing` | A/B test management |
| 2 | `admin` | Admin operations |
| 3 | `ai_editor` | AI-powered editing tools |
| 4 | `ai_keys` | BYOK API key management (CRUD + validate) |
| 5 | `ai_suggestions` | Smart content suggestions |
| 6 | `alerts` | Performance alerts |
| 7 | `analytics` | Analytics & KPIs |
| 8 | `attribution` | Attribution modeling |
| 9 | `audience` | Audience insights |
| 10 | `audit_logs` | Audit logging & export |
| 11 | `auth` | Authentication (JWT, SSO) |
| 12 | `automation` | Automation rules & triggers |
| 13 | `categorization` | Smart categorization |
| 14 | `collaboration` | Real-time collaboration |
| 15 | `comments` | Comments v2 (threaded) |
| 16 | `competitors` | Competitor analysis |
| 17 | `content` | Content CRUD & import |
| 18 | `dashboards` | Custom dashboards |
| 19 | `distributions` | Distribution management |
| 20 | `docs` | API documentation |
| 21 | `engagement_prediction` | Engagement predictions |
| 22 | `freshness` | Content freshness scoring |
| 23 | `funnel` | Funnel tracking |
| 24 | `health` | Health checks |
| 25 | `init` | App initialization |
| 26 | `integration_framework` | Integration hub |
| 27 | `integrations` | External integrations |
| 28 | `marketplace` | Plugin marketplace |
| 29 | `notifications` | Notification management |
| 30 | `organizations` | Organization management |
| 31 | `performance` | Performance analytics |
| 32 | `plugins` | Plugin system |
| 33 | `presence` | WebSocket presence |
| 34 | `projects` | Project management |
| 35 | `quality_scoring` | Quality scoring |
| 36 | `reports` | Report generation |
| 37 | `retention` | Data retention policies |
| 38 | `rss` | RSS feed management |
| 39 | `saml` | SAML SSO |
| 40 | `scheduler` | Scheduled publishing |
| 41 | `search` | Full-text search |
| 42 | `sentiment` | Sentiment analysis |
| 43 | `sla` | SLA monitoring |
| 44 | `sso` | OIDC SSO |
| 45 | `stripe` | Stripe payments |
| 46 | `suggestions` | Auto-suggestions |
| 47 | `team_calendar` | Team content calendar |
| 48 | `trash` | Trash/restore |
| 49 | `trends` | Trending topics |
| 50 | `usage` | Usage tracking |
| 51 | `user` | User management |
| 52 | `version_history` | Version history & diff |
| 53 | `webhooks` | Webhook management |
| 54 | `ws` | WebSocket endpoints |

## Backend Services (36)

| Service | Description |
|---------|-------------|
| `alert_service` | Performance alert management |
| `attribution_service` | Channel attribution & ROI |
| `audience_service` | Audience growth insights |
| `audit_service` | Action logging & export |
| `categorization_service` | AI content clustering |
| `collaboration_service` | Real-time collaboration |
| `comments_service` | Threaded comments v2 |
| `competitor_service` | Competitor tracking |
| `dashboard_service` | Custom dashboards |
| `email_service` | Email via Resend |
| `extraction_service` | Content extraction |
| `freshness_service` | Content freshness scoring |
| `funnel_service` | Conversion funnel analytics |
| `ai_service` | AI content generation (BYOK, provider-agnostic) |
| `integration_framework_service` | Integration hub management |
| `integration_services` | External integrations |
| `marketplace_service` | Plugin marketplace |
| `performance_service` | Performance analytics |
| `plugin_service` | Plugin lifecycle management |
| `presence_service` | WebSocket presence |
| `quality_service` | Quality scoring |
| `report_service` | Report generation |
| `retention_service` | Data retention policies |
| `rss_service` | RSS feed processing |
| `saml_service` | SAML 2.0 authentication |
| `scheduler_service` | Content scheduling |
| `sentiment_service` | Sentiment analysis |
| `sla_service` | SLA monitoring & alerting |
| `sso_service` | OIDC SSO authentication |
| `suggestion_service` | Smart suggestions |
| `trend_service` | Trending topics |
| `version_service` | Version history & diff |
| `websocket_manager` | WebSocket connection management |

## Middleware Modules (4)

| Middleware | Description |
|-----------|-------------|
| `etag` | HTTP ETag support (304 Not Modified) |
| `performance` | X-Response-Time header injection |
| `request_id` | X-Request-ID header for tracing |
| `rate_limit_headers` | X-RateLimit-* headers on rate-limited endpoints |

## Development Workflow

### Branch Strategy
- `main` — Production-ready code
- `develop` — Integration branch
- `feature/*` — Feature branches
- `hotfix/*` — Emergency fixes

### Commit Convention
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Tests
- `chore:` Maintenance
- `perf:` Performance optimization

### CI/CD Pipelines

| Pipeline | Status | Runner |
|----------|--------|--------|
| Backend Tests | ✅ Green | srv1503460 (Ubuntu 25.10) |
| Frontend Build | ✅ Green | srv1503460 (Ubuntu 25.10) |
| CI/CD | ✅ Green | srv1503460 (Ubuntu 25.10) |
| Security Pipeline | ✅ Green | srv1503460 (Ubuntu 25.10) |

## Code Metrics

| Metric | Count |
|--------|-------|
| Total commits | 298 |
| API routes | 427 (211 GET · 144 POST · 16 PUT · 17 PATCH · 39 DELETE) |
| Router modules | 54 |
| Backend services | 36 |
| Middleware modules | 4 |
| Migrations | 20 (incl. BYOK api_keys) |
| Backend Python LOC | 48,494 |
| Frontend TypeScript/TSX LOC | 47,992 |
| Frontend components | 59 |
| Frontend pages | 16 |
| Backend test files | 30 |
| Integration tests | 13 |
| Deep system tests | 163/164 (99.4%) |

## Team

- **Executive Agent**: Project orchestration
- **Project Manager**: End-to-end delivery
- **Backend Engineer**: API & AI integration
- **Frontend Engineer**: UI/UX development
- **DevOps Engineer**: Infrastructure & deployment

---

*This is a production-grade project. Quality is non-negotiable.*