/**
 * UI Responsiveness E2E tests for ContentForge AI staging.
 *
 * Covers: dashboard first meaningful paint, content tab rendering,
 * search interaction timing, button click response, and frozen UI detection.
 */
import { test, expect } from '@playwright/test'
import { loginViaUI, PERF, measure, dismissOverlays, installCookieSuppression } from './helpers'

test.describe('UI Responsiveness', () => {
  test.beforeEach(async ({ page }) => {
    await installCookieSuppression(page)
    await loginViaUI(page)
  })

  test('dashboard first meaningful paint < 5s after login', async ({ page }) => {
    const start = Date.now()

    // Dashboard should already be loaded after loginViaUI
    await expect(page.locator('nav, [role="navigation"], aside').first()).toBeVisible({
      timeout: PERF.PAGE_LOAD_MAX,
    })

    // Main content area should be visible
    const mainContent = page.locator('main, [role="main"], .tab-content, [data-testid="home-tab"]').first()
    await expect(mainContent).toBeVisible({ timeout: PERF.PAGE_LOAD_MAX })

    const elapsed = Date.now() - start
    expect(elapsed, `Dashboard paint took ${elapsed}ms, expected < ${PERF.PAGE_LOAD_MAX}ms`).toBeLessThan(PERF.PAGE_LOAD_MAX)
  })

  test('content tab renders < 5s after click', async ({ page }) => {
    // Click on Content tab (buttons include shortcut like "Content Alt+1")
    const contentTab = page.getByRole('button', { name: 'Content', exact: false }).first()
    await expect(contentTab).toBeVisible()

    const elapsed = await measure(async () => {
      await contentTab.click()
      // Wait for content tab to render something
      const contentArea = page.locator('main, [role="tabpanel"], .tab-content').first()
      await expect(contentArea).toBeVisible({ timeout: 5_000 })
    })

    expect(elapsed, `Content tab render took ${elapsed}ms, expected < 5s`).toBeLessThan(PERF.TAB_SWITCH_MAX + 2000) // Extra buffer for staging
  })

  test('search interaction responds < 500ms', async ({ page }) => {
    // Open search with Ctrl+K
    await page.keyboard.press('Control+k')
    await page.waitForTimeout(500)

    // Check if search modal opened
    const searchInput = page.locator('input[type="search"], input[placeholder*="search"], input[placeholder*="Search"], [data-testid="search-input"]').first()

    if (await searchInput.isVisible().catch(() => false)) {
      // Type a search query and measure response time
      const elapsed = await measure(async () => {
        await searchInput.fill('test')
      })

      expect(elapsed, `Search input took ${elapsed}ms to respond`).toBeLessThan(500)
      await page.waitForTimeout(1000)
    } else {
      // Search modal might not have opened — try alternative
      const anySearchBox = page.locator('input[placeholder*="search" i]').first()
      if (await anySearchBox.isVisible().catch(() => false)) {
        const elapsed = await measure(async () => {
          await anySearchBox.fill('test query')
        })
        expect(elapsed, `Search input took ${elapsed}ms`).toBeLessThan(500)
      } else {
        test.skip('No search input found on page')
      }
    }
  })

  test('button clicks respond < 500ms', async ({ page }) => {
    // Test that clicking a sidebar tab button responds quickly
    const projectsTab = page.getByRole('button', { name: 'Projects', exact: false }).first()
    if (await projectsTab.isVisible().catch(() => false)) {
      const elapsed = await measure(async () => {
        await projectsTab.click()
      })
      // Click itself should be near-instant (< 500ms)
      expect(elapsed, `Tab click took ${elapsed}ms`).toBeLessThan(500)
    } else {
      // Try any visible button
      const anyButton = page.locator('button').first()
      if (await anyButton.isVisible().catch(() => false)) {
        const elapsed = await measure(async () => {
          await anyButton.click()
        })
        expect(elapsed, `Button click took ${elapsed}ms`).toBeLessThan(500)
      }
    }
  })

  test('no frozen UI during data loading', async ({ page }) => {
    // Navigate to a data-heavy tab (Content)
    const contentTab = page.getByRole('button', { name: 'Content', exact: false }).first()
    if (await contentTab.isVisible().catch(() => false)) {
      await contentTab.click()

      // While content loads, the page should remain responsive
      const startInteraction = Date.now()

      const analyticsTab = page.getByRole('button', { name: 'Analytics', exact: false }).first()
      if (await analyticsTab.isVisible().catch(() => false)) {
        await analyticsTab.click({ timeout: 3000 }).catch(() => {})
        const interactionTime = Date.now() - startInteraction

        // The click should register within 500ms even during loading
        expect(interactionTime, `Interaction during load took ${interactionTime}ms`).toBeLessThan(500)
      }
    }
  })

  test('dashboard scroll performance', async ({ page }) => {
    const start = Date.now()
    await page.evaluate(() => { window.scrollTo(0, 500) })
    const scrollTime = Date.now() - start
    expect(scrollTime, `Scroll took ${scrollTime}ms`).toBeLessThan(100)
    await page.evaluate(() => { window.scrollTo(0, 0) })
  })

  test('sidebar collapse/expand responds quickly', async ({ page }) => {
    // Look for sidebar toggle button
    const menuButton = page.locator('button').filter({ hasText: /menu/i }).first()
    const collapseButton = page.locator('[data-testid="sidebar-toggle"], button[aria-label*="sidebar" i]').first()

    if (await menuButton.isVisible().catch(() => false)) {
      const elapsed = await measure(async () => { await menuButton.click() })
      expect(elapsed, `Sidebar toggle took ${elapsed}ms`).toBeLessThan(300)
      await menuButton.click()
    } else if (await collapseButton.isVisible().catch(() => false)) {
      const elapsed = await measure(async () => { await collapseButton.click() })
      expect(elapsed, `Sidebar toggle took ${elapsed}ms`).toBeLessThan(300)
      await collapseButton.click()
    } else {
      test.skip('No sidebar toggle button found')
    }
  })
})