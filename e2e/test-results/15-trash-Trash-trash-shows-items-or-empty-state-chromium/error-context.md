# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 15-trash.spec.ts >> Trash >> trash shows items or empty state
- Location: 15-trash.spec.ts:19:7

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
        - paragraph [ref=e372]: Press Ctrl+K to search · Alt+N switch tabs
      - main [ref=e373]
    - contentinfo [ref=e380]:
      - generic [ref=e382]:
        - paragraph [ref=e383]: © 2026 ContentForge AI. All rights reserved.
        - navigation [ref=e384]:
          - link "Terms of Service" [ref=e385] [cursor=pointer]:
            - /url: /legal/terms
          - link "Privacy Policy" [ref=e386] [cursor=pointer]:
            - /url: /legal/privacy
          - link "Cookie Policy" [ref=e387] [cursor=pointer]:
            - /url: /legal/cookies
            - img [ref=e388]
            - text: Cookie Policy
          - link "DMCA Notice" [ref=e390] [cursor=pointer]:
            - /url: /legal/dmca
  - region "Notifications"
```

# Test source

```ts
  1  | /**
  2  |  * 15-trash.spec.ts — Trash & Soft Delete
  3  |  *
  4  |  * Validates: Trash tab, item list, restore, permanent delete, empty trash.
  5  |  */
  6  | import { test, expect, loginViaUI, navigateToTab, PERF, API_URL } from './helpers'
  7  | 
  8  | test.describe('Trash', () => {
  9  |   test.beforeEach(async ({ page }) => {
  10 |     await loginViaUI(page)
  11 |   })
  12 | 
  13 |   test('trash tab loads', async ({ page }) => {
  14 |     await navigateToTab(page, 'trash')
  15 |     await page.waitForTimeout(2000)
  16 |     await expect(page.getByText(/trash|deleted|restore|permanently/i).first()).toBeVisible({ timeout: PERF.TAB_SWITCH_MAX })
  17 |   })
  18 | 
  19 |   test('trash shows items or empty state', async ({ page }) => {
  20 |     await navigateToTab(page, 'trash')
  21 |     await page.waitForTimeout(2000)
  22 |     const hasItems = await page.getByText(/restore|delete|item/i).first().isVisible().catch(() => false)
  23 |     const hasEmpty = await page.getByText(/empty|no.*deleted|trash.*empty/i).first().isVisible().catch(() => false)
> 24 |     expect(hasItems || hasEmpty).toBeTruthy()
     |                                  ^ Error: expect(received).toBeTruthy()
  25 |   })
  26 | 
  27 |   test('trash stats API', async ({ page }) => {
  28 |     const token = await page.evaluate(async () => {
  29 |       const res = await fetch('/api/v1/auth/login', {
  30 |         method: 'POST',
  31 |         headers: { 'Content-Type': 'application/json' },
  32 |         body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
  33 |       })
  34 |       return (await res.json()).access_token
  35 |     })
  36 |     const res = await page.request.get(`${API_URL}/api/v1/trash/stats`, {
  37 |       headers: { Authorization: `Bearer ${token}` },
  38 |     })
  39 |     expect(res.status()).toBe(200)
  40 |   })
  41 | 
  42 |   test('trash items API', async ({ page }) => {
  43 |     const token = await page.evaluate(async () => {
  44 |       const res = await fetch('/api/v1/auth/login', {
  45 |         method: 'POST',
  46 |         headers: { 'Content-Type': 'application/json' },
  47 |         body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
  48 |       })
  49 |       return (await res.json()).access_token
  50 |     })
  51 |     const res = await page.request.get(`${API_URL}/api/v1/trash`, {
  52 |       headers: { Authorization: `Bearer ${token}` },
  53 |     })
  54 |     expect(res.status()).toBe(200)
  55 |   })
  56 | 
  57 |   test('restore from trash API (fake ID)', async ({ page }) => {
  58 |     const token = await page.evaluate(async () => {
  59 |       const res = await fetch('/api/v1/auth/login', {
  60 |         method: 'POST',
  61 |         headers: { 'Content-Type': 'application/json' },
  62 |         body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
  63 |       })
  64 |       return (await res.json()).access_token
  65 |     })
  66 |     // Fake ID — should return 404, not 500
  67 |     const res = await page.request.post(`${API_URL}/api/v1/trash/00000000-0000-0000-0000-000000000000/restore`, {
  68 |       headers: { Authorization: `Bearer ${token}` },
  69 |     })
  70 |     expect([200, 404, 422]).toContain(res.status())
  71 |   })
  72 | 
  73 |   test('permanent delete API (fake ID)', async ({ page }) => {
  74 |     const token = await page.evaluate(async () => {
  75 |       const res = await fetch('/api/v1/auth/login', {
  76 |         method: 'POST',
  77 |         headers: { 'Content-Type': 'application/json' },
  78 |         body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
  79 |       })
  80 |       return (await res.json()).access_token
  81 |     })
  82 |     // Fake ID — should return 404, not 500
  83 |     const res = await page.request.delete(`${API_URL}/api/v1/trash/00000000-0000-0000-0000-000000000000`, {
  84 |       headers: { Authorization: `Bearer ${token}` },
  85 |     })
  86 |     expect([200, 404, 422]).toContain(res.status())
  87 |   })
  88 | })
```