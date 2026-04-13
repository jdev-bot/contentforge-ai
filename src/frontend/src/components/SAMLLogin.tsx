'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Shield,
  Key,
  ExternalLink,
  Loader2,
  Check,
  AlertCircle,
  Globe,
  ChevronDown,
  ChevronRight,
  Copy,
  Plus,
  Trash2,
  RefreshCw,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Input } from '@/components/ui/Input'
import { useToast } from '@/hooks/useToast'
import {
  listSAMLProviders,
  createSAMLProvider,
  fetchSAMLMetadata,
  initiateSAMLLogin,
  type SAMLProvider,
} from '@/lib/api'

interface SAMLLoginProps {
  isOpen: boolean
  onClose: () => void
  onLoginSuccess?: (result: { user_id: string; email: string; is_new_user: boolean }) => void
}

type TabId = 'login' | 'configure' | 'mapping'

export default function SAMLLogin({ isOpen, onClose, onLoginSuccess }: SAMLLoginProps) {
  const { showToast } = useToast()
  const [activeTab, setActiveTab] = useState<TabId>('login')
  const [providers, setProviders] = useState<SAMLProvider[]>([])
  const [selectedProviderId, setSelectedProviderId] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingProviders, setIsLoadingProviders] = useState(false)

  // Configure form state
  const [configForm, setConfigForm] = useState({
    name: '',
    display_name: '',
    entity_id: '',
    sso_url: '',
    slo_url: '',
    metadata_url: '',
    certificate: '',
  })
  const [isFetchingMetadata, setIsFetchingMetadata] = useState(false)

  // Attribute mapping state
  const [attributeMapping, setAttributeMapping] = useState<Record<string, string>>({
    email: 'email',
    full_name: 'displayName',
    first_name: 'firstName',
    last_name: 'lastName',
    groups: 'groups',
  })
  const [selectedProviderForMapping, setSelectedProviderForMapping] = useState<string>('')

  // Load available SAML providers
  useEffect(() => {
    if (isOpen) {
      loadProviders()
    }
  }, [isOpen])

  const loadProviders = async () => {
    setIsLoadingProviders(true)
    try {
      const result = await listSAMLProviders()
      setProviders(result)
      if (result.length > 0 && !selectedProviderId) {
        setSelectedProviderId(result[0].id)
      }
    } catch (error: any) {
      showToast('Failed to load SAML providers', 'error')
    } finally {
      setIsLoadingProviders(false)
    }
  }

  const handleSAMLLogin = useCallback(async () => {
    if (!selectedProviderId) {
      showToast('Please select an Identity Provider', 'error')
      return
    }

    setIsLoading(true)
    try {
      const result = await initiateSAMLLogin({
        provider_id: selectedProviderId,
        redirect_uri: `${window.location.origin}/saml/acs`,
      })
      // Redirect to IdP
      window.location.href = result.login_url
    } catch (error: any) {
      showToast(error.message || 'SAML login failed', 'error')
    } finally {
      setIsLoading(false)
    }
  }, [selectedProviderId, showToast])

  const handleFetchMetadata = useCallback(async () => {
    if (!configForm.metadata_url) {
      showToast('Enter a metadata URL first', 'error')
      return
    }

    setIsFetchingMetadata(true)
    try {
      const result = await fetchSAMLMetadata({ metadata_url: configForm.metadata_url })
      setConfigForm(prev => ({
        ...prev,
        entity_id: result.entity_id || prev.entity_id,
        sso_url: result.sso_url || prev.sso_url,
        slo_url: result.slo_url || prev.slo_url,
        certificate: result.certificate || prev.certificate,
      }))
      showToast('Metadata fetched successfully', 'success')
    } catch (error: any) {
      showToast(error.message || 'Failed to fetch metadata', 'error')
    } finally {
      setIsFetchingMetadata(false)
    }
  }, [configForm.metadata_url, showToast])

  const handleCreateProvider = useCallback(async () => {
    if (!configForm.name || !configForm.display_name || !configForm.entity_id || !configForm.sso_url) {
      showToast('Please fill in all required fields', 'error')
      return
    }

    setIsLoading(true)
    try {
      await createSAMLProvider({
        name: configForm.name,
        display_name: configForm.display_name,
        entity_id: configForm.entity_id,
        sso_url: configForm.sso_url,
        slo_url: configForm.slo_url || undefined,
        metadata_url: configForm.metadata_url || undefined,
        certificate: configForm.certificate || undefined,
        is_active: true,
      })
      showToast('SAML provider created successfully', 'success')
      setConfigForm({ name: '', display_name: '', entity_id: '', sso_url: '', slo_url: '', metadata_url: '', certificate: '' })
      loadProviders()
      setActiveTab('login')
    } catch (error: any) {
      showToast(error.message || 'Failed to create provider', 'error')
    } finally {
      setIsLoading(false)
    }
  }, [configForm, showToast])

  const handleAddMappingRow = useCallback(() => {
    const key = `custom_${Object.keys(attributeMapping).length + 1}`
    setAttributeMapping(prev => ({ ...prev, [key]: '' }))
  }, [attributeMapping])

  const handleRemoveMappingRow = useCallback((key: string) => {
    setAttributeMapping(prev => {
      const next = { ...prev }
      delete next[key]
      return next
    })
  }, [])

  if (!isOpen) return null

  const tabs = [
    { id: 'login' as TabId, label: 'SSO Login', icon: Shield },
    { id: 'configure' as TabId, label: 'Configure IdP', icon: Key },
    { id: 'mapping' as TabId, label: 'Attribute Mapping', icon: Globe },
  ]

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ type: 'spring', duration: 0.5 }}
          className="w-full max-w-2xl"
          onClick={(e) => e.stopPropagation()}
        >
          <Card variant="glass" padding="none" className="overflow-hidden">
            {/* Header */}
            <div className="p-6 border-b border-white/10 dark:border-white/5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-xl bg-gradient-to-br from-violet-500/20 to-blue-500/20">
                    <Shield className="w-5 h-5 text-violet-500" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">
                      SAML Single Sign-On
                    </h2>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      Authenticate with your enterprise Identity Provider
                    </p>
                  </div>
                </div>
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors text-slate-500"
                >
                  ✕
                </button>
              </div>

              {/* Tabs */}
              <div className="flex gap-1 mt-5 bg-slate-100 dark:bg-slate-800/50 rounded-xl p-1">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                      activeTab === tab.id
                        ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm'
                        : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
                    }`}
                  >
                    <tab.icon className="w-4 h-4" />
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Content */}
            <div className="p-6 max-h-[60vh] overflow-y-auto">
              <AnimatePresence mode="wait">
                {/* Login Tab */}
                {activeTab === 'login' && (
                  <motion.div
                    key="login"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 10 }}
                    className="space-y-4"
                  >
                    {isLoadingProviders ? (
                      <div className="flex items-center justify-center py-12">
                        <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
                      </div>
                    ) : providers.length === 0 ? (
                      <div className="text-center py-12">
                        <div className="text-4xl mb-3">🏢</div>
                        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                          No SAML Providers Configured
                        </h3>
                        <p className="text-sm text-slate-500 dark:text-slate-400 mt-2 max-w-sm mx-auto">
                          Set up your enterprise Identity Provider to enable SAML SSO for your organization.
                        </p>
                        <Button className="mt-4" onClick={() => setActiveTab('configure')}>
                          <Plus className="w-4 h-4 mr-2" /> Configure IdP
                        </Button>
                      </div>
                    ) : (
                      <>
                        <div>
                          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                            Select Identity Provider
                          </label>
                          <div className="space-y-2">
                            {providers.map((provider) => (
                              <motion.button
                                key={provider.id}
                                whileHover={{ scale: 1.01 }}
                                whileTap={{ scale: 0.99 }}
                                onClick={() => setSelectedProviderId(provider.id)}
                                className={`w-full text-left p-4 rounded-xl border-2 transition-all ${
                                  selectedProviderId === provider.id
                                    ? 'border-violet-500 bg-violet-50 dark:bg-violet-900/20'
                                    : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
                                }`}
                              >
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center gap-3">
                                    <div className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800">
                                      <Shield className="w-4 h-4 text-slate-600 dark:text-slate-400" />
                                    </div>
                                    <div>
                                      <p className="font-medium text-slate-900 dark:text-slate-100">
                                        {provider.display_name}
                                      </p>
                                      <p className="text-xs text-slate-500 dark:text-slate-400">
                                        {provider.name}
                                      </p>
                                    </div>
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <Badge variant="outline" className="text-xs">
                                      {provider.is_active ? 'Active' : 'Inactive'}
                                    </Badge>
                                    {selectedProviderId === provider.id && (
                                      <Check className="w-5 h-5 text-violet-500" />
                                    )}
                                  </div>
                                </div>
                              </motion.button>
                            ))}
                          </div>
                        </div>

                        <Button
                          className="w-full"
                          onClick={handleSAMLLogin}
                          disabled={isLoading || !selectedProviderId}
                        >
                          {isLoading ? (
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          ) : (
                            <ExternalLink className="w-4 h-4 mr-2" />
                          )}
                          {isLoading ? 'Redirecting...' : 'Sign in with SAML SSO'}
                        </Button>
                      </>
                    )}
                  </motion.div>
                )}

                {/* Configure Tab */}
                {activeTab === 'configure' && (
                  <motion.div
                    key="configure"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 10 }}
                    className="space-y-4"
                  >
                    {/* Metadata URL (auto-fetch) */}
                    <div>
                      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                        IdP Metadata URL
                      </label>
                      <div className="flex gap-2">
                        <Input
                          value={configForm.metadata_url}
                          onChange={(e) => setConfigForm(prev => ({ ...prev, metadata_url: e.target.value }))}
                          placeholder="https://idp.example.com/metadata"
                          className="flex-1"
                        />
                        <Button
                          variant="secondary"
                          onClick={handleFetchMetadata}
                          disabled={isFetchingMetadata}
                        >
                          {isFetchingMetadata ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <RefreshCw className="w-4 h-4" />
                          )}
                        </Button>
                      </div>
                      <p className="text-xs text-slate-500 mt-1">
                        Enter your IdP metadata URL to auto-configure
                      </p>
                    </div>

                    <div className="h-px bg-slate-200 dark:bg-slate-700" />

                    {/* Manual configuration */}
                    <div className="space-y-3">
                      <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                        <Key className="w-4 h-4" /> Provider Details
                      </h4>

                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                            Name *
                          </label>
                          <Input
                            value={configForm.name}
                            onChange={(e) => setConfigForm(prev => ({ ...prev, name: e.target.value }))}
                            placeholder="okta"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                            Display Name *
                          </label>
                          <Input
                            value={configForm.display_name}
                            onChange={(e) => setConfigForm(prev => ({ ...prev, display_name: e.target.value }))}
                            placeholder="Okta"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                          Entity ID *
                        </label>
                        <Input
                          value={configForm.entity_id}
                          onChange={(e) => setConfigForm(prev => ({ ...prev, entity_id: e.target.value }))}
                          placeholder="https://idp.example.com/entity"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                          SSO URL *
                        </label>
                        <Input
                          value={configForm.sso_url}
                          onChange={(e) => setConfigForm(prev => ({ ...prev, sso_url: e.target.value }))}
                          placeholder="https://idp.example.com/sso"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                          SLO URL (optional)
                        </label>
                        <Input
                          value={configForm.slo_url}
                          onChange={(e) => setConfigForm(prev => ({ ...prev, slo_url: e.target.value }))}
                          placeholder="https://idp.example.com/slo"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                          X.509 Certificate
                        </label>
                        <textarea
                          value={configForm.certificate}
                          onChange={(e) => setConfigForm(prev => ({ ...prev, certificate: e.target.value }))}
                          placeholder="MIIDBzCCAe+gAwIBAgIJAP..."
                          className="w-full h-24 px-3 py-2 text-sm rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 font-mono resize-none"
                        />
                      </div>
                    </div>

                    <Button
                      className="w-full"
                      onClick={handleCreateProvider}
                      disabled={isLoading}
                    >
                      {isLoading ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <Plus className="w-4 h-4 mr-2" />
                      )}
                      Create Provider
                    </Button>
                  </motion.div>
                )}

                {/* Attribute Mapping Tab */}
                {activeTab === 'mapping' && (
                  <motion.div
                    key="mapping"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 10 }}
                    className="space-y-4"
                  >
                    <div>
                      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                        Select Provider
                      </label>
                      <select
                        value={selectedProviderForMapping}
                        onChange={(e) => setSelectedProviderForMapping(e.target.value)}
                        className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm"
                      >
                        <option value="">Choose a provider...</option>
                        {providers.map((p) => (
                          <option key={p.id} value={p.id}>
                            {p.display_name} ({p.name})
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                          Attribute Mapping
                        </h4>
                        <Button variant="ghost" size="sm" onClick={handleAddMappingRow}>
                          <Plus className="w-3 h-3 mr-1" /> Add
                        </Button>
                      </div>
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        Map SAML assertion attributes to local user fields
                      </p>

                      <div className="space-y-2">
                        {Object.entries(attributeMapping).map(([localAttr, samlAttr]) => (
                          <motion.div
                            key={localAttr}
                            layout
                            className="flex items-center gap-2"
                          >
                            <Input
                              value={localAttr}
                              disabled
                              className="w-1/3 text-sm bg-slate-50 dark:bg-slate-900"
                            />
                            <ChevronRight className="w-4 h-4 text-slate-400 shrink-0" />
                            <Input
                              value={samlAttr}
                              onChange={(e) =>
                                setAttributeMapping(prev => ({
                                  ...prev,
                                  [localAttr]: e.target.value,
                                }))
                              }
                              placeholder="SAML attribute name"
                              className="flex-1 text-sm"
                            />
                            {!['email', 'full_name', 'first_name', 'last_name', 'groups'].includes(localAttr) && (
                              <button
                                onClick={() => handleRemoveMappingRow(localAttr)}
                                className="p-1.5 hover:bg-red-50 dark:hover:bg-red-900/20 rounded text-red-500 transition-colors"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            )}
                          </motion.div>
                        ))}
                      </div>
                    </div>

                    <Button
                      className="w-full"
                      disabled={!selectedProviderForMapping}
                      onClick={() => {
                        if (selectedProviderForMapping) {
                          // Update attribute mapping via API
                          import('@/lib/api').then(api => api.updateSAMLAttributeMapping(selectedProviderForMapping, attribute_mapping))
                            .then(() => showToast('Attribute mapping updated', 'success'))
                            .catch((err: any) => showToast(err.message || 'Failed to update mapping', 'error'))
                        }
                      }}
                    >
                      <Globe className="w-4 h-4 mr-2" />
                      Save Attribute Mapping
                    </Button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </Card>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}