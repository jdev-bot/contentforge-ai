'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState, ReactNode } from 'react';
import { useReducedMotion } from './useReducedMotion';

interface InteractiveHotspotProps {
  children: ReactNode;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  color?: 'blue' | 'green' | 'purple' | 'amber' | 'rose';
  pulse?: boolean;
  ripple?: boolean;
  onClick?: () => void;
  onHover?: (isHovering: boolean) => void;
  onReveal?: (isRevealed: boolean) => void;
  revealContent?: ReactNode;
  tooltip?: string;
  delay?: number;
}

const colorClasses = {
  blue: 'bg-blue-500 shadow-blue-500/50',
  green: 'bg-emerald-500 shadow-emerald-500/50',
  purple: 'bg-violet-500 shadow-violet-500/50',
  amber: 'bg-amber-500 shadow-amber-500/50',
  rose: 'bg-rose-500 shadow-rose-500/50',
};

export function InteractiveHotspot({
  children,
  className = '',
  size = 'md',
  color = 'blue',
  pulse = true,
  ripple = true,
  onClick,
  onHover,
  onReveal,
  revealContent,
  tooltip,
  delay = 0,
}: InteractiveHotspotProps) {
  const prefersReducedMotion = useReducedMotion();
  const [isHovered, setIsHovered] = useState(false);
  const [isRevealed, setIsRevealed] = useState(false);
  const [ripples, setRipples] = useState<Array<{ x: number; y: number; id: number }>>([]);

  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
  };

  const handleMouseEnter = () => {
    setIsHovered(true);
    onHover?.(true);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    onHover?.(false);
  };

  const handleClick = (e: React.MouseEvent) => {
    if (ripple && !prefersReducedMotion) {
      const rect = e.currentTarget.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const id = Date.now();
      
      setRipples(prev => [...prev, { x, y, id }]);
      setTimeout(() => {
        setRipples(prev => prev.filter(r => r.id !== id));
      }, 800);
    }

    if (revealContent) {
      const newRevealed = !isRevealed;
      setIsRevealed(newRevealed);
      onReveal?.(newRevealed);
    }

    onClick?.();
  };

  return (
    <motion.div
      className={`relative inline-block ${className}`}
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ 
        delay, 
        duration: prefersReducedMotion ? 0 : 0.3,
        ease: [0.34, 1.56, 0.64, 1],
      }}
    >
      <motion.div
        className={`
          relative ${sizeClasses[size]} rounded-full cursor-pointer
          ${colorClasses[color]}
          shadow-lg
          flex items-center justify-center
          transition-transform duration-200
        `}
        whileHover={prefersReducedMotion ? undefined : { scale: 1.1 }}
        whileTap={prefersReducedMotion ? undefined : { scale: 0.95 }}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onClick={handleClick}
        title={tooltip}
      >
        {pulse && !prefersReducedMotion && (
          <>
            {[1, 2].map((i) => (
              <motion.div
                key={i}
                className={`absolute inset-0 rounded-full ${colorClasses[color].split(' ')[0]} opacity-40`}
                initial={{ scale: 1, opacity: 0.4 }}
                animate={{
                  scale: 1.5 + i * 0.2,
                  opacity: 0,
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  delay: i * 0.5,
                  ease: 'easeOut',
                }}
              />
            ))}
          </>
        )}

        {ripples.map((ripple) => (
          <motion.span
            key={ripple.id}
            className="absolute rounded-full bg-white/30 pointer-events-none"
            style={{
              left: ripple.x - 5,
              top: ripple.y - 5,
              width: 10,
              height: 10,
            }}
            initial={{ scale: 0, opacity: 1 }}
            animate={{ scale: 8, opacity: 0 }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          />
        ))}

        <div className="relative z-10 text-white">
          {children}
        </div>

        {!prefersReducedMotion && (
          <motion.div
            className={`absolute inset-0 rounded-full ${colorClasses[color].split(' ')[0]} blur-xl`}
            initial={{ opacity: 0 }}
            animate={{ opacity: isHovered ? 0.5 : 0 }}
            transition={{ duration: 0.3 }}
          />
        )}
      </motion.div>

      <AnimatePresence>
        {isRevealed && revealContent && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.9 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="absolute top-full mt-3 left-1/2 -translate-x-1/2 z-20"
          >
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-xl p-4 border border-slate-200 dark:border-slate-700 min-w-[200px]">
              <div className="absolute -top-2 left-1/2 -translate-x-1/2 w-4 h-4 bg-white dark:bg-slate-800 border-l border-t border-slate-200 dark:border-slate-700 rotate-45" />
              
              {revealContent}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// Pulsing Ring Component
interface PulsingRingProps {
  children: ReactNode;
  className?: string;
  color?: 'blue' | 'green' | 'purple' | 'amber';
  duration?: number;
}

export function PulsingRing({ 
  children, 
  className = '', 
  color = 'blue',
  duration = 2,
}: PulsingRingProps) {
  const prefersReducedMotion = useReducedMotion();

  const colorMap = {
    blue: 'border-blue-500',
    green: 'border-emerald-500',
    purple: 'border-violet-500',
    amber: 'border-amber-500',
  };

  return (
    <div className={`relative inline-block ${className}`}>
      {!prefersReducedMotion && (
        <>
          {[1, 2].map((i) => (
            <motion.div
              key={i}
              className={`absolute inset-0 rounded-full border-2 ${colorMap[color]}`}
              initial={{ scale: 1, opacity: 0.6 }}
              animate={{
                scale: 1.3 + i * 0.2,
                opacity: 0,
              }}
              transition={{
                duration,
                repeat: Infinity,
                delay: i * (duration / 3),
                ease: 'easeOut',
              }}
            />
          ))}
        </>
      )}
      
      <div className="relative z-10">{children}</div>
    </div>
  );
}

// Hover Preview Component
interface HoverPreviewProps {
  children: ReactNode;
  preview: ReactNode;
  className?: string;
  delay?: number;
}

export function HoverPreview({ children, preview, className = '', delay = 300 }: HoverPreviewProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const prefersReducedMotion = useReducedMotion();

  const handleMouseEnter = () => {
    setIsHovered(true);
    const timer = setTimeout(() => {
      setShowPreview(true);
    }, delay);
    return () => clearTimeout(timer);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    setShowPreview(false);
  };

  return (
    <div 
      className={`relative ${className}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {children}
      
      <AnimatePresence>
        {showPreview && isHovered && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            transition={{ 
              duration: prefersReducedMotion ? 0 : 0.2,
              ease: [0.16, 1, 0.3, 1],
            }}
            className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-30"
          >
            <div className="bg-slate-900 dark:bg-slate-800 text-white px-4 py-2 rounded-lg shadow-xl text-sm whitespace-nowrap">
              {preview}
              <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-900 dark:border-t-slate-800" />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
