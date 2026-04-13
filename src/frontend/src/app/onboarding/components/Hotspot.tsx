'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';

interface HotspotProps {
  id: string;
  x: number;
  y: number;
  title: string;
  description: string;
  isRevealed?: boolean;
  onToggle?: (id: string) => void;
  index: number;
}

export function Hotspot({
  id,
  x,
  y,
  title,
  description,
  isRevealed = false,
  onToggle,
  index
}: HotspotProps) {
  const [isHovered, setIsHovered] = useState(false);

  const handleClick = () => {
    onToggle?.(id);
  };

  return (
    <motion.div
      className="absolute"
      style={{ left: `${x}%`, top: `${y}%` }}
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ delay: 0.5 + index * 0.15, duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
    >
      {/* Hotspot Button */}
      <button
        onClick={handleClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className="relative w-10 h-10 -translate-x-1/2 -translate-y-1/2 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 rounded-full"
        aria-label={`${title}: ${description}`}
        aria-expanded={isRevealed}
      >
        {/* Pulsing Ring */}
        <motion.div
          className="absolute inset-0 rounded-full bg-gradient-to-r from-blue-500 to-violet-500"
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.6, 0.2, 0.6],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />

        {/* Inner Ring */}
        <motion.div
          className="absolute inset-1 rounded-full bg-gradient-to-r from-blue-400 to-violet-400"
          animate={{
            scale: isHovered || isRevealed ? 1.1 : 1,
          }}
          transition={{ duration: 0.2 }}
        />

        {/* Center Dot with Number */}
        <motion.div
          className="absolute inset-2 rounded-full bg-white dark:bg-slate-800 flex items-center justify-center shadow-lg"
          animate={{
            scale: isHovered || isRevealed ? 1.1 : 1,
          }}
          transition={{ duration: 0.2 }}
        >
          <span className="text-sm font-bold bg-gradient-to-r from-blue-600 to-violet-600 bg-clip-text text-transparent">
            {index + 1}
          </span>
        </motion.div>
      </button>

      {/* Tooltip */}
      <AnimatePresence>
        {(isHovered || isRevealed) && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            transition={{ duration: 0.2, ease: [0.34, 1.56, 0.64, 1] }}
            className="absolute left-1/2 top-full mt-3 -translate-x-1/2 z-50 w-64"
          >
            <div className="glass-card rounded-xl p-4 shadow-xl border border-white/20 dark:border-white/10">
              <h4 className="font-semibold text-slate-900 dark:text-white mb-1 flex items-center gap-2">
                <span className="flex items-center justify-center w-5 h-5 rounded-full bg-gradient-to-r from-blue-500 to-violet-500 text-white text-xs font-bold">
                  {index + 1}
                </span>
                {title}
              </h4>
              <p className="text-sm text-slate-600 dark:text-slate-300">
                {description}
              </p>
            </div>

            {/* Tooltip Arrow */}
            <div className="absolute -top-2 left-1/2 -translate-x-1/2 w-4 h-4 bg-white/10 dark:bg-slate-800/10 rotate-45 border-t border-l border-white/20 dark:border-white/10" />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

interface HotspotDemoProps {
  hotspots: Array<{
    id: string;
    x: number;
    y: number;
    title: string;
    description: string;
  }>;
  revealedHotspots: Record<string, boolean>;
  onToggleHotspot: (id: string) => void;
}

export function HotspotDemo({ hotspots, revealedHotspots, onToggleHotspot }: HotspotDemoProps) {
  return (
    <div className="relative w-full h-64 sm:h-80 bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800/50 dark:to-slate-900/50 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      {/* Mock UI Background */}
      <div className="absolute inset-4 sm:inset-6">
        {/* Mock Header */}
        <div className="flex items-center gap-3 mb-4">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-r from-blue-500 to-violet-500" />
          <div className="flex-1 h-3 bg-slate-200 dark:bg-slate-700 rounded-full max-w-[200px]" />
        </div>

        {/* Mock Content Grid */}
        <div className="grid grid-cols-3 gap-3">
          <div className="h-20 bg-white dark:bg-slate-800 rounded-lg shadow-sm" />
          <div className="h-20 bg-white dark:bg-slate-800 rounded-lg shadow-sm" />
          <div className="h-20 bg-white dark:bg-slate-800 rounded-lg shadow-sm" />
        </div>

        {/* Mock List */}
        <div className="mt-4 space-y-2">
          <div className="h-12 bg-white dark:bg-slate-800 rounded-lg shadow-sm" />
          <div className="h-12 bg-white dark:bg-slate-800 rounded-lg shadow-sm" />
        </div>
      </div>

      {/* Hotspots */}
      {hotspots.map((hotspot, index) => (
        <Hotspot
          key={hotspot.id}
          {...hotspot}
          isRevealed={revealedHotspots[hotspot.id]}
          onToggle={onToggleHotspot}
          index={index}
        />
      ))}

      {/* Hint Text */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 2 }}
        className="absolute bottom-3 left-1/2 -translate-x-1/2 text-xs text-slate-400 dark:text-slate-500"
      >
        Click the hotspots to learn more
      </motion.div>
    </div>
  );
}
