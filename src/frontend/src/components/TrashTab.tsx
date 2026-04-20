'use client'

import { useState, useEffect } from 'react'
import { TrashItem, TrashStats, getTrashItems, getTrashStats, restoreFromTrash, permanentlyDeleteFromTrash, emptyTrash } from '@/lib/api'
import { useToast } from '@/hooks/useToast'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { 
  Trash2, 
  RotateCcw, 
  AlertTriangle, 
  FileText, 
  FolderOpen,
  Clock,
  X,
  AlertCircle,
  RefreshCw
} from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'

interface TrashTabProps {
  onItemRestored?: () => void
}

export default function TrashTab({ onItemRestored }: TrashTabProps) {
  const { showToast } = useToast()
  const [items, setItems] = useState<TrashItem[]>([])
  const [stats, setStats] = useState<TrashStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedType, setSelectedType] = useState<'content' | 'project' | 'all'>('all')
  const [restoring, setRestoring] = useState<string | null>(null)
  const [deleting, setDeleting] = useState<string | null>(null)
  const [showEmptyConfirm, setShowEmptyConfirm] = useState(false)

  useEffect(() => {
    loadTrash()
  }, [selectedType])

  const loadTrash = async () => {
    try {
      setLoading(true)
      const [itemsData, statsData] = await Promise.all([
        getTrashItems(selectedType === 'all' ? undefined : selectedType),
        getTrashStats()
      ])
      setItems(itemsData)
      setStats(statsData)
    } catch (error) {
      console.error('Failed to load trash:', error)
      showToast('Failed to load trash', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleRestore = async (itemId: string) => {
    try {
      setRestoring(itemId)
      await restoreFromTrash(itemId)
      showToast('Item restored successfully', 'success')
      await loadTrash()
      onItemRestored?.()
    } catch (error) {
      console.error('Failed to restore:', error)
      showToast('Failed to restore item', 'error')
    } finally {
      setRestoring(null)
    }
  }

  const handlePermanentDelete = async (itemId: string) => {
    if (!confirm('Are you sure? This action cannot be undone.')) return

    try {
      setDeleting(itemId)
      await permanentlyDeleteFromTrash(itemId)
      showToast('Item permanently deleted', 'success')
      await loadTrash()
    } catch (error) {
      console.error('Failed to delete:', error)
      showToast('Failed to delete item', 'error')
    } finally {
      setDeleting(null)
    }
  }

  const handleEmptyTrash = async () => {
    try {
      const result = await emptyTrash()
      showToast(`Trash emptied. ${result.items_deleted} items deleted.`, 'success')
      await loadTrash()
      setShowEmptyConfirm(false)
    } catch (error) {
      console.error('Failed to empty trash:', error)
      showToast('Failed to empty trash', 'error')
    }
  }

  const getItemIcon = (type: string) => {
    switch (type) {
      case 'content':
        return <FileText className="h-5 w-5 text-blue-500" />
      case 'project':
        return <FolderOpen className="h-5 w-5 text-purple-500" />
      default:
        return <FileText className="h-5 w-5 text-slate-500 dark:text-slate-400" />
    }
  }

  const getItemTitle = (item: TrashItem) => {
    const data = item.original_data as { title?: string; name?: string }
    return data.title || data.name || 'Untitled'
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffDays = Math.ceil((date.getTime() - now.getTime()) / (1000 * 60 * 60 * 24) + (stats?.retention_days || 30))
    
    if (diffDays <= 0) return 'Expires soon'
    if (diffDays === 1) return 'Expires in 1 day'
    return `Expires in ${diffDays} days`
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-16 w-full" />
        <Skeleton className="h-16 w-full" />
        <Skeleton className="h-16 w-full" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Trash"
        description={`Items are kept for ${stats?.retention_days || 30} days before permanent deletion`}
        icon={<Trash2 className="w-5 h-5 text-blue-600" />}
        actions={
          items.length > 0 ? (
            <Button
              variant="danger"
              size="sm"
              onClick={() => setShowEmptyConfirm(true)}
            >
              Empty Trash
            </Button>
          ) : undefined
        }
      />

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-3 gap-4">
          <Card className="border-slate-200 dark:border-slate-700">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-slate-100 dark:bg-slate-800 rounded-lg">
                  <Trash2 className="h-5 w-5 text-slate-600 dark:text-slate-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">{stats.total}</p>
                  <p className="text-sm text-slate-600 dark:text-slate-400">Total Items</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="border-slate-200 dark:border-slate-700">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-50 rounded-lg">
                  <FileText className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">{stats.content_count}</p>
                  <p className="text-sm text-slate-600 dark:text-slate-400">Content Items</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="border-slate-200 dark:border-slate-700">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-50 rounded-lg">
                  <FolderOpen className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">{stats.project_count}</p>
                  <p className="text-sm text-slate-600 dark:text-slate-400">Projects</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex gap-2">
        {(['all', 'content', 'project'] as const).map((type) => (
          <button
            key={type}
            onClick={() => setSelectedType(type)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedType === type
                ? 'bg-blue-100 text-blue-700'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:bg-slate-700'
            }`}
          >
            {type.charAt(0).toUpperCase() + type.slice(1)}
          </button>
        ))}
      </div>

      {/* Empty State */}
      {items.length === 0 && (
        <Card className="border-dashed border-slate-300 dark:border-slate-600">
          <CardContent className="p-12 text-center">
            <div className="mx-auto w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mb-4">
              <Trash2 className="h-8 w-8 text-slate-400 dark:text-slate-500" />
            </div>
            <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-1">Trash is empty</h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Deleted items will appear here for {stats?.retention_days || 30} days
            </p>
          </CardContent>
        </Card>
      )}

      {/* Items List */}
      {items.length > 0 && (
        <div className="space-y-2">
          {items.map((item) => (
            <Card key={item.id} className="border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:border-slate-600 transition-colors">
              <CardContent className="p-4">
                <div className="flex items-center gap-4">
                  {/* Icon */}
                  <div className="flex-shrink-0">
                    {getItemIcon(item.type)}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-slate-900 dark:text-slate-100 truncate">
                      {getItemTitle(item)}
                    </h4>
                    <div className="flex items-center gap-4 text-sm text-slate-500 dark:text-slate-400 mt-1">
                      <span className="capitalize">{item.type}</span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatDate(item.deleted_at)}
                      </span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleRestore(item.id)}
                      disabled={restoring === item.id}
                      className="flex items-center gap-1"
                    >
                      {restoring === item.id ? (
                        <RefreshCw className="h-4 w-4 animate-spin" />
                      ) : (
                        <RotateCcw className="h-4 w-4" />
                      )}
                      Restore
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handlePermanentDelete(item.id)}
                      disabled={deleting === item.id}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      {deleting === item.id ? (
                        <RefreshCw className="h-4 w-4 animate-spin" />
                      ) : (
                        <X className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Empty Trash Confirmation Modal */}
      {showEmptyConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md mx-4">
            <CardContent className="p-6">
              <div className="flex items-start gap-4">
                <div className="p-2 bg-red-100 rounded-full flex-shrink-0">
                  <AlertTriangle className="h-6 w-6 text-red-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-1">
                    Empty Trash?
                  </h3>
                  <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
                    This will permanently delete all {stats?.total || items.length} items in your trash. 
                    This action cannot be undone.
                  </p>
                  <div className="flex gap-3">
                    <Button
                      variant="danger"
                      onClick={handleEmptyTrash}
                      className="flex-1"
                    >
                      Yes, Empty Trash
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => setShowEmptyConfirm(false)}
                      className="flex-1"
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
