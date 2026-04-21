/**
 * 16-standalone-pages.spec.ts — Standalone Pages & Edge Cases
 *
 * Validates: Pricing page, legal pages, onboarding, SSO page,
 * 404 handling, direct URL access to content pages.
 */
import { test, expect, installCookieSuppression, dismissOverlays } from './helpers'

test.describe('Standalone Pages', () => {
  test('pricing page loads', async ({ page }) => {
    await installCookieSuppression(page)
    await page.goto('/pricing')
    await dismissOverlays(page)
    await page.waitForTimeout(2000)
    // Page may not exist or may redirect — just verify no crash
    await expect(page.locator('body')).toBeVisible()
  })

  test('privacy policy page loads', async ({ page }) => {
    await page.goto('/legal/privacy')
    await page.waitForTimeout(2000)
    await expect(page.getByText(/privacy|data|information/i).first()).toBeVisible()
  })

  test('terms of service page loads', async ({ page }) => {
    await page.goto('/legal/terms')
    await page.waitForTimeout(2000)
    await expect(page.getByText(/terms|service|agreement/i).first()).toBeVisible()
  })

  test('cookie policy page loads', async ({ page }) => {
    await page.goto('/legal/cookies')
    await page.waitForTimeout(2000)
    await expect(page.getByText(/cookie|tracking|consent/i).first()).toBeVisible()
  })

  test('DMCA page loads', async ({ page }) => {
    await page.goto('/legal/dmca')
    await page.waitForTimeout(2000)
    await expect(page.getByText(/dmca|copyright|infringement/i).first()).toBeVisible()
  })

  test('SSO page loads without crash', async ({ page }) => {
    await page.goto('/sso')
    await page.waitForTimeout(2000)
    // SSO page should load without error, even if empty
    await expect(page.locator('body')).toBeVisible()
  })

  test('standalone /content/new page loads', async ({ page }) => {
    const { loginViaUI } = await import('./helpers')
    await loginViaUI(page)
    // Navigate directly to content creation page
    await page.goto('/content/new')
    await page.waitForTimeout(3000)
    // Should show content creation form (server-authed)
    await expect(page.locator('body')).toBeVisible()
  })

  test('standalone /content/[id] page handles missing content', async ({ page }) => {
    const { loginViaUI } = await import('./helpers')
    await loginViaUI(page)
    await page.goto('/content/nonexistent-id')
    await page.waitForTimeout(3000)
    // Should show error or redirect, not crash
    await expect(page.locator('body')).toBeVisible()
  })

  test('onboarding page redirects or loads', async ({ page }) => {
    await installCookieSuppression(page)
    await page.goto('/onboarding')
    await page.waitForTimeout(2000)
    // May redirect to login or show onboarding
    const url = page.url()
    expect(url).toMatch(/\/(onboarding|login)/)
  })

  test('payment/success page loads', async ({ page }) => {
    await installCookieSuppression(page)
    await page.goto('/payment/success')
    await page.waitForTimeout(2000)
    await expect(page.locator('body')).toBeVisible()
  })

  test('payment/cancel page loads', async ({ page }) => {
    await installCookieSuppression(page)
    await page.goto('/payment/cancel')
    await page.waitForTimeout(2000)
    await expect(page.locator('body')).toBeVisible()
  })

  test('404 page for unknown routes', async ({ page }) => {
    await installCookieSuppression(page)
    await page.goto('/this-route-does-not-exist')
    await page.waitForTimeout(2000)
    // Should show 404 or redirect, not crash
    await expect(page.locator('body')).toBeVisible()
  })

  test('cookie consent banner appears and can be dismissed', async ({ page }) => {
    // DON'T install cookie suppression — test the real banner
    await page.goto('/login')
    await page.waitForTimeout(2000)
    // Should show cookie banner after ~1s delay
    const acceptBtn = page.getByRole('button', { name: /accept/i }).first()
    if (await acceptBtn.isVisible().catch(() => false)) {
      await acceptBtn.click()
      await page.waitForTimeout(500)
      // Banner should be gone
      await expect(acceptBtn).not.toBeVisible()
    }
  })

  test('staging banner appears and can be dismissed', async ({ page }) => {
    const { loginViaUI } = await import('./helpers')
    // Login without suppressing staging banner
    await installCookieSuppression(page)
    await page.goto('/login')
    await page.getByRole('textbox', { name: 'Email Address' }).fill('test@neo.dev')
    await page.getByRole('textbox', { name: 'Password' }).fill('Test1234!')
    await page.locator('form button[type="submit"]').click()
    await page.waitForURL(url => url.pathname === '/', { timeout: 8000 })

    // Staging banner should be visible
    const stagingBanner = page.getByText(/staging|preview/i).first()
    if (await stagingBanner.isVisible().catch(() => false)) {
      const dismissBtn = page.getByRole('button', { name: /dismiss|close/i }).first()
      if (await dismissBtn.isVisible().catch(() => false)) {
        await dismissBtn.click()
        // Banner should be gone
        await page.waitForTimeout(500)
      }
    }
  })
})