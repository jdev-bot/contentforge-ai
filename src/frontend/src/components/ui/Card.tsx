import { cn } from '@/lib/utils'
import { ReactNode, HTMLAttributes, forwardRef, memo } from 'react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  className?: string
  interactive?: boolean
}

export const Card = memo(forwardRef<HTMLDivElement, CardProps>(
  ({ children, className, interactive = false, ...props }, ref) => {
    return (
      <div 
        className={cn(
          'bg-white rounded-xl shadow-lg border border-gray-100 transition-shadow duration-200',
          interactive && 'hover:shadow-xl cursor-pointer hover:-translate-y-0.5 transition-transform',
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

export const CardHeader = memo(function CardHeader({ children, className }: CardProps) {
  return <div className={cn('p-6 border-b border-gray-100', className)}>{children}</div>
})

export const CardTitle = memo(function CardTitle({ children, className }: CardProps) {
  return <h2 className={cn('text-xl font-semibold text-gray-900', className)}>{children}</h2>
})

export const CardDescription = memo(function CardDescription({ children, className }: CardProps) {
  return <p className={cn('text-sm text-gray-500 mt-1', className)}>{children}</p>
})

export const CardContent = memo(function CardContent({ children, className }: CardProps) {
  return <div className={cn('p-6', className)}>{children}</div>
})

// Add display names for better debugging
CardHeader.displayName = 'CardHeader'
CardTitle.displayName = 'CardTitle'
CardDescription.displayName = 'CardDescription'
CardContent.displayName = 'CardContent'
