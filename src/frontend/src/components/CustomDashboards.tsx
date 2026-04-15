'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
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
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Skeleton } from '@/components/ui/Skeleton'
import {
  LayoutDashboard,
  Plus,
  Trash2,
  Settings,
  RefreshCw,
  BarChart3,
  PieChart as PieChartIcon,
  Activity,
  FileText,
  Users,
  TrendingUp,
  Eye,
  Clock,
  Star,
  GripVertical,
  X,
  ChevronDown,
  AlertCircle,
} from 'lucide-react'
import { formatApiError } from '@/lib/api'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#6b7280', '#06b6d4']

const WIDGET_TYPES = [
  { value: 'metric_card', label: 'Metric Card', icon: Activity },
  { value: 'line_chart', label: 'Line Chart', icon: TrendingUp },
  { value: 'bar_chart', label: 'Bar Chart', icon: BarChart3 },
  { value: 'pie_chart', label: 'Pie Chart', icon: PieChartIcon },
  { value: 'table', label: 'Table', icon: FileText },
  { value: 'counter', label: 'Counter', icon: Eye },
  { value: 'recent_list', label: 'Recent List', icon: Clock },
] as const

const DATA_SOURCES = [
  { value: 'content_count', label: 'Content Count' },
  { value: 'distribution_stats', label: 'Distribution Stats' },
  { value: 'quality_scores', label: 'Quality Scores' },
  { value: 'sentiment_summary', label: 'Sentiment Summary' },
  { value: 'team_activity', label: 'Team Activity' },
  { value: 'usage_stats', label: 'Usage Stats' },
] as const

const REFRESH_INTERVALS = [
  { value: 30, label: '30s' },
  { value: 60, label: '1m' },
  { value: 300, label: '5m' },
  { value: 900, label: '15m' },
  { value: 1800, label: '30m' },
] as const

interface Widget {
  id: string
  dashboard_id: string
  widget_type: string
  title: string
  data_source: string
  refresh_interval: number
  size: { w: number; h: number }
  position: number
  config: Record<string, unknown>
  created_at: string
  updated_at: string
}

interface Dashboard {
  id: string
  user_id: string
  name: string
  description?: string
  layout_config: Record<string, unknown>
  is_default: boolean
  widgets: Widget[]
  created_at: string
  updated_at: string
}

interface WidgetLiveData {
  widget_id: string
  widget_type: string
  title: string
  data_source: string
  refresh_interval: number
  data: Record<string, unknown>
}

async function getAuthHeader(): Promise<Record<string, string>> {
  const { supabase } = await import('@/lib/supabase')
  const { data: { session } } = await supabase.auth.getSession()
  if (!session?.access_token) return {}
  return { 'Authorization': `Bearer ${session.access_token}`, 'Content-Type': 'application/json' }
}

async function apiCall(path: string, options?: RequestInit) {
  const headers = await getAuthHeader()
  const resp = await fetch(`${API_URL}${path}`, { ...options, headers: { ...headers, ...(options?.headers || {}) } })
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(err.detail || 'Request failed')
  }
  if (resp.status === 204) return null
  return resp.json()
}

// ── Widget Components ──────────────────────────────────────────────

function MetricCardWidget({ data, title }: { data: Record<string, unknown>; title: string }) {
  const total = (data.total as number) ?? (data.average as number) ?? 0
  return (
    <div className="flex flex-col items-center justify-center h-full p-4">
      <p className="text-sm text-slate-400 mb-1">{title}</p>
      <p className="text-3xl font-bold text-white">{total.toLocaleString()}</p>
            {(data.by_status && typeof data.by_status === 'object') ? (
        <div className="flex gap-2 mt-2 flex-wrap justify-center">
          {Object.entries(data.by_status as Record<string, number>).map(([status, count]) => (
            <span key={status} className="text-xs px-2 py-0.5 rounded-full bg-slate-700/50 text-slate-300">
              {status}: {count}
            </span>
          ))}
        </div>
      ) : null}
    </div>
  )
}

function LineChartWidget({ data, title }: { data: Record<string, unknown>; title: string }) {
  const chartData = Array.isArray(data.items) ? data.items.map((item: Record<string, unknown>, i: number) => ({
    name: (item.created_at as string)?.slice(5, 10) || `Item ${i + 1}`,
    value: (item.value as number) || (item.count as number) || 0,
  })) : []
  return (
    <div className="h-full flex flex-col">
      <p className="text-sm text-slate-400 mb-2 px-2">{title}</p>
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" stroke="#94a3b8" fontSize={10} />
            <YAxis stroke="#94a3b8" fontSize={10} />
            <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} />
            <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

function BarChartWidget({ data, title }: { data: Record<string, unknown>; title: string }) {
  const chartData = data.by_status
    ? Object.entries(data.by_status as Record<string, number>).map(([k, v]) => ({ name: k, value: v }))
    : data.by_platform
      ? Object.entries(data.by_platform as Record<string, number>).map(([k, v]) => ({ name: k, value: v }))
      : data.by_sentiment
        ? Object.entries(data.by_sentiment as Record<string, number>).map(([k, v]) => ({ name: k, value: v }))
        : []
  return (
    <div className="h-full flex flex-col">
      <p className="text-sm text-slate-400 mb-2 px-2">{title}</p>
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" stroke="#94a3b8" fontSize={10} />
            <YAxis stroke="#94a3b8" fontSize={10} />
            <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} />
            <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

function PieChartWidget({ data, title }: { data: Record<string, unknown>; title: string }) {
  const chartData = data.by_status
    ? Object.entries(data.by_status as Record<string, number>).map(([k, v]) => ({ name: k, value: v }))
    : data.by_platform
      ? Object.entries(data.by_platform as Record<string, number>).map(([k, v]) => ({ name: k, value: v }))
      : data.by_sentiment
        ? Object.entries(data.by_sentiment as Record<string, number>).map(([k, v]) => ({ name: k, value: v }))
        : data.by_event_type
          ? Object.entries(data.by_event_type as Record<string, number>).map(([k, v]) => ({ name: k, value: v }))
          : []
  return (
    <div className="h-full flex flex-col">
      <p className="text-sm text-slate-400 mb-2 px-2">{title}</p>
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius="80%" label fontSize={10}>
              {chartData.map((_, i) => (
                <Cell key={`cell-${i}`} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} />
            <Legend wrapperStyle={{ fontSize: 10, color: '#94a3b8' }} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

function TableWidget({ data, title }: { data: Record<string, unknown>; title: string }) {
  const items = (Array.isArray(data.items) ? data.items : []) as Record<string, unknown>[]
  if (items.length === 0) {
    return (
      <div className="flex items-center justify-center h-full p-4">
        <p className="text-sm text-slate-500">{title} — No data available</p>
      </div>
    )
  }
  const keys = Object.keys(items[0])
  return (
    <div className="h-full flex flex-col">
      <p className="text-sm text-slate-400 mb-2 px-2">{title}</p>
      <div className="flex-1 overflow-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-slate-700/50">
              {keys.slice(0, 4).map(k => (
                <th key={k} className="text-left p-2 text-slate-400 font-medium">{k}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.slice(0, 10).map((item, i) => (
              <tr key={i} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                {keys.slice(0, 4).map(k => (
                  <td key={k} className="p-2 text-slate-300">{String(item[k] ?? '')}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function CounterWidget({ data, title }: { data: Record<string, unknown>; title: string }) {
  const total = (data.total as number) ?? (data.total_events as number) ?? (data.total_tokens as number) ?? (data.recent_items_count as number) ?? 0
  return (
    <div className="flex flex-col items-center justify-center h-full p-4">
      <p className="text-sm text-slate-400 mb-2">{title}</p>
      <p className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
        {total.toLocaleString()}
      </p>
      {typeof data.total_tokens === 'number' && (
        <p className="text-xs text-slate-500 mt-2">{data.total_tokens} tokens used</p>
      )}
    </div>
  )
}

function RecentListWidget({ data, title }: { data: Record<string, unknown>; title: string }) {
  const items = (Array.isArray(data.items) ? data.items : data.recent_items ? data.recent_items : []) as Record<string, unknown>[]
  return (
    <div className="h-full flex flex-col">
      <p className="text-sm text-slate-400 mb-2 px-2">{title}</p>
      <div className="flex-1 overflow-auto space-y-1 px-2">
        {items.slice(0, 8).map((item, i) => (
          <div key={i} className="flex items-center gap-2 py-1.5 border-b border-slate-800/50 text-xs">
            <span className="text-slate-400">{String(item.id ?? '').slice(0, 8)}</span>
            <span className="text-slate-500 ml-auto">{String(item.created_at ?? '').slice(0, 10)}</span>
          </div>
        ))}
        {items.length === 0 && (
          <p className="text-xs text-slate-500 py-4 text-center">No recent items</p>
        )}
      </div>
    </div>
  )
}

function WidgetRenderer({ widget, liveData }: { widget: Widget; liveData?: Record<string, unknown> }) {
  const data = liveData || {}
  const common = { data, title: widget.title }

  switch (widget.widget_type) {
    case 'metric_card': return <MetricCardWidget {...common} />
    case 'line_chart': return <LineChartWidget {...common} />
    case 'bar_chart': return <BarChartWidget {...common} />
    case 'pie_chart': return <PieChartWidget {...common} />
    case 'table': return <TableWidget {...common} />
    case 'counter': return <CounterWidget {...common} />
    case 'recent_list': return <RecentListWidget {...common} />
    default: return <MetricCardWidget {...common} />
  }
}

// ── Widget Config Modal ────────────────────────────────────────────

function WidgetConfigModal({
  isOpen,
  onClose,
  onSave,
  initialData,
}: {
  isOpen: boolean
  onClose: () => void
  onSave: (config: { widget_type: string; title: string; data_source: string; refresh_interval: number }) => void
  initialData?: { widget_type: string; title: string; data_source: string; refresh_interval: number }
}) {
  const [widgetType, setWidgetType] = useState(initialData?.widget_type || 'metric_card')
  const [title, setTitle] = useState(initialData?.title || '')
  const [dataSource, setDataSource] = useState(initialData?.data_source || 'content_count')
  const [refreshInterval, setRefreshInterval] = useState(initialData?.refresh_interval || 60)

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-slate-900/95 border border-slate-700/50 rounded-2xl p-6 w-full max-w-md mx-4 shadow-2xl">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Configure Widget</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-white"><X size={20} /></button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="text-sm text-slate-400 mb-1 block">Widget Type</label>
            <select
              value={widgetType}
              onChange={e => setWidgetType(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm"
            >
              {WIDGET_TYPES.map(w => (
                <option key={w.value} value={w.value}>{w.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm text-slate-400 mb-1 block">Title</label>
            <input
              type="text"
              value={title}
              onChange={e => setTitle(e.target.value)}
              placeholder="Widget title"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm"
            />
          </div>

          <div>
            <label className="text-sm text-slate-400 mb-1 block">Data Source</label>
            <select
              value={dataSource}
              onChange={e => setDataSource(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm"
            >
              {DATA_SOURCES.map(d => (
                <option key={d.value} value={d.value}>{d.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm text-slate-400 mb-1 block">Refresh Interval</label>
            <select
              value={refreshInterval}
              onChange={e => setRefreshInterval(Number(e.target.value))}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm"
            >
              {REFRESH_INTERVALS.map(r => (
                <option key={r.value} value={r.value}>{r.label}</option>
              ))}
            </select>
          </div>

          <div className="flex gap-3 pt-2">
            <Button onClick={onClose} variant="outline" className="flex-1">Cancel</Button>
            <Button
              onClick={() => onSave({ widget_type: widgetType, title, data_source: dataSource, refresh_interval: refreshInterval })}
              disabled={!title.trim()}
              className="flex-1 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white"
            >
              Save Widget
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Main Component ──────────────────────────────────────────────────

export default function CustomDashboards() {
  const [dashboards, setDashboards] = useState<Dashboard[]>([])
  const [activeDashboard, setActiveDashboard] = useState<Dashboard | null>(null)
  const [liveData, setLiveData] = useState<WidgetLiveData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showWidgetModal, setShowWidgetModal] = useState(false)
  const [editingWidget, setEditingWidget] = useState<Widget | null>(null)
  const [creating, setCreating] = useState(false)
  const [newName, setNewName] = useState('')
  const [refreshing, setRefreshing] = useState(false)
  const refreshTimerRef = useRef<NodeJS.Timeout | null>(null)

  const loadDashboards = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiCall('/dashboards') as Dashboard[]
      setDashboards(data)
      // Find default or first dashboard
      const defaultDash = data.find((d: Dashboard) => d.is_default) || data[0]
      if (defaultDash) {
        await selectDashboard(defaultDash.id)
      }
    } catch (err) {
      setError(formatApiError(err, 'Failed to load dashboards'))
    } finally {
      setLoading(false)
    }
  }, [])

  const selectDashboard = useCallback(async (id: string) => {
    try {
      const data = await apiCall(`/dashboards/${id}`) as Dashboard
      setActiveDashboard(data)
      await fetchLiveData(id)
    } catch (err) {
      setError(formatApiError(err, 'Failed to load dashboard'))
    }
  }, [])

  const fetchLiveData = useCallback(async (dashboardId: string) => {
    try {
      setRefreshing(true)
      const data = await apiCall(`/dashboards/${dashboardId}/data`) as { widgets: WidgetLiveData[] }
      setLiveData(data.widgets || [])
    } catch {
      // silently fail — data will be stale
    } finally {
      setRefreshing(false)
    }
  }, [])

  useEffect(() => {
    loadDashboards()
  }, [loadDashboards])

  // Auto-refresh based on shortest widget interval
  useEffect(() => {
    if (refreshTimerRef.current) clearInterval(refreshTimerRef.current)
    if (!activeDashboard) return

    const intervals = activeDashboard.widgets.map(w => w.refresh_interval).filter(Boolean)
    const minInterval = intervals.length > 0 ? Math.min(...intervals) * 1000 : 60000

    refreshTimerRef.current = setInterval(() => {
      if (activeDashboard) fetchLiveData(activeDashboard.id)
    }, minInterval)

    return () => {
      if (refreshTimerRef.current) clearInterval(refreshTimerRef.current)
    }
  }, [activeDashboard, fetchLiveData])

  const handleCreateDashboard = async () => {
    if (!newName.trim()) return
    try {
      setCreating(true)
      const result = await apiCall('/dashboards', {
        method: 'POST',
        body: JSON.stringify({ name: newName.trim() }),
      }) as Dashboard
      setDashboards(prev => [...prev, result])
      setNewName('')
      await selectDashboard(result.id)
    } catch (err) {
      setError(formatApiError(err, 'Failed to create dashboard'))
    } finally {
      setCreating(false)
    }
  }

  const handleDeleteDashboard = async (id: string) => {
    try {
      await apiCall(`/dashboards/${id}`, { method: 'DELETE' })
      setDashboards(prev => prev.filter(d => d.id !== id))
      if (activeDashboard?.id === id) {
        const remaining = dashboards.filter(d => d.id !== id)
        setActiveDashboard(remaining[0] || null)
        setLiveData([])
      }
    } catch (err) {
      setError(formatApiError(err, 'Failed to delete dashboard'))
    }
  }

  const handleSetDefault = async (id: string) => {
    try {
      await apiCall(`/dashboards/${id}`, {
        method: 'PUT',
        body: JSON.stringify({ is_default: true }),
      })
      setDashboards(prev => prev.map(d => ({ ...d, is_default: d.id === id })))
      if (activeDashboard?.id === id) {
        setActiveDashboard(prev => prev ? { ...prev, is_default: true } : null)
      }
    } catch (err) {
      setError(formatApiError(err, 'Failed to set default'))
    }
  }

  const handleAddWidget = async (config: { widget_type: string; title: string; data_source: string; refresh_interval: number }) => {
    if (!activeDashboard) return
    try {
      const widget = await apiCall(`/dashboards/${activeDashboard.id}/widgets`, {
        method: 'POST',
        body: JSON.stringify({ ...config, position: activeDashboard.widgets.length }),
      }) as Widget
      setActiveDashboard(prev => prev ? { ...prev, widgets: [...prev.widgets, widget] } : null)
      setShowWidgetModal(false)
      await fetchLiveData(activeDashboard.id)
    } catch (err) {
      setError(formatApiError(err, 'Failed to add widget'))
    }
  }

  const handleUpdateWidget = async (config: { widget_type: string; title: string; data_source: string; refresh_interval: number }) => {
    if (!activeDashboard || !editingWidget) return
    try {
      await apiCall(`/dashboards/${activeDashboard.id}/widgets/${editingWidget.id}`, {
        method: 'PUT',
        body: JSON.stringify(config),
      })
      setShowWidgetModal(false)
      setEditingWidget(null)
      await selectDashboard(activeDashboard.id)
    } catch (err) {
      setError(formatApiError(err, 'Failed to update widget'))
    }
  }

  const handleDeleteWidget = async (widgetId: string) => {
    if (!activeDashboard) return
    try {
      await apiCall(`/dashboards/${activeDashboard.id}/widgets/${widgetId}`, { method: 'DELETE' })
      setActiveDashboard(prev => prev ? { ...prev, widgets: prev.widgets.filter(w => w.id !== widgetId) } : null)
      setLiveData(prev => prev.filter(w => w.widget_id !== widgetId))
    } catch (err) {
      setError(formatApiError(err, 'Failed to remove widget'))
    }
  }

  const handleRefresh = () => {
    if (activeDashboard) fetchLiveData(activeDashboard.id)
  }

  const getWidgetLiveData = (widgetId: string): Record<string, unknown> | undefined => {
    return liveData.find(w => w.widget_id === widgetId)?.data
  }

  if (loading) {
    return (
      <div className="space-y-6 p-6">
        <Skeleton className="h-10 w-48" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map(i => <Skeleton key={i} className="h-48 rounded-xl" />)}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <LayoutDashboard className="h-6 w-6 text-blue-400" />
          <h2 className="text-2xl font-bold text-white">Custom Dashboards</h2>
        </div>
        <div className="flex items-center gap-2">
          <Button
            onClick={handleRefresh}
            variant="outline"
            size="sm"
            disabled={refreshing}
            className="border-slate-700 text-slate-300 hover:text-white"
          >
            <RefreshCw className={`h-4 w-4 mr-1 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-3 text-red-400 text-sm flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {error}
          <button onClick={() => setError(null)} className="ml-auto text-red-400 hover:text-red-300"><X size={16} /></button>
        </div>
      )}

      {/* Dashboard Tabs + Create */}
      <div className="flex items-center gap-2 flex-wrap">
        {dashboards.map(d => (
          <div key={d.id} className="flex items-center gap-1">
            <button
              onClick={() => selectDashboard(d.id)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                activeDashboard?.id === d.id
                  ? 'bg-blue-500/20 text-blue-400 border border-blue-500/50'
                  : 'bg-slate-800/50 text-slate-400 border border-slate-700/50 hover:text-white hover:border-slate-600'
              }`}
            >
              {d.name}
              {d.is_default && <Star className="inline h-3 w-3 ml-1 text-yellow-400" />}
            </button>
            {dashboards.length > 1 && (
              <button
                onClick={() => handleDeleteDashboard(d.id)}
                className="text-slate-600 hover:text-red-400 transition-colors"
                title="Delete dashboard"
              >
                <Trash2 size={14} />
              </button>
            )}
          </div>
        ))}
        <div className="flex items-center gap-1 ml-2">
          <input
            type="text"
            value={newName}
            onChange={e => setNewName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleCreateDashboard()}
            placeholder="New dashboard name"
            className="bg-slate-800/50 border border-slate-700/50 rounded-lg px-3 py-1.5 text-sm text-white placeholder:text-slate-500 w-44"
          />
          <Button
            onClick={handleCreateDashboard}
            disabled={!newName.trim() || creating}
            size="sm"
            className="bg-gradient-to-r from-blue-500 to-purple-500 text-white"
          >
            <Plus size={14} className="mr-1" />
            Create
          </Button>
        </div>
      </div>

      {/* Dashboard Content */}
      {activeDashboard ? (
        <div className="space-y-4">
          {/* Dashboard Header */}
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white">{activeDashboard.name}</h3>
              {activeDashboard.description && (
                <p className="text-sm text-slate-400">{activeDashboard.description}</p>
              )}
            </div>
            <div className="flex items-center gap-2">
              {!activeDashboard.is_default && (
                <Button
                  onClick={() => handleSetDefault(activeDashboard.id)}
                  variant="outline"
                  size="sm"
                  className="border-slate-700 text-slate-300 hover:text-white"
                >
                  <Star size={14} className="mr-1" />
                  Set Default
                </Button>
              )}
              <Button
                onClick={() => { setEditingWidget(null); setShowWidgetModal(true) }}
                size="sm"
                className="bg-gradient-to-r from-blue-500 to-purple-500 text-white"
              >
                <Plus size={14} className="mr-1" />
                Add Widget
              </Button>
            </div>
          </div>

          {/* Widget Grid */}
          {activeDashboard.widgets.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {activeDashboard.widgets.map(widget => (
                <Card
                  key={widget.id}
                  className="bg-slate-900/50 backdrop-blur-sm border-slate-700/50 hover:border-slate-600/50 transition-all group"
                  style={{ gridColumn: `span ${Math.min(widget.size?.w || 1, 4)}` }}
                >
                  <CardHeader className="pb-2 flex-row items-center justify-between space-y-0">
                    <div className="flex items-center gap-2">
                      <GripVertical size={14} className="text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity cursor-grab" />
                      <CardTitle className="text-sm font-medium text-slate-300">{widget.title}</CardTitle>
                    </div>
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => {
                          setEditingWidget(widget)
                          setShowWidgetModal(true)
                        }}
                        className="text-slate-500 hover:text-blue-400 transition-colors"
                        title="Configure widget"
                      >
                        <Settings size={14} />
                      </button>
                      <button
                        onClick={() => handleDeleteWidget(widget.id)}
                        className="text-slate-500 hover:text-red-400 transition-colors"
                        title="Remove widget"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0" style={{ minHeight: widget.size?.h ? `${widget.size.h * 80}px` : '200px' }}>
                    <WidgetRenderer widget={widget} liveData={getWidgetLiveData(widget.id)} />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            /* Empty state */
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <div className="w-16 h-16 rounded-2xl bg-slate-800/50 flex items-center justify-center mb-4">
                <LayoutDashboard className="h-8 w-8 text-slate-500" />
              </div>
              <h3 className="text-lg font-medium text-slate-300 mb-2">No widgets yet</h3>
              <p className="text-sm text-slate-500 max-w-sm mb-4">
                Add widgets to your dashboard to visualize content metrics, distributions, and more.
              </p>
              <Button
                onClick={() => { setEditingWidget(null); setShowWidgetModal(true) }}
                className="bg-gradient-to-r from-blue-500 to-purple-500 text-white"
              >
                <Plus size={16} className="mr-2" />
                Add Your First Widget
              </Button>
            </div>
          )}
        </div>
      ) : (
        /* No dashboards */
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="w-16 h-16 rounded-2xl bg-slate-800/50 flex items-center justify-center mb-4">
            <LayoutDashboard className="h-8 w-8 text-slate-500" />
          </div>
          <h3 className="text-lg font-medium text-slate-300 mb-2">No dashboards yet</h3>
          <p className="text-sm text-slate-500 max-w-sm mb-4">
            Create your first custom dashboard to track the metrics that matter most to you.
          </p>
        </div>
      )}

      {/* Widget Config Modal */}
      <WidgetConfigModal
        isOpen={showWidgetModal}
        onClose={() => { setShowWidgetModal(false); setEditingWidget(null) }}
        onSave={editingWidget ? handleUpdateWidget : handleAddWidget}
        initialData={editingWidget ? {
          widget_type: editingWidget.widget_type,
          title: editingWidget.title,
          data_source: editingWidget.data_source,
          refresh_interval: editingWidget.refresh_interval,
        } : undefined}
      />
    </div>
  )
}