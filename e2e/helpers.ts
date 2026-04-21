/**
 * Shared test utilities for ContentForge AI E2E tests.
 *
 * Provides authenticated page setup, performance metrics helpers,
 * and common selectors used across the test suite.
 */
import { Page, expect } from '@playwright/test'

// ─── Test credentials ────────────────────────────────────────────────
export const TEST_USER = {
  email: 'test@neo.dev',
  password: 'Test1234!',
}

export const BASE_URL = process.env.E2E_BASE_URL || 'https://frontend-theta-seven-65.vercel.app'
export const API_URL = process.env.E2E_API_URL || 'https://contentforge-ai-api.onrender.com'

// ─── Performance thresholds (milliseconds) ───────────────────────────
// These are generous for staging on Render free tier.
export const PERF = {
  LOGIN_MAX: 8_000,            // Login + redirect
  PAGE_LOAD_MAX: 5_000,        // First meaningful paint after login
  TAB_SWITCH_MAX: 3_000,       // Switching between tabs
  API_CALL_MAX: 4_000,         // Individual API call
  CONTENT_DETAIL_MAX: 5_000,   // Opening a content item
  CONTENT_CREATE_MAX: 15_000,   // Creating content (Render cold start can take 9+ seconds)
  INIT_ENDPOINT_MAX: 3_000,    // Batch /init endpoint (warm)
  COLD_START_MAX: 10_000,      // First request after idle (cold start)
}

// ─── Overlay dismissal ──────────────────────────────────────────────

/**
 * Install an init script that sets localStorage BEFORE any page loads,
 * preventing the cookie consent banner from ever appearing.
 * Call this once per test (typically in beforeEach).
 */
export async function installCookieSuppression(page: Page): Promise<void> {
  await page.addInitScript(() => {
    localStorage.setItem('contentforge-cookie-consent', 'true')
  })
}

/**
 * Dismiss overlays (cookie banner, staging banner) that may block interactions.
 * Call this after any page navigation to ensure the page is usable.
 * The cookie banner has a 1-second delay before showing, so we wait for it.
 */
export async function dismissOverlays(page: Page): Promise<void> {
  // Dismiss staging banner if present
  const dismissBanner = page.getByRole('button', { name: 'Dismiss staging banner', exact: true })
  if (await dismissBanner.isVisible().catch(() => false)) {
    await dismissBanner.click()
    await page.waitForTimeout(300)
  }
  // Cookie banner has a 1s delay before appearing — wait up to 2.5s for it
  const acceptCookies = page.getByRole('button', { name: 'Accept All', exact: true })
  try {
    await acceptCookies.waitFor({ state: 'visible', timeout: 2500 })
    await acceptCookies.click()
    await page.waitForTimeout(300)
  } catch {
    // Cookie banner not visible within timeout — already dismissed or not present
  }
}

// ─── Auth helpers ─────────────────────────────────────────────────────

/**
 * Log in via the UI and return the authenticated page.
 * Asserts that login succeeds and we reach the dashboard.
 * Dismisses cookie consent and staging banner overlays.
 */
export async function loginViaUI(page: Page): Promise<void> {
  // Install cookie suppression BEFORE any page loads so the banner never appears
  await installCookieSuppression(page)

  await page.goto('/login')

  // Dismiss any remaining overlays (staging banner)
  await dismissOverlays(page)

  // Use getByRole('textbox') to avoid matching social login buttons
  await page.getByRole('textbox', { name: 'Email Address' }).fill(TEST_USER.email)
  await page.getByRole('textbox', { name: 'Password' }).fill(TEST_USER.password)
  await page.getByRole('button', { name: 'Sign In', exact: true }).click()

  // Should redirect to dashboard (home) — login uses window.location.href = '/'
  await page.waitForURL(url => url.pathname === '/', { timeout: PERF.LOGIN_MAX })

  // Dismiss any remaining overlays (staging banner)
  await dismissOverlays(page)

  // Dashboard should be visible
  await expect(page.getByText(/home|dashboard|welcome/i).first()).toBeVisible({ timeout: PERF.PAGE_LOAD_MAX })
}

/**
 * Navigate to a URL and dismiss any overlays that appear.
 * Cookie suppression should already be installed via installCookieSuppression() in loginViaUI.
 * Use this instead of page.goto() to handle cookie consent dialogs.
 */
export async function navigateTo(page: Page, url: string): Promise<void> {
  // addInitScript only needs to be called once per page context,
  // but calling it multiple times is safe (it's idempotent).
  // However, since we already install it in loginViaUI, we just navigate.
  await page.goto(url)
  await dismissOverlays(page)
}

/**
 * Log in via API and inject the session cookies into the page.
 * Faster than UI login — used for tests that don't need to test login flow.
 */
export async function loginViaAPI(page: Page): Promise<string> {
  const response = await page.request.post(`${BASE_URL}/api/v1/auth/login`, {
    data: { email: TEST_USER.email, password: TEST_USER.password },
    headers: { 'Content-Type': 'application/json' },
  })
  expect(response.ok(), 'Login API should succeed').toBeTruthy()
  const body = await response.json()
  expect(body.access_token, 'Should return access token').toBeDefined()
  return body.access_token as string
}

/**
 * Authenticate page by logging in via UI, then waiting for the dashboard to load.
 */
export async function authenticate(page: Page): Promise<void> {
  await loginViaUI(page)
}

// ─── Performance metrics ─────────────────────────────────────────────

/**
 * Measure the time for a navigation/action and return milliseconds.
 */
export async function measure(fn: () => Promise<void>): Promise<number> {
  const start = Date.now()
  await fn()
  return Date.now() - start
}

/**
 * Measure API response time from the staging backend.
 * Returns { ttfb, total, status }.
 */
export async function measureAPI(
  page: Page,
  method: string,
  path: string,
  token?: string,
): Promise<{ ttfb: number; total: number; status: number }> {
  const headers: Record<string, string> = {}
  if (token) headers['Authorization'] = `Bearer ${token}`

  const start = Date.now()
  const response = await page.request.fetch(`${API_URL}${path}`, { method, headers })
  const total = Date.now() - start
  await response.body()

  return { ttfb: total, total, status: response.status() }
}

// ─── DOM helpers ─────────────────────────────────────────────────────

/**
 * Wait for the dashboard to be fully loaded (sidebar visible).
 */
export async function waitForDashboard(page: Page): Promise<void> {
  await expect(page.locator('nav, [role="navigation"], aside').first()).toBeVisible({ timeout: PERF.PAGE_LOAD_MAX })
}

/**
 * Get all visible sidebar tab buttons.
 */
export function getSidebarTabs(page: Page) {
  return page.locator('[role="tab"], nav button, aside button').filter({ hasNot: page.locator('.sr-only') })
}

/**
 * Click a sidebar tab by name (case-insensitive partial match).
 */
export async function clickTab(page: Page, tabName: string): Promise<void> {
  const tab = page.locator('button, [role="tab"]').filter({ hasText: new RegExp(tabName, 'i') }).first()
  await tab.click()
  await page.waitForTimeout(500)
}

/**
 * Dismiss any toast/notification that might block interactions.
 */
export async function dismissToasts(page: Page): Promise<void> {
  const closeButtons = page.locator('[role="alert"] button, .toast button, [aria-label="Close"]')
  const count = await closeButtons.count()
  for (let i = 0; i < count; i++) {
    await closeButtons.nth(i).click().catch(() => {})
  }
}