import { cn } from '@/lib/utils'
import { InputHTMLAttributes, forwardRef } from 'react'

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: string
  label?: string
  helperText?: string
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, error, label, helperText, id, ...props }, ref) => {
    const inputId = id || `input-${Math.random().toString(36).slice(2, 11)}`
    
    return (
      <div className="w-full">
        {label && (
          <label 
            htmlFor={inputId}
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            {label}
          </label>
        )}
        
        <input
          id={inputId}
          className={cn(
            'flex w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900',
            'transition-all duration-200 ease-out',
            'placeholder:text-gray-400',
            'focus:outline-none focus:ring-2 focus:ring-offset-0 focus:ring-blue-500 focus:border-blue-500',
            'hover:border-gray-400',
            'disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-gray-100',
            error && 'border-red-500 focus:border-red-500 focus:ring-red-500',
            'min-h-[40px]', // Touch target size
            className
          )}
          ref={ref}
          {...props}
        />
        
        {helperText && !error && (
          <p className="mt-1 text-xs text-gray-500">{helperText}</p>
        )}
        
        {error && (
          <p className="mt-1 text-xs text-red-600" role="alert">{error}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export { Input }
