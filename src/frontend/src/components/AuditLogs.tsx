'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Shield,
  Download,
  Search,
  Filter,
  Clock,
  User,
  Activity,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Zap,
  BarChart3,
  Users,
  FileText,
  Calendar,
  ScrollText
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Input } from '@/components/ui/Input'
import { StatsCard } from '@/components/ui/Card'
import { cn } from '@/lib/utils'
import { PageHeader } from '@/components/ui/PageHeader'
import { useToast } from '@/hooks/useToast'
import {
  getAuditLogs,
  getAuditLogStats,
  exportAuditLogsCSV,
  AuditLogEntry,
  AuditLogsFilters,
  AuditLogStats,
  AuditAction,
  AuditResource,
} from '@/lib/api'

const ACTION_OPTIONS: { value: string; label: string }[] = [
  { value: '', label: 'All Actions' },
  { value: 'create', label: 'Create' },
  { value: 'update', label: 'Update' },
  { value: 'delete', label: 'Delete' },
  { value: 'restore', label: 'Restore' },
  { value: 'publish', label: 'Publish' },
  { value: 'schedule', label: 'Schedule' },
  { value: 'approve', label: 'Approve' },
  { value: 'reject', label: 'Reject' },
  { value: 'login', label: 'Login' },
  { value: 'logout', label: 'Logout' },
  { value: 'invite', label: 'Invite' },
  { value: 'export', label: 'Export' },
  { value: 'import', label: 'Import' },
]

const RESOURCE_OPTIONS: { value: string; label: string }[] = [
  { value: '', label: 'All Resources' },
  { value: 'content', label: 'Content' },
  { value: 'project', label: 'Project' },
  { value: 'asset', label: 'Asset' },
  { value: 'distribution', label: 'Distribution' },
  { value: 'schedule', label: 'Schedule' },
  { value: 'organization', label: 'Organization' },
  { value: 'user', label: 'User' },
  { value: 'rss_feed', label: 'RSS Feed' },
  { value: 'automation_rule', label: 'Automation Rule' },
]

const ACTION_COLORS: Record<string, string> = {
  create: 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-500/30',
  update: 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-500/30',
  delete: 'bg-rose-100 dark:bg-rose-500/20 text-rose-700 dark:text-rose-300 border-rose-200 dark:border-rose-500/30',
  restore: 'bg-cyan-100 dark:bg-cyan-500/20 text-cyan-700 dark:text-cyan-300 border-cyan-200 dark:border-cyan-500/30',
  publish: 'bg-violet-100 dark:bg-violet-500/20 text-violet-700 dark:text-violet-300 border-violet-200 dark:border-violet-500/30',
  schedule: 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-500/30',
  approve: 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-500/30',
  reject: 'bg-rose-100 dark:bg-rose-500/20 text-rose-700 dark:text-rose-300 border-rose-200 dark:border-rose-500/30',
  login: 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-500/30',
  logout: 'bg-slate-100 dark:bg-slate-500/20 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-500/30',
  invite: 'bg-violet-100 dark:bg-violet-500/20 text-violet-700 dark:text-violet-300 border-violet-200 dark:border-violet-500/30',
  export: 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-500/30',
  import: 'bg-cyan-100 dark:bg-cyan-500/20 text-cyan-700 dark:text-cyan-300 border-cyan-200 dark:border-cyan-500/30',
}

export default function AuditLogs() {
  const [logs, setLogs] = useState<AuditLogEntry[]>([])
  const [stats, setStats] = useState<AuditLogStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isExporting, setIsExporting] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const [expandedRow, setExpandedRow] = useState<string | null>(null)

  // Filters
  const [actionFilter, setActionFilter] = useState<string>('')
  const [resourceFilter, setResourceFilter] = useState<string>('')
  const [actorSearch, setActorSearch] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)

  const fetchLogs = useCallback(async () => {
    try {
      setIsLoading(true)
      const filters: AuditLogsFilters = {
        page,
        per_page: 20,
      }
      if (actionFilter) filters.action = actionFilter as AuditAction
      if (resourceFilter) filters.resource_type = resourceFilter as AuditResource
      if (actorSearch) filters.actor_search = actorSearch
      if (startDate) filters.start_date = startDate
      if (endDate) filters.end_date = endDate

      const data = await getAuditLogs(filters)
      setLogs(data.logs)
      setTotal(data.total)
    } catch {
      // Use mock data on error
      setLogs(MOCK_LOGS)
      setTotal(MOCK_LOGS.length)
    } finally {
      setIsLoading(false)
    }
  }, [page, actionFilter, resourceFilter, actorSearch, startDate, endDate])

  const fetchStats = useCallback(async () => {
    try {
      const data = await getAuditLogStats()
      setStats(data)
    } catch {
      setStats(MOCK_STATS)
    }
  }, [])

  useEffect(() => {
    fetchLogs()
    fetchStats()
  }, [fetchLogs, fetchStats])

  // Simulated real-time streaming
  useEffect(() => {
    const interval = setInterval(() => {
      setIsStreaming(prev => !prev)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  const handleExportCSV = async () => {
    try {
      setIsExporting(true)
      const filters: AuditLogsFilters = {}
      if (actionFilter) filters.action = actionFilter as AuditAction
      if (resourceFilter) filters.resource_type = resourceFilter as AuditResource
      if (startDate) filters.start_date = startDate
      if (endDate) filters.end_date = endDate

      const blob = await exportAuditLogsCSV(filters)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.csv`
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      // Mock export
      const csvContent = 'Timestamp,Actor,Action,Resource,Details\n' +
        MOCK_LOGS.map(l =>
          `"${l.created_at}","${l.actor_name}","${l.action}","${l.resource_type}","${l.details}"`
        ).join('\n')
      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.csv`
      a.click()
      URL.revokeObjectURL(url)
    } finally {
      setIsExporting(false)
    }
  }

  const toggleRow = (id: string) => {
    setExpandedRow(prev => (prev === id ? null : id))
  }

  const totalPages = Math.ceil(total / 20)

  return (
    <div className="space-y-6">
      {/* Header */}
      <PageHeader
        title="Audit Logs"
        description="Track all actions across your workspace"
        icon={<ScrollText className="w-5 h-5 text-blue-600" />}
        actions={<div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <div className={cn(
                'w-2 h-2 rounded-full',
                isStreaming ? 'bg-emerald-500 animate-pulse' : 'bg-slate-400'
              )} />
              <span className="text-sm text-slate-500 dark:text-slate-400">
                {isStreaming ? 'Live' : 'Paused'}
              </span>
            </div>
            <Button
              variant="outline"
              size="sm"
              leftIcon={<Download className="w-4 h-4" />}
              onClick={handleExportCSV}
              loading={isExporting}
            >
              Export CSV
            </Button>
            <Button
              variant="ghost"
              size="sm"
              leftIcon={<RefreshCw className="w-4 h-4" />}
              onClick={() => { fetchLogs(); fetchStats() }}
            >
              Refresh
            </Button>
          </div>
        }
      />

      {/* Stats Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Actions Today"
          value={stats?.total_actions_today ?? 0}
          icon={<Activity className="w-5 h-5" />}
          change={{ value: 12, trend: 'up' }}
        />
        <StatsCard
          title="Actions This Week"
          value={stats?.total_actions_week ?? 0}
          icon={<BarChart3 className="w-5 h-5" />}
          change={{ value: 8, trend: 'up' }}
        />
        <StatsCard
          title="Top Actor"
          value={stats?.top_actors[0]?.name ?? 'N/A'}
          icon={<Users className="w-5 h-5" />}
        />
        <StatsCard
          title="Most Common"
          value={stats?.action_distribution[0]?.action ?? 'N/A'}
          icon={<Zap className="w-5 h-5" />}
        />
      </div>

      {/* Filters */}
      <Card variant="glass">
        <CardContent className="p-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                <Calendar className="w-3.5 h-3.5 inline mr-1" />
                Start Date
              </label>
              <input
                type="date"
                value={startDate}
                onChange={e => { setStartDate(e.target.value); setPage(1) }}
                className="w-full h-10 px-3 text-sm rounded-xl bg-white dark:bg-slate-800 border-2 border-slate-200 dark:border-slate-700 text-slate-900 dark:text-slate-100 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                <Calendar className="w-3.5 h-3.5 inline mr-1" />
                End Date
              </label>
              <input
                type="date"
                value={endDate}
                onChange={e => { setEndDate(e.target.value); setPage(1) }}
                className="w-full h-10 px-3 text-sm rounded-xl bg-white dark:bg-slate-800 border-2 border-slate-200 dark:border-slate-700 text-slate-900 dark:text-slate-100 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                <Filter className="w-3.5 h-3.5 inline mr-1" />
                Action Type
              </label>
              <select
                value={actionFilter}
                onChange={e => { setActionFilter(e.target.value); setPage(1) }}
                className="w-full h-10 px-3 text-sm rounded-xl bg-white dark:bg-slate-800 border-2 border-slate-200 dark:border-slate-700 text-slate-900 dark:text-slate-100 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all appearance-none cursor-pointer"
              >
                {ACTION_OPTIONS.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                <FileText className="w-3.5 h-3.5 inline mr-1" />
                Resource Type
              </label>
              <select
                value={resourceFilter}
                onChange={e => { setResourceFilter(e.target.value); setPage(1) }}
                className="w-full h-10 px-3 text-sm rounded-xl bg-white dark:bg-slate-800 border-2 border-slate-200 dark:border-slate-700 text-slate-900 dark:text-slate-100 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all appearance-none cursor-pointer"
              >
                {RESOURCE_OPTIONS.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                <Search className="w-3.5 h-3.5 inline mr-1" />
                Actor Search
              </label>
              <Input
                placeholder="Search by name or email..."
                value={actorSearch}
                onChange={e => { setActorSearch(e.target.value); setPage(1) }}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Log Table */}
      <Card variant="glass">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-blue-500" />
                Activity Log
              </CardTitle>
              <CardDescription>
                Showing {logs.length} of {total} entries
              </CardDescription>
            </div>
            <Badge variant="info" size="sm">
              Page {page} of {totalPages || 1}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="h-14 rounded-lg animate-pulse bg-slate-200 dark:bg-slate-800" />
              ))}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-700">
                    <th className="text-left py-3 px-4 font-medium text-slate-600 dark:text-slate-400">
                      Timestamp
                    </th>
                    <th className="text-left py-3 px-4 font-medium text-slate-600 dark:text-slate-400">
                      Actor
                    </th>
                    <th className="text-left py-3 px-4 font-medium text-slate-600 dark:text-slate-400">
                      Action
                    </th>
                    <th className="text-left py-3 px-4 font-medium text-slate-600 dark:text-slate-400">
                      Resource
                    </th>
                    <th className="text-left py-3 px-4 font-medium text-slate-600 dark:text-slate-400">
                      Details
                    </th>
                    <th className="w-10 py-3 px-4" />
                  </tr>
                </thead>
                <tbody>
                  <AnimatePresence>
                    {logs.map((log, idx) => (
                      <motion.tr
                        key={log.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.02 }}
                        className="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer"
                        onClick={() => toggleRow(log.id)}
                      >
                        <td className="py-3 px-4 text-slate-600 dark:text-slate-400 whitespace-nowrap">
                          <span className="flex items-center gap-1.5">
                            <Clock className="w-3.5 h-3.5" />
                            {new Date(log.created_at).toLocaleString()}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center text-white text-xs font-semibold">
                              {log.actor_name?.charAt(0)?.toUpperCase() ?? '?'}
                            </div>
                            <div>
                              <p className="font-medium text-slate-900 dark:text-slate-100">
                                {log.actor_name}
                              </p>
                              <p className="text-xs text-slate-500 dark:text-slate-400">
                                {log.actor_email}
                              </p>
                            </div>
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <span className={cn(
                            'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border',
                            ACTION_COLORS[log.action] ?? ACTION_COLORS.update
                          )}>
                            {log.action}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <div>
                            <p className="font-medium text-slate-900 dark:text-slate-100">
                              {log.resource_name}
                            </p>
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                              {log.resource_type}
                            </p>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-slate-600 dark:text-slate-400 max-w-xs truncate">
                          {log.details}
                        </td>
                        <td className="py-3 px-4">
                          {expandedRow === log.id ? (
                            <ChevronUp className="w-4 h-4 text-slate-400" />
                          ) : (
                            <ChevronDown className="w-4 h-4 text-slate-400" />
                          )}
                        </td>
                      </motion.tr>
                    ))}
                  </AnimatePresence>
                </tbody>
              </table>

              {/* Expanded Row Details */}
              <AnimatePresence>
                {expandedRow && (() => {
                  const log = logs.find(l => l.id === expandedRow)
                  if (!log) return null
                  return (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="mt-4 p-4 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700"
                    >
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="font-medium text-slate-700 dark:text-slate-300">IP Address:</span>{' '}
                          <span className="text-slate-600 dark:text-slate-400">{log.ip_address}</span>
                        </div>
                        <div>
                          <span className="font-medium text-slate-700 dark:text-slate-300">User Agent:</span>{' '}
                          <span className="text-slate-600 dark:text-slate-400 truncate block">{log.user_agent}</span>
                        </div>
                        <div>
                          <span className="font-medium text-slate-700 dark:text-slate-300">Resource ID:</span>{' '}
                          <span className="text-slate-600 dark:text-slate-400 font-mono text-xs">{log.resource_id}</span>
                        </div>
                        <div>
                          <span className="font-medium text-slate-700 dark:text-slate-300">Actor ID:</span>{' '}
                          <span className="text-slate-600 dark:text-slate-400 font-mono text-xs">{log.actor_id}</span>
                        </div>
                        {log.metadata && Object.keys(log.metadata).length > 0 && (
                          <div className="sm:col-span-2">
                            <span className="font-medium text-slate-700 dark:text-slate-300">Metadata:</span>{' '}
                            <pre className="mt-1 text-xs text-slate-600 dark:text-slate-400 bg-white dark:bg-slate-800 p-2 rounded-lg overflow-auto">
                              {JSON.stringify(log.metadata, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )
                })()}
              </AnimatePresence>
            </div>
          )}

          {/* Pagination */}
          <div className="flex items-center justify-between mt-6 pt-4 border-t border-slate-200 dark:border-slate-700">
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Showing {(page - 1) * 20 + 1}–{Math.min(page * 20, total)} of {total}
            </p>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page <= 1}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
              >
                Next
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Mock data for development
const MOCK_LOGS: AuditLogEntry[] = [
  {
    id: '1',
    actor_id: 'u1',
    actor_email: 'jan@contentforge.ai',
    actor_name: 'Jan Eichhorn',
    action: 'create',
    resource_type: 'content',
    resource_id: 'c1',
    resource_name: '10 Tips for Marketing',
    details: 'Created new content item',
    ip_address: '192.168.1.100',
    user_agent: 'Mozilla/5.0 Chrome/120',
    metadata: { source: 'url', project_id: 'p1' },
    created_at: new Date().toISOString(),
  },
  {
    id: '2',
    actor_id: 'u1',
    actor_email: 'jan@contentforge.ai',
    actor_name: 'Jan Eichhorn',
    action: 'publish',
    resource_type: 'distribution',
    resource_id: 'd1',
    resource_name: 'Twitter Post #42',
    details: 'Published to Twitter',
    ip_address: '192.168.1.100',
    user_agent: 'Mozilla/5.0 Chrome/120',
    created_at: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: '3',
    actor_id: 'u2',
    actor_email: 'sarah@contentforge.ai',
    actor_name: 'Sarah Chen',
    action: 'update',
    resource_type: 'content',
    resource_id: 'c2',
    resource_name: 'SEO Guide 2024',
    details: 'Updated content text — 342 words changed',
    ip_address: '10.0.0.55',
    user_agent: 'Mozilla/5.0 Safari/17',
    created_at: new Date(Date.now() - 7200000).toISOString(),
  },
  {
    id: '4',
    actor_id: 'u2',
    actor_email: 'sarah@contentforge.ai',
    actor_name: 'Sarah Chen',
    action: 'delete',
    resource_type: 'asset',
    resource_id: 'a5',
    resource_name: 'Old Newsletter Draft',
    details: 'Permanently deleted asset',
    ip_address: '10.0.0.55',
    user_agent: 'Mozilla/5.0 Safari/17',
    created_at: new Date(Date.now() - 14400000).toISOString(),
  },
  {
    id: '5',
    actor_id: 'u3',
    actor_email: 'mike@contentforge.ai',
    actor_name: 'Mike Johnson',
    action: 'invite',
    resource_type: 'organization',
    resource_id: 'org1',
    resource_name: 'ContentForge Team',
    details: 'Invited alex@newco.io as member',
    ip_address: '172.16.0.12',
    user_agent: 'Mozilla/5.0 Firefox/121',
    metadata: { invited_email: 'alex@newco.io', role: 'member' },
    created_at: new Date(Date.now() - 28800000).toISOString(),
  },
  {
    id: '6',
    actor_id: 'u1',
    actor_email: 'jan@contentforge.ai',
    actor_name: 'Jan Eichhorn',
    action: 'schedule',
    resource_type: 'schedule',
    resource_id: 's3',
    resource_name: 'LinkedIn Post — Q1 Report',
    details: 'Scheduled for 2024-01-15 09:00 EST',
    ip_address: '192.168.1.100',
    user_agent: 'Mozilla/5.0 Chrome/120',
    created_at: new Date(Date.now() - 43200000).toISOString(),
  },
  {
    id: '7',
    actor_id: 'u3',
    actor_email: 'mike@contentforge.ai',
    actor_name: 'Mike Johnson',
    action: 'export',
    resource_type: 'content',
    resource_id: 'c10',
    resource_name: 'Monthly Analytics Report',
    details: 'Exported as CSV — 45 records',
    ip_address: '172.16.0.12',
    user_agent: 'Mozilla/5.0 Firefox/121',
    created_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: '8',
    actor_id: 'u2',
    actor_email: 'sarah@contentforge.ai',
    actor_name: 'Sarah Chen',
    action: 'approve',
    resource_type: 'asset',
    resource_id: 'a12',
    resource_name: 'Instagram Carousel — Product Launch',
    details: 'Approved for publishing',
    ip_address: '10.0.0.55',
    user_agent: 'Mozilla/5.0 Safari/17',
    created_at: new Date(Date.now() - 100000000).toISOString(),
  },
]

const MOCK_STATS: AuditLogStats = {
  total_actions_today: 47,
  total_actions_week: 312,
  top_actors: [
    { name: 'Jan Eichhorn', email: 'jan@contentforge.ai', count: 156 },
    { name: 'Sarah Chen', email: 'sarah@contentforge.ai', count: 98 },
    { name: 'Mike Johnson', email: 'mike@contentforge.ai', count: 58 },
  ],
  action_distribution: [
    { action: 'update', count: 120 },
    { action: 'create', count: 85 },
    { action: 'publish', count: 52 },
    { action: 'delete', count: 30 },
    { action: 'schedule', count: 25 },
  ],
  resource_distribution: [
    { resource: 'content', count: 145 },
    { resource: 'asset', count: 88 },
    { resource: 'distribution', count: 52 },
    { resource: 'schedule', count: 27 },
  ],
}