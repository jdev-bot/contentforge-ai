# ContentForge AI - Local Deployment Guide

Step-by-step instructions to run ContentForge AI on your local machine for manual testing.

---

## Prerequisites

Make sure you have these installed:

- **Python 3.11+** (`python3 --version`)
- **Node.js 20+** (`node --version`)
- **Redis** (for Celery background tasks)
- **Git** with SSH configured for `github.com`
- **A Supabase account** (free tier works)
- **A Groq account** (free tier: 14M tokens/month)

---

## Step 1: Clone the Repository

```bash
cd ~/projects  # or wherever you keep code

git clone git@github.com:jdev-bot/contentforge-ai.git
cd contentforge-ai
```

---

## Step 2: Set Up Supabase (Database + Auth)

This is the most important step — you need a Supabase project for the database and authentication.

### 2a. Create a Supabase Project

1. Go to [https://supabase.com](https://supabase.com) and sign up/log in
2. Click **"New Project"**
3. Name it `contentforge-ai-dev`
4. Set a database password (save it!)
5. Choose the closest region
6. Click **"Create new project"**
7. Wait for the project to provision (~2 min)

### 2b. Run the Database Migrations

Go to **SQL Editor** in your Supabase dashboard and run these migration files **in order**:

1. `infra/supabase/schema.sql` — Core tables (profiles, projects, content, distributions, etc.)
2. `src/backend/migrations/004_email_system.sql`
3. `src/backend/migrations/009_trash_table.sql`
4. `src/backend/migrations/010_scheduled_posts.sql`
5. `src/backend/migrations/011_rss_feeds.sql`
6. `src/backend/migrations/013_content_freshness.sql`
7. `src/backend/migrations/014_trending_topics.sql`
8. `src/backend/migrations/015_audience_metrics.sql`
9. `src/backend/migrations/016_content_alerts.sql`
10. `src/backend/migrations/017_competitor_analysis.sql`
11. `src/backend/migrations/018_integrations.sql`

> ⚠️ **Skip** `011_translations_table.sql` and `012_remove_translations.sql` — these were removed per design decision.

For each file: Copy its contents → Paste into SQL Editor → Click **Run**.

### 2c. Get Your API Keys

Go to **Settings → API** in your Supabase dashboard. You need:

| Key | Where to find |
|-----|---------------|
| `Project URL` | Shown at the top (e.g., `https://abc123.supabase.co`) |
| `anon public` key | Under "Project API keys" |
| `service_role` key | Under "Project API keys" (⚠️ keep secret!) |

---

## Step 3: Get a Groq API Key

1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Go to **API Keys**
4. Click **"Create API Key"**
5. Copy the key (starts with `gsk_`)

Free tier gives you 14M tokens/month — more than enough for testing.

---

## Step 4: Set Up Backend (Python/FastAPI)

### 4a. Create a Virtual Environment

```bash
cd contentforge-ai/src/backend

python3 -m venv venv
source venv/bin.activate  # on macOS/Linux
# OR: venv\Scripts\activate  # on Windows

pip install --upgrade pip
pip install -r requirements.txt
```

### 4b. Create the Backend `.env` File

```bash
cat > .env << 'EOF'
# App
APP_NAME=ContentForge AI
APP_ENV=development
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production-abc123xyz

# Supabase
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_KEY=YOUR_SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY=YOUR_SUPABASE_SERVICE_ROLE_KEY

# Groq
GROQ_API_KEY=YOUR_GROQ_API_KEY
GROQ_MODEL=llama-3.3-70b-versatile

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Optional (can leave empty for testing)
RESEND_API_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
EOF
```

**Replace the values:**
- `YOUR_PROJECT_ID` → Your Supabase project ID
- `YOUR_SUPABASE_ANON_KEY` → Your anon key from Step 2c
- `YOUR_SUPABASE_SERVICE_ROLE_KEY` → Your service role key from Step 2c
- `YOUR_GROQ_API_KEY` → Your Groq key from Step 3

### 4c. Install and Start Redis

Redis is required for Celery (background task queue).

**Linux (Debian/Ubuntu):**
```bash
sudo apt install redis-server
sudo systemctl start redis-server
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Verify Redis is running:**
```bash
redis-cli ping
# Should respond: PONG
```

### 4d. Start the Backend API Server

```bash
cd contentforge-ai/src/backend
source venv/bin/activate

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
🚀 Starting ContentForge AI in development mode
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verify:** Open [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health) — should return `{"status": "healthy"}`

**API Docs:** Open [http://localhost:8000/docs](http://localhost:8000/docs) — interactive Swagger UI

### 4e. Start the Celery Worker (Optional — for background tasks)

Open a **new terminal**:

```bash
cd contentforge-ai/src/backend
source venv/bin/activate

celery -A app.core.celery_app worker --loglevel=info --concurrency=2
```

### 4f. Start the Celery Beat Scheduler (Optional — for scheduled tasks)

Open **another terminal**:

```bash
cd contentforge-ai/src/backend
source venv/bin/activate

celery -A app.core.celery_app beat --loglevel=info
```

> 💡 **Without Celery**, the app still works — you just won't have background tasks (scheduled publishing, RSS auto-import, trend detection). Start with just the API server and add Celery when you need those features.

---

## Step 5: Set Up Frontend (Next.js)

### 5a. Install Dependencies

```bash
cd contentforge-ai/src/frontend

npm install
```

### 5b. Create the Frontend `.env.local` File

```bash
cat > .env.local << 'EOF'
# Supabase (public — safe to expose)
NEXT_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=YOUR_SUPABASE_ANON_KEY

# API URL (points to your local backend)
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# App URL
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Optional
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
NEXT_PUBLIC_R2_PUBLIC_URL=
EOF
```

**Replace the values** same as Step 4b.

### 5c. Start the Frontend Dev Server

```bash
npm run dev
```

You should see:
```
✓ Ready in 2s
○ Local: http://localhost:3000
```

**Open:** [http://localhost:3000](http://localhost:3000)

---

## Step 6: Create a Test User

1. Open [http://localhost:3000](http://localhost:3000)
2. Click **"Sign Up"** or go to `/login`
3. Enter an email and password
4. If Supabase email confirmation is enabled, check your email and confirm
5. Log in with your new credentials

> 💡 **Tip:** To skip email confirmation during testing, go to your Supabase dashboard → **Authentication → Settings → Email** → Disable "Enable email confirmations"

---

## Step 7: Test the Features

Here's what you can test and how:

| Feature | How to Test |
|---------|-------------|
| **Dashboard** | Navigate the main dashboard at `/` |
| **Content Creation** | Go to Content tab → "New Content" → Paste a URL or text |
| **Smart Editor** | Open a content item → Use Ctrl+R (Rewrite), Ctrl+E (Expand), Ctrl+Shift+C (Condense), Ctrl+O (Optimize) |
| **Scheduled Publishing** | Content tab → "Schedule" → Pick date/time |
| **RSS Import** | Dashboard → RSS tab → "Add Feed" → Enter an RSS URL (e.g., `https://hnrss.org/frontpage`) |
| **Freshness Dashboard** | Dashboard → Freshness tab → See content scores |
| **Trending Topics** | Dashboard → Trends tab → Browse trending topics |
| **Audience Growth** | Dashboard → Growth tab → See metrics |
| **Performance Alerts** | Bell icon in header → Configure alert rules |
| **Team Calendar** | Dashboard → Calendar tab → View scheduled posts |
| **Competitor Analysis** | Dashboard → Competitors tab → Add a competitor |
| **Integrations** | Settings → Integrations → Configure webhooks |
| **Search** | Press Ctrl+K → Search content |
| **Onboarding** | Navigate to `/onboarding` → Walk through the guide |
| **API Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) |

---

## Step 8: Verify Everything Works

Run this quick checklist:

- [ ] Backend API responds: `curl http://localhost:8000/api/v1/health`
- [ ] Frontend loads: Open `http://localhost:3000`
- [ ] Can sign up / log in
- [ ] Can create a project
- [ ] Can import content (try a blog post URL)
- [ ] AI features work (Smart Editor rewrite/expand)
- [ ] Dashboard shows content and stats
- [ ] API docs accessible at `/docs`

---

## Troubleshooting

### Backend won't start — `SECRET_KEY` error
Make sure your `.env` file exists in `src/backend/` and has `SECRET_KEY` set.

### Backend won't start — `Supabase` error
Check that `SUPABASE_URL` and `SUPABASE_KEY` are correct in `.env`.

### Frontend shows blank page
Check the browser console (F12). Usually a missing `NEXT_PUBLIC_SUPABASE_URL` or `NEXT_PUBLIC_SUPABASE_ANON_KEY` in `.env.local`.

### Frontend can't reach backend
Verify the backend is running on port 8000. Check `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1` in `.env.local`.

### AI features return errors
Check that `GROQ_API_KEY` is set correctly in the backend `.env`. Verify at [https://console.groq.com](https://console.groq.com).

### Celery tasks not running
Make sure Redis is running (`redis-cli ping` → `PONG`) and both the Celery worker and beat are started.

### CORS errors in browser
Ensure `CORS_ORIGINS=["http://localhost:3000"]` is set in the backend `.env`.

### Database errors (table not found)
You likely missed a migration. Re-run Step 2b — make sure all migration files were executed in order.

---

## Quick Reference: Running the Stack

```bash
# Terminal 1: Redis
redis-server  # or: sudo systemctl start redis-server

# Terminal 2: Backend API
cd contentforge-ai/src/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Celery Worker (optional)
cd contentforge-ai/src/backend
source venv/bin/activate
celery -A app.core.celery_app worker --loglevel=info --concurrency=2

# Terminal 4: Celery Beat (optional)
cd contentforge-ai/src/backend
source venv/bin/activate
celery -A app.core.celery_app beat --loglevel=info

# Terminal 5: Frontend
cd contentforge-ai/src/frontend
npm run dev
```

**Minimum for testing:** Redis + Backend API + Frontend (3 terminals)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│  Browser  (http://localhost:3000)                 │
│  ┌─────────────────────────────────────────────┐ │
│  │  Next.js Frontend                           │ │
│  │  React 19 + Tailwind + Framer Motion        │ │
│  └──────────────┬──────────────────────────────┘ │
└─────────────────┼────────────────────────────────┘
                  │ HTTP API calls
                  ▼
┌─────────────────────────────────────────────────┐
│  FastAPI Backend  (http://localhost:8000)         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │ API Router│  │ Services │  │ Groq AI      │   │
│  │ (50+ endp)│  │          │  │ Integration  │   │
│  └──────┬────┘  └────┬─────┘  └──────────────┘   │
│         │            │                            │
│  ┌──────▼────────────▼─────┐                     │
│  │     Supabase Client     │                     │
│  └──────────┬──────────────┘                     │
└─────────────┼────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────┐
│  Supabase  (Cloud)                               │
│  ┌──────────┐  ┌──────────┐                      │
│  │ PostgreSQL│  │ Auth      │                      │
│  │ Database  │  │ Service   │                      │
│  └──────────┘  └──────────┘                      │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  Redis  (localhost:6379)                         │
│  Celery Broker + Result Backend                  │
└─────────────────────────────────────────────────┘
```

---

*That's it! ContentForge AI should be running locally. 🚀*