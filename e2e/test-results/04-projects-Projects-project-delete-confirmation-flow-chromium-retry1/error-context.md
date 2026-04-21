# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 04-projects.spec.ts >> Projects >> project delete confirmation flow
- Location: 04-projects.spec.ts:97:7

# Error details

```
Error: expect(received).toBeTruthy()

Received: false
```

# Page snapshot

```yaml
- generic [ref=e1]:
  - alert [ref=e2]
  - generic [ref=e4]:
    - banner [ref=e5]:
      - generic [ref=e7]:
        - generic [ref=e9]:
          - img [ref=e11]
          - generic [ref=e14]: ContentForge
        - generic [ref=e15]:
          - button "Search" [ref=e17]:
            - img [ref=e19]
            - generic [ref=e22]: Search
          - button "New Content" [ref=e24]:
            - img [ref=e26]
            - generic [ref=e27]: New Content
          - button "Alerts" [ref=e30]:
            - img [ref=e31]
            - generic [ref=e35]: "3"
          - button "T test test@neo.dev" [ref=e37]:
            - generic [ref=e40]: T
            - generic [ref=e42]:
              - paragraph [ref=e43]: test
              - paragraph [ref=e44]: test@neo.dev
    - generic [ref=e46]:
      - complementary [ref=e47]:
        - navigation [ref=e48]:
          - generic [ref=e49]:
            - generic [ref=e50]:
              - img [ref=e51]
              - text: Pinned
            - generic [ref=e53]:
              - button "Content" [ref=e54]:
                - img [ref=e55]
                - generic [ref=e58]: Content
                - img [ref=e59]
              - button "Unpin tab" [ref=e61]:
                - img [ref=e62]
            - generic [ref=e64]:
              - button "Analytics" [ref=e65]:
                - img [ref=e66]
                - generic [ref=e68]: Analytics
                - img [ref=e69]
              - button "Unpin tab" [ref=e71]:
                - img [ref=e72]
            - generic [ref=e74]:
              - button "Schedule" [ref=e75]:
                - img [ref=e76]
                - generic [ref=e78]: Schedule
                - img [ref=e79]
              - button "Unpin tab" [ref=e81]:
                - img [ref=e82]
          - button "Home Alt+0" [ref=e86]:
            - img [ref=e87]
            - generic [ref=e90]: Home
            - generic [ref=e91]: Alt+0
          - generic [ref=e92]:
            - button "Content 5" [ref=e93]:
              - generic [ref=e94]:
                - generic [ref=e95]: Content
                - generic [ref=e96]: "5"
              - img [ref=e97]
            - generic [ref=e99]:
              - button "Content Alt+1" [ref=e100]:
                - img [ref=e101]
                - generic [ref=e104]: Content
                - img [ref=e105]
                - generic [ref=e107]: Alt+1
              - button "Unpin tab" [ref=e108]:
                - img [ref=e109]
            - generic [ref=e111]:
              - button "Projects Alt+2" [ref=e112]:
                - img [ref=e113]
                - generic [ref=e115]: Projects
                - generic [ref=e116]: Alt+2
              - button "Pin tab" [ref=e117]:
                - img [ref=e118]
            - generic [ref=e120]:
              - button "Schedule Alt+3" [ref=e121]:
                - img [ref=e122]
                - generic [ref=e124]: Schedule
                - img [ref=e125]
                - generic [ref=e127]: Alt+3
              - button "Unpin tab" [ref=e128]:
                - img [ref=e129]
            - generic [ref=e131]:
              - button "RSS Feeds Alt+4" [ref=e132]:
                - img [ref=e133]
                - generic [ref=e137]: RSS Feeds
                - generic [ref=e138]: Alt+4
              - button "Pin tab" [ref=e139]:
                - img [ref=e140]
            - generic [ref=e142]:
              - button "Freshness Alt+5" [ref=e143]:
                - img [ref=e144]
                - generic [ref=e147]: Freshness
                - generic [ref=e148]: Alt+5
              - button "Pin tab" [ref=e149]:
                - img [ref=e150]
          - generic [ref=e152]:
            - button "Analytics 7" [ref=e153]:
              - generic [ref=e154]:
                - generic [ref=e155]: Analytics
                - generic [ref=e156]: "7"
              - img [ref=e157]
            - generic [ref=e159]:
              - button "Analytics Alt+6" [ref=e160]:
                - img [ref=e161]
                - generic [ref=e163]: Analytics
                - img [ref=e164]
                - generic [ref=e166]: Alt+6
              - button "Unpin tab" [ref=e167]:
                - img [ref=e168]
            - generic [ref=e170]:
              - button "Trends Alt+7" [ref=e171]:
                - img [ref=e172]
                - generic [ref=e175]: Trends
                - generic [ref=e176]: Alt+7
              - button "Pin tab" [ref=e177]:
                - img [ref=e178]
            - generic [ref=e180]:
              - button "Distributions Alt+8" [ref=e181]:
                - img [ref=e182]
                - generic [ref=e188]: Distributions
                - generic [ref=e189]: Alt+8
              - button "Pin tab" [ref=e190]:
                - img [ref=e191]
            - generic [ref=e193]:
              - button "Performance Alt+9" [ref=e194]:
                - img [ref=e195]
                - generic [ref=e197]: Performance
                - generic [ref=e198]: Alt+9
              - button "Pin tab" [ref=e199]:
                - img [ref=e200]
            - generic [ref=e202]:
              - button "Funnels New" [ref=e203]:
                - img [ref=e204]
                - generic [ref=e206]: Funnels
                - generic [ref=e208]: New
              - button "Pin tab" [ref=e209]:
                - img [ref=e210]
            - generic [ref=e212]:
              - button "Attribution New" [ref=e213]:
                - img [ref=e214]
                - generic [ref=e217]: Attribution
                - generic [ref=e219]: New
              - button "Pin tab" [ref=e220]:
                - img [ref=e221]
            - generic [ref=e223]:
              - button "Competitors New" [ref=e224]:
                - img [ref=e225]
                - generic [ref=e229]: Competitors
                - generic [ref=e231]: New
              - button "Pin tab" [ref=e232]:
                - img [ref=e233]
          - generic [ref=e235]:
            - button "Insights 4" [ref=e236]:
              - generic [ref=e237]:
                - generic [ref=e238]: Insights
                - generic [ref=e239]: "4"
              - img [ref=e240]
            - generic [ref=e242]:
              - button "Quality" [ref=e243]:
                - img [ref=e244]
                - generic [ref=e247]: Quality
              - button "Pin tab" [ref=e248]:
                - img [ref=e249]
            - generic [ref=e251]:
              - button "Sentiment" [ref=e252]:
                - img [ref=e253]
                - generic [ref=e255]: Sentiment
              - button "Pin tab" [ref=e256]:
                - img [ref=e257]
            - generic [ref=e259]:
              - button "Categories New" [ref=e260]:
                - img [ref=e261]
                - generic [ref=e264]: Categories
                - generic [ref=e266]: New
              - button "Pin tab" [ref=e267]:
                - img [ref=e268]
            - generic [ref=e270]:
              - button "Suggestions New" [ref=e271]:
                - img [ref=e272]
                - generic [ref=e274]: Suggestions
                - generic [ref=e276]: New
              - button "Pin tab" [ref=e277]:
                - img [ref=e278]
          - generic [ref=e280]:
            - button "Team 4" [ref=e281]:
              - generic [ref=e282]:
                - generic [ref=e283]: Team
                - generic [ref=e284]: "4"
              - img [ref=e285]
            - generic [ref=e287]:
              - button "Team" [ref=e288]:
                - img [ref=e289]
                - generic [ref=e294]: Team
              - button "Pin tab" [ref=e295]:
                - img [ref=e296]
            - generic [ref=e298]:
              - button "Team Calendar New" [ref=e299]:
                - img [ref=e300]
                - generic [ref=e304]: Team Calendar
                - generic [ref=e306]: New
              - button "Pin tab" [ref=e307]:
                - img [ref=e308]
            - generic [ref=e310]:
              - button "Comments" [ref=e311]:
                - img [ref=e312]
                - generic [ref=e314]: Comments
              - button "Pin tab" [ref=e315]:
                - img [ref=e316]
            - generic [ref=e318]:
              - button "History New" [ref=e319]:
                - img [ref=e320]
                - generic [ref=e324]: History
                - generic [ref=e326]: New
              - button "Pin tab" [ref=e327]:
                - img [ref=e328]
          - button "System 5" [ref=e331]:
            - generic [ref=e332]:
              - generic [ref=e333]: System
              - generic [ref=e334]: "5"
            - img [ref=e335]
          - button "Extensions 4" [ref=e338]:
            - generic [ref=e339]:
              - generic [ref=e340]: Extensions
              - generic [ref=e341]: "4"
            - img [ref=e342]
          - generic [ref=e344]:
            - generic [ref=e346]:
              - button "Settings" [ref=e347]:
                - img [ref=e348]
                - generic [ref=e351]: Settings
              - button "Pin tab" [ref=e352]:
                - img [ref=e353]
            - generic [ref=e355]:
              - button "Trash" [active] [ref=e356]:
                - img [ref=e357]
                - generic [ref=e360]: Trash
              - button "Pin tab" [ref=e361]:
                - img [ref=e362]
        - generic [ref=e366]:
          - generic [ref=e367]:
            - generic [ref=e368]:
              - img [ref=e369]
              - generic [ref=e371]: free Plan
            - generic [ref=e372]:
              - img [ref=e373]
              - text: Limit Reached
          - generic [ref=e378]:
            - generic [ref=e379]: 10 / 10 used
            - generic [ref=e380]: 0 remaining
          - generic [ref=e382]:
            - paragraph [ref=e383]: You've reached your monthly limit. Upgrade to continue creating content.
            - button "Upgrade Plan" [ref=e384]:
              - generic [ref=e385]: Upgrade Plan
        - paragraph [ref=e387]: Press Ctrl+K to search · Alt+N switch tabs
      - main [ref=e388]
    - contentinfo [ref=e395]:
      - generic [ref=e397]:
        - paragraph [ref=e398]: © 2026 ContentForge AI. All rights reserved.
        - navigation [ref=e399]:
          - link "Terms of Service" [ref=e400] [cursor=pointer]:
            - /url: /legal/terms
          - link "Privacy Policy" [ref=e401] [cursor=pointer]:
            - /url: /legal/privacy
          - link "Cookie Policy" [ref=e402] [cursor=pointer]:
            - /url: /legal/cookies
            - img [ref=e403]
            - text: Cookie Policy
          - link "DMCA Notice" [ref=e405] [cursor=pointer]:
            - /url: /legal/dmca
  - region "Notifications"
```

# Test source

```ts
  7   | 
  8   | test.describe('Projects', () => {
  9   |   test.beforeEach(async ({ page }) => {
  10  |     await loginViaUI(page)
  11  |   })
  12  | 
  13  |   test('projects tab loads', async ({ page }) => {
  14  |     await navigateToTab(page, 'projects')
  15  |     await expect(page.getByText(/project/i).first()).toBeVisible({ timeout: PERF.TAB_SWITCH_MAX })
  16  |   })
  17  | 
  18  |   test('projects list renders (items or empty state)', async ({ page }) => {
  19  |     await navigateToTab(page, 'projects')
  20  |     await page.waitForTimeout(2000)
  21  |     // Check that projects tab rendered something
  22  |     const hasContent = await page.getByText(/project/i).first().isVisible().catch(() => false)
  23  |     expect(hasContent).toBeTruthy()
  24  |   })
  25  | 
  26  |   test('create new project', async ({ page }) => {
  27  |     await navigateToTab(page, 'projects')
  28  |     await page.waitForTimeout(1000)
  29  |     const createBtn = page.getByRole('button', { name: /new project|create project|\+ project/i }).first()
  30  |     if (await createBtn.isVisible().catch(() => false)) {
  31  |       await createBtn.click()
  32  |       await page.waitForTimeout(1000)
  33  |       // Fill project name
  34  |       const nameInput = page.getByPlaceholder(/name|title/i).first()
  35  |       if (await nameInput.isVisible().catch(() => false)) {
  36  |         await nameInput.fill('E2E Test Project')
  37  |       }
  38  |       // Submit
  39  |       const submitBtn = page.getByRole('button', { name: /create|save|submit/i }).first()
  40  |       if (await submitBtn.isVisible().catch(() => false)) {
  41  |         await submitBtn.click()
  42  |         await page.waitForTimeout(2000)
  43  |       }
  44  |     } else {
  45  |       test.info().annotations.push({ type: 'info', description: 'Create project button not found' })
  46  |     }
  47  |   })
  48  | 
  49  |   test('project items are clickable', async ({ page }) => {
  50  |     await navigateToTab(page, 'projects')
  51  |     await page.waitForTimeout(2000)
  52  |     const projectItem = page.locator('[class*="project"]').first()
  53  |     if (await projectItem.isVisible().catch(() => false)) {
  54  |       await projectItem.click()
  55  |       await page.waitForTimeout(1500)
  56  |     } else {
  57  |       test.info().annotations.push({ type: 'info', description: 'No project items to click' })
  58  |     }
  59  |   })
  60  | 
  61  |   test('standalone /projects/new page loads', async ({ page }) => {
  62  |     const { installCookieSuppression, dismissOverlays } = await import('./helpers')
  63  |     await installCookieSuppression(page)
  64  |     await page.goto('/projects/new')
  65  |     await dismissOverlays(page)
  66  |     await page.waitForTimeout(2000)
  67  |     await expect(page.locator('body')).toBeVisible()
  68  |   })
  69  | 
  70  |   test('standalone /projects/[id] page handles missing id', async ({ page }) => {
  71  |     const { installCookieSuppression, dismissOverlays } = await import('./helpers')
  72  |     await installCookieSuppression(page)
  73  |     await page.goto('/projects/nonexistent-id')
  74  |     await dismissOverlays(page)
  75  |     await page.waitForTimeout(2000)
  76  |     // Should show error or redirect, not crash
  77  |     await expect(page.locator('body')).toBeVisible()
  78  |   })
  79  | 
  80  |   test('projects API returns data', async ({ page }) => {
  81  |     const token = await page.evaluate(async () => {
  82  |       const res = await fetch('/api/v1/auth/login', {
  83  |         method: 'POST',
  84  |         headers: { 'Content-Type': 'application/json' },
  85  |         body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
  86  |       })
  87  |       return (await res.json()).access_token
  88  |     })
  89  |     const res = await page.request.get(`${API_URL}/api/v1/projects`, {
  90  |       headers: { Authorization: `Bearer ${token}` },
  91  |     })
  92  |     expect(res.status()).toBe(200)
  93  |     const data = await res.json()
  94  |     expect(Array.isArray(data) || (data && typeof data === 'object')).toBeTruthy()
  95  |   })
  96  | 
  97  |   test('project delete confirmation flow', async ({ page }) => {
  98  |     await navigateToTab(page, 'projects')
  99  |     await page.waitForTimeout(2000)
  100 |     // Find delete button if any project exists
  101 |     const deleteBtn = page.getByRole('button', { name: /delete|trash|remove/i }).first()
  102 |     if (await deleteBtn.isVisible().catch(() => false)) {
  103 |       await deleteBtn.click()
  104 |       await page.waitForTimeout(500)
  105 |       // Should show confirmation dialog
  106 |       const confirmBtn = page.getByRole('button', { name: /confirm|yes|delete/i }).first()
> 107 |       expect(await confirmBtn.isVisible().catch(() => false)).toBeTruthy()
      |                                                               ^ Error: expect(received).toBeTruthy()
  108 |     } else {
  109 |       test.info().annotations.push({ type: 'info', description: 'No delete button found' })
  110 |     }
  111 |   })
  112 | })
  113 | 
```