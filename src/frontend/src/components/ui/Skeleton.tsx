import { cn } from '@/lib/utils'
import { HTMLAttributes, memo } from 'react'

interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  className?: string
  variant?: 'default' | 'card' | 'text' | 'avatar' | 'button'
}

const variantStyles = {
  default: 'animate-pulse bg-gray-200 rounded',
  card: 'animate-pulse bg-white rounded-xl shadow-sm border border-gray-100',
  text: 'animate-pulse bg-gray-200 rounded h-4',
  avatar: 'animate-pulse bg-gray-200 rounded-full',
  button: 'animate-pulse bg-gray-200 rounded-lg h-10',
}

function SkeletonBase({ className, variant = 'default', ...props }: SkeletonProps) {
  return (
    <div
      className={cn(variantStyles[variant], className)}
      {...props}
    />
  )
}

export const Skeleton = memo(SkeletonBase)
Skeleton.displayName = 'Skeleton'

// Pre-built skeleton patterns for common use cases
export function ContentCardSkeleton() {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 animate-pulse">
      <div className="flex items-start gap-3">
        <div className="h-10 w-10 bg-gray-200 rounded-lg flex-shrink-0" />
        <div className="flex-1 space-y-3">
          <div className="h-5 bg-gray-200 rounded w-3/4" />
          <div className="h-4 bg-gray-200 rounded w-full" />
          <div className="flex gap-4">
            <div className="h-4 bg-gray-200 rounded w-24" />
            <div className="h-4 bg-gray-200 rounded w-20" />
          </div>
        </div>
        <div className="h-8 w-8 bg-gray-200 rounded-full flex-shrink-0" />
      </div>
    </div>
  )
}

export function ProjectCardSkeleton() {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 animate-pulse">
      <div className="flex items-start gap-3">
        <div className="h-10 w-10 bg-gray-200 rounded-lg flex-shrink-0" />
        <div className="flex-1 space-y-3">
          <div className="h-5 bg-gray-200 rounded w-3/4" />
          <div className="h-4 bg-gray-200 rounded w-full" />
          <div className="h-4 bg-gray-200 rounded w-1/2" />
        </div>
      </div>
    </div>
  )
}

export function StatsCardSkeleton() {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 animate-pulse">
      <div className="flex items-center justify-between">
        <div className="h-12 w-12 bg-gray-200 rounded-lg" />
        <div className="h-5 w-5 bg-gray-200 rounded" />
      </div>
      <div className="mt-4 space-y-2">
        <div className="h-8 bg-gray-200 rounded w-16" />
        <div className="h-4 bg-gray-200 rounded w-32" />
      </div>
    </div>
  )
}

export function ActivityItemSkeleton() {
  return (
    <div className="flex items-center gap-4 p-3 animate-pulse">
      <div className="h-8 w-8 bg-gray-200 rounded-full flex-shrink-0" />
      <div className="flex-1 space-y-2">
        <div className="h-4 bg-gray-200 rounded w-3/4" />
        <div className="h-3 bg-gray-200 rounded w-1/2" />
      </div>
      <div className="h-4 bg-gray-200 rounded w-16 flex-shrink-0" />
    </div>
  )
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {[...Array(rows)].map((_, i) => (
        <div key={i} className="flex gap-4 p-4 animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4" />
          <div className="h-4 bg-gray-200 rounded w-1/4 flex-1" />
          <div className="h-4 bg-gray-200 rounded w-1/6" />
          <div className="h-4 bg-gray-200 rounded w-16" />
        </div>
      ))}
    </div>
  )
}

export function FormSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="space-y-2">
        <div className="h-4 bg-gray-200 rounded w-24" />
        <div className="h-10 bg-gray-200 rounded w-full" />
      </div>
      <div className="space-y-2">
        <div className="h-4 bg-gray-200 rounded w-32" />
        <div className="h-32 bg-gray-200 rounded w-full" />
      </div>
      <div className="flex justify-end gap-4">
        <div className="h-10 bg-gray-200 rounded w-24" />
        <div className="h-10 bg-gray-200 rounded w-32" />
      </div>
    </div>
  )
}
