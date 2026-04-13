'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
} from 'recharts'
import {
  PieChart as RechartsPieChart,
  Pie,
} from 'recharts'
import {
  Target,
  TrendingUp,
  ArrowUpRight,
  ArrowDownRight,
  BarChart3,
  Clock,
  Layers,
  Plus,
  Loader2,
  Zap,
  MousePointerClick,
  Mail,
  Share2,
  Search,
  Globe,
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Input } from '@/components/ui/Input'
import { cn } from '@/lib/utils'
import { useToast } from '@/hooks/useToast'
import {
  recordTouchpoint,
  getTouchpoints,
  calculateAttribution,
  getChannelPerformance,
  type AttributionTouchpoint,
  type AttributionResult,
  type AttributionModel,
} from '@/lib/api'

// ── Types ────────────────────────────────────────────────────────

interface ModelOption {
  value: AttributionModel
  label: string
  description: string
  icon: React.ReactNode
}

// ── Constants ────────────────────────────────────────────────────

const MODEL_OPTIONS: ModelOption[] = [
  {
    value: 'first_touch',
    label: 'First Touch',
    description: '100% credit to first interaction',
    icon: <Zap className="w-4 h-4" />,
  },
  {
    value: 'last_touch',
    label: 'Last Touch',
    description: '100% credit to last interaction',
    icon: <MousePointerClick className="w-4 h-4" />,
  },
  {
    value: 'linear',
    label: 'Linear',
    description: 'Equal credit across all touches',
    icon: <Layers className="w-4 h-4" />,
  },
  {
    value: 'time_decay',
    label: 'Time Decay',
    description: 'More credit to recent touches',
    icon: <Clock className="w-4 h-4" />,
  },
  {
    value: 'position_based',
    label: 'Position-Based',
    description: 'U-shaped: first & last get 40%',
    icon: <Target className="w-4 h-4" />,
  },
]

const CHANNEL_ICONS: Record<string, React.ReactNode> = {
  organic: <Search className="w-5 h-5" />,
  email: <Mail className="w-5 h-5" />,
  social: <Share2 className="w-5 h-5" />,
  paid: <Globe className="w-5 h-5" />,
  referral: <ArrowUpRight className="w-5 h-5" />,
  direct: <MousePointerClick className="w-5 h-5" />,
}

const CHANNEL_COLORS: Record<string, string> = {
  organic: '#3b82f6',
  email: '#8b5cf6',
  social: '#f59e0b',
  paid: '#ef4444',
  referral: '#10b981',
  direct: '#6366f1',
}

const DEFAULT_CHANNEL_COLOR = '#94a3b8'

// ── Main Component ───────────────────────────────────────────────

export default function AttributionDashboard() {
  const { showToast } = useToast()
  const [selectedModel, setSelectedModel] = useState<AttributionModel>('first_touch')
  const [contentId, setContentId] = useState('')
  const [attributionResults, setAttributionResults] = useState<AttributionResult[]>([])
  const [touchpoints, setTouchpoints] = useState<AttributionTouchpoint[]>([])
  const [channelPerformance, setChannelPerformance] = useState<AttributionResult[]>([])
  const [loading, setLoading] = useState(false)
  const [channelLoading, setChannelLoading] = useState(false)

  // Touchpoint form state
  const [showTouchpointForm, setShowTouchpointForm] = useState(false)
  const [tpChannel, setTpChannel] = useState('')
  const [tpSource, setTpSource] = useState('')
  const [tpCampaign, setTpCampaign] = useState('')

  // Fetch channel performance on mount
  useEffect(() => {
    const fetchChannels = async () => {
      setChannelLoading(true)
      try {
        const result = await getChannelPerformance()
        setChannelPerformance(result)
      } catch {
        // silently fail - may not have data yet
      } finally {
        setChannelLoading(false)
      }
    }
    fetchChannels()
  }, [])

  const handleCalculateAttribution = useCallback(async () => {
    if (!contentId.trim()) {
      showToast('Please enter a content ID', 'error')
      return
    }

    setLoading(true)
    try {
      const [attrResults, tpData] = await Promise.all([
        calculateAttribution(contentId, selectedModel),
        getTouchpoints(contentId),
      ])
      setAttributionResults(attrResults)
      setTouchpoints(tpData)
    } catch (err) {
      showToast('Failed to calculate attribution', 'error')
    } finally {
      setLoading(false)
    }
  }, [contentId, selectedModel, showToast])

  const handleRecordTouchpoint = async () => {
    if (!contentId.trim()) {
      showToast('Please enter a content ID', 'error')
      return
    }
    if (!tpChannel.trim()) {
      showToast('Please enter a channel', 'error')
      return
    }

    try {
      await recordTouchpoint({
        content_id: contentId,
        channel: tpChannel,
        source: tpSource,
        campaign: tpCampaign,
      })
      showToast('Touchpoint recorded!', 'success')
      setShowTouchpointForm(false)
      setTpChannel('')
      setTpSource('')
      setTpCampaign('')
      // Refresh data
      if (contentId) {
        handleCalculateAttribution()
      }
      // Refresh channel performance
      const result = await getChannelPerformance()
      setChannelPerformance(result)
    } catch {
      showToast('Failed to record touchpoint', 'error')
    }
  }

  // ── Render ────────────────────────────────────────────────

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <Target className="w-6 h-6 text-violet-600" />
            Attribution Dashboard
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Multi-touch attribution modeling for content conversions
          </p>
        </div>
        <Button
          onClick={() => setShowTouchpointForm(true)}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          Add Touchpoint
        </Button>
      </div>

      {/* Add Touchpoint Modal */}
      <AnimatePresence>
        {showTouchpointForm && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
            onClick={(e) => { if (e.target === e.currentTarget) setShowTouchpointForm(false) }}
          >
            <Card className="w-full max-w-md mx-4" variant="elevated">
              <CardHeader>
                <CardTitle>Record Touchpoint</CardTitle>
                <CardDescription>Add a marketing touchpoint for content attribution</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                    Content ID
                  </label>
                  <Input
                    value={contentId}
                    onChange={(e) => setContentId(e.target.value)}
                    placeholder="Enter content ID"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                    Channel *
                  </label>
                  <select
                    value={tpChannel}
                    onChange={(e) => setTpChannel(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
                  >
                    <option value="">Select channel...</option>
                    <option value="organic">Organic Search</option>
                    <option value="email">Email</option>
                    <option value="social">Social Media</option>
                    <option value="paid">Paid Advertising</option>
                    <option value="referral">Referral</option>
                    <option value="direct">Direct</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                    Source
                  </label>
                  <Input
                    value={tpSource}
                    onChange={(e) => setTpSource(e.target.value)}
                    placeholder="e.g., google, newsletter"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                    Campaign
                  </label>
                  <Input
                    value={tpCampaign}
                    onChange={(e) => setTpCampaign(e.target.value)}
                    placeholder="e.g., spring-launch-2024"
                  />
                </div>
              </CardContent>
              <CardFooter>
                <div className="flex justify-end gap-3 w-full">
                  <Button variant="outline" onClick={() => setShowTouchpointForm(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleRecordTouchpoint}>
                    Record Touchpoint
                  </Button>
                </div>
              </CardFooter>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Channel Performance Cards */}
      <div>
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-3">
          Channel Performance
        </h3>
        {channelLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-6 h-6 text-violet-500 animate-spin" />
          </div>
        ) : channelPerformance.length === 0 ? (
          <Card variant="outline" className="py-8 text-center">
            <Globe className="w-10 h-10 text-slate-300 mx-auto mb-3" />
            <p className="text-sm text-slate-500">No channel data yet. Add touchpoints to see performance.</p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {channelPerformance.map((channel) => (
              <Card key={channel.channel} variant="glass" className="group hover:shadow-xl transition-all">
                <CardContent className="py-4">
                  <div className="flex items-center gap-3 mb-4">
                    <div
                      className="p-2.5 rounded-xl"
                      style={{ backgroundColor: `${CHANNEL_COLORS[channel.channel] || DEFAULT_CHANNEL_COLOR}15` }}
                    >
                      <div style={{ color: CHANNEL_COLORS[channel.channel] || DEFAULT_CHANNEL_COLOR }}>
                        {CHANNEL_ICONS[channel.channel] || <Globe className="w-5 h-5" />}
                      </div>
                    </div>
                    <div>
                      <p className="font-semibold text-slate-900 dark:text-slate-100 capitalize">
                        {channel.channel}
                      </p>
                      <p className="text-xs text-slate-500">
                        {channel.total_touchpoints} touchpoints
                      </p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="text-center p-2 rounded-lg bg-slate-50 dark:bg-slate-800">
                      <p className="text-lg font-bold text-slate-900 dark:text-slate-100">
                        {channel.total_touchpoints}
                      </p>
                      <p className="text-xs text-slate-500">Touchpoints</p>
                    </div>
                    <div className="text-center p-2 rounded-lg bg-slate-50 dark:bg-slate-800">
                      <p className="text-lg font-bold text-emerald-600 dark:text-emerald-400">
                        {channel.total_conversions}
                      </p>
                      <p className="text-xs text-slate-500">Conversions</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Attribution Calculator */}
      <Card variant="elevated">
        <CardHeader>
          <CardTitle>Attribution Calculator</CardTitle>
          <CardDescription>Select a model and content to calculate attribution weights</CardDescription>
        </CardHeader>
        <CardContent>
          {/* Model Selector */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
              Attribution Model
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
              {MODEL_OPTIONS.map((model) => (
                <button
                  key={model.value}
                  onClick={() => setSelectedModel(model.value)}
                  className={cn(
                    'flex flex-col items-center gap-1.5 p-3 rounded-xl border-2 transition-all text-center',
                    selectedModel === model.value
                      ? 'border-violet-500 bg-violet-50 dark:bg-violet-900/20 shadow-md'
                      : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600',
                  )}
                >
                  <div className={cn(
                    'p-2 rounded-lg',
                    selectedModel === model.value
                      ? 'text-violet-600 bg-violet-100 dark:bg-violet-800/30'
                      : 'text-slate-400 bg-slate-100 dark:bg-slate-700',
                  )}>
                    {model.icon}
                  </div>
                  <span className={cn(
                    'text-sm font-medium',
                    selectedModel === model.value
                      ? 'text-violet-700 dark:text-violet-300'
                      : 'text-slate-600 dark:text-slate-400',
                  )}>
                    {model.label}
                  </span>
                  <span className="text-xs text-slate-400 hidden sm:block">
                    {model.description}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Content ID Input */}
          <div className="flex items-end gap-3">
            <div className="flex-1">
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Content ID
              </label>
              <Input
                value={contentId}
                onChange={(e) => setContentId(e.target.value)}
                placeholder="Enter content ID to analyze"
                onKeyDown={(e) => { if (e.key === 'Enter') handleCalculateAttribution() }}
              />
            </div>
            <Button
              onClick={handleCalculateAttribution}
              disabled={loading}
              leftIcon={loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <BarChart3 className="w-4 h-4" />}
            >
              Calculate
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Attribution Results */}
      {attributionResults.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
          {/* Attribution Weight Bars */}
          <Card variant="elevated">
            <CardHeader>
              <CardTitle>Attribution Weights</CardTitle>
              <CardDescription>
                {MODEL_OPTIONS.find(m => m.value === selectedModel)?.label} model results
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {attributionResults.map((result, index) => {
                  const color = CHANNEL_COLORS[result.channel] || DEFAULT_CHANNEL_COLOR
                  return (
                    <div key={`${result.channel}-${result.source}-${index}`}>
                      <div className="flex items-center justify-between mb-1.5">
                        <div className="flex items-center gap-2">
                          <div
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: color }}
                          />
                          <span className="font-medium text-slate-900 dark:text-slate-100 capitalize">
                            {result.channel}
                          </span>
                          {result.source && (
                            <span className="text-sm text-slate-500">({result.source})</span>
                          )}
                        </div>
                        <span className="font-semibold text-slate-900 dark:text-slate-100">
                          {(result.attribution_weight * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="h-3 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${result.attribution_weight * 100}%` }}
                          transition={{ duration: 0.5, delay: index * 0.1 }}
                          className="h-full rounded-full"
                          style={{ backgroundColor: color }}
                        />
                      </div>
                      <div className="flex items-center gap-4 mt-1.5 text-xs text-slate-500">
                        <span>{result.conversion_count} conversion{result.conversion_count !== 1 ? 's' : ''}</span>
                        {result.revenue_attributed > 0 && (
                          <span>${result.revenue_attributed.toFixed(2)} revenue</span>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          {/* Pie Chart Visualization */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card variant="elevated">
              <CardHeader>
                <CardTitle>Weight Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsPieChart>
                      <Pie
                        data={attributionResults.map(r => ({
                          name: r.channel,
                          value: parseFloat((r.attribution_weight * 100).toFixed(1)),
                          color: CHANNEL_COLORS[r.channel] || DEFAULT_CHANNEL_COLOR,
                        }))}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={90}
                        paddingAngle={2}
                        dataKey="value"
                      >
                        {attributionResults.map((result, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={CHANNEL_COLORS[result.channel] || DEFAULT_CHANNEL_COLOR}
                          />
                        ))}
                      </Pie>
                      <Tooltip
                        formatter={(value) => [`${value}%`, 'Weight']}
                        contentStyle={{
                          backgroundColor: 'rgba(255, 255, 255, 0.95)',
                          borderRadius: '8px',
                          border: '1px solid #e2e8f0',
                        }}
                      />
                    </RechartsPieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Touchpoint Timeline */}
            <Card variant="elevated">
              <CardHeader>
                <CardTitle>Touchpoint Timeline</CardTitle>
                <CardDescription>
                  {touchpoints.length} touchpoint{touchpoints.length !== 1 ? 's' : ''} recorded
                </CardDescription>
              </CardHeader>
              <CardContent>
                {touchpoints.length === 0 ? (
                  <div className="flex items-center justify-center h-48 text-sm text-slate-500">
                    No touchpoints found for this content
                  </div>
                ) : (
                  <div className="space-y-3 max-h-64 overflow-y-auto">
                    {touchpoints.map((tp, index) => (
                      <div key={tp.id || index} className="flex items-start gap-3 p-2 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                        <div
                          className="w-2.5 h-2.5 rounded-full mt-1.5 flex-shrink-0"
                          style={{ backgroundColor: CHANNEL_COLORS[tp.channel] || DEFAULT_CHANNEL_COLOR }}
                        />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <span className="font-medium text-sm text-slate-900 dark:text-slate-100 capitalize">
                              {tp.channel}
                            </span>
                            <span className="text-xs text-slate-500">
                              {tp.created_at ? new Date(tp.created_at).toLocaleDateString() : ''}
                            </span>
                          </div>
                          {tp.source && (
                            <p className="text-xs text-slate-500 truncate">Source: {tp.source}</p>
                          )}
                          {tp.campaign && (
                            <p className="text-xs text-slate-500 truncate">Campaign: {tp.campaign}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Revenue Attribution Breakdown */}
          {attributionResults.some(r => r.revenue_attributed > 0) && (
            <Card variant="elevated">
              <CardHeader>
                <CardTitle>Revenue Attribution Breakdown</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {attributionResults
                    .filter(r => r.revenue_attributed > 0)
                    .sort((a, b) => b.revenue_attributed - a.revenue_attributed)
                    .map((result, index) => {
                      const totalRevenue = attributionResults.reduce((sum, r) => sum + r.revenue_attributed, 0)
                      const percent = totalRevenue > 0 ? (result.revenue_attributed / totalRevenue) * 100 : 0
                      const color = CHANNEL_COLORS[result.channel] || DEFAULT_CHANNEL_COLOR

                      return (
                        <div key={`revenue-${index}`} className="flex items-center gap-4">
                          <div className="w-28">
                            <div className="flex items-center gap-2">
                              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
                              <span className="font-medium text-sm capitalize text-slate-900 dark:text-slate-100">
                                {result.channel}
                              </span>
                            </div>
                          </div>
                          <div className="flex-1">
                            <div className="h-4 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                              <div
                                className="h-full rounded-full transition-all duration-500"
                                style={{ width: `${percent}%`, backgroundColor: color }}
                              />
                            </div>
                          </div>
                          <div className="w-24 text-right">
                            <span className="font-semibold text-slate-900 dark:text-slate-100">
                              ${result.revenue_attributed.toFixed(2)}
                            </span>
                          </div>
                          <div className="w-16 text-right">
                            <span className="text-sm text-slate-500">{percent.toFixed(1)}%</span>
                          </div>
                        </div>
                      )
                    })}
                </div>
              </CardContent>
            </Card>
          )}
        </motion.div>
      )}
    </div>
  )
}