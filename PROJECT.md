# Neo DevOrg — ContentForge AI Project

## Project Structure

```
contentforge-ai/
├── src/
│   ├── backend/                  # FastAPI backend (Python 3.13)
│   │   └── app/
│   │       ├── main.py           # Application entry point
│   │       ├── routers/          # 49 router modules (375 routes)
│   │       ├── services/        # 34 service modules
│   │       ├── middleware/       # 4 middleware modules
│   │       ├── models/           # Pydantic models
│   │       ├── schemas/          # Request/response schemas
│   │       ├── utils/            # Utility functions
│   │       └── config.py         # Configuration
│   ├── frontend/                 # Next.js 14 frontend (TypeScript)
│   │   └── src/
│   │       ├── app/              # 16 pages (App Router)
│   │       ├── components/       # 73 components
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

## Router Modules (49)

| # | Module | Key Endpoints |
|---|--------|---------------|
| 1 | `admin` | Admin operations |
| 2 | `ai_editor` | AI-powered editing tools |
| 3 | `ai_suggestions` | Smart content suggestions |
| 4 | `alerts` | Performance alerts |
| 5 | `analytics` | Analytics & KPIs |
| 6 | `attribution` | Attribution modeling |
| 7 | `audience` | Audience insights |
| 8 | `audit_logs` | Audit logging & export |
| 9 | `auth` | Authentication (JWT, SSO) |
| 10 | `automation` | Automation rules & triggers |
| 11 | `categorization` | Smart categorization |
| 12 | `collaboration` | Real-time collaboration |
| 13 | `comments` | Comments v2 (threaded) |
| 14 | `competitors` | Competitor analysis |
| 15 | `content` | Content CRUD & import |
| 16 | `dashboards` | Custom dashboards |
| 17 | `distributions` | Distribution management |
| 18 | `docs` | API documentation |
| 19 | `freshness` | Content freshness scoring |
| 20 | `funnel` | Funnel tracking |
| 21 | `health` | Health checks |
| 22 | `integration_framework` | Integration hub |
| 23 | `integrations` | External integrations |
| 24 | `marketplace` | Plugin marketplace |
| 25 | `notifications` | Notification management |
| 26 | `organizations` | Organization management |
| 27 | `performance` | Performance analytics |
| 28 | `plugins` | Plugin system |
| 29 | `presence` | WebSocket presence |
| 30 | `projects` | Project management |
| 31 | `quality_scoring` | Quality scoring |
| 32 | `reports` | Report generation |
| 33 | `retention` | Data retention policies |
| 34 | `rss` | RSS feed management |
| 35 | `saml` | SAML SSO |
| 36 | `scheduler` | Scheduled publishing |
| 37 | `search` | Full-text search |
| 38 | `sentiment` | Sentiment analysis |
| 39 | `sla` | SLA monitoring |
| 40 | `sso` | OIDC SSO |
| 41 | `stripe` | Stripe payments |
| 42 | `suggestions` | Auto-suggestions |
| 43 | `trash` | Trash/restore |
| 44 | `trends` | Trending topics |
| 45 | `usage` | Usage tracking |
| 46 | `user` | User management |
| 47 | `version_history` | Version history & diff |
| 48 | `webhooks` | Webhook management |
| 49 | `ws` | WebSocket endpoints |

## Backend Services (34)

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
| `groq_service` | Groq AI integration |
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
| Total commits | 187 |
| API routes | 375 (184 GET · 124 POST · 15 PUT · 15 PATCH · 37 DELETE) |
| Router modules | 49 |
| Backend services | 34 |
| Middleware modules | 4 |
| Backend Python LOC | 44,101 |
| Frontend TypeScript/TSX LOC | 44,801 |
| Frontend components | 73 |
| Frontend pages | 16 |
| Backend tests | 571 (530 passing · 41 skipped · 0 failing) |
| Deep system tests | 163/164 (99.4%) |

## Team

- **Executive Agent**: Project orchestration
- **Project Manager**: End-to-end delivery
- **Backend Engineer**: API & AI integration
- **Frontend Engineer**: UI/UX development
- **DevOps Engineer**: Infrastructure & deployment

---

*This is a production-grade project. Quality is non-negotiable.*