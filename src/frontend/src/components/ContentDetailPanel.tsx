'use client'

import { useEffect, useState } from 'react'
import { 
  getContent, 
  generateAssets, 
  listAssets, 
  deleteContent, 
  updateContent,
  Content, 
  GeneratedAsset, 
  createDistribution, 
  publishNow, 
  getUsageSummary, 
  UsageSummary 
} from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/Card'
import { ArrowLeft, Loader2, Sparkles, Trash2, RefreshCw, Send, AlertCircle, Edit3 } from 'lucide-react'
import { useToast } from '@/hooks/useToast'
import { AuthUser } from '@/lib/supabase'
import dynamic from 'next/dynamic'

// Dynamic import for SmartEditor to avoid SSR issues
const SmartEditor = dynamic(() => import('@/components/SmartEditor'), {
  ssr: false,
  loading: () => (
    <div className="h-[500px] flex items-center justify-center">
      <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
    </div>
  ),
})

interface ContentDetailPanelProps {
  id: string
  user: AuthUser
  onBack: () => void
}

export default function ContentDetailPanel({ id, user, onBack }: ContentDetailPanelProps) {
  const [content, setContent] = useState<Content | null>(null)
  const [assets, setAssets] = useState<GeneratedAsset[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const [usage, setUsage] = useState<UsageSummary | null>(null)
  const [activeTab, setActiveTab] = useState<'editor' | 'assets'>('editor')
  const [editorContent, setEditorContent] = useState('')
  const { showToast } = useToast()

  useEffect(() => {
    loadContent()
  }, [id])

  async function loadContent() {
    try {
      const [contentData, assetsData, usageData] = await Promise.all([
        getContent(id),
        listAssets(id),
        getUsageSummary(),
      ])
      setContent(contentData)
      setAssets(assetsData)
      setUsage(usageData)
      setEditorContent(contentData.original_text || '')
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to load content'
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  async function handleGenerate() {
    if (usage?.status === 'limit_reached') {
      setError('Monthly usage limit reached. Please upgrade your plan to continue.')
      showToast('Monthly usage limit reached', 'error')
      return
    }

    setGenerating(true)
    try {
      const newAssets = await generateAssets(id)
      setAssets(newAssets)
      
      const updatedUsage = await getUsageSummary()
      setUsage(updatedUsage)
      
      showToast('Assets generated successfully!', 'success')
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to generate assets'
      if (errorMsg.includes('limit exceeded') || errorMsg.includes('429')) {
        setError('Monthly usage limit reached. Please upgrade your plan to continue.')
        showToast('Monthly usage limit reached', 'error')
      } else {
        setError(errorMsg)
        showToast('Failed to generate assets', 'error')
      }
    } finally {
      setGenerating(false)
    }
  }

  async function handleDelete() {
    if (!confirm('Are you sure you want to delete this content?')) return
    try {
      await deleteContent(id)
      showToast('Content deleted successfully!', 'success')
      onBack()
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to delete content'
      setError(errorMsg)
    }
  }

  async function handleSaveContent(newContent: string) {
    const updated = await updateContent(id, { original_text: newContent })
    setContent(updated)
    setEditorContent(newContent)
    
    const wordCount = newContent.trim().split(/\s+/).filter(Boolean).length
    setContent(prev => prev ? { ...prev, word_count: wordCount } : null)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    )
  }

  if (!content) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="text-center">
          <p className="text-slate-600 dark:text-slate-400">Content not found</p>
          <Button onClick={onBack} className="mt-4">
            Go Back
          </Button>
        </div>
      </div>
    )
  }

  const isLimitReached = usage?.status === 'limit_reached'
  const isApproachingLimit = !isLimitReached && usage && usage.stats.remaining !== -1 && usage.stats.remaining <= 3

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <button
            onClick={onBack}
            className="mr-4 p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100">{content.title}</h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 capitalize">{content.source_type}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Tab Switcher */}
          <div className="flex items-center bg-slate-100 dark:bg-slate-700 rounded-lg p-1 mr-2">
            <button
              onClick={() => setActiveTab('editor')}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                activeTab === 'editor'
                  ? 'bg-white dark:bg-slate-600 text-slate-900 dark:text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <span className="flex items-center gap-2">
                <Edit3 className="h-4 w-4" />
                Editor
              </span>
            </button>
            <button
              onClick={() => setActiveTab('assets')}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                activeTab === 'assets'
                  ? 'bg-white dark:bg-slate-600 text-slate-900 dark:text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <span className="flex items-center gap-2">
                <Sparkles className="h-4 w-4" />
                Assets ({assets.length})
              </span>
            </button>
          </div>

          <Button
            variant="outline"
            onClick={handleDelete}
            className="flex items-center gap-2 text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-900/20"
          >
            <Trash2 className="h-4 w-4" />
            Delete
          </Button>
        </div>
      </div>

      {/* Usage Warnings */}
      {isLimitReached && (
        <div className="mb-6 p-4 bg-rose-50 dark:bg-rose-900/20 border border-rose-200 dark:border-rose-800 rounded-xl">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-rose-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-rose-800 dark:text-rose-400">Monthly Limit Reached</p>
              <p className="text-sm text-rose-600 dark:text-rose-400 mt-1">
                You&apos;ve used all {usage?.stats.monthly_usage_limit} content generations this month.
                Upgrade your plan to generate more assets.
              </p>
            </div>
          </div>
        </div>
      )}

      {isApproachingLimit && (
        <div className="mb-6 p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-amber-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-amber-800 dark:text-amber-400">Approaching Limit</p>
              <p className="text-sm text-amber-600 dark:text-amber-400 mt-1">
                You have {usage?.stats.remaining} content generations remaining this month.
              </p>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="mb-6 p-4 bg-rose-50 dark:bg-rose-900/20 border border-rose-200 dark:border-rose-800 rounded-xl">
          <p className="text-sm text-rose-600 dark:text-rose-400">{error}</p>
        </div>
      )}

      {/* Editor Tab */}
      {activeTab === 'editor' && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Smart Editor - Main Area */}
          <div className="lg:col-span-3">
            <SmartEditor
              content={content.original_text || ''}
              contentId={content.id}
              onContentChange={setEditorContent}
              onSave={handleSaveContent}
            />
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-4">
            {/* Content Info */}
            <Card variant="glass">
              <CardHeader>
                <CardTitle className="text-sm">Content Info</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500 dark:text-slate-400">Status</span>
                  <span className="capitalize font-medium">{content.status}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500 dark:text-slate-400">Word Count</span>
                  <span className="font-medium">{content.word_count || 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500 dark:text-slate-400">Source</span>
                  <span className="capitalize font-medium">{content.source_type}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500 dark:text-slate-400">Created</span>
                  <span className="font-medium">
                    {new Date(content.created_at).toLocaleDateString()}
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card variant="glass">
              <CardHeader>
                <CardTitle className="text-sm">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button
                  onClick={handleGenerate}
                  disabled={generating || !content.original_text || isLimitReached}
                  className="w-full"
                  title={isLimitReached ? 'Monthly usage limit reached' : ''}
                >
                  {generating ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      Generating...
                    </>
                  ) : isLimitReached ? (
                    <>
                      <AlertCircle className="h-4 w-4 mr-2" />
                      Limit Reached
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4 mr-2" />
                      Generate Assets
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Assets Tab */}
      {activeTab === 'assets' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">Generated Assets</h2>
            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                size="sm"
                onClick={loadContent}
                className="flex items-center gap-2"
              >
                <RefreshCw className="h-4 w-4" />
                Refresh
              </Button>
              <Button
                onClick={handleGenerate}
                disabled={generating || !content.original_text || isLimitReached}
              >
                {generating ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 mr-2" />
                    Generate More
                  </>
                )}
              </Button>
            </div>
          </div>

          {assets.length === 0 ? (
            <div className="text-center py-12">
              <Sparkles className="h-12 w-12 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-2">No assets yet</h3>
              <p className="text-slate-500 dark:text-slate-400 mb-4">
                Generate AI-powered content assets from your source material.
              </p>
              <Button
                onClick={handleGenerate}
                disabled={generating || !content.original_text || isLimitReached}
              >
                {generating ? 'Generating...' : 'Generate Assets'}
              </Button>
            </div>
          ) : (
            <div className="grid gap-6">
              {assets.map((asset) => (
                <AssetCard key={asset.id} asset={asset} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// Inline AssetCard component
function AssetCard({ asset }: { asset: GeneratedAsset }) {
  const [copied, setCopied] = useState(false)
  const [publishing, setPublishing] = useState(false)
  const [published, setPublished] = useState(false)
  const [publishError, setPublishError] = useState('')
  const { showToast } = useToast()

  const typeLabels: Record<string, string> = {
    'thread': 'Twitter Thread',
    'social_post': 'Social Post',
    'newsletter': 'Newsletter',
    'video_script': 'Video Script',
    'blog_post': 'Blog Post',
  }

  const platformColors: Record<string, string> = {
    'twitter': 'bg-sky-100 text-sky-700 dark:bg-sky-900/30 dark:text-sky-400',
    'linkedin': 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
    'instagram': 'bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-400',
  }

  const platformDisplayNames: Record<string, string> = {
    'twitter': 'Twitter/X',
    'linkedin': 'LinkedIn',
    'instagram': 'Instagram',
  }

  async function handleCopy() {
    await navigator.clipboard.writeText(asset.content)
    setCopied(true)
    showToast('Content copied to clipboard!', 'success')
    setTimeout(() => setCopied(false), 2000)
  }

  async function handlePublish() {
    if (!asset.platform) return
    
    setPublishing(true)
    setPublishError('')
    
    try {
      const distribution = await createDistribution({
        asset_id: asset.id,
        platform: asset.platform,
      })
      
      await publishNow(distribution.id)
      
      setPublished(true)
      showToast('Published successfully!', 'success')
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to publish'
      setPublishError(errorMsg)
      showToast('Failed to publish', 'error')
    } finally {
      setPublishing(false)
    }
  }

  return (
    <Card className="overflow-hidden" variant="elevated">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-3 flex-wrap">
            <span className="font-medium text-slate-900 dark:text-slate-100">
              {typeLabels[asset.type] || asset.type}
            </span>
            {asset.platform && (
              <span className={`text-xs px-2 py-1 rounded-full ${platformColors[asset.platform] || 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300'}`}>
                {platformDisplayNames[asset.platform] || asset.platform}
              </span>
            )}
            {published && (
              <span className="text-xs px-2 py-1 rounded-full bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">
                Published
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCopy}
            >
              {copied ? 'Copied!' : 'Copy'}
            </Button>
            
            {asset.platform && !published && (
              <Button
                variant="outline"
                size="sm"
                onClick={handlePublish}
                disabled={publishing}
                className="flex items-center gap-1"
              >
                {publishing ? (
                  <>
                    <Loader2 className="h-3 w-3 animate-spin" />
                    Publishing...
                  </>
                ) : (
                  <>
                    <Send className="h-3 w-3" />
                    Publish Now
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
        
        {publishError && (
          <p className="text-xs text-rose-600 dark:text-rose-400 mt-2">{publishError}</p>
        )}
      </CardHeader>
      <CardContent>
        <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl p-4 max-h-64 overflow-y-auto">
          <p className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap">{asset.content}</p>
        </div>
      </CardContent>
    </Card>
  )
}