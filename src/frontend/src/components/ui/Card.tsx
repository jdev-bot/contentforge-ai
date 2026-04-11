import { cn } from '@/lib/utils'
import { ReactNode } from 'react'

interface CardProps {
  children: ReactNode
  className?: string
}

export function Card({ children, className }: CardProps) {
  return (
    <div className={cn('bg-white rounded-xl shadow-lg border border-gray-100', className)}>
      {children}
    </div>
  )
}

export function CardHeader({ children, className }: CardProps) {
  return <div className={cn('p-6 border-b border-gray-100', className)}>{children}</div>
}

export function CardTitle({ children, className }: CardProps) {
  return <h2 className={cn('text-xl font-semibold', className)}>{children}</h2>
}

export function CardDescription({ children, className }: CardProps) {
  return <p className={cn('text-sm text-gray-500 mt-1', className)}>{children}</p>
}

export function CardContent({ children, className }: CardProps) {
  return <div className={cn('p-6', className)}>{children}</div>
}
