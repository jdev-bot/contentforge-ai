'use client'

import { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import { X, CheckCircle, AlertCircle, Info, Loader2, AlertTriangle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'

type ToastType = 'success' | 'error' | 'info' | 'loading' | 'warning'

interface Toast {
  id: string
  message: string
  type: ToastType
  duration?: number
  action?: {
    label: string
    onClick: () => void
  }
}

interface ToastContextType {
  showToast: (message: string, type?: ToastType, duration?: number) => void
  showToastWithAction: (message: string, action: { label: string; onClick: () => void }, type?: ToastType) => void
  dismissToast: (id: string) => void
}

const ToastContext = createContext<ToastContextType | undefined>(undefined)

const typeConfig = {
  success: {
    bg: 'bg-emerald-50 dark:bg-emerald-900/20',
    border: 'border-emerald-200 dark:border-emerald-800',
    text: 'text-emerald-900 dark:text-emerald-100',
    icon: CheckCircle,
    iconColor: 'text-emerald-600 dark:text-emerald-400',
    title: 'Success',
  },
  error: {
    bg: 'bg-rose-50 dark:bg-rose-900/20',
    border: 'border-rose-200 dark:border-rose-800',
    text: 'text-rose-900 dark:text-rose-100',
    icon: AlertCircle,
    iconColor: 'text-rose-600 dark:text-rose-400',
    title: 'Error',
  },
  warning: {
    bg: 'bg-amber-50 dark:bg-amber-900/20',
    border: 'border-amber-200 dark:border-amber-800',
    text: 'text-amber-900 dark:text-amber-100',
    icon: AlertTriangle,
    iconColor: 'text-amber-600 dark:text-amber-400',
    title: 'Warning',
  },
  info: {
    bg: 'bg-blue-50 dark:bg-blue-900/20',
    border: 'border-blue-200 dark:border-blue-800',
    text: 'text-blue-900 dark:text-blue-100',
    icon: Info,
    iconColor: 'text-blue-600 dark:text-blue-400',
    title: 'Info',
  },
  loading: {
    bg: 'bg-slate-50 dark:bg-slate-800',
    border: 'border-slate-200 dark:border-slate-700',
    text: 'text-slate-900 dark:text-slate-100',
    icon: Loader2,
    iconColor: 'text-slate-600 dark:text-slate-400',
    title: 'Loading',
  },
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const showToast = useCallback((message: string, type: ToastType = 'info', duration = 5000) => {
    const id = Math.random().toString(36).substring(2, 9)
    setToasts((prev) => [...prev, { id, message, type, duration }])

    // Auto-dismiss for non-loading toasts
    if (type !== 'loading') {
      setTimeout(() => {
        dismissToast(id)
      }, duration)
    }
  }, [dismissToast])

  const showToastWithAction = useCallback((message: string, action: { label: string; onClick: () => void }, type: ToastType = 'info') => {
    const id = Math.random().toString(36).substring(2, 9)
    setToasts((prev) => [...prev, { id, message, type, duration: 10000, action }])

    setTimeout(() => {
      dismissToast(id)
    }, 10000)
  }, [dismissToast])

  return (
    <ToastContext.Provider value={{ showToast, showToastWithAction, dismissToast }}>
      {children}
      
      {/* Toast Container */}
      <div 
        className="fixed bottom-4 right-4 z-[100] flex flex-col gap-3 w-full max-w-sm pointer-events-none p-4 sm:p-0"
        role="region"
        aria-live="polite"
        aria-label="Notifications"
      >
        {toasts.map((toast, index) => {
          const config = typeConfig[toast.type]
          const Icon = config.icon

          return (
            <div
              key={toast.id}
              className={cn(
                'pointer-events-auto',
                'w-full max-w-sm',
                'rounded-xl',
                'shadow-2xl shadow-slate-900/10 dark:shadow-black/50',
                'border',
                'transform transition-all duration-300 ease-out',
                'animate-slideInRight',
                config.bg,
                config.border,
              )}
              style={{
                animationDelay: `${index * 50}ms`,
              }}
              role="alert"
            >
              <div className="p-4 flex items-start gap-3">
                <Icon 
                  className={cn(
                    'h-5 w-5 flex-shrink-0 mt-0.5',
                    config.iconColor,
                    toast.type === 'loading' && 'animate-spin'
                  )} 
                />
                
                <div className="flex-1 min-w-0">
                  <p className={cn('text-sm font-medium', config.text)}>
                    {toast.message}
                  </p>
                  
                  {toast.action && (
                    <div className="mt-3 flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          toast.action?.onClick()
                          dismissToast(toast.id)
                        }}
                      >
                        {toast.action.label}
                      </Button>
                    </div>
                  )}
                </div>
                
                <button
                  onClick={() => dismissToast(toast.id)}
                  className={cn(
                    'flex-shrink-0 p-1 rounded-lg transition-colors',
                    'text-slate-400 hover:text-slate-600 dark:hover:text-slate-200',
                    'hover:bg-slate-100 dark:hover:bg-slate-700/50'
                  )}
                  aria-label="Dismiss notification"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
              
              {/* Progress bar for auto-dismiss */}
              {toast.type !== 'loading' && (
                <div className="h-1 bg-slate-200 dark:bg-slate-700 rounded-b-xl overflow-hidden">
                  <div 
                    className={cn(
                      'h-full transition-all duration-300',
                      toast.type === 'success' && 'bg-emerald-500',
                      toast.type === 'error' && 'bg-rose-500',
                      toast.type === 'warning' && 'bg-amber-500',
                      toast.type === 'info' && 'bg-blue-500'
                    )}
                    style={{
                      width: '100%',
                      animation: `shrink ${toast.duration}ms linear forwards`,
                    }}
                  />
                </div>
              )}
            </div>
          )
        })}
      </div>
      
      <style jsx>{`
        @keyframes shrink {
          from { width: 100%; }
          to { width: 0%; }
        }
      `}</style>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}

// Helper hook for promise-based toasts
export function usePromiseToast() {
  const { showToast, dismissToast } = useToast()

  const toastPromise = useCallback(
    async function toastPromise<T>(
      promise: Promise<T>,
      messages: {
        loading: string
        success: string
        error: string
      }
    ): Promise<T> {
      const loadingId = Math.random().toString(36).substring(2, 9)
      showToast(messages.loading, 'loading', 0)

      try {
        const result = await promise
        dismissToast(loadingId)
        showToast(messages.success, 'success')
        return result
      } catch (error) {
        dismissToast(loadingId)
        showToast(messages.error, 'error')
        throw error
      }
    },
    [showToast, dismissToast]
  )

  return { toastPromise }
}
