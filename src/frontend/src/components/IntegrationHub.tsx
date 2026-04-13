'use client'

import { useState } from 'react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Network, Plus, CheckCircle, XCircle, Zap } from 'lucide-react'

interface IntegrationConfig {
  id: string
  name: string
  type: string
  provider: string
  enabled: boolean
  last_sync: string | null
  status: 'connected' | 'disconnected' | 'error'
}

export default function IntegrationHub() {
  const [integrations] = useState<IntegrationConfig[]>([])

  const availableIntegrations = [
    { type: 'webhook', name: 'Slack Webhook', provider: 'Slack', icon: '💬' },
    { type: 'api', name: 'GitHub API', provider: 'GitHub', icon: '🐙' },
    { type: 'api', name: 'Twitter API', provider: 'Twitter', icon: '🐦' },
    { type: 'webhook', name: 'Discord Webhook', provider: 'Discord', icon: '🎮' },
    { type: 'polling', name: 'RSS Feed Poller', provider: 'RSS', icon: '📡' },
    { type: 'streaming', name: 'SSE Stream', provider: 'Custom', icon: '🔌' },
  ]

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Integration Hub</h2>
          <p className="text-slate-500 mt-1">Connect and manage third-party integrations</p>
        </div>
        <Button className="flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Add Integration
        </Button>
      </div>

      {/* Active Integrations */}
      <Card className="p-4">
        <h3 className="font-medium text-slate-900 dark:text-white mb-3">Active Integrations</h3>
        {integrations.length === 0 ? (
          <div className="text-center py-8">
            <Network className="w-12 h-12 mx-auto text-slate-300 mb-4" />
            <p className="text-slate-500">No integrations configured yet</p>
          </div>
        ) : (
          <div className="space-y-2">
            {integrations.map((integration) => (
              <div key={integration.id} className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                <div className="flex items-center gap-3">
                  {integration.status === 'connected' ? (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  ) : integration.status === 'error' ? (
                    <XCircle className="w-5 h-5 text-red-500" />
                  ) : (
                    <XCircle className="w-5 h-5 text-slate-400" />
                  )}
                  <div>
                    <span className="font-medium">{integration.name}</span>
                    <span className="text-xs text-slate-500 ml-2">{integration.provider}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-500">{integration.type}</span>
                  <Button className="text-xs">Configure</Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Available Integrations */}
      <Card className="p-4">
        <h3 className="font-medium text-slate-900 dark:text-white mb-3">Available Integrations</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {availableIntegrations.map((integration) => (
            <div key={integration.name} className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg flex items-center gap-3 cursor-pointer hover:shadow-md transition-shadow">
              <span className="text-2xl">{integration.icon}</span>
              <div className="flex-1">
                <span className="font-medium text-sm">{integration.name}</span>
                <p className="text-xs text-slate-500">{integration.type} • {integration.provider}</p>
              </div>
              <Zap className="w-4 h-4 text-blue-500" />
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}