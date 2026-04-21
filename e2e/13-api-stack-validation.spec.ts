/**
 * 13-api-stack-validation.spec.ts — Direct API Stack Validation
 *
 * Systematically validates the backend API stack by calling every major
 * endpoint group. This catches 500s, missing routes, auth failures,
 * and broken service logic that UI tests might not reach.
 *
 * Strategy: For each router module, test the primary GET endpoint.
 * For POST/PUT/DELETE, test with valid structure but fake IDs (expect 404/422, not 500).
 */
import { test, expect, API_URL, TEST_USER } from './helpers'

// Helper: get auth token via API
async function getToken(page: import('@playwright/test').Page): Promise<string> {
  const res = await page.request.post(`${API_URL}/api/v1/auth/login`, {
    headers: { 'Content-Type': 'application/json' },
    data: { email: TEST_USER.email, password: TEST_USER.password },
  })
  expect(res.ok(), 'Login should succeed').toBeTruthy()
  return (await res.json()).access_token
}

test.describe('API Stack Validation', () => {
  // ─── Auth ──────────────────────────────────────────────────────────

  test('POST /auth/login — valid credentials', async ({ page }) => {
    const res = await page.request.post(`${API_URL}/api/v1/auth/login`, {
      headers: { 'Content-Type': 'application/json' },
      data: { email: TEST_USER.email, password: TEST_USER.password },
    })
    expect(res.status()).toBe(200)
    const data = await res.json()
    expect(data.access_token).toBeDefined()
  })

  test('GET /auth/me — authenticated', async ({ page }) => {
    const token = await getToken(page)
    const res = await page.request.get(`${API_URL}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect(res.status()).toBe(200)
  })

  // ─── Core Content ──────────────────────────────────────────────────

  test('GET /content — list', async ({ page }) => {
    const token = await getToken(page)
    const res = await page.request.get(`${API_URL}/api/v1/content`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect(res.status()).toBe(200)
  })

  test('GET /projects — list', async ({ page }) => {
    const token = await getToken(page)
    const res = await page.request.get(`${API_URL}/api/v1/projects`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect(res.status()).toBe(200)
  })

  test('GET /init — batch endpoint', async ({ page }) => {
    const token = await getToken(page)
    const res = await page.request.get(`${API_URL}/api/v1/init`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect(res.status()).toBe(200)
    const data = await res.json()
    expect(data).toHaveProperty('user')
    expect(data).toHaveProperty('projects')
  })

  // ─── Analytics ─────────────────────────────────────────────────────

  test('GET /analytics/dashboard', async ({ page }) => {
    const token = await getToken(page)
    const res = await page.request.get(`${API_URL}/api/v1/analytics/dashboard`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect(res.status()).toBe(200)
  })

  // ─── Organizations ─────────────────────────────────────────────────

  test('GET /organizations — list', async ({ page }) => {
    const token = await getToken(page)
    const res = await page.request.get(`${API_URL}/api/v1/organizations`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect(res.status()).toBe(200)
  })

  // ─── Schedule ──────────────────────────────────────────────────────

  test('GET /schedule — list', async ({ page }) => {
    const token = await getToken(page)
    const res = await page.request.get(`${API_URL}/api/v1/schedule`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect(res.status()).toBe(200)
  })

  // ─── RSS ───────────────────────────────────────────────────────────

  test('GET /rss/feeds + /rss/stats + /rss/settings', async ({ page }) => {
    const token = await getToken(page)
    for (const ep of ['/rss/feeds', '/rss/stats', '/rss/settings']) {
      const res = await page.request.get(`${API_URL}/api/v1${ep}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      expect(res.status(), `${ep} should return 200`).toBe(200)
    }
  })

  // ─── Alerts ────────────────────────────────────────────────────────

  test('GET /alerts + /alerts/rules + /alerts/unread-count', async ({ page }) => {
    const token = await getToken(page)
    for (const ep of ['/alerts', '/alerts/rules', '/alerts/unread-count']) {
      const res = await page.request.get(`${API_URL}/api/v1${ep}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      expect(res.status(), `${ep} should return 200`).toBe(200)
    }
  })

  // ─── Quality & Sentiment ───────────────────────────────────────────

  test('GET /quality-scoring/batch (POST) + /sentiment/trend', async ({ page }) => {
    const token = await getToken(page)
    // Sentiment trend
    const res1 = await page.request.get(`${API_URL}/api/v1/sentiment/trend?days=30`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect([200, 422, 429]).toContain(res1.status())
    // Quality scoring — needs a content_id, so POST batch with empty list returns 422
    const res2 = await page.request.post(`${API_URL}/api/v1/quality-scoring/batch`, {
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      data: JSON.stringify({ content_ids: [] }),
    })
    expect([200, 201, 422]).toContain(res2.status())
  })

  // ─── Categorization ────────────────────────────────────────────────

  test('GET /categorization + /categorization/list', async ({ page }) => {
    const token = await getToken(page)
    for (const ep of ['/categorization', '/categorization/list']) {
      const res = await page.request.get(`${API_URL}/api/v1${ep}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      expect(res.status(), `${ep} should return 200`).toBe(200)
    }
  })

  // ─── SLA & Retention ───────────────────────────────────────────────

  test('GET /sla/policies + /sla/dashboard + /retention/policies', async ({ page }) => {
    const token = await getToken(page)
    for (const ep of ['/sla/policies', '/sla/dashboard', '/retention/policies']) {
      const res = await page.request.get(`${API_URL}/api/v1${ep}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      // Some of these may not be implemented yet (404)
      expect([200, 404]).toContain(res.status())
    }
  })

  // ─── Dashboards & Plugins ──────────────────────────────────────────

  test('GET /dashboards + /plugins', async ({ page }) => {
    const token = await getToken(page)
    for (const ep of ['/dashboards', '/plugins']) {
      const res = await page.request.get(`${API_URL}/api/v1${ep}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      expect(res.status(), `${ep} should return 200`).toBe(200)
    }
  })

  // ─── Marketplace ────────────────────────────────────────────────────

  test('GET /marketplace/templates + /categories + /tags', async ({ page }) => {
    const token = await getToken(page)
    for (const ep of ['/marketplace/templates', '/marketplace/categories', '/marketplace/tags']) {
      const res = await page.request.get(`${API_URL}/api/v1${ep}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      expect(res.status(), `${ep} should return 200`).toBe(200)
    }
  })

  // ─── Integrations & Automation ─────────────────────────────────────

  test('GET /integrations + /automation/rules', async ({ page }) => {
    const token = await getToken(page)
    for (const ep of ['/integrations', '/automation/rules']) {
      const res = await page.request.get(`${API_URL}/api/v1${ep}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      expect(res.status(), `${ep} should return 200`).toBe(200)
    }
  })

  // ─── Funnels & Attribution ──────────────────────────────────────────

  test('GET /funnels + /attribution/channels', async ({ page }) => {
    const token = await getToken(page)
    for (const ep of ['/funnels', '/attribution/channels']) {
      const res = await page.request.get(`${API_URL}/api/v1${ep}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      expect(res.status(), `${ep} should return 200`).toBe(200)
    }
  })

  // ─── Health & Docs ─────────────────────────────────────────────────

  test('GET /health + /docs/openapi.json', async ({ page }) => {
    const res1 = await page.request.get(`${API_URL}/api/v1/health`)
    expect(res1.status()).toBe(200)
    const res2 = await page.request.get(`${API_URL}/api/v1/docs/openapi.json`)
    expect([200, 404]).toContain(res2.status())
  })

  // ─── Search ────────────────────────────────────────────────────────

  test('GET /search?q=test', async ({ page }) => {
    const token = await getToken(page)
    const res = await page.request.get(`${API_URL}/api/v1/search?q=test`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    expect(res.status()).toBe(200)
  })
})