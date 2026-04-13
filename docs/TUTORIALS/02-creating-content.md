# Tutorial: Creating Your First Content

> Learn to import, extract, and repurpose content

---

## What You'll Learn

By the end of this tutorial, you will:
- Import content from different sources
- Extract text from URLs and YouTube videos
- Generate multiple content assets
- Understand the content workflow

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
5. Store in your project

**Time**: 10-30 seconds

### View Extracted Content

Once complete, you'll see:
```
✅ Content Imported Successfully

Title: 10 Marketing Tips Article
Source: URL
Word Count: 1,247
Status: Completed

Original Text:
[Full article text extracted and displayed]

Actions:
[💎 Generate Assets] [Edit] [Delete]
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
   Or short URL:
   ```
   Example: https://youtu.be/dQw4w9WgXcQ
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

**Note**: Videos without captions/transcripts cannot be processed.

### Supported Video Types

✅ **Works Well:**
- Videos with captions/subtitles
- Podcast videos
- Tutorial videos
- Interview videos

❌ **Doesn't Work:**
- Private videos
- Videos without captions
- Age-restricted videos
- Region-blocked videos

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
5. Paste or type your content:
   ```
   Our company helps small businesses grow through 
   digital marketing. We offer SEO, social media 
   management, and content creation services...
   ```
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

The AI will create:

**Twitter Thread (5-7 tweets):**
```
Tweet 1/7 💡 Marketing isn't magic—it's method.

Here are 10 proven strategies that helped 
our clients 3x their revenue:

👇👇👇

Tweet 2/7 1/ Focus on retention before acquisition...
[continues]
```

**LinkedIn Post:**
```
I analyzed 100+ marketing campaigns and found 
10 strategies that consistently outperform...

[Professional, long-form content]

#Marketing #BusinessGrowth
```

**Newsletter:**
```
Subject: 10 Marketing Strategies That Actually Work

Hi [Name],

This week I'm sharing the exact strategies...

[Full newsletter format]
```

**Video Script:**
```
[0:00-0:15] Hook: "What if I told you 90% of 
businesses are making the same marketing mistake?"

[0:15-0:30] Problem statement...

[Full script with timestamps]
```

### Review and Edit

Each generated asset can be:
- ✅ **Accepted** - Save to assets
- ✍️ **Edited** - Modify in AI Editor
- 🗑️ **Deleted** - Remove if not useful
- 📤 **Scheduled** - Add to publishing queue

---

## Step 6: Manage Your Content

### Content List View

Navigate to **Content** to see all your items:

```
┌─────────────────────────────────────────────────────┐
│ All Content                              [+ New]  │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ▼ Project: All Projects | Status: All             │
│                                                     │
│ □ 10 Marketing Tips Article                      │
│   URL • 1,247 words • 4 assets • Completed        │
│   [✍️ Edit] [💎 Assets] [🗑️ Delete]            │
│                                                     │
│ □ Marketing Strategy Video                         │
│   YouTube • 2,341 words • 4 assets • Completed   │
│   [✍️ Edit] [💎 Assets] [🗑️ Delete]            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Actions Available

| Action | Description |
|--------|-------------|
| View | See full content |
| Edit | Modify text |
| Assets | View generated assets |
| Generate | Create more assets |
| Schedule | Add to publishing queue |
| Delete | Move to trash |

---

## Step 7: Organize with Projects

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

1. **Review before scheduling** - Always check AI output
2. **Edit for your voice** - AI learns from your edits
3. **Add context** - Include industry specifics
4. **Use brand voice settings** - Configure in project
5. **Generate multiple versions** - Choose the best

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

### "Transcript not available"

**Causes:**
- No captions on video
- Auto-captions disabled
- Video is private

**Solutions:**
- Check video has captions
- Try a different video
- Use direct text input with summary

### "Content too short"

**Minimum:** 300 characters recommended

**Fix:**
- Add more detail
- Combine multiple sources
- Expand with AI Editor

---

## Next Steps

Now you have content imported, try:

1. **[Using the Smart Editor](04-smart-editor.md)** - Refine your generated content
2. **[Setting up RSS Feeds](03-rss-feeds.md)** - Automate content import
3. **[Scheduling Posts](05-scheduling-posts.md)** - Publish your assets

---

## Summary

You now know how to:
- ✅ Import content from URLs, YouTube, and text
- ✅ Generate multiple content assets with AI
- ✅ Review and edit generated content
- ✅ Organize content in projects

**Questions?** Contact support@contentforge.ai
