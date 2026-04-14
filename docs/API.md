# ContentForge AI API Documentation

## Overview

The ContentForge AI API is a RESTful API for AI-powered content repurposing and distribution. The API is built with FastAPI and uses JWT Bearer token authentication via Supabase Auth.

**Base URL**: `https://api.contentforge.ai/api/v1`

**Current Version**: 2.0.0

**Route Summary**: 375 routes across 49 modules (184 GET | 124 POST | 15 PUT | 15 PATCH | 37 DELETE)

> **Full endpoint listing:** See [API_COMPLETE.md](./API_COMPLETE.md) for the complete reference of all 375 endpoints with parameters, request/response schemas, and examples.

---

## Authentication

The API uses JWT Bearer token authentication. All endpoints (except public health checks and authentication endpoints) require a valid access token.

### Authentication Methods

| Method | Endpoints | Description |
|--------|-----------|-------------|
| **Email/Password** | `POST /auth/login`, `POST /auth/register` | Standard credential auth via Supabase |
| **OIDC SSO** | `POST /sso/*`, `GET /sso/callback` | OpenID Connect single sign-on |
| **SAML SSO** | `POST /saml/*`, `GET /saml/acs` | SAML 2.0 single sign-on |

### Getting a Token

1. **Register** a new account via `POST /auth/register`
2. **Login** via `POST /auth/login` to receive an access token
3. **Use** the token in subsequent requests

### Using the Token

Include the token in the `Authorization` header with the `Bearer` scheme:

```
Authorization: Bearer <your_access_token>
```

---

## API Endpoint Categories

### Core Endpoints (6 modules)

| Module | Key Endpoints | Description |
|--------|--------------|-------------|
| **auth** | `/auth/register`, `/auth/login`, `/auth/logout`, `/auth/me` | Authentication & authorization |
| **user** | `/user/profile`, `/user/preferences` | User profile management |
| **organizations** | `/organizations`, `/organizations/{id}/members` | Organization CRUD & membership |
| **health** | `/health`, `/health/detailed` | System health checks |
| **docs** | `/docs/openapi.json` | API documentation |
| **admin** | `/admin/users`, `/admin/stats` | Administrative functions |

### Content Management (4 modules)

| Module | Key Endpoints | Description |
|--------|--------------|-------------|
| **projects** | `/projects`, `/projects/{id}` | Project CRUD operations |
| **content** | `/content`, `/content/{id}/generate` | Content generation & management |
| **distributions** | `/distributions`, `/distributions/{id}/publish` | Distribution tracking & management |
| **rss** | `/rss/feeds`, `/rss/entries` | RSS feed management |

### AI Features (2 modules)

| Module | Key Endpoints | Description |
|--------|--------------|-------------|
| **ai_editor** | `/ai/edit/rewrite`, `/ai/edit/expand`, `/ai/edit/condense`, `/ai/edit/optimize` | AI content editing operations |
| **ai_suggestions** | `/ai/suggestions`, `/ai/suggestions/{id}/apply` | AI-powered content suggestions |

### P4 Wave 1 — Insights & Reporting (6 modules)

| Module | Key Endpoints | Description |
|--------|--------------|-------------|
| **version_history** | `/content/{id}/versions`, `/content/{id}/versions/{vid}/rollback` | Content version tracking & rollback |
| **audit_logs** | `/audit-logs`, `/audit-logs/export` | System audit trail |
| **quality_scoring** | `/content/{id}/quality`, `/quality/bulk` | Content quality metrics |
| **sentiment** | `/sentiment/analyze`, `/sentiment/trends` | Sentiment analysis |
| **dashboards** | `/dashboards`, `/dashboards/{id}/widgets` | Custom dashboard CRUD |
| **reports** | `/reports`, `/reports/{id}/generate` | Report generation & scheduling |

### P4 Wave 2 — Intelligence & Governance (5 modules)

| Module | Key Endpoints | Description |
|--------|--------------|-------------|
| **suggestions** | `/suggestions`, `/suggestions/auto` | Auto-suggestion engine |
| **categorization** | `/categorization`, `/categorization/cluster` | Smart categorization & clustering |
| **performance** | `/performance/metrics`, `/performance/trends` | Performance analytics |
| **retention** | `/retention/policies`, `/retention/execute` | Data retention policies |
| **comments** | `/content/{id}/comments`, `/comments/{id}/replies` | Comments v2 with threading & resolution |

### P4 Wave 3 — Enterprise & Extensibility (7 modules)

| Module | Key Endpoints | Description |
|--------|--------------|-------------|
| **sso** | `/sso/providers`, `/sso/callback` | OIDC SSO authentication |
| **saml** | `/saml/metadata`, `/saml/acs` | SAML 2.0 SSO authentication |
| **plugins** | `/plugins`, `/plugins/{id}/install` | Plugin system management |
| **ws** | `/ws/connect` | WebSocket real-time connections |
| **collaboration** | `/collaboration/sessions`, `/collaboration/changes` | Real-time collaboration |
| **marketplace** | `/marketplace/plugins`, `/marketplace/templates` | Plugin/template marketplace |
| **notifications** | `/notifications`, `/notifications/{id}/read` | Notification management |

### P4 Wave 4 — Analytics & Integration (4 modules)

| Module | Key Endpoints | Description |
|--------|--------------|-------------|
| **funnel** | `/funnels`, `/funnels/{id}/stages` | Funnel tracking & analysis |
| **attribution** | `/attribution/models`, `/attribution/analyze` | Attribution modeling |
| **sla** | `/sla/definitions`, `/sla/alerts` | SLA monitoring & alerting |
| **integration_framework** | `/integrations/hub`, `/integrations/hub/{id}/configure` | Integration Hub framework |

### Analytics & Monitoring (6 modules)

| Module | Key Endpoints | Description |
|--------|--------------|-------------|
| **analytics** | `/analytics/dashboard`, `/analytics/kpis` | Analytics & reporting |
| **freshness** | `/freshness/scores`, `/freshness/bulk` | Content freshness scoring |
| **trends** | `/trends`, `/trends/emerging` | Trend tracking & analysis |
| **audience** | `/audience/segments`, `/audience/metrics` | Audience analytics |
| **alerts** | `/alerts`, `/alerts/{id}/acknowledge` | Alert management |
| **competitors** | `/competitors`, `/competitors/{id}/compare` | Competitor analysis |

### Automation & Utility (9 modules)

| Module | Key Endpoints | Description |
|--------|--------------|-------------|
| **automation** | `/automation/rules`, `/automation/rules/{id}/trigger` | Automation rules engine |
| **scheduler** | `/scheduler/schedules`, `/scheduler/schedules/{id}/execute` | Content scheduling |
| **search** | `/search`, `/search/suggestions` | Full-text search |
| **trash** | `/trash`, `/trash/{id}/restore` | Soft-delete & recovery |
| **usage** | `/usage`, `/usage/stats` | Usage tracking & rate limits |
| **webhooks** | `/webhooks`, `/webhooks/{id}/deliveries` | External service webhooks |
| **integrations** | `/integrations`, `/integrations/{id}/connect` | Third-party integrations |
| **stripe** | `/stripe/checkout`, `/stripe/webhook` | Payment processing |
| **presence** | `/presence/online`, `/presence/{user_id}` | Real-time user presence |

---

## Example Requests & Responses

### POST /api/v1/auth/register

Register a new user account.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**curl Example:**

```bash
curl -X POST "https://api.contentforge.ai/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

**Success Response (201 Created):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "subscription_tier": "free"
  }
}
```

---

### POST /api/v1/auth/login

Login to obtain an access token.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Success Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "subscription_tier": "free"
  }
}
```

---

## AI Content Editor Examples

### POST /api/v1/ai/edit/rewrite

Rewrite content with a different tone and style.

**Request Body:**

```json
{
  "content": "Our company provides excellent software development services.",
  "tone": "witty",
  "style": "persuasive"
}
```

**Success Response (200 OK):**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "operation": "rewrite",
  "original_content": "Our company provides excellent software development services...",
  "rewritten_content": "We're the code wizards your business has been waiting for...",
  "tone": "witty",
  "style": "persuasive",
  "tokens_used": 245,
  "created_at": "2026-04-13T11:30:00Z"
}
```

**Supported Tones:** casual, professional, witty, formal, friendly, authoritative, enthusiastic, empathetic

**Supported Styles:** neutral, persuasive, informative, storytelling, concise, descriptive

---

### POST /api/v1/ai/edit/optimize

Optimize content for a specific platform.

**Request Body:**

```json
{
  "content": "We just launched our new AI-powered content creation tool.",
  "platform": "twitter",
  "include_hashtags": true,
  "include_cta": true
}
```

**Supported Platforms:** twitter, linkedin, blog, newsletter, instagram, tiktok

---

## P4 Endpoint Examples

### Version History

```bash
# List versions for a content item
curl "https://api.contentforge.ai/api/v1/content/{id}/versions" \
  -H "Authorization: Bearer <token>"

# Rollback to a specific version
curl -X POST "https://api.contentforge.ai/api/v1/content/{id}/versions/{version_id}/rollback" \
  -H "Authorization: Bearer <token>"
```

### Quality Scoring

```bash
# Get quality score for content
curl "https://api.contentforge.ai/api/v1/content/{id}/quality" \
  -H "Authorization: Bearer <token>"

# Bulk quality analysis
curl -X POST "https://api.contentforge.ai/api/v1/quality/bulk" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"content_ids": ["id1", "id2", "id3"]}'
```

### Funnel Tracking

```bash
# List funnels
curl "https://api.contentforge.ai/api/v1/funnels" \
  -H "Authorization: Bearer <token>"

# Get funnel stage analytics
curl "https://api.contentforge.ai/api/v1/funnels/{id}/stages" \
  -H "Authorization: Bearer <token>"
```

### Integration Hub

```bash
# List available integrations
curl "https://api.contentforge.ai/api/v1/integrations/hub" \
  -H "Authorization: Bearer <token>"

# Configure an integration
curl -X POST "https://api.contentforge.ai/api/v1/integrations/hub/{id}/configure" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"settings": {"api_key": "...", "sync_interval": 300}}'
```

---

## Error Responses

All API errors follow this format:

```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created successfully |
| 304 | Not Modified (ETag match) |
| 400 | Bad request — invalid input |
| 401 | Unauthorized — invalid or missing token |
| 404 | Resource not found |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

---

## Rate Limiting

API requests are subject to rate limiting based on subscription tier:

| Tier | Requests/Hour | Generations/Month |
|------|---------------|-------------------|
| Free | 100 | 10 |
| Pro | 1,000 | 100 |
| Enterprise | 10,000 | Unlimited |

Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1713520800
```

---

## Performance Response Headers

All API responses include performance and tracing headers:

| Header | Description |
|--------|-------------|
| `X-Response-Time` | Request processing time in milliseconds |
| `X-Request-ID` | Unique identifier for request tracing |
| `ETag` | Resource version hash (conditional requests) |
| `Cache-Control` | Caching directives |

---

## Data Types

### Content Status

- `pending` — Content is being processed
- `completed` — Content extraction complete
- `failed` — Content extraction failed

### Asset Types

- `thread` — Twitter/X thread
- `social_post` — Social media post
- `newsletter` — Email newsletter
- `video_script` — Short-form video script

### Source Types

- `url` — Web page URL
- `youtube` — YouTube video URL
- `text` — Raw text input
- `upload` — Uploaded file (audio/video)

---

## OpenAPI Specification

The API provides interactive documentation via Swagger UI and ReDoc:

- **Swagger UI**: `/docs` (development only)
- **ReDoc**: `/redoc` (development only)

These endpoints provide complete OpenAPI specification for all endpoints, schemas, and authentication methods.

---

## Support

For API support or questions:

- Documentation: https://docs.contentforge.ai
- Support Email: support@contentforge.ai
- Status Page: https://status.contentforge.ai

---

*Last updated: 2026-04-14*