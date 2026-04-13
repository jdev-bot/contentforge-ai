# ContentForge AI API Documentation

## Overview

The ContentForge AI API is a RESTful API for AI-powered content repurposing and distribution. The API is built with FastAPI and uses JWT Bearer token authentication via Supabase Auth.

**Base URL**: `https://api.contentforge.ai/api/v1`

**Current Version**: 1.0.0

---

## Authentication

The API uses JWT Bearer token authentication. All endpoints (except public health checks and authentication endpoints) require a valid access token.

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

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and get access token |
| POST | `/auth/logout` | Logout current user |
| GET | `/auth/me` | Get current user profile |
| PATCH | `/auth/me` | Update user profile |

### Content Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/content` | Create new content from source |
| GET | `/content` | List all user content |
| GET | `/content/{id}` | Get specific content |
| DELETE | `/content/{id}` | Delete content |
| POST | `/content/{id}/generate` | Generate repurposed assets |
| GET | `/content/{id}/assets` | List generated assets |

### Project Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/projects` | Create new project |
| GET | `/projects` | List all projects |
| GET | `/projects/{id}` | Get specific project |
| PATCH | `/projects/{id}` | Update project |
| DELETE | `/projects/{id}` | Delete project |

### Distribution Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/distributions` | Create distribution |
| GET | `/distributions` | List distributions |
| GET | `/distributions/{id}` | Get specific distribution |
| POST | `/distributions/{id}/publish` | Publish to platform |

### Usage & Health Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check (public) |
| GET | `/usage` | Get usage statistics |

### AI Content Editor Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ai/edit/rewrite` | Rewrite content with different tone/style |
| POST | `/ai/edit/expand` | Expand content with more detail |
| POST | `/ai/edit/condense` | Condense content to be shorter |
| POST | `/ai/edit/optimize` | Optimize content for specific platform |
| GET | `/ai/edit/history` | Get editor operation history |

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

**Error Response (400 Bad Request):**

```json
{
  "detail": "Registration failed"
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

**curl Example:**

```bash
curl -X POST "https://api.contentforge.ai/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
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

**Error Response (401 Unauthorized):**

```json
{
  "detail": "Invalid credentials"
}
```

---

## AI Content Editor Examples

### POST /api/v1/ai/edit/rewrite

Rewrite content with a different tone and style.

**Headers:**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "content": "Our company provides excellent software development services. We help businesses build scalable applications.",
  "tone": "witty",
  "style": "persuasive"
}
```

**curl Example:**

```bash
curl -X POST "https://api.contentforge.ai/api/v1/ai/edit/rewrite" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Our company provides excellent software development services. We help businesses build scalable applications.",
    "tone": "witty",
    "style": "persuasive"
  }'
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

**Supported Tones:**
- `casual` - Relaxed, conversational
- `professional` - Business-appropriate
- `witty` - Clever and humorous
- `formal` - Academic and sophisticated
- `friendly` - Warm and approachable
- `authoritative` - Confident and expert
- `enthusiastic` - Excited and energetic
- `empathetic` - Understanding and compassionate

**Supported Styles:**
- `neutral` - Balanced and objective
- `persuasive` - Convincing and compelling
- `informative` - Educational and factual
- `storytelling` - Narrative-driven
- `concise` - Brief and to-the-point
- `descriptive` - Vivid and sensory

---

### POST /api/v1/ai/edit/expand

Expand content with more detail and depth.

**Request Body:**

```json
{
  "content": "We help businesses grow through digital marketing.",
  "target_length": 3,
  "focus_areas": ["strategies", "case studies"]
}
```

**curl Example:**

```bash
curl -X POST "https://api.contentforge.ai/api/v1/ai/edit/expand" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "content": "We help businesses grow through digital marketing.",
    "target_length": 3,
    "focus_areas": ["strategies", "case studies"]
  }'
```

**Success Response (200 OK):**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "operation": "expand",
  "original_content": "We help businesses grow through digital marketing.",
  "expanded_content": "At our core, we specialize in helping businesses achieve remarkable growth through comprehensive digital marketing strategies. Our approach combines data-driven insights with creative execution to deliver measurable results...",
  "target_length": 3,
  "actual_expansion_ratio": 2.8,
  "tokens_used": 890,
  "created_at": "2026-04-13T11:31:00Z"
}
```

---

### POST /api/v1/ai/edit/condense

Condense content while preserving key points.

**Request Body:**

```json
{
  "content": "Our comprehensive guide to digital marketing covers everything from SEO to social media advertising. We dive deep into keyword research, content strategy, paid campaigns, and analytics. Learn how to optimize your website for search engines, create engaging social media content, run effective ad campaigns, and measure your results using advanced analytics tools.",
  "target_percentage": 40,
  "preserve_key_points": true
}
```

**curl Example:**

```bash
curl -X POST "https://api.contentforge.ai/api/v1/ai/edit/condense" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Our comprehensive guide to digital marketing covers everything...",
    "target_percentage": 40,
    "preserve_key_points": true
  }'
```

**Success Response (200 OK):**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "operation": "condense",
  "original_content": "Our comprehensive guide to digital marketing covers everything...",
  "condensed_content": "Master digital marketing with our guide covering SEO, social media, paid campaigns, and analytics. Learn optimization, content creation, ad management, and results measurement.",
  "target_percentage": 40,
  "actual_reduction_percentage": 45.2,
  "tokens_used": 320,
  "created_at": "2026-04-13T11:32:00Z"
}
```

---

### POST /api/v1/ai/edit/optimize

Optimize content for a specific platform.

**Request Body:**

```json
{
  "content": "We just launched our new AI-powered content creation tool that helps businesses generate engaging social media posts, newsletters, and blog content in minutes.",
  "platform": "twitter",
  "include_hashtags": true,
  "include_cta": true
}
```

**curl Example:**

```bash
curl -X POST "https://api.contentforge.ai/api/v1/ai/edit/optimize" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "content": "We just launched our new AI-powered content creation tool...",
    "platform": "twitter",
    "include_hashtags": true,
    "include_cta": true
  }'
```

**Success Response (200 OK):**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "operation": "optimize",
  "original_content": "We just launched our new AI-powered content creation tool...",
  "optimized_content": "🚀 Big news! Our AI content tool is LIVE\n\nCreate engaging posts, newsletters & blogs in MINUTES\n\nNo more writer's block ✨\n\nReady to transform your content game?\n\nTry it free →\n\n#AI #ContentCreation #Marketing",
  "platform": "twitter",
  "character_count": 234,
  "word_count": 32,
  "tokens_used": 450,
  "created_at": "2026-04-13T11:33:00Z"
}
```

**Supported Platforms:**
- `twitter` - Up to 280 characters, punchy style
- `linkedin` - Professional, thought leadership
- `blog` - SEO-optimized, structured format
- `newsletter` - Personal, conversational
- `instagram` - Engaging captions with hashtags
- `tiktok` - Trendy, authentic style

---

### GET /api/v1/ai/edit/history

Get history of AI editor operations.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| limit | integer | Number of results (default: 50) |
| operation | string | Filter by operation type |

**curl Example:**

```bash
# Get all history
curl "https://api.contentforge.ai/api/v1/ai/edit/history" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."

# Filter by operation type
curl "https://api.contentforge.ai/api/v1/ai/edit/history?operation=rewrite&limit=10" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**Success Response (200 OK):**

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "content_id": "content-uuid",
    "operation": "rewrite",
    "original_preview": "Our company provides...",
    "result_preview": "We're the code wizards...",
    "tokens_used": 245,
    "created_at": "2026-04-13T11:30:00Z"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440003",
    "operation": "optimize",
    "original_preview": "We just launched...",
    "result_preview": "🚀 Big news!...",
    "tokens_used": 450,
    "created_at": "2026-04-13T11:33:00Z"
  }
]
```

---

### POST /api/v1/content

Create new content from a source (URL, YouTube, or text).

**Headers:**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "title": "My Blog Post Analysis",
  "source": {
    "type": "url",
    "url": "https://example.com/article"
  },
  "project_id": "project-uuid"
}
```

**curl Example:**

```bash
curl -X POST "https://api.contentforge.ai/api/v1/content" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Blog Post Analysis",
    "source": {
      "type": "url",
      "url": "https://example.com/article"
    },
    "project_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Alternative - YouTube Source:**

```bash
curl -X POST "https://api.contentforge.ai/api/v1/content" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "YouTube Video Summary",
    "source": {
      "type": "youtube",
      "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    },
    "project_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Alternative - Text Source:**

```bash
curl -X POST "https://api.contentforge.ai/api/v1/content" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Direct Text Input",
    "source": {
      "type": "text",
      "text": "Your raw text content here..."
    },
    "project_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Success Response (201 Created):**

```json
{
  "id": "content-uuid",
  "project_id": "project-uuid",
  "user_id": "user-uuid",
  "title": "My Blog Post Analysis",
  "source_type": "url",
  "source_url": "https://example.com/article",
  "original_text": "Extracted text content from the URL...",
  "word_count": 1500,
  "status": "completed",
  "created_at": "2026-04-12T14:00:00Z",
  "updated_at": "2026-04-12T14:00:00Z"
}
```

**Error Response (400 Bad Request):**

```json
{
  "detail": "Invalid source URL"
}
```

---

### GET /api/v1/content

List all content for the authenticated user.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| project_id | UUID | Filter by project |
| status | string | Filter by status (pending, completed, failed) |

**curl Example:**

```bash
# List all content
curl "https://api.contentforge.ai/api/v1/content" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."

# Filter by project
curl "https://api.contentforge.ai/api/v1/content?project_id=550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."

# Filter by status
curl "https://api.contentforge.ai/api/v1/content?status=completed" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**Success Response (200 OK):**

```json
[
  {
    "id": "content-uuid-1",
    "project_id": "project-uuid",
    "user_id": "user-uuid",
    "title": "My Blog Post Analysis",
    "source_type": "url",
    "source_url": "https://example.com/article",
    "original_text": "Extracted text content...",
    "word_count": 1500,
    "status": "completed",
    "created_at": "2026-04-12T14:00:00Z",
    "updated_at": "2026-04-12T14:00:00Z"
  },
  {
    "id": "content-uuid-2",
    "project_id": "project-uuid",
    "user_id": "user-uuid",
    "title": "YouTube Video Summary",
    "source_type": "youtube",
    "source_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "original_text": "Video transcript...",
    "word_count": 2500,
    "status": "completed",
    "created_at": "2026-04-12T13:00:00Z",
    "updated_at": "2026-04-12T13:00:00Z"
  }
]
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
| 400 | Bad request - invalid input |
| 401 | Unauthorized - invalid or missing token |
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

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1713520800
```

---

## Data Types

### Content Status

- `pending` - Content is being processed
- `completed` - Content extraction complete
- `failed` - Content extraction failed

### Asset Types

- `thread` - Twitter/X thread
- `social_post` - Social media post
- `newsletter` - Email newsletter
- `video_script` - Short-form video script

### Source Types

- `url` - Web page URL
- `youtube` - YouTube video URL
- `text` - Raw text input
- `upload` - Uploaded file (audio/video)

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
