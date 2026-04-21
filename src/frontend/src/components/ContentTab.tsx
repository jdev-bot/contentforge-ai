'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { listContent, deleteContent, Content, listAssets, GeneratedAsset } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { EmptyState, NoDataState } from '@/components/ui/EmptyState'
import { useToast } from '@/hooks/useToast'
import { PageHeader } from '@/components/ui/PageHeader'
import { getStatusColor, getStatusDotColor, formatDate, cn } from '@/lib/utils'
import ScheduleModal from './ScheduleModal'
import {
  Plus,
  FileText,
  Trash2,
  ExternalLink,
  MoreVertical,
  Loader2,
  Calendar,
  Search,
  SlidersHorizontal,
  ArrowUpDown,
  LayoutGrid,
  List,
  X,
} from 'lucide-react'

type SortOption = 'newest' | 'oldest' | 'az'
type ViewMode = 'list' | 'grid'
type StatusFilter = 'pending' | 'processing' | 'completed' | 'failed'

interface ContentTabProps {
  onCreateContent?: () => void
  onViewContent?: (id: string) => void
}

const STATUS_FILTERS: { value: StatusFilter; label: string }[] = [
  { value: 'pending', label: 'Pending' },
  { value: 'processing', label: 'Processing' },
  { value: 'completed', label: 'Completed' },
  { value: 'failed', label: 'Failed' },
]

export default function ContentTab({ onCreateContent, onViewContent }: ContentTabProps) {
  const router = useRouter()
  const { showToast } = useToast()
  const [content, setContent] = useState<Content[]>([])
  const [loading, setLoading] = useState(true)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [showMenu, setShowMenu] = useState<string | null>(null)
  const [assets, setAssets] = useState<Record<string, GeneratedAsset[]>>({})

  // Search, filter, sort state
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilters, setStatusFilters] = useState<StatusFilter[]>([])
  const [sortBy, setSortBy] = useState<SortOption>('newest')
  const [viewMode, setViewMode] = useState<ViewMode>('list')
  const [showFilters, setShowFilters] = useState(false)

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

  // Filtered & sorted content
  const filteredContent = useMemo(() => {
    let result = [...content]

    // Search filter
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      result = result.filter(item =>
        item.title.toLowerCase().includes(q) ||
        (item.original_text && item.original_text.toLowerCase().includes(q)) ||
        item.source_type.toLowerCase().includes(q)
      )
    }

    // Status filter
    if (statusFilters.length > 0) {
      result = result.filter(item => statusFilters.includes(item.status as StatusFilter))
    }

    // Sort
    switch (sortBy) {
      case 'newest':
        result.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        break
      case 'oldest':
        result.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
        break
      case 'az':
        result.sort((a, b) => a.title.localeCompare(b.title))
        break
    }

    return result
  }, [content, searchQuery, statusFilters, sortBy])

  const toggleStatusFilter = (status: StatusFilter) => {
    setStatusFilters(prev =>
      prev.includes(status)
        ? prev.filter(s => s !== status)
        : [...prev, status]
    )
  }

  const clearFilters = () => {
    setSearchQuery('')
    setStatusFilters([])
    setSortBy('newest')
  }

  const hasActiveFilters = searchQuery.trim() !== '' || statusFilters.length > 0

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
  }, [showToast])

  const handleSchedule = useCallback((e: React.MouseEvent, contentItem: Content) => {
    e.stopPropagation()
    const contentAssets = assets[contentItem.id] || []
    if (contentAssets.length === 0) {
      showToast('No generated assets available for scheduling', 'error')
      return
    }

    setSelectedAsset(contentAssets[0])
    setSelectedContentTitle(contentItem.title)
    setShowScheduleModal(true)
    setShowMenu(null)
  }, [assets, showToast])

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Content"
          description="Manage and transform your content across multiple formats"
          icon={<FileText className="w-5 h-5 text-blue-500" />}
          actions={
            <Button variant="primary" size="sm" leftIcon={<Plus className="h-4 w-4" />}>
              New Content
            </Button>
          }
        />
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
        <PageHeader
          title="Content"
          description="Manage and transform your content across multiple formats"
          icon={<FileText className="w-5 h-5 text-blue-500" />}
          actions={
            <Button
              variant="primary"
              size="sm"
              leftIcon={<Plus className="h-4 w-4" />}
              onClick={() => onCreateContent ? onCreateContent() : router.push('/content/new')}
            >
              New Content
            </Button>
          }
        />
        <NoDataState
          title="No content yet"
          description="Get started by adding your first piece of content. We'll transform it into multiple formats."
          onCreate={() => onCreateContent ? onCreateContent() : router.push('/content/new')}
          createLabel="Add Content"
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Content"
        description="Manage and transform your content across multiple formats"
        icon={<FileText className="w-5 h-5 text-blue-500" />}
        actions={
          <Button
            variant="primary"
            size="sm"
            leftIcon={<Plus className="h-4 w-4" />}
            onClick={() => onCreateContent ? onCreateContent() : router.push('/content/new')}
          >
            New Content
          </Button>
        }
      />

      {/* Search & Filter Bar */}
      <div className="space-y-3">
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 dark:text-slate-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search content..."
              className="w-full pl-10 pr-10 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 dark:focus:ring-blue-500/30 transition-all text-sm"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>

          {/* View toggle */}
          <div className="flex items-center gap-1 p-1 bg-slate-100 dark:bg-slate-800 rounded-xl">
            <button
              onClick={() => setViewMode('list')}
              className={cn(
                'p-2 rounded-lg transition-colors',
                viewMode === 'list'
                  ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 shadow-sm'
                  : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
              )}
              aria-label="List view"
            >
              <List className="h-4 w-4" />
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={cn(
                'p-2 rounded-lg transition-colors',
                viewMode === 'grid'
                  ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 shadow-sm'
                  : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
              )}
              aria-label="Grid view"
            >
              <LayoutGrid className="h-4 w-4" />
            </button>
          </div>

          {/* Sort dropdown */}
          <div className="relative">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortOption)}
              className="appearance-none pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 dark:focus:ring-blue-500/30 cursor-pointer"
            >
              <option value="newest">Newest first</option>
              <option value="oldest">Oldest first</option>
              <option value="az">A — Z</option>
            </select>
            <ArrowUpDown className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none" />
          </div>

          {/* Filter toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={cn(
              'flex items-center gap-2 px-4 py-2.5 rounded-xl border text-sm font-medium transition-colors',
              statusFilters.length > 0
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-500/20 text-blue-700 dark:text-blue-300'
                : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700'
            )}
          >
            <SlidersHorizontal className="h-4 w-4" />
            Filters
            {statusFilters.length > 0 && (
              <span className="bg-blue-500 text-white text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center">
                {statusFilters.length}
              </span>
            )}
          </button>
        </div>

        {/* Status filter chips */}
        {showFilters && (
          <div className="flex flex-wrap items-center gap-2 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700">
            <span className="text-xs font-medium text-slate-500 dark:text-slate-400 mr-1">Status:</span>
            {STATUS_FILTERS.map((filter) => (
              <button
                key={filter.value}
                onClick={() => toggleStatusFilter(filter.value)}
                className={cn(
                  'px-3 py-1.5 rounded-full text-xs font-medium transition-all',
                  statusFilters.includes(filter.value)
                    ? getStatusColor(filter.value) + ' ring-2 ring-offset-1 ring-blue-500/30'
                    : 'bg-white dark:bg-slate-700 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-600 hover:bg-slate-100 dark:hover:bg-slate-600'
                )}
              >
                {filter.label}
              </button>
            ))}
            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="ml-auto text-xs text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300 underline"
              >
                Clear all
              </button>
            )}
          </div>
        )}

        {/* Results count */}
        <div className="flex items-center justify-between text-sm text-slate-500 dark:text-slate-400">
          <span>
            Showing {filteredContent.length} of {content.length} item{content.length !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      {/* Content List/Grid */}
      {filteredContent.length === 0 && hasActiveFilters ? (
        <EmptyState
          title="No matching content"
          description="Try adjusting your search or filters."
          icon="search"
          action={{
            label: 'Clear filters',
            onClick: clearFilters,
          }}
        />
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {filteredContent.map((item) => (
            <Card
              key={item.id}
              interactive
              className="group hover:shadow-lg transition-all duration-200"
              onClick={() => onViewContent ? onViewContent(item.id) : router.push(`/content/${item.id}`)}
            >
              <CardContent className="p-5">
                <div className="flex items-start gap-3">
                  <div className="h-10 w-10 rounded-lg bg-blue-100 dark:bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                    <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className={cn('w-2 h-2 rounded-full flex-shrink-0', getStatusDotColor(item.status))} />
                      <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate">
                        {item.title}
                      </h3>
                    </div>
                    <div className="flex items-center gap-2 mt-1.5">
                      <span className={cn('text-xs px-2 py-0.5 rounded-full', getStatusColor(item.status))}>
                        {item.status}
                      </span>
                      <span className="text-xs text-slate-400 dark:text-slate-500 capitalize">{item.source_type}</span>
                    </div>
                    <p className="text-xs text-slate-400 dark:text-slate-500 mt-1.5">
                      {formatDate(item.created_at)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {filteredContent.map((item) => (
            <Card
              key={item.id}
              interactive
              className="group hover:shadow-md transition-all duration-200"
              onClick={() => onViewContent ? onViewContent(item.id) : router.push(`/content/${item.id}`)}
            >
              <CardContent className="p-5">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1 min-w-0">
                    <div className="h-10 w-10 rounded-lg bg-blue-100 dark:bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                      <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className={cn('w-2 h-2 rounded-full flex-shrink-0', getStatusDotColor(item.status))} />
                        <h3 className="text-base font-semibold text-slate-900 dark:text-slate-100 truncate">
                          {item.title}
                        </h3>
                        <span className={cn('text-xs px-2 py-0.5 rounded-full', getStatusColor(item.status))}>
                          {item.status}
                        </span>
                      </div>

                      {item.original_text && (
                        <p className="mt-1.5 text-sm text-slate-500 dark:text-slate-400 line-clamp-2">
                          {item.original_text.substring(0, 150)}...
                        </p>
                      )}

                      <div className="mt-2 flex items-center gap-4 text-sm text-slate-400 dark:text-slate-500 flex-wrap">
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3.5 w-3.5" />
                          {formatDate(item.created_at)}
                        </span>
                        <span className="capitalize">{item.source_type}</span>
                        {item.word_count && (
                          <span>{item.word_count} words</span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="relative ml-3" onClick={(e) => e.stopPropagation()}>
                    <button
                      className="p-2 text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:text-slate-400 rounded-full hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                      onClick={(e) => {
                        e.preventDefault()
                        setShowMenu(showMenu === item.id ? null : item.id)
                      }}
                    >
                      <MoreVertical className="h-4 w-4" />
                    </button>

                    {showMenu === item.id && (
                      <div className="absolute right-0 mt-1 w-48 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 py-1 z-10">
                        <button
                          className="w-full flex items-center gap-2 px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700"
                          onClick={() => {
                            onViewContent ? onViewContent(item.id) : router.push(`/content/${item.id}`)
                            setShowMenu(null)
                          }}
                        >
                          <ExternalLink className="h-4 w-4" />
                          View Details
                        </button>
                        {(assets[item.id]?.length || 0) > 0 && (
                          <button
                            className="w-full flex items-center gap-2 px-4 py-2 text-sm text-violet-600 hover:bg-violet-50 dark:hover:bg-violet-500/10"
                            onClick={(e) => handleSchedule(e, item)}
                          >
                            <Calendar className="h-4 w-4" />
                            Schedule
                          </button>
                        )}
                        <button
                          className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-500/10"
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
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Schedule Modal */}
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
  )
}