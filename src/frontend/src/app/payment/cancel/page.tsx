'use client'

import { useEffect, useState, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { XCircle, ArrowLeft, CreditCard } from 'lucide-react'
import Link from 'next/link'

function PaymentCancelContent() {
  const searchParams = useSearchParams()
  const [countdown, setCountdown] = useState(5)
  const [autoRedirect, setAutoRedirect] = useState(true)

  useEffect(() => {
    // Check if there's a session_id - if not, it was cancelled before checkout
    const sessionId = searchParams.get('session_id')
    if (!sessionId) {
      setAutoRedirect(false)
    }
  }, [searchParams])

  useEffect(() => {
    if (!autoRedirect) return

    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          window.location.href = '/pricing'
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [autoRedirect])

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardContent className="p-8 text-center">
          <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <XCircle className="h-10 w-10 text-yellow-600" />
          </div>
          
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Payment Canceled</h1>
          
          <p className="text-gray-600 mb-6">
            Your payment was not completed. No charges were made to your account.
          </p>
          
          <div className="space-y-3">
            <Link href="/pricing">
              <Button className="w-full">
                <CreditCard className="h-4 w-4 mr-2" />
                Try Again
              </Button>
            </Link>
            
            <Link href="/">
              <Button variant="outline" className="w-full">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Home
              </Button>
            </Link>
          </div>
          
          {autoRedirect && (
            <p className="text-sm text-gray-500 mt-6">
              Redirecting to pricing in {countdown} seconds...
            </p>
          )}
          
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-700">
              <strong>Need help?</strong> If you&apos;re experiencing issues with payment, please contact our support team.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default function PaymentCancelPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardContent className="p-8 text-center">
            <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <XCircle className="h-10 w-10 text-yellow-600" />
            </div>
            
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Payment Canceled</h1>
            
            <p className="text-gray-600 mb-6">
              Your payment was not completed. No charges were made to your account.
            </p>
          </CardContent>
        </Card>
      </div>
    }>
      <PaymentCancelContent />
    </Suspense>
  )
}
