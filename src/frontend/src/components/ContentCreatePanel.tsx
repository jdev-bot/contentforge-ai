'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/Card'
import { ArrowLeft, Link, FileText, Video, Upload, Loader2, AlertCircle } from 'lucide-react'
import { createContent, listProjects, getUsageSummary, ContentCreate, UsageSummary } from '@/lib/api'
import { useToast } from '@/hooks/useToast'
import { AuthUser } from '@/lib/supabase'

interface ContentCreatePanelProps {
  user: AuthUser
  onBack: () => void
  onContentCreated: (id: string) => void
}

export default function ContentCreatePanel({ user, onBack, onContentCreated }: ContentCreatePanelProps) {
  const [sourceType, setSourceType] = useState('url')
  const [url, setUrl] = useState('')
  const [title, setTitle] = useState('')
  const [text, setText] = useState('')
  const [projectId, setProjectId] = useState('')
  const [projects, setProjects] = useState<Array<{ id: string; name: string }>>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [usage, setUsage] = useState<UsageSummary | null>(null)
  const [checkingUsage, setCheckingUsage] = useState(true)
  const { showToast } = useToast()

  const sourceTypes = [
    { id: 'url', name: 'Website URL', icon: Link, description: 'Extract from blog post or article' },
    { id: 'youtube', name: 'YouTube Video', icon: Video, description: 'Extract transcript from video' },
    { id: 'text', name: 'Paste Text', icon: FileText, description: 'Copy and paste your content' },
    { id: 'upload', name: 'Upload File', icon: Upload, description: 'Audio or video file' },
  ]

  // Load projects and usage on mount
  useEffect(() => {
    async function loadData() {
      try {
        setCheckingUsage(true)
        // Check usage first
        const usageData = await getUsageSummary()
        setUsage(usageData)

        // Then load projects
        const projects = await listProjects()
        setProjects(projects.filter(p => p.is_active).map(p => ({ id: p.id, name: p.name })))
        if (projects.length > 0) {
          setProjectId(projects[0].id)
        }
      } catch (e) {
        console.error('Failed to load data:', e)
      } finally {
        setCheckingUsage(false)
      }
    }
    loadData()
  }, [])

  const isLimitReached = usage?.status === 'limit_reached'
  const isApproachingLimit = !isLimitReached && usage && usage.stats.remaining !== -1 && usage.stats.remaining <= 3

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Check limit before submitting
    if (isLimitReached) {
      setError('Monthly usage limit reached. Please upgrade your plan to continue.')
      return
    }

    setLoading(true)
    setError('')

    try {
      if (!projectId) {
        throw new Error('Please select a project')
      }

      const contentData: ContentCreate = {
        title,
        project_id: projectId,
        source: {
          type: sourceType as 'url' | 'youtube' | 'text' | 'upload',
          url: sourceType === 'url' || sourceType === 'youtube' ? url : undefined,
          text: sourceType === 'text' ? text : undefined,
        },
      }

      const content = await createContent(contentData)
      showToast('Content created successfully!', 'success')
      
      // Navigate to content detail view inline
      onContentCreated(content.id)
    } catch (err: unknown) {
      // Check if error is due to limit exceeded
      const errorMessage = err instanceof Error ? err.message : 'Failed to create content'
      if (errorMessage.includes('limit exceeded') || errorMessage.includes('429')) {
        setError('Monthly usage limit reached. Please upgrade your plan to continue.')
      } else {
        setError(errorMessage)
      }
      showToast('Failed to create content', 'error')
    } finally {
      setLoading(false)
    }
  }

  if (checkingUsage) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="animate-spin h-8 w-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center mb-6">
        <button
          onClick={onBack}
          className="mr-4 p-2 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <span className="text-xl font-bold">New Content</span>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Add Your Content</CardTitle>
        </CardHeader>

        <CardContent>
          {/* Usage Warning */}
          {isLimitReached && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-red-800">Monthly Limit Reached</p>
                  <p className="text-sm text-red-600 mt-1">
                    You&apos;ve used all {usage?.stats.monthly_usage_limit} content generations this month.
                    Upgrade your plan to continue creating content.
                  </p>
                  <button
                    onClick={onBack}
                    className="mt-3 text-sm font-medium text-red-700 hover:text-red-800 underline"
                  >
                    Upgrade Plan →
                  </button>
                </div>
              </div>
            </div>
          )}

          {isApproachingLimit && (
            <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-yellow-500 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-yellow-800">Approaching Limit</p>
                  <p className="text-sm text-yellow-600 mt-1">
                    You have {usage?.stats.remaining} content generations remaining this month.
                  </p>
                </div>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Project Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Project
              </label>
              <select
                value={projectId}
                onChange={(e) => setProjectId(e.target.value)}
                className="w-full rounded-lg border border-gray-300 dark:border-slate-600 px-3 py-2 text-sm bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Select a project...</option>
                {projects.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.name}
                  </option>
                ))}
              </select>
              {projects.length === 0 && (
                <p className="text-sm text-amber-600 mt-1">
                  No projects found. Create one in the Projects tab first.
                </p>
              )}
            </div>

            {/* Source Type Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Content Source
              </label>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {sourceTypes.map((type) => {
                  const Icon = type.icon
                  return (
                    <button
                      key={type.id}
                      type="button"
                      onClick={() => setSourceType(type.id)}
                      disabled={type.id === 'upload'}
                      className={`p-4 rounded-lg border-2 text-left transition-all ${
                        sourceType === type.id
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-500/20'
                          : 'border-gray-200 dark:border-slate-700 hover:border-gray-300 dark:hover:border-slate-600'
                      } ${type.id === 'upload' ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                      <Icon className="h-6 w-6 mb-2" />
                      <p className="font-medium text-sm">{type.name}</p>
                      <p className="text-xs text-gray-500 mt-1">{type.description}</p>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Title Input */}
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Content Title
              </label>
              <Input
                id="title"
                type="text"
                placeholder="e.g., My Blog Post About AI"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                className="mt-1"
              />
            </div>

            {/* URL Input (for URL and YouTube) */}
            {(sourceType === 'url' || sourceType === 'youtube') && (
              <div>
                <label htmlFor="url" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  {sourceType === 'youtube' ? 'YouTube URL' : 'Website URL'}
                </label>
                
                <Input
                  id="url"
                  type="url"
                  placeholder={sourceType === 'youtube' 
                    ? 'https://youtube.com/watch?v=...' 
                    : 'https://example.com/blog-post'
                  }
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  required
                  className="mt-1"
                />
              </div>
            )}

            {/* Text Area (for text input) */}
            {sourceType === 'text' && (
              <div>
                <label htmlFor="content" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Paste Your Content
                </label>
                
                <textarea
                  id="content"
                  rows={10}
                  placeholder="Paste your blog post, article, or any text here..."
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-gray-300 dark:border-slate-600 px-3 py-2 text-sm bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
            )}

            {/* File Upload (for upload) */}
            {sourceType === 'upload' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Upload Audio or Video
                </label>
                
                <div className="mt-1 border-2 border-dashed border-gray-300 dark:border-slate-600 rounded-lg p-8 text-center hover:border-gray-400 cursor-pointer">
                  <Upload className="mx-auto h-12 w-12 text-gray-400" />
                  <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">Upload coming soon</p>
                  <p className="text-xs text-gray-500">Use URL or text input for now</p>
                </div>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
              </div>
            )}

            {/* Submit Button */}
            <div className="flex justify-end gap-4 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={onBack}
                disabled={loading}
              >
                Cancel
              </Button>
              
              <Button
                type="submit"
                disabled={loading || !projectId || isLimitReached}
                className="flex items-center gap-2"
                title={isLimitReached ? 'Monthly usage limit reached' : ''}
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Processing...
                  </>
                ) : isLimitReached ? (
                  <>
                    <AlertCircle className="h-4 w-4" />
                    Limit Reached
                  </>
                ) : (
                  'Add Content'
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}