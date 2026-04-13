'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

interface Particle {
  id: number;
  x: number;
  y: number;
  size: number;
  duration: number;
  delay: number;
}

function generateParticles(count: number): Particle[] {
  return Array.from({ length: count }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: 4 + Math.random() * 8,
    duration: 20 + Math.random() * 20,
    delay: Math.random() * 10
  }));
}

export function AnimatedBackground() {
  const [particles, setParticles] = useState<Particle[]>([]);
  const [mounted, setMounted] = useState(false);

  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => {
    setParticles(generateParticles(25));
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      {/* Animated Gradient Background */}
      <motion.div
        className="absolute inset-0 opacity-30 dark:opacity-20"
        animate={{
          background: [
            'radial-gradient(circle at 0% 0%, rgba(59, 130, 246, 0.4) 0%, transparent 50%), radial-gradient(circle at 100% 100%, rgba(139, 92, 246, 0.4) 0%, transparent 50%)',
            'radial-gradient(circle at 100% 0%, rgba(139, 92, 246, 0.4) 0%, transparent 50%), radial-gradient(circle at 0% 100%, rgba(236, 72, 153, 0.4) 0%, transparent 50%)',
            'radial-gradient(circle at 50% 50%, rgba(236, 72, 153, 0.4) 0%, transparent 50%), radial-gradient(circle at 0% 0%, rgba(59, 130, 246, 0.4) 0%, transparent 50%)',
            'radial-gradient(circle at 0% 0%, rgba(59, 130, 246, 0.4) 0%, transparent 50%), radial-gradient(circle at 100% 100%, rgba(139, 92, 246, 0.4) 0%, transparent 50%)'
          ]
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: 'linear'
        }}
      />

      {/* Floating Particles */}
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          className="absolute rounded-full bg-gradient-to-br from-blue-400/20 to-violet-400/20 dark:from-blue-500/15 dark:to-violet-500/15"
          style={{
            left: `${particle.x}%`,
            top: `${particle.y}%`,
            width: particle.size,
            height: particle.size,
          }}
          animate={{
            y: [-30, 30, -30],
            x: [-20, 20, -20],
            opacity: [0.2, 0.5, 0.2],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: particle.duration,
            delay: particle.delay,
            repeat: Infinity,
            ease: 'easeInOut'
          }}
        />
      ))}

      {/* Grid Pattern */}
      <div 
        className="absolute inset-0 opacity-[0.02] dark:opacity-[0.03]"
        style={{
          backgroundImage: `
            linear-gradient(rgba(59, 130, 246, 0.5) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59, 130, 246, 0.5) 1px, transparent 1px)
          `,
          backgroundSize: '60px 60px'
        }}
      />

      {/* Bottom Gradient Fade */}
      <div className="absolute inset-x-0 bottom-0 h-40 bg-gradient-to-t from-white/50 to-transparent dark:from-slate-900/50" />
    </div>
  );
}

export function StepBackground({ step }: { step: number }) {
  const gradients = [
    'from-blue-500/10 via-violet-500/10 to-purple-500/10',
    'from-violet-500/10 via-purple-500/10 to-pink-500/10',
    'from-purple-500/10 via-pink-500/10 to-rose-500/10',
    'from-pink-500/10 via-rose-500/10 to-orange-500/10',
    'from-rose-500/10 via-orange-500/10 to-amber-500/10',
    'from-orange-500/10 via-amber-500/10 to-yellow-500/10',
    'from-amber-500/10 via-yellow-500/10 to-lime-500/10',
    'from-yellow-500/10 via-lime-500/10 to-green-500/10',
    'from-lime-500/10 via-green-500/10 to-emerald-500/10',
    'from-green-500/10 via-emerald-500/10 to-teal-500/10'
  ];

  return (
    <motion.div
      key={step}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.8 }}
      className={`absolute inset-0 bg-gradient-to-br ${gradients[step - 1] || gradients[0]}`}
    />
  );
}
