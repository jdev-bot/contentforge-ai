'use client'

import { cn } from '@/lib/utils'
import { ButtonHTMLAttributes, forwardRef, useRef, useState, ReactNode } from 'react'
import { Loader2 } from 'lucide-react'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success' | 'gradient'
  size?: 'sm' | 'md' | 'lg' | 'icon'
  loading?: boolean
  tooltip?: string
  leftIcon?: ReactNode
  rightIcon?: ReactNode
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    className, 
    variant = 'primary', 
    size = 'md', 
    loading = false,
    tooltip,
    leftIcon,
    rightIcon,
    children,
    disabled,
    ...props 
  }, ref) => {
    const buttonRef = useRef<HTMLButtonElement>(null)
    const [ripples, setRipples] = useState<Array<{ x: number; y: number; id: number }>>([])

    const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
      // Create ripple effect
      const button = e.currentTarget
      const rect = button.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      const id = Date.now()
      
      setRipples(prev => [...prev, { x, y, id }])
      
      // Remove ripple after animation
      setTimeout(() => {
        setRipples(prev => prev.filter(r => r.id !== id))
      }, 600)

      props.onClick?.(e)
    }

    const variants = {
      primary: [
        'bg-gradient-to-r from-blue-600 to-violet-600',
        'text-white',
        'shadow-lg shadow-blue-500/30 dark:shadow-blue-500/20',
        'hover:shadow-xl hover:shadow-blue-500/40',
        'hover:scale-[1.02]',
        'active:scale-[0.98]',
        'border-0',
      ],
      secondary: [
        'bg-slate-100 dark:bg-slate-800',
        'text-slate-900 dark:text-slate-100',
        'border border-slate-200 dark:border-slate-700',
        'hover:bg-slate-200 dark:hover:bg-slate-700',
        'hover:border-slate-300 dark:hover:border-slate-600',
        'shadow-sm',
        'hover:shadow-md',
      ],
      outline: [
        'bg-transparent',
        'text-slate-700 dark:text-slate-300',
        'border-2 border-slate-200 dark:border-slate-700',
        'hover:bg-slate-50 dark:hover:bg-slate-800/50',
        'hover:border-slate-300 dark:hover:border-slate-600',
      ],
      ghost: [
        'bg-transparent',
        'text-slate-700 dark:text-slate-300',
        'hover:bg-slate-100 dark:hover:bg-slate-800',
        'hover:text-slate-900 dark:hover:text-slate-100',
      ],
      danger: [
        'bg-gradient-to-r from-rose-600 to-red-600',
        'text-white',
        'shadow-lg shadow-rose-500/30 dark:shadow-rose-500/20',
        'hover:shadow-xl hover:shadow-rose-500/40',
        'hover:scale-[1.02]',
        'active:scale-[0.98]',
        'border-0',
      ],
      success: [
        'bg-gradient-to-r from-emerald-600 to-teal-600',
        'text-white',
        'shadow-lg shadow-emerald-500/30 dark:shadow-emerald-500/20',
        'hover:shadow-xl hover:shadow-emerald-500/40',
        'hover:scale-[1.02]',
        'active:scale-[0.98]',
        'border-0',
      ],
      gradient: [
        'bg-gradient-to-r from-violet-600 via-purple-600 to-fuchsia-600',
        'text-white',
        'shadow-lg shadow-violet-500/30 dark:shadow-violet-500/20',
        'hover:shadow-xl hover:shadow-violet-500/40',
        'hover:scale-[1.02]',
        'active:scale-[0.98]',
        'border-0',
      ],
    }

    const sizes = {
      sm: 'h-9 px-4 text-sm min-h-[36px] rounded-lg',
      md: 'h-11 px-5 text-sm min-h-[44px] rounded-xl',
      lg: 'h-13 px-6 text-base min-h-[52px] rounded-xl',
      icon: 'h-11 w-11 p-0 min-h-[44px] min-w-[44px] rounded-xl',
    }

    const isDisabled = disabled || loading

    return (
      <button
        ref={ref || buttonRef}
        className={cn(
          'relative inline-flex items-center justify-center whitespace-nowrap',
          'font-semibold',
          'transition-all duration-200 ease-out',
          'focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
          'focus-visible:ring-blue-500 focus-visible:ring-offset-white dark:focus-visible:ring-offset-slate-900',
          'overflow-hidden',
          'touch-manipulation',
          variants[variant],
          sizes[size],
          isDisabled && 'opacity-50 cursor-not-allowed pointer-events-none transform-none shadow-none',
          className
        )}
        disabled={isDisabled}
        title={tooltip}
        onClick={handleClick}
        {...props}
      >
        {/* Ripple Effects */}
        {ripples.map((ripple) => (
          <span
            key={ripple.id}
            className="absolute bg-white/30 rounded-full animate-ping pointer-events-none"
            style={{
              left: ripple.x - 10,
              top: ripple.y - 10,
              width: 20,
              height: 20,
              animationDuration: '0.6s',
            }}
          />
        ))}
        
        {/* Loading Spinner */}
        {loading && (
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        )}
        
        {/* Left Icon */}
        {!loading && leftIcon && (
          <span className="mr-2">{leftIcon}</span>
        )}
        
        {/* Button Content */}
        <span className="relative z-10 whitespace-nowrap">{children}</span>
        
        {/* Right Icon */}
        {!loading && rightIcon && (
          <span className="ml-2">{rightIcon}</span>
        )}
      </button>
    )
  }
)

Button.displayName = 'Button'

export { Button }

// Icon Button Component
interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  icon: ReactNode
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  tooltip?: string
  'aria-label': string
}

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ icon, className, variant = 'ghost', size = 'md', tooltip, ...props }, ref) => {
    const sizes = {
      sm: 'h-9 w-9',
      md: 'h-11 w-11',
      lg: 'h-13 w-13',
    }

    return (
      <Button
        ref={ref}
        variant={variant === 'primary' ? 'primary' : variant === 'danger' ? 'danger' : 'ghost'}
        className={cn(sizes[size], 'p-0 rounded-xl', className)}
        tooltip={tooltip}
        {...props}
      >
        <span className="flex items-center justify-center">{icon}</span>
      </Button>
    )
  }
)

IconButton.displayName = 'IconButton'

// Floating Action Button
interface FabProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  icon: ReactNode
  variant?: 'primary' | 'secondary' | 'success'
  size?: 'sm' | 'md' | 'lg'
  tooltip?: string
  'aria-label': string
}

export const Fab = forwardRef<HTMLButtonElement, FabProps>(
  ({ icon, className, variant = 'primary', size = 'md', ...props }, ref) => {
    const variants = {
      primary: 'from-blue-600 to-violet-600 shadow-blue-500/40',
      secondary: 'from-slate-600 to-slate-700 shadow-slate-500/40',
      success: 'from-emerald-600 to-teal-600 shadow-emerald-500/40',
    }

    const sizes = {
      sm: 'h-12 w-12',
      md: 'h-14 w-14',
      lg: 'h-16 w-16',
    }

    const iconSizes = {
      sm: 'h-5 w-5',
      md: 'h-6 w-6',
      lg: 'h-7 w-7',
    }

    return (
      <button
        ref={ref}
        className={cn(
          'fixed bottom-6 right-6 z-50',
          'flex items-center justify-center',
          'rounded-full',
          'bg-gradient-to-r',
          variants[variant],
          'text-white',
          'shadow-lg hover:shadow-xl',
          'transition-all duration-300 ease-out',
          'hover:scale-110 active:scale-95',
          'focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-500',
          sizes[size],
          className
        )}
        {...props}
      >
        <span className={cn(iconSizes[size])}>{icon}</span>
      </button>
    )
  }
)

Fab.displayName = 'Fab'
