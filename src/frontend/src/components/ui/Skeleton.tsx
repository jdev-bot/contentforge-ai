'use client'

import { cn } from '@/lib/utils'
import { HTMLAttributes, memo } from 'react'

interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  className?: string
  variant?: 'default' | 'card' | 'text' | 'avatar' | 'button' | 'circle' | 'image'
  shimmer?: boolean
}

function SkeletonBase({ className, variant = 'default', shimmer = true, ...props }: SkeletonProps) {
  const variantClasses = {
    default: 'rounded-lg h-4',
    card: 'rounded-xl h-32',
    text: 'rounded h-4',
    avatar: 'rounded-full',
    button: 'rounded-xl h-11',
    circle: 'rounded-full aspect-square',
    image: 'rounded-xl aspect-video',
  }

  return (
    <div
      className={cn(
        'bg-slate-200 dark:bg-slate-800',
        'relative overflow-hidden',
        variantClasses[variant],
        shimmer && [
          'before:absolute before:inset-0',
          'before:-translate-x-full',
          'before:animate-[shimmer_2s_infinite]',
          'before:bg-gradient-to-r',
          'before:from-transparent before:via-white/20 before:to-transparent',
          'dark:before:via-white/5',
        ],
        className
      )}
      {...props}
    />
  )
}

export const Skeleton = memo(SkeletonBase)
Skeleton.displayName = 'Skeleton'

// Pre-built skeleton patterns for common use cases
export function ContentCardSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn(
      'bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-100 dark:border-slate-700',
      'p-6 space-y-4',
      className
    )}>
      <div className="flex items-start gap-4">
        <Skeleton variant="avatar" className="h-12 w-12 flex-shrink-0" />
        <div className="flex-1 space-y-3">
          <Skeleton className="h-5 w-3/4" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
          <div className="flex gap-3 pt-1">
            <Skeleton className="h-6 w-20 rounded-full" />
            <Skeleton className="h-6 w-16 rounded-full" />
          </div>
        </div>
      </div>
      
      <div className="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-700">
        <div className="flex items-center gap-3">
          <Skeleton variant="circle" className="h-8 w-8" />
          <Skeleton className="h-4 w-24" />
        </div>
        <Skeleton variant="button" className="w-24" />
      </div>
    </div>
  )
}

export function ProjectCardSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn(
      'bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-100 dark:border-slate-700',
      'p-6 space-y-4',
      className
    )}>
      <div className="flex items-start gap-4">
        <div className="p-3 bg-slate-100 dark:bg-slate-700 rounded-xl">
          <Skeleton variant="circle" className="h-6 w-6" />
        </div>
        <div className="flex-1 space-y-2">
          <Skeleton className="h-5 w-3/4" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-1/2" />
        </div>
      </div>
    </div>
  )
}

export function StatsCardSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn(
      'bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-100 dark:border-slate-700',
      'p-6 space-y-4',
      className
    )}>
      <div className="flex items-center justify-between">
        <Skeleton variant="circle" className="h-12 w-12" />
        <Skeleton variant="button" className="w-10" />
      </div>
      
      <div className="space-y-2">
        <Skeleton className="h-8 w-20" />
        <Skeleton className="h-4 w-32" />
      </div>
    </div>
  )
}

export function ActivityItemSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn('flex items-center gap-4 p-3', className)}>
      <Skeleton variant="avatar" className="h-10 w-10 flex-shrink-0" />
      <div className="flex-1 space-y-2">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-3 w-1/2" />
      </div>
      <Skeleton className="h-4 w-16 flex-shrink-0" />
    </div>
  )
}

export function TableSkeleton({ rows = 5, columns = 4, className }: { rows?: number; columns?: number; className?: string }) {
  return (
    <div className={cn('space-y-3', className)}>
      {/* Header */}
      <div className="flex gap-4 p-4 border-b border-slate-100 dark:border-slate-700">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={`header-${i}`} className="h-4 flex-1" />
        ))}
      </div>
      
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="flex gap-4 p-4 items-center">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton 
              key={`cell-${rowIndex}-${colIndex}`} 
              className={cn(
                'h-4',
                colIndex === 0 ? 'w-1/4' : colIndex === columns - 1 ? 'w-20' : 'flex-1'
              )} 
            />
          ))}
        </div>
      ))}
    </div>
  )
}

export function FormSkeleton({ fields = 3, className }: { fields?: number; className?: string }) {
  return (
    <div className={cn('space-y-6', className)}>
      {Array.from({ length: fields }).map((_, i) => (
        <div key={i} className="space-y-2">
          <Skeleton className="h-4 w-24" />
          <Skeleton variant="button" className="w-full h-12" />
        </div>
      ))}
      <div className="flex justify-end gap-4 pt-4">
        <Skeleton variant="button" className="w-24" />
        <Skeleton variant="button" className="w-32" />
      </div>
    </div>
  )
}

export function DashboardSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn('space-y-8', className)}>
      {/* Stats Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <StatsCardSkeleton key={i} />
        ))}
      </div>
      
      {/* Content Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <Skeleton className="h-8 w-48" />
          {Array.from({ length: 3 }).map((_, i) => (
            <ContentCardSkeleton key={i} />
          ))}
        </div>
        
        <div className="space-y-4">
          <Skeleton className="h-8 w-32" />
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-100 dark:border-slate-700 p-6">
            {Array.from({ length: 5 }).map((_, i) => (
              <ActivityItemSkeleton key={i} />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export function ProfileSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn(
      'bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-100 dark:border-slate-700',
      'p-8 space-y-6',
      className
    )}>
      <div className="flex items-center gap-6">
        <Skeleton variant="avatar" className="h-24 w-24" />
        <div className="space-y-2 flex-1">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-32" />
        </div>
      </div>
      
      <div className="space-y-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="flex items-center gap-4">
            <Skeleton variant="circle" className="h-10 w-10" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-full" />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
