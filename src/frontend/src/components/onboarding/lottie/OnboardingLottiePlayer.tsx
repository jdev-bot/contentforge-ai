'use client';

import { motion, AnimatePresence } from 'framer-motion';
import React from 'react';
import { LottieAnimation } from './LottieAnimation';
import { useReducedMotion } from '../animations/useReducedMotion';

// Import animation data
import { welcomeAnimation } from './animations/welcome';
import { contentCreationAnimation } from './animations/content-creation';
import { aiMagicAnimation } from './animations/ai-magic';
import { teamCollaborationAnimation } from './animations/team-collaboration';
import { analyticsAnimation } from './animations/analytics';
import { successAnimation } from './animations/success';

const animations = {
  welcome: welcomeAnimation,
  contentCreation: contentCreationAnimation,
  aiMagic: aiMagicAnimation,
  teamCollaboration: teamCollaborationAnimation,
  analytics: analyticsAnimation,
  success: successAnimation,
};

type AnimationType = keyof typeof animations;

interface OnboardingLottiePlayerProps {
  animation: AnimationType;
  className?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  autoplay?: boolean;
  loop?: boolean;
}

const sizeClasses = {
  sm: 'w-32 h-32',
  md: 'w-48 h-48',
  lg: 'w-64 h-64',
  xl: 'w-80 h-80',
};

export function OnboardingLottiePlayer({
  animation,
  className = '',
  size = 'md',
  autoplay = true,
  loop = true,
}: OnboardingLottiePlayerProps) {
  const prefersReducedMotion = useReducedMotion();
  const animationData = animations[animation];

  if (prefersReducedMotion) {
    return (
      <div className={`${sizeClasses[size]} ${className} flex items-center justify-center`}>
        <StaticAnimationIcon type={animation} size={size} />
      </div>
    );
  }

  return (
    <div className={`${className} flex flex-col items-center`}>
      <div className={`${sizeClasses[size]} relative`}>
        <AnimatePresence mode="wait">
          <motion.div
            key={animation}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="w-full h-full"
          >
            <LottieAnimation
              animationData={animationData}
              loop={loop}
              autoplay={autoplay}
              className="w-full h-full"
            />
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}

// Static icon fallback for reduced motion
function StaticAnimationIcon({ type, size }: { type: AnimationType; size: 'sm' | 'md' | 'lg' | 'xl' }) {
  const icons: Record<AnimationType, React.ReactNode> = {
    welcome: (
      <svg className="w-full h-full" viewBox="0 0 100 100" fill="none">
        <circle cx="50" cy="50" r="40" fill="url(#welcome-gradient)" />
        <path d="M35 45L45 55L65 35" stroke="white" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        <defs>
          <linearGradient id="welcome-gradient" x1="0" y1="0" x2="100" y2="100">
            <stop stopColor="#3b82f6" />
            <stop offset="1" stopColor="#8b5cf6" />
          </linearGradient>
        </defs>
      </svg>
    ),
    contentCreation: (
      <svg className="w-full h-full" viewBox="0 0 100 100" fill="none">
        <rect x="20" y="20" width="60" height="60" rx="8" fill="url(#content-gradient)" />
        <path d="M35 50H65M35 40H55M35 60H50" stroke="white" strokeWidth="4" strokeLinecap="round" />
        <defs>
          <linearGradient id="content-gradient" x1="0" y1="0" x2="100" y2="100">
            <stop stopColor="#8b5cf6" />
            <stop offset="1" stopColor="#ec4899" />
          </linearGradient>
        </defs>
      </svg>
    ),
    aiMagic: (
      <svg className="w-full h-full" viewBox="0 0 100 100" fill="none">
        <circle cx="50" cy="50" r="40" fill="url(#ai-gradient)" />
        <path d="M50 30L54 42H66L56 50L60 62L50 54L40 62L44 50L34 42H46L50 30Z" fill="white" />
        <defs>
          <linearGradient id="ai-gradient" x1="0" y1="0" x2="100" y2="100">
            <stop stopColor="#ec4899" />
            <stop offset="1" stopColor="#f59e0b" />
          </linearGradient>
        </defs>
      </svg>
    ),
    teamCollaboration: (
      <svg className="w-full h-full" viewBox="0 0 100 100" fill="none">
        <circle cx="50" cy="50" r="40" fill="url(#team-gradient)" />
        <circle cx="35" cy="40" r="8" fill="white" />
        <circle cx="65" cy="40" r="8" fill="white" />
        <circle cx="50" cy="60" r="8" fill="white" />
        <path d="M35 48L50 55L65 48" stroke="white" strokeWidth="3" strokeLinecap="round" />
        <defs>
          <linearGradient id="team-gradient" x1="0" y1="0" x2="100" y2="100">
            <stop stopColor="#10b981" />
            <stop offset="1" stopColor="#06b6d4" />
          </linearGradient>
        </defs>
      </svg>
    ),
    analytics: (
      <svg className="w-full h-full" viewBox="0 0 100 100" fill="none">
        <rect x="20" y="20" width="60" height="60" rx="8" fill="url(#analytics-gradient)" />
        <rect x="30" y="55" width="8" height="20" rx="2" fill="white" />
        <rect x="42" y="40" width="8" height="35" rx="2" fill="white" />
        <rect x="54" y="48" width="8" height="27" rx="2" fill="white" />
        <rect x="66" y="35" width="8" height="40" rx="2" fill="white" />
        <defs>
          <linearGradient id="analytics-gradient" x1="0" y1="0" x2="100" y2="100">
            <stop stopColor="#3b82f6" />
            <stop offset="1" stopColor="#06b6d4" />
          </linearGradient>
        </defs>
      </svg>
    ),
    success: (
      <svg className="w-full h-full" viewBox="0 0 100 100" fill="none">
        <circle cx="50" cy="50" r="40" fill="url(#success-gradient)" />
        <path d="M30 52L42 64L70 36" stroke="white" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" />
        <defs>
          <linearGradient id="success-gradient" x1="0" y1="0" x2="100" y2="100">
            <stop stopColor="#10b981" />
            <stop offset="1" stopColor="#34d399" />
          </linearGradient>
        </defs>
      </svg>
    ),
  };

  return (
    <div className={`${sizeClasses[size]} opacity-50`}>
      {icons[type]}
    </div>
  );
}
