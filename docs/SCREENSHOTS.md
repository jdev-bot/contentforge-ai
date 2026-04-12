# ContentForge AI - Screenshot Capture Workflow

This document describes the automated screenshot capture workflow using Chrome/Chromium and Playwright.

## Prerequisites

### Chrome/Chromium Installation

The system uses Playwright's bundled Chromium browser which is installed automatically.

```bash
# Install Playwright Chromium browser (already in devDependencies)
npx playwright install chromium
```

**Verified browsers:**
- Chromium (bundled with Playwright)
- Chrome (if installed locally)

### Required Dependencies

```bash
# From src/frontend/package.json
cd src/frontend
npm install
```

Required dev dependencies:
- `@playwright/test`: For screenshot capture
- `puppeteer-core`: Alternative browser automation
- `node-screenshots`: Native screenshot capture

## Screenshot Capture Process

### Manual Capture with Playwright

```bash
# Capture a single screenshot
npx playwright screenshot \
  --browser=chromium \
  --viewport-size=1280,720 \
  --full-page \
  http://localhost:3000/login \
  docs/screenshots/login.png
```

### Options

- `--browser=chromium`: Use Chromium browser (lightweight, fast)
- `--viewport-size=1280,720`: Desktop viewport dimensions
- `--full-page`: Capture full page, not just viewport
- `--wait-for-timeout=5000`: Wait for page to load (5 seconds)

### Automated Screenshot Script

Use the provided script to start services and capture screenshots automatically:

```bash
# From project root
./scripts/capture-screenshots.sh
```

This script will:
1. Start the backend API server (port 8000)
2. Start the frontend dev server (port 3000)
3. Wait for services to be ready
4. Capture screenshots of key pages:
   - `/login` - Login page
   - `/dashboard` - Dashboard (requires authentication)
5. Stop services after capture

## Screenshot Locations

All screenshots are saved to:
```
docs/screenshots/
├── login.png              # Login/signup page
├── dashboard.png          # Main dashboard
├── content-tab.png        # Content management
├── content-new-page.png   # Create content form
├── projects-tab.png       # Projects list
├── analytics-tab.png      # Analytics view
└── real/                  # Production screenshots
```

## Development Workflow

### Adding New Screenshots

1. Start the application:
   ```bash
   ./scripts/dev-start.sh
   ```

2. Capture specific pages:
   ```bash
   npx playwright screenshot \
     --browser=chromium \
     --viewport-size=1280,720 \
     --full-page \
     http://localhost:3000/PATH \
     docs/screenshots/NAME.png
   ```

3. Verify screenshots in `docs/screenshots/`

### Automated Workflow

The capture script handles the full workflow:
- Backend startup with uvicorn
- Frontend dev server startup
- Health check polling
- Screenshot capture at multiple resolutions
- Automatic cleanup

## Troubleshooting

### Chrome not found

```bash
# Install Playwright browsers
npx playwright install

# Or install system Chromium
# Ubuntu/Debian:
sudo apt-get install chromium-browser

# macOS:
brew install chromium
```

### Port conflicts

The script uses ports 8000 (backend) and 3000 (frontend). Ensure these are free:

```bash
# Check if ports are in use
lsof -i :8000
lsof -i :3000

# Kill processes if needed
kill $(lsof -t -i :8000)
kill $(lsof -t -i :3000)
```

### Screenshots show loading states

Increase wait time before capture:

```bash
npx playwright screenshot \
  --browser=chromium \
  --viewport-size=1280,720 \
  --wait-for-timeout=10000 \
  http://localhost:3000 \
  docs/screenshots/page.png
```

## CI/CD Integration

For automated documentation updates:

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

## Notes

- Screenshots are captured with a 1280x720 viewport (standard desktop)
- Full-page screenshots capture the entire scrollable content
- The script includes a 10-second delay for page hydration
- Authentication may be required for dashboard screenshots
