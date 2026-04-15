'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Check, X, Zap, Crown, AlertCircle } from 'lucide-react'

interface UpgradeModalProps {
  isOpen: boolean
  onClose: () => void
  currentTier: string
}

interface PricingTier {
  name: string
  price: string
  description: string
  icon: React.ReactNode
  features: string[]
  highlighted?: boolean
  cta: string
}

const PRICING_TIERS: PricingTier[] = [
  {
    name: 'Free',
    price: '$0',
    description: 'Perfect for getting started',
    icon: <AlertCircle className="h-5 w-5 text-slate-500 dark:text-slate-400" />,
    features: [
      '10 content generations/month',
      'Basic text extraction',
      '1 project',
      'Email support',
    ],
    cta: 'Current Plan',
  },
  {
    name: 'Pro',
    price: '$29',
    description: 'Best for content creators',
    icon: <Zap className="h-5 w-5 text-blue-500" />,
    highlighted: true,
    features: [
      '100 content generations/month',
      'Advanced AI generation',
      'Unlimited projects',
      'Priority support',
      'Analytics dashboard',
    ],
    cta: 'Upgrade to Pro',
  },
  {
    name: 'Agency',
    price: '$99',
    description: 'For teams & agencies',
    icon: <Crown className="h-5 w-5 text-purple-500" />,
    features: [
      'Unlimited content generations',
      'Custom AI training',
      'Unlimited projects',
      'Priority support',
      'Advanced analytics',
      'Team collaboration',
      'API access',
    ],
    cta: 'Upgrade to Agency',
  },
]

export default function UpgradeModal({ isOpen, onClose, currentTier }: UpgradeModalProps) {
  const [loading, setLoading] = useState<string | null>(null)

  if (!isOpen) return null

  const handleUpgrade = async (tier: string) => {
    setLoading(tier)
    // TODO: Implement Stripe checkout integration
    // For now, just simulate a redirect
    setTimeout(() => {
      setLoading(null)
      // In production, redirect to Stripe checkout
      // Redirecting to checkout for ${tier} plan
      alert('Stripe checkout integration coming in Phase 2!')
    }, 1000)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="bg-slate-50 dark:bg-slate-900 rounded-2xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-slate-200 dark:border-slate-700 p-6 flex items-center justify-between z-10">
          <div>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Upgrade Your Plan</h2>
            <p className="text-slate-500 dark:text-slate-400 mt-1">
              Choose the plan that fits your content creation needs
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-100 dark:bg-slate-800 rounded-full transition-colors"
          >
            <X className="h-6 w-6 text-slate-500 dark:text-slate-400" />
          </button>
        </div>

        {/* Pricing cards */}
        <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
          {PRICING_TIERS.map((tier) => {
            const isCurrent = currentTier.toLowerCase() === tier.name.toLowerCase()
            const isLoading = loading === tier.name

            return (
              <Card
                key={tier.name}
                className={`flex flex-col ${
                  tier.highlighted
                    ? 'border-blue-500 border-2 shadow-lg'
                    : 'border-slate-200 dark:border-slate-700'
                } ${isCurrent ? 'opacity-75' : ''}`}
              >
                <CardHeader className="pb-4">
                  <div className="flex items-center gap-2 mb-2">
                    {tier.icon}
                    <CardTitle className="text-lg">{tier.name}</CardTitle>
                  </div>
                  <div className="flex items-baseline gap-1">
                    <span className="text-3xl font-bold">{tier.price}</span>
                    <span className="text-slate-500 dark:text-slate-400">/month</span>
                  </div>
                  <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">{tier.description}</p>
                </CardHeader>

                <CardContent className="flex-1 flex flex-col">
                  <ul className="space-y-3 mb-6 flex-1">
                    {tier.features.map((feature, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <Check className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-slate-600 dark:text-slate-400">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <Button
                    variant={tier.highlighted ? 'primary' : 'outline'}
                    className="w-full"
                    disabled={isCurrent || isLoading}
                    onClick={() => handleUpgrade(tier.name)}
                  >
                    {isLoading ? (
                      <span className="flex items-center gap-2">
                        <span className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
                        Loading...
                      </span>
                    ) : isCurrent ? (
                      'Current Plan'
                    ) : (
                      tier.cta
                    )}
                  </Button>
                </CardContent>
              </Card>
            )
          })}
        </div>

        {/* Footer */}
        <div className="border-t border-slate-200 dark:border-slate-700 p-6 bg-slate-50 dark:bg-slate-900 rounded-b-2xl">
          <p className="text-center text-sm text-slate-500 dark:text-slate-400">
            All plans include SSL security, automatic backups, and 99.9% uptime guarantee.
            <br />
            Questions?{' '}
            <a href="mailto:support@contentforge.ai" className="text-blue-600 hover:underline">
              Contact our sales team
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
