import { supabase } from './supabase'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

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

async function getAuthHeader(): Promise<Record<string, string>> {
  const { data: { session } } = await supabase.auth.getSession()
  
  if (!session?.access_token) {
    return {}
  }
  
  return {
    'Authorization': `Bearer ${session.access_token}`,
    'Content-Type': 'application/json',
  }
}

export async function createContent(data: ContentCreate): Promise<Content> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/content`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create content')
  }
  
  return response.json()
}

export async function listContent(projectId?: string): Promise<Content[]> {
  const headers = await getAuthHeader()
  
  let url = `${API_URL}/content`
  if (projectId) {
    url += `?project_id=${projectId}`
  }
  
  const response = await fetch(url, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch content')
  }
  
  return response.json()
}

export async function getContent(contentId: string): Promise<Content> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/content/${contentId}`, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch content')
  }
  
  return response.json()
}

export async function generateAssets(contentId: string): Promise<GeneratedAsset[]> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/content/${contentId}/generate`, {
    method: 'POST',
    headers,
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to generate assets')
  }
  
  return response.json()
}

export async function listAssets(contentId: string): Promise<GeneratedAsset[]> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/content/${contentId}/assets`, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch assets')
  }
  
  return response.json()
}

export async function deleteContent(contentId: string): Promise<void> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/content/${contentId}`, {
    method: 'DELETE',
    headers,
  })
  
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/projects`, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch projects')
  }
  
  return response.json()
}

export async function createProject(data: { name: string; description?: string }): Promise<Project> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/projects`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create project')
  }
  
  return response.json()
}

export async function getProject(projectId: string): Promise<Project> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/projects/${projectId}`, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch project')
  }
  
  return response.json()
}

export async function deleteProject(projectId: string): Promise<void> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/projects/${projectId}`, {
    method: 'DELETE',
    headers,
  })
  
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/distributions`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to schedule distribution')
  }
  
  return response.json()
}

export async function listDistributions(status?: string): Promise<Distribution[]> {
  const headers = await getAuthHeader()
  
  let url = `${API_URL}/distributions`
  if (status) {
    url += `?status=${status}`
  }
  
  const response = await fetch(url, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch distributions')
  }
  
  return response.json()
}

export async function publishNow(distributionId: string): Promise<Distribution> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/distributions/${distributionId}/publish-now`, {
    method: 'POST',
    headers,
  })
  
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/usage/summary`, { headers })
  
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/analytics/content`, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch content metrics')
  }
  
  return response.json()
}

export async function getAssetMetrics(): Promise<AssetMetricsResponse> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/analytics/assets`, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch asset metrics')
  }
  
  return response.json()
}

export async function getUsageMetrics(days: number = 30): Promise<UsageMetricsResponse> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/analytics/usage?days=${days}`, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch usage metrics')
  }
  
  return response.json()
}

export async function getDistributionMetrics(): Promise<DistributionMetricsResponse> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/analytics/distributions`, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch distribution metrics')
  }
  
  return response.json()
}

export async function getDashboardKPIs(): Promise<KPIDashboardResponse> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/analytics/dashboard`, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch dashboard KPIs')
  }
  
  return response.json()
}

export async function exportAnalyticsCSV(days: number = 30): Promise<Blob> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/analytics/export?format=csv&days=${days}`, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to export analytics')
  }
  
  return response.blob()
}

export async function exportAnalyticsJSON(days: number = 30): Promise<Blob> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/analytics/export/json?days=${days}`, { headers })
  
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/ai-suggestions/improve`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ content_id: contentId, suggestion_type: suggestionType }),
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/ai-suggestions/seo`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ content_id: contentId, keywords, target_audience: targetAudience }),
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/ai-suggestions/tone`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ content_id: contentId, tone }),
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
  const headers = await getAuthHeader()
  
  let url = `${API_URL}/ai-suggestions/${contentId}`
  if (suggestionType) {
    url += `?suggestion_type=${suggestionType}`
  }
  
  const response = await fetch(url, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to list AI suggestions')
  }
  
  return response.json()
}

export async function applySuggestion(suggestionId: string): Promise<AIImprovementSuggestion> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/ai-suggestions/${suggestionId}/apply`, {
    method: 'PATCH',
    headers,
  })
  
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/automation/rules`, {
    method: 'POST',
    headers,
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
  const headers = await getAuthHeader()
  
  let url = `${API_URL}/automation/rules`
  const params = new URLSearchParams()
  if (projectId) params.append('project_id', projectId)
  if (status) params.append('status', status)
  if (params.toString()) url += `?${params.toString()}`
  
  const response = await fetch(url, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch automation rules')
  }
  
  return response.json()
}

export async function getAutomationRule(ruleId: string): Promise<AutomationRule> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/automation/rules/${ruleId}`, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch automation rule')
  }
  
  return response.json()
}

export async function toggleAutomationRule(ruleId: string): Promise<{ status: string }> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/automation/rules/${ruleId}/toggle`, {
    method: 'POST',
    headers,
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to toggle automation rule')
  }
  
  return response.json()
}

export async function runAutomationRule(ruleId: string): Promise<{ message: string; log_id: string }> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/automation/rules/${ruleId}/run`, {
    method: 'POST',
    headers,
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to run automation rule')
  }
  
  return response.json()
}

export async function listAutomationLogs(ruleId?: string): Promise<AutomationLog[]> {
  const headers = await getAuthHeader()
  
  let url = `${API_URL}/automation/logs`
  if (ruleId) url += `?rule_id=${ruleId}`
  
  const response = await fetch(url, { headers })
  
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/automation/best-times/${platform}`, { headers })
  
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/automation/schedule/bulk`, {
    method: 'POST',
    headers,
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
  const headers = await getAuthHeader()
  
  let url = `${API_URL}/automation/queue`
  if (status) url += `?status=${status}`
  
  const response = await fetch(url, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch publishing queue')
  }
  
  return response.json()
}

export async function cancelQueueItem(queueId: string): Promise<{ message: string }> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/automation/queue/${queueId}/cancel`, {
    method: 'POST',
    headers,
  })
  
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/schedule`, {
    method: 'POST',
    headers,
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
  const headers = await getAuthHeader()
  
  let url = `${API_URL}/schedule`
  const params = new URLSearchParams()
  if (status) params.append('status', status)
  if (startDate) params.append('start_date', startDate)
  if (endDate) params.append('end_date', endDate)
  if (params.toString()) url += `?${params.toString()}`
  
  const response = await fetch(url, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch scheduled posts')
  }
  
  return response.json()
}

export async function getScheduledPost(scheduleId: string): Promise<ScheduledPost> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/schedule/${scheduleId}`, { headers })
  
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/schedule/${scheduleId}`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(updates),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update scheduled post')
  }
  
  return response.json()
}

export async function cancelScheduledPost(scheduleId: string): Promise<{ message: string }> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/schedule/${scheduleId}/cancel`, {
    method: 'POST',
    headers,
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to cancel scheduled post')
  }
  
  return response.json()
}

export async function publishScheduledPost(scheduleId: string): Promise<ScheduledPost> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/schedule/${scheduleId}/publish-now`, {
    method: 'POST',
    headers,
  })
  
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
  const headers = await getAuthHeader()
  
  const params = new URLSearchParams()
  params.append('scheduled_at', scheduledAt)
  platforms.forEach(p => params.append('platforms', p))
  if (excludeId) params.append('exclude_id', excludeId)
  
  const response = await fetch(`${API_URL}/schedule/conflicts?${params.toString()}`, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to check conflicts')
  }
  
  return response.json()
}

export async function getUpcomingPosts(limit: number = 5): Promise<ScheduledPost[]> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/schedule/upcoming?limit=${limit}`, { headers })
  
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
  const headers = await getAuthHeader()
  
  const body: Record<string, string | undefined> = {}
  if (newScheduledAt) body.scheduled_at = newScheduledAt
  
  const response = await fetch(`${API_URL}/schedule/${scheduleId}/duplicate`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  })
  
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/auth/me`, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch profile')
  }
  
  return response.json()
}

export async function updateUserProfile(data: { full_name: string }): Promise<UserProfile> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/auth/me`, {
    method: 'PATCH',
    headers,
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/organizations`, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch organizations')
  }
  
  return response.json()
}

export async function createOrganization(data: OrganizationCreate): Promise<Organization> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/organizations`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to create organization')
  }
  
  return response.json()
}

export async function getOrganization(orgId: string): Promise<OrganizationWithMembers> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/organizations/${orgId}`, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch organization')
  }
  
  return response.json()
}

export async function updateOrganization(orgId: string, data: OrganizationUpdate): Promise<Organization> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/organizations/${orgId}`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(data),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update organization')
  }
  
  return response.json()
}

export async function deleteOrganization(orgId: string): Promise<void> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/organizations/${orgId}`, {
    method: 'DELETE',
    headers,
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to delete organization')
  }
}

export async function inviteMember(orgId: string, data: OrganizationInvite): Promise<OrganizationInvitationResponse> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/organizations/${orgId}/invite`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to invite member')
  }
  
  return response.json()
}

export async function listMembers(orgId: string): Promise<OrganizationMember[]> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/organizations/${orgId}/members`, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch members')
  }
  
  return response.json()
}

export async function updateMemberRole(orgId: string, memberId: string, role: OrganizationRole): Promise<OrganizationMember> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/organizations/${orgId}/members/${memberId}`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify({ role }),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update member role')
  }
  
  return response.json()
}

export async function removeMember(orgId: string, memberId: string): Promise<void> {
  const headers = await getAuthHeader()

  const response = await fetch(`${API_URL}/organizations/${orgId}/members/${memberId}`, {
    method: 'DELETE',
    headers,
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to remove member')
  }
}

export async function transferOwnership(orgId: string, newOwnerId: string): Promise<{ message: string; organization_id: string; new_owner_id: string }> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/organizations/${orgId}/transfer-ownership`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ new_owner_id: newOwnerId }),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to transfer ownership')
  }
  
  return response.json()
}

export async function leaveOrganization(orgId: string): Promise<void> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/organizations/${orgId}/leave`, {
    method: 'POST',
    headers,
  })
  
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/user/export-data`, { headers })
  
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/user/account`, {
    method: 'DELETE',
    headers,
  })
  
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/user/account/restore`, {
    method: 'POST',
    headers,
  })
  
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/user/deletion-status`, { headers })
  
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
  const headers = await getAuthHeader()
  
  const params = new URLSearchParams()
  params.append('q', query)
  if (options?.type) params.append('type', options.type)
  if (options?.projectId) params.append('project_id', options.projectId)
  if (options?.status) params.append('status', options.status)
  if (options?.limit) params.append('limit', options.limit.toString())
  
  const response = await fetch(`${API_URL}/search?${params.toString()}`, { headers })
  
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/search/suggestions?q=${encodeURIComponent(query)}`, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to get suggestions')
  }
  
  return response.json()
}

export async function getTrashItems(type?: 'content' | 'project' | 'asset'): Promise<TrashItem[]> {
  const headers = await getAuthHeader()
  
  let url = `${API_URL}/trash`
  if (type) url += `?item_type=${type}`
  
  const response = await fetch(url, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch trash')
  }
  
  return response.json()
}

export async function getTrashStats(): Promise<TrashStats> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/trash/stats`, { headers })
  
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/trash/${itemId}/restore`, {
    method: 'POST',
    headers,
  })
  
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/trash/${itemId}`, {
    method: 'DELETE',
    headers,
  })
  
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/trash/empty`, {
    method: 'POST',
    headers,
  })
  
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
  const headers = await getAuthHeader()

  const response = await fetch(`${API_URL}/ai-suggestions/rewrite`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ content, tone, style }),
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
  const headers = await getAuthHeader()

  const response = await fetch(`${API_URL}/ai-suggestions/expand`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ content, target_length: targetLength }),
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
  const headers = await getAuthHeader()

  const response = await fetch(`${API_URL}/ai-suggestions/condense`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ content, percentage }),
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
  const headers = await getAuthHeader()

  const response = await fetch(`${API_URL}/ai-suggestions/optimize`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ content, platform }),
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
  const headers = await getAuthHeader()

  const response = await fetch(`${API_URL}/content/${contentId}`, {
    method: 'PATCH',
    headers,
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/freshness/${contentId}/analyze`, {
    method: 'POST',
    headers,
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to analyze freshness')
  }
  
  return response.json()
}

export async function getStaleContent(): Promise<Content[]> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/freshness/stale`, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch stale content')
  }
  
  return response.json()
}

export async function getFreshnessMetrics(): Promise<FreshnessMetrics> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/freshness/metrics`, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch freshness metrics')
  }
  
  return response.json()
}

export async function bulkRefreshContent(contentIds?: string[]): Promise<{ refreshed: number }> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/freshness/bulk-refresh`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ content_ids: contentIds }),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to bulk refresh')
  }
  
  return response.json()
}

// ============ Trending Topics API ============

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

export async function getTrendingTopics(category?: string): Promise<Trend[]> {
  const headers = await getAuthHeader()
  
  let url = `${API_URL}/trends`
  if (category) {
    url += `?category=${category}`
  }
  
  const response = await fetch(url, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch trending topics')
  }
  
  return response.json()
}

export async function generateFromTrend(topicId: string): Promise<Content> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/trends/${topicId}/generate`, {
    method: 'POST',
    headers,
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to generate content from trend')
  }
  
  return response.json()
}

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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/rss/feeds`, {
    method: 'POST',
    headers,
    body: JSON.stringify(feed),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to add RSS feed')
  }
  
  return response.json()
}

export async function getRSSFeeds(): Promise<RSSFeed[]> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/rss/feeds`, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch RSS feeds')
  }
  
  return response.json()
}

export async function updateRSSFeed(id: string, updates: Partial<RSSFeedRequest>): Promise<RSSFeed> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/rss/feeds/${id}`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(updates),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update RSS feed')
  }
  
  return response.json()
}

export async function deleteRSSFeed(id: string): Promise<void> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/rss/feeds/${id}`, {
    method: 'DELETE',
    headers,
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to delete RSS feed')
  }
}

export async function fetchRSSFeed(id: string): Promise<{ message: string; entries_fetched: number }> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/rss/feeds/${id}/fetch`, {
    method: 'POST',
    headers,
  })
  
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
  const headers = await getAuthHeader()
  
  const params = new URLSearchParams()
  if (options?.feedId) params.append('feed_id', options.feedId)
  if (options?.processed !== undefined) params.append('processed', String(options.processed))
  if (options?.limit) params.append('limit', options.limit.toString())
  if (options?.offset) params.append('offset', options.offset.toString())
  if (options?.startDate) params.append('start_date', options.startDate)
  if (options?.endDate) params.append('end_date', options.endDate)
  
  const url = `${API_URL}/rss/entries}${params.toString() ? `?${params.toString()}` : ''}`
  const response = await fetch(url, { headers })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to fetch RSS entries')
  }
  
  return response.json()
}

export async function importRSSEntry(id: string, projectId?: string): Promise<Content> {
  const headers = await getAuthHeader()
  
  const body: { entry_id: string; project_id?: string } = { entry_id: id }
  if (projectId) body.project_id = projectId
  
  const response = await fetch(`${API_URL}/rss/entries/import`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to import RSS entry')
  }
  
  return response.json()
}

export async function bulkImportRSSEntries(entryIds: string[], projectId?: string): Promise<{ imported: number; failed: number; content_ids: string[] }> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/rss/entries/bulk-import`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ entry_ids: entryIds, project_id: projectId }),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to bulk import entries')
  }
  
  return response.json()
}

export async function getRSSStats(): Promise<RSSStats> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/rss/stats`, { headers })
  
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/rss/settings`, { headers })
  
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
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/rss/settings`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(settings),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to update RSS settings')
  }
  
  return response.json()
}

export async function markRSSEntryAsRead(id: string): Promise<void> {
  const headers = await getAuthHeader()
  
  const response = await fetch(`${API_URL}/rss/entries/${id}/read`, {
    method: 'POST',
    headers,
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to mark entry as read')
  }
}

// ============ End RSS Feed API ============
