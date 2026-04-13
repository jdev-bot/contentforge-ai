'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/Button'
import { X, Cookie, Settings2, Check } from 'lucide-react'

interface CookiePreferences {
  essential: boolean
  functional: boolean
  analytics: boolean
  marketing: boolean
}

const COOKIE_CONSENT_KEY = 'contentforge-cookie-consent'
const COOKIE_PREFERENCES_KEY = 'contentforge-cookie-preferences'

const defaultPreferences: CookiePreferences = {
  essential: true, // Always required
  functional: false,
  analytics: false,
  marketing: false,
}

export default function CookieConsent() {
  const [isVisible, setIsVisible] = useState(false)
  const [showPreferences, setShowPreferences] = useState(false)
  const [preferences, setPreferences] = useState<CookiePreferences>(defaultPreferences)
  const [isAnimating, setIsAnimating] = useState(false)

  useEffect(() => {
    // Check if user has already made a choice
    const hasConsent = localStorage.getItem(COOKIE_CONSENT_KEY)
    if (!hasConsent) {
      // Delay showing the banner slightly for better UX
      const timer = setTimeout(() => {
        setIsVisible(true)
        setIsAnimating(true)
      }, 1000)
      return () => clearTimeout(timer)
    }

    // Load saved preferences
    const savedPreferences = localStorage.getItem(COOKIE_PREFERENCES_KEY)
    if (savedPreferences) {
      setPreferences(JSON.parse(savedPreferences))
    }
  }, [])

  const savePreferences = (prefs: CookiePreferences) => {
    localStorage.setItem(COOKIE_PREFERENCES_KEY, JSON.stringify(prefs))
    localStorage.setItem(COOKIE_CONSENT_KEY, 'true')
    
    // Apply preferences
    applyCookiePreferences(prefs)
    
    setPreferences(prefs)
    closeBanner()
  }

  const applyCookiePreferences = (prefs: CookiePreferences) => {
    // Essential cookies are always set
    
    // Functional cookies
    if (prefs.functional) {
      document.documentElement.setAttribute('data-cookies-functional', 'true')
    } else {
      document.documentElement.removeAttribute('data-cookies-functional')
    }

    // Analytics cookies
    if (prefs.analytics) {
      document.documentElement.setAttribute('data-cookies-analytics', 'true')
      // Enable analytics scripts here if needed
    } else {
      document.documentElement.removeAttribute('data-cookies-analytics')
      // Disable analytics
    }

    // Marketing cookies
    if (prefs.marketing) {
      document.documentElement.setAttribute('data-cookies-marketing', 'true')
      // Enable marketing scripts here if needed
    } else {
      document.documentElement.removeAttribute('data-cookies-marketing')
      // Disable marketing scripts
    }
  }

  const handleAcceptAll = () => {
    const allAccepted: CookiePreferences = {
      essential: true,
      functional: true,
      analytics: true,
      marketing: true,
    }
    savePreferences(allAccepted)
  }

  const handleRejectNonEssential = () => {
    const onlyEssential: CookiePreferences = {
      essential: true,
      functional: false,
      analytics: false,
      marketing: false,
    }
    savePreferences(onlyEssential)
  }

  const handleSavePreferences = () => {
    savePreferences(preferences)
  }

  const closeBanner = () => {
    setIsAnimating(false)
    setTimeout(() => {
      setIsVisible(false)
      setShowPreferences(false)
    }, 300)
  }

  const togglePreference = (key: keyof CookiePreferences) => {
    if (key === 'essential') return // Cannot toggle essential
    setPreferences(prev => ({
      ...prev,
      [key]: !prev[key],
    }))
  }

  if (!isVisible) return null

  return (
    <>
      {/* Backdrop */}
      {showPreferences && (
        <div 
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 transition-opacity duration-300"
          onClick={() => setShowPreferences(false)}
        />
      )}

      {/* Main Banner */}
      {!showPreferences ? (
        <div
          className={`fixed bottom-0 left-0 right-0 z-50 transition-all duration-300 ease-out transform ${
            isAnimating ? 'translate-y-0 opacity-100' : 'translate-y-full opacity-0'
          }`}
        >
          <div className="bg-white dark:bg-slate-800 border-t border-slate-200 dark:border-slate-700 shadow-2xl">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
              <div className="flex flex-col lg:flex-row items-start lg:items-center gap-4 lg:gap-6">
                {/* Icon and Text */}
                <div className="flex items-start gap-4 flex-1">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                    <Cookie className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-1">
                      We value your privacy
                    </h3>
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      We use cookies to enhance your browsing experience, serve personalized content, 
                      and analyze our traffic. By clicking &quot;Accept All&quot;, you consent to our use of cookies.{' '}
                      <a 
                        href="/legal/cookies" 
                        className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Learn more
                      </a>
                    </p>
                  </div>
                </div>

                {/* Buttons */}
                <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowPreferences(true)}
                    leftIcon={<Settings2 className="w-4 h-4" />}
                    className="flex-1 lg:flex-none"
                  >
                    Manage
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleRejectNonEssential}
                    className="flex-1 lg:flex-none"
                  >
                    Reject All
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={handleAcceptAll}
                    leftIcon={<Check className="w-4 h-4" />}
                    className="flex-1 lg:flex-none"
                  >
                    Accept All
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Preferences Modal */
        <div
          className={`fixed inset-x-4 bottom-4 sm:inset-auto sm:bottom-auto sm:top-1/2 sm:left-1/2 sm:-translate-x-1/2 sm:-translate-y-1/2 z-[60] w-auto sm:w-full sm:max-w-lg transition-all duration-300 ease-out transform ${
            isAnimating ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
          }`}
        >
          <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
            {/* Header */}
            <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                  <Cookie className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                  Cookie Preferences
                </h3>
              </div>
              <button
                onClick={() => setShowPreferences(false)}
                className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-full transition-colors"
              >
                <X className="w-5 h-5 text-slate-500 dark:text-slate-400" />
              </button>
            </div>

            {/* Cookie Types */}
            <div className="px-6 py-4 space-y-4 max-h-[60vh] overflow-y-auto">
              {/* Essential */}
              <div className="flex items-start justify-between gap-4 p-4 bg-slate-50 dark:bg-slate-900/50 rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-slate-900 dark:text-slate-100">Essential</span>
                    <span className="px-2 py-0.5 text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full">
                      Required
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    These cookies are necessary for the website to function and cannot be switched off.
                  </p>
                </div>
                <div className="relative inline-flex h-6 w-11 items-center rounded-full bg-blue-600 cursor-not-allowed">
                  <span className="inline-block h-4 w-4 translate-x-6 rounded-full bg-white transition-transform" />
                </div>
              </div>

              {/* Functional */}
              <div className="flex items-start justify-between gap-4 p-4 hover:bg-slate-50 dark:hover:bg-slate-900/50 rounded-lg transition-colors cursor-pointer"
                onClick={() => togglePreference('functional')}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-slate-900 dark:text-slate-100">Functional</span>
                  </div>
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    Enable enhanced functionality and personalization, such as remembering your preferences.
                  </p>
                </div>
                <div 
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors cursor-pointer ${
                    preferences.functional ? 'bg-blue-600' : 'bg-slate-300 dark:bg-slate-600'
                  }`}
                >
                  <span 
                    className={`inline-block h-4 w-4 rounded-full bg-white transition-transform ${
                      preferences.functional ? 'translate-x-6' : 'translate-x-1'
                    }`} 
                  />
                </div>
              </div>

              {/* Analytics */}
              <div className="flex items-start justify-between gap-4 p-4 hover:bg-slate-50 dark:hover:bg-slate-900/50 rounded-lg transition-colors cursor-pointer"
                onClick={() => togglePreference('analytics')}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-slate-900 dark:text-slate-100">Analytics</span>
                  </div>
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    Help us understand how visitors interact with our website by collecting anonymous data.
                  </p>
                </div>
                <div 
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors cursor-pointer ${
                    preferences.analytics ? 'bg-blue-600' : 'bg-slate-300 dark:bg-slate-600'
                  }`}
                >
                  <span 
                    className={`inline-block h-4 w-4 rounded-full bg-white transition-transform ${
                      preferences.analytics ? 'translate-x-6' : 'translate-x-1'
                    }`} 
                  />
                </div>
              </div>

              {/* Marketing */}
              <div className="flex items-start justify-between gap-4 p-4 hover:bg-slate-50 dark:hover:bg-slate-900/50 rounded-lg transition-colors cursor-pointer"
                onClick={() => togglePreference('marketing')}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-slate-900 dark:text-slate-100">Marketing</span>
                  </div>
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    Used to deliver relevant advertisements and measure their effectiveness.
                  </p>
                </div>
                <div 
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors cursor-pointer ${
                    preferences.marketing ? 'bg-blue-600' : 'bg-slate-300 dark:bg-slate-600'
                  }`}
                >
                  <span 
                    className={`inline-block h-4 w-4 rounded-full bg-white transition-transform ${
                      preferences.marketing ? 'translate-x-6' : 'translate-x-1'
                    }`} 
                  />
                </div>
              </div>
            </div>

            {/* Footer Actions */}
            <div className="px-6 py-4 border-t border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 flex flex-col sm:flex-row gap-3">
              <Button
                variant="outline"
                onClick={handleRejectNonEssential}
                className="flex-1"
              >
                Reject All
              </Button>
              <Button
                variant="primary"
                onClick={handleSavePreferences}
                className="flex-1"
              >
                Save Preferences
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

// Export helper function to check if cookies are accepted
export function areCookiesAccepted(type: keyof CookiePreferences): boolean {
  if (typeof window === 'undefined') return false
  
  const preferences = localStorage.getItem(COOKIE_PREFERENCES_KEY)
  if (!preferences) return false
  
  const prefs: CookiePreferences = JSON.parse(preferences)
  return prefs[type] || false
}

// Export function to manually show cookie banner
export function showCookieBanner(): void {
  localStorage.removeItem(COOKIE_CONSENT_KEY)
  window.location.reload()
}
