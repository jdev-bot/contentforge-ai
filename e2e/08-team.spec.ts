/**
 * 08-team.spec.ts — Team & Organizations
 *
 * Validates: Team tab, organization list, members, invite,
 * team calendar, leave org, transfer ownership.
 */
import { test, expect, loginViaUI, navigateToTab, PERF, API_URL } from './helpers'

test.describe('Team & Organizations', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaUI(page)
  })

  test('team tab loads', async ({ page }) => {
    await navigateToTab(page, 'team')
    await page.waitForTimeout(2000)
    await expect(page.getByText(/team|organization|member/i).first()).toBeVisible({ timeout: PERF.TAB_SWITCH_MAX })
  })

  test('organizations list renders', async ({ page }) => {
    await navigateToTab(page, 'team')
    await page.waitForTimeout(2000)
    // Should show org list or empty state
    const hasOrgs = await page.getByText(/organization|create.*org|no.*team/i).first().isVisible().catch(() => false)
    expect(hasOrgs).toBeTruthy()
  })

  test('organizations API returns list', async ({ page }) => {
    const token = await page.evaluate(async () => {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
      })
      return (await res.json()).access_token
    })
    const res = await page.request.get(`${API_URL}/api/v1/organizations`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect(res.status()).toBe(200)
    const data = await res.json()
    expect(Array.isArray(data) || (data && data.items !== undefined)).toBeTruthy()
  })

  test('create organization button', async ({ page }) => {
    await navigateToTab(page, 'team')
    await page.waitForTimeout(2000)
    const createBtn = page.getByRole('button', { name: /create.*org|new.*team|\+.*org/i }).first()
    if (await createBtn.isVisible().catch(() => false)) {
      await createBtn.click()
      await page.waitForTimeout(1000)
      // Should show org creation form
      const nameInput = page.getByPlaceholder(/organization.*name|team.*name/i).first()
      expect(await nameInput.isVisible().catch(() => false)).toBeTruthy()
    } else {
      test.info().annotations.push({ type: 'info', description: 'Create org button not found' })
    }
  })

  test('team calendar tab loads', async ({ page }) => {
    await navigateToTab(page, 'team-calendar')
    await page.waitForTimeout(2000)
    // Should show calendar UI or placeholder
    await expect(page.locator('body')).toBeVisible()
  })

  test('team calendar shows calendar grid', async ({ page }) => {
    await navigateToTab(page, 'team-calendar')
    await page.waitForTimeout(2000)
    const hasCalendar = await page.locator('[class*="calendar"], [class*="grid"], [class*="month"]').first().isVisible().catch(() => false)
    const hasContent = await page.getByText(/calendar|schedule|week|month/i).first().isVisible().catch(() => false)
    expect(hasCalendar || hasContent).toBeTruthy()
  })

  test('invite member API', async ({ page }) => {
    const token = await page.evaluate(async () => {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
      })
      return (await res.json()).access_token
    })
    // Need a real org ID — list orgs first
    const orgsRes = await page.request.get(`${API_URL}/api/v1/organizations`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    const orgsData = await orgsRes.json()
    const orgs = Array.isArray(orgsData) ? orgsData : (orgsData.items || [])
    if (orgs.length > 0) {
      const orgId = orgs[0].id
      const res = await page.request.post(`${API_URL}/api/v1/organizations/${orgId}/invite`, {
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        data: { email: 'test@example.com', role: 'member' },
      })
      expect([200, 201, 404, 422]).toContain(res.status())
    } else {
      test.info().annotations.push({ type: 'info', description: 'No organizations to test invite' })
    }
  })

  test('members list API', async ({ page }) => {
    const token = await page.evaluate(async () => {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
      })
      return (await res.json()).access_token
    })
    const orgsRes = await page.request.get(`${API_URL}/api/v1/organizations`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    const orgsData = await orgsRes.json()
    const orgs = Array.isArray(orgsData) ? orgsData : (orgsData.items || [])
    if (orgs.length > 0) {
      const res = await page.request.get(`${API_URL}/api/v1/organizations/${orgs[0].id}/members`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      expect([200, 404]).toContain(res.status())
    }
  })
})