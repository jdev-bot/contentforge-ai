# Tutorial: Scheduling Posts

> Automate your content publishing with scheduled posts

---

## What You'll Learn

By the end of this tutorial, you will:
- Schedule posts for future publication
- Use smart scheduling recommendations
- Manage your publishing queue
- Bulk schedule multiple posts
- Handle failed posts and retries

**Time Required**: 20 minutes

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
│   Pending: 3 | Published: 12 | Failed: 1        │
│                                                     │
│ [+ Schedule New Post]                              │
│                                                     │
│ Upcoming Posts:                                    │
│ ├─ Tomorrow 9:00 AM - Twitter Thread            │
│ ├─ Apr 15 2:00 PM - LinkedIn Article            │
│ └─ Apr 16 10:00 AM - Newsletter                 │
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
Asset Type: thread
Settings:
  ├─ thread_mode: true
  ├─ auto_hashtags: true
  └─ first_tweet_only: false
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
4. Show confirmation

---

## Step 3: Use Smart Scheduling

### Get Best Time Recommendations

1. When scheduling, click **"Find Best Time"**
2. System analyzes:
   - Platform peak hours
   - Your historical engagement
   - Industry benchmarks

### Best Time Defaults

| Platform | Recommended Times |
|----------|-------------------|
| Twitter | 9:00 AM, 12:00 PM, 3:00 PM, 6:00 PM |
| LinkedIn | 8:00 AM, 12:00 PM, 5:00 PM |
| Instagram | 11:00 AM, 2:00 PM, 7:00 PM |
| Facebook | 9:00 AM, 1:00 PM, 3:00 PM |
| TikTok | 7:00 AM, 12:00 PM, 7:00 PM, 9:00 PM |

### Timezone Considerations

**Select the timezone for your audience:**

- Local business: Your timezone
- National audience: Central US
- Global audience: UTC
- Specific region: Target timezone

---

## Step 4: View Publishing Queue

### Queue Statuses

| Status | Description | Actions |
|--------|-------------|---------|
| Pending | Waiting for scheduled time | Edit, Cancel |
| Scheduled | Time set, ready | Edit, Cancel |
| Processing | Currently publishing | Wait |
| Published | Successfully posted | View post |
| Failed | Error occurred | Retry, Edit |
| Cancelled | User cancelled | Reschedule |

### Queue Management

**Actions Available:**

1. **Edit** - Change time or content
2. **Cancel** - Remove from queue
3. **Publish Now** - Immediate publication
4. **Retry** - Retry failed posts
5. **Duplicate** - Clone schedule

---

## Step 5: Bulk Scheduling

### When to Use Bulk Schedule

- Weekly content calendars
- Campaign rollouts
- Series publishing
- Consistent posting schedules

### Create Bulk Schedule

1. Go to **Distribute > Schedule**
2. Click **"Bulk Schedule"**
3. Select content to schedule:
   ```
   [x] Blog Post Analysis
   [x] Twitter Thread
   [x] LinkedIn Article
   [x] Newsletter
   ```

4. Configure schedule:
   ```
   Platform: Twitter
   Start Time: Apr 15, 2026 9:00 AM
   Interval: 60 minutes
   Timezone: America/New_York
   ```

5. Review schedule preview:
   ```
   Apr 15 09:00 - Blog Post Analysis
   Apr 15 10:00 - Twitter Thread
   Apr 15 11:00 - LinkedIn Article
   Apr 15 12:00 - Newsletter
   ```

6. Click **"Schedule All"**

### Bulk Schedule Tips

- Space posts 1-2 hours apart minimum
- Mix content types for variety
- Consider platform-specific timing
- Leave buffer time for engagement

---

## Step 6: Manage Scheduled Posts

### Edit a Scheduled Post

1. Find post in queue
2. Click **"Edit"**
3. Update:
   - Schedule time
   - Content
   - Platform settings
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

## Step 7: Handle Failed Posts

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

### Fix and Retry

If retry fails:

1. Click **"Edit"** on failed post
2. Review error message
3. Fix issue:
   - Reconnect account if auth expired
   - Edit content if policy violation
   - Shorten if over character limit
4. Save and retry

---

## Step 8: View Schedule Calendar

### Calendar View

Navigate to **Distribute > Calendar**:

```
┌─────────────────────────────────────────────────────┐
│ Content Calendar - April 2026                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Sun  Mon  Tue  Wed  Thu  Fri  Sat                 │
│       1    2    3    4    5    6                  │
│  7    8    9   10   11   12   13                  │
│ 14   15   16   17   18   19   20                  │
│      [🐦] [📄]                                     │
│                                                     │
│ 21   22   23   24   25   26   27                  │
│      [📧]                                         │
│                                                     │
│ 28   29   30                                       │
│                                                     │
│                                                     │
│ 🐦 = Twitter  📄 = LinkedIn  📧 = Newsletter      │
└─────────────────────────────────────────────────────┘
```

### Calendar Features

- **Month view** - See entire month
- **Week view** - Detailed weekly schedule
- **Day view** - Hour-by-hour breakdown
- **List view** - Sortable post list

### Calendar Actions

- Click date to schedule new post
- Drag post to reschedule
- Click post to edit
- Filter by platform

---

## Step 9: Monitor Queue Statistics

### Stats Dashboard

View key metrics:

```
┌─────────────────────────────────────────────────────┐
│ Publishing Statistics                                │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Total Posts: 156                                   │
│ ├─ Published: 142 (91%)                           │
│ ├─ Pending: 10                                     │
│ ├─ Failed: 3                                       │
│ └─ Cancelled: 1                                    │
│                                                     │
│ Success Rate: 97.9%                                │
│ Avg Time to Publish: 2.3 minutes                   │
│                                                     │
│ By Platform:                                       │
│ ├─ Twitter: 89 posts                               │
│ ├─ LinkedIn: 45 posts                              │
│ └─ Newsletter: 22 posts                            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Understanding Metrics

| Metric | Good Range |
|--------|------------|
| Success Rate | >95% |
| Failed Posts | <5% |
| Pending Time | <1 week |
| Platform Distribution | Balanced |

---

## Best Practices

### Scheduling Strategy

1. **Plan ahead** - Schedule 2-4 weeks in advance
2. **Maintain consistency** - Post at regular intervals
3. **Consider timing** - Post when audience is active
4. **Mix content types** - Variety keeps engagement
5. **Leave gaps** - Room for spontaneous content

### Content Calendar

**Weekly Template:**
```
Monday: Industry news/insights
Tuesday: Educational content
Wednesday: Behind-the-scenes
Thursday: User-generated content
Friday: Fun/casual content
Weekend: Minimal or none
```

### Platform-Specific Tips

**Twitter/X:**
- 3-5 tweets per day
- Space 2-3 hours apart
- Use threads for longer content

**LinkedIn:**
- 1 post per weekday
- Morning or evening works best
- Professional tone

**Instagram:**
- 1 post per day
- Stories can be more frequent
- Evening posts often perform better

---

## Troubleshooting

### Post Not Publishing

**Check:**
1. Account is connected
2. Authentication hasn't expired
3. Content meets platform requirements
4. Not rate limited

### Wrong Time Published

**Common Issues:**
- Wrong timezone selected
- Daylight saving time
- Timezone mismatch

**Fix:**
- Always set correct timezone
- Use platform's timezone
- Double-check schedule

### Bulk Schedule Error

**Causes:**
- Too many posts at once
- Invalid content selected
- Platform rate limits

**Fix:**
- Schedule in smaller batches
- Verify all content is valid
- Space posts further apart

---

## Summary

You now know how to:
- ✅ Schedule posts for future publication
- ✅ Use smart scheduling recommendations
- ✅ Bulk schedule multiple posts
- ✅ Manage the publishing queue
- ✅ Handle failed posts and retries
- ✅ View and use the content calendar

---

## Next Steps

Now that you can schedule posts:

1. **[Team Collaboration](06-team-collaboration.md)** - Work with your team
2. **[Analytics & Insights](07-analytics.md)** - Track scheduled post performance
3. **[Performance Alerts](../FEATURES_GUIDE.md#performance-alerts)** - Get notified of important events

---

**Questions?** Contact support@contentforge.ai
