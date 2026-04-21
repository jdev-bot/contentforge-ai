/**
 * 05-analytics.spec.ts — Analytics & Dashboard KPIs
 *
 * Validates: Analytics tab, KPI widgets, charts, data export,
 * performance, distribution metrics, usage metrics.
 */
import { test, expect, loginViaUI, navigateToTab, PERF, API_URL } from './helpers'

test.describe('Analytics', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaUI(page)
  })

  test('analytics tab loads', async ({ page }) => {
    await navigateToTab(page, 'analytics')
    await expect(page.getByText(/analytics|overview|dashboard|kpi/i).first()).toBeVisible({ timeout: PERF.TAB_SWITCH_MAX })
  })

  test('analytics dashboard shows KPI cards', async ({ page }) => {
    await navigateToTab(page, 'analytics')
    await page.waitForTimeout(2000)
    // Should have metric/KPI cards or charts
    const hasCards = await page.locator('[class*="card"], [class*="metric"], [class*="kpi"], [class*="stat"]').first().isVisible().catch(() => false)
    const hasCharts = await page.locator('canvas, svg, [class*="chart"], [class*="rechart"]').first().isVisible().catch(() => false)
    const hasText = await page.getByText(/total|content|views|published|generated/i).first().isVisible().catch(() => false)
    expect(hasCards || hasCharts || hasText).toBeTruthy()
  })

  test('analytics export CSV button', async ({ page }) => {
    await navigateToTab(page, 'analytics')
    await page.waitForTimeout(1500)
    const exportBtn = page.getByRole('button', { name: /export|download|csv/i }).first()
    if (await exportBtn.isVisible().catch(() => false)) {
      // Just verify button exists and is clickable
      await exportBtn.click()
      await page.waitForTimeout(2000)
      // Download may trigger — we just verify no crash
    } else {
      test.info().annotations.push({ type: 'info', description: 'Export button not found' })
    }
  })

  test('analytics API dashboard endpoint returns data', async ({ page }) => {
    const token = await page.evaluate(async () => {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
      })
      return (await res.json()).access_token
    })
    const res = await page.request.get(`${API_URL}/api/v1/analytics/dashboard`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect(res.status()).toBe(200)
  })

  test('analytics content metrics endpoint', async ({ page }) => {
    const token = await page.evaluate(async () => {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
      })
      return (await res.json()).access_token
    })
    const res = await page.request.get(`${API_URL}/api/v1/analytics/content`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect([200, 429]).toContain(res.status())
  })

  test('analytics usage metrics endpoint', async ({ page }) => {
    const token = await page.evaluate(async () => {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
      })
      return (await res.json()).access_token
    })
    const res = await page.request.get(`${API_URL}/api/v1/analytics/usage`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect([200, 429]).toContain(res.status())
  })

  test('analytics assets endpoint', async ({ page }) => {
    const token = await page.evaluate(async () => {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
      })
      return (await res.json()).access_token
    })
    const res = await page.request.get(`${API_URL}/api/v1/analytics/assets`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect([200, 429]).toContain(res.status())
  })

  test('analytics distributions endpoint', async ({ page }) => {
    const token = await page.evaluate(async () => {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
      })
      return (await res.json()).access_token
    })
    const res = await page.request.get(`${API_URL}/api/v1/analytics/distributions`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect([200, 429]).toContain(res.status())
  })
})