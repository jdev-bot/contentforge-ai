'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useState, useCallback } from 'react';
import { useReducedMotion } from './useReducedMotion';

interface ConfettiCelebrationProps {
  isActive: boolean;
  onComplete?: () => void;
  particleCount?: number;
  duration?: number;
  className?: string;
  colors?: string[];
}

interface Particle {
  id: number;
  x: number;
  y: number;
  rotation: number;
  scale: number;
  color: string;
  shape: 'square' | 'circle' | 'triangle';
}

const defaultColors = [
  '#3b82f6', // blue
  '#8b5cf6', // violet
  '#ec4899', // pink
  '#10b981', // emerald
  '#f59e0b', // amber
  '#ef4444', // red
  '#06b6d4', // cyan
  '#a855f7', // purple
];

export function ConfettiCelebration({
  isActive,
  onComplete,
  particleCount = 100,
  duration = 3000,
  className = '',
  colors = defaultColors,
}: ConfettiCelebrationProps) {
  const prefersReducedMotion = useReducedMotion();
  const [particles, setParticles] = useState<Particle[]>([]);

  const generateParticles = useCallback(() => {
    const newParticles: Particle[] = [];
    for (let i = 0; i < particleCount; i++) {
      newParticles.push({
        id: i,
        x: Math.random() * window.innerWidth,
        y: -20 - Math.random() * 100,
        rotation: Math.random() * 360,
        scale: 0.5 + Math.random() * 0.5,
        color: colors[Math.floor(Math.random() * colors.length)],
        shape: ['square', 'circle', 'triangle'][Math.floor(Math.random() * 3)] as Particle['shape'],
      });
    }
    return newParticles;
  }, [particleCount, colors]);

  useEffect(() => {
    if (isActive) {
      setParticles(generateParticles());
      
      const timer = setTimeout(() => {
        onComplete?.();
      }, duration);

      return () => clearTimeout(timer);
    } else {
      setParticles([]);
    }
  }, [isActive, duration, onComplete, generateParticles]);

  if (prefersReducedMotion || !isActive) return null;

  return (
    <AnimatePresence>
      {isActive && (
        <div className={`fixed inset-0 pointer-events-none overflow-hidden z-50 ${className}`}>
          {particles.map((particle) => (
            <motion.div
              key={particle.id}
              initial={{
                x: particle.x,
                y: particle.y,
                rotate: particle.rotation,
                scale: 0,
                opacity: 1,
              }}
              animate={{
                y: window.innerHeight + 100,
                x: particle.x + (Math.random() - 0.5) * 300,
                rotate: particle.rotation + Math.random() * 720 - 360,
                scale: particle.scale,
                opacity: [1, 1, 0],
              }}
              exit={{ opacity: 0 }}
              transition={{
                duration: 2 + Math.random() * 2,
                ease: [0.25, 0.46, 0.45, 0.94],
                opacity: {
                  duration: duration / 1000,
                  times: [0, 0.7, 1],
                },
              }}
              className="absolute"
              style={{ color: particle.color }}
            >
              <svg width="12" height="12" viewBox="0 0 12 12">
                {particle.shape === 'circle' ? (
                  <circle cx="6" cy="6" r="6" fill="currentColor" />
                ) : particle.shape === 'triangle' ? (
                  <polygon points="6,0 12,12 0,12" fill="currentColor" />
                ) : (
                  <rect width="12" height="12" rx="2" fill="currentColor" />
                )}
              </svg>
            </motion.div>
          ))}
        </div>
      )}
    </AnimatePresence>
  );
}

// Celebration Badge Component
interface CelebrationBadgeProps {
  children: React.ReactNode;
  show: boolean;
  className?: string;
}

export function CelebrationBadge({ children, show, className = '' }: CelebrationBadgeProps) {
  const prefersReducedMotion = useReducedMotion();

  return (
    <motion.div
      className={`relative inline-block ${className}`}
      animate={show ? {
        scale: [1, 1.1, 1],
      } : {}}
      transition={{
        duration: 0.5,
        ease: [0.34, 1.56, 0.64, 1],
      }}
    >
      {show && !prefersReducedMotion && (
        <>
          {Array.from({ length: 8 }).map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-4 bg-gradient-to-t from-blue-500 to-violet-500 rounded-full"
              style={{
                top: '50%',
                left: '50%',
                transformOrigin: 'center bottom',
              }}
              initial={{ 
                scale: 0, 
                opacity: 1,
                rotate: i * 45,
              }}
              animate={{ 
                scale: [0, 1.5, 0],
                opacity: [1, 1, 0],
                y: [0, -40, -60],
              }}
              transition={{
                duration: 0.8,
                delay: i * 0.05,
                ease: [0.16, 1, 0.3, 1],
              }}
            />
          ))}
          
          <motion.div
            className="absolute inset-0 border-2 border-blue-500 rounded-full"
            initial={{ scale: 1, opacity: 1 }}
            animate={{ scale: 1.5, opacity: 0 }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
          />
        </>
      )}
      
      {children}
    </motion.div>
  );
}

// Success Animation Component
interface SuccessAnimationProps {
  show: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function SuccessAnimation({ show, size = 'md', className = '' }: SuccessAnimationProps) {
  const prefersReducedMotion = useReducedMotion();

  const sizeClasses = {
    sm: 'w-12 h-12',
    md: 'w-16 h-16',
    lg: 'w-24 h-24',
  };

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0, opacity: 0 }}
          transition={{ 
            duration: prefersReducedMotion ? 0 : 0.5,
            ease: [0.34, 1.56, 0.64, 1],
          }}
          className={`${sizeClasses[size]} ${className}`}
        >
          <div className="relative w-full h-full">
            <motion.div
              className="absolute inset-0 rounded-full bg-gradient-to-br from-green-400 to-emerald-500"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.1, duration: 0.3 }}
            />
            
            <svg
              className="absolute inset-0 w-full h-full p-3"
              viewBox="0 0 24 24"
              fill="none"
            >
              <motion.path
                d="M5 13l4 4L19 7"
                stroke="white"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ 
                  delay: 0.3, 
                  duration: prefersReducedMotion ? 0 : 0.5,
                  ease: 'easeOut',
                }}
              />
            </svg>
            
            {!prefersReducedMotion && (
              <>
                {[1, 2].map((i) => (
                  <motion.div
                    key={i}
                    className="absolute inset-0 rounded-full border-2 border-green-400"
                    initial={{ scale: 1, opacity: 0.5 }}
                    animate={{ 
                      scale: 1.5 + i * 0.3, 
                      opacity: 0,
                    }}
                    transition={{
                      duration: 1,
                      delay: 0.2 + i * 0.2,
                      repeat: 0,
                    }}
                  />
                ))}
              </>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
