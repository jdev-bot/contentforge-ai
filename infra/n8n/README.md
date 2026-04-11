# ContentForge AI - n8n Workflows

This directory contains exported n8n workflows for the ContentForge AI platform.

## Workflows

### 1. Content Processing Pipeline
- **File**: `content-processing.json`
- **Trigger**: Webhook from backend
- **Steps**:
  1. Receive content ID
  2. Extract content from source
  3. Generate assets via Groq API
  4. Save to database
  5. Notify user

### 2. Distribution Scheduler
- **File**: `distribution-scheduler.json`
- **Trigger**: Schedule (cron)
- **Steps**:
  1. Query pending distributions
  2. Check if ready to publish
  3. Publish to platform APIs
  4. Update status
  5. Log result

### 3. Usage Reporter
- **File**: `usage-reporter.json`
- **Trigger**: Daily at midnight
- **Steps**:
  1. Aggregate daily usage
  2. Send email report
  3. Check usage limits
  4. Alert if approaching limit

## Setup

1. Install n8n: `npm install -g n8n`
2. Start n8n: `n8n start`
3. Import workflows from this directory
4. Configure credentials for:
   - Supabase
   - Groq API
   - Social media APIs
   - Email (Resend)

## Environment Variables

Create `.env` in n8n directory:

```
SUPABASE_URL=
SUPABASE_KEY=
GROQ_API_KEY=
RESEND_API_KEY=
TWITTER_API_KEY=
LINKEDIN_ACCESS_TOKEN=
```
