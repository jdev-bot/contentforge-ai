'use client'

import { useState, useEffect, useCallback } from 'react'
import { listAPIKeys, createAPIKey, deleteAPIKey, validateAPIKey, APIKey, APIKeyCreate } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { useToast } from '@/hooks/useToast'
import {
  Key,
  Plus,
  Trash2,
  RefreshCw,
  CheckCircle,
  XCircle,
  Eye,
  EyeOff,
  Zap,
  AlertTriangle,
  Loader2,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const PROVIDERS = [
  { id: 'google', name: 'Google AI Studio', description: 'Gemini 2.5 Flash — best free tier' },
  { id: 'groq', name: 'Groq', description: 'Llama 3.3 70B — fast inference' },
  { id: 'cerebras', name: 'Cerebras', description: 'Llama 3.3 70B — ultra-fast' },
  { id: 'openrouter', name: 'OpenRouter', description: 'Multi-model gateway' },
  { id: 'custom', name: 'Custom Provider', description: 'Any OpenAI-compatible API' },
] as const

type ProviderId = (typeof PROVIDERS)[number]['id']

interface APIKeysTabProps {
  userId?: string
}

export default function APIKeysTab(_props?: APIKeysTabProps) {
  const [keys, setKeys] = useState<APIKey[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddForm, setShowAddForm] = useState(false)
  const [adding, setAdding] = useState(false)
  const [validating, setValidating] = useState<string | null>(null)
  const [deleting, setDeleting] = useState<string | null>(null)
  const { showToast } = useToast()

  // Form state
  const [provider, setProvider] = useState<ProviderId>('google')
  const [apiKeyInput, setApiKeyInput] = useState('')
  const [showKey, setShowKey] = useState(false)
  const [baseUrl, setBaseUrl] = useState('')
  const [model, setModel] = useState('')
  const [label, setLabel] = useState('')

  const loadKeys = useCallback(async () => {
    try {
      setLoading(true)
      const data = await listAPIKeys()
      setKeys(data)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load API keys'
      showToast(message, 'error')
    } finally {
      setLoading(false)
    }
  }, [showToast])

  useEffect(() => {
    loadKeys()
  }, [loadKeys])

  const handleAdd = async () => {
    if (!apiKeyInput.trim()) {
      showToast('Please enter an API key', 'error')
      return
    }

    const data: APIKeyCreate = {
      provider,
      api_key: apiKeyInput.trim(),
    }
    if (provider === 'custom' && baseUrl.trim()) data.base_url = baseUrl.trim()
    if (model.trim()) data.model = model.trim()
    if (label.trim()) data.label = label.trim()

    try {
      setAdding(true)
      const newKey = await createAPIKey(data)
      setKeys(prev => [newKey, ...prev])
      setShowAddForm(false)
      setApiKeyInput('')
      setBaseUrl('')
      setModel('')
      setLabel('')
      showToast('API key added successfully', 'success')
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to add API key'
      showToast(message, 'error')
    } finally {
      setAdding(false)
    }
  }

  const handleDelete = async (keyId: string) => {
    try {
      setDeleting(keyId)
      await deleteAPIKey(keyId)
      setKeys(prev => prev.filter(k => k.id !== keyId))
      showToast('API key removed', 'success')
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to delete API key'
      showToast(message, 'error')
    } finally {
      setDeleting(null)
    }
  }

  const handleValidate = async (keyId: string) => {
    try {
      setValidating(keyId)
      const result = await validateAPIKey(keyId)
      setKeys(prev =>
        prev.map(k =>
          k.id === keyId
            ? { ...k, is_valid: result.is_valid, last_validated_at: new Date().toISOString() }
            : k
        )
      )
      showToast(result.is_valid ? 'API key is valid!' : `Key invalid: ${result.message}`, result.is_valid ? 'success' : 'error')
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Validation failed'
      showToast(message, 'error')
    } finally {
      setValidating(null)
    }
  }

  const getProviderName = (id: string) => PROVIDERS.find(p => p.id === id)?.name ?? id

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <Key className="h-5 w-5 text-amber-600" />
            AI Provider Keys
          </h3>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Bring your own API key — use your own provider account for AI features.
          </p>
        </div>
        {!showAddForm && (
          <Button onClick={() => setShowAddForm(true)} size="sm" className="flex items-center gap-1.5">
            <Plus className="h-4 w-4" />
            Add Key
          </Button>
        )}
      </div>

      {/* Info card */}
      <Card className="border-blue-200 dark:border-blue-800 bg-blue-50/50 dark:bg-blue-900/20">
        <CardContent className="p-4">
          <div className="flex gap-3">
            <Zap className="h-5 w-5 text-blue-600 mt-0.5 shrink-0" />
            <div className="text-sm text-blue-800 dark:text-blue-200">
              <p className="font-medium">Why bring your own key?</p>
              <ul className="mt-1 space-y-1 list-disc list-inside text-blue-700 dark:text-blue-300">
                <li>Your AI usage goes through <strong>your own provider account</strong></li>
                <li>No shared rate limits — you get your provider&apos;s full quota</li>
                <li>Your API key is <strong>encrypted at rest</strong> and never shown in full</li>
                <li>Free Google AI Studio tier: 10 RPM, 250 requests/day — enough to start</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Add form */}
      {showAddForm && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Add API Key</CardTitle>
            <CardDescription>Your key will be validated against the provider before saving.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Provider selector */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Provider
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                {PROVIDERS.map(p => (
                  <button
                    key={p.id}
                    onClick={() => { setProvider(p.id as ProviderId); if (p.id !== 'custom') setBaseUrl('') }}
                    className={cn(
                      'p-3 rounded-xl border-2 text-left transition-all',
                      provider === p.id
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30'
                        : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
                    )}
                  >
                    <div className="font-medium text-sm text-slate-900 dark:text-slate-100">{p.name}</div>
                    <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{p.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* API Key input */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                API Key
              </label>
              <div className="relative">
                <Input
                  type={showKey ? 'text' : 'password'}
                  value={apiKeyInput}
                  onChange={e => setApiKeyInput(e.target.value)}
                  placeholder={
                    provider === 'google' ? 'AIzaSy...' :
                    provider === 'groq' ? 'gsk_...' :
                    'Enter your API key'
                  }
                  className="pr-10"
                />
                <button
                  onClick={() => setShowKey(!showKey)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
                >
                  {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {/* Base URL (custom provider) */}
            {provider === 'custom' && (
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Base URL <span className="text-red-500">*</span>
                </label>
                <Input
                  value={baseUrl}
                  onChange={e => setBaseUrl(e.target.value)}
                  placeholder="https://your-llm.example.com/v1"
                />
              </div>
            )}

            {/* Model override (optional) */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Model Override <span className="text-slate-400">(optional)</span>
              </label>
              <Input
                value={model}
                onChange={e => setModel(e.target.value)}
                placeholder={
                  provider === 'google' ? 'gemini-2.5-flash (default)' :
                  provider === 'groq' ? 'llama-3.3-70b-versatile (default)' :
                  'Leave empty for provider default'
                }
              />
            </div>

            {/* Label (optional) */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Label <span className="text-slate-400">(optional)</span>
              </label>
              <Input
                value={label}
                onChange={e => setLabel(e.target.value)}
                placeholder="My Google Key"
              />
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-2">
              <Button onClick={handleAdd} disabled={adding || !apiKeyInput.trim()} className="flex items-center gap-1.5">
                {adding ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle className="h-4 w-4" />}
                {adding ? 'Validating & Saving...' : 'Add & Validate Key'}
              </Button>
              <Button variant="outline" onClick={() => { setShowAddForm(false); setApiKeyInput(''); setBaseUrl(''); setModel(''); setLabel('') }}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Keys list */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2].map(i => (
            <div key={i} className="h-24 rounded-xl bg-slate-100 dark:bg-slate-800 animate-pulse" />
          ))}
        </div>
      ) : keys.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Key className="h-12 w-12 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
            <p className="text-slate-500 dark:text-slate-400">
              No API keys added yet. Add your own key to start using AI features.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {keys.map(key => (
            <Card key={key.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-slate-900 dark:text-slate-100">
                        {key.label || getProviderName(key.provider)}
                      </span>
                      <Badge
                        variant={key.provider === 'google' ? 'info' : key.provider === 'groq' ? 'purple' : key.provider === 'cerebras' ? 'warning' : 'secondary'}
                        size="sm"
                      >
                        {getProviderName(key.provider)}
                      </Badge>
                      {key.is_valid ? (
                        <Badge variant="success" size="sm" dot>Valid</Badge>
                      ) : (
                        <Badge variant="error" size="sm" dot>
                          <span className="flex items-center gap-1">
                            <AlertTriangle className="h-3 w-3" />
                            Invalid
                          </span>
                        </Badge>
                      )}
                    </div>
                    <div className="text-sm text-slate-500 dark:text-slate-400 space-y-0.5">
                      <p>
                        <span className="font-mono bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded text-xs">
                          {key.masked_key}
                        </span>
                      </p>
                      {key.model && <p>Model: {key.model}</p>}
                      {key.base_url && <p className="truncate">URL: {key.base_url}</p>}
                      {key.last_validated_at && (
                        <p className="text-xs">
                          Last validated: {new Date(key.last_validated_at).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-1.5 shrink-0">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleValidate(key.id)}
                      disabled={validating === key.id}
                      title="Re-validate key"
                    >
                      {validating === key.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <RefreshCw className="h-4 w-4" />
                      )}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        if (confirm('Remove this API key?')) handleDelete(key.id)
                      }}
                      disabled={deleting === key.id}
                      className="text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
                      title="Delete key"
                    >
                      {deleting === key.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Trash2 className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}