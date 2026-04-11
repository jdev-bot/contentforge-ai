'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { listProjects, deleteProject, Project } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { useToast } from '@/hooks/useToast'
import { 
  Plus, 
  Folder, 
  Trash2, 
  ExternalLink, 
  Calendar,
  MoreVertical,
  Loader2
} from 'lucide-react'

export default function ProjectsTab() {
  const router = useRouter()
  const { showToast } = useToast()
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [showMenu, setShowMenu] = useState<string | null>(null)

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      setLoading(true)
      const data = await listProjects()
      setProjects(data)
    } catch (error) {
      console.error('Failed to load projects:', error)
      showToast('Failed to load projects', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (projectId: string, projectName: string) => {
    if (!confirm(`Are you sure you want to delete "${projectName}"? This action cannot be undone.`)) {
      setShowMenu(null)
      return
    }

    try {
      setDeletingId(projectId)
      await deleteProject(projectId)
      setProjects(projects.filter(p => p.id !== projectId))
      showToast(`Project "${projectName}" deleted successfully`, 'success')
    } catch (error) {
      console.error('Failed to delete project:', error)
      showToast('Failed to delete project', 'error')
    } finally {
      setDeletingId(null)
      setShowMenu(null)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = () => setShowMenu(null)
    if (showMenu) {
      document.addEventListener('click', handleClickOutside)
      return () => document.removeEventListener('click', handleClickOutside)
    }
  }, [showMenu])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <Skeleton className="h-8 w-32" />
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-start gap-3">
                <Skeleton className="h-10 w-10 rounded-lg" />
                <div className="flex-1">
                  <Skeleton className="h-5 w-3/4 mb-2" />
                  <Skeleton className="h-4 w-full mb-3" />
                  <Skeleton className="h-4 w-1/2" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (projects.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Projects</h2>
          <Button 
            className="flex items-center gap-2"
            onClick={() => router.push('/projects/new')}
          >
            <Plus className="h-4 w-4" />
            New Project
          </Button>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <div className="mx-auto h-12 w-12 text-gray-400">
            <Folder className="h-12 w-12" />
          </div>
          
          <h3 className="mt-4 text-lg font-medium text-gray-900">No projects yet</h3>
          <p className="mt-2 text-gray-500 max-w-sm mx-auto">
            Create your first project to organize your content.
          </p>
          
          <div className="mt-6">
            <Button 
              className="flex items-center gap-2 mx-auto"
              onClick={() => router.push('/projects/new')}
            >
              <Plus className="h-4 w-4" />
              Create Project
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Projects</h2>
        <Button 
          className="flex items-center gap-2"
          onClick={() => router.push('/projects/new')}
        >
          <Plus className="h-4 w-4" />
          New Project
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map((project) => (
          <Card 
            key={project.id} 
            className="group cursor-pointer hover:shadow-md transition-shadow relative"
            onClick={() => router.push(`/projects/${project.id}`)}
          >
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <div className="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                      <Folder className="h-5 w-5 text-blue-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-semibold text-gray-900 truncate">
                        {project.name}
                      </h3>
                    </div>
                  </div>
                  
                  {project.description && (
                    <p className="mt-3 text-sm text-gray-500 line-clamp-2">
                      {project.description}
                    </p>
                  )}

                  <div className="mt-4 flex items-center text-sm text-gray-400">
                    <Calendar className="h-4 w-4 mr-1" />
                    Created {formatDate(project.created_at)}
                  </div>
                </div>

                <div className="relative" onClick={(e) => e.stopPropagation()}>
                  <button
                    className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
                    onClick={(e) => {
                      e.preventDefault()
                      setShowMenu(showMenu === project.id ? null : project.id)
                    }}
                  >
                    <MoreVertical className="h-4 w-4" />
                  </button>

                  {showMenu === project.id && (
                    <div className="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-10">
                      <button
                        className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                        onClick={() => {
                          router.push(`/projects/${project.id}`)
                          setShowMenu(null)
                        }}
                      >
                        <ExternalLink className="h-4 w-4" />
                        View Details
                      </button>
                      <button
                        className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                        onClick={() => handleDelete(project.id, project.name)}
                        disabled={deletingId === project.id}
                      >
                        {deletingId === project.id ? (
                          <>
                            <Loader2 className="h-4 w-4 animate-spin" />
                            Deleting...
                          </>
                        ) : (
                          <>
                            <Trash2 className="h-4 w-4" />
                            Delete
                          </>
                        )}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
