# Tutorial: Getting Started with ContentForge AI

> Your first steps to AI-powered content creation

---

## What You'll Learn

By the end of this tutorial, you will:
- Set up your local development environment
- Create your ContentForge AI account
- Understand the dashboard
- Navigate the main features

**Time Required**: 15 minutes

---

## Prerequisites

Before you begin, make sure you have the following installed:

| Requirement | Version | Notes |
|-------------|---------|-------|
| **Python** | 3.13+ | Backend runtime |
| **Node.js** | v22.22.2+ | Frontend runtime |
| **npm** | Included with Node | Package manager |
| **Git** | Latest | Version control |
| **PostgreSQL** | 15+ | Via Supabase (cloud or self-hosted) |
| **Redis** | 7+ | Rate limiting & caching (optional for dev) |

### Self-Hosted Option

ContentForge AI supports a fully self-hosted deployment. If you prefer to run everything on your own infrastructure:

1. **Database**: Use self-hosted Supabase or a standalone PostgreSQL instance
2. **Cache**: Run Redis locally (`docker run -p 6379:6379 redis:alpine`)
3. **AI Provider**: Configure your own Groq API key (or swap the `GroqService` for another LLM provider)
4. **Runner**: Use the provided Dockerfile at `infra/docker/Dockerfile.backend`

See [Deployment Guide](../DEPLOYMENT.md) for full self-hosted setup instructions.

---

## Step 1: Clone and Set Up

### Clone the Repository

```bash
git clone git@github.com:jdev-bot/contentforge-ai.git
cd contentforge-ai
```

### Backend Setup

```bash
cd src/backend

# Create virtual environment
python3.13 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your Supabase, Groq, and Redis credentials
```

### Frontend Setup

```bash
cd src/frontend

# Install dependencies
npm install

# Copy environment template
cp .env.local.example .env.local
# Edit .env.local with your API URL and Supabase credentials
```

### Start the Application

```bash
# Terminal 1: Backend
cd src/backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd src/frontend
npm run dev
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Step 2: Create Your Account

### Sign Up

1. Go to [http://localhost:3000](http://localhost:3000) (or your deployed URL)
2. Click **"Get Started Free"**
3. Enter your email address
4. Create a secure password (min 8 characters)
5. Enter your full name
6. Click **"Create Account"**

### Verify Your Email

1. Check your email inbox
2. Open the verification email from ContentForge AI
3. Click the **"Verify Email"** button
4. You'll be redirected to the dashboard

> **Tip**: If you don't see the email, check your spam folder.

---

## Step 3: Explore the Dashboard

After logging in, you'll see your dashboard. Here's what each section does:

### Dashboard Overview

```
┌─────────────────────────────────────────────────────┐
│  <Logo>     Dashboard   Projects   Content  [Profile]  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  📊 Quick Stats                                    │
│  ├─ Total Content: 0                               │
│  ├─ Assets Generated: 0                              │
│  ├─ Published Posts: 0                               │
│  └─ This Month's Usage: 0/10                       │
│                                                     │
│  📅 Upcoming Scheduled Posts                       │
│  ├─ No posts scheduled                             │
│                                                     │
│  🎯 Recent Activity                                 │
│  ├─ Welcome to ContentForge! 🎉                  │
│                                                     │
│  [+ Create New Content]                             │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Navigation Menu

| Icon | Section | Purpose |
|------|---------|---------|
| 📊 Dashboard | Overview | Stats, quick actions, recent activity |
| 📁 Projects | Projects | Manage content projects |
| 📝 Content | Content | All your content items |
| 📤 Distribute | Publishing | Schedule and publish posts |
| 🧠 AI Editor | Editor | Smart content editing |
| 📈 Analytics | Analytics | Performance insights, custom dashboards, funnel tracking |
| ⚙️ Settings | Settings | Account configuration, SSO, integrations |

---

## Step 4: Create Your First Project

Projects help organize your content by theme, campaign, or client.

### Create a Project

1. Click **"Projects"** in the navigation
2. Click the **"+ New Project"** button
3. Fill in the project details:

**Example:**
```
Name: Q2 Marketing Campaign
Description: Content for our Q2 product launch and awareness campaign
Target Platforms: Twitter, LinkedIn, Blog
Brand Voice:
  Tone: Professional
  Style: Friendly
```

4. Click **"Create Project"**

### Project Settings

Each project can have:
- **Name** - Project identifier
- **Description** - What this project is about
- **Brand Voice** - Tone and style settings
- **Target Platforms** - Where you'll publish
- **Team Members** - Who can access (Pro+)
- **Quality Scoring** - Enable/disable AI quality assessment
- **Data Retention** - Configure content retention policies

---

## Step 5: Connect Your Accounts (Optional)

To publish directly to social platforms, connect your accounts:

### Connect a Platform

1. Go to **Settings > Integrations**
2. Click **"Connect"** next to a platform:
   - Twitter/X
   - LinkedIn
   - Instagram
   - Facebook
3. Follow the OAuth authorization flow
4. Your accounts are now connected

### SSO / SAML Login (Enterprise)

Organizations on the Enterprise plan can configure:
- **OIDC-based SSO** — Connect your identity provider (Okta, Auth0, Azure AD, etc.)
- **SAML SSO** — Federated authentication for enterprise deployments

Navigate to **Settings > Security > SSO** to configure your identity provider.

> **Note**: You can still use ContentForge without connecting accounts — you'll just copy/paste content manually.

---

## Step 6: Understanding Your Usage

### Free Plan Limits

| Feature | Limit |
|---------|-------|
| Content Generations | 10/month |
| Scheduled Posts | 5/month |
| RSS Feeds | 1 |
| Competitors Tracked | 2 |

### Track Usage

Your usage is shown in the dashboard:
- Monthly generation count
- Remaining generations
- Reset date (monthly)

### Upgrade Options

Click **"Upgrade"** in the dashboard to see Pro and Enterprise plans with higher limits, including custom dashboards, SLA monitoring, and advanced analytics.

---

## Step 7: Access Help Resources

### Where to Get Help

1. **In-App Help** - Click the **?** icon in any screen
2. **Documentation** - Visit [docs.contentforge.ai](https://docs.contentforge.ai)
3. **Video Tutorials** - Watch on our [YouTube channel](https://youtube.com/contentforge)
4. **Community** - Join our [Discord](https://discord.gg/contentforge)
5. **Email Support** - support@contentforge.ai
6. **Plugin Marketplace** - Browse community plugins at **Settings > Marketplace**

---

## Next Steps

Now that you're set up, try these tutorials:

1. **[Creating Your First Content](02-creating-content.md)** - Import and repurpose content
2. **[Using the Smart Editor](04-smart-editor.md)** - Edit content with AI
3. **[Scheduling Posts](05-scheduling-posts.md)** - Automate your publishing

---

## Quick Tips

### ✅ Do's

- Create projects before adding content
- Use descriptive names for everything
- Save drafts frequently
- Preview content before scheduling
- Check your usage regularly
- Review quality scores on generated content

### ❌ Don'ts

- Don't share your login credentials
- Don't exceed your monthly limits
- Don't ignore failed notifications
- Don't forget to verify your email

---

## Troubleshooting

### Can't Log In?

1. Check you're using the correct email
2. Try "Forgot Password"
3. Clear browser cache
4. Try incognito/private mode

### Verification Email Not Received?

1. Check spam/junk folder
2. Wait 5 minutes and check again
3. Click "Resend Email" on the verification page
4. Try a different email address

### Dashboard Not Loading?

1. Refresh the page
2. Clear browser cache
3. Disable browser extensions
4. Try a different browser

### Backend Won't Start?

1. Verify Python 3.13+ is installed: `python --version`
2. Check `.env` file has required credentials
3. Ensure port 8000 is not in use: `lsof -i :8000`
4. Check Supabase connection is reachable

### Frontend Won't Start?

1. Verify Node.js v22.22.2+ is installed: `node --version`
2. Run `npm install` in `src/frontend/`
3. Check `.env.local` is configured
4. Ensure port 3000 is not in use: `lsof -i :3000`

---

**Congratulations!** 🎉 You're now ready to start creating content with ContentForge AI.

Need help? Contact us at **support@contentforge.ai**