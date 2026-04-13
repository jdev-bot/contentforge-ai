'use client'

import { useState, useEffect, useCallback } from 'react'
import { Card, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Skeleton } from '@/components/ui/Skeleton'
import { Button } from '@/components/ui/Button'
import { getUpcomingPosts, ScheduledPost } from '@/lib/api'
import { useToast } from '@/hooks/useToast'
import { 
  Calendar, 
  Clock, 
  ChevronRight,
  Hash,
  AlertCircle
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface UpcomingPostsWidgetProps {
  onViewAll?: () => void
  onEditPost?: (post: ScheduledPost) => void
  maxItems?: number
}

const PLATFORM_ICONS: Record<string, string> = {
  twitter: '𝕏',
  linkedin: 'in',
  facebook: 'f',
  instagram: '📷',
  threads: '🧵',
  tiktok: '🎵',
  youtube: '▶',
  newsletter: '📧',
  blog: '📝',
}

const STATUS_COLORS: Record<string, string> = {
  scheduled: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300',
  published: 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300',
  failed: 'bg-rose-100 dark:bg-rose-900/30 text-rose-700 dark:text-rose-300',
  cancelled: 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400',
  processing: 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300',
}

export default function UpcomingPostsWidget({ 
  onViewAll, 
  onEditPost,
  maxItems = 5 
}: UpcomingPostsWidgetProps) {
  const { showToast } = useToast()
  const [posts, setPosts] = useState<ScheduledPost[]>([])
  const [loading, setLoading] = useState(true)

  const loadPosts = useCallback(async () => {
    try {
      setLoading(true)
      const data = await getUpcomingPosts(maxItems)
      setPosts(data)
    } catch (error) {
      console.error('Failed to load upcoming posts:', error)
    } finally {
      setLoading(false)
    }
  }, [maxItems])

  useEffect(() => {
    loadPosts()
    // Refresh every minute to keep times accurate
    const interval = setInterval(loadPosts, 60000)
    return () => clearInterval(interval)
  }, [loadPosts])

  const formatTimeUntil = useCallback((scheduledAt: string) => {
    const scheduled = new Date(scheduledAt)
    const now = new Date()
    const diffMs = scheduled.getTime() - now.getTime()
    
    if (diffMs < 0) return 'Overdue'
    
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)
    
    if (diffDays > 0) return `${diffDays}d ${diffHours % 24}h`
    if (diffHours > 0) return `${diffHours}h ${diffMins % 60}m`
    if (diffMins > 0) return `${diffMins}m`
    return 'Now'
  }, [])

  const formatScheduledDate = useCallback((scheduledAt: string) => {
    const date = new Date(scheduledAt)
    const now = new Date()
    const isToday = date.toDateString() === now.toDateString()
    const isTomorrow = new Date(now.getTime() + 86400000).toDateString() === date.toDateString()
    
    if (isToday) {
      return `Today at ${date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}`
    }
    if (isTomorrow) {
      return `Tomorrow at ${date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}`
    }
    
    return date.toLocaleString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      hour: 'numeric', 
      minute: '2-digit' 
    })
  }, [])

  if (loading) {
    return (
      <Card className="border border-slate-200 dark:border-slate-700">
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-4">
            <Skeleton className="h-5 w-32" />
            <Skeleton className="h-4 w-12" />
          </div>
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="flex items-start gap-3">
                <Skeleton className="h-10 w-10 rounded-lg flex-shrink-0" />
                <div className="flex-1 min-w-0 space-y-2">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/2" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (posts.length === 0) {
    return (
      <Card className="border border-slate-200 dark:border-slate-700">
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <Calendar className="h-4 w-4 text-violet-600" />
              Upcoming Posts
            </h3>
          </div>
          
          <div className="text-center py-6">
            <p className="text-sm text-slate-500 dark:text-slate-400">
              No upcoming posts scheduled
            </p>
            <Button 
              variant="ghost" 
              size="sm" 
              className="mt-2 text-violet-600"
              onClick={onViewAll}
            >
              View Calendar
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border border-slate-200 dark:border-slate-700">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <Calendar className="h-4 w-4 text-violet-600" />
            Upcoming Posts
            <span className="text-xs font-normal text-slate-500">
              ({posts.length})
            </span>
          </h3>
          
          <button
            onClick={onViewAll}
            className="text-xs text-violet-600 hover:text-violet-700 flex items-center gap-1 transition-colors"
          >
            View All
            <ChevronRight className="h-3 w-3" />
          </button>
        </div>
        
        <div className="space-y-3">
          {posts.map(post => {
            const timeUntil = formatTimeUntil(post.scheduled_at)
            const isUrgent = timeUntil.includes('m') && !timeUntil.includes('d') && !timeUntil.includes('h')
            
            return (
              <div 
                key={post.id}
                onClick={() => onEditPost?.(post)}
                className="group flex items-start gap-3 p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer transition-colors"
              >
                <div className={cn(
                  "w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0",
                  STATUS_COLORS[post.status]?.split(' ')[0] || 'bg-slate-100'
                )}>
                  <Clock className={cn(
                    "h-4 w-4",
                    post.status === 'scheduled' && "text-blue-600",
                    post.status === 'published' && "text-emerald-600"
                  )} />
                </div>
                
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-900 dark:text-slate-100 line-clamp-1">
                    {post.content.substring(0, 60)}
                    {post.content.length > 60 && '...'}
                  </p>
                  
                  <div className="flex items-center gap-2 mt-1 flex-wrap">
                    <span className="text-xs text-slate-500 dark:text-slate-400">
                      {formatScheduledDate(post.scheduled_at)}
                    </span>
                    
                    <Badge 
                      variant="secondary" 
                      size="sm"
                      className={cn(
                        "text-[10px] px-1.5 py-0",
                        isUrgent && "bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300"
                      )}
                    >
                      {timeUntil}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center gap-1 mt-1.5">
                    {post.platforms.slice(0, 4).map(platform => (
                      <span 
                        key={platform}
                        className="text-[10px] bg-slate-100 dark:bg-slate-700 px-1.5 py-0.5 rounded text-slate-600 dark:text-slate-300"
                      >
                        {PLATFORM_ICONS[platform] || platform}
                      </span>
                    ))}
                    {post.platforms.length > 4 && (
                      <span className="text-[10px] text-slate-400">
                        +{post.platforms.length - 4}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
