'use client'

import { ReactNode, useState } from 'react'
import { cn } from '@/lib/utils'

interface TooltipProps {
  children: ReactNode
  content: string
  position?: 'top' | 'bottom' | 'left' | 'right'
  delay?: number
}

export function Tooltip({ 
  children, 
  content, 
  position = 'top',
  delay = 200 
}: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [timeoutId, setTimeoutId] = useState<NodeJS.Timeout | null>(null)

  const handleMouseEnter = () => {
    const id = setTimeout(() => setIsVisible(true), delay)
    setTimeoutId(id)
  }

  const handleMouseLeave = () => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
    setIsVisible(false)
  }

  const positionClasses = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  }

  const arrowClasses = {
    top: 'top-full left-1/2 -translate-x-1/2 -mt-1 border-l-transparent border-r-transparent border-b-transparent border-t-gray-900',
    bottom: 'bottom-full left-1/2 -translate-x-1/2 -mb-1 border-l-transparent border-r-transparent border-t-transparent border-b-gray-900',
    left: 'left-full top-1/2 -translate-y-1/2 -ml-1 border-t-transparent border-b-transparent border-r-transparent border-l-gray-900',
    right: 'right-full top-1/2 -translate-y-1/2 -mr-1 border-t-transparent border-b-transparent border-l-transparent border-r-gray-900',
  }

  return (
    <div 
      className="relative inline-flex"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {children}
      
      {isVisible && (
        <div
          className={cn(
            'absolute z-50 px-2 py-1 text-xs font-medium text-white bg-gray-900 rounded',
            'whitespace-nowrap pointer-events-none',
            'animate-in fade-in duration-150',
            positionClasses[position]
          )}
          role="tooltip"
        >
          {content}
          <span 
            className={cn(
              'absolute w-0 h-0 border-4',
              arrowClasses[position]
            )} 
          />
        </div>
      )}
    </div>
  )
}

// Button with tooltip wrapper
interface TooltipButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  tooltip: string
  icon?: ReactNode
  label?: string
}

export function TooltipButton({ 
  tooltip, 
  icon, 
  label,
  className,
  ...props 
}: TooltipButtonProps) {
  return (
    <Tooltip content={tooltip}>
      <button
        type="button"
        className={cn(
          'inline-flex items-center justify-center',
          'rounded-lg transition-colors duration-200',
          'hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500',
          'disabled:opacity-50 disabled:pointer-events-none',
          'min-h-[40px] min-w-[40px]', // Touch target
          className
        )}
        {...props}
      >
        {icon && <span className={cn(label && 'mr-2')} >{icon}</span>}
        {label}
      </button>
    </Tooltip>
  )
}
