'use client';

import { useEffect, useCallback } from 'react';

interface UseKeyboardNavigationProps {
  onNext: () => void;
  onPrevious: () => void;
  onSkip?: () => void;
  isEnabled?: boolean;
  isFirstStep?: boolean;
  isLastStep?: boolean;
}

export function useKeyboardNavigation({
  onNext,
  onPrevious,
  onSkip,
  isEnabled = true,
  isFirstStep = false,
  isLastStep = false
}: UseKeyboardNavigationProps): void {
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (!isEnabled) return;

    switch (event.key) {
      case 'ArrowRight':
      case 'ArrowDown':
        if (!isLastStep) {
          event.preventDefault();
          onNext();
        }
        break;
      
      case 'ArrowLeft':
      case 'ArrowUp':
        if (!isFirstStep) {
          event.preventDefault();
          onPrevious();
        }
        break;
      
      case 'Escape':
        if (onSkip) {
          event.preventDefault();
          onSkip();
        }
        break;
      
      case 'Enter':
        if (isLastStep) {
          event.preventDefault();
          onNext(); // This will trigger completion
        }
        break;
      
      case 'Home':
        event.preventDefault();
        // Could add goToFirst callback
        break;
      
      case 'End':
        event.preventDefault();
        // Could add goToLast callback
        break;
    }
  }, [isEnabled, isFirstStep, isLastStep, onNext, onPrevious, onSkip]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);
}
