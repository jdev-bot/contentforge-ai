'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getContent, generateAssets, listAssets, deleteContent, Content, GeneratedAsset } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/Card'
import { ArrowLeft, Loader2, Sparkles, Trash2, RefreshCw } from 'lucide-react'

export default function ContentDetailPage({ params }: { params: { id: string } }) {
  const [content, setContent] = useState<Content | null>(null)
  const [assets, setAssets] = useState<GeneratedAsset[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()

  useEffect(() => {
    loadContent()
  }, [params.id])

  async function loadContent() {
    try {
      const [contentData, assetsData] = await Promise.all([
        getContent(params.id),
        listAssets(params.id),
      ])
      setContent(contentData)
      setAssets(assetsData)
    } catch (err: any) {
      setError(err.message || 'Failed to load content')
    } finally {
      setLoading(false)
    }
  }

  async function handleGenerate() {
    setGenerating(true)
    try {
      const newAssets = await generateAssets(params.id)
      setAssets(newAssets)
    } catch (err: any) {
      setError(err.message || 'Failed to generate assets')
    } finally {
      setGenerating(false)
    }
  }

  async function handleDelete() {
    if (!confirm('Are you sure you want to delete this content?')) return
    try {
      await deleteContent(params.id)
      router.push('/')
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
                  disabled={generating || !content.original_text}
                  className="w-full mt-6 flex items-center justify-center gap-2"
                >
                  {generating ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Generating...
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

function AssetCard({ asset }: { asset: GeneratedAsset }) {
  const [copied, setCopied] = useState(false)

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

  async function handleCopy() {
    await navigator.clipboard.writeText(asset.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <Card className="overflow-hidden">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="font-medium">{typeLabels[asset.type] || asset.type}</span>
            {asset.platform && (
              <span className={`text-xs px-2 py-1 rounded-full ${platformColors[asset.platform] || 'bg-gray-100 text-gray-700'}`}>
                {asset.platform}
              </span>
            )}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleCopy}
          >
            {copied ? 'Copied!' : 'Copy'}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-700 whitespace-pre-wrap">{asset.content}</p>
        </div>
      </CardContent>
    </Card>
  )
}
