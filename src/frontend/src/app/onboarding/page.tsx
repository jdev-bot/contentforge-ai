import type { Metadata } from 'next';
import { OnboardingContainer } from './components/OnboardingContainer';

export const metadata: Metadata = {
  title: 'Welcome to ContentForge AI - Interactive Tour',
  description: 'Take a guided tour of ContentForge AI and discover how to transform your content with AI-powered tools.',
  robots: {
    index: false,
    follow: false
  }
};

export default function OnboardingPage() {
  return <OnboardingContainer />;
}
