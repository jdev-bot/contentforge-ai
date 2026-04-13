'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { useOnboarding } from '../hooks/useOnboarding';
import { useKeyboardNavigation } from '../hooks/useKeyboardNavigation';
import { useSwipe } from '../hooks/useSwipe';
import { getStepById } from '../data/steps';
import { AnimatedBackground, StepBackground } from './AnimatedBackground';
import { ProgressBar } from './ProgressBar';
import { NavigationControls } from './NavigationControls';
import { WelcomeScreen } from './WelcomeScreen';
import { FeatureShowcase } from './FeatureShowcase';
import { CompletionScreen } from './CompletionScreen';
import { slideVariants } from '../animations/variants';

export function OnboardingContainer() {
  const {
    currentStep,
    direction,
    totalSteps,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    completed,
    hotspotsRevealed,
    goToNext,
    goToPrevious,
    skipTour,
    completeTour,
    toggleHotspot,
    isFirstStep,
    isLastStep,
    progress
  } = useOnboarding();

  // Keyboard navigation
  useKeyboardNavigation({
    onNext: isLastStep ? completeTour : goToNext,
    onPrevious: goToPrevious,
    onSkip: skipTour,
    isEnabled: true,
    isFirstStep,
    isLastStep
  });

  // Swipe gestures for mobile
  const swipeHandlers = useSwipe({
    onSwipeLeft: isLastStep ? completeTour : goToNext,
    onSwipeRight: goToPrevious
  });

  const currentStepData = getStepById(currentStep);

  return (
    <div
      className="min-h-screen bg-white dark:bg-slate-900 relative overflow-hidden"
      {...swipeHandlers}
    >
      {/* Animated Background */}
      <AnimatedBackground />
      <StepBackground step={currentStep} />

      {/* Progress Bar */}
      <ProgressBar
        currentStep={currentStep}
        totalSteps={totalSteps}
        progress={progress}
      />

      {/* Main Content */}
      <div className="relative z-10">
        <AnimatePresence mode="wait" custom={direction}>
          {currentStep === 1 ? (
            <motion.div
              key="welcome"
              custom={direction}
              variants={slideVariants}
              initial="enter"
              animate="center"
              exit="exit"
            >
              <WelcomeScreen
                onStart={goToNext}
                onSkip={skipTour}
              />
            </motion.div>
          ) : currentStep === totalSteps ? (
            <motion.div
              key="completion"
              custom={direction}
              variants={slideVariants}
              initial="enter"
              animate="center"
              exit="exit"
            >
              <CompletionScreen onComplete={completeTour} />
            </motion.div>
          ) : currentStepData ? (
            <motion.div
              key={`step-${currentStep}`}
              custom={direction}
              variants={slideVariants}
              initial="enter"
              animate="center"
              exit="exit"
            >
              <FeatureShowcase
                step={currentStepData}
                hotspotsRevealed={hotspotsRevealed}
                onToggleHotspot={toggleHotspot}
              />
            </motion.div>
          ) : null}
        </AnimatePresence>
      </div>

      {/* Navigation Controls */}
      <NavigationControls
        onPrevious={goToPrevious}
        onNext={isLastStep ? completeTour : goToNext}
        onSkip={skipTour}
        isFirstStep={isFirstStep}
        isLastStep={isLastStep}
      />
    </div>
  );
}
