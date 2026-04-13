'use client';

import Lottie, { LottieComponentProps } from 'lottie-react';
import { useReducedMotion } from '../animations/useReducedMotion';
import { CSSProperties } from 'react';

interface LottieAnimationProps {
  animationData: object;
  className?: string;
  style?: CSSProperties;
  loop?: boolean;
  autoplay?: boolean;
  onComplete?: () => void;
}

export function LottieAnimation({
  animationData,
  className = '',
  style = {},
  loop = true,
  autoplay = true,
  onComplete,
}: LottieAnimationProps) {
  const prefersReducedMotion = useReducedMotion();

  // Disable animation for users who prefer reduced motion
  if (prefersReducedMotion) {
    return (
      <div 
        className={`${className} flex items-center justify-center bg-slate-100 dark:bg-slate-800 rounded-lg`}
        style={style}
      >
        <div className="text-slate-400">
          <svg className="w-16 h-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
      </div>
    );
  }

  const lottieProps: LottieComponentProps = {
    animationData,
    loop,
    autoplay,
    className,
    style,
  };

  return (
    <div style={style} className={className}>
      <Lottie {...lottieProps} />
    </div>
  );
}
