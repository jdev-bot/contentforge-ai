'use client';

import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight, X, SkipForward } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface NavigationControlsProps {
  onPrevious: () => void;
  onNext: () => void;
  onSkip: () => void;
  isFirstStep: boolean;
  isLastStep: boolean;
}

export function NavigationControls({
  onPrevious,
  onNext,
  onSkip,
  isFirstStep,
  isLastStep
}: NavigationControlsProps) {
  return (
    <>
      {/* Exit to Dashboard - Top Right */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fixed top-4 right-4 sm:top-6 sm:right-6 z-50"
      >
        <Button
          variant="ghost"
          size="sm"
          onClick={onSkip}
          className="text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
          leftIcon={<X className="w-4 h-4" />}
          aria-label="Exit onboarding and go to dashboard"
        >
          <span className="hidden sm:inline">Skip Tour</span>
        </Button>
      </motion.div>

      {/* Bottom Navigation Bar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="fixed bottom-0 left-0 right-0 z-50 p-4 sm:p-6"
      >
        <div className="max-w-4xl mx-auto">
          <div className="glass-card rounded-2xl px-4 sm:px-6 py-4 flex items-center justify-between gap-4">
            {/* Previous Button */}
            <Button
              variant="secondary"
              size="md"
              onClick={onPrevious}
              disabled={isFirstStep}
              leftIcon={<ChevronLeft className="w-5 h-5" />}
              className="hidden sm:flex"
            >
              Previous
            </Button>

            {/* Mobile Previous (Icon Only) */}
            <Button
              variant="secondary"
              size="icon"
              onClick={onPrevious}
              disabled={isFirstStep}
              className="sm:hidden"
              aria-label="Previous step"
            >
              <ChevronLeft className="w-5 h-5" />
            </Button>

            {/* Center Info / Skip Button (Mobile Only) */}
            <div className="sm:hidden">
              <Button
                variant="ghost"
                size="sm"
                onClick={onSkip}
                leftIcon={<SkipForward className="w-4 h-4" />}
              >
                Skip
              </Button>
            </div>

            {/* Desktop Skip Button */}
            <div className="hidden sm:block">
              <Button
                variant="ghost"
                size="md"
                onClick={onSkip}
                leftIcon={<SkipForward className="w-4 h-4" />}
                className="text-slate-500"
              >
                Skip Tour
              </Button>
            </div>

            {/* Next / Finish Button */}
            <Button
              variant={isLastStep ? 'success' : 'primary'}
              size="md"
              onClick={onNext}
              rightIcon={isLastStep ? undefined : <ChevronRight className="w-5 h-5" />}
              className="min-w-[120px]"
            >
              {isLastStep ? 'Get Started' : 'Continue'}
            </Button>
          </div>

          {/* Keyboard Navigation Hint */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
            className="hidden sm:flex justify-center mt-3"
          >
            <p className="text-xs text-slate-400 dark:text-slate-500 flex items-center gap-2">
              <span className="flex items-center gap-1">
                <kbd className="px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded text-slate-600 dark:text-slate-400 font-mono text-[10px]">←</kbd>
                <kbd className="px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded text-slate-600 dark:text-slate-400 font-mono text-[10px]">→</kbd>
              </span>
              Navigate
              <span className="mx-1">•</span>
              <kbd className="px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded text-slate-600 dark:text-slate-400 font-mono text-[10px]">Esc</kbd>
              Skip
            </p>
          </motion.div>
        </div>
      </motion.div>
    </>
  );
}
