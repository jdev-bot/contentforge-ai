'use client'

import { cn } from '@/lib/utils'
import { InputHTMLAttributes, forwardRef, useId, useState, ReactNode } from 'react'
import { Eye, EyeOff, AlertCircle, Check, X } from 'lucide-react'

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: string
  label?: string
  helperText?: string
  floatingLabel?: boolean
  leftIcon?: ReactNode
  rightIcon?: ReactNode
  clearable?: boolean
  onClear?: () => void
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ 
    className, 
    error, 
    label, 
    helperText, 
    floatingLabel = false,
    leftIcon,
    rightIcon,
    clearable,
    onClear,
    id: propId,
    type = 'text',
    disabled,
    value,
    defaultValue,
    onChange,
    ...props 
  }, ref) => {
    const generatedId = useId()
    const id = propId || `input-${generatedId}`
    const [showPassword, setShowPassword] = useState(false)
    const [isFocused, setIsFocused] = useState(false)
    const [hasValue, setHasValue] = useState(
      Boolean(value || defaultValue)
    )

    const isPassword = type === 'password'
    const inputType = isPassword ? (showPassword ? 'text' : 'password') : type
    
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setHasValue(Boolean(e.target.value))
      onChange?.(e)
    }

    const handleClear = () => {
      onClear?.()
      setHasValue(false)
    }

    const inputClasses = cn(
      'flex w-full',
      'bg-white dark:bg-slate-800',
      'border-2 border-slate-200 dark:border-slate-700',
      'rounded-xl',
      'text-slate-900 dark:text-slate-100',
      'placeholder:text-slate-400 dark:placeholder:text-slate-500',
      'transition-all duration-200 ease-out',
      'focus:outline-none',
      'hover:border-slate-300 dark:hover:border-slate-600',
      error && [
        'border-rose-500 dark:border-rose-500',
        'focus:border-rose-500 dark:focus:border-rose-500',
        'focus:ring-rose-500/20 dark:focus:ring-rose-500/20',
      ],
      !error && [
        'focus:border-blue-500 dark:focus:border-blue-500',
        'focus:ring-4 focus:ring-blue-500/10 dark:focus:ring-blue-500/20',
      ],
      disabled && [
        'cursor-not-allowed',
        'bg-slate-100 dark:bg-slate-900',
        'opacity-60',
      ],
      // Size variants based on floating label
      floatingLabel && 'px-4 pt-6 pb-2 text-base',
      !floatingLabel && 'px-4 py-3 text-sm',
      // Left icon padding
      leftIcon && 'pl-12',
      // Right icon/clear padding
      (rightIcon || clearable || isPassword) && 'pr-12',
      className
    )

    if (floatingLabel) {
      return (
        <div className="w-full">
          <div className="relative">
            <input
              id={id}
              ref={ref}
              type={inputType}
              className={inputClasses}
              disabled={disabled}
              value={value}
              defaultValue={defaultValue}
              onChange={handleChange}
              onFocus={(e) => {
                setIsFocused(true)
                props.onFocus?.(e)
              }}
              onBlur={(e) => {
                setIsFocused(false)
                props.onBlur?.(e)
              }}
              placeholder=" "
              {...props}
            />
            
            {/* Floating Label */}
            <label
              htmlFor={id}
              className={cn(
                'absolute left-4 transition-all duration-200 ease-out pointer-events-none',
                'origin-left',
                (isFocused || hasValue) && [
                  'top-1.5 text-xs',
                  error && 'text-rose-500',
                  !error && 'text-blue-500',
                ],
                !(isFocused || hasValue) && [
                  'top-1/2 -translate-y-1/2 text-base',
                  'text-slate-500 dark:text-slate-400',
                ]
              )}
            >
              {label}
            </label>
            
            {/* Left Icon */}
            {leftIcon && (
              <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500 pointer-events-none">
                {leftIcon}
              </div>
            )}
            
            {/* Right Section */}
            <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
              {/* Clear Button */}
              {clearable && hasValue && !disabled && (
                <button
                  type="button"
                  onClick={handleClear}
                  className="p-1 rounded-md text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                  tabIndex={-1}
                >
                  <X className="h-4 w-4" />
                </button>
              )}
              
              {/* Password Toggle */}
              {isPassword && (
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="p-1 rounded-md text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                  tabIndex={-1}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              )}
              
              {/* Custom Right Icon */}
              {rightIcon && !clearable && !isPassword && (
                <div className="text-slate-400 dark:text-slate-500">{rightIcon}</div>
              )}
            </div>
          </div>
          
          {/* Helper Text / Error */}
          {(helperText || error) && (
            <div className="mt-1.5 flex items-start gap-1.5">
              {error && <AlertCircle className="h-4 w-4 text-rose-500 flex-shrink-0 mt-0.5" />}
              <p className={cn(
                'text-xs',
                error && 'text-rose-600 dark:text-rose-400',
                !error && 'text-slate-500 dark:text-slate-400'
              )}>
                {error || helperText}
              </p>
            </div>
          )}
        </div>
      )
    }

    // Standard input with separate label
    return (
      <div className="w-full">
        {label && (
          <label 
            htmlFor={id}
            className={cn(
              'block text-sm font-medium mb-1.5',
              error && 'text-rose-600 dark:text-rose-400',
              !error && 'text-slate-700 dark:text-slate-300'
            )}
          >
            {label}
          </label>
        )}
        
        <div className="relative">
          <input
            id={id}
            ref={ref}
            type={inputType}
            className={cn(
              inputClasses,
              !floatingLabel && [
                'h-12',
                leftIcon && 'pl-12',
                (rightIcon || clearable || isPassword) && 'pr-12',
              ]
            )}
            disabled={disabled}
            value={value}
            defaultValue={defaultValue}
            onChange={handleChange}
            {...props}
          />
          
          {/* Left Icon */}
          {leftIcon && (
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500 pointer-events-none">
              {leftIcon}
            </div>
          )}
          
          {/* Right Section */}
          <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
            {clearable && hasValue && !disabled && (
              <button
                type="button"
                onClick={handleClear}
                className="p-1 rounded-md text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                tabIndex={-1}
              >
                <X className="h-4 w-4" />
              </button>
            )}
            
            {isPassword && (
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="p-1 rounded-md text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                tabIndex={-1}
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            )}
            
            {rightIcon && !clearable && !isPassword && (
              <div className="text-slate-400 dark:text-slate-500">{rightIcon}</div>
            )}
          </div>
        </div>
        
        {(helperText || error) && (
          <div className="mt-1.5 flex items-start gap-1.5">
            {error && <AlertCircle className="h-4 w-4 text-rose-500 flex-shrink-0 mt-0.5" />}
            <p className={cn(
              'text-xs',
              error && 'text-rose-600 dark:text-rose-400',
              !error && 'text-slate-500 dark:text-slate-400'
            )}>
              {error || helperText}
            </p>
          </div>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export { Input }

// Textarea Component
interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: string
  label?: string
  helperText?: string
  resize?: 'none' | 'vertical' | 'horizontal' | 'both'
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, error, label, helperText, resize = 'vertical', ...props }, ref) => {
    const generatedId = useId()
    const id = props.id || `textarea-${generatedId}`

    const resizeClasses = {
      none: 'resize-none',
      vertical: 'resize-y',
      horizontal: 'resize-x',
      both: 'resize',
    }

    return (
      <div className="w-full">
        {label && (
          <label 
            htmlFor={id}
            className={cn(
              'block text-sm font-medium mb-1.5',
              error && 'text-rose-600 dark:text-rose-400',
              !error && 'text-slate-700 dark:text-slate-300'
            )}
          >
            {label}
          </label>
        )}
        
        <textarea
          id={id}
          ref={ref}
          className={cn(
            'flex w-full min-h-[120px]',
            'bg-white dark:bg-slate-800',
            'border-2 border-slate-200 dark:border-slate-700',
            'rounded-xl',
            'px-4 py-3',
            'text-slate-900 dark:text-slate-100',
            'placeholder:text-slate-400 dark:placeholder:text-slate-500',
            'transition-all duration-200 ease-out',
            'focus:outline-none',
            resizeClasses[resize],
            error && [
              'border-rose-500 dark:border-rose-500',
              'focus:border-rose-500 dark:focus:border-rose-500',
              'focus:ring-4 focus:ring-rose-500/20',
            ],
            !error && [
              'hover:border-slate-300 dark:hover:border-slate-600',
              'focus:border-blue-500 dark:focus:border-blue-500',
              'focus:ring-4 focus:ring-blue-500/10 dark:focus:ring-blue-500/20',
            ],
            props.disabled && [
              'cursor-not-allowed',
              'bg-slate-100 dark:bg-slate-900',
              'opacity-60',
            ],
            className
          )}
          {...props}
        />
        
        {(helperText || error) && (
          <div className="mt-1.5 flex items-start gap-1.5">
            {error && <AlertCircle className="h-4 w-4 text-rose-500 flex-shrink-0 mt-0.5" />}
            <p className={cn(
              'text-xs',
              error && 'text-rose-600 dark:text-rose-400',
              !error && 'text-slate-500 dark:text-slate-400'
            )}>
              {error || helperText}
            </p>
          </div>
        )}
      </div>
    )
  }
)

Textarea.displayName = 'Textarea'

// Select Component
interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  error?: string
  label?: string
  helperText?: string
  options: Array<{ value: string; label: string; disabled?: boolean }>
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, error, label, helperText, options, ...props }, ref) => {
    const generatedId = useId()
    const id = props.id || `select-${generatedId}`

    return (
      <div className="w-full">
        {label && (
          <label 
            htmlFor={id}
            className={cn(
              'block text-sm font-medium mb-1.5',
              error && 'text-rose-600 dark:text-rose-400',
              !error && 'text-slate-700 dark:text-slate-300'
            )}
          >
            {label}
          </label>
        )}
        
        <div className="relative">
          <select
            id={id}
            ref={ref}
            className={cn(
              'flex w-full h-12',
              'bg-white dark:bg-slate-800',
              'border-2 border-slate-200 dark:border-slate-700',
              'rounded-xl',
              'px-4 pr-10',
              'text-slate-900 dark:text-slate-100',
              'text-sm',
              'transition-all duration-200 ease-out',
              'focus:outline-none',
              'appearance-none',
              'cursor-pointer',
              error && [
                'border-rose-500 dark:border-rose-500',
                'focus:border-rose-500 dark:focus:border-rose-500',
                'focus:ring-4 focus:ring-rose-500/20',
              ],
              !error && [
                'hover:border-slate-300 dark:hover:border-slate-600',
                'focus:border-blue-500 dark:focus:border-blue-500',
                'focus:ring-4 focus:ring-blue-500/10 dark:focus:ring-blue-500/20',
              ],
              props.disabled && [
                'cursor-not-allowed',
                'bg-slate-100 dark:bg-slate-900',
                'opacity-60',
              ],
              className
            )}
            {...props}
          >
            {options.map((option) => (
              <option 
                key={option.value} 
                value={option.value}
                disabled={option.disabled}
              >
                {option.label}
              </option>
            ))}
          </select>
          
          {/* Custom Arrow */}
          <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500 dark:text-slate-400">
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
        
        {(helperText || error) && (
          <div className="mt-1.5 flex items-start gap-1.5">
            {error && <AlertCircle className="h-4 w-4 text-rose-500 flex-shrink-0 mt-0.5" />}
            <p className={cn(
              'text-xs',
              error && 'text-rose-600 dark:text-rose-400',
              !error && 'text-slate-500 dark:text-slate-400'
            )}>
              {error || helperText}
            </p>
          </div>
        )}
      </div>
    )
  }
)

Select.displayName = 'Select'
