'use client'

import { ReactNode, useState, useRef, useEffect, useCallback } from 'react'
import { cn } from '@/lib/utils'

type TooltipPosition = 'top' | 'bottom' | 'left' | 'right' | 'top-start' | 'top-end' | 'bottom-start' | 'bottom-end'
type TooltipVariant = 'default' | 'light' | 'info' | 'success' | 'warning' | 'error'

interface TooltipProps {
  children: ReactNode
  content: ReactNode
  position?: TooltipPosition
  delay?: number
  hideDelay?: number
  variant?: TooltipVariant
  maxWidth?: number
  disabled?: boolean
  className?: string
}

const variantClasses: Record<TooltipVariant, string> = {
  default: 'bg-slate-900 dark:bg-slate-800 text-white',
  light: 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white border border-slate-200 dark:border-slate-600 shadow-lg',
  info: 'bg-blue-600 text-white',
  success: 'bg-emerald-600 text-white',
  warning: 'bg-amber-500 text-white',
  error: 'bg-rose-600 text-white',
}

export function Tooltip({ 
  children, 
  content, 
  position = 'top',
  delay = 300,
  hideDelay = 100,
  variant = 'default',
  maxWidth = 250,
  disabled = false,
  className,
}: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [tooltipPosition, setTooltipPosition] = useState(position)
  const [isMounted, setIsMounted] = useState(false)
  const triggerRef = useRef<HTMLDivElement>(null)
  const tooltipRef = useRef<HTMLDivElement>(null)
  const showTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const hideTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  const clearTimeouts = useCallback(() => {
    if (showTimeoutRef.current) clearTimeout(showTimeoutRef.current)
    if (hideTimeoutRef.current) clearTimeout(hideTimeoutRef.current)
    showTimeoutRef.current = null
    hideTimeoutRef.current = null
  }, [])

  const calculatePosition = useCallback(() => {
    if (!triggerRef.current || !tooltipRef.current) return

    const triggerRect = triggerRef.current.getBoundingClientRect()
    const tooltipRect = tooltipRef.current.getBoundingClientRect()
    const viewportWidth = window.innerWidth
    const viewportHeight = window.innerHeight
    const gap = 8

    let calculatedPosition = position

    // Check if tooltip would overflow and adjust position
    const positions: Record<string, { top: number; left: number }> = {
      top: {
        top: triggerRect.top - tooltipRect.height - gap,
        left: triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2,
      },
      'top-start': {
        top: triggerRect.top - tooltipRect.height - gap,
        left: triggerRect.left,
      },
      'top-end': {
        top: triggerRect.top - tooltipRect.height - gap,
        left: triggerRect.right - tooltipRect.width,
      },
      bottom: {
        top: triggerRect.bottom + gap,
        left: triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2,
      },
      'bottom-start': {
        top: triggerRect.bottom + gap,
        left: triggerRect.left,
      },
      'bottom-end': {
        top: triggerRect.bottom + gap,
        left: triggerRect.right - tooltipRect.width,
      },
      left: {
        top: triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2,
        left: triggerRect.left - tooltipRect.width - gap,
      },
      right: {
        top: triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2,
        left: triggerRect.right + gap,
      },
    }

    // Check for overflow and flip position if needed
    const pos = positions[position]
    if (pos) {
      if (pos.left < 8) {
        if (position.startsWith('top') || position.startsWith('bottom')) {
          calculatedPosition = position.replace('start', '').replace('end', '') as TooltipPosition
        }
      }
      if (pos.left + tooltipRect.width > viewportWidth - 8) {
        if (position.startsWith('top') || position.startsWith('bottom')) {
          calculatedPosition = position.replace('start', '').replace('end', '') as TooltipPosition
        }
      }
      if (pos.top < 8) {
        calculatedPosition = position.replace('top', 'bottom') as TooltipPosition
      }
      if (pos.top + tooltipRect.height > viewportHeight - 8) {
        calculatedPosition = position.replace('bottom', 'top') as TooltipPosition
      }
    }

    setTooltipPosition(calculatedPosition)
  }, [position])

  const showTooltip = useCallback(() => {
    if (disabled) return
    clearTimeouts()
    showTimeoutRef.current = setTimeout(() => {
      setIsVisible(true)
      setIsMounted(true)
      // Calculate position after tooltip is rendered
      requestAnimationFrame(() => {
        calculatePosition()
      })
    }, delay)
  }, [disabled, delay, clearTimeouts, calculatePosition])

  const hideTooltip = useCallback(() => {
    clearTimeouts()
    hideTimeoutRef.current = setTimeout(() => {
      setIsVisible(false)
      setTimeout(() => setIsMounted(false), 200)
    }, hideDelay)
  }, [hideDelay, clearTimeouts])

  // Handle keyboard focus
  const handleFocus = useCallback(() => {
    showTooltip()
  }, [showTooltip])

  const handleBlur = useCallback(() => {
    hideTooltip()
  }, [hideTooltip])

  // Cleanup on unmount
  useEffect(() => {
    return () => clearTimeouts()
  }, [clearTimeouts])

  const arrowClasses = {
    top: 'top-full left-1/2 -translate-x-1/2 border-t-slate-900 dark:border-t-slate-800',
    'top-start': 'top-full left-4 border-t-slate-900 dark:border-t-slate-800',
    'top-end': 'top-full right-4 border-t-slate-900 dark:border-t-slate-800',
    bottom: 'bottom-full left-1/2 -translate-x-1/2 border-b-slate-900 dark:border-b-slate-800',
    'bottom-start': 'bottom-full left-4 border-b-slate-900 dark:border-b-slate-800',
    'bottom-end': 'bottom-full right-4 border-b-slate-900 dark:border-b-slate-800',
    left: 'left-full top-1/2 -translate-y-1/2 border-l-slate-900 dark:border-l-slate-800',
    right: 'right-full top-1/2 -translate-y-1/2 border-r-slate-900 dark:border-r-slate-800',
  }

  const arrowBorderClasses = {
    light: {
      top: 'border-t-slate-200 dark:border-t-slate-600',
      'top-start': 'border-t-slate-200 dark:border-t-slate-600',
      'top-end': 'border-t-slate-200 dark:border-t-slate-600',
      bottom: 'border-b-slate-200 dark:border-b-slate-600',
      'bottom-start': 'border-b-slate-200 dark:border-b-slate-600',
      'bottom-end': 'border-b-slate-200 dark:border-b-slate-600',
      left: 'border-l-slate-200 dark:border-l-slate-600',
      right: 'border-r-slate-200 dark:border-r-slate-600',
    },
  }

  return (
    <div
      ref={triggerRef}
      className="inline-flex relative"
      onMouseEnter={showTooltip}
      onMouseLeave={hideTooltip}
      onFocus={handleFocus}
      onBlur={handleBlur}
      onTouchStart={showTooltip}
      onTouchEnd={hideTooltip}
    >
      {children}
      
      {isMounted && (
        <div
          ref={tooltipRef}
          className={cn(
            'fixed z-50',
            'px-3 py-2',
            'rounded-lg',
            'text-sm font-medium',
            'shadow-lg shadow-black/10',
            'transition-all duration-200 ease-out',
            isVisible 
              ? 'opacity-100 translate-y-0' 
              : 'opacity-0 translate-y-1',
            variantClasses[variant],
            className
          )}
          style={{
            maxWidth,
            pointerEvents: 'none',
          }}
          role="tooltip"
        >
          {content}
          
          {/* Arrow */}
          {variant !== 'light' && (
            <span
              className={cn(
                'absolute w-0 h-0 border-4 border-transparent',
                arrowClasses[tooltipPosition]
              )}
            />
          )}
          {variant === 'light' && (
            <span
              className={cn(
                'absolute w-0 h-0 border-4 border-transparent',
                arrowClasses[tooltipPosition],
                arrowBorderClasses.light[tooltipPosition as keyof typeof arrowBorderClasses.light]
              )}
            />
          )}
        </div>
      )}
    </div>
  )
}

// Simple tooltip button wrapper
interface TooltipButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  tooltip: string
  tooltipPosition?: TooltipPosition
  tooltipVariant?: TooltipVariant
  icon?: ReactNode
  label?: string
  showLabel?: boolean
}

export function TooltipButton({ 
  tooltip, 
  tooltipPosition = 'top',
  tooltipVariant = 'default',
  icon, 
  label,
  showLabel = false,
  className,
  ...props 
}: TooltipButtonProps) {
  return (
    <Tooltip content={tooltip} position={tooltipPosition} variant={tooltipVariant}>
      <button
        type="button"
        className={cn(
          'inline-flex items-center justify-center',
          'rounded-xl',
          'transition-all duration-200',
          'hover:bg-slate-100 dark:hover:bg-slate-800',
          'focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500',
          'disabled:opacity-50 disabled:pointer-events-none',
          'min-h-[44px] min-w-[44px]',
          className
        )}
        {...props}
      >
        {icon && <span className={cn(label && showLabel && 'mr-2')}>{icon}</span>}
        {label && showLabel && <span>{label}</span>}
      </button>
    </Tooltip>
  )
}

// Help tooltip with info icon
interface HelpTooltipProps {
  content: ReactNode
  position?: TooltipPosition
  className?: string
}

export function HelpTooltip({ content, position = 'top', className }: HelpTooltipProps) {
  return (
    <Tooltip content={content} position={position} variant="info">
      <button
        type="button"
        className={cn(
          'inline-flex items-center justify-center',
          'w-5 h-5 rounded-full',
          'bg-blue-100 dark:bg-blue-500/20',
          'text-blue-600 dark:text-blue-400',
          'text-xs font-semibold',
          'hover:bg-blue-200 dark:hover:bg-blue-500/30',
          'transition-colors',
          'focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2',
          className
        )}
        aria-label="Help"
      >
        ?
      </button>
    </Tooltip>
  )
}
