# ContentForge AI - Features Guide

> Complete guide to all platform features across 54 router modules and 427 API routes

---

## Platform Overview

| Metric | Value |
|--------|-------|
| API Routes | 375 (184 GET \| 124 POST \| 15 PUT \| 15 PATCH \| 37 DELETE) |
| Router Modules | 49 |
| Backend Services | 34 |
| Frontend Components | 73 |
| Pages | 16 |
| Backend Tests | 530 passing (163/164 deep system) |
| CI Pipelines | 4/4 green (self-hosted runner: srv1503460) |

---

## Table of Contents

### Core Features (P0-P1)
1. [Smart Content Editor](#smart-content-editor)
2. [Scheduled Publishing](#scheduled-publishing)
3. [RSS Import](#rss-import)
4. [Content Freshness](#content-freshness)
5. [Trending Topics](#trending-topics)
6. [Growth Analytics](#growth-analytics)
7. [Performance Alerts](#performance-alerts)
8. [Content Calendar](#content-calendar)
9. [Competitor Analysis](#competitor-analysis)
10. [Third-Party Integrations](#third-party-integrations)

### P4 Wave 1 Features
11. [Version History](#version-history)
12. [Audit Logs](#audit-logs)
13. [Quality Scoring](#quality-scoring)
14. [Sentiment Analysis](#sentiment-analysis)
15. [Custom Dashboards](#custom-dashboards)
16. [Reports](#reports)

### P4 Wave 2 Features
17. [Auto-Suggestions](#auto-suggestions)
18. [Smart Categorization](#smart-categorization)
19. [Performance Analytics](#performance-analytics)
20. [Data Retention](#data-retention)
21. [Comments v2](#comments-v2)

### P4 Wave 3 Features
22. [SSO (OIDC)](#sso-oidc)
23. [SAML SSO](#saml-sso)
24. [Plugin System](#plugin-system)
25. [SDK](#sdk)
26. [WebSocket & Real-Time](#websocket--real-time)
27. [Collaboration](#collaboration)
28. [Marketplace](#marketplace)

### P4 Wave 4 Features
29. [Funnel Tracking](#funnel-tracking)
30. [Attribution Modeling](#attribution-modeling)
31. [SLA Monitoring](#sla-monitoring)
32. [Integration Hub Framework](#integration-hub-framework)

### Infrastructure & Operations
33. [Health & Monitoring](#health--monitoring)
34. [Search](#search)
35. [Notifications](#notifications)
36. [Usage & Billing](#usage--billing)
37. [Organizations](#organizations)
38. [Trash & Recovery](#trash--recovery)
39. [Automation](#automation)
40. [Audience Intelligence](#audience-intelligence)

---

## Smart Content Editor

The Smart Content Editor is an AI-powered tool that helps you transform and optimize your content for different purposes and platforms.

**Router:** `ai_editor` | **Service:** `ai_service`, `extraction_service` | **Component:** `SmartEditor`

### Overview

The editor uses AIService (provider-agnostic) to rewrite, expand, condense, and optimize your content while maintaining your core message.

### Features

#### Rewrite
Transform your content with different tones and styles.

**Available Tones:**
| Tone | Description | Best For |
|------|-------------|----------|
| Casual | Relaxed, conversational | Social media, blogs |
| Professional | Business-appropriate | LinkedIn, corporate |
| Witty | Clever and humorous | Twitter, engaging posts |
| Formal | Academic and sophisticated | Whitepapers, reports |
| Friendly | Warm and approachable | Newsletters, community |
| Authoritative | Confident and expert | Thought leadership |
| Enthusiastic | Excited and energetic | Product launches |
| Empathetic | Understanding and compassionate | Support content |

**Available Styles:**
| Style | Description | Best For |
|-------|-------------|----------|
| Neutral | Balanced and objective | News, updates |
| Persuasive | Convincing and compelling | Sales, CTAs |
| Informative | Educational and factual | Tutorials, guides |
| Storytelling | Narrative-driven | Brand stories |
| Concise | Brief and to-the-point | Summaries, abstracts |
| Descriptive | Vivid and sensory | Product descriptions |

#### Expand / Condense / Optimize

- **Expand**: Target expansion (2x–5x), add examples, statistics
- **Condense**: Target percentage (20–80%), preserve key points, TL;DR
- **Optimize**: Platform-specific tailoring for Twitter/X, LinkedIn, Blog, Newsletter, Instagram, TikTok

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ai-editor/rewrite` | Rewrite content with tone/style |
| POST | `/api/v1/ai-editor/expand` | Expand content |
| POST | `/api/v1/ai-editor/condense` | Condense content |
| POST | `/api/v1/ai-editor/optimize` | Platform-specific optimization |
| GET | `/api/v1/ai-editor/tones` | List available tones |
| GET | `/api/v1/ai-editor/styles` | List available styles |

### Usage Notes

- Start with your best content — AI works best with solid source material
- Experiment with tone + style combinations
- Always optimize before publishing to specific platforms
- Review AI output and refine as needed

---

## Scheduled Publishing

Schedule your content to be published automatically at the optimal time.

**Router:** `scheduler` | **Service:** `scheduler_service` | **Components:** `ScheduleTab`, `ScheduleCalendar`, `ScheduleModal`, `UpcomingPostsWidget`

### Overview

The scheduler lets you queue content for future publication across multiple platforms, with smart timing recommendations and bulk scheduling.

### Features

- **Single Post Scheduling**: Exact date/time, timezone, platform config
- **Bulk Scheduling**: Multiple posts with intervals
- **Smart Scheduling**: AI-recommended best posting times based on platform, audience, and history
- **Publishing Queue**: Monitor, edit, cancel, retry, or publish immediately

### Queue Statuses

| Status | Description |
|--------|-------------|
| Pending | Waiting for scheduled time |
| Scheduled | Time set, ready to publish |
| Processing | Currently publishing |
| Published | Successfully published |
| Failed | Publish failed, can retry |
| Cancelled | Manually cancelled |

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/scheduler/schedule` | Schedule a post |
| POST | `/api/v1/scheduler/bulk` | Bulk schedule posts |
| GET | `/api/v1/scheduler/queue` | View publishing queue |
| GET | `/api/v1/scheduler/smart-times` | Get AI-recommended times |
| PATCH | `/api/v1/scheduler/{id}` | Update scheduled post |
| DELETE | `/api/v1/scheduler/{id}` | Cancel scheduled post |
| POST | `/api/v1/scheduler/{id}/retry` | Retry failed post |

---

## RSS Import

Automatically import content from RSS feeds and convert it into ContentForge projects.

**Router:** `rss` | **Service:** `rss_service` | **Components:** `RSSTab`, `RSSFeedManager`, `RSSEntriesPanel`

### Overview

Monitor RSS feeds from blogs, news sites, and publications. New entries are automatically fetched and can be imported as content items for repurposing.

### Features

- **Feed Management**: Add any RSS/Atom feed, set fetch frequency, enable auto-import
- **Auto-Import**: Automatically create content items from new entries
- **Manual Import**: Selectively import entries with preview
- **Entry Management**: Track processed/unprocessed entries

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/rss/feeds` | Add RSS feed |
| GET | `/api/v1/rss/feeds` | List feeds |
| GET | `/api/v1/rss/feeds/{id}/entries` | Get feed entries |
| POST | `/api/v1/rss/feeds/{id}/import` | Import entries |
| POST | `/api/v1/rss/feeds/{id}/refresh` | Refresh feed |
| DELETE | `/api/v1/rss/feeds/{id}` | Remove feed |

---

## Content Freshness

Monitor and score your content's freshness to identify what needs updating.

**Router:** `freshness` | **Service:** `freshness_service` | **Component:** `FreshnessDashboard`

### Overview

The Freshness system scores content (0–100) based on age, engagement, and relevance. Scores below 50 indicate content needing attention.

### Scoring Factors

| Factor | Points | Description |
|--------|--------|-------------|
| Age | 0–30 | Recently published → 6+ months old |
| Engagement | 0–35 | High → low engagement levels |
| Trend | 0–35 | Trending → declining topics |

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/freshness/content/{id}` | Analyze single content |
| POST | `/api/v1/freshness/bulk` | Bulk analysis |
| GET | `/api/v1/freshness/stale` | List stale content |
| GET | `/api/v1/freshness/dashboard` | Freshness overview |

---

## Trending Topics

Discover and leverage trending topics to create timely, relevant content.

**Router:** `trends` | **Service:** `trend_service` | **Component:** `TrendingTopics`

### Features

- **Trend Discovery**: Sources include Twitter/X, Google Trends, Reddit, news APIs
- **Category Organization**: Technology, Business, Entertainment, Sports, Politics, Health, Science, General
- **Relevance Matching**: AI matches trends to your content history
- **Trend Tracking**: Save topics, notifications, velocity changes
- **Content Generation**: Headline suggestions, draft content, angle options

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/trends` | List current trends |
| GET | `/api/v1/trends/categories` | Get trend categories |
| GET | `/api/v1/trends/relevant` | Get trends relevant to your content |
| POST | `/api/v1/trends/track` | Track a topic |
| GET | `/api/v1/trends/velocity` | Velocity leaderboard |

---

## Growth Analytics

Track your content performance and growth over time.

**Router:** `analytics` | **Component:** `AnalyticsTab`, `AnalyticsDashboard`

### Dashboard KPIs

- Total content, assets, distributions, published counts
- 30-day growth rates
- Success rate metrics
- Time-based trends (daily, weekly, monthly)

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/dashboard` | Dashboard KPIs |
| GET | `/api/v1/analytics/content` | Content analytics |
| GET | `/api/v1/analytics/assets` | Asset analytics |
| GET | `/api/v1/analytics/distributions` | Distribution analytics |
| GET | `/api/v1/analytics/usage` | Usage tracking |
| GET | `/api/v1/analytics/export` | Export data (CSV/JSON) |

---

## Performance Alerts

Get notified when your content achieves milestones or needs attention.

**Router:** `alerts` | **Service:** `alert_service` | **Component:** `AlertsCenter`

### Alert Types

| Type | Trigger | Action |
|------|---------|--------|
| Viral | Engagement exceeds threshold | Amplify, capitalize |
| Declining | Engagement drops below threshold | Refresh, adjust |
| Milestone | Follower/view achievements | Celebrate, analyze |
| Error | Publishing/API failures | Retry, debug |

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/alerts` | List alerts |
| POST | `/api/v1/alerts/rules` | Create alert rule |
| PATCH | `/api/v1/alerts/{id}` | Update alert |
| POST | `/api/v1/alerts/{id}/acknowledge` | Acknowledge alert |
| POST | `/api/v1/alerts/{id}/resolve` | Resolve alert |

---

## Content Calendar

Visualize and plan your content schedule.

**Components:** `ScheduleCalendar`, `TeamCalendar`

### Views

- **Monthly/Weekly/List views** with platform color coding
- Visual indicators: green (published), yellow (scheduled), red (failed), gray (draft)
- Filtering by platform, project, content type, status
- Export to PDF, ICS, CSV

---

## Competitor Analysis

Track and analyze your competitors' content strategies.

**Router:** `competitors` | **Service:** `competitor_service` | **Component:** `CompetitorAnalysis`

### Features

- **Competitor Tracking**: Add handles/profiles across 7+ platforms
- **Content Analysis**: Volume, engagement, timing, content mix, sentiment
- **Gap Analysis**: Identify topics competitors cover that you don't
- **Benchmark Comparison**: Percentile ranking against competitors

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/competitors` | Add competitor |
| GET | `/api/v1/competitors` | List competitors |
| GET | `/api/v1/competitors/{id}/analysis` | Content analysis |
| GET | `/api/v1/competitors/gaps` | Gap analysis |
| GET | `/api/v1/competitors/benchmark` | Benchmark comparison |

---

## Third-Party Integrations

Connect ContentForge with your favorite tools and platforms.

**Router:** `integrations` | **Service:** `integration_services` | **Component:** `IntegrationsPanel`

### Available Integrations

- **Zapier**: 5,000+ app connections with triggers and actions
- **Webhooks**: Generic incoming/outgoing webhook integration
- **WordPress**: Direct publish with categories, tags, media upload

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/integrations` | List integrations |
| POST | `/api/v1/integrations/webhooks` | Create webhook |
| POST | `/api/v1/integrations/webhooks/{id}/test` | Test webhook |
| GET | `/api/v1/webhooks/logs` | Webhook delivery logs |

---

## Version History

Track every change to your content with full version history and the ability to compare and restore previous versions.

**Router:** `version_history` | **Service:** `version_service` | **Component:** `VersionHistory`

### Description

Every content edit is automatically saved as a new version. Browse the full history, compare any two versions side by side with diff highlighting, and restore previous versions with a single click.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/version-history/content/{id}` | List versions for content |
| GET | `/api/v1/version-history/content/{id}/current` | Get current version |
| GET | `/api/v1/version-history/compare` | Compare two versions (diff) |
| POST | `/api/v1/version-history/content/{id}/restore` | Restore a previous version |
| GET | `/api/v1/version-history/content/{id}/count` | Version count |

### Usage Notes

- Versions are created automatically on every content save
- Use the compare endpoint to see what changed between versions
- Restoring a version creates a new version (non-destructive)
- Version history is scoped per content item

---

## Audit Logs

Comprehensive audit trail of all platform actions for compliance and security review.

**Router:** `audit_logs` | **Service:** `audit_service` | **Component:** `AuditLogs`

### Description

Track all significant actions on the platform — logins, content changes, permission modifications, data exports, and admin actions. Filter by user, action type, date range, and resource. Essential for compliance (SOC 2, GDPR) and security incident investigation.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/audit-logs` | List audit log entries |
| GET | `/api/v1/audit-logs/filters` | Get available filter options |
| GET | `/api/v1/audit-logs/export` | Export audit logs (CSV/JSON) |
| GET | `/api/v1/audit-logs/summary` | Action summary statistics |

### Usage Notes

- Audit logs are immutable — they cannot be edited or deleted
- Admin-only access by default; configure role permissions as needed
- Use the export endpoint for compliance reporting
- Retention follows data retention policy settings

---

## Quality Scoring

AI-powered content quality assessment with actionable improvement suggestions.

**Router:** `quality_scoring` | **Service:** `quality_service` | **Component:** `QualityDashboard`

### Description

Automatically evaluate content quality across multiple dimensions: readability, structure, SEO optimization, tone consistency, and engagement potential. Receive a composite score (0–100) with specific improvement suggestions for each dimension.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/quality/content/{id}/score` | Score a content item |
| GET | `/api/v1/quality/content/{id}` | Get existing score |
| POST | `/api/v1/quality/bulk` | Bulk score content |
| GET | `/api/v1/quality/dashboard` | Quality overview dashboard |
| GET | `/api/v1/quality/dimensions` | List quality dimensions |

### Usage Notes

- Scores are cached; re-score after content edits
- Use bulk scoring to assess content library health
- The dashboard shows quality distribution and trends
- Dimension scores help prioritize specific improvements

---

## Sentiment Analysis

Analyze the emotional tone and sentiment of content and audience responses.

**Router:** `sentiment` | **Service:** `sentiment_service` | **Component:** `SentimentDashboard`

### Description

AI-driven sentiment analysis classifies content and feedback as positive, negative, or neutral. Track sentiment trends over time, compare sentiment across content types, and identify sentiment shifts that may require action.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/sentiment/analyze` | Analyze text sentiment |
| GET | `/api/v1/sentiment/content/{id}` | Get content sentiment |
| GET | `/api/v1/sentiment/trends` | Sentiment trends over time |
| POST | `/api/v1/sentiment/bulk` | Bulk sentiment analysis |
| GET | `/api/v1/sentiment/dashboard` | Sentiment overview |

### Usage Notes

- Supports single text analysis and bulk processing
- Trend analysis requires sufficient data volume
- Use alongside quality scoring for comprehensive content assessment
- Dashboard aggregates sentiment across all content

---

## Custom Dashboards

Create personalized dashboards with configurable widgets and layouts.

**Router:** `dashboards` | **Service:** `dashboard_service` | **Component:** `CustomDashboards`

### Description

Build custom dashboards by selecting and arranging widgets — analytics charts, KPI cards, content lists, sentiment gauges, quality scores, and more. Save multiple dashboards for different use cases (executive overview, content health, team performance).

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/dashboards` | Create dashboard |
| GET | `/api/v1/dashboards` | List dashboards |
| GET | `/api/v1/dashboards/{id}` | Get dashboard with widgets |
| PATCH | `/api/v1/dashboards/{id}` | Update dashboard layout/config |
| DELETE | `/api/v1/dashboards/{id}` | Delete dashboard |
| POST | `/api/v1/dashboards/{id}/widgets` | Add widget |
| PATCH | `/api/v1/dashboards/{id}/widgets/{wid}` | Update widget |

### Usage Notes

- Each user can create multiple dashboards
- Widgets pull data from various platform services
- Layout changes are saved automatically
- Share dashboards with team members (org-level)

---

## Reports

Generate and schedule comprehensive content performance reports.

**Router:** `reports` | **Service:** `report_service` | **Components:** `TemplateGallery`

### Description

Generate PDF and CSV reports covering content performance, quality scores, sentiment trends, distribution metrics, and competitor comparisons. Schedule recurring reports (daily, weekly, monthly) for automated delivery via email.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/reports/generate` | Generate a report |
| GET | `/api/v1/reports` | List generated reports |
| GET | `/api/v1/reports/{id}/download` | Download report file |
| POST | `/api/v1/reports/schedule` | Schedule recurring report |
| GET | `/api/v1/reports/templates` | List report templates |
| DELETE | `/api/v1/reports/{id}` | Delete report |

---

## Auto-Suggestions

AI-powered content suggestions based on trends, audience behavior, and content gaps.

**Router:** `ai_suggestions`, `suggestions` | **Service:** `suggestion_service` | **Component:** `SuggestionPanel`

### Description

Receive intelligent content suggestions including topic ideas, optimal posting times, platform recommendations, content angle variations, and hashtag suggestions. Suggestions are generated based on your content history, trending topics, and performance data.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/suggestions` | Get current suggestions |
| GET | `/api/v1/suggestions/topics` | Topic suggestions |
| GET | `/api/v1/suggestions/timing` | Optimal timing suggestions |
| POST | `/api/v1/suggestions/{id}/dismiss` | Dismiss a suggestion |
| POST | `/api/v1/suggestions/{id}/apply` | Apply a suggestion |
| POST | `/api/v1/ai-suggestions/generate` | Generate new suggestions |

### Usage Notes

- Suggestions refresh based on content activity and trend changes
- Apply suggestions directly to create content drafts
- Dismissed suggestions influence future recommendation quality
- AI suggestions combine trend data with your performance history

---

## Smart Categorization

Automatically categorize content using AI with manual override capabilities.

**Router:** `categorization` | **Service:** `categorization_service` | **Component:** `CategorizationPanel`

### Description

AI automatically assigns categories and tags to content based on topic analysis. Review AI-assigned categories, accept or override them, and create custom category hierarchies. Improves content organization and discoverability.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/categorization/content/{id}/auto` | Auto-categorize content |
| GET | `/api/v1/categorization/content/{id}` | Get content categories |
| PATCH | `/api/v1/categorization/content/{id}` | Override categories |
| GET | `/api/v1/categorization/categories` | List all categories |
| POST | `/api/v1/categorization/categories` | Create custom category |
| POST | `/api/v1/categorization/bulk` | Bulk categorize |

### Usage Notes

- Auto-categorization runs on content creation and major edits
- Override categories persist even after content re-editing
- Custom categories support hierarchical organization
- Bulk categorization is useful for existing content libraries

---

## Performance Analytics

Deep performance analytics for content, distribution, and platform metrics.

**Router:** `performance` | **Service:** `performance_service` | **Component:** `PerformanceAnalytics`

### Description

Advanced analytics beyond basic growth metrics: content velocity, engagement rate trends, platform-specific performance breakdowns, content lifecycle analysis, and attribution of performance changes to specific actions. Includes caching for high-traffic endpoints.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/performance/overview` | Performance overview |
| GET | `/api/v1/performance/content` | Content performance detail |
| GET | `/api/v1/performance/platforms` | Platform breakdown |
| GET | `/api/v1/performance/lifecycle` | Content lifecycle analysis |
| GET | `/api/v1/performance/trends` | Performance trend analysis |

### Usage Notes

- Performance endpoints are cached (Redis + in-memory) for fast access
- Lifecycle analysis shows content performance over time from creation
- Platform breakdown helps optimize cross-platform strategy
- X-Response-Time header included on all responses for monitoring

---

## Data Retention

Configure and enforce data retention policies across the platform.

**Router:** `retention` | **Service:** `retention_service` | **Component:** `DataRetentionManager`

### Description

Define retention policies per data type — content, audit logs, analytics, webhooks, etc. Set automatic expiration and cleanup schedules. Ensures compliance with GDPR data minimization and internal data governance requirements.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/retention/policies` | List retention policies |
| POST | `/api/v1/retention/policies` | Create retention policy |
| PATCH | `/api/v1/retention/policies/{id}` | Update policy |
| DELETE | `/api/v1/retention/policies/{id}` | Delete policy |
| POST | `/api/v1/retention/apply` | Manually apply retention |
| GET | `/api/v1/retention/status` | Retention enforcement status |

### Usage Notes

- Default policies are pre-configured for common data types
- Admin-only configuration
- Apply retention manually or schedule via cron
- Deleted data follows the trash system before permanent removal

---

## Comments v2

Enhanced commenting system with threading, reactions, and real-time updates.

**Router:** `comments` | **Service:** `comments_service` | **Component:** `CommentsPanel`

### Description

Upgraded commenting system supporting threaded replies, emoji reactions, @mentions, real-time updates via WebSocket, and resolution tracking. Designed for collaborative content review workflows.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/comments/content/{id}` | List comments for content |
| POST | `/api/v1/comments/content/{id}` | Add comment |
| PATCH | `/api/v1/comments/{id}` | Edit comment |
| DELETE | `/api/v1/comments/{id}` | Delete comment |
| POST | `/api/v1/comments/{id}/react` | Add reaction |
| POST | `/api/v1/comments/{id}/resolve` | Resolve comment thread |

### Usage Notes

- Comments support nested threading (reply to reply)
- Real-time updates require WebSocket connection
- @mentions trigger notifications to mentioned users
- Resolved threads are collapsed by default

---

## SSO (OIDC)

OpenID Connect single sign-on integration for enterprise authentication.

**Router:** `sso` | **Service:** `sso_service` | **Component:** `SAMLLogin` (handles both SAML and OIDC UI), `CookieConsent`

### Description

Enable SSO via OpenID Connect protocol. Connect to identity providers like Okta, Auth0, Azure AD, Google Workspace, and Keycloak. Supports automatic user provisioning, group mapping, and session management.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/sso/configure` | Configure OIDC provider |
| GET | `/api/v1/sso/providers` | List configured providers |
| GET | `/api/v1/sso/{provider}/login` | Initiate OIDC login |
| GET | `/api/v1/sso/{provider}/callback` | OIDC callback |
| DELETE | `/api/v1/sso/providers/{id}` | Remove provider |
| GET | `/api/v1/sso/test/{provider}` | Test SSO connection |

### Usage Notes

- Configure via admin panel or API
- Supports multiple concurrent OIDC providers
- User provisioning is automatic on first login
- Group/role mapping configurable per provider

---

## SAML SSO

SAML 2.0 single sign-on for enterprise identity providers.

**Router:** `saml` | **Service:** `saml_service` | **Component:** `SAMLLogin`

### Description

Full SAML 2.0 SSO support for enterprise identity providers. Supports SP-initiated and IdP-initiated flows. Compatible with Okta, Azure AD, OneLogin, and other SAML providers.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/saml/configure` | Configure SAML provider |
| GET | `/api/v1/saml/metadata` | SP metadata XML |
| POST | `/api/v1/saml/acs` | Assertion Consumer Service |
| GET | `/api/v1/saml/slo` | Single Logout |
| GET | `/api/v1/saml/providers` | List SAML providers |
| DELETE | `/api/v1/saml/providers/{id}` | Remove provider |

### Usage Notes

- Download SP metadata from `/api/v1/saml/metadata` for IdP configuration
- Both SP-initiated and IdP-initiated login flows supported
- Configure attribute mapping for user provisioning
- SAML and OIDC can coexist for different user populations

---

## Plugin System

Extensible plugin architecture for platform customization.

**Router:** `plugins` | **Service:** `plugin_service` | **Component:** `PluginManager`

### Description

Install, configure, and manage plugins that extend ContentForge functionality. Plugins can add custom routes, modify content pipelines, integrate external services, and provide custom UI components. Supports a managed plugin lifecycle with install, enable, disable, and uninstall operations.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/plugins` | List installed plugins |
| POST | `/api/v1/plugins/install` | Install a plugin |
| PATCH | `/api/v1/plugins/{id}/enable` | Enable plugin |
| PATCH | `/api/v1/plugins/{id}/disable` | Disable plugin |
| DELETE | `/api/v1/plugins/{id}` | Uninstall plugin |
| GET | `/api/v1/plugins/{id}/config` | Get plugin configuration |
| PATCH | `/api/v1/plugins/{id}/config` | Update plugin config |

### Usage Notes

- Plugins are installed from the marketplace or via upload
- Disabled plugins retain configuration but don't execute
- Plugin permissions are scoped to declared capabilities
- Admin approval required for plugin installation (configurable)

---

## SDK

Developer SDK for building ContentForge integrations and extensions.

**Router:** N/A (client library) | **Component:** N/A (developer tooling)

### Description

The ContentForge SDK provides a typed client library (Python and TypeScript) for programmatic access to all platform APIs. Includes authentication helpers, rate limit handling, retry logic, and type-safe request/response models.

### Key Endpoints

SDK wraps all 427 API routes with type-safe clients.

### Usage Notes

- Python SDK: `pip install contentforge-sdk`
- TypeScript SDK: `npm install @contentforge/sdk`
- SDK documentation available at `docs.contentforge.ai/sdk`
- Auto-generated from OpenAPI spec for accuracy

---

## WebSocket & Real-Time

Real-time event streaming via WebSocket connections.

**Router:** `ws` | **Service:** `websocket_manager` | **Component:** Various (real-time updates)

### Description

WebSocket connections enable real-time updates for collaboration, comments, notifications, and presence. The connection manager handles room-based subscriptions, authentication, and reconnection logic.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `ws://.../ws` | WebSocket connection endpoint |
| POST | `/api/v1/ws/subscribe` | Subscribe to event channels |
| POST | `/api/v1/ws/unsubscribe` | Unsubscribe from channels |

### Usage Notes

- WebSocket connections require authentication token
- Events are scoped to channels (content, comments, presence, notifications)
- Automatic reconnection with exponential backoff
- Heartbeat/ping-pong for connection health monitoring

---

## Collaboration

Real-time collaborative editing and presence tracking for team content creation.

**Router:** `collaboration` | **Service:** `collaboration_service` | **Component:** Various

### Description

Enable multiple team members to edit content simultaneously with conflict-free resolution. Shows real-time user presence (who's viewing/editing), cursor positions, and editing locks. Integrates with Comments v2 and WebSocket for live updates.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/collaboration/content/{id}/presence` | Get active users on content |
| POST | `/api/v1/collaboration/content/{id}/join` | Join collaborative session |
| POST | `/api/v1/collaboration/content/{id}/leave` | Leave session |
| POST | `/api/v1/collaboration/content/{id}/lock` | Acquire edit lock |
| DELETE | `/api/v1/collaboration/content/{id}/lock` | Release edit lock |

### Usage Notes

- Requires WebSocket connection for real-time sync
- Edit locks prevent conflicting simultaneous edits
- Presence shows active viewers and editors
- Integrates with version history for change tracking

---

## Marketplace

Template and plugin marketplace for community-driven extensions.

**Router:** `marketplace` | **Service:** `marketplace_service` | **Components:** `TemplateMarketplace`, `TemplateGallery`

### Description

Browse and install community templates, plugins, and integrations from the ContentForge marketplace. Content creators can publish their own templates and plugins. Includes ratings, reviews, and usage statistics.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/marketplace` | Browse marketplace |
| GET | `/api/v1/marketplace/search` | Search marketplace |
| POST | `/api/v1/marketplace/install/{id}` | Install marketplace item |
| POST | `/api/v1/marketplace/publish` | Publish to marketplace |
| GET | `/api/v1/marketplace/{id}/reviews` | Get reviews |
| POST | `/api/v1/marketplace/{id}/reviews` | Add review |

### Usage Notes

- Marketplace items install as plugins or templates
- Publishing requires review approval (configurable)
- Ratings help surface quality content
- Admin can feature and curate marketplace items

---

## Funnel Tracking

Track content conversion funnels from creation to publication and engagement.

**Router:** `funnel` | **Service:** `funnel_service` | **Component:** `FunnelAnalytics`

### Description

Define and track conversion funnels across the content lifecycle: creation → editing → review → scheduling → publication → engagement. Identify bottleneck stages, measure conversion rates between steps, and optimize your content pipeline.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/funnel/define` | Define a funnel |
| GET | `/api/v1/funnel` | List funnels |
| GET | `/api/v1/funnel/{id}/analysis` | Funnel analysis |
| GET | `/api/v1/funnel/{id}/conversion` | Conversion rates |
| GET | `/api/v1/funnel/{id}/dropoff` | Drop-off analysis |
| PATCH | `/api/v1/funnel/{id}` | Update funnel definition |

### Usage Notes

- Funnel analysis requires sufficient event volume for statistical significance
- Drop-off analysis identifies stages losing the most content
- Use alongside performance analytics for full pipeline visibility
- Funnels can be shared across team members

---

## Attribution Modeling

Attribute content performance to specific actions, channels, and campaigns.

**Router:** `attribution` | **Service:** `attribution_service` | **Component:** `AttributionDashboard`

### Description

Multi-touch attribution modeling to understand which actions, channels, and campaigns contribute to content success. Supports first-touch, last-touch, linear, and time-decay models. Compare attribution across content types and platforms.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/attribution/model` | Configure attribution model |
| GET | `/api/v1/attribution/analysis` | Get attribution analysis |
| GET | `/api/v1/attribution/channels` | Channel attribution breakdown |
| GET | `/api/v1/attribution/comparison` | Compare attribution models |
| GET | `/api/v1/attribution/dashboard` | Attribution dashboard |

### Usage Notes

- Multiple models can run simultaneously for comparison
- Attribution data accumulates over time — longer windows yield better insights
- Channel attribution helps optimize distribution strategy
- Dashboard shows top-performing attribution paths

---

## SLA Monitoring

Monitor and enforce service level agreements with automated tracking and alerting.

**Router:** `sla` | **Service:** `sla_service` | **Component:** `SLAMonitoring`

### Description

Define SLA targets for response times, uptime, processing delays, and error rates. Automated monitoring tracks compliance, generates breach alerts, and provides historical SLA reports. Essential for enterprise customers with contractual SLA requirements.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/sla/define` | Define SLA target |
| GET | `/api/v1/sla` | List SLA definitions |
| GET | `/api/v1/sla/compliance` | Current compliance status |
| GET | `/api/v1/sla/breaches` | Recent SLA breaches |
| GET | `/api/v1/sla/report` | SLA compliance report |
| PATCH | `/api/v1/sla/{id}` | Update SLA definition |

### Usage Notes

- SLA monitoring runs continuously in the background
- Breach alerts integrate with the existing alerts system
- Reports can be scheduled for automated delivery
- Historical data available for compliance evidence

---

## Integration Hub Framework

Unified framework for building and managing third-party integrations.

**Router:** `integration_framework` | **Service:** `integration_framework_service` | **Component:** `IntegrationHub`

### Description

The Integration Hub Framework provides a standardized way to build, deploy, and manage integrations. Includes connection management, credential storage, health monitoring, and rate limit handling. Pre-built connectors available for common services; custom connectors via the SDK.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/integrations-hub/connectors` | List available connectors |
| POST | `/api/v1/integrations-hub/connect` | Create integration connection |
| GET | `/api/v1/integrations-hub/connections` | List active connections |
| PATCH | `/api/v1/integrations-hub/connections/{id}` | Update connection |
| DELETE | `/api/v1/integrations-hub/connections/{id}` | Remove connection |
| POST | `/api/v1/integrations-hub/connections/{id}/test` | Test connection |
| GET | `/api/v1/integrations-hub/connections/{id}/health` | Connection health |

### Usage Notes

- Pre-built connectors: Slack, Zapier, WordPress, Google Analytics, HubSpot, and more
- Custom connectors built via the SDK follow the same framework
- Connection health is monitored automatically
- Credential storage is encrypted and scoped per integration

---

## Health & Monitoring

System health checks and operational monitoring.

**Router:** `health`

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Basic health check |
| GET | `/api/v1/health/detailed` | Detailed component health |

---

## Search

Full-text search across content, projects, and assets.

**Router:** `search` | **Component:** `SearchModal`

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/search` | Global search |
| GET | `/api/v1/search/suggestions` | Search suggestions |

---

## Notifications

In-app and email notification management.

**Router:** `notifications`

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/notifications` | List notifications |
| PATCH | `/api/v1/notifications/{id}/read` | Mark as read |
| POST | `/api/v1/notifications/read-all` | Mark all as read |

---

## Usage & Billing

Usage tracking, subscription management, and billing via Stripe.

**Routers:** `usage`, `stripe` | **Components:** `UsageCounter`, `UpgradeModal`, `SubscriptionModal`

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/usage` | Current usage stats |
| POST | `/api/v1/stripe/checkout` | Create checkout session |
| POST | `/api/v1/stripe/webhook` | Stripe webhook handler |
| GET | `/api/v1/stripe/subscription` | Subscription status |

---

## Organizations

Multi-tenant organization and team management.

**Router:** `organizations` | **Component:** `TeamTab`

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/organizations` | Create organization |
| GET | `/api/v1/organizations/{id}` | Get organization |
| PATCH | `/api/v1/organizations/{id}` | Update organization |
| POST | `/api/v1/organizations/{id}/members` | Add member |
| DELETE | `/api/v1/organizations/{id}/members/{uid}` | Remove member |

---

## Trash & Recovery

Soft-delete with trash bin and recovery capabilities.

**Router:** `trash` | **Component:** `TrashTab`

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/trash` | List trashed items |
| POST | `/api/v1/trash/{id}/restore` | Restore item |
| DELETE | `/api/v1/trash/{id}` | Permanently delete |

---

## Automation

Automated content workflows and triggers.

**Router:** `automation`

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/automation/rules` | List automation rules |
| POST | `/api/v1/automation/rules` | Create rule |
| PATCH | `/api/v1/automation/rules/{id}` | Update rule |
| DELETE | `/api/v1/automation/rules/{id}` | Delete rule |
| POST | `/api/v1/automation/rules/{id}/test` | Test rule |

---

## Audience Intelligence

Audience segmentation and behavior analysis.

**Router:** `audience` | **Service:** `audience_service`

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/audience/segments` | List audience segments |
| GET | `/api/v1/audience/behavior` | Audience behavior analysis |
| GET | `/api/v1/audience/growth` | Growth metrics |
| POST | `/api/v1/audience/predictions` | Engagement predictions |

---

## Presence

Real-time user presence tracking for collaboration features.

**Router:** `presence` | **Service:** `presence_service`

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/presence/online` | List online users |
| POST | `/api/v1/presence/heartbeat` | Presence heartbeat |
| GET | `/api/v1/presence/content/{id}` | Users viewing content |

---

## Additional Routers

| Router | Description |
|--------|-------------|
| `auth` | Authentication (login, register, token refresh) |
| `content` | Content CRUD, import, export |
| `distributions` | Distribution channel management |
| `docs` | API documentation endpoints |
| `projects` | Project CRUD and organization |
| `user` | User profile and preferences |

---

## Quick Reference

### Feature Comparison by Plan

| Feature | Free | Pro | Enterprise |
|---------|------|-----|------------|
| Smart Editor | ✅ | ✅ | ✅ |
| Scheduled Publishing | 5/month | Unlimited | Unlimited |
| RSS Feeds | 1 | 10 | Unlimited |
| Freshness Scoring | ✅ | ✅ | ✅ |
| Trend Discovery | Basic | Full | Full + API |
| Analytics | Basic | Advanced | Custom |
| Alerts | In-app | All channels | All + Custom |
| Competitors | 2 | 10 | Unlimited |
| Integrations | Webhooks | Zapier + | All + Custom |
| Version History | 10 versions | Unlimited | Unlimited |
| Audit Logs | — | ✅ | ✅ + Export |
| Quality Scoring | ✅ | ✅ | ✅ + Custom dims |
| Sentiment | Basic | Full | Full + Bulk |
| Custom Dashboards | 1 | 5 | Unlimited |
| Reports | — | ✅ | ✅ + Scheduled |
| Auto-Suggestions | Basic | Full | Full + Custom |
| Smart Categorization | ✅ | ✅ | ✅ + Custom |
| Data Retention | Default | Configurable | Custom policies |
| Comments v2 | ✅ | ✅ | ✅ + Moderation |
| SSO/SAML | — | — | ✅ |
| Plugin System | — | ✅ | ✅ + Custom |
| Marketplace | Browse | Install | Install + Publish |
| Funnel Tracking | — | ✅ | ✅ |
| Attribution | — | ✅ | ✅ + Multi-model |
| SLA Monitoring | — | — | ✅ |
| Integration Hub | Basic | Standard | Full + Custom connectors |

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + N` | New content |
| `Cmd/Ctrl + S` | Save |
| `Cmd/Ctrl + E` | Open editor |
| `Cmd/Ctrl + /` | Search |
| `Esc` | Close modal |

### Support Resources

- **Help Center**: https://help.contentforge.ai
- **API Docs**: https://docs.contentforge.ai/api
- **SDK Docs**: https://docs.contentforge.ai/sdk
- **Community**: https://community.contentforge.ai
- **Email**: support@contentforge.ai

---

*Last Updated: 2026-04-14*  
*Routes: 375 | Routers: 49 | Services: 34 | Components: 73 | Pages: 16*