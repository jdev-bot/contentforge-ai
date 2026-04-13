'use client'

import { useState, useMemo, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Plus,
  Search,
  TrendingUp,
  TrendingDown,
  Minus,
  Users,
  Eye,
  Heart,
  Share2,
  MessageCircle,
  MoreVertical,
  Trash2,
  RefreshCw,
  Target,
  Zap,
  BarChart3,
  LineChart,
  ArrowUpRight,
  ArrowDownRight,
  Filter,
  ExternalLink,
  Clock,
  AlertCircle
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/Card'
import { Avatar } from '@/components/ui/Avatar'
import { Tooltip } from '@/components/ui/Tooltip'
import { Input, Select } from '@/components/ui/Input'
import { cn } from '@/lib/utils'

// Types
export interface Competitor {
  id: string
  name: string
  platform: 'linkedin' | 'twitter' | 'facebook' | 'instagram' | 'youtube' | 'blog'
  handle: string
  profileUrl?: string
  avatar?: string
  followers: number
  engagementRate: number
  avgViews: number
  postsPerWeek: number
  lastPostDate?: Date
  trackedSince: Date
  isActive: boolean
}

export interface CompetitorPost {
  id: string
  competitorId: string
  title: string
  content: string
  platform: string
  publishedAt: Date
  metrics: {
    views: number
    likes: number
    comments: number
    shares: number
    engagement: number
  }
  url?: string
}

export interface PerformanceComparison {
  metric: string
  yourValue: number
  competitorAvg: number
  gap: number
  trend: 'up' | 'down' | 'stable'
}

// Mock data
const mockCompetitors: Competitor[] = [
  {
    id: '1',
    name: 'TechCorp Insights',
    platform: 'linkedin',
    handle: '@techcorp',
    followers: 45000,
    engagementRate: 4.2,
    avgViews: 12000,
    postsPerWeek: 5,
    trackedSince: new Date('2024-01-15'),
    isActive: true,
  },
  {
    id: '2',
    name: 'Marketing Pro',
    platform: 'twitter',
    handle: '@marketingpro',
    followers: 32000,
    engagementRate: 3.8,
    avgViews: 8500,
    postsPerWeek: 12,
    trackedSince: new Date('2024-02-01'),
    isActive: true,
  },
  {
    id: '3',
    name: 'Growth Daily',
    platform: 'linkedin',
    handle: '@growthdaily',
    followers: 67000,
    engagementRate: 5.1,
    avgViews: 18000,
    postsPerWeek: 3,
    trackedSince: new Date('2024-03-10'),
    isActive: true,
  },
]

const mockCompetitorPosts: CompetitorPost[] = [
  {
    id: '1',
    competitorId: '1',
    title: '10 AI Trends for 2025',
    content: 'The AI landscape is evolving rapidly. Here are the top trends...',
    platform: 'linkedin',
    publishedAt: new Date(Date.now() - 86400000),
    metrics: { views: 25000, likes: 1200, comments: 89, shares: 234, engagement: 6.1 },
    url: 'https://linkedin.com/post/1',
  },
  {
    id: '2',
    competitorId: '1',
    title: 'Marketing Automation Guide',
    content: 'How to automate your marketing workflows...',
    platform: 'linkedin',
    publishedAt: new Date(Date.now() - 172800000),
    metrics: { views: 18000, likes: 890, comments: 45, shares: 156, engagement: 6.1 },
    url: 'https://linkedin.com/post/2',
  },
  {
    id: '3',
    competitorId: '2',
    title: 'Thread: Social Media Tips',
    content: '1/ 🧵 Here are 10 social media tips that changed my business...',
    platform: 'twitter',
    publishedAt: new Date(Date.now() - 43200000),
    metrics: { views: 45000, likes: 2300, comments: 234, shares: 890, engagement: 7.5 },
    url: 'https://twitter.com/post/3',
  },
  {
    id: '4',
    competitorId: '3',
    title: 'The Future of Content Marketing',
    content: 'Content marketing is changing. Here\'s what you need to know...',
    platform: 'linkedin',
    publishedAt: new Date(Date.now() - 259200000),
    metrics: { views: 32000, likes: 1500, comments: 123, shares: 340, engagement: 6.2 },
    url: 'https://linkedin.com/post/4',
  },
]

const mockComparison: PerformanceComparison[] = [
  { metric: 'Followers', yourValue: 28500, competitorAvg: 48000, gap: -40.6, trend: 'up' },
  { metric: 'Engagement Rate', yourValue: 4.5, competitorAvg: 4.4, gap: 2.3, trend: 'stable' },
  { metric: 'Avg Views', yourValue: 11200, competitorAvg: 15600, gap: -28.2, trend: 'down' },
  { metric: 'Posts/Week', yourValue: 7, competitorAvg: 6.7, gap: 4.5, trend: 'up' },
]

// Helper functions
const formatNumber = (num: number): string => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const getPlatformIcon = (platform: string) => {
  const icons: Record<string, string> = {
    linkedin: '🔗',
    twitter: '🐦',
    facebook: '📘',
    instagram: '📷',
    youtube: '📺',
    blog: '📝',
  }
  return icons[platform] || '📄'
}

// Components
export default function CompetitorAnalysis() {
  const [competitors, setCompetitors] = useState<Competitor[]>(mockCompetitors)
  const [posts] = useState<CompetitorPost[]>(mockCompetitorPosts)
  const [showAddForm, setShowAddForm] = useState(false)
  const [selectedCompetitor, setSelectedCompetitor] = useState<string | 'all'>('all')
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d')
  const [isRefreshing, setIsRefreshing] = useState(false)

  const filteredPosts = useMemo(() => {
    let filtered = posts
    if (selectedCompetitor !== 'all') {
      filtered = filtered.filter(p => p.competitorId === selectedCompetitor)
    }
    return filtered.sort((a, b) => b.publishedAt.getTime() - a.publishedAt.getTime())
  }, [posts, selectedCompetitor])

  const handleAddCompetitor = useCallback((data: { name: string; platform: string; handle: string }) => {
    const newCompetitor: Competitor = {
      id: Date.now().toString(),
      name: data.name,
      platform: data.platform as Competitor['platform'],
      handle: data.handle,
      followers: 0,
      engagementRate: 0,
      avgViews: 0,
      postsPerWeek: 0,
      trackedSince: new Date(),
      isActive: true,
    }
    setCompetitors(prev => [...prev, newCompetitor])
    setShowAddForm(false)
  }, [])

  const handleRemoveCompetitor = useCallback((id: string) => {
    setCompetitors(prev => prev.filter(c => c.id !== id))
  }, [])

  const handleRefresh = useCallback(() => {
    setIsRefreshing(true)
    setTimeout(() => setIsRefreshing(false), 1500)
  }, [])

  const getCompetitorById = (id: string) => competitors.find(c => c.id === id)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
            Competitor Analysis
          </h2>
          <p className="text-slate-500 dark:text-slate-400 mt-1">
            Track and analyze your competitors' content performance
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            leftIcon={<RefreshCw className={cn('h-4 w-4', isRefreshing && 'animate-spin')} />}
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            Refresh
          </Button>
          
          <Button
            variant="primary"
            size="sm"
            leftIcon={<Plus className="h-4 w-4" />}
            onClick={() => setShowAddForm(true)}
          >
            Add Competitor
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="border-l-4 border-l-blue-500">
          <CardContent className="p-4">
            <p className="text-sm text-slate-500 dark:text-slate-400">Tracked Competitors</p>
            <p className="text-2xl font-bold text-slate-900 dark:text-slate-100 mt-1">
              {competitors.length}
            </p>
          </CardContent>
        </Card>
        
        <Card className="border-l-4 border-l-emerald-500">
          <CardContent className="p-4">
            <p className="text-sm text-slate-500 dark:text-slate-400">Avg Engagement</p>
            <p className="text-2xl font-bold text-slate-900 dark:text-slate-100 mt-1">
              4.4%
            </p>
            <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-1 flex items-center gap-1">
              <TrendingUp className="h-3 w-3" />
              +0.3% vs yours
            </p>
          </CardContent>
        </Card>
        
        <Card className="border-l-4 border-l-violet-500">
          <CardContent className="p-4">
            <p className="text-sm text-slate-500 dark:text-slate-400">Content Tracked</p>
            <p className="text-2xl font-bold text-slate-900 dark:text-slate-100 mt-1">
              {posts.length}
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Last 30 days
            </p>
          </CardContent>
        </Card>
        
        <Card className="border-l-4 border-l-amber-500">
          <CardContent className="p-4">
            <p className="text-sm text-slate-500 dark:text-slate-400">Top Performer</p>
            <p className="text-lg font-bold text-slate-900 dark:text-slate-100 mt-1 truncate">
              Growth Daily
            </p>
            <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-1 flex items-center gap-1">
              <TrendingUp className="h-3 w-3" />
              5.1% engagement
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Performance Comparison */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 dark:bg-blue-500/20 rounded-lg">
                <BarChart3 className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <CardTitle>Performance Comparison</CardTitle>
                <CardDescription>How you compare to competitor averages</CardDescription>
              </div>
            </div>
            
            <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 rounded-lg p-1">
              {(['7d', '30d', '90d'] as const).map((range) => (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={cn(
                    'px-3 py-1 text-sm font-medium rounded-md transition-colors',
                    timeRange === range
                      ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 shadow-sm'
                      : 'text-slate-600 dark:text-slate-400'
                  )}
                >
                  {range}
                </button>
              ))}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mockComparison.map((item) => (
              <div key={item.metric} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-slate-900 dark:text-slate-100">
                    {item.metric}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      'text-sm font-medium',
                      item.gap > 0 
                        ? 'text-emerald-600 dark:text-emerald-400' 
                        : 'text-rose-600 dark:text-rose-400'
                    )}>
                      {item.gap > 0 ? '+' : ''}{item.gap}%
                    </span>
                    {item.trend === 'up' && <TrendingUp className="h-4 w-4 text-emerald-500" />}
                    {item.trend === 'down' && <TrendingDown className="h-4 w-4 text-rose-500" />}
                    {item.trend === 'stable' && <Minus className="h-4 w-4 text-slate-400" />}
                  </div>
                </div>
                
                <div className="relative h-8 bg-slate-100 dark:bg-slate-800 rounded-lg overflow-hidden">
                  <div className="absolute inset-y-0 left-0 flex">
                    <div
                      className="h-full bg-blue-500 flex items-center justify-end px-2"
                      style={{ width: `${Math.min((item.yourValue / (item.competitorAvg * 1.5)) * 50, 50)}%` }}
                    >
                      <span className="text-xs font-medium text-white whitespace-nowrap">
                        You: {typeof item.yourValue === 'number' && item.yourValue > 1000 
                          ? formatNumber(item.yourValue) 
                          : item.yourValue}
                      </span>
                    </div>
                  </div>
                  
                  <div className="absolute inset-y-0 right-0 flex">
                    <div
                      className="h-full bg-slate-400 dark:bg-slate-600 flex items-center px-2"
                      style={{ width: `${Math.min((item.competitorAvg / (item.yourValue * 1.5)) * 50, 50)}%` }}
                    >
                      <span className="text-xs font-medium text-white whitespace-nowrap">
                        Avg: {typeof item.competitorAvg === 'number' && item.competitorAvg > 1000 
                          ? formatNumber(item.competitorAvg) 
                          : item.competitorAvg}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Competitor List */}
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Tracked Competitors</CardTitle>
                <Badge variant="primary" size="sm">
                  {competitors.filter(c => c.isActive).length} Active
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {competitors.map((competitor) => (
                <motion.div
                  key={competitor.id}
                  layout
                  className={cn(
                    'p-4 rounded-xl border-2 transition-all cursor-pointer',
                    selectedCompetitor === competitor.id
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-500/10'
                      : 'border-slate-100 dark:border-slate-700 hover:border-slate-200 dark:hover:border-slate-600'
                  )}
                  onClick={() => setSelectedCompetitor(
                    selectedCompetitor === competitor.id ? 'all' : competitor.id
                  )}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <Avatar 
                        name={competitor.name} 
                        size="md"
                        className="bg-gradient-to-br from-blue-500 to-violet-500"
                      />
                      <div>
                        <p className="font-medium text-slate-900 dark:text-slate-100">
                          {competitor.name}
                        </p>
                        <p className="text-sm text-slate-500 dark:text-slate-400">
                          {competitor.handle}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="outline" size="sm">
                            {getPlatformIcon(competitor.platform)} {competitor.platform}
                          </Badge>
                          <span className="text-xs text-slate-400">
                            {formatNumber(competitor.followers)} followers
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-1">
                      <Tooltip content="View profile" position="top">
                        <button 
                          className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                          onClick={(e) => {
                            e.stopPropagation()
                            window.open(competitor.profileUrl || '#', '_blank')
                          }}
                        >
                          <ExternalLink className="h-4 w-4 text-slate-400" />
                        </button>
                      </Tooltip>
                      
                      <Tooltip content="Remove" position="top">
                        <button 
                          className="p-2 hover:bg-rose-100 dark:hover:bg-rose-900/30 rounded-lg transition-colors"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleRemoveCompetitor(competitor.id)
                          }}
                        >
                          <Trash2 className="h-4 w-4 text-rose-500" />
                        </button>
                      </Tooltip>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-2 mt-4 pt-4 border-t border-slate-100 dark:border-slate-700">
                    <div>
                      <p className="text-xs text-slate-500 dark:text-slate-400">Engagement</p>
                      <p className="font-semibold text-slate-900 dark:text-slate-100">
                        {competitor.engagementRate}%
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 dark:text-slate-400">Avg Views</p>
                      <p className="font-semibold text-slate-900 dark:text-slate-100">
                        {formatNumber(competitor.avgViews)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 dark:text-slate-400">Posts/Week</p>
                      <p className="font-semibold text-slate-900 dark:text-slate-100">
                        {competitor.postsPerWeek}
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
              
              <Button
                variant="outline"
                className="w-full"
                leftIcon={<Plus className="h-4 w-4" />}
                onClick={() => setShowAddForm(true)}
              >
                Add Competitor
              </Button>
            </CardContent>
          </Card>

          {/* Gap Analysis */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-amber-100 dark:bg-amber-500/20 rounded-lg">
                  <Target className="h-5 w-5 text-amber-600 dark:text-amber-400" />
                </div>
                <div>
                  <CardTitle>Gap Analysis</CardTitle>
                  <CardDescription>Opportunities identified</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="p-3 bg-emerald-50 dark:bg-emerald-500/10 rounded-lg">
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                  <span className="font-medium text-emerald-700 dark:text-emerald-300">
                    Strength
                  </span>
                </div>
                <p className="text-sm text-emerald-600 dark:text-emerald-400 mt-1">
                  Your posting frequency (+7/week) is above competitor average
                </p>
              </div>
              
              <div className="p-3 bg-rose-50 dark:bg-rose-500/10 rounded-lg">
                <div className="flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-rose-600 dark:text-rose-400" />
                  <span className="font-medium text-rose-700 dark:text-rose-300">
                    Gap
                  </span>
                </div>
                <p className="text-sm text-rose-600 dark:text-rose-400 mt-1">
                  Average views per post are 28% lower than competitors
                </p>
              </div>
              
              <div className="p-3 bg-blue-50 dark:bg-blue-500/10 rounded-lg">
                <div className="flex items-center gap-2">
                  <LineChart className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                  <span className="font-medium text-blue-700 dark:text-blue-300">
                    Trend
                  </span>
                </div>
                <p className="text-sm text-blue-600 dark:text-blue-400 mt-1">
                  Engagement rate is stable and competitive
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Competitor Content Feed */}
        <div className="lg:col-span-2">
          <Card className="h-full">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-violet-100 dark:bg-violet-500/20 rounded-lg">
                    <Eye className="h-5 w-5 text-violet-600 dark:text-violet-400" />
                  </div>
                  <div>
                    <CardTitle>Competitor Content Feed</CardTitle>
                    <CardDescription>Latest posts from tracked competitors</CardDescription>
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <Filter className="h-4 w-4 text-slate-400" />
                    <select
                      value={selectedCompetitor}
                      onChange={(e) => setSelectedCompetitor(e.target.value)}
                      className="text-sm bg-transparent border-none focus:ring-0 text-slate-700 dark:text-slate-300 cursor-pointer"
                    >
                      <option value="all">All Competitors</option>
                      {competitors.map(c => (
                        <option key={c.id} value={c.id}>{c.name}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="space-y-4">
              {filteredPosts.length === 0 ? (
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Search className="h-8 w-8 text-slate-400" />
                  </div>
                  <p className="text-slate-500 dark:text-slate-400">No posts found</p>
                  <p className="text-sm text-slate-400 dark:text-slate-500 mt-1">
                    Try adjusting your filters
                  </p>
                </div>
              ) : (
                filteredPosts.map((post) => {
                  const competitor = getCompetitorById(post.competitorId)
                  if (!competitor) return null
                  
                  return (
                    <motion.div
                      key={post.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="p-4 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-blue-300 dark:hover:border-blue-600 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-3">
                          <Avatar name={competitor.name} size="sm" />
                          <div>
                            <p className="font-medium text-slate-900 dark:text-slate-100">
                              {competitor.name}
                            </p>
                            <div className="flex items-center gap-2">
                              <Badge variant="outline" size="sm">
                                {getPlatformIcon(post.platform)} {post.platform}
                              </Badge>
                              <span className="text-xs text-slate-400">
                                <Clock className="h-3 w-3 inline mr-1" />
                                {post.publishedAt.toLocaleDateString()}
                              </span>
                            </div>
                          </div>
                        </div>
                        
                        <Tooltip content="View post" position="top">
                          <button 
                            className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                            onClick={() => window.open(post.url || '#', '_blank')}
                          >
                            <ExternalLink className="h-4 w-4 text-slate-400" />
                          </button>
                        </Tooltip>
                      </div>
                      
                      <h4 className="font-medium text-slate-900 dark:text-slate-100 mt-3">
                        {post.title}
                      </h4>
                      
                      <p className="text-sm text-slate-600 dark:text-slate-400 mt-1 line-clamp-2">
                        {post.content}
                      </p>
                      
                      <div className="flex items-center gap-4 mt-4 pt-4 border-t border-slate-100 dark:border-slate-700">
                        <div className="flex items-center gap-1.5">
                          <Eye className="h-4 w-4 text-slate-400" />
                          <span className="text-sm text-slate-600 dark:text-slate-400">
                            {formatNumber(post.metrics.views)}
                          </span>
                        </div>
                        
                        <div className="flex items-center gap-1.5">
                          <Heart className="h-4 w-4 text-rose-400" />
                          <span className="text-sm text-slate-600 dark:text-slate-400">
                            {formatNumber(post.metrics.likes)}
                          </span>
                        </div>
                        
                        <div className="flex items-center gap-1.5">
                          <MessageCircle className="h-4 w-4 text-blue-400" />
                          <span className="text-sm text-slate-600 dark:text-slate-400">
                            {formatNumber(post.metrics.comments)}
                          </span>
                        </div>
                        
                        <div className="flex items-center gap-1.5">
                          <Share2 className="h-4 w-4 text-emerald-400" />
                          <span className="text-sm text-slate-600 dark:text-slate-400">
                            {formatNumber(post.metrics.shares)}
                          </span>
                        </div>
                        
                        <div className="ml-auto">
                          <Badge 
                            variant={post.metrics.engagement > 5 ? 'success' : 'primary'} 
                            size="sm"
                          >
                            {post.metrics.engagement}% engagement
                          </Badge>
                        </div>
                      </div>
                    </motion.div>
                  )
                })
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Add Competitor Modal */}
      <AnimatePresence>
        {showAddForm && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
              onClick={() => setShowAddForm(false)}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="fixed inset-0 m-auto w-full max-w-md h-fit bg-white dark:bg-slate-900 rounded-2xl shadow-2xl z-50 overflow-hidden"
            >
              <AddCompetitorForm 
                onSubmit={handleAddCompetitor}
                onCancel={() => setShowAddForm(false)}
              />
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}

// Add Competitor Form Component
function AddCompetitorForm({
  onSubmit,
  onCancel,
}: {
  onSubmit: (data: { name: string; platform: string; handle: string }) => void
  onCancel: () => void
}) {
  const [formData, setFormData] = useState({
    name: '',
    platform: 'linkedin',
    handle: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (formData.name && formData.handle) {
      onSubmit(formData)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="p-6 border-b border-slate-200 dark:border-slate-700">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
          Add Competitor
        </h3>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Track a new competitor to analyze their content performance
        </p>
      </div>
      
      <div className="p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Competitor Name
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g., TechCorp Insights"
            className="w-full px-4 py-2 rounded-xl border-2 border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:border-blue-500 focus:outline-none"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Platform
          </label>
          <select
            value={formData.platform}
            onChange={(e) => setFormData({ ...formData, platform: e.target.value })}
            className="w-full px-4 py-2 rounded-xl border-2 border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:border-blue-500 focus:outline-none"
          >
            <option value="linkedin">LinkedIn</option>
            <option value="twitter">Twitter/X</option>
            <option value="facebook">Facebook</option>
            <option value="instagram">Instagram</option>
            <option value="youtube">YouTube</option>
            <option value="blog">Blog</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Handle/Username
          </label>
          <input
            type="text"
            value={formData.handle}
            onChange={(e) => setFormData({ ...formData, handle: e.target.value })}
            placeholder="e.g., @companyname"
            className="w-full px-4 py-2 rounded-xl border-2 border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:border-blue-500 focus:outline-none"
            required
          />
        </div>
      </div>
      
      <div className="p-6 border-t border-slate-200 dark:border-slate-700 flex gap-3">
        <Button type="submit" variant="primary" className="flex-1">
          Add Competitor
        </Button>
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  )
}
