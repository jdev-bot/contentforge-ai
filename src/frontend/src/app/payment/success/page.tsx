'use client'

import { useEffect, useState, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { CheckCircle, Loader2, ArrowRight } from 'lucide-react'
import Link from 'next/link'

interface SubscriptionDetails {
  plan?: string
  status?: string
}

function PaymentSuccessContent() {
  const searchParams = useSearchParams()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [subscriptionDetails, setSubscriptionDetails] = useState<SubscriptionDetails | null>(null)

  useEffect(() => {
    verifyPayment()
  }, [searchParams])

  async function verifyPayment() {
    try {
      // Get session_id from URL if present
      const sessionId = searchParams.get('session_id')
      
      // Wait a moment for webhook to process
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Fetch subscription status to confirm
      const response = await fetch('/api/stripe/subscription', {
        credentials: 'include',
      })
      
      if (!response.ok) {
        throw new Error('Failed to verify subscription')
      }
      
      const data = await response.json()
      setSubscriptionDetails(data)
      setLoading(false)
    } catch {
      setError('Your payment was successful, but there was an issue loading your subscription details. Please check your account in a moment.')
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardContent className="p-8 text-center">
            <Loader2 className="h-12 w-12 text-blue-600 animate-spin mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Processing Payment</h1>
            <p className="text-gray-600">Please wait while we confirm your subscription...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardContent className="p-8 text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="h-10 w-10 text-green-600" />
          </div>
          
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Payment Successful!</h1>
          
          {error ? (
            <p className="text-yellow-700 mb-6">{error}</p>
          ) : (
            <p className="text-gray-600 mb-6">
              Thank you for subscribing to ContentForge {subscriptionDetails?.plan || 'Pro'}!
              Your subscription is now active.
            </p>
          )}
          
          <div className="space-y-3">
            <Link href="/dashboard">
              <Button className="w-full">
                Go to Dashboard
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </Link>
            
            <Link href="/settings">
              <Button variant="outline" className="w-full">
                Manage Subscription
              </Button>
            </Link>
          </div>
          
          <p className="text-sm text-gray-500 mt-6">
            You will receive a confirmation email shortly.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

export default function PaymentSuccessPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardContent className="p-8 text-center">
            <Loader2 className="h-12 w-12 text-blue-600 animate-spin mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Processing Payment</h1>
            <p className="text-gray-600">Please wait while we confirm your subscription...</p>
          </CardContent>
        </Card>
      </div>
    }>
      <PaymentSuccessContent />
    </Suspense>
  )
}
