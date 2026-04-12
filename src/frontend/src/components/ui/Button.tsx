import { cn } from '@/lib/utils'
import { ButtonHTMLAttributes, forwardRef } from 'react'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg' | 'icon'
  tooltip?: string
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', tooltip, ...props }, ref) => {
    return (
      <button
        className={cn(
          'inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200 ease-out',
          'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-white',
          'active:scale-[0.98]',
          'disabled:opacity-50 disabled:pointer-events-none disabled:transform-none',
          'touch-manipulation', // Optimize for touch
          {
            // Primary variant
            'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-md hover:-translate-y-0.5 focus:ring-blue-500': variant === 'primary',
            // Secondary variant
            'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500 hover:shadow-sm hover:-translate-y-0.5': variant === 'secondary',
            // Outline variant
            'border-2 border-gray-300 bg-transparent hover:bg-gray-50 hover:border-gray-400 focus:ring-gray-500': variant === 'outline',
            // Ghost variant
            'bg-transparent hover:bg-gray-100 focus:ring-gray-500': variant === 'ghost',
            // Danger variant
            'bg-red-600 text-white hover:bg-red-700 hover:shadow-md hover:-translate-y-0.5 focus:ring-red-500': variant === 'danger',
            // Sizes
            'h-8 px-3 text-sm min-h-[32px]': size === 'sm',
            'h-10 px-4 py-2 text-sm min-h-[40px]': size === 'md',
            'h-12 px-6 text-base min-h-[48px]': size === 'lg',
            'h-10 w-10 p-0 min-h-[40px] min-w-[40px]': size === 'icon',
          },
          className
        )}
        ref={ref}
        title={tooltip}
        {...props}
      />
    )
  }
)

Button.displayName = 'Button'

export { Button }
