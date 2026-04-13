'use client';

import { motion } from 'framer-motion';
import { Rocket, Check, ArrowRight, BookOpen, Users, Sparkles, FileText } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { staggerContainer, staggerItem, celebrationVariants } from '../animations/variants';
import { quickTips } from '../data/steps';

interface CompletionScreenProps {
  onComplete: () => void;
}

export function CompletionScreen({ onComplete }: CompletionScreenProps) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8 py-20">
      {/* Confetti Effect */}
      <ConfettiEffect />

      <motion.div
        variants={staggerContainer}
        initial="initial"
        animate="animate"
        className="max-w-3xl mx-auto text-center"
      >
        {/* Celebration Icon */}
        <motion.div
          variants={celebrationVariants}
          className="mb-8"
        >
          <div className="relative inline-block">
            {/* Glow rings */}
            {[...Array(3)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute inset-0 rounded-full border-2 border-emerald-400/30"
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{
                  scale: [1, 1.5, 1.5],
                  opacity: [0.5, 0, 0]
                }}
                transition={{
                  duration: 2,
                  delay: i * 0.3,
                  repeat: Infinity
                }}
              />
            ))}

            <div className="relative w-24 h-24 sm:w-32 sm:h-32 mx-auto rounded-2xl bg-gradient-to-br from-emerald-500 via-green-500 to-teal-500 flex items-center justify-center shadow-2xl">
              <motion.div
                animate={{ rotate: [0, 10, -10, 0] }}
                transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
              >
                <Rocket className="w-12 h-12 sm:w-16 sm:h-16 text-white" />
              </motion.div>
            </div>
          </div>
        </motion.div>

        {/* Success Badge */}
        <motion.div
          variants={staggerItem}
          className="mb-6"
        >
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 text-sm font-medium">
            <Check className="w-4 h-4" />
            Onboarding Complete!
          </span>
        </motion.div>

        {/* Title */}
        <motion.h1
          variants={staggerItem}
          className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 dark:text-white mb-4"
        >
          You&apos;re All Set!
        </motion.h1>

        {/* Description */}
        <motion.p
          variants={staggerItem}
          className="text-lg sm:text-xl text-slate-600 dark:text-slate-300 mb-10 max-w-xl mx-auto"
        >
          Start creating amazing content with ContentForge AI. Your journey to content excellence begins now.
        </motion.p>

        {/* Quick Tips */}
        <motion.div variants={staggerItem} className="mb-10">
          <h3 className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4">
            Quick Tips to Get Started
          </h3>
          <div className="grid sm:grid-cols-2 gap-4 max-w-2xl mx-auto">
            {quickTips.map((tip, index) => (
              <motion.div
                key={tip.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 + index * 0.1 }}
                whileHover={{ scale: 1.02 }}
                className="glass-card rounded-xl p-4 text-left"
              >
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-violet-500 flex items-center justify-center">
                    <TipIcon name={tip.icon} />
                  </div>
                  <div>
                    <h4 className="font-semibold text-slate-900 dark:text-white text-sm">
                      {tip.title}
                    </h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                      {tip.description}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* CTA Buttons */}
        <motion.div
          variants={staggerItem}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <Button
            variant="success"
            size="lg"
            onClick={onComplete}
            rightIcon={<ArrowRight className="w-5 h-5" />}
            className="min-w-[220px] text-lg"
          >
            Go to Dashboard
          </Button>

          <Button
            variant="secondary"
            size="lg"
            leftIcon={<BookOpen className="w-5 h-5" />}
            className="min-w-[180px]"
          >
            View Docs
          </Button>
        </motion.div>

        {/* Footer Note */}
        <motion.p
          variants={staggerItem}
          className="mt-8 text-sm text-slate-400 dark:text-slate-500"
        >
          Need help? Contact our support team anytime
        </motion.p>
      </motion.div>
    </div>
  );
}

// Confetti Effect Component
function ConfettiEffect() {
  const colors = ['#3b82f6', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b', '#ef4444'];
  const particleCount = 50;

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-10">
      {[...Array(particleCount)].map((_, i) => {
        const color = colors[i % colors.length];
        const delay = Math.random() * 2;
        const duration = 2 + Math.random() * 2;
        const startX = 50 + (Math.random() - 0.5) * 100; // Spread from center
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const endX = startX + (Math.random() - 0.5) * 200;
        const rotation = Math.random() * 720 - 360;

        return (
          <motion.div
            key={i}
            className="absolute"
            style={{
              left: `${startX}%`,
              top: '30%',
              width: 8 + Math.random() * 8,
              height: 8 + Math.random() * 8,
              backgroundColor: color,
              borderRadius: Math.random() > 0.5 ? '50%' : '0%'
            }}
            initial={{ opacity: 0, y: 0, scale: 0, rotate: 0 }}
            animate={{
              opacity: [0, 1, 1, 0],
              y: [-20, 100 + Math.random() * 300],
              x: [0, (i % 2 === 0 ? 1 : -1) * Math.random() * 100],
              scale: [0, 1, 1, 0.5],
              rotate: [0, rotation]
            }}
            transition={{
              duration,
              delay,
              ease: 'easeOut'
            }}
          />
        );
      })}
    </div>
  );
}

// Tip Icon Component
function TipIcon({ name }: { name: string }) {
  const icons: Record<string, React.ComponentType<{ className?: string }>> = {
    Keyboard: Sparkles,
    Zap: Sparkles,
    LayoutTemplate: FileText,
    HelpCircle: Users
  };

  const Icon = icons[name] || Sparkles;
  return <Icon className="w-5 h-5 text-white" />;
}
