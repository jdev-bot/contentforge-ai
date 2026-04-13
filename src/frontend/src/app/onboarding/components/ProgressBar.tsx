'use client';

import { motion } from 'framer-motion';
import { Check } from 'lucide-react';

interface ProgressBarProps {
  currentStep: number;
  totalSteps: number;
  progress: number;
}

export function ProgressBar({ currentStep, totalSteps, progress }: ProgressBarProps) {
  return (
    <div className="fixed top-0 left-0 right-0 z-50 px-4 sm:px-6 lg:px-8 pt-4">
      <div className="max-w-4xl mx-auto">
        {/* Progress Info */}
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-slate-600 dark:text-slate-400">
            Step {currentStep} of {totalSteps}
          </span>
          <span className="text-sm font-medium text-slate-600 dark:text-slate-400">
            {Math.round(progress)}%
          </span>
        </div>

        {/* Segmented Progress Bar */}
        <div className="relative flex items-center gap-1">
          {Array.from({ length: totalSteps }, (_, i) => {
            const stepNum = i + 1;
            const isCompleted = stepNum < currentStep;
            const isCurrent = stepNum === currentStep;
            const isFuture = stepNum > currentStep;

            return (
              <motion.div
                key={stepNum}
                className={`
                  relative flex-1 h-2 rounded-full overflow-hidden transition-all duration-300
                  ${isCompleted ? 'bg-emerald-500' : ''}
                  ${isCurrent ? 'bg-slate-200 dark:bg-slate-700' : ''}
                  ${isFuture ? 'bg-slate-200 dark:bg-slate-700' : ''}
                `}
                initial={false}
                animate={{
                  scale: isCurrent ? [1, 1.05, 1] : 1,
                }}
                transition={{
                  duration: 0.5,
                  repeat: isCurrent ? Infinity : 0,
                  repeatDelay: 1
                }}
              >
                {/* Fill Animation for Current Step */}
                {isCurrent && (
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-blue-500 to-violet-500 rounded-full"
                    initial={{ width: '0%' }}
                    animate={{ width: '100%' }}
                    transition={{
                      duration: 5,
                      ease: 'linear',
                      repeat: Infinity
                    }}
                  />
                )}

                {/* Completed Checkmark */}
                {isCompleted && (
                  <motion.div
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="absolute inset-0 flex items-center justify-center"
                  >
                    <Check className="w-3 h-3 text-white" />
                  </motion.div>
                )}
              </motion.div>
            );
          })}
        </div>

        {/* Step Labels (Mobile: Current Only, Desktop: All) */}
        <div className="hidden sm:flex justify-between mt-3 px-1">
          {Array.from({ length: totalSteps }, (_, i) => {
            const stepNum = i + 1;
            const isCompleted = stepNum < currentStep;
            const isCurrent = stepNum === currentStep;
            
            // Only show first, current, and last on desktop to avoid crowding
            if (stepNum !== 1 && stepNum !== currentStep && stepNum !== totalSteps) {
              return <div key={stepNum} className="w-8" />;
            }

            return (
              <motion.div
                key={stepNum}
                className={`
                  text-xs font-medium transition-colors duration-300
                  ${isCurrent ? 'text-blue-600 dark:text-blue-400' : ''}
                  ${isCompleted ? 'text-emerald-600 dark:text-emerald-400' : ''}
                  ${!isCurrent && !isCompleted ? 'text-slate-400 dark:text-slate-600' : ''}
                `}
                animate={isCurrent ? { opacity: [0.7, 1, 0.7] } : {}}
                transition={{ duration: 2, repeat: Infinity }}
              >
                {stepNum === 1 && 'Start'}
                {stepNum === currentStep && stepNum !== 1 && stepNum !== totalSteps && `Step ${stepNum}`}
                {stepNum === totalSteps && 'Finish'}
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
