# ContentForge AI API Documentation

> Complete API Reference with 50+ Endpoints

## Overview

The ContentForge AI API is a RESTful API for AI-powered content repurposing and distribution. Built with FastAPI and uses JWT Bearer token authentication via Supabase Auth.

**Base URL**: `https://api.contentforge.ai/api/v1`

**Current Version**: 1.0.0

---

## Table of Contents

1. [Authentication](#authentication)
2. [Core Endpoints](#core-endpoints)
   - [Health](#health-endpoints)
   - [Auth](#authentication-endpoints)
   - [User](#user-endpoints)
   - [Organizations](#organization-endpoints)
3. [Content Management](#content-management)
   - [Projects](#project-endpoints)
   - [Content](#content-endpoints)
   - [Distributions](#distribution-endpoints)
4. [AI Features](#ai-features)
   - [AI Editor](#ai-content-editor-endpoints)
   - [AI Suggestions](#ai-suggestions-endpoints)
5. [Analytics & Insights](#analytics--insights)
   - [Analytics](#analytics-endpoints)
   - [Freshness](#freshness-endpoints)
   - [Trends](#trends-endpoints)
   - [Audience](#audience-endpoints)
6. [Automation](#automation)
   - [Scheduler](#scheduler-endpoints)
   - [Automation Rules](#automation-endpoints)
   - [RSS](#rss-endpoints)
7. [Monitoring](#monitoring)
   - [Alerts](#alerts-endpoints)
   - [Competitors](#competitors-endpoints)
8. [Integrations](#integrations)
   - [Third-Party Integrations](#integrations-endpoints)
   - [Webhooks](#webhook-endpoints)
9. [Utility](#utility)
   - [Search](#search-endpoints)
   - [Trash](#trash-endpoints)
   - [Usage](#usage-endpoints)
10. [Rate Limits & Errors](#rate-limits--error-codes)

---

## Authentication

The API uses JWT Bearer token authentication. All endpoints (except public health checks) require a valid access token.

### Getting a Token

1. **Register** a new account via `POST /auth/register`
2. **Login** via `POST /auth/login` to receive an access token
3. **Use** the token in subsequent requests

### Using the Token

Include the token in the `Authorization` header:

```
Authorization: Bearer <your_access_token>
```

---

## Core Endpoints

### Health Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Health check (public) | No |
| GET | `/` | Root endpoint with API info | No |

#### GET /health

**Success Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-13T10:00:00Z"
}
```

---

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and get access token |
| POST | `/auth/logout` | Logout current user |
| GET | `/auth/me` | Get current user profile |
| PATCH | `/auth/me` | Update user profile |

#### POST /auth/register

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
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
    "subscription_tier": "free",
    "monthly_usage_count": 0,
    "monthly_usage_limit": 10
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "Registration failed"
}
```

#### POST /auth/login

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
    "subscription_tier": "free",
    "monthly_usage_count": 2,
    "monthly_usage_limit": 10
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

### User Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/user/profile` | Get user profile |
| PATCH | `/user/profile` | Update profile |
| GET | `/user/settings` | Get user settings |
| PATCH | `/user/settings` | Update settings |
| GET | `/user/subscription` | Get subscription info |

---

### Organization Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/organizations` | Create organization |
| GET | `/organizations` | List organizations |
| GET | `/organizations/{id}` | Get organization |
| PATCH | `/organizations/{id}` | Update organization |
| DELETE | `/organizations/{id}` | Delete organization |
| GET | `/organizations/{id}/members` | List members |
| POST | `/organizations/{id}/members` | Add member |
| DELETE | `/organizations/{id}/members/{user_id}` | Remove member |

---

## Content Management

### Project Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/projects` | Create new project |
| GET | `/projects` | List all projects |
| GET | `/projects/{id}` | Get specific project |
| PATCH | `/projects/{id}` | Update project |
| DELETE | `/projects/{id}` | Delete project (soft) |

#### POST /projects

Create a new content project.

**Request Body:**
```json
{
  "name": "My Content Project",
  "description": "Marketing content for Q2 2026",
  "brand_voice": {
    "tone": "professional",
    "style": "friendly"
  },
  "target_platforms": ["twitter", "linkedin", "blog"]
}
```

**Success Response (201 Created):**
```json
{
  "id": "project-uuid",
  "user_id": "user-uuid",
  "name": "My Content Project",
  "description": "Marketing content for Q2 2026",
  "brand_voice": {
    "tone": "professional",
    "style": "friendly"
  },
  "target_platforms": ["twitter", "linkedin", "blog"],
  "created_at": "2026-04-13T10:00:00Z",
  "updated_at": "2026-04-13T10:00:00Z",
  "is_active": true
}
```

---

### Content Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/content` | Create new content |
| GET | `/content` | List all content |
| GET | `/content/{id}` | Get specific content |
| DELETE | `/content/{id}` | Delete content |
| POST | `/content/{id}/generate` | Generate repurposed assets |
| GET | `/content/{id}/assets` | List generated assets |
| POST | `/upload` | Upload file (audio/video) |

#### POST /content

Create new content from a source.

**Source Types:**
- `url` - Web page URL
- `youtube` - YouTube video URL
- `text` - Raw text input
- `upload` - Uploaded file

**Request Body:**
```json
{
  "title": "My Blog Post Analysis",
  "source": {
    "type": "url",
    "url": "https://example.com/article"
  },
  "project_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Alternative - YouTube:**
```json
{
  "title": "YouTube Video Summary",
  "source": {
    "type": "youtube",
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  },
  "project_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Alternative - Text:**
```json
{
  "title": "Direct Text Input",
  "source": {
    "type": "text",
    "text": "Your raw text content here..."
  },
  "project_id": "550e8400-e29b-41d4-a716-446655440000"
}
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

#### POST /content/{id}/generate

Generate repurposed assets from content using AI.

**Success Response (200 OK):**
```json
[
  {
    "id": "asset-uuid-1",
    "content_id": "content-uuid",
    "user_id": "user-uuid",
    "type": "thread",
    "platform": "twitter",
    "content": "🧵 Thread post content...",
    "tokens_used": 245,
    "status": "generated",
    "created_at": "2026-04-12T14:05:00Z"
  },
  {
    "id": "asset-uuid-2",
    "content_id": "content-uuid",
    "user_id": "user-uuid",
    "type": "social_post",
    "platform": "linkedin",
    "content": "LinkedIn post content...",
    "tokens_used": 180,
    "status": "generated",
    "created_at": "2026-04-12T14:06:00Z"
  }
]
```

---

### Distribution Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/distributions` | Create distribution |
| GET | `/distributions` | List distributions |
| GET | `/distributions/{id}` | Get specific distribution |
| PATCH | `/distributions/{id}` | Update distribution |
| DELETE | `/distributions/{id}` | Cancel distribution |
| POST | `/distributions/{id}/publish` | Publish immediately |

#### POST /distributions

Schedule a new distribution.

**Request Body:**
```json
{
  "asset_id": "550e8400-e29b-41d4-a716-446655440000",
  "platform": "twitter",
  "scheduled_at": "2026-04-14T10:00:00Z"
}
```

**Supported Platforms:**
- `twitter` - X/Twitter
- `linkedin` - LinkedIn
- `instagram` - Instagram
- `facebook` - Facebook
- `tiktok` - TikTok
- `email` - Email newsletter
- `blog` - Blog post

**Success Response (201 Created):**
```json
{
  "id": "distribution-uuid",
  "asset_id": "asset-uuid",
  "user_id": "user-uuid",
  "platform": "twitter",
  "status": "scheduled",
  "scheduled_at": "2026-04-14T10:00:00Z",
  "published_url": null,
  "external_id": null,
  "error_message": null,
  "retry_count": 0,
  "created_at": "2026-04-13T10:00:00Z",
  "updated_at": "2026-04-13T10:00:00Z"
}
```

---

## AI Features

### AI Content Editor Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ai/edit/rewrite` | Rewrite with different tone/style |
| POST | `/ai/edit/expand` | Expand content with more detail |
| POST | `/ai/edit/condense` | Condense content shorter |
| POST | `/ai/edit/optimize` | Optimize for platform |
| GET | `/ai/edit/history` | Get editor operation history |

#### POST /ai/edit/rewrite

Rewrite content with a different tone and style.

**Request Body:**
```json
{
  "content": "Our company provides excellent software development services. We help businesses build scalable applications.",
  "tone": "witty",
  "style": "persuasive"
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

#### POST /ai/edit/expand

Expand content with more detail.

**Request Body:**
```json
{
  "content": "We help businesses grow through digital marketing.",
  "target_length": 3,
  "focus_areas": ["strategies", "case studies"]
}
```

**Success Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "operation": "expand",
  "original_content": "We help businesses grow through digital marketing.",
  "expanded_content": "At our core, we specialize in helping businesses achieve remarkable growth through comprehensive digital marketing strategies...",
  "target_length": 3,
  "actual_expansion_ratio": 2.8,
  "tokens_used": 890,
  "created_at": "2026-04-13T11:31:00Z"
}
```

#### POST /ai/edit/condense

Condense content while preserving key points.

**Request Body:**
```json
{
  "content": "Our comprehensive guide to digital marketing covers everything from SEO to social media advertising...",
  "target_percentage": 40,
  "preserve_key_points": true
}
```

**Success Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "operation": "condense",
  "original_content": "Our comprehensive guide to digital marketing covers everything...",
  "condensed_content": "Master digital marketing with our guide covering SEO, social media, paid campaigns, and analytics...",
  "target_percentage": 40,
  "actual_reduction_percentage": 45.2,
  "tokens_used": 320,
  "created_at": "2026-04-13T11:32:00Z"
}
```

#### POST /ai/edit/optimize

Optimize content for a specific platform.

**Request Body:**
```json
{
  "content": "We just launched our new AI-powered content creation tool that helps businesses generate engaging social media posts...",
  "platform": "twitter",
  "include_hashtags": true,
  "include_cta": true
}
```

**Supported Platforms:**
- `twitter` - Up to 280 characters, punchy style
- `linkedin` - Professional, thought leadership
- `blog` - SEO-optimized, structured format
- `newsletter` - Personal, conversational
- `instagram` - Engaging captions with hashtags
- `tiktok` - Trendy, authentic style

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

---

### AI Suggestions Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ai-suggestions/improve` | Get improvement suggestions |
| POST | `/ai-suggestions/seo` | SEO analysis |
| POST | `/ai-suggestions/tone` | Tone analysis |
| GET | `/ai-suggestions/{content_id}` | Get suggestions for content |
| PATCH | `/ai-suggestions/{id}/apply` | Apply suggestion |
| POST | `/ai-suggestions/rewrite` | Legacy rewrite endpoint |

---

## Analytics & Insights

### Analytics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/dashboard` | Dashboard KPIs |
| GET | `/analytics/content` | Content metrics |
| GET | `/analytics/assets` | Asset metrics |
| GET | `/analytics/distributions` | Distribution metrics |
| GET | `/analytics/usage` | Usage over time |
| GET | `/analytics/export/csv` | Export activity (CSV) |
| GET | `/analytics/export/json` | Export activity (JSON) |

#### GET /analytics/dashboard

Get key performance indicators.

**Success Response (200 OK):**
```json
{
  "total_content": 42,
  "total_assets": 156,
  "total_distributions": 89,
  "published_distributions": 78,
  "content_growth_30d": 8,
  "asset_growth_30d": 24,
  "distribution_success_rate": 87.64
}
```

#### GET /analytics/usage

Get usage statistics over time.

**Query Parameters:**
- `days` - Number of days to fetch (7-365, default: 30)

**Success Response (200 OK):**
```json
{
  "daily_counts": [
    {"date": "2026-03-14", "count": 5},
    {"date": "2026-03-15", "count": 8}
  ],
  "weekly_counts": [
    {"week": "2026-W11", "count": 45}
  ],
  "monthly_counts": [
    {"month": "2026-03", "count": 156}
  ],
  "total_in_period": 156,
  "average_daily": 5.2
}
```

---

### Freshness Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/freshness/analyze/{content_id}` | Analyze content freshness |
| GET | `/freshness/{content_id}` | Get freshness score |
| GET | `/freshness/stale` | List stale content |
| POST | `/freshness/bulk-analyze` | Bulk analyze freshness |
| GET | `/freshness/dashboard` | Freshness dashboard |

#### POST /freshness/analyze/{content_id}

Analyze content freshness and store the score.

**Request Body:**
```json
{
  "force_reanalyze": false
}
```

**Success Response (200 OK):**
```json
{
  "content_id": "550e8400-e29b-41d4-a716-446655440000",
  "freshness_score": 72,
  "age_days": 45,
  "status": "good",
  "factors": {
    "age_factor": 0.8,
    "engagement_factor": 0.9,
    "trend_factor": 0.7,
    "age_points": 25,
    "engagement_points": 30,
    "trend_points": 17
  },
  "recommendations": [
    "Update statistics and data points",
    "Refresh trending hashtags"
  ],
  "message": "Freshness analysis completed"
}
```

**Freshness Scores:**
- 80-100: `fresh` - Recently created content
- 60-79: `good` - Content is still relevant
- 40-59: `aging` - Consider updating soon
- 20-39: `stale` - Needs refresh
- 0-19: `outdated` - Requires significant update

---

### Trends Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/trends` | List trending topics |
| GET | `/trends/relevant` | Relevant trends for user |
| GET | `/trends/categories` | Trends by category |
| GET | `/trends/{id}` | Get trend details |
| POST | `/trends/track` | Track a topic |
| GET | `/trends/tracked` | Get tracked topics |
| DELETE | `/trends/tracked/{id}` | Untrack topic |
| GET | `/trends/velocity` | Velocity leaderboard |
| GET | `/trends/insights` | Trend insights |
| POST | `/trends/refresh` | Refresh trends (admin) |
| GET | `/trends/search` | Search trends |
| POST | `/trends/generate-content` | Generate from trend |

#### POST /trends/generate-content

Generate content based on a trending topic.

**Request Body:**
```json
{
  "topic": "AI in Marketing",
  "category": "technology",
  "platform": "linkedin",
  "tone": "professional"
}
```

**Success Response (200 OK):**
```json
{
  "topic": "AI in Marketing",
  "platform": "linkedin",
  "headline": "How AI is Revolutionizing Marketing in 2026",
  "content": "AI is transforming how marketers approach customer engagement...",
  "angles": [
    "Personalization at scale",
    "Predictive analytics",
    "Automated content creation"
  ],
  "hashtags": ["#AIMarketing", "#MarketingTrends", "#DigitalTransformation"],
  "cta": "What's your experience with AI in marketing? Share in the comments!",
  "saved_suggestion_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### Audience Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/audience/insights` | Audience insights |
| GET | `/audience/segments` | Audience segments |
| GET | `/audience/growth` | Growth metrics |
| GET | `/audience/engagement` | Engagement by time |

---

## Automation

### Scheduler Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/schedule` | Schedule a post |
| GET | `/schedule` | List scheduled posts |
| GET | `/schedule/{id}` | Get scheduled post |
| PUT | `/schedule/{id}` | Update scheduled post |
| DELETE | `/schedule/{id}` | Cancel scheduled post |
| POST | `/schedule/{id}/publish-now` | Publish immediately |
| GET | `/schedule/stats` | Scheduler statistics |
| GET | `/schedule/upcoming` | Upcoming posts |
| POST | `/schedule/bulk` | Bulk schedule posts |

#### POST /schedule

Schedule a new post for automated publishing.

**Request Body:**
```json
{
  "content_id": "550e8400-e29b-41d4-a716-446655440000",
  "asset_id": "550e8400-e29b-41d4-a716-446655440001",
  "platform": "twitter",
  "scheduled_at": "2026-04-14T14:00:00Z",
  "asset_type": "post",
  "settings": {
    "thread_mode": false,
    "auto_hashtags": true
  },
  "timezone": "America/New_York",
  "content": "Post content here..."
}
```

**Success Response (201 Created):**
```json
{
  "id": "schedule-uuid",
  "user_id": "user-uuid",
  "content_id": "content-uuid",
  "asset_id": "asset-uuid",
  "platform": "twitter",
  "scheduled_at": "2026-04-14T14:00:00Z",
  "status": "pending",
  "asset_type": "post",
  "settings": {...},
  "content": "Post content here...",
  "retry_count": 0,
  "max_retries": 3,
  "timezone": "America/New_York",
  "created_at": "2026-04-13T10:00:00Z",
  "updated_at": "2026-04-13T10:00:00Z"
}
```

---

### Automation Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/automation/rules` | Create automation rule |
| GET | `/automation/rules` | List automation rules |
| GET | `/automation/rules/{id}` | Get automation rule |
| PATCH | `/automation/rules/{id}` | Update automation rule |
| DELETE | `/automation/rules/{id}` | Delete automation rule |
| POST | `/automation/rules/{id}/toggle` | Toggle rule status |
| POST | `/automation/rules/{id}/run` | Run rule manually |
| GET | `/automation/logs` | Get execution logs |
| POST | `/automation/webhooks` | Create webhook endpoint |
| GET | `/automation/webhooks` | List webhook endpoints |
| DELETE | `/automation/webhooks/{id}` | Delete webhook endpoint |
| GET | `/automation/queue` | Get publishing queue |
| POST | `/automation/queue/{id}/cancel` | Cancel queue item |
| POST | `/automation/queue/{id}/retry` | Retry failed item |
| GET | `/automation/best-times/{platform}` | Get best posting times |
| POST | `/automation/schedule/bulk` | Bulk schedule content |

#### Trigger Types
- `content_created` - When new content is created
- `content_updated` - When content is updated
- `scheduled_time` - Based on schedule
- `webhook_received` - External webhook trigger
- `usage_threshold` - When usage threshold reached
- `manual` - Manual trigger

#### Action Types
- `generate_assets` - Generate content assets
- `publish_content` - Publish to platform
- `send_email` - Send notification email
- `call_webhook` - Call external webhook
- `update_status` - Update content status
- `create_task` - Create task

---

### RSS Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/rss/feeds` | Add RSS feed |
| GET | `/rss/feeds` | List RSS feeds |
| GET | `/rss/feeds/{id}` | Get RSS feed |
| PATCH | `/rss/feeds/{id}` | Update RSS feed |
| DELETE | `/rss/feeds/{id}` | Delete RSS feed |
| POST | `/rss/feeds/{id}/fetch` | Manual fetch |
| GET | `/rss/entries` | List RSS entries |
| GET | `/rss/entries/{id}` | Get RSS entry |
| POST | `/rss/entries/{id}/import` | Import as content |
| POST | `/rss/feeds/{id}/import-all` | Import all entries |

#### POST /rss/feeds

Add a new RSS feed for monitoring.

**Request Body:**
```json
{
  "name": "TechCrunch RSS",
  "url": "https://techcrunch.com/feed/",
  "fetch_frequency": "hourly",
  "auto_create_content": false
}
```

**Success Response (201 Created):**
```json
{
  "id": "feed-uuid",
  "user_id": "user-uuid",
  "name": "TechCrunch RSS",
  "url": "https://techcrunch.com/feed/",
  "last_fetched_at": null,
  "fetch_frequency": "hourly",
  "auto_create_content": false,
  "status": "active",
  "error_message": null,
  "created_at": "2026-04-13T10:00:00Z",
  "updated_at": "2026-04-13T10:00:00Z"
}
```

---

## Monitoring

### Alerts Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/alerts` | List alerts |
| POST | `/alerts/acknowledge/{id}` | Acknowledge alert |
| POST | `/alerts/resolve/{id}` | Resolve alert |
| GET | `/alerts/unread-count` | Get unread count |
| GET | `/alerts/rules` | List alert rules |
| POST | `/alerts/rules` | Create alert rule |
| PUT | `/alerts/rules/{id}` | Update alert rule |
| DELETE | `/alerts/rules/{id}` | Delete alert rule |
| POST | `/alerts/check-metrics` | Check content metrics |
| GET | `/alerts/notifications` | List notifications |
| POST | `/alerts/notifications/{id}/read` | Mark as read |
| POST | `/alerts/notifications/mark-all-read` | Mark all read |

#### POST /alerts/rules

Create a new alert rule.

**Request Body:**
```json
{
  "name": "Viral Content Alert",
  "alert_type": "viral",
  "metric_name": "views",
  "operator": "greater_than",
  "threshold_value": 10000,
  "notification_channels": ["in_app", "email"]
}
```

**Alert Types:**
- `viral` - Content going viral
- `declining` - Engagement dropping
- `milestone` - Milestone reached
- `error` - Publishing error

**Metrics:**
- `views`, `engagement`, `clicks`, `shares`, `comments`, `likes`

**Operators:**
- `greater_than`, `less_than`, `equals`, `percentage_change`

---

### Competitors Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/competitors` | Add competitor |
| GET | `/competitors` | List competitors |
| GET | `/competitors/{id}` | Get competitor |
| DELETE | `/competitors/{id}` | Remove competitor |
| GET | `/competitors/{id}/content` | Get competitor content |
| GET | `/competitors/analysis` | Performance analysis |
| GET | `/competitors/gaps` | Content gaps |
| POST | `/competitors/gaps/analyze` | Analyze gaps |
| GET | `/competitors/topics/overlap` | Topic overlap |
| GET | `/competitors/benchmark` | Benchmark comparison |
| POST | `/competitors/{id}/refresh` | Refresh data |
| GET | `/competitors/platforms/list` | Supported platforms |

#### POST /competitors

Add a new competitor to track.

**Request Body:**
```json
{
  "name": "Competitor Inc",
  "platform": "twitter",
  "handle": "@competitor",
  "description": "Main competitor in our space",
  "profile_url": "https://twitter.com/competitor"
}
```

**Supported Platforms:**
- `twitter`, `linkedin`, `instagram`, `youtube`, `tiktok`, `facebook`, `blog`, `newsletter`

---

## Integrations

### Integrations Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/integrations` | List integrations |
| GET | `/integrations/{id}` | Get integration |
| POST | `/integrations` | Create integration |
| PUT | `/integrations/{id}` | Update integration |
| DELETE | `/integrations/{id}` | Delete integration |
| GET | `/integrations/types` | Available types |
| POST | `/integrations/{id}/test` | Test connection |
| GET | `/integrations/{id}/deliveries` | List deliveries |
| POST | `/integrations/{id}/deliveries/{delivery_id}/retry` | Retry delivery |
| POST | `/integrations/{id}/trigger` | Trigger event |
| POST | `/webhooks/incoming/{token}` | Incoming webhook |

**Supported Integration Types:**
- `zapier` - Zapier integration
- `webhook` - Generic webhook
- `wordpress` - WordPress site

---

## Utility

### Search Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/search` | Search content |
| GET | `/search/suggestions` | Search suggestions |

### Trash Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/trash` | List trashed items |
| GET | `/trash/stats` | Trash statistics |
| POST | `/trash/{id}/restore` | Restore item |
| DELETE | `/trash/{id}` | Permanently delete |
| POST | `/trash/empty` | Empty trash |

### Usage Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/usage` | Get usage statistics |
| GET | `/usage/history` | Usage history |

---

## Rate Limits & Error Codes

### Rate Limiting

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

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created successfully |
| 204 | No content (delete success) |
| 400 | Bad request - invalid input |
| 401 | Unauthorized - invalid/missing token |
| 403 | Forbidden - insufficient permissions |
| 404 | Resource not found |
| 409 | Conflict - duplicate or conflict |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

### Error Response Format

All API errors follow this format:

```json
{
  "detail": "Error message description"
}
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Invalid credentials` | Wrong email/password | Check credentials |
| `Missing or invalid authorization header` | No token provided | Include Bearer token |
| `Invalid token` | Token expired | Login again |
| `Rate limit exceeded` | Too many requests | Wait and retry |
| `Content not found` | Invalid content ID | Verify content ID |
| `Invalid source URL` | URL unreachable | Check URL format |

---

## OpenAPI Specification

Interactive API documentation is available at:

- **Swagger UI**: `/docs` (development)
- **ReDoc**: `/redoc` (development)

---

## Support

For API support or questions:

- **Documentation**: https://docs.contentforge.ai
- **Support Email**: support@contentforge.ai
- **Status Page**: https://status.contentforge.ai
