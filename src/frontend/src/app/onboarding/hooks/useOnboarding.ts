'use client';

import { useState, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface OnboardingState {
  currentStep: number;
  direction: number;
  completed: boolean;
  skipped: boolean;
  hotspotsRevealed: Record<string, boolean>;
  hasSeenOnboarding: boolean;
}

interface UseOnboardingReturn {
  currentStep: number;
  direction: number;
  totalSteps: number;
  completed: boolean;
  skipped: boolean;
  hotspotsRevealed: Record<string, boolean>;
  hasSeenOnboarding: boolean;
  goToNext: () => void;
  goToPrevious: () => void;
  goToStep: (step: number) => void;
  skipTour: () => void;
  completeTour: () => void;
  toggleHotspot: (hotspotId: string) => void;
  isFirstStep: boolean;
  isLastStep: boolean;
  progress: number;
}

const STORAGE_KEY = 'contentforge-onboarding';
const TOTAL_STEPS = 10;

export function useOnboarding(): UseOnboardingReturn {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  
  const [state, setState] = useState<OnboardingState>({
    currentStep: 1,
    direction: 0,
    completed: false,
    skipped: false,
    hotspotsRevealed: {},
    hasSeenOnboarding: false
  });

  // Load state from localStorage on mount
   
  useEffect(() => {
    setMounted(true);
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        setState(prev => ({
          ...prev,
          ...parsed,
          // Always start at step 1 when explicitly visiting onboarding
          currentStep: 1,
          direction: 0
        }));
      }
    } catch {
      // Silent fail - use defaults
    }
  }, []);

  // Save state to localStorage
  useEffect(() => {
    if (!mounted) return;
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      completed: state.completed,
      skipped: state.skipped,
      hotspotsRevealed: state.hotspotsRevealed,
      hasSeenOnboarding: state.hasSeenOnboarding
    }));
  }, [state.completed, state.skipped, state.hotspotsRevealed, state.hasSeenOnboarding, mounted]);

  const goToNext = useCallback(() => {
    setState(prev => {
      if (prev.currentStep >= TOTAL_STEPS) {
        return prev;
      }
      return {
        ...prev,
        currentStep: prev.currentStep + 1,
        direction: 1
      };
    });
  }, []);

  const goToPrevious = useCallback(() => {
    setState(prev => {
      if (prev.currentStep <= 1) {
        return prev;
      }
      return {
        ...prev,
        currentStep: prev.currentStep - 1,
        direction: -1
      };
    });
  }, []);

  const goToStep = useCallback((step: number) => {
    setState(prev => ({
      ...prev,
      currentStep: Math.max(1, Math.min(step, TOTAL_STEPS)),
      direction: step > prev.currentStep ? 1 : -1
    }));
  }, []);

  const skipTour = useCallback(() => {
    setState(prev => ({
      ...prev,
      skipped: true,
      hasSeenOnboarding: true
    }));
    router.push('/dashboard');
  }, [router]);

  const completeTour = useCallback(() => {
    setState(prev => ({
      ...prev,
      completed: true,
      hasSeenOnboarding: true
    }));
    router.push('/dashboard');
  }, [router]);

  const toggleHotspot = useCallback((hotspotId: string) => {
    setState(prev => ({
      ...prev,
      hotspotsRevealed: {
        ...prev.hotspotsRevealed,
        [hotspotId]: !prev.hotspotsRevealed[hotspotId]
      }
    }));
  }, []);

  const isFirstStep = state.currentStep === 1;
  const isLastStep = state.currentStep === TOTAL_STEPS;
  const progress = (state.currentStep / TOTAL_STEPS) * 100;

  return {
    currentStep: state.currentStep,
    direction: state.direction,
    totalSteps: TOTAL_STEPS,
    completed: state.completed,
    skipped: state.skipped,
    hotspotsRevealed: state.hotspotsRevealed,
    hasSeenOnboarding: state.hasSeenOnboarding,
    goToNext,
    goToPrevious,
    goToStep,
    skipTour,
    completeTour,
    toggleHotspot,
    isFirstStep,
    isLastStep,
    progress
  };
}

// Hook to check if user has seen onboarding (for redirecting)
export function useHasSeenOnboarding(): boolean {
  const [hasSeen, setHasSeen] = useState(false);

   
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        setHasSeen(parsed.hasSeenOnboarding || false);
      }
    } catch {
      setHasSeen(false);
    }
  }, []);

  return hasSeen;
}
