'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Tag,
  Layers,
  RefreshCw,
  Check,
  X,
  ChevronRight,
  ChevronDown,
  Edit3,
  Save,
  Plus,
  Sparkles,
  AlertCircle,
} from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { useToast } from '@/hooks/useToast'
import { cn } from '@/lib/utils'
import {
  getCategorization,
  updateCategories,
  type CategorizationResult,
  type CategoryTag,
} from '@/lib/api'

interface ContentItem {
  id: string
  title: string
}

export default function CategorizationPanel() {
  const [categorizations, setCategorizations] = useState<CategorizationResult[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editCategories, setEditCategories] = useState<string>('')
  const { showToast } = useToast()

  const fetchCategorizations = useCallback(async () => {
    try {
      setLoading(true)
      const data = await getCategorization()
      setCategorizations(data)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to fetch categorizations'
      showToast(message, 'error')
    } finally {
      setLoading(false)
    }
  }, [showToast])

  useEffect(() => {
    fetchCategorizations()
  }, [fetchCategorizations])

  const handleRefresh = async () => {
    setRefreshing(true)
    await fetchCategorizations()
    setRefreshing(false)
  }

  const handleManualOverride = async (contentId: string, categories: string[]) => {
    try {
      await updateCategories(contentId, { categories })
      setCategorizations(prev =>
        prev.map(c =>
          c.content_id === contentId
            ? { ...c, categories: categories.map((name, i) => ({ name, confidence: 1.0, is_auto: false, order: i })) }
            : c
        )
      )
      setEditingId(null)
      showToast('Manual override saved.', 'success')
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to update categories'
      showToast(message, 'error')
    }
  }

  const startEditing = (cat: CategorizationResult) => {
    setEditingId(cat.content_id)
    setEditCategories(cat.categories.map(c => c.name).join(', '))
  }

  const saveEditing = (cat: CategorizationResult) => {
    const categories = editCategories.split(',').map(s => s.trim()).filter(Boolean)
    handleManualOverride(cat.content_id, categories)
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-emerald-500'
    if (confidence >= 0.5) return 'bg-amber-500'
    return 'bg-rose-500'
  }

  const getConfidenceVariant = (confidence: number): 'success' | 'warning' | 'error' => {
    if (confidence >= 0.8) return 'success'
    if (confidence >= 0.5) return 'warning'
    return 'error'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
          <p className="text-slate-500 dark:text-slate-400">Loading categorizations...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <Tag className="w-6 h-6 text-violet-500" />
            Smart Categorization
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            AI-powered content classification with manual override
          </p>
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

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card variant="glass">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-gradient-to-br from-violet-500/10 to-purple-500/10 dark:from-violet-500/20 dark:to-purple-500/20">
              <Layers className="h-5 w-5 text-violet-600 dark:text-violet-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">{categorizations.length}</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">Categorized</p>
            </div>
          </div>
        </Card>
        <Card variant="glass">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-500/10 to-teal-500/10 dark:from-emerald-500/20 dark:to-teal-500/20">
              <Sparkles className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                {categorizations.reduce((sum, c) => sum + c.categories.filter(t => t.is_auto).length, 0)}
              </p>
              <p className="text-sm text-slate-500 dark:text-slate-400">Auto-tagged</p>
            </div>
          </div>
        </Card>
        <Card variant="glass">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-gradient-to-br from-amber-500/10 to-orange-500/10 dark:from-amber-500/20 dark:to-orange-500/20">
              <Edit3 className="h-5 w-5 text-amber-600 dark:text-amber-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                {categorizations.reduce((sum, c) => sum + c.categories.filter(t => !t.is_auto).length, 0)}
              </p>
              <p className="text-sm text-slate-500 dark:text-slate-400">Manual overrides</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Categorization List */}
      <div className="space-y-3">
        <AnimatePresence>
          {categorizations.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-12"
            >
              <Tag className="h-12 w-12 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
              <p className="text-slate-500 dark:text-slate-400 text-lg font-medium">No categorizations yet</p>
              <p className="text-slate-400 dark:text-slate-500 text-sm mt-1">
                Content will be automatically categorized as it&apos;s created
              </p>
            </motion.div>
          ) : (
            categorizations.map((cat, index) => {
              const isExpanded = expandedId === cat.content_id
              const isEditing = editingId === cat.content_id
              return (
                <motion.div
                  key={cat.content_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                >
                  <Card variant="glass">
                    <CardContent>
                      <button
                        className="w-full flex items-center justify-between"
                        onClick={() => setExpandedId(isExpanded ? null : cat.content_id)}
                      >
                        <div className="flex items-center gap-3">
                          {isExpanded ? (
                            <ChevronDown className="h-4 w-4 text-slate-400" />
                          ) : (
                            <ChevronRight className="h-4 w-4 text-slate-400" />
                          )}
                          <div className="text-left">
                            <h3 className="font-semibold text-slate-900 dark:text-slate-100">
                              {cat.content_title || `Content ${cat.content_id.slice(0, 8)}…`}
                            </h3>
                            <div className="flex items-center gap-2 mt-1 flex-wrap">
                              {cat.categories.slice(0, 3).map((tag, i) => (
                                <Badge
                                  key={i}
                                  variant={tag.is_auto ? 'primary' : 'warning'}
                                  size="sm"
                                  dot
                                >
                                  {tag.name}
                                </Badge>
                              ))}
                              {cat.categories.length > 3 && (
                                <Badge size="sm" variant="default">+{cat.categories.length - 3}</Badge>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {!isEditing && (
                            <Button
                              variant="ghost"
                              size="sm"
                              leftIcon={<Edit3 className="h-3.5 w-3.5" />}
                              onClick={(e) => {
                                e.stopPropagation()
                                startEditing(cat)
                              }}
                            >
                              Override
                            </Button>
                          )}
                        </div>
                      </button>

                      <AnimatePresence>
                        {isExpanded && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.3 }}
                            className="overflow-hidden"
                          >
                            <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-700/50 space-y-3">
                              {/* Category Hierarchy */}
                              <div>
                                <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2 flex items-center gap-1.5">
                                  <Layers className="h-4 w-4 text-violet-500" />
                                  Category Tags
                                </h4>
                                {isEditing ? (
                                  <div className="flex items-center gap-2">
                                    <input
                                      type="text"
                                      value={editCategories}
                                      onChange={e => setEditCategories(e.target.value)}
                                      className="flex-1 px-3 py-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                      placeholder="Enter categories (comma-separated)"
                                    />
                                    <Button
                                      variant="success"
                                      size="sm"
                                      leftIcon={<Save className="h-3.5 w-3.5" />}
                                      onClick={() => saveEditing(cat)}
                                    >
                                      Save
                                    </Button>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      leftIcon={<X className="h-3.5 w-3.5" />}
                                      onClick={() => setEditingId(null)}
                                    >
                                      Cancel
                                    </Button>
                                  </div>
                                ) : (
                                  <div className="space-y-2">
                                    {cat.categories
                                      .sort((a, b) => a.order - b.order)
                                      .map((tag, i) => (
                                        <motion.div
                                          key={i}
                                          initial={{ opacity: 0, x: -10 }}
                                          animate={{ opacity: 1, x: 0 }}
                                          transition={{ delay: i * 0.05 }}
                                          className="flex items-center gap-3 pl-2"
                                        >
                                          <span className="text-slate-300 dark:text-slate-600 text-xs font-mono w-4">
                                            {i + 1}.
                                          </span>
                                          <Badge
                                            variant={tag.is_auto ? 'primary' : 'warning'}
                                            size="sm"
                                          >
                                            {tag.name}
                                          </Badge>
                                          {!tag.is_auto && (
                                            <Badge variant="outline" size="sm">
                                              manual
                                            </Badge>
                                          )}
                                          <div className="flex-1 flex items-center gap-2">
                                            <div className="flex-1 h-1.5 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden max-w-[100px]">
                                              <motion.div
                                                className={cn('h-full rounded-full', getConfidenceColor(tag.confidence))}
                                                initial={{ width: 0 }}
                                                animate={{ width: `${tag.confidence * 100}%` }}
                                                transition={{ duration: 0.6, delay: 0.2 }}
                                              />
                                            </div>
                                            <Badge variant={getConfidenceVariant(tag.confidence)} size="sm">
                                              {Math.round(tag.confidence * 100)}%
                                            </Badge>
                                          </div>
                                        </motion.div>
                                      ))}
                                  </div>
                                )}
                              </div>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
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