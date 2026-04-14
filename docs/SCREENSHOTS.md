# ContentForge AI - Screenshot Reference

This document catalogs all available screenshots for ContentForge AI.

## Screenshot Directory

All screenshots are stored in `docs/screenshots/`.

## Available Screenshots

### Core Application Screens

| Screenshot | File | Description |
|-----------|------|-------------|
| Login Page | `login.png` | Main login/signup page |
| Login Page (Mobile) | `login-page-mobile.png` | Login page on mobile viewport |
| Login (Signup Mode) | `login-signup-mode.png` | Login page in signup mode |
| Dashboard | `dashboard.png` | Main dashboard with stats and widgets |
| Dashboard (Mobile) | `dashboard-mobile.png` | Dashboard on mobile viewport |
| Dashboard Overview | `dashboard-overview.png` | Dashboard overview widget |
| Content Tab | `content-tab.png` | Content library listing |
| Create Content | `content_new.png` | Content creation page |
| Create Content (New) | `content-new-page.png` | New content creation page |
| Create Project | `projects-new-page.png` | New project creation form |
| Settings | `settings.png` | User settings page |

### Backend/API Screenshots

| Screenshot | File | Description |
|-----------|------|-------------|
| Login Page (HTML) | `real/login-page.html` | Rendered login page HTML |
| API Docs | `real/api-docs.html` | Backend API documentation |
| Health Response | `real/health-response.json` | Health endpoint JSON response |
| Backend Log | `real/backend.log` | Backend startup log |

## Screenshot Capture

### Manual Capture

```bash
# Capture a single screenshot
npx playwright screenshot \
  --browser=chromium \
  --viewport-size=1280,720 \
  --full-page \
  http://localhost:3000/login \
  docs/screenshots/login.png
```

### Automated Capture

```bash
# From project root
./scripts/capture-screenshots.sh
```

### Capture with Wait

```bash
npx playwright screenshot \
  --browser=chromium \
  --viewport-size=1280,720 \
  --full-page \
  --wait-for-timeout=10000 \
  http://localhost:3000 \
  docs/screenshots/page.png
```

## Screenshot Guidelines

### Recommended Resolutions

| Type | Viewport | Filename Pattern |
|------|----------|-----------------|
| Desktop | 1280×720 | `feature-name.png` |
| Desktop (Full) | 1280×900 | `feature-name-full.png` |
| Mobile | 375×812 | `feature-name-mobile.png` |
| Tablet | 768×1024 | `feature-name-tablet.png` |

### Naming Convention

- Use lowercase, hyphen-separated names
- Include feature or page name
- Append `-mobile` or `-tablet` for responsive variants
- Examples: `dashboard.png`, `schedule-calendar.png`, `analytics-funnel.png`

## Screenshots Needed (P4 Features)

The following P4 feature screenshots should be captured when staging environment is available:

| Feature | Screenshot | Priority |
|---------|-----------|----------|
| Quality Score | `quality-score-badge.png` | High |
| Sentiment Analysis | `sentiment-badge.png` | High |
| Version History | `version-history.png` | Medium |
| Custom Dashboards | `custom-dashboard.png` | High |
| Auto-Suggestions | `auto-suggestions.png` | High |
| SEO Optimization | `seo-analysis.png` | Medium |
| Tone Adjustment | `tone-adjustment.png` | Medium |
| Funnel Analytics | `funnel-analytics.png` | High |
| Attribution Report | `attribution-report.png` | High |
| SLA Monitoring | `sla-monitoring.png` | Medium |
| Content Freshness | `content-freshness.png` | Medium |
| Competitor Tracking | `competitor-tracking.png` | Medium |
| SSO Configuration | `sso-config.png` | Low |
| Comments v2 | `comments-v2.png` | Medium |
| Collaboration | `collaboration-view.png` | Medium |
| Marketplace | `marketplace.png` | Low |
| Schedule Calendar | `schedule-calendar.png` | High |
| Smart Editor | `smart-editor-full.png` | High |

## CI/CD Integration

For automated screenshot updates:

```yaml
# .github/workflows/screenshots.yml
name: Update Screenshots
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:

jobs:
  screenshots:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npx playwright install chromium
      - run: ./scripts/capture-screenshots.sh
      - uses: actions/upload-artifact@v4
        with:
          name: screenshots
          path: docs/screenshots/
```

---

*Updated: April 14, 2026*