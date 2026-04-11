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
| Core Infrastructure | 🔄 In Progress | |
| AI Integration | ⏳ Pending | |
| Workflow Automation | ⏳ Pending | |
| Distribution Layer | ⏳ Pending | |
| UI/UX | ⏳ Pending | |
| Beta Launch | ⏳ Pending | |

## License

MIT

---

*Built with 💙 by Neo DevOrg*
