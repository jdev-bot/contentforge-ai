import { defineConfig } from '@playwright/test'

/**
 * Playwright E2E test configuration for ContentForge AI staging.
 *
 * Run:  npx playwright test
 * Run with UI: npx playwright test --ui
 * Run single file: npx playwright test e2e/auth-flow.spec.ts
 *
 * All tests target the live staging environment (no local server spin-up).
 */
export default defineConfig({
  testDir: '.',
  timeout: 60_000,           // Per-test timeout (staging can be slow)
  expect: { timeout: 15_000 },
  fullyParallel: false,      // Sequential — avoid auth race conditions on shared test account
  retries: 1,                // Retry once for flaky network
  reporter: [
    ['html', { open: 'never' }],
    ['json', { outputFile: 'test-results.json' }],
    ['list'],
  ],
  use: {
    baseURL: process.env.E2E_BASE_URL || 'https://frontend-theta-seven-65.vercel.app',
    headless: true,
    viewport: { width: 1280, height: 720 },
    actionTimeout: 10_000,
    navigationTimeout: 30_000,
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
    video: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: {
        browserName: 'chromium',
        // Use system Chromium (snap) since Playwright's bundled Chromium
        // is missing shared libraries (libatk) on this system
        launchOptions: {
          executablePath: '/snap/bin/chromium',
          args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
        },
      },
    },
  ],
  outputDir: 'test-artifacts/',
})