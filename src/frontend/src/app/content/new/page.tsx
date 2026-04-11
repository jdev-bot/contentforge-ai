'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/Card'
import { ArrowLeft, Link, FileText, Youtube, Upload } from 'lucide-react'

export default function NewContentPage() {
  const [sourceType, setSourceType] = useState('url')
  const [url, setUrl] = useState('')
  const [title, setTitle] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const sourceTypes = [
    { id: 'url', name: 'Website URL', icon: Link, description: 'Extract from blog post or article' },
    { id: 'youtube', name: 'YouTube Video', icon: Youtube, description: 'Extract transcript from video' },
    { id: 'text', name: 'Paste Text', icon: FileText, description: 'Copy and paste your content' },
    { id: 'upload', name: 'Upload File', icon: Upload, description: 'Audio or video file' },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    // TODO: Connect to backend API
    console.log('Creating content:', { sourceType, url, title })

    setTimeout(() => {
      setLoading(false)
      router.push('/')
    }, 2000)
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
                        className={`p-4 rounded-lg border-2 text-left transition-all ${
                          sourceType === type.id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
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
                    <p className="mt-2 text-sm text-gray-600">Click to upload or drag and drop</p>
                    <p className="text-xs text-gray-500">MP3, MP4, WAV up to 100MB</p>
                  </div>
                </div>
              )}

              {/* Submit Button */}
              <div className="flex justify-end gap-4 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.back()}
                >
                  Cancel
                </Button>
                
                <Button
                  type="submit"
                  disabled={loading}
                  className="flex items-center gap-2"
                >
                  {loading ? 'Processing...' : 'Add Content'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
