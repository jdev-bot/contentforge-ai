'use client';

import { useState, useCallback, TouchEvent } from 'react';

interface SwipeCallbacks {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  onSwipeStart?: () => void;
  onSwipeEnd?: () => void;
}

interface SwipeOptions {
  threshold?: number;
  preventDefault?: boolean;
  direction?: 'horizontal' | 'vertical' | 'both';
}

/**
 * Hook for handling touch swipe gestures
 */
export function useSwipeGestures(
  callbacks: SwipeCallbacks,
  options: SwipeOptions = {}
) {
  const {
    threshold = 50,
    preventDefault = false,
    direction = 'horizontal',
  } = options;

  const [isSwiping, setIsSwiping] = useState(false);
  const [touchStart, setTouchStart] = useState<{ x: number; y: number } | null>(null);

  const handleTouchStart = useCallback(
    (e: TouchEvent) => {
      if (preventDefault) {
        e.preventDefault();
      }

      const touch = e.touches[0];
      setTouchStart({
        x: touch.clientX,
        y: touch.clientY,
      });
      setIsSwiping(false);

      callbacks.onSwipeStart?.();
    },
    [callbacks, preventDefault]
  );

  const handleTouchMove = useCallback(
    (e: TouchEvent) => {
      if (!touchStart) return;

      if (preventDefault) {
        e.preventDefault();
      }

      setIsSwiping(true);
    },
    [touchStart, preventDefault]
  );

  const handleTouchEnd = useCallback(
    (e: TouchEvent) => {
      if (!touchStart) return;

      if (preventDefault) {
        e.preventDefault();
      }

      const touch = e.changedTouches[0];
      const deltaX = touch.clientX - touchStart.x;
      const deltaY = touch.clientY - touchStart.y;
      const absDeltaX = Math.abs(deltaX);
      const absDeltaY = Math.abs(deltaY);

      // Determine swipe direction
      const isHorizontal = absDeltaX > absDeltaY;
      
      if (direction === 'horizontal' || (direction === 'both' && isHorizontal)) {
        if (absDeltaX > threshold) {
          if (deltaX > 0) {
            callbacks.onSwipeRight?.();
          } else {
            callbacks.onSwipeLeft?.();
          }
        }
      }

      if (direction === 'vertical' || (direction === 'both' && !isHorizontal)) {
        if (absDeltaY > threshold) {
          if (deltaY > 0) {
            callbacks.onSwipeDown?.();
          } else {
            callbacks.onSwipeUp?.();
          }
        }
      }

      callbacks.onSwipeEnd?.();
      setTouchStart(null);
      setIsSwiping(false);
    },
    [touchStart, callbacks, threshold, direction, preventDefault]
  );

  const handleTouchCancel = useCallback(
    (e: TouchEvent) => {
      if (preventDefault) {
        e.preventDefault();
      }
      callbacks.onSwipeEnd?.();
      setTouchStart(null);
      setIsSwiping(false);
    },
    [callbacks, preventDefault]
  );

  return {
    handlers: {
      onTouchStart: handleTouchStart,
      onTouchMove: handleTouchMove,
      onTouchEnd: handleTouchEnd,
      onTouchCancel: handleTouchCancel,
    },
    isSwiping,
  };
}

/**
 * Hook for carousel-style swipe navigation
 */
export function useCarouselSwipe(
  totalSlides: number,
  onSlideChange: (index: number) => void,
  options: SwipeOptions = {}
) {
  const [currentSlide, setCurrentSlide] = useState(0);

  const handleSwipeLeft = useCallback(() => {
    if (currentSlide < totalSlides - 1) {
      const newIndex = currentSlide + 1;
      setCurrentSlide(newIndex);
      onSlideChange(newIndex);
    }
  }, [currentSlide, totalSlides, onSlideChange]);

  const handleSwipeRight = useCallback(() => {
    if (currentSlide > 0) {
      const newIndex = currentSlide - 1;
      setCurrentSlide(newIndex);
      onSlideChange(newIndex);
    }
  }, [currentSlide, onSlideChange]);

  const goToSlide = useCallback(
    (index: number) => {
      if (index >= 0 && index < totalSlides) {
        setCurrentSlide(index);
        onSlideChange(index);
      }
    },
    [totalSlides, onSlideChange]
  );

  const { handlers } = useSwipeGestures(
    {
      onSwipeLeft: handleSwipeLeft,
      onSwipeRight: handleSwipeRight,
    },
    { ...options, direction: 'horizontal' }
  );

  return {
    currentSlide,
    goToSlide,
    handlers,
    canGoNext: currentSlide < totalSlides - 1,
    canGoPrev: currentSlide > 0,
  };
}
