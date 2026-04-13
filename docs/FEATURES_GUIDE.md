# ContentForge AI - Features Guide

> Complete guide to all platform features

---

## Table of Contents

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

---

## Smart Content Editor

The Smart Content Editor is an AI-powered tool that helps you transform and optimize your content for different purposes and platforms.

### Overview

The editor uses advanced AI (Llama 3.3 70B via Groq) to rewrite, expand, condense, and optimize your content while maintaining your core message.

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

#### Expand
Add depth and detail to short content.

**Options:**
- Target expansion (2x to 5x)
- Focus on specific areas
- Add examples and case studies
- Include statistics and data

#### Condense
Shorten content while preserving key points.

**Options:**
- Target percentage (20-80%)
- Preserve key points
- Generate executive summaries
- Create TL;DR versions

#### Optimize
Tailor content for specific platforms.

**Platforms:**
| Platform | Characteristics |
|----------|-----------------|
| Twitter/X | 280 chars, punchy, threads |
| LinkedIn | Professional, longer-form |
| Blog | SEO-optimized, structured |
| Newsletter | Personal, conversational |
| Instagram | Engaging captions, hashtags |
| TikTok | Trendy, authentic, hook-focused |

### Usage Tips

1. **Start with your best content** - The editor works best with solid source material
2. **Experiment with combinations** - Try different tone + style pairs
3. **Use platform optimization** - Always optimize before publishing
4. **Save iterations** - Compare different versions
5. **Review AI output** - Always review and refine AI suggestions

---

## Scheduled Publishing

Schedule your content to be published automatically at the optimal time.

### Overview

The scheduler lets you queue content for future publication across multiple platforms, with smart timing recommendations and bulk scheduling capabilities.

### Features

#### Single Post Scheduling

Schedule individual posts with precise timing.

**Options:**
- Set exact date and time
- Choose timezone
- Select platform
- Configure platform-specific settings

#### Bulk Scheduling

Schedule multiple posts at once with intervals.

**Use Cases:**
- Weekly content calendars
- Campaign rollouts
- Series publishing
- A/B testing schedules

**Configuration:**
```
Content IDs: [id1, id2, id3, ...]
Platform: twitter
Start Time: 2026-04-14T09:00:00Z
Interval: 60 minutes
```

#### Smart Scheduling

Get AI-recommended best posting times.

**Factors Considered:**
- Platform-specific peak hours
- Your historical engagement data
- Industry benchmarks
- Timezone of target audience

**Default Best Times:**
| Platform | Recommended Times |
|----------|-------------------|
| Twitter | 9:00 AM, 12:00 PM, 3:00 PM, 6:00 PM |
| LinkedIn | 8:00 AM, 12:00 PM, 5:00 PM |
| Facebook | 9:00 AM, 1:00 PM, 3:00 PM |
| Instagram | 11:00 AM, 2:00 PM, 7:00 PM |
| TikTok | 7:00 AM, 12:00 PM, 7:00 PM, 9:00 PM |

#### Publishing Queue

Monitor and manage your scheduled content.

**Actions:**
- View upcoming posts
- Edit scheduled times
- Cancel scheduled posts
- Publish immediately
- Retry failed posts
- Track queue statistics

### Queue Statuses

| Status | Description |
|--------|-------------|
| Pending | Waiting for scheduled time |
| Scheduled | Time set, ready to publish |
| Processing | Currently publishing |
| Published | Successfully published |
| Failed | Publish failed, can retry |
| Cancelled | Manually cancelled |

### Best Practices

1. **Schedule in advance** - Plan your content calendar weekly
2. **Use timezone awareness** - Consider your audience's timezone
3. **Space out posts** - Avoid overwhelming your audience
4. **Monitor queue health** - Check for failed posts regularly
5. **Test with one post first** - Verify platform connections

---

## RSS Import

Automatically import content from RSS feeds and convert it into ContentForge projects.

### Overview

Monitor RSS feeds from blogs, news sites, and publications. New entries are automatically fetched and can be imported as content items for repurposing.

### Features

#### Feed Management

**Add RSS Feeds:**
- Any valid RSS/Atom feed URL
- Set fetch frequency (hourly/daily)
- Enable auto-import
- Organize with custom names

**Supported Sources:**
- WordPress blogs
- Medium publications
- Substack newsletters
- News sites (TechCrunch, etc.)
- YouTube channels (via RSS)
- Any RSS/Atom feed

#### Auto-Import

Automatically create content items from new RSS entries.

**Configuration:**
```
Feed: TechCrunch
Auto-create content: Enabled
Project: Industry News
Status: Active
```

#### Manual Import

Selectively import RSS entries.

**Options:**
- Import individual entries
- Bulk import all unprocessed
- Preview before importing
- Assign to specific projects

#### Entry Management

Track and manage imported entries.

**Filters:**
- Processed vs unprocessed
- By feed
- By date range
- By content status

### Use Cases

1. **Industry Monitoring** - Track competitor blogs and news
2. **Content Curation** - Aggregate relevant articles for repurposing
3. **News Roundups** - Create weekly newsletter content
4. **Research** - Build content libraries from thought leaders
5. **Trend Tracking** - Monitor trending topics in your niche

### Best Practices

1. **Validate feeds before adding** - Ensure RSS URL is correct
2. **Set appropriate frequency** - Hourly for active sources, daily for others
3. **Organize by project** - Import into relevant projects
4. **Review before publishing** - Always edit AI-generated content
5. **Monitor feed health** - Check for errors in feed fetching

---

## Content Freshness

Monitor and score your content's freshness to identify what needs updating.

### Overview

The Freshness system automatically scores your content based on age, engagement, and relevance factors to help you maintain a current and effective content library.

### Scoring System

**Freshness Score: 0-100**

| Score | Status | Action Required |
|-------|--------|-----------------|
| 80-100 | Fresh | Recently created, no action needed |
| 60-79 | Good | Still relevant, monitor for trends |
| 40-59 | Aging | Consider updating soon |
| 20-39 | Stale | Needs refresh or major update |
| 0-19 | Outdated | Requires significant revision |

### Scoring Factors

Content freshness is calculated based on:

#### Age Factor (0-30 points)
- Recently published: 25-30 points
- 1-3 months old: 15-25 points
- 3-6 months old: 5-15 points
- 6+ months old: 0-5 points

#### Engagement Factor (0-35 points)
- High engagement: 30-35 points
- Moderate engagement: 15-30 points
- Low engagement: 0-15 points

#### Trend Factor (0-35 points)
- Trending topic: 30-35 points
- Stable topic: 15-30 points
- Declining topic: 0-15 points

### Features

#### Individual Analysis

Analyze specific content freshness on-demand.

**Output:**
- Freshness score
- Age in days
- Status label
- Factor breakdown
- Specific recommendations

#### Bulk Analysis

Analyze all your content at once.

**Results:**
- Scores for all content
- Summary statistics
- Content needing attention
- Average freshness metrics

#### Stale Content Report

View content below a freshness threshold.

**Configuration:**
- Set threshold (default: 50)
- Sort by score or age
- Paginate results
- Export reports

#### Dashboard

Comprehensive freshness overview.

**Metrics:**
- Total content count
- Analyzed vs pending
- Average freshness score
- Distribution by status
- Content needing refresh
- Recommendations summary

### Recommendations

The system provides specific recommendations:

| Recommendation | When Shown |
|----------------|------------|
| Update statistics | Content > 3 months with data |
| Refresh trending hashtags | Social content > 1 month |
| Review for accuracy | Technical content > 6 months |
| Optimize for current trends | Score < 60 |
| Archive or repurpose | Score < 20 |

### Best Practices

1. **Analyze regularly** - Run bulk analysis monthly
2. **Prioritize updates** - Focus on content with score < 50
3. **Update in batches** - Schedule content refresh sprints
4. **Track improvements** - Re-analyze after updates
5. **Set reminders** - Create calendar reminders for stale content

---

## Trending Topics

Discover and leverage trending topics to create timely, relevant content.

### Overview

The Trends system monitors current events, social media, and industry news to identify trending topics that are relevant to your niche and audience.

### Features

#### Trend Discovery

**Sources:**
- Twitter/X trending topics
- Google Trends
- Industry news aggregators
- Reddit discussions
- News APIs

**Metrics:**
- Trend score (0-100)
- Mention velocity (mentions/hour)
- Category classification
- Related keywords
- Sample content

#### Category Organization

Trends are organized by category:

| Category | Description |
|----------|-------------|
| Technology | Tech news, product launches, innovations |
| Business | Markets, startups, corporate news |
| Entertainment | Movies, music, celebrity news |
| Sports | Games, athletes, championships |
| Politics | Elections, policy, government |
| Health | Medical news, wellness trends |
| Science | Research, discoveries, space |
| General | Uncategorized trending topics |

#### Relevance Matching

Find trends relevant to your content history.

**How It Works:**
1. Analyzes your existing content
2. Extracts key topics and themes
3. Matches against current trends
4. Ranks by relevance score

**Output:**
- Relevant trends
- Relevance score (0-1)
- Suggested content angles
- Platform recommendations

#### Trend Tracking

Track specific topics over time.

**Features:**
- Save topics of interest
- Get notifications on tracked trends
- View trend velocity changes
- Compare against competitors

#### Content Generation

Generate content based on trends.

**Outputs:**
- Headline suggestions
- Draft content
- Multiple angle options
- Recommended hashtags
- Call-to-action ideas

### Velocity Leaderboard

See the fastest-growing trends:

**Velocity Calculation:**
```
Velocity = (Current Mentions - Previous Mentions) / Time Interval
```

**Use Cases:**
- Catch trends early
- Identify viral opportunities
- Compare growth rates
- Plan timely content

### Trend Insights

Aggregate statistics about current trends:

- Total active trends
- Top category
- Average velocity
- Highest velocity topic
- Category distribution

### Best Practices

1. **Check trends daily** - Timing is critical for trend content
2. **Act quickly** - Trends have short lifespans
3. **Add unique value** - Don't just repeat the trend
4. **Match your brand** - Only pursue relevant trends
5. **Track performance** - Measure trend content success

---

## Growth Analytics

Track your content performance and growth over time.

### Overview

Comprehensive analytics to understand how your content performs, identify growth opportunities, and make data-driven decisions.

### Dashboard KPIs

**Key Metrics:**
| Metric | Description |
|--------|-------------|
| Total Content | All content items created |
| Total Assets | Generated repurposed assets |
| Total Distributions | Scheduled/published posts |
| Published | Successfully published |
| Content Growth (30d) | New content in last 30 days |
| Asset Growth (30d) | New assets in last 30 days |
| Success Rate | Published / Total attempts |

### Content Analytics

**Breakdown by:**
- Status (completed, processing, failed)
- Source type (URL, YouTube, text)
- Creation date
- Word count distribution

**Time-Based Metrics:**
- Daily creation counts
- Weekly trends
- Monthly summaries
- Growth rates

### Asset Analytics

**By Type:**
- Twitter/X threads
- LinkedIn posts
- Newsletters
- Video scripts
- Social posts

**By Platform:**
- Platform distribution
- Performance by platform
- Asset utilization

### Distribution Analytics

**Status Tracking:**
| Status | Meaning |
|--------|---------|
| Pending | Waiting to publish |
| Scheduled | Time set |
| Publishing | In progress |
| Published | Successfully posted |
| Failed | Error occurred |
| Cancelled | User cancelled |

**Platform Performance:**
- Posts per platform
- Success rate by platform
- Average engagement
- Time-to-publish

### Usage Analytics

**Track:**
- Daily/weekly/monthly usage
- Feature utilization
- Token consumption
- API calls
- Export history

### Export Features

**Export Formats:**
- CSV - Spreadsheet compatible
- JSON - Structured data

**Export Data:**
- Content history
- Asset generation
- Usage tracking
- Custom date ranges

### Best Practices

1. **Review weekly** - Check analytics dashboard regularly
2. **Set benchmarks** - Establish baseline metrics
3. **Identify patterns** - Look for high-performing content types
4. **Export monthly** - Keep records for reporting
5. **Act on insights** - Use data to guide content strategy

---

## Performance Alerts

Get notified when your content achieves milestones or needs attention.

### Overview

Automated alert system that monitors your content performance and notifies you of important events, viral moments, or issues requiring action.

### Alert Types

#### Viral Alerts

Triggered when content exceeds engagement thresholds.

**Triggers:**
- Views exceed threshold
- Shares spike
- Engagement rate jumps
- Trending on platform

**Response Actions:**
- Amplify with additional posts
- Monitor comments
- Capitalize on momentum
- Document learnings

#### Declining Alerts

Notify when content engagement drops.

**Triggers:**
- Engagement rate drops below threshold
- Views declining over time
- Negative sentiment detected
- Performance vs benchmark

**Response Actions:**
- Refresh content
- Adjust promotion
- Analyze cause
- Test alternatives

#### Milestone Alerts

Celebrate achievement milestones.

**Triggers:**
- Follower milestones (1K, 10K, etc.)
- View milestones (100K, 1M, etc.)
- Post count milestones
- Engagement rate goals

**Actions:**
- Thank audience
- Share achievement
- Analyze growth drivers
- Set next milestone

#### Error Alerts

Notify of publishing failures.

**Triggers:**
- Failed distribution
- API errors
- Authentication issues
- Rate limiting

**Actions:**
- Retry publishing
- Check connections
- Update credentials
- Contact support

### Alert Rules

Create custom alert conditions:

**Components:**
- **Name** - Rule identifier
- **Type** - Viral, declining, milestone, error
- **Metric** - Views, engagement, clicks, etc.
- **Operator** - Greater than, less than, equals
- **Threshold** - Trigger value
- **Channels** - In-app, email, Slack

**Example Rules:**
```
Rule 1: Viral Content
- Type: viral
- Metric: views
- Operator: greater_than
- Threshold: 10000
- Channels: [in_app, email]

Rule 2: Low Engagement
- Type: declining
- Metric: engagement
- Operator: less_than
- Threshold: 2.0
- Channels: [in_app]
```

### Notification Channels

| Channel | Description | Setup |
|---------|-------------|-------|
| In-App | Dashboard notifications | Automatic |
| Email | Email alerts | Verified email required |
| Slack | Slack messages | Webhook configuration |

### Managing Alerts

**Actions:**
- Acknowledge - Mark as seen
- Resolve - Mark as complete
- Snooze - Temporarily hide
- Delete - Remove permanently

### Best Practices

1. **Set realistic thresholds** - Avoid alert fatigue
2. **Prioritize channels** - Critical alerts to email
3. **Act quickly** - Viral moments are time-sensitive
4. **Review weekly** - Analyze alert patterns
5. **Update rules** - Adjust thresholds based on growth

---

## Content Calendar

Visualize and plan your content schedule.

### Overview

The Content Calendar provides a visual interface for planning, scheduling, and managing your content across time. See what's publishing when, identify gaps, and plan campaigns.

### Views

#### Monthly View

See the full month at a glance.

**Features:**
- All scheduled content
- Draft vs scheduled indicators
- Platform color coding
- Quick add new content

#### Weekly View

Detailed week view for planning.

**Features:**
- Time slots
- Platform breakdown
- Content status
- Drag-and-drop rescheduling

#### List View

Sortable list of all scheduled content.

**Features:**
- Filter by platform
- Sort by date
- Search content
- Bulk actions

### Calendar Features

#### Content Scheduling

- Click any date to schedule
- Set specific times
- Recurring schedules
- Bulk scheduling

#### Visual Indicators

| Indicator | Meaning |
|-----------|---------|
| Green dot | Successfully published |
| Yellow dot | Scheduled/pending |
| Red dot | Failed/cancelled |
| Gray dot | Draft/not scheduled |

#### Filtering

- By platform
- By project
- By content type
- By status

#### Export

- PDF calendar
- ICS calendar files
- CSV schedule
- Share view links

### Best Practices

1. **Plan ahead** - Schedule content 2-4 weeks in advance
2. **Maintain consistency** - Regular posting schedule
3. **Leave buffer time** - Don't over-schedule
4. **Cross-reference** - Sync with company events/holidays
5. **Review weekly** - Adjust schedule based on performance

---

## Competitor Analysis

Track and analyze your competitors' content strategies.

### Overview

Monitor competitor content, identify gaps in your strategy, and benchmark your performance against industry leaders.

### Features

#### Competitor Tracking

**Add Competitors:**
- Twitter/X handles
- LinkedIn profiles
- Instagram accounts
- YouTube channels
- Blogs and newsletters
- TikTok accounts

**Tracked Data:**
- Follower counts
- Post frequency
- Engagement rates
- Content types
- Publishing times

#### Content Analysis

**Metrics Tracked:**
| Metric | Description |
|--------|-------------|
| Content Volume | Posts per month |
| Engagement Rate | Likes + comments / followers |
| Best Performing | Top posts by engagement |
| Post Timing | When they post |
| Content Mix | Types of content shared |

**Sentiment Analysis:**
- Positive/negative/neutral
- Emotional tone
- Common themes

#### Performance Insights

**Aggregated Metrics:**
- Average engagement per platform
- Posting frequency comparison
- Content type performance
- Growth trends

**Recommendations:**
- Opportunities identified
- Best practices observed
- Areas to differentiate
- Content gaps to fill

#### Content Gap Analysis

Identify topics competitors cover that you don't.

**Process:**
1. Analyze competitor topics
2. Compare to your content
3. Identify missing topics
4. Score opportunity (0-100)
5. Suggest content ideas

**Output:**
- Gap topics
- Opportunity score
- Competitor coverage count
- Your coverage count
- Suggested content angles

#### Topic Overlap

Compare topic coverage between you and competitors.

**Analysis:**
- Shared topics
- Your unique topics
- Competitor-only topics
- Overlap percentage

**Strategic Insights:**
- Differentiation opportunities
- Market coverage gaps
- Collaboration potential
- Content positioning

#### Benchmark Comparison

Compare your metrics to competitor averages.

**Metrics Compared:**
- Follower growth rate
- Engagement rate
- Post frequency
- Content diversity
- Response time

**Percentile Ranking:**
- How you rank vs competitors
- Industry benchmarks
- Improvement areas
- Competitive advantages

### Supported Platforms

| Platform | Data Available |
|----------|----------------|
| Twitter/X | Followers, tweets, engagement |
| LinkedIn | Followers, posts, engagement |
| Instagram | Followers, posts, engagement |
| YouTube | Subscribers, videos, views |
| TikTok | Followers, videos, engagement |
| Facebook | Followers, posts, engagement |
| Blog | Posts, frequency, topics |
| Newsletter | Issues, subscribers (if public) |

### Best Practices

1. **Track 3-5 key competitors** - Quality over quantity
2. **Review weekly** - Stay current with competitor moves
3. **Don't copy** - Learn from competitors, differentiate
4. **Focus on gaps** - Find underserved topics
5. **Set benchmarks** - Track your improvement vs competition

### Privacy & Ethics

- Only track publicly available data
- Respect terms of service
- Don't scrape private data
- Use insights ethically
- Focus on learning, not copying

---

## Third-Party Integrations

Connect ContentForge with your favorite tools and platforms.

### Overview

Integrate with Zapier, webhooks, WordPress, and more to create seamless workflows between ContentForge and your existing tool stack.

### Available Integrations

#### Zapier

Connect with 5,000+ apps via Zapier.

**Triggers:**
- Content created
- Assets generated
- Distribution published
- Alert triggered

**Actions:**
- Create content
- Generate assets
- Schedule distribution
- Send notification

**Popular Zaps:**
- RSS → ContentForge → Twitter
- ContentForge → Google Sheets
- Slack → ContentForge
- ContentForge → Mailchimp

#### Webhooks

Generic webhook integration for custom connections.

**Outgoing Webhooks:**
- Content created events
- Asset generated events
- Distribution events
- Alert events

**Incoming Webhooks:**
- Trigger content creation
- Import external content
- Update content status
- Manual automation triggers

**Configuration:**
- Webhook URL
- HTTP method (POST, PUT, etc.)
- Custom headers
- Payload templates
- Secret/signature verification

#### WordPress

Publish directly to WordPress sites.

**Features:**
- Create posts
- Update existing posts
- Upload media
- Set categories/tags
- Schedule publishing

**Configuration:**
- Site URL
- Application password
- Default author
- Default category
- Post status (draft/publish)

### Integration Management

#### Connection Testing

Test integrations before activating.

**Test Types:**
- Connection test
- Authentication test
- Sample event test
- Error handling test

#### Delivery Tracking

Monitor webhook deliveries.

**Status Tracking:**
- Pending
- Delivered
- Failed
- Retrying

**Retry Logic:**
- Automatic retry (3 attempts)
- Exponential backoff
- Manual retry option
- Error logging

#### Security

**Webhook Security:**
- Signature verification (HMAC-SHA256)
- IP allowlisting
- Secret tokens
- HTTPS required

**Data Privacy:**
- No credential storage in plain text
- Encrypted configuration
- Audit logging
- Access controls

### Building Custom Integrations

**Using Incoming Webhooks:**
```
POST /webhooks/incoming/{token}
Content-Type: application/json

{
  "event_type": "content.import",
  "data": {
    "title": "Imported Article",
    "content": "Article content...",
    "source_url": "https://example.com"
  }
}
```

**Event Types:**
- `content.created` - New content created
- `assets.generated` - Assets generated
- `distribution.published` - Content published
- `alert.triggered` - Alert fired
- `user.action` - User performed action

### Best Practices

1. **Test in development** - Use staging environment first
2. **Handle failures gracefully** - Implement retry logic
3. **Monitor delivery rates** - Check for failed deliveries
4. **Secure your webhooks** - Always verify signatures
5. **Document integrations** - Keep integration documentation updated

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
- **Community**: https://community.contentforge.ai
- **Email**: support@contentforge.ai
