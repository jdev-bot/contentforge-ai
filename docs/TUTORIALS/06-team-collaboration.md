# Tutorial: Team Collaboration

> Work together with your team on content projects — with SSO, advanced comments, and marketplace integrations

---

## What You'll Learn

By the end of this tutorial, you will:
- Set up organizations for team collaboration
- Invite team members with appropriate roles
- Configure SSO/SAML for enterprise authentication
- Use Comments v2 for content review
- Collaborate in real-time with live editing
- Browse and install plugins from the Marketplace
- Share projects and content with your team
- Manage permissions and access levels

**Time Required**: 30 minutes

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
├── Shared Resources
│   ├── Brand Guidelines
│   ├── Templates
│   └── Analytics
└── Integrations
    ├── SSO / SAML
    ├── Plugins
    └── Marketplace Apps
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
Data Retention: 90 days (customizable per project)
```

---

## Step 3: Configure SSO / SAML (Enterprise)

Enterprise organizations can configure single sign-on for streamlined team access.

### OIDC-Based SSO

1. Go to **Settings > Security > SSO**
2. Select **"OpenID Connect (OIDC)"**
3. Configure your identity provider:

```
Provider: Okta (or Auth0, Azure AD, Keycloak, etc.)
Issuer URL: https://acme.okta.com/oauth2/default
Client ID: your-client-id
Client Secret: ••••••••
Authorization URL: https://acme.okta.com/oauth2/default/v1/authorize
Token URL: https://acme.okta.com/oauth2/default/v1/token
User Info URL: https://acme.okta.com/oauth2/default/v1/userinfo
Scopes: openid profile email
```

4. Click **"Test Connection"** to verify
5. Click **"Enable SSO"**

### SAML SSO

1. Go to **Settings > Security > SSO**
2. Select **"SAML 2.0"**
3. Configure:

```
Identity Provider: Okta / Azure AD / OneLogin
Entity ID: https://app.contentforge.ai/saml/metadata
ACS URL: https://app.contentforge.ai/saml/acs
IdP Metadata URL: https://idp.example.com/metadata
Name ID Format: EmailAddress
```

4. Download the SP metadata XML for your IdP
5. Click **"Test SAML Connection"**
6. Click **"Enable SAML SSO"**

### SSO User Experience

Once SSO is enabled:
- Team members click **"Sign in with SSO"** on the login page
- Redirected to your identity provider
- Authenticated and returned to ContentForge
- Automatically added to your organization based on IdP group mapping

> **Note**: SSO can be enforced so that all organization members must authenticate through your identity provider.

---

## Step 4: Invite Team Members

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
3. If SSO is enabled, user authenticates through your IdP
4. Creates/joins ContentForge account
5. Added to organization
6. Receives welcome email

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

## Step 5: Configure Project Permissions

### Project-Level Access

Each project can have specific permissions:

```
Project: Q2 Marketing Campaign

Members:
├─ Sarah (Editor) - Full access
├─ John (Writer) - Can create and edit
└─ Mike (Viewer) - View only
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

## Step 6: Collaborate with Comments v2

The enhanced Comments v2 system provides rich, threaded conversations for content review.

### Accessing Comments

1. Open any content item
2. Click the **"Comments"** tab (speech bubble icon)
3. View and add comments

### Comment Features

```
┌─────────────────────────────────────────────────────┐
│ Comments (5)                                         │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 💬 Sarah Chen • Editor • 2 hours ago                │
│ "The intro paragraph needs a stronger hook."        │
│                                                     │
│   ↳ 💬 John Park • Writer • 1 hour ago              │
│     "Updated — see v3 in history. Added a question  │
│      hook instead."                                  │
│     ✅ Resolved by Sarah                            │
│                                                     │
│ 💬 Mike Ross • Viewer • 45 min ago                  │
│ "Can we add the Q2 revenue numbers here?"            │
│ 🏷️ Action Item • Assigned to: John                  │
│ 📎 Attachment: Q2-figures.pdf                        │
│                                                     │
│ [+ Add Comment]                                     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Comments v2 Features

| Feature | Description |
|---------|-------------|
| **Threaded Replies** | Nest comments in conversation threads |
| **Inline Comments** | Highlight text and comment on specific passages |
| **@Mentions** | Tag team members to notify them |
| **Action Items** | Convert comments to assigned tasks |
| **Attachments** | Attach files to comments (PDFs, images, spreadsheets) |
| **Reactions** | Quick emoji reactions (👍 ❤️ 🎉) without full reply |
| **Resolution** | Mark comments as resolved when addressed |
| **History** | Full comment history preserved in content version |

### Inline Comments

1. Select text in the content editor
2. Click the **comment icon** that appears
3. Type your comment
4. The comment is anchored to that specific text selection

### @Mentions

Type `@` in a comment to mention a team member:
- They receive an in-app notification + email
- The comment shows their name highlighted
- They can reply directly from the notification

---

## Step 7: Real-Time Collaboration

ContentForge supports real-time collaboration so multiple team members can work on content simultaneously.

### How It Works

1. Open a content item for editing
2. See active collaborators in the top bar:

```
┌─────────────────────────────────────────────────────┐
│ Editing: Q2 Marketing Campaign                       │
│ 👤 Sarah C. • 👤 John P. • +2 viewers              │
│ [WebSocket Connected ●]                              │
├─────────────────────────────────────────────────────┤
│                                                     │
│ (Live cursors and changes appear in real-time)       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Collaboration Features

| Feature | Description |
|---------|-------------|
| **Live Cursors** | See where teammates are editing |
| **Real-Time Updates** | Changes appear instantly for all editors |
| **Presence Indicators** | See who's viewing/editing |
| **Conflict Resolution** | Auto-merge for non-overlapping edits |
| **Edit Indicators** | Highlighted sections being edited by others |

### Best Practices for Collaboration

- Communicate in comments before making major changes
- Use @mentions to coordinate on overlapping sections
- Save frequently to push your changes to collaborators
- Use version history to review changes made while you were away

---

## Step 8: Plugin Marketplace

The ContentForge Marketplace offers plugins that extend the platform with additional features and integrations.

### Access the Marketplace

1. Go to **Settings > Marketplace**
2. Browse available plugins:

```
┌─────────────────────────────────────────────────────┐
│ 🏪 Plugin Marketplace                               │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 🔍 Search plugins...                                │
│                                                     │
│ 📊 Google Analytics Connector                       │
│ Sync GA4 data with ContentForge analytics           │
│ ⭐ 4.8 • 1.2k installs • Free                      │
│ [Install]                                           │
│                                                     │
│ 📝 Grammarly Integration                            │
│ AI-powered grammar and style checking                │
│ ⭐ 4.6 • 890 installs • $5/mo                      │
│ [Install]                                           │
│                                                     │
│ 🔔 Slack Notifications                              │
│ Get publishing alerts in Slack channels              │
│ ⭐ 4.9 • 2.1k installs • Free                      │
│ [Install]                                           │
│                                                     │
│ 📈 HubSpot Integration                              │
│ Sync contacts and attribution data                   │
│ ⭐ 4.5 • 450 installs • $10/mo                     │
│ [Install]                                           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Plugin Categories

| Category | Examples |
|----------|---------|
| **Analytics** | Google Analytics, Mixpanel, Amplitude |
| **Communication** | Slack, Microsoft Teams, Discord |
| **CRM** | HubSpot, Salesforce, Pipedrive |
| **Writing** | Grammarly, Hemingway, LanguageTool |
| **SEO** | Ahrefs, SEMrush, Moz |
| **Automation** | Zapier, Make, n8n |
| **Custom** | Organization-built internal plugins |

### Installing a Plugin

1. Find the plugin in the Marketplace
2. Click **"Install"**
3. Review permissions requested
4. Click **"Authorize"**
5. Configure plugin settings
6. Plugin is now available in your workflow

### Plugin SDK

For organizations that want to build custom plugins, ContentForge provides a Plugin SDK:

1. Go to **Settings > Developer > SDK**
2. Download the SDK or view documentation
3. Build, test, and deploy custom plugins
4. Optionally publish to the Marketplace for other organizations

---

## Step 9: Share Resources

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

### Shared Analytics

Team access to performance data:

```
Analytics Access:
├─ Overall team stats
├─ Individual performance
├─ Project-level reports
├─ Custom dashboards (shared)
└─ Comparison tools
```

---

## Step 10: Manage Team Activity

### Activity Feed

View team activity:

```
┌─────────────────────────────────────────────────────┐
│ Team Activity                                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Today                                                │
│ ├─ Sarah published "Q2 Strategy" on LinkedIn        │
│ ├─ John created new content "Product Update"         │
│ ├─ Mike commented on "Marketing Tips"               │
│ ├─ Sarah approved "Newsletter Draft"                 │
│ └─ New plugin installed: Slack Notifications         │
│                                                     │
│ Yesterday                                            │
│ ├─ John completed "Twitter Thread"                  │
│ ├─ SSO configured for Okta                          │
│ └─ Mike joined the team                             │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Audit Logs

Enterprise plans include comprehensive audit logs:

1. Go to **Settings > Audit Logs**
2. View all organization actions:
   - Login events
   - Content changes
   - Permission modifications
   - SSO configuration changes
   - Plugin installations
   - Data exports

---

## Collaboration Best Practices

### Communication

✅ **Do:**
- Use Comments v2 for specific, threaded feedback
- @mention team members for direct input
- Convert recurring feedback into action items
- Resolve comments when addressed
- Use real-time collaboration for pair-writing sessions

❌ **Don't:**
- Edit others' content without leaving a comment first
- Delete team members' work
- Share login credentials (use SSO instead)
- Ignore assigned action items

### Workflow Tips

1. **Clear assignments** — Every piece has an owner
2. **Defined deadlines** — Set due dates for all content
3. **Regular check-ins** — Weekly team sync on content
4. **Version control** — Use drafts, comments, and history
5. **Approval gates** — Required reviews before publish
6. **SSO enforcement** — Use SSO for consistent, secure access
7. **Plugin standardization** — Install organization-wide plugins

---

## Troubleshooting

### SSO Not Working

**Check:**
1. IdP configuration (URLs, client ID/secret)
2. User exists in your identity provider
3. Callback URL is correct
4. Clock skew between servers (SAML requires time sync)

**Fix:**
- Click "Test Connection" in SSO settings
- Verify IdP metadata is up to date
- Check IdP logs for rejected requests

### Comments Not Loading

**Check:**
1. WebSocket connection is active
2. User has comment permissions
3. Content item is accessible

### Plugin Installation Fails

**Check:**
1. Organization has required plan (some plugins require Pro/Enterprise)
2. API credentials are valid
3. Plugin permissions are authorized

---

## Summary

You now know how to:
- ✅ Create and manage an organization
- ✅ Configure OIDC and SAML SSO for enterprise authentication
- ✅ Invite team members with appropriate roles
- ✅ Use Comments v2 for threaded, inline feedback
- ✅ Collaborate in real-time with live editing
- ✅ Browse and install plugins from the Marketplace
- ✅ Configure project-level permissions
- ✅ Monitor team activity and audit logs

---

## Next Steps

Now that your team is set up:

1. **[Analytics & Insights](07-analytics.md)** - Track team and content performance
2. **[Scheduling Posts](05-scheduling-posts.md)** - Set up your team publishing workflow
3. **[Custom Dashboards](07-analytics.md#custom-dashboards)** — Build shared analytics views

---

**Questions?** Contact support@contentforge.ai