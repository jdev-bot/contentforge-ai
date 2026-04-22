'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion } from 'framer-motion'
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import {
  SmilePlus,
  Frown,
  Meh,
  TrendingUp,
  BarChart3,
  Activity,
  RefreshCw,
  ThumbsUp,
  ThumbsDown,
  Minus,
} from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { cn } from '@/lib/utils'
import { useToast } from '@/hooks/useToast'
import {
  analyzeSentiment,
  getSentiment,
  getSentimentTrends,
  getSentimentDistribution,
  SentimentResponse,
  SentimentTrendsResponse,
  SentimentDistributionResponse,
} from '@/lib/api'

interface SentimentDashboardProps {
  contentId?: string
}

const EMOTION_COLORS: Record<string, string> = {
  joy: '#fbbf24',
  anger: '#ef4444',
  sadness: '#6b7280',
  fear: '#8b5cf6',
  surprise: '#ec4899',
  disgust: '#10b981',
}

const TONE_COLORS = [
  '#3b82f6',
  '#8b5cf6',
  '#10b981',
  '#f59e0b',
  '#ec4899',
  '#06b6d4',
]

const SENTIMENT_LABEL_COLORS: Record<string, string> = {
  positive: '#10b981',
  negative: '#ef4444',
  neutral: '#6b7280',
  mixed: '#f59e0b',
}

// Circular gauge for sentiment (-1.0 to +1.0)
function SentimentGauge({ value, size = 180 }: { value: number; size?: number }) {
  const strokeWidth = 12
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  // Map -1..+1 to 0..1 for the arc
  const normalizedValue = (value + 1) / 2
  const strokeDashoffset = circumference - normalizedValue * circumference

  const getColor = (v: number) => {
    if (v >= 0.5) return '#10b981'
    if (v >= 0.2) return '#22c55e'
    if (v >= -0.2) return '#f59e0b'
    if (v >= -0.5) return '#f97316'
    return '#ef4444'
  }

  const getLabel = (v: number) => {
    if (v >= 0.5) return 'Very Positive'
    if (v >= 0.2) return 'Positive'
    if (v >= -0.2) return 'Neutral'
    if (v >= -0.5) return 'Negative'
    return 'Very Negative'
  }

  const color = getColor(value)

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
          {value.toFixed(2)}
        </span>
        <span className="text-sm font-medium" style={{ color }}>
          {getLabel(value)}
        </span>
      </div>
    </div>
  )
}

// Aspect sentiment card
function AspectCard({
  section,
  sentiment,
  score,
}: {
  section: string
  sentiment: string
  score: number
}) {
  const label = sentiment as 'positive' | 'negative' | 'neutral'
  const color = SENTIMENT_LABEL_COLORS[sentiment] ?? '#6b7280'
  const Icon = sentiment === 'positive' ? ThumbsUp : sentiment === 'negative' ? ThumbsDown : Minus

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-4 rounded-xl bg-white/50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700/50 hover:bg-white dark:hover:bg-slate-800 transition-colors"
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Icon className="w-4 h-4" style={{ color }} />
          <span className="text-sm font-semibold text-slate-900 dark:text-slate-100 capitalize">
            {section}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Badge
            variant={label === 'positive' ? 'success' : label === 'negative' ? 'error' : 'secondary'}
            size="sm"
          >
            {sentiment}
          </Badge>
          <span className="text-sm font-bold" style={{ color }}>
            {score.toFixed(2)}
          </span>
        </div>
      </div>
      {/* Mini bar */}
      <div className="h-1.5 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${((score + 1) / 2) * 100}%` }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
        />
      </div>
    </motion.div>
  )
}

export default function SentimentDashboard({ contentId }: SentimentDashboardProps) {
  const [sentiment, setSentiment] = useState<SentimentResponse | null>(null)
  const [trendsData, setTrendsData] = useState<SentimentResponse[]>([])
  const [distribution, setDistribution] = useState<SentimentDistributionResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { showToast } = useToast()

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      if (contentId) {
        const [result, trendResp] = await Promise.all([
          getSentiment(contentId).catch(() => null),
          getSentimentTrends(contentId).catch(() => null),
        ])
        setSentiment(result)
        setTrendsData(trendResp?.trends ?? [])
      }
      // Always fetch distribution (global, doesn't need contentId)
      const dist = await getSentimentDistribution().catch(() => null)
      setDistribution(dist)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sentiment data')
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
      const result = await analyzeSentiment(contentId)
      setSentiment(result)
      showToast('Sentiment analysis completed', 'success')
    } catch {
      showToast('Failed to analyze sentiment', 'error')
    } finally {
      setIsAnalyzing(false)
    }
  }

  // Prepare chart data from the real backend response shape
  // Emotion radar: emotions is { joy, anger, sadness, fear, surprise, disgust }
  const emotionRadarData = sentiment
    ? Object.entries(sentiment.emotions).map(([key, value]) => ({
        emotion: key.charAt(0).toUpperCase() + key.slice(1),
        score: value,
        fullMark: 1,
      }))
    : []

  // Tone: single string from backend, show as a simple visual
  const toneDisplayData = sentiment
    ? [{ name: sentiment.tone.charAt(0).toUpperCase() + sentiment.tone.slice(1), value: 100 }]
    : []

  // Distribution bar data from the distribution endpoint
  const distributionBarData = distribution
    ? Object.entries(distribution.distribution).map(([key, value]) => ({
        name: key.charAt(0).toUpperCase() + key.slice(1),
        value,
        fill: SENTIMENT_LABEL_COLORS[key] ?? '#6b7280',
      }))
    : sentiment
      ? [
          { name: sentiment.sentiment, value: 1, fill: SENTIMENT_LABEL_COLORS[sentiment.sentiment] ?? '#6b7280' },
        ]
      : []

  // Trend data for line chart
  const trendChartData = trendsData.map((entry, i) => ({
    index: i,
    date: entry.created_at ? new Date(entry.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : `#${i + 1}`,
    score: entry.score,
    sentiment: entry.score,
  }))

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="flex items-center justify-center h-64 rounded-xl animate-pulse bg-slate-200 dark:bg-slate-800" />
          <div className="h-64 rounded-xl animate-pulse bg-slate-200 dark:bg-slate-800" />
          <div className="h-64 rounded-xl animate-pulse bg-slate-200 dark:bg-slate-800" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Sentiment Analysis"
          description="Emotional and tonal analysis of your content"
          icon={<Activity className="w-5 h-5 text-purple-600" />}
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

  return (
    <div className="space-y-6">
      <PageHeader
        title="Sentiment Analysis"
        description="Emotional and tonal analysis of your content"
        icon={<Activity className="w-5 h-5 text-purple-600" />}
        actions={
          <>
            {contentId && (
              <Button
                variant="primary"
                size="sm"
                leftIcon={<Activity className="w-4 h-4" />}
                onClick={handleAnalyze}
                loading={isAnalyzing}
              >
                Analyze
              </Button>
            )}
            <Button
              variant="ghost"
              size="sm"
              leftIcon={<RefreshCw className="w-4 h-4" />}
              onClick={fetchData}
            >
              Refresh
            </Button>
          </>
        }
      />

      {/* Top Row: Gauge + Radar + Tone */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sentiment Gauge */}
        <Card variant="glass" className="flex flex-col items-center justify-center">
          <CardContent className="p-6 flex flex-col items-center">
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <SentimentGauge value={sentiment?.score ?? 0} />
            </motion.div>
            <div className="mt-4 flex items-center gap-2">
              <Badge
                variant={
                  sentiment?.sentiment === 'positive'
                    ? 'success'
                    : sentiment?.sentiment === 'negative'
                      ? 'error'
                      : sentiment?.sentiment === 'mixed'
                        ? 'warning'
                        : 'secondary'
                }
                size="sm"
                dot
              >
                {sentiment?.sentiment ?? 'N/A'}
              </Badge>
            </div>
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-2">
              Scale: -1.0 (negative) to +1.0 (positive)
            </p>
          </CardContent>
        </Card>

        {/* Emotion Radar Chart */}
        <Card variant="glass">
          <CardHeader>
            <div className="flex items-center gap-2">
              <SmilePlus className="w-5 h-5 text-amber-500" />
              <CardTitle>Emotion Profile</CardTitle>
            </div>
            <CardDescription>Six primary emotions detected</CardDescription>
          </CardHeader>
          <CardContent>
            {emotionRadarData.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={emotionRadarData}>
                    <PolarGrid
                      stroke="currentColor"
                      className="text-slate-200 dark:text-slate-700"
                    />
                    <PolarAngleAxis
                      dataKey="emotion"
                      tick={{ fontSize: 11, fill: '#94a3b8' }}
                    />
                    <PolarRadiusAxis
                      angle={30}
                      domain={[0, 1]}
                      tick={{ fontSize: 9, fill: '#64748b' }}
                    />
                    <Radar
                      name="Score"
                      dataKey="score"
                      stroke="#8b5cf6"
                      fill="#8b5cf6"
                      fillOpacity={0.2}
                      strokeWidth={2}
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
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-sm text-slate-400">
                No emotion data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Detected Tone */}
        <Card variant="glass">
          <CardHeader>
            <div className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-blue-500" />
              <CardTitle>Detected Tone</CardTitle>
            </div>
            <CardDescription>Primary tone of the content</CardDescription>
          </CardHeader>
          <CardContent>
            {sentiment ? (
              <div className="h-64 flex flex-col items-center justify-center gap-4">
                <div
                  className="w-24 h-24 rounded-full flex items-center justify-center text-3xl font-bold"
                  style={{
                    background: `linear-gradient(135deg, ${TONE_COLORS[0]}20, ${TONE_COLORS[1]}20)`,
                    border: `2px solid ${TONE_COLORS[0]}40`,
                    color: TONE_COLORS[0],
                  }}
                >
                  {sentiment.tone.charAt(0).toUpperCase()}
                </div>
                <p className="text-lg font-semibold text-slate-900 dark:text-slate-100 capitalize">
                  {sentiment.tone}
                </p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {['formal', 'casual', 'urgent', 'persuasive', 'informative'].map(t => (
                    <span
                      key={t}
                      className={cn(
                        'px-2 py-1 rounded-full text-xs font-medium',
                        t === sentiment.tone
                          ? 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-300'
                          : 'bg-slate-100 dark:bg-slate-700 text-slate-400 dark:text-slate-500'
                      )}
                    >
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-sm text-slate-400">
                No tone data available
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Content Distribution Bar */}
      <Card variant="glass">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Meh className="w-5 h-5 text-slate-500" />
            <CardTitle>Sentiment Distribution</CardTitle>
          </div>
          <CardDescription>
            Breakdown of sentiment across analyzed content
          </CardDescription>
        </CardHeader>
        <CardContent>
          {distributionBarData.length > 0 ? (
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={distributionBarData} layout="vertical">
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="currentColor"
                    className="text-slate-200 dark:text-slate-700"
                    horizontal={false}
                  />
                  <XAxis
                    type="number"
                    tick={{ fontSize: 12, fill: '#94a3b8' }}
                  />
                  <YAxis
                    type="category"
                    dataKey="name"
                    tick={{ fontSize: 12, fill: '#94a3b8' }}
                    width={80}
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
                  <Bar dataKey="value" radius={[0, 8, 8, 0]} barSize={24}>
                    {distributionBarData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center text-sm text-slate-400">
              No distribution data available. Analyze content to see distribution.
            </div>
          )}
          {distribution && (
            <div className="mt-3 flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
              <span>Total analyses: {distribution.total_analyses}</span>
              {Object.entries(distribution.percentages).map(([key, value]) => (
                <span key={key}>
                  {key}: {value.toFixed(1)}%
                </span>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Sentiment Trend Over Time */}
      <Card variant="glass">
        <CardHeader>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-emerald-500" />
            <CardTitle>Sentiment Trend</CardTitle>
          </div>
          <CardDescription>
            How sentiment has changed over time
          </CardDescription>
        </CardHeader>
        <CardContent>
          {trendChartData.length > 0 ? (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendChartData}>
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
                    domain={[-1, 1]}
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
                  <Line
                    type="monotone"
                    dataKey="sentiment"
                    stroke="#8b5cf6"
                    strokeWidth={3}
                    dot={false}
                    activeDot={{ r: 5 }}
                  />
                  <Legend
                    verticalAlign="top"
                    height={36}
                    iconType="line"
                    formatter={(value: string) => (
                      <span className="text-xs text-slate-500 dark:text-slate-400 capitalize">
                        {value.replace('_', ' ')}
                      </span>
                    )}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-72 flex items-center justify-center text-sm text-slate-400 dark:text-slate-500">
              No trend data available. Analyze content to start tracking sentiment.
            </div>
          )}
        </CardContent>
      </Card>

      {/* Aspect-Based Sentiment Cards */}
      {sentiment?.aspects && sentiment.aspects.length > 0 && (
        <Card variant="glass">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Frown className="w-5 h-5 text-violet-500" />
              <CardTitle>Aspect-Based Sentiment</CardTitle>
            </div>
            <CardDescription>
              Sentiment broken down by content sections
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {sentiment.aspects.map((aspect, idx) => (
                <AspectCard
                  key={aspect.section}
                  section={aspect.section}
                  sentiment={aspect.sentiment}
                  score={aspect.score}
                />
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Empty state when no data */}
      {!sentiment && (
        <Card variant="glass">
          <CardContent className="p-8 text-center">
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-3">
              No sentiment analysis available yet.
            </p>
            {contentId && (
              <Button variant="primary" size="sm" onClick={handleAnalyze} loading={isAnalyzing}>
                Run Sentiment Analysis
              </Button>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}