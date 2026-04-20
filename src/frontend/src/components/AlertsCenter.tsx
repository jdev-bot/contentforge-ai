'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Bell, 
  TrendingUp, 
  TrendingDown, 
  Trophy, 
  X, 
  Check, 
  Settings,
  Clock,
  Zap,
  Filter,
  RefreshCw,
  EyeOff
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Badge, CountBadge } from '@/components/ui/Badge'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Avatar } from '@/components/ui/Avatar'
import { Tooltip } from '@/components/ui/Tooltip'
import { Input } from '@/components/ui/Input'
import { cn } from '@/lib/utils'
import { PageHeader } from '@/components/ui/PageHeader'

// Types
export type AlertType = 'viral' | 'declining' | 'milestone' | 'system' | 'team'
export type AlertSeverity = 'critical' | 'high' | 'medium' | 'low'
export type AlertStatus = 'unread' | 'read' | 'acknowledged' | 'dismissed'

export interface Alert {
  id: string
  type: AlertType
  severity: AlertSeverity
  status: AlertStatus
  title: string
  message: string
  contentPreview?: {
    title: string
    platform: string
    metrics: {
      views?: number
      engagement?: number
      changePercent: number
    }
  }
  timestamp: Date
  acknowledgedAt?: Date
  dismissedAt?: Date
  metadata?: Record<string, unknown>
}

export interface AlertRule {
  id: string
  name: string
  type: AlertType
  enabled: boolean
  conditions: {
    metric: 'views' | 'engagement' | 'shares' | 'comments' | 'reach'
    operator: 'gt' | 'lt' | 'gte' | 'lte' | 'eq'
    threshold: number
    timeframe: '1h' | '24h' | '7d' | '30d'
  }
  notificationChannels: ('in_app' | 'email' | 'push' | 'slack')[]
}

// Mock data
const mockAlerts: Alert[] = [
  {
    id: '1',
    type: 'viral',
    severity: 'high',
    status: 'unread',
    title: 'Content Going Viral!',
    message: 'Your post "10 AI Trends for 2025" is gaining rapid traction.',
    contentPreview: {
      title: '10 AI Trends for 2025',
      platform: 'LinkedIn',
      metrics: { views: 45000, engagement: 12.5, changePercent: 340 }
    },
    timestamp: new Date(Date.now() - 1000 * 60 * 15) // 15 mins ago
  },
  {
    id: '2',
    type: 'milestone',
    severity: 'medium',
    status: 'unread',
    title: 'Milestone Reached!',
    message: 'Congratulations! You\'ve reached 10,000 total views this month.',
    timestamp: new Date(Date.now() - 1000 * 60 * 60) // 1 hour ago
  },
  {
    id: '3',
    type: 'declining',
    severity: 'medium',
    status: 'read',
    title: 'Engagement Declining',
    message: 'Your recent post engagement has dropped by 25% compared to average.',
    contentPreview: {
      title: 'Marketing Strategy Tips',
      platform: 'Twitter',
      metrics: { views: 1200, engagement: 2.1, changePercent: -25 }
    },
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 3) // 3 hours ago
  },
  {
    id: '4',
    type: 'team',
    severity: 'low',
    status: 'acknowledged',
    title: 'New Team Member',
    message: 'Sarah Johnson has joined your ContentForge team.',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24) // 1 day ago
  },
  {
    id: '5',
    type: 'system',
    severity: 'low',
    status: 'dismissed',
    title: 'Weekly Report Ready',
    message: 'Your weekly performance report is now available.',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 48) // 2 days ago
  }
]

const mockAlertRules: AlertRule[] = [
  {
    id: '1',
    name: 'Viral Content Detection',
    type: 'viral',
    enabled: true,
    conditions: { metric: 'views', operator: 'gt', threshold: 10000, timeframe: '24h' },
    notificationChannels: ['in_app', 'email', 'push']
  },
  {
    id: '2',
    name: 'Engagement Drop Alert',
    type: 'declining',
    enabled: true,
    conditions: { metric: 'engagement', operator: 'lt', threshold: 5, timeframe: '7d' },
    notificationChannels: ['in_app', 'email']
  },
  {
    id: '3',
    name: 'Milestone Notifications',
    type: 'milestone',
    enabled: true,
    conditions: { metric: 'views', operator: 'gte', threshold: 10000, timeframe: '30d' },
    notificationChannels: ['in_app', 'push']
  }
]

// Components
export function AlertsBell({ 
  onClick, 
  className 
}: { 
  onClick?: () => void
  className?: string 
}) {
  const [unreadCount, setUnreadCount] = useState(3)
  const [isRealTime, setIsRealTime] = useState(true)

  // Simulate real-time updates
  useEffect(() => {
    if (!isRealTime) return
    const interval = setInterval(() => {
      // In real implementation, this would check for new alerts
    }, 30000)
    return () => clearInterval(interval)
  }, [isRealTime])

  return (
    <Tooltip content="Alerts" position="bottom">
      <button
        onClick={onClick}
        className={cn(
          'relative p-2.5 rounded-xl',
          'text-slate-600 dark:text-slate-400',
          'hover:bg-slate-100 dark:hover:bg-slate-800',
          'hover:text-slate-900 dark:hover:text-slate-100',
          'transition-all duration-200',
          'focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500',
          className
        )}
        aria-label="Alerts"
      >
        <Bell className="h-5 w-5" />
        
        {/* Real-time indicator */}
        {isRealTime && (
          <span className="absolute top-1 right-1 w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
        )}
        
        {/* Unread badge */}
        <CountBadge 
          count={unreadCount} 
          variant="danger" 
          className="absolute -top-1 -right-1"
        />
      </button>
    </Tooltip>
  )
}

export function AlertsPanel({ 
  isOpen, 
  onClose 
}: { 
  isOpen: boolean
  onClose: () => void 
}) {
  const [alerts, setAlerts] = useState<Alert[]>(mockAlerts)
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null)
  const [filterType, setFilterType] = useState<AlertType | 'all'>('all')
  const [showRules, setShowRules] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)

  const unreadCount = useMemo(() => 
    alerts.filter(a => a.status === 'unread').length, 
    [alerts]
  )

  const filteredAlerts = useMemo(() => {
    let filtered = alerts
    if (filterType !== 'all') {
      filtered = filtered.filter(a => a.type === filterType)
    }
    // Sort by timestamp (newest first) and status (unread first)
    return filtered.sort((a, b) => {
      if (a.status === 'unread' && b.status !== 'unread') return -1
      if (a.status !== 'unread' && b.status === 'unread') return 1
      return b.timestamp.getTime() - a.timestamp.getTime()
    })
  }, [alerts, filterType])

  const handleAcknowledge = useCallback((alertId: string) => {
    setAlerts(prev => prev.map(a => 
      a.id === alertId 
        ? { ...a, status: 'acknowledged', acknowledgedAt: new Date() }
        : a
    ))
  }, [])

  const handleDismiss = useCallback((alertId: string) => {
    setAlerts(prev => prev.map(a => 
      a.id === alertId 
        ? { ...a, status: 'dismissed', dismissedAt: new Date() }
        : a
    ))
    if (selectedAlert?.id === alertId) {
      setSelectedAlert(null)
    }
  }, [selectedAlert])

  const handleMarkAllRead = useCallback(() => {
    setAlerts(prev => prev.map(a => 
      a.status === 'unread' 
        ? { ...a, status: 'read' }
        : a
    ))
  }, [])

  const handleRefresh = useCallback(() => {
    setIsRefreshing(true)
    setTimeout(() => setIsRefreshing(false), 1000)
  }, [])

  const formatTimeAgo = (date: Date) => {
    const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000)
    if (seconds < 60) return 'Just now'
    const minutes = Math.floor(seconds / 60)
    if (minutes < 60) return `${minutes}m ago`
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}h ago`
    const days = Math.floor(hours / 24)
    return `${days}d ago`
  }

  const getAlertIcon = (type: AlertType) => {
    switch (type) {
      case 'viral': return <TrendingUp className="h-5 w-5 text-emerald-500" />
      case 'declining': return <TrendingDown className="h-5 w-5 text-rose-500" />
      case 'milestone': return <Trophy className="h-5 w-5 text-amber-500" />
      case 'team': return <Avatar name="Team" size="sm" />
      default: return <Zap className="h-5 w-5 text-blue-500" />
    }
  }

  const getSeverityColor = (severity: AlertSeverity) => {
    switch (severity) {
      case 'critical': return 'bg-rose-500'
      case 'high': return 'bg-orange-500'
      case 'medium': return 'bg-amber-500'
      case 'low': return 'bg-blue-500'
    }
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
            onClick={onClose}
          />
          
          {/* Panel */}
          <motion.div
            initial={{ opacity: 0, x: 400 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 400 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 bottom-0 w-full max-w-md bg-white dark:bg-slate-900 shadow-2xl z-50 flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <Bell className="h-6 w-6 text-slate-700 dark:text-slate-300" />
                  {unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 w-4 h-4 bg-rose-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                      {unreadCount}
                    </span>
                  )}
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                    Alerts Center
                  </h2>
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                    <span className="text-xs text-slate-500 dark:text-slate-400">
                      Real-time
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <Tooltip content="Refresh" position="bottom">
                  <button
                    onClick={handleRefresh}
                    className={cn(
                      'p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors',
                      isRefreshing && 'animate-spin'
                    )}
                  >
                    <RefreshCw className="h-4 w-4 text-slate-500" />
                  </button>
                </Tooltip>
                <Tooltip content="Alert Rules" position="bottom">
                  <button
                    onClick={() => setShowRules(!showRules)}
                    className={cn(
                      'p-2 rounded-lg transition-colors',
                      showRules 
                        ? 'bg-blue-100 dark:bg-blue-500/20 text-blue-600' 
                        : 'hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500'
                    )}
                  >
                    <Settings className="h-4 w-4" />
                  </button>
                </Tooltip>
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <X className="h-5 w-5 text-slate-500" />
                </button>
              </div>
            </div>

            {/* Filters */}
            {!showRules && (
              <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Filter className="h-4 w-4 text-slate-400" />
                  <select
                    value={filterType}
                    onChange={(e) => setFilterType(e.target.value as AlertType | 'all')}
                    className="text-sm bg-transparent border-none focus:ring-0 text-slate-700 dark:text-slate-300 cursor-pointer"
                  >
                    <option value="all">All Alerts</option>
                    <option value="viral">Viral</option>
                    <option value="declining">Declining</option>
                    <option value="milestone">Milestones</option>
                    <option value="team">Team</option>
                    <option value="system">System</option>
                  </select>
                </div>
                
                {unreadCount > 0 && (
                  <button
                    onClick={handleMarkAllRead}
                    className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                  >
                    Mark all as read
                  </button>
                )}
              </div>
            )}

            {/* Content */}
            <div className="flex-1 overflow-y-auto">
              {showRules ? (
                <AlertRulesConfig 
                  rules={mockAlertRules}
                  onSave={(rules) => {
                    // Saving rules
                    setShowRules(false)
                  }}
                />
              ) : selectedAlert ? (
                <AlertDetailView 
                  alert={selectedAlert}
                  onBack={() => setSelectedAlert(null)}
                  onAcknowledge={() => handleAcknowledge(selectedAlert.id)}
                  onDismiss={() => handleDismiss(selectedAlert.id)}
                />
              ) : (
                <div className="divide-y divide-slate-100 dark:divide-slate-800">
                  {filteredAlerts.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-12 text-center">
                      <div className="w-16 h-16 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-4">
                        <Bell className="h-8 w-8 text-slate-400" />
                      </div>
                      <p className="text-slate-500 dark:text-slate-400">
                        No alerts to display
                      </p>
                      <p className="text-sm text-slate-400 dark:text-slate-500 mt-1">
                        You&apos;re all caught up!
                      </p>
                    </div>
                  ) : (
                    filteredAlerts.map((alert) => (
                      <motion.div
                        key={alert.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className={cn(
                          'p-4 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer',
                          alert.status === 'unread' && 'bg-blue-50/50 dark:bg-blue-500/5'
                        )}
                        onClick={() => {
                          if (alert.status === 'unread') {
                            handleAcknowledge(alert.id)
                          }
                          setSelectedAlert(alert)
                        }}
                      >
                        <div className="flex gap-3">
                          <div className="flex-shrink-0 mt-1">
                            {getAlertIcon(alert.type)}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-start justify-between gap-2">
                              <div>
                                <p className={cn(
                                  'font-medium text-slate-900 dark:text-slate-100',
                                  alert.status === 'unread' && 'font-semibold'
                                )}>
                                  {alert.title}
                                </p>
                                <p className="text-sm text-slate-600 dark:text-slate-400 mt-1 line-clamp-2">
                                  {alert.message}
                                </p>
                              </div>
                              <span className={cn(
                                'w-2 h-2 rounded-full flex-shrink-0 mt-2',
                                getSeverityColor(alert.severity)
                              )} />
                            </div>
                            
                            <div className="flex items-center gap-3 mt-2">
                              <span className="text-xs text-slate-400 dark:text-slate-500 flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                {formatTimeAgo(alert.timestamp)}
                              </span>
                              
                              {alert.contentPreview && (
                                <Badge variant="outline" size="sm">
                                  {alert.contentPreview.platform}
                                </Badge>
                              )}
                              
                              <Badge 
                                variant={alert.status === 'unread' ? 'primary' : 'default'} 
                                size="sm"
                              >
                                {alert.status}
                              </Badge>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    ))
                  )}
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

function AlertDetailView({ 
  alert, 
  onBack, 
  onAcknowledge, 
  onDismiss 
}: { 
  alert: Alert
  onBack: () => void
  onAcknowledge: () => void
  onDismiss: () => void 
}) {
  const getAlertIcon = (type: AlertType) => {
    switch (type) {
      case 'viral': return <TrendingUp className="h-8 w-8 text-emerald-500" />
      case 'declining': return <TrendingDown className="h-8 w-8 text-rose-500" />
      case 'milestone': return <Trophy className="h-8 w-8 text-amber-500" />
      default: return <Zap className="h-8 w-8 text-blue-500" />
    }
  }

  return (
    <div className="p-4">
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-sm text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 mb-6"
      >
        ← Back to alerts
      </button>

      <div className="flex items-start gap-4 mb-6">
        <div className="p-3 rounded-2xl bg-slate-100 dark:bg-slate-800">
          {getAlertIcon(alert.type)}
        </div>
        <div>
          <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100">
            {alert.title}
          </h3>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            {alert.timestamp.toLocaleString()}
          </p>
        </div>
      </div>

      <Card className="mb-6">
        <CardContent className="p-4">
          <p className="text-slate-700 dark:text-slate-300">
            {alert.message}
          </p>
        </CardContent>
      </Card>

      {alert.contentPreview && (
        <Card className="mb-6 border-l-4 border-l-blue-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Related Content</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="font-medium text-slate-900 dark:text-slate-100 mb-4">
              {alert.contentPreview.title}
            </p>
            
            <div className="grid grid-cols-3 gap-4">
              {alert.contentPreview.metrics.views && (
                <div>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Views</p>
                  <p className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                    {alert.contentPreview.metrics.views.toLocaleString()}
                  </p>
                </div>
              )}
              {alert.contentPreview.metrics.engagement && (
                <div>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Engagement</p>
                  <p className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                    {alert.contentPreview.metrics.engagement}%
                  </p>
                </div>
              )}
              <div>
                <p className="text-xs text-slate-500 dark:text-slate-400">Change</p>
                <p className={cn(
                  'text-lg font-semibold',
                  alert.contentPreview.metrics.changePercent > 0 
                    ? 'text-emerald-600 dark:text-emerald-400' 
                    : 'text-rose-600 dark:text-rose-400'
                )}>
                  {alert.contentPreview.metrics.changePercent > 0 ? '+' : ''}
                  {alert.contentPreview.metrics.changePercent}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="flex gap-3">
        {alert.status !== 'acknowledged' && (
          <Button 
            variant="primary" 
            className="flex-1"
            leftIcon={<Check className="h-4 w-4" />}
            onClick={onAcknowledge}
          >
            Acknowledge
          </Button>
        )}
        <Button 
          variant="outline" 
          className={alert.status === 'acknowledged' ? 'flex-1' : ''}
          leftIcon={<EyeOff className="h-4 w-4" />}
          onClick={onDismiss}
        >
          Dismiss
        </Button>
      </div>
    </div>
  )
}

function AlertRulesConfig({ 
  rules, 
  onSave 
}: { 
  rules: AlertRule[]
  onSave: (rules: AlertRule[]) => void 
}) {
  const [localRules, setLocalRules] = useState(rules)
  const [editingRule, setEditingRule] = useState<AlertRule | null>(null)

  const handleToggle = (ruleId: string) => {
    setLocalRules(prev => prev.map(r => 
      r.id === ruleId ? { ...r, enabled: !r.enabled } : r
    ))
  }

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
          Alert Rules
        </h3>
        <Button 
          size="sm" 
          leftIcon={<Check className="h-4 w-4" />}
          onClick={() => onSave(localRules)}
        >
          Save Changes
        </Button>
      </div>

      <div className="space-y-4">
        {localRules.map((rule) => (
          <Card key={rule.id} className={cn(
            'transition-all',
            !rule.enabled && 'opacity-60'
          )}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h4 className="font-medium text-slate-900 dark:text-slate-100">
                      {rule.name}
                    </h4>
                    <Badge 
                      variant={rule.enabled ? 'success' : 'default'} 
                      size="sm"
                    >
                      {rule.enabled ? 'Active' : 'Disabled'}
                    </Badge>
                  </div>
                  
                  <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
                    Trigger when {rule.conditions.metric} is {rule.conditions.operator} {rule.conditions.threshold} in {rule.conditions.timeframe}
                  </p>
                  
                  <div className="flex items-center gap-2 mt-3">
                    <span className="text-xs text-slate-400">Notify via:</span>
                    {rule.notificationChannels.map(channel => (
                      <Badge key={channel} variant="outline" size="sm">
                        {channel}
                      </Badge>
                    ))}
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleToggle(rule.id)}
                    className={cn(
                      'w-12 h-6 rounded-full transition-colors relative',
                      rule.enabled 
                        ? 'bg-blue-500' 
                        : 'bg-slate-300 dark:bg-slate-600'
                    )}
                  >
                    <span className={cn(
                      'absolute top-1 w-4 h-4 rounded-full bg-white transition-transform',
                      rule.enabled ? 'left-7' : 'left-1'
                    )} />
                  </button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Button 
        variant="outline" 
        className="w-full mt-4"
        leftIcon={<Zap className="h-4 w-4" />}
      >
        Create New Rule
      </Button>
    </div>
  )
}

// Main export component for tab view
export default function AlertsCenter() {
  const [isPanelOpen, setIsPanelOpen] = useState(false)

  return (
    <div className="space-y-6">
      <PageHeader
        title="Alerts Center"
        description="Monitor your content performance and team activity"
        icon={<Bell className="w-5 h-5 text-blue-600" />}
        actions={<AlertsBell onClick={() => setIsPanelOpen(true)} />}
      />

      <AlertsPanel 
        isOpen={isPanelOpen} 
        onClose={() => setIsPanelOpen(false)} 
      />

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="border-l-4 border-l-rose-500">
          <CardContent className="p-4">
            <p className="text-sm text-slate-500 dark:text-slate-400">Critical Alerts</p>
            <p className="text-2xl font-bold text-rose-600 dark:text-rose-400 mt-1">0</p>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-orange-500">
          <CardContent className="p-4">
            <p className="text-sm text-slate-500 dark:text-slate-400">High Priority</p>
            <p className="text-2xl font-bold text-orange-600 dark:text-orange-400 mt-1">1</p>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-blue-500">
          <CardContent className="p-4">
            <p className="text-sm text-slate-500 dark:text-slate-400">Unread</p>
            <p className="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-1">3</p>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-emerald-500">
          <CardContent className="p-4">
            <p className="text-sm text-slate-500 dark:text-slate-400">Active Rules</p>
            <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">3</p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-500 dark:text-slate-400 text-center py-8">
            Click the bell icon to view and manage your alerts
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
