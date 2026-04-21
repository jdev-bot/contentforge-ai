'use client'

import { ReactNode } from 'react'
import { cn } from '@/lib/utils'
import { ChevronRight } from 'lucide-react'

interface Breadcrumb {
  label: string
  href?: string
  onClick?: () => void
}

interface PageHeaderProps {
  title: string
  description: string
  icon?: ReactNode
  actions?: ReactNode
  badge?: ReactNode
  breadcrumbs?: Breadcrumb[]
  className?: string
}

export function PageHeader({
  title,
  description,
  icon,
  actions,
  badge,
  breadcrumbs,
  className,
}: PageHeaderProps) {
  return (
    <div className={cn('mb-6', className)}>
      {/* Breadcrumbs */}
      {breadcrumbs && breadcrumbs.length > 0 && (
        <nav className="flex items-center gap-1.5 text-sm text-slate-500 dark:text-slate-400 mb-3">
          {breadcrumbs.map((crumb, index) => (
            <span key={index} className="flex items-center gap-1.5">
              {index > 0 && <ChevronRight className="w-3.5 h-3.5 text-slate-400 dark:text-slate-500" />}
              {crumb.onClick || crumb.href ? (
                <button
                  onClick={crumb.onClick}
                  className="hover:text-slate-700 dark:hover:text-slate-300 transition-colors"
                >
                  {crumb.label}
                </button>
              ) : (
                <span>{crumb.label}</span>
              )}
            </span>
          ))}
        </nav>
      )}

      {/* Header row */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3 min-w-0">
          {icon && (
            <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500/10 to-violet-500/10 dark:from-blue-500/20 dark:to-violet-500/20 flex items-center justify-center">
              {icon}
            </div>
          )}
          <div className="min-w-0">
            <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 truncate">
              {title}
              {badge && <span className="ml-3">{badge}</span>}
            </h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">
              {description}
            </p>
          </div>
        </div>

        {actions && (
          <div className="flex items-center gap-3 flex-shrink-0">
            {actions}
          </div>
        )}
      </div>
    </div>
  )
}