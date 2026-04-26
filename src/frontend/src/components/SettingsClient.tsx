'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { getUserProfile, updateUserProfile, getUsageSummary, UserProfile, UsageStats, exportUserData, deleteUserAccount, restoreUserAccount, getDeletionStatus } from '@/lib/api'
import { formatApiError } from '@/lib/api'
import { getSubscriptionStatus, createPortalSession, SubscriptionStatus, getStripeConfig } from '@/lib/stripe'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { useToast } from '@/hooks/useToast'
import SubscriptionModal from './SubscriptionModal'
import APIKeysTab from './APIKeysTab'
import { 
  User, 
  Key, 
  CreditCard, 
  CheckCircle, 
  AlertCircle,
  Loader2,
  ExternalLink,
  Sparkles,
  Crown,
  AlertTriangle,
  X,
  Download,
  Trash2,
  RefreshCw,
  Shield,
  FileText,
  ArrowLeft
} from 'lucide-react'

export interface AuthUser {
  id: string
  email: string
  full_name?: string
  avatar_url?: string
}

interface SettingsClientProps {
  user: AuthUser
}

export default function SettingsClient({ user }: SettingsClientProps) {
  const router = useRouter()
  const { showToast } = useToast()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [usageStats, setUsageStats] = useState<UsageStats | null>(null)
  const [subscription, setSubscription] = useState<SubscriptionStatus | null>(null)
  const [stripeConfig, setStripeConfig] = useState<{ is_configured: boolean; test_mode: boolean } | null>(null)
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false)
  const [portalLoading, setPortalLoading] = useState(false)
  
  // GDPR states
  const [exportLoading, setExportLoading] = useState(false)
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [restoreLoading, setRestoreLoading] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [deleteConfirmText, setDeleteConfirmText] = useState('')
  const [deletionStatus, setDeletionStatus] = useState<{ deletion_scheduled: boolean; days_remaining?: number } | null>(null)
  
  // Form state
  const [fullName, setFullName] = useState('')
  const [originalFullName, setOriginalFullName] = useState('')
  
  useEffect(() => {
    loadSettings()
    loadStripeConfig()
    loadDeletionStatus()
  }, [])

  async function loadSettings() {
    try {
      setLoading(true)
      const [profileData, usageData, subData] = await Promise.all([
        getUserProfile(),
        getUsageSummary(),
        getSubscriptionStatus().catch(() => null),
      ])
      setProfile(profileData)
      setUsageStats(usageData.stats)
      setSubscription(subData)
      
      const name = profileData.full_name || ''
      setFullName(name)
      setOriginalFullName(name)
    } catch (error) {
      console.error('Failed to load settings:', error)
      showToast('Failed to load settings', 'error')
    } finally {
      setLoading(false)
    }
  }

  async function loadStripeConfig() {
    try {
      const config = await getStripeConfig()
      setStripeConfig(config)
    } catch (error) {
      console.error('Failed to load Stripe config:', error)
    }
  }

  async function loadDeletionStatus() {
    try {
      const status = await getDeletionStatus()
      setDeletionStatus(status)
    } catch (error) {
      // Deletion status endpoint may not exist yet, that's OK
    }
  }

  const handleSaveProfile = async () => {
    if (fullName === originalFullName) return
    
    try {
      setSaving(true)
      const updated = await updateUserProfile({ full_name: fullName })
      setProfile(updated)
      setOriginalFullName(fullName)
      showToast('Profile updated successfully', 'success')
    } catch (error: unknown) {
      console.error('Failed to update profile:', error)
      const errorMessage = formatApiError(error, 'Failed to update profile')
      showToast(errorMessage, 'error')
    } finally {
      setSaving(false)
    }
  }

  const handleManageSubscription = async () => {
    try {
      setPortalLoading(true)
      const { url } = await createPortalSession()
      window.open(url, '_blank')
    } catch (error: unknown) {
      console.error('Failed to open portal:', error)
      const errorMessage = formatApiError(error, 'Failed to open billing portal')
      showToast(errorMessage, 'error')
    } finally {
      setPortalLoading(false)
    }
  }

  // GDPR: Export User Data
  const handleExportData = async () => {
    try {
      setExportLoading(true)
      const exportData = await exportUserData()
      
      const blob = new Blob([JSON.stringify(exportData.user_data, null, 2)], { type: 'application/json' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `contentforge-data-export-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      showToast('Your data has been exported successfully', 'success')
    } catch (error: unknown) {
      console.error('Failed to export data:', error)
      const errorMessage = formatApiError(error, 'Failed to export data')
      showToast(errorMessage, 'error')
    } finally {
      setExportLoading(false)
    }
  }

  // GDPR: Request Account Deletion
  const handleDeleteAccount = async () => {
    if (deleteConfirmText !== 'DELETE') {
      showToast('Please type DELETE to confirm', 'error')
      return
    }
    
    try {
      setDeleteLoading(true)
      const result = await deleteUserAccount()
      setDeletionStatus({ deletion_scheduled: true, days_remaining: 30 })
      setShowDeleteConfirm(false)
      showToast(result.message, 'success')
    } catch (error: unknown) {
      console.error('Failed to delete account:', error)
      const errorMessage = formatApiError(error, 'Failed to request account deletion')
      showToast(errorMessage, 'error')
    } finally {
      setDeleteLoading(false)
    }
  }

  // GDPR: Restore Account
  const handleRestoreAccount = async () => {
    try {
      setRestoreLoading(true)
      await restoreUserAccount()
      setDeletionStatus(null)
      showToast('Account restored successfully', 'success')
    } catch (error: unknown) {
      console.error('Failed to restore account:', error)
      const errorMessage = formatApiError(error, 'Failed to restore account')
      showToast(errorMessage, 'error')
    } finally {
      setRestoreLoading(false)
    }
  }

  const formatDate = (timestamp?: number | string) => {
    if (!timestamp) return 'N/A'
    const date = typeof timestamp === 'number' ? new Date(timestamp * 1000) : new Date(timestamp)
    return date.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    })
  }

  const getPlanIcon = (tier?: string) => {
    switch (tier) {
      case 'pro':
        return <Crown className="h-5 w-5 text-purple-600" />
      case 'starter':
        return <Sparkles className="h-5 w-5 text-blue-600" />
      default:
        return <CreditCard className="h-5 w-5 text-slate-500 dark:text-slate-400" />
    }
  }

  const getStatusBadge = (status?: string) => {
    switch (status) {
      case 'active':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-green-100 text-green-700 text-xs font-medium">
            <CheckCircle className="h-3 w-3" />
            Active
          </span>
        )
      case 'past_due':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-yellow-100 text-yellow-700 text-xs font-medium">
            <AlertTriangle className="h-3 w-3" />
            Past Due
          </span>
        )
      case 'canceled':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-red-100 text-red-700 text-xs font-medium">
            <X className="h-3 w-3" />
            Canceled
          </span>
        )
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-medium">
            Inactive
          </span>
        )
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 p-4 md:p-8">
        <div className="max-w-3xl mx-auto space-y-6">
          <Skeleton className="h-8 w-48 mb-2" />
          <Skeleton className="h-4 w-64 mb-8" />
          <Card>
            <CardContent className="p-6">
              <Skeleton className="h-6 w-32 mb-4" />
              <div className="space-y-4">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <Skeleton className="h-6 w-32 mb-4" />
              <Skeleton className="h-20 w-full" />
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  const currentTier = (profile?.subscription_tier || 'free') as 'free' | 'starter' | 'pro'

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 p-4 md:p-8">
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push('/dashboard')}
            className="p-2 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors"
          >
            <ArrowLeft className="h-5 w-5 text-slate-600 dark:text-slate-400" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <Shield className="h-6 w-6 text-blue-500" />
              Settings
            </h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
              Manage your profile, subscription, and account preferences
            </p>
          </div>
        </div>

        {/* Profile Settings */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center">
                <User className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Profile</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">Manage your personal information</p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Email Address
                </label>
                <Input
                  value={profile?.email || user.email}
                  disabled
                  className="bg-slate-50 dark:bg-slate-900"
                />
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Email cannot be changed</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Full Name
                </label>
                <Input
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Enter your full name"
                />
              </div>

              <div className="flex items-center justify-between pt-2">
                {fullName !== originalFullName && (
                  <span className="text-sm text-blue-600 flex items-center gap-1">
                    <AlertCircle className="h-4 w-4" />
                    Unsaved changes
                  </span>
                )}
                <div className="ml-auto">
                  <Button
                    onClick={handleSaveProfile}
                    disabled={fullName === originalFullName || saving}
                  >
                    {saving ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Save Changes
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Subscription Settings */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center">
                {getPlanIcon(profile?.subscription_tier)}
              </div>
              <div>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Subscription</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">Manage your plan and billing</p>
              </div>
            </div>

            <div className="space-y-6">
              {/* Current Plan */}
              <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-900 rounded-lg">
                <div>
                  <p className="text-sm text-slate-600 dark:text-slate-400">Current Plan</p>
                  <div className="flex items-center gap-2 mt-1">
                    <p className="text-lg font-semibold text-slate-900 dark:text-slate-100 capitalize">
                      {profile?.subscription_tier || 'Free'}
                    </p>
                    {getStatusBadge(subscription?.status)}
                  </div>
                  {subscription?.current_period_end && (
                    <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                      Renews on {formatDate(subscription.current_period_end)}
                    </p>
                  )}
                  {subscription?.cancel_at_period_end && (
                    <p className="text-sm text-red-600 mt-1">
                      Cancels at period end
                    </p>
                  )}
                </div>
                <div className="flex flex-col gap-2">
                  {currentTier === 'free' ? (
                    <Button onClick={() => setShowSubscriptionModal(true)}>
                      Upgrade
                    </Button>
                  ) : (
                    <>
                      <Button
                        variant="outline"
                        onClick={handleManageSubscription}
                        disabled={portalLoading}
                      >
                        {portalLoading ? (
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        ) : (
                          <ExternalLink className="h-4 w-4 mr-2" />
                        )}
                        Manage Billing
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setShowSubscriptionModal(true)}
                      >
                        Change Plan
                      </Button>
                    </>
                  )}
                </div>
              </div>

              {/* Usage */}
              <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-slate-600 dark:text-slate-400">Monthly Usage</span>
                  <span className="font-medium">
                    {usageStats?.monthly_usage_count || 0} / {usageStats?.monthly_usage_limit || 10}
                  </span>
                </div>
                <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      (usageStats?.percentage_used || 0) > 80 ? 'bg-red-500' : 
                      (usageStats?.percentage_used || 0) > 50 ? 'bg-yellow-500' : 'bg-blue-500'
                    }`}
                    style={{ width: `${Math.min(usageStats?.percentage_used || 0, 100)}%` }}
                  />
                </div>
                <div className="flex justify-between mt-2">
                  <span className="text-xs text-slate-500 dark:text-slate-400">
                    {usageStats?.percentage_used || 0}% used
                  </span>
                  <span className="text-xs text-slate-500 dark:text-slate-400">
                    {usageStats?.remaining || 0} remaining
                  </span>
                </div>
              </div>

              {/* Test Mode Notice */}
              {stripeConfig?.test_mode && (
                <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start gap-3">
                  <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                  <div className="text-sm text-yellow-800">
                    <p className="font-medium">Test Mode Active</p>
                    <p className="mt-1">
                      Use test card <code className="bg-yellow-100 px-1 py-0.5 rounded font-mono text-xs">4242 4242 4242 4242</code> with any future date and CVC.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* API Keys — Real BYOK */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center">
                <Key className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">API Keys</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">Manage your AI provider keys</p>
              </div>
            </div>

            <APIKeysTab userId={user.id} showHeader={false} />
          </CardContent>
        </Card>

        {/* GDPR Data & Privacy Section */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="h-10 w-10 rounded-lg bg-emerald-100 flex items-center justify-center">
                <Shield className="h-5 w-5 text-emerald-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Data & Privacy</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">Manage your personal data and privacy settings</p>
              </div>
            </div>

            <div className="space-y-6">
              {/* Account Deletion Status Warning */}
              {deletionStatus?.deletion_scheduled && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <h4 className="font-medium text-red-900">Account Deletion Scheduled</h4>
                      <p className="text-sm text-red-700 mt-1">
                        Your account is scheduled for deletion in {deletionStatus.days_remaining} days. 
                        You can restore your account before this date by clicking the button below.
                      </p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleRestoreAccount}
                        disabled={restoreLoading}
                        className="mt-3"
                      >
                        {restoreLoading ? (
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        ) : (
                          <RefreshCw className="h-4 w-4 mr-2" />
                        )}
                        Restore Account
                      </Button>
                    </div>
                  </div>
                </div>
              )}

              {/* Download My Data */}
              <div className="flex items-start justify-between p-4 bg-slate-50 dark:bg-slate-900 rounded-lg">
                <div>
                  <h4 className="font-medium text-slate-900 dark:text-slate-100 flex items-center gap-2">
                    <Download className="h-4 w-4" />
                    Download My Data
                  </h4>
                  <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                    Export all your personal data including content, projects, and activity logs in JSON format.
                    This is in compliance with GDPR data portability rights.
                  </p>
                </div>
                <Button
                  variant="outline"
                  onClick={handleExportData}
                  disabled={exportLoading}
                >
                  {exportLoading ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <FileText className="h-4 w-4 mr-2" />
                  )}
                  Export Data
                </Button>
              </div>

              {/* Delete Account */}
              {!deletionStatus?.deletion_scheduled && (
                <div className="flex items-start justify-between p-4 bg-red-50 rounded-lg border border-red-100">
                  <div>
                    <h4 className="font-medium text-red-900 flex items-center gap-2">
                      <Trash2 className="h-4 w-4" />
                      Delete Account
                    </h4>
                    <p className="text-sm text-red-700 mt-1">
                      Permanently delete your account and all associated data. This action can be undone 
                      within 30 days. After that, all data will be permanently removed.
                    </p>
                  </div>
                  <Button
                    variant="danger"
                    onClick={() => setShowDeleteConfirm(true)}
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete Account
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Delete Account Confirmation Modal */}
        {showDeleteConfirm && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-md w-full p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="h-10 w-10 rounded-full bg-red-100 flex items-center justify-center">
                  <AlertTriangle className="h-5 w-5 text-red-600" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Delete Account</h3>
              </div>
              
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                This action will schedule your account for deletion. You will have 30 days to restore 
                your account. After 30 days, all your data including content, projects, and personal 
                information will be permanently deleted.
              </p>
              
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                <p className="text-sm text-red-700 font-medium">This action cannot be undone after 30 days.</p>
              </div>
              
              <div className="space-y-3">
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
                  Type DELETE to confirm:
                </label>
                <Input
                  value={deleteConfirmText}
                  onChange={(e) => setDeleteConfirmText(e.target.value)}
                  placeholder="Type DELETE"
                  className="border-red-300 focus:border-red-500 focus:ring-red-500"
                />
              </div>
              
              <div className="flex gap-3 mt-6">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowDeleteConfirm(false)
                    setDeleteConfirmText('')
                  }}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  variant="danger"
                  onClick={handleDeleteAccount}
                  disabled={deleteConfirmText !== 'DELETE' || deleteLoading}
                  className="flex-1"
                >
                  {deleteLoading ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Trash2 className="h-4 w-4 mr-2" />
                  )}
                  Delete Account
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Subscription Modal */}
        {showSubscriptionModal && (
          <SubscriptionModal
            isOpen={showSubscriptionModal}
            onClose={() => setShowSubscriptionModal(false)}
            currentTier={currentTier}
          />
        )}
      </div>
    </div>
  )
}