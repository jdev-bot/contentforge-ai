// Lottie animation exports
export { LottieAnimation } from './LottieAnimation';
export { OnboardingLottiePlayer } from './OnboardingLottiePlayer';

// Animation data exports
export { welcomeAnimation } from './animations/welcome';
export { contentCreationAnimation } from './animations/content-creation';
export { aiMagicAnimation } from './animations/ai-magic';
export { teamCollaborationAnimation } from './animations/team-collaboration';
export { analyticsAnimation } from './animations/analytics';
export { successAnimation } from './animations/success';

// Animation mapping
export const ONBOARDING_ANIMATIONS = {
  welcome: 'welcome',
  contentCreation: 'content-creation',
  aiMagic: 'ai-magic',
  teamCollaboration: 'team-collaboration',
  analytics: 'analytics',
  success: 'success',
} as const;

export type OnboardingAnimationType = keyof typeof ONBOARDING_ANIMATIONS;
