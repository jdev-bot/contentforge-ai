'use client'

import { useState, useCallback, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Zap,
  Webhook,
  Globe,
  Key,
  RefreshCw,
  Copy,
  Eye,
  EyeOff,
  Settings,
  Plus,
  Trash2,
  AlertCircle,
  Shield,
  Clock,
  Puzzle
} from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Card, CardContent } from '@/components/ui/Card'
import { Tooltip } from '@/components/ui/Tooltip'
import { Input } from '@/components/ui/Input'
import { cn } from '@/lib/utils'
import {
  listUserIntegrations,
  createIntegration,
  updateIntegrationById,
  deleteIntegrationById,
  testIntegrationConnection,
  type IntegrationItem,
} from '@/lib/api'

// Types
export interface Integration {
  id: string
  name: string
  description: string
  icon: string
  status: 'connected' | 'disconnected' | 'pending' | 'error'
  lastSync?: Date
  category: 'automation' | 'cms' | 'webhook' | 'api'
  config?: Record<string, unknown>
}

export interface WebhookConfig {
  id: string
  name: string
  url: string
  events: string[]
  secret: string
  isActive: boolean
  createdAt: Date
  lastTriggered?: Date
}

export interface APIKey {
  id: string
  name: string
  key: string
  prefix: string
  createdAt: Date
  lastUsed?: Date
  expiresAt?: Date
  scopes: string[]
}

// Helper functions
const formatDate = (date?: Date | string | null) => {
  if (!date) return 'Never'
  const d = date instanceof Date ? date : new Date(date)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  const hours = Math.floor(diff / 3600000)
  if (hours < 1) return 'Just now'
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}d ago`
  return d.toLocaleDateString()
}

const mapIntegrationStatus = (item: IntegrationItem): Integration['status'] => {
  if (item.is_active) return 'connected'
  return 'disconnected'
}

const getIntegrationIcon = (type: string): string => {
  const icons: Record<string, string> = {
    zapier: '⚡',
    wordpress: '📰',
    webhook: '🪝',
    slack: '💬',
    make: '🔗',
    linkedin: '💼',
    twitter: '🐦',
  }
  return icons[type] || '🔗'
}

const getIntegrationCategory = (type: string): Integration['category'] => {
  if (type === 'webhook') return 'webhook'
  if (type === 'zapier' || type === 'make') return 'automation'
  if (type === 'wordpress') return 'cms'
  return 'api'
}

export default function IntegrationsPanel() {
  const [integrations, setIntegrations] = useState<Integration[]>([])
  const [isLoadingIntegrations, setIsLoadingIntegrations] = useState(true)
  const [integrationsError, setIntegrationsError] = useState<string | null>(null)
  const [webhooks, setWebhooks] = useState<WebhookConfig[]>([])
  const [isLoadingWebhooks, setIsLoadingWebhooks] = useState(true)
  const [apiKeys, setApiKeys] = useState<APIKey[]>([])
  const [isLoadingApiKeys, setIsLoadingApiKeys] = useState(false)
  const [activeTab, setActiveTab] = useState<'integrations' | 'webhooks' | 'apikeys'>('integrations')
  const [showAddWebhook, setShowAddWebhook] = useState(false)
  const [showAddKey, setShowAddKey] = useState(false)
  const [showKeySecret, setShowKeySecret] = useState<Record<string, boolean>>({})
  const [testingId, setTestingId] = useState<string | null>(null)

  // Fetch integrations from API
  const fetchIntegrations = useCallback(async () => {
    try {
      setIsLoadingIntegrations(true)
      setIntegrationsError(null)
      const data = await listUserIntegrations()
      const mapped: Integration[] = data.integrations.map((item) => ({
        id: item.id,
        name: item.name,
        description: item.integration_type,
        icon: getIntegrationIcon(item.integration_type),
        status: mapIntegrationStatus(item),
        lastSync: item.last_used_at ? new Date(item.last_used_at) : undefined,
        category: getIntegrationCategory(item.integration_type),
        config: item.config,
      }))
      setIntegrations(mapped)
    } catch (err) {
      setIntegrationsError(err instanceof Error ? err.message : 'Failed to load integrations')
    } finally {
      setIsLoadingIntegrations(false)
    }
  }, [])

  // Fetch webhook-type integrations from API
  const fetchWebhooks = useCallback(async () => {
    try {
      setIsLoadingWebhooks(true)
      const data = await listUserIntegrations('webhook')
      const mapped: WebhookConfig[] = data.integrations
        .filter((item) => item.integration_type === 'webhook')
        .map((item) => ({
          id: item.id,
          name: item.name,
          url: (item.config?.url as string) || '',
          events: (item.config?.events as string[]) || [],
          secret: (item.config?.secret as string) || '••••••••',
          isActive: item.is_active,
          createdAt: new Date(item.created_at),
          lastTriggered: item.last_used_at ? new Date(item.last_used_at) : undefined,
        }))
      setWebhooks(mapped)
    } catch {
      // Webhooks may be empty — that's fine
    } finally {
      setIsLoadingWebhooks(false)
    }
  }, [])

  useEffect(() => {
    fetchIntegrations()
    fetchWebhooks()
    setIsLoadingApiKeys(false)
  }, [fetchIntegrations, fetchWebhooks])

  const handleToggleIntegration = useCallback(async (id: string) => {
    const integration = integrations.find((i) => i.id === id)
    if (!integration) return

    const newActive = integration.status !== 'connected'
    // Optimistic update
    setIntegrations((prev) =>
      prev.map((int) => {
        if (int.id === id) {
          return {
            ...int,
            status: newActive ? 'connected' as const : 'disconnected' as const,
            lastSync: newActive ? new Date() : int.lastSync,
          }
        }
        return int
      })
    )

    try {
      await updateIntegrationById(id, { is_active: newActive })
    } catch {
      // Revert on failure
      setIntegrations((prev) =>
        prev.map((int) => {
          if (int.id === id) {
            return {
              ...int,
              status: !newActive ? 'connected' as const : 'disconnected' as const,
              lastSync: !newActive ? new Date() : int.lastSync,
            }
          }
          return int
        })
      )
    }
  }, [integrations])

  const handleTestIntegration = useCallback(async (id: string) => {
    setTestingId(id)
    try {
      await testIntegrationConnection(id)
      // Refresh to get updated last_used_at
      fetchIntegrations()
    } catch {
      // Test failed
    } finally {
      setTestingId(null)
    }
  }, [fetchIntegrations])

  const handleCopy = async (text: string) => {
    await navigator.clipboard.writeText(text)
  }

  const handleDeleteWebhook = useCallback(async (id: string) => {
    try {
      await deleteIntegrationById(id)
      setWebhooks((prev) => prev.filter((w) => w.id !== id))
    } catch {
      // Delete failed
    }
  }, [])

  const handleDeleteKey = (id: string) => {
    setApiKeys((prev) => prev.filter((k) => k.id !== id))
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'bg-emerald-500'
      case 'disconnected': return 'bg-slate-400'
      case 'pending': return 'bg-amber-500'
      case 'error': return 'bg-rose-500'
      default: return 'bg-slate-400'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'connected': return 'Connected'
      case 'disconnected': return 'Disconnected'
      case 'pending': return 'Pending'
      case 'error': return 'Error'
      default: return status
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <PageHeader
        title="Integrations"
        description="Connect ContentForge with your favorite tools and services"
        icon={<Puzzle className="w-5 h-5 text-blue-600" />}
      />

      {/* Tabs */}
      <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 rounded-xl p-1 w-fit">
        {[
          { id: 'integrations', label: 'Integrations', icon: Zap },
          { id: 'webhooks', label: 'Webhooks', icon: Webhook },
          { id: 'apikeys', label: 'API Keys', icon: Key },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as typeof activeTab)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-all',
              activeTab === tab.id
                ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
            )}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Integrations Tab */}
      {activeTab === 'integrations' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {isLoadingIntegrations && (
            <div className="col-span-full flex items-center justify-center py-12">
              <RefreshCw className="h-6 w-6 text-slate-400 animate-spin" />
              <span className="ml-3 text-slate-500">Loading integrations...</span>
            </div>
          )}

          {integrationsError && !isLoadingIntegrations && (
            <div className="col-span-full">
              <Card className="bg-rose-50 dark:bg-rose-900/20 border-rose-200 dark:border-rose-800">
                <CardContent className="p-4 flex items-center gap-3">
                  <AlertCircle className="h-5 w-5 text-rose-600 dark:text-rose-400 flex-shrink-0" />
                  <div>
                    <p className="text-sm text-rose-800 dark:text-rose-300 font-medium">Failed to load integrations</p>
                    <p className="text-sm text-rose-700 dark:text-rose-400 mt-1">{integrationsError}</p>
                  </div>
                  <Button variant="outline" size="sm" onClick={fetchIntegrations} className="ml-auto">Retry</Button>
                </CardContent>
              </Card>
            </div>
          )}

          {!isLoadingIntegrations && !integrationsError && integrations.map((integration) => (
            <Card key={integration.id} className="relative">
              <CardContent className="p-5">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-2xl">
                      {integration.icon}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-slate-900 dark:text-slate-100">
                          {integration.name}
                        </h3>
                        <span className={cn(
                          'w-2 h-2 rounded-full',
                          getStatusColor(integration.status)
                        )} />
                      </div>
                      <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
                        {integration.description}
                      </p>
                      {integration.lastSync && (
                        <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
                          Last synced: {formatDate(integration.lastSync)}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Tooltip content="Test connection" position="top">
                      <button
                        className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                        onClick={() => handleTestIntegration(integration.id)}
                        disabled={testingId === integration.id}
                      >
                        <RefreshCw className={cn('h-4 w-4 text-slate-500', testingId === integration.id && 'animate-spin')} />
                      </button>
                    </Tooltip>
                    <Tooltip content="Settings" position="top">
                      <button className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors">
                        <Settings className="h-4 w-4 text-slate-500" />
                      </button>
                    </Tooltip>
                  </div>
                </div>

                {integration.config && (
                  <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-700">
                    <div className="flex items-center gap-4 text-sm">
                      {(integration.config.account as string) && (
                        <div className="flex items-center gap-1.5">
                          <Shield className="h-4 w-4 text-blue-500" />
                          <span className="text-slate-600 dark:text-slate-400">
                            {String(integration.config.account)} plan
                          </span>
                        </div>
                      )}
                      {integration.config.zaps !== undefined && (
                        <div className="flex items-center gap-1.5">
                          <Zap className="h-4 w-4 text-amber-500" />
                          <span className="text-slate-600 dark:text-slate-400">
                            {String(integration.config.zaps)} active Zaps
                          </span>
                        </div>
                      )}
                      {(integration.config.site as string) && (
                        <div className="flex items-center gap-1.5">
                          <Globe className="h-4 w-4 text-emerald-500" />
                          <span className="text-slate-600 dark:text-slate-400 truncate max-w-[200px]">
                            {String(integration.config.site)}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                <div className="mt-4 flex items-center justify-between">
                  <Badge
                    variant={integration.status === 'connected' ? 'success' : 'default'}
                    size="sm"
                  >
                    {getStatusText(integration.status)}
                  </Badge>

                  <Button
                    variant={integration.status === 'connected' ? 'outline' : 'primary'}
                    size="sm"
                    onClick={() => handleToggleIntegration(integration.id)}
                  >
                    {integration.status === 'connected' ? 'Disconnect' : 'Connect'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}

          {!isLoadingIntegrations && !integrationsError && integrations.length === 0 && (
            <Card className="col-span-full border-dashed border-2">
              <CardContent className="p-8 text-center">
                <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Puzzle className="h-8 w-8 text-slate-400" />
                </div>
                <h3 className="font-medium text-slate-900 dark:text-slate-100">No integrations yet</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  Connect your favorite tools to get started
                </p>
              </CardContent>
            </Card>
          )}

          {/* Add Custom Integration */}
          <Card className="border-dashed border-2 border-slate-300 dark:border-slate-600 hover:border-blue-400 dark:hover:border-blue-500 transition-colors cursor-pointer">
            <CardContent className="p-5 flex flex-col items-center justify-center text-center h-full min-h-[200px]">
              <div className="w-12 h-12 rounded-xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-3">
                <Plus className="h-6 w-6 text-slate-400" />
              </div>
              <h3 className="font-medium text-slate-900 dark:text-slate-100">
                Custom Integration
              </h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                Request a new integration
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Webhooks Tab */}
      {activeTab === 'webhooks' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                Webhook Endpoints
              </h3>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Configure webhooks to receive real-time event notifications
              </p>
            </div>
            <Button
              variant="primary"
              size="sm"
              leftIcon={<Plus className="h-4 w-4" />}
              onClick={() => setShowAddWebhook(true)}
            >
              Add Webhook
            </Button>
          </div>

          {isLoadingWebhooks && (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="h-6 w-6 text-slate-400 animate-spin" />
              <span className="ml-3 text-slate-500">Loading webhooks...</span>
            </div>
          )}

          {!isLoadingWebhooks && (
            <div className="space-y-3">
              {webhooks.map((webhook) => (
                <Card key={webhook.id}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h4 className="font-medium text-slate-900 dark:text-slate-100">
                            {webhook.name}
                          </h4>
                          <Badge
                            variant={webhook.isActive ? 'success' : 'default'}
                            size="sm"
                          >
                            {webhook.isActive ? 'Active' : 'Paused'}
                          </Badge>
                        </div>

                        <div className="flex items-center gap-2 mt-2">
                          <code className="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded text-slate-600 dark:text-slate-400">
                            {webhook.url}
                          </code>
                          <Tooltip content="Copy URL" position="top">
                            <button
                              onClick={() => handleCopy(webhook.url)}
                              className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded"
                            >
                              <Copy className="h-3 w-3 text-slate-400" />
                            </button>
                          </Tooltip>
                        </div>

                        <div className="flex items-center gap-4 mt-3 text-xs text-slate-500 dark:text-slate-400">
                          <div className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            Created {formatDate(webhook.createdAt)}
                          </div>
                          <div className="flex items-center gap-1">
                            <RefreshCw className="h-3 w-3" />
                            Last triggered {formatDate(webhook.lastTriggered)}
                          </div>
                        </div>

                        <div className="flex flex-wrap gap-1 mt-3">
                          {webhook.events.map(event => (
                            <Badge key={event} variant="outline" size="sm">
                              {event}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <Tooltip content="Test webhook" position="top">
                          <button
                            className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                            onClick={() => handleTestIntegration(webhook.id)}
                            disabled={testingId === webhook.id}
                          >
                            <RefreshCw className={cn('h-4 w-4 text-slate-500', testingId === webhook.id && 'animate-spin')} />
                          </button>
                        </Tooltip>
                        <Tooltip content="Delete" position="top">
                          <button
                            onClick={() => handleDeleteWebhook(webhook.id)}
                            className="p-2 hover:bg-rose-100 dark:hover:bg-rose-900/30 rounded-lg transition-colors"
                          >
                            <Trash2 className="h-4 w-4 text-rose-500" />
                          </button>
                        </Tooltip>
                      </div>
                    </div>

                    <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-700">
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-slate-500 dark:text-slate-400">Secret:</span>
                        <code className="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded text-slate-600 dark:text-slate-400 font-mono">
                          {webhook.secret}
                        </code>
                        <Tooltip content="Copy secret" position="top">
                          <button
                            onClick={() => handleCopy(webhook.secret)}
                            className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded"
                          >
                            <Copy className="h-3 w-3 text-slate-400" />
                          </button>
                        </Tooltip>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {!isLoadingWebhooks && webhooks.length === 0 && (
            <Card className="border-dashed border-2">
              <CardContent className="p-8 text-center">
                <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Webhook className="h-8 w-8 text-slate-400" />
                </div>
                <h3 className="font-medium text-slate-900 dark:text-slate-100">
                  No webhooks configured
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 mb-4">
                  Add a webhook to receive real-time event notifications
                </p>
                <Button
                  variant="outline"
                  leftIcon={<Plus className="h-4 w-4" />}
                  onClick={() => setShowAddWebhook(true)}
                >
                  Add Webhook
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* API Keys Tab */}
      {activeTab === 'apikeys' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                API Keys
              </h3>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Manage API keys for accessing the ContentForge API
              </p>
            </div>
            <Button
              variant="primary"
              size="sm"
              leftIcon={<Plus className="h-4 w-4" />}
              onClick={() => setShowAddKey(true)}
            >
              Generate Key
            </Button>
          </div>

          <Card className="bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800">
            <CardContent className="p-4 flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm text-amber-800 dark:text-amber-300 font-medium">
                  Security Notice
                </p>
                <p className="text-sm text-amber-700 dark:text-amber-400 mt-1">
                  Keep your API keys secure. Never share them or commit them to version control.
                  Keys with write access should be treated with extra caution.
                </p>
              </div>
            </CardContent>
          </Card>

          <div className="space-y-3">
            {apiKeys.map((apiKey) => (
              <Card key={apiKey.id}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className="font-medium text-slate-900 dark:text-slate-100">
                          {apiKey.name}
                        </h4>
                        {apiKey.prefix.includes('live') && (
                          <Badge variant="error" size="sm">Production</Badge>
                        )}
                        {apiKey.prefix.includes('test') && (
                          <Badge variant="warning" size="sm">Test</Badge>
                        )}
                      </div>

                      <div className="flex items-center gap-2 mt-2">
                        <code className="text-sm bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded font-mono text-slate-600 dark:text-slate-400">
                          {showKeySecret[apiKey.id] ? apiKey.key : apiKey.key.replace(/\*/g, '•')}
                        </code>
                        <button
                          onClick={() => setShowKeySecret(prev => ({
                            ...prev,
                            [apiKey.id]: !prev[apiKey.id]
                          }))}
                          className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded"
                        >
                          {showKeySecret[apiKey.id] ? (
                            <EyeOff className="h-4 w-4 text-slate-500" />
                          ) : (
                            <Eye className="h-4 w-4 text-slate-500" />
                          )}
                        </button>
                        <button
                          onClick={() => handleCopy(apiKey.key)}
                          className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded"
                        >
                          <Copy className="h-4 w-4 text-slate-500" />
                        </button>
                      </div>

                      <div className="flex items-center gap-4 mt-3 text-xs text-slate-500 dark:text-slate-400">
                        <span>Created {formatDate(apiKey.createdAt)}</span>
                        {apiKey.lastUsed && (
                          <span>Last used {formatDate(apiKey.lastUsed)}</span>
                        )}
                        {apiKey.expiresAt && (
                          <span>Expires {formatDate(apiKey.expiresAt)}</span>
                        )}
                      </div>

                      <div className="flex flex-wrap gap-1 mt-3">
                        {apiKey.scopes.map(scope => (
                          <Badge key={scope} variant="outline" size="sm">
                            {scope}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <Tooltip content="Delete key" position="top">
                      <button
                        onClick={() => handleDeleteKey(apiKey.id)}
                        className="p-2 hover:bg-rose-100 dark:hover:bg-rose-900/30 rounded-lg transition-colors"
                      >
                        <Trash2 className="h-4 w-4 text-rose-500" />
                      </button>
                    </Tooltip>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {apiKeys.length === 0 && !isLoadingApiKeys && (
            <Card className="border-dashed border-2">
              <CardContent className="p-8 text-center">
                <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Key className="h-8 w-8 text-slate-400" />
                </div>
                <h3 className="font-medium text-slate-900 dark:text-slate-100">
                  No API keys
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 mb-4">
                  Generate an API key to access the ContentForge API
                </p>
                <Button
                  variant="outline"
                  leftIcon={<Plus className="h-4 w-4" />}
                  onClick={() => setShowAddKey(true)}
                >
                  Generate Key
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Add Webhook Modal */}
      <AnimatePresence>
        {showAddWebhook && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
              onClick={() => setShowAddWebhook(false)}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="fixed inset-0 m-auto w-full max-w-md h-fit bg-white dark:bg-slate-900 rounded-2xl shadow-2xl z-50 overflow-hidden"
            >
              <div className="p-6 border-b border-slate-200 dark:border-slate-700">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                  Add Webhook
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  Configure a new webhook endpoint
                </p>
              </div>
              <div className="p-6 space-y-4">
                <Input
                  label="Webhook Name"
                  placeholder="e.g., Content Published"
                />
                <Input
                  label="Endpoint URL"
                  placeholder="https://api.example.com/webhooks"
                />
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Events to subscribe
                  </label>
                  <div className="space-y-2">
                    {['content.published', 'content.updated', 'content.deleted', 'analytics.daily'].map(event => (
                      <label key={event} className="flex items-center gap-2">
                        <input type="checkbox" className="rounded border-slate-300" />
                        <span className="text-sm text-slate-600 dark:text-slate-400">{event}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
              <div className="p-6 border-t border-slate-200 dark:border-slate-700 flex gap-3">
                <Button variant="primary" className="flex-1">
                  Create Webhook
                </Button>
                <Button variant="outline" onClick={() => setShowAddWebhook(false)}>
                  Cancel
                </Button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Add API Key Modal */}
      <AnimatePresence>
        {showAddKey && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
              onClick={() => setShowAddKey(false)}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="fixed inset-0 m-auto w-full max-w-md h-fit bg-white dark:bg-slate-900 rounded-2xl shadow-2xl z-50 overflow-hidden"
            >
              <div className="p-6 border-b border-slate-200 dark:border-slate-700">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                  Generate API Key
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  Create a new API key for accessing ContentForge
                </p>
              </div>
              <div className="p-6 space-y-4">
                <Input
                  label="Key Name"
                  placeholder="e.g., Production API"
                />
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Permissions
                  </label>
                  <div className="space-y-2">
                    {['content:read', 'content:write', 'analytics:read', 'webhooks:manage'].map(scope => (
                      <label key={scope} className="flex items-center gap-2">
                        <input type="checkbox" className="rounded border-slate-300" />
                        <span className="text-sm text-slate-600 dark:text-slate-400">{scope}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
              <div className="p-6 border-t border-slate-200 dark:border-slate-700 flex gap-3">
                <Button variant="primary" className="flex-1">
                  Generate Key
                </Button>
                <Button variant="outline" onClick={() => setShowAddKey(false)}>
                  Cancel
                </Button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}