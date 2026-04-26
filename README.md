# ContentForge AI

> AI-Powered Content Repurposing & Distribution Platform

[![CI: Backend Tests](https://img.shields.io/badge/Backend_Tests-32%20passing-brightgreen)](https://github.com/jdev-bot/contentforge-ai)
[![CI: Frontend Build](https://img.shields.io/badge/Frontend_Build-passing-brightgreen)](https://github.com/jdev-bot/contentforge-ai)
[![CI: Security](https://img.shields.io/badge/Security_Pipeline-clean-brightgreen)](https://github.com/jdev-bot/contentforge-ai)
[![CI: CI/CD](https://img.shields.io/badge/CI%2FCD-green-brightgreen)](https://github.com/jdev-bot/contentforge-ai)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js_14-000000.svg?logo=next.js)](https://nextjs.org/)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E.svg?logo=supabase)](https://supabase.com/)
[![Routes](https://img.shields.io/badge/API_routes-427-blue)](docs/API_COMPLETE.md)
[![Security](https://img.shields.io/badge/security-0%20open%20findings-brightgreen)](docs/SECURITY_AUDIT_REPORT.md)
[![BYOK](https://img.shields.io/badge/AI_Mode-BYOK-orange)](docs/)

**Transform one piece of long-form content into 20+ platform-native formats automatically using AI, then distribute across social platforms, email, and blogs with zero manual intervention.**

[🚀 Quick Start](#quick-start) • [📚 Documentation](#documentation) • [✨ Features](#features) • [🏗️ Architecture](#architecture) • [📖 API Reference](docs/API_COMPLETE.md)

---

## 🌟 What is ContentForge AI?

ContentForge AI is a comprehensive content repurposing platform that helps content creators, marketers, and businesses:

- **📥 Import** content from URLs, YouTube videos, RSS feeds, or direct text
- **🤖 Generate** AI-powered content variations for every platform
- **✏️ Edit** content with smart AI tools (rewrite, expand, condense, optimize)
- **📅 Schedule** posts for optimal times across all platforms
- **📊 Analyze** performance and track growth metrics
- **🎯 Monitor** competitors and trending topics
- **🔔 Get alerts** for important content performance events

### Use Cases

| Role | How ContentForge Helps |
|------|------------------------|
| **Content Creator** | Turn blog posts into weeks of social content |
| **Marketing Team** | Maintain consistent brand voice across platforms |
| **Agency** | Scale client content production efficiently |
| **Solopreneur** | Maximize content ROI with automation |
| **Enterprise** | Centralize content operations and analytics |

---

## 🚀 Quick Start

### 1. Sign Up

```bash
# Visit the web app
open https://app.contentforge.ai

# Create your free account
# No credit card required
```

### 2. Create Your First Project

1. Click **"New Project"**
2. Name your project (e.g., "Q2 Marketing Campaign")
3. Set brand voice preferences
4. Choose target platforms

### 3. Import Content

```bash
# Option 1: From URL
curl -X POST "https://api.contentforge.ai/api/v1/content" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Blog Post",
    "source": {"type": "url", "url": "https://example.com/article"},
    "project_id": "your-project-id"
  }'

# Option 2: YouTube Video
# Option 3: Direct Text
```

### 4. Generate Assets

Your content is automatically processed to create:
- 🐦 Twitter/X threads
- 💼 LinkedIn posts
- 📧 Newsletters
- 🎥 Video scripts
- 📱 Instagram captions

### 5. Schedule & Publish

1. Review generated assets
2. Schedule for optimal times
3. Connect social accounts (or copy/paste)
4. Track performance in analytics

**That's it!** Your content is now working across all platforms.

---

## ✨ Features

### Core Platform (P0–P1)

| Feature | Description |
|---------|-------------|
| **📥 Content Import** | URLs, YouTube videos, RSS feeds, direct text, file uploads |
| **🤖 AI Generation** | AIService (provider-agnostic) powered content repurposing |
| **✏️ Smart Editor** | Rewrite, expand, condense, optimize for any platform |
| **📅 Scheduled Publishing** | Queue posts for optimal times with timezone support |
| **📊 Analytics Dashboard** | Track performance, growth, and engagement metrics |
| **🔍 Search** | Full-text search across all your content |
| **🗑️ Trash/Restore** | Soft delete with recovery options |

### AI Content Editor

Transform your content with AI:

| Tool | Capabilities |
|------|--------------|
| **Rewrite** | 8 tones × 6 styles = 48 combinations |
| **Expand** | 2x-5x length expansion with focus areas |
| **Condense** | 20%-80% reduction while preserving key points |
| **Optimize** | Platform-specific formatting (Twitter, LinkedIn, etc.) |

### Automation & Scheduling (P2)

| Feature | Description |
|---------|-------------|
| **⏰ Smart Scheduling** | AI-recommended best posting times |
| **📦 Bulk Scheduling** | Schedule multiple posts at once |
| **🔁 Recurring Posts** | Set up repeating content schedules |
| **📡 RSS Auto-Import** | Monitor feeds and auto-create content |
| **⚙️ Automation Rules** | Trigger actions based on events |
| **🔗 Webhooks** | Incoming and outgoing webhook support |

### Analytics & Insights (P2–P3)

| Feature | Description |
|---------|-------------|
| **📈 Dashboard KPIs** | Content, asset, and distribution metrics |
| **📊 Usage Tracking** | Monitor your monthly limits |
| **📉 Content Analytics** | Performance by content type |
| **📤 Distribution Stats** | Success rates by platform |
| **📥 Data Export** | CSV and JSON export for reporting |
| **🎯 Custom Reports** | Build custom analytics views (Pro+) |

### Advanced Features (P3)

| Feature | Description |
|---------|-------------|
| **🌡️ Content Freshness** | Score and track content freshness |
| **🔥 Trending Topics** | Discover and leverage trending content |
| **👥 Audience Insights** | Understand your audience growth |
| **🚨 Performance Alerts** | Get notified of viral moments and issues |
| **📆 Content Calendar** | Visual calendar for content planning |
| **🏆 Competitor Analysis** | Track competitors and identify gaps |
| **🧪 A/B Testing** | Content variation testing framework |
| **📝 Content Templates** | Blog, social, newsletter templates |
| **📦 Bulk Operations** | CSV/JSON import and batch operations |

### P4 Advanced Features

#### Wave 1 — Content Intelligence

| Feature | Description |
|---------|-------------|
| **📋 Version History** | Track content versions with full diff support |
| **📝 Audit Logs** | Comprehensive action logging with CSV/JSON export |
| **⭐ Quality Scoring** | AI-powered content quality assessment |
| **💭 Sentiment Analysis** | Real-time sentiment tracking and analysis |
| **📈 Custom Dashboards** | User-configurable analytics dashboards |
| **📊 Reports** | Custom report generation with scheduling |

#### Wave 2 — Smart Operations

| Feature | Description |
|---------|-------------|
| **🎯 Auto-Suggestions** | Smart content improvement recommendations |
| **🏷️ Smart Categorization** | AI-driven content clustering and tagging |
| **📊 Performance Analytics** | Deep content performance insights |
| **🗄️ Data Retention** | Configurable retention policies per content type |
| **💬 Comments v2** | Threaded comments with resolution tracking |

#### Wave 3 — Platform & Extensibility

| Feature | Description |
|---------|-------------|
| **🔐 SSO (OIDC)** | Google, Microsoft, Okta SSO support |
| **🔑 SAML SSO** | Enterprise SAML 2.0 authentication |
| **🔌 Plugin System** | Extensible plugin architecture with lifecycle hooks |
| **📡 Developer SDK** | Python SDK for programmatic API access |
| **🔄 WebSocket** | Real-time collaboration with presence tracking |
| **🤝 Collaboration** | Multi-user real-time editing |
| **🏪 Marketplace** | Plugin and template marketplace |

#### Wave 4 — Business Intelligence

| Feature | Description |
|---------|-------------|
| **📊 Funnel Tracking** | Content conversion funnel analytics |
| **🎯 Attribution Modeling** | Channel attribution and ROI tracking |
| **⏱️ SLA Monitoring** | Service level agreement tracking with alerting |
| **🔗 Integration Hub** | Unified integration management framework |

### Integrations

| Integration | Capabilities |
|-------------|--------------|
| **Zapier** | Connect with 5,000+ apps |
| **Webhooks** | Custom incoming/outgoing webhooks |
| **WordPress** | Direct publishing to WordPress sites |
| **Social Platforms** | Twitter/X, LinkedIn, Instagram, Facebook, TikTok |
| **Email** | Newsletter distribution via Resend |

### Team Features (Pro+)

| Feature | Description |
|---------|-------------|
| **👥 Organizations** | Multi-user workspace management |
| **🔐 Role-Based Access** | Owner, Admin, Editor, Writer, Viewer roles |
| **💬 Comments** | Collaborate with inline comments |
| **✅ Approvals** | Review workflows before publishing |
| **📋 Shared Templates** | Team-wide content templates |

---

## ⚡ Performance

All performance optimizations applied and verified in production:

| Optimization | Impact |
|-------------|--------|
| **Redis/in-memory caching** | 9 high-traffic read endpoints cached |
| **Parallel DB queries** | `asyncio.gather` for concurrent data fetching |
| **N+1 query elimination** | Fixed in 5 endpoints |
| **ETag middleware** | HTTP 304 Not Modified support |
| **X-Response-Time header** | Request duration visibility |
| **X-Request-ID header** | Request tracing across services |
| **Slow request logging** | >2s threshold with structured logging |
| **@lru_cache on Supabase** | Admin client instance reuse |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend                                  │
│                Next.js 14 + Tailwind CSS                         │
│                   59 components · 16 pages                      │
│                        Vercel                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API                                      │
│            FastAPI + Python 3.13                                 │
│       427 routes · 49 routers · 34 services                     │
│     Rate Limiting · JWT Auth · ETag · Request ID                │
│                        Render                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐   ┌──────────┐    ┌──────────────┐
│   Supabase   │   │  Celery  │    │ Cloudflare   │
│  PostgreSQL  │   │ Workers  │    │     R2       │
│     Auth     │   │  Redis   │    │   Storage    │
└──────────────┘   └──────────┘    └──────────────┘
        │                                │
        ▼                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     External Services                            │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  │
│  │  Groq  │  │Resend  │  │ Stripe │  │  n8n   │  │ Social │  │
│  │GLM-5.1│  │ Email  │  │Payments│  │Workflow│  │  APIs  │  │
│  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 14, React 18, Tailwind CSS, TypeScript |
| **Backend** | FastAPI, Python 3.13, Pydantic, SQLAlchemy |
| **Database** | PostgreSQL (Supabase) |
| **Cache/Queue** | Redis, Celery |
| **AI** | BYOK Mode — User-provided keys (Google, Groq, Cerebras, OpenRouter, Custom) |
| **Storage** | Cloudflare R2 |
| **Email** | Resend |
| **Payments** | Stripe |
| **Auth** | Supabase Auth (JWT), OIDC SSO, SAML 2.0 |
| **Hosting** | Vercel (frontend), Render (backend) |
| **CI/CD** | GitHub Actions (self-hosted runner: srv1503460, Ubuntu 25.10) |

### By the Numbers

| Metric | Count |
|--------|-------|
| **Total commits** | 298 |
| **API routes** | 427 (211 GET · 144 POST · 16 PUT · 17 PATCH · 39 DELETE) |
| **Router modules** | 54 |
| **Backend services** | 36 |
| **Middleware modules** | 4 (ETag, Performance, RequestID, RateLimitHeaders) |
| **Migrations** | 20 (incl. BYOK api_keys) |
| **Backend Python LOC** | 48,494 |
| **Frontend TS/TSX LOC** | 47,992 |
| **Frontend components** | 59 |
| **Frontend pages** | 16 |
| **Backend test files** | 30 |
| **Deep system tests** | 163/164 (99.4% pass rate) |
| **Security findings** | 0 open (all 9 HIGH/CRITICAL fixed) |

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [📘 API Complete Reference](docs/API_COMPLETE.md) | All 427 endpoints documented with examples |
| [📖 Features Guide](docs/FEATURES_GUIDE.md) | Detailed feature documentation |
| [🎓 Tutorials](docs/TUTORIALS/) | Step-by-step user guides |
| [⚙️ Admin Guide](docs/ADMIN_GUIDE.md) | Deployment and operations |
| [🏗️ Architecture](docs/ARCHITECTURE.md) | System design overview |
| [🚀 Deployment Guide](docs/DEPLOYMENT.md) | Production deployment steps |
| [⚡ Performance](docs/PERFORMANCE_OPTIMIZATION.md) | Optimization details |
| [🔒 Security Policy](SECURITY.md) | Security practices |
| [🤝 Contributing](CONTRIBUTING.md) | Contribution guidelines |

### Tutorial Series

1. [Getting Started](docs/TUTORIALS/01-getting-started.md) - Create account and first project
2. [Creating Content](docs/TUTORIALS/02-creating-content.md) - Import and generate assets
3. [Setting up RSS Feeds](docs/TUTORIALS/03-rss-feeds.md) - Auto-import content
4. [Using Smart Editor](docs/TUTORIALS/04-smart-editor.md) - AI-powered editing
5. [Scheduling Posts](docs/TUTORIALS/05-scheduling-posts.md) - Automated publishing
6. [Team Collaboration](docs/TUTORIALS/06-team-collaboration.md) - Multi-user workflows
7. [Analytics & Insights](docs/TUTORIALS/07-analytics.md) - Performance tracking

---

## 💰 Pricing

| Feature | Free | Pro ($29/mo) | Enterprise |
|---------|------|--------------|------------|
| Content Generations | 10/month | 100/month | Unlimited |
| Scheduled Posts | 5/month | Unlimited | Unlimited |
| RSS Feeds | 1 | 10 | Unlimited |
| Competitors | 2 | 10 | Unlimited |
| Team Members | 1 | 5 | Unlimited |
| API Rate Limit | 100/hr | 1,000/hr | 10,000/hr |
| AI Editor | ✅ | ✅ | ✅ |
| Analytics | Basic | Advanced | Custom |
| SSO / SAML | ❌ | ❌ | ✅ |
| Plugin System | ❌ | ❌ | ✅ |
| Priority Support | ❌ | ✅ | ✅ |
| Custom Integrations | ❌ | ❌ | ✅ |

---

## 🛠️ Development

### Prerequisites

- Python 3.13+
- Node.js 22+
- Docker (optional)
- Git

### Backend Setup

```bash
# Clone repository
git clone git@github.com:jdev-bot/contentforge-ai.git
cd contentforge-ai

# Backend setup
cd src/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Run development server
uvicorn app.main:app --reload

# Run tests
pytest
```

### Frontend Setup

```bash
# Frontend setup
cd src/frontend
npm install

# Copy environment template
cp .env.local.example .env.local

# Run development server
npm run dev

# Build for production
npm run build
```

### Running Tests

```bash
# Backend tests
cd src/backend
pytest
pytest --cov=app

# Frontend tests
cd src/frontend
npm test

# Deep system tests
cd tests
pytest -v
```

---

## 🚢 Deployment

### Quick Deploy to Render

```bash
# Deploy backend with blueprint
curl -X POST https://api.render.com/v1/blueprints \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d @render.yaml
```

### Deploy Frontend to Vercel

```bash
# Using CLI
npm install -g vercel
vercel --prod

# Or connect GitHub repo in Vercel dashboard
```

### Environment Variables

See [`.env.production`](.env.production) for complete list of required environment variables.

**Required for Production:**
- `SUPABASE_URL` & `SUPABASE_SERVICE_ROLE_KEY`
- `ENCRYPTION_KEY` _(BYOK)_
- `RESEND_API_KEY`
- `REDIS_URL`
- `SECRET_KEY` (generate with `openssl rand -hex 32`)

---

## 🔌 API Quick Reference

### Authentication

```bash
# Login
curl -X POST "https://api.contentforge.ai/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret"}'
```

### Create Content

```bash
curl -X POST "https://api.contentforge.ai/api/v1/content" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Article",
    "source": {"type": "url", "url": "https://example.com"},
    "project_id": "project-uuid"
  }'
```

### Generate Assets

```bash
curl -X POST "https://api.contentforge.ai/api/v1/content/{id}/generate" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Schedule Post

```bash
curl -X POST "https://api.contentforge.ai/api/v1/schedule" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": "content-uuid",
    "platform": "twitter",
    "scheduled_at": "2026-04-15T09:00:00Z"
  }'
```

See [API_COMPLETE.md](docs/API_COMPLETE.md) for full documentation of all 427 endpoints.

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Ways to Contribute

- 🐛 Report bugs via GitHub Issues
- 💡 Suggest features
- 📝 Improve documentation
- 🔧 Submit pull requests
- 💬 Join discussions

---

## 📞 Support

- **Documentation**: [docs.contentforge.ai](https://docs.contentforge.ai)
- **Email**: support@contentforge.ai
- **Status**: [status.contentforge.ai](https://status.contentforge.ai)
- **Community**: [Discord](https://discord.gg/contentforge)

---

## 📄 License

ContentForge AI is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [Groq](https://groq.com) for fast AI inference
- [Supabase](https://supabase.com) for database and auth
- [Vercel](https://vercel.com) for frontend hosting
- [Render](https://render.com) for backend hosting
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
- [Next.js](https://nextjs.org/) for the frontend framework

---

<div align="center">

**[🚀 Get Started](https://app.contentforge.ai)** • **[📚 Documentation](docs/)** • **[💬 Community](https://discord.gg/contentforge)**

*Built with 💙 by Neo DevOrg*

</div>