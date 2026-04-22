'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion } from 'framer-motion'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import {
  Award,
  BookOpen,
  Search,
  Heart,
  SpellCheck,
  Palette,
  TrendingUp,
  Lightbulb,
  CheckCircle2,
  Loader2,
  BarChart3,
  Zap,
} from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { cn } from '@/lib/utils'
import { useToast } from '@/hooks/useToast'
import {
  analyzeContentQuality,
  getQualityScore,
  getQualityScoreHistory,
  batchAnalyzeQuality,
  QualityScoreResponse,
  QualityHistoryResponse,
} from '@/lib/api'

interface QualityDashboardProps {
  contentId?: string
}

/** Dimension metadata derived from the flat QualityScoreResponse fields */
const DIMENSIONS = [
  { key: 'readability', label: 'Readability', icon: <BookOpen className="w-4 h-4" />, color: '#3b82f6' },
  { key: 'seo', label: 'SEO', icon: <Search className="w-4 h-4" />, color: '#8b5cf6' },
  { key: 'engagement', label: 'Engagement', icon: <Heart className="w-4 h-4" />, color: '#f59e0b' },
  { key: 'grammar', label: 'Grammar', icon: <SpellCheck className="w-4 h-4" />, color: '#10b981' },
  { key: 'brand', label: 'Brand', icon: <Palette className="w-4 h-4" />, color: '#ec4899' },
] as const

// Circular gauge component
function QualityGauge({ score, size = 180 }: { score: number; size?: number }) {
  const strokeWidth = 12
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const strokeDashoffset = circumference - (score / 100) * circumference

  const getColor = (s: number) => {
    if (s >= 80) return '#10b981'
    if (s >= 60) return '#3b82f6'
    if (s >= 40) return '#f59e0b'
    return '#ef4444'
  }

  const getLabel = (s: number) => {
    if (s >= 80) return 'Excellent'
    if (s >= 60) return 'Good'
    if (s >= 40) return 'Needs Work'
    return 'Poor'
  }

  const color = getColor(score)

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-slate-200 dark:text-slate-700"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          className="transition-all duration-1000 ease-out"
          style={{
            filter: `drop-shadow(0 0 8px ${color}40)`,
          }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-4xl font-bold text-slate-900 dark:text-slate-100">
          {Math.round(score)}
        </span>
        <span className="text-sm font-medium" style={{ color }}>
          {getLabel(score)}
        </span>
      </div>
    </div>
  )
}

// Dimension score bar
function DimensionBar({
  label,
  score,
  icon,
  color,
}: {
  label: string
  score: number
  icon: React.ReactNode
  color: string
}) {
  const percentage = Math.min(Math.max(score, 0), 100)

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300">
          <span style={{ color }}>{icon}</span>
          <span>{label}</span>
        </div>
        <span className="text-sm font-semibold text-slate-900 dark:text-slate-100">
          {score}<span className="text-slate-400">/100</span>
        </span>
      </div>
      <div className="h-2.5 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
        />
      </div>
    </div>
  )
}

export default function QualityDashboard({ contentId }: QualityDashboardProps) {
  const [qualityResult, setQualityResult] = useState<QualityScoreResponse | null>(null)
  const [historyData, setHistoryData] = useState<QualityScoreResponse[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [batchProgress, setBatchProgress] = useState<{ completed: number; total: number } | null>(null)
  const { showToast } = useToast()

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      if (contentId) {
        const [result, hist] = await Promise.all([
          getQualityScore(contentId).catch(() => null),
          getQualityScoreHistory(contentId).catch(() => null),
        ])
        setQualityResult(result)
        setHistoryData(hist?.history ?? [])
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load quality data')
    } finally {
      setIsLoading(false)
    }
  }, [contentId])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const handleAnalyze = async () => {
    if (!contentId) return
    try {
      setIsAnalyzing(true)
      const result = await analyzeContentQuality(contentId)
      setQualityResult(result)
      showToast('Quality analysis completed', 'success')
    } catch {
      showToast('Failed to analyze quality', 'error')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleBatchAnalyze = async () => {
    if (!contentId) {
      showToast('No content selected for batch analysis', 'error')
      return
    }
    try {
      setIsAnalyzing(true)
      setBatchProgress({ completed: 0, total: 1 })
      // Use real batch API — analyze the current content
      const results = await batchAnalyzeQuality([{ content_id: contentId, text: '' }])
      if (results.length > 0) {
        setQualityResult(results[0])
      }
      setBatchProgress({ completed: 1, total: 1 })
      setTimeout(() => setBatchProgress(null), 800)
      showToast('Batch analysis completed', 'success')
    } catch {
      setBatchProgress(null)
      showToast('Batch analysis failed', 'error')
    } finally {
      setIsAnalyzing(false)
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="flex items-center justify-center h-64 rounded-xl animate-pulse bg-slate-200 dark:bg-slate-800" />
          <div className="lg:col-span-2 space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-10 rounded-lg animate-pulse bg-slate-200 dark:bg-slate-800" />
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Quality Dashboard"
          description="Content quality analysis and improvement suggestions"
          icon={<Award className="w-5 h-5 text-blue-600" />}
        />
        <Card variant="glass">
          <CardContent className="p-6 text-center">
            <p className="text-sm text-rose-500 mb-3">{error}</p>
            <Button variant="outline" size="sm" onClick={fetchData}>
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Build chart data from history entries
  const chartData = historyData.map((entry, i) => ({
    index: i,
    date: entry.created_at ? new Date(entry.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : `#${i + 1}`,
    overall: entry.overall_score,
    readability: entry.readability,
    seo: entry.seo,
    engagement: entry.engagement,
    grammar: entry.grammar,
    brand: entry.brand,
  }))

  return (
    <div className="space-y-6">
      <PageHeader
        title="Quality Dashboard"
        description="Content quality analysis and improvement suggestions"
        icon={<Award className="w-5 h-5 text-blue-600" />}
        actions={
          <>
            {contentId && (
              <Button
                variant="primary"
                size="sm"
                leftIcon={<Award className="w-4 h-4" />}
                onClick={handleAnalyze}
                loading={isAnalyzing}
              >
                Analyze
              </Button>
            )}
            <Button
              variant="outline"
              size="sm"
              leftIcon={<Zap className="w-4 h-4" />}
              onClick={handleBatchAnalyze}
              loading={isAnalyzing}
            >
              Batch Analyze
            </Button>
          </>
        }
      />

      {/* Batch Progress */}
      {batchProgress && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card variant="glass" className="border-blue-200 dark:border-blue-500/30">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
                  <span className="text-sm font-medium text-slate-900 dark:text-slate-100">
                    Batch Analysis in Progress
                  </span>
                </div>
                <span className="text-sm text-slate-500 dark:text-slate-400">
                  {batchProgress.completed}/{batchProgress.total}
                </span>
              </div>
              <div className="h-2 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden">
                <motion.div
                  className="h-full rounded-full bg-gradient-to-r from-blue-500 to-violet-500"
                  animate={{
                    width: `${(batchProgress.completed / batchProgress.total) * 100}%`,
                  }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Overall Score Gauge */}
        <Card variant="glass" className="flex flex-col items-center justify-center">
          <CardContent className="p-6 flex flex-col items-center">
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <QualityGauge score={qualityResult?.overall_score ?? 0} />
            </motion.div>
            <p className="mt-4 text-sm text-slate-500 dark:text-slate-400">
              Overall Quality Score
            </p>
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
              {qualityResult?.created_at
                ? `Analyzed ${new Date(qualityResult.created_at).toLocaleDateString()}`
                : 'No analysis yet'}
            </p>
          </CardContent>
        </Card>

        {/* Dimension Scores */}
        <Card variant="glass" className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-blue-500" />
              <CardTitle>Dimension Scores</CardTitle>
            </div>
            <CardDescription>
              Breakdown across 5 quality dimensions
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {DIMENSIONS.map(dim => (
              <DimensionBar
                key={dim.key}
                label={dim.label}
                score={qualityResult?.[dim.key] ?? 0}
                icon={dim.icon}
                color={dim.color}
              />
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Score History Chart */}
      <Card variant="glass">
        <CardHeader>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-violet-500" />
            <CardTitle>Score History</CardTitle>
          </div>
          <CardDescription>
            Quality score trends over time
          </CardDescription>
        </CardHeader>
        <CardContent>
          {chartData.length > 0 ? (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="currentColor"
                    className="text-slate-200 dark:text-slate-700"
                  />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 12, fill: '#94a3b8' }}
                  />
                  <YAxis
                    domain={[0, 100]}
                    tick={{ fontSize: 12, fill: '#94a3b8' }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(15, 23, 42, 0.9)',
                      border: '1px solid rgba(148, 163, 184, 0.2)',
                      borderRadius: '12px',
                      color: '#f1f5f9',
                      fontSize: 12,
                    }}
                  />
                  {DIMENSIONS.map(dim => (
                    <Line
                      key={dim.key}
                      type="monotone"
                      dataKey={dim.key}
                      stroke={dim.color}
                      strokeWidth={2}
                      dot={false}
                      activeDot={{ r: 4 }}
                    />
                  ))}
                  <Line
                    type="monotone"
                    dataKey="overall"
                    stroke="#f8fafc"
                    strokeWidth={3}
                    dot={false}
                    activeDot={{ r: 5 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center text-sm text-slate-400 dark:text-slate-500">
              No history data available. Analyze content to start tracking scores.
            </div>
          )}
        </CardContent>
      </Card>

      {/* Improvement Suggestions */}
      {qualityResult?.suggestions && qualityResult.suggestions.length > 0 && (
        <Card variant="glass">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-amber-500" />
                <CardTitle>Improvement Suggestions</CardTitle>
              </div>
              <Badge variant="warning" size="sm">
                {qualityResult.suggestions.length} suggestions
              </Badge>
            </div>
            <CardDescription>
              Recommendations to boost your quality score
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {qualityResult.suggestions.map((suggestion, idx) => {
                // Auto-assign priority based on position (first = high, middle = medium, rest = low)
                const priority = idx < qualityResult.suggestions.length / 3
                  ? 'high' as const
                  : idx < (qualityResult.suggestions.length * 2) / 3
                    ? 'medium' as const
                    : 'low' as const
                const style = {
                  high: { bg: 'bg-rose-100 dark:bg-rose-500/20', text: 'text-rose-700 dark:text-rose-300', icon: <Lightbulb className="w-3.5 h-3.5" /> },
                  medium: { bg: 'bg-amber-100 dark:bg-amber-500/20', text: 'text-amber-700 dark:text-amber-300', icon: <Lightbulb className="w-3.5 h-3.5" /> },
                  low: { bg: 'bg-blue-100 dark:bg-blue-500/20', text: 'text-blue-700 dark:text-blue-300', icon: <CheckCircle2 className="w-3.5 h-3.5" /> },
                }[priority]

                return (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className="flex items-start gap-3 p-3 rounded-xl bg-white/50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700/50 hover:bg-white dark:hover:bg-slate-800 transition-colors group"
                  >
                    <div className={cn('p-1.5 rounded-lg flex-shrink-0', style.bg, style.text)}>
                      {style.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge
                          variant={priority === 'high' ? 'error' : priority === 'medium' ? 'warning' : 'info'}
                          size="sm"
                        >
                          {priority}
                        </Badge>
                      </div>
                      <p className="text-sm text-slate-700 dark:text-slate-300">
                        {suggestion}
                      </p>
                    </div>
                  </motion.div>
                )
              })}
            </div>
          </CardContent>
          <CardFooter>
            <Button variant="ghost" size="sm" className="w-full">
              Show All Suggestions
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* Empty state when no data */}
      {!qualityResult && (
        <Card variant="glass">
          <CardContent className="p-8 text-center">
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-3">
              No quality analysis available yet.
            </p>
            {contentId && (
              <Button variant="primary" size="sm" onClick={handleAnalyze} loading={isAnalyzing}>
                Run Quality Analysis
              </Button>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}