'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion } from 'framer-motion'
import {
  BarChart3,
  TrendingUp,
  Users,
  ArrowRight,
  RefreshCw,
  Filter,
  Calendar,
  Target,
  Eye,
  MousePointerClick,
  Share2,
  DollarSign,
} from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { useToast } from '@/hooks/useToast'
import { cn } from '@/lib/utils'
import {
  getPerformanceOverview,
  getPerformanceFunnel,
  getPerformanceCohorts,
  getPerformanceAttribution,
  getPerformanceTrend,
  type PerformanceOverview,
  type FunnelStage,
  type CohortData,
  type AttributionData,
  type TrendDataPoint,
} from '@/lib/api'
import { formatApiError } from '@/lib/api'

const COLORS = ['#6366f1', '#8b5cf6', '#a78bfa', '#c4b5fd', '#3b82f6', '#60a5fa', '#93c5fd', '#2563eb']

const FUNNEL_COLORS = ['#3b82f6', '#6366f1', '#8b5cf6', '#a78bfa']

export default function PerformanceAnalytics() {
  const [overview, setOverview] = useState<PerformanceOverview | null>(null)
  const [funnel, setFunnel] = useState<FunnelStage[]>([])
  const [cohorts, setCohorts] = useState<CohortData[]>([])
  const [attribution, setAttribution] = useState<AttributionData[]>([])
  const [trend, setTrend] = useState<TrendDataPoint[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [dateRange, setDateRange] = useState<'7d' | '30d' | '90d'>('30d')
  const { showToast } = useToast()

  const fetchData = useCallback(async () => {
    try {
      setLoading(true)
      const [ov, fn, co, at, tr] = await Promise.all([
        getPerformanceOverview(),
        getPerformanceFunnel(),
        getPerformanceCohorts(),
        getPerformanceAttribution(),
        getPerformanceTrend(dateRange === '7d' ? 7 : dateRange === '30d' ? 30 : 90),
      ])
      setOverview(ov)
      setFunnel(fn)
      setCohorts(co)
      setAttribution(at)
      setTrend(tr)
    } catch (err: unknown) {
      const message = formatApiError(err, 'Failed to fetch performance data')
      showToast(message, 'error')
    } finally {
      setLoading(false)
    }
  }, [dateRange, showToast])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const handleRefresh = async () => {
    setRefreshing(true)
    await fetchData()
    setRefreshing(false)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
          <p className="text-slate-500 dark:text-slate-400">Loading analytics...</p>
        </div>
      </div>
    )
  }

  const maxFunnelValue = Math.max(...funnel.map(s => s.count), 1)

  return (
    <div className="space-y-6">
      {/* Header */}
      <PageHeader
        title="Performance Analytics"
        description="Content performance overview and insights"
        icon={<BarChart3 className="w-5 h-5 text-blue-500" />}
        actions={
          <div className="flex items-center gap-3">
            {/* Date Range Selector */}
            <div className="flex items-center bg-white/70 dark:bg-slate-800/70 backdrop-blur-xl rounded-xl border border-slate-200 dark:border-slate-700 p-1">
              {(['7d', '30d', '90d'] as const).map(range => (
                <button
                  key={range}
                  onClick={() => setDateRange(range)}
                  className={cn(
                    'px-3 py-1.5 text-xs font-medium rounded-lg transition-all',
                    dateRange === range
                      ? 'bg-blue-600 text-white shadow-sm'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100'
                  )}
                >
                  {range}
                </button>
              ))}
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

      {/* Overview Stats */}
      {overview && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0 }}>
            <Card variant="glass">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500/10 to-violet-500/10 dark:from-blue-500/20 dark:to-violet-500/20">
                  <Eye className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                    {overview.total_views.toLocaleString()}
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Total Views</p>
                </div>
              </div>
            </Card>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
            <Card variant="glass">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-500/10 to-teal-500/10 dark:from-emerald-500/20 dark:to-teal-500/20">
                  <MousePointerClick className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                    {(overview.engagement_rate * 100).toFixed(1)}%
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Engagement Rate</p>
                </div>
              </div>
            </Card>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <Card variant="glass">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-gradient-to-br from-amber-500/10 to-orange-500/10 dark:from-amber-500/20 dark:to-orange-500/20">
                  <Share2 className="h-5 w-5 text-amber-600 dark:text-amber-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                    {overview.total_shares.toLocaleString()}
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Total Shares</p>
                </div>
              </div>
            </Card>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
            <Card variant="glass">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-gradient-to-br from-violet-500/10 to-fuchsia-500/10 dark:from-violet-500/20 dark:to-fuchsia-500/20">
                  <DollarSign className="h-5 w-5 text-violet-600 dark:text-violet-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                    {(overview.conversion_rate * 100).toFixed(1)}%
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Conversion Rate</p>
                </div>
              </div>
            </Card>
          </motion.div>
        </div>
      )}

      {/* Funnel Visualization */}
      <Card variant="glass">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5 text-violet-500" />
            Content Funnel
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {funnel.map((stage, i) => {
              const widthPercent = (stage.count / maxFunnelValue) * 100
              const conversionFromPrev = i > 0 && funnel[i - 1].count > 0
                ? ((stage.count / funnel[i - 1].count) * 100).toFixed(1)
                : '100'
              return (
                <motion.div
                  key={stage.stage}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="flex items-center gap-4"
                >
                  <div className="w-24 text-right">
                    <p className="text-sm font-medium text-slate-900 dark:text-slate-100">{stage.stage}</p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">{stage.count.toLocaleString()}</p>
                  </div>
                  <div className="flex-1 h-10 bg-slate-100 dark:bg-slate-800 rounded-xl overflow-hidden relative">
                    <motion.div
                      className={cn('h-full rounded-xl', `bg-gradient-to-r from-blue-500 to-violet-500`)}
                      style={{ opacity: 1 - i * 0.15 }}
                      initial={{ width: 0 }}
                      animate={{ width: `${widthPercent}%` }}
                      transition={{ duration: 0.8, delay: 0.3 + i * 0.1 }}
                    />
                  </div>
                  {i > 0 && (
                    <div className="w-16 text-center">
                      <Badge variant={Number(conversionFromPrev) >= 50 ? 'success' : Number(conversionFromPrev) >= 25 ? 'warning' : 'error'} size="sm">
                        {conversionFromPrev}%
                      </Badge>
                    </div>
                  )}
                </motion.div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Time-Series Performance Trends */}
      <Card variant="glass">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-blue-500" />
            Performance Trends
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trend}>
                <defs>
                  <linearGradient id="viewsGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="engagementGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" className="dark:opacity-20" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="#94a3b8" />
                <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" />
                <RechartsTooltip
                  contentStyle={{
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    border: '1px solid rgba(148, 163, 184, 0.2)',
                    borderRadius: '12px',
                    color: '#f1f5f9',
                  }}
                />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="views"
                  stroke="#3b82f6"
                  fill="url(#viewsGradient)"
                  strokeWidth={2}
                  name="Views"
                />
                <Area
                  type="monotone"
                  dataKey="engagement"
                  stroke="#8b5cf6"
                  fill="url(#engagementGradient)"
                  strokeWidth={2}
                  name="Engagement"
                />
                {trend.length > 0 && 'conversions' in trend[0] && (
                  <Area
                    type="monotone"
                    dataKey="conversions"
                    stroke="#10b981"
                    fill="transparent"
                    strokeWidth={2}
                    name="Conversions"
                    strokeDasharray="5 5"
                  />
                )}
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Cohort Comparison + Attribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cohort Comparison */}
        <Card variant="glass">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5 text-emerald-500" />
              Cohort Comparison
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={cohorts}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" className="dark:opacity-20" />
                  <XAxis dataKey="cohort" tick={{ fontSize: 11 }} stroke="#94a3b8" />
                  <YAxis tick={{ fontSize: 11 }} stroke="#94a3b8" />
                  <RechartsTooltip
                    contentStyle={{
                      backgroundColor: 'rgba(15, 23, 42, 0.9)',
                      border: '1px solid rgba(148, 163, 184, 0.2)',
                      borderRadius: '12px',
                      color: '#f1f5f9',
                    }}
                  />
                  <Bar dataKey="engagement" fill="#6366f1" radius={[6, 6, 0, 0]} name="Engagement" />
                  <Bar dataKey="retention" fill="#8b5cf6" radius={[6, 6, 0, 0]} name="Retention" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Attribution Breakdown */}
        <Card variant="glass">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-amber-500" />
              Attribution Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={attribution}
                    dataKey="value"
                    nameKey="source"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    innerRadius={40}
                    strokeWidth={2}
                    stroke="rgba(15, 23, 42, 0.8)"
                  >
                    {attribution.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip
                    contentStyle={{
                      backgroundColor: 'rgba(15, 23, 42, 0.9)',
                      border: '1px solid rgba(148, 163, 184, 0.2)',
                      borderRadius: '12px',
                      color: '#f1f5f9',
                    }}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}