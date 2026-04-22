'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  getRSSFeeds,
  addRSSFeed,
  updateRSSFeed,
  deleteRSSFeed,
  fetchRSSFeed,
  RSSFeed,
  RSSFeedRequest,
} from '@/lib/api'
import { formatApiError } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { useToast } from '@/hooks/useToast'
import {
  Rss,
  Plus,
  RefreshCw,
  Trash2,
  Power,
  PowerOff,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  ExternalLink,
  MoreVertical,
  Loader2,
} from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { cn } from '@/lib/utils'

interface RSSFeedManagerProps {
  onFeedSelect?: (feedId: string | null) => void
  selectedFeedId?: string | null
}

export default function RSSFeedManager({ onFeedSelect, selectedFeedId }: RSSFeedManagerProps) {
  const { showToast } = useToast()
  const [feeds, setFeeds] = useState<RSSFeed[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddForm, setShowAddForm] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [fetchingId, setFetchingId] = useState<string | null>(null)
  const [togglingId, setTogglingId] = useState<string | null>(null)
  const [showMenu, setShowMenu] = useState<string | null>(null)

  // Form state
  const [formData, setFormData] = useState<RSSFeedRequest>({
    name: '',
    url: '',
    frequency: 'daily',
    is_active: true,
  })
  const [formErrors, setFormErrors] = useState<Record<string, string>>({})
  const [submitting, setSubmitting] = useState(false)

  const loadFeeds = useCallback(async () => {
    try {
      setLoading(true)
      const data = await getRSSFeeds()
      setFeeds(data)
    } catch (error) {
      console.error('Failed to load RSS feeds:', error)
      showToast('Failed to load RSS feeds', 'error')
    } finally {
      setLoading(false)
    }
  }, [showToast])

  useEffect(() => {
    loadFeeds()
  }, [loadFeeds])

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = () => setShowMenu(null)
    if (showMenu) {
      document.addEventListener('click', handleClickOutside)
      return () => document.removeEventListener('click', handleClickOutside)
    }
  }, [showMenu])

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {}
    
    if (!formData.name.trim()) {
      errors.name = 'Name is required'
    }
    
    if (!formData.url.trim()) {
      errors.url = 'URL is required'
    } else {
      try {
        new URL(formData.url)
      } catch {
        errors.url = 'Please enter a valid URL'
      }
    }
    
    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return
    
    try {
      setSubmitting(true)
      await addRSSFeed(formData)
      showToast('RSS feed added successfully', 'success')
      setFormData({ name: '', url: '', frequency: 'daily', is_active: true })
      setShowAddForm(false)
      loadFeeds()
    } catch (error) {
      console.error('Failed to add RSS feed:', error)
      showToast(formatApiError(error, 'Failed to add RSS feed'), 'error')
    } finally {
      setSubmitting(false)
    }
  }

  const handleToggle = async (feed: RSSFeed, e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      setTogglingId(feed.id)
      await updateRSSFeed(feed.id, { is_active: !feed.is_active })
      showToast(`Feed ${feed.is_active ? 'disabled' : 'enabled'}`, 'success')
      loadFeeds()
    } catch (error) {
      console.error('Failed to toggle feed:', error)
      showToast('Failed to update feed', 'error')
    } finally {
      setTogglingId(null)
    }
  }

  const handleFetch = async (feedId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      setFetchingId(feedId)
      const result = await fetchRSSFeed(feedId)
      showToast(`Fetched ${result.entries_fetched} entries`, 'success')
      loadFeeds()
    } catch (error) {
      console.error('Failed to fetch feed:', error)
      showToast('Failed to fetch feed', 'error')
    } finally {
      setFetchingId(null)
      setShowMenu(null)
    }
  }

  const handleDelete = async (feed: RSSFeed, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!confirm(`Are you sure you want to delete "${feed.name}"?`)) {
      setShowMenu(null)
      return
    }
    
    try {
      setDeletingId(feed.id)
      await deleteRSSFeed(feed.id)
      showToast('Feed deleted successfully', 'success')
      if (selectedFeedId === feed.id) {
        onFeedSelect?.(null)
      }
      loadFeeds()
    } catch (error) {
      console.error('Failed to delete feed:', error)
      showToast('Failed to delete feed', 'error')
    } finally {
      setDeletingId(null)
      setShowMenu(null)
    }
  }

  const formatLastFetched = (dateString?: string): string => {
    if (!dateString) return 'Never'
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)
    
    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    if (days < 7) return `${days}d ago`
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-emerald-500" />
      case 'failed':
        return <XCircle className="w-4 h-4 text-rose-500" />
      case 'pending':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
      default:
        return <AlertCircle className="w-4 h-4 text-slate-400" />
    }
  }

  const getFrequencyLabel = (frequency: string): string => {
    const labels: Record<string, string> = {
      manual: 'Manual',
      hourly: 'Hourly',
      daily: 'Daily',
      weekly: 'Weekly',
    }
    return labels[frequency] || frequency
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <Skeleton className="h-8 w-32" />
          <Skeleton className="h-10 w-28" />
        </div>
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-4">
              <div className="flex items-center gap-4">
                <Skeleton className="h-10 w-10 rounded-lg" />
                <div className="flex-1">
                  <Skeleton className="h-5 w-48 mb-2" />
                  <Skeleton className="h-4 w-32" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="RSS Feeds"
        description={`${feeds.length} feed${feeds.length !== 1 ? 's' : ''} subscribed`}
        icon={<Rss className="w-5 h-5 text-orange-500" />}
        actions={
          <Button
            onClick={() => setShowAddForm(!showAddForm)}
            leftIcon={<Plus className="w-4 h-4" />}
            variant={showAddForm ? 'secondary' : 'primary'}
          >
            {showAddForm ? 'Cancel' : 'Add Feed'}
          </Button>
        }
      />

      {/* Add Feed Form */}
      {showAddForm && (
        <Card className="border-2 border-dashed border-blue-200 dark:border-blue-800 bg-blue-50/50 dark:bg-blue-900/20">
          <CardContent className="p-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                    Feed Name
                  </label>
                  <Input
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="e.g., TechCrunch News"
                    error={formErrors.name}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                    RSS URL
                  </label>
                  <Input
                    value={formData.url}
                    onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                    placeholder="https://example.com/feed.xml"
                    error={formErrors.url}
                    type="url"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Fetch Frequency
                </label>
                <div className="flex flex-wrap gap-2">
                  {(['manual', 'hourly', 'daily', 'weekly'] as const).map((freq) => (
                    <button
                      key={freq}
                      type="button"
                      onClick={() => setFormData({ ...formData, frequency: freq })}
                      className={cn(
                        'px-4 py-2 rounded-lg text-sm font-medium transition-all',
                        formData.frequency === freq
                          ? 'bg-blue-600 text-white shadow-md'
                          : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700 hover:border-blue-300 dark:hover:border-blue-600'
                      )}
                    >
                      {getFrequencyLabel(freq)}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex gap-3 pt-2">
                <Button type="submit" loading={submitting}>
                  Add Feed
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => {
                    setShowAddForm(false)
                    setFormData({ name: '', url: '', frequency: 'daily', is_active: true })
                    setFormErrors({})
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Feeds List */}
      {feeds.length === 0 ? (
        <Card className="border-dashed border-2 border-slate-200 dark:border-slate-700">
          <CardContent className="p-12 text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
              <Rss className="w-8 h-8 text-slate-400" />
            </div>
            <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-2">
              No RSS feeds yet
            </h3>
            <p className="text-slate-500 dark:text-slate-400 mb-4 max-w-md mx-auto">
              Subscribe to RSS feeds to automatically import content from your favorite blogs and news sources.
            </p>
            <Button
              onClick={() => setShowAddForm(true)}
              leftIcon={<Plus className="w-4 h-4" />}
            >
              Add Your First Feed
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {feeds.map((feed) => (
            <Card
              key={feed.id}
              onClick={() => onFeedSelect?.(selectedFeedId === feed.id ? null : feed.id)}
              className={cn(
                'cursor-pointer transition-all duration-200',
                selectedFeedId === feed.id
                  ? 'ring-2 ring-blue-500 border-blue-500 dark:border-blue-400 shadow-md'
                  : 'hover:shadow-md hover:border-slate-300 dark:hover:border-slate-600',
                !feed.is_active && 'opacity-60'
              )}
            >
              <CardContent className="p-4">
                <div className="flex items-center gap-4">
                  {/* Icon */}
                  <div className={cn(
                    'w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0',
                    feed.is_active
                      ? 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-400'
                  )}>
                    <Rss className="w-5 h-5" />
                  </div>

                  {/* Feed Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium text-slate-900 dark:text-slate-100 truncate">
                        {feed.name}
                      </h3>
                      {!feed.is_active && (
                        <span className="px-2 py-0.5 text-xs rounded-full bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400">
                          Disabled
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-slate-500 dark:text-slate-400 mt-1">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5" />
                        {getFrequencyLabel(feed.frequency)}
                      </span>
                      <span className="flex items-center gap-1">
                        {getStatusIcon(feed.last_fetch_status)}
                        {feed.last_fetch_status === 'failed' ? 'Failed' : formatLastFetched(feed.last_fetched_at)}
                      </span>
                      <span>{feed.entry_count} entries</span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    {/* Toggle Button */}
                    <button
                      onClick={(e) => handleToggle(feed, e)}
                      disabled={togglingId === feed.id}
                      className={cn(
                        'p-2 rounded-lg transition-colors',
                        feed.is_active
                          ? 'text-emerald-600 dark:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-900/30'
                          : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                      )}
                      title={feed.is_active ? 'Disable feed' : 'Enable feed'}
                    >
                      {togglingId === feed.id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : feed.is_active ? (
                        <Power className="w-4 h-4" />
                      ) : (
                        <PowerOff className="w-4 h-4" />
                      )}
                    </button>

                    {/* Menu */}
                    <div className="relative">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setShowMenu(showMenu === feed.id ? null : feed.id)
                        }}
                        className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                      >
                        <MoreVertical className="w-4 h-4" />
                      </button>
                      
                      {showMenu === feed.id && (
                        <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 py-1 z-50">
                          <button
                            onClick={(e) => handleFetch(feed.id, e)}
                            disabled={fetchingId === feed.id}
                            className="w-full flex items-center gap-2 px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 disabled:opacity-50"
                          >
                            {fetchingId === feed.id ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <RefreshCw className="w-4 h-4" />
                            )}
                            Fetch Now
                          </button>
                          <a
                            href={feed.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="w-full flex items-center gap-2 px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
                          >
                            <ExternalLink className="w-4 h-4" />
                            View Source
                          </a>
                          <div className="border-t border-slate-200 dark:border-slate-700 my-1" />
                          <button
                            onClick={(e) => handleDelete(feed, e)}
                            disabled={deletingId === feed.id}
                            className="w-full flex items-center gap-2 px-4 py-2 text-sm text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-900/30 disabled:opacity-50"
                          >
                            {deletingId === feed.id ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Trash2 className="w-4 h-4" />
                            )}
                            Delete Feed
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Feed Selection Hint */}
      {feeds.length > 0 && !selectedFeedId && onFeedSelect && (
        <div className="text-center py-4 text-sm text-slate-500 dark:text-slate-400">
          Click on a feed to filter entries
        </div>
      )}
    </div>
  )
}
