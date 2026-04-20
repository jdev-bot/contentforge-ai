'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Lightbulb,
  Clock,
  TrendingUp,
  Filter,
  Check,
  X,
  RefreshCw,
  ChevronDown,
  Sparkles,
  MessageSquare,
  Calendar,
  Target,
} from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { useToast } from '@/hooks/useToast'
import { cn } from '@/lib/utils'
import {
  getSuggestions,
  acceptSuggestion,
  dismissSuggestion,
  type Suggestion,
  type SuggestionType,
} from '@/lib/api'
import { formatApiError } from '@/lib/api'

type FilterType = 'all' | SuggestionType

const SUGGESTION_TYPE_CONFIG: Record<SuggestionType, { icon: typeof Lightbulb; label: string; color: string; gradient: string }> = {
  topic: {
    icon: Sparkles,
    label: 'Topic',
    color: 'text-violet-600 dark:text-violet-400',
    gradient: 'from-violet-500/10 to-purple-500/10 dark:from-violet-500/20 dark:to-purple-500/20',
  },
  timing: {
    icon: Clock,
    label: 'Timing',
    color: 'text-amber-600 dark:text-amber-400',
    gradient: 'from-amber-500/10 to-orange-500/10 dark:from-amber-500/20 dark:to-orange-500/20',
  },
  improvement: {
    icon: TrendingUp,
    label: 'Improvement',
    color: 'text-emerald-600 dark:text-emerald-400',
    gradient: 'from-emerald-500/10 to-teal-500/10 dark:from-emerald-500/20 dark:to-teal-500/20',
  },
}

export default function SuggestionPanel() {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<FilterType>('all')
  const [filterOpen, setFilterOpen] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const { showToast } = useToast()

  const fetchSuggestions = useCallback(async () => {
    try {
      setLoading(true)
      const data = await getSuggestions(filter === 'all' ? undefined : filter)
      setSuggestions(data)
    } catch (err: unknown) {
      const message = formatApiError(err, 'Failed to fetch suggestions')
      showToast(message, 'error')
    } finally {
      setLoading(false)
    }
  }, [filter, showToast])

  useEffect(() => {
    fetchSuggestions()
  }, [fetchSuggestions])

  const handleRefresh = async () => {
    setRefreshing(true)
    await fetchSuggestions()
    setRefreshing(false)
  }

  const handleAccept = async (suggestionId: string) => {
    try {
      await acceptSuggestion(suggestionId)
      setSuggestions(prev => prev.filter(s => s.id !== suggestionId))
      showToast('The suggestion has been applied.', 'success')
    } catch (err: unknown) {
      const message = formatApiError(err, 'Failed to accept suggestion')
      showToast(message, 'error')
    }
  }

  const handleDismiss = async (suggestionId: string) => {
    try {
      await dismissSuggestion(suggestionId)
      setSuggestions(prev => prev.filter(s => s.id !== suggestionId))
      showToast('Suggestion dismissed', 'info')
    } catch (err: unknown) {
      const message = formatApiError(err, 'Failed to dismiss suggestion')
      showToast(message, 'error')
    }
  }

  const filteredSuggestions = suggestions.filter(s => filter === 'all' || s.type === filter)

  const typeCounts = {
    topic: suggestions.filter(s => s.type === 'topic').length,
    timing: suggestions.filter(s => s.type === 'timing').length,
    improvement: suggestions.filter(s => s.type === 'improvement').length,
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
          <p className="text-slate-500 dark:text-slate-400">Loading suggestions...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <PageHeader
        title="AI Suggestions"
        description="Smart recommendations to improve your content"
        icon={<Lightbulb className="w-5 h-5 text-amber-500" />}
        actions={
          <div className="flex items-center gap-3">
            {/* Filter Dropdown */}
            <div className="relative">
              <Button
                variant="outline"
                size="sm"
                leftIcon={<Filter className="h-4 w-4" />}
                rightIcon={<ChevronDown className="h-3 w-3" />}
                onClick={() => setFilterOpen(!filterOpen)}
              >
                {filter === 'all' ? 'All Types' : SUGGESTION_TYPE_CONFIG[filter].label}
              </Button>
              <AnimatePresence>
                {filterOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: -8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    className="absolute right-0 mt-2 w-48 py-2 bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-slate-200 dark:border-slate-700 z-20"
                  >
                    <button
                      onClick={() => { setFilter('all'); setFilterOpen(false) }}
                      className={cn(
                        'w-full px-4 py-2 text-sm text-left hover:bg-slate-50 dark:hover:bg-slate-700 flex items-center justify-between',
                        filter === 'all' && 'text-blue-600 dark:text-blue-400 font-medium'
                      )}
                    >
                      All Types
                      <Badge size="sm" variant="default">{suggestions.length}</Badge>
                    </button>
                    {(['topic', 'timing', 'improvement'] as SuggestionType[]).map(type => {
                      const config = SUGGESTION_TYPE_CONFIG[type]
                      const Icon = config.icon
                      return (
                        <button
                          key={type}
                          onClick={() => { setFilter(type); setFilterOpen(false) }}
                          className={cn(
                            'w-full px-4 py-2 text-sm text-left hover:bg-slate-50 dark:hover:bg-slate-700 flex items-center justify-between',
                            filter === type && 'text-blue-600 dark:text-blue-400 font-medium'
                          )}
                        >
                          <span className="flex items-center gap-2">
                            <Icon className={cn('h-4 w-4', config.color)} />
                            {config.label}
                          </span>
                          <Badge size="sm" variant="default">{typeCounts[type]}</Badge>
                        </button>
                      )
                    })}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
            <Button
              variant="ghost"
              size="sm"
              leftIcon={<RefreshCw className={cn('h-4 w-4', refreshing && 'animate-spin')} />}
              onClick={handleRefresh}
              disabled={refreshing}
            >
              Refresh
            </Button>
          </div>
        }
      />

      {/* Type Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {(['topic', 'timing', 'improvement'] as SuggestionType[]).map(type => {
          const config = SUGGESTION_TYPE_CONFIG[type]
          const Icon = config.icon
          const count = typeCounts[type]
          return (
            <motion.div key={type} whileHover={{ y: -2 }} transition={{ duration: 0.2 }}>
              <Card variant="glass" interactive onClick={() => setFilter(filter === type ? 'all' : type)}>
                <div className="flex items-center gap-4">
                  <div className={cn('p-3 rounded-xl bg-gradient-to-br', config.gradient)}>
                    <Icon className={cn('h-6 w-6', config.color)} />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">{count}</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">{config.label} Suggestions</p>
                  </div>
                </div>
              </Card>
            </motion.div>
          )
        })}
      </div>

      {/* Suggestion Cards */}
      <div className="space-y-4">
        <AnimatePresence mode="popLayout">
          {filteredSuggestions.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-12"
            >
              <Lightbulb className="h-12 w-12 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
              <p className="text-slate-500 dark:text-slate-400 text-lg font-medium">No suggestions available</p>
              <p className="text-slate-400 dark:text-slate-500 text-sm mt-1">
                Create more content to receive AI-powered suggestions
              </p>
            </motion.div>
          ) : (
            filteredSuggestions.map((suggestion, index) => {
              const config = SUGGESTION_TYPE_CONFIG[suggestion.type]
              const TypeIcon = config.icon
              return (
                <motion.div
                  key={suggestion.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: -100, scale: 0.95 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                  layout
                >
                  <Card variant="glass" className="group">
                    <CardContent>
                      <div className="flex items-start gap-4">
                        <div className={cn('p-2.5 rounded-xl bg-gradient-to-br flex-shrink-0', config.gradient)}>
                          <TypeIcon className={cn('h-5 w-5', config.color)} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge variant={suggestion.type === 'topic' ? 'purple' : suggestion.type === 'timing' ? 'warning' : 'success'} size="sm">
                              {config.label}
                            </Badge>
                            {suggestion.priority && (
                              <Badge
                                variant={suggestion.priority === 'high' ? 'error' : suggestion.priority === 'medium' ? 'warning' : 'default'}
                                size="sm"
                                dot
                              >
                                {suggestion.priority}
                              </Badge>
                            )}
                          </div>
                          <h3 className="text-base font-semibold text-slate-900 dark:text-slate-100 mb-1">
                            {suggestion.title}
                          </h3>
                          <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                            {suggestion.description}
                          </p>
                          {suggestion.relevance_score !== undefined && (
                            <div className="mt-3 flex items-center gap-2">
                              <span className="text-xs text-slate-500 dark:text-slate-400">Relevance</span>
                              <div className="flex-1 h-1.5 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden max-w-[120px]">
                                <motion.div
                                  className={cn('h-full rounded-full',
                                    suggestion.relevance_score >= 0.8 ? 'bg-emerald-500' :
                                    suggestion.relevance_score >= 0.5 ? 'bg-amber-500' : 'bg-slate-400'
                                  )}
                                  initial={{ width: 0 }}
                                  animate={{ width: `${suggestion.relevance_score * 100}%` }}
                                  transition={{ duration: 0.8, delay: 0.3 }}
                                />
                              </div>
                              <span className="text-xs font-medium text-slate-600 dark:text-slate-300">
                                {Math.round(suggestion.relevance_score * 100)}%
                              </span>
                            </div>
                          )}
                          {suggestion.content_id && (
                            <p className="text-xs text-slate-400 dark:text-slate-500 mt-2 flex items-center gap-1">
                              <MessageSquare className="h-3 w-3" />
                              Content: {suggestion.content_id.slice(0, 8)}…
                            </p>
                          )}
                        </div>
                        <div className="flex items-center gap-2 flex-shrink-0">
                          <Button
                            variant="success"
                            size="sm"
                            leftIcon={<Check className="h-3.5 w-3.5" />}
                            onClick={() => handleAccept(suggestion.id)}
                          >
                            Accept
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            leftIcon={<X className="h-3.5 w-3.5" />}
                            onClick={() => handleDismiss(suggestion.id)}
                          >
                            Dismiss
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )
            })
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}