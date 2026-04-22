'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import DOMPurify from 'dompurify'
import {
  getRSSEntries,
  importRSSEntry,
  bulkImportRSSEntries,
  getRSSFeeds,
  RSSEntry,
  RSSFeed,
} from '@/lib/api'
import { formatApiError } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { useToast } from '@/hooks/useToast'
import {
  FileText,
  Import,
  Check,
  ExternalLink,
  Calendar,
  User,
  Tag,
  Filter,
  Search,
  ChevronDown,
  ChevronUp,
  Square,
  CheckSquare,
  Inbox,
  X,
} from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { cn } from '@/lib/utils'

interface RSSEntriesPanelProps {
  selectedFeedId?: string | null
  onImportSuccess?: () => void
}

export default function RSSEntriesPanel({ selectedFeedId, onImportSuccess }: RSSEntriesPanelProps) {
  const router = useRouter()
  const { showToast } = useToast()
  const [entries, setEntries] = useState<RSSEntry[]>([])
  const [feeds, setFeeds] = useState<RSSFeed[]>([])
  const [loading, setLoading] = useState(true)
  const [feedsLoading, setFeedsLoading] = useState(true)
  const [importingId, setImportingId] = useState<string | null>(null)
  const [bulkImporting, setBulkImporting] = useState(false)
  const [selectedEntries, setSelectedEntries] = useState<Set<string>>(new Set())
  const [expandedEntry, setExpandedEntry] = useState<string | null>(null)
  
  // Filters
  const [searchQuery, setSearchQuery] = useState('')
  const [filterFeed, setFilterFeed] = useState<string>('')
  const [filterProcessed, setFilterProcessed] = useState<string>('')
  const [dateRange, setDateRange] = useState<{ start?: string; end?: string }>({})
  const [showFilters, setShowFilters] = useState(false)

  const loadFeeds = useCallback(async () => {
    try {
      setFeedsLoading(true)
      const data = await getRSSFeeds()
      setFeeds(data)
    } catch (error) {
      console.error('Failed to load feeds:', error)
    } finally {
      setFeedsLoading(false)
    }
  }, [])

  const loadEntries = useCallback(async () => {
    try {
      setLoading(true)
      const options: Parameters<typeof getRSSEntries>[0] = {
        limit: 50,
      }
      
      if (selectedFeedId) {
        options.feedId = selectedFeedId
      } else if (filterFeed) {
        options.feedId = filterFeed
      }
      
      if (filterProcessed === 'processed') {
        options.processed = true
      } else if (filterProcessed === 'unprocessed') {
        options.processed = false
      }
      
      if (dateRange.start) {
        options.startDate = dateRange.start
      }
      if (dateRange.end) {
        options.endDate = dateRange.end
      }
      
      const data = await getRSSEntries(options)
      setEntries(data)
      setSelectedEntries(new Set()) // Clear selections on reload
    } catch (error) {
      console.error('Failed to load RSS entries:', error)
      showToast('Failed to load RSS entries', 'error')
    } finally {
      setLoading(false)
    }
  }, [selectedFeedId, filterFeed, filterProcessed, dateRange, showToast])

  useEffect(() => {
    loadFeeds()
  }, [loadFeeds])

  useEffect(() => {
    loadEntries()
  }, [loadEntries])

  // Update filter when selectedFeedId changes from parent
  useEffect(() => {
    if (selectedFeedId) {
      setFilterFeed(selectedFeedId)
    } else {
      setFilterFeed('')
    }
  }, [selectedFeedId])

  const handleImport = async (entry: RSSEntry) => {
    try {
      setImportingId(entry.id)
      await importRSSEntry(entry.id)
      showToast('Entry imported successfully', 'success')
      loadEntries()
      onImportSuccess?.()
    } catch (error) {
      console.error('Failed to import entry:', error)
      showToast(formatApiError(error, 'Failed to import entry'), 'error')
    } finally {
      setImportingId(null)
    }
  }

  const handleBulkImport = async () => {
    if (selectedEntries.size === 0) return
    
    try {
      setBulkImporting(true)
      const result = await bulkImportRSSEntries(Array.from(selectedEntries))
      showToast(`Imported ${result.imported} entries`, 'success')
      setSelectedEntries(new Set())
      loadEntries()
      onImportSuccess?.()
    } catch (error) {
      console.error('Failed to bulk import:', error)
      showToast(formatApiError(error, 'Failed to import entries'), 'error')
    } finally {
      setBulkImporting(false)
    }
  }

  const toggleSelection = (entryId: string) => {
    setSelectedEntries(prev => {
      const newSet = new Set(prev)
      if (newSet.has(entryId)) {
        newSet.delete(entryId)
      } else {
        newSet.add(entryId)
      }
      return newSet
    })
  }

  const selectAll = () => {
    const unimportedEntries = filteredEntries.filter(e => !e.is_imported)
    if (selectedEntries.size === unimportedEntries.length) {
      setSelectedEntries(new Set())
    } else {
      setSelectedEntries(new Set(unimportedEntries.map(e => e.id)))
    }
  }

  const filteredEntries = entries.filter(entry => {
    if (!searchQuery) return true
    const query = searchQuery.toLowerCase()
    return (
      entry.title.toLowerCase().includes(query) ||
      entry.description?.toLowerCase().includes(query) ||
      entry.author?.toLowerCase().includes(query)
    )
  })

  const unimportedCount = filteredEntries.filter(e => !e.is_imported).length
  const selectedCount = selectedEntries.size

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / 86400000)
    
    if (days === 0) {
      return 'Today'
    } else if (days === 1) {
      return 'Yesterday'
    } else if (days < 7) {
      return `${days} days ago`
    }
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

  const getFeedName = (feedId: string): string => {
    const feed = feeds.find(f => f.id === feedId)
    return feed?.name || 'Unknown Feed'
  }

  if (loading && entries.length === 0) {
    return (
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <Skeleton className="h-8 w-40" />
          <Skeleton className="h-10 w-32" />
        </div>
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-4">
              <div className="flex items-start gap-4">
                <Skeleton className="h-5 w-5 mt-1" />
                <div className="flex-1">
                  <Skeleton className="h-5 w-3/4 mb-2" />
                  <Skeleton className="h-4 w-full" />
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
        title="RSS Entries"
        description={`${filteredEntries.length} entries • ${unimportedCount} unimported`}
        icon={<Inbox className="w-5 h-5 text-blue-500" />}
        actions={
          <>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search entries..."
                className="pl-10 w-48"
              />
            </div>
            <Button
              variant="secondary"
              onClick={() => setShowFilters(!showFilters)}
              leftIcon={<Filter className="w-4 h-4" />}
              className={showFilters ? 'bg-slate-200 dark:bg-slate-700' : ''}
            >
              Filters
            </Button>
          </>
        }
      />

        {/* Filters Panel */}
        {showFilters && (
          <Card className="bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700">
            <CardContent className="p-4 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {/* Feed Filter */}
                <div>
                  <label className="block text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">
                    Feed
                  </label>
                  <select
                    value={filterFeed}
                    onChange={(e) => setFilterFeed(e.target.value)}
                    disabled={!!selectedFeedId || feedsLoading}
                    className="w-full h-11 px-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    <option value="">All feeds</option>
                    {feeds.map(feed => (
                      <option key={feed.id} value={feed.id}>
                        {feed.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Processed Filter */}
                <div>
                  <label className="block text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">
                    Status
                  </label>
                  <select
                    value={filterProcessed}
                    onChange={(e) => setFilterProcessed(e.target.value)}
                    className="w-full h-11 px-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All entries</option>
                    <option value="unprocessed">Unimported</option>
                    <option value="processed">Imported</option>
                  </select>
                </div>

                {/* Date Range */}
                <div>
                  <label className="block text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">
                    Date Range
                  </label>
                  <div className="flex items-center gap-2">
                    <Input
                      type="date"
                      value={dateRange.start || ''}
                      onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
                      className="flex-1"
                    />
                    <span className="text-slate-400">-</span>
                    <Input
                      type="date"
                      value={dateRange.end || ''}
                      onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
                      className="flex-1"
                    />
                  </div>
                </div>
              </div>

              {/* Clear Filters */}
              <div className="flex justify-end pt-2 border-t border-slate-200 dark:border-slate-700">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setFilterFeed(selectedFeedId || '')
                    setFilterProcessed('')
                    setDateRange({})
                    setSearchQuery('')
                  }}
                  leftIcon={<X className="w-4 h-4" />}
                >
                  Clear Filters
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

      {/* Bulk Actions */}
      {selectedCount > 0 && (
        <div className="flex items-center justify-between bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-xl px-4 py-3">
          <span className="text-sm text-blue-900 dark:text-blue-100">
            {selectedCount} entr{selectedCount === 1 ? 'y' : 'ies'} selected
          </span>
          <Button
            onClick={handleBulkImport}
            loading={bulkImporting}
            size="sm"
            leftIcon={<Import className="w-4 h-4" />}
          >
            Import Selected
          </Button>
        </div>
      )}

      {/* Entries List */}
      {filteredEntries.length === 0 ? (
        <Card className="border-dashed border-2 border-slate-200 dark:border-slate-700">
          <CardContent className="p-12 text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
              <Inbox className="w-8 h-8 text-slate-400" />
            </div>
            <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-2">
              No entries found
            </h3>
            <p className="text-slate-500 dark:text-slate-400 max-w-md mx-auto">
              {searchQuery || filterProcessed || filterFeed || dateRange.start
                ? 'Try adjusting your filters to see more results.'
                : 'New RSS entries will appear here when your feeds are fetched.'}
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {/* Select All Header */}
          {unimportedCount > 0 && (
            <div className="flex items-center gap-3 px-2">
              <button
                onClick={selectAll}
                className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 transition-colors"
              >
                {selectedEntries.size === unimportedCount && unimportedCount > 0 ? (
                  <CheckSquare className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                ) : (
                  <Square className="w-4 h-4" />
                )}
                {selectedEntries.size === unimportedCount && unimportedCount > 0
                  ? 'Deselect all'
                  : 'Select all unimported'}
              </button>
            </div>
          )}

          {/* Entries */}
          {filteredEntries.map((entry) => (
            <Card
              key={entry.id}
              className={cn(
                'transition-all duration-200 overflow-hidden',
                entry.is_imported
                  ? 'opacity-60 bg-slate-50 dark:bg-slate-900/50'
                  : 'hover:shadow-md cursor-pointer',
                expandedEntry === entry.id && 'ring-2 ring-blue-500 border-blue-500 dark:border-blue-400'
              )}
              onClick={() => !entry.is_imported && setExpandedEntry(expandedEntry === entry.id ? null : entry.id)}
            >
              <CardContent className="p-4">
                <div className="flex items-start gap-4">
                  {/* Checkbox (only for unimported) */}
                  {!entry.is_imported && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleSelection(entry.id)
                      }}
                      className="mt-1 flex-shrink-0 text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                    >
                      {selectedEntries.has(entry.id) ? (
                        <CheckSquare className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                      ) : (
                        <Square className="w-5 h-5" />
                      )}
                    </button>
                  )}

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    {/* Title Row */}
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h3 className={cn(
                            'font-medium text-slate-900 dark:text-slate-100',
                            expandedEntry === entry.id ? 'line-clamp-none' : 'line-clamp-1'
                          )}>
                            {entry.title}
                          </h3>
                          {entry.is_imported && (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded-full bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400">
                              <Check className="w-3 h-3" />
                              Imported
                            </span>
                          )}
                        </div>
                        
                        {/* Meta */}
                        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-slate-500 dark:text-slate-400 mt-1">
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3.5 h-3.5" />
                            {formatDate(entry.published_at)}
                          </span>
                          {!selectedFeedId && (
                            <span className="flex items-center gap-1">
                              <Tag className="w-3.5 h-3.5" />
                              {getFeedName(entry.feed_id)}
                            </span>
                          )}
                          {entry.author && (
                            <span className="flex items-center gap-1">
                              <User className="w-3.5 h-3.5" />
                              {entry.author}
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {entry.is_imported ? (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation()
                              router.push(`/content/${entry.imported_as_content_id}`)
                            }}
                            leftIcon={<FileText className="w-4 h-4" />}
                          >
                            View
                          </Button>
                        ) : (
                          <Button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleImport(entry)
                            }}
                            loading={importingId === entry.id}
                            size="sm"
                            leftIcon={<Import className="w-4 h-4" />}
                          >
                            Import
                          </Button>
                        )}
                        
                        <a
                          href={entry.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={(e) => e.stopPropagation()}
                          className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                          title="Open original"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </a>
                        
                        {!entry.is_imported && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              setExpandedEntry(expandedEntry === entry.id ? null : entry.id)
                            }}
                            className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                          >
                            {expandedEntry === entry.id ? (
                              <ChevronUp className="w-4 h-4" />
                            ) : (
                              <ChevronDown className="w-4 h-4" />
                            )}
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Description (always visible, truncated) */}
                    {entry.description && (
                      <p className={cn(
                        'text-sm text-slate-600 dark:text-slate-400 mt-2',
                        expandedEntry !== entry.id && 'line-clamp-2'
                      )}>
                        {entry.description}
                      </p>
                    )}

                    {/* Expanded Content */}
                    {expandedEntry === entry.id && entry.content && (
                      <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
                        <div className="prose prose-sm dark:prose-invert max-w-none text-slate-700 dark:text-slate-300">
                          <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(entry.content.substring(0, 2000)) }} />
                          {entry.content.length > 2000 && (
                            <p className="text-slate-500 italic">... (content truncated)</p>
                          )}
                        </div>
                        
                        {/* Categories */}
                        {entry.categories && entry.categories.length > 0 && (
                          <div className="flex flex-wrap gap-2 mt-4">
                            {entry.categories.map((category, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-1 text-xs rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                              >
                                {category}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
