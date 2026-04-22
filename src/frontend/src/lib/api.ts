import { supabase } from './supabase'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

/** Format API error messages into user-friendly strings */
export function formatApiError(error: unknown, fallback = 'Something went wrong'): string {
  if (error instanceof Error) {
    const msg = error.message
    // Supabase PGRST errors
    if (msg.includes('PGRST205') || msg.includes('does not exist')) return 'This feature is not yet available'
    if (msg.includes('PGRST116')) return 'No data found'
    if (msg.includes('PGRST200')) return 'Relationship not found'
    // HTTP error mapping
    if (msg.includes('404') || msg.includes('Not Found')) return 'Resource not found'
    if (msg.includes('403') || msg.includes('Forbidden')) return 'You don\'t have permission to access this'
    if (msg.includes('401') || msg.includes('Unauthorized')) return 'Please sign in again'
    if (msg.includes('429') || msg.includes('Rate limit')) return 'Too many requests — please wait a moment'
    if (msg.includes('500') || msg.includes('Internal Server Error')) return 'Server error — please try again later'
    if (msg.includes('502') || msg.includes('Bad Gateway')) return 'Service temporarily unavailable'
    if (msg.includes('503')) return 'Service temporarily unavailable'
    // Stripe placeholder
    if (msg.includes('stripe') || msg.includes('checkout')) return 'Payment system not configured yet'
    // Fallback to message if it\'s short and readable
    if (msg.length < 100) return msg
    return fallback
  }
  return fallback
}

export interface ContentSource {
  type: 'url' | 'youtube' | 'text' | 'upload'
  url?: string
  text?: string
  file_path?: string
}

export interface ContentCreate {
  title: string
  source: ContentSource
  project_id: string
}

export interface Content {
  id: string
  project_id: string
  user_id: string
  title: string
  source_type: string
  source_url?: string
  original_text?: string
  word_count?: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  created_at: string
  updated_at: string
}

export interface GeneratedAsset {
  id: string
  content_id: string
  user_id: string
  type: 'social_post' | 'thread' | 'newsletter' | 'blog_post' | 'video_script'
  platform?: string
  content: string
  tokens_used?: number
  status: 'pending' | 'generated' | 'approved' | 'rejected'
  created_at: string
}

/**
 * Wait for the Supabase session to be available in the browser.
 * On initial page load, the @supabase/ssr browser client may not have
 * hydrated the session from cookies yet. This function subscribes to
 * auth state changes and waits until a session is available, or until
 * we determine there truly is no session (e.g. user not logged in).
 *
 * Returns the access token, or throws if no session after timeout.
 */
// Cache the access token after first successful resolution to avoid
// re-waiting on every API call within the same page session
let cachedToken: string | null = null

/**
 * Decode a JWT's exp claim without a library.
 * Returns the expiry timestamp in seconds, or null if not decodable.
 */
function getTokenExpiry(token: string): number | null {
  try {
    const payload = token.split('.')[1]
    if (!payload) return null
    const padded = payload + '='.repeat((4 - payload.length % 4) % 4)
    const decoded = JSON.parse(atob(padded))
    return decoded.exp ?? null
  } catch {
    return null
  }
}

async function waitForSession(timeoutMs = 8000): Promise<string> {
  // Return cached token if available and not expired (with 60s buffer)
  if (cachedToken) {
    const exp = getTokenExpiry(cachedToken)
    if (exp && exp * 1000 > Date.now() + 60000) {
      return cachedToken
    }
    // Token expired or about to expire — clear cache and refresh
    cachedToken = null
  }

  // Strategy: Try getSession() first. If it returns a session, use it immediately.
  // If not, subscribe to onAuthStateChange for up to `timeoutMs`.
  // The @supabase/ssr browser client initializes asynchronously from document.cookie,
  // so INITIAL_SESSION may fire shortly after the client is created.
  // We also retry getSession() as a fallback in case onAuthStateChange misses the event.

  // First try: maybe session is already available
  const { data: { session: firstSession } } = await supabase.auth.getSession()
  if (firstSession?.access_token) {
    cachedToken = firstSession.access_token
    return firstSession.access_token
  }

  // Session not immediately available — race between onAuthStateChange and getSession retry
  return new Promise<string>((resolve, reject) => {
    let resolved = false
    const cleanup = () => { resolved = true }

    const timeout = setTimeout(() => {
      if (!resolved) {
        resolved = true
        subscription?.unsubscribe()
        clearInterval(retryInterval)
        // Final attempt before giving up
        supabase.auth.getSession().then(({ data: { session: finalSession } }) => {
          if (finalSession?.access_token) {
            cachedToken = finalSession.access_token
            resolve(finalSession.access_token)
          } else {
            reject(new Error('AUTH_TIMEOUT'))
          }
        })
      }
    }, timeoutMs)

    // Retry getSession every 500ms as fallback (onAuthStateChange may miss INITIAL_SESSION)
    const retryInterval = setInterval(() => {
      if (resolved) return
      supabase.auth.getSession().then(({ data: { session: retrySession } }) => {
        if (retrySession?.access_token && !resolved) {
          resolved = true
          clearTimeout(timeout)
          clearInterval(retryInterval)
          subscription?.unsubscribe()
          cachedToken = retrySession.access_token
          resolve(retrySession.access_token)
        }
      })
    }, 500)

    // Also listen for auth state changes
    let subscription: { unsubscribe: () => void } | null = null
    const { data: { subscription: sub } } = supabase.auth.onAuthStateChange((event, newSession) => {
      if (resolved) return
      if (newSession?.access_token) {
        resolved = true
        clearTimeout(timeout)
        clearInterval(retryInterval)
        subscription?.unsubscribe()
        cachedToken = newSession.access_token
        resolve(newSession.access_token)
      }
    })
    subscription = sub
  })
}

/**
 * Get auth headers, with automatic 401 retry via apiFetch.
 * 
 * IMPORTANT: API functions should use apiFetch() instead of raw fetch().
 * getAuthHeader() is kept for backward compatibility but does NOT handle 401 retries.
 * apiFetch() handles 401 by refreshing the token and retrying.
 */
async function getAuthHeader(): Promise<Record<string, string>> {
  try {
    const token = await waitForSession()
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    }
  } catch {
    // Session truly not available after waiting — redirect to login
    if (typeof window !== 'undefined') {
      const currentPath = window.location.pathname + window.location.search
      window.location.href = `/login?redirectTo=${encodeURIComponent(currentPath)}`
    }
    throw new Error('Authentication required')
  }
}

/**
 * Authenticated fetch that automatically:
 * 1. Waits for the session to be available
 * 2. Retries once on 401 (refreshes token first)
 * 3. Redirects to login on persistent 401
 * 
 * ALL API functions should use this instead of raw fetch().
 */
async function apiFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const headers = await getAuthHeader()
  const response = await fetch(url, {
    ...options,
    headers: {
      ...headers,
      ...options.headers,
    },
  })

  // Handle 401 — token may have expired, try refresh
  if (response.status === 401) {
    // Clear cached token — it's stale
    cachedToken = null

    // Force refresh the session
    const { data: { session } } = await supabase.auth.refreshSession()
    if (session?.access_token) {
      // Update cache with fresh token
      cachedToken = session.access_token
      // Retry with fresh token
      const retryHeaders = {
        'Authorization': `Bearer ${session.access_token}`,
        'Content-Type': 'application/json',
      }
      const retryResponse = await fetch(url, {
        ...options,
        headers: {
          ...retryHeaders,
          ...options.headers,
        },
      })
      if (retryResponse.status !== 401) {
        return retryResponse
      }
    }
    // Still 401 after refresh — redirect to login
    if (typeof window !== 'undefined') {
      const currentPath = window.location.pathname + window.location.search
      window.location.href = `/login?redirectTo=${encodeURIComponent(currentPath)}`
    }
    throw new Error('Session expired. Please sign in again.')
  }

  return response
}

// ============ Init API (Batch) ============

export interface InitUserProfile {
  id: string
  email: string
  full_name: string | null
  is_active: boolean
  subscription_tier: string
  monthly_usage_count: number
  monthly_usage_limit: number
}

export interface InitProjectItem {
  id: string
  name: string
  description: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface InitContentItem {
  id: string
  project_id: string
  title: string
  source_type: string
  status: string
  created_at: string
  updated_at: string
}

export interface InitUsageSummary {
  monthly_usage_count: number
  monthly_usage_limit: number
  remaining: number
  percentage_used: number
  subscription_tier: string
}

export interface InitDashboardKPIs {
  total_content: number
  total_assets: number
  total_distributions: number
  published_distributions: number
  content_growth_30d: number
  asset_growth_30d: number
  distribution_success_rate: number
}

export interface InitResponse {
  user: InitUserProfile
  projects: InitProjectItem[]
  content: InitContentItem[]
  usage: InitUsageSummary
  dashboard_kpis: InitDashboardKPIs
}

/**
 * Batch init — fetches all data needed on page load in a single request.
 * Replaces 5+ individual API calls (auth/me, projects, content, usage, analytics).
 * All sub-queries run in parallel on the backend.
 *
 * Uses stale-while-revalidate: returns cached data immediately if available,
 * then revalidates in the background.
 */
const INIT_CACHE_KEY = 'contentforge_init_data'
const INIT_CACHE_TTL_MS = 30_000 // 30 seconds — fresh enough for tab switching

function getCachedInit(): InitResponse | null {
  try {
    const raw = sessionStorage.getItem(INIT_CACHE_KEY)
    if (!raw) return null
    const { data, timestamp } = JSON.parse(raw)
    if (Date.now() - timestamp < INIT_CACHE_TTL_MS) {
      return data
    }
  } catch {
    // Corrupt cache — ignore
  }
  return null
}

function setCachedInit(data: InitResponse): void {
  try {
    sessionStorage.setItem(INIT_CACHE_KEY, JSON.stringify({ data, timestamp: Date.now() }))
  } catch {
    // Storage full or unavailable — ignore
  }
}

export async function getInit(forceRefresh = false): Promise<InitResponse> {
  // Return cached data immediately if available and not forced
  if (!forceRefresh) {
    const cached = getCachedInit()
    if (cached) {
      // Revalidate in background (fire-and-forget)
      apiFetch(`${API_URL}/init`).then(async (res) => {
        if (res.ok) {
          const fresh = await res.json()
          setCachedInit(fresh)
        }
      }).catch(() => {}) // Swallow background revalidation errors
      return cached
    }
  }

  const response = await apiFetch(`${API_URL}/init`)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to initialize app')
  }

  const data = await response.json()
  setCachedInit(data)
  return data
}

// ============ Content API ============

export async function createContent(data: ContentCreate): Promise<Content> {
    const response = await apiFetch(`${API_URL}/content`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create content')
  }
  
  return response.json()
}

export async function listContent(projectId?: string): Promise<Content[]> {
  let url = `${API_URL}/content`
  if (projectId) {
    url += `?project_id=${projectId}`
  }
  const response = await apiFetch(url)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch content')
  }
  
  return response.json()
}

export async function getContent(contentId: string): Promise<Content> {
    const response = await apiFetch(`${API_URL}/content/${contentId}`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch content')
  }
  
  return response.json()
}

export async function generateAssets(contentId: string): Promise<GeneratedAsset[]> {
    const response = await apiFetch(`${API_URL}/content/${contentId}/generate`, { method: 'POST' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to generate assets')
  }
  
  return response.json()
}

export async function listAssets(contentId: string): Promise<GeneratedAsset[]> {
    const response = await apiFetch(`${API_URL}/content/${contentId}/assets`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch assets')
  }
  
  return response.json()
}

export async function deleteContent(contentId: string): Promise<void> {
    const response = await apiFetch(`${API_URL}/content/${contentId}`, { method: 'DELETE' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to delete content')
  }
}

export interface Project {
  id: string
  user_id: string
  name: string
  description?: string
  brand_voice?: Record<string, unknown>
  target_platforms?: string[]
  is_active: boolean
  created_at: string
  updated_at: string
}

export async function listProjects(): Promise<Project[]> {
    const response = await apiFetch(`${API_URL}/projects`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch projects')
  }
  
  return response.json()
}

export async function createProject(data: { name: string; description?: string }): Promise<Project> {
    const response = await apiFetch(`${API_URL}/projects`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create project')
  }
  
  return response.json()
}

export async function getProject(projectId: string): Promise<Project> {
    const response = await apiFetch(`${API_URL}/projects/${projectId}`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch project')
  }
  
  return response.json()
}

export async function deleteProject(projectId: string): Promise<void> {
    const response = await apiFetch(`${API_URL}/projects/${projectId}`, { method: 'DELETE' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to delete project')
  }
}

export interface Distribution {
  id: string
  asset_id: string
  user_id: string
  platform: string
  status: 'pending' | 'scheduled' | 'publishing' | 'published' | 'failed' | 'cancelled'
  scheduled_at?: string
  published_at?: string
  published_url?: string
  external_id?: string
  retry_count: number
  created_at: string
  updated_at: string
}

export async function createDistribution(data: { asset_id: string; platform: string; scheduled_at?: string }): Promise<Distribution> {
    const response = await apiFetch(`${API_URL}/distributions`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to schedule distribution')
  }
  
  return response.json()
}

export async function listDistributions(status?: string): Promise<Distribution[]> {
  let url = `${API_URL}/distributions`
  if (status) {
    url += `?status=${status}`
  }
  const response = await apiFetch(url)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch distributions')
  }
  
  return response.json()
}

export async function publishNow(distributionId: string): Promise<Distribution> {
    const response = await apiFetch(`${API_URL}/distributions/${distributionId}/publish-now`, { method: 'POST' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to publish')
  }
  
  return response.json()
}

// Usage Types
export interface UsageStats {
  monthly_usage_count: number
  monthly_usage_limit: number
  remaining: number
  percentage_used: number
  subscription_tier: string
  reset_at?: string
}

export interface UsageActivity {
  event_type: string
  tokens_used?: number
  created_at: string
}

export interface UsageSummary {
  stats: UsageStats & { subscription_tier: string }
  recent_activity: UsageActivity[]
  status: 'active' | 'limit_reached'
}

export async function getUsageSummary(): Promise<UsageSummary> {
    const response = await apiFetch(`${API_URL}/usage/summary`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch usage summary')
  }
  
  return response.json()
}

// Analytics Types
export interface ContentStatusMetric {
  status: string
  count: number
}

export interface ContentMetricsResponse {
  total_content: number
  by_status: ContentStatusMetric[]
  total_views?: number
  last_30_days_count: number
}

export interface AssetTypeMetric {
  type: string
  count: number
}

export interface AssetPlatformMetric {
  platform: string | null
  count: number
}

export interface AssetMetricsResponse {
  total_assets: number
  by_type: AssetTypeMetric[]
  by_platform: AssetPlatformMetric[]
}

export interface DailyUsageMetric {
  date: string
  count: number
}

export interface WeeklyUsageMetric {
  week: string
  count: number
}

export interface MonthlyUsageMetric {
  month: string
  count: number
}

export interface UsageMetricsResponse {
  daily_counts: DailyUsageMetric[]
  weekly_counts: WeeklyUsageMetric[]
  monthly_counts: MonthlyUsageMetric[]
  total_in_period: number
  average_daily: number
}

export interface DistributionStatusMetric {
  status: string
  count: number
}

export interface PlatformDistributionMetric {
  platform: string
  count: number
  success_rate: number
}

export interface DistributionMetricsResponse {
  total_distributions: number
  by_status: DistributionStatusMetric[]
  by_platform: PlatformDistributionMetric[]
  success_rate: number
}

export interface KPIDashboardResponse {
  total_content: number
  total_assets: number
  total_distributions: number
  published_distributions: number
  content_growth_30d: number
  asset_growth_30d: number
  distribution_success_rate: number
}

export async function getContentMetrics(): Promise<ContentMetricsResponse> {
    const response = await apiFetch(`${API_URL}/analytics/content`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch content metrics')
  }
  
  return response.json()
}

export async function getAssetMetrics(): Promise<AssetMetricsResponse> {
    const response = await apiFetch(`${API_URL}/analytics/assets`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch asset metrics')
  }
  
  return response.json()
}

export async function getUsageMetrics(days: number = 30): Promise<UsageMetricsResponse> {
    const response = await apiFetch(`${API_URL}/analytics/usage?days=${days}`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch usage metrics')
  }
  
  return response.json()
}

export async function getDistributionMetrics(): Promise<DistributionMetricsResponse> {
    const response = await apiFetch(`${API_URL}/analytics/distributions`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch distribution metrics')
  }
  
  return response.json()
}

export async function getDashboardKPIs(): Promise<KPIDashboardResponse> {
    const response = await apiFetch(`${API_URL}/analytics/dashboard`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch dashboard KPIs')
  }
  
  return response.json()
}

export async function exportAnalyticsCSV(days: number = 30): Promise<Blob> {
    const response = await apiFetch(`${API_URL}/analytics/export?format=csv&days=${days}`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to export analytics')
  }
  
  return response.blob()
}

export async function exportAnalyticsJSON(days: number = 30): Promise<Blob> {
    const response = await apiFetch(`${API_URL}/analytics/export/json?days=${days}`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to export analytics')
  }
  
  return response.blob()
}

// ============ AI Suggestions Types ============

export interface AIImprovementSuggestion {
  id: string
  content_id: string
  user_id: string
  suggestion_type: string
  original_text: string
  improved_text: string
  explanation: string
  confidence_score: number
  applied: boolean
  created_at: string
}

export interface SEOAnalysisResult {
  id: string
  content_id: string
  user_id: string
  seo_score: number
  keyword_density: Record<string, number>
  readability_score: number
  suggestions: string[]
  meta_title_suggestion: string | null
  meta_description_suggestion: string | null
  heading_structure_suggestions: string[]
  created_at: string
}

export interface ToneAdjustmentResult {
  id: string
  content_id: string
  user_id: string
  original_tone: string
  target_tone: string
  adjusted_text: string
  tone_characteristics: Record<string, unknown>
  created_at: string
}

export async function getContentImprovements(
  contentId: string,
  suggestionType: 'readability' | 'engagement' | 'clarity' | 'grammar'
): Promise<AIImprovementSuggestion> {
    const response = await apiFetch(`${API_URL}/ai-suggestions/improve`, { method: 'POST', body: JSON.stringify({ content_id: contentId, suggestion_type: suggestionType  }),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to get content improvements')
  }
  
  return response.json()
}

export async function getSEOOtimization(
  contentId: string,
  keywords?: string[],
  targetAudience?: string
): Promise<SEOAnalysisResult> {
    const response = await apiFetch(`${API_URL}/ai-suggestions/seo`, { method: 'POST', body: JSON.stringify({ content_id: contentId, keywords, target_audience: targetAudience  }),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to get SEO analysis')
  }
  
  return response.json()
}

export async function adjustContentTone(
  contentId: string,
  tone: 'professional' | 'casual' | 'humorous' | 'formal' | 'friendly' | 'authoritative'
): Promise<ToneAdjustmentResult> {
    const response = await apiFetch(`${API_URL}/ai-suggestions/tone`, { method: 'POST', body: JSON.stringify({ content_id: contentId, tone  }),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to adjust tone')
  }
  
  return response.json()
}

export async function listAISuggestions(
  contentId: string,
  suggestionType?: string
): Promise<AIImprovementSuggestion[]> {
  let url = `${API_URL}/ai-suggestions/${contentId}`
  if (suggestionType) {
    url += `?suggestion_type=${suggestionType}`
  }
  const response = await apiFetch(url)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to list AI suggestions')
  }
  
  return response.json()
}

export async function applySuggestion(suggestionId: string): Promise<AIImprovementSuggestion> {
    const response = await apiFetch(`${API_URL}/ai-suggestions/${suggestionId}/apply`, { method: 'PATCH' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to apply suggestion')
  }
  
  return response.json()
}

// ============ Automation Types ============

export interface AutomationRule {
  id: string
  name: string
  description?: string
  project_id?: string
  user_id: string
  trigger_type: string
  trigger_config?: Record<string, unknown>
  conditions?: Record<string, unknown>[]
  action_type: string
  action_config: Record<string, unknown>
  schedule_config?: Record<string, unknown>
  webhook_config?: Record<string, unknown>
  status: string
  last_run_at?: string
  next_run_at?: string
  run_count: number
  success_count: number
  fail_count: number
  created_at: string
  updated_at: string
}

export interface AutomationLog {
  id: string
  rule_id: string
  user_id: string
  status: string
  triggered_by: string
  input_data?: Record<string, unknown>
  output_data?: Record<string, unknown>
  error_message?: string
  execution_time_ms?: number
  created_at: string
}

export interface WebhookEndpoint {
  id: string
  name: string
  description?: string
  project_id?: string
  user_id: string
  endpoint_url: string
  secret?: string
  allowed_ips?: string[]
  is_active: boolean
  total_calls: number
  last_called_at?: string
  created_at: string
}

export interface QueueItem {
  id: string
  user_id: string
  content_id: string
  asset_id?: string
  platform: string
  status: string
  scheduled_for?: string
  published_at?: string
  error_message?: string
  retry_count: number
  created_at: string
  updated_at: string
}

export async function createAutomationRule(rule: {
  name: string
  description?: string
  project_id?: string
  trigger_type: string
  action_type: string
  action_config: Record<string, unknown>
  enabled?: boolean
}): Promise<AutomationRule> {
    const response = await apiFetch(`${API_URL}/automation/rules`, {
    method: 'POST',
    body: JSON.stringify(rule),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create automation rule')
  }
  
  return response.json()
}

export async function listAutomationRules(
  projectId?: string,
  status?: string
): Promise<AutomationRule[]> {
  let url = `${API_URL}/automation/rules`
  const params = new URLSearchParams()
  if (projectId) params.append('project_id', projectId)
  if (status) params.append('status', status)
  if (params.toString()) url += `?${params.toString()}`
  const response = await apiFetch(url)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch automation rules')
  }
  
  return response.json()
}

export async function getAutomationRule(ruleId: string): Promise<AutomationRule> {
    const response = await apiFetch(`${API_URL}/automation/rules/${ruleId}`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch automation rule')
  }
  
  return response.json()
}

export async function toggleAutomationRule(ruleId: string): Promise<{ status: string }> {
    const response = await apiFetch(`${API_URL}/automation/rules/${ruleId}/toggle`, { method: 'POST' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to toggle automation rule')
  }
  
  return response.json()
}

export async function runAutomationRule(ruleId: string): Promise<{ message: string; log_id: string }> {
    const response = await apiFetch(`${API_URL}/automation/rules/${ruleId}/run`, { method: 'POST' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to run automation rule')
  }
  
  return response.json()
}

export async function listAutomationLogs(ruleId?: string): Promise<AutomationLog[]> {
  let url = `${API_URL}/automation/logs`
  if (ruleId) url += `?rule_id=${ruleId}`
  const response = await apiFetch(url)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch automation logs')
  }
  
  return response.json()
}

export async function getBestPostingTime(platform: string): Promise<{
  platform: string
  best_times: string[]
  timezone_recommendation: string
  frequency_recommendation: string
}> {
    const response = await apiFetch(`${API_URL}/automation/best-times/${platform}`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch best posting times')
  }
  
  return response.json()
}

export async function bulkScheduleContent(
  contentIds: string[],
  platform: string,
  startTime: string,
  intervalMinutes: number
): Promise<{
  scheduled_count: number
  start_time: string
  end_time: string
  queue_items: string[]
}> {
  const response = await apiFetch(`${API_URL}/automation/schedule/bulk`, {
    method: 'POST',
    body: JSON.stringify({
      content_ids: contentIds,
      platform,
      start_time: startTime,
      interval_minutes: intervalMinutes,
    }),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to bulk schedule content')
  }
  
  return response.json()
}

export async function getPublishingQueue(status?: string): Promise<QueueItem[]> {
  let url = `${API_URL}/automation/queue`
  if (status) url += `?status=${status}`
  const response = await apiFetch(url)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch publishing queue')
  }
  
  return response.json()
}

export async function cancelQueueItem(queueId: string): Promise<{ message: string }> {
    const response = await apiFetch(`${API_URL}/automation/queue/${queueId}/cancel`, { method: 'POST' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to cancel queue item')
  }
  
  return response.json()
}

// ============ Scheduled Publishing Types ============

export interface ScheduleRequest {
  asset_id: string
  content: string
  platforms: string[]
  scheduled_at: string
  timezone?: string
  recurring_pattern?: string
  metadata?: Record<string, unknown>
}

export interface ScheduledPost {
  id: string
  asset_id: string
  user_id: string
  content: string
  platforms: string[]
  scheduled_at: string
  timezone: string
  status: 'scheduled' | 'published' | 'failed' | 'cancelled' | 'processing'
  recurring_pattern?: string
  recurring_parent_id?: string
  published_at?: string
  published_url?: string
  error_message?: string
  metadata?: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface ScheduleConflict {
  schedule_id: string
  scheduled_at: string
  platforms: string[]
  conflict_type: 'time' | 'platform'
}

export async function schedulePost(request: ScheduleRequest): Promise<ScheduledPost> {
    const response = await apiFetch(`${API_URL}/schedule`, {
    method: 'POST',
    body: JSON.stringify(request),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to schedule post')
  }
  
  return response.json()
}

export async function getScheduledPosts(
  status?: string,
  startDate?: string,
  endDate?: string
): Promise<ScheduledPost[]> {
  let url = `${API_URL}/schedule`
  const params = new URLSearchParams()
  if (status) params.append('status', status)
  if (startDate) params.append('start_date', startDate)
  if (endDate) params.append('end_date', endDate)
  if (params.toString()) url += `?${params.toString()}`
  const response = await apiFetch(url)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch scheduled posts')
  }
  
  return response.json()
}

export async function getScheduledPost(scheduleId: string): Promise<ScheduledPost> {
    const response = await apiFetch(`${API_URL}/schedule/${scheduleId}`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch scheduled post')
  }
  
  return response.json()
}

export async function updateScheduledPost(
  scheduleId: string, 
  updates: Partial<ScheduleRequest>
): Promise<ScheduledPost> {
    const response = await apiFetch(`${API_URL}/schedule/${scheduleId}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update scheduled post')
  }
  
  return response.json()
}

export async function cancelScheduledPost(scheduleId: string): Promise<{ message: string }> {
    const response = await apiFetch(`${API_URL}/schedule/${scheduleId}/cancel`, { method: 'POST' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to cancel scheduled post')
  }
  
  return response.json()
}

export async function publishScheduledPost(scheduleId: string): Promise<ScheduledPost> {
    const response = await apiFetch(`${API_URL}/schedule/${scheduleId}/publish-now`, { method: 'POST' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to publish now')
  }
  
  return response.json()
}

export async function checkScheduleConflicts(
  scheduledAt: string,
  platforms: string[],
  excludeId?: string
): Promise<ScheduleConflict[]> {
  const params = new URLSearchParams()
  params.append('scheduled_at', scheduledAt)
  platforms.forEach(p => params.append('platforms', p))
  if (excludeId) params.append('exclude_id', excludeId)
  const response = await apiFetch(`${API_URL}/schedule/conflicts?${params.toString()}`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to check conflicts')
  }
  
  return response.json()
}

export async function getUpcomingPosts(limit: number = 5): Promise<ScheduledPost[]> {
    const response = await apiFetch(`${API_URL}/schedule/upcoming?limit=${limit}`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch upcoming posts')
  }
  
  return response.json()
}

export async function duplicateSchedule(
  scheduleId: string, 
  newScheduledAt?: string
): Promise<ScheduledPost> {
    const body: Record<string, string | undefined> = {}
  if (newScheduledAt) body.scheduled_at = newScheduledAt
  
  const response = await apiFetch(`${API_URL}/schedule/${scheduleId}/duplicate`, { method: 'POST', body: JSON.stringify(body) })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to duplicate schedule')
  }
  
  return response.json()
}

// ============ End Scheduled Publishing ============

// ============ End Advanced Features ============

export interface AnalyticsSummaryData {
  contentMetrics: ContentMetricsResponse
  assetMetrics: AssetMetricsResponse
  usageMetrics: UsageMetricsResponse
  distributionMetrics: DistributionMetricsResponse
  dashboardKPIs: KPIDashboardResponse
  usageSummary: UsageSummary
}

export async function getAnalyticsSummary(days: number = 30): Promise<AnalyticsSummaryData> {
  const [contentMetrics, assetMetrics, usageMetrics, distributionMetrics, dashboardKPIs, usageSummary] = await Promise.all([
    getContentMetrics().catch(() => ({ total_content: 0, by_status: [], last_30_days_count: 0 })),
    getAssetMetrics().catch(() => ({ total_assets: 0, by_type: [], by_platform: [] })),
    getUsageMetrics(days).catch(() => ({ daily_counts: [], weekly_counts: [], monthly_counts: [], total_in_period: 0, average_daily: 0 })),
    getDistributionMetrics().catch(() => ({ total_distributions: 0, by_status: [], by_platform: [], success_rate: 0 })),
    getDashboardKPIs().catch(() => ({ total_content: 0, total_assets: 0, total_distributions: 0, published_distributions: 0, content_growth_30d: 0, asset_growth_30d: 0, distribution_success_rate: 0 })),
    getUsageSummary().catch(() => ({ stats: { monthly_usage_count: 0, monthly_usage_limit: 100, remaining: 100, percentage_used: 0, subscription_tier: 'free' }, recent_activity: [], status: 'active' as const })),
  ])
  
  return {
    contentMetrics,
    assetMetrics,
    usageMetrics,
    distributionMetrics,
    dashboardKPIs,
    usageSummary,
  }
}

// Legacy Analytics Stats - for backward compatibility
export interface AnalyticsStats {
  content_count: number
  assets_generated: number
  distributions_published: number
}

export async function getAnalyticsStats(): Promise<AnalyticsStats> {
  const [content, distributions] = await Promise.all([
    listContent(),
    listDistributions('published')
  ])
  
  let totalAssets = 0
  for (const item of content) {
    try {
      const assets = await listAssets(item.id)
      totalAssets += assets.length
    } catch {
      // Skip if error
    }
  }
  
  return {
    content_count: content.length,
    assets_generated: totalAssets,
    distributions_published: distributions.length,
  }
}

// User Profile
export interface UserProfile {
  id: string
  email: string
  full_name?: string
  subscription_tier: string
  monthly_usage_count: number
  monthly_usage_limit: number
}

export async function getUserProfile(): Promise<UserProfile> {
    const response = await apiFetch(`${API_URL}/auth/me`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch profile')
  }
  
  return response.json()
}

export async function updateUserProfile(data: { full_name: string }): Promise<UserProfile> {
    const response = await apiFetch(`${API_URL}/auth/me`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update profile')
  }
  
  return response.json()
}

// API Keys (mock for now - would come from backend)
export interface ApiKeys {
  stripe_key?: string
  groq_key?: string // Server-side only; never exposed to frontend
}

export async function getApiKeys(): Promise<ApiKeys> {
  return {
    stripe_key: process.env.NEXT_PUBLIC_STRIPE_KEY,
    groq_key: undefined, // Groq key is server-side only; use backend /api/ai/* endpoints
  }
}

// Organization Types
export type OrganizationRole = 'admin' | 'member'

export interface Organization {
  id: string
  name: string
  owner_id: string
  created_at: string
  updated_at: string
  member_count?: number
  is_owner?: boolean
}

export interface OrganizationMember {
  id: string
  org_id: string
  user_id: string
  role: OrganizationRole
  created_at: string
  user_email?: string
  user_name?: string
  avatar_url?: string
}

export interface OrganizationWithMembers extends Organization {
  members: OrganizationMember[]
  current_user_role?: string
}

export interface OrganizationCreate {
  name: string
}

export interface OrganizationUpdate {
  name?: string
}

export interface OrganizationInvite {
  email: string
  role: OrganizationRole
}

export interface OrganizationInvitationResponse {
  message: string
  email: string
  org_id: string
}

// Organization API Functions

export async function listOrganizations(): Promise<Organization[]> {
    const response = await apiFetch(`${API_URL}/organizations`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch organizations')
  }
  
  return response.json()
}

export async function createOrganization(data: OrganizationCreate): Promise<Organization> {
    const response = await apiFetch(`${API_URL}/organizations`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create organization')
  }
  
  return response.json()
}

export async function getOrganization(orgId: string): Promise<OrganizationWithMembers> {
    const response = await apiFetch(`${API_URL}/organizations/${orgId}`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch organization')
  }
  
  return response.json()
}

export async function updateOrganization(orgId: string, data: OrganizationUpdate): Promise<Organization> {
    const response = await apiFetch(`${API_URL}/organizations/${orgId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update organization')
  }
  
  return response.json()
}

export async function deleteOrganization(orgId: string): Promise<void> {
    const response = await apiFetch(`${API_URL}/organizations/${orgId}`, { method: 'DELETE' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to delete organization')
  }
}

export async function inviteMember(orgId: string, data: OrganizationInvite): Promise<OrganizationInvitationResponse> {
    const response = await apiFetch(`${API_URL}/organizations/${orgId}/invite`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to invite member')
  }
  
  return response.json()
}

export async function listMembers(orgId: string): Promise<OrganizationMember[]> {
    const response = await apiFetch(`${API_URL}/organizations/${orgId}/members`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch members')
  }
  
  return response.json()
}

export async function updateMemberRole(orgId: string, memberId: string, role: OrganizationRole): Promise<OrganizationMember> {
    const response = await apiFetch(`${API_URL}/organizations/${orgId}/members/${memberId}`, { method: 'PATCH', body: JSON.stringify({ role  }),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update member role')
  }
  
  return response.json()
}

export async function removeMember(orgId: string, memberId: string): Promise<void> {
    const response = await apiFetch(`${API_URL}/organizations/${orgId}/members/${memberId}`, { method: 'DELETE' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to remove member')
  }
}

export async function transferOwnership(orgId: string, newOwnerId: string): Promise<{ message: string; organization_id: string; new_owner_id: string }> {
    const response = await apiFetch(`${API_URL}/organizations/${orgId}/transfer-ownership`, { method: 'POST', body: JSON.stringify({ new_owner_id: newOwnerId  }),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to transfer ownership')
  }
  
  return response.json()
}

export async function leaveOrganization(orgId: string): Promise<void> {
    const response = await apiFetch(`${API_URL}/organizations/${orgId}/leave`, { method: 'POST' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to leave organization')
  }
}

// ============ GDPR / User Data Compliance ============

export interface UserDataExport {
  export_id: string
  user_data: {
    export_metadata: {
      user_id: string
      email: string
      export_date: string
      version: string
    }
    profile: Record<string, unknown>
    content: Record<string, unknown>[]
    projects: Record<string, unknown>[]
    assets: Record<string, unknown>[]
    distributions: Record<string, unknown>[]
    organizations: Record<string, unknown>[]
    usage_logs: Record<string, unknown>[]
  }
  generated_at: string
  expires_at: string
}

export interface AccountDeletionResponse {
  message: string
  deleted_at?: string
  grace_period_ends?: string
}

export interface DeletionStatusResponse {
  deletion_scheduled: boolean
  status?: string
  requested_at?: string
  scheduled_deletion_at?: string
  days_remaining?: number
  message?: string
}

/**
 * Export all user data for GDPR data portability.
 * Returns JSON with all user data including content, projects, assets, and distributions.
 */
export async function exportUserData(): Promise<UserDataExport> {
    const response = await apiFetch(`${API_URL}/user/export-data`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to export user data')
  }
  
  return response.json()
}

/**
 * Request account deletion with 30-day grace period (GDPR-compliant soft delete).
 */
export async function deleteUserAccount(): Promise<AccountDeletionResponse> {
    const response = await apiFetch(`${API_URL}/user/account`, { method: 'DELETE' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to request account deletion')
  }
  
  return response.json()
}

/**
 * Restore a user account that was scheduled for deletion (within grace period).
 */
export async function restoreUserAccount(): Promise<{ message: string }> {
    const response = await apiFetch(`${API_URL}/user/account/restore`, { method: 'POST' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to restore account')
  }
  
  return response.json()
}

/**
 * Check the status of an account deletion request.
 */
export async function getDeletionStatus(): Promise<DeletionStatusResponse> {
    const response = await apiFetch(`${API_URL}/user/deletion-status`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to get deletion status')
  }
  
  return response.json()
}

// ============ End GDPR / User Data Compliance ============

// ============ Search & Trash API ============

export interface SearchResult {
  id: string
  type: 'content' | 'project' | 'asset'
  title: string
  description?: string
  matched_field: string
  matched_text: string
  score: number
  created_at: string
  project_id?: string
  project_name?: string
}

export interface SearchResponse {
  query: string
  total: number
  results: SearchResult[]
  filters_applied?: Record<string, string>
}

export interface SearchSuggestion {
  text: string
  type: string
}

export interface TrashItem {
  id: string
  type: 'content' | 'project' | 'asset'
  original_data: Record<string, unknown>
  deleted_at: string
  expires_at: string
}

export interface TrashStats {
  total: number
  content_count: number
  project_count: number
  retention_days: number
}

export async function searchContent(
  query: string,
  options?: {
    type?: 'content' | 'project' | 'asset'
    projectId?: string
    status?: string
    limit?: number
  }
): Promise<SearchResponse> {
  const params = new URLSearchParams()
  params.append('q', query)
  if (options?.type) params.append('type', options.type)
  if (options?.projectId) params.append('project_id', options.projectId)
  if (options?.status) params.append('status', options.status)
  if (options?.limit) params.append('limit', options.limit.toString())
  const response = await apiFetch(`${API_URL}/search?${params.toString()}`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Search failed')
  }
  
  return response.json()
}

export async function getSearchSuggestions(query: string): Promise<{
  query: string
  suggestions: SearchSuggestion[]
}> {
    const response = await apiFetch(`${API_URL}/search/suggestions?q=${encodeURIComponent(query)}`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to get suggestions')
  }
  
  return response.json()
}

export async function getTrashItems(type?: 'content' | 'project' | 'asset'): Promise<TrashItem[]> {
    let url = `${API_URL}/trash`
  if (type) url += `?item_type=${type}`
  const response = await apiFetch(url)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch trash')
  }
  
  return response.json()
}

export async function getTrashStats(): Promise<TrashStats> {
    const response = await apiFetch(`${API_URL}/trash/stats`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch trash stats')
  }
  
  return response.json()
}

export async function restoreFromTrash(itemId: string): Promise<{
  message: string
  item_id: string
  restored: boolean
}> {
    const response = await apiFetch(`${API_URL}/trash/${itemId}/restore`, { method: 'POST' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to restore item')
  }
  
  return response.json()
}

export async function permanentlyDeleteFromTrash(itemId: string): Promise<{
  message: string
  item_id: string
  deleted: boolean
}> {
    const response = await apiFetch(`${API_URL}/trash/${itemId}`, { method: 'DELETE' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to delete item')
  }
  
  return response.json()
}

export async function emptyTrash(): Promise<{
  message: string
  items_deleted: number
}> {
    const response = await apiFetch(`${API_URL}/trash/empty`, { method: 'POST' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to empty trash')
  }
  
  return response.json()
}

// ============ End Search & Trash API ============

// ============ Smart Content Editor API ============

export interface RewriteResult {
  content: string
  tokens_used: number
}

export interface ExpandResult {
  content: string
  tokens_used: number
  original_length: number
  new_length: number
}

export interface CondenseResult {
  content: string
  tokens_used: number
  reduction_percentage: number
}

export interface OptimizeResult {
  content: string
  tokens_used: number
  platform: string
  optimizations_applied: string[]
}

/**
 * Rewrite content with different tone and style
 */
export async function rewriteContent(
  content: string,
  tone: string,
  style: string
): Promise<string> {
    const response = await apiFetch(`${API_URL}/ai-suggestions/rewrite`, { method: 'POST', body: JSON.stringify({ content, tone, style  }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to rewrite content')
  }

  const result: RewriteResult = await response.json()
  return result.content
}

/**
 * Expand content to target length
 */
export async function expandContent(
  content: string,
  targetLength: number
): Promise<string> {
    const response = await apiFetch(`${API_URL}/ai-suggestions/expand`, { method: 'POST', body: JSON.stringify({ content, target_length: targetLength  }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to expand content')
  }

  const result: ExpandResult = await response.json()
  return result.content
}

/**
 * Condense content by percentage
 */
export async function condenseContent(
  content: string,
  percentage: number
): Promise<string> {
    const response = await apiFetch(`${API_URL}/ai-suggestions/condense`, { method: 'POST', body: JSON.stringify({ content, percentage  }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to condense content')
  }

  const result: CondenseResult = await response.json()
  return result.content
}

/**
 * Optimize content for specific platform
 */
export async function optimizeContent(
  content: string,
  platform: string
): Promise<string> {
    const response = await apiFetch(`${API_URL}/ai-suggestions/optimize`, { method: 'POST', body: JSON.stringify({ content, platform  }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to optimize content')
  }

  const result: OptimizeResult = await response.json()
  return result.content
}

/**
 * Update content text
 */
export async function updateContent(contentId: string, data: { original_text: string }): Promise<Content> {
    const response = await apiFetch(`${API_URL}/content/${contentId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update content')
  }

  return response.json()
}

// ============ End Smart Content Editor API ============

// ============ Freshness API ============

export interface FreshnessAnalysis {
  content_id: string
  freshness_score: number
  last_updated: string
  recommendations: string[]
  trend: 'up' | 'down' | 'stable'
  trend_value: number
}

export interface FreshnessMetrics {
  average_score: number
  total_content: number
  stale_count: number
  fresh_count: number
  needs_attention: number
  last_scan: string
}

export async function analyzeFreshness(contentId: string): Promise<FreshnessAnalysis> {
    const response = await apiFetch(`${API_URL}/freshness/${contentId}/analyze`, { method: 'POST' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to analyze freshness')
  }
  
  return response.json()
}

export async function getStaleContent(): Promise<Content[]> {
    const response = await apiFetch(`${API_URL}/freshness/stale`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch stale content')
  }
  
  return response.json()
}

export async function getFreshnessMetrics(): Promise<FreshnessMetrics> {
    const response = await apiFetch(`${API_URL}/freshness/metrics`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch freshness metrics')
  }
  
  return response.json()
}

export async function bulkRefreshContent(contentIds?: string[]): Promise<{ refreshed: number }> {
    const response = await apiFetch(`${API_URL}/freshness/bulk-refresh`, { method: 'POST', body: JSON.stringify({ content_ids: contentIds  }),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to bulk refresh')
  }
  
  return response.json()
}

// ============ Trending Topics API ============

export interface TrendingTopicData {
  id: string
  topic: string
  category: string | null
  trend_score: number | null
  mention_count: number | null
  velocity: number | null
  source: string | null
  discovered_at: string
  expires_at: string | null
  related_keywords: string[] | null
  sample_content: Array<{ title: string; url: string }> | null
}

export interface TrendingTopicWithRelevanceData extends TrendingTopicData {
  relevance_score: number
}

export interface TrendCategoryData {
  category: string
  topics: TrendingTopicData[]
  topic_count: number
}

export interface TrackTopicRequestData {
  topic_id: string
  relevance_score?: number
}

export interface TrackTopicResponseData {
  success: boolean
  message: string
}

export interface TrendVelocityData {
  id: string
  topic: string
  velocity: number
  category: string | null
}

// Legacy Trend interface kept for backward compatibility
export interface Trend {
  id: string
  title: string
  category: string
  velocity: number
  relevance_score: number
  mention_count: number
  growth_rate: number
  is_hot: boolean
  is_cold: boolean
  timestamp: string
  related_hashtags: string[]
  description?: string
}

export async function getTrendingTopics(category?: string, limit?: number, minScore?: number): Promise<TrendingTopicData[]> {
  const params = new URLSearchParams()
  if (category) params.append('category', category)
  if (limit) params.append('limit', limit.toString())
  if (minScore !== undefined) params.append('min_score', minScore.toString())
  const url = `${API_URL}/trends${params.toString() ? `?${params.toString()}` : ''}`
  const response = await apiFetch(url)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch trending topics')
  }
  
  return response.json()
}

export async function getRelevantTrends(limit?: number): Promise<TrendingTopicWithRelevanceData[]> {
  const params = new URLSearchParams()
  if (limit) params.append('limit', limit.toString())
  const url = `${API_URL}/trends/relevant${params.toString() ? `?${params.toString()}` : ''}`
  const response = await apiFetch(url)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch relevant trends')
  }
  
  return response.json()
}

export async function getTrendsByCategory(): Promise<TrendCategoryData[]> {
  const response = await apiFetch(`${API_URL}/trends/categories`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch trends by category')
  }
  
  return response.json()
}

export async function trackTopic(request: TrackTopicRequestData): Promise<TrackTopicResponseData> {
  const response = await apiFetch(`${API_URL}/trends/track`, {
    method: 'POST',
    body: JSON.stringify(request),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to track topic')
  }
  
  return response.json()
}

export async function getTrackedTopics(): Promise<Array<Record<string, unknown>>> {
  const response = await apiFetch(`${API_URL}/trends/tracked`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch tracked topics')
  }
  
  return response.json()
}

export async function untrackTopic(topicId: string): Promise<void> {
  const response = await apiFetch(`${API_URL}/trends/tracked/${topicId}`, { method: 'DELETE' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to untrack topic')
  }
}

export async function getTrendsVelocity(limit?: number): Promise<TrendVelocityData[]> {
  const params = new URLSearchParams()
  if (limit) params.append('limit', limit.toString())
  const url = `${API_URL}/trends/velocity${params.toString() ? `?${params.toString()}` : ''}`
  const response = await apiFetch(url)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch velocity data')
  }
  
  return response.json()
}

export async function generateFromTrend(topicId: string, request?: { topic?: string; category?: string; platform?: string; tone?: string }): Promise<Content> {
    const response = await apiFetch(`${API_URL}/trends/${topicId}/generate`, {
      method: 'POST',
      body: JSON.stringify(request || {}),
    })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to generate content from trend')
  }
  
  return response.json()
}

// ============ End Trending Topics API ============

// ============ RSS Feed API ============

export interface RSSFeed {
  id: string
  name: string
  url: string
  frequency: 'manual' | 'hourly' | 'daily' | 'weekly'
  is_active: boolean
  last_fetched_at?: string
  last_fetch_status?: 'success' | 'failed' | 'pending'
  entry_count: number
  created_at: string
  updated_at: string
}

export interface RSSFeedRequest {
  name: string
  url: string
  frequency: 'manual' | 'hourly' | 'daily' | 'weekly'
  is_active?: boolean
}

export interface RSSEntry {
  id: string
  feed_id: string
  feed_name: string
  title: string
  description?: string
  content?: string
  link: string
  published_at: string
  author?: string
  categories?: string[]
  image_url?: string
  is_imported: boolean
  imported_as_content_id?: string
  created_at: string
}

export interface RSSStats {
  total_feeds: number
  active_feeds: number
  total_entries: number
  unimported_entries: number
  recent_entries_count: number
}

export async function addRSSFeed(feed: RSSFeedRequest): Promise<RSSFeed> {
    const response = await apiFetch(`${API_URL}/rss/feeds`, {
    method: 'POST',
    body: JSON.stringify(feed),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to add RSS feed')
  }
  
  return response.json()
}

export async function getRSSFeeds(): Promise<RSSFeed[]> {
    const response = await apiFetch(`${API_URL}/rss/feeds`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch RSS feeds')
  }
  
  return response.json()
}

export async function updateRSSFeed(id: string, updates: Partial<RSSFeedRequest>): Promise<RSSFeed> {
    const response = await apiFetch(`${API_URL}/rss/feeds/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update RSS feed')
  }
  
  return response.json()
}

export async function deleteRSSFeed(id: string): Promise<void> {
    const response = await apiFetch(`${API_URL}/rss/feeds/${id}`, { method: 'DELETE' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to delete RSS feed')
  }
}

export async function fetchRSSFeed(id: string): Promise<{ message: string; entries_fetched: number }> {
    const response = await apiFetch(`${API_URL}/rss/feeds/${id}/fetch`, { method: 'POST' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch RSS feed')
  }
  
  return response.json()
}

export async function getRSSEntries(
  options?: {
    feedId?: string
    processed?: boolean
    limit?: number
    offset?: number
    startDate?: string
    endDate?: string
  }
): Promise<RSSEntry[]> {
  const params = new URLSearchParams()
  if (options?.feedId) params.append('feed_id', options.feedId)
  if (options?.processed !== undefined) params.append('processed', String(options.processed))
  if (options?.limit) params.append('limit', options.limit.toString())
  if (options?.offset) params.append('offset', options.offset.toString())
  if (options?.startDate) params.append('start_date', options.startDate)
  if (options?.endDate) params.append('end_date', options.endDate)
  
  const url = `${API_URL}/rss/entries${params.toString() ? `?${params.toString()}` : ''}`
  const response = await apiFetch(url)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch RSS entries')
  }
  
  return response.json()
}

export async function importRSSEntry(id: string, projectId?: string): Promise<Content> {
    const body: { entry_id: string; project_id?: string } = { entry_id: id }
  if (projectId) body.project_id = projectId
  
  const response = await apiFetch(`${API_URL}/rss/entries/import`, { method: 'POST', body: JSON.stringify(body) })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to import RSS entry')
  }
  
  return response.json()
}

export async function bulkImportRSSEntries(entryIds: string[], projectId?: string): Promise<{ imported: number; failed: number; content_ids: string[] }> {
    const response = await apiFetch(`${API_URL}/rss/entries/bulk-import`, { method: 'POST', body: JSON.stringify({ entry_ids: entryIds, project_id: projectId  }),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to bulk import entries')
  }
  
  return response.json()
}

export async function getRSSStats(): Promise<RSSStats> {
    const response = await apiFetch(`${API_URL}/rss/stats`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch RSS stats')
  }
  
  return response.json()
}

export async function getRSSSettings(): Promise<{
  auto_import: boolean
  default_project_id?: string
  notification_email?: boolean
  notification_in_app: boolean
}> {
    const response = await apiFetch(`${API_URL}/rss/settings`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch RSS settings')
  }
  
  return response.json()
}

export async function updateRSSSettings(settings: {
  auto_import?: boolean
  default_project_id?: string | null
  notification_email?: boolean
  notification_in_app?: boolean
}): Promise<{
  auto_import: boolean
  default_project_id?: string
  notification_email?: boolean
  notification_in_app: boolean
}> {
    const response = await apiFetch(`${API_URL}/rss/settings`, {
    method: 'PATCH',
    body: JSON.stringify(settings),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update RSS settings')
  }
  
  return response.json()
}

export async function markRSSEntryAsRead(id: string): Promise<void> {
    const response = await apiFetch(`${API_URL}/rss/entries/${id}/read`, { method: 'POST' })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to mark entry as read')
  }
}

// ============ End RSS Feed API ============

// ============ Version History API ============

export interface ContentVersion {
  id: string
  content_id: string
  version_number: number
  content_text: string
  title: string
  change_summary: string
  is_auto_version: boolean
  created_at: string
  created_by: string
  word_count: number
  diff_from_previous?: VersionDiff
}

export interface VersionDiff {
  additions: number
  deletions: number
  unchanged: number
  diff_html: string
}

export interface VersionComparison {
  old_version: ContentVersion
  new_version: ContentVersion
  diff: VersionDiff
}

export interface VersionHistoryResponse {
  content_id: string
  versions: ContentVersion[]
  total_versions: number
}

export async function getContentVersions(contentId: string): Promise<VersionHistoryResponse> {
    const response = await apiFetch(`${API_URL}/content/${contentId}/versions`)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch version history')
  }

  return response.json()
}

export async function getContentVersion(
  contentId: string,
  versionId: string
): Promise<ContentVersion> {
    const response = await apiFetch(`${API_URL}/content/${contentId}/versions/${versionId}`)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch version')
  }

  return response.json()
}

export async function compareVersions(
  contentId: string,
  oldVersionId: string,
  newVersionId: string
): Promise<VersionComparison> {
    const response = await apiFetch(`${API_URL}/content/${contentId}/versions/compare?old=${oldVersionId}&new=${newVersionId}`)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to compare versions')
  }

  return response.json()
}

export async function restoreContentVersion(
  contentId: string,
  versionId: string
): Promise<Content> {
    const response = await apiFetch(`${API_URL}/content/${contentId}/versions/${versionId}/restore`, { method: 'POST' })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to restore version')
  }

  return response.json()
}

// ============ End Version History API ============

// ============ Audit Logs API ============

export type AuditAction =
  | 'create'
  | 'update'
  | 'delete'
  | 'restore'
  | 'publish'
  | 'schedule'
  | 'approve'
  | 'reject'
  | 'login'
  | 'logout'
  | 'invite'
  | 'export'
  | 'import'

export type AuditResource =
  | 'content'
  | 'project'
  | 'asset'
  | 'distribution'
  | 'schedule'
  | 'organization'
  | 'user'
  | 'rss_feed'
  | 'automation_rule'

export interface AuditLogEntry {
  id: string
  actor_id: string
  actor_email: string
  actor_name: string
  action: AuditAction
  resource_type: AuditResource
  resource_id: string
  resource_name: string
  details: string
  ip_address: string
  user_agent: string
  metadata?: Record<string, unknown>
  created_at: string
}

export interface AuditLogsResponse {
  logs: AuditLogEntry[]
  total: number
  page: number
  per_page: number
}

export interface AuditLogsFilters {
  start_date?: string
  end_date?: string
  action?: AuditAction
  resource_type?: AuditResource
  actor_search?: string
  page?: number
  per_page?: number
}

export interface AuditLogStats {
  total_actions_today: number
  total_actions_week: number
  top_actors: Array<{ name: string; email: string; count: number }>
  action_distribution: Array<{ action: string; count: number }>
  resource_distribution: Array<{ resource: string; count: number }>
}

export async function getAuditLogs(
  filters?: AuditLogsFilters
): Promise<AuditLogsResponse> {
  const params = new URLSearchParams()
  if (filters?.start_date) params.append('start_date', filters.start_date)
  if (filters?.end_date) params.append('end_date', filters.end_date)
  if (filters?.action) params.append('action', filters.action)
  if (filters?.resource_type) params.append('resource_type', filters.resource_type)
  if (filters?.actor_search) params.append('actor_search', filters.actor_search)
  if (filters?.page) params.append('page', filters.page.toString())
  if (filters?.per_page) params.append('per_page', filters.per_page.toString())

  const url = `${API_URL}/audit-logs${params.toString() ? `?${params.toString()}` : ''}`
  const response = await apiFetch(url)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch audit logs')
  }

  return response.json()
}

export async function getAuditLogStats(): Promise<AuditLogStats> {
    const response = await apiFetch(`${API_URL}/audit-logs/stats`)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch audit log stats')
  }

  return response.json()
}

export async function getAuditLogById(logId: string): Promise<AuditLogEntry> {
  const response = await apiFetch(`${API_URL}/audit-logs/${logId}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch audit log')
  }
  return response.json()
}

export async function exportAuditLogsCSV(
  filters?: AuditLogsFilters
): Promise<Blob> {
    const params = new URLSearchParams()
  if (filters?.start_date) params.append('start_date', filters.start_date)
  if (filters?.end_date) params.append('end_date', filters.end_date)
  if (filters?.action) params.append('action', filters.action)
  if (filters?.resource_type) params.append('resource_type', filters.resource_type)

  const url = `${API_URL}/audit-logs/export${params.toString() ? `?${params.toString()}` : ''}`
  const response = await apiFetch(url)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to export audit logs')
  }

  return response.blob()
}

// ============ End Audit Logs API ============

// ============ Quality Scoring API ============

/** Backend response: QualityScoreResponse (flat score fields) */
export interface QualityScoreResponse {
  id?: string | null
  content_id?: string | null
  overall_score: number
  readability: number
  seo: number
  engagement: number
  grammar: number
  brand: number
  suggestions: string[]
  created_at?: string | null
}

export interface QualityHistoryResponse {
  content_id: string
  history: QualityScoreResponse[]
}

export interface QualitySuggestionsResponse {
  content_id: string
  suggestions: string[]
}

export interface QualityBatchItem {
  content_id: string
  text: string
  brand_voice?: Record<string, unknown>
}

/**
 * Analyze content quality by submitting raw text.
 */
export async function analyzeQualityText(
  text: string,
  brandVoice?: Record<string, unknown>
): Promise<QualityScoreResponse> {
  const response = await apiFetch(`${API_URL}/quality-scoring/analyze`, {
    method: 'POST',
    body: JSON.stringify({ text, brand_voice: brandVoice }),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to analyze content quality')
  }
  return response.json()
}

/**
 * Get quality score for existing content by content ID.
 */
export async function getQualityScore(
  contentId: string
): Promise<QualityScoreResponse> {
  const response = await apiFetch(`${API_URL}/quality-scoring/${contentId}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch quality score')
  }
  return response.json()
}

/**
 * Analyze quality for existing content by content ID (fetches text from DB, then analyzes).
 */
export async function analyzeContentQuality(
  contentId: string
): Promise<QualityScoreResponse> {
  const response = await apiFetch(`${API_URL}/quality-scoring/${contentId}/analyze`, { method: 'POST' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to analyze content quality')
  }
  return response.json()
}

/**
 * Get quality score history for a content item.
 */
export async function getQualityScoreHistory(
  contentId: string,
  days: number = 30
): Promise<QualityHistoryResponse> {
  const response = await apiFetch(`${API_URL}/quality-scoring/${contentId}/history?days=${days}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch quality history')
  }
  return response.json()
}

/**
 * Batch analyze multiple content items.
 */
export async function batchAnalyzeQuality(
  items: QualityBatchItem[]
): Promise<QualityScoreResponse[]> {
  const response = await apiFetch(`${API_URL}/quality-scoring/batch`, {
    method: 'POST',
    body: JSON.stringify({ items }),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to start batch analysis')
  }
  return response.json()
}

/**
 * Get improvement suggestions for a content item.
 */
export async function getQualitySuggestions(
  contentId: string
): Promise<QualitySuggestionsResponse> {
  const response = await apiFetch(`${API_URL}/quality-scoring/suggestions/${contentId}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch quality suggestions')
  }
  return response.json()
}

/**
 * Get quality score for content by the /content/{id} route (alias).
 */
export async function getContentQualityScore(
  contentId: string
): Promise<QualityScoreResponse> {
  const response = await apiFetch(`${API_URL}/quality-scoring/content/${contentId}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch quality score')
  }
  return response.json()
}

// ============ End Quality Scoring API ============

// ============ Sentiment Analysis API ============

/** Backend response: EmotionScores */
export interface EmotionScores {
  joy: number
  anger: number
  sadness: number
  fear: number
  surprise: number
  disgust: number
}

/** Backend response: AspectSentiment */
export interface AspectSentiment {
  section: string
  sentiment: string
  score: number
}

/** Backend response: SentimentResponse */
export interface SentimentResponse {
  id?: string | null
  content_id?: string | null
  sentiment: string
  score: number
  emotions: EmotionScores
  aspects: AspectSentiment[]
  tone: string
  created_at?: string | null
}

export interface SentimentTrendsResponse {
  content_id: string
  trends: SentimentResponse[]
}

export interface SentimentDistributionResponse {
  total_analyses: number
  distribution: Record<string, number>
  percentages: Record<string, number>
}

export interface SentimentBatchItem {
  content_id: string
  text: string
}

/**
 * Analyze sentiment of raw text.
 */
export async function analyzeSentimentText(
  text: string
): Promise<SentimentResponse> {
  const response = await apiFetch(`${API_URL}/sentiment/analyze`, {
    method: 'POST',
    body: JSON.stringify({ text }),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to analyze sentiment')
  }
  return response.json()
}

/**
 * Analyze sentiment for existing content by content ID.
 */
export async function analyzeSentiment(
  contentId: string
): Promise<SentimentResponse> {
  const response = await apiFetch(`${API_URL}/sentiment/${contentId}/analyze`, { method: 'POST' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to analyze sentiment')
  }
  return response.json()
}

/**
 * Get sentiment analysis for existing content by content ID.
 */
export async function getSentiment(
  contentId: string
): Promise<SentimentResponse> {
  const response = await apiFetch(`${API_URL}/sentiment/${contentId}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch sentiment')
  }
  return response.json()
}

/**
 * Get sentiment for content via the /content/{id} route (alias).
 */
export async function getContentSentiment(
  contentId: string
): Promise<SentimentResponse> {
  const response = await apiFetch(`${API_URL}/sentiment/content/${contentId}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch sentiment')
  }
  return response.json()
}

/**
 * Get sentiment trends for a content item.
 */
export async function getSentimentTrends(
  contentId: string,
  days: number = 30
): Promise<SentimentTrendsResponse> {
  const response = await apiFetch(`${API_URL}/sentiment/${contentId}/trend?days=${days}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch sentiment trends')
  }
  return response.json()
}

/**
 * Batch analyze sentiment for multiple content items.
 */
export async function batchAnalyzeSentiment(
  items: SentimentBatchItem[]
): Promise<SentimentResponse[]> {
  const response = await apiFetch(`${API_URL}/sentiment/batch`, {
    method: 'POST',
    body: JSON.stringify({ items }),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to batch analyze sentiment')
  }
  return response.json()
}

/**
 * Get sentiment distribution across all user content.
 */
export async function getSentimentDistribution(): Promise<SentimentDistributionResponse> {
  const response = await apiFetch(`${API_URL}/sentiment/distribution`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch sentiment distribution')
  }
  return response.json()
}

// ============ End Sentiment Analysis API ============

// ============ Custom Dashboards API ============

export interface DashboardWidget {
  id: string
  dashboard_id: string
  widget_type: string
  title: string
  data_source: string
  refresh_interval: number
  size: { w: number; h: number }
  position: number
  config: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface Dashboard {
  id: string
  user_id: string
  name: string
  description?: string
  layout_config: Record<string, unknown>
  is_default: boolean
  widgets: DashboardWidget[]
  created_at: string
  updated_at: string
}

export interface WidgetLiveData {
  widget_id: string
  widget_type: string
  title: string
  data_source: string
  refresh_interval: number
  data: Record<string, unknown>
}

export async function listDashboards(): Promise<Dashboard[]> {
    const response = await apiFetch(`${API_URL}/dashboards`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch dashboards')
  }
  return response.json()
}

export async function createDashboard(data: { name: string; description?: string; is_default?: boolean }): Promise<Dashboard> {
    const response = await apiFetch(`${API_URL}/dashboards`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create dashboard')
  }
  return response.json()
}

export async function getDashboard(dashboardId: string): Promise<Dashboard> {
    const response = await apiFetch(`${API_URL}/dashboards/${dashboardId}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch dashboard')
  }
  return response.json()
}

export async function updateDashboard(dashboardId: string, data: { name?: string; description?: string; layout_config?: Record<string, unknown>; is_default?: boolean }): Promise<Dashboard> {
    const response = await apiFetch(`${API_URL}/dashboards/${dashboardId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update dashboard')
  }
  return response.json()
}

export async function deleteDashboard(dashboardId: string): Promise<void> {
    const response = await apiFetch(`${API_URL}/dashboards/${dashboardId}`, { method: 'DELETE' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to delete dashboard')
  }
}

export async function addWidget(dashboardId: string, data: { widget_type: string; title: string; data_source: string; refresh_interval: number; size?: Record<string, number>; position?: number; config?: Record<string, unknown> }): Promise<DashboardWidget> {
    const response = await apiFetch(`${API_URL}/dashboards/${dashboardId}/widgets`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to add widget')
  }
  return response.json()
}

export async function updateWidget(dashboardId: string, widgetId: string, data: Record<string, unknown>): Promise<DashboardWidget> {
    const response = await apiFetch(`${API_URL}/dashboards/${dashboardId}/widgets/${widgetId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update widget')
  }
  return response.json()
}

export async function deleteWidget(dashboardId: string, widgetId: string): Promise<void> {
    const response = await apiFetch(`${API_URL}/dashboards/${dashboardId}/widgets/${widgetId}`, { method: 'DELETE' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to delete widget')
  }
}

export async function getDashboardData(dashboardId: string): Promise<{ dashboard_id: string; widgets: WidgetLiveData[]; fetched_at: string }> {
    const response = await apiFetch(`${API_URL}/dashboards/${dashboardId}/data`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch dashboard data')
  }
  return response.json()
}

// ============ End Custom Dashboards API ============

// ============ Report Scheduling API ============

export interface ScheduledReport {
  id: string
  user_id: string
  name: string
  description?: string
  report_type: string
  schedule: string
  format: string
  recipients: string[]
  filters: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface ReportRun {
  id: string
  report_id: string
  status: string
  format: string
  storage_path?: string
  file_name?: string
  generated_at: string
  error_message?: string
  download_url?: string
}

export async function listReports(): Promise<ScheduledReport[]> {
    const response = await apiFetch(`${API_URL}/reports`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch reports')
  }
  return response.json()
}

export async function createReport(data: { name: string; report_type: string; schedule: string; format?: string; description?: string; recipients?: string[]; filters?: Record<string, unknown> }): Promise<ScheduledReport> {
    const response = await apiFetch(`${API_URL}/reports`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create report')
  }
  return response.json()
}

export async function getReport(reportId: string): Promise<ScheduledReport> {
    const response = await apiFetch(`${API_URL}/reports/${reportId}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch report')
  }
  return response.json()
}

export async function updateReport(reportId: string, data: Record<string, unknown>): Promise<ScheduledReport> {
    const response = await apiFetch(`${API_URL}/reports/${reportId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update report')
  }
  return response.json()
}

export async function deleteReport(reportId: string): Promise<void> {
    const response = await apiFetch(`${API_URL}/reports/${reportId}`, { method: 'DELETE' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to delete report')
  }
}

export async function generateReport(reportId: string): Promise<ReportRun> {
    const response = await apiFetch(`${API_URL}/reports/${reportId}/generate`, { method: 'POST' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to generate report')
  }
  return response.json()
}

export async function getReportHistory(reportId: string): Promise<ReportRun[]> {
    const response = await apiFetch(`${API_URL}/reports/${reportId}/history`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch report history')
  }
  return response.json()
}

export async function downloadReport(reportId: string, runId: string): Promise<ReportRun> {
    const response = await apiFetch(`${API_URL}/reports/${reportId}/download/${runId}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to download report')
  }
  return response.json()
}

// ============ End Report Scheduling API ============

// ============ P4: Suggestions API ============

export type SuggestionType = 'topic' | 'timing' | 'improvement'
export type SuggestionPriority = 'high' | 'medium' | 'low'

export interface Suggestion {
  id: string
  content_id: string
  type: SuggestionType
  title: string
  description: string
  priority: SuggestionPriority
  relevance_score: number
  content_title?: string
  created_at: string
  updated_at: string
}

export async function getSuggestions(type?: SuggestionType): Promise<Suggestion[]> {
  const params = new URLSearchParams()
  if (type) params.append('type', type)
  const url = `${API_URL}/suggestions${params.toString() ? `?${params.toString()}` : ''}`
  const response = await apiFetch(url)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch suggestions')
  }
  return response.json()
}

export async function acceptSuggestion(suggestionId: string): Promise<{ message: string; suggestion: Suggestion }> {
    const response = await apiFetch(`${API_URL}/suggestions/${suggestionId}/accept`, { method: 'POST' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to accept suggestion')
  }
  return response.json()
}

export async function dismissSuggestion(suggestionId: string): Promise<{ message: string }> {
    const response = await apiFetch(`${API_URL}/suggestions/${suggestionId}/dismiss`, { method: 'POST' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to dismiss suggestion')
  }
  return response.json()
}

// ============ End P4: Suggestions API ============

// ============ P4: Categorization API ============

export interface CategoryTag {
  name: string
  confidence: number
  is_auto: boolean
  order: number
}

export interface CategorizationResult {
  content_id: string
  content_title: string
  categories: CategoryTag[]
  categorized_at: string
}

export async function getCategorization(): Promise<CategorizationResult[]> {
    const response = await apiFetch(`${API_URL}/categorization`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch categorizations')
  }
  return response.json()
}

export async function updateCategories(
  contentId: string,
  data: { categories: string[] }
): Promise<CategorizationResult> {
    const response = await apiFetch(`${API_URL}/categorization/${contentId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update categories')
  }
  return response.json()
}

// ============ End P4: Categorization API ============

// ============ P4: Performance API ============

export interface PerformanceOverview {
  total_views: number
  engagement_rate: number
  total_shares: number
  conversion_rate: number
}

export interface FunnelStage {
  stage: string
  count: number
  percentage?: number
}

export interface CohortData {
  cohort: string
  engagement: number
  retention: number
}

export interface AttributionData {
  source: string
  value: number
}

export interface TrendDataPoint {
  date: string
  views: number
  engagement: number
  conversions?: number
}

export async function getPerformanceOverview(): Promise<PerformanceOverview> {
    const response = await apiFetch(`${API_URL}/performance/overview`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch performance overview')
  }
  return response.json()
}

export async function getPerformanceFunnel(): Promise<FunnelStage[]> {
    const response = await apiFetch(`${API_URL}/performance/funnel`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch performance funnel')
  }
  return response.json()
}

export async function getPerformanceCohorts(): Promise<CohortData[]> {
    const response = await apiFetch(`${API_URL}/performance/cohort`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch performance cohorts')
  }
  return response.json()
}

export async function getPerformanceAttribution(): Promise<AttributionData[]> {
    const response = await apiFetch(`${API_URL}/performance/attribution`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch performance attribution')
  }
  return response.json()
}

export async function getPerformanceTrend(days: number = 30): Promise<TrendDataPoint[]> {
    const response = await apiFetch(`${API_URL}/performance/trends?days=${days}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch performance trend')
  }
  return response.json()
}

// ============ End P4: Performance API ============

// ============ P4: Data Retention API ============

export interface RetentionPolicy {
  id: string
  user_id: string
  content_type: string
  archive_after_days: number
  delete_after_days: number | null
  description: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface RetentionPolicyListResponse {
  items: RetentionPolicy[]
  total: number
  page: number
  page_size: number
}

export interface ComplianceIssue {
  severity: 'high' | 'medium' | 'low'
  message: string
  recommendation?: string
}

export interface ComplianceReport {
  report_generated_at: string
  gdpr_article: string
  compliance_score: number
  total_content: number
  content_by_status: Record<string, number>
  content_by_type: Record<string, number>
  active_policies: number
  inactive_policies: number
  content_covered_by_policy: number
  content_without_policy: string[]
  audit_trail_last_30_days: Record<string, number>
  recommendations: string[]
}

export interface RetentionAuditEntry {
  id: string
  user_id: string
  action: string
  resource_type: string
  resource_id: string
  details: string | null
  created_at: string
}

export async function getRetentionPolicies(): Promise<RetentionPolicy[]> {
    const response = await apiFetch(`${API_URL}/retention/policies`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch retention policies')
  }
  const result: RetentionPolicyListResponse = await response.json()
  return result.items
}

export async function createRetentionPolicy(data: {
  content_type: string
  archive_after_days: number
  delete_after_days?: number
  description?: string
  is_active?: boolean
}): Promise<RetentionPolicy> {
    const response = await apiFetch(`${API_URL}/retention/policies`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create retention policy')
  }
  return response.json()
}

export async function updateRetentionPolicy(
  policyId: string,
  data: Partial<Omit<RetentionPolicy, 'id' | 'created_at' | 'updated_at' | 'user_id'>>
): Promise<RetentionPolicy> {
    const response = await apiFetch(`${API_URL}/retention/policies/${policyId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update retention policy')
  }
  return response.json()
}

export async function deleteRetentionPolicy(policyId: string): Promise<void> {
    const response = await apiFetch(`${API_URL}/retention/policies/${policyId}`, { method: 'DELETE' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to delete retention policy')
  }
}

export async function getRetentionCompliance(): Promise<ComplianceReport> {
    const response = await apiFetch(`${API_URL}/retention/compliance`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch compliance report')
  }
  return response.json()
}

export async function getRetentionAuditTrail(): Promise<RetentionAuditEntry[]> {
    const response = await apiFetch(`${API_URL}/retention/audit`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch audit trail')
  }
  const result = await response.json()
  return result.items || result
}

// ============ End P4: Data Retention API ============

// ============ P4: SSO / OIDC API ============

export interface AvailableSSOProvider {
  name: string
  display_name: string
  is_active: boolean
}

export interface SSOProvider {
  id: string
  name: string
  display_name: string
  client_id: string
  discovery_url: string | null
  authorization_url: string | null
  token_url: string | null
  userinfo_url: string | null
  scopes: string
  domain: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface SSOInitiateResponse {
  authorization_url: string
  state: string
}

export interface SSOCallbackResponse {
  action: 'login' | 'register' | 'linked'
  user_id: string
  email: string
  full_name: string | null
  is_new_user: boolean
}

export interface SSOIdentity {
  id: string
  provider: string
  email: string | null
  full_name: string | null
  created_at: string
}

export async function getAvailableSSOProviders(): Promise<AvailableSSOProvider[]> {
  const response = await apiFetch(`${API_URL}/sso/available`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch SSO providers')
  }
  return response.json()
}

export async function getSSOProviders(): Promise<SSOProvider[]> {
    const response = await apiFetch(`${API_URL}/sso/providers`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch SSO providers')
  }
  return response.json()
}

export async function getSSOProvider(providerId: string): Promise<SSOProvider> {
    const response = await apiFetch(`${API_URL}/sso/providers/${providerId}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch SSO provider')
  }
  return response.json()
}

export async function createSSOProvider(data: {
  name: string
  display_name: string
  client_id: string
  client_secret: string
  discovery_url?: string
  authorization_url?: string
  token_url?: string
  userinfo_url?: string
  scopes?: string
  domain?: string
  is_active?: boolean
}): Promise<SSOProvider> {
    const response = await apiFetch(`${API_URL}/sso/providers`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create SSO provider')
  }
  return response.json()
}

export async function updateSSOProvider(
  providerId: string,
  data: Partial<Omit<SSOProvider, 'id' | 'created_at' | 'updated_at'>>
): Promise<SSOProvider> {
    const response = await apiFetch(`${API_URL}/sso/providers/${providerId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update SSO provider')
  }
  return response.json()
}

export async function deleteSSOProvider(providerId: string): Promise<void> {
    const response = await apiFetch(`${API_URL}/sso/providers/${providerId}`, { method: 'DELETE' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to delete SSO provider')
  }
}

export async function initiateSSOLogin(data: {
  provider: string
  redirect_uri: string
  link_user?: boolean
}): Promise<SSOInitiateResponse> {
      const response = await apiFetch(`${API_URL}/sso/login/public`, { method: 'POST', body: JSON.stringify(data) })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to initiate SSO login')
  }
  return response.json()
}

export async function handleSSOCallback(data: {
  state: string
  code: string
}): Promise<SSOCallbackResponse> {
    const response = await apiFetch(`${API_URL}/sso/callback`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'SSO callback failed')
  }
  return response.json()
}

export async function getUserSSOIdentities(): Promise<SSOIdentity[]> {
    const response = await apiFetch(`${API_URL}/sso/identities`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch SSO identities')
  }
  return response.json()
}

export async function unlinkSSOIdentity(identityId: string): Promise<void> {
    const response = await apiFetch(`${API_URL}/sso/identities/${identityId}`, { method: 'DELETE' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to unlink SSO identity')
  }
}

// ============ End P4: SSO / OIDC API ============

// ============ P4: Comments API ============

export interface ContentComment {
  id: string
  user_id: string
  content_id: string
  text: string
  position_start: number | null
  position_end: number | null
  parent_id: string | null
  is_resolved: boolean
  resolved_at: string | null
  resolved_by: string | null
  created_at: string
  updated_at: string
  mentions: string[]
}

export interface CommentListResponse {
  items: ContentComment[]
  total: number
  page: number
  page_size: number
}

export interface CommentThread {
  parent: ContentComment
  replies: ContentComment[]
  reply_count: number
}

export interface CommentReaction {
  emoji: string
  user_ids: string[]
  count: number
}

export interface MentionUser {
  id: string
  full_name: string | null
  email: string | null
}

export async function getComments(
  contentId: string,
  options?: {
    parentId?: string
    isResolved?: boolean
    page?: number
    pageSize?: number
  }
): Promise<CommentListResponse> {
  const params = new URLSearchParams()
  if (options?.parentId) params.set('parent_id', options.parentId)
  if (options?.isResolved !== undefined) params.set('is_resolved', String(options.isResolved))
  if (options?.page) params.set('page', String(options.page))
  if (options?.pageSize) params.set('page_size', String(options.pageSize))
  const qs = params.toString() ? `?${params.toString()}` : ''
  const response = await apiFetch(`${API_URL}/content/${contentId}/comments${qs}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch comments')
  }
  return response.json()
}

export async function createComment(
  contentId: string,
  data: {
    text: string
    position_start?: number
    position_end?: number
    parent_id?: string
  }
): Promise<ContentComment> {
    const response = await apiFetch(`${API_URL}/content/${contentId}/comments`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create comment')
  }
  return response.json()
}

export async function updateComment(
  commentId: string,
  data: { text: string }
): Promise<ContentComment> {
    const response = await apiFetch(`${API_URL}/content/comments/${commentId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update comment')
  }
  return response.json()
}

export async function deleteComment(commentId: string): Promise<void> {
    const response = await apiFetch(`${API_URL}/content/comments/${commentId}`, { method: 'DELETE' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to delete comment')
  }
}

export async function getCommentThread(commentId: string): Promise<CommentThread> {
    const response = await apiFetch(`${API_URL}/content/comments/${commentId}/thread`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch comment thread')
  }
  return response.json()
}

export async function resolveComment(commentId: string): Promise<ContentComment> {
    const response = await apiFetch(`${API_URL}/content/comments/${commentId}/resolve`, { method: 'PUT' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to resolve comment')
  }
  return response.json()
}

export async function unresolveComment(commentId: string): Promise<ContentComment> {
    const response = await apiFetch(`${API_URL}/content/comments/${commentId}/unresolve`, { method: 'PUT' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to unresolve comment')
  }
  return response.json()
}

export async function lookupMentions(query: string): Promise<MentionUser[]> {
    const response = await apiFetch(`${API_URL}/comments/mentions/lookup?q=${encodeURIComponent(query)}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to lookup mentions')
  }
  return response.json()
}

export async function addCommentReaction(
  commentId: string,
  emoji: string
): Promise<Record<string, unknown>> {
    const response = await apiFetch(`${API_URL}/content/comments/${commentId}/reactions`, { method: 'POST', body: JSON.stringify({ emoji  }),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to add reaction')
  }
  return response.json()
}

export async function removeCommentReaction(
  commentId: string,
  emoji: string
): Promise<void> {
    const response = await apiFetch(`${API_URL}/content/comments/${commentId}/reactions?emoji=${encodeURIComponent(emoji)}`, { method: 'DELETE' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to remove reaction')
  }
}

export async function getCommentReactions(commentId: string): Promise<CommentReaction[]> {
    const response = await apiFetch(`${API_URL}/content/comments/${commentId}/reactions`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch reactions')
  }
  return response.json()
}

// ============ End P4: Comments API ============

// ============ P4: Plugin System API ============

export interface PluginRegistryItem {
  id: string
  name: string
  slug: string
  description: string
  version: string
  category: string
  author_id: string
  icon_url?: string
  homepage_url?: string
  repository_url?: string
  permissions: string[]
  hooks: string[]
  config_schema: Record<string, unknown>
  default_config: Record<string, unknown>
  is_official: boolean
  status: string
  downloads: number
  rating_avg: number
  rating_count: number
  created_at: string
  updated_at: string
}

export interface PluginListResponse {
  plugins: PluginRegistryItem[]
  total: number
}

export interface InstalledPlugin {
  id: string
  plugin_id: string
  organization_id: string
  installed_by: string
  config: Record<string, unknown>
  is_enabled: boolean
  installed_at: string
  updated_at: string
  plugin?: PluginRegistryItem
}

export interface InstalledPluginListResponse {
  plugins: InstalledPlugin[]
  total: number
}

export interface PluginMeta {
  hooks: Array<{ value: string; label: string }>
  permissions: Array<{ value: string; label: string }>
}

export async function listPlugins(options?: {
  category?: string
  search?: string
  is_official?: boolean
  limit?: number
  offset?: number
}): Promise<PluginListResponse> {
  const params = new URLSearchParams()
  if (options?.category) params.append('category', options.category)
  if (options?.search) params.append('search', options.search)
  if (options?.is_official !== undefined) params.append('is_official', String(options.is_official))
  if (options?.limit) params.append('limit', options.limit.toString())
  if (options?.offset) params.append('offset', options.offset.toString())
  const url = `${API_URL}/plugins${params.toString() ? `?${params.toString()}` : ''}`
  const response = await apiFetch(url)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch plugins')
  }
  return response.json()
}

export async function getPlugin(pluginId: string): Promise<PluginRegistryItem> {
    const response = await apiFetch(`${API_URL}/plugins/${pluginId}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch plugin')
  }
  return response.json()
}

export async function getPluginMeta(): Promise<PluginMeta> {
    const response = await apiFetch(`${API_URL}/plugins/meta`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch plugin metadata')
  }
  return response.json()
}

export async function listInstalledPlugins(
  organizationId: string,
  isEnabled?: boolean
): Promise<InstalledPluginListResponse> {
    const params = new URLSearchParams()
  if (isEnabled !== undefined) params.append('is_enabled', String(isEnabled))
  const url = `${API_URL}/organizations/${organizationId}/plugins${params.toString() ? `?${params.toString()}` : ''}`
  const response = await apiFetch(url)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch installed plugins')
  }
  return response.json()
}

export async function installPlugin(
  pluginId: string,
  organizationId: string,
  customConfig?: Record<string, unknown>
): Promise<InstalledPlugin> {
  const response = await apiFetch(`${API_URL}/organizations/${organizationId}/plugins/install`, {
    method: 'POST',
    body: JSON.stringify({
      plugin_id: pluginId,
      organization_id: organizationId,
      custom_config: customConfig || {},
    }),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to install plugin')
  }
  return response.json()
}

export async function uninstallPlugin(
  installId: string,
  organizationId: string
): Promise<void> {
    const response = await apiFetch(`${API_URL}/organizations/${organizationId}/plugins/${installId}`, { method: 'DELETE' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to uninstall plugin')
  }
}

export async function getPluginConfig(
  installId: string,
  organizationId: string
): Promise<{ config: Record<string, unknown> }> {
    const response = await apiFetch(`${API_URL}/organizations/${organizationId}/plugins/${installId}/config`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch plugin config')
  }
  return response.json()
}

export async function updatePluginConfig(
  installId: string,
  organizationId: string,
  config: Record<string, unknown>
): Promise<InstalledPlugin> {
    const response = await apiFetch(`${API_URL}/organizations/${organizationId}/plugins/${installId}/config`, { method: 'PUT', body: JSON.stringify({ config  }),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update plugin config')
  }
  return response.json()
}

export async function togglePlugin(
  installId: string,
  organizationId: string,
  isEnabled: boolean
): Promise<InstalledPlugin> {
    const response = await apiFetch(`${API_URL}/organizations/${organizationId}/plugins/${installId}/toggle`, { method: 'PATCH', body: JSON.stringify({ is_enabled: isEnabled  }),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to toggle plugin')
  }
  return response.json()
}

export async function validatePluginPermissions(data: {
  name: string
  permissions: string[]
  hooks: string[]
}): Promise<{ valid: boolean; errors: string[] }> {
    const response = await apiFetch(`${API_URL}/plugins/validate-permissions`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to validate permissions')
  }
  return response.json()
}

// ============ End P4: Plugin System API ============

// ============ SAML SSO API ============

export interface SAMLProvider {
  id: string
  name: string
  display_name?: string
  entity_id: string
  sso_url: string
  slo_url?: string
  x509_cert?: string
  certificate?: string
  metadata_url?: string
  attribute_mapping: Record<string, string>
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface SAMLProviderCreate {
  name: string
  display_name?: string
  entity_id: string
  sso_url: string
  slo_url?: string
  x509_cert?: string
  certificate?: string
  metadata_url?: string
  is_active?: boolean
  attribute_mapping?: Record<string, string>
}

export interface SAMLProviderUpdate {
  name?: string
  entity_id?: string
  sso_url?: string
  slo_url?: string
  metadata_url?: string
  certificate?: string
  attribute_mapping?: Record<string, string>
  is_active?: boolean
}

export interface SAMLMetadata {
  entity_id: string
  sso_url: string
  slo_url?: string
  certificate: string
  valid_until?: string
}

export interface SAMLLoginResponse {
  login_url: string
  request_id: string
  provider_id: string
}

export interface SAMLCallbackResult {
  user_id: string
  email: string
  full_name?: string
  is_new_user: boolean
  session_token: string
}

export interface SAMLSLOResponse {
  logout_url: string
  request_id: string
}

export interface SAMLIdentity {
  id: string
  provider_id: string
  provider_name: string
  name_id: string
  name_id_format: string
  attributes: Record<string, string[]>
  created_at: string
}

export async function createSAMLProvider(data: SAMLProviderCreate): Promise<SAMLProvider> {
    const response = await apiFetch(`${API_URL}/saml/providers`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create SAML provider')
  }
  return response.json()
}

export async function listSAMLProviders(): Promise<SAMLProvider[]> {
    const response = await apiFetch(`${API_URL}/saml/providers`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to list SAML providers')
  }
  return response.json()
}

export async function getSAMLProvider(providerId: string): Promise<SAMLProvider> {
    const response = await apiFetch(`${API_URL}/saml/providers/${providerId}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to get SAML provider')
  }
  return response.json()
}

export async function updateSAMLProvider(providerId: string, data: SAMLProviderUpdate): Promise<SAMLProvider> {
    const response = await apiFetch(`${API_URL}/saml/providers/${providerId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update SAML provider')
  }
  return response.json()
}

export async function deleteSAMLProvider(providerId: string): Promise<void> {
    const response = await apiFetch(`${API_URL}/saml/providers/${providerId}`, { method: 'DELETE' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to delete SAML provider')
  }
}

export async function fetchSAMLMetadata(data: { metadata_url: string } | string): Promise<SAMLMetadata> {
  const metadataUrl = typeof data === 'string' ? data : data.metadata_url
    const response = await apiFetch(`${API_URL}/saml/providers/metadata/fetch`, { method: 'POST', body: JSON.stringify({ metadata_url: metadataUrl  }),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch SAML metadata')
  }
  return response.json()
}

export async function updateSAMLAttributeMapping(
  providerId: string,
  attributeMapping: Record<string, string>
): Promise<SAMLProvider> {
    const response = await apiFetch(`${API_URL}/saml/providers/${providerId}/attribute-mapping`, { method: 'PUT', body: JSON.stringify({ attribute_mapping: attributeMapping  }),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update attribute mapping')
  }
  return response.json()
}

export async function initiateSAMLLogin(data: { provider_id: string; relay_state?: string; redirect_uri?: string } | string): Promise<SAMLLoginResponse> {
  const providerId = typeof data === 'string' ? data : data.provider_id
  const body = typeof data === 'string' ? JSON.stringify({}) : JSON.stringify(data)
  const endpoint = typeof data === 'string' ? `${API_URL}/saml/login/${providerId}` : `${API_URL}/saml/login/public`
  const response = await apiFetch(endpoint, { method: 'POST', body, headers: { 'Content-Type': 'application/json' } })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to initiate SAML login')
  }
  return response.json()
}

export async function initiateSAMLLogout(providerId: string): Promise<SAMLSLOResponse> {
    const response = await apiFetch(`${API_URL}/saml/logout/${providerId}`, { method: 'POST' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to initiate SAML logout')
  }
  return response.json()
}

export async function listSAMLIdentities(): Promise<SAMLIdentity[]> {
    const response = await apiFetch(`${API_URL}/saml/identities`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to list SAML identities')
  }
  return response.json()
}

export async function unlinkSAMLIdentity(identityId: string): Promise<void> {
    const response = await apiFetch(`${API_URL}/saml/identities/${identityId}`, { method: 'DELETE' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to unlink SAML identity')
  }
}

export async function listAvailableSAMLProviders(): Promise<Array<{ id: string; name: string }>> {
  const response = await apiFetch(`${API_URL}/saml/providers/available`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to list available SAML providers')
  }
  return response.json()
}

// ============ End SAML SSO API ============

// ============ Template Marketplace API ============

export interface MarketplaceTemplate {
  id: string
  name: string
  description: string
  content: string
  category: string
  tags: string[]
  platforms: string[]
  version: string
  is_published: boolean
  is_featured: boolean
  author_id: string
  author?: {
    id: string
    email: string
    full_name?: string
    avatar_url?: string
    template_count: number
    total_installs: number
    avg_rating: number
  }
  install_count: number
  avg_rating: number
  rating_count: number
  review_count: number
  downloads: number
  created_at: string
  updated_at: string
  published_at?: string
}

export interface MarketplaceCategory {
  id: string
  name: string
  slug: string
  icon: string
  description?: string
  template_count: number
}

export interface MarketplaceTag {
  name: string
  count: number
}

export interface MarketplaceTemplateListResponse {
  templates: MarketplaceTemplate[]
  total: number
}

export interface MarketplaceRating {
  id: string
  template_id: string
  user_id: string
  user?: {
    id: string
    full_name?: string
    email: string
  }
  rating: number
  review?: string
  created_at: string
}

export interface MarketplaceRatingSubmit {
  rating: number
  review?: string
}

export interface MarketplaceTemplateCreate {
  name: string
  description: string
  content: string
  category: string
  tags?: string[]
  platforms?: string[]
  version?: string
  is_published?: boolean
}

export interface MarketplaceTemplateUpdate {
  name?: string
  description?: string
  content?: string
  category?: string
  tags?: string[]
  platforms?: string[]
  version?: string
}

export interface MarketplaceInstallResult {
  template_id: string
  already_installed: boolean
  install_count: number
}

export interface MarketplaceRatingsResponse {
  ratings: MarketplaceRating[]
  total: number
}

export interface MarketplaceVersion {
  version: string
  changelog?: string
  published_at: string
}

export async function listMarketplaceTemplates(options?: {
  category?: string
  search?: string
  tags?: string[]
  sort?: 'newest' | 'popular' | 'rating'
  limit?: number
  offset?: number
}): Promise<MarketplaceTemplateListResponse> {
  const params = new URLSearchParams()
  if (options?.category) params.append('category', options.category)
  if (options?.search) params.append('search', options.search)
  if (options?.tags && options.tags.length > 0) params.append('tags', options.tags.join(','))
  if (options?.sort) params.append('sort', options.sort)
  if (options?.limit) params.append('limit', options.limit.toString())
  if (options?.offset) params.append('offset', options.offset.toString())
  const url = `${API_URL}/marketplace/templates${params.toString() ? `?${params.toString()}` : ''}`
  const response = await apiFetch(url)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to list marketplace templates')
  }
  return response.json()
}

export async function getMarketplaceTemplate(templateId: string): Promise<MarketplaceTemplate> {
    const response = await apiFetch(`${API_URL}/marketplace/templates/${templateId}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to get template')
  }
  return response.json()
}

export async function createMarketplaceTemplate(data: MarketplaceTemplateCreate): Promise<MarketplaceTemplate> {
    const response = await apiFetch(`${API_URL}/marketplace/templates`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create template')
  }
  return response.json()
}

export async function updateMarketplaceTemplate(templateId: string, data: MarketplaceTemplateUpdate): Promise<MarketplaceTemplate> {
    const response = await apiFetch(`${API_URL}/marketplace/templates/${templateId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update template')
  }
  return response.json()
}

export async function deleteMarketplaceTemplate(templateId: string): Promise<void> {
    const response = await apiFetch(`${API_URL}/marketplace/templates/${templateId}`, { method: 'DELETE' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to delete template')
  }
}

export async function publishMarketplaceTemplate(templateId: string): Promise<MarketplaceTemplate> {
    const response = await apiFetch(`${API_URL}/marketplace/templates/${templateId}/publish`, { method: 'POST' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to publish template')
  }
  return response.json()
}

export async function unpublishMarketplaceTemplate(templateId: string): Promise<MarketplaceTemplate> {
    const response = await apiFetch(`${API_URL}/marketplace/templates/${templateId}/unpublish`, { method: 'POST' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to unpublish template')
  }
  return response.json()
}

export async function getMarketplaceCategories(): Promise<MarketplaceCategory[]> {
    const response = await apiFetch(`${API_URL}/marketplace/categories`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch categories')
  }
  return response.json()
}

export async function getMarketplaceTags(limit?: number): Promise<MarketplaceTag[]> {
  const params = limit ? `?limit=${limit}` : ''
  const response = await apiFetch(`${API_URL}/marketplace/tags${params}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch tags')
  }
  return response.json()
}

export async function installMarketplaceTemplate(templateId: string): Promise<MarketplaceInstallResult> {
    const response = await apiFetch(`${API_URL}/marketplace/templates/${templateId}/install`, { method: 'POST' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to install template')
  }
  return response.json()
}

export async function rateMarketplaceTemplate(templateId: string, data: MarketplaceRatingSubmit): Promise<MarketplaceRating> {
    const response = await apiFetch(`${API_URL}/marketplace/templates/${templateId}/ratings`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to rate template')
  }
  return response.json()
}

export async function getTemplateRatings(templateId: string, limit?: number, offset?: number): Promise<MarketplaceRatingsResponse> {
  const params = new URLSearchParams()
  if (limit) params.append('limit', limit.toString())
  if (offset) params.append('offset', offset.toString())
  const url = `${API_URL}/marketplace/templates/${templateId}/ratings${params.toString() ? `?${params.toString()}` : ''}`
  const response = await apiFetch(url)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch template ratings')
  }
  return response.json()
}

export async function getFeaturedTemplates(limit?: number): Promise<MarketplaceTemplate[]> {
    const params = limit ? `?limit=${limit}` : ''
  const response = await apiFetch(`${API_URL}/marketplace/featured${params}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch featured templates')
  }
  return response.json()
}

export async function getTrendingTemplates(limit?: number): Promise<MarketplaceTemplate[]> {
    const params = limit ? `?limit=${limit}` : ''
  const response = await apiFetch(`${API_URL}/marketplace/trending${params}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch trending templates')
  }
  return response.json()
}

export async function getTemplateVersions(templateId: string): Promise<MarketplaceVersion[]> {
    const response = await apiFetch(`${API_URL}/marketplace/templates/${templateId}/versions`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch template versions')
  }
  return response.json()
}

export async function getMarketplaceAuthorProfile(authorId: string): Promise<{
  id: string
  email: string
  full_name?: string
  avatar_url?: string
  template_count: number
  total_installs: number
  avg_rating: number
  templates: MarketplaceTemplate[]
}> {
    const response = await apiFetch(`${API_URL}/marketplace/authors/${authorId}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch author profile')
  }
  return response.json()
}

// ============ End Template Marketplace API ============

// ============ P4: Funnel Analytics API ============

export interface FunnelStep {
  id: string
  step_id: string
  name: string
  order: number
  description?: string
}

export interface FunnelResponse {
  id: string
  name: string
  description?: string
  steps: FunnelStep[]
  created_at: string
  updated_at: string
}

export interface FunnelAnalyticsData {
  funnel_id: string
  step_conversions: Record<string, number>
  step_conversion_rates: Record<string, number>
  total_entered: number
  total_completed: number
  conversion_rate: number
  drop_off_steps: Array<{
    step_id: string
    step_name: string
    drop_off_rate: number
    users_entered: number
    users_exited: number
    drop_off_count: number
  }>
}

export interface FunnelListResponse {
  funnels: FunnelResponse[]
}

export async function createFunnel(data: {
  name: string
  description?: string
  steps: Array<{ step_id: string; name: string; order: number; description?: string }>
}): Promise<FunnelResponse> {
    const response = await apiFetch(`${API_URL}/funnels`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error('Failed to create funnel')
  return response.json()
}

export async function getFunnel(funnelId: string): Promise<FunnelResponse> {
    const response = await apiFetch(`${API_URL}/funnels/${funnelId}`)
  if (!response.ok) throw new Error('Failed to get funnel')
  return response.json()
}

export async function listFunnels(): Promise<FunnelListResponse> {
    const response = await apiFetch(`${API_URL}/funnels`)
  if (!response.ok) throw new Error('Failed to list funnels')
  return response.json()
}

export async function trackFunnelEvent(funnelId: string, stepId: string, eventData?: Record<string, unknown>): Promise<{ success: boolean }> {
    const response = await apiFetch(`${API_URL}/funnels/${funnelId}/events`, { method: 'POST', body: JSON.stringify({ step_id: stepId, event_data: eventData  }),
  })
  if (!response.ok) throw new Error('Failed to track funnel event')
  return response.json()
}

export async function getFunnelAnalytics(funnelId: string, dateRange?: { start: string; end: string }): Promise<FunnelAnalyticsData> {
    const params = dateRange ? `?start=${dateRange.start}&end=${dateRange.end}` : ''
  const response = await apiFetch(`${API_URL}/funnels/${funnelId}/analytics${params}`)
  if (!response.ok) throw new Error('Failed to get funnel analytics')
  return response.json()
}

export async function deleteFunnel(funnelId: string): Promise<void> {
    const response = await apiFetch(`${API_URL}/funnels/${funnelId}`, { method: 'DELETE' })
  if (!response.ok) throw new Error('Failed to delete funnel')
}

// ============ End P4: Funnel Analytics API ============

// ============ P4: Attribution API ============

export interface TouchpointData {
  id: string
  content_id: string
  channel: string
  source: string
  campaign?: string
  created_at?: string
}

export type AttributionTouchpoint = TouchpointData

export interface ChannelPerformanceData {
  channel: string
  source: string
  attribution_weight: number
  revenue_attributed: number
  conversion_count: number
  total_touchpoints?: number
  total_conversions?: number
}

export type ChannelPerformanceResult = ChannelPerformanceData

export type AttributionResult = ChannelPerformanceData

export interface TouchpointListResponse {
  touchpoints: TouchpointData[]
}

export type AttributionModel = 'first_touch' | 'last_touch' | 'linear' | 'time_decay' | 'position_based'

export async function recordTouchpoint(data: { content_id: string; channel: string; source: string; campaign?: string }): Promise<TouchpointData> {
    const response = await apiFetch(`${API_URL}/attribution/touchpoints`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error('Failed to record touchpoint')
  return response.json()
}

export async function getTouchpoints(contentId: string): Promise<AttributionTouchpoint[]> {
    const response = await apiFetch(`${API_URL}/attribution/touchpoints/${contentId}`)
  if (!response.ok) throw new Error('Failed to get touchpoints')
  return response.json()
}

export async function calculateAttribution(contentId: string, model: AttributionModel): Promise<AttributionResult[]> {
    const response = await apiFetch(`${API_URL}/attribution/calculate`, { method: 'POST', body: JSON.stringify({ content_id: contentId, model  }),
  })
  if (!response.ok) throw new Error('Failed to calculate attribution')
  return response.json()
}

export async function getChannelPerformance(dateRange?: { start: string; end: string }): Promise<AttributionResult[]> {
  const params = dateRange ? `?start=${dateRange.start}&end=${dateRange.end}` : ''
  const response = await apiFetch(`${API_URL}/attribution/channels${params}`)
  if (!response.ok) throw new Error('Failed to get channel performance')
  return response.json()
}

// ============ End P4: Attribution API ============

// ============ P4: SLA Monitoring API ============

export interface SLAPolicy {
  id: string
  name: string
  metric: string
  threshold: number
  window_minutes: number
  severity: string
  enabled: boolean
  created_at: string
  updated_at: string
}

export interface SLAAlert {
  id: string
  policy_id: string
  metric_type: string
  current_value: number
  threshold: number
  severity: string
  message: string
  created_at: string
  acknowledged: boolean
}

export interface SLADashboardData {
  uptime_percentage: number
  avg_response_time_ms: number
  error_rate: number
  throughput_rps: number
  active_alerts: number
  policy_compliance: Record<string, boolean>
}

export async function createSLAPolicy(data: { name: string; metric: string; threshold: number; window_minutes: number; severity: string }): Promise<SLAPolicy> {
    const response = await apiFetch(`${API_URL}/sla/policies`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error('Failed to create SLA policy')
  return response.json()
}

export async function listSLAPolicies(): Promise<SLAPolicy[]> {
    const response = await apiFetch(`${API_URL}/sla/policies`)
  if (!response.ok) throw new Error('Failed to list SLA policies')
  return response.json()
}

export async function getSLADashboard(): Promise<SLADashboardData> {
    const response = await apiFetch(`${API_URL}/sla/dashboard`)
  if (!response.ok) throw new Error('Failed to get SLA dashboard')
  return response.json()
}

export async function getSLAAlerts(acknowledged?: boolean): Promise<SLAAlert[]> {
    const params = acknowledged !== undefined ? `?acknowledged=${acknowledged}` : ''
  const response = await apiFetch(`${API_URL}/sla/alerts${params}`)
  if (!response.ok) throw new Error('Failed to get SLA alerts')
  return response.json()
}

export async function acknowledgeSLAAlert(alertId: string): Promise<void> {
    const response = await apiFetch(`${API_URL}/sla/alerts/${alertId}/acknowledge`, { method: 'PUT' })
  if (!response.ok) throw new Error('Failed to acknowledge SLA alert')
}

export async function updateSLAPolicy(policyId: string, data: Partial<SLAPolicy>): Promise<SLAPolicy> {
    const response = await apiFetch(`${API_URL}/sla/policies/${policyId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error('Failed to update SLA policy')
  return response.json()
}

export async function deleteSLAPolicy(policyId: string): Promise<void> {
    const response = await apiFetch(`${API_URL}/sla/policies/${policyId}`, { method: 'DELETE' })
  if (!response.ok) throw new Error('Failed to delete SLA policy')
}

export interface SLAMetricData {
  metric_type: string
  value: number
  labels?: Record<string, string>
  timestamp?: string
}

export async function recordSLAMetric(data: SLAMetricData): Promise<{ success: boolean }> {
    const response = await apiFetch(`${API_URL}/sla/metrics`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error('Failed to record SLA metric')
  return response.json()
}

export async function getSLAUptime(days: number = 30): Promise<{ uptime_percentage: number; period_days: number }> {
    const response = await apiFetch(`${API_URL}/sla/uptime?days=${days}`)
  if (!response.ok) throw new Error('Failed to get SLA uptime')
  return response.json()
}

export async function getSLAResponseTime(days: number = 30): Promise<{ avg_ms: number; p50: number; p95: number; p99: number }> {
    const response = await apiFetch(`${API_URL}/sla/response-time?days=${days}`)
  if (!response.ok) throw new Error('Failed to get SLA response time')
  return response.json()
}

export async function getSLAErrorRate(days: number = 30): Promise<{ error_rate: number; period_days: number }> {
    const response = await apiFetch(`${API_URL}/sla/error-rate?days=${days}`)
  if (!response.ok) throw new Error('Failed to get SLA error rate')
  return response.json()
}

export type SLAAlertData = SLAAlert

export interface SLAAlertListResponse {
  alerts: SLAAlertData[]
  total: number
}

// Override getSLAAlerts to return list response
export async function getSLAAlertsWithResponse(acknowledged?: boolean): Promise<SLAAlertListResponse> {
  const params = acknowledged !== undefined ? `?acknowledged=${acknowledged}` : ''
  const response = await apiFetch(`${API_URL}/sla/alerts${params}`)
  if (!response.ok) throw new Error('Failed to get SLA alerts')
  return response.json()
}

// ============ End P4: SLA Monitoring API ============

// ============ P4: Integration Framework API ============

export interface IntegrationConfigData {
  id: string
  user_id: string
  name: string
  type: string
  provider: string
  credentials: Record<string, unknown>
  settings: Record<string, unknown>
  enabled: boolean
  created_at: string
  updated_at: string
}

export interface IntegrationLogData {
  id: string
  config_id: string
  event_id: string | null
  level: string
  message: string
  created_at: string
}

export interface IntegrationLogListResponse {
  logs: IntegrationLogData[]
  total: number
}

export interface IntegrationStatusData {
  config_id: string
  name: string
  type: string
  provider: string
  enabled: boolean
  health_status: string
  total_events_24h: number
  completed_events_24h: number
  failed_events_24h: number
  pending_events: number
  last_event_at: string | null
  last_log: { created_at: string; level: string; message: string } | null
}

export interface IntegrationEventData {
  id: string
  user_id: string
  config_id: string
  event_type: string
  payload: Record<string, unknown>
  status: string
  retries: number
  created_at: string
}

export async function registerIntegration(data: { name: string; type: string; provider: string; credentials: Record<string, unknown>; settings?: Record<string, unknown> }): Promise<IntegrationConfigData> {
    const response = await apiFetch(`${API_URL}/integration-framework/configs`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error('Failed to register integration')
  return response.json()
}

export async function listIntegrations(): Promise<IntegrationConfigData[]> {
    const response = await apiFetch(`${API_URL}/integration-framework/configs`)
  if (!response.ok) throw new Error('Failed to list integrations')
  return response.json()
}

export async function updateIntegration(configId: string, data: Record<string, unknown>): Promise<IntegrationConfigData> {
    const response = await apiFetch(`${API_URL}/integration-framework/configs/${configId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error('Failed to update integration')
  return response.json()
}

export async function deleteIntegration(configId: string): Promise<void> {
    const response = await apiFetch(`${API_URL}/integration-framework/configs/${configId}`, { method: 'DELETE' })
  if (!response.ok) throw new Error('Failed to delete integration')
}

export async function testIntegration(configId: string): Promise<{ success: boolean; message: string; latency_ms: number }> {
    const response = await apiFetch(`${API_URL}/integration-framework/configs/${configId}/test`, { method: 'POST' })
  if (!response.ok) throw new Error('Failed to test integration')
  return response.json()
}

export async function triggerIntegrationEvent(configId: string, data: { event_type: string; payload: Record<string, unknown> }): Promise<IntegrationEventData> {
    const response = await apiFetch(`${API_URL}/integration-framework/configs/${configId}/events`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error('Failed to trigger integration event')
  return response.json()
}

export async function retryFailedEvent(eventId: string): Promise<{ success: boolean; message: string }> {
    const response = await apiFetch(`${API_URL}/integration-framework/events/${eventId}/retry`, { method: 'POST' })
  if (!response.ok) throw new Error('Failed to retry event')
  return response.json()
}

export async function getIntegrationLogs(configId: string, limit: number = 100): Promise<IntegrationLogListResponse> {
    const response = await apiFetch(`${API_URL}/integration-framework/configs/${configId}/logs?limit=${limit}`)
  if (!response.ok) throw new Error('Failed to get integration logs')
  return response.json()
}

export async function getIntegrationStatus(configId: string): Promise<IntegrationStatusData> {
    const response = await apiFetch(`${API_URL}/integration-framework/configs/${configId}/status`)
  if (!response.ok) throw new Error('Failed to get integration status')
  return response.json()
}

// ============ End P4: Integration Framework API ============

// ============ Alerts API ============

export interface AlertData {
  id: string
  user_id: string
  alert_type: string
  content_id: string | null
  metric_name: string
  threshold_value: number
  current_value: number
  status: string
  message: string | null
  created_at: string
  acknowledged_at: string | null
}

export interface AlertListData {
  alerts: AlertData[]
  total: number
  limit: number
  offset: number
}

export interface UnreadCountData {
  unread_count: number
}

export interface AlertRuleData {
  id: string
  user_id: string
  name: string
  alert_type: string
  metric_name: string
  operator: string
  threshold_value: number
  is_enabled: boolean
  notification_channels: string[]
  created_at: string
  updated_at: string
}

export async function getAlerts(limit: number = 50, offset: number = 0): Promise<AlertListData> {
  const response = await apiFetch(`${API_URL}/alerts?limit=${limit}&offset=${offset}`)
  if (!response.ok) throw new Error('Failed to fetch alerts')
  return response.json()
}

export async function getUnreadAlertCount(): Promise<UnreadCountData> {
  const response = await apiFetch(`${API_URL}/alerts/unread-count`)
  if (!response.ok) throw new Error('Failed to fetch unread count')
  return response.json()
}

export async function acknowledgeAlert(alertId: string): Promise<void> {
  const response = await apiFetch(`${API_URL}/alerts/acknowledge/${alertId}`, { method: 'POST' })
  if (!response.ok) throw new Error('Failed to acknowledge alert')
}

export async function resolveAlert(alertId: string): Promise<void> {
  const response = await apiFetch(`${API_URL}/alerts/resolve/${alertId}`, { method: 'POST' })
  if (!response.ok) throw new Error('Failed to resolve alert')
}

export async function getAlertRules(): Promise<AlertRuleData[]> {
  const response = await apiFetch(`${API_URL}/alerts/rules`)
  if (!response.ok) throw new Error('Failed to fetch alert rules')
  const data = await response.json()
  return data.rules ?? data
}

export interface AlertRuleCreateData {
  name: string
  alert_type: string
  metric_name: string
  operator: string
  threshold_value: number
  notification_channels?: string[]
}

export interface AlertRuleUpdateData {
  name?: string
  alert_type?: string
  metric_name?: string
  operator?: string
  threshold_value?: number
  is_enabled?: boolean
  notification_channels?: string[]
}

export async function createAlertRule(rule: AlertRuleCreateData): Promise<AlertRuleData> {
  const response = await apiFetch(`${API_URL}/alerts/rules`, {
    method: 'POST',
    body: JSON.stringify(rule),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create alert rule')
  }
  return response.json()
}

export async function updateAlertRule(ruleId: string, updates: AlertRuleUpdateData): Promise<AlertRuleData> {
  const response = await apiFetch(`${API_URL}/alerts/rules/${ruleId}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update alert rule')
  }
  return response.json()
}

export async function deleteAlertRule(ruleId: string): Promise<void> {
  const response = await apiFetch(`${API_URL}/alerts/rules/${ruleId}`, { method: 'DELETE' })
  if (!response.ok) throw new Error('Failed to delete alert rule')
}

// ============ End Alerts API ============

// ============ Competitors API ============

export interface CompetitorData {
  id: string
  name: string
  website: string | null
  industry: string | null
  notes: string | null
  created_at: string
}

export interface CompetitorListData {
  competitors: CompetitorData[]
}

export interface PerformanceAnalysisData {
  competitors: Array<{
    name: string
    metrics: Record<string, number>
  }>
}

export async function getCompetitors(): Promise<CompetitorListData> {
  const response = await apiFetch(`${API_URL}/competitors`)
  if (!response.ok) throw new Error('Failed to fetch competitors')
  return response.json()
}

export async function getCompetitorAnalysis(): Promise<PerformanceAnalysisData> {
  const response = await apiFetch(`${API_URL}/competitors/analysis`)
  if (!response.ok) throw new Error('Failed to fetch competitor analysis')
  return response.json()
}

// ============ End Competitors API ============


// ============ Team Calendar API ============

export interface TeamCalendarMember {
  id: string
  name: string
  email: string
  role: string
  avatar_url: string | null
  color: string | null
}

export interface TeamCalendarPost {
  id: string
  user_id: string
  content_id: string
  platform: string
  scheduled_at: string
  status: string
  asset_type: string
  timezone: string
  content: string | null
  settings: Record<string, unknown>
  assigned_to: string[]
  recurrence: string | null
  created_at: string
  updated_at: string
  published_at: string | null
  error_message: string | null
  published_url: string | null
  author_name: string | null
  author_avatar: string | null
}

export interface TeamCalendarDay {
  date: string
  posts: TeamCalendarPost[]
}

export interface TeamCalendarMonthResponse {
  org_id: string
  year: number
  month: number
  members: TeamCalendarMember[]
  days: TeamCalendarDay[]
  stats: Record<string, number>
}

export interface TeamCalendarWeekResponse {
  org_id: string
  start_date: string
  end_date: string
  members: TeamCalendarMember[]
  days: TeamCalendarDay[]
  stats: Record<string, number>
}

export interface TeamCalendarDayResponse {
  org_id: string
  date: string
  members: TeamCalendarMember[]
  posts: TeamCalendarPost[]
  stats: Record<string, number>
}

export interface TeamConflictDetail {
  post_id: string
  title: string | null
  platform: string
  scheduled_at: string
  assigned_to: string[]
}

export interface TeamConflictCheckResponse {
  has_conflicts: boolean
  conflict_count: number
  conflicts: TeamConflictDetail[]
}

export async function getTeamCalendarMonth(
  orgId: string,
  year: number,
  month: number,
  memberId?: string,
  platform?: string,
): Promise<TeamCalendarMonthResponse> {
  const params = new URLSearchParams({ org_id: orgId, year: String(year), month: String(month) })
  if (memberId) params.append('member', memberId)
  if (platform) params.append('platform', platform)
  const response = await apiFetch(`${API_URL}/team-calendar/month?${params.toString()}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch team calendar month')
  }
  return response.json()
}

export async function getTeamCalendarWeek(
  orgId: string,
  startDate: string,
  memberId?: string,
  platform?: string,
): Promise<TeamCalendarWeekResponse> {
  const params = new URLSearchParams({ org_id: orgId, start_date: startDate })
  if (memberId) params.append('member', memberId)
  if (platform) params.append('platform', platform)
  const response = await apiFetch(`${API_URL}/team-calendar/week?${params.toString()}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch team calendar week')
  }
  return response.json()
}

export async function getTeamCalendarDay(
  orgId: string,
  date: string,
  memberId?: string,
  platform?: string,
): Promise<TeamCalendarDayResponse> {
  const params = new URLSearchParams({ org_id: orgId, date })
  if (memberId) params.append('member', memberId)
  if (platform) params.append('platform', platform)
  const response = await apiFetch(`${API_URL}/team-calendar/day?${params.toString()}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch team calendar day')
  }
  return response.json()
}

export async function getTeamCalendarMembers(orgId: string): Promise<TeamCalendarMember[]> {
  const params = new URLSearchParams({ org_id: orgId })
  const response = await apiFetch(`${API_URL}/team-calendar/members?${params.toString()}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch team members')
  }
  return response.json()
}

export async function updatePostAssignment(
  postId: string,
  orgId: string,
  assignedTo: string[],
): Promise<{ message: string; post_id: string; assigned_to: string[] }> {
  const params = new URLSearchParams({ org_id: orgId })
  const response = await apiFetch(`${API_URL}/team-calendar/schedule/${postId}/assign?${params.toString()}`, {
    method: 'PUT',
    body: JSON.stringify({ assigned_to: assignedTo }),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update post assignment')
  }
  return response.json()
}

export async function checkTeamCalendarConflicts(
  orgId: string,
  scheduledAt: string,
  platform: string,
  excludeId?: string,
  windowMinutes?: number,
): Promise<TeamConflictCheckResponse> {
  const params = new URLSearchParams({ org_id: orgId, scheduled_at: scheduledAt, platform })
  if (excludeId) params.append('exclude_id', excludeId)
  if (windowMinutes) params.append('window_minutes', String(windowMinutes))
  const response = await apiFetch(`${API_URL}/team-calendar/conflicts?${params.toString()}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to check conflicts')
  }
  return response.json()
}

// ============ End Team Calendar API ============

// ============ Engagement Prediction API ============

export interface EngagementFactorScores {
  readability: number
  emotional_impact: number
  hashtag_usage: number
  optimal_length: number
  call_to_action: number
}

export interface PredictedEngagementMetrics {
  likes: number
  comments: number
  shares: number
  impressions: number
}

export interface EngagementPredictionResult {
  score: number
  confidence: number
  factors: EngagementFactorScores
  suggestions: string[]
  predicted_engagement: PredictedEngagementMetrics
  best_posting_time: string
  platform: string
  content_length: number
  analyzed_at: string
}

export interface EngagementPredictionHistoryItem {
  id: string
  user_id: string
  content_id: string | null
  platform: string
  score: number
  content_preview: string
  created_at: string
}

export interface EngagementPredictionHistory {
  items: EngagementPredictionHistoryItem[]
  total: number
  page: number
  limit: number
}

export interface PlatformConfig {
  optimal_length_range: [number, number]
  max_length: number
  hashtag_ideal: [number, number]
  best_times: string[]
  base_engagement: {
    likes: number
    comments: number
    shares: number
    impressions: number
  }
}

export async function analyzeEngagement(
  content: string,
  platform: string = 'twitter',
  contentId?: string,
  useAi: boolean = false,
): Promise<EngagementPredictionResult> {
  const response = await apiFetch(`${API_URL}/engagement-prediction/analyze`, {
    method: 'POST',
    body: JSON.stringify({
      content,
      platform,
      content_id: contentId,
      use_ai: useAi,
    }),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to analyze engagement')
  }
  return response.json()
}

export async function getEngagementPredictionHistory(
  limit: number = 20,
  offset: number = 0,
): Promise<EngagementPredictionHistory> {
  const response = await apiFetch(`${API_URL}/engagement-prediction/history?limit=${limit}&offset=${offset}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to get prediction history')
  }
  return response.json()
}

export async function getEngagementPlatformConfig(): Promise<Record<string, PlatformConfig>> {
  const response = await apiFetch(`${API_URL}/engagement-prediction/platform-config`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to get platform config')
  }
  const data = await response.json()
  return data.platforms
}

// ============ End Engagement Prediction API ============

// ============ Integrations Panel API (CRUD) ============

export interface IntegrationItem {
  id: string
  user_id: string
  integration_type: string
  name: string
  config: Record<string, unknown>
  is_active: boolean
  last_used_at: string | null
  created_at: string
  updated_at: string
}

export interface IntegrationListResult {
  integrations: IntegrationItem[]
  total: number
}

export interface IntegrationTypeInfo {
  type: string
  name: string
  description: string
  icon: string
  config_schema: Record<string, unknown>
}

export interface IntegrationTypesResult {
  types: IntegrationTypeInfo[]
  event_types: Array<{ value: string; label: string }>
}

export interface IntegrationTestResult {
  success: boolean
  message: string
  integration_id: string
}

export async function listUserIntegrations(
  integrationType?: string,
  isActive?: boolean,
): Promise<IntegrationListResult> {
  const params = new URLSearchParams()
  if (integrationType) params.append('integration_type', integrationType)
  if (isActive !== undefined) params.append('is_active', String(isActive))
  const qs = params.toString()
  const response = await apiFetch(`${API_URL}/integrations${qs ? `?${qs}` : ''}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to list integrations')
  }
  return response.json()
}

export async function getIntegrationById(id: string): Promise<IntegrationItem> {
  const response = await apiFetch(`${API_URL}/integrations/${id}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to get integration')
  }
  return response.json()
}

export async function createIntegration(data: {
  integration_type: string
  name: string
  config?: Record<string, unknown>
  is_active?: boolean
}): Promise<IntegrationItem> {
  const response = await apiFetch(`${API_URL}/integrations`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create integration')
  }
  return response.json()
}

export async function updateIntegrationById(
  id: string,
  data: { name?: string; config?: Record<string, unknown>; is_active?: boolean },
): Promise<IntegrationItem> {
  const response = await apiFetch(`${API_URL}/integrations/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update integration')
  }
  return response.json()
}

export async function deleteIntegrationById(id: string): Promise<void> {
  const response = await apiFetch(`${API_URL}/integrations/${id}`, { method: 'DELETE' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to delete integration')
  }
}

export async function getIntegrationTypes(): Promise<IntegrationTypesResult> {
  const response = await apiFetch(`${API_URL}/integrations/types`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to get integration types')
  }
  return response.json()
}

export async function testIntegrationConnection(id: string): Promise<IntegrationTestResult> {
  const response = await apiFetch(`${API_URL}/integrations/${id}/test`, { method: 'POST' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to test integration')
  }
  return response.json()
}

// ============ End Integrations Panel API ============

// ============ A/B Testing API ============

export interface ABExperiment {
  id: string
  user_id: string
  name: string
  content_id: string | null
  variant_a: string
  variant_b: string
  platform: string
  status: 'draft' | 'running' | 'paused' | 'completed' | 'stopped'
  duration_days: number
  started_at: string | null
  ended_at: string | null
  created_at: string
  updated_at: string
}

export interface ABExperimentDetail extends ABExperiment {
  variant_a_results: {
    impressions: number
    engagements: number
    clicks: number
    engagementRate: number
    clickRate: number
  } | null
  variant_b_results: {
    impressions: number
    engagements: number
    clicks: number
    engagementRate: number
    clickRate: number
  } | null
  winner: string | null
  confidence: number | null
}

export interface ABExperimentListResult {
  experiments: ABExperiment[]
  total: number
}

export interface ABExperimentResults {
  experiment_id: string
  variant_a: {
    impressions: number
    engagements: number
    clicks: number
    engagementRate: number
    clickRate: number
  }
  variant_b: {
    impressions: number
    engagements: number
    clicks: number
    engagementRate: number
    clickRate: number
  }
  winner: string | null
  confidence: number | null
  total_results: number
}

export async function createABExperiment(data: {
  name: string
  content_id?: string
  variant_a: string
  variant_b: string
  platform?: string
  duration_days?: number
}): Promise<ABExperiment> {
  const response = await apiFetch(`${API_URL}/ab-testing/experiments`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create experiment')
  }
  return response.json()
}

export async function listABExperiments(status?: string): Promise<ABExperimentListResult> {
  const params = new URLSearchParams()
  if (status) params.append('status', status)
  const qs = params.toString()
  const response = await apiFetch(`${API_URL}/ab-testing/experiments${qs ? `?${qs}` : ''}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to list experiments')
  }
  return response.json()
}

export async function getABExperiment(id: string): Promise<ABExperimentDetail> {
  const response = await apiFetch(`${API_URL}/ab-testing/experiments/${id}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to get experiment')
  }
  return response.json()
}

export async function updateABExperiment(
  id: string,
  data: { status?: string; name?: string },
): Promise<ABExperiment> {
  const response = await apiFetch(`${API_URL}/ab-testing/experiments/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update experiment')
  }
  return response.json()
}

export async function recordABResult(
  experimentId: string,
  data: { variant: 'a' | 'b'; impressions: number; engagements: number; clicks: number },
): Promise<{ success: boolean; message: string }> {
  const response = await apiFetch(`${API_URL}/ab-testing/experiments/${experimentId}/results`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to record result')
  }
  return response.json()
}

export async function getABExperimentResults(experimentId: string): Promise<ABExperimentResults> {
  const response = await apiFetch(`${API_URL}/ab-testing/experiments/${experimentId}/results`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to get experiment results')
  }
  return response.json()
}

export async function deleteABExperiment(id: string): Promise<void> {
  const response = await apiFetch(`${API_URL}/ab-testing/experiments/${id}`, { method: 'DELETE' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to delete experiment')
  }
}

// ============ End A/B Testing API ============

// ============ Competitor Analysis Full API ============

export interface CompetitorItem {
  id: string
  user_id: string
  name: string
  platform: string
  handle: string
  follower_count: number
  description: string | null
  profile_url: string | null
  is_active: boolean
  last_synced_at: string | null
  created_at: string
}

export interface CompetitorContentItem {
  id: string
  competitor_id: string
  external_id: string
  content: string
  content_type: string
  published_at: string
  url: string | null
  likes: number
  shares: number
  comments: number
  views: number
  engagement_score: number
  sentiment: string | null
  topics: string[]
  keywords: string[]
  analyzed_at: string | null
}

export interface CompetitorAnalysisItem {
  id: string
  name: string
  platform: string
  handle: string
  follower_count: number
  content_last_30_days: number
  avg_engagement_rate: number
  last_synced: string | null
}

export interface PerformanceInsight {
  type: string
  title: string
  description: string
  platform: string | null
  recommendation: string
}

export interface CompetitorPerformanceAnalysis {
  competitor_count: number
  competitors: CompetitorAnalysisItem[]
  aggregated_metrics: Record<string, unknown>
  platform_breakdown: Record<string, Record<string, unknown>>
  insights: PerformanceInsight[]
}

export interface ContentGapItem {
  id: string
  user_id: string
  topic: string
  category: string | null
  competitor_count: number
  user_has_content: boolean
  user_content_count: number
  opportunity_score: number
  suggested_action: string | null
  content_ideas: string[]
  priority: string
  is_addressed: boolean
  created_at: string
}

export interface ContentGapAnalysisResult {
  gaps_analyzed: number
  gaps_stored: number
  gaps: ContentGapItem[]
}

export interface TopicOverlapResult {
  competitor_topic_count: number
  user_topic_count: number
  overlap_count: number
  overlap_percentage: number
  shared_topics: string[]
  competitor_only_topics: string[]
  user_only_topics: string[]
  recommendation: string
}

export interface BenchmarkComparisonResult {
  user_metrics: Record<string, unknown>
  competitor_avg: Record<string, unknown>
  comparison: Record<string, unknown>
  percentile: Record<string, number>
}

export async function addCompetitor(data: {
  name: string
  platform: string
  handle: string
  description?: string
  profile_url?: string
}): Promise<CompetitorItem> {
  const response = await apiFetch(`${API_URL}/competitors`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to add competitor')
  }
  return response.json()
}

export async function listCompetitors(platform?: string): Promise<CompetitorItem[]> {
  const params = new URLSearchParams()
  if (platform) params.append('platform', platform)
  const qs = params.toString()
  const response = await apiFetch(`${API_URL}/competitors${qs ? `?${qs}` : ''}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to list competitors')
  }
  return response.json()
}

export async function removeCompetitor(id: string): Promise<{ success: boolean; message: string }> {
  const response = await apiFetch(`${API_URL}/competitors/${id}`, { method: 'DELETE' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to remove competitor')
  }
  return response.json()
}

export async function getCompetitorContent(
  competitorId: string,
  limit: number = 50,
  offset: number = 0,
): Promise<CompetitorContentItem[]> {
  const response = await apiFetch(`${API_URL}/competitors/${competitorId}/content?limit=${limit}&offset=${offset}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch competitor content')
  }
  return response.json()
}

export async function getCompetitorPerformanceAnalysis(): Promise<CompetitorPerformanceAnalysis> {
  const response = await apiFetch(`${API_URL}/competitors/analysis`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch performance analysis')
  }
  return response.json()
}

export async function getContentGaps(minOpportunity: number = 0): Promise<ContentGapItem[]> {
  const response = await apiFetch(`${API_URL}/competitors/gaps?min_opportunity=${minOpportunity}`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch content gaps')
  }
  return response.json()
}

export async function analyzeContentGaps(): Promise<ContentGapAnalysisResult> {
  const response = await apiFetch(`${API_URL}/competitors/gaps/analyze`, { method: 'POST' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to analyze content gaps')
  }
  return response.json()
}

export async function getTopicOverlap(): Promise<TopicOverlapResult> {
  const response = await apiFetch(`${API_URL}/competitors/topics/overlap`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to get topic overlap')
  }
  return response.json()
}

export async function getBenchmarkComparison(): Promise<BenchmarkComparisonResult> {
  const response = await apiFetch(`${API_URL}/competitors/benchmark`)
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to get benchmark comparison')
  }
  return response.json()
}

export async function refreshCompetitorData(competitorId: string): Promise<{
  success: boolean
  competitor_id: string
  new_content_count: number
  total_content: number
}> {
  const response = await apiFetch(`${API_URL}/competitors/${competitorId}/refresh`, { method: 'POST' })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to refresh competitor data')
  }
  return response.json()
}

// ============ End Competitor Analysis Full API ============
