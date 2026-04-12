'use client'

import { useOfflineBanner } from '@/hooks/useNetworkStatus'
import { Wifi, WifiOff, CloudOff, CheckCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function OfflineBanner() {
  const { showBanner, showReconnected, pendingActionsCount } = useOfflineBanner()

  if (!showBanner && !showReconnected) return null

  return (
    <div className="fixed top-0 left-0 right-0 z-[100]">
      {/* Offline Banner */}
      {showBanner && (
        <div
          className={cn(
            'flex items-center justify-center gap-2 px-4 py-2',
            'bg-amber-500 text-white shadow-lg',
            'animate-in slide-in-from-top duration-300'
          )}
        >
          <WifiOff className="h-4 w-4" />
          <span className="text-sm font-medium">
            You&apos;re offline. Changes will be saved locally.
          </span>
          {pendingActionsCount > 0 && (
            <span className="ml-2 text-xs bg-amber-600 px-2 py-0.5 rounded-full">
              {pendingActionsCount} pending
            </span>
          )}
        </div>
      )}

      {/* Reconnected Banner */}
      {showReconnected && (
        <div
          className={cn(
            'flex items-center justify-center gap-2 px-4 py-2',
            'bg-green-500 text-white shadow-lg',
            'animate-in slide-in-from-top duration-300'
          )}
        >
          <CheckCircle className="h-4 w-4" />
          <span className="text-sm font-medium">
            Back online! Syncing your changes...
          </span>
        </div>
      )}
    </div>
  )
}

// Network status indicator for inline use
interface NetworkIndicatorProps {
  className?: string
  showLabel?: boolean
}

export function NetworkIndicator({ className, showLabel = false }: NetworkIndicatorProps) {
  const { isOnline } = useOfflineBanner()

  return (
    <div className={cn('flex items-center gap-1.5', className)}>
      {isOnline ? (
        <Wifi className="h-4 w-4 text-green-500" />
      ) : (
        <CloudOff className="h-4 w-4 text-amber-500" />
      )}
      {showLabel && (
        <span className={cn(
          'text-xs font-medium',
          isOnline ? 'text-green-600' : 'text-amber-600'
        )}>
          {isOnline ? 'Online' : 'Offline'}
        </span>
      )}
    </div>
  )
}
