'use client'

import { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { getUserProfile, updateUserProfile, getUsageSummary, UserProfile, UsageStats } from '@/lib/api'
import { getSubscriptionStatus, createPortalSession, SubscriptionStatus, getStripeConfig } from '@/lib/stripe'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { useToast } from '@/hooks/useToast'
import SubscriptionModal from '@/components/SubscriptionModal'
import { 
  User, 
  Key, 
  CreditCard, 
  CheckCircle, 
  AlertCircle,
  Eye,
  EyeOff,
  Copy,
  Loader2,
  ExternalLink,
  Sparkles,
  Crown,
  RefreshCw,
  AlertTriangle,
  X
} from 'lucide-react'

interface SettingsTabProps {
  user: {
    id: string
    email: string
    full_name?: string
  }
}

// Separate component that uses useSearchParams
function SettingsContent({ user }: SettingsTabProps) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { showToast } = useToast()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [usageStats, setUsageStats] = useState<UsageStats | null>(null)
  const [subscription, setSubscription] = useState<SubscriptionStatus | null>(null)
  const [stripeConfig, setStripeConfig] = useState<{ is_configured: boolean; test_mode: boolean } | null>(null)
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false)
  const [portalLoading, setPortalLoading] = useState(false)
  const [syncLoading, setSyncLoading] = useState(false)
  
  // Form state
  const [fullName, setFullName] = useState('')
  const [originalFullName, setOriginalFullName] = useState('')
  
  // API Key visibility
  const [showStripeKey, setShowStripeKey] = useState(false)
  const [showGroqKey, setShowGroqKey] = useState(false)
  
  // Success/Cancel messages from URL
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [cancelMessage, setCancelMessage] = useState<string | null>(null)
  const [canceledMessage, setCanceledMessage] = useState<string | null>(null)

  // Mock API keys (in production, these would be fetched from secure storage)
  const [apiKeys] = useState({
    stripe: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || 'pk_live_•••••••••••••••••••••••••••••••••',
    groq: process.env.NEXT_PUBLIC_GROQ_API_KEY || 'gsk_•••••••••••••••••••••••••••••••••',
  })

  useEffect(() => {
    loadSettings()
    checkUrlParams()
    loadStripeConfig()
  }, [])

  function checkUrlParams() {
    const success = searchParams.get('success')
    const canceled = searchParams.get('canceled')
    
    if (success) {
      setSuccessMessage('Payment successful! Your subscription is now active.')
      // Clear URL params
      router.replace('/settings')
    }
    if (canceled) {
      setCanceledMessage('Payment was canceled. Your subscription was not changed.')
      // Clear URL params
      router.replace('/settings')
    }
  }

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
      const errorMessage = error instanceof Error ? error.message : 'Failed to update profile'
      showToast(errorMessage, 'error')
    } finally {
      setSaving(false)
    }
  }

  const handleCopyKey = (key: string, label: string) => {
    navigator.clipboard.writeText(key)
    showToast(`${label} copied to clipboard`, 'success')
  }

  const maskKey = (key: string) => {
    if (key.includes('•')) return key
    if (key.length <= 8) return key
    return `${key.slice(0, 8)}••••••••••••••••••••`
  }

  const handleManageSubscription = async () => {
    try {
      setPortalLoading(true)
      const { url } = await createPortalSession()
      window.open(url, '_blank')
    } catch (error: unknown) {
      console.error('Failed to open portal:', error)
      const errorMessage = error instanceof Error ? error.message : 'Failed to open billing portal'
      showToast(errorMessage, 'error')
    } finally {
      setPortalLoading(false)
    }
  }

  const handleSyncSubscription = async () => {
    try {
      setSyncLoading(true)
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/stripe/sync`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${(await supabase.auth.getSession()).data.session?.access_token || ''}`,
          'Content-Type': 'application/json',
        },
      })
      
      if (!response.ok) throw new Error('Failed to sync')
      
      const result = await response.json()
      if (result.synced) {
        showToast('Subscription synced successfully', 'success')
        await loadSettings()
      }
    } catch (error: unknown) {
      console.error('Failed to sync subscription:', error)
      showToast('Failed to sync subscription', 'error')
    } finally {
      setSyncLoading(false)
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
        return <CreditCard className="h-5 w-5 text-gray-500" />
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
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-gray-100 text-gray-700 text-xs font-medium">
            Inactive
          </span>
        )
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
        </div>
        
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
    )
  }

  const currentTier = (profile?.subscription_tier || 'free') as 'free' | 'starter' | 'pro'

  return (
    <div className="space-y-6">
      {/* Success/Cancel Messages */}
      {successMessage && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
          <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-green-900">{successMessage}</p>
          </div>
        </div>
      )}
      {canceledMessage && (
        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-yellow-900">{canceledMessage}</p>
          </div>
        </div>
      )}

      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
      </div>

      {/* Profile Settings */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center">
              <User className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Profile</h3>
              <p className="text-sm text-gray-500">Manage your personal information</p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Address
              </label>
              <Input
                value={profile?.email || user.email}
                disabled
                className="bg-gray-50"
              />
              <p className="text-xs text-gray-500 mt-1">Email cannot be changed</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
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
              <h3 className="text-lg font-semibold text-gray-900">Subscription</h3>
              <p className="text-sm text-gray-500">Manage your plan and billing</p>
            </div>
          </div>

          <div className="space-y-6">
            {/* Current Plan */}
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="text-sm text-gray-600">Current Plan</p>
                <div className="flex items-center gap-2 mt-1">
                  <p className="text-lg font-semibold text-gray-900 capitalize">
                    {profile?.subscription_tier || 'Free'}
                  </p>
                  {getStatusBadge(subscription?.status)}
                </div>
                {subscription?.current_period_end && (
                  <p className="text-sm text-gray-500 mt-1">
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
            <div className="pt-4 border-t border-gray-200">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">Monthly Usage</span>
                <span className="font-medium">
                  {usageStats?.monthly_usage_count || 0} / {usageStats?.monthly_usage_limit || 10}
                </span>
              </div>
              <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    (usageStats?.percentage_used || 0) > 80 ? 'bg-red-500' : 
                    (usageStats?.percentage_used || 0) > 50 ? 'bg-yellow-500' : 'bg-blue-500'
                  }`}
                  style={{ width: `${Math.min(usageStats?.percentage_used || 0, 100)}%` }}
                />
              </div>
              <div className="flex justify-between mt-2">
                <span className="text-xs text-gray-500">
                  {usageStats?.percentage_used || 0}% used
                </span>
                <span className="text-xs text-gray-500">
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

      {/* API Keys */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center">
              <Key className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">API Keys</h3>
              <p className="text-sm text-gray-500">Manage your integration keys</p>
            </div>
          </div>

          <div className="space-y-4">
            {/* Stripe Key */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Stripe Publishable Key
              </label>
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <Input
                    value={showStripeKey ? apiKeys.stripe : maskKey(apiKeys.stripe)}
                    disabled
                    className="font-mono text-sm"
                  />
                </div>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => setShowStripeKey(!showStripeKey)}
                >
                  {showStripeKey ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => handleCopyKey(apiKeys.stripe, 'Stripe key')}
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Used for payment processing
              </p>
            </div>

            {/* Groq Key */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Groq API Key
              </label>
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <Input
                    value={showGroqKey ? apiKeys.groq : maskKey(apiKeys.groq)}
                    disabled
                    className="font-mono text-sm"
                  />
                </div>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => setShowGroqKey(!showGroqKey)}
                >
                  {showGroqKey ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => handleCopyKey(apiKeys.groq, 'Groq key')}
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Used for AI content generation
              </p>
            </div>

            <div className="p-4 bg-blue-50 rounded-lg mt-4">
              <p className="text-sm text-blue-700">
                <strong>Note:</strong> These keys are read-only. To update them, modify your environment variables or contact support.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Subscription Modal */}
      {showSubscriptionModal && (
        <SubscriptionModal
          isOpen={showSubscriptionModal}
          onClose={() => setShowSubscriptionModal(false)}
          currentTier={currentTier}
        />
      )}
    </div>
  )
}

// Loading fallback
function SettingsLoading() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-8 w-48" />
      <Card>
        <CardContent className="p-6">
          <Skeleton className="h-32 w-full" />
        </CardContent>
      </Card>
    </div>
  )
}

// Main export with Suspense
export default function SettingsPage() {
  // Mock user - in real implementation this would come from auth context
  const user = {
    id: 'mock-user-id',
    email: 'user@example.com',
    full_name: 'User Name',
  }

  return (
    <Suspense fallback={<SettingsLoading />}>
      <SettingsContent user={user} />
    </Suspense>
  )
}

// Import supabase for sync function
import { supabase } from '@/lib/supabase'
