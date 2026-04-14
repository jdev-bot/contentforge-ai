# ContentForge AI - Interactive Onboarding Guide Design Document

## Overview

A comprehensive, immersive onboarding experience that introduces users to ContentForge AI's features through a guided 10-step interactive tour. The experience combines stunning visuals, smooth animations, and intuitive interactions to create a memorable first impression.

## Design Philosophy

- **Immersive**: Full-screen experience that captures attention
- **Interactive**: Clickable hotspots, hover effects, and gesture support
- **Delightful**: Smooth animations and visual flourishes
- **Educational**: Clear value proposition at each step
- **Accessible**: Keyboard navigation, reduced motion support, screen reader friendly

## Architecture

### Page Structure

```
src/frontend/src/app/onboarding/
├── page.tsx                 # Main onboarding page
├── components/
│   ├── OnboardingContainer.tsx    # State management & navigation
│   ├── WelcomeScreen.tsx          # Step 1: Welcome & logo reveal
│   ├── FeatureShowcase.tsx        # Steps 2-9: Feature demonstrations
│   ├── CompletionScreen.tsx       # Step 10: Final CTA
│   ├── ProgressBar.tsx            # Step indicator
│   ├── Hotspot.tsx                # Interactive hotspots
│   ├── Tooltip.tsx                # Animated tooltips
│   ├── NavigationControls.tsx     # Prev/Next/Skip buttons
│   └── AnimatedBackground.tsx     # Gradient animations
├── hooks/
│   ├── useOnboarding.ts           # Onboarding state logic
│   ├── useKeyboardNavigation.ts   # Arrow key support
│   └── useSwipe.ts                # Mobile swipe gestures
├── animations/
│   ├── variants.ts                # Framer Motion variants
│   └── transitions.ts             # Shared transitions
└── data/
    └── steps.ts                   # Step content & metadata
```

## Visual Design System

### Color Palette

**Primary Gradients:**
- Main: `linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%)`
- Success: `linear-gradient(135deg, #10b981 0%, #34d399 100%)`
- Accent: `linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)`

**Glassmorphism:**
- Background: `rgba(255, 255, 255, 0.1)` (light) / `rgba(15, 23, 42, 0.7)` (dark)
- Border: `rgba(255, 255, 255, 0.2)` (light) / `rgba(255, 255, 255, 0.1)` (dark)
- Blur: `backdrop-filter: blur(20px)`

### Typography

- **Hero Title**: 48-64px, font-weight: 700, gradient text
- **Section Title**: 32-40px, font-weight: 600
- **Body**: 16-18px, font-weight: 400, line-height: 1.6
- **Caption**: 14px, font-weight: 500, uppercase tracking

### Spacing & Layout

- **Container**: max-width 1200px, centered
- **Section Padding**: 80px vertical, 24-48px horizontal
- **Card Padding**: 32px
- **Grid Gap**: 24-32px

## Animations Specification

### Page Transitions

```typescript
const slideVariants = {
  enter: (direction: number) => ({
    x: direction > 0 ? 1000 : -1000,
    opacity: 0
  }),
  center: {
    x: 0,
    opacity: 1
  },
  exit: (direction: number) => ({
    x: direction < 0 ? 1000 : -1000,
    opacity: 0
  })
};
```

### Element Animations

**Logo Reveal:**
- Scale: 0.5 → 1.0, Opacity: 0 → 1
- Duration: 0.8s, Easing: `[0.34, 1.56, 0.64, 1]` (spring)

**Text Reveal:**
- Y: 30px → 0, Opacity: 0 → 1
- Stagger: 0.1s between lines, Duration: 0.6s

**Card Entrance:**
- Y: 40px → 0, Opacity: 0 → 1, Scale: 0.95 → 1
- Duration: 0.5s, Stagger: 0.08s

**Hotspot Pulse:**
- Scale: 1 → 1.2 → 1, Opacity ring: 0.4 → 0
- Duration: 2s, infinite

### Background Animation

**Animated Gradient:**
```css
background: linear-gradient(-45deg, #3b82f6, #8b5cf6, #ec4899, #3b82f6);
background-size: 400% 400%;
animation: gradient-shift 15s ease infinite;
```

**Floating Particles:**
- Count: 20-30 particles
- Size: 4-12px, Opacity: 0.1-0.3
- Movement: Random drift, 20-40s cycle

## Step-by-Step Content

### Step 1: Welcome & Overview

**Content:**
- Animated ContentForge AI logo
- Headline: "Welcome to the Future of Content Creation"
- Subheadline: "Transform your ideas into engaging content across 20+ platforms with AI"
- CTA: "Start Tour" (primary) / "Skip Tour" (ghost)

**Visual Elements:**
- Logo animation with glow effect
- Gradient background with floating particles
- Tagline fade-in sequence

### Step 2: Dashboard Walkthrough

**Content:**
- Title: "Your Command Center"
- Description: "Everything you need at a glance — projects, analytics, and quick actions"
- Hotspots: Projects overview, Quick actions, Analytics preview, SLA compliance, Content freshness

**Visual:**
- Dashboard mockup screenshot
- Highlight overlays on key areas
- Tooltip explanations

### Step 3: Creating Content

**Content:**
- Title: "Create Content Your Way"
- Description: "Import from URLs, paste text, or upload files — AI handles the rest"
- Input methods showcase: URL import, Direct text, File upload
- **New:** Quality scoring and sentiment analysis on import

**Visual:**
- Interactive input demo
- Quality score badge animation
- Sentiment indicator

### Step 4: AI Generation & Smart Editor

**Content:**
- Title: "AI-Powered Magic"
- Description: "Watch as AI transforms your content into multiple formats instantly"
- Live demo simulation
- Output format carousel
- **New:** Auto-suggestions, SEO optimization, tone adjustment

**Visual:**
- Typing animation
- Format transformation showcase
- Auto-suggestion panel preview
- SEO score animation

### Step 5: Organize & Version

**Content:**
- Title: "Organize Your Assets"
- Description: "Library, folders, tags, and search — your content, organized"
- Features: Folder creation, Tag system, Bulk operations, Version history

**Visual:**
- Folder structure visualization
- Version history timeline
- Smart categorization tags

### Step 6: Team Collaboration

**Content:**
- Title: "Work Together"
- Description: "Invite team members, assign roles, and collaborate seamlessly"
- Role breakdown: Admin, Editor, Writer, Viewer
- **New:** SSO/SAML authentication, Comments v2, Real-time collaboration

**Visual:**
- Team member avatars
- Permission indicators
- Comment thread preview
- Live cursor indicators

### Step 7: Analytics & Insights

**Content:**
- Title: "Insights That Matter"
- Description: "Track performance, understand engagement, optimize your content"
- Metrics showcase: Engagement rates, Top platforms, Content performance
- **New:** Custom dashboards, Funnel analytics, Attribution modeling, SLA monitoring, Freshness scores

**Visual:**
- Animated charts
- Funnel visualization
- Attribution report preview
- SLA compliance indicator

### Step 8: Scheduling & Publishing

**Content:**
- Title: "Publish with Precision"
- Description: "Schedule posts, track funnels, and meet your SLAs"
- Features: Calendar view, Smart scheduling, Bulk schedule
- **New:** Funnel stage assignment, Attribution tags, SLA tracking

**Visual:**
- Calendar mockup with color-coded posts
- Funnel stage labels
- SLA compliance badge

### Step 9: Settings & Integrations

**Content:**
- Title: "Make It Yours"
- Description: "Customize your experience — themes, notifications, integrations, and plugins"
- Customization options: Dark/light mode, Notification preferences, SSO configuration, Plugin marketplace

**Visual:**
- Settings mockup
- Theme toggle animation
- Marketplace preview

### Step 10: Completion & CTA

**Content:**
- Title: "You're All Set!"
- Description: "Start creating amazing content with ContentForge AI"
- Quick tips card
- CTA: "Go to Dashboard" (primary) / "View Documentation" (secondary)

**Visual:**
- Celebration animation
- Confetti effect
- Progress completion indicator

## Interactive Elements

### Progress Bar

**Design:**
- Horizontal segmented bar, 10 segments
- Current step: filled with gradient
- Completed steps: solid color
- Future steps: muted/transparent

### Navigation Controls

**Keyboard Support:**
- Left/Right arrows: Navigate steps
- Escape: Skip/exit
- Enter/Space: Activate focused element

### Hotspots

**Behavior:**
- Expand on hover
- Show tooltip with delay
- Click to reveal detailed info
- Auto-hide after interaction

## Mobile Considerations

### Responsive Breakpoints

- **Mobile**: < 640px — Stack layout, full-width cards
- **Tablet**: 640px - 1024px — 2-column grid
- **Desktop**: > 1024px — Full layout with sidebar

### Touch Interactions

- Swipe left/right to navigate steps
- Tap hotspots to reveal info
- Larger touch targets (44px minimum)

### Mobile Optimizations

- Reduced particle count
- Simplified animations
- Bottom sheet for tooltips
- Full-screen step cards

## Technical Implementation

### Dependencies

```json
{
  "framer-motion": "^11.x",
  "lucide-react": "^1.x",
  "clsx": "^2.x",
  "tailwind-merge": "^3.x"
}
```

### Performance

- Lazy load step components
- Use `will-change` on animated elements
- Debounce scroll handlers
- Prefetch next step assets
- Reduced motion media query support

### Accessibility

```typescript
const prefersReducedMotion = 
  typeof window !== 'undefined' 
    ? window.matchMedia('(prefers-reduced-motion: reduce)').matches 
    : false;

const variants = prefersReducedMotion 
  ? { enter: {}, center: {}, exit: {} }
  : defaultVariants;
```

**ARIA:**
- `role="region"` for each step
- `aria-live="polite"` for progress updates
- `aria-label` for navigation buttons
- Focus trap during tour

## State Management

```typescript
interface OnboardingState {
  currentStep: number;
  totalSteps: number;
  direction: number;
  completed: boolean;
  skipped: boolean;
  hotspotsRevealed: Record<string, boolean>;
  preferences: {
    reducedMotion: boolean;
    autoPlay: boolean;
  };
}
```

## Completion Criteria

- [x] All 10 steps implemented with content
- [x] Smooth animations throughout
- [x] Keyboard navigation fully functional
- [x] Mobile swipe gestures working
- [x] Dark/light mode support
- [x] Reduced motion support
- [x] Screen reader accessible
- [x] Exit to dashboard functional
- [x] Progress persistence (localStorage)
- [x] Skip option working
- [x] P4 features included in relevant steps
- [x] SSO/SAML mentioned in Step 6
- [x] Custom dashboards mentioned in Step 7
- [x] Funnel tracking mentioned in Step 8

## Future Enhancements

1. **Video Backgrounds**: Optional video backgrounds per step
2. **Interactive Demos**: Live mini-demos within steps
3. **Progressive Onboarding**: Contextual hints after initial tour
4. **Team Onboarding**: Admin-invited team member flow
5. **A/B Testing**: Test different onboarding sequences
6. **Analytics**: Track completion rates and drop-offs
7. **Plugin Showcase**: Interactive marketplace demo in Step 9

---

*Design Document v2.0 — ContentForge AI Onboarding Experience*  
*Updated: April 14, 2026 — Added P4 feature references throughout*