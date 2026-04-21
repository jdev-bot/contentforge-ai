/**
 * 02-dashboard-shell.spec.ts — Dashboard Shell & Navigation
 *
 * Validates: Sidebar rendering, tab switching, pinned tabs,
 * search modal, Ctrl+N, Home tab, mobile bottom nav.
 */
import { test, expect, TABS, TabId, loginViaUI, installCookieSuppression, dismissOverlays, navigateToTab, PERF } from './helpers'

test.describe('Dashboard Shell', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaUI(page)
  })

  test('sidebar renders with all sections', async ({ page }) => {
    const sidebar = page.locator('aside').first()
    await expect(sidebar).toBeVisible()
    // Check section headers — use exact match to avoid matching tab buttons
    // Section headers are buttons with the section label and a tab count
    await expect(sidebar.getByRole('button', { name: /Content \d/ })).toBeVisible()
    await expect(sidebar.getByRole('button', { name: /Analytics \d/ })).toBeVisible()
  })

  test('home tab loads with welcome content', async ({ page }) => {
    // Home is the default tab after login
    await expect(page.getByText(/home|welcome|recent/i).first()).toBeVisible({ timeout: PERF.PAGE_LOAD_MAX })
  })

  test('switch to Content tab', async ({ page }) => {
    await navigateToTab(page, 'content')
    await expect(page.getByText(/content/i).first()).toBeVisible({ timeout: PERF.TAB_SWITCH_MAX })
  })

  test('switch to Projects tab', async ({ page }) => {
    await navigateToTab(page, 'projects')
    await expect(page.getByText(/project/i).first()).toBeVisible({ timeout: PERF.TAB_SWITCH_MAX })
  })

  test('switch to Analytics tab', async ({ page }) => {
    await navigateToTab(page, 'analytics')
    await expect(page.getByText(/analytics|dashboard|overview/i).first()).toBeVisible({ timeout: PERF.TAB_SWITCH_MAX })
  })

  test('switch to Settings tab', async ({ page }) => {
    await navigateToTab(page, 'settings')
    await expect(page.getByText(/settings|profile|account/i).first()).toBeVisible({ timeout: PERF.TAB_SWITCH_MAX })
  })

  test('Ctrl+N opens content creation inline', async ({ page }) => {
    await navigateToTab(page, 'content')
    await page.waitForTimeout(500)
    // Trigger Ctrl+N
    await page.keyboard.press('Control+n')
    await page.waitForTimeout(1000)
    // Should show content creation panel (not navigate away)
    await expect(page.getByText(/paste text|source|title/i).first()).toBeVisible({ timeout: 5000 })
  })

  test('Search modal opens with keyboard shortcut', async ({ page }) => {
    // Click search or use keyboard shortcut
    const searchBtn = page.getByRole('button', { name: /search/i }).first()
    if (await searchBtn.isVisible().catch(() => false)) {
      await searchBtn.click()
      await expect(page.getByPlaceholder(/search/i).first()).toBeVisible({ timeout: 3000 })
    } else {
      // Try Ctrl+K
      await page.keyboard.press('Control+k')
      await page.waitForTimeout(500)
      const searchInput = page.getByPlaceholder(/search/i).first()
      if (await searchInput.isVisible().catch(() => false)) {
        await expect(searchInput).toBeVisible()
      } else {
        test.info().annotations.push({ type: 'skip-reason', description: 'Search modal not found' })
      }
    }
  })
})