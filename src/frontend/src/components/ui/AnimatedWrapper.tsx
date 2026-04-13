'use client'

import { motion, Variants, Transition } from 'framer-motion'
import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface AnimatedWrapperProps {
  children: ReactNode
  className?: string
  variant?: 'fadeIn' | 'fadeInUp' | 'fadeInDown' | 'slideInLeft' | 'slideInRight' | 'scaleIn' | 'none'
  delay?: number
  duration?: number
  staggerChildren?: number
  as?: keyof typeof motion
}

const variants: Record<string, Variants> = {
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
  },
  fadeInUp: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -10 },
  },
  fadeInDown: {
    initial: { opacity: 0, y: -20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: 10 },
  },
  slideInLeft: {
    initial: { opacity: 0, x: -30 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -20 },
  },
  slideInRight: {
    initial: { opacity: 0, x: 30 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 20 },
  },
  scaleIn: {
    initial: { opacity: 0, scale: 0.95 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.95 },
  },
  none: {
    initial: {},
    animate: {},
    exit: {},
  },
}

const defaultTransition: Transition = {
  duration: 0.4,
  ease: [0.16, 1, 0.3, 1],
}

export function AnimatedWrapper({
  children,
  className,
  variant = 'fadeInUp',
  delay = 0,
  duration = 0.4,
  as: Component = 'div',
}: AnimatedWrapperProps) {
  const MotionComponent = motion[Component as keyof typeof motion] as typeof motion.div

  return (
    <MotionComponent
      initial="initial"
      animate="animate"
      exit="exit"
      variants={variants[variant]}
      transition={{
        ...defaultTransition,
        duration,
        delay,
      }}
      className={cn(className)}
    >
      {children}
    </MotionComponent>
  )
}

// Stagger container for lists
interface StaggerContainerProps {
  children: ReactNode
  className?: string
  staggerDelay?: number
  delayChildren?: number
}

export function StaggerContainer({
  children,
  className,
  staggerDelay = 0.05,
  delayChildren = 0.1,
}: StaggerContainerProps) {
  return (
    <motion.div
      initial="initial"
      animate="animate"
      exit="exit"
      variants={{
        initial: {},
        animate: {
          transition: {
            staggerChildren: staggerDelay,
            delayChildren,
          },
        },
        exit: {
          transition: {
            staggerChildren: staggerDelay,
            staggerDirection: -1,
          },
        },
      }}
      className={cn(className)}
    >
      {children}
    </motion.div>
  )
}

// Stagger item for use inside StaggerContainer
interface StaggerItemProps {
  children: ReactNode
  className?: string
}

export function StaggerItem({ children, className }: StaggerItemProps) {
  return (
    <motion.div
      variants={variants.fadeInUp}
      className={cn(className)}
    >
      {children}
    </motion.div>
  )
}

// Hover scale animation wrapper
interface HoverScaleProps {
  children: ReactNode
  className?: string
  scale?: number
}

export function HoverScale({ children, className, scale = 1.02 }: HoverScaleProps) {
  return (
    <motion.div
      whileHover={{ scale }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
      className={cn(className)}
    >
      {children}
    </motion.div>
  )
}

// Fade in when in view
interface FadeInViewProps {
  children: ReactNode
  className?: string
  delay?: number
  once?: boolean
}

export function FadeInView({ children, className, delay = 0, once = true }: FadeInViewProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once, margin: '-50px' }}
      transition={{
        duration: 0.6,
        delay,
        ease: [0.16, 1, 0.3, 1],
      }}
      className={cn(className)}
    >
      {children}
    </motion.div>
  )
}

// Loading spinner with animation
interface LoadingSpinnerProps {
  className?: string
  size?: 'sm' | 'md' | 'lg'
}

export function LoadingSpinner({ className, size = 'md' }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  }

  return (
    <motion.div
      className={cn(
        'border-2 border-slate-200 border-t-blue-600 rounded-full',
        sizeClasses[size],
        className
      )}
      animate={{ rotate: 360 }}
      transition={{
        duration: 1,
        repeat: Infinity,
        ease: 'linear',
      }}
    />
  )
}
