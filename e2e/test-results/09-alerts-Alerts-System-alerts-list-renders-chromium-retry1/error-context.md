# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 09-alerts.spec.ts >> Alerts System >> alerts list renders
- Location: 09-alerts.spec.ts:19:7

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
              - button "Trash" [ref=e356]:
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
      - main [ref=e388]:
        - generic [ref=e390]:
          - generic [ref=e392]:
            - generic [ref=e393]:
              - img [ref=e395]
              - generic [ref=e397]:
                - heading "Dashboard" [level=1] [ref=e398]
                - paragraph [ref=e399]: Overview of your content creation workspace
            - button "New Content" [ref=e402]:
              - img [ref=e404]
              - generic [ref=e405]: New Content
          - generic [ref=e406]:
            - generic [ref=e408]:
              - generic [ref=e409]:
                - paragraph [ref=e410]: Total Content
                - paragraph [ref=e411]: "6"
              - img [ref=e413]
            - generic [ref=e417]:
              - generic [ref=e418]:
                - paragraph [ref=e419]: Completed
                - paragraph [ref=e420]: "6"
              - img [ref=e422]
            - generic [ref=e426]:
              - generic [ref=e427]:
                - paragraph [ref=e428]: Processing
                - paragraph [ref=e429]: "0"
              - img [ref=e431]
            - generic [ref=e435]:
              - generic [ref=e436]:
                - paragraph [ref=e437]: Failed
                - paragraph [ref=e438]: "0"
              - img [ref=e440]
          - generic [ref=e442]:
            - generic [ref=e444]:
              - generic [ref=e446]:
                - heading "Recent Activity" [level=3] [ref=e447]:
                  - img [ref=e448]
                  - text: Recent Activity
                - button "View all" [ref=e451]:
                  - generic [ref=e452]: View all
                  - img [ref=e454]
              - generic [ref=e457]:
                - button "E2E Delete Test text · completed 5h ago" [ref=e458]:
                  - generic [ref=e460]:
                    - paragraph [ref=e461]: E2E Delete Test
                    - paragraph [ref=e462]: text · completed
                  - generic [ref=e463]: 5h ago
                - button "E2E Test Content text · completed 5h ago" [ref=e464]:
                  - generic [ref=e466]:
                    - paragraph [ref=e467]: E2E Test Content
                    - paragraph [ref=e468]: text · completed
                  - generic [ref=e469]: 5h ago
                - button "E2E Detail Page Test text · completed 5h ago" [ref=e470]:
                  - generic [ref=e472]:
                    - paragraph [ref=e473]: E2E Detail Page Test
                    - paragraph [ref=e474]: text · completed
                  - generic [ref=e475]: 5h ago
                - button "E2E Test Content text · completed 5h ago" [ref=e476]:
                  - generic [ref=e478]:
                    - paragraph [ref=e479]: E2E Test Content
                    - paragraph [ref=e480]: text · completed
                  - generic [ref=e481]: 5h ago
                - button "E2E Delete Test text · completed 5h ago" [ref=e482]:
                  - generic [ref=e484]:
                    - paragraph [ref=e485]: E2E Delete Test
                    - paragraph [ref=e486]: text · completed
                  - generic [ref=e487]: 5h ago
            - generic [ref=e489]:
              - heading "Quick Actions" [level=3] [ref=e491]
              - generic [ref=e492]:
                - button "New Content Create and transform content" [ref=e493]:
                  - img [ref=e495]
                  - generic [ref=e496]:
                    - paragraph [ref=e497]: New Content
                    - paragraph [ref=e498]: Create and transform content
                - button "New Project Organize your content" [ref=e499]:
                  - img [ref=e501]
                  - generic [ref=e503]:
                    - paragraph [ref=e504]: New Project
                    - paragraph [ref=e505]: Organize your content
                - button "View Schedule Manage publishing schedule" [ref=e506]:
                  - img [ref=e508]
                  - generic [ref=e510]:
                    - paragraph [ref=e511]: View Schedule
                    - paragraph [ref=e512]: Manage publishing schedule
                - button "Analytics View content performance" [ref=e513]:
                  - img [ref=e515]
                  - generic [ref=e517]:
                    - paragraph [ref=e518]: Analytics
                    - paragraph [ref=e519]: View content performance
    - contentinfo [ref=e520]:
      - generic [ref=e522]:
        - paragraph [ref=e523]: © 2026 ContentForge AI. All rights reserved.
        - navigation [ref=e524]:
          - link "Terms of Service" [ref=e525] [cursor=pointer]:
            - /url: /legal/terms
          - link "Privacy Policy" [ref=e526] [cursor=pointer]:
            - /url: /legal/privacy
          - link "Cookie Policy" [ref=e527] [cursor=pointer]:
            - /url: /legal/cookies
            - img [ref=e528]
            - text: Cookie Policy
          - link "DMCA Notice" [ref=e530] [cursor=pointer]:
            - /url: /legal/dmca
  - region "Notifications"
```

# Test source

```ts
  1   | /**
  2   |  * 09-alerts.spec.ts — Alerts, Rules & Notifications
  3   |  *
  4   |  * Validates: Alerts center, rules CRUD, notifications, unread count.
  5   |  */
  6   | import { test, expect, loginViaUI, navigateToTab, PERF, API_URL } from './helpers'
  7   | 
  8   | test.describe('Alerts System', () => {
  9   |   test.beforeEach(async ({ page }) => {
  10  |     await loginViaUI(page)
  11  |   })
  12  | 
  13  |   test('alerts tab loads', async ({ page }) => {
  14  |     await navigateToTab(page, 'alerts')
  15  |     await page.waitForTimeout(2000)
  16  |     await expect(page.getByText(/alert|notification/i).first()).toBeVisible({ timeout: PERF.TAB_SWITCH_MAX })
  17  |   })
  18  | 
  19  |   test('alerts list renders', async ({ page }) => {
  20  |     await navigateToTab(page, 'alerts')
  21  |     await page.waitForTimeout(2000)
  22  |     const hasAlerts = await page.getByText(/alert|no.*alert|notification|rule/i).first().isVisible().catch(() => false)
> 23  |     expect(hasAlerts).toBeTruthy()
      |                       ^ Error: expect(received).toBeTruthy()
  24  |   })
  25  | 
  26  |   test('alerts API returns data', async ({ page }) => {
  27  |     const token = await page.evaluate(async () => {
  28  |       const res = await fetch('/api/v1/auth/login', {
  29  |         method: 'POST',
  30  |         headers: { 'Content-Type': 'application/json' },
  31  |         body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
  32  |       })
  33  |       return (await res.json()).access_token
  34  |     })
  35  |     const res = await page.request.get(`${API_URL}/api/v1/alerts`, {
  36  |       headers: { Authorization: `Bearer ${token}` },
  37  |     })
  38  |     expect(res.status()).toBe(200)
  39  |   })
  40  | 
  41  |   test('alerts notifications API', async ({ page }) => {
  42  |     const token = await page.evaluate(async () => {
  43  |       const res = await fetch('/api/v1/auth/login', {
  44  |         method: 'POST',
  45  |         headers: { 'Content-Type': 'application/json' },
  46  |         body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
  47  |       })
  48  |       return (await res.json()).access_token
  49  |     })
  50  |     const res = await page.request.get(`${API_URL}/api/v1/alerts/notifications`, {
  51  |       headers: { Authorization: `Bearer ${token}` },
  52  |     })
  53  |     expect(res.status()).toBe(200)
  54  |   })
  55  | 
  56  |   test('alerts unread count API', async ({ page }) => {
  57  |     const token = await page.evaluate(async () => {
  58  |       const res = await fetch('/api/v1/auth/login', {
  59  |         method: 'POST',
  60  |         headers: { 'Content-Type': 'application/json' },
  61  |         body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
  62  |       })
  63  |       return (await res.json()).access_token
  64  |     })
  65  |     const res = await page.request.get(`${API_URL}/api/v1/alerts/unread-count`, {
  66  |       headers: { Authorization: `Bearer ${token}` },
  67  |     })
  68  |     expect(res.status()).toBe(200)
  69  |   })
  70  | 
  71  |   test('alert rules API', async ({ page }) => {
  72  |     const token = await page.evaluate(async () => {
  73  |       const res = await fetch('/api/v1/auth/login', {
  74  |         method: 'POST',
  75  |         headers: { 'Content-Type': 'application/json' },
  76  |         body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
  77  |       })
  78  |       return (await res.json()).access_token
  79  |     })
  80  |     const res = await page.request.get(`${API_URL}/api/v1/alerts/rules`, {
  81  |       headers: { Authorization: `Bearer ${token}` },
  82  |     })
  83  |     expect(res.status()).toBe(200)
  84  |   })
  85  | 
  86  |   test('create alert rule', async ({ page }) => {
  87  |     const token = await page.evaluate(async () => {
  88  |       const res = await fetch('/api/v1/auth/login', {
  89  |         method: 'POST',
  90  |         headers: { 'Content-Type': 'application/json' },
  91  |         body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
  92  |       })
  93  |       return (await res.json()).access_token
  94  |     })
  95  |     const res = await page.request.post(`${API_URL}/api/v1/alerts/rules`, {
  96  |       headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
  97  |       data: JSON.stringify({
  98  |         name: 'E2E Test Alert Rule',
  99  |         metric: 'content_count',
  100 |         condition: 'above',
  101 |         threshold: 100,
  102 |         enabled: true,
  103 |       }),
  104 |     })
  105 |     expect([200, 201, 422]).toContain(res.status())
  106 |   })
  107 | 
  108 |   test('acknowledge alert API', async ({ page }) => {
  109 |     const token = await page.evaluate(async () => {
  110 |       const res = await fetch('/api/v1/auth/login', {
  111 |         method: 'POST',
  112 |         headers: { 'Content-Type': 'application/json' },
  113 |         body: JSON.stringify({ email: 'test@neo.dev', password: 'Test1234!' }),
  114 |       })
  115 |       return (await res.json()).access_token
  116 |     })
  117 |     // Using a fake alert ID — should return 404, not 500
  118 |     const res = await page.request.post(`${API_URL}/api/v1/alerts/acknowledge/00000000-0000-0000-0000-000000000000`, {
  119 |       headers: { Authorization: `Bearer ${token}` },
  120 |     })
  121 |     expect([200, 404]).toContain(res.status())
  122 |   })
  123 | 
```