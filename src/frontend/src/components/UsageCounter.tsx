'use client'

import { useState, useEffect } from 'react'
import { getUsageSummary, UsageSummary } from '@/lib/api'
import { useToast } from '@/hooks/useToast'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { AlertCircle, Zap, Crown, Infinity } from 'lucide-react'

interface UsageCounterProps {
  onUpgrade?: () => void
}

export default function UsageCounter({ onUpgrade }: UsageCounterProps) {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const _unused = useToast()
  const [usage, setUsage] = useState<UsageSummary | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadUsage()
  }, [])

  const loadUsage = async () => {
    try {
      setLoading(true)
      const data = await getUsageSummary()
      setUsage(data)
    } catch (error) {
      console.error('Failed to load usage:', error)
    } finally {
      setLoading(false)
    }
  }

  const getTierIcon = (tier: string) => {
    switch (tier.toLowerCase()) {
      case 'agency':
        return <Crown className="h-4 w-4 text-purple-600" />
      case 'pro':
        return <Zap className="h-4 w-4 text-blue-600" />
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const _getTierColor = (tier: string) => {
    switch (tier.toLowerCase()) {
      case 'agency':
        return 'bg-purple-50 text-purple-700 border-purple-200'
      case 'pro':
        return 'bg-blue-50 text-blue-700 border-blue-200'
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200'
    }
  }

  const getProgressBarColor = (percentage: number, remaining: number) => {
    if (remaining === -1) return 'bg-green-500' // Unlimited
    if (percentage >= 90) return 'bg-red-500'
    if (percentage >= 70) return 'bg-yellow-500'
    return 'bg-blue-500'
  }

  if (loading) {
    return (
      <Card className="border-gray-200">
        <CardContent className="p-4">
          <div className="animate-pulse space-y-2">
            <div className="h-4 w-24 bg-gray-200 rounded"></div>
            <div className="h-2 w-full bg-gray-200 rounded"></div>
            <div className="h-4 w-16 bg-gray-200 rounded"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!usage) {
    return null
  }

  const { stats } = usage
  const isUnlimited = stats.remaining === -1
  const isLimitReached = usage.status === 'limit_reached'
  const isApproachingLimit = !isUnlimited && stats.percentage_used >= 80

  return (
    <Card className={`border ${isLimitReached ? 'border-red-300 bg-red-50' : 'border-gray-200'}`}>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            {getTierIcon(stats.subscription_tier)}
            <span className="text-sm font-medium capitalize">
              {stats.subscription_tier} Plan
            </span>
          </div>
          {isLimitReached && (
            <span className="text-xs font-medium text-red-600 flex items-center gap-1">
              <AlertCircle className="h-3 w-3" />
              Limit Reached
            </span>
          )}
        </div>

        <div className="space-y-2">
          {/* Progress bar */}
          <div className="h-2 w-full bg-gray-200 rounded-full overflow-hidden">
            <div
              className={`h-full ${getProgressBarColor(stats.percentage_used, stats.remaining)} transition-all duration-500`}
              style={{
                width: isUnlimited ? '100%' : `${Math.min(stats.percentage_used, 100)}%`
              }}
            />
          </div>

          {/* Usage text */}
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">
              {isUnlimited ? (
                <span className="flex items-center gap-1">
                  <Infinity className="h-4 w-4" />
                  Unlimited usage
                </span>
              ) : (
                <>
                  <span className="font-semibold text-gray-900">{stats.monthly_usage_count}</span>
                  {' / '}
                  <span className="text-gray-600">{stats.monthly_usage_limit}</span>
                  {' '}used
                </>
              )}
            </span>
            {!isUnlimited && (
              <span className={`font-medium ${isApproachingLimit ? 'text-yellow-600' : 'text-gray-600'}`}>
                {stats.remaining} remaining
              </span>
            )}
          </div>
        </div>

        {/* Upgrade prompt */}
        {(isLimitReached || isApproachingLimit) && stats.subscription_tier !== 'agency' && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            {isLimitReached ? (
              <div className="text-center">
                <p className="text-sm text-red-600 mb-2">
                  You&apos;ve reached your monthly limit. Upgrade to continue creating content.
                </p>
                <Button
                  size="sm"
                  variant="primary"
                  onClick={onUpgrade}
                  className="w-full"
                >
                  Upgrade Plan
                </Button>
              </div>
            ) : (
              <div className="text-center">
                <p className="text-xs text-yellow-600 mb-2">
                  Approaching limit ({Math.round(stats.percentage_used)}% used)
                </p>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={onUpgrade}
                  className="w-full text-xs"
                >
                  Upgrade for More
                </Button>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
