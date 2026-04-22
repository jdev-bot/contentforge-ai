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
  getSentimentTrend,
  SentimentResult,
  SentimentTrendPoint,
} from '@/lib/api'

interface SentimentDashboardProps {
  contentId?: string
}

const EMOTION_COLORS: Record<string, string> = {
  joy: '#fbbf24',
  trust: '#3b82f6',
  fear: '#8b5cf6',
  surprise: '#ec4899',
  sadness: '#6b7280',
  anticipation: '#10b981',
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
  aspect,
  score,
  label,
  evidence,
}: {
  aspect: string
  score: number
  label: 'positive' | 'negative' | 'neutral'
  evidence: string[]
}) {
  const color = SENTIMENT_LABEL_COLORS[label]
  const Icon = label === 'positive' ? ThumbsUp : label === 'negative' ? ThumbsDown : Minus

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
            {aspect}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Badge
            variant={label === 'positive' ? 'success' : label === 'negative' ? 'error' : 'secondary'}
            size="sm"
          >
            {label}
          </Badge>
          <span className="text-sm font-bold" style={{ color }}>
            {score.toFixed(2)}
          </span>
        </div>
      </div>
      {/* Mini bar */}
      <div className="h-1.5 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden mb-3">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${((score + 1) / 2) * 100}%` }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
        />
      </div>
      {evidence.length > 0 && (
        <div className="space-y-1">
          {evidence.slice(0, 2).map((e, i) => (
            <p key={i} className="text-xs text-slate-500 dark:text-slate-400 truncate">
              &ldquo;{e}&rdquo;
            </p>
          ))}
        </div>
      )}
    </motion.div>
  )
}

export default function SentimentDashboard({ contentId }: SentimentDashboardProps) {
  const [sentiment, setSentiment] = useState<SentimentResult | null>(null)
  const [trend, setTrend] = useState<SentimentTrendPoint[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const { showToast } = useToast()

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true)
      if (contentId) {
        const [result, trendData] = await Promise.all([
          getSentiment(contentId).catch(() => MOCK_SENTIMENT),
          getSentimentTrend(contentId).catch(() => MOCK_TREND),
        ])
        setSentiment(result)
        setTrend(trendData)
      } else {
        setSentiment(MOCK_SENTIMENT)
        setTrend(MOCK_TREND)
      }
    } catch {
      setSentiment(MOCK_SENTIMENT)
      setTrend(MOCK_TREND)
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

  // Prepare chart data
  const emotionRadarData = sentiment?.emotions.map(e => ({
    emotion: e.emotion.charAt(0).toUpperCase() + e.emotion.slice(1),
    score: e.score,
    fullMark: 1,
  })) ?? []

  const tonePieData = sentiment?.tone_distribution.map(t => ({
    name: t.tone.charAt(0).toUpperCase() + t.tone.slice(1),
    value: t.percentage,
  })) ?? []

  const distributionBarData = sentiment
    ? [
        { name: 'Positive', value: sentiment.content_distribution.positive, fill: '#10b981' },
        { name: 'Negative', value: sentiment.content_distribution.negative, fill: '#ef4444' },
        { name: 'Neutral', value: sentiment.content_distribution.neutral, fill: '#6b7280' },
      ]
    : []

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

      {/* Top Row: Gauge + Radar + Pie */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sentiment Gauge */}
        <Card variant="glass" className="flex flex-col items-center justify-center">
          <CardContent className="p-6 flex flex-col items-center">
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <SentimentGauge value={sentiment?.overall_sentiment ?? 0} />
            </motion.div>
            <div className="mt-4 flex items-center gap-2">
              <Badge
                variant={
                  sentiment?.sentiment_label === 'positive'
                    ? 'success'
                    : sentiment?.sentiment_label === 'negative'
                      ? 'error'
                      : 'secondary'
                }
                size="sm"
                dot
              >
                {sentiment?.sentiment_label ?? 'N/A'}
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
          </CardContent>
        </Card>

        {/* Tone Distribution Pie */}
        <Card variant="glass">
          <CardHeader>
            <div className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-blue-500" />
              <CardTitle>Tone Distribution</CardTitle>
            </div>
            <CardDescription>Detected tones in your content</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={tonePieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {tonePieData.map((_, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={TONE_COLORS[index % TONE_COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(15, 23, 42, 0.9)',
                      border: '1px solid rgba(148, 163, 184, 0.2)',
                      borderRadius: '12px',
                      color: '#f1f5f9',
                      fontSize: 12,
                    }}
                    formatter={(value: unknown) => [`${value}%`, 'Percentage']}
                  />
                  <Legend
                    verticalAlign="bottom"
                    height={36}
                    iconType="circle"
                    iconSize={8}
                    formatter={(value: string) => (
                      <span className="text-xs text-slate-500 dark:text-slate-400">
                        {value}
                      </span>
                    )}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Content Distribution Bar */}
      <Card variant="glass">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Meh className="w-5 h-5 text-slate-500" />
            <CardTitle>Content Distribution</CardTitle>
          </div>
          <CardDescription>
            Positive, negative, and neutral content breakdown
          </CardDescription>
        </CardHeader>
        <CardContent>
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
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trend}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="currentColor"
                  className="text-slate-200 dark:text-slate-700"
                />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 12, fill: '#94a3b8' }}
                  tickFormatter={(val: string) =>
                    new Date(val).toLocaleDateString(undefined, {
                      month: 'short',
                      day: 'numeric',
                    })
                  }
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
                <Line
                  type="monotone"
                  dataKey="positive_count"
                  stroke="#10b981"
                  strokeWidth={1.5}
                  strokeDasharray="4 4"
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="negative_count"
                  stroke="#ef4444"
                  strokeWidth={1.5}
                  strokeDasharray="4 4"
                  dot={false}
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
        </CardContent>
      </Card>

      {/* Aspect-Based Sentiment Cards */}
      {sentiment?.aspect_sentiments && sentiment.aspect_sentiments.length > 0 && (
        <Card variant="glass">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Frown className="w-5 h-5 text-violet-500" />
              <CardTitle>Aspect-Based Sentiment</CardTitle>
            </div>
            <CardDescription>
              Sentiment broken down by content aspects
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {sentiment.aspect_sentiments.map((aspect, idx) => (
                <AspectCard
                  key={aspect.aspect}
                  aspect={aspect.aspect}
                  score={aspect.sentiment_score}
                  label={aspect.sentiment_label}
                  evidence={aspect.evidence}
                />
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

// Mock data
const MOCK_SENTIMENT: SentimentResult = {
  id: 's1',
  content_id: 'c1',
  user_id: 'u1',
  overall_sentiment: 0.42,
  sentiment_label: 'positive',
  emotions: [
    { emotion: 'joy', score: 0.72 },
    { emotion: 'trust', score: 0.65 },
    { emotion: 'anticipation', score: 0.58 },
    { emotion: 'surprise', score: 0.3 },
    { emotion: 'fear', score: 0.12 },
    { emotion: 'sadness', score: 0.08 },
  ],
  tone_distribution: [
    { tone: 'professional', percentage: 35 },
    { tone: 'friendly', percentage: 28 },
    { tone: 'authoritative', percentage: 18 },
    { tone: 'conversational', percentage: 12 },
    { tone: 'persuasive', percentage: 7 },
  ],
  aspect_sentiments: [
    {
      aspect: 'Product Quality',
      sentiment_score: 0.82,
      sentiment_label: 'positive',
      evidence: [
        'The build quality exceeded expectations',
        'Premium materials throughout',
      ],
    },
    {
      aspect: 'Pricing',
      sentiment_score: -0.25,
      sentiment_label: 'negative',
      evidence: [
        'Significantly more expensive than competitors',
        'Limited value at this price point',
      ],
    },
    {
      aspect: 'Customer Service',
      sentiment_score: 0.61,
      sentiment_label: 'positive',
      evidence: ['Responsive support team', 'Quick resolution times'],
    },
    {
      aspect: 'User Experience',
      sentiment_score: 0.44,
      sentiment_label: 'positive',
      evidence: ['Intuitive interface design'],
    },
    {
      aspect: 'Documentation',
      sentiment_score: -0.1,
      sentiment_label: 'neutral',
      evidence: ['Documentation could be more comprehensive'],
    },
    {
      aspect: 'Performance',
      sentiment_score: 0.7,
      sentiment_label: 'positive',
      evidence: ['Fast load times', 'Smooth animations'],
    },
  ],
  content_distribution: {
    positive: 62,
    negative: 18,
    neutral: 20,
  },
  analyzed_at: new Date().toISOString(),
}

const MOCK_TREND: SentimentTrendPoint[] = Array.from({ length: 14 }, (_, i) => {
  const date = new Date()
  date.setDate(date.getDate() - (13 - i))
  return {
    date: date.toISOString().split('T')[0],
    sentiment: -0.3 + Math.random() * 0.8,
    positive_count: Math.floor(5 + Math.random() * 15),
    negative_count: Math.floor(2 + Math.random() * 8),
    neutral_count: Math.floor(3 + Math.random() * 10),
  }
})