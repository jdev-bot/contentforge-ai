# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 16-standalone-pages.spec.ts >> Standalone Pages >> pricing page loads
- Location: 16-standalone-pages.spec.ts:10:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByText(/price|plan|tier|free|pro/i).first()
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByText(/price|plan|tier|free|pro/i).first()

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - alert [ref=e2]
  - generic [ref=e4]:
    - generic [ref=e11]:
      - generic [ref=e12]:
        - generic [ref=e14]:
          - img [ref=e15]
          - text: "New: AI Content Generation"
        - heading "Transform Your Content With AI Power" [level=1] [ref=e18]:
          - text: Transform Your Content
          - text: With AI Power
        - paragraph [ref=e19]: Create, repurpose, and distribute content across 20+ formats in minutes, not hours.
      - generic [ref=e20]:
        - generic [ref=e21]:
          - img [ref=e23]
          - generic [ref=e26]: AI-powered content transformation
        - generic [ref=e27]:
          - img [ref=e29]
          - generic [ref=e31]: 20+ content formats supported
        - generic [ref=e32]:
          - img [ref=e34]
          - generic [ref=e36]: Enterprise-grade security
      - generic [ref=e37]:
        - paragraph [ref=e38]: Trusted by teams at
        - generic [ref=e39]:
          - generic [ref=e40]: Google
          - generic [ref=e41]: Meta
          - generic [ref=e42]: Netflix
          - generic [ref=e43]: Spotify
    - generic [ref=e45]:
      - generic [ref=e46]:
        - generic [ref=e47]:
          - heading "Welcome Back" [level=3] [ref=e48]
          - paragraph [ref=e49]: Sign in to access your content workspace
          - generic [ref=e50]:
            - img [ref=e51]
            - generic [ref=e54]: Invite-only access — Contact an admin for an account.
        - generic [ref=e55]:
          - generic [ref=e56]:
            - button "Sign in with GitHub" [ref=e57]:
              - img [ref=e58]
            - button "Sign in with Twitter" [ref=e60]:
              - img [ref=e61]
            - button "Sign in with Email" [ref=e63]:
              - img [ref=e64]
          - generic [ref=e71]: Or continue with email
          - generic [ref=e72]:
            - generic [ref=e73]:
              - generic [ref=e74]: Email Address
              - textbox "Email Address" [ref=e76]:
                - /placeholder: you@example.com
            - generic [ref=e77]:
              - generic [ref=e78]: Password
              - generic [ref=e79]:
                - textbox "Password" [ref=e80]:
                  - /placeholder: ••••••••
                - button [ref=e82]:
                  - img [ref=e83]
            - button "Sign In" [ref=e86]:
              - generic [ref=e87]: Sign In
          - paragraph [ref=e89]:
            - text: Don't have an account?
            - button "Sign Up" [ref=e90]
      - paragraph [ref=e91]: © 2024 ContentForge AI. All rights reserved.
  - region "Notifications"
```

# Test source

```ts
  1   | /**
  2   |  * 16-standalone-pages.spec.ts — Standalone Pages & Edge Cases
  3   |  *
  4   |  * Validates: Pricing page, legal pages, onboarding, SSO page,
  5   |  * 404 handling, direct URL access to content pages.
  6   |  */
  7   | import { test, expect, installCookieSuppression, dismissOverlays } from './helpers'
  8   | 
  9   | test.describe('Standalone Pages', () => {
  10  |   test('pricing page loads', async ({ page }) => {
  11  |     await installCookieSuppression(page)
  12  |     await page.goto('/pricing')
  13  |     await dismissOverlays(page)
  14  |     await page.waitForTimeout(2000)
> 15  |     await expect(page.getByText(/price|plan|tier|free|pro/i).first()).toBeVisible({ timeout: 5000 })
      |                                                                       ^ Error: expect(locator).toBeVisible() failed
  16  |   })
  17  | 
  18  |   test('privacy policy page loads', async ({ page }) => {
  19  |     await page.goto('/legal/privacy')
  20  |     await page.waitForTimeout(2000)
  21  |     await expect(page.getByText(/privacy|data|information/i).first()).toBeVisible()
  22  |   })
  23  | 
  24  |   test('terms of service page loads', async ({ page }) => {
  25  |     await page.goto('/legal/terms')
  26  |     await page.waitForTimeout(2000)
  27  |     await expect(page.getByText(/terms|service|agreement/i).first()).toBeVisible()
  28  |   })
  29  | 
  30  |   test('cookie policy page loads', async ({ page }) => {
  31  |     await page.goto('/legal/cookies')
  32  |     await page.waitForTimeout(2000)
  33  |     await expect(page.getByText(/cookie|tracking|consent/i).first()).toBeVisible()
  34  |   })
  35  | 
  36  |   test('DMCA page loads', async ({ page }) => {
  37  |     await page.goto('/legal/dmca')
  38  |     await page.waitForTimeout(2000)
  39  |     await expect(page.getByText(/dmca|copyright|infringement/i).first()).toBeVisible()
  40  |   })
  41  | 
  42  |   test('SSO page loads without crash', async ({ page }) => {
  43  |     await page.goto('/sso')
  44  |     await page.waitForTimeout(2000)
  45  |     // SSO page should load without error, even if empty
  46  |     await expect(page.locator('body')).toBeVisible()
  47  |   })
  48  | 
  49  |   test('standalone /content/new page loads', async ({ page }) => {
  50  |     const { loginViaUI } = await import('./helpers')
  51  |     await loginViaUI(page)
  52  |     // Navigate directly to content creation page
  53  |     await page.goto('/content/new')
  54  |     await page.waitForTimeout(3000)
  55  |     // Should show content creation form (server-authed)
  56  |     await expect(page.locator('body')).toBeVisible()
  57  |   })
  58  | 
  59  |   test('standalone /content/[id] page handles missing content', async ({ page }) => {
  60  |     const { loginViaUI } = await import('./helpers')
  61  |     await loginViaUI(page)
  62  |     await page.goto('/content/nonexistent-id')
  63  |     await page.waitForTimeout(3000)
  64  |     // Should show error or redirect, not crash
  65  |     await expect(page.locator('body')).toBeVisible()
  66  |   })
  67  | 
  68  |   test('onboarding page redirects or loads', async ({ page }) => {
  69  |     await installCookieSuppression(page)
  70  |     await page.goto('/onboarding')
  71  |     await page.waitForTimeout(2000)
  72  |     // May redirect to login or show onboarding
  73  |     const url = page.url()
  74  |     expect(url).toMatch(/\/(onboarding|login)/)
  75  |   })
  76  | 
  77  |   test('payment/success page loads', async ({ page }) => {
  78  |     await installCookieSuppression(page)
  79  |     await page.goto('/payment/success')
  80  |     await page.waitForTimeout(2000)
  81  |     await expect(page.locator('body')).toBeVisible()
  82  |   })
  83  | 
  84  |   test('payment/cancel page loads', async ({ page }) => {
  85  |     await installCookieSuppression(page)
  86  |     await page.goto('/payment/cancel')
  87  |     await page.waitForTimeout(2000)
  88  |     await expect(page.locator('body')).toBeVisible()
  89  |   })
  90  | 
  91  |   test('404 page for unknown routes', async ({ page }) => {
  92  |     await installCookieSuppression(page)
  93  |     await page.goto('/this-route-does-not-exist')
  94  |     await page.waitForTimeout(2000)
  95  |     // Should show 404 or redirect, not crash
  96  |     await expect(page.locator('body')).toBeVisible()
  97  |   })
  98  | 
  99  |   test('cookie consent banner appears and can be dismissed', async ({ page }) => {
  100 |     // DON'T install cookie suppression — test the real banner
  101 |     await page.goto('/login')
  102 |     await page.waitForTimeout(2000)
  103 |     // Should show cookie banner after ~1s delay
  104 |     const acceptBtn = page.getByRole('button', { name: /accept/i }).first()
  105 |     if (await acceptBtn.isVisible().catch(() => false)) {
  106 |       await acceptBtn.click()
  107 |       await page.waitForTimeout(500)
  108 |       // Banner should be gone
  109 |       await expect(acceptBtn).not.toBeVisible()
  110 |     }
  111 |   })
  112 | 
  113 |   test('staging banner appears and can be dismissed', async ({ page }) => {
  114 |     const { loginViaUI } = await import('./helpers')
  115 |     // Login without suppressing staging banner
```