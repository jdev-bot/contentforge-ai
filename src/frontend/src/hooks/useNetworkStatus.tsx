'use client'

import { useState, useEffect, useCallback, useRef } from 'react'

interface QueuedAction {
  id: string
  type: string
  payload: unknown
  timestamp: number
}

interface NetworkStatus {
  isOnline: boolean
  isOffline: boolean
  wasOffline: boolean
  pendingActions: QueuedAction[]
  queueAction: (type: string, payload: unknown) => void
  processQueue: () => void
  clearQueue: () => void
}

const QUEUE_KEY = 'contentforge_offline_queue'

export function useNetworkStatus(): NetworkStatus {
  const [isOnline, setIsOnline] = useState(typeof navigator !== 'undefined' ? navigator.onLine : true)
  const [wasOffline, setWasOffline] = useState(false)
  const [pendingActions, setPendingActions] = useState<QueuedAction[]>([])
  const processedRef = useRef<Set<string>>(new Set())

  // Load queued actions from localStorage on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        const stored = localStorage.getItem(QUEUE_KEY)
        if (stored) {
          const parsed = JSON.parse(stored)
          setPendingActions(parsed)
        }
      } catch (e) {
        console.error('Failed to load offline queue:', e)
      }
    }
  }, [])

  // Save queue to localStorage when it changes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        if (pendingActions.length > 0) {
          localStorage.setItem(QUEUE_KEY, JSON.stringify(pendingActions))
        } else {
          localStorage.removeItem(QUEUE_KEY)
        }
      } catch (e) {
        console.error('Failed to save offline queue:', e)
      }
    }
  }, [pendingActions])

  // Listen for online/offline events
  useEffect(() => {
    const handleOnline = () => {
      setWasOffline(!isOnline)
      setIsOnline(true)
      // Auto-process queue when coming back online
      setTimeout(() => processQueue(), 1000)
    }

    const handleOffline = () => {
      setIsOnline(false)
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [isOnline])

  const queueAction = useCallback((type: string, payload: unknown) => {
    const action: QueuedAction = {
      id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      payload,
      timestamp: Date.now(),
    }

    setPendingActions(prev => [...prev, action])
  }, [])

  const processQueue = useCallback(() => {
    if (!navigator.onLine) return

    const actionsToProcess = pendingActions.filter(a => !processedRef.current.has(a.id))
    
    if (actionsToProcess.length === 0) return

    // Mark actions as processed
    actionsToProcess.forEach(action => {
      processedRef.current.add(action.id)
    })

    // Dispatch a custom event for the application to handle
    const event = new CustomEvent('process-offline-queue', {
      detail: { actions: actionsToProcess }
    })
    window.dispatchEvent(event)

    // Clear processed actions after a delay
    setTimeout(() => {
      setPendingActions(prev => prev.filter(a => !processedRef.current.has(a.id)))
    }, 5000)
  }, [pendingActions])

  const clearQueue = useCallback(() => {
    processedRef.current.clear()
    setPendingActions([])
    if (typeof window !== 'undefined') {
      localStorage.removeItem(QUEUE_KEY)
    }
  }, [])

  return {
    isOnline,
    isOffline: !isOnline,
    wasOffline,
    pendingActions,
    queueAction,
    processQueue,
    clearQueue,
  }
}

// Offline banner component hook
export function useOfflineBanner() {
  const { isOnline, wasOffline, pendingActions } = useNetworkStatus()
  const [showBanner, setShowBanner] = useState(false)
  const [showReconnected, setShowReconnected] = useState(false)

  useEffect(() => {
    setShowBanner(!isOnline)
    
    if (wasOffline && isOnline) {
      setShowReconnected(true)
      const timer = setTimeout(() => setShowReconnected(false), 3000)
      return () => clearTimeout(timer)
    }
  }, [isOnline, wasOffline])

  return {
    showBanner,
    showReconnected,
    isOnline,
    pendingActionsCount: pendingActions.length,
  }
}
