'use client';

import { useState, useEffect, useCallback, TouchEvent } from 'react';

interface SwipeState {
  startX: number;
  startY: number;
  startTime: number;
}

interface UseSwipeProps {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  threshold?: number;
  timeout?: number;
}

export function useSwipe({
  onSwipeLeft,
  onSwipeRight,
  threshold = 50,
  timeout = 300
}: UseSwipeProps) {
  const [touchState, setTouchState] = useState<SwipeState | null>(null);

  const onTouchStart = useCallback((e: TouchEvent) => {
    const touch = e.touches[0];
    setTouchState({
      startX: touch.clientX,
      startY: touch.clientY,
      startTime: Date.now()
    });
  }, []);

  const onTouchEnd = useCallback((e: TouchEvent) => {
    if (!touchState) return;

    const touch = e.changedTouches[0];
    const deltaX = touch.clientX - touchState.startX;
    const deltaY = touch.clientY - touchState.startY;
    const deltaTime = Date.now() - touchState.startTime;

    // Check if swipe was fast enough
    if (deltaTime > timeout) {
      setTouchState(null);
      return;
    }

    // Check if horizontal swipe (not vertical scroll)
    if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > threshold) {
      if (deltaX > 0 && onSwipeRight) {
        onSwipeRight();
      } else if (deltaX < 0 && onSwipeLeft) {
        onSwipeLeft();
      }
    }

    setTouchState(null);
  }, [touchState, threshold, timeout, onSwipeLeft, onSwipeRight]);

  const onTouchMove = useCallback((e: TouchEvent) => {
    // Can add logic here to prevent scroll during swipe if needed
  }, []);

  return {
    onTouchStart,
    onTouchEnd,
    onTouchMove
  };
}
