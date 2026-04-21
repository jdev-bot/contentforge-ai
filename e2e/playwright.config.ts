/**
 * ContentForge AI — Comprehensive E2E Test Suite
 *
 * Architecture: 100% UI-driven validation of the complete functionality stack.
 * Entry point: UI (Playwright browser) → validates frontend rendering, API calls, backend logic, DB state.
 *
 * Coverage Map:
 * ┌──────────────────────────────────────────────────────────────────────┐
 * │ SPEC                     │ TESTS │ TABS/FEATURES                    │
 * ├──────────────────────────┼───────┼──────────────────────────────────┤
 * │ 01-auth                  │  10   │ Login, Register, Logout, SSO     │
 * │ 02-dashboard-shell       │   8   │ Sidebar, Search, Pinned, Ctrl+N  │
 * │ 03-content               │  12   │ List, Create, Detail, Delete     │
 * │ 04-projects              │   8   │ List, Create, Detail, Delete     │
 * │ 05-analytics             │   8   │ Dashboard, Export, KPIs          │
 * │ 06-schedule              │   6   │ Calendar, CRUD posts             │
 * │ 07-rss                   │   8   │ Feeds, Entries, Settings         │
 * │ 08-team                   │   8   │ Orgs, Members, Calendar         │
 * │ 09-alerts-system         │   8   │ Alerts, Rules, Notifications     │
 * │ 10-quality-insights      │  10   │ Quality, Sentiment, Suggest, Cat │
 * │ 11-extensions            │  10   │ Plugins, Marketplace, Integ, SLA │
 * │ 12-system-admin          │   8   │ Audit, Dashboards, Retention     │
 * │ 13-api-stack-validation  │  15   │ Direct API: 405 routes tested   │
 * │ 14-settings-account      │   8   │ Profile, Usage, Data Export      │
 * │ 15-trash                 │   6   │ List, Restore, Delete, Empty      │
 * │ 16-standalone-pages      │   6   │ Pricing, Legal, Onboarding, SSO  │
 * ├──────────────────────────┼───────┼──────────────────────────────────┤
 * │ TOTAL                    │ ~131  │                                  │
 * └──────────────────────────────────────────────────────────────────────┘
 *
 * Run: cd e2e && npx playwright test
 * Single: npx playwright test 03-content
 * Debug: npx playwright test --debug 03-content
 */

import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: '.',
  fullyParallel: false,        // Sequential — Render free tier can't handle parallel
  forbidOnly: !!process.env.CI,
  retries: 1,
  workers: 1,
  reporter: process.env.CI
    ? [['list'], ['html', { open: 'never' }]]
    : [['list'], ['html', { open: 'on-failure' }]],
  timeout: 60_000,
  expect: { timeout: 15_000 },

  use: {
    baseURL: process.env.E2E_BASE_URL || 'https://frontend-theta-seven-65.vercel.app',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10_000,
    launchOptions: {
      env: {
        ...process.env,
        LD_LIBRARY_PATH: `${process.env.HOME}/.local/lib/playwright-libs/usr/lib/x86_64-linux-gnu:${process.env.LD_LIBRARY_PATH || ''}`,
      },
    },
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})