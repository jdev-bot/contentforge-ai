'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Activity,
  Clock,
  AlertTriangle,
  Plus,
  Edit3,
  Trash2,
  RefreshCw,
  CheckCircle,
  XCircle,
  TrendingUp,
  TrendingDown,
  Zap,
  Shield,
  BarChart3,
  X,
} from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { useToast } from '@/hooks/useToast'
import { cn } from '@/lib/utils'
import {
  createSLAPolicy,
  listSLAPolicies,
  updateSLAPolicy,
  deleteSLAPolicy,
  getSLADashboard,
  getSLAAlertsWithResponse,
  acknowledgeSLAAlert,
  type SLAPolicy,
  type SLADashboardData,
  type SLAAlert as SLAAlertData,
} from '@/lib/api'
import { formatApiError } from '@/lib/api'

type TimeRange = '24h' | '7d' | '30d'

const METRIC_OPTIONS = [
  { value: 'uptime', label: 'Uptime', unit: '%' },
  { value: 'response_time', label: 'Response Time', unit: 'ms' },
  { value: 'error_rate', label: 'Error Rate', unit: '%' },
  { value: 'throughput', label: 'Throughput', unit: 'req/s' },
]

const SEVERITY_OPTIONS = [
  { value: 'critical', label: 'Critical', color: 'text-rose-600 bg-rose-50 dark:bg-rose-900/20 dark:text-rose-400' },
  { value: 'warning', label: 'Warning', color: 'text-amber-600 bg-amber-50 dark:bg-amber-900/20 dark:text-amber-400' },
  { value: 'info', label: 'Info', color: 'text-blue-600 bg-blue-50 dark:bg-blue-900/20 dark:text-blue-400' },
]

const TIME_RANGE_MAP: Record<TimeRange, number> = {
  '24h': 1,
  '7d': 7,
  '30d': 30,
}

export default function SLAMonitoring() {
  const [policies, setPolicies] = useState<SLAPolicy[]>([])
  const [dashboard, setDashboard] = useState<SLADashboardData | null>(null)
  const [alerts, setAlerts] = useState<SLAAlertData[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [timeRange, setTimeRange] = useState<TimeRange>('7d')
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [editingPolicy, setEditingPolicy] = useState<string | null>(null)
  const [showAlertsOnly, setShowAlertsOnly] = useState(false)

  const [formData, setFormData] = useState({
    name: '',
    metric: 'uptime',
    threshold: 99.9,
    window_minutes: 5,
    severity: 'warning',
  })

  const { showToast } = useToast()

  const fetchData = useCallback(async () => {
    try {
      const [pol, dash, alrt] = await Promise.all([
        listSLAPolicies(),
        getSLADashboard(),
        getSLAAlertsWithResponse(),
      ])
      setPolicies(pol)
      setDashboard(dash)
      setAlerts(Array.isArray(alrt) ? alrt : [])
    } catch (error: unknown) {
      const message = formatApiError(error, 'Failed to load SLA data')
      showToast(message, 'error')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [showToast])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const handleRefresh = async () => {
    setRefreshing(true)
    await fetchData()
  }

  const handleCreatePolicy = async () => {
    try {
      await createSLAPolicy(formData)
      showToast('SLA policy created successfully', 'success')
      setShowCreateForm(false)
      resetForm()
      await fetchData()
    } catch (error: unknown) {
      const message = formatApiError(error, 'Failed to create SLA policy')
      showToast(message, 'error')
    }
  }

  const handleUpdatePolicy = async (policyId: string) => {
    try {
      const updates: Record<string, unknown> = {}
      if (formData.name) updates.name = formData.name
      if (formData.metric) updates.metric = formData.metric
      if (formData.threshold !== undefined) updates.threshold = formData.threshold
      if (formData.window_minutes) updates.window_minutes = formData.window_minutes
      if (formData.severity) updates.severity = formData.severity

      await updateSLAPolicy(policyId, updates)
      showToast('SLA policy updated successfully', 'success')
      setEditingPolicy(null)
      resetForm()
      await fetchData()
    } catch (error: unknown) {
      const message = formatApiError(error, 'Failed to update SLA policy')
      showToast(message, 'error')
    }
  }

  const handleDeletePolicy = async (policyId: string) => {
    try {
      await deleteSLAPolicy(policyId)
      showToast('SLA policy deleted', 'success')
      await fetchData()
    } catch (error: unknown) {
      const message = formatApiError(error, 'Failed to delete SLA policy')
      showToast(message, 'error')
    }
  }

  const handleAcknowledgeAlert = async (alertId: string) => {
    try {
      await acknowledgeSLAAlert(alertId)
      showToast('Alert acknowledged', 'success')
      await fetchData()
    } catch (error: unknown) {
      const message = formatApiError(error, 'Failed to acknowledge alert')
      showToast(message, 'error')
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      metric: 'uptime',
      threshold: 99.9,
      window_minutes: 5,
      severity: 'warning',
    })
  }

  const startEdit = (policy: SLAPolicy) => {
    setEditingPolicy(policy.id)
    setFormData({
      name: policy.name,
      metric: policy.metric,
      threshold: policy.threshold,
      window_minutes: policy.window_minutes,
      severity: policy.severity,
    })
    setShowCreateForm(false)
  }

  const getComplianceIcon = (compliant: boolean | undefined) => {
    if (compliant === undefined || compliant === null) {
      return <span className="text-slate-400">—</span>
    }
    return compliant ? (
      <CheckCircle className="h-5 w-5 text-emerald-500" />
    ) : (
      <XCircle className="h-5 w-5 text-rose-500" />
    )
  }

  const getComplianceColor = (compliant: boolean | undefined) => {
    if (compliant === undefined || compliant === null) return 'border-slate-300 bg-slate-50'
    return compliant
      ? 'border-emerald-300 bg-emerald-50 dark:border-emerald-700 dark:bg-emerald-900/20'
      : 'border-rose-300 bg-rose-50 dark:border-rose-700 dark:bg-rose-900/20'
  }

  const getSeverityBadge = (severity: string) => {
    const opt = SEVERITY_OPTIONS.find(s => s.value === severity)
    return opt || SEVERITY_OPTIONS[1]
  }

  const getMetricLabel = (metric: string) => {
    const opt = METRIC_OPTIONS.find(m => m.value === metric)
    return opt ? opt.label : metric
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <PageHeader
        title="SLA Monitoring"
        description="Monitor service level agreements and compliance"
        icon={<Shield className="w-5 h-5 text-blue-600" />}
        actions={
          <div className="flex items-center gap-3">
            {/* Time Range Selector */}
            <div className="flex items-center bg-slate-100 dark:bg-slate-800 rounded-lg p-1">
              {(['24h', '7d', '30d'] as TimeRange[]).map((range) => (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={cn(
                    'px-3 py-1.5 text-sm font-medium rounded-md transition-all',
                    timeRange === range
                      ? 'bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                  )}
                >
                  {range}
                </button>
              ))}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={refreshing}
            >
              <RefreshCw className={cn('h-4 w-4 mr-2', refreshing && 'animate-spin')} />
              Refresh
            </Button>
            <Button
              size="sm"
              onClick={() => { setShowCreateForm(true); setEditingPolicy(null); resetForm() }}
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Policy
            </Button>
          </div>
        }
      />

      {/* Dashboard Cards */}
      {dashboard && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className={cn('border-2', getComplianceColor(dashboard.uptime_percentage >= 99))}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-500 dark:text-slate-400">Uptime</p>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">
                    {dashboard.uptime_percentage.toFixed(2)}%
                  </p>
                </div>
                <Activity className="h-8 w-8 text-emerald-500" />
              </div>
              <div className="mt-2 flex items-center gap-1">
                {getComplianceIcon(dashboard.uptime_percentage >= 99)}
                <span className="text-xs text-slate-500 dark:text-slate-400">
                  {dashboard.uptime_percentage >= 99 ? 'Meeting SLA' : 'Below SLA'}
                </span>
              </div>
            </CardContent>
          </Card>

          <Card className={cn('border-2', getComplianceColor(dashboard.avg_response_time_ms <= 500))}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-500 dark:text-slate-400">Avg Response Time</p>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">
                    {dashboard.avg_response_time_ms.toFixed(0)}ms
                  </p>
                </div>
                <Clock className="h-8 w-8 text-blue-500" />
              </div>
              <div className="mt-2 flex items-center gap-1">
                {getComplianceIcon(dashboard.avg_response_time_ms <= 500)}
                <span className="text-xs text-slate-500 dark:text-slate-400">
                  {dashboard.avg_response_time_ms <= 500 ? 'Meeting SLA' : 'Above threshold'}
                </span>
              </div>
            </CardContent>
          </Card>

          <Card className={cn('border-2', getComplianceColor(dashboard.error_rate <= 1))}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-500 dark:text-slate-400">Error Rate</p>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">
                    {dashboard.error_rate.toFixed(2)}%
                  </p>
                </div>
                <AlertTriangle className="h-8 w-8 text-amber-500" />
              </div>
              <div className="mt-2 flex items-center gap-1">
                {getComplianceIcon(dashboard.error_rate <= 1)}
                <span className="text-xs text-slate-500 dark:text-slate-400">
                  {dashboard.error_rate <= 1 ? 'Meeting SLA' : 'Above threshold'}
                </span>
              </div>
            </CardContent>
          </Card>

          <Card className={cn('border-2', getComplianceColor(dashboard.throughput_rps >= 100))}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-500 dark:text-slate-400">Throughput</p>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">
                    {dashboard.throughput_rps.toFixed(1)} req/s
                  </p>
                </div>
                <BarChart3 className="h-8 w-8 text-purple-500" />
              </div>
              <div className="mt-2 flex items-center gap-1">
                {getComplianceIcon(dashboard.throughput_rps >= 100)}
                <span className="text-xs text-slate-500 dark:text-slate-400">
                  {dashboard.throughput_rps >= 100 ? 'Meeting SLA' : 'Below threshold'}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Create/Edit Form */}
      <AnimatePresence>
        {(showCreateForm || editingPolicy) && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>{editingPolicy ? 'Edit SLA Policy' : 'Create SLA Policy'}</span>
                  <button
                    onClick={() => { setShowCreateForm(false); setEditingPolicy(null); resetForm() }}
                    className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                    Policy Name
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white"
                    placeholder="e.g., Production Uptime SLA"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                      Metric
                    </label>
                    <select
                      value={formData.metric}
                      onChange={(e) => setFormData(prev => ({ ...prev, metric: e.target.value }))}
                      className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white"
                    >
                      {METRIC_OPTIONS.map(opt => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                      Severity
                    </label>
                    <select
                      value={formData.severity}
                      onChange={(e) => setFormData(prev => ({ ...prev, severity: e.target.value }))}
                      className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white"
                    >
                      {SEVERITY_OPTIONS.map(opt => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                      Threshold
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.threshold}
                      onChange={(e) => setFormData(prev => ({ ...prev, threshold: parseFloat(e.target.value) || 0 }))}
                      className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                      Window (minutes)
                    </label>
                    <input
                      type="number"
                      value={formData.window_minutes}
                      onChange={(e) => setFormData(prev => ({ ...prev, window_minutes: parseInt(e.target.value) || 5 }))}
                      className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white"
                    />
                  </div>
                </div>

                <div className="flex justify-end gap-3">
                  <Button
                    variant="outline"
                    onClick={() => { setShowCreateForm(false); setEditingPolicy(null); resetForm() }}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={() => editingPolicy ? handleUpdatePolicy(editingPolicy) : handleCreatePolicy()}
                    disabled={!formData.name}
                  >
                    {editingPolicy ? 'Update Policy' : 'Create Policy'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Policies List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-blue-500" />
            SLA Policies
            <Badge variant="secondary">{policies.length}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {policies.length === 0 ? (
            <div className="text-center py-8 text-slate-500 dark:text-slate-400">
              <Shield className="h-12 w-12 mx-auto mb-3 opacity-30" />
              <p>No SLA policies configured yet</p>
              <p className="text-sm mt-1">Create a policy to start monitoring SLA compliance</p>
            </div>
          ) : (
            <div className="space-y-3">
              {policies.map((policy) => {
                const severityBadge = getSeverityBadge(policy.severity)
                const metricLabel = getMetricLabel(policy.metric)
                const isCompliant = dashboard?.policy_compliance?.[policy.id]

                return (
                  <div
                    key={policy.id}
                    className={cn(
                      'flex items-center justify-between p-4 rounded-lg border transition-colors',
                      getComplianceColor(isCompliant),
                    )}
                  >
                    <div className="flex items-center gap-4">
                      {getComplianceIcon(isCompliant)}
                      <div>
                        <p className="font-medium text-slate-900 dark:text-white">{policy.name}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs text-slate-500 dark:text-slate-400">
                            {metricLabel}
                          </span>
                          <span className="text-xs text-slate-400">•</span>
                          <span className="text-xs text-slate-500 dark:text-slate-400">
                            Threshold: {policy.threshold}
                          </span>
                          <span className="text-xs text-slate-400">•</span>
                          <span className="text-xs text-slate-500 dark:text-slate-400">
                            Window: {policy.window_minutes}min
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={cn('px-2 py-1 rounded-md text-xs font-medium', severityBadge.color)}>
                        {severityBadge.label}
                      </span>
                      {!policy.enabled && (
                        <Badge variant="outline" className="text-slate-500">Disabled</Badge>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => startEdit(policy)}
                      >
                        <Edit3 className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeletePolicy(policy.id)}
                      >
                        <Trash2 className="h-4 w-4 text-rose-500" />
                      </Button>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Alerts Section */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-amber-500" />
              SLA Alerts
              {dashboard && dashboard.active_alerts > 0 && (
                <Badge variant="error">{dashboard.active_alerts}</Badge>
              )}
            </CardTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowAlertsOnly(!showAlertsOnly)}
            >
              {showAlertsOnly ? 'Show All' : 'Show Unacknowledged'}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {alerts.length === 0 ? (
            <div className="text-center py-8 text-slate-500 dark:text-slate-400">
              <CheckCircle className="h-12 w-12 mx-auto mb-3 text-emerald-300" />
              <p>No SLA alerts</p>
              <p className="text-sm mt-1">All systems operating within SLA thresholds</p>
            </div>
          ) : (
            <div className="space-y-3">
              {(showAlertsOnly ? alerts.filter(a => !a.acknowledged) : alerts).map((alert) => {
                const severityBadge = getSeverityBadge(alert.severity)
                return (
                  <div
                    key={alert.id}
                    className={cn(
                      'flex items-center justify-between p-4 rounded-lg border',
                      alert.acknowledged
                        ? 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50'
                        : 'border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/20',
                    )}
                  >
                    <div className="flex items-center gap-3">
                      <span className={cn('px-2 py-1 rounded-md text-xs font-medium', severityBadge.color)}>
                        {severityBadge.label}
                      </span>
                      <div>
                        <p className={cn(
                          'text-sm font-medium',
                          alert.acknowledged ? 'text-slate-500 dark:text-slate-400' : 'text-slate-900 dark:text-white'
                        )}>
                          {alert.message || `${getMetricLabel(alert.metric_type)} SLA violation`}
                        </p>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                          Current: {alert.current_value?.toFixed(2)} • Threshold: {alert.threshold?.toFixed(2)} • {new Date(alert.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    {!alert.acknowledged && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleAcknowledgeAlert(alert.id)}
                      >
                        Acknowledge
                      </Button>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}