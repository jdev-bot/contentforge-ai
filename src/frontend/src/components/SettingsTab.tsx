'use client'

import { useState, useEffect } from 'react'
import { getUserProfile, updateUserProfile, getUsageSummary, UserProfile, UsageStats } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { useToast } from '@/hooks/useToast'
import { 
  User, 
  Key, 
  CreditCard, 
  CheckCircle, 
  AlertCircle,
  Eye,
  EyeOff,
  Copy,
  Loader2
} from 'lucide-react'

interface SettingsTabProps {
  user: {
    id: string
    email: string
    full_name?: string
  }
}

export default function SettingsTab({ user }: SettingsTabProps) {
  const { showToast } = useToast()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [usageStats, setUsageStats] = useState<UsageStats | null>(null)
  
  // Form state
  const [fullName, setFullName] = useState('')
  const [originalFullName, setOriginalFullName] = useState('')
  
  // API Key visibility
  const [showStripeKey, setShowStripeKey] = useState(false)
  const [showGroqKey, setShowGroqKey] = useState(false)
  
  // Mock API keys (in production, these would be fetched from secure storage)
  const [apiKeys] = useState({
    stripe: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || 'pk_live_•••••••••••••••••••••••••••••••••',
    groq: process.env.NEXT_PUBLIC_GROQ_API_KEY || 'gsk_•••••••••••••••••••••••••••••••••',
  })

  useEffect(() => {
    loadSettings()
  }, [])

  async function loadSettings() {
    try {
      setLoading(true)
      const [profileData, usageData] = await Promise.all([
        getUserProfile(),
        getUsageSummary(),
      ])
      setProfile(profileData)
      setUsageStats(usageData.stats)
      
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

  return (
    <div className="space-y-6">
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

      {/* Usage Limit */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center">
              <CreditCard className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Subscription</h3>
              <p className="text-sm text-gray-500">Manage your plan and usage</p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Current Plan</p>
                <p className="text-lg font-semibold text-gray-900 capitalize">
                  {profile?.subscription_tier || 'Free'}
                </p>
              </div>
              <Button variant="outline">Upgrade</Button>
            </div>

            <div className="pt-4 border-t border-gray-200">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">Monthly Usage</span>
                <span className="font-medium">
                  {usageStats?.monthly_usage_count || 0} / {usageStats?.monthly_usage_limit || 100}
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
    </div>
  )
}
