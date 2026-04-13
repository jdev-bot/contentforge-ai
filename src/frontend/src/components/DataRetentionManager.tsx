'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Shield,
  FileText,
  Clock,
  AlertTriangle,
  Plus,
  Edit3,
  Trash2,
  RefreshCw,
  Save,
  X,
  ChevronDown,
  ChevronRight,
  Check,
  Archive,
  Calendar,
  Eye,
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
} from 'recharts'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { useToast } from '@/hooks/useToast'
import { cn } from '@/lib/utils'
import {
  getRetentionPolicies,
  createRetentionPolicy,
  updateRetentionPolicy,
  deleteRetentionPolicy,
  getRetentionCompliance,
  getRetentionAuditTrail,
  type RetentionPolicy,
  type ComplianceReport,
  type RetentionAuditEntry,
} from '@/lib/api'

type ActiveView = 'policies' | 'compliance' | 'audit'

export default function DataRetentionManager() {
  const [policies, setPolicies] = useState<RetentionPolicy[]>([])
  const [compliance, setCompliance] = useState<ComplianceReport | null>(null)
  const [auditTrail, setAuditTrail] = useState<RetentionAuditEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [activeView, setActiveView] = useState<ActiveView>('policies')
  const [expandedPolicy, setExpandedPolicy] = useState<string | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [editingPolicy, setEditingPolicy] = useState<string | null>(null)

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    data_type: 'content' as RetentionPolicy['data_type'],
    retention_days: 365,
    auto_delete: true,
    compliance_tags: [] as string[],
  })
  const [tagInput, setTagInput] = useState('')

  const { toast } = useToast()

  const fetchData = useCallback(async () => {
    try {
      setLoading(true)
      const [pol, comp, audit] = await Promise.all([
        getRetentionPolicies(),
        getRetentionCompliance(),
        getRetentionAuditTrail(),
      ])
      setPolicies(pol)
      setCompliance(comp)
      setAuditTrail(audit)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to fetch retention data'
      toast({ title: 'Error', description: message, variant: 'error' })
    } finally {
      setLoading(false)
    }
  }, [toast])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const handleRefresh = async () => {
    setRefreshing(true)
    await fetchData()
    setRefreshing(false)
  }

  const handleCreate = async () => {
    try {
      await createRetentionPolicy(formData)
      setShowCreateForm(false)
      resetForm()
      await fetchData()
      toast({ title: 'Policy created', description: 'Retention policy has been created.', variant: 'success' })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to create policy'
      toast({ title: 'Error', description: message, variant: 'error' })
    }
  }

  const handleUpdate = async (policyId: string) => {
    try {
      await updateRetentionPolicy(policyId, {
        name: formData.name,
        description: formData.description,
        data_type: formData.data_type,
        retention_days: formData.retention_days,
        auto_delete: formData.auto_delete,
        compliance_tags: formData.compliance_tags,
      })
      setEditingPolicy(null)
      resetForm()
      await fetchData()
      toast({ title: 'Policy updated', variant: 'success' })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to update policy'
      toast({ title: 'Error', description: message, variant: 'error' })
    }
  }

  const handleDelete = async (policyId: string) => {
    if (!confirm('Are you sure you want to delete this retention policy?')) return
    try {
      await deleteRetentionPolicy(policyId)
      await fetchData()
      toast({ title: 'Policy deleted', variant: 'info' })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to delete policy'
      toast({ title: 'Error', description: message, variant: 'error' })
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      data_type: 'content',
      retention_days: 365,
      auto_delete: true,
      compliance_tags: [],
    })
    setTagInput('')
  }

  const startEdit = (policy: RetentionPolicy) => {
    setEditingPolicy(policy.id)
    setFormData({
      name: policy.name,
      description: policy.description || '',
      data_type: policy.data_type,
      retention_days: policy.retention_days,
      auto_delete: policy.auto_delete,
      compliance_tags: policy.compliance_tags || [],
    })
  }

  const addTag = () => {
    if (tagInput.trim()) {
      setFormData(prev => ({
        ...prev,
        compliance_tags: [...prev.compliance_tags, tagInput.trim()],
      }))
      setTagInput('')
    }
  }

  const removeTag = (tag: string) => {
    setFormData(prev => ({
      ...prev,
      compliance_tags: prev.compliance_tags.filter(t => t !== tag),
    }))
  }

  const dataTypeIcon = (type: RetentionPolicy['data_type']) => {
    switch (type) {
      case 'content': return <FileText className="h-4 w-4" />
      case 'user_data': return <Shield className="h-4 w-4" />
      case 'analytics': return <BarChart className="h-4 w-4" />
      case 'logs': return <Archive className="h-4 w-4" />
      default: return <FileText className="h-4 w-4" />
    }
  }

  const dataTypeColor = (type: RetentionPolicy['data_type']) => {
    switch (type) {
      case 'content': return 'text-blue-600 dark:text-blue-400 bg-blue-500/10 dark:bg-blue-500/20'
      case 'user_data': return 'text-rose-600 dark:text-rose-400 bg-rose-500/10 dark:bg-rose-500/20'
      case 'analytics': return 'text-amber-600 dark:text-amber-400 bg-amber-500/10 dark:bg-amber-500/20'
      case 'logs': return 'text-slate-600 dark:text-slate-400 bg-slate-500/10 dark:bg-slate-500/20'
      default: return 'text-blue-600 dark:text-blue-400 bg-blue-500/10 dark:bg-blue-500/20'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
          <p className="text-slate-500 dark:text-slate-400">Loading retention data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <Shield className="w-6 h-6 text-violet-500" />
            Data Retention Manager
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Manage retention policies and compliance
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="primary"
            size="sm"
            leftIcon={<Plus className="h-4 w-4" />}
            onClick={() => { setShowCreateForm(true); resetForm() }}
          >
            New Policy
          </Button>
          <Button
            variant="ghost"
            size="sm"
            leftIcon={<RefreshCw className={cn('h-4 w-4', refreshing && 'animate-spin')} />}
            onClick={handleRefresh}
            disabled={refreshing}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* View Tabs */}
      <div className="flex items-center gap-2 bg-white/70 dark:bg-slate-800/70 backdrop-blur-xl rounded-xl border border-slate-200 dark:border-slate-700 p-1">
        {(['policies', 'compliance', 'audit'] as ActiveView[]).map(view => (
          <button
            key={view}
            onClick={() => setActiveView(view)}
            className={cn(
              'px-4 py-2 text-sm font-medium rounded-lg transition-all capitalize',
              activeView === view
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100'
            )}
          >
            {view}
          </button>
        ))}
      </div>

      {/* Create Policy Form */}
      <AnimatePresence>
        {showCreateForm && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <Card variant="glass" className="border-blue-500/30">
              <CardHeader>
                <CardTitle>Create Retention Policy</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                        Policy Name
                      </label>
                      <input
                        type="text"
                        value={formData.name}
                        onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))}
                        className="w-full px-3 py-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g. GDPR Content Retention"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                        Data Type
                      </label>
                      <select
                        value={formData.data_type}
                        onChange={e => setFormData(prev => ({ ...prev, data_type: e.target.value as RetentionPolicy['data_type'] }))}
                        className="w-full px-3 py-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="content">Content</option>
                        <option value="user_data">User Data</option>
                        <option value="analytics">Analytics</option>
                        <option value="logs">Logs</option>
                      </select>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                      Description
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={e => setFormData(prev => ({ ...prev, description: e.target.value }))}
                      className="w-full px-3 py-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      rows={2}
                      placeholder="Describe the retention policy..."
                    />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                        Retention Period (days)
                      </label>
                      <input
                        type="number"
                        value={formData.retention_days}
                        onChange={e => setFormData(prev => ({ ...prev, retention_days: parseInt(e.target.value) || 0 }))}
                        className="w-full px-3 py-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        min={1}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                        Auto-Delete
                      </label>
                      <div className="flex items-center gap-3 h-[42px]">
                        <button
                          onClick={() => setFormData(prev => ({ ...prev, auto_delete: !prev.auto_delete }))}
                          className={cn(
                            'relative w-12 h-6 rounded-full transition-colors',
                            formData.auto_delete ? 'bg-blue-600' : 'bg-slate-300 dark:bg-slate-600'
                          )}
                        >
                          <div className={cn(
                            'absolute top-0.5 w-5 h-5 rounded-full bg-white shadow-sm transition-transform',
                            formData.auto_delete ? 'left-6' : 'left-0.5'
                          )} />
                        </button>
                        <span className="text-sm text-slate-600 dark:text-slate-400">
                          {formData.auto_delete ? 'Enabled' : 'Disabled'}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                      Compliance Tags
                    </label>
                    <div className="flex items-center gap-2 mb-2">
                      <input
                        type="text"
                        value={tagInput}
                        onChange={e => setTagInput(e.target.value)}
                        onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addTag() } }}
                        className="flex-1 px-3 py-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Add tag..."
                      />
                      <Button variant="outline" size="sm" onClick={addTag}>
                        Add
                      </Button>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {formData.compliance_tags.map(tag => (
                        <Badge key={tag} variant="primary" size="sm" removable onRemove={() => removeTag(tag)}>
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <div className="flex items-center gap-3 pt-2">
                    <Button variant="primary" size="sm" leftIcon={<Save className="h-4 w-4" />} onClick={handleCreate}>
                      Create Policy
                    </Button>
                    <Button variant="ghost" size="sm" leftIcon={<X className="h-4 w-4" />} onClick={() => { setShowCreateForm(false); resetForm() }}>
                      Cancel
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Policies View */}
      {activeView === 'policies' && (
        <div className="space-y-3">
          <AnimatePresence>
            {policies.length === 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-12"
              >
                <Shield className="h-12 w-12 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
                <p className="text-slate-500 dark:text-slate-400 text-lg font-medium">No retention policies</p>
                <p className="text-slate-400 dark:text-slate-500 text-sm mt-1">
                  Create a policy to start managing data retention
                </p>
              </motion.div>
            ) : (
              policies.map((policy, index) => {
                const isExpanded = expandedPolicy === policy.id
                const isEditing = editingPolicy === policy.id
                return (
                  <motion.div
                    key={policy.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <Card variant="glass">
                      <CardContent>
                        <button
                          className="w-full flex items-center justify-between"
                          onClick={() => setExpandedPolicy(isExpanded ? null : policy.id)}
                        >
                          <div className="flex items-center gap-3">
                            {isExpanded ? <ChevronDown className="h-4 w-4 text-slate-400" /> : <ChevronRight className="h-4 w-4 text-slate-400" />}
                            <div className={cn('p-2 rounded-lg', dataTypeColor(policy.data_type))}>
                              {dataTypeIcon(policy.data_type)}
                            </div>
                            <div className="text-left">
                              <h3 className="font-semibold text-slate-900 dark:text-slate-100">{policy.name}</h3>
                              <div className="flex items-center gap-2 mt-1">
                                <Badge variant="outline" size="sm">
                                  {policy.data_type}
                                </Badge>
                                <Badge variant={policy.auto_delete ? 'success' : 'warning'} size="sm" dot>
                                  {policy.auto_delete ? 'Auto-delete' : 'Manual'}
                                </Badge>
                                <span className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1">
                                  <Clock className="h-3 w-3" />
                                  {policy.retention_days} days
                                </span>
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-2" onClick={e => e.stopPropagation()}>
                            <Button variant="ghost" size="sm" leftIcon={<Edit3 className="h-3.5 w-3.5" />} onClick={() => startEdit(policy)}>
                              Edit
                            </Button>
                            <Button variant="ghost" size="sm" leftIcon={<Trash2 className="h-3.5 w-3.5 text-rose-500" />} onClick={() => handleDelete(policy.id)}>
                              Delete
                            </Button>
                          </div>
                        </button>

                        <AnimatePresence>
                          {isExpanded && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: 'auto', opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                              transition={{ duration: 0.3 }}
                              className="overflow-hidden"
                            >
                              <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-700/50 space-y-3">
                                {policy.description && (
                                  <p className="text-sm text-slate-600 dark:text-slate-400">{policy.description}</p>
                                )}
                                {policy.compliance_tags && policy.compliance_tags.length > 0 && (
                                  <div>
                                    <p className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Compliance Tags</p>
                                    <div className="flex flex-wrap gap-2">
                                      {policy.compliance_tags.map(tag => (
                                        <Badge key={tag} variant="primary" size="sm">{tag}</Badge>
                                      ))}
                                    </div>
                                  </div>
                                )}
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                                  <div>
                                    <p className="text-xs text-slate-500 dark:text-slate-400">Data Type</p>
                                    <p className="font-medium text-slate-900 dark:text-slate-100 capitalize">{policy.data_type.replace('_', ' ')}</p>
                                  </div>
                                  <div>
                                    <p className="text-xs text-slate-500 dark:text-slate-400">Retention</p>
                                    <p className="font-medium text-slate-900 dark:text-slate-100">{policy.retention_days} days</p>
                                  </div>
                                  <div>
                                    <p className="text-xs text-slate-500 dark:text-slate-400">Auto-Delete</p>
                                    <p className="font-medium text-slate-900 dark:text-slate-100">{policy.auto_delete ? 'Yes' : 'No'}</p>
                                  </div>
                                  <div>
                                    <p className="text-xs text-slate-500 dark:text-slate-400">Created</p>
                                    <p className="font-medium text-slate-900 dark:text-slate-100">{new Date(policy.created_at).toLocaleDateString()}</p>
                                  </div>
                                </div>
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>

                        {/* Inline Edit Form */}
                        <AnimatePresence>
                          {isEditing && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: 'auto', opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                              className="overflow-hidden"
                            >
                              <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-700/50 space-y-3">
                                <input
                                  type="text"
                                  value={formData.name}
                                  onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))}
                                  className="w-full px-3 py-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                                <div className="flex items-center gap-2">
                                  <Button variant="primary" size="sm" leftIcon={<Save className="h-3.5 w-3.5" />} onClick={() => handleUpdate(policy.id)}>
                                    Save
                                  </Button>
                                  <Button variant="ghost" size="sm" leftIcon={<X className="h-3.5 w-3.5" />} onClick={() => setEditingPolicy(null)}>
                                    Cancel
                                  </Button>
                                </div>
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </CardContent>
                    </Card>
                  </motion.div>
                )
              })
            )}
          </AnimatePresence>
        </div>
      )}

      {/* Compliance View */}
      {activeView === 'compliance' && compliance && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card variant="glass">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-500/10 to-teal-500/10 dark:from-emerald-500/20 dark:to-teal-500/20">
                  <Check className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">{compliance.compliant_count}</p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">Compliant</p>
                </div>
              </div>
            </Card>
            <Card variant="glass">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-gradient-to-br from-amber-500/10 to-orange-500/10 dark:from-amber-500/20 dark:to-orange-500/20">
                  <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">{compliance.warning_count}</p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">Warnings</p>
                </div>
              </div>
            </Card>
            <Card variant="glass">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-gradient-to-br from-rose-500/10 to-red-500/10 dark:from-rose-500/20 dark:to-red-500/20">
                  <AlertTriangle className="h-5 w-5 text-rose-600 dark:text-rose-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">{compliance.violation_count}</p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">Violations</p>
                </div>
              </div>
            </Card>
          </div>

          {/* Compliance Score */}
          <Card variant="glass">
            <CardHeader>
              <CardTitle>Compliance Score</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4">
                <div className="relative w-24 h-24">
                  <svg className="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="40" fill="none" stroke="currentColor" strokeWidth="8" className="text-slate-200 dark:text-slate-700" />
                    <circle cx="50" cy="50" r="40" fill="none" stroke="currentColor" strokeWidth="8" strokeDasharray={`${compliance.score * 2.51} 251`} className={cn(
                      compliance.score >= 90 ? 'text-emerald-500' : compliance.score >= 70 ? 'text-amber-500' : 'text-rose-500'
                    )} />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-xl font-bold text-slate-900 dark:text-slate-100">{compliance.score}%</span>
                  </div>
                </div>
                <div className="flex-1">
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    {compliance.score >= 90
                      ? 'Your data retention practices are fully compliant.'
                      : compliance.score >= 70
                        ? 'Some areas need attention to achieve full compliance.'
                        : 'Significant compliance issues detected. Immediate action recommended.'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Issues List */}
          {compliance.issues && compliance.issues.length > 0 && (
            <Card variant="glass">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-amber-500" />
                  Compliance Issues
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {compliance.issues.map((issue, i) => (
                    <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50">
                      <Badge variant={issue.severity === 'high' ? 'error' : issue.severity === 'medium' ? 'warning' : 'info'} size="sm" dot>
                        {issue.severity}
                      </Badge>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-slate-900 dark:text-slate-100">{issue.message}</p>
                        {issue.recommendation && (
                          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{issue.recommendation}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Audit Trail View */}
      {activeView === 'audit' && (
        <div className="space-y-4">
          {auditTrail.length === 0 ? (
            <div className="text-center py-12">
              <Eye className="h-12 w-12 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
              <p className="text-slate-500 dark:text-slate-400 text-lg font-medium">No audit entries</p>
              <p className="text-slate-400 dark:text-slate-500 text-sm mt-1">
                Retention actions will appear here
              </p>
            </div>
          ) : (
            auditTrail.map((entry, index) => (
              <motion.div
                key={entry.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <Card variant="glass">
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={cn(
                          'p-2 rounded-lg',
                          entry.action === 'delete' ? 'bg-rose-500/10 dark:bg-rose-500/20 text-rose-600 dark:text-rose-400' :
                          entry.action === 'archive' ? 'bg-amber-500/10 dark:bg-amber-500/20 text-amber-600 dark:text-amber-400' :
                          'bg-blue-500/10 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400'
                        )}>
                          {entry.action === 'delete' ? <Trash2 className="h-4 w-4" /> :
                           entry.action === 'archive' ? <Archive className="h-4 w-4" /> :
                           <FileText className="h-4 w-4" />}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-slate-900 dark:text-slate-100 capitalize">
                            {entry.action} — {entry.resource_type.replace('_', ' ')}
                          </p>
                          <p className="text-xs text-slate-500 dark:text-slate-400">
                            {entry.details} · {new Date(entry.timestamp).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <Badge variant={entry.action === 'delete' ? 'error' : entry.action === 'archive' ? 'warning' : 'info'} size="sm">
                        {entry.action}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))
          )}
        </div>
      )}
    </div>
  )
}