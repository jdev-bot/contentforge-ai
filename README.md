# ContentForge AI

> AI-Powered Content Repurposing & Distribution Platform

## Vision

Transform a single piece of long-form content into 20+ platform-native formats automatically using AI, then distribute across social platforms, email, and blogs with zero manual intervention.

## Tech Stack

### AI Layer
- **Groq API** - 14M tokens/month free tier
- **Llama 3.3 70B** - For content generation
- **Whisper** - For audio transcription

### Database & Storage
- **Supabase** - PostgreSQL + Auth + Storage (500MB free tier)
- **Cloudflare R2** - File storage (10GB free tier)

### Hosting
- **Vercel** - Frontend + API routes (100GB free tier)
- **Render** - Background workers (512MB free tier)

### Automation
- **n8n** - Self-hosted workflow engine (unlimited)

### Email
- **Resend** - 3,000 emails/month free

### Payments
- **Stripe** - Pay-as-you-go

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend                                  │
│                    Next.js 14 + Tailwind                        │
│                        Vercel                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API                                      │
│              Next.js API Routes + FastAPI                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Processing Engine                               │
│                   n8n (Self-hosted)                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                       AI Layer                                   │
│                    Groq API                                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data & Storage                                │
│               Supabase + Cloudflare R2                        │
└─────────────────────────────────────────────────────────────────┘
```

## Development Status

| Milestone | Status | Date |
|-----------|--------|------|
| Project Initialization | ✅ Complete | 2026-04-11 |
| Core Infrastructure | ✅ Complete | 2026-04-12 |
| AI Integration | ✅ Complete | 2026-04-12 |
| Workflow Automation | ✅ Complete | 2026-04-12 |
| Distribution Layer | ✅ Complete | 2026-04-12 |
| UI/UX | ✅ Complete | 2026-04-12 |
| Staging Deployment | 🔄 In Progress | 2026-04-13 |
| Beta Launch | ⏳ Pending | TBD |

## Quick Links

- [📚 API Documentation](docs/API.md)
- [🏗️ Architecture Overview](docs/ARCHITECTURE.md)
- [🚀 Deployment Guide](docs/DEPLOYMENT.md)
- [📋 Project Audit](docs/PROJECT_AUDIT.md)
- [🔒 Security Policy](SECURITY.md)
- [🤝 Contributing](CONTRIBUTING.md)
- [📜 License](LICENSE)

## Deployment

### Quick Deploy

**Render:**
- Use `render.yaml` blueprint for auto-provisioning
- Web Service + Worker + Redis + Scheduler
- Supports Git-based auto-deploy

**Vercel:**
- Connect GitHub repo for auto-deploy
- Serverless functions via API routes
- Edge network CDN included

> See `docs/` for detailed instructions

### Prerequisites

Before deploying, ensure you have:

1. **Vercel Account** - Sign up at [vercel.com](https://vercel.com)
2. **Render Account** - Sign up at [render.com](https://render.com)
3. **Supabase Project** - Create at [supabase.com](https://supabase.com)
4. **API Keys** - Gather keys for Groq, Resend, Stripe, and Cloudflare R2

### Environment Setup

1. Copy the production environment template:
   ```bash
   cp .env.production .env.local
   ```

2. Fill in all required environment variables (see `.env.production` for details)

### Deploy Frontend (Vercel)

#### Option 1: Using Deploy Script

```bash
# Preview deployment
./scripts/deploy-frontend.sh

# Production deployment
./scripts/deploy-frontend.sh --prod
```

#### Option 2: Manual Deployment

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy (from project root)
vercel --prod
```

#### Option 3: Git Integration

1. Push code to GitHub
2. Connect repository in Vercel dashboard
3. Vercel auto-deploys on every push to `main`

### Deploy Backend (Render)

#### Option 1: Using Render Blueprint (Recommended)

1. Go to [Render Dashboard Blueprints](https://dashboard.render.com/blueprints)
2. Click "New Blueprint Instance"
3. Connect your GitHub repository
4. Render reads `render.yaml` and creates services automatically

#### Option 2: Using Deploy Script

```bash
# Run deployment helper
./scripts/deploy-backend.sh

# Or apply blueprint directly (requires Render CLI)
./scripts/deploy-backend.sh --apply
```

#### Option 3: Manual Service Creation

1. Create a new **Web Service** in Render dashboard
2. Connect your GitHub repository
3. Configure:
   - **Runtime**: Docker
   - **Dockerfile Path**: `./infra/docker/Dockerfile.backend`
   - **Port**: 8000
4. Add all environment variables from `.env.production`

### Service Architecture on Render

The `render.yaml` blueprint creates:

| Service | Type | Purpose |
|---------|------|---------|
| `contentforge-ai-api` | Web Service | FastAPI backend API |
| `contentforge-ai-redis` | Redis | Celery task queue |
| `contentforge-ai-worker` | Worker | Background task processing |
| `contentforge-ai-scheduler` | Worker | Scheduled task runner |

### Environment Variables

Required environment variables for production:

| Variable | Source | Required For |
|----------|--------|--------------|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase | Auth & Database |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase | Auth & Database |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase | Server operations |
| `GROQ_API_KEY` | Groq Console | AI content generation |
| `RESEND_API_KEY` | Resend | Email notifications |
| `STRIPE_SECRET_KEY` | Stripe | Payments |
| `R2_*` | Cloudflare | File storage |
| `N8N_WEBHOOK_URL` | Self-hosted | Workflow automation |

See `.env.production` for complete list.

### Post-Deployment Verification

After deployment, verify everything works:

```bash
# Test frontend
curl https://your-vercel-url.vercel.app

# Test backend API
curl https://contentforge-ai-api.onrender.com/api/v1/health

# View API documentation
open https://contentforge-ai-api.onrender.com/docs
```

### Useful Commands

```bash
# View Vercel logs
vercel logs --tail

# View Render logs
render logs --service contentforge-ai-api --tail

# Trigger Vercel redeploy
vercel --prod

# Trigger Render redeploy
render deploy --service contentforge-ai-api
```

## License

MIT

---

*Built with 💙 by Neo DevOrg*
