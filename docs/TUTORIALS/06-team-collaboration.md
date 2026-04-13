# Tutorial: Team Collaboration

> Work together with your team on content projects

---

## What You'll Learn

By the end of this tutorial, you will:
- Set up organizations for team collaboration
- Invite team members with appropriate roles
- Share projects and content with your team
- Manage permissions and access levels
- Collaborate on content creation and review

**Time Required**: 25 minutes

**Plan Required**: Pro or Enterprise (Free plan is single-user)

---

## Prerequisites

Before starting:
- Pro or Enterprise ContentForge account
- Team members' email addresses
- Defined content workflow

---

## Step 1: Understanding Team Structure

### Organization Hierarchy

```
Organization (e.g., "Acme Corp")
├── Members
│   ├── Owner (you)
│   ├── Admin(s)
│   ├── Editor(s)
│   ├── Writer(s)
│   └── Viewer(s)
├── Projects
│   ├── Marketing Campaign
│   ├── Product Launch
│   └── Blog Content
└── Shared Resources
    ├── Brand Guidelines
    ├── Templates
    └── Analytics
```

### Role Definitions

| Role | Permissions | Best For |
|------|-------------|----------|
| **Owner** | Full control, billing | Account holder |
| **Admin** | Manage team, all content | Team leads |
| **Editor** | Edit all content, publish | Content managers |
| **Writer** | Create content, edit own | Content creators |
| **Viewer** | View only, can comment | Stakeholders |

---

## Step 2: Create an Organization

### Set Up Organization

1. Go to **Settings > Organization**
2. Click **"Create Organization"**
3. Enter organization details:

```
Organization Name: Acme Corporation
Slug: acme-corp
Description: Marketing and content team
Website: https://acme.com
```

4. Set organization logo (optional)
5. Click **"Create Organization"**

### Organization Settings

Configure organization defaults:

```
Default Brand Voice: Professional
Default Platforms: Twitter, LinkedIn, Blog
Content Review Required: Yes
Notification Settings: All members
```

---

## Step 3: Invite Team Members

### Send Invitations

1. Go to **Settings > Team Members**
2. Click **"Invite Member"**
3. Enter member details:

```
Email: sarah@acme.com
Role: Editor
Projects: All projects
Message: Welcome to the content team!
```

4. Click **"Send Invitation"**

### Invitation Process

**What Happens:**
1. Email sent to invited user
2. User clicks link to accept
3. Creates/joins ContentForge account
4. Added to organization
5. Receives welcome email

**Invitation States:**
- Pending - Waiting for acceptance
- Accepted - Member joined
- Expired - Invitation timed out (can resend)

### Bulk Invitations

Invite multiple members at once:

```
Emails: john@acme.com, sarah@acme.com, mike@acme.com
Role: Writer
Projects: Marketing Campaign
```

---

## Step 4: Configure Project Permissions

### Project-Level Access

Each project can have specific permissions:

```
Project: Q2 Marketing Campaign

Members:
├─ Sarah (Editor) - Full access
├─ John (Writer) - Can create and edit
└─ Mike (Viewer) - View only
```

### Set Project Permissions

1. Go to **Projects**
2. Select a project
3. Click **"Members"** tab
4. Add or modify members:

```
Add Member:
User: john@acme.com
Permission Level: Writer
Can Schedule: Yes
Can Publish: No
Can Delete: No
```

### Permission Levels

| Action | Owner | Admin | Editor | Writer | Viewer |
|--------|-------|-------|--------|--------|--------|
| View content | ✅ | ✅ | ✅ | ✅ | ✅ |
| Create content | ✅ | ✅ | ✅ | ✅ | ❌ |
| Edit any content | ✅ | ✅ | ✅ | ❌ | ❌ |
| Edit own content | ✅ | ✅ | ✅ | ✅ | ❌ |
| Schedule posts | ✅ | ✅ | ✅ | ✅* | ❌ |
| Publish posts | ✅ | ✅ | ✅ | ❌ | ❌ |
| Delete content | ✅ | ✅ | ✅ | ❌ | ❌ |
| Manage team | ✅ | ✅ | ❌ | ❌ | ❌ |
| View analytics | ✅ | ✅ | ✅ | ✅* | ✅* |

*Requires project-level permission

---

## Step 5: Collaborate on Content

### Content Workflow

**Typical Team Workflow:**

```
1. Writer creates draft
   ↓
2. Submits for review
   ↓
3. Editor reviews and provides feedback
   ↓
4. Writer revises
   ↓
5. Editor approves
   ↓
6. Content scheduled/published
```

### Assign Content to Team Members

1. Create or open content
2. Click **"Assign To"**
3. Select team member:

```
Assigned to: Sarah (Editor)
Due Date: 2026-04-20
Priority: High
Notes: Please review for brand voice
```

### Content Status Tracking

Track content through workflow:

| Status | Meaning | Who Can Set |
|--------|---------|-------------|
| Draft | Initial creation | Creator |
| In Review | Submitted for review | Creator |
| Needs Revision | Feedback provided | Reviewer |
| Approved | Ready to publish | Editor/Admin |
| Scheduled | Queued for publishing | Editor/Admin |
| Published | Live on platforms | System |

### Review and Feedback

**Add Comments:**

1. Open content
2. Select text or click comment icon
3. Add comment:

```
Comment on paragraph 3:
"This point is great, but could we add 
a statistic to support it?"

- Sarah, 2 hours ago
[Reply] [Resolve]
```

**Review Mode:**
- Compare versions
- See suggested changes
- Accept or reject edits
- Track all changes

---

## Step 6: Share Resources

### Shared Brand Assets

**Upload to Organization:**

1. Go to **Settings > Brand Assets**
2. Upload resources:
   - Logo files
   - Brand guidelines PDF
   - Style guide
   - Approved images

### Shared Templates

Create templates for consistent content:

```
Template: LinkedIn Company Post

Structure:
1. Hook (attention grabber)
2. Problem statement
3. Solution/benefit
4. Call to action
5. Hashtags

Voice: Professional but approachable
Length: 150-300 words
```

**Share Template:**
1. Create template
2. Click **"Share with Team"**
3. Select which members/projects

### Shared Analytics

Team access to performance data:

```
Analytics Access:
├─ Overall team stats
├─ Individual performance
├─ Project-level reports
└─ Comparison tools
```

---

## Step 7: Manage Team Activity

### Activity Feed

View team activity:

```
┌─────────────────────────────────────────────────────┐
│ Team Activity                                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Today                                                │
│ ├─ Sarah published "Q2 Strategy" on LinkedIn      │
│ ├─ John created new content "Product Update"        │
│ ├─ Mike commented on "Marketing Tips"             │
│ └─ Sarah approved "Newsletter Draft"              │
│                                                     │
│ Yesterday                                            │
│ ├─ John completed "Twitter Thread"                │
│ └─ Mike joined the team                            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Notifications

Configure team notifications:

| Event | Notification |
|-------|--------------|
| Content assigned to you | Email + In-app |
| Content needs review | Email + In-app |
| Comment added | In-app |
| Content published | In-app |
| Team member joins | In-app |

### Team Performance

View team metrics:

```
Team Performance (Last 30 Days)

Content Created:
├─ Sarah: 12 posts
├─ John: 8 posts
└─ Total: 20 posts

Published:
├─ On time: 18 (90%)
├─ Late: 2 (10%)
└─ Total: 20

Engagement:
├─ Avg per post: 245
└─ Best performer: "Product Launch"
```

---

## Step 8: Handle Team Administration

### Remove Team Members

1. Go to **Settings > Team Members**
2. Find member to remove
3. Click **"Remove"**
4. Choose action for their content:
   - Transfer to another member
   - Keep under organization
   - Delete (irreversible)

### Change Member Roles

1. Go to member's profile
2. Click **"Change Role"**
3. Select new role
4. Update permissions

**Role Change Impact:**
- Immediate effect
- May affect access to content
- Member receives notification

### Organization Settings

**Billing Management:**
- View/upgrade plan
- Add payment method
- View invoices
- Manage seats

**Security Settings:**
- Require 2FA
- Session timeout
- IP restrictions
- Audit logs

---

## Collaboration Best Practices

### Communication

✅ **Do:**
- Use comments for specific feedback
- @mention team members
- Respond to reviews within 24 hours
- Keep feedback constructive
- Resolve comments when addressed

❌ **Don't:**
- Edit others' content without permission
- Delete team members' work
- Share login credentials
- Ignore assigned content

### Workflow Tips

1. **Clear assignments** - Every piece has an owner
2. **Defined deadlines** - Set due dates for all content
3. **Regular check-ins** - Weekly team sync on content
4. **Version control** - Use drafts and revisions
5. **Approval gates** - Required reviews before publish

### Content Standards

**Establish team guidelines:**
- Brand voice and tone
- Content length by platform
- Image requirements
- Approval workflows
- Publishing schedule

---

## Troubleshooting

### Member Can't Access Content

**Check:**
1. Invitation accepted
2. Correct role assigned
3. Project permissions set
4. Account not expired

### Can't Invite Member

**Reasons:**
- Seat limit reached (upgrade plan)
- Email already in use
- Invalid email format

**Fix:**
- Upgrade for more seats
- Check email address
- Contact support

### Content Not Syncing

**Solutions:**
1. Refresh the page
2. Check internet connection
3. Verify permissions
4. Contact admin

---

## Summary

You now know how to:
- ✅ Create and manage an organization
- ✅ Invite team members with appropriate roles
- ✅ Configure project-level permissions
- ✅ Assign and track content workflows
- ✅ Share resources and templates
- ✅ Monitor team activity and performance

---

## Next Steps

Now that your team is set up:

1. **[Analytics & Insights](07-analytics.md)** - Track team performance
2. **[Competitor Analysis](../FEATURES_GUIDE.md#competitor-analysis)** - Monitor competition
3. **[Content Calendar](../FEATURES_GUIDE.md#content-calendar)** - Plan team content schedule

---

**Questions?** Contact support@contentforge.ai
