'use client'

import { X, FlaskConical } from 'lucide-react'
import { useState, useEffect } from 'react'

/**
 * Staging environment banner.
 * 
 * Shows a dismissible "STAGING" badge at the top of every page
 * when NEXT_PUBLIC_APP_ENV=staging.
 * Hidden entirely in production.
 */
export function StagingBanner() {
  const [dismissed, setDismissed] = useState(false)
  const [isStaging, setIsStaging] = useState(false)

  useEffect(() => {
    setIsStaging(
      (process.env.NEXT_PUBLIC_APP_ENV || 'production') === 'staging'
    )

    // Check if user previously dismissed (session only)
    if (sessionStorage.getItem('staging-banner-dismissed') === 'true') {
      setDismissed(true)
    }
  }, [])

  if (!isStaging || dismissed) return null

  const handleDismiss = () => {
    setDismissed(true)
    sessionStorage.setItem('staging-banner-dismissed', 'true')
  }

  return (
    <div className="fixed top-0 left-0 right-0 z-[9999] bg-amber-500 text-amber-950 px-4 py-1.5 flex items-center justify-center gap-2 text-sm font-medium shadow-md">
      <FlaskConical className="w-4 h-4" />
      <span>
        <strong>STAGING</strong> — This is a test environment. Data may be reset at any time.
      </span>
      <button
        onClick={handleDismiss}
        className="absolute right-2 top-1/2 -translate-y-1/2 p-0.5 hover:bg-amber-600/30 rounded transition-colors"
        aria-label="Dismiss staging banner"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  )
}