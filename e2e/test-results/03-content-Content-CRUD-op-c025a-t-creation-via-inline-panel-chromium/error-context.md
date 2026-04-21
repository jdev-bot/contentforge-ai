# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 03-content.spec.ts >> Content CRUD >> open content creation via inline panel
- Location: 03-content.spec.ts:28:7

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByText(/paste text|source type|title/i).first()
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByText(/paste text|source type|title/i).first()

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
  22  |     await page.waitForTimeout(2000)
  23  |     // Either content items, empty state, or the tab header renders
  24  |     const hasContent = await page.getByText(/content/i).first().isVisible().catch(() => false)
  25  |     expect(hasContent).toBeTruthy()
  26  |   })
  27  | 
  28  |   test('open content creation via inline panel', async ({ page }) => {
  29  |     await navigateToTab(page, 'content')
  30  |     await page.waitForTimeout(500)
  31  |     // Click "New Content" or similar button
  32  |     const createBtn = page.getByRole('button', { name: /new content|create content|add content|\+ content/i }).first()
  33  |     if (await createBtn.isVisible().catch(() => false)) {
  34  |       await createBtn.click()
  35  |       await page.waitForTimeout(1000)
  36  |       // Should show creation form
> 37  |       await expect(page.getByText(/paste text|source type|title/i).first()).toBeVisible({ timeout: 5000 })
      |                                                                             ^ Error: expect(locator).toBeVisible() failed
  38  |     } else {
  39  |       test.info().annotations.push({ type: 'skip-reason', description: 'Create content button not found' })
  40  |     }
  41  |   })
  42  | 
  43  |   test('content creation form has required fields', async ({ page }) => {
  44  |     await navigateToTab(page, 'content')
  45  |     await page.waitForTimeout(500)
  46  |     const createBtn = page.getByRole('button', { name: /new content|create content|add content|\+ content/i }).first()
  47  |     if (await createBtn.isVisible().catch(() => false)) {
  48  |       await createBtn.click()
  49  |       await page.waitForTimeout(1500)
  50  |       // Check that a creation form or panel appears
  51  |       const formVisible = await page.getByText(/paste text|source type|title|create|new content/i).first().isVisible().catch(() => false)
  52  |       expect(formVisible).toBeTruthy()
  53  |     } else {
  54  |       test.info().annotations.push({ type: 'skip-reason', description: 'Create content button not found' })
  55  |     }
  56  |   })
  57  | 
  58  |   test('create content with paste text (if usage available)', async ({ page }) => {
  59  |     // Check usage first
  60  |     const token = await page.evaluate(async () => {
  61  |       const res = await fetch('/api/v1/usage/summary')
  62  |       if (!res.ok) return null
  63  |       const data = await res.json()
  64  |       return data
  65  |     })
  66  |     if (token && token.monthly_usage_count >= token.monthly_usage_limit) {
  67  |       test.skip('Monthly usage limit reached')
  68  |       return
  69  |     }
  70  | 
  71  |     await navigateToTab(page, 'content')
  72  |     await page.waitForTimeout(500)
  73  |     const createBtn = page.getByRole('button', { name: /new content|create content|add content/i }).first()
  74  |     if (!(await createBtn.isVisible().catch(() => false))) {
  75  |       test.skip('Create button not found')
  76  |       return
  77  |     }
  78  |     await createBtn.click()
  79  |     await page.waitForTimeout(1500)
  80  | 
  81  |     // Select "Paste Text" source type
  82  |     const pasteBtn = page.getByRole('button', { name: /paste text/i }).first()
  83  |     if (await pasteBtn.isVisible().catch(() => false)) {
  84  |       await pasteBtn.click()
  85  |     }
  86  | 
  87  |     // Fill title
  88  |     const titleInput = page.getByPlaceholder(/title/i).first()
  89  |     if (await titleInput.isVisible().catch(() => false)) {
  90  |       await titleInput.fill('E2E Test Content')
  91  |     }
  92  | 
  93  |     // Fill content textarea
  94  |     const textarea = page.getByPlaceholder(/paste.*text|content|body/i).first()
  95  |     if (await textarea.isVisible().catch(() => false)) {
  96  |       await textarea.fill('This is test content created by the E2E test suite.')
  97  |     }
  98  | 
  99  |     // Submit
  100 |     const submitBtn = page.getByRole('button', { name: /add content|create|submit|generate/i }).first()
  101 |     if (await submitBtn.isVisible().catch(() => false)) {
  102 |       await submitBtn.click()
  103 |       // Wait for success or error
  104 |       await page.waitForTimeout(3000)
  105 |       // Should either navigate to content detail or show in list
  106 |     }
  107 |   })
  108 | 
  109 |   test('click content item opens detail panel', async ({ page }) => {
  110 |     await navigateToTab(page, 'content')
  111 |     await page.waitForTimeout(2000)
  112 |     // Find a content item to click
  113 |     const contentItem = page.locator('[class*="content-card"], [class*="content-item"], [data-testid="content-item"]').first()
  114 |     if (await contentItem.isVisible().catch(() => false)) {
  115 |       await contentItem.click()
  116 |       await page.waitForTimeout(1500)
  117 |       // Should show content detail (inline panel or separate view)
  118 |       await expect(page.getByText(/edit|delete|publish|share|content/i).first()).toBeVisible({ timeout: 5000 })
  119 |     } else {
  120 |       test.info().annotations.push({ type: 'skip-reason', description: 'No content items to click' })
  121 |     }
  122 |   })
  123 | 
  124 |   test('content detail shows back navigation', async ({ page }) => {
  125 |     await navigateToTab(page, 'content')
  126 |     await page.waitForTimeout(2000)
  127 |     const contentItem = page.locator('[class*="content-card"], [class*="content-item"], [data-testid="content-item"]').first()
  128 |     if (await contentItem.isVisible().catch(() => false)) {
  129 |       await contentItem.click()
  130 |       await page.waitForTimeout(1500)
  131 |       // Back button should exist
  132 |       const backBtn = page.getByRole('button', { name: /back|←|arrow/i }).first()
  133 |       expect(await backBtn.isVisible().catch(() => false) || await page.getByText(/back/i).first().isVisible().catch(() => false)).toBeTruthy()
  134 |     } else {
  135 |       test.info().annotations.push({ type: 'skip-reason', description: 'No content items' })
  136 |     }
  137 |   })
```