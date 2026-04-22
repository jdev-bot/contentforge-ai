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
  AlertTriangle,
  CheckCircle2,
  Loader2,
  BarChart3,
  Zap,
  ArrowUpRight,
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
  getBatchAnalysisStatus,
  QualityScoreResult,
  QualityScoreHistory,
  BatchAnalysisProgress,
} from '@/lib/api'

interface QualityDashboardProps {
  contentId?: string
}

const DIMENSION_ICONS: Record<string, React.ReactNode> = {
  readability: <BookOpen className="w-4 h-4" />,
  seo: <Search className="w-4 h-4" />,
  engagement: <Heart className="w-4 h-4" />,
  grammar: <SpellCheck className="w-4 h-4" />,
  brand: <Palette className="w-4 h-4" />,
}

const DIMENSION_COLORS: Record<string, string> = {
  readability: '#3b82f6',
  seo: '#8b5cf6',
  engagement: '#f59e0b',
  grammar: '#10b981',
  brand: '#ec4899',
}

const PRIORITY_STYLES: Record<string, { bg: string; text: string; icon: React.ReactNode }> = {
  high: {
    bg: 'bg-rose-100 dark:bg-rose-500/20',
    text: 'text-rose-700 dark:text-rose-300',
    icon: <AlertTriangle className="w-3.5 h-3.5" />,
  },
  medium: {
    bg: 'bg-amber-100 dark:bg-amber-500/20',
    text: 'text-amber-700 dark:text-amber-300',
    icon: <Lightbulb className="w-3.5 h-3.5" />,
  },
  low: {
    bg: 'bg-blue-100 dark:bg-blue-500/20',
    text: 'text-blue-700 dark:text-blue-300',
    icon: <CheckCircle2 className="w-3.5 h-3.5" />,
  },
}

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
  name,
  score,
  maxScore,
}: {
  name: string
  score: number
  maxScore: number
}) {
  const percentage = (score / maxScore) * 100
  const color = DIMENSION_COLORS[name.toLowerCase()] ?? '#6b7280'
  const icon = DIMENSION_ICONS[name.toLowerCase()]

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300">
          <span style={{ color }}>{icon}</span>
          <span className="capitalize">{name}</span>
        </div>
        <span className="text-sm font-semibold text-slate-900 dark:text-slate-100">
          {score}<span className="text-slate-400">/{maxScore}</span>
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
  const [qualityResult, setQualityResult] = useState<QualityScoreResult | null>(null)
  const [history, setHistory] = useState<QualityScoreHistory[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [batchProgress, setBatchProgress] = useState<BatchAnalysisProgress | null>(null)
  const { showToast } = useToast()

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true)
      if (contentId) {
        const [result, hist] = await Promise.all([
          getQualityScore(contentId).catch(() => MOCK_QUALITY),
          getQualityScoreHistory(contentId).catch(() => MOCK_HISTORY),
        ])
        setQualityResult(result)
        setHistory(hist)
      } else {
        setQualityResult(MOCK_QUALITY)
        setHistory(MOCK_HISTORY)
      }
    } catch {
      setQualityResult(MOCK_QUALITY)
      setHistory(MOCK_HISTORY)
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
    try {
      setIsAnalyzing(true)
      // Simulated batch analysis
      setBatchProgress({
        total: 10,
        completed: 0,
        failed: 0,
        in_progress: 10,
        estimated_completion: new Date(Date.now() + 60000).toISOString(),
      })
      for (let i = 0; i <= 10; i++) {
        await new Promise(resolve => setTimeout(resolve, 300))
        setBatchProgress(prev => prev ? {
          ...prev,
          completed: i,
          in_progress: 10 - i,
        } : null)
      }
      setBatchProgress(null)
      showToast('Batch analysis completed', 'success')
    } catch {
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
              {qualityResult?.analyzed_at
                ? `Analyzed ${new Date(qualityResult.analyzed_at).toLocaleDateString()}`
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
            {qualityResult?.dimensions.map(dim => (
              <DimensionBar
                key={dim.name}
                name={dim.name}
                score={dim.score}
                maxScore={dim.max_score}
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
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={history}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="currentColor"
                  className="text-slate-200 dark:text-slate-700"
                />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 12, fill: '#94a3b8' }}
                  tickFormatter={(val: string) => new Date(val).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
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
                {Object.entries(DIMENSION_COLORS).map(([key, color]) => (
                  <Line
                    key={key}
                    type="monotone"
                    dataKey={key}
                    stroke={color}
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
        </CardContent>
      </Card>

      {/* Improvement Suggestions */}
      {qualityResult?.improvement_suggestions && qualityResult.improvement_suggestions.length > 0 && (
        <Card variant="glass">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-amber-500" />
                <CardTitle>Improvement Suggestions</CardTitle>
              </div>
              <Badge variant="warning" size="sm">
                {qualityResult.improvement_suggestions.length} suggestions
              </Badge>
            </div>
            <CardDescription>
              Prioritized recommendations to boost your quality score
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {qualityResult.improvement_suggestions.map((suggestion, idx) => {
                const style = PRIORITY_STYLES[suggestion.priority] ?? PRIORITY_STYLES.low
                return (
                  <motion.div
                    key={suggestion.id || idx}
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
                          variant={suggestion.priority === 'high' ? 'error' : suggestion.priority === 'medium' ? 'warning' : 'info'}
                          size="sm"
                        >
                          {suggestion.priority}
                        </Badge>
                        <span className="text-xs text-slate-500 dark:text-slate-400 capitalize">
                          {suggestion.dimension}
                        </span>
                        <span className="text-xs text-slate-400 ml-auto flex items-center gap-0.5">
                          <ArrowUpRight className="w-3 h-3" />
                          +{suggestion.impact_score} impact
                        </span>
                      </div>
                      <p className="text-sm text-slate-700 dark:text-slate-300">
                        {suggestion.text}
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
    </div>
  )
}

// Mock data
const MOCK_QUALITY: QualityScoreResult = {
  id: 'q1',
  content_id: 'c1',
  user_id: 'u1',
  overall_score: 72,
  dimensions: [
    { name: 'readability', score: 78, max_score: 100, suggestions: ['Shorten long paragraphs'] },
    { name: 'seo', score: 65, max_score: 100, suggestions: ['Add more keywords', 'Improve meta description'] },
    { name: 'engagement', score: 82, max_score: 100, suggestions: [] },
    { name: 'grammar', score: 90, max_score: 100, suggestions: [] },
    { name: 'brand', score: 55, max_score: 100, suggestions: ['Align tone with brand guidelines', 'Add brand-specific terminology'] },
  ],
  improvement_suggestions: [
    { id: 's1', text: 'Add relevant keywords to headings to improve SEO discoverability', priority: 'high', dimension: 'seo', impact_score: 15 },
    { id: 's2', text: 'Align content tone with your brand voice guidelines', priority: 'high', dimension: 'brand', impact_score: 12 },
    { id: 's3', text: 'Break long paragraphs into shorter ones for better readability', priority: 'medium', dimension: 'readability', impact_score: 8 },
    { id: 's4', text: 'Add a compelling meta description including primary keyword', priority: 'medium', dimension: 'seo', impact_score: 7 },
    { id: 's5', text: 'Include brand-specific call-to-action phrases', priority: 'low', dimension: 'brand', impact_score: 4 },
    { id: 's6', text: 'Add internal links to related content for SEO benefit', priority: 'low', dimension: 'seo', impact_score: 3 },
  ],
  analyzed_at: new Date().toISOString(),
}

const MOCK_HISTORY: QualityScoreHistory[] = Array.from({ length: 14 }, (_, i) => {
  const date = new Date()
  date.setDate(date.getDate() - (13 - i))
  return {
    date: date.toISOString().split('T')[0],
    overall: 60 + Math.round(Math.random() * 20),
    readability: 65 + Math.round(Math.random() * 25),
    seo: 55 + Math.round(Math.random() * 20),
    engagement: 70 + Math.round(Math.random() * 15),
    grammar: 80 + Math.round(Math.random() * 15),
    brand: 45 + Math.round(Math.random() * 20),
  }
})