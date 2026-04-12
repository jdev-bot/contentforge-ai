'use client'

import { cn } from '@/lib/utils'
import { HTMLAttributes, forwardRef, memo, ReactNode } from 'react'
import { User } from 'lucide-react'

type AvatarSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl'
type AvatarStatus = 'online' | 'offline' | 'away' | 'busy'

interface AvatarProps extends HTMLAttributes<HTMLDivElement> {
  src?: string
  alt?: string
  name?: string
  size?: AvatarSize
  status?: AvatarStatus
  fallback?: ReactNode
  className?: string
}

const sizeClasses: Record<AvatarSize, { container: string; status: string; text: string }> = {
  xs: { container: 'h-6 w-6', status: 'h-1.5 w-1.5', text: 'text-[10px]' },
  sm: { container: 'h-8 w-8', status: 'h-2 w-2', text: 'text-xs' },
  md: { container: 'h-10 w-10', status: 'h-2.5 w-2.5', text: 'text-sm' },
  lg: { container: 'h-12 w-12', status: 'h-3 w-3', text: 'text-base' },
  xl: { container: 'h-16 w-16', status: 'h-3.5 w-3.5', text: 'text-lg' },
  '2xl': { container: 'h-20 w-20', status: 'h-4 w-4', text: 'text-xl' },
}

const statusColors: Record<AvatarStatus, string> = {
  online: 'bg-emerald-500',
  offline: 'bg-slate-400',
  away: 'bg-amber-500',
  busy: 'bg-rose-500',
}

const Avatar = memo(forwardRef<HTMLDivElement, AvatarProps>(
  ({ 
    src, 
    alt, 
    name, 
    size = 'md', 
    status,
    fallback,
    className,
    ...props 
  }, ref) => {
    const sizeClass = sizeClasses[size]
    
    // Generate initials from name
    const initials = name
      ?.split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)

    // Generate consistent background color from name
    const getColorFromName = (name: string) => {
      const colors = [
        'from-blue-500 to-indigo-500',
        'from-emerald-500 to-teal-500',
        'from-violet-500 to-purple-500',
        'from-rose-500 to-pink-500',
        'from-amber-500 to-orange-500',
        'from-cyan-500 to-blue-500',
      ]
      const index = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length
      return colors[index]
    }

    return (
      <div
        ref={ref}
        className={cn(
          'relative inline-flex items-center justify-center',
          'rounded-full',
          'overflow-hidden',
          'flex-shrink-0',
          'bg-slate-100 dark:bg-slate-800',
          sizeClass.container,
          className
        )}
        {...props}
      >
        {src ? (
          <img
            src={src}
            alt={alt || name || 'Avatar'}
            className="h-full w-full object-cover"
            onError={(e) => {
              // Hide broken image and show fallback
              e.currentTarget.style.display = 'none'
            }}
          />
        ) : null}
        
        {/* Fallback */}
        <div className={cn(
          'absolute inset-0 flex items-center justify-center',
          src && 'hidden'
        )}>
          {fallback || (initials ? (
            <span 
              className={cn(
                'font-semibold text-white',
                'bg-gradient-to-br',
                name ? getColorFromName(name) : 'from-blue-500 to-indigo-500',
                'w-full h-full flex items-center justify-center',
                sizeClass.text
              )}
            >
              {initials}
            </span>
          ) : (
            <User className={cn(
              'text-slate-400 dark:text-slate-500',
              size === 'xs' && 'h-3 w-3',
              size === 'sm' && 'h-4 w-4',
              size === 'md' && 'h-5 w-5',
              size === 'lg' && 'h-6 w-6',
              size === 'xl' && 'h-8 w-8',
              size === '2xl' && 'h-10 w-10',
            )} />
          ))}
        </div>
        
        {/* Status Indicator */}
        {status && (
          <span
            className={cn(
              'absolute bottom-0 right-0',
              'rounded-full',
              'ring-2 ring-white dark:ring-slate-900',
              statusColors[status],
              sizeClass.status
            )}
          />
        )}
      </div>
    )
  }
))

Avatar.displayName = 'Avatar'

export { Avatar }

// Avatar Group Component
interface AvatarGroupProps extends HTMLAttributes<HTMLDivElement> {
  avatars: Array<{
    src?: string
    name: string
    alt?: string
  }>
  size?: AvatarSize
  max?: number
  className?: string
}

const AvatarGroup = memo(forwardRef<HTMLDivElement, AvatarGroupProps>(
  ({ avatars, size = 'md', max = 4, className, ...props }, ref) => {
    const displayedAvatars = avatars.slice(0, max)
    const remainingCount = avatars.length - max
    const sizeClass = sizeClasses[size]

    // Calculate negative margin based on size
    const overlapClasses = {
      xs: '-space-x-2',
      sm: '-space-x-2',
      md: '-space-x-3',
      lg: '-space-x-3',
      xl: '-space-x-4',
      '2xl': '-space-x-5',
    }

    return (
      <div
        ref={ref}
        className={cn(
          'flex items-center',
          overlapClasses[size],
          className
        )}
        {...props}
      >
        {displayedAvatars.map((avatar, index) => (
          <Avatar
            key={index}
            src={avatar.src}
            name={avatar.name}
            alt={avatar.alt}
            size={size}
            className="ring-2 ring-white dark:ring-slate-900"
          />
        ))}
        
        {remainingCount > 0 && (
          <div
            className={cn(
              'flex items-center justify-center',
              'rounded-full',
              'bg-slate-200 dark:bg-slate-700',
              'text-slate-600 dark:text-slate-300',
              'font-medium',
              'ring-2 ring-white dark:ring-slate-900',
              sizeClass.container,
              sizeClass.text
            )}
          >
            +{remainingCount}
          </div>
        )}
      </div>
    )
  }
))

AvatarGroup.displayName = 'AvatarGroup'

export { AvatarGroup }

// Avatar with text (for user info display)
interface AvatarWithTextProps extends HTMLAttributes<HTMLDivElement> {
  src?: string
  name: string
  subtitle?: string
  size?: AvatarSize
  status?: AvatarStatus
  align?: 'left' | 'right'
  className?: string
}

const AvatarWithText = memo(forwardRef<HTMLDivElement, AvatarWithTextProps>(
  ({ src, name, subtitle, size = 'md', status, align = 'left', className, ...props }, ref) => {
    const textSizes = {
      xs: { name: 'text-xs', subtitle: 'text-[10px]' },
      sm: { name: 'text-sm', subtitle: 'text-xs' },
      md: { name: 'text-sm', subtitle: 'text-xs' },
      lg: { name: 'text-base', subtitle: 'text-sm' },
      xl: { name: 'text-lg', subtitle: 'text-base' },
      '2xl': { name: 'text-xl', subtitle: 'text-lg' },
    }

    return (
      <div
        ref={ref}
        className={cn(
          'flex items-center gap-3',
          align === 'right' && 'flex-row-reverse',
          className
        )}
        {...props}
      >
        <Avatar
          src={src}
          name={name}
          size={size}
          status={status}
        />
        
        <div className={cn('flex flex-col', align === 'right' && 'items-end')}>
          <span className={cn(
            'font-medium text-slate-900 dark:text-slate-100',
            textSizes[size].name
          )}>
            {name}
          </span>
          
          {subtitle && (
            <span className={cn(
              'text-slate-500 dark:text-slate-400',
              textSizes[size].subtitle
            )}>
              {subtitle}
            </span>
          )}
        </div>
      </div>
    )
  }
))

AvatarWithText.displayName = 'AvatarWithText'

export { AvatarWithText }
