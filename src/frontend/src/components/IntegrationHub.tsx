'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Plug,
  Plus,
  Edit3,
  Trash2,
  RefreshCw,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  Zap,
  Globe,
  Radio,
  Activity,
  X,
  ExternalLink,
  Play,
  RotateCw,
  ChevronDown,
  ChevronRight,
  Puzzle
} from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { useToast } from '@/hooks/useToast'
import { cn } from '@/lib/utils'
import {
  registerIntegration,
  listIntegrations,
  updateIntegration,
  deleteIntegration,
  testIntegration,
  triggerIntegrationEvent,
  retryFailedEvent,
  getIntegrationLogs,
  getIntegrationStatus,
  type IntegrationConfigData,
  type IntegrationLogData,
  type IntegrationStatusData,
} from '@/lib/api'
import { formatApiError } from '@/lib/api'

const INTEGRATION_TYPES = [
  {
    value: 'webhook',
    label: 'Webhook',
    icon: Globe,
    description: 'Send HTTP requests to external URLs on events',
    color: 'text-blue-600 bg-blue-50 dark:bg-blue-900/20 dark:text-blue-400',
  },
  {
    value: 'api',
    label: 'REST API',
    icon: Zap,
    description: 'Connect to RESTful APIs for data exchange',
    color: 'text-purple-600 bg-purple-50 dark:bg-purple-900/20 dark:text-purple-400',
  },
  {
    value: 'polling',
    label: 'Polling',
    icon: Clock,
    description: 'Periodically fetch data from external sources',
    color: 'text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20 dark:text-emerald-400',
  },
  {
    value: 'streaming',
    label: 'Streaming',
    icon: Radio,
    description: 'Continuous real-time data stream connections',
    color: 'text-amber-600 bg-amber-50 dark:bg-amber-900/20 dark:text-amber-400',
  },
]

const STATUS_COLORS: Record<string, string> = {
  healthy: 'text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20 dark:text-emerald-400',
  degraded: 'text-amber-600 bg-amber-50 dark:bg-amber-900/20 dark:text-amber-400',
  unhealthy: 'text-rose-600 bg-rose-50 dark:bg-rose-900/20 dark:text-rose-400',
  disabled: 'text-slate-500 bg-slate-100 dark:bg-slate-800 dark:text-slate-400',
}

type ActiveView = 'marketplace' | 'configurations' | 'logs'

export default function IntegrationHub() {
  const [integrations, setIntegrations] = useState<IntegrationConfigData[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [activeView, setActiveView] = useState<ActiveView>('configurations')
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [editingIntegration, setEditingIntegration] = useState<string | null>(null)
  const [selectedIntegration, setSelectedIntegration] = useState<string | null>(null)
  const [integrationStatuses, setIntegrationStatuses] = useState<Record<string, IntegrationStatusData>>({})
  const [logs, setLogs] = useState<IntegrationLogData[]>([])
  const [testingId, setTestingId] = useState<string | null>(null)
  const [testResults, setTestResults] = useState<Record<string, { success: boolean; message: string }>>({})

  const [formData, setFormData] = useState({
    name: '',
    type: 'webhook',
    provider: '',
    credentials: '{}',
    settings: '{}',
  })

  const { showToast } = useToast()

  const fetchIntegrations = useCallback(async () => {
    try {
      const data = await listIntegrations()
      setIntegrations(data)

      // Fetch status for each integration
      const statusMap: Record<string, IntegrationStatusData> = {}
      for (const integration of data) {
        try {
          const status = await getIntegrationStatus(integration.id)
          if (status) {
            statusMap[integration.id] = status
          }
        } catch {
          // Skip status fetch errors
        }
      }
      setIntegrationStatuses(statusMap)
    } catch (error: unknown) {
      const message = formatApiError(error, 'Failed to load integrations')
      showToast(message, 'error')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [showToast])

  useEffect(() => {
    fetchIntegrations()
  }, [fetchIntegrations])

  const handleRefresh = async () => {
    setRefreshing(true)
    await fetchIntegrations()
  }

  const handleCreateIntegration = async () => {
    try {
      const credentials = JSON.parse(formData.credentials || '{}')
      const settings = JSON.parse(formData.settings || '{}')
      await registerIntegration({
        name: formData.name,
        type: formData.type,
        provider: formData.provider,
        credentials,
        settings,
      })
      showToast('Integration created successfully', 'success')
      setShowCreateForm(false)
      resetForm()
      await fetchIntegrations()
    } catch (error: unknown) {
      if (error instanceof SyntaxError) {
        showToast('Invalid JSON in credentials or settings', 'error')
      } else {
        const message = formatApiError(error, 'Failed to create integration')
        showToast(message, 'error')
      }
    }
  }

  const handleUpdateIntegration = async (configId: string) => {
    try {
      const updates: Record<string, unknown> = {}
      if (formData.name) updates.name = formData.name
      if (formData.type) updates.type = formData.type
      if (formData.provider) updates.provider = formData.provider
      try {
        updates.credentials = JSON.parse(formData.credentials || '{}')
        updates.settings = JSON.parse(formData.settings || '{}')
      } catch {
        showToast('Invalid JSON in credentials or settings', 'error')
        return
      }

      await updateIntegration(configId, updates)
      showToast('Integration updated successfully', 'success')
      setEditingIntegration(null)
      resetForm()
      await fetchIntegrations()
    } catch (error: unknown) {
      const message = formatApiError(error, 'Failed to update integration')
      showToast(message, 'error')
    }
  }

  const handleDeleteIntegration = async (configId: string) => {
    try {
      await deleteIntegration(configId)
      showToast('Integration deleted', 'success')
      if (selectedIntegration === configId) {
        setSelectedIntegration(null)
      }
      await fetchIntegrations()
    } catch (error: unknown) {
      const message = formatApiError(error, 'Failed to delete integration')
      showToast(message, 'error')
    }
  }

  const handleTestIntegration = async (configId: string) => {
    setTestingId(configId)
    try {
      const result = await testIntegration(configId)
      setTestResults(prev => ({
        ...prev,
        [configId]: { success: result.success, message: result.message },
      }))
      showToast(result.success ? 'Connection test successful' : `Test failed: ${result.message}`, result.success ? 'success' : 'error')
    } catch (error: unknown) {
      const message = formatApiError(error, 'Connection test failed')
      setTestResults(prev => ({
        ...prev,
        [configId]: { success: false, message },
      }))
      showToast(message, 'error')
    } finally {
      setTestingId(null)
    }
  }

  const handleTriggerEvent = async (configId: string) => {
    try {
      await triggerIntegrationEvent(configId, {
        event_type: 'manual_trigger',
        payload: { triggered_at: new Date().toISOString(), source: 'manual' },
      })
      showToast('Event triggered successfully', 'success')
    } catch (error: unknown) {
      const message = formatApiError(error, 'Failed to trigger event')
      showToast(message, 'error')
    }
  }

  const handleViewLogs = async (configId: string) => {
    try {
      const result = await getIntegrationLogs(configId)
      setLogs(result.logs || [])
      setSelectedIntegration(configId)
      setActiveView('logs')
    } catch (error: unknown) {
      const message = formatApiError(error, 'Failed to load logs')
      showToast(message, 'error')
    }
  }

  const handleRetryEvent = async (eventId: string) => {
    try {
      await retryFailedEvent(eventId)
      showToast('Event retry initiated', 'success')
    } catch (error: unknown) {
      const message = formatApiError(error, 'Failed to retry event')
      showToast(message, 'error')
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      type: 'webhook',
      provider: '',
      credentials: '{}',
      settings: '{}',
    })
  }

  const startEdit = (integration: IntegrationConfigData) => {
    setEditingIntegration(integration.id)
    setFormData({
      name: integration.name,
      type: integration.type,
      provider: integration.provider,
      credentials: JSON.stringify(integration.credentials || {}, null, 2),
      settings: JSON.stringify(integration.settings || {}, null, 2),
    })
    setShowCreateForm(false)
  }

  const getTypeConfig = (type: string) => {
    return INTEGRATION_TYPES.find(t => t.value === type) || INTEGRATION_TYPES[0]
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
        title="Integration Hub"
        description="Manage custom integrations and monitor their health"
        icon={<Puzzle className="w-5 h-5 text-blue-600" />}
        actions={
          <div className="flex items-center gap-3">
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
              onClick={() => { setShowCreateForm(true); setEditingIntegration(null); resetForm() }}
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Integration
            </Button>
          </div>
        }
      />

      {/* Tab Navigation */}
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit">
        {([
          { key: 'configurations' as ActiveView, label: 'Configurations', count: integrations.length },
          { key: 'marketplace' as ActiveView, label: 'Marketplace' },
          { key: 'logs' as ActiveView, label: 'Event Logs' },
        ]).map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveView(tab.key)}
            className={cn(
              'px-4 py-2 text-sm font-medium rounded-md transition-all flex items-center gap-2',
              activeView === tab.key
                ? 'bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            )}
          >
            {tab.label}
            {tab.count !== undefined && (
              <Badge variant="secondary" className="text-xs">{tab.count}</Badge>
            )}
          </button>
        ))}
      </div>

      {/* Create/Edit Form */}
      <AnimatePresence>
        {(showCreateForm || editingIntegration) && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>{editingIntegration ? 'Edit Integration' : 'Create Integration'}</span>
                  <button
                    onClick={() => { setShowCreateForm(false); setEditingIntegration(null); resetForm() }}
                    className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                    Integration Name
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white"
                    placeholder="e.g., Slack Notifications"
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                      Type
                    </label>
                    <select
                      value={formData.type}
                      onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value }))}
                      className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white"
                    >
                      {INTEGRATION_TYPES.map(type => (
                        <option key={type.value} value={type.value}>{type.label}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                      Provider
                    </label>
                    <input
                      type="text"
                      value={formData.provider}
                      onChange={(e) => setFormData(prev => ({ ...prev, provider: e.target.value }))}
                      className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white"
                      placeholder="e.g., Slack, Stripe, GitHub"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                    Credentials (JSON)
                  </label>
                  <textarea
                    value={formData.credentials}
                    onChange={(e) => setFormData(prev => ({ ...prev, credentials: e.target.value }))}
                    className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white font-mono text-sm"
                    rows={3}
                    placeholder='{"api_key": "...", "secret": "..."}'
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                    Settings (JSON)
                  </label>
                  <textarea
                    value={formData.settings}
                    onChange={(e) => setFormData(prev => ({ ...prev, settings: e.target.value }))}
                    className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white font-mono text-sm"
                    rows={3}
                    placeholder='{"url": "https://...", "timeout": 30}'
                  />
                </div>

                <div className="flex justify-end gap-3">
                  <Button
                    variant="outline"
                    onClick={() => { setShowCreateForm(false); setEditingIntegration(null); resetForm() }}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={() => editingIntegration ? handleUpdateIntegration(editingIntegration) : handleCreateIntegration()}
                    disabled={!formData.name || !formData.provider}
                  >
                    {editingIntegration ? 'Update Integration' : 'Create Integration'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Marketplace View */}
      {activeView === 'marketplace' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {INTEGRATION_TYPES.map((type) => {
            const Icon = type.icon
            return (
              <Card key={type.value} className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => {
                setFormData(prev => ({ ...prev, type: type.value }))
                setShowCreateForm(true)
                setEditingIntegration(null)
              }}>
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className={cn('p-3 rounded-lg', type.color)}>
                      <Icon className="h-6 w-6" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-slate-900 dark:text-white">{type.label}</h3>
                      <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">{type.description}</p>
                      <div className="mt-3">
                        <Badge variant="outline" className="text-xs">
                          <Plus className="h-3 w-3 mr-1" />
                          Add Integration
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {/* Configurations View */}
      {activeView === 'configurations' && (
        <div className="space-y-4">
          {integrations.length === 0 ? (
            <Card>
              <CardContent className="py-12">
                <div className="text-center text-slate-500 dark:text-slate-400">
                  <Plug className="h-12 w-12 mx-auto mb-3 opacity-30" />
                  <p>No integrations configured yet</p>
                  <p className="text-sm mt-1">Add an integration to connect external services</p>
                  <Button
                    variant="outline"
                    size="sm"
                    className="mt-4"
                    onClick={() => { setShowCreateForm(true); setEditingIntegration(null); resetForm() }}
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Integration
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            integrations.map((integration) => {
              const typeConfig = getTypeConfig(integration.type)
              const TypeIcon = typeConfig.icon
              const status = integrationStatuses[integration.id]
              const statusColor = STATUS_COLORS[status?.health_status || 'disabled']
              const testResult = testResults[integration.id]

              return (
                <Card key={integration.id}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className={cn('p-2 rounded-lg', typeConfig.color)}>
                          <TypeIcon className="h-5 w-5" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <p className="font-medium text-slate-900 dark:text-white">{integration.name}</p>
                            {status && (
                              <Badge variant="outline" className={cn('text-xs', statusColor)}>
                                {status.health_status}
                              </Badge>
                            )}
                            {!integration.enabled && (
                              <Badge variant="outline" className="text-xs text-slate-500">Disabled</Badge>
                            )}
                          </div>
                          <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
                            {typeConfig.label} • {integration.provider}
                          </p>
                          {status && (
                            <div className="flex items-center gap-3 mt-1 text-xs text-slate-500 dark:text-slate-400">
                              <span>{status.total_events_24h} events (24h)</span>
                              <span>•</span>
                              <span className="text-emerald-600">{status.completed_events_24h} completed</span>
                              {status.failed_events_24h > 0 && (
                                <>
                                  <span>•</span>
                                  <span className="text-rose-600">{status.failed_events_24h} failed</span>
                                </>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {testResult && (
                          <Badge variant={testResult.success ? 'default' : 'error'} className="text-xs">
                            {testResult.success ? '✓ Connected' : '✗ Failed'}
                          </Badge>
                        )}
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleTestIntegration(integration.id)}
                          disabled={testingId === integration.id}
                        >
                          {testingId === integration.id ? (
                            <RefreshCw className="h-4 w-4 mr-1 animate-spin" />
                          ) : (
                            <Zap className="h-4 w-4 mr-1" />
                          )}
                          Test
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleTriggerEvent(integration.id)}
                        >
                          <Play className="h-4 w-4 mr-1" />
                          Trigger
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleViewLogs(integration.id)}
                        >
                          <Activity className="h-4 w-4 mr-1" />
                          Logs
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => startEdit(integration)}
                        >
                          <Edit3 className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteIntegration(integration.id)}
                        >
                          <Trash2 className="h-4 w-4 text-rose-500" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })
          )}
        </div>
      )}

      {/* Logs View */}
      {activeView === 'logs' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-blue-500" />
              Integration Logs
              {selectedIntegration && (
                <Badge variant="secondary" className="text-xs">
                  {integrations.find(i => i.id === selectedIntegration)?.name || selectedIntegration}
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {logs.length === 0 ? (
              <div className="text-center py-8 text-slate-500 dark:text-slate-400">
                <Activity className="h-12 w-12 mx-auto mb-3 opacity-30" />
                <p>No logs available</p>
                <p className="text-sm mt-1">Trigger an event or test a connection to generate logs</p>
              </div>
            ) : (
              <div className="space-y-2">
                {logs.map((log) => (
                  <div
                    key={log.id}
                    className={cn(
                      'flex items-start gap-3 p-3 rounded-lg border',
                      log.level === 'error' ? 'border-rose-200 dark:border-rose-800 bg-rose-50 dark:bg-rose-900/10' :
                      log.level === 'warning' ? 'border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/10' :
                      'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50'
                    )}
                  >
                    <Badge variant="outline" className={cn(
                      'text-xs shrink-0',
                      log.level === 'error' ? 'text-rose-600 border-rose-300' :
                      log.level === 'warning' ? 'text-amber-600 border-amber-300' :
                      log.level === 'info' ? 'text-blue-600 border-blue-300' :
                      'text-slate-600 border-slate-300'
                    )}>
                      {log.level.toUpperCase()}
                    </Badge>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-slate-900 dark:text-white">{log.message}</p>
                      <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                        {new Date(log.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}