'use client'

import { useState, useEffect } from 'react'
import { getAnalyticsStats, getUsageSummary, UsageActivity, AnalyticsStats } from '@/lib/api'
import { Card, CardContent } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { 
  FileText, 
  Sparkles, 
  Share2, 
  TrendingUp, 
  Activity,
  Calendar
} from 'lucide-react'

export default function AnalyticsTab() {
  const [stats, setStats] = useState<AnalyticsStats | null>(null)
  const [usage, setUsage] = useState<{ stats: { monthly_usage_count: number; monthly_usage_limit: number; percentage_used: number }; recent_activity: UsageActivity[] } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadAnalytics()
  }, [])

  async function loadAnalytics() {
    try {
      setLoading(true)
      const [analyticsData, usageData] = await Promise.all([
        getAnalyticsStats().catch(() => ({ content_count: 0, assets_generated: 0, distributions_published: 0 })),
        getUsageSummary().catch(() => ({ stats: { monthly_usage_count: 0, monthly_usage_limit: 100, percentage_used: 0 }, recent_activity: [] })),
      ])
      setStats(analyticsData)
      setUsage(usageData)
    } catch (err: any) {
      setError(err.message || 'Failed to load analytics')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const getActivityIcon = (eventType: string) => {
    switch (eventType) {
      case 'content_generation':
        return <FileText className="h-4 w-4 text-blue-500" />
      case 'asset_generation':
        return <Sparkles className="h-4 w-4 text-purple-500" />
      case 'distribution':
        return <Share2 className="h-4 w-4 text-green-500" />
      default:
        return <Activity className="h-4 w-4 text-gray-500" />
    }
  }

  const getActivityLabel = (eventType: string) => {
    const labels: Record<string, string> = {
      content_generation: 'Content created',
      asset_generation: 'Asset generated',
      distribution: 'Content published',
      api_call: 'API call made',
    }
    return labels[eventType] || 'Activity recorded'
  }

  // Simple bar chart data
  const barData = [
    { label: 'Content', value: stats?.content_count || 0, color: 'bg-blue-500' },
    { label: 'Assets', value: stats?.assets_generated || 0, color: 'bg-purple-500' },
    { label: 'Published', value: stats?.distributions_published || 0, color: 'bg-green-500' },
  ]

  const maxValue = Math.max(...barData.map(d => d.value), 1)

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Analytics</h2>
        </div>
        
        {/* Skeleton Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <Skeleton className="h-8 w-8 rounded-lg mb-4" />
                <Skeleton className="h-8 w-16 mb-2" />
                <Skeleton className="h-4 w-24" />
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Skeleton Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardContent className="p-6">
              <Skeleton className="h-6 w-32 mb-6" />
              <Skeleton className="h-48 w-full" />
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <Skeleton className="h-6 w-32 mb-6" />
              <div className="space-y-3">
                {[...Array(5)].map((_, i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900">Analytics</h2>
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Analytics</h2>
        <span className="text-sm text-gray-500">
          Last updated: {new Date().toLocaleDateString()}
        </span>
      </div>

      {/* Usage Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="h-12 w-12 rounded-lg bg-blue-100 flex items-center justify-center">
                <FileText className="h-6 w-6 text-blue-600" />
              </div>
              <TrendingUp className="h-5 w-5 text-green-500" />
            </div>
            <div className="mt-4">
              <p className="text-3xl font-bold text-gray-900">{stats?.content_count || 0}</p>
              <p className="text-sm text-gray-500 mt-1">Content Pieces</p>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="h-12 w-12 rounded-lg bg-purple-100 flex items-center justify-center">
                <Sparkles className="h-6 w-6 text-purple-600" />
              </div>
              <TrendingUp className="h-5 w-5 text-green-500" />
            </div>
            <div className="mt-4">
              <p className="text-3xl font-bold text-gray-900">{stats?.assets_generated || 0}</p>
              <p className="text-sm text-gray-500 mt-1">Assets Generated</p>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="h-12 w-12 rounded-lg bg-green-100 flex items-center justify-center">
                <Share2 className="h-6 w-6 text-green-600" />
              </div>
              <TrendingUp className="h-5 w-5 text-green-500" />
            </div>
            <div className="mt-4">
              <p className="text-3xl font-bold text-gray-900">{stats?.distributions_published || 0}</p>
              <p className="text-sm text-gray-500 mt-1">Published</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts and Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Simple Bar Chart */}
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Content Overview</h3>
            <div className="h-48 flex items-end justify-around gap-4">
              {barData.map((item) => (
                <div key={item.label} className="flex flex-col items-center flex-1">
                  <div className="relative w-full flex items-end justify-center">
                    <div
                      className={`w-16 ${item.color} rounded-t-lg transition-all duration-500`}
                      style={{
                        height: `${(item.value / maxValue) * 160}px`,
                      }}
                    />
                  </div>
                  <p className="text-2xl font-bold text-gray-900 mt-2">{item.value}</p>
                  <p className="text-xs text-gray-500">{item.label}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Usage Progress */}
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Usage</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-600">API Calls</span>
                  <span className="font-medium">
                    {usage?.stats.monthly_usage_count || 0} / {usage?.stats.monthly_usage_limit || 100}
                  </span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      (usage?.stats.percentage_used || 0) > 80 ? 'bg-red-500' : 
                      (usage?.stats.percentage_used || 0) > 50 ? 'bg-yellow-500' : 'bg-blue-500'
                    }`}
                    style={{ width: `${Math.min(usage?.stats.percentage_used || 0, 100)}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {usage?.stats.percentage_used || 0}% used this month
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          {usage?.recent_activity && usage.recent_activity.length > 0 ? (
            <div className="space-y-3">
              {usage.recent_activity.slice(0, 10).map((activity, index) => (
                <div
                  key={index}
                  className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="h-8 w-8 rounded-full bg-white flex items-center justify-center shadow-sm">
                    {getActivityIcon(activity.event_type)}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      {getActivityLabel(activity.event_type)}
                    </p>
                    <p className="text-xs text-gray-500 flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {formatDate(activity.created_at)}
                    </p>
                  </div>
                  {activity.tokens_used && (
                    <span className="text-xs text-gray-500">
                      {activity.tokens_used} tokens
                    </span>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Activity className="h-12 w-12 mx-auto mb-3 text-gray-300" />
              <p>No recent activity</p>
              <p className="text-sm text-gray-400">Start creating content to see activity here</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
