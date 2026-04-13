'use client'

import { useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertTriangle, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from './Button'

interface ConfirmDialogProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  variant?: 'danger' | 'warning' | 'info'
  loading?: boolean
}

export function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'danger',
  loading = false,
}: ConfirmDialogProps) {
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose()
    }
    if (e.key === 'Enter' && !loading) {
      onConfirm()
    }
  }, [onClose, onConfirm, loading])

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown)
      document.body.style.overflow = 'hidden'
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = ''
    }
  }, [isOpen, handleKeyDown])

  const variantStyles = {
    danger: {
      icon: AlertTriangle,
      iconBg: 'bg-rose-100 dark:bg-rose-900/30',
      iconColor: 'text-rose-600 dark:text-rose-400',
      buttonVariant: 'danger' as const,
    },
    warning: {
      icon: AlertTriangle,
      iconBg: 'bg-amber-100 dark:bg-amber-900/30',
      iconColor: 'text-amber-600 dark:text-amber-400',
      buttonVariant: 'outline' as const,
    },
    info: {
      icon: AlertTriangle,
      iconBg: 'bg-blue-100 dark:bg-blue-900/30',
      iconColor: 'text-blue-600 dark:text-blue-400',
      buttonVariant: 'primary' as const,
    },
  }

  const { icon: Icon, iconBg, iconColor, buttonVariant } = variantStyles[variant]

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
            onClick={onClose}
            aria-hidden="true"
          />

          {/* Dialog */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
              className={cn(
                'w-full max-w-md pointer-events-auto',
                'bg-white dark:bg-slate-800',
                'rounded-2xl shadow-2xl',
                'border border-slate-200 dark:border-slate-700',
                'overflow-hidden'
              )}
              role="dialog"
              aria-modal="true"
              aria-labelledby="confirm-dialog-title"
              aria-describedby="confirm-dialog-description"
            >
              {/* Header */}
              <div className="flex items-center justify-between p-6 pb-0">
                <div className={cn('p-3 rounded-xl', iconBg)}>
                  <Icon className={cn('h-6 w-6', iconColor)} />
                </div>
                <button
                  onClick={onClose}
                  className="p-2 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                  aria-label="Close dialog"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              {/* Content */}
              <div className="p-6 pt-4">
                <h2
                  id="confirm-dialog-title"
                  className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-2"
                >
                  {title}
                </h2>
                <p
                  id="confirm-dialog-description"
                  className="text-slate-600 dark:text-slate-400"
                >
                  {message}
                </p>
              </div>

              {/* Actions */}
              <div className="flex gap-3 p-6 pt-0">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={onClose}
                  disabled={loading}
                >
                  {cancelText}
                </Button>
                <Button
                  variant={buttonVariant}
                  className="flex-1"
                  onClick={onConfirm}
                  loading={loading}
                >
                  {confirmText}
                </Button>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  )
}

// Hook for using confirm dialog
import { useState } from 'react'

interface UseConfirmDialogOptions {
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  variant?: 'danger' | 'warning' | 'info'
}

export function useConfirmDialog() {
  const [isOpen, setIsOpen] = useState(false)
  const [options, setOptions] = useState<UseConfirmDialogOptions>({
    title: '',
    message: '',
  })
  const [resolveRef, setResolveRef] = useState<((value: boolean) => void) | null>(null)
  const [loading, setLoading] = useState(false)

  const confirm = useCallback((opts: UseConfirmDialogOptions): Promise<boolean> => {
    setOptions(opts)
    setIsOpen(true)
    return new Promise((resolve) => {
      setResolveRef(() => resolve)
    })
  }, [])

  const handleConfirm = useCallback(async () => {
    setLoading(true)
    resolveRef?.(true)
    setIsOpen(false)
    setLoading(false)
  }, [resolveRef])

  const handleClose = useCallback(() => {
    resolveRef?.(false)
    setIsOpen(false)
  }, [resolveRef])

  const ConfirmDialogComponent = useCallback(
    () => (
      <ConfirmDialog
        isOpen={isOpen}
        onClose={handleClose}
        onConfirm={handleConfirm}
        title={options.title}
        message={options.message}
        confirmText={options.confirmText}
        cancelText={options.cancelText}
        variant={options.variant}
        loading={loading}
      />
    ),
    [isOpen, options, loading, handleClose, handleConfirm]
  )

  return { confirm, ConfirmDialogComponent }
}
