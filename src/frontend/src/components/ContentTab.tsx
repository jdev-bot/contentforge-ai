'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { listContent, deleteContent, Content, listAssets, GeneratedAsset } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { NoDataState } from '@/components/ui/EmptyState'
import { useToast } from '@/hooks/useToast'
import ScheduleModal from './ScheduleModal'
import {
  Plus,
  FileText,
  Trash2,
  ExternalLink,
  MoreVertical,
  Loader2,
  Calendar,
  Clock,
} from 'lucide-react'

interface ContentTabProps {
  router?: ReturnType<typeof import('next/navigation').useRouter>
}

export default function ContentTab({ router: routerProp }: ContentTabProps) {
  const nextRouter = useRouter()
  const router = routerProp || nextRouter
  const { showToast } = useToast()
  const [content, setContent] = useState<Content[]>([])
  const [loading, setLoading] = useState(true)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [showMenu, setShowMenu] = useState<string | null>(null)
  const [assets, setAssets] = useState<Record<string, GeneratedAsset[]>>({})

  // Schedule modal state
  const [showScheduleModal, setShowScheduleModal] = useState(false)
  const [selectedAsset, setSelectedAsset] = useState<GeneratedAsset | null>(null)
  const [selectedContentTitle, setSelectedContentTitle] = useState('')

  const loadContent = useCallback(async () => {
    try {
      setLoading(true)
      const data = await listContent()
      setContent(data)

      // Load assets for each content item
      const assetsMap: Record<string, GeneratedAsset[]> = {}
      for (const item of data) {
        try {
          const itemAssets = await listAssets(item.id)
          assetsMap[item.id] = itemAssets.filter(a => a.status === 'generated' || a.status === 'approved')
        } catch {
          // Skip if error
        }
      }
      setAssets(assetsMap)
    } catch (error) {
      console.error('Failed to load content:', error)
      showToast('Failed to load content', 'error')
    } finally {
      setLoading(false)
    }
  }, [showToast])

  useEffect(() => {
    loadContent()
  }, [loadContent])

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = () => setShowMenu(null)
    if (showMenu) {
      document.addEventListener('click', handleClickOutside)
      return () => document.removeEventListener('click', handleClickOutside)
    }
  }, [showMenu])

  const handleDelete = useCallback(async (contentId: string, title: string) => {
    if (!confirm(`Are you sure you want to delete "${title}"? This action cannot be undone.`)) {
      setShowMenu(null)
      return
    }

    try {
      setDeletingId(contentId)
      await deleteContent(contentId)
      setContent(prev => prev.filter(c => c.id !== contentId))
      showToast(`Content deleted successfully`, 'success')
    } catch (error) {
      console.error('Failed to delete content:', error)
      showToast('Failed to delete content', 'error')
    } finally {
      setDeletingId(null)
      setShowMenu(null)
    }
  }, [])

  const handleSchedule = useCallback((e: React.MouseEvent, contentItem: Content) => {
    e.stopPropagation()
    const contentAssets = assets[contentItem.id] || []
    if (contentAssets.length === 0) {
      showToast('No generated assets available for scheduling', 'error')
      return
    }

    // Use the first available asset
    setSelectedAsset(contentAssets[0])
    setSelectedContentTitle(contentItem.title)
    setShowScheduleModal(true)
    setShowMenu(null)
  }, [assets, showToast])

  const formatDate = useCallback((dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }, [])

  const getStatusColor = useCallback((status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-700',
      processing: 'bg-blue-100 text-blue-700',
      completed: 'bg-green-100 text-green-700',
      failed: 'bg-red-100 text-red-700',
    }
    return colors[status] || 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300'
  }, [])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <Skeleton className="h-8 w-32" />
          <Skeleton className="h-10 w-32" />
        </div>

        <div className="space-y-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-slate-50 dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
              <div className="flex items-start gap-3">
                <Skeleton className="h-10 w-10 rounded-lg" />
                <div className="flex-1">
                  <Skeleton className="h-5 w-3/4 mb-2" />
                  <Skeleton className="h-4 w-full mb-3" />
                  <div className="flex items-center gap-4">
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-4 w-20" />
                  </div>
                </div>
                <Skeleton className="h-8 w-8 rounded-full" />
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (content.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Your Content</h2>
          <Button
            className="flex items-center gap-2"
            onClick={() => router.push('/content/new')}
          >
            <Plus className="h-4 w-4" />
            New Content
          </Button>
        </div>

        <NoDataState
          title="No content yet"
          description="Get started by adding your first piece of content. We'll transform it into multiple formats."
          onCreate={() => router.push('/content/new')}
          createLabel="Add Content"
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Your Content</h2>
        <Button
          className="flex items-center gap-2"
          onClick={() => router.push('/content/new')}
        >
          <Plus className="h-4 w-4" />
          New Content
        </Button>
      </div>

      <div className="space-y-4">
        {content.map((item) => (
          <Card
            key={item.id}
            className="group cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => router.push(`/content/${item.id}`)}
          >
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3 flex-1 min-w-0">
                  <div className="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                    <FileText className="h-5 w-5 text-blue-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 truncate">
                        {item.title}
                      </h3>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${getStatusColor(item.status)}`}>
                        {item.status}
                      </span>
                    </div>

                    {item.original_text && (
                      <p className="mt-2 text-sm text-slate-500 dark:text-slate-400 line-clamp-2">
                        {item.original_text.substring(0, 150)}...
                      </p>
                    )}

                    <div className="mt-3 flex items-center gap-4 text-sm text-slate-400 dark:text-slate-500 flex-wrap">
                      <span className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        {formatDate(item.created_at)}
                      </span>
                      <span className="capitalize">{item.source_type}</span>
                      {item.word_count && (
                        <span>{item.word_count} words</span>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="relative" onClick={(e) => e.stopPropagation()}>
                  <button
                    className="p-2 text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:text-slate-400 rounded-full hover:bg-slate-100 dark:bg-slate-800 transition-colors"
                    onClick={(e) => {
                      e.preventDefault()
                      setShowMenu(showMenu === item.id ? null : item.id)
                    }}
                  >
                    <MoreVertical className="h-4 w-4" />
                  </button>

                  {showMenu === item.id && (
                    <div className="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 py-1 z-10">
                      <button
                        className="w-full flex items-center gap-2 px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:bg-slate-900"
                        onClick={() => {
                          router.push(`/content/${item.id}`)
                          setShowMenu(null)
                        }}
                      >
                        <ExternalLink className="h-4 w-4" />
                        View Details
                      </button>
                      {(assets[item.id]?.length || 0) > 0 && (
                        <button
                          className="w-full flex items-center gap-2 px-4 py-2 text-sm text-violet-600 hover:bg-violet-50"
                          onClick={(e) => handleSchedule(e, item)}
                        >
                          <Clock className="h-4 w-4" />
                          Schedule
                        </button>
                      )}
                      <button
                        className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                        onClick={() => handleDelete(item.id, item.title)}
                        disabled={deletingId === item.id}
                      >
                        {deletingId === item.id ? (
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
                
                <ScheduleModal
                  isOpen={showScheduleModal}
                  onClose={() => {
                    setShowScheduleModal(false)
                    setSelectedAsset(null)
                  }}
                  asset={selectedAsset || undefined}
                  contentTitle={selectedContentTitle}
                  onSuccess={() => {
                    showToast('Post scheduled successfully', 'success')
                  }}
                />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
