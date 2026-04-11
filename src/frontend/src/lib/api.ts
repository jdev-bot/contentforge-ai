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
  brand_voice?: Record<string, any>
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
