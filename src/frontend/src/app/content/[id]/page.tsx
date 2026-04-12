'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getContent, generateAssets, listAssets, deleteContent, Content, GeneratedAsset, createDistribution, publishNow, getUsageSummary, UsageSummary } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/Card'
import { ArrowLeft, Loader2, Sparkles, Trash2, RefreshCw, Share2, Send, AlertCircle } from 'lucide-react'
import { useToast } from '@/hooks/useToast'

export default function ContentDetailPage({ params }: { params: { id: string } }) {
  const [content, setContent] = useState<Content | null>(null)
  const [assets, setAssets] = useState<GeneratedAsset[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const [usage, setUsage] = useState<UsageSummary | null>(null)
  const router = useRouter()
  const { showToast } = useToast()

  useEffect(() => {
    loadContent()
  }, [params.id])

  async function loadContent() {
    try {
      const [contentData, assetsData, usageData] = await Promise.all([
        getContent(params.id),
        listAssets(params.id),
        getUsageSummary(),
      ])
      setContent(contentData)
      setAssets(assetsData)
      setUsage(usageData)
    } catch (err: any) {
      setError(err.message || 'Failed to load content')
    } finally {
      setLoading(false)
    }
  }

  async function handleGenerate() {
    // Check if limit is reached
    if (usage?.status === 'limit_reached') {
      setError('Monthly usage limit reached. Please upgrade your plan to continue.')
      showToast('Monthly usage limit reached', 'error')
      return
    }

    setGenerating(true)
    try {
      const newAssets = await generateAssets(params.id)
      setAssets(newAssets)
      
      // Update usage after generating
      const updatedUsage = await getUsageSummary()
      setUsage(updatedUsage)
      
      showToast('Assets generated successfully!', 'success')
    } catch (err: any) {
      if (err.message?.includes('limit exceeded') || err.message?.includes('429')) {
        setError('Monthly usage limit reached. Please upgrade your plan to continue.')
        showToast('Monthly usage limit reached', 'error')
      } else {
        setError(err.message || 'Failed to generate assets')
        showToast('Failed to generate assets', 'error')
      }
    } finally {
      setGenerating(false)
    }
  }

  async function handleDelete() {
    if (!confirm('Are you sure you want to delete this content?')) return
    try {
      await deleteContent(params.id)
      showToast('Content deleted successfully!', 'success')
      router.push('/dashboard')
    } catch (err: any) {
      setError(err.message || 'Failed to delete content')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    )
  }

  if (!content) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Content not found</p>
          <Button onClick={() => router.push('/')} className="mt-4">
            Go Home
          </Button>
        </div>
      </div>
    )
  }

  const isLimitReached = usage?.status === 'limit_reached'
  const isApproachingLimit = !isLimitReached && usage && usage.stats.remaining !== -1 && usage.stats.remaining <= 3

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => router.back()}
                className="mr-4 p-2 hover:bg-gray-100 rounded-lg"
              >
                <ArrowLeft className="h-5 w-5" />
              </button>
              <div>
                <h1 className="text-xl font-bold">{content.title}</h1>
                <p className="text-sm text-gray-500 capitalize">{content.source_type}</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                onClick={handleDelete}
                className="flex items-center gap-2 text-red-600 hover:bg-red-50"
              >
                <Trash2 className="h-4 w-4" />
                Delete
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Usage Warning */}
        {isLimitReached && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-red-800">Monthly Limit Reached</p>
                <p className="text-sm text-red-600 mt-1">
                  You've used all {usage?.stats.monthly_usage_limit} content generations this month.
                  Upgrade your plan to generate more assets.
                </p>
                <button
                  onClick={() => router.push('/dashboard?upgrade=true')}
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

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Original Content */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Original Content</CardTitle>
              </CardHeader>
              <CardContent>
                {content.original_text ? (
                  <div className="space-y-4">
                    <div className="text-sm text-gray-600">
                      <span className="font-medium">Word count:</span> {content.word_count || 0}
                    </div>
                    <div className="max-h-96 overflow-y-auto">
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">
                        {content.original_text.substring(0, 1000)}
                        {content.original_text.length > 1000 && '...'}
                      </p>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No text extracted yet</p>
                )}

                <Button
                  onClick={handleGenerate}
                  disabled={generating || !content.original_text || isLimitReached}
                  className="w-full mt-6 flex items-center justify-center gap-2"
                  title={isLimitReached ? 'Monthly usage limit reached' : ''}
                >
                  {generating ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : isLimitReached ? (
                    <>
                      <AlertCircle className="h-4 w-4" />
                      Limit Reached
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4" />
                      Generate Assets
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Generated Assets */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold">Generated Assets</h2>
              <Button
                variant="outline"
                size="sm"
                onClick={loadContent}
                className="flex items-center gap-2"
              >
                <RefreshCw className="h-4 w-4" />
                Refresh
              </Button>
            </div>

            {assets.length === 0 ? (
              <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
                <Sparkles className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-4 text-lg font-medium text-gray-900">No assets yet</h3>
                <p className="mt-2 text-gray-500 max-w-sm mx-auto">
                  Click "Generate Assets" to transform your content into multiple formats.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {assets.map((asset) => (
                  <AssetCard key={asset.id} asset={asset} />
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

function AssetCard({ asset, onCopy, onPublish }: { asset: GeneratedAsset; onCopy?: () => void; onPublish?: () => void }) {
  const [copied, setCopied] = useState(false)
  const [publishing, setPublishing] = useState(false)
  const [publishError, setPublishError] = useState('')
  const [published, setPublished] = useState(false)
  const { showToast } = useToast()

  const typeLabels: Record<string, string> = {
    'thread': 'Twitter Thread',
    'social_post': 'Social Post',
    'newsletter': 'Newsletter',
    'video_script': 'Video Script',
    'blog_post': 'Blog Post',
  }

  const platformColors: Record<string, string> = {
    'twitter': 'bg-sky-100 text-sky-700',
    'linkedin': 'bg-blue-100 text-blue-700',
    'instagram': 'bg-pink-100 text-pink-700',
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
      // Create distribution first
      const distribution = await createDistribution({
        asset_id: asset.id,
        platform: asset.platform,
      })
      
      // Then publish immediately
      await publishNow(distribution.id)
      
      setPublished(true)
      showToast('Published successfully!', 'success')
    } catch (err: any) {
      setPublishError(err.message || 'Failed to publish')
      showToast('Failed to publish', 'error')
    } finally {
      setPublishing(false)
    }
  }

  return (
    <Card className="overflow-hidden">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="font-medium">{typeLabels[asset.type] || asset.type}</span>
            {asset.platform && (
              <span className={`text-xs px-2 py-1 rounded-full ${platformColors[asset.platform] || 'bg-gray-100 text-gray-700'}`}>
                {platformDisplayNames[asset.platform] || asset.platform}
              </span>
            )}
            {published && (
              <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-700">
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
          <p className="text-xs text-red-600 mt-2">{publishError}</p>
        )}
      </CardHeader>
      <CardContent>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-700 whitespace-pre-wrap">{asset.content}</p>
        </div>
      </CardContent>
    </Card>
  )
}
