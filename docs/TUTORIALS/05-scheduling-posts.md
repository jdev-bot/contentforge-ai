# Tutorial: Scheduling Posts

> Automate your content publishing with scheduled posts, funnel tracking, and SLA monitoring

---

## What You'll Learn

By the end of this tutorial, you will:
- Schedule posts for future publication
- Use smart scheduling recommendations
- Manage your publishing queue
- Track content through your marketing funnel
- Attribute results to specific content pieces
- Monitor SLA compliance for publishing commitments
- Bulk schedule multiple posts
- Handle failed posts and retries

**Time Required**: 25 minutes

---

## Prerequisites

Before starting:
- ContentForge account
- Content or assets ready to publish
- Connected social accounts (optional)

---

## Step 1: Access the Scheduler

### Navigation

1. Click **"Distribute"** in the main navigation
2. Select **"Schedule"** tab
3. Or click **"Schedule"** from any content/asset

### Scheduler Overview

```
┌─────────────────────────────────────────────────────┐
│ Schedule                                             │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 📊 Stats Summary:                                  │
│   Pending: 3 | Published: 12 | Failed: 1           │
│   SLA Compliance: 98.5% | On-time Rate: 96%        │
│                                                     │
│ [+ Schedule New Post]                              │
│                                                     │
│ Upcoming Posts:                                    │
│ ├─ Tomorrow 9:00 AM - Twitter Thread               │
│ ├─ Apr 15 2:00 PM - LinkedIn Article               │
│ └─ Apr 16 10:00 AM - Newsletter                    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Step 2: Schedule a Single Post

### Choose Content to Schedule

1. Navigate to your content or assets
2. Find the asset you want to schedule
3. Click **"Schedule"** button

Or from the scheduler:
1. Click **"+ Schedule New Post"**
2. Select content from dropdown

### Configure Schedule

**Required Fields:**

```
Content: "10 Marketing Tips Thread"
Platform: Twitter
Schedule Time: 2026-04-15 09:00
Timezone: America/New_York
```

**Optional Settings:**

```
Funnel Stage: Awareness
Attribution Tags: q2-campaign, blog-repurpose
SLA Deadline: 2026-04-15 10:00 (1hr buffer)
```

### Platform Selection

| Platform | Content Types |
|----------|---------------|
| Twitter/X | Posts, threads |
| LinkedIn | Posts, articles |
| Instagram | Posts, stories |
| Facebook | Posts, links |
| TikTok | Video scripts |
| Email | Newsletters |
| Blog | Articles |

### Time Selection

**Options:**
- Specific date and time
- "Best time" recommendation
- Recurring schedules

### Save Schedule

Click **"Schedule Post"** - the system will:
1. Validate the content
2. Add to publishing queue
3. Set status to "pending"
4. Track funnel stage and attribution
5. Show confirmation

---

## Step 3: Use Smart Scheduling

### Get Best Time Recommendations

1. When scheduling, click **"Find Best Time"**
2. System analyzes:
   - Platform peak hours
   - Your historical engagement
   - Industry benchmarks
   - Funnel stage performance data

### Best Time Defaults

| Platform | Recommended Times |
|----------|-------------------|
| Twitter | 9:00 AM, 12:00 PM, 3:00 PM, 6:00 PM |
| LinkedIn | 8:00 AM, 12:00 PM, 5:00 PM |
| Instagram | 11:00 AM, 2:00 PM, 7:00 PM |
| Facebook | 9:00 AM, 1:00 PM, 3:00 PM |
| TikTok | 7:00 AM, 12:00 PM, 7:00 PM, 9:00 PM |

---

## Step 4: Funnel Tracking

Funnel tracking lets you see how content moves prospects through your marketing funnel.

### Setting Funnel Stages

When scheduling a post, assign it a funnel stage:

| Stage | Description | Content Types |
|-------|-------------|---------------|
| **Awareness** | Top of funnel — attracting new audiences | Blog posts, infographics, social posts |
| **Interest** | Engaging curious prospects | Educational content, how-tos |
| **Consideration** | Nurturing toward decision | Case studies, comparisons, webinars |
| **Conversion** | Driving action | Demos, trials, pricing, CTAs |
| **Retention** | Keeping existing customers | Updates, tips, community content |

### Assigning Funnel Stages

1. When creating a schedule, select **"Funnel Stage"**
2. Choose the appropriate stage
3. Optionally add **"Attribution Tags"** for campaign tracking

```
Schedule Post:

Content: "10 Marketing Tips Thread"
Platform: Twitter
Funnel Stage: Awareness
Attribution Tags: q2-campaign, awareness-phase
```

### Viewing Funnel Analytics

Navigate to **Analytics > Funnel** to see:

```
┌─────────────────────────────────────────────────────┐
│ Content Funnel Analysis                              │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Awareness → Interest → Consideration → Conversion   │
│   420 posts  210 posts   85 posts      32 posts     │
│   ──────70%────→ ────60%────→ ────50%────→          │
│                                                     │
│ Top Performing (Awareness):                          │
│ 1. "AI Marketing Tips" - 1,240 engagements          │
│ 2. "Industry Trends" - 890 engagements             │
│                                                     │
│ Drop-off Point: Consideration → Conversion (50%)    │
│ Recommendation: Add more case studies & demos        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Step 5: Attribution Modeling

Attribution modeling helps you understand which content pieces and campaigns drive results.

### How Attribution Works

Each scheduled post can carry attribution tags that link it to campaigns, channels, and content sources. When engagement data comes in, ContentForge attributes results back to the originating content.

### Setting Up Attribution

1. When scheduling, add **Attribution Tags**:
   ```
   Campaign: q2-2026-launch
   Channel: organic-social
   Source: blog-repurpose
   Content Type: thread
   ```
2. Tags are automatically included in UTM parameters when applicable
3. Engagement and conversion data flows back to the content item

### Attribution Models

| Model | Description | Best For |
|-------|-------------|----------|
| **First Touch** | Credit to the first content that brought the user | Brand awareness campaigns |
| **Last Touch** | Credit to the content before conversion | Direct response campaigns |
| **Linear** | Equal credit across all touchpoints | Multi-channel strategies |
| **Time Decay** | More credit to recent touchpoints | Long sales cycles |

Configure your attribution model in **Analytics > Attribution > Settings**.

### Viewing Attribution Reports

Navigate to **Analytics > Attribution** to see:

```
┌─────────────────────────────────────────────────────┐
│ Attribution Report - Q2 2026 Campaign                │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Top Attributed Content:                             │
│ 1. "10 Marketing Tips" → 45 conversions ($12.3k)    │
│ 2. "Product Launch Thread" → 32 conversions ($8.9k) │
│ 3. "Case Study Newsletter" → 28 conversions ($7.4k) │
│                                                     │
│ Channel Attribution:                                │
│ ├─ Organic Social: 42% of conversions              │
│ ├─ Email: 31% of conversions                       │
│ └─ Blog: 27% of conversions                        │
│                                                     │
│ Model: Last Touch (change in Settings)              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Step 6: SLA Monitoring

SLA monitoring ensures you meet your publishing commitments and content delivery targets.

### Setting Up SLA Policies

1. Go to **Analytics > SLA**
2. Click **"Create SLA Policy"**
3. Configure:

```
SLA Policy: Daily Publishing Commitment

Target: Publish at least 3 posts per day
Schedule Window: 8:00 AM - 8:00 PM (ET)
Grace Period: 30 minutes
Alert: Email + In-app if SLA at risk
Escalation: Notify team lead if SLA breached
```

### SLA Dashboard

```
┌─────────────────────────────────────────────────────┐
│ SLA Monitoring                                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Active SLAs: 2                                     │
│                                                     │
│ 📊 Daily Publishing (3 posts/day)                   │
│   Today: 2/3 published (67%)                       │
│   Status: 🟡 At Risk — 1 more needed by 8:00 PM    │
│   Compliance (30d): 98.5%                          │
│                                                     │
│ 📊 Weekly Content (15 posts/week)                   │
│   This Week: 12/15 published (80%)                  │
│   Status: 🟢 On Track — 3 remaining by Sunday      │
│   Compliance (30d): 96%                             │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### SLA Alerts

| Alert Type | Trigger | Recipient |
|------------|---------|-----------|
| **At Risk** | Below target with time remaining | Content creator |
| **Breached** | SLA target missed | Creator + team lead |
| **Recovered** | SLA back on track after breach | Creator |
| **Weekly Summary** | SLA compliance for the week | Team |

---

## Step 7: Bulk Scheduling

### When to Use Bulk Schedule

- Weekly content calendars
- Campaign rollouts
- Series publishing
- Consistent posting schedules

### Create Bulk Schedule

1. Go to **Distribute > Schedule**
2. Click **"Bulk Schedule"**
3. Select content to schedule
4. Configure schedule (time, platform, funnel stage, attribution tags)
5. Review schedule preview
6. Click **"Schedule All"**

### Bulk Schedule Tips

- Space posts 1-2 hours apart minimum
- Mix content types for variety
- Assign funnel stages to each post
- Add consistent attribution tags for campaign tracking
- Consider platform-specific timing
- Leave buffer time for engagement

---

## Step 8: Manage Scheduled Posts

### Edit a Scheduled Post

1. Find post in queue
2. Click **"Edit"**
3. Update schedule time, content, funnel stage, attribution tags
4. Save changes

**Restrictions:**
- Can't edit posts currently processing
- Can't edit already published posts
- Some changes may require reschedule

### Cancel a Scheduled Post

1. Find post in queue
2. Click **"Cancel"**
3. Confirm cancellation
4. Post removed from queue

**Note:** Cancelled posts can be rescheduled later.

### Publish Immediately

Bypass the schedule and publish now:

1. Find scheduled post
2. Click **"Publish Now"**
3. Confirm immediate publication
4. Post processes immediately

---

## Step 9: Handle Failed Posts

### Common Failure Reasons

| Reason | Solution |
|--------|----------|
| Authentication expired | Reconnect account |
| Rate limited | Wait and retry |
| Content violates policy | Edit content |
| Platform API error | Retry later |
| Network error | Retry |

### Retry Failed Posts

1. Go to **Failed** tab in queue
2. Find failed post
3. Click **"Retry"**
4. System attempts publication again

**Auto-Retry:**
- System retries failed posts automatically
- Up to 3 attempts with backoff
- Manual retry available anytime
- SLA policies may trigger alerts on repeated failures

---

## Step 10: View Schedule Calendar

### Calendar View

Navigate to **Distribute > Calendar**:

- **Month view** — See entire month at a glance
- **Week view** — Detailed weekly schedule
- **Day view** — Hour-by-hour breakdown
- **List view** — Sortable post list with funnel stages

### Calendar Features

- Click date to schedule new post
- Drag post to reschedule
- Click post to edit
- Filter by platform
- Color-coded by funnel stage
- SLA deadlines shown as markers

---

## Best Practices

### Scheduling Strategy

1. **Plan ahead** — Schedule 2-4 weeks in advance
2. **Maintain consistency** — Post at regular intervals
3. **Consider timing** — Post when audience is active
4. **Mix content types** — Variety keeps engagement
5. **Track funnel stages** — Ensure balanced content across the funnel
6. **Use attribution** — Know what content drives results

### Funnel Strategy

```
Recommended Content Mix:

Awareness: 40% of posts (blog repurposes, industry news)
Interest: 25% of posts (how-tos, educational)
Consideration: 20% (case studies, comparisons)
Conversion: 10% (CTAs, demos, pricing)
Retention: 5% (updates, tips)
```

### SLA Management

- Set realistic SLA targets based on team capacity
- Use grace periods to avoid false alarms
- Monitor compliance weekly, not just daily
- Adjust SLA targets when team size changes

---

## Troubleshooting

### Post Not Publishing

**Check:**
1. Account is connected
2. Authentication hasn't expired
3. Content meets platform requirements
4. Not rate limited

### SLA Showing "Breached" Unexpectedly

**Common Issues:**
- Timezone mismatch between SLA and schedule
- Grace period too short
- Failed posts not retried in time

**Fix:**
- Align SLA and schedule timezones
- Extend grace period for reliability
- Enable auto-retry for failed posts

### Attribution Data Missing

**Causes:**
- No attribution tags assigned to scheduled posts
- UTM parameters not configured
- Engagement data not yet available

**Fix:**
- Add attribution tags when scheduling
- Check Analytics > Attribution > Settings for UTM config
- Wait 24-48 hours for engagement data to flow in

---

## Summary

You now know how to:
- ✅ Schedule posts for future publication
- ✅ Use smart scheduling recommendations
- ✅ Track content through marketing funnel stages
- ✅ Use attribution modeling to measure content ROI
- ✅ Monitor SLA compliance for publishing commitments
- ✅ Bulk schedule multiple posts
- ✅ Manage the publishing queue
- ✅ Handle failed posts and retries
- ✅ View and use the content calendar

---

## Next Steps

Now that you can schedule posts:

1. **[Team Collaboration](06-team-collaboration.md)** - Work with your team
2. **[Analytics & Insights](07-analytics.md)** - Track funnel and attribution performance
3. **[Custom Dashboards](07-analytics.md#custom-dashboards)** — Build dashboards for SLA and funnel tracking

---

**Questions?** Contact support@contentforge.ai