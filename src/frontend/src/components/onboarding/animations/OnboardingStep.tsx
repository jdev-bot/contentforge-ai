'use client';

import { motion, AnimatePresence, Variants } from 'framer-motion';
import { ReactNode, useEffect, useState } from 'react';
import { useReducedMotion } from './useReducedMotion';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface OnboardingStepProps {
  children: ReactNode;
  step: number;
  totalSteps: number;
  isActive: boolean;
  direction?: 'forward' | 'backward';
  onNext?: () => void;
  onPrev?: () => void;
  onSkip?: () => void;
  title?: string;
  description?: string;
  className?: string;
  showNavigation?: boolean;
  allowSwipe?: boolean;
}

const slideVariants: Variants = {
  enter: (direction: number) => ({
    x: direction > 0 ? 300 : -300,
    opacity: 0,
    scale: 0.95,
  }),
  center: {
    x: 0,
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: [0.16, 1, 0.3, 1], // Custom ease-out
    },
  },
  exit: (direction: number) => ({
    x: direction < 0 ? 300 : -300,
    opacity: 0,
    scale: 0.95,
    transition: {
      duration: 0.4,
      ease: [0.7, 0, 0.84, 0], // Custom ease-in
    },
  }),
};

const contentVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: i * 0.1,
      duration: 0.5,
      ease: [0.16, 1, 0.3, 1],
    },
  }),
};

export function OnboardingStep({
  children,
  step,
  totalSteps,
  isActive,
  direction = 'forward',
  onNext,
  onPrev,
  onSkip,
  title,
  description,
  className = '',
  showNavigation = true,
  allowSwipe = true,
}: OnboardingStepProps) {
  const prefersReducedMotion = useReducedMotion();
  const [touchStart, setTouchStart] = useState<{ x: number; y: number } | null>(null);
  const swipeDirection = direction === 'forward' ? 1 : -1;

  // Handle keyboard navigation
  useEffect(() => {
    if (!isActive) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' && onNext) {
        onNext();
      } else if (e.key === 'ArrowLeft' && onPrev) {
        onPrev();
      } else if (e.key === 'Escape' && onSkip) {
        onSkip();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isActive, onNext, onPrev, onSkip]);

  // Handle swipe gestures
  const handleTouchStart = (e: React.TouchEvent) => {
    if (!allowSwipe) return;
    setTouchStart({
      x: e.touches[0].clientX,
      y: e.touches[0].clientY,
    });
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (!allowSwipe || !touchStart) return;

    const touchEnd = {
      x: e.changedTouches[0].clientX,
      y: e.changedTouches[0].clientY,
    };

    const diffX = touchStart.x - touchEnd.x;
    const diffY = touchStart.y - touchEnd.y;

    // Only handle horizontal swipes (abs diffX > abs diffY)
    if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
      if (diffX > 0 && onNext) {
        onNext(); // Swipe left -> next
      } else if (diffX < 0 && onPrev) {
        onPrev(); // Swipe right -> prev
      }
    }

    setTouchStart(null);
  };

  if (!isActive) return null;

  return (
    <AnimatePresence mode="wait" custom={swipeDirection}>
      <motion.div
        key={step}
        custom={swipeDirection}
        variants={prefersReducedMotion ? undefined : slideVariants}
        initial="enter"
        animate="center"
        exit="exit"
        className={`w-full h-full flex flex-col ${className}`}
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
      >
        {/* Step Header */}
        {(title || description) && (
          <div className="mb-6 text-center">
            {title && (
              <motion.h2
                custom={0}
                variants={prefersReducedMotion ? undefined : contentVariants}
                initial="hidden"
                animate="visible"
                className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white mb-3"
              >
                {title}
              </motion.h2>
            )}
            {description && (
              <motion.p
                custom={1}
                variants={prefersReducedMotion ? undefined : contentVariants}
                initial="hidden"
                animate="visible"
                className="text-slate-600 dark:text-slate-400 text-base sm:text-lg max-w-md mx-auto"
              >
                {description}
              </motion.p>
            )}
          </div>
        )}

        {/* Step Content */}
        <motion.div
          custom={2}
          variants={prefersReducedMotion ? undefined : contentVariants}
          initial="hidden"
          animate="visible"
          className="flex-1 flex flex-col items-center justify-center"
        >
          {children}
        </motion.div>

        {/* Navigation */}
        {showNavigation && (
          <motion.div
            custom={3}
            variants={prefersReducedMotion ? undefined : contentVariants}
            initial="hidden"
            animate="visible"
            className="mt-8 flex items-center justify-between gap-4"
          >
            {/* Skip Button (only on first steps) */}
            {step < totalSteps - 1 && onSkip && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onSkip}
                className="text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
              >
                Skip
              </Button>
            )}
            {step === totalSteps - 1 && <div />} {/* Spacer */}

            {/* Step Counter */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-slate-500 dark:text-slate-400">
                Step {step + 1} of {totalSteps}
              </span>
            </div>

            {/* Navigation Buttons */}
            <div className="flex items-center gap-3">
              {onPrev && step > 0 && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onPrev}
                  leftIcon={<ChevronLeft className="h-4 w-4" />}
                  className="hidden sm:flex"
                >
                  Back
                </Button>
              )}
              
              {onNext && (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={onNext}
                  rightIcon={step < totalSteps - 1 ? <ChevronRight className="h-4 w-4" /> : undefined}
                >
                  {step === totalSteps - 1 ? 'Get Started' : 'Next'}
                </Button>
              )}
            </div>
          </motion.div>
        )}
      </motion.div>
    </AnimatePresence>
  );
}
