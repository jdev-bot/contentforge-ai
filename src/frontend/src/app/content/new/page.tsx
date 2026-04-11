'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/Card'
import { ArrowLeft, Link, FileText, Video, Upload, Loader2 } from 'lucide-react'
import { createContent, listProjects, ContentCreate } from '@/lib/api'
import { useToast } from '@/hooks/useToast'

export default function NewContentPage() {
  const [sourceType, setSourceType] = useState('url')
  const [url, setUrl] = useState('')
  const [title, setTitle] = useState('')
  const [text, setText] = useState('')
  const [projectId, setProjectId] = useState('')
  const [projects, setProjects] = useState<Array<{ id: string; name: string }>>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()
  const { showToast } = useToast()

  const sourceTypes = [
    { id: 'url', name: 'Website URL', icon: Link, description: 'Extract from blog post or article' },
    { id: 'youtube', name: 'YouTube Video', icon: Video, description: 'Extract transcript from video' },
    { id: 'text', name: 'Paste Text', icon: FileText, description: 'Copy and paste your content' },
    { id: 'upload', name: 'Upload File', icon: Upload, description: 'Audio or video file' },
  ]

  // Load projects on mount
  useEffect(() => {
    async function loadProjects() {
      try {
        const projects = await listProjects()
        setProjects(projects.filter(p => p.is_active).map(p => ({ id: p.id, name: p.name })))
        if (projects.length > 0) {
          setProjectId(projects[0].id)
        }
      } catch (e) {
        console.error('Failed to load projects:', e)
      }
    }
    loadProjects()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
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
      
      // Redirect to content view page
      router.push(`/content/${content.id}`)
    } catch (err: any) {
      setError(err.message || 'Failed to create content')
      showToast('Failed to create content', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16">
            <button
              onClick={() => router.back()}
              className="mr-4 p-2 hover:bg-gray-100 rounded-lg"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <span className="text-xl font-bold">New Content</span>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card>
          <CardHeader>
            <CardTitle>Add Your Content</CardTitle>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Project Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Project
                </label>
                <select
                  value={projectId}
                  onChange={(e) => setProjectId(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Content Source
                </label>
                
                <div className="grid grid-cols-2 gap-4">
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
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
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
                <label htmlFor="title" className="block text-sm font-medium text-gray-700">
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
                  <label htmlFor="url" className="block text-sm font-medium text-gray-700">
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
                  <label htmlFor="content" className="block text-sm font-medium text-gray-700">
                    Paste Your Content
                  </label>
                  
                  <textarea
                    id="content"
                    rows={10}
                    placeholder="Paste your blog post, article, or any text here..."
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
              )}

              {/* File Upload (for upload) */}
              {sourceType === 'upload' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Upload Audio or Video
                  </label>
                  
                  <div className="mt-1 border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 cursor-pointer">
                    <Upload className="mx-auto h-12 w-12 text-gray-400" />
                    <p className="mt-2 text-sm text-gray-600">Upload coming soon</p>
                    <p className="text-xs text-gray-500">Use URL or text input for now</p>
                  </div>
                </div>
              )}

              {/* Error Message */}
              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}

              {/* Submit Button */}
              <div className="flex justify-end gap-4 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.back()}
                  disabled={loading}
                >
                  Cancel
                </Button>
                
                <Button
                  type="submit"
                  disabled={loading || !projectId}
                  className="flex items-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    'Add Content'
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
