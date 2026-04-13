'use client';

import { motion } from 'framer-motion';
import { Sparkles, ArrowRight, Zap, Shield, Globe } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { staggerContainer, staggerItem, logoReveal } from '../animations/variants';

interface WelcomeScreenProps {
  onStart: () => void;
  onSkip: () => void;
}

export function WelcomeScreen({ onStart, onSkip }: WelcomeScreenProps) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8 py-20">
      <motion.div
        variants={staggerContainer}
        initial="initial"
        animate="animate"
        className="max-w-3xl mx-auto text-center"
      >
        {/* Logo Animation */}
        <motion.div
          variants={logoReveal}
          className="mb-8"
        >
          <div className="relative inline-block">
            {/* Glow Effect */}
            <motion.div
              className="absolute inset-0 blur-3xl bg-gradient-to-r from-blue-500 to-violet-500 opacity-50"
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.3, 0.5, 0.3]
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: 'easeInOut'
              }}
            />
            
            {/* Logo Container */}
            <div className="relative w-24 h-24 sm:w-32 sm:h-32 mx-auto rounded-2xl bg-gradient-to-br from-blue-600 via-violet-600 to-purple-600 flex items-center justify-center shadow-2xl">
              <motion.div
                animate={{ rotate: [0, 10, -10, 0] }}
                transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
              >
                <Sparkles className="w-12 h-12 sm:w-16 sm:h-16 text-white" />
              </motion.div>
            </div>
          </div>
        </motion.div>

        {/* Main Heading */}
        <motion.h1
          variants={staggerItem}
          className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6"
        >
          <span className="bg-gradient-to-r from-blue-600 via-violet-600 to-purple-600 bg-clip-text text-transparent">
            Welcome to
          </span>
          <br />
          <motion.span
            className="bg-gradient-to-r from-violet-600 via-purple-600 to-pink-600 bg-clip-text text-transparent"
            animate={{
              backgroundPosition: ['0% 50%', '100% 50%', '0% 50%']
            }}
            transition={{
              duration: 5,
              repeat: Infinity,
              ease: 'linear'
            }}
            style={{
              backgroundSize: '200% auto'
            }}
          >
            ContentForge AI
          </motion.span>
        </motion.h1>

        {/* Tagline */}
        <motion.p
          variants={staggerItem}
          className="text-xl sm:text-2xl text-slate-600 dark:text-slate-300 mb-4 max-w-2xl mx-auto"
        >
          Your Content Creation Journey Begins
        </motion.p>

        {/* Description */}
        <motion.p
          variants={staggerItem}
          className="text-base sm:text-lg text-slate-500 dark:text-slate-400 mb-10 max-w-xl mx-auto leading-relaxed"
        >
          Transform your ideas into engaging content across 20+ platforms with the power of artificial intelligence.
        </motion.p>

        {/* Feature Pills */}
        <motion.div
          variants={staggerItem}
          className="flex flex-wrap justify-center gap-3 mb-12"
        >
          {[
            { icon: Zap, text: 'AI-Powered' },
            { icon: Globe, text: '20+ Platforms' },
            { icon: Shield, text: 'Enterprise Ready' }
          ].map((feature, index) => (
            <motion.div
              key={feature.text}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.8 + index * 0.1, duration: 0.3 }}
              className="flex items-center gap-2 px-4 py-2 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-sm font-medium"
            >
              <feature.icon className="w-4 h-4 text-blue-500" />
              {feature.text}
            </motion.div>
          ))}
        </motion.div>

        {/* CTA Buttons */}
        <motion.div
          variants={staggerItem}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <Button
            variant="primary"
            size="lg"
            onClick={onStart}
            rightIcon={<ArrowRight className="w-5 h-5" />}
            className="min-w-[200px] text-lg"
          >
            Start Tour
          </Button>

          <Button
            variant="ghost"
            size="lg"
            onClick={onSkip}
            className="min-w-[160px]"
          >
            Skip for Now
          </Button>
        </motion.div>

        {/* Trust Indicators */}
        <motion.div
          variants={staggerItem}
          className="mt-12 pt-8 border-t border-slate-200 dark:border-slate-800"
        >
          <p className="text-sm text-slate-400 dark:text-slate-500 mb-4">
            Trusted by content creators worldwide
          </p>
          <div className="flex items-center justify-center gap-8 opacity-50">
            {/* Placeholder for partner logos */}
            <div className="flex gap-2">
              {[...Array(5)].map((_, i) => (
                <div
                  key={i}
                  className="w-8 h-8 rounded-full bg-slate-300 dark:bg-slate-700"
                />
              ))}
            </div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
