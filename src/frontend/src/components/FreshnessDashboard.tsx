'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  Clock,
  TrendingUp,
  TrendingDown,
  Minus,
  Zap,
  Calendar,
  BarChart3,
  ChevronRight,
  Sparkles,
  RotateCcw,
  Lightbulb,
  ArrowUpRight,
  Filter,
} from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter, GradientCard } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { cn } from '@/lib/utils'
import { useToast } from '@/hooks/useToast'
import { analyzeFreshness, getStaleContent, bulkRefreshContent } from '@/lib/api'

// Types
interface FreshnessScore {
  contentId: string
  title: string
  score: number
  lastUpdated: string
  recommendations: string[]
  trend: 'up' | 'down' | 'stable'
  trendValue: number
}

interface FreshnessMetrics {
  averageScore: number
  totalContent: number
  staleCount: number
  freshCount: number
  needsAttention: number
  lastScan: string
}

// Circular Progress Component
interface CircularProgressProps {
  value: number
  size?: 'sm' | 'md' | 'lg'
  showValue?: boolean
  className?: string
}

function CircularProgress({ value, size = 'md', showValue = true, className }: CircularProgressProps) {
  const sizes = {
    sm: { width: 60, strokeWidth: 6, fontSize: '14px' },
    md: { width: 100, strokeWidth: 8, fontSize: '20px' },
    lg: { width: 140, strokeWidth: 10, fontSize: '28px' },
  }

  const { width, strokeWidth, fontSize } = sizes[size]
  const radius = (width - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const strokeDashoffset = circumference - (value / 100) * circumference

  const getColor = (score: number) => {
    if (score >= 70) return '#10b981' // emerald-500
    if (score >= 50) return '#f59e0b' // amber-500
    return '#ef4444' // rose-500
  }

  const color = getColor(value)

  return (
    <div className={cn('relative inline-flex items-center justify-center', className)}>
      <svg width={width} height={width} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={width / 2}
          cy={width / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-slate-200 dark:text-slate-700"
        />
        {/* Progress circle */}
        <circle
          cx={width / 2}
          cy={width / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      {showValue && (
        <div
          className="absolute inset-0 flex items-center justify-center font-bold text-slate-900 dark:text-slate-100"
          style={{ fontSize }}
        >
          {Math.round(value)}
        </div>
      )}
    </div>
  )
}

// Score Card Component
interface ScoreCardProps {
  title: string
  score: number
  icon: React.ReactNode
  trend?: 'up' | 'down' | 'stable'
  trendValue?: number
  description: string
}

function ScoreCard({ title, score, icon, trend, trendValue, description }: ScoreCardProps) {
  const getScoreColor = (s: number) => {
    if (s >= 70) return 'text-emerald-600 dark:text-emerald-400'
    if (s >= 50) return 'text-amber-600 dark:text-amber-400'
    return 'text-rose-600 dark:text-rose-400'
  }

  const getScoreBg = (s: number) => {
    if (s >= 70) return 'from-emerald-500/10 to-teal-500/10 dark:from-emerald-500/20 dark:to-teal-500/20 border-emerald-200/50 dark:border-emerald-500/30'
    if (s >= 50) return 'from-amber-500/10 to-orange-500/10 dark:from-amber-500/20 dark:to-orange-500/20 border-amber-200/50 dark:border-amber-500/30'
    return 'from-rose-500/10 to-red-500/10 dark:from-rose-500/20 dark:to-red-500/20 border-rose-200/50 dark:border-rose-500/30'
  }

  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus
  const trendColor = trend === 'up' ? 'text-emerald-600 dark:text-emerald-400' : trend === 'down' ? 'text-rose-600 dark:text-rose-400' : 'text-slate-600 dark:text-slate-400'

  return (
    <Card variant="glass" className={cn('overflow-hidden group', getScoreBg(score))}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <div className={cn('p-2 rounded-lg bg-gradient-to-br', getScoreBg(score))}>
                {icon}
              </div>
              <span className="text-sm font-medium text-slate-600 dark:text-slate-400">{title}</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className={cn('text-3xl font-bold', getScoreColor(score))}>
                {score}
              </span>
              <span className="text-sm text-slate-500 dark:text-slate-400">/100</span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{description}</p>
          </div>
          <CircularProgress value={score} size="md" />
        </div>
        {trend && (
          <div className={cn('flex items-center gap-1 mt-4 text-sm', trendColor)}>
            <TrendIcon className="w-4 h-4" />
            <span className="font-medium">{trendValue && `${trendValue > 0 ? '+' : ''}${trendValue}%`}</span>
            <span className="text-slate-500 dark:text-slate-400 ml-1">vs last week</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// Stale Content Item
interface StaleContentItemProps {
  content: FreshnessScore
  onRefresh: (id: string) => void
  isRefreshing: boolean
}

function StaleContentItem({ content, onRefresh, isRefreshing }: StaleContentItemProps) {
  const getStatusColor = (score: number) => {
    if (score >= 70) return 'bg-emerald-500'
    if (score >= 50) return 'bg-amber-500'
    return 'bg-rose-500'
  }

  const getStatusLabel = (score: number) => {
    if (score >= 70) return 'Fresh'
    if (score >= 50) return 'Needs Update'
    return 'Stale'
  }

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -100 }}
      className="group relative p-4 rounded-xl bg-white/50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 transition-all duration-200"
    >
      <div className="flex items-start gap-4">
        <div className={cn('w-2 h-full absolute left-0 top-0 rounded-l-xl', getStatusColor(content.score))} />
        
        <div className="flex-1 min-w-0 pl-2">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-medium text-slate-900 dark:text-slate-100 truncate">{content.title}</h4>
            <Badge variant={content.score < 50 ? 'error' : content.score < 70 ? 'warning' : 'success'} size="sm">
              {getStatusLabel(content.score)}
            </Badge>
          </div>
          
          <div className="flex items-center gap-4 text-sm text-slate-500 dark:text-slate-400">
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" />
              {new Date(content.lastUpdated).toLocaleDateString()}
            </span>
            <span className="flex items-center gap-1">
              <BarChart3 className="w-3.5 h-3.5" />
              Score: {content.score}
            </span>
          </div>

          {content.recommendations.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {content.recommendations.map((rec, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1 px-2 py-1 text-xs rounded-full bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300"
                >
                  <Lightbulb className="w-3 h-3" />
                  {rec}
                </span>
              ))}
            </div>
          )}
        </div>

        <Button
          variant="ghost"
          size="sm"
          leftIcon={<RefreshCw className={cn('w-4 h-4', isRefreshing && 'animate-spin')} />}
          onClick={() => onRefresh(content.contentId)}
          disabled={isRefreshing}
          className="opacity-0 group-hover:opacity-100 transition-opacity"
        >
          Refresh
        </Button>
      </div>
    </motion.div>
  )
}

// Recommendations Panel
function RecommendationsPanel({ recommendations }: { recommendations: string[] }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <Card variant="glass" className="h-full">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-gradient-to-br from-violet-500/10 to-fuchsia-500/10 dark:from-violet-500/20 dark:to-fuchsia-500/20">
              <Sparkles className="w-5 h-5 text-violet-600 dark:text-violet-400" />
            </div>
            <CardTitle>AI Recommendations</CardTitle>
          </div>
          <Badge variant="purple" size="sm">
            {recommendations.length} tips
          </Badge>
        </div>
        <CardDescription>Smart suggestions to improve content freshness</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <AnimatePresence>
          {(expanded ? recommendations : recommendations.slice(0, 4)).map((rec, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="flex items-start gap-3 p-3 rounded-lg bg-white/50 dark:bg-slate-800/50 hover:bg-white dark:hover:bg-slate-800 transition-colors group cursor-pointer"
            >
              <div className="p-1.5 rounded-md bg-violet-100 dark:bg-violet-900/30 text-violet-600 dark:text-violet-400 group-hover:bg-violet-200 dark:group-hover:bg-violet-900/50 transition-colors">
                <ArrowUpRight className="w-4 h-4" />
              </div>
              <div className="flex-1">
                <p className="text-sm text-slate-700 dark:text-slate-300">{rec}</p>
              </div>
              <ChevronRight className="w-4 h-4 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity" />
            </motion.div>
          ))}
        </AnimatePresence>
      </CardContent>
      {recommendations.length > 4 && (
        <CardFooter className="pt-2">
          <Button variant="ghost" size="sm" className="w-full" onClick={() => setExpanded(!expanded)}>
            {expanded ? 'Show Less' : `Show ${recommendations.length - 4} More`}
          </Button>
        </CardFooter>
      )}
    </Card>
  )
}

// Main Dashboard Component
export default function FreshnessDashboard() {
  const [metrics, setMetrics] = useState<FreshnessMetrics | null>(null)
  const [staleContent, setStaleContent] = useState<FreshnessScore[]>([])
  const [recommendations, setRecommendations] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState<string | null>(null)
  const [selectedFilter, setSelectedFilter] = useState<'all' | 'stale' | 'needs-attention'>('all')
  const { showToast } = useToast()

  // Mock data - replace with actual API calls
  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true)
      // const data = await getFreshnessMetrics()
      // const stale = await getStaleContent()
      
      // Mock data
      await new Promise(resolve => setTimeout(resolve, 800))
      
      setMetrics({
        averageScore: 68,
        totalContent: 156,
        staleCount: 23,
        freshCount: 89,
        needsAttention: 44,
        lastScan: new Date().toISOString(),
      })

      setStaleContent([
        {
          contentId: '1',
          title: '10 Tips for Social Media Marketing in 2023',
          score: 35,
          lastUpdated: '2023-06-15',
          recommendations: ['Update statistics', 'Refresh examples', 'Add 2024 trends'],
          trend: 'down',
          trendValue: -12,
        },
        {
          contentId: '2',
          title: 'Ultimate Guide to SEO',
          score: 42,
          lastUpdated: '2023-08-20',
          recommendations: ['Update Google algorithm changes', 'Add new tools'],
          trend: 'stable',
          trendValue: 0,
        },
        {
          contentId: '3',
          title: 'Content Marketing Strategies',
          score: 48,
          lastUpdated: '2023-09-10',
          recommendations: ['Refresh case studies', 'Update metrics'],
          trend: 'up',
          trendValue: 5,
        },
        {
          contentId: '4',
          title: 'Email Marketing Best Practices',
          score: 38,
          lastUpdated: '2023-07-05',
          recommendations: ['Update open rate benchmarks', 'Add new templates'],
          trend: 'down',
          trendValue: -8,
        },
        {
          contentId: '5',
          title: 'Video Marketing Trends',
          score: 45,
          lastUpdated: '2023-10-01',
          recommendations: ['Add TikTok updates', 'Update platform stats'],
          trend: 'up',
          trendValue: 3,
        },
      ])

      setRecommendations([
        'Update outdated statistics and metrics from 2023',
        'Refresh case studies with recent success stories',
        'Add emerging trends for 2024 and beyond',
        'Update SEO recommendations for latest algorithm changes',
        'Review and refresh image alt text for accessibility',
        'Add new tool recommendations and retire outdated ones',
        'Update social media platform best practices',
        'Refresh email template examples with new designs',
        'Add video content to text-heavy articles',
        'Update CTAs based on current conversion benchmarks',
      ])
    } catch (error) {
      showToast('Failed to load freshness data', 'error')
    } finally {
      setIsLoading(false)
    }
  }, [showToast])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const handleRefreshContent = async (contentId: string) => {
    setIsRefreshing(contentId)
    try {
      // await analyzeFreshness(contentId)
      await new Promise(resolve => setTimeout(resolve, 1500))
      showToast('Content analysis refreshed successfully', 'success')
    } catch (error) {
      showToast('Failed to refresh content', 'error')
    } finally {
      setIsRefreshing(null)
    }
  }

  const handleBulkRefresh = async () => {
    setIsRefreshing('bulk')
    try {
      // await bulkRefreshContent()
      await new Promise(resolve => setTimeout(resolve, 2000))
      showToast(`Refreshed ${staleContent.length} content items`, 'success')
      fetchData()
    } catch (error) {
      showToast('Failed to bulk refresh', 'error')
    } finally {
      setIsRefreshing(null)
    }
  }

  const filteredContent = staleContent.filter(item => {
    if (selectedFilter === 'stale') return item.score < 50
    if (selectedFilter === 'needs-attention') return item.score >= 50 && item.score < 70
    return true
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="h-32 animate-pulse bg-slate-200 dark:bg-slate-800">{null}</Card>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-24 rounded-xl animate-pulse bg-slate-200 dark:bg-slate-800" />
            ))}
          </div>
          <Card className="h-96 animate-pulse bg-slate-200 dark:bg-slate-800">{null}</Card>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Content Freshness"
        description="Monitor and improve your content quality over time"
        icon={<BarChart3 className="w-5 h-5 text-emerald-600" />}
        actions={
          <>
            <span className="text-sm text-slate-500 dark:text-slate-400 flex items-center gap-1">
              <Clock className="w-4 h-4" />
              Last scan: {metrics?.lastScan && new Date(metrics.lastScan).toLocaleTimeString()}
            </span>
            <Button
              variant="outline"
              size="sm"
              leftIcon={<RotateCcw className="w-4 h-4" />}
              onClick={fetchData}
              disabled={isLoading}
            >
              Refresh
            </Button>
          </>
        }
      />

      {/* Score Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <ScoreCard
          title="Average Score"
          score={metrics?.averageScore || 0}
          icon={<BarChart3 className="w-5 h-5" />}
          trend="up"
          trendValue={5}
          description="Overall content freshness"
        />
        <ScoreCard
          title="Fresh Content"
          score={metrics?.freshCount || 0}
          icon={<CheckCircle2 className="w-5 h-5" />}
          description="Score above 70"
        />
        <ScoreCard
          title="Needs Attention"
          score={metrics?.needsAttention || 0}
          icon={<AlertTriangle className="w-5 h-5" />}
          trend="down"
          trendValue={3}
          description="Score between 50-70"
        />
        <ScoreCard
          title="Stale Content"
          score={metrics?.staleCount || 0}
          icon={<Clock className="w-5 h-5" />}
          description="Score below 50"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Stale Content List */}
        <div className="lg:col-span-2 space-y-4">
          <Card variant="glass">
            <CardHeader className="pb-4">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-amber-500" />
                    Content Requiring Updates
                  </CardTitle>
                  <CardDescription>Content with freshness score below 70</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1 p-1 rounded-lg bg-slate-100 dark:bg-slate-800">
                    {(['all', 'stale', 'needs-attention'] as const).map((filter) => (
                      <button
                        key={filter}
                        onClick={() => setSelectedFilter(filter)}
                        className={cn(
                          'px-3 py-1.5 text-sm font-medium rounded-md transition-all',
                          selectedFilter === filter
                            ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 shadow-sm'
                            : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                        )}
                      >
                        {filter.charAt(0).toUpperCase() + filter.slice(1).replace('-', ' ')}
                      </button>
                    ))}
                  </div>
                  <Button
                    variant="primary"
                    size="sm"
                    leftIcon={<Zap className="w-4 h-4" />}
                    onClick={handleBulkRefresh}
                    disabled={isRefreshing === 'bulk' || filteredContent.length === 0}
                    loading={isRefreshing === 'bulk'}
                  >
                    Bulk Refresh
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <AnimatePresence mode="popLayout">
                {filteredContent.length === 0 ? (
                  <div className="text-center py-12">
                    <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-4" />
                    <p className="text-slate-900 dark:text-slate-100 font-medium">All content is fresh!</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                      No content requires updates at this time.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {filteredContent.map((content) => (
                      <StaleContentItem
                        key={content.contentId}
                        content={content}
                        onRefresh={handleRefreshContent}
                        isRefreshing={isRefreshing === content.contentId}
                      />
                    ))}
                  </div>
                )}
              </AnimatePresence>
            </CardContent>
          </Card>
        </div>

        {/* Recommendations Panel */}
        <RecommendationsPanel recommendations={recommendations} />
      </div>
    </div>
  )
}
