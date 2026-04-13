'use client'

import { ReactNode } from 'react'
import { motion } from 'framer-motion'
import { FolderOpen, FileText, Search, Inbox, Package, Ghost } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from './Button'

type EmptyIcon = 'folder' | 'file' | 'search' | 'inbox' | 'package' | 'ghost'

interface EmptyStateProps {
  title: string
  description?: string
  icon?: EmptyIcon | ReactNode
  action?: {
    label: string
    onClick: () => void
    icon?: ReactNode
  }
  secondaryAction?: {
    label: string
    onClick: () => void
  }
  className?: string
}

const iconMap: Record<EmptyIcon, React.ComponentType<{ className?: string }>> = {
  folder: FolderOpen,
  file: FileText,
  search: Search,
  inbox: Inbox,
  package: Package,
  ghost: Ghost,
}

export function EmptyState({
  title,
  description,
  icon = 'folder',
  action,
  secondaryAction,
  className,
}: EmptyStateProps) {
  const IconComponent = typeof icon === 'string' ? (iconMap[icon as EmptyIcon] ?? null) : null

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className={cn(
        'flex flex-col items-center justify-center',
        'text-center',
        'p-8 md:p-12',
        className
      )}
    >
      {/* Icon */}
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.1, duration: 0.4 }}
        className={cn(
          'w-24 h-24 rounded-full',
          'bg-slate-100 dark:bg-slate-800',
          'flex items-center justify-center',
          'mb-6'
        )}
      >
        {IconComponent ? (
          <IconComponent className="w-10 h-10 text-slate-400 dark:text-slate-500" />
        ) : (
          icon
        )}
      </motion.div>

      {/* Title */}
      <motion.h3
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.4 }}
        className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-2"
      >
        {title}
      </motion.h3>

      {/* Description */}
      {description && (
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.4 }}
          className="text-slate-500 dark:text-slate-400 max-w-md mb-6"
        >
          {description}
        </motion.p>
      )}

      {/* Actions */}
      {(action || secondaryAction) && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.4 }}
          className="flex flex-col sm:flex-row items-center gap-3"
        >
          {action && (
            <Button
              variant="primary"
              onClick={action.onClick}
              leftIcon={action.icon}
            >
              {action.label}
            </Button>
          )}
          {secondaryAction && (
            <Button
              variant="ghost"
              onClick={secondaryAction.onClick}
            >
              {secondaryAction.label}
            </Button>
          )}
        </motion.div>
      )}
    </motion.div>
  )
}

// Specialized empty states for common scenarios
export function NoResultsState({
  query,
  onClear,
  className,
}: {
  query: string
  onClear: () => void
  className?: string
}) {
  return (
    <EmptyState
      title="No results found"
      description={`We couldn't find any results for "${query}". Try adjusting your search or filters.`}
      icon="search"
      action={{
        label: 'Clear search',
        onClick: onClear,
      }}
      className={className}
    />
  )
}

export function NoDataState({
  title = 'No data yet',
  description = 'Get started by creating your first item.',
  onCreate,
  createLabel = 'Create New',
  className,
}: {
  title?: string
  description?: string
  onCreate: () => void
  createLabel?: string
  className?: string
}) {
  return (
    <EmptyState
      title={title}
      description={description}
      icon="folder"
      action={{
        label: createLabel,
        onClick: onCreate,
      }}
      className={className}
    />
  )
}

export function ErrorState({
  title = 'Something went wrong',
  description = 'An error occurred while loading the data.',
  onRetry,
  className,
}: {
  title?: string
  description?: string
  onRetry: () => void
  className?: string
}) {
  return (
    <EmptyState
      title={title}
      description={description}
      icon="ghost"
      action={{
        label: 'Try again',
        onClick: onRetry,
      }}
      className={className}
    />
  )
}
