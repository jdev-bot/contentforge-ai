# Tutorial: Creating Your First Content

> Learn to import, extract, and repurpose content

---

## What You'll Learn

By the end of this tutorial, you will:
- Import content from different sources
- Extract text from URLs and YouTube videos
- Generate multiple content assets
- Check quality scores and sentiment analysis
- Manage version history for your content

**Time Required**: 20 minutes

---

## Prerequisites

Before starting:
- You have a ContentForge account
- You've created at least one project

Not done yet? Complete [Getting Started](01-getting-started.md) first.

---

## Step 1: Choose Your Content Source

ContentForge supports multiple source types:

| Source | Best For | Examples |
|--------|----------|----------|
| **URL** | Blog posts, articles | Company blog, news articles |
| **YouTube** | Video content | Tutorials, interviews, podcasts |
| **Text** | Direct input | Notes, documents, ideas |
| **Upload** | Audio/video files | Podcasts, webinars, recordings |

---

## Step 2: Import from URL

### Process

1. Navigate to **Content > New Content**
2. Select **"From URL"** as source type
3. Enter a URL:
   ```
   Example: https://yourblog.com/10-marketing-tips
   ```
4. Choose or create a project
5. Give your content a title:
   ```
   Title: 10 Marketing Tips Article
   ```
6. Click **"Import Content"**

### What Happens Next

The system will:
1. Fetch the webpage
2. Extract the main article text
3. Clean and format the content
4. Calculate word count
5. **Assign a quality score** — an AI-generated assessment of content readability, structure, and depth
6. **Run sentiment analysis** — detect tone (positive, neutral, negative) and emotional cues
7. Store in your project

**Time**: 10-30 seconds

### View Extracted Content

Once complete, you'll see:
```
✅ Content Imported Successfully

Title: 10 Marketing Tips Article
Source: URL
Word Count: 1,247
Quality Score: 82/100
Sentiment: Positive (0.73)
Status: Completed

Original Text:
[Full article text extracted and displayed]

Actions:
[💎 Generate Assets] [Edit] [View History] [Delete]
```

---

## Step 3: Import from YouTube

### Process

1. Navigate to **Content > New Content**
2. Select **"YouTube Video"**
3. Paste a YouTube URL:
   ```
   Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ
   ```
4. Choose a project
5. Add a title:
   ```
   Title: Marketing Strategy Video Analysis
   ```
6. Click **"Import Video"**

### Transcription

The system will:
1. Extract the video ID
2. Fetch transcript (if available)
3. Clean and format text
4. Remove timestamps (optional)
5. Assign quality score and sentiment

**Note**: Videos without captions/transcripts cannot be processed.

---

## Step 4: Enter Direct Text

### When to Use Direct Text

- Blog post drafts
- Meeting notes
- Brainstorming ideas
- Existing documents

### Process

1. Navigate to **Content > New Content**
2. Select **"Direct Text"**
3. Choose a project
4. Add a title
5. Paste or type your content
6. Click **"Save Content"**

---

## Step 5: Generate Content Assets

Once your content is imported, generate repurposed assets:

### Start Generation

1. Open your imported content
2. Click **"Generate Assets"**
3. Select asset types:
   - ☑️ Twitter/X Thread
   - ☑️ LinkedIn Posts
   - ☑️ Newsletter
   - ☑️ Video Script
4. Click **"Generate"**

### AI Processing

The AI will create each asset and assign a **quality score**:

**Twitter Thread (5-7 tweets):**
```
Tweet 1/7 💡 Marketing isn't magic—it's method.

Here are 10 proven strategies that helped 
our clients 3x their revenue:

👇👇👇

Tweet 2/7 1/ Focus on retention before acquisition...
[continues]

Quality Score: 78/100
Sentiment: Positive (enthusiastic)
```

**LinkedIn Post:**
```
I analyzed 100+ marketing campaigns and found 
10 strategies that consistently outperform...

[Professional, long-form content]

#Marketing #BusinessGrowth

Quality Score: 85/100
Sentiment: Professional (neutral-positive)
```

### Review and Edit

Each generated asset can be:
- ✅ **Accepted** - Save to assets
- ✍️ **Edited** - Modify in AI Editor
- 🗑️ **Deleted** - Remove if not useful
- 📤 **Scheduled** - Add to publishing queue
- 📊 **Quality Reviewed** - Check quality score details

---

## Step 6: View Quality Scores

Quality scores help you assess content effectiveness before publishing.

### Score Breakdown

| Score Range | Rating | Recommendation |
|-------------|--------|----------------|
| 90-100 | Excellent | Ready to publish |
| 75-89 | Good | Minor tweaks optional |
| 60-74 | Fair | Consider revisions |
| Below 60 | Needs Work | Significant edits recommended |

### What Quality Scores Measure

- **Readability** — Sentence length, vocabulary level, structure
- **Clarity** — Main message clarity, logical flow
- **Engagement** — Hook strength, call-to-action presence
- **SEO Potential** — Keyword usage, heading structure (for blog content)

### Sentiment Analysis

ContentForge also provides sentiment analysis for imported and generated content:

- **Positive** — Content that conveys enthusiasm, success, or optimism
- **Neutral** — Factual or informational content
- **Negative** — Content addressing problems or challenges
- **Mixed** — Content with varying emotional tones

Use sentiment to:
- Match tone to platform (LinkedIn: professional; Twitter: casual)
- Ensure brand voice consistency
- Avoid unintended negative messaging

---

## Step 7: Manage Version History

ContentForge tracks all changes to your content, so you never lose work.

### Access Version History

1. Open any content item
2. Click **"History"** tab
3. View all saved versions

```
┌─────────────────────────────────────────────────────┐
│ Version History                                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│ v3 (Current) • 2026-04-14 10:30 AM                │
│ Quality Score: 85 | Sentiment: Positive            │
│ [View] [Compare with v2]                           │
│                                                     │
│ v2 • 2026-04-14 09:15 AM                           │
│ Quality Score: 72 | Sentiment: Neutral             │
│ [View] [Restore] [Compare with v1]                 │
│                                                     │
│ v1 (Original) • 2026-04-13 04:00 PM                │
│ Quality Score: 80 | Sentiment: Positive            │
│ [View] [Restore]                                   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Version History Features

- **Compare** — View diff between two versions side by side
- **Restore** — Revert to a previous version
- **Track Quality** — See how quality scores change over edits
- **Audit Trail** — See who made changes and when (team accounts)

> **Tip**: Version history is automatically created whenever you save content, generate assets, or use the Smart Editor.

---

## Step 8: Manage Your Content

### Content List View

Navigate to **Content** to see all your items:

```
┌─────────────────────────────────────────────────────┐
│ All Content                              [+ New]  │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ▼ Project: All Projects | Status: All              │
│ ▼ Quality: All | Sentiment: All                     │
│                                                     │
│ □ 10 Marketing Tips Article                        │
│   URL • 1,247 words • 4 assets • Score: 82         │
│   [✍️ Edit] [💎 Assets] [📜 History] [🗑️ Delete] │
│                                                     │
│ □ Marketing Strategy Video                         │
│   YouTube • 2,341 words • 4 assets • Score: 78    │
│   [✍️ Edit] [💎 Assets] [📜 History] [🗑️ Delete] │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Filter by Quality and Sentiment

- Filter content by **quality score range** (e.g., show only content scoring 80+)
- Filter by **sentiment** (positive, neutral, negative)
- Combine filters with project, source type, and date

### Actions Available

| Action | Description |
|--------|-------------|
| View | See full content with quality score |
| Edit | Modify text |
| Assets | View generated assets |
| History | View version history |
| Generate | Create more assets |
| Schedule | Add to publishing queue |
| Delete | Move to trash |

---

## Step 9: Organize with Projects

### Assign Content to Projects

1. Select content with checkboxes
2. Click **"Move to Project"**
3. Choose destination project
4. Click **"Move"**

### Filter by Project

Use the project filter to:
- See project-specific content
- Compare across projects
- Generate project reports

---

## Tips for Best Results

### Source Content Tips

✅ **Good Sources:**
- Clear, well-structured articles
- 500+ words minimum
- Single topic focus
- Properly formatted HTML

❌ **Avoid:**
- Paywalled content
- Heavy image-based content
- Very short articles (<300 words)
- Multi-topic articles

### Generation Tips

1. **Review quality scores** — Higher scores tend to publish better
2. **Edit for your voice** — AI learns from your edits
3. **Check sentiment** — Ensure tone matches your platform
4. **Use version history** — Compare edits to see what works
5. **Add context** — Include industry specifics
6. **Use brand voice settings** — Configure in project

---

## Common Issues

### "Failed to extract content"

**Causes:**
- Website blocks scrapers
- Paywall/protected content
- JavaScript-heavy site
- Invalid URL

**Solutions:**
- Try direct text input
- Check URL is accessible
- Use "Import Text" for paywalled content
- Contact support with URL

### "Quality score seems low"

**Causes:**
- Content is too short (< 200 words)
- Poor structure or formatting
- Mixed topics without clear focus

**Solutions:**
- Expand content before generating
- Improve structure with headings
- Focus on a single topic

---

## Next Steps

Now you have content imported, try:

1. **[Using the Smart Editor](04-smart-editor.md)** - Refine your generated content with AI suggestions
2. **[Setting up RSS Feeds](03-rss-feeds.md)** - Automate content import
3. **[Scheduling Posts](05-scheduling-posts.md)** - Publish your assets

---

## Summary

You now know how to:
- ✅ Import content from URLs, YouTube, and text
- ✅ Generate multiple content assets with AI
- ✅ Review quality scores and sentiment analysis
- ✅ Track changes with version history
- ✅ Organize content in projects

**Questions?** Contact support@contentforge.ai