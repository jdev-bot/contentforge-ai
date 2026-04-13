'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BarChart3,
  Plus,
  Trash2,
  ChevronDown,
  ChevronUp,
  Download,
  Calendar,
  Filter,
  TrendingDown,
  ArrowRight,
  GripVertical,
  Loader2,
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Input } from '@/components/ui/Input'
import { cn } from '@/lib/utils'
import { useToast } from '@/hooks/useToast'
import {
  createFunnel,
  getFunnel,
  listFunnels,
  trackFunnelEvent,
  getFunnelAnalytics,
  deleteFunnel as deleteFunnelApi,
  FunnelResponse,
  FunnelAnalyticsData,
} from '@/lib/api'

// ── Types ────────────────────────────────────────────────────────

interface FunnelStepInput {
  step_id: string
  name: string
  order: number
  description: string
}

interface FunnelFormData {
  name: string
  description: string
  steps: FunnelStepInput[]
}

// ── Helper ──────────────────────────────────────────────────────

const STEP_COLORS = [
  'from-blue-500 to-blue-600',
  'from-indigo-500 to-indigo-600',
  'from-violet-500 to-violet-600',
  'from-purple-500 to-purple-600',
  'from-fuchsia-500 to-fuchsia-600',
  'from-pink-500 to-pink-600',
  'from-rose-500 to-rose-600',
  'from-red-500 to-red-600',
]

function getConversionColor(rate: number): string {
  if (rate >= 0.7) return 'text-emerald-600 dark:text-emerald-400'
  if (rate >= 0.4) return 'text-amber-600 dark:text-amber-400'
  return 'text-rose-600 dark:text-rose-400'
}

function getConversionBarColor(rate: number): string {
  if (rate >= 0.7) return 'bg-emerald-500'
  if (rate >= 0.4) return 'bg-amber-500'
  return 'bg-rose-500'
}

function formatNumber(num: number): string {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toString()
}

// ── Main Component ───────────────────────────────────────────────

export default function FunnelAnalytics() {
  const { showToast } = useToast()
  const [funnels, setFunnels] = useState<FunnelResponse[]>([])
  const [selectedFunnel, setSelectedFunnel] = useState<FunnelResponse | null>(null)
  const [analytics, setAnalytics] = useState<FunnelAnalyticsData | null>(null)
  const [loading, setLoading] = useState(false)
  const [analyticsLoading, setAnalyticsLoading] = useState(false)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [dateRange, setDateRange] = useState<{ start: string; end: string } | undefined>(undefined)

  // Create form state
  const [formData, setFormData] = useState<FunnelFormData>({
    name: '',
    description: '',
    steps: [
      { step_id: 'awareness', name: 'Awareness', order: 0, description: 'User becomes aware' },
      { step_id: 'interest', name: 'Interest', order: 1, description: 'User shows interest' },
      { step_id: 'consideration', name: 'Consideration', order: 2, description: 'User considers purchase' },
      { step_id: 'conversion', name: 'Conversion', order: 3, description: 'User converts' },
    ],
  })

  const fetchFunnels = useCallback(async () => {
    setLoading(true)
    try {
      const result = await listFunnels()
      setFunnels(result.funnels)
    } catch (err) {
      showToast('Failed to load funnels', 'error')
    } finally {
      setLoading(false)
    }
  }, [showToast])

  useEffect(() => {
    fetchFunnels()
  }, [fetchFunnels])

  const fetchAnalytics = useCallback(async (funnelId: string) => {
    setAnalyticsLoading(true)
    try {
      const result = await getFunnelAnalytics(funnelId, dateRange)
      setAnalytics(result)
    } catch (err) {
      showToast('Failed to load funnel analytics', 'error')
    } finally {
      setAnalyticsLoading(false)
    }
  }, [dateRange, showToast])

  useEffect(() => {
    if (selectedFunnel) {
      fetchAnalytics(selectedFunnel.id)
    }
  }, [selectedFunnel, dateRange, fetchAnalytics])

  const handleCreateFunnel = async () => {
    if (!formData.name.trim()) {
      showToast('Funnel name is required', 'error')
      return
    }
    if (formData.steps.length < 2) {
      showToast('A funnel needs at least 2 steps', 'error')
      return
    }

    try {
      const result = await createFunnel({
        name: formData.name,
        description: formData.description,
        steps: formData.steps,
      })
      showToast('Funnel created successfully!', 'success')
      setShowCreateForm(false)
      setFormData({ name: '', description: '', steps: [] })
      await fetchFunnels()
      setSelectedFunnel(result)
    } catch (err) {
      showToast('Failed to create funnel', 'error')
    }
  }

  const handleDeleteFunnel = async (funnelId: string) => {
    try {
      await deleteFunnelApi(funnelId)
      showToast('Funnel deleted', 'success')
      if (selectedFunnel?.id === funnelId) {
        setSelectedFunnel(null)
        setAnalytics(null)
      }
      await fetchFunnels()
    } catch (err) {
      showToast('Failed to delete funnel', 'error')
    }
  }

  const handleAddStep = () => {
    const newOrder = formData.steps.length
    setFormData({
      ...formData,
      steps: [
        ...formData.steps,
        {
          step_id: `step_${newOrder}`,
          name: `Step ${newOrder + 1}`,
          order: newOrder,
          description: '',
        },
      ],
    })
  }

  const handleRemoveStep = (index: number) => {
    const newSteps = formData.steps
      .filter((_, i) => i !== index)
      .map((s, i) => ({ ...s, order: i }))
    setFormData({ ...formData, steps: newSteps })
  }

  const handleStepChange = (index: number, field: keyof FunnelStepInput, value: string) => {
    const newSteps = [...formData.steps]
    newSteps[index] = { ...newSteps[index], [field]: value }
    setFormData({ ...formData, steps: newSteps })
  }

  const moveStep = (index: number, direction: 'up' | 'down') => {
    const newSteps = [...formData.steps]
    const targetIndex = direction === 'up' ? index - 1 : index + 1
    if (targetIndex < 0 || targetIndex >= newSteps.length) return
    const temp = newSteps[targetIndex]
    newSteps[targetIndex] = newSteps[index]
    newSteps[index] = temp
    // Reassign order
    newSteps.forEach((s, i) => { s.order = i })
    setFormData({ ...formData, steps: newSteps })
  }

  const exportCSV = () => {
    if (!analytics || !selectedFunnel) return

    const rows: string[][] = [
      ['Step', 'Step ID', 'Events', 'Conversion Rate'],
    ]

    const orderedSteps = [...(selectedFunnel.steps || [])].sort((a, b) => a.order - b.order)
    for (const step of orderedSteps) {
      const events = analytics.step_conversions[step.step_id] ?? 0
      const rateKey = Object.keys(analytics.step_conversions).find(k => k.startsWith(step.step_id))
      const rate = rateKey ? analytics.step_conversions[rateKey] : '-'
      rows.push([step.name, step.step_id, String(events), typeof rate === 'number' ? `${(rate * 100).toFixed(1)}%` : String(rate)])
    }

    rows.push([], ['Total Entered', String(analytics.total_entered)])
    rows.push(['Total Completed', String(analytics.total_completed)])
    rows.push(['Overall Conversion', `${(analytics.conversion_rate * 100).toFixed(1)}%`])

    const csv = rows.map(r => r.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `funnel_${selectedFunnel.id}_analytics.csv`
    a.click()
    URL.revokeObjectURL(url)
    showToast('CSV exported', 'success')
  }

  // ── Render ────────────────────────────────────────────────

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-blue-600" />
            Funnel Analytics
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Track conversion funnels and identify drop-off points
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button onClick={() => setShowCreateForm(true)} leftIcon={<Plus className="w-4 h-4" />}>
            Create Funnel
          </Button>
        </div>
      </div>

      {/* Create Funnel Modal */}
      <AnimatePresence>
        {showCreateForm && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
            onClick={(e) => { if (e.target === e.currentTarget) setShowCreateForm(false) }}
          >
            <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto mx-4" variant="elevated">
              <CardHeader>
                <CardTitle>Create New Funnel</CardTitle>
                <CardDescription>Define the steps in your conversion funnel</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                    Funnel Name
                  </label>
                  <Input
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="e.g., Content to Conversion"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Describe the purpose of this funnel..."
                    className="w-full h-20 px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Funnel Steps
                  </label>
                  <div className="space-y-3">
                    {formData.steps.map((step, index) => (
                      <div key={index} className="flex items-start gap-2 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700">
                        <div className="flex flex-col gap-1 pt-2">
                          <button
                            onClick={() => moveStep(index, 'up')}
                            disabled={index === 0}
                            className="text-slate-400 hover:text-slate-600 disabled:opacity-30"
                          >
                            <ChevronUp className="w-3 h-3" />
                          </button>
                          <button
                            onClick={() => moveStep(index, 'down')}
                            disabled={index === formData.steps.length - 1}
                            className="text-slate-400 hover:text-slate-600 disabled:opacity-30"
                          >
                            <ChevronDown className="w-3 h-3" />
                          </button>
                        </div>
                        <div className="flex-1 grid grid-cols-2 gap-2">
                          <Input
                            value={step.name}
                            onChange={(e) => handleStepChange(index, 'name', e.target.value)}
                            placeholder="Step name"
                          />
                          <Input
                            value={step.step_id}
                            onChange={(e) => handleStepChange(index, 'step_id', e.target.value)}
                            placeholder="Step ID"
                          />
                        </div>
                        <Input
                          value={step.description}
                          onChange={(e) => handleStepChange(index, 'description', e.target.value)}
                          placeholder="Description"
                          className="flex-1"
                        />
                        <button
                          onClick={() => handleRemoveStep(index)}
                          className="p-1 text-rose-500 hover:text-rose-700 hover:bg-rose-50 dark:hover:bg-rose-900/20 rounded"
                          disabled={formData.steps.length <= 2}
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleAddStep}
                    className="mt-3"
                    leftIcon={<Plus className="w-3 h-3" />}
                  >
                    Add Step
                  </Button>
                </div>
              </CardContent>
              <CardFooter>
                <div className="flex justify-end gap-3 w-full">
                  <Button variant="outline" onClick={() => setShowCreateForm(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleCreateFunnel}>
                    Create Funnel
                  </Button>
                </div>
              </CardFooter>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Funnel Selector + Date Range */}
      <div className="flex items-center gap-4">
        <div className="flex-1">
          <select
            value={selectedFunnel?.id || ''}
            onChange={(e) => {
              const funnel = funnels.find(f => f.id === e.target.value) || null
              setSelectedFunnel(funnel)
              setAnalytics(null)
            }}
            className="w-full px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
          >
            <option value="">Select a funnel...</option>
            {funnels.map(f => (
              <option key={f.id} value={f.id}>{f.name}</option>
            ))}
          </select>
        </div>
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-slate-400" />
          <select
            value={dateRange ? 'custom' : 'all'}
            onChange={(e) => {
              if (e.target.value === 'all') {
                setDateRange(undefined)
              } else {
                const days = parseInt(e.target.value, 10)
                const end = new Date().toISOString().split('T')[0]
                const start = new Date(Date.now() - days * 86400000).toISOString().split('T')[0]
                setDateRange({ start, end })
              }
            }}
            className="px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
          >
            <option value="all">All time</option>
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
            <option value="365">Last 365 days</option>
          </select>
        </div>
        {analytics && (
          <Button variant="outline" size="sm" onClick={exportCSV} leftIcon={<Download className="w-3 h-3" />}>
            Export CSV
          </Button>
        )}
      </div>

      {/* Loading States */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
        </div>
      )}

      {/* Empty State */}
      {!loading && funnels.length === 0 && !showCreateForm && (
        <Card variant="outline" className="py-12 text-center">
          <BarChart3 className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">No funnels yet</h3>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-2 mb-4">
            Create your first funnel to start tracking conversions
          </p>
          <Button onClick={() => setShowCreateForm(true)} leftIcon={<Plus className="w-4 h-4" />}>
            Create Funnel
          </Button>
        </Card>
      )}

      {/* Funnel Visualization */}
      {selectedFunnel && analyticsLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
        </div>
      )}

      {selectedFunnel && analytics && !analyticsLoading && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
          {/* Overall Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card variant="glass">
              <div className="text-center py-4">
                <p className="text-sm text-slate-500 dark:text-slate-400">Total Entered</p>
                <p className="text-3xl font-bold text-slate-900 dark:text-slate-100 mt-1">
                  {formatNumber(analytics.total_entered)}
                </p>
              </div>
            </Card>
            <Card variant="glass">
              <div className="text-center py-4">
                <p className="text-sm text-slate-500 dark:text-slate-400">Total Completed</p>
                <p className="text-3xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">
                  {formatNumber(analytics.total_completed)}
                </p>
              </div>
            </Card>
            <Card variant="glass">
              <div className="text-center py-4">
                <p className="text-sm text-slate-500 dark:text-slate-400">Conversion Rate</p>
                <p className={cn('text-3xl font-bold mt-1', getConversionColor(analytics.conversion_rate))}>
                  {(analytics.conversion_rate * 100).toFixed(1)}%
                </p>
              </div>
            </Card>
          </div>

          {/* Funnel Steps Visualization */}
          <Card variant="elevated">
            <CardHeader>
              <CardTitle>Funnel Steps</CardTitle>
              <CardDescription>
                Step-by-step conversion for {selectedFunnel.name}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {[...(selectedFunnel.steps || [])]
                  .sort((a, b) => a.order - b.order)
                  .map((step, index) => {
                    const events = analytics.step_conversions[step.step_id] ?? 0
                    const maxEvents = Math.max(...Object.values(analytics.step_conversions).map(Number), 1)
                    const widthPercent = (events / maxEvents) * 100
                    const isLast = index === (selectedFunnel.steps?.length ?? 0) - 1
                    const nextStepId = !isLast ? selectedFunnel.steps?.[index + 1]?.id : null
                    const stepRateKey = nextStepId ? `${step.step_id}_to_${nextStepId}` : null
                    const stepRate = stepRateKey ? analytics.step_conversions[stepRateKey] : null

                    return (
                      <div key={step.step_id}>
                        <div className="flex items-center gap-4">
                          <div className="w-28 text-right">
                            <p className="text-sm font-medium text-slate-900 dark:text-slate-100 truncate">
                              {step.name}
                            </p>
                            <p className="text-xs text-slate-500">{formatNumber(events)} events</p>
                          </div>
                          <div className="flex-1">
                            <div className="relative h-12 bg-slate-100 dark:bg-slate-700 rounded-lg overflow-hidden">
                              <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${widthPercent}%` }}
                                transition={{ duration: 0.6, delay: index * 0.1 }}
                                className={cn(
                                  'h-full rounded-lg bg-gradient-to-r',
                                  STEP_COLORS[index % STEP_COLORS.length],
                                )}
                              />
                              {events > 0 && (
                                <div className="absolute inset-0 flex items-center justify-center">
                                  <span className="text-white font-semibold text-sm drop-shadow">
                                    {formatNumber(events)}
                                  </span>
                                </div>
                              )}
                            </div>
                          </div>
                          {stepRate !== null && stepRate !== undefined && (
                            <div className="w-24 text-right">
                              <p className={cn('text-sm font-medium', getConversionColor(stepRate))}>
                                {(stepRate * 100).toFixed(1)}%
                              </p>
                              <div className="h-1.5 bg-slate-200 dark:bg-slate-600 rounded-full mt-1 overflow-hidden">
                                <div
                                  className={cn('h-full rounded-full transition-all', getConversionBarColor(stepRate))}
                                  style={{ width: `${stepRate * 100}%` }}
                                />
                              </div>
                            </div>
                          )}
                          {!isLast && (
                            <div className="w-6 text-center">
                              <ArrowRight className="w-4 h-4 text-slate-400" />
                            </div>
                          )}
                        </div>
                        {!isLast && (
                          <div className="flex items-center justify-center py-1">
                            <TrendingDown className="w-3 h-3 text-slate-400" />
                          </div>
                        )}
                      </div>
                    )
                  })}
              </div>
            </CardContent>
          </Card>

          {/* Drop-off Analysis */}
          {analytics.drop_off_steps && analytics.drop_off_steps.length > 0 && (
            <Card variant="elevated">
              <CardHeader>
                <CardTitle>Drop-off Analysis</CardTitle>
                <CardDescription>Steps with the highest user drop-off</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analytics.drop_off_steps.map((dropItem: { step_id: string; step_name: string; drop_off_rate: number }, dropIndex: number) => (
                    <div key={dropItem.step_id} className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <p className="font-medium text-slate-900 dark:text-slate-100">
                            {dropItem.step_name}
                          </p>
                          <p className="text-xs text-slate-500">Step ID: {dropItem.step_id}</p>
                        </div>
                        <Badge variant={dropItem.drop_off_rate >= 0.5 ? 'error' : dropItem.drop_off_rate >= 0.3 ? 'warning' : 'default'}>
                          {(dropItem.drop_off_rate * 100).toFixed(1)}% drop-off
                        </Badge>
                      </div>
                      <div className="text-sm text-slate-600 dark:text-slate-400">
                        {(dropItem.drop_off_rate * 100).toFixed(1)}% of users dropped off at this step
                      </div>
                      <div className="mt-2 h-2 bg-slate-200 dark:bg-slate-600 rounded-full overflow-hidden">
                        <div className="h-full bg-rose-500 rounded-full" style={{ width: `${dropItem.drop_off_rate * 100}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Funnel Actions */}
          <Card variant="outline">
            <CardContent className="py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Filter className="w-4 h-4 text-slate-400" />
                  <span className="text-sm text-slate-500">
                    Viewing data for the selected period
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => handleDeleteFunnel(selectedFunnel.id)}
                    leftIcon={<Trash2 className="w-3 h-3" />}
                  >
                    Delete Funnel
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  )
}