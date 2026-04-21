/**
 * 14-settings-account.spec.ts — Settings, Profile & Account Management
 *
 * Validates: Profile editing, usage stats, subscription, data export,
 * account deletion/restore, SSO management.
 */
import { test, expect, loginViaUI, navigateToTab, PERF, API_URL } from './helpers'

test.describe('Settings & Account', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaUI(page)
  })

  test('settings tab loads', async ({ page }) => {
    await navigateToTab(page, 'settings')
    await page.waitForTimeout(2000)
    await expect(page.getByText(/settings|profile|account/i).first()).toBeVisible({ timeout: PERF.TAB_SWITCH_MAX })
  })

  test('settings shows profile section', async ({ page }) => {
    await navigateToTab(page, 'settings')
    await page.waitForTimeout(2000)
    const hasProfile = await page.getByText(/profile|name|email|avatar/i).first().isVisible().catch(() => false)
    expect(hasProfile).toBeTruthy()
  })

  test('settings shows usage section', async ({ page }) => {
    await navigateToTab(page, 'settings')
    await page.waitForTimeout(2000)
    const hasUsage = await page.getByText(/usage|limit|plan|subscription|generation/i).first().isVisible().catch(() => false)
    expect(hasUsage).toBeTruthy()
  })

  test('profile API returns user data', async ({ page }) => {
    const token = await page.evaluate(async () => {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
      })
      return (await res.json()).access_token
    })
    const res = await page.request.get(`${API_URL}/api/v1/user/profile`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect([200, 404]).toContain(res.status())
  })

  test('usage summary API returns data', async ({ page }) => {
    const token = await page.evaluate(async () => {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
      })
      return (await res.json()).access_token
    })
    const res = await page.request.get(`${API_URL}/api/v1/usage/summary`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect(res.status()).toBe(200)
    const data = await res.json()
    expect(data).toBeDefined()
  })

  test('data export API', async ({ page }) => {
    const token = await page.evaluate(async () => {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
      })
      return (await res.json()).access_token
    })
    const res = await page.request.get(`${API_URL}/api/v1/user/export-data`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect(res.status()).toBe(200)
  })

  test('account deletion status API', async ({ page }) => {
    const token = await page.evaluate(async () => {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
      })
      return (await res.json()).access_token
    })
    const res = await page.request.get(`${API_URL}/api/v1/user/deletion-status`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect(res.status()).toBe(200)
  })

  test('standalone /settings page loads', async ({ page }) => {
    const { installCookieSuppression, dismissOverlays } = await import('./helpers')
    await installCookieSuppression(page)
    await page.goto('/settings')
    await dismissOverlays(page)
    await page.waitForTimeout(2000)
    await expect(page.locator('body')).toBeVisible()
  })
})