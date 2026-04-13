'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Flame,
  TrendingUp,
  TrendingDown,
  Minus,
  Clock,
  Hash,
  Target,
  Sparkles,
  ChevronRight,
  Filter,
  ArrowUpRight,
  BarChart3,
  Zap,
  Globe,
  Cpu,
  Briefcase,
  Heart,
  ShoppingBag,
  Gamepad2,
  Music,
  Film,
  BookOpen,
  Beaker,
  type LucideIcon,
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Tooltip } from '@/components/ui/Tooltip'
import { cn } from '@/lib/utils'
import { useToast } from '@/hooks/useToast'
import { getTrendingTopics, generateFromTrend } from '@/lib/api'

// Types
interface Trend {
  id: string
  title: string
  category: string
  velocity: number
  relevanceScore: number
  mentionCount: number
  growthRate: number
  isHot: boolean
  isCold: boolean
  timestamp: string
  relatedHashtags: string[]
  description?: string
}

type Category = 'all' | 'tech' | 'business' | 'lifestyle' | 'entertainment' | 'science' | 'gaming' | 'fashion'

interface CategoryConfig {
  id: Category
  label: string
  icon: LucideIcon
  color: string
}

const categories: CategoryConfig[] = [
  { id: 'all', label: 'All Topics', icon: Globe, color: 'text-blue-500' },
  { id: 'tech', label: 'Technology', icon: Cpu, color: 'text-cyan-500' },
  { id: 'business', label: 'Business', icon: Briefcase, color: 'text-violet-500' },
  { id: 'lifestyle', label: 'Lifestyle', icon: Heart, color: 'text-rose-500' },
  { id: 'entertainment', label: 'Entertainment', icon: Film, color: 'text-amber-500' },
  { id: 'science', label: 'Science', icon: Beaker, color: 'text-emerald-500' },
  { id: 'gaming', label: 'Gaming', icon: Gamepad2, color: 'text-purple-500' },
  { id: 'fashion', label: 'Fashion', icon: ShoppingBag, color: 'text-pink-500' },
]

// Sparkline Component
function Sparkline({ data, isPositive }: { data: number[]; isPositive: boolean }) {
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1

  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * 100
    const y = 100 - ((value - min) / range) * 100
    return `${x},${y}`
  }).join(' ')

  return (
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="w-full h-10">
      <polyline
        points={points}
        fill="none"
        stroke={isPositive ? '#10b981' : '#ef4444'}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="opacity-80"
      />
      <defs>
        <linearGradient id={`gradient-${isPositive}`} x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor={isPositive ? '#10b981' : '#ef4444'} stopOpacity="0.2" />
          <stop offset="100%" stopColor={isPositive ? '#10b981' : '#ef4444'} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polygon
        points={`0,100 ${points} 100,100`}
        fill={`url(#gradient-${isPositive})`}
      />
    </svg>
  )
}

// Velocity Indicator
function VelocityIndicator({ velocity, growthRate }: { velocity: number; growthRate: number }) {
  const isPositive = growthRate > 0
  const isNeutral = growthRate === 0

  return (
    <div className="flex items-center gap-2">
      <div className={cn(
        'flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium',
        isPositive && 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300',
        !isPositive && !isNeutral && 'bg-rose-100 dark:bg-rose-900/30 text-rose-700 dark:text-rose-300',
        isNeutral && 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300'
      )}>
        {isPositive ? (
          <TrendingUp className="w-3 h-3" />
        ) : !isNeutral ? (
          <TrendingDown className="w-3 h-3" />
        ) : (
          <Minus className="w-3 h-3" />
        )}
        <span>{isPositive ? '+' : ''}{growthRate}%</span>
      </div>
      <div className="relative w-16 h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
        <motion.div
          className={cn(
            'absolute h-full rounded-full',
            velocity > 70 ? 'bg-gradient-to-r from-amber-500 to-orange-500' :
            velocity > 40 ? 'bg-gradient-to-r from-blue-500 to-cyan-500' :
            'bg-slate-400'
          )}
          initial={{ width: 0 }}
          animate={{ width: `${velocity}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>
      <span className="text-xs text-slate-500 dark:text-slate-400 w-8">{velocity}</span>
    </div>
  )
}

// Hot/Cold Indicator
function TrendTemperature({ isHot, isCold }: { isHot: boolean; isCold: boolean }) {
  if (isHot) {
    return (
      <Badge variant="error" size="sm" className="animate-pulse">
        <Flame className="w-3 h-3 mr-1" />
        Hot
      </Badge>
    )
  }
  if (isCold) {
    return (
      <Badge variant="secondary" size="sm">
        <TrendingDown className="w-3 h-3 mr-1" />
        Cooling
      </Badge>
    )
  }
  return (
    <Badge variant="secondary" size="sm">
      <Minus className="w-3 h-3 mr-1" />
      Steady
    </Badge>
  )
}

// Trend Card Component
interface TrendCardProps {
  trend: Trend
  onGenerate: (id: string) => void
  isGenerating: boolean
}

function TrendCard({ trend, onGenerate, isGenerating }: TrendCardProps) {
  const category = categories.find(c => c.id === trend.category)
  const CategoryIcon = category?.icon || Globe

  // Generate mock sparkline data based on velocity
  const sparklineData = Array.from({ length: 10 }, (_, i) => {
    const base = trend.velocity
    const noise = Math.sin(i * 0.5) * 10 + Math.random() * 5
    return Math.max(0, Math.min(100, base + noise + (i * trend.growthRate / 10)))
  })

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      whileHover={{ y: -2 }}
      className={cn(
        'group relative p-5 rounded-2xl transition-all duration-300',
        'bg-white/70 dark:bg-slate-800/70',
        'backdrop-blur-xl',
        'border border-white/20 dark:border-white/10',
        'hover:shadow-xl hover:shadow-slate-900/5 dark:hover:shadow-black/20',
        trend.isHot && 'ring-2 ring-rose-500/30 dark:ring-rose-500/20'
      )}
    >
      {/* Hot indicator glow */}
      {trend.isHot && (
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-rose-500/5 to-orange-500/5 pointer-events-none" />
      )}

      <div className="relative">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={cn(
              'p-2 rounded-xl bg-gradient-to-br',
              'from-slate-100 to-slate-200 dark:from-slate-700 dark:to-slate-800'
            )}>
              <CategoryIcon className={cn('w-5 h-5', category?.color)} />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 dark:text-slate-100 line-clamp-1">
                {trend.title}
              </h3>
              <div className="flex items-center gap-2 mt-1">
                <TrendTemperature isHot={trend.isHot} isCold={trend.isCold} />
                <span className="text-xs text-slate-500 dark:text-slate-400">
                  <Clock className="w-3 h-3 inline mr-1" />
                  {new Date(trend.timestamp).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
          <Tooltip content="Relevance to your niche" position="left">
            <div className="flex flex-col items-end">
              <div className={cn(
                'flex items-center gap-1 text-sm font-semibold',
                trend.relevanceScore >= 80 ? 'text-emerald-600 dark:text-emerald-400' :
                trend.relevanceScore >= 50 ? 'text-amber-600 dark:text-amber-400' :
                'text-slate-600 dark:text-slate-400'
              )}>
                <Target className="w-4 h-4" />
                {trend.relevanceScore}%
              </div>
              <span className="text-xs text-slate-500 dark:text-slate-400">relevance</span>
            </div>
          </Tooltip>
        </div>

        {/* Sparkline */}
        <div className="mb-4">
          <Sparkline data={sparklineData} isPositive={trend.growthRate > 0} />
        </div>

        {/* Stats */}
        <div className="flex items-center justify-between mb-4">
          <VelocityIndicator velocity={trend.velocity} growthRate={trend.growthRate} />
          <div className="flex items-center gap-1 text-sm text-slate-600 dark:text-slate-400">
            <BarChart3 className="w-4 h-4" />
            <span>{trend.mentionCount.toLocaleString()}</span>
            <span className="text-slate-400">mentions</span>
          </div>
        </div>

        {/* Hashtags */}
        <div className="flex flex-wrap gap-1.5 mb-4">
          {trend.relatedHashtags.slice(0, 4).map((tag, idx) => (
            <span
              key={idx}
              className="inline-flex items-center gap-1 px-2 py-1 text-xs rounded-full bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300"
            >
              <Hash className="w-3 h-3" />
              {tag}
            </span>
          ))}
          {trend.relatedHashtags.length > 4 && (
            <span className="text-xs text-slate-400 px-1">+{trend.relatedHashtags.length - 4}</span>
          )}
        </div>

        {/* Description */}
        {trend.description && (
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-4 line-clamp-2">
            {trend.description}
          </p>
        )}

        {/* Generate Button */}
        <Button
          variant="primary"
          size="sm"
          className="w-full"
          leftIcon={<Sparkles className="w-4 h-4" />}
          rightIcon={<ChevronRight className="w-4 h-4" />}
          onClick={() => onGenerate(trend.id)}
          loading={isGenerating}
          disabled={isGenerating}
        >
          Generate Content
        </Button>
      </div>
    </motion.div>
  )
}

// Empty State
function EmptyState({ category }: { category: string }) {
  return (
    <div className="col-span-full flex flex-col items-center justify-center py-16 text-center">
      <div className="w-16 h-16 rounded-2xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-4">
        <TrendingUp className="w-8 h-8 text-slate-400" />
      </div>
      <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-2">
        No trending topics found
      </h3>
      <p className="text-sm text-slate-500 dark:text-slate-400 max-w-sm">
        {category === 'all'
          ? 'We\'re currently tracking trends. Check back soon for updates!'
          : `No trending topics in ${category} right now. Try another category.`}
      </p>
    </div>
  )
}

// Main Component
export default function TrendingTopics() {
  const [trends, setTrends] = useState<Trend[]>([])
  const [selectedCategory, setSelectedCategory] = useState<Category>('all')
  const [isLoading, setIsLoading] = useState(true)
  const [isGenerating, setIsGenerating] = useState<string | null>(null)
  const { showToast } = useToast()

  // Mock data - replace with actual API calls
  const fetchTrends = useCallback(async () => {
    try {
      setIsLoading(true)
      // const data = await getTrendingTopics()
      // Mock data
      await new Promise(resolve => setTimeout(resolve, 800))

      const mockTrends: Trend[] = [
        {
          id: '1',
          title: 'AI Content Creation Tools',
          category: 'tech',
          velocity: 92,
          relevanceScore: 95,
          mentionCount: 125000,
          growthRate: 45,
          isHot: true,
          isCold: false,
          timestamp: new Date().toISOString(),
          relatedHashtags: ['#AIContent', '#ContentCreation', '#AItools', '#MarketingAI'],
          description: 'Revolutionary AI tools transforming how marketers create and optimize content at scale.',
        },
        {
          id: '2',
          title: 'Short-Form Video Marketing',
          category: 'business',
          velocity: 88,
          relevanceScore: 90,
          mentionCount: 98000,
          growthRate: 32,
          isHot: true,
          isCold: false,
          timestamp: new Date(Date.now() - 86400000).toISOString(),
          relatedHashtags: ['#ShortFormVideo', '#TikTok', '#Reels', '#VideoMarketing'],
          description: 'Brands leveraging TikTok, Reels, and Shorts for maximum engagement.',
        },
        {
          id: '3',
          title: 'Sustainable Fashion Trends',
          category: 'fashion',
          velocity: 65,
          relevanceScore: 60,
          mentionCount: 45000,
          growthRate: 18,
          isHot: false,
          isCold: false,
          timestamp: new Date(Date.now() - 172800000).toISOString(),
          relatedHashtags: ['#SustainableFashion', '#EcoFriendly', '#SlowFashion', '#GreenStyle'],
          description: 'Consumer shift towards eco-conscious and ethical fashion choices.',
        },
        {
          id: '4',
          title: 'Remote Work Best Practices',
          category: 'business',
          velocity: 72,
          relevanceScore: 75,
          mentionCount: 67000,
          growthRate: 8,
          isHot: false,
          isCold: false,
          timestamp: new Date(Date.now() - 259200000).toISOString(),
          relatedHashtags: ['#RemoteWork', '#WorkFromHome', '#DigitalNomad', '#Productivity'],
          description: 'Companies refining their remote and hybrid work strategies.',
        },
        {
          id: '5',
          title: 'Web3 and Blockchain Marketing',
          category: 'tech',
          velocity: 45,
          relevanceScore: 40,
          mentionCount: 28000,
          growthRate: -15,
          isHot: false,
          isCold: true,
          timestamp: new Date(Date.now() - 345600000).toISOString(),
          relatedHashtags: ['#Web3', '#Blockchain', '#Crypto', '#NFTMarketing'],
          description: 'Marketing strategies adapting to decentralized technologies.',
        },
        {
          id: '6',
          title: 'Gaming Industry Growth',
          category: 'gaming',
          velocity: 78,
          relevanceScore: 55,
          mentionCount: 82000,
          growthRate: 28,
          isHot: false,
          isCold: false,
          timestamp: new Date(Date.now() - 432000000).toISOString(),
          relatedHashtags: ['#Gaming', '#Esports', '#GameDev', '#Streaming'],
          description: 'Gaming continues to expand across demographics and platforms.',
        },
        {
          id: '7',
          title: 'Mindfulness and Wellness',
          category: 'lifestyle',
          velocity: 58,
          relevanceScore: 50,
          mentionCount: 39000,
          growthRate: 12,
          isHot: false,
          isCold: false,
          timestamp: new Date(Date.now() - 518400000).toISOString(),
          relatedHashtags: ['#Mindfulness', '#Wellness', '#SelfCare', '#MentalHealth'],
          description: 'Growing focus on mental health and holistic well-being.',
        },
        {
          id: '8',
          title: 'Streaming Wars Analysis',
          category: 'entertainment',
          velocity: 81,
          relevanceScore: 70,
          mentionCount: 74000,
          growthRate: 22,
          isHot: false,
          isCold: false,
          timestamp: new Date(Date.now() - 604800000).toISOString(),
          relatedHashtags: ['#Streaming', '#Netflix', '#OTT', '#ContentWars'],
          description: 'Competition intensifies among major streaming platforms.',
        },
        {
          id: '9',
          title: 'Climate Tech Innovation',
          category: 'science',
          velocity: 69,
          relevanceScore: 45,
          mentionCount: 52000,
          growthRate: 24,
          isHot: false,
          isCold: false,
          timestamp: new Date(Date.now() - 691200000).toISOString(),
          relatedHashtags: ['#ClimateTech', '#GreenTech', '#Sustainability', '#Innovation'],
          description: 'Breakthrough technologies addressing climate challenges.',
        },
      ]

      setTrends(mockTrends)
    } catch (error) {
      showToast('Failed to load trending topics', 'error')
    } finally {
      setIsLoading(false)
    }
  }, [showToast])

  useEffect(() => {
    fetchTrends()
  }, [fetchTrends])

  const handleGenerate = async (trendId: string) => {
    setIsGenerating(trendId)
    try {
      // await generateFromTrend(trendId)
      await new Promise(resolve => setTimeout(resolve, 1500))
      showToast('Content generated successfully!', 'success')
    } catch (error) {
      showToast('Failed to generate content', 'error')
    } finally {
      setIsGenerating(null)
    }
  }

  const filteredTrends = selectedCategory === 'all'
    ? trends
    : trends.filter(t => t.category === selectedCategory)

  const hotTrendsCount = trends.filter(t => t.isHot).length
  const newTrendsCount = trends.filter(t => {
    const hoursSince = (Date.now() - new Date(t.timestamp).getTime()) / 3600000
    return hoursSince < 24
  }).length

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
              Trending Topics
            </h2>
            {newTrendsCount > 0 && (
              <Badge variant="primary" size="sm">
                {newTrendsCount} new
              </Badge>
            )}
          </div>
          <p className="text-slate-500 dark:text-slate-400">
Discover what&apos;s trending in your industry and generate content ideas
          </p>
        </div>

        {/* Stats */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-rose-50 dark:bg-rose-900/20">
            <Flame className="w-5 h-5 text-rose-500" />
            <div>
              <p className="text-lg font-bold text-rose-600 dark:text-rose-400">{hotTrendsCount}</p>
              <p className="text-xs text-rose-600/70 dark:text-rose-400/70">Hot trends</p>
            </div>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-50 dark:bg-blue-900/20">
            <Zap className="w-5 h-5 text-blue-500" />
            <div>
              <p className="text-lg font-bold text-blue-600 dark:text-blue-400">{trends.length}</p>
              <p className="text-xs text-blue-600/70 dark:text-blue-400/70">Total tracked</p>
            </div>
          </div>
        </div>
      </div>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2">
        {categories.map((cat) => {
          const Icon = cat.icon
          const count = cat.id === 'all'
            ? trends.length
            : trends.filter(t => t.category === cat.id).length

          return (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200',
                selectedCategory === cat.id
                  ? 'bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 shadow-lg'
                  : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700'
              )}
            >
              <Icon className={cn('w-4 h-4', selectedCategory === cat.id ? '' : cat.color)} />
              <span>{cat.label}</span>
              <span className={cn(
                'ml-1 px-1.5 py-0.5 text-xs rounded-full',
                selectedCategory === cat.id
                  ? 'bg-white/20 text-white'
                  : 'bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-400'
              )}>
                {count}
              </span>
            </button>
          )
        })}
      </div>

      {/* Trends Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="h-80 animate-pulse bg-slate-200 dark:bg-slate-800">{null}</Card>
          ))}
        </div>
      ) : (
        <motion.div
          layout
          className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4"
        >
          <AnimatePresence mode="popLayout">
            {filteredTrends.length === 0 ? (
              <EmptyState category={selectedCategory} />
            ) : (
              filteredTrends.map((trend) => (
                <TrendCard
                  key={trend.id}
                  trend={trend}
                  onGenerate={handleGenerate}
                  isGenerating={isGenerating === trend.id}
                />
              ))
            )}
          </AnimatePresence>
        </motion.div>
      )}
    </div>
  )
}

// Compact Widget for Sidebar
export function TrendingTopicsWidget() {
  const [trends, setTrends] = useState<Trend[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const { showToast } = useToast()

  useEffect(() => {
    const fetchWidgetTrends = async () => {
      try {
        // const data = await getTrendingTopics({ limit: 3 })
        await new Promise(resolve => setTimeout(resolve, 500))

        const mockTrends: Trend[] = [
          {
            id: '1',
            title: 'AI Content Creation Tools',
            category: 'tech',
            velocity: 92,
            relevanceScore: 95,
            mentionCount: 125000,
            growthRate: 45,
            isHot: true,
            isCold: false,
            timestamp: new Date().toISOString(),
            relatedHashtags: ['#AIContent', '#ContentCreation'],
          },
          {
            id: '2',
            title: 'Short-Form Video Marketing',
            category: 'business',
            velocity: 88,
            relevanceScore: 90,
            mentionCount: 98000,
            growthRate: 32,
            isHot: true,
            isCold: false,
            timestamp: new Date(Date.now() - 86400000).toISOString(),
            relatedHashtags: ['#ShortFormVideo', '#TikTok'],
          },
          {
            id: '3',
            title: 'Sustainable Fashion Trends',
            category: 'fashion',
            velocity: 65,
            relevanceScore: 60,
            mentionCount: 45000,
            growthRate: 18,
            isHot: false,
            isCold: false,
            timestamp: new Date(Date.now() - 172800000).toISOString(),
            relatedHashtags: ['#SustainableFashion'],
          },
        ]

        setTrends(mockTrends)
      } catch (error) {
        showToast('Failed to load trends', 'error')
      } finally {
        setIsLoading(false)
      }
    }

    fetchWidgetTrends()
  }, [showToast])

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-16 rounded-xl animate-pulse bg-slate-200 dark:bg-slate-800" />
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {trends.map((trend, idx) => (
        <motion.div
          key={trend.id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: idx * 0.1 }}
          className="group flex items-center gap-3 p-3 rounded-xl bg-white/50 dark:bg-slate-800/50 hover:bg-white dark:hover:bg-slate-800 border border-slate-200/50 dark:border-slate-700/50 cursor-pointer transition-all hover:shadow-md"
        >
          <div className={cn(
            'flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center',
            trend.isHot ? 'bg-rose-100 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400' :
            'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400'
          )}>
            {trend.isHot ? (
              <Flame className="w-4 h-4" />
            ) : (
              <TrendingUp className="w-4 h-4" />
            )}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-900 dark:text-slate-100 truncate">
              {trend.title}
            </p>
            <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
              <span className={cn(
                trend.growthRate > 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'
              )}>
                {trend.growthRate > 0 ? '+' : ''}{trend.growthRate}%
              </span>
              <span>•</span>
              <span>{trend.relevanceScore}% relevant</span>
            </div>
          </div>
          <ArrowUpRight className="w-4 h-4 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity" />
        </motion.div>
      ))}
    </div>
  )
}
