'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { useToast } from '@/hooks/useToast'
import { createCheckoutSession, createPortalSession, getSubscriptionStatus, SubscriptionStatus } from '@/lib/stripe'
import { 
  Check, 
  X, 
  Loader2,
  Crown,
  Sparkles,
  Zap,
  ArrowRight,
  ExternalLink,
  AlertCircle
} from 'lucide-react'

interface SubscriptionModalProps {
  isOpen: boolean
  onClose: () => void
  currentTier?: 'free' | 'starter' | 'pro'
}

const plans = [
  {
    id: 'starter' as const,
    name: 'Starter',
    description: 'Perfect for content creators',
    price: { monthly: 19, yearly: 190 },
    features: [
      '100 content items/month',
      '10 projects',
      'Advanced AI generation',
      'All export formats',
      'Social media scheduling',
      'Priority support',
    ],
    popular: true,
  },
  {
    id: 'pro' as const,
    name: 'Pro',
    description: 'For growing teams',
    price: { monthly: 49, yearly: 490 },
    features: [
      'Unlimited content',
      'Unlimited projects',
      'Premium AI models',
      'Team collaboration',
      'Custom brand voice',
      'API access',
    ],
    popular: false,
  },
]

export default function SubscriptionModal({ isOpen, onClose, currentTier = 'free' }: SubscriptionModalProps) {
  const { showToast } = useToast()
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly')
  const [loading, setLoading] = useState<string | null>(null)
  const [subscription, setSubscription] = useState<SubscriptionStatus | null>(null)
  const [, setIsLoadingStatus] = useState(false)

  useEffect(() => {
    if (isOpen && currentTier !== 'free') {
      loadSubscriptionStatus()
    }
  }, [isOpen, currentTier])

  async function loadSubscriptionStatus() {
    setIsLoadingStatus(true)
    try {
      const status = await getSubscriptionStatus()
      setSubscription(status)
    } catch (error) {
      console.error('Failed to load subscription status:', error)
    } finally {
      setIsLoadingStatus(false)
    }
  }

  const handleSubscribe = async (planId: 'starter' | 'pro') => {
    try {
      setLoading(planId)
      const { url } = await createCheckoutSession({
        plan: planId,
        billingCycle,
        successUrl: `${window.location.origin}/settings?success=true`,
        cancelUrl: `${window.location.origin}/settings?canceled=true`,
      })
      
      window.location.href = url
    } catch (error: unknown) {
      console.error('Failed to create checkout:', error)
      const errorMessage = error instanceof Error ? error.message : 'Failed to start checkout'
      showToast(errorMessage, 'error')
    } finally {
      setLoading(null)
    }
  }

  const handleManageSubscription = async () => {
    try {
      setLoading('manage')
      const { url } = await createPortalSession()
      window.open(url, '_blank')
    } catch (error: unknown) {
      console.error('Failed to open portal:', error)
      const errorMessage = error instanceof Error ? error.message : 'Failed to open billing portal'
      showToast(errorMessage, 'error')
    } finally {
      setLoading(null)
    }
  }

  const getYearlySavings = (monthly: number, yearly: number) => {
    const percentage = Math.round(((monthly * 12 - yearly) / (monthly * 12)) * 100)
    return percentage
  }

  const formatDate = (timestamp?: number) => {
    if (!timestamp) return ''
    return new Date(timestamp * 1000).toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    })
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between z-10">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Crown className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Upgrade Your Plan</h2>
              <p className="text-sm text-gray-500">Choose the plan that works for you</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Current Status */}
          {currentTier !== 'free' && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start gap-3">
                <Sparkles className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-blue-900">
                    You&apos;re currently on the <span className="capitalize">{currentTier}</span> plan
                  </p>
                  {subscription?.current_period_end && (
                    <p className="text-sm text-blue-700 mt-1">
                      Renews on {formatDate(subscription.current_period_end)}
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Billing Toggle */}
          <div className="flex items-center justify-center gap-4 mb-8">
            <span className={`text-sm font-medium ${billingCycle === 'monthly' ? 'text-gray-900' : 'text-gray-500'}`}>
              Monthly
            </span>
            <button
              onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
              className="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              style={{ backgroundColor: billingCycle === 'yearly' ? '#3b82f6' : '#e5e7eb' }}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  billingCycle === 'yearly' ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
            <span className={`text-sm font-medium ${billingCycle === 'yearly' ? 'text-gray-900' : 'text-gray-500'}`}>
              Yearly
            </span>
            {billingCycle === 'yearly' && (
              <span className="ml-2 px-2 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-full">
                Save 20%
              </span>
            )}
          </div>

          {/* Plan Cards */}
          <div className="grid md:grid-cols-2 gap-6">
            {plans.map((plan) => {
              const isCurrentPlan = currentTier === plan.id
              const isDowngrade = currentTier === 'pro' && plan.id === 'starter'
              
              return (
                <Card
                  key={plan.id}
                  className={`relative overflow-hidden ${
                    plan.popular && !isCurrentPlan
                      ? 'border-2 border-blue-500 shadow-lg'
                      : 'border border-gray-200'
                  } ${isCurrentPlan ? 'ring-2 ring-green-500' : ''}`}
                >
                  {plan.popular && !isCurrentPlan && (
                    <div className="absolute top-0 right-0 bg-blue-500 text-white text-xs font-semibold px-3 py-1 rounded-bl-lg">
                      Most Popular
                    </div>
                  )}
                  {isCurrentPlan && (
                    <div className="absolute top-0 right-0 bg-green-500 text-white text-xs font-semibold px-3 py-1 rounded-bl-lg">
                      Current Plan
                    </div>
                  )}
                  
                  <CardContent className="p-6">
                    <div className="mb-4">
                      <h3 className="text-xl font-bold text-gray-900">{plan.name}</h3>
                      <p className="text-sm text-gray-500 mt-1">{plan.description}</p>
                    </div>

                    <div className="mb-6">
                      <div className="flex items-baseline gap-1">
                        <span className="text-3xl font-bold text-gray-900">
                          ${billingCycle === 'monthly' ? plan.price.monthly : plan.price.yearly}
                        </span>
                        <span className="text-gray-500">/{billingCycle === 'monthly' ? 'mo' : 'yr'}</span>
                      </div>
                      {billingCycle === 'yearly' && (
                        <p className="text-sm text-green-600 mt-1">
                          Save {getYearlySavings(plan.price.monthly, plan.price.yearly)}%
                        </p>
                      )}
                    </div>

                    <ul className="space-y-2 mb-6">
                      {plan.features.map((feature, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <Check className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                          <span className="text-sm text-gray-600">{feature}</span>
                        </li>
                      ))}
                    </ul>

                    {isCurrentPlan ? (
                      <Button
                        variant="outline"
                        className="w-full border-green-500 text-green-700 hover:bg-green-50"
                        disabled
                      >
                        <Check className="h-4 w-4 mr-2" />
                        Current Plan
                      </Button>
                    ) : isDowngrade ? (
                      <Button
                        variant="outline"
                        onClick={handleManageSubscription}
                        disabled={loading === 'manage'}
                        className="w-full"
                      >
                        {loading === 'manage' ? (
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        ) : (
                          <>
                            <ExternalLink className="h-4 w-4 mr-2" />
                            Manage in Portal
                          </>
                        )}
                      </Button>
                    ) : (
                      <Button
                        onClick={() => handleSubscribe(plan.id)}
                        disabled={loading === plan.id}
                        className={`w-full ${
                          plan.popular
                            ? 'bg-blue-600 hover:bg-blue-700 text-white'
                            : ''
                        }`}
                      >
                        {loading === plan.id ? (
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        ) : (
                          <>
                            {currentTier === 'free' ? 'Upgrade' : 'Switch to'} {plan.name}
                            <ArrowRight className="h-4 w-4 ml-2" />
                          </>
                        )}
                      </Button>
                    )}
                  </CardContent>
                </Card>
              )
            })}
          </div>

          {/* Manage Subscription Link */}
          {currentTier !== 'free' && (
            <div className="mt-6 text-center">
              <button
                onClick={handleManageSubscription}
                disabled={loading === 'manage'}
                className="text-sm text-gray-600 hover:text-gray-900 flex items-center justify-center gap-1 mx-auto"
              >
                {loading === 'manage' ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    Manage subscription in Stripe Portal
                    <ExternalLink className="h-3 w-3" />
                  </>
                )}
              </button>
            </div>
          )}

          {/* Test Mode Notice */}
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-yellow-800">
              <p className="font-medium">Test Mode Active</p>
              <p className="mt-1">
                Use test card number <code className="bg-yellow-100 px-1 py-0.5 rounded">4242 4242 4242 4242</code> with any future date and CVC.
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 px-6 py-4 bg-gray-50 flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Zap className="h-4 w-4" />
            <span>14-day free trial • Cancel anytime</span>
          </div>
          <button
            onClick={onClose}
            className="text-sm text-gray-600 hover:text-gray-900"
          >
            Maybe later
          </button>
        </div>
      </div>
    </div>
  )
}
