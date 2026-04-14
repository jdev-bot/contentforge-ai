# ContentForge AI - System Architecture

## Overview

ContentForge AI is an AI-powered content repurposing and distribution platform. The system transforms long-form content into 20+ platform-native formats and distributes them across social platforms, email, and blogs.

**Tech Stack:** Python 3.13 · FastAPI · Next.js 14 · Supabase PostgreSQL · Groq API (GLM-5.1) · Redis · Node v22.22.2

**Scale:** 375 API routes · 49 router modules · 34 backend services · 73 frontend components · 16 pages

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                      CLIENT LAYER                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Web Browser   │  │  Mobile Browser │  │    API Client   │  │   n8n Webhook   │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
└───────────┼────────────────────┼────────────────────┼────────────────────┼──────────┘
            │                    │                    │                    │
            ▼                    ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    FRONTEND LAYER                                    │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │                      Next.js 14 + Tailwind CSS (73 components, 16 pages)      │  │
│  │                    (Vercel - Edge Network, Serverless)                         │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────┬───────────────────────────────────────────────────┘
                                  │ HTTPS / REST
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                     API GATEWAY                                      │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │                           Load Balancer / Vercel Edge                        │  │
│  │                    Rate Limiting, CORS, GZIP Compression                       │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────┬───────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              MIDDLEWARE STACK                                        │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────┐ ┌──────┐ ┌──────┐      │
│  │    ETag     │ │Performance │ │ RequestID  │ │RateLimit │ │ GZip │ │ CORS │      │
│  │ (304 Not   │ │  (X-Resp-  │ │ (X-Request │ │ Headers  │ │      │ │      │      │
│  │  Modified) │ │  Time)     │ │    -ID)    │ │          │ │      │ │      │      │
│  └────────────┘ └────────────┘ └────────────┘ └──────────┘ └──────┘ └──────┘      │
│  ┌──────────────┐  ┌──────────────────┐                                            │
│  │ ErrorTracking │  │  UsageTracking   │                                            │
│  └──────────────┘  └──────────────────┘                                            │
└─────────────────────────────────┬───────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    BACKEND LAYER                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │                         FastAPI (Python 3.13)                                │  │
│  │                    (Render - Web Service)                                    │  │
│  │                     375 routes / 49 router modules                          │  │
│  │                                                                              │  │
│  │  ┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐        │  │
│  │  │   Auth   │ Projects │ Content  │ Distrib. │  Usage   │  Admin   │        │  │
│  │  ├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤        │  │
│  │  │   SSO    │  SAML    │  Audit   │ Version  │ Quality  │Sentiment │        │  │
│  │  ├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤        │  │
│  │  │  Dashbd  │ Reports │ Suggest. │ Categor. │PerfAnalyt│ Retention│        │  │
│  │  ├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤        │  │
│  │  │ Comments │  Plugins │   SDK    │WebSocket │Collabor. │Marketpl. │        │  │
│  │  ├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤        │  │
│  │  │  Funnels │Attribut. │   SLA   │ IntegHub │ AIEditor │AISuggest │        │  │
│  │  ├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤        │  │
│  │  │  Alerts  │Analytics │ Audience │Automation│Scheduler │   RSS    │        │  │
│  │  ├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤        │  │
│  │  │ Search   │  Trash   │  Trends  │ Freshness│Competit. │Presence  │        │  │
│  │  ├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤        │  │
│  │  │  Stripe  │   Docs   │ Health   │ Notific. │   User   │   Orgs   │        │  │
│  │  └──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘        │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────┬───────────────────────────────────────────────────┘
            │                     │                    │
            ▼                     ▼                    ▼
┌───────────────────┐ ┌───────────────────┐ ┌─────────────────────────────────────┐
│   AI SERVICE      │ │  WORKER SERVICE   │ │         DATABASE LAYER              │
│  ┌─────────────┐  │ │  ┌─────────────┐  │ │  ┌───────────┐    ┌───────────────┐  │
│  │   Groq API  │  │ │  │   Celery    │  │ │  │ Supabase  │    │ Redis Cache   │  │
│  │  GLM-5.1   │  │ │  │   Worker    │  │ │  │PostgreSQL │    │ + In-Memory   │  │
│  │             │  │ │  │  (Render)   │  │ │  │  (Auth)   │    │   Fallback    │  │
│  └─────────────┘  │ │  └─────────────┘  │ │  └───────────┘    └───────────────┘  │
└───────────────────┘ │         │         │ └─────────────────────────────────────┘
                      │         ▼         │
                      │  ┌─────────────┐  │
                      │  │ Celery Beat │  │
                      │  │ (Scheduler) │  │
                      │  └─────────────┘  │
                      └───────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                               STORAGE LAYER                                          │
│  ┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────┐ │
│  │    Cloudflare R2        │  │      Supabase           │  │      n8n            │ │
│  │    (File Storage)       │  │      (Database)         │  │   (Workflows)       │ │
│  └─────────────────────────┘  └─────────────────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                             DISTRIBUTION LAYER                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐  │
│  │   Twitter   │  │  LinkedIn   │  │   Email     │  │   Blog      │  │  Other  │  │
│  │             │  │             │  │  (Resend)   │  │  Platforms  │  │Platforms│  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Descriptions

### 1. Frontend (Next.js 14)

**Technology Stack:**
- **Framework:** Next.js 14 (App Router)
- **Styling:** Tailwind CSS
- **UI Components:** 73 custom components + 12 shared UI primitives (Card, Button, Input, Skeleton, etc.)
- **State Management:** React hooks
- **Authentication:** Supabase Auth + SSO (OIDC/SAML)

**Pages (16):**
- `/` — Dashboard
- `/login` — Authentication
- `/sso` — SSO login
- `/projects/new` — Create project
- `/projects/[id]` — Project details
- `/content/new` — Create content
- `/content/[id]` — Content details
- `/settings` — Settings & configuration
- `/pricing` — Pricing plans
- `/payment/success` — Payment success
- `/payment/cancel` — Payment cancelled
- `/onboarding` — User onboarding
- `/dashboard` — Analytics dashboard
- `/legal/*` — Legal pages
- `/sso` — SSO authentication
- Additional dynamic routes for SSO callback

**Key P4 Features (Frontend):**
- Version History panel
- Audit Logs viewer
- Quality Scoring dashboard
- Sentiment Analysis dashboard
- Custom Dashboards builder
- Reports generator
- AI Suggestions panel
- Smart Categorization panel
- Performance Analytics dashboard
- Data Retention manager
- Comments v2 panel
- Plugin Manager
- Funnel Analytics dashboard
- Attribution Dashboard
- SLA Monitoring dashboard
- Integration Hub
- Marketplace (Template Gallery)
- Collaboration & Team features

**Hosting:** Vercel (Edge Network, 100GB free tier)

---

### 2. Backend (FastAPI)

**Technology Stack:**
- **Framework:** FastAPI (Python 3.13)
- **API Standard:** OpenAPI 3.0 / REST
- **Authentication:** JWT tokens + SSO (OIDC) + SAML SSO
- **Validation:** Pydantic models
- **Runtime:** Uvicorn

**API Routes:** 375 total (184 GET | 124 POST | 15 PUT | 15 PATCH | 37 DELETE)

**Router Modules (49):**

| Router | Purpose |
|--------|---------|
| `auth` | Authentication & authorization |
| `user` | User profile management |
| `organizations` | Organization CRUD & membership |
| `projects` | Project CRUD operations |
| `content` | Content generation & management |
| `distributions` | Distribution tracking & management |
| `usage` | Usage tracking & rate limits |
| `health` | Health checks & monitoring |
| `docs` | API documentation |
| `admin` | Administrative functions |
| `webhooks` | External service webhooks |
| `analytics` | Analytics & reporting |
| `stripe` | Payment processing |
| `ai_editor` | AI content editing (rewrite, expand, condense, optimize) |
| `ai_suggestions` | AI-powered content suggestions |
| `version_history` | Content version tracking & rollback |
| `audit_logs` | System audit trail |
| `quality_scoring` | Content quality metrics |
| `sentiment` | Sentiment analysis |
| `dashboards` | Custom dashboard CRUD |
| `reports` | Report generation & scheduling |
| `suggestions` | Auto-suggestion engine |
| `categorization` | Smart categorization & clustering |
| `performance` | Performance analytics |
| `retention` | Data retention policies |
| `comments` | Comments v2 with threading |
| `sso` | OIDC SSO authentication |
| `saml` | SAML SSO authentication |
| `plugins` | Plugin system management |
| `ws` | WebSocket real-time connections |
| `collaboration` | Real-time collaboration features |
| `marketplace` | Plugin/template marketplace |
| `funnel` | Funnel tracking & analysis |
| `attribution` | Attribution modeling |
| `sla` | SLA monitoring & alerting |
| `integration_framework` | Integration Hub framework |
| `alerts` | Alert management & notifications |
| `audience` | Audience analytics |
| `automation` | Automation rules engine |
| `scheduler` | Content scheduling |
| `rss` | RSS feed management |
| `search` | Full-text search |
| `trash` | Soft-delete & recovery |
| `trends` | Trend tracking & analysis |
| `freshness` | Content freshness scoring |
| `competitors` | Competitor analysis |
| `notifications` | Notification management |
| `presence` | Real-time user presence |

**Backend Services (34):**

| Service | Purpose |
|---------|---------|
| `alert_service` | Alert management |
| `attribution_service` | Attribution modeling |
| `audience_service` | Audience analytics |
| `audit_service` | Audit logging |
| `categorization_service` | Smart categorization |
| `collaboration_service` | Real-time collaboration |
| `comments_service` | Comments management |
| `competitor_service` | Competitor tracking |
| `dashboard_service` | Custom dashboards |
| `email_service` | Email delivery (Resend) |
| `extraction_service` | Content extraction |
| `freshness_service` | Freshness scoring |
| `funnel_service` | Funnel tracking |
| `groq_service` | AI content generation (GLM-5.1) |
| `integration_framework_service` | Integration Hub |
| `integration_services` | Third-party integrations |
| `marketplace_service` | Plugin marketplace |
| `performance_service` | Performance analytics |
| `plugin_service` | Plugin system |
| `presence_service` | Real-time presence |
| `quality_service` | Quality scoring |
| `report_service` | Report generation |
| `retention_service` | Data retention |
| `rss_service` | RSS feed processing |
| `saml_service` | SAML SSO |
| `scheduler_service` | Content scheduling |
| `sentiment_service` | Sentiment analysis |
| `sla_service` | SLA monitoring |
| `sso_service` | OIDC SSO |
| `suggestion_service` | AI suggestions |
| `trend_service` | Trend analysis |
| `version_service` | Version history |
| `websocket_manager` | WebSocket connections |

**Hosting:** Render (Docker container, 512MB free tier)

---

### 3. Middleware Stack

The backend applies the following middleware (in processing order):

| Middleware | Purpose | Response Headers |
|-----------|---------|-----------------|
| **ETagMiddleware** | HTTP conditional requests (304 Not Modified) | `ETag`, `Cache-Control` |
| **PerformanceMiddleware** | Request timing & slow request logging (>2s) | `X-Response-Time` |
| **RequestIDMiddleware** | Distributed request tracing | `X-Request-ID` |
| **RateLimitHeadersMiddleware** | Rate limit status in responses | `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` |
| **GZipMiddleware** | Response payload compression | `Content-Encoding: gzip` |
| **CORSMiddleware** | Cross-origin resource sharing | `Access-Control-Allow-*` |
| **ErrorTrackingMiddleware** | Error capture & logging | — |
| **UsageTrackingMiddleware** | API usage tracking & rate enforcement | — |

---

### 4. Caching Layer

**Implementation:** `CacheManager` with Redis primary + automatic in-memory fallback

**Cached Endpoints:**

| Endpoint Category | Cache TTL | Invalidation |
|-------------------|-----------|-------------|
| Analytics dashboard | 300s | On write |
| Content list/detail | 60–120s | On create/update/delete |
| Project list/detail | 60–120s | On create/update/delete |
| Distribution list/stats | 120s | On create/schedule |
| Audience metrics | 300s | On create |
| Trends | 300s | On write |
| Competitors | 300s | On write |
| Freshness scores | 120s | On write |
| Health check | 60s | Auto-expiry |

**Behavior:** When Redis is unavailable, the cache transparently falls back to an in-memory store. Cache is cleared between tests to prevent pollution.

---

### 5. Database Layer

#### Supabase (PostgreSQL)

**Purpose:** Primary database for application data

**Tables:** Users, projects, content, distributions, usage records, webhook logs, organizations, audit logs, version history, quality scores, sentiment records, dashboards, reports, comments, plugins, funnel events, attribution data, SLA records, integration configs, and more.

**Features:**
- Row Level Security (RLS) for data isolation
- Real-time subscriptions
- Built-in authentication

#### Redis

**Purpose:** Caching, task queue, and session storage

**Uses:**
- **Caching:** API response cache (9 endpoint groups), session storage
- **Task Queue:** Celery message broker
- **Rate Limiting:** Token bucket implementation

**Hosting:** Render Redis (or self-hosted via Docker)

---

### 6. AI Layer

#### Groq API

**Purpose:** AI-powered content generation

**Models:**
- **GLM-5.1** — Primary content generation model

**Capabilities:**
- Content repurposing (blog → social posts)
- Platform-native formatting
- Multi-language support
- Tone adjustment
- AI-powered suggestions & auto-suggestions
- Sentiment analysis
- Quality scoring
- Smart categorization

**Services:**
- `extraction_service.py` — Content extraction from URLs/files
- `groq_service.py` — AI content generation interface
- `suggestion_service.py` — AI suggestion engine
- `sentiment_service.py` — Sentiment analysis
- `quality_service.py` — Quality scoring
- `categorization_service.py` — Smart categorization

**Rate Limits:** 14M tokens/month free tier

---

### 7. Worker Layer (Celery)

**Technology Stack:**
- **Task Queue:** Celery
- **Message Broker:** Redis
- **Scheduler:** Celery Beat

**Worker Types:**

| Worker | Purpose |
|--------|---------|
| `worker` | Background task processing |
| `beat` | Scheduled task execution |

**Tasks:**
- Content generation (async)
- Distribution publishing
- Analytics aggregation
- Cleanup jobs
- Scheduled reports
- Data retention enforcement
- SLA monitoring checks
- Funnel event processing

---

### 8. Storage Layer

#### Cloudflare R2

**Purpose:** File storage for uploaded and generated content

**Storage:**
- Original content uploads
- Generated assets
- Export files

**Free Tier:** 10GB storage

#### Supabase Storage

**Purpose:** Alternative file storage (optional)

---

### 9. Automation Layer (n8n)

**Purpose:** Workflow automation and integrations

**Workflows:**
- Content distribution pipelines
- Social media posting
- Email notifications
- Webhook processing

**Hosting:** Self-hosted (Docker) or n8n cloud

---

### 10. External Services

| Service | Purpose | Integration |
|---------|---------|-------------|
| **Resend** | Email delivery | API |
| **Stripe** | Payment processing | API + Webhooks |
| **Twitter/X API** | Social distribution | n8n workflow |
| **LinkedIn API** | Social distribution | n8n workflow |
| **Webhooks** | External integrations | HTTP callbacks |
| **SSO Providers** | OIDC/SAML authentication | OAuth 2.0 / SAML |

---

## Performance Optimizations

### Caching (9 Endpoint Groups)

Redis-backed caching with in-memory fallback reduces database roundtrips for frequently-accessed read endpoints. See [Caching Layer](#4-caching-layer) above for details.

### Parallel Database Queries

Multiple independent Supabase queries are executed concurrently via `asyncio.gather` with `asyncio.to_thread`:

- **Analytics Dashboard KPIs:** 3 sequential queries → parallel (3x faster)
- **Organization List:** Owned orgs + member links fetched in parallel

### N+1 Query Elimination

Batch queries replace per-record database calls:

| Endpoint | Before | After |
|----------|--------|-------|
| `list_organizations` (member count) | 1 + N queries | 1 batch query |
| `get_organization` (with profiles) | 1 + N queries | 1 batch query |
| `list_members` (with profiles) | 1 + N queries | 1 batch query |
| `bulk_analyze_freshness` | N upsert calls | 1 batch upsert |
| `export_user_data` (with orgs) | 1 + N queries | 1 batch query |

### HTTP Performance Middleware

- **ETag:** 304 Not Modified responses for analytics/health/trends endpoints
- **Performance:** `X-Response-Time` header, slow request logging (>2s)
- **Request ID:** `X-Request-ID` for distributed tracing
- **Rate Limit Headers:** Rate limit status in all responses
- **GZip:** Response compression

### Connection Pooling

- `get_supabase_client()` — cached with `@lru_cache`
- `get_supabase_admin_client()` — cached with `@lru_cache`

---

## Data Flow

### 1. Content Creation Flow

```
User → Frontend (Next.js) → Backend (FastAPI) → AI (Groq) → Database (Supabase)
                                          ↘ Cache (Redis) ↗
```

1. User authenticates via Supabase Auth / SSO
2. Creates project and uploads source content
3. Backend extracts content, calls AI service
4. Results cached and stored in database
5. Frontend displays generated content

### 2. Distribution Flow

```
User → Frontend → Backend → Celery Worker → n8n → External Platforms
```

1. User selects content to distribute
2. Backend validates and queues task
3. Celery worker processes distribution
4. n8n workflow handles platform-specific posting
5. Results tracked in database

### 3. Real-Time Collaboration Flow

```
User A → WebSocket → Backend → WebSocket → User B
                            ↘ Database
```

1. Users connect via WebSocket
2. Presence tracked in real-time
3. Changes broadcast to collaborators
4. Conflicts resolved server-side

---

## Security Architecture

### Authentication Flows

- **JWT Authentication** — Stateless token-based auth via Supabase
- **OIDC SSO** — OpenID Connect single sign-on
- **SAML SSO** — SAML 2.0 single sign-on

### Security Measures

- **JWT Authentication** — Stateless token-based auth
- **Row Level Security** — Database-level access control
- **Rate Limiting** — Token bucket algorithm with response headers
- **CORS Protection** — Configurable origin validation
- **HTTPS Only** — TLS 1.3 for all connections
- **Error Tracking** — Middleware error capture & logging
- **ETag** — Conditional requests reduce unnecessary data transfer
- **Webhook Security** — HMAC-SHA256 signatures, idempotency, replay protection
- **All 9 HIGH/CRITICAL findings resolved** — See [Security Audit Report](./SECURITY_AUDIT_REPORT.md)

---

## Deployment Architecture

### Production Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                           Vercel Edge                            │
│                    (Global CDN + Serverless)                       │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
           ┌──────────────┐            ┌──────────────┐
           │  Next.js     │            │  Next.js     │
           │  Instance 1  │            │  Instance 2  │
           └──────┬───────┘            └──────┬───────┘
                  │                          │
                  └──────────────┬───────────┘
                                 │
                                 ▼
                    ┌──────────────────────┐
                    │    Render Load       │
                    │    Balancer          │
                    └──────────┬───────────┘
                               │
           ┌───────────────────┼───────────────────┐
           ▼                   ▼                   ▼
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │  FastAPI    │    │  FastAPI    │    │  FastAPI    │
    │  Instance 1 │    │  Instance 2 │    │  Instance N │
    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
           │                  │                  │
           └──────────────────┼──────────────────┘
                              │
           ┌──────────────────┼──────────────────┐
           ▼                  ▼                  ▼
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │  Supabase   │    │   Redis     │    │ Cloudflare  │
    │ PostgreSQL  │    │  (Cache)    │    │     R2      │
    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## Scaling Considerations

### Horizontal Scaling

| Component | Scaling Method | Trigger |
|-----------|---------------|---------|
| Frontend | Vercel auto-scale | Traffic increase |
| Backend | Render auto-scale | CPU/Memory |
| Workers | Render worker scaling | Queue depth |
| Database | Supabase auto-scale | Connection limits |
| Cache | Redis clustering | Memory usage |

---

## Monitoring & Observability

### Health Endpoints

- `GET /api/v1/health` — Basic health check
- `GET /api/v1/health/detailed` — Component status

### Metrics

- **Application:** Response time (via `X-Response-Time` header), error rate, throughput
- **Infrastructure:** CPU, memory, disk, network
- **Business:** Active users, content generated, distributions sent

### Middleware Response Headers

| Header | Middleware | Description |
|--------|-----------|-------------|
| `X-Response-Time` | PerformanceMiddleware | Request processing time in ms |
| `X-Request-ID` | RequestIDMiddleware | Unique request identifier for tracing |
| `X-RateLimit-Limit` | RateLimitHeadersMiddleware | Max requests allowed |
| `X-RateLimit-Remaining` | RateLimitHeadersMiddleware | Remaining requests |
| `X-RateLimit-Reset` | RateLimitHeadersMiddleware | Reset timestamp |
| `ETag` | ETagMiddleware | Resource version hash |
| `Cache-Control` | ETagMiddleware | Caching directives |

### Logging

- Structured JSON logging
- Request/response logging with request IDs
- Error tracking with context
- Slow request alerts (>2s)

---

## Disaster Recovery

### Backup Strategy

- **Database:** Supabase automated backups (daily)
- **Files:** R2 versioning and cross-region replication
- **Code:** Git repository with commit history

### Failover

- **Frontend:** Vercel automatic failover
- **Backend:** Render health checks and restart
- **Database:** Supabase point-in-time recovery
- **Cache:** In-memory fallback when Redis unavailable

---

## Related Documentation

- [Project Status](./STATUS.md) — Current development status
- [API Reference](./API.md) — API overview and examples
- [API Complete Reference](./API_COMPLETE.md) — Full endpoint listing (375 routes)
- [Testing Report](./TESTING.md) — Test results and coverage
- [Performance Report](./PERFORMANCE.md) — Benchmarks and optimizations
- [Security Audit](./SECURITY_AUDIT_REPORT.md) — Security assessment
- [Deployment Guide](./DEPLOYMENT.md) — Deployment instructions
- [Performance Optimization](./PERFORMANCE_OPTIMIZATION.md) — Optimization details

---

*Last updated: 2026-04-14*