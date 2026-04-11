'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { getProject, Project } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { useToast } from '@/hooks/useToast'
import { 
  ArrowLeft, 
  Folder, 
  Calendar,
  Loader2
} from 'lucide-react'

export default function ProjectDetailPage() {
  const params = useParams()
  const router = useRouter()
  const { showToast } = useToast()
  const [project, setProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(true)

  const projectId = params.id as string

  useEffect(() => {
    loadProject()
  }, [projectId])

  const loadProject = async () => {
    try {
      setLoading(true)
      const data = await getProject(projectId)
      setProject(data)
    } catch (error) {
      console.error('Failed to load project:', error)
      showToast('Failed to load project', 'error')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="flex items-center">
          <Loader2 className="h-8 w-8 text-blue-600 animate-spin" />
          <span className="ml-3 text-gray-600">Loading project...</span>
        </div>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Project not found</h1>
          <Button onClick={() => router.push('/dashboard')}>
            Go to Dashboard
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
          <div className="flex items-center h-16">
            <button
              onClick={() => router.push('/dashboard')}
              className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeft className="h-5 w-5 mr-2" />
              Back to Dashboard
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Project Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4">
            <div className="h-16 w-16 rounded-xl bg-blue-100 flex items-center justify-center">
              <Folder className="h-8 w-8 text-blue-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
              {project.description && (
                <p className="mt-1 text-gray-500">{project.description}</p>
              )}
            </div>
          </div>
        </div>

        {/* Project Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <Calendar className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500">Created</p>
                  <p className="font-medium text-gray-900">{formatDate(project.created_at)}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <Calendar className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500">Last Updated</p>
                  <p className="font-medium text-gray-900">{formatDate(project.updated_at)}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <div className={`h-5 w-5 rounded-full ${project.is_active ? 'bg-green-500' : 'bg-gray-400'}`} />
                <div>
                  <p className="text-sm text-gray-500">Status</p>
                  <p className="font-medium text-gray-900">{project.is_active ? 'Active' : 'Inactive'}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Content Section */}
        <div className="mt-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Content</h2>
          <Card>
            <CardContent className="p-12 text-center">
              <p className="text-gray-500">No content in this project yet.</p>
              <Button 
                className="mt-4"
                onClick={() => router.push('/content/new')}
              >
                Add Content
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
