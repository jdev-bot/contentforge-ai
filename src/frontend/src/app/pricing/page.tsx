'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { useToast } from '@/hooks/useToast'
import { createCheckoutSession } from '@/lib/stripe'
import { 
  Check, 
  Sparkles, 
  Zap, 
  Loader2,
  ArrowLeft,
  Crown
} from 'lucide-react'
import Link from 'next/link'

const plans = [
  {
    id: 'free',
    name: 'Free',
    description: 'Get started with basic content repurposing',
    price: { monthly: 0, yearly: 0 },
    features: [
      '10 content items per month',
      '3 projects',
      'Basic AI generation',
      'Export to text formats',
      'Email support',
    ],
    cta: 'Get Started',
    popular: false,
  },
  {
    id: 'starter',
    name: 'Starter',
    description: 'Perfect for content creators and small teams',
    price: { monthly: 19, yearly: 190 },
    features: [
      '100 content items per month',
      '10 projects',
      'Advanced AI generation',
      'All export formats',
      'Social media scheduling',
      'Priority email support',
      'Analytics dashboard',
    ],
    cta: 'Start Free Trial',
    popular: true,
  },
  {
    id: 'pro',
    name: 'Pro',
    description: 'For growing teams with advanced needs',
    price: { monthly: 49, yearly: 490 },
    features: [
      'Unlimited content items',
      'Unlimited projects',
      'Premium AI models',
      'All export formats',
      'Social media scheduling',
      'Priority support (24h)',
      'Advanced analytics',
      'Team collaboration',
      'Custom brand voice',
      'API access',
    ],
    cta: 'Start Free Trial',
    popular: false,
  },
]

export default function PricingPage() {
  const router = useRouter()
  const { showToast } = useToast()
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly')
  const [loading, setLoading] = useState<string | null>(null)

  const handleSubscribe = async (planId: string) => {
    if (planId === 'free') {
      router.push('/login')
      return
    }

    try {
      setLoading(planId)
      const { url } = await createCheckoutSession({
        plan: planId as 'starter' | 'pro',
        billingCycle,
        successUrl: `${window.location.origin}/settings?success=true`,
        cancelUrl: `${window.location.origin}/pricing?canceled=true`,
      })
      
      // Redirect to Stripe Checkout
      window.location.href = url
    } catch (error: any) {
      console.error('Failed to create checkout:', error)
      showToast(error.message || 'Failed to start checkout. Please try again.', 'error')
    } finally {
      setLoading(null)
    }
  }

  const getYearlySavings = (monthly: number, yearly: number) => {
    const yearlyEquivalent = monthly * 12
    const savings = yearlyEquivalent - yearly
    const percentage = Math.round((savings / yearlyEquivalent) * 100)
    return percentage
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="h-8 w-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <span className="font-bold text-xl text-gray-900">ContentForge</span>
          </Link>
          <Link 
            href="/"
            className="flex items-center gap-1 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to home
          </Link>
        </div>
      </header>

      {/* Hero */}
      <div className="pt-16 pb-12 text-center px-4">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-50 text-blue-700 text-sm font-medium mb-6">
          <Crown className="h-4 w-4" />
          Simple, transparent pricing
        </div>
        <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
          Choose your plan
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
          Start free and scale as you grow. No hidden fees, cancel anytime.
        </p>

        {/* Billing Toggle */}
        <div className="flex items-center justify-center gap-4">
          <span className={`text-sm font-medium ${billingCycle === 'monthly' ? 'text-gray-900' : 'text-gray-500'}`}>
            Monthly
          </span>
          <button
            onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
            className="relative inline-flex h-6 w-11 items-center rounded-full bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            style={{ backgroundColor: billingCycle === 'yearly' ? '#3b82f6' : undefined }}
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
              Save up to 20%
            </span>
          )}
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
        <div className="grid md:grid-cols-3 gap-8">
          {plans.map((plan) => (
            <Card
              key={plan.id}
              className={`relative overflow-hidden ${
                plan.popular
                  ? 'border-2 border-blue-500 shadow-xl scale-105 z-10'
                  : 'border border-gray-200 hover:border-gray-300 hover:shadow-lg'
              } transition-all`}
            >
              {plan.popular && (
                <div className="absolute top-0 right-0 bg-blue-500 text-white text-xs font-semibold px-3 py-1 rounded-bl-lg">
                  Most Popular
                </div>
              )}
              <CardContent className="p-6 sm:p-8">
                <div className="mb-4">
                  <h3 className="text-xl font-bold text-gray-900">{plan.name}</h3>
                  <p className="text-sm text-gray-500 mt-1">{plan.description}</p>
                </div>

                <div className="mb-6">
                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl font-bold text-gray-900">
                      ${billingCycle === 'monthly' ? plan.price.monthly : plan.price.yearly}
                    </span>
                    <span className="text-gray-500">/{billingCycle === 'monthly' ? 'month' : 'year'}</span>
                  </div>
                  {billingCycle === 'yearly' && plan.price.monthly > 0 && (
                    <p className="text-sm text-green-600 mt-1">
                      Save {getYearlySavings(plan.price.monthly, plan.price.yearly)}%
                    </p>
                  )}
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-3">
                      <Check className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                      <span className="text-sm text-gray-600">{feature}</span>
                    </li>
                  ))}
                </ul>

                <Button
                  onClick={() => handleSubscribe(plan.id)}
                  disabled={loading === plan.id}
                  variant={plan.popular ? 'default' : 'outline'}
                  className={`w-full ${
                    plan.popular
                      ? 'bg-blue-600 hover:bg-blue-700 text-white'
                      : 'border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {loading === plan.id ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    plan.cta
                  )}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Trust Indicators */}
        <div className="mt-16 text-center">
          <p className="text-sm text-gray-500 mb-4">Trusted by content creators worldwide</p>
          <div className="flex items-center justify-center gap-8 text-gray-400">
            <div className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              <span className="text-sm font-medium">Instant Setup</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="h-5 w-5" />
              <span className="text-sm font-medium">No Credit Card Required</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="h-5 w-5" />
              <span className="text-sm font-medium">Cancel Anytime</span>
            </div>
          </div>
        </div>

        {/* FAQ */}
        <div className="mt-20 max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Frequently Asked Questions
          </h2>
          <div className="space-y-6">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-2">Can I change my plan later?</h3>
              <p className="text-gray-600 text-sm">
                Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.
              </p>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-2">Is there a free trial?</h3>
              <p className="text-gray-600 text-sm">
                Yes, both Starter and Pro plans come with a 14-day free trial. No credit card required.
              </p>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-2">What happens when I hit my limit?</h3>
              <p className="text-gray-600 text-sm">
                You'll be notified when you're close to your limit. You can upgrade anytime or wait until the next billing cycle.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-8">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-gray-500">
          <p>© 2025 ContentForge AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
