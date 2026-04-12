'use client'

import { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import { X, CheckCircle, AlertCircle, Info, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

type ToastType = 'success' | 'error' | 'info' | 'loading'

interface Toast {
  id: string
  message: string
  type: ToastType
  duration?: number
}

interface ToastContextType {
  showToast: (message: string, type?: ToastType, duration?: number) => void
  dismissToast: (id: string) => void
}

const ToastContext = createContext<ToastContextType | undefined>(undefined)

const typeConfig = {
  success: {
    bg: 'bg-green-50',
    border: 'border-green-200',
    text: 'text-green-900',
    icon: CheckCircle,
    iconColor: 'text-green-600',
  },
  error: {
    bg: 'bg-red-50',
    border: 'border-red-200',
    text: 'text-red-900',
    icon: AlertCircle,
    iconColor: 'text-red-600',
  },
  info: {
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    text: 'text-blue-900',
    icon: Info,
    iconColor: 'text-blue-600',
  },
  loading: {
    bg: 'bg-gray-50',
    border: 'border-gray-200',
    text: 'text-gray-900',
    icon: Loader2,
    iconColor: 'text-gray-600',
  },
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const showToast = useCallback((message: string, type: ToastType = 'info', duration = 5000) => {
    const id = Math.random().toString(36).substring(2, 9)
    setToasts((prev) => [...prev, { id, message, type, duration }])

    // Auto-dismiss for non-loading toasts
    if (type !== 'loading') {
      setTimeout(() => {
        dismissToast(id)
      }, duration)
    }
  }, [])

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  return (
    <ToastContext.Provider value={{ showToast, dismissToast }}>
      {children}
      <div 
        className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none"
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
                'flex items-start gap-3 px-4 py-3 rounded-lg shadow-lg border',
                'min-w-[320px] max-w-md',
                'transition-all duration-300 ease-out',
                'animate-in slide-in-from-right-full fade-in',
                'hover:shadow-xl hover:-translate-y-0.5',
                config.bg,
                config.border,
                config.text
              )}
              style={{
                animationDelay: `${index * 50}ms`,
              }}
              role="alert"
            >
              <Icon 
                className={cn(
                  'h-5 w-5 flex-shrink-0 mt-0.5',
                  config.iconColor,
                  toast.type === 'loading' && 'animate-spin'
                )} 
              />
              <span className="flex-1 text-sm font-medium leading-relaxed">
                {toast.message}
              </span>
              <button
                onClick={() => dismissToast(toast.id)}
                className="flex-shrink-0 -mr-1 -mt-1 p-1 rounded-lg opacity-60 hover:opacity-100 hover:bg-black/5 transition-all"
                aria-label="Dismiss notification"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          )
        })}
      </div>
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
    async <T extends unknown>(
      promise: Promise<T>,
      messages: {
        loading: string
        success: string
        error: string
      }
    ): Promise<T> => {
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
