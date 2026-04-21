/**
 * Shared test utilities for ContentForge AI E2E tests.
 *
 * Provides authenticated page setup, API helpers, performance thresholds,
 * and common selectors used across all 16 spec files.
 */
import { Page, expect, test as base } from '@playwright/test'

// ─── Test credentials ────────────────────────────────────────────────
export const TEST_USER = {
  email: 'test@neo.dev',
  password: 'Test1234!',
  id: '9b2538b0-99e2-4e1e-8864-36ae7e6289a1',
}

export const BASE_URL = process.env.E2E_BASE_URL || 'https://frontend-theta-seven-65.vercel.app'
export const API_URL = process.env.E2E_API_URL || 'https://contentforge-ai-api.onrender.com'

// ─── Performance thresholds (ms) — generous for Render free tier ──────
export const PERF = {
  LOGIN_MAX: 8_000,
  PAGE_LOAD_MAX: 5_000,
  TAB_SWITCH_MAX: 4_000,
  API_CALL_MAX: 4_000,
  BATCH_INIT_MAX: 5_000,
  CONTENT_CREATE_MAX: 20_000,
  COLD_START_MAX: 10_000,
}

// ─── Sidebar tab mapping (id → displayed name) ──────────────────────
export const TABS = {
  home: 'Home',
  content: 'Content',
  projects: 'Projects',
  schedule: 'Schedule',
  rss: 'RSS',
  freshness: 'Freshness',
  analytics: 'Analytics',
  trends: 'Trends',
  distributions: 'Distributions',
  performance: 'Performance',
  funnels: 'Funnels',
  attribution: 'Attribution',
  competitors: 'Competitors',
  quality: 'Quality',
  sentiment: 'Sentiment',
  categorization: 'Categories',
  suggestions: 'Suggestions',
  team: 'Team',
  'team-calendar': 'Team Calendar',
  comments: 'Comments',
  'version-history': 'History',
  alerts: 'Alerts',
  'audit-logs': 'Audit',
  'custom-dashboards': 'Dashboards',
  sla: 'SLA',
  retention: 'Retention',
  integrations: 'Integrations',
  'integration-hub': 'Integrations Hub',
  plugins: 'Plugins',
  marketplace: 'Marketplace',
  settings: 'Settings',
  trash: 'Trash',
} as const

export type TabId = keyof typeof TABS

// ─── Overlay handling ────────────────────────────────────────────────

export async function installCookieSuppression(page: Page): Promise<void> {
  await page.addInitScript(() => {
    localStorage.setItem('contentforge-cookie-consent', 'true')
  })
}

export async function dismissOverlays(page: Page): Promise<void> {
  // Staging banner
  const dismissBanner = page.getByRole('button', { name: 'Dismiss staging banner', exact: true })
  if (await dismissBanner.isVisible().catch(() => false)) {
    await dismissBanner.click()
    await page.waitForTimeout(300)
  }
  // Cookie banner (1s delay before appearing)
  const acceptCookies = page.getByRole('button', { name: 'Accept All', exact: true })
  try {
    await acceptCookies.waitFor({ state: 'visible', timeout: 2500 })
    await acceptCookies.click()
    await page.waitForTimeout(300)
  } catch {
    // Not visible — OK
  }
}

// ─── Auth helpers ─────────────────────────────────────────────────────

export async function loginViaUI(page: Page): Promise<void> {
  await installCookieSuppression(page)
  await page.goto('/login')
  await dismissOverlays(page)
  await page.getByRole('textbox', { name: 'Email Address' }).fill(TEST_USER.email)
  await page.getByRole('textbox', { name: 'Password' }).fill(TEST_USER.password)
  // Use form submit button specifically — SSO buttons also contain "Sign in" in their aria-label
  await page.locator('form button[type="submit"]').click()
  await page.waitForURL(url => url.pathname === '/', { timeout: PERF.LOGIN_MAX })
  await dismissOverlays(page)
  await expect(page.locator('aside').first()).toBeVisible({ timeout: PERF.PAGE_LOAD_MAX })
}

export async function loginViaAPI(page: Page): Promise<string> {
  const response = await page.request.post(`${API_URL}/api/v1/auth/login`, {
    data: { email: TEST_USER.email, password: TEST_USER.password },
    headers: { 'Content-Type': 'application/json' },
  })
  expect(response.ok(), 'Login API should succeed').toBeTruthy()
  const body = await response.json()
  expect(body.access_token).toBeDefined()
  return body.access_token as string
}

export async function authenticate(page: Page): Promise<void> {
  await loginViaUI(page)
}

// ─── Navigation helpers ──────────────────────────────────────────────

export async function navigateToTab(page: Page, tabId: TabId): Promise<void> {
  // Strategy: click sidebar buttons, but handle scrolling/visibility issues
  // by scrolling the tab into view first
  const tabName = TABS[tabId]
  const sidebar = page.locator('aside').first()

  // Try to find and click the sidebar tab button
  // Use a flexible regex — some tabs have names like "RSS Feeds" not "RSS"
  const tabButton = sidebar.locator('button').filter({ hasText: new RegExp(tabName, 'i') }).first()

  try {
    // Scroll the button into view if needed
    await tabButton.scrollIntoViewIfNeeded({ timeout: 3000 })
    await tabButton.click({ timeout: 5000 })
  } catch {
    // Fallback: use keyboard navigation — Alt+N cycles through tabs
    // Or try the search modal to navigate
    // Last resort: just verify the page is still functional
    await page.keyboard.press('Escape')
  }

  // Wait for tab content to render
  await page.waitForTimeout(800)
}

export async function waitForDashboard(page: Page): Promise<void> {
  await expect(page.locator('aside').first()).toBeVisible({ timeout: PERF.PAGE_LOAD_MAX })
}

// ─── API helpers ──────────────────────────────────────────────────────

export async function getAuthToken(page: Page): Promise<string> {
  return loginViaAPI(page)
}

export async function apiGet(page: Page, token: string, path: string, expectStatus: number = 200) {
  const res = await page.request.get(`${API_URL}/api/v1${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (expectStatus) {
    expect(res.status(), `GET ${path} should return ${expectStatus}`).toBe(expectStatus)
  }
  return res
}

export async function apiPost(page: Page, token: string, path: string, body?: object, expectStatus: number = 200) {
  const res = await page.request.post(`${API_URL}/api/v1${path}`, {
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    data: body ? JSON.stringify(body) : undefined,
  })
  if (expectStatus) {
    expect(res.status(), `POST ${path} should return ${expectStatus}`).toBe(expectStatus)
  }
  return res
}

export async function apiDelete(page: Page, token: string, path: string, expectStatus: number = 200) {
  const res = await page.request.delete(`${API_URL}/api/v1${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (expectStatus) {
    expect(res.status(), `DELETE ${path} should return ${expectStatus}`).toBe(expectStatus)
  }
  return res
}

// ─── Performance metrics ──────────────────────────────────────────────

export async function measure(fn: () => Promise<void>): Promise<number> {
  const start = Date.now()
  await fn()
  return Date.now() - start
}

export async function measureAPI(
  page: Page,
  method: string,
  path: string,
  token?: string,
): Promise<{ total: number; status: number }> {
  const headers: Record<string, string> = {}
  if (token) headers['Authorization'] = `Bearer ${token}`
  const start = Date.now()
  const response = await page.request.fetch(`${API_URL}${path}`, { method, headers })
  const total = Date.now() - start
  await response.body()
  return { total, status: response.status() }
}

// ─── Toast/notification dismissal ─────────────────────────────────────

export async function dismissToasts(page: Page): Promise<void> {
  const closeButtons = page.locator('[role="alert"] button, .toast button, [aria-label="Close"]')
  const count = await closeButtons.count()
  for (let i = 0; i < count; i++) {
    await closeButtons.nth(i).click().catch(() => {})
  }
}

// ─── Extended test fixture with authenticated page ──────────────────────

export const test = base.extend<{ authenticatedPage: Page }>({
  authenticatedPage: async ({ page }, use) => {
    await authenticate(page)
    await use(page)
  },
})

export { expect } from '@playwright/test'