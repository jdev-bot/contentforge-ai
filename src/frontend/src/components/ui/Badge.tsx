'use client'

import { cn } from '@/lib/utils'
import { HTMLAttributes, forwardRef, memo, ReactNode } from 'react'

type BadgeVariant = 'default' | 'primary' | 'success' | 'warning' | 'error' | 'info' | 'purple' | 'orange' | 'outline'
type BadgeSize = 'sm' | 'md' | 'lg'

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  children: ReactNode
  variant?: BadgeVariant
  size?: BadgeSize
  dot?: boolean
  removable?: boolean
  onRemove?: () => void
  className?: string
}

const Badge = memo(forwardRef<HTMLSpanElement, BadgeProps>(
  ({ 
    children, 
    variant = 'default', 
    size = 'md', 
    dot = false,
    removable = false,
    onRemove,
    className, 
    ...props 
  }, ref) => {
    const variants: Record<BadgeVariant, string> = {
      default: [
        'bg-slate-100 dark:bg-slate-800',
        'text-slate-700 dark:text-slate-300',
        'border border-slate-200 dark:border-slate-700',
      ].join(' '),
      primary: [
        'bg-blue-100 dark:bg-blue-500/20',
        'text-blue-700 dark:text-blue-300',
        'border border-blue-200 dark:border-blue-500/30',
      ].join(' '),
      success: [
        'bg-emerald-100 dark:bg-emerald-500/20',
        'text-emerald-700 dark:text-emerald-300',
        'border border-emerald-200 dark:border-emerald-500/30',
      ].join(' '),
      warning: [
        'bg-amber-100 dark:bg-amber-500/20',
        'text-amber-700 dark:text-amber-300',
        'border border-amber-200 dark:border-amber-500/30',
      ].join(' '),
      error: [
        'bg-rose-100 dark:bg-rose-500/20',
        'text-rose-700 dark:text-rose-300',
        'border border-rose-200 dark:border-rose-500/30',
      ].join(' '),
      info: [
        'bg-cyan-100 dark:bg-cyan-500/20',
        'text-cyan-700 dark:text-cyan-300',
        'border border-cyan-200 dark:border-cyan-500/30',
      ].join(' '),
      purple: [
        'bg-violet-100 dark:bg-violet-500/20',
        'text-violet-700 dark:text-violet-300',
        'border border-violet-200 dark:border-violet-500/30',
      ].join(' '),
      orange: [
        'bg-orange-100 dark:bg-orange-500/20',
        'text-orange-700 dark:text-orange-300',
        'border border-orange-200 dark:border-orange-500/30',
      ].join(' '),
      outline: [
        'bg-transparent',
        'text-slate-600 dark:text-slate-400',
        'border border-slate-300 dark:border-slate-600',
      ].join(' '),
    }

    const sizes: Record<BadgeSize, string> = {
      sm: 'px-2 py-0.5 text-xs',
      md: 'px-2.5 py-1 text-xs',
      lg: 'px-3 py-1.5 text-sm',
    }

    const dotColors: Record<BadgeVariant, string> = {
      default: 'bg-slate-500',
      primary: 'bg-blue-500',
      success: 'bg-emerald-500',
      warning: 'bg-amber-500',
      error: 'bg-rose-500',
      info: 'bg-cyan-500',
      purple: 'bg-violet-500',
      orange: 'bg-orange-500',
      outline: 'bg-slate-500',
    }

    return (
      <span
        ref={ref}
        className={cn(
          'inline-flex items-center gap-1.5',
          'font-medium',
          'rounded-full',
          'transition-all duration-200',
          variants[variant],
          sizes[size],
          removable && 'pr-1',
          className
        )}
        {...props}
      >
        {dot && (
          <span 
            className={cn(
              'w-1.5 h-1.5 rounded-full',
              dotColors[variant]
            )} 
          />
        )}
        <span>{children}</span>
        
        {removable && (
          <button
            type="button"
            onClick={onRemove}
            className={cn(
              'ml-1 -mr-0.5 p-0.5 rounded-full',
              'hover:bg-black/10 dark:hover:bg-white/10',
              'transition-colors',
              'focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-1',
              'focus-visible:ring-blue-500'
            )}
            aria-label="Remove badge"
          >
            <svg 
              className="w-3 h-3" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M6 18L18 6M6 6l12 12" 
              />
            </svg>
          </button>
        )}
      </span>
    )
  }
))

Badge.displayName = 'Badge'

export { Badge }

// Status Badge with pulse animation
interface StatusBadgeProps extends Omit<BadgeProps, 'variant' | 'dot'> {
  status: 'online' | 'offline' | 'away' | 'busy' | 'pending' | 'active' | 'inactive'
}

const StatusBadge = memo(forwardRef<HTMLSpanElement, StatusBadgeProps>(
  ({ status, className, ...props }, ref) => {
    const statusConfig = {
      online: { variant: 'success' as const, label: 'Online' },
      offline: { variant: 'default' as const, label: 'Offline' },
      away: { variant: 'warning' as const, label: 'Away' },
      busy: { variant: 'error' as const, label: 'Busy' },
      pending: { variant: 'warning' as const, label: 'Pending' },
      active: { variant: 'success' as const, label: 'Active' },
      inactive: { variant: 'default' as const, label: 'Inactive' },
    }

    const config = statusConfig[status]
    const shouldPulse = status === 'online' || status === 'active'

    return (
      <span ref={ref} className={cn('inline-flex items-center gap-2', className)} {...props}>
        <span className={cn(
          'relative flex h-2.5 w-2.5',
          shouldPulse && 'animate-pulse'
        )}>
          {shouldPulse && (
            <span className={cn(
              'absolute inline-flex h-full w-full rounded-full opacity-75',
              'animate-ping',
              status === 'online' && 'bg-emerald-400',
              status === 'active' && 'bg-emerald-400',
            )} />
          )}
          <span className={cn(
            'relative inline-flex rounded-full h-2.5 w-2.5',
            status === 'online' && 'bg-emerald-500',
            status === 'offline' && 'bg-slate-400',
            status === 'away' && 'bg-amber-500',
            status === 'busy' && 'bg-rose-500',
            status === 'pending' && 'bg-amber-500',
            status === 'active' && 'bg-emerald-500',
            status === 'inactive' && 'bg-slate-400',
          )} />
        </span>
        <span className="text-sm text-slate-600 dark:text-slate-400">{config.label}</span>
      </span>
    )
  }
))

StatusBadge.displayName = 'StatusBadge'

export { StatusBadge }

// Count Badge (for notifications, etc.)
interface CountBadgeProps extends HTMLAttributes<HTMLSpanElement> {
  count: number
  max?: number
  variant?: 'primary' | 'danger' | 'default'
  size?: 'sm' | 'md'
}

const CountBadge = memo(forwardRef<HTMLSpanElement, CountBadgeProps>(
  ({ count, max = 99, variant = 'danger', size = 'sm', className, ...props }, ref) => {
    const displayCount = count > max ? `${max}+` : count
    
    const variants = {
      primary: 'bg-blue-500 text-white',
      danger: 'bg-rose-500 text-white',
      default: 'bg-slate-500 text-white',
    }

    const sizes = {
      sm: 'min-w-[18px] h-[18px] text-[10px] px-1',
      md: 'min-w-[22px] h-[22px] text-xs px-1.5',
    }

    if (count <= 0) return null

    return (
      <span
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center',
          'rounded-full',
          'font-semibold',
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      >
        {displayCount}
      </span>
    )
  }
))

CountBadge.displayName = 'CountBadge'

export { CountBadge }

// Plan/Tier Badge
interface PlanBadgeProps extends HTMLAttributes<HTMLSpanElement> {
  plan: 'free' | 'starter' | 'pro' | 'enterprise' | 'basic' | 'premium'
}

const PlanBadge = memo(forwardRef<HTMLSpanElement, PlanBadgeProps>(
  ({ plan, className, ...props }, ref) => {
    const planConfig = {
      free: { 
        bg: 'bg-slate-100 dark:bg-slate-800', 
        text: 'text-slate-700 dark:text-slate-300',
        border: 'border-slate-200 dark:border-slate-700',
        icon: '●',
      },
      starter: { 
        bg: 'bg-blue-100 dark:bg-blue-500/20', 
        text: 'text-blue-700 dark:text-blue-300',
        border: 'border-blue-200 dark:border-blue-500/30',
        icon: '◐',
      },
      basic: { 
        bg: 'bg-blue-100 dark:bg-blue-500/20', 
        text: 'text-blue-700 dark:text-blue-300',
        border: 'border-blue-200 dark:border-blue-500/30',
        icon: '◐',
      },
      pro: { 
        bg: 'bg-gradient-to-r from-violet-100 to-fuchsia-100 dark:from-violet-500/20 dark:to-fuchsia-500/20', 
        text: 'text-violet-700 dark:text-violet-300',
        border: 'border-violet-200 dark:border-violet-500/30',
        icon: '◆',
      },
      premium: { 
        bg: 'bg-gradient-to-r from-violet-100 to-fuchsia-100 dark:from-violet-500/20 dark:to-fuchsia-500/20', 
        text: 'text-violet-700 dark:text-violet-300',
        border: 'border-violet-200 dark:border-violet-500/30',
        icon: '◆',
      },
      enterprise: { 
        bg: 'bg-gradient-to-r from-amber-100 to-orange-100 dark:from-amber-500/20 dark:to-orange-500/20', 
        text: 'text-amber-700 dark:text-amber-300',
        border: 'border-amber-200 dark:border-amber-500/30',
        icon: '★',
      },
    }

    const config = planConfig[plan]

    return (
      <span
        ref={ref}
        className={cn(
          'inline-flex items-center gap-1.5',
          'px-3 py-1',
          'text-xs font-semibold uppercase tracking-wider',
          'rounded-full border',
          config.bg,
          config.text,
          config.border,
          className
        )}
        {...props}
      >
        <span className="opacity-70">{config.icon}</span>
        <span>{plan}</span>
      </span>
    )
  }
))

PlanBadge.displayName = 'PlanBadge'

export { PlanBadge }
