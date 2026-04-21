# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 03-content.spec.ts >> Content CRUD >> content creation form has required fields
- Location: 03-content.spec.ts:45:7

# Error details

```
Error: expect(received).toBeTruthy()

Received: false
```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - alert [ref=e2]
  - generic [ref=e4]:
    - banner [ref=e5]:
      - generic [ref=e7]:
        - button [ref=e8]:
          - img [ref=e9]
        - generic [ref=e11]: New Content
    - main [ref=e12]
  - region "Notifications"
```

# Test source

```ts
  1   | /**
  2   |  * 03-content.spec.ts — Content CRUD & Detail View
  3   |  *
  4   |  * Validates: Content list, create (paste text), detail view,
  5   |  * delete, inline panel navigation, asset generation.
  6   |  */
  7   | import { test, expect, loginViaUI, navigateToTab, PERF, API_URL, TEST_USER } from './helpers'
  8   | 
  9   | test.describe('Content CRUD', () => {
  10  |   test.beforeEach(async ({ page }) => {
  11  |     await loginViaUI(page)
  12  |   })
  13  | 
  14  |   test('content tab loads and displays list', async ({ page }) => {
  15  |     await navigateToTab(page, 'content')
  16  |     // Should show content list header or empty state
  17  |     await expect(page.getByText(/content|no content|empty/i).first()).toBeVisible({ timeout: PERF.TAB_SWITCH_MAX })
  18  |   })
  19  | 
  20  |   test('content tab shows existing items or empty state', async ({ page }) => {
  21  |     await navigateToTab(page, 'content')
  22  |     const contentArea = page.locator('main, [role="main"], .content-area').first()
  23  |     // Either content items OR empty state message
  24  |     await page.waitForTimeout(2000)
  25  |     const hasContent = await page.getByText(/create.*content|add.*content|empty|no content/i).first().isVisible()
  26  |     const hasItems = await page.locator('[data-testid="content-item"], [class*="content-card"], [class*="content-item"]').first().isVisible().catch(() => false)
  27  |     expect(hasContent || hasItems).toBeTruthy()
  28  |   })
  29  | 
  30  |   test('open content creation via inline panel', async ({ page }) => {
  31  |     await navigateToTab(page, 'content')
  32  |     await page.waitForTimeout(500)
  33  |     // Click "New Content" or similar button
  34  |     const createBtn = page.getByRole('button', { name: /new content|create content|add content|\+ content/i }).first()
  35  |     if (await createBtn.isVisible().catch(() => false)) {
  36  |       await createBtn.click()
  37  |       await page.waitForTimeout(1000)
  38  |       // Should show creation form
  39  |       await expect(page.getByText(/paste text|source type|title/i).first()).toBeVisible({ timeout: 5000 })
  40  |     } else {
  41  |       test.info().annotations.push({ type: 'skip-reason', description: 'Create content button not found' })
  42  |     }
  43  |   })
  44  | 
  45  |   test('content creation form has required fields', async ({ page }) => {
  46  |     await navigateToTab(page, 'content')
  47  |     await page.waitForTimeout(500)
  48  |     const createBtn = page.getByRole('button', { name: /new content|create content|add content/i }).first()
  49  |     if (await createBtn.isVisible().catch(() => false)) {
  50  |       await createBtn.click()
  51  |       await page.waitForTimeout(1000)
  52  |       // Check for source type selector, title input
  53  |       const sourceSelector = page.getByText(/paste text|url|file|source/i).first()
  54  |       const titleInput = page.getByPlaceholder(/title|name/i).first()
  55  |       const hasSource = await sourceSelector.isVisible().catch(() => false)
  56  |       const hasTitle = await titleInput.isVisible().catch(() => false)
> 57  |       expect(hasSource || hasTitle).toBeTruthy()
      |                                     ^ Error: expect(received).toBeTruthy()
  58  |     }
  59  |   })
  60  | 
  61  |   test('create content with paste text (if usage available)', async ({ page }) => {
  62  |     // Check usage first
  63  |     const token = await page.evaluate(async () => {
  64  |       const res = await fetch('/api/v1/usage/summary')
  65  |       if (!res.ok) return null
  66  |       const data = await res.json()
  67  |       return data
  68  |     })
  69  |     if (token && token.monthly_usage_count >= token.monthly_usage_limit) {
  70  |       test.skip('Monthly usage limit reached')
  71  |       return
  72  |     }
  73  | 
  74  |     await navigateToTab(page, 'content')
  75  |     await page.waitForTimeout(500)
  76  |     const createBtn = page.getByRole('button', { name: /new content|create content|add content/i }).first()
  77  |     if (!(await createBtn.isVisible().catch(() => false))) {
  78  |       test.skip('Create button not found')
  79  |       return
  80  |     }
  81  |     await createBtn.click()
  82  |     await page.waitForTimeout(1500)
  83  | 
  84  |     // Select "Paste Text" source type
  85  |     const pasteBtn = page.getByRole('button', { name: /paste text/i }).first()
  86  |     if (await pasteBtn.isVisible().catch(() => false)) {
  87  |       await pasteBtn.click()
  88  |     }
  89  | 
  90  |     // Fill title
  91  |     const titleInput = page.getByPlaceholder(/title/i).first()
  92  |     if (await titleInput.isVisible().catch(() => false)) {
  93  |       await titleInput.fill('E2E Test Content')
  94  |     }
  95  | 
  96  |     // Fill content textarea
  97  |     const textarea = page.getByPlaceholder(/paste.*text|content|body/i).first()
  98  |     if (await textarea.isVisible().catch(() => false)) {
  99  |       await textarea.fill('This is test content created by the E2E test suite.')
  100 |     }
  101 | 
  102 |     // Submit
  103 |     const submitBtn = page.getByRole('button', { name: /add content|create|submit|generate/i }).first()
  104 |     if (await submitBtn.isVisible().catch(() => false)) {
  105 |       await submitBtn.click()
  106 |       // Wait for success or error
  107 |       await page.waitForTimeout(3000)
  108 |       // Should either navigate to content detail or show in list
  109 |     }
  110 |   })
  111 | 
  112 |   test('click content item opens detail panel', async ({ page }) => {
  113 |     await navigateToTab(page, 'content')
  114 |     await page.waitForTimeout(2000)
  115 |     // Find a content item to click
  116 |     const contentItem = page.locator('[class*="content-card"], [class*="content-item"], [data-testid="content-item"]').first()
  117 |     if (await contentItem.isVisible().catch(() => false)) {
  118 |       await contentItem.click()
  119 |       await page.waitForTimeout(1500)
  120 |       // Should show content detail (inline panel or separate view)
  121 |       await expect(page.getByText(/edit|delete|publish|share|content/i).first()).toBeVisible({ timeout: 5000 })
  122 |     } else {
  123 |       test.info().annotations.push({ type: 'skip-reason', description: 'No content items to click' })
  124 |     }
  125 |   })
  126 | 
  127 |   test('content detail shows back navigation', async ({ page }) => {
  128 |     await navigateToTab(page, 'content')
  129 |     await page.waitForTimeout(2000)
  130 |     const contentItem = page.locator('[class*="content-card"], [class*="content-item"], [data-testid="content-item"]').first()
  131 |     if (await contentItem.isVisible().catch(() => false)) {
  132 |       await contentItem.click()
  133 |       await page.waitForTimeout(1500)
  134 |       // Back button should exist
  135 |       const backBtn = page.getByRole('button', { name: /back|←|arrow/i }).first()
  136 |       expect(await backBtn.isVisible().catch(() => false) || await page.getByText(/back/i).first().isVisible().catch(() => false)).toBeTruthy()
  137 |     } else {
  138 |       test.info().annotations.push({ type: 'skip-reason', description: 'No content items' })
  139 |     }
  140 |   })
  141 | 
  142 |   test('content tab search/filter works', async ({ page }) => {
  143 |     await navigateToTab(page, 'content')
  144 |     await page.waitForTimeout(1500)
  145 |     // Look for search input in content tab
  146 |     const searchInput = page.getByPlaceholder(/search.*content|filter/i).first()
  147 |     if (await searchInput.isVisible().catch(() => false)) {
  148 |       await searchInput.fill('test')
  149 |       await page.waitForTimeout(1000)
  150 |       // Should filter content list
  151 |       const visibleItems = await page.locator('[class*="content-card"], [class*="content-item"]').count()
  152 |       // Either shows filtered results or "no results"
  153 |       expect(visibleItems >= 0).toBeTruthy()
  154 |     } else {
  155 |       test.info().annotations.push({ type: 'info', description: 'Content search input not found' })
  156 |     }
  157 |   })
```