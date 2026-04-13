'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useReducedMotion } from './useReducedMotion';
import { Check } from 'lucide-react';

interface ProgressIndicatorProps {
  currentStep: number;
  totalSteps: number;
  className?: string;
  variant?: 'bar' | 'dots' | 'steps';
  showPercentage?: boolean;
  onStepClick?: (step: number) => void;
  stepLabels?: string[];
}

export function ProgressIndicator({
  currentStep,
  totalSteps,
  className = '',
  variant = 'bar',
  showPercentage = false,
  onStepClick,
  stepLabels = [],
}: ProgressIndicatorProps) {
  const prefersReducedMotion = useReducedMotion();
  const progress = Math.min(((currentStep + 1) / totalSteps) * 100, 100);

  // Bar variant
  if (variant === 'bar') {
    return (
      <div className={`w-full ${className}`}>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
            Progress
          </span>
          {showPercentage && (
            <span className="text-sm font-medium text-slate-900 dark:text-white">
              {Math.round(progress)}%
            </span>
          )}
        </div>
        
        <div className="relative h-3 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
          {/* Background Pattern */}
          <div className="absolute inset-0 opacity-20">
            <div 
              className="h-full w-full"
              style={{
                backgroundImage: 'repeating-linear-gradient(90deg, transparent, transparent 10px, rgba(255,255,255,0.3) 10px, rgba(255,255,255,0.3) 20px)',
              }}
            />
          </div>
          
          {/* Progress Fill */}
          <motion.div
            className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-blue-500 via-violet-500 to-purple-500"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{
              duration: prefersReducedMotion ? 0 : 0.5,
              ease: [0.16, 1, 0.3, 1],
            }}
          >
            {/* Animated Shine Effect */}
            {!prefersReducedMotion && (
              <motion.div
                className="absolute inset-0 rounded-full"
                style={{
                  background: 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.4) 50%, transparent 100%)',
                }}
                animate={{
                  x: ['-100%', '200%'],
                }}
                transition={{
                  duration: 1.5,
                  repeat: Infinity,
                  repeatDelay: 1,
                  ease: 'easeInOut',
                }}
              />
            )}
            
            {/* Glow Effect */}
            <div className="absolute inset-0 rounded-full shadow-[0_0_20px_rgba(139,92,246,0.5)]" />
          </motion.div>
          
          {/* Step Markers */}
          {Array.from({ length: totalSteps }).map((_, i) => {
            const isCompleted = i < currentStep;
            const isCurrent = i === currentStep;
            
            return (
              <motion.div
                key={i}
                className={`
                  absolute top-1/2 -translate-y-1/2 w-4 h-4 rounded-full
                  border-2 border-white dark:border-slate-800
                  ${isCompleted ? 'bg-green-500' : isCurrent ? 'bg-blue-500' : 'bg-slate-300 dark:bg-slate-600'}
                  cursor-pointer transition-colors duration-200
                `}
                style={{ left: `${((i + 1) / totalSteps) * 100}%`, transform: 'translate(-50%, -50%)' }}
                onClick={() => onStepClick?.(i)}
                whileHover={prefersReducedMotion ? undefined : { scale: 1.2 }}
                whileTap={prefersReducedMotion ? undefined : { scale: 0.95 }}
                initial={false}
                animate={isCurrent ? {
                  scale: [1, 1.2, 1],
                  boxShadow: [
                    '0 0 0 0 rgba(59, 130, 246, 0.4)',
                    '0 0 0 8px rgba(59, 130, 246, 0)',
                  ],
                } : {}}
                transition={isCurrent ? {
                  duration: 1.5,
                  repeat: Infinity,
                } : {}}
              >
                {isCompleted && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="flex items-center justify-center w-full h-full"
                  >
                    <Check className="w-2.5 h-2.5 text-white" />
                  </motion.div>
                )}
              </motion.div>
            );
          })}
        </div>
      </div>
    );
  }

  // Dots variant
  if (variant === 'dots') {
    return (
      <div className={`flex items-center justify-center gap-2 ${className}`}>
        {Array.from({ length: totalSteps }).map((_, i) => {
          const isCompleted = i < currentStep;
          const isCurrent = i === currentStep;
          
          return (
            <motion.button
              key={i}
              onClick={() => onStepClick?.(i)}
              className={`
                relative w-3 h-3 rounded-full transition-colors duration-200
                ${isCompleted 
                  ? 'bg-green-500' 
                  : isCurrent 
                    ? 'bg-blue-500' 
                    : 'bg-slate-300 dark:bg-slate-600 hover:bg-slate-400 dark:hover:bg-slate-500'
                }
              `}
              whileHover={prefersReducedMotion ? undefined : { scale: 1.3 }}
              whileTap={prefersReducedMotion ? undefined : { scale: 0.9 }}
              animate={isCurrent ? {
                scale: [1, 1.3, 1],
              } : {}}
              transition={isCurrent ? {
                duration: 1,
                repeat: Infinity,
                ease: 'easeInOut',
              } : {}}
              aria-label={`Go to step ${i + 1}`}
              aria-current={isCurrent ? 'step' : undefined}
            >
              {/* Pulse Ring */}
              {isCurrent && !prefersReducedMotion && (
                <span className="absolute inset-0 rounded-full animate-ping bg-blue-400 opacity-75" />
              )}
            </motion.button>
          );
        })}
      </div>
    );
  }

  // Steps variant
  return (
    <div className={`w-full ${className}`}>
      <div className="relative">
        {/* Progress Line Background */}
        <div className="absolute top-5 left-0 right-0 h-0.5 bg-slate-200 dark:bg-slate-700 -z-10" />
        
        {/* Progress Line Fill */}
        <motion.div
          className="absolute top-5 left-0 h-0.5 bg-gradient-to-r from-blue-500 to-violet-600 -z-10"
          initial={{ width: 0 }}
          animate={{ width: `${(currentStep / (totalSteps - 1)) * 100}%` }}
          transition={{
            duration: prefersReducedMotion ? 0 : 0.5,
            ease: [0.16, 1, 0.3, 1],
          }}
        />
        
        {/* Steps */}
        <div className="flex justify-between">
          {Array.from({ length: totalSteps }).map((_, i) => {
            const isCompleted = i < currentStep;
            const isCurrent = i === currentStep;
            const isUpcoming = i > currentStep;
            
            return (
              <motion.button
                key={i}
                onClick={() => onStepClick?.(i)}
                disabled={isUpcoming && !onStepClick}
                className="flex flex-col items-center group"
                whileHover={prefersReducedMotion ? undefined : { y: -2 }}
              >
                {/* Step Circle */}
                <motion.div
                  className={`
                    w-10 h-10 rounded-full flex items-center justify-center
                    text-sm font-semibold transition-colors duration-200
                    ${isCompleted 
                      ? 'bg-green-500 text-white' 
                      : isCurrent 
                        ? 'bg-blue-500 text-white ring-4 ring-blue-500/20'
                        : 'bg-white dark:bg-slate-800 text-slate-400 border-2 border-slate-300 dark:border-slate-600'
                    }
                  `}
                  animate={isCurrent ? {
                    boxShadow: [
                      '0 0 0 0 rgba(59, 130, 246, 0.4)',
                      '0 0 0 8px rgba(59, 130, 246, 0)',
                    ],
                  } : {}}
                  transition={isCurrent ? {
                    duration: 1.5,
                    repeat: Infinity,
                  } : {}}
                >
                  <AnimatePresence mode="wait">
                    {isCompleted ? (
                      <motion.div
                        key="check"
                        initial={{ scale: 0, rotate: -180 }}
                        animate={{ scale: 1, rotate: 0 }}
                        exit={{ scale: 0 }}
                        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                      >
                        <Check className="w-5 h-5" />
                      </motion.div>
                    ) : (
                      <motion.span
                        key="number"
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        exit={{ scale: 0 }}
                      >
                        {i + 1}
                      </motion.span>
                    )}
                  </AnimatePresence>
                </motion.div>
                
                {/* Step Label */}
                {stepLabels[i] && (
                  <span
                    className={`
                      mt-2 text-xs font-medium transition-colors duration-200
                      ${isCurrent 
                        ? 'text-blue-600 dark:text-blue-400' 
                        : isCompleted 
                          ? 'text-green-600 dark:text-green-400'
                          : 'text-slate-400 group-hover:text-slate-500 dark:group-hover:text-slate-400'
                      }
                    `}
                  >
                    {stepLabels[i]}
                  </span>
                )}
              </motion.button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
