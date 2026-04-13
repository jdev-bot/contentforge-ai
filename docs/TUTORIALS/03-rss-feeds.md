# Tutorial: Setting Up RSS Feeds

> Automatically import content from RSS feeds

---

## What You'll Learn

By the end of this tutorial, you will:
- Add RSS feeds to monitor
- Configure auto-import settings
- Manage imported entries
- Create content from RSS items

**Time Required**: 15 minutes

---

## Prerequisites

Before starting:
- ContentForge account (Free plan supports 1 feed, Pro supports 10)
- URLs of RSS feeds you want to monitor

---

## What is RSS?

RSS (Really Simple Syndication) is a way to automatically receive updates from websites. When a blog publishes a new post, the RSS feed is updated, and ContentForge can automatically import it.

### Common Sources with RSS

| Source | Typical Feed URL |
|--------|------------------|
| WordPress | `https://blog.com/feed/` |
| Medium | `https://medium.com/feed/@username` |
| Substack | `https://newsletter.substack.com/feed` |
| YouTube | `https://www.youtube.com/feeds/videos.xml?channel_id=...` |
| News Sites | Usually `/feed/` or `/rss/` |

---

## Step 1: Find RSS Feed URLs

### For Blogs/Websites

1. Look for the RSS icon (◎) in the website header/footer
2. Check `/feed/` or `/rss/` after the domain
3. Search the page source for "rss" or "feed"

### For YouTube Channels

1. Go to the YouTube channel
2. View page source (Ctrl+U / Cmd+Option+U)
3. Search for "channelId"
4. Build URL:
   ```
   https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID_HERE
   ```

### Validation Tools

Test RSS URLs with:
- [RSS Validator](https://validator.w3.org/feed/)
- Browser feed preview
- curl command: `curl -I https://site.com/feed/`

---

## Step 2: Add Your First RSS Feed

### Navigate to RSS Section

1. Click **"Content"** in navigation
2. Select **"RSS Feeds"** tab
3. Click **"+ Add RSS Feed"**

### Configure Feed

**Required Fields:**

```
Feed Name: TechCrunch News
Feed URL: https://techcrunch.com/feed/
Fetch Frequency: hourly
Auto-create content: [ ] (we'll enable later)
```

**Feed Name Tips:**
- Use descriptive names
- Include source name
- Add category if needed

Example good names:
- "TechCrunch AI News"
- "Company Blog"
- "Industry Updates - Marketing"

### Frequency Options

| Frequency | Best For | Data Usage |
|-----------|----------|------------|
| Hourly | Active blogs, news sites | Higher |
| Daily | Weekly blogs, newsletters | Lower |

### Save Feed

Click **"Add Feed"** - the system will:
1. Validate the RSS URL
2. Test connection
3. Perform initial fetch
4. Save to your account

---

## Step 3: Initial Fetch

### What Happens

After adding a feed:
1. Feed entries are fetched
2. Last 10-20 items imported
3. Marked as "unprocessed"
4. Available for manual import

### View Entries

Navigate to **Content > RSS Entries** to see:

```
┌─────────────────────────────────────────────────────┐
│ RSS Entries                               [Filter]  │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Feed: All Feeds | Status: Unprocessed              │
│                                                     │
│ □ OpenAI Announces GPT-5 Development               │
│   From: TechCrunch News • 2 hours ago              │
│   [Import] [View] [Mark Processed]               │
│                                                     │
│ □ New AI Startup Raises $50M                       │
│   From: TechCrunch News • 5 hours ago              │
│   [Import] [View] [Mark Processed]               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Step 4: Import RSS Entries

### Manual Import

Import entries one by one:

1. Review entry title and preview
2. Click **"Import"**
3. Choose target project
4. Click **"Import as Content"**

**What Happens:**
- Content item created
- Entry marked as "processed"
- Original link preserved
- Ready for asset generation

### Bulk Import

Import all unprocessed entries:

1. Select feed from dropdown
2. Click **"Import All"**
3. Choose project
4. Confirm import

⚠️ **Warning**: This creates content items for ALL unprocessed entries.

### Auto-Import (Optional)

Enable automatic content creation:

1. Go to **RSS Feeds**
2. Find your feed
3. Click **"Edit"**
4. Toggle **"Auto-create content"**
5. Select default project
6. Save

**How It Works:**
- New entries automatically imported
- Created in specified project
- Marked as "processed"
- Ready for asset generation

**Recommended For:**
- Trusted sources
- High-quality content only
- Regular monitoring

**Not Recommended For:**
- High-volume feeds
- Mixed quality sources
- Automated workflows

---

## Step 5: Manage Your Feeds

### Feed Health

Check feed status in the feeds list:

| Status | Meaning | Action |
|--------|---------|--------|
| Active | Working normally | None |
| Paused | Manually paused | Resume if needed |
| Error | Fetch failed | Check URL, retry |

### Common Errors

**"Invalid RSS feed"**
- URL is not a valid RSS feed
- Site blocks scrapers
- Feed moved or deleted

**"Fetch failed"**
- Site is down
- Rate limited
- Authentication required

### Edit Feed Settings

1. Click **"Edit"** on a feed
2. Update:
   - Name
   - Frequency
   - Auto-import setting
   - Status
3. Save changes

### Pause a Feed

Temporarily stop fetching:

1. Edit feed
2. Change status to **"Paused"**
3. Save

To resume, change back to **"Active"**.

---

## Step 6: Organize Imported Content

### Entry States

| State | Meaning |
|-------|---------|
| Unprocessed | Not yet imported as content |
| Processed | Already imported |
| Imported | Has associated content item |

### Filter Entries

Filter by:
- Feed source
- Processed status
- Date range
- Search terms

### Bulk Actions

Select multiple entries:
- Import selected
- Mark as processed
- Delete entries

---

## Step 7: Advanced Settings

### Duplicate Detection

ContentForge automatically:
- Detects duplicate entries
- Prevents double imports
- Updates existing if changed

### Content Attribution

Imported content preserves:
- Original URL
- Publication date
- Source feed name
- Author (if available)

### Notification Settings

Configure alerts:
- New entries available
- Import failures
- Feed errors

---

## RSS Feed Best Practices

### Source Selection

✅ **Good Sources:**
- Industry blogs you trust
- Competitor public blogs
- Thought leaders in your space
- News sites relevant to your niche

❌ **Avoid:**
- Spam feeds
- Duplicate content farms
- Unreliable sources
- Off-topic content

### Frequency Guidelines

| Source Type | Recommended Frequency |
|-------------|----------------------|
| Breaking news | Hourly |
| Industry blogs | Daily |
| Weekly newsletters | Daily |
| Monthly publications | Daily |

### Quantity Management

**Free Plan:**
- 1 RSS feed maximum
- Choose your most important source

**Pro Plan:**
- 10 RSS feeds
- Mix of high and low frequency

**Enterprise:**
- Unlimited feeds
- Organize by category

---

## Use Cases

### Competitive Monitoring

Track competitor blogs:
- Know when they publish
- Analyze their content strategy
- Identify trending topics
- Find content gaps

**Setup:**
1. Add competitor blog RSS
2. Daily fetch frequency
3. Manual import review
4. Tag competitive analysis

### Content Curation

Build a content library:
- Track industry news
- Aggregate thought leadership
- Create weekly roundups
- Stay informed

**Setup:**
1. Add industry news feeds
2. Hourly or daily frequency
3. Auto-import to "News" project
4. Generate weekly summaries

### Research

Gather reference material:
- Track research publications
- Monitor academic blogs
- Collect case studies
- Build knowledge base

---

## Troubleshooting

### Feed Not Updating

**Check:**
1. Feed URL is correct
2. Feed is still active
3. Website hasn't changed format
4. Not blocked by rate limiting

**Fix:**
1. Re-add feed with updated URL
2. Try different frequency
3. Contact site owner

### Import Creates Bad Content

**Cause:** Poor quality RSS entries

**Fix:**
1. Disable auto-import
2. Manually review before importing
3. Consider different source

### Duplicate Imports

**Prevention:**
- System automatically detects duplicates
- Check before bulk import
- Review processed entries list

---

## Summary

You now know how to:
- ✅ Find and validate RSS feed URLs
- ✅ Add feeds to ContentForge
- ✅ Configure auto-import settings
- ✅ Import entries as content
- ✅ Manage feed health and errors

---

## Next Steps

Now that you have RSS set up:

1. **[Using the Smart Editor](04-smart-editor.md)** - Edit imported content
2. **[Scheduling Posts](05-scheduling-posts.md)** - Publish imported content
3. **[Analytics & Insights](07-analytics.md)** - Track RSS content performance

---

**Questions?** Contact support@contentforge.ai
