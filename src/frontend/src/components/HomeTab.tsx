'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { listContent, Content } from '@/lib/api'
import { Card, CardContent, StatsCard } from '@/components/ui/Card'
import { CardHeader } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { Button } from '@/components/ui/Button'
import { EmptyState } from '@/components/ui/EmptyState'
import { PageHeader } from '@/components/ui/PageHeader'
import { cn, formatRelativeTime, getStatusDotColor } from '@/lib/utils'
import {
  FileText,
  Plus,
  Calendar,
  BarChart3,
  TrendingUp,
  Clock,
  FolderOpen,
  Activity,
  ArrowRight,
} from 'lucide-react'

interface HomeTabProps {
  onCreateContent?: () => void
  onCreateProject?: () => void
  onViewSchedule?: () => void
  onTabChange?: (tab: string) => void
}

interface ActivityItem {
  id: string
  title: string
  status: string
  source_type: string
  created_at: string
}

function StatsCardSkeleton() {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-sm border border-slate-200/50 dark:border-slate-700/50">
      <div className="flex items-start justify-between">
        <div className="space-y-3">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-8 w-16" />
        </div>
        <Skeleton className="h-10 w-10 rounded-xl" />
      </div>
    </div>
  )
}

export default function HomeTab({ onCreateContent, onCreateProject, onViewSchedule, onTabChange }: HomeTabProps) {
  const router = useRouter()
  const [content, setContent] = useState<Content[]>([])
  const [loading, setLoading] = useState(true)

  const loadContent = useCallback(async () => {
    try {
      setLoading(true)
      console.log('[HomeTab] loadContent called, fetching...')
      const data = await listContent()
      console.log('[HomeTab] loadContent got data:', data?.length, 'items', data)
      setContent(data)
    } catch (error) {
      console.error('[HomeTab] Failed to load content for home:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadContent()
  }, [loadContent])

  // Compute stats
  const stats = {
    total: content.length,
    completed: content.filter(c => c.status === 'completed').length,
    processing: content.filter(c => c.status === 'processing').length,
    failed: content.filter(c => c.status === 'failed').length,
  }

  // Recent activity (last 5)
  const recentActivity: ActivityItem[] = content
    .slice()
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5)
    .map(item => ({
      id: item.id,
      title: item.title,
      status: item.status,
      source_type: item.source_type,
      created_at: item.created_at,
    }))

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Dashboard"
          description="Overview of your content creation workspace"
          icon={<Activity className="w-5 h-5 text-blue-500" />}
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <StatsCardSkeleton key={i} />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <Skeleton className="h-8 w-48" />
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} className="h-16 w-full" />
            ))}
          </div>
          <div className="space-y-4">
            <Skeleton className="h-8 w-32" />
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} className="h-20 w-full" />
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dashboard"
        description="Overview of your content creation workspace"
        icon={<Activity className="w-5 h-5 text-blue-500" />}
        actions={
          <div className="flex items-center gap-3">
            <Button
              variant="primary"
              size="sm"
              leftIcon={<Plus className="h-4 w-4" />}
              onClick={() => onCreateContent?.() || router.push('/content/new')}
            >
              New Content
            </Button>
          </div>
        }
      />

      {/* Stats Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Total Content"
          value={stats.total}
          icon={<FileText className="w-5 h-5" />}
        />
        <StatsCard
          title="Completed"
          value={stats.completed}
          icon={<TrendingUp className="w-5 h-5" />}
        />
        <StatsCard
          title="Processing"
          value={stats.processing}
          icon={<Clock className="w-5 h-5" />}
        />
        <StatsCard
          title="Failed"
          value={stats.failed}
          icon={<Activity className="w-5 h-5" />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <div className="lg:col-span-2">
          <Card variant="glass">
            <CardHeader divider>
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                  <Clock className="w-5 h-5 text-blue-500" />
                  Recent Activity
                </h3>
                {content.length > 5 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    rightIcon={<ArrowRight className="w-4 h-4" />}
                    onClick={() => onTabChange?.('content')}
                  >
                    View all
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {recentActivity.length === 0 ? (
                <EmptyState
                  title="No activity yet"
                  description="Start creating content to see activity here."
                  icon="inbox"
                  action={{
                    label: 'Create Content',
                    onClick: () => onCreateContent?.() || router.push('/content/new'),
                    icon: <Plus className="w-4 h-4" />,
                  }}
                />
              ) : (
                <div className="space-y-1">
                  {recentActivity.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => router.push(`/content/${item.id}`)}
                      className="w-full flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors text-left group"
                    >
                      <span className={cn(
                        'w-2 h-2 rounded-full flex-shrink-0',
                        getStatusDotColor(item.status)
                      )} />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-900 dark:text-slate-100 truncate group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                          {item.title}
                        </p>
                        <p className="text-xs text-slate-500 dark:text-slate-400 capitalize">
                          {item.source_type} · {item.status}
                        </p>
                      </div>
                      <span className="text-xs text-slate-400 dark:text-slate-500 flex-shrink-0">
                        {formatRelativeTime(item.created_at)}
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="space-y-4">
          <Card variant="glass">
            <CardHeader divider>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                Quick Actions
              </h3>
            </CardHeader>
            <CardContent className="space-y-3">
              <button
                onClick={() => onCreateContent?.() || router.push('/content/new')}
                className="w-full flex items-center gap-3 p-3 rounded-xl bg-gradient-to-r from-blue-500/10 to-violet-500/10 dark:from-blue-500/20 dark:to-violet-500/20 hover:from-blue-500/20 hover:to-violet-500/20 dark:hover:from-blue-500/30 dark:hover:to-violet-500/30 transition-all group"
              >
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center flex-shrink-0">
                  <Plus className="w-5 h-5 text-white" />
                </div>
                <div className="text-left">
                  <p className="text-sm font-medium text-slate-900 dark:text-slate-100">New Content</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Create and transform content</p>
                </div>
              </button>

              <button
                onClick={() => onCreateProject?.() || router.push('/projects/new')}
                className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-all group"
              >
                <div className="w-10 h-10 rounded-lg bg-violet-100 dark:bg-violet-500/20 flex items-center justify-center flex-shrink-0">
                  <FolderOpen className="w-5 h-5 text-violet-600 dark:text-violet-400" />
                </div>
                <div className="text-left">
                  <p className="text-sm font-medium text-slate-900 dark:text-slate-100">New Project</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Organize your content</p>
                </div>
              </button>

              <button
                onClick={() => onViewSchedule?.() || onTabChange?.('schedule')}
                className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-all group"
              >
                <div className="w-10 h-10 rounded-lg bg-emerald-100 dark:bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
                  <Calendar className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                </div>
                <div className="text-left">
                  <p className="text-sm font-medium text-slate-900 dark:text-slate-100">View Schedule</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Manage publishing schedule</p>
                </div>
              </button>

              <button
                onClick={() => onTabChange?.('analytics')}
                className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-all group"
              >
                <div className="w-10 h-10 rounded-lg bg-amber-100 dark:bg-amber-500/20 flex items-center justify-center flex-shrink-0">
                  <BarChart3 className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                </div>
                <div className="text-left">
                  <p className="text-sm font-medium text-slate-900 dark:text-slate-100">Analytics</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">View content performance</p>
                </div>
              </button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}