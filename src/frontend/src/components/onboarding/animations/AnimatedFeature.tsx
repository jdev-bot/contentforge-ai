'use client';

import { motion, useInView, Variants } from 'framer-motion';
import { useRef, ReactNode, useState } from 'react';
import { useReducedMotion } from './useReducedMotion';

interface AnimatedFeatureProps {
  icon: ReactNode;
  title: string;
  description: string;
  delay?: number;
  className?: string;
  variant?: 'card' | 'row' | 'minimal';
  highlight?: boolean;
  onClick?: () => void;
  onHover?: (isHovering: boolean) => void;
}

const containerVariants: Variants = {
  hidden: { opacity: 0, y: 30 },
  visible: (delay: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: delay * 0.1,
      duration: 0.6,
      ease: [0.16, 1, 0.3, 1],
    },
  }),
};

const iconVariants: Variants = {
  initial: { scale: 1, rotate: 0 },
  hover: {
    scale: 1.1,
    rotate: [0, -10, 10, 0],
    transition: {
      scale: { duration: 0.3, ease: 'easeOut' },
      rotate: { duration: 0.5, ease: 'easeInOut' },
    },
  },
};

const glowVariants: Variants = {
  initial: { 
    opacity: 0,
    scale: 0.8,
  },
  hover: {
    opacity: 1,
    scale: 1.2,
    transition: {
      duration: 0.4,
      ease: 'easeOut',
    },
  },
};

export function AnimatedFeature({
  icon,
  title,
  description,
  delay = 0,
  className = '',
  variant = 'card',
  highlight = false,
  onClick,
  onHover,
}: AnimatedFeatureProps) {
  const prefersReducedMotion = useReducedMotion();
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-50px' });
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseEnter = () => {
    setIsHovered(true);
    onHover?.(true);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    onHover?.(false);
  };

  const baseClasses = {
    card: `
      relative p-6 rounded-2xl
      bg-white dark:bg-slate-800
      border border-slate-200 dark:border-slate-700
      shadow-sm hover:shadow-xl
      transition-shadow duration-300
      group cursor-pointer
      overflow-hidden
    `,
    row: `
      relative p-4 rounded-xl
      bg-white/50 dark:bg-slate-800/50
      border border-slate-200 dark:border-slate-700
      hover:bg-white dark:hover:bg-slate-800
      transition-colors duration-200
      group cursor-pointer
      flex items-center gap-4
    `,
    minimal: `
      relative text-center p-4
      group cursor-pointer
    `,
  };

  const highlightClasses = highlight
    ? 'ring-2 ring-blue-500 dark:ring-blue-400 ring-offset-2 dark:ring-offset-slate-900'
    : '';

  return (
    <motion.div
      ref={ref}
      custom={delay}
      variants={prefersReducedMotion ? undefined : containerVariants}
      initial="hidden"
      animate={isInView ? 'visible' : 'hidden'}
      whileHover={prefersReducedMotion ? undefined : { y: -4 }}
      onHoverStart={handleMouseEnter}
      onHoverEnd={handleMouseLeave}
      onClick={onClick}
      className={`${baseClasses[variant]} ${highlightClasses} ${className}`}
    >
      {/* Glow Effect */}
      {!prefersReducedMotion && variant === 'card' && (
        <motion.div
          variants={glowVariants}
          initial="initial"
          animate={isHovered ? 'hover' : 'initial'}
          className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-pink-500/10 rounded-2xl -z-10 blur-xl"
        />
      )}

      {/* Highlight Pulse */}
      {highlight && !prefersReducedMotion && (
        <motion.div
          className="absolute inset-0 rounded-2xl ring-2 ring-blue-500"
          animate={{
            scale: [1, 1.02, 1],
            opacity: [1, 0.8, 1],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      )}

      {/* Icon */}
      <motion.div
        variants={prefersReducedMotion ? undefined : iconVariants}
        initial="initial"
        animate={isHovered ? 'hover' : 'initial'}
        className={`
          ${variant === 'card' ? 'w-14 h-14 mb-4 mx-auto' : ''}
          ${variant === 'row' ? 'w-12 h-12 flex-shrink-0' : ''}
          ${variant === 'minimal' ? 'w-16 h-16 mx-auto mb-3' : ''}
          flex items-center justify-center
          rounded-xl
          bg-gradient-to-br from-blue-500 to-violet-600
          text-white shadow-lg shadow-blue-500/25
          group-hover:shadow-blue-500/40
          transition-shadow duration-300
        `}
      >
        {icon}
      </motion.div>

      {/* Content */}
      <div className={variant === 'row' ? 'flex-1' : ''}>
        <motion.h3
          className={`
            font-semibold text-slate-900 dark:text-white
            ${variant === 'card' ? 'text-lg mb-2 text-center' : ''}
            ${variant === 'row' ? 'text-base mb-1' : ''}
            ${variant === 'minimal' ? 'text-lg mb-1' : ''}
            group-hover:text-blue-600 dark:group-hover:text-blue-400
            transition-colors duration-200
          `}
        >
          {title}
        </motion.h3>
        
        <motion.p
          className={`
            text-slate-600 dark:text-slate-400 text-sm
            ${variant === 'card' ? 'text-center leading-relaxed' : ''}
            ${variant === 'row' ? 'leading-relaxed' : ''}
            ${variant === 'minimal' ? 'text-center' : ''}
          `}
        >
          {description}
        </motion.p>
      </div>

      {/* Click Hint */}
      {onClick && !prefersReducedMotion && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={isHovered ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }}
          transition={{ duration: 0.2 }}
          className={`
            text-xs text-blue-600 dark:text-blue-400 font-medium
            ${variant === 'card' ? 'mt-3 text-center' : ''}
            ${variant === 'row' ? 'ml-2' : ''}
            ${variant === 'minimal' ? 'mt-2' : ''}
          `}
        >
          Click to explore →
        </motion.div>
      )}
    </motion.div>
  );
}

// Feature Grid Component
interface FeatureGridProps {
  children: ReactNode;
  className?: string;
  columns?: 2 | 3 | 4;
}

export function FeatureGrid({ children, className = '', columns = 3 }: FeatureGridProps) {
  const prefersReducedMotion = useReducedMotion();
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });

  const gridColumns = {
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4',
  };

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0 }}
      animate={isInView ? { opacity: 1 } : { opacity: 0 }}
      transition={{ duration: prefersReducedMotion ? 0 : 0.5 }}
      className={`grid ${gridColumns[columns]} gap-6 ${className}`}
    >
      {children}
    </motion.div>
  );
}
