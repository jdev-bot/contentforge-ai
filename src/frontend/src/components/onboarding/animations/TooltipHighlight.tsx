'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState, useRef, useEffect, ReactNode } from 'react';
import { useReducedMotion } from './useReducedMotion';
import { X } from 'lucide-react';

interface TooltipHighlightProps {
  children: ReactNode;
  isActive: boolean;
  title?: string;
  description?: string;
  position?: 'top' | 'bottom' | 'left' | 'right';
  onDismiss?: () => void;
  spotlightSize?: 'sm' | 'md' | 'lg' | 'full';
  pulseRing?: boolean;
  className?: string;
  arrow?: boolean;
}

export function TooltipHighlight({
  children,
  isActive,
  title,
  description,
  position = 'bottom',
  onDismiss,
  spotlightSize = 'md',
  pulseRing = true,
  className = '',
  arrow = true,
}: TooltipHighlightProps) {
  const prefersReducedMotion = useReducedMotion();
  const containerRef = useRef<HTMLDivElement>(null);
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });

  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-20 h-20',
    full: 'inset-0',
  };

  const tooltipPositionClasses = {
    top: 'bottom-full mb-3',
    bottom: 'top-full mt-3',
    left: 'right-full mr-3',
    right: 'left-full ml-3',
  };

  useEffect(() => {
    if (isActive && containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      setTooltipPosition({ top: rect.bottom + 12, left: rect.left + rect.width / 2 });
    }
  }, [isActive, position]);

  return (
    <div ref={containerRef} className={`relative inline-block ${className}`}>
      <AnimatePresence>
        {isActive && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="fixed inset-0 bg-black/50 z-40 pointer-events-none"
            />

            {spotlightSize !== 'full' && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
                className={`absolute ${sizeClasses[spotlightSize]} rounded-full border-2 border-blue-400 pointer-events-none z-50`}
                style={{
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                }}
              >
                {pulseRing && !prefersReducedMotion && (
                  <>
                    {[1, 2, 3].map((i) => (
                      <motion.div
                        key={i}
                        className="absolute inset-0 rounded-full border-2 border-blue-400"
                        initial={{ scale: 1, opacity: 0.6 }}
                        animate={{
                          scale: 1.5 + i * 0.3,
                          opacity: 0,
                        }}
                        transition={{
                          duration: 2,
                          repeat: Infinity,
                          delay: i * 0.4,
                          ease: 'easeOut',
                        }}
                      />
                    ))}
                  </>
                )}
              </motion.div>
            )}

            {(title || description) && (
              <motion.div
                data-tooltip
                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 10, scale: 0.95 }}
                transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
                className={`absolute z-50 ${tooltipPositionClasses[position]}`}
                style={{
                  position: 'fixed',
                  top: tooltipPosition.top,
                  left: tooltipPosition.left,
                }}
              >
                <div className="bg-slate-900 dark:bg-slate-800 text-white px-4 py-3 rounded-xl shadow-xl max-w-xs">
                  <div className="flex items-start justify-between gap-2">
                    {title && (
                      <h4 className="font-semibold text-sm">{title}</h4>
                    )}
                    {onDismiss && (
                      <button
                        onClick={onDismiss}
                        className="text-slate-400 hover:text-white transition-colors p-0.5 -mr-1"
                        aria-label="Dismiss tooltip"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                  
                  {description && (
                    <p className="text-slate-300 text-sm mt-1 leading-relaxed">
                      {description}
                    </p>
                  )}
                </div>
              </motion.div>
            )}
          </>
        )}
      </AnimatePresence>

      {children}
    </div>
  );
}

export function useSequentialHighlight(steps: Array<{ target: string; title: string; description: string; position?: 'top' | 'bottom' | 'left' | 'right' }>) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isActive, setIsActive] = useState(false);

  const start = () => {
    setCurrentStep(0);
    setIsActive(true);
  };

  const next = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      setIsActive(false);
    }
  };

  const prev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const dismiss = () => {
    setIsActive(false);
  };

  return {
    currentStep,
    isActive,
    start,
    next,
    prev,
    dismiss,
    currentHighlight: steps[currentStep],
  };
}
