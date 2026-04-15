'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  listPlugins,
  listInstalledPlugins,
  installPlugin,
  uninstallPlugin,
  getPluginConfig,
  updatePluginConfig,
  togglePlugin as togglePluginApi,
  type PluginRegistryItem,
  type InstalledPlugin,
  type PluginListResponse,
  type InstalledPluginListResponse,
} from '../lib/api'
import { formatApiError } from '../lib/api'

// ============================================================================
// Types
// ============================================================================

type PluginTab = 'marketplace' | 'installed'

interface ConfigField {
  key: string
  label: string
  type: 'text' | 'number' | 'boolean' | 'select'
  description?: string
  default?: unknown
  options?: string[]
}

// ============================================================================
// Component
// ============================================================================

export default function PluginManager({ organizationId }: { organizationId: string }) {
  const [activeTab, setActiveTab] = useState<PluginTab>('marketplace')
  const [plugins, setPlugins] = useState<PluginRegistryItem[]>([])
  const [installedPlugins, setInstalledPlugins] = useState<InstalledPlugin[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<string>('')
  const [configuringPlugin, setConfiguringPlugin] = useState<InstalledPlugin | null>(null)
  const [pluginConfig, setPluginConfig] = useState<Record<string, unknown>>({})
  const [configSaving, setConfigSaving] = useState(false)

  // ---- Data fetching ----

  const fetchPlugins = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result: PluginListResponse = await listPlugins({
        category: categoryFilter || undefined,
        search: searchQuery || undefined,
      })
      setPlugins(result.plugins)
    } catch (err: unknown) {
      setError(formatApiError(err, 'Failed to fetch plugins'))
    } finally {
      setLoading(false)
    }
  }, [categoryFilter, searchQuery])

  const fetchInstalled = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result: InstalledPluginListResponse = await listInstalledPlugins(organizationId)
      setInstalledPlugins(result.plugins)
    } catch (err: unknown) {
      setError(formatApiError(err, 'Failed to fetch installed plugins'))
    } finally {
      setLoading(false)
    }
  }, [organizationId])

  useEffect(() => {
    if (activeTab === 'marketplace') {
      fetchPlugins()
    } else {
      fetchInstalled()
    }
  }, [activeTab, fetchPlugins, fetchInstalled])

  // ---- Actions ----

  const handleInstall = async (pluginId: string) => {
    setLoading(true)
    setError(null)
    try {
      await installPlugin(pluginId, organizationId)
      await fetchInstalled()
      await fetchPlugins()
    } catch (err: unknown) {
      setError(formatApiError(err, 'Failed to install plugin'))
    } finally {
      setLoading(false)
    }
  }

  const handleUninstall = async (installId: string) => {
    if (!confirm('Are you sure you want to uninstall this plugin?')) return
    setLoading(true)
    setError(null)
    try {
      await uninstallPlugin(installId, organizationId)
      await fetchInstalled()
    } catch (err: unknown) {
      setError(formatApiError(err, 'Failed to uninstall plugin'))
    } finally {
      setLoading(false)
    }
  }

  const handleToggle = async (installId: string, isEnabled: boolean) => {
    setError(null)
    try {
      await togglePluginApi(installId, organizationId, !isEnabled)
      await fetchInstalled()
    } catch (err: unknown) {
      setError(formatApiError(err, 'Failed to toggle plugin'))
    }
  }

  const handleOpenConfig = async (plugin: InstalledPlugin) => {
    setConfiguringPlugin(plugin)
    try {
      const result = await getPluginConfig(plugin.id, organizationId)
      setPluginConfig(result.config)
    } catch {
      setPluginConfig(plugin.config || {})
    }
  }

  const handleSaveConfig = async () => {
    if (!configuringPlugin) return
    setConfigSaving(true)
    try {
      await updatePluginConfig(configuringPlugin.id, organizationId, pluginConfig)
      setConfiguringPlugin(null)
      await fetchInstalled()
    } catch (err: unknown) {
      setError(formatApiError(err, 'Failed to save config'))
    } finally {
      setConfigSaving(false)
    }
  }

  // ---- Helpers ----

  const isInstalled = (pluginId: string) =>
    installedPlugins.some((ip) => ip.plugin_id === pluginId)

  // ---- Render ----

  return (
    <div className="plugin-manager">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Plugin Manager</h2>
        <div className="flex gap-2">
          <button
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'marketplace'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
            onClick={() => setActiveTab('marketplace')}
          >
            Marketplace
          </button>
          <button
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'installed'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
            onClick={() => setActiveTab('installed')}
          >
            Installed ({installedPlugins.length})
          </button>
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
          <button onClick={() => setError(null)} className="ml-2 underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Marketplace Tab */}
      {activeTab === 'marketplace' && (
        <div>
          {/* Search & filter */}
          <div className="flex gap-3 mb-4">
            <input
              type="text"
              placeholder="Search plugins..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white"
            >
              <option value="">All Categories</option>
              <option value="utility">Utility</option>
              <option value="analytics">Analytics</option>
              <option value="distribution">Distribution</option>
              <option value="editor">Editor</option>
              <option value="integration">Integration</option>
            </select>
          </div>

          {/* Plugin grid */}
          {loading ? (
            <div className="text-center py-12 text-gray-500">Loading plugins...</div>
          ) : plugins.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              No plugins found. Try adjusting your search.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {plugins.map((plugin) => (
                <div
                  key={plugin.id}
                  className="border border-gray-200 rounded-xl p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start gap-3">
                    {plugin.icon_url ? (
                      <img
                        src={plugin.icon_url}
                        alt={plugin.name}
                        className="w-10 h-10 rounded-lg object-cover"
                      />
                    ) : (
                      <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-lg">
                        {plugin.name.charAt(0)}
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-sm truncate">{plugin.name}</h3>
                      <p className="text-xs text-gray-500 mt-0.5">
                        v{plugin.version} · {plugin.category}
                        {plugin.is_official && (
                          <span className="ml-1 text-blue-600">✓ Official</span>
                        )}
                      </p>
                    </div>
                  </div>
                  <p className="text-xs text-gray-600 mt-2 line-clamp-2">
                    {plugin.description || 'No description available.'}
                  </p>
                  <div className="flex items-center justify-between mt-3">
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <span>⬇ {plugin.downloads}</span>
                      <span>⭐ {plugin.rating_avg.toFixed(1)}</span>
                    </div>
                    {isInstalled(plugin.id) ? (
                      <span className="text-xs text-green-600 font-medium">Installed</span>
                    ) : (
                      <button
                        onClick={() => handleInstall(plugin.id)}
                        disabled={loading}
                        className="px-3 py-1.5 bg-blue-600 text-white text-xs rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                      >
                        Install
                      </button>
                    )}
                  </div>
                  {/* Permissions badge */}
                  {(plugin.permissions?.length > 0) && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {plugin.permissions.slice(0, 3).map((perm: string) => (
                        <span
                          key={perm}
                          className="px-1.5 py-0.5 bg-gray-100 text-gray-600 text-[10px] rounded"
                        >
                          {perm.replace(/_/g, ' ')}
                        </span>
                      ))}
                      {plugin.permissions.length > 3 && (
                        <span className="px-1.5 py-0.5 bg-gray-100 text-gray-500 text-[10px] rounded">
                          +{plugin.permissions.length - 3} more
                        </span>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Installed Tab */}
      {activeTab === 'installed' && (
        <div>
          {loading ? (
            <div className="text-center py-12 text-gray-500">Loading installed plugins...</div>
          ) : installedPlugins.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              No plugins installed. Browse the marketplace to find plugins.
            </div>
          ) : (
            <div className="space-y-3">
              {installedPlugins.map((ip) => {
                const plugin = ip.plugin
                return (
                  <div
                    key={ip.id}
                    className={`border rounded-xl p-4 transition-opacity ${
                      ip.is_enabled ? 'border-gray-200' : 'border-gray-100 opacity-60'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {plugin?.icon_url ? (
                          <img
                            src={plugin.icon_url}
                            alt={plugin.name}
                            className="w-8 h-8 rounded-lg object-cover"
                          />
                        ) : (
                          <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-sm">
                            {plugin?.name?.charAt(0) || '?'}
                          </div>
                        )}
                        <div>
                          <h3 className="font-semibold text-sm">
                            {plugin?.name || 'Unknown Plugin'}
                            <span className="ml-2 text-xs text-gray-400">
                              v{plugin?.version || '—'}
                            </span>
                          </h3>
                          <p className="text-xs text-gray-500 mt-0.5">
                            {plugin?.description?.substring(0, 80) || 'No description'}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {/* Toggle */}
                        <button
                          onClick={() => handleToggle(ip.id, ip.is_enabled)}
                          className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
                            ip.is_enabled ? 'bg-blue-600' : 'bg-gray-300'
                          }`}
                        >
                          <span
                            className={`inline-block h-3.5 w-3.5 rounded-full bg-white transition-transform ${
                              ip.is_enabled ? 'translate-x-4.5' : 'translate-x-0.5'
                            }`}
                          />
                        </button>
                        {/* Config */}
                        <button
                          onClick={() => handleOpenConfig(ip)}
                          className="px-2.5 py-1.5 text-xs border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                          ⚙ Config
                        </button>
                        {/* Uninstall */}
                        <button
                          onClick={() => handleUninstall(ip.id)}
                          className="px-2.5 py-1.5 text-xs text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
                        >
                          Uninstall
                        </button>
                      </div>
                    </div>

                    {/* Hooks */}
                    {plugin?.hooks && plugin.hooks.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        <span className="text-[10px] text-gray-400">Hooks:</span>
                        {plugin.hooks.map((hook: string) => (
                          <span
                            key={hook}
                            className="px-1.5 py-0.5 bg-purple-50 text-purple-600 text-[10px] rounded"
                          >
                            {hook.replace(/on_/g, '').replace(/_/g, ' ')}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}

      {/* Configuration Modal */}
      {configuringPlugin && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full max-h-[80vh] overflow-auto p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">
                Configure: {configuringPlugin.plugin?.name || 'Plugin'}
              </h3>
              <button
                onClick={() => setConfiguringPlugin(null)}
                className="text-gray-400 hover:text-gray-600 text-xl"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              {/* Config form — dynamic based on plugin config_schema */}
              {Object.entries(pluginConfig).length === 0 ? (
                <p className="text-sm text-gray-500">
                  This plugin has no configuration options.
                </p>
              ) : (
                Object.entries(pluginConfig).map(([key, value]) => (
                  <div key={key}>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                    </label>
                    {typeof value === 'boolean' ? (
                      <input
                        type="checkbox"
                        checked={value as boolean}
                        onChange={(e) =>
                          setPluginConfig((prev) => ({ ...prev, [key]: e.target.checked }))
                        }
                        className="h-4 w-4 rounded border-gray-300"
                      />
                    ) : typeof value === 'number' ? (
                      <input
                        type="number"
                        value={value as number}
                        onChange={(e) =>
                          setPluginConfig((prev) => ({
                            ...prev,
                            [key]: Number(e.target.value),
                          }))
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                    ) : (
                      <input
                        type="text"
                        value={String(value)}
                        onChange={(e) =>
                          setPluginConfig((prev) => ({ ...prev, [key]: e.target.value }))
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                    )}
                  </div>
                ))
              )}
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setConfiguringPlugin(null)}
                className="px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveConfig}
                disabled={configSaving}
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {configSaving ? 'Saving...' : 'Save Configuration'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}