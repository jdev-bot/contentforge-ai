'use client'

import { useState, useEffect, useMemo, useCallback } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts'
import { getAnalyticsSummary, exportAnalyticsCSV, exportAnalyticsJSON, AnalyticsSummaryData } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Skeleton } from '@/components/ui/Skeleton'
import {
  FileText,
  Sparkles,
  Share2,
  TrendingUp,
  TrendingDown,
  Activity,
  Calendar,
  Download,
  RefreshCw,
  AlertCircle,
} from 'lucide-react'

type DateRange = '7d' | '30d' | '90d'

const DATE_RANGE_DAYS: Record<DateRange, number> = {
  '7d': 7,
  '30d': 30,
  '90d': 90,
}

const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#6b7280']

export default function AnalyticsDashboard() {
  const [data, setData] = useState<AnalyticsSummaryData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [dateRange, setDateRange] = useState<DateRange>('30d')
  const [exporting, setExporting] = useState<false | 'csv' | 'json'>(false)

  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const analyticsData = await getAnalyticsSummary(DATE_RANGE_DAYS[dateRange])
      setData(analyticsData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics data')
    } finally {
      setLoading(false)
    }
  }, [dateRange])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handleExport = async (format: 'csv' | 'json') => {
    try {
      setExporting(format)
      const blob = format === 'csv' 
        ? await exportAnalyticsCSV(DATE_RANGE_DAYS[dateRange])
        : await exportAnalyticsJSON(DATE_RANGE_DAYS[dateRange])
      
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `analytics_export_${dateRange}_${new Date().toISOString().split('T')[0]}.${format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export data')
    } finally {
      setExporting(false)
    }
  }

  // Prepare chart data
  const usageChartData = useMemo(() => {
    if (!data?.usageMetrics?.daily_counts) return []
    return data.usageMetrics.daily_counts.map(item => ({
      date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      count: item.count,
    }))
  }, [data?.usageMetrics?.daily_counts])

  const contentTypeData = useMemo(() => {
    if (!data?.assetMetrics?.by_type) return []
    return data.assetMetrics.by_type.map(item => ({
      name: item.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
      value: item.count,
    }))
  }, [data?.assetMetrics?.by_type])

  const platformData = useMemo(() => {
    if (!data?.distributionMetrics?.by_platform) return []
    return data.distributionMetrics.by_platform
      .filter(p => p.platform !== 'unknown')
      .map(item => ({
        name: item.platform.charAt(0).toUpperCase() + item.platform.slice(1),
        value: item.count,
        successRate: item.success_rate,
      }))
  }, [data?.distributionMetrics?.by_platform])

  const kpiCards = useMemo(() => {
    if (!data?.dashboardKPIs) return []
    const kpis = data.dashboardKPIs
    
    return [
      {
        title: 'Total Content',
        value: kpis.total_content,
        change: kpis.content_growth_30d,
        changeLabel: 'last 30 days',
        icon: FileText,
        color: 'bg-blue-500',
        bgColor: 'bg-blue-50',
        textColor: 'text-blue-600',
      },
      {
        title: 'Assets Generated',
        value: kpis.total_assets,
        change: kpis.asset_growth_30d,
        changeLabel: 'last 30 days',
        icon: Sparkles,
        color: 'bg-purple-500',
        bgColor: 'bg-purple-50',
        textColor: 'text-purple-600',
      },
      {
        title: 'Distributions',
        value: kpis.total_distributions,
        change: kpis.published_distributions,
        changeLabel: 'published',
        icon: Share2,
        color: 'bg-green-500',
        bgColor: 'bg-green-50',
        textColor: 'text-green-600',
      },
      {
        title: 'Success Rate',
        value: `${Math.round(kpis.distribution_success_rate)}%`,
        change: kpis.distribution_success_rate >= 80 ? 'Good' : kpis.distribution_success_rate >= 50 ? 'Fair' : 'Needs improvement',
        changeLabel: 'status',
        icon: Activity,
        color: 'bg-amber-500',
        bgColor: 'bg-amber-50',
        textColor: 'text-amber-600',
      },
    ]
  }, [data?.dashboardKPIs])

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
          <Button onClick={loadData} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-3 text-red-600">
              <AlertCircle className="h-5 w-5" />
              <p>{error}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
          <p className="text-sm text-gray-500 mt-1">
            Track your content performance and usage metrics
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Date Range Selector */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            {(['7d', '30d', '90d'] as DateRange[]).map((range) => (
              <button
                key={range}
                onClick={() => setDateRange(range)}
                disabled={loading}
                className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${
                  dateRange === range
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {range === '7d' ? '7 Days' : range === '30d' ? '30 Days' : '90 Days'}
              </button>
            ))}
          </div>
          
          {/* Export Buttons */}
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleExport('csv')}
            disabled={exporting !== false || loading}
          >
            <Download className="h-4 w-4 mr-2" />
            {exporting === 'csv' ? 'Exporting...' : 'CSV'}
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleExport('json')}
            disabled={exporting !== false || loading}
          >
            <Download className="h-4 w-4 mr-2" />
            {exporting === 'json' ? 'Exporting...' : 'JSON'}
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {loading
          ? Array.from({ length: 4 }).map((_, i) => (
              <Card key={i}>
                <CardContent className="p-6">
                  <Skeleton className="h-8 w-8 rounded-lg mb-4" />
                  <Skeleton className="h-8 w-16 mb-2" />
                  <Skeleton className="h-4 w-24" />
                </CardContent>
              </Card>
            ))
          : kpiCards.map((kpi) => (
              <Card key={kpi.title} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className={`h-10 w-10 rounded-lg ${kpi.bgColor} flex items-center justify-center`}>
                      <kpi.icon className={`h-5 w-5 ${kpi.textColor}`} />
                    </div>
                    {typeof kpi.change === 'number' && kpi.change >= 0 ? (
                      <TrendingUp className="h-4 w-4 text-green-500" />
                    ) : typeof kpi.change === 'number' ? (
                      <TrendingDown className="h-4 w-4 text-red-500" />
                    ) : null}
                  </div>
                  <div className="mt-4">
                    <p className="text-2xl font-bold text-gray-900">{kpi.value}</p>
                    <p className="text-sm text-gray-500">{kpi.title}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {typeof kpi.change === 'number' ? `+${kpi.change} ` : `${kpi.change} `}
                      {kpi.changeLabel}
                    </p>
                  </div>
                </CardContent>
              </Card>
            ))}
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Usage Over Time */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-gray-900">
              Usage Over Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="h-64 flex items-center justify-center">
                <Skeleton className="h-full w-full" />
              </div>
            ) : usageChartData.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={usageChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis 
                      dataKey="date" 
                      tick={{ fontSize: 12 }}
                      stroke="#6b7280"
                    />
                    <YAxis 
                      tick={{ fontSize: 12 }}
                      stroke="#6b7280"
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'white', 
                        border: '1px solid #e5e7eb',
                        borderRadius: '6px',
                      }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="count" 
                      stroke="#3b82f6" 
                      strokeWidth={2}
                      dot={{ fill: '#3b82f6', strokeWidth: 2 }}
                      activeDot={{ r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex flex-col items-center justify-center text-gray-400">
                <Activity className="h-12 w-12 mb-2" />
                <p>No usage data available</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Content by Type */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-gray-900">
              Assets by Type
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="h-64 flex items-center justify-center">
                <Skeleton className="h-full w-full" />
              </div>
            ) : contentTypeData.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={contentTypeData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis 
                      dataKey="name" 
                      tick={{ fontSize: 12 }}
                      stroke="#6b7280"
                    />
                    <YAxis 
                      tick={{ fontSize: 12 }}
                      stroke="#6b7280"
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'white', 
                        border: '1px solid #e5e7eb',
                        borderRadius: '6px',
                      }}
                    />
                    <Bar 
                      dataKey="value" 
                      fill="#8b5cf6"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex flex-col items-center justify-center text-gray-400">
                <Sparkles className="h-12 w-12 mb-2" />
                <p>No assets generated yet</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Platform Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-gray-900">
              Platform Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="h-64 flex items-center justify-center">
                <Skeleton className="h-full w-full" />
              </div>
            ) : platformData.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={platformData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                      outerRadius={80}
                      dataKey="value"
                    >
                      {platformData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'white', 
                        border: '1px solid #e5e7eb',
                        borderRadius: '6px',
                      }}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex flex-col items-center justify-center text-gray-400">
                <Share2 className="h-12 w-12 mb-2" />
                <p>No distributions yet</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Platform Success Rates */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-gray-900">
              Platform Success Rates
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="h-64 flex items-center justify-center">
                <Skeleton className="h-full w-full" />
              </div>
            ) : platformData.length > 0 ? (
              <div className="space-y-4">
                {platformData.map((platform) => (
                  <div key={platform.name} className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="font-medium text-gray-700">{platform.name}</span>
                      <span className="text-gray-500">{platform.value} distributions</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          platform.successRate >= 80 ? 'bg-green-500' :
                          platform.successRate >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${platform.successRate}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-500">
                      {Math.round(platform.successRate)}% success rate
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="h-64 flex flex-col items-center justify-center text-gray-400">
                <Activity className="h-12 w-12 mb-2" />
                <p>No distribution data available</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Usage Summary */}
      {data?.usageSummary?.stats && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Monthly Usage
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-600">API Calls</span>
                  <span className="font-medium">
                    {data.usageSummary.stats.monthly_usage_count} / {data.usageSummary.stats.monthly_usage_limit > 0 ? data.usageSummary.stats.monthly_usage_limit : '∞'}
                  </span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      data.usageSummary.stats.percentage_used > 80 ? 'bg-red-500' :
                      data.usageSummary.stats.percentage_used > 50 ? 'bg-yellow-500' : 'bg-blue-500'
                    }`}
                    style={{ width: `${Math.min(data.usageSummary.stats.percentage_used, 100)}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {data.usageSummary.stats.percentage_used}% used this month
                  {data.usageSummary.stats.monthly_usage_limit === -1 && ' (Unlimited)'}
                </p>
              </div>
              
              {data.usageSummary.recent_activity.length > 0 && (
                <div className="mt-6">
                  <h4 className="text-sm font-medium text-gray-900 mb-3">Recent Activity</h4>
                  <div className="space-y-2">
                    {data.usageSummary.recent_activity.slice(0, 5).map((activity, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <div className="flex items-center gap-3">
                          <div className="h-2 w-2 rounded-full bg-blue-500" />
                          <span className="text-sm text-gray-700">
                            {activity.event_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </span>
                        </div>
                        <div className="text-xs text-gray-500">
                          {new Date(activity.created_at).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
