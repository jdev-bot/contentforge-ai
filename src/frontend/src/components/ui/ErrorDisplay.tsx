'use client'

import { AlertCircle, Info, CheckCircle, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { ReactNode } from 'react'

type ErrorVariant = 'error' | 'warning' | 'info' | 'success'

interface ErrorDisplayProps {
  title?: string
  message: string | ReactNode
  variant?: ErrorVariant
  onDismiss?: () => void
  className?: string
  actions?: ReactNode
}

const variantConfig = {
  error: {
    bg: 'bg-red-50',
    border: 'border-red-200',
    icon: AlertCircle,
    iconColor: 'text-red-500',
    titleColor: 'text-red-800',
    textColor: 'text-red-600',
  },
  warning: {
    bg: 'bg-yellow-50',
    border: 'border-yellow-200',
    icon: AlertCircle,
    iconColor: 'text-yellow-500',
    titleColor: 'text-yellow-800',
    textColor: 'text-yellow-600',
  },
  info: {
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    icon: Info,
    iconColor: 'text-blue-500',
    titleColor: 'text-blue-800',
    textColor: 'text-blue-600',
  },
  success: {
    bg: 'bg-green-50',
    border: 'border-green-200',
    icon: CheckCircle,
    iconColor: 'text-green-500',
    titleColor: 'text-green-800',
    textColor: 'text-green-600',
  },
}

export function ErrorDisplay({
  title,
  message,
  variant = 'error',
  onDismiss,
  className,
  actions,
}: ErrorDisplayProps) {
  const config = variantConfig[variant]
  const Icon = config.icon

  return (
    <div
      role="alert"
      className={cn(
        'rounded-lg border p-4',
        config.bg,
        config.border,
        className
      )}
    >
      <div className="flex gap-3">
        <Icon className={cn('h-5 w-5 flex-shrink-0 mt-0.5', config.iconColor)} />
        
        <div className="flex-1 min-w-0">
          {title && (
            <h3 className={cn('font-semibold text-sm', config.titleColor)}>
              {title}
            </h3>
          )}
          <div className={cn('text-sm', config.textColor, title && 'mt-1')} >
            {message}
          </div>
          
          {actions && (
            <div className="mt-3 flex gap-2">{actions}</div>
          )}
        </div>
        
        {onDismiss && (
          <button
            type="button"
            onClick={onDismiss}
            className={cn(
              'flex-shrink-0 -mr-1 -mt-1 p-1 rounded-lg',
              'hover:bg-black/5 transition-colors',
              'focus:outline-none focus:ring-2 focus:ring-offset-0',
              config.textColor
            )}
            aria-label="Dismiss"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  )
}

// Inline error for forms
export function FormError({ message, className }: { message?: string; className?: string }) {
  if (!message) return null

  return (
    <div 
      role="alert"
      className={cn(
        'flex items-center gap-1.5 text-sm text-red-600 mt-1',
        'animate-in fade-in slide-in-from-top-1',
        className
      )}
    >
      <AlertCircle className="h-3.5 w-3.5 flex-shrink-0" />
      <span>{message}</span>
    </div>
  )
}

// Error boundary fallback
export function ErrorFallback({ 
  error, 
  resetError 
}: { 
  error: Error; 
  resetError?: () => void 
}) {
  return (
    <div className="min-h-[400px] flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <ErrorDisplay
          title="Something went wrong"
          message={
            <div className="space-y-2">
              <p>{error.message}</p>
              {process.env.NODE_ENV === 'development' && error.stack && (
                <pre className="text-xs bg-red-100/50 p-2 rounded overflow-auto max-h-32">
                  {error.stack}
                </pre>
              )}
            </div>
          }
          variant="error"
          actions={
            resetError && (
              <button
                onClick={resetError}
                className="px-3 py-1.5 text-sm font-medium text-red-700 bg-white border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
              >
                Try Again
              </button>
            )
          }
        />
      </div>
    </div>
  )
}
