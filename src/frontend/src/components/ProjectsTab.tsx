'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { listProjects, deleteProject, Project } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { NoDataState } from '@/components/ui/EmptyState'
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
import { PageHeader } from '@/components/ui/PageHeader'

export default function ProjectsTab() {
  const router = useRouter()
  const { showToast } = useToast()
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [showMenu, setShowMenu] = useState<string | null>(null)
  const [confirmDelete, setConfirmDelete] = useState<{ id: string; name: string } | null>(null)

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
    setConfirmDelete({ id: projectId, name: projectName })
  }

  const confirmDeleteProject = async () => {
    if (!confirmDelete) return
    const { id: projectId, name: projectName } = confirmDelete
    setConfirmDelete(null)

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
            <div key={i} className="bg-slate-50 dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
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
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Projects</h2>
          <Button 
            className="flex items-center gap-2"
            onClick={() => router.push('/projects/new')}
          >
            <Plus className="h-4 w-4" />
            New Project
          </Button>
        </div>
        
        <NoDataState
          title="No projects yet"
          description="Create your first project to organize your content."
          onCreate={() => router.push('/projects/new')}
          createLabel="Create Project"
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Projects"
        description="Organize and manage your content creation projects"
        icon={<Folder className="w-5 h-5 text-blue-600" />}
        actions={
          <Button
            className="flex items-center gap-2"
            onClick={() => router.push('/projects/new')}
          >
            <Plus className="h-4 w-4" />
            New Project
          </Button>
        }
      />

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
                      <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 truncate">
                        {project.name}
                      </h3>
                    </div>
                  </div>
                  
                  {project.description && (
                    <p className="mt-3 text-sm text-slate-500 dark:text-slate-400 line-clamp-2">
                      {project.description}
                    </p>
                  )}

                  <div className="mt-4 flex items-center text-sm text-slate-400 dark:text-slate-500">
                    <Calendar className="h-4 w-4 mr-1" />
                    Created {formatDate(project.created_at)}
                  </div>
                </div>

                <div className="relative" onClick={(e) => e.stopPropagation()}>
                  <button
                    className="p-2 text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:text-slate-400 rounded-full hover:bg-slate-100 dark:bg-slate-800 transition-colors"
                    onClick={(e) => {
                      e.preventDefault()
                      setShowMenu(showMenu === project.id ? null : project.id)
                    }}
                  >
                    <MoreVertical className="h-4 w-4" />
                  </button>

                  {showMenu === project.id && (
                    <div className="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 py-1 z-10">
                      <button
                        className="w-full flex items-center gap-2 px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:bg-slate-900"
                        onClick={() => {
                          router.push(`/projects/${project.id}`)
                          setShowMenu(null)
                        }}
                      >
                        <ExternalLink className="h-4 w-4" />
                        View Details
                      </button>
                      <button
                        className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-500 dark:text-red-400 hover:bg-red-500/10 dark:hover:bg-red-500/20"
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

      {/* Delete Confirmation Dialog */}
      {confirmDelete && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setConfirmDelete(null)}>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md mx-4 shadow-xl" onClick={e => e.stopPropagation()}>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">Delete Project?</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Are you sure you want to delete &quot;{confirmDelete.name}&quot;? This action cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                onClick={() => setConfirmDelete(null)}
              >
                Cancel
              </button>
              <button
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 transition-colors"
                onClick={confirmDeleteProject}
                disabled={!!deletingId}
              >
                {deletingId ? 'Deleting...' : 'Yes, Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
