import { Variants } from 'framer-motion';

// Page transition variants
export const pageTransition: Variants = {
  initial: { opacity: 0, scale: 0.98 },
  animate: { 
    opacity: 1, 
    scale: 1,
    transition: { 
      duration: 0.5, 
      ease: [0.34, 1.56, 0.64, 1] // Spring easing
    }
  },
  exit: { 
    opacity: 0, 
    scale: 0.98,
    transition: { duration: 0.3, ease: 'easeOut' }
  }
};

// Slide transitions for step navigation
export const slideVariants: Variants = {
  enter: (direction: number) => ({
    x: direction > 0 ? 300 : -300,
    opacity: 0,
    scale: 0.95
  }),
  center: {
    x: 0,
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: [0.34, 1.56, 0.64, 1]
    }
  },
  exit: (direction: number) => ({
    x: direction < 0 ? 300 : -300,
    opacity: 0,
    scale: 0.95,
    transition: { duration: 0.3, ease: 'easeIn' }
  })
};

// Fade up animation
export const fadeUp: Variants = {
  initial: { opacity: 0, y: 30 },
  animate: (delay: number = 0) => ({
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
      delay,
      ease: [0.34, 1.56, 0.64, 1]
    }
  })
};

// Stagger container
export const staggerContainer: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2
    }
  }
};

// Stagger item
export const staggerItem: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: [0.34, 1.56, 0.64, 1]
    }
  }
};

// Scale animation
export const scaleIn: Variants = {
  initial: { opacity: 0, scale: 0.8 },
  animate: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: [0.34, 1.56, 0.64, 1]
    }
  }
};

// Card entrance
export const cardEntrance: Variants = {
  initial: { opacity: 0, y: 40, scale: 0.95 },
  animate: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.6,
      ease: [0.34, 1.56, 0.64, 1]
    }
  }
};

// Logo reveal
export const logoReveal: Variants = {
  initial: { opacity: 0, scale: 0.5, rotate: -10 },
  animate: {
    opacity: 1,
    scale: 1,
    rotate: 0,
    transition: {
      duration: 0.8,
      ease: [0.34, 1.56, 0.64, 1]
    }
  }
};

// Hotspot pulse
export const hotspotPulse = {
  scale: [1, 1.2, 1],
  opacity: [0.6, 1, 0.6],
  transition: {
    duration: 2,
    repeat: Infinity,
    ease: 'easeInOut'
  }
};

// Progress bar fill
export const progressFill = (progress: number) => ({
  width: `${progress}%`,
  transition: { duration: 0.5, ease: 'easeOut' }
});

// Floating animation
export const floating = {
  y: [-10, 10, -10],
  transition: {
    duration: 6,
    repeat: Infinity,
    ease: 'easeInOut'
  }
};

// Gradient text shimmer
export const gradientShimmer = {
  backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
  transition: {
    duration: 5,
    repeat: Infinity,
    ease: 'linear'
  }
};

// Celebration animation for completion
export const celebrationVariants: Variants = {
  initial: { scale: 0, rotate: -180 },
  animate: {
    scale: 1,
    rotate: 0,
    transition: {
      duration: 0.8,
      ease: [0.34, 1.56, 0.64, 1],
      type: 'spring' as const,
      stiffness: 200
    }
  }
};

// Confetti particle
export const confettiVariant = (index: number) => ({
  initial: { 
    opacity: 0, 
    y: 0, 
    x: 0, 
    rotate: 0,
    scale: 0 
  },
  animate: {
    opacity: [0, 1, 1, 0],
    y: [-20, -100 - Math.random() * 200],
    x: [(index % 2 === 0 ? 1 : -1) * Math.random() * 200],
    rotate: [0, 360 + Math.random() * 360],
    scale: [0, 1, 1, 0],
    transition: {
      duration: 2 + Math.random(),
      delay: index * 0.05,
      ease: 'easeOut'
    }
  }
});

// Hover lift effect
export const hoverLift = {
  rest: { y: 0, scale: 1 },
  hover: { 
    y: -4, 
    scale: 1.02,
    transition: { duration: 0.2, ease: 'easeOut' }
  }
};

// Tooltip animation
export const tooltipVariants: Variants = {
  hidden: { 
    opacity: 0, 
    y: 10, 
    scale: 0.95,
    transition: { duration: 0.15 }
  },
  visible: { 
    opacity: 1, 
    y: 0, 
    scale: 1,
    transition: { 
      duration: 0.2,
      ease: [0.34, 1.56, 0.64, 1]
    }
  }
};

// Reduced motion variants
export const reducedMotionVariants = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: { duration: 0.2 } },
  exit: { opacity: 0, transition: { duration: 0.1 } }
};
