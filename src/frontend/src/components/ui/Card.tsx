'use client'

import { cn } from '@/lib/utils'
import { ReactNode, HTMLAttributes, forwardRef, memo } from 'react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  className?: string
  variant?: 'default' | 'glass' | 'elevated' | 'outline'
  interactive?: boolean
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

export const Card = memo(forwardRef<HTMLDivElement, CardProps>(
  ({ children, className, variant = 'default', interactive = false, padding = 'md', ...props }, ref) => {
    const variantClasses = {
      default: [
        'bg-white dark:bg-slate-800',
        'border border-slate-200 dark:border-slate-700',
        'shadow-md shadow-slate-200/50 dark:shadow-black/20',
      ],
      glass: [
        'glass',
        'bg-white/70 dark:bg-slate-900/70',
        'backdrop-blur-xl',
        'border border-white/20 dark:border-white/10',
        'shadow-xl shadow-slate-900/5 dark:shadow-black/30',
      ],
      elevated: [
        'bg-white dark:bg-slate-800',
        'border border-slate-100 dark:border-slate-700',
        'shadow-xl shadow-slate-200/60 dark:shadow-black/40',
      ],
      outline: [
        'bg-transparent',
        'border-2 border-slate-200 dark:border-slate-700',
      ],
    }

    const paddingClasses = {
      none: '',
      sm: 'p-4',
      md: 'p-6',
      lg: 'p-8',
    }

    return (
      <div 
        className={cn(
          'rounded-2xl transition-all duration-300 ease-out',
          variantClasses[variant],
          padding !== 'none' && paddingClasses[padding],
          interactive && [
            'cursor-pointer',
            'hover:shadow-2xl hover:shadow-slate-900/10 dark:hover:shadow-black/40',
            'hover:-translate-y-1',
            'active:translate-y-0 active:scale-[0.99]',
            'focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2',
          ],
          className
        )} 
        ref={ref}
        {...props}
      >
        {children}
      </div>
    )
  }
))

Card.displayName = 'Card'

interface CardHeaderProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  className?: string
  divider?: boolean
}

export const CardHeader = memo(forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ children, className, divider = true, ...props }, ref) => (
    <div 
      ref={ref}
      className={cn(
        'pb-4',
        divider && 'border-b border-slate-100 dark:border-slate-700/50 mb-4',
        className
      )} 
      {...props}
    >
      {children}
    </div>
  )
))

CardHeader.displayName = 'CardHeader'

interface CardTitleProps extends HTMLAttributes<HTMLHeadingElement> {
  children: ReactNode
  className?: string
  as?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6'
}

export const CardTitle = memo(forwardRef<HTMLHeadingElement, CardTitleProps>(
  ({ children, className, as: Component = 'h3', ...props }, ref) => (
    <Component 
      ref={ref}
      className={cn(
        'text-xl font-semibold text-slate-900 dark:text-slate-100',
        'tracking-tight',
        className
      )} 
      {...props}
    >
      {children}
    </Component>
  )
))

CardTitle.displayName = 'CardTitle'

interface CardDescriptionProps extends HTMLAttributes<HTMLParagraphElement> {
  children: ReactNode
  className?: string
}

export const CardDescription = memo(forwardRef<HTMLParagraphElement, CardDescriptionProps>(
  ({ children, className, ...props }, ref) => (
    <p 
      ref={ref}
      className={cn(
        'text-sm text-slate-500 dark:text-slate-400 mt-1.5',
        'leading-relaxed',
        className
      )} 
      {...props}
    >
      {children}
    </p>
  )
))

CardDescription.displayName = 'CardDescription'

interface CardContentProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  className?: string
}

export const CardContent = memo(forwardRef<HTMLDivElement, CardContentProps>(
  ({ children, className, ...props }, ref) => (
    <div 
      ref={ref}
      className={cn('', className)} 
      {...props}
    >
      {children}
    </div>
  )
))

CardContent.displayName = 'CardContent'

interface CardFooterProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  className?: string
  divider?: boolean
}

export const CardFooter = memo(forwardRef<HTMLDivElement, CardFooterProps>(
  ({ children, className, divider = true, ...props }, ref) => (
    <div 
      ref={ref}
      className={cn(
        'pt-4 mt-4',
        divider && 'border-t border-slate-100 dark:border-slate-700/50',
        'flex items-center justify-between gap-3',
        className
      )} 
      {...props}
    >
      {children}
    </div>
  )
))

CardFooter.displayName = 'CardFooter'

// Premium gradient card for feature highlights
interface GradientCardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  className?: string
  gradient?: 'primary' | 'success' | 'warning' | 'danger' | 'purple' | 'orange'
  interactive?: boolean
}

export const GradientCard = memo(forwardRef<HTMLDivElement, GradientCardProps>(
  ({ children, className, gradient = 'primary', interactive = false, ...props }, ref) => {
    const gradientClasses = {
      primary: 'from-blue-500/10 to-violet-500/10 dark:from-blue-500/20 dark:to-violet-500/20',
      success: 'from-emerald-500/10 to-teal-500/10 dark:from-emerald-500/20 dark:to-teal-500/20',
      warning: 'from-amber-500/10 to-orange-500/10 dark:from-amber-500/20 dark:to-orange-500/20',
      danger: 'from-rose-500/10 to-red-500/10 dark:from-rose-500/20 dark:to-red-500/20',
      purple: 'from-violet-500/10 to-fuchsia-500/10 dark:from-violet-500/20 dark:to-fuchsia-500/20',
      orange: 'from-orange-500/10 to-pink-500/10 dark:from-orange-500/20 dark:to-pink-500/20',
    }

    return (
      <div 
        ref={ref}
        className={cn(
          'relative rounded-2xl overflow-hidden',
          'bg-gradient-to-br',
          gradientClasses[gradient],
          'border border-white/20 dark:border-white/10',
          'p-6',
          interactive && [
            'cursor-pointer',
            'hover:shadow-xl hover:shadow-blue-500/10',
            'hover:-translate-y-1',
            'transition-all duration-300 ease-out',
          ],
          className
        )}
        {...props}
      >
        {/* Animated glow effect */}
        <div className={cn(
          'absolute inset-0 opacity-0 transition-opacity duration-500',
          interactive && 'group-hover:opacity-100',
          'bg-gradient-to-br',
          gradientClasses[gradient].replace('/10', '/5').replace('/20', '/10')
        )} />
        <div className="relative z-10">{children}</div>
      </div>
    )
  }
))

GradientCard.displayName = 'GradientCard'

// Stats card for dashboard
interface StatsCardProps extends HTMLAttributes<HTMLDivElement> {
  title: string
  value: string | number
  change?: {
    value: number
    trend: 'up' | 'down' | 'neutral'
  }
  icon?: ReactNode
  className?: string
}

export const StatsCard = memo(forwardRef<HTMLDivElement, StatsCardProps>(
  ({ title, value, change, icon, className, ...props }, ref) => {
    const trendColors = {
      up: 'text-emerald-600 dark:text-emerald-400',
      down: 'text-rose-600 dark:text-rose-400',
      neutral: 'text-slate-600 dark:text-slate-400',
    }

    const trendIcons = {
      up: '↑',
      down: '↓',
      neutral: '→',
    }

    return (
      <Card 
        ref={ref}
        variant="glass" 
        className={cn('group', className)}
        {...props}
      >
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-medium text-slate-600 dark:text-slate-400">{title}</p>
            <p className="text-3xl font-bold text-slate-900 dark:text-slate-100 mt-2">{value}</p>
            {change && (
              <div className={cn('flex items-center gap-1 mt-2 text-sm', trendColors[change.trend])}>
                <span>{trendIcons[change.trend]}</span>
                <span>{Math.abs(change.value)}%</span>
                <span className="text-slate-500 dark:text-slate-500 ml-1">vs last month</span>
              </div>
            )}
          </div>
          {icon && (
            <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500/10 to-violet-500/10 dark:from-blue-500/20 dark:to-violet-500/20 text-blue-600 dark:text-blue-400">
              {icon}
            </div>
          )}
        </div>
      </Card>
    )
  }
))

StatsCard.displayName = 'StatsCard'
