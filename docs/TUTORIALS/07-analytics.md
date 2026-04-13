# Tutorial: Analytics & Insights

> Track, analyze, and optimize your content performance

---

## What You'll Learn

By the end of this tutorial, you will:
- Navigate the analytics dashboard
- Understand key performance metrics
- Export data for reporting
- Use insights to improve content
- Set up custom reports

**Time Required**: 20 minutes

---

## Prerequisites

Before starting:
- ContentForge account with published content
- Some content history (at least 1 week recommended)

---

## Step 1: Access Analytics

### Navigation

1. Click **"Analytics"** in main navigation
2. Or find **"Analytics"** widget on dashboard

### Analytics Overview

```
┌─────────────────────────────────────────────────────┐
│ Analytics Dashboard                                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 📊 Key Performance Indicators                       │
│ ├─ Total Content: 42                               │
│ ├─ Total Assets: 156                                 │
│ ├─ Published Posts: 78                             │
│ ├─ Success Rate: 87.6%                             │
│ └─ Growth (30d): +12 content, +45 assets           │
│                                                     │
│ 📈 Performance Charts                                │
│ ├─ Content created over time                       │
│ ├─ Assets by type                                  │
│ └─ Publishing success rate                         │
│                                                     │
│ 🎯 Recent Activity                                   │
│ ├─ Most recent content                             │
│ └─ Latest published posts                          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Step 2: Understand Key Metrics

### Dashboard KPIs

| Metric | Description | Good Range |
|--------|-------------|------------|
| **Total Content** | All content items created | Growing |
| **Total Assets** | Generated repurposed content | Growing |
| **Published Posts** | Successfully published | Growing |
| **Success Rate** | Published / Attempted | >90% |
| **Content Growth** | New content (30 days) | Consistent |
| **Asset Growth** | New assets (30 days) | Consistent |

### Content Metrics

**By Status:**
- Completed - Successfully imported
- Processing - Currently working
- Failed - Import/generation failed

**By Source:**
- URL - Web articles
- YouTube - Video transcripts
- Text - Direct input
- Upload - File uploads

**Time-Based:**
- Daily creation count
- Weekly trends
- Monthly summaries

### Asset Metrics

**By Type:**
| Type | Description |
|------|-------------|
| Thread | Twitter/X thread |
| Social Post | Single social media post |
| Newsletter | Email newsletter format |
| Video Script | Short-form video script |
| Blog | Blog post format |

**By Platform:**
- Distribution across Twitter, LinkedIn, etc.
- Performance per platform
- Platform success rates

### Distribution Metrics

**Status Distribution:**
```
Pending:     ████████ 10%
Scheduled:   ██████ 8%
Publishing:  ██ 2%
Published:   ████████████████████████ 78%
Failed:      ███ 2%
```

**Platform Performance:**
| Platform | Posts | Success Rate | Avg Time |
|----------|-------|--------------|----------|
| Twitter | 45 | 95% | 1.2 min |
| LinkedIn | 23 | 92% | 2.1 min |
| Instagram | 10 | 80% | 3.5 min |

---

## Step 3: View Detailed Analytics

### Content Analytics

**Access:** Analytics > Content

**Metrics Available:**
- Content count by status
- Creation timeline
- Word count distribution
- Source type breakdown
- Content age analysis

**Example Report:**
```
Content Analysis (Last 30 Days)

Created: 12
├─ From URLs: 5
├─ From YouTube: 3
└─ Direct text: 4

Status:
├─ Completed: 11 (92%)
└─ Failed: 1 (8%)

Average word count: 1,245
```

### Asset Analytics

**Access:** Analytics > Assets

**Metrics Available:**
- Assets by type
- Assets by platform
- Generation success rate
- Token usage
- Popular content sources

**Example Report:**
```
Asset Generation (Last 30 Days)

Generated: 45 assets
├─ Threads: 15
├─ LinkedIn Posts: 12
├─ Newsletters: 10
└─ Video Scripts: 8

Success Rate: 96%
Average tokens per asset: 850
```

### Distribution Analytics

**Access:** Analytics > Distributions

**Metrics Available:**
- Posts by platform
- Publishing success rate
- Time-to-publish
- Failed post reasons
- Platform engagement

**Example Report:**
```
Distribution Performance

Total Attempts: 80
├─ Successful: 78 (97.5%)
└─ Failed: 2 (2.5%)

By Platform:
├─ Twitter: 40 posts, 100% success
├─ LinkedIn: 25 posts, 96% success
└─ Instagram: 15 posts, 93% success

Average time to publish: 1.8 minutes
```

---

## Step 4: Usage Analytics

### Track Your Usage

**Access:** Analytics > Usage

**Available Views:**
- Daily usage counts
- Weekly summaries
- Monthly reports
- Feature utilization

### Usage Breakdown

```
Usage This Month

Content Generations: 8/10
├─ Used: 8
└─ Remaining: 2

Scheduled Posts: 3/5
├─ Used: 3
└─ Remaining: 2

RSS Feeds: 1/1 (Free) or 1/10 (Pro)

Resets on: May 1, 2026
```

### Feature Utilization

See which features you use most:

```
Feature Usage (Last 30 Days)

Most Used:
1. AI Content Editor: 25 uses
2. Scheduled Publishing: 8 uses
3. Content Import: 5 uses
4. RSS Import: 12 uses
5. Smart Editor: 20 uses
```

---

## Step 5: Export Data

### Export Formats

**Available Formats:**
- **CSV** - Spreadsheet compatible (Excel, Google Sheets)
- **JSON** - Structured data for developers

### What to Export

| Data Type | Use Case |
|-----------|----------|
| Content list | Backup, migration |
| Asset history | Reporting, analysis |
| Usage tracking | Billing verification |
| Activity log | Audit trail |

### Export Content

1. Go to **Analytics > Export**
2. Select data type:
   ```
   [x] Content
   [ ] Assets
   [ ] Distributions
   [ ] Usage
   ```

3. Set date range:
   ```
   From: 2026-03-01
   To: 2026-04-13
   ```

4. Choose format:
   ```
   Format: [x] CSV  [ ] JSON
   ```

5. Click **"Export"**

### CSV Export Example

```csv
ID,Title,Source Type,Word Count,Status,Created At
123,Blog Post Analysis,url,1247,completed,2026-04-01T10:00:00Z
124,Video Summary,youtube,2341,completed,2026-04-02T14:30:00Z
125,Meeting Notes,text,456,completed,2026-04-03T09:15:00Z
```

### JSON Export Example

```json
{
  "export_info": {
    "exported_at": "2026-04-13T10:00:00Z",
    "user_id": "user-uuid",
    "days_exported": 30
  },
  "content": [
    {
      "id": "content-uuid",
      "title": "Blog Post Analysis",
      "source_type": "url",
      "word_count": 1247,
      "status": "completed"
    }
  ],
  "summary": {
    "total_content": 42,
    "total_assets": 156
  }
}
```

---

## Step 6: Use Insights for Improvement

### Identify Trends

**Look For:**
- Content types that generate most assets
- Platforms with highest success rates
- Times when content performs best
- Topics that get most engagement

### Actionable Insights

**Example Analysis:**

```
Insight: Twitter threads have 40% higher 
engagement than single tweets.

Action: Generate more threads from blog content.

---

Insight: LinkedIn posts published at 8am 
get 2x more views.

Action: Schedule LinkedIn content for morning.

---

Insight: Video scripts have highest conversion 
to publishing (85%).

Action: Prioritize video content creation.
```

### Performance Comparison

Compare periods:

```
This Month vs Last Month

Content Created: +25% 📈
Assets Generated: +32% 📈
Published Posts: +18% 📈
Success Rate: +2% 📈
```

---

## Step 7: Advanced Analytics (Pro+)

### Custom Reports

Create custom analytics views:

1. Go to **Analytics > Custom Reports**
2. Click **"New Report"**
3. Configure metrics:

```
Report Name: Q2 Marketing Performance

Metrics to Include:
[x] Content created
[x] Assets generated
[x] Posts by platform
[x] Success rates
[x] Engagement metrics

Filters:
Project: Marketing Campaign
Date Range: Apr 1 - Jun 30
```

4. Save and schedule (optional)

### Scheduled Reports

Get regular reports via email:

```
Weekly Report Settings:

Frequency: Weekly (Monday)
Time: 9:00 AM
Recipients: team@company.com

Include:
[x] Content summary
[x] Publishing stats
[x] Performance highlights
[x] Week-over-week comparison
```

### Team Analytics (Organizations)

View team performance:

```
Team Performance - April 2026

Content by Member:
├─ Sarah: 15 pieces
├─ John: 12 pieces
└─ Mike: 8 pieces

Best Performing Content:
├─ "Product Launch" by Sarah
├─ "Industry Trends" by John
└─ "Customer Story" by Mike

Team Success Rate: 94%
```

---

## Step 8: Set Goals and Track Progress

### Define Content Goals

**Example Goals:**
- Publish 20 posts per month
- Maintain >95% success rate
- Generate 50 assets monthly
- Grow content library by 30%

### Track Progress

```
Monthly Goals Progress

🎯 Target: 20 published posts
✅ Current: 18 posts
📊 90% complete - On track

🎯 Target: 95% success rate
✅ Current: 97.5%
📊 Exceeding target

🎯 Target: 50 assets
✅ Current: 45 assets
📊 90% complete - On track
```

### Celebrate Milestones

```
🏆 Milestones Reached

100th Content Item: Apr 5, 2026
500th Asset Generated: Apr 10, 2026
50th Published Post: Apr 12, 2026
```

---

## Analytics Best Practices

### Regular Review

**Weekly:**
- Check publishing success rate
- Review failed posts
- Monitor usage limits

**Monthly:**
- Full analytics review
- Compare to previous month
- Identify trends
- Adjust strategy

**Quarterly:**
- Deep dive analysis
- Set new goals
- Plan content strategy

### Data-Driven Decisions

**Use analytics to:**
- Focus on high-performing content types
- Optimize publishing times
- Improve success rates
- Allocate resources effectively

### Sharing Insights

**Export for stakeholders:**
- Executive summaries
- Performance reports
- ROI calculations
- Trend analysis

---

## Troubleshooting

### Analytics Not Loading

**Solutions:**
1. Check internet connection
2. Refresh the page
3. Wait a moment and retry
4. Contact support if persists

### Data Seems Incorrect

**Check:**
- Correct date range selected
- Proper filters applied
- Data hasn't been deleted
- Account is correct

### Export Fails

**Common Issues:**
- Large date range (try smaller)
- Browser timeout (try again)
- Insufficient permissions

---

## Summary

You now know how to:
- ✅ Navigate the analytics dashboard
- ✅ Understand key performance metrics
- ✅ View detailed analytics by category
- ✅ Export data for reporting
- ✅ Use insights to improve content strategy
- ✅ Set and track content goals

---

## Next Steps

Now that you understand analytics:

1. **[Performance Alerts](../FEATURES_GUIDE.md#performance-alerts)** - Get notified of important events
2. **[Competitor Analysis](../FEATURES_GUIDE.md#competitor-analysis)** - Compare to competition
3. **[Trending Topics](../FEATURES_GUIDE.md#trending-topics)** - Create timely content

---

**Questions?** Contact support@contentforge.ai
