# ContentForge AI - System Architecture

## Overview

ContentForge AI is an AI-powered content repurposing and distribution platform. The system transforms long-form content into 20+ platform-native formats and distributes them across social platforms, email, and blogs.

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
│  │                        Next.js 14 + Tailwind CSS                             │  │
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
│                                    BACKEND LAYER                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │                         FastAPI (Python)                                     │  │
│  │                    (Render - Web Service)                                    │  │
│  │  ┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐        │  │
│  │  │   Auth   │ Projects │ Content  │ Distribute│  Usage   │  Admin   │        │  │
│  │  │  Router  │  Router  │  Router  │  Router   │  Router  │  Router  │        │  │
│  │  └──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘        │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────┬───────────────────────────────────────────────────┘
            │                     │                    │
            ▼                     ▼                    ▼
┌───────────────────┐ ┌───────────────────┐ ┌─────────────────────────────────────┐
│   AI SERVICE      │ │  WORKER SERVICE   │ │         DATABASE LAYER              │
│  ┌─────────────┐  │ │  ┌─────────────┐  │ │  ┌───────────┐    ┌───────────────┐  │
│  │   Groq API  │  │ │  │   Celery    │  │ │  │ Supabase  │    │ Redis Cache   │  │
│  │  Llama 3.3  │  │ │  │   Worker    │  │ │  │PostgreSQL │    │   + Queue     │  │
│  │   70B       │  │ │  │  (Render)   │  │ │  │  (Auth)   │    │               │  │
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
- **UI Components:** Custom components (Card, Button, Input, Skeleton)
- **State Management:** React hooks
- **Authentication:** Supabase Auth

**Key Features:**
- Dashboard with analytics
- Project management interface
- Content creation and editing
- Distribution tracking
- Settings and user management
- Real-time updates

**Pages:**
- `/` - Dashboard
- `/login` - Authentication
- `/projects/new` - Create project
- `/projects/[id]` - Project details
- `/content/new` - Create content
- `/content/[id]` - Content details

**Hosting:** Vercel (Edge Network, 100GB free tier)

---

### 2. Backend (FastAPI)

**Technology Stack:**
- **Framework:** FastAPI (Python)
- **API Standard:** OpenAPI 3.0 / REST
- **Authentication:** JWT tokens
- **Validation:** Pydantic models

**API Routers:**

| Router | Purpose | Endpoints |
|--------|---------|-----------|
| `auth` | Authentication & authorization | `/auth/login`, `/auth/register`, `/auth/refresh` |
| `projects` | Project CRUD operations | `/projects`, `/projects/{id}` |
| `content` | Content generation & management | `/content`, `/content/{id}/generate` |
| `distributions` | Distribution tracking & management | `/distributions`, `/distributions/{id}` |
| `usage` | Usage tracking & rate limits | `/usage`, `/usage/stats` |
| `health` | Health checks & monitoring | `/health`, `/health/detailed` |
| `docs` | API documentation | `/docs/openapi.json` |
| `admin` | Administrative functions | `/admin/users`, `/admin/stats` |
| `webhooks` | External service webhooks | `/webhooks/*` |
| `analytics` | Analytics & reporting | `/analytics/*` |
| `stripe` | Payment processing | `/stripe/*` |

**Middleware:**
- **ErrorTrackingMiddleware** - Captures and logs all errors
- **UsageTrackingMiddleware** - Tracks API usage and enforces rate limits
- **CORS Middleware** - Cross-origin resource sharing
- **GZip Middleware** - Response compression

**Hosting:** Render (Docker container, 512MB free tier)

---

### 3. Database Layer

#### Supabase (PostgreSQL)

**Purpose:** Primary database for application data

**Tables:**
- `users` - User accounts and profiles
- `projects` - Content projects
- `content` - Generated content pieces
- `distributions` - Distribution records
- `usage_records` - API usage tracking
- `webhook_logs` - Webhook delivery logs

**Features:**
- Row Level Security (RLS) for data isolation
- Real-time subscriptions (optional)
- Built-in authentication

#### Redis

**Purpose:** Caching and task queue

**Uses:**
- **Caching:** API response cache, session storage
- **Task Queue:** Celery message broker
- **Rate Limiting:** Token bucket implementation

**Hosting:** Render Redis (or self-hosted via Docker)

---

### 4. AI Layer

#### Groq API

**Purpose:** AI-powered content generation

**Models:**
- **Llama 3.3 70B** - Primary content generation model

**Capabilities:**
- Content repurposing (blog → social posts)
- Platform-native formatting
- Multi-language support
- Tone adjustment

**Services:**
- `extraction_service.py` - Content extraction from URLs/files
- `groq_service.py` - AI content generation interface

**Rate Limits:** 14M tokens/month free tier

---

### 5. Worker Layer (Celery)

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

---

### 6. Storage Layer

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

### 7. Automation Layer (n8n)

**Purpose:** Workflow automation and integrations

**Workflows:**
- Content distribution pipelines
- Social media posting
- Email notifications
- Webhook processing

**Hosting:** Self-hosted (Docker) or n8n cloud

---

### 8. External Services

| Service | Purpose | Integration |
|---------|---------|-------------|
| **Resend** | Email delivery | API |
| **Stripe** | Payment processing | API + Webhooks |
| **Twitter/X API** | Social distribution | n8n workflow |
| **LinkedIn API** | Social distribution | n8n workflow |
| **Webhooks** | External integrations | HTTP callbacks |

---

## Data Flow

### 1. Content Creation Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │────▶│ Frontend │────▶│  Backend │────▶│   AI     │────▶│ Database │
│(Browser) │     │ (Next.js)│     │ (FastAPI)│     │  (Groq)  │     │(Supabase)│
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                  │                │                │                │
     │  1. Login        │                │                │                │
     │────────────────▶│                │                │                │
     │                  │  2. Auth Req   │                │                │
     │                  │───────────────▶│                │                │
     │                  │                │  3. JWT Token  │                │
     │                  │◀───────────────│                │                │
     │  4. Create       │                │                │                │
     │     Project      │                │                │                │
     │────────────────▶│                │                │                │
     │                  │  5. POST       │                │                │
     │                  │  /projects     │                │                │
     │                  │───────────────▶│                │                │
     │                  │                │                │  6. Create     │
     │                  │                │───────────────────────────────▶│
     │                  │                │                │  7. Return ID  │
     │                  │                │◀──────────────│◀───────────────│
     │  8. Upload       │                │                │                │
     │     Content      │                │                │                │
     │────────────────▶│                │                │                │
     │                  │  9. POST       │                │                │
     │                  │  /content      │                │                │
     │                  │───────────────▶│                │                │
     │                  │                │ 10. Extract    │                │
     │                  │                │     Content    │                │
     │                  │                │                │                │
     │                  │                │ 11. Call AI    │                │
     │                  │                │    Service     │                │
     │                  │                │───────────────▶│                │
     │                  │                │                │12. Generate  │
     │                  │                │                │    Variants   │
     │                  │                │                │                │
     │                  │                │ 13. Return     │                │
     │                  │                │    Generated   │                │
     │                  │                │    Content     │                │
     │                  │                │◀──────────────│                │
     │                  │                │                │                │
     │                  │                │ 14. Store      │                │
     │                  │                │    Results     │                │
     │                  │                │───────────────────────────────▶│
     │                  │ 15. Response   │                │                │
     │                  │◀──────────────│◀──────────────│◀───────────────│
     │ 16. Display      │                │                │                │
     │     Content      │                │                │                │
     │◀─────────────────│                │                │                │
```

### 2. Distribution Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │────▶│ Frontend │────▶│  Backend │────▶│  Celery  │────▶│   n8n    │
│(Browser) │     │ (Next.js)│     │ (FastAPI)│     │  Worker  │     │(Workflow)│
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └────┬─────┘
     │                                                                     │
     │                                                                     ▼
     │                                                              ┌──────────┐
     │                                                              │ External │
     │                                                              │ Platforms│
     │                                                              │(Twitter, │
     │                                                              │LinkedIn) │
     │                                                              └──────────┘
```

**Steps:**
1. User selects content to distribute
2. Frontend sends distribution request
3. Backend validates and queues task
4. Celery worker processes distribution
5. n8n workflow handles platform-specific posting
6. Results tracked in database

### 3. Webhook Flow

```
┌────────────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ External       │────▶│  Backend │────▶│  Process │────▶│ Database │
│ Service        │     │ (FastAPI)│     │ Webhook  │     │(Supabase)│
│(Stripe, n8n)   │     │          │     │          │     │          │
└────────────────┘     └──────────┘     └──────────┘     └──────────┘
```

---

## Security Architecture

### Authentication Flow

```
┌─────────┐              ┌──────────┐              ┌───────────┐
│  User   │              │ Frontend │              │  Backend  │
└────┬────┘              └────┬─────┘              └─────┬─────┘
     │                        │                        │
     │  1. Login Request      │                        │
     │───────────────────────▶│                        │
     │                        │  2. POST /auth/login   │
     │                        │───────────────────────▶│
     │                        │                        │
     │                        │                        │  3. Validate
     │                        │                        │     with Supabase
     │                        │                        │
     │                        │  4. JWT Access Token    │
     │                        │◀───────────────────────│
     │  5. Store Token        │                        │
     │     (httpOnly cookie)  │                        │
     │◀───────────────────────│                        │
     │                        │                        │
     │  6. Authenticated      │                        │
     │     Requests           │                        │
     │     (Bearer Token)     │                        │
     │───────────────────────▶│───────────────────────▶│
```

### Security Measures

- **JWT Authentication** - Stateless token-based auth
- **Row Level Security** - Database-level access control
- **Rate Limiting** - Token bucket algorithm
- **CORS Protection** - Origin validation
- **HTTPS Only** - TLS 1.3 for all connections
- **Error Tracking** - Sentry integration for error monitoring

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

### Performance Optimizations

- **CDN** - Static assets served from edge
- **Caching** - Redis for API responses
- **Connection Pooling** - Database connections reused
- **Async Processing** - Celery for heavy tasks
- **GZIP Compression** - Response payload reduction

---

## Monitoring & Observability

### Health Endpoints

- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Component status

### Metrics

- **Application:** Response time, error rate, throughput
- **Infrastructure:** CPU, memory, disk, network
- **Business:** Active users, content generated, distributions sent

### Logging

- Structured JSON logging
- Request/response logging
- Error tracking with context

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

---

## Related Documentation

- [Project Status](./STATUS.md) - Current development status
- [Deployment Guide](../README.md#deployment) - Deployment instructions
- [API Documentation](./API.md) - API reference (auto-generated)
- [Environment Setup](../.env.production) - Environment variables
