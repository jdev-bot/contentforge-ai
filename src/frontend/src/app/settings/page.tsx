'use client'

import { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { getUserProfile, updateUserProfile, getUsageSummary, UserProfile, UsageStats } from '@/lib/api'
import { getSubscriptionStatus, createPortalSession, SubscriptionStatus, getStripeConfig } from '@/lib/stripe'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { Badge, PlanBadge } from '@/components/ui/Badge'
import { Avatar } from '@/components/ui/Avatar'
import { Tooltip } from '@/components/ui/Tooltip'
import { useToast } from '@/hooks/useToast'
import SubscriptionModal from '@/components/SubscriptionModal'
import { 
  User, 
  Key, 
  CreditCard, 
  CheckCircle, 
  Copy,
  ExternalLink,
  AlertTriangle,
  Settings,
  Bell,
  Shield,
  Palette,
  Moon,
  Sun,
  Monitor,
  Upload,
  LogOut,
  Sparkles
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface SettingsTabProps {
  user: {
    id: string
    email: string
    full_name?: string
  }
}

type SettingsTab = 'profile' | 'account' | 'billing' | 'notifications' | 'security' | 'appearance'

// Profile Tab Component
function ProfileTab({ user, profile, loading, onSave }: { 
  user: SettingsTabProps['user']
  profile: UserProfile | null
  loading: boolean
  onSave: (data: { full_name: string }) => Promise<void>
}) {
  const [fullName, setFullName] = useState(profile?.full_name || '')
  const [saving, setSaving] = useState(false)
  const { showToast } = useToast()
  const originalName = profile?.full_name || ''
  const hasChanges = fullName !== originalName

  const handleSave = async () => {
    if (!hasChanges) return
    try {
      setSaving(true)
      await onSave({ full_name: fullName })
      showToast('Profile updated successfully', 'success')
    } catch (_error) {
      showToast('Failed to update profile', 'error')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton variant="card" className="h-48" />
        <Skeleton variant="card" className="h-32" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Profile Header */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row items-center gap-6">
            <div className="relative">
              <Avatar
                name={fullName || user.email}
                size="xl"
                className="ring-4 ring-blue-100 dark:ring-blue-900/30"
              />
              <button className="absolute -bottom-1 -right-1 p-2 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-colors">
                <Upload className="h-4 w-4" />
              </button>
            </div>
            
            <div className="text-center sm:text-left flex-1">
              <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100">
                {fullName || user.email.split('@')[0]}
              </h3>
              <p className="text-slate-500 dark:text-slate-400">{user.email}</p>
              <div className="flex items-center justify-center sm:justify-start gap-2 mt-2">
                <PlanBadge plan={(profile?.subscription_tier || 'free') as 'free' | 'starter' | 'pro' | 'enterprise'} />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Profile Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5 text-blue-600" />
            Personal Information
          </CardTitle>
          <CardDescription>Update your personal details</CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <Input
              label="Full Name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="John Doe"
            />
            
            <Input
              label="Email Address"
              value={user.email}
              disabled
              helperText="Contact support to change your email"
            />
          </div>
          
          <div className="flex justify-end pt-4 border-t border-slate-100 dark:border-slate-700">
            <Button
              onClick={handleSave}
              disabled={!hasChanges || saving}
              loading={saving}
              leftIcon={saving ? undefined : <CheckCircle className="h-4 w-4" />}
            >
              Save Changes
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Bio Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5 text-violet-600" />
            Bio
          </CardTitle>
        </CardHeader>
        
        <CardContent>
          <textarea
            className="w-full min-h-[100px] p-4 rounded-xl border-2 border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all resize-none"
            placeholder="Tell us about yourself..."
          />
          <p className="text-xs text-slate-500 mt-2">Maximum 500 characters</p>
        </CardContent>
      </Card>
    </div>
  )
}

// Account Tab Component
function AccountTab({ user: _user }: { user: SettingsTabProps['user'] }) {
  const { showToast } = useToast()

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Key className="h-5 w-5 text-amber-600" />
            API Keys
          </CardTitle>
          <CardDescription>Manage your API keys for integrations</CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {[
            { name: 'Stripe Publishable Key', value: 'pk_live_•••••••••••••••••••••••••••••••••', type: 'publishable' },
            { name: 'Groq API Key', value: 'gsk_•••••••••••••••••••••••••••••••••', type: 'secret' },
          ].map((key) => (
            <div key={key.name} className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-slate-900 dark:text-slate-100">{key.name}</span>
                <Badge variant="secondary" size="sm">{key.type}</Badge>
              </div>
              <div className="flex gap-2">
                <code className="flex-1 p-3 bg-white dark:bg-slate-900 rounded-lg font-mono text-sm text-slate-600 dark:text-slate-400 break-all">
                  {key.value}
                </code>
                <Tooltip content="Copy to clipboard">
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => {
                      navigator.clipboard.writeText(key.value)
                      showToast('Copied to clipboard', 'success')
                    }}
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                </Tooltip>
              </div>
            </div>
          ))}
          
          <div className="p-4 rounded-xl bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
            <p className="text-sm text-blue-800 dark:text-blue-200">
              <strong>Note:</strong> These keys are read-only. To update them, modify your environment variables or contact support.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="border-rose-200 dark:border-rose-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-rose-600">
            <AlertTriangle className="h-5 w-5" />
            Danger Zone
          </CardTitle>
          <CardDescription>Irreversible actions for your account</CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-4 rounded-xl bg-rose-50 dark:bg-rose-900/20">
            <div>
              <h4 className="font-medium text-rose-900 dark:text-rose-100">Delete Account</h4>
              <p className="text-sm text-rose-700 dark:text-rose-300">Permanently delete your account and all data</p>
            </div>
            <Button variant="danger">Delete Account</Button>
          </div>
          
          <div className="flex items-center justify-between p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50">
            <div>
              <h4 className="font-medium text-slate-900 dark:text-slate-100">Sign Out</h4>
              <p className="text-sm text-slate-600 dark:text-slate-400">Sign out from all devices</p>
            </div>
            <Button variant="outline" leftIcon={<LogOut className="h-4 w-4" />}>
              Sign Out
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Billing Tab Component
function BillingTab({ 
  profile, 
  subscription, 
  usageStats, 
  stripeConfig,
  loading,
  onManageBilling,
  onSync,
  onUpgrade
}: {
  profile: UserProfile | null
  subscription: SubscriptionStatus | null
  usageStats: UsageStats | null
  stripeConfig: { is_configured: boolean; test_mode: boolean } | null
  loading: boolean
  onManageBilling: () => Promise<void>
  onSync: () => Promise<void>
  onUpgrade: () => void
}) {
  const { showToast: _showToast } = useToast()
  const [portalLoading, setPortalLoading] = useState(false)
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [syncLoading, setSyncLoading] = useState(false)
  const currentTier = (profile?.subscription_tier || 'free') as 'free' | 'starter' | 'pro'

  const formatDate = (timestamp?: number | string) => {
    if (!timestamp) return 'N/A'
    const date = typeof timestamp === 'number' ? new Date(timestamp * 1000) : new Date(timestamp)
    return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
  }

  const handleManageBilling = async () => {
    setPortalLoading(true)
    await onManageBilling()
    setPortalLoading(false)
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleSync = async () => {
    setSyncLoading(true)
    await onSync()
    setSyncLoading(false)
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton variant="card" className="h-64" />
        <Skeleton variant="card" className="h-48" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Current Plan */}
      <Card className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-violet-500/5" />
        
        <CardHeader className="relative">
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5 text-blue-600" />
            Current Plan
          </CardTitle>
        </CardHeader>
        
        <CardContent className="relative space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h3 className="text-2xl font-bold text-slate-900 dark:text-slate-100 capitalize">
                  {profile?.subscription_tier || 'Free'}
                </h3>
                <Badge 
                  variant={subscription?.status === 'active' ? 'success' : 'default'}
                  dot
                >
                  {subscription?.status || 'Inactive'}
                </Badge>
              </div>
              
              {subscription?.current_period_end && (
                <p className="text-slate-500 dark:text-slate-400">
                  Renews on {formatDate(subscription.current_period_end)}
                </p>
              )}
              
              {subscription?.cancel_at_period_end && (
                <p className="text-rose-600 mt-1">
                  Cancels at period end
                </p>
              )}
            </div>
            
            <div className="flex flex-wrap gap-2">
              {currentTier === 'free' ? (
                <Button onClick={onUpgrade} leftIcon={<Sparkles className="h-4 w-4" />}>
                  Upgrade Now
                </Button>
              ) : (
                <>
                  <Button
                    variant="outline"
                    onClick={handleManageBilling}
                    loading={portalLoading}
                    leftIcon={<ExternalLink className="h-4 w-4" />}
                  >
                    Manage Billing
                  </Button>
                  <Button
                    variant="ghost"
                    onClick={onUpgrade}
                  >
                    Change Plan
                  </Button>
                </>
              )}
            </div>
          </div>
          
          {/* Usage Bar */}
          <div className="pt-4 border-t border-slate-100 dark:border-slate-700">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-slate-600 dark:text-slate-400">Monthly Usage</span>
              <span className="font-medium text-slate-900 dark:text-slate-100">
                {usageStats?.monthly_usage_count || 0} / {usageStats?.monthly_usage_limit || 10}
              </span>
            </div>
            
            <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
              <div
                className={cn(
                  'h-full rounded-full transition-all duration-500',
                  (usageStats?.percentage_used || 0) > 80 ? 'bg-gradient-to-r from-rose-500 to-orange-500' :
                  (usageStats?.percentage_used || 0) > 50 ? 'bg-gradient-to-r from-amber-500 to-yellow-500' :
                  'bg-gradient-to-r from-blue-500 to-violet-500'
                )}
                style={{ width: `${Math.min(usageStats?.percentage_used || 0, 100)}%` }}
              />
            </div>
            
            <div className="flex justify-between mt-2 text-xs text-slate-500">
              <span>{usageStats?.percentage_used || 0}% used</span>
              <span>{usageStats?.remaining || 0} remaining</span>
            </div>
          </div>
          
          {/* Test Mode Notice */}
          {stripeConfig?.test_mode && (
            <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-amber-900 dark:text-amber-100">Test Mode Active</p>
                  <p className="text-sm text-amber-800 dark:text-amber-200 mt-1">
                    Use test card <code className="bg-amber-100 dark:bg-amber-900/50 px-1.5 py-0.5 rounded font-mono text-xs">4242 4242 4242 4242</code> with any future date and CVC.
                  </p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Billing History */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5 text-emerald-600" />
            Billing History
          </CardTitle>
        </CardHeader>
        
        <CardContent>
          <div className="text-center py-8 text-slate-500 dark:text-slate-400">
            <p>No billing history available</p>
            <p className="text-sm mt-1">Your invoices will appear here</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Settings Content Component
function SettingsContent({ user }: SettingsTabProps) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { showToast } = useToast()
  const [activeTab, setActiveTab] = useState<SettingsTab>('profile')
  const [loading, setLoading] = useState(true)
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [usageStats, setUsageStats] = useState<UsageStats | null>(null)
  const [subscription, setSubscription] = useState<SubscriptionStatus | null>(null)
  const [stripeConfig, setStripeConfig] = useState<{ is_configured: boolean; test_mode: boolean } | null>(null)
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false)

  const tabs: { id: SettingsTab; name: string; icon: typeof User; badge?: string }[] = [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'account', name: 'Account', icon: Key },
    { id: 'billing', name: 'Billing', icon: CreditCard },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'appearance', name: 'Appearance', icon: Palette },
  ]

  useEffect(() => {
    loadSettings()
    checkUrlParams()
    loadStripeConfig()
  }, [])

  function checkUrlParams() {
    const success = searchParams.get('success')
    const canceled = searchParams.get('canceled')
    
    if (success) {
      showToast('Payment successful! Your subscription is now active.', 'success')
      router.replace('/settings')
    }
    if (canceled) {
      showToast('Payment was canceled. Your subscription was not changed.', 'error')
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

  const handleSaveProfile = async (data: { full_name: string }) => {
    const updated = await updateUserProfile(data)
    setProfile(updated)
    return Promise.resolve()
  }

  const handleManageBilling = async () => {
    const { url } = await createPortalSession()
    window.open(url, '_blank')
  }

  const handleSyncSubscription = async () => {
    await loadSettings()
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return (
          <ProfileTab
            user={user}
            profile={profile}
            loading={loading}
            onSave={handleSaveProfile}
          />
        )
      case 'account':
        return <AccountTab user={user} />
      case 'billing':
        return (
          <BillingTab
            profile={profile}
            subscription={subscription}
            usageStats={usageStats}
            stripeConfig={stripeConfig}
            loading={loading}
            onManageBilling={handleManageBilling}
            onSync={handleSyncSubscription}
            onUpgrade={() => setShowSubscriptionModal(true)}
          />
        )
      case 'notifications':
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5 text-amber-600" />
                Notification Preferences
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { label: 'Email notifications', desc: 'Receive updates about your content' },
                  { label: 'Marketing emails', desc: 'Receive tips and product updates' },
                  { label: 'Team invitations', desc: 'Get notified when invited to teams' },
                  { label: 'Usage alerts', desc: 'Get notified when approaching limits' },
                ].map((item) => (
                  <div key={item.label} className="flex items-center justify-between p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50">
                    <div>
                      <h4 className="font-medium text-slate-900 dark:text-slate-100">{item.label}</h4>
                      <p className="text-sm text-slate-500 dark:text-slate-400">{item.desc}</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" />
                      <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-slate-600 peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )
      case 'security':
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-emerald-600" />
                  Security Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50">
                  <div>
                    <h4 className="font-medium text-slate-900 dark:text-slate-100">Two-Factor Authentication</h4>
                    <p className="text-sm text-slate-500 dark:text-slate-400">Add an extra layer of security</p>
                  </div>
                  <Badge variant="default">Not Enabled</Badge>
                </div>
                
                <div className="flex items-center justify-between p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50">
                  <div>
                    <h4 className="font-medium text-slate-900 dark:text-slate-100">Change Password</h4>
                    <p className="text-sm text-slate-500 dark:text-slate-400">Last changed 3 months ago</p>
                  </div>
                  <Button variant="outline">Change</Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )
      case 'appearance':
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5 text-violet-600" />
                Appearance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { id: 'light', name: 'Light', icon: Sun },
                  { id: 'dark', name: 'Dark', icon: Moon },
                  { id: 'system', name: 'System', icon: Monitor },
                ].map((theme) => (
                  <button
                    key={theme.id}
                    className="p-4 rounded-xl border-2 border-slate-200 dark:border-slate-700 hover:border-blue-500 dark:hover:border-blue-500 transition-colors text-center"
                  >
                    <theme.icon className="h-8 w-8 mx-auto mb-2 text-slate-600 dark:text-slate-400" />
                    <span className="text-sm font-medium text-slate-900 dark:text-slate-100">{theme.name}</span>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        )
      default:
        return null
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Settings</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">Manage your account preferences</p>
      </div>

      {/* Tabs Navigation */}
      <div className="border-b border-slate-200 dark:border-slate-700">
        <nav className="flex gap-1 overflow-x-auto scrollbar-hide">
          {tabs.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  'flex items-center gap-2 px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors relative',
                  isActive
                    ? 'text-blue-600 dark:text-blue-400'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100'
                )}
              >
                <Icon className="h-4 w-4" />
                {tab.name}
                {tab.badge && (
                  <Badge variant="primary" size="sm">{tab.badge}</Badge>
                )}
                {isActive && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600 dark:bg-blue-400" />
                )}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="animate-fadeIn">
        {renderTabContent()}
      </div>

      {/* Subscription Modal */}
      {showSubscriptionModal && (
        <SubscriptionModal
          isOpen={showSubscriptionModal}
          onClose={() => setShowSubscriptionModal(false)}
          currentTier={(profile?.subscription_tier as 'free' | 'starter' | 'pro') || 'free'}
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
      <div className="flex gap-2">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <Skeleton key={i} className="h-10 w-24" />
        ))}
      </div>
      <Skeleton variant="card" className="h-96" />
    </div>
  )
}

// Main export with Suspense
export default function SettingsPage() {
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

// Import supabase for sync function - kept for future use
// import { supabase } from '@/lib/supabase'
