# Frontend Documentation

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 14 | React framework with App Router |
| **React** | 19 | UI library |
| **TypeScript** | ^5 | Type safety |
| **Tailwind CSS** | ^4 | Utility-first CSS framework |
| **Supabase** | ^2.103.0 | Backend-as-a-Service (auth, database) |
| **Lucide React** | ^1.8.0 | Icon library |
| **Recharts** | ^3.8.1 | Data visualization |
| **clsx + tailwind-merge** | ^2.1.1, ^3.5.0 | Conditional CSS classes |

### Development Tools

- **ESLint** - Code linting
- **Playwright** - E2E testing
- **Puppeteer** - Screenshot testing

---

## Project Structure

```
src/frontend/src/
├── app/                    # Next.js App Router pages (16 pages)
│   ├── layout.tsx          # Root layout with providers
│   ├── page.tsx            # Home page (redirects to dashboard or login)
│   ├── globals.css         # Global styles
│   ├── login/              # Login/signup page
│   ├── sso/                # SSO/SAML login page
│   ├── pricing/            # Pricing page
│   ├── settings/           # User settings page
│   ├── onboarding/         # New user onboarding
│   ├── content/
│   │   ├── new/            # Create new content
│   │   └── [id]/           # Content detail/editor
│   ├── projects/
│   │   ├── new/            # Create new project
│   │   └── [id]/           # Project detail
│   ├── payment/
│   │   ├── success/        # Payment success
│   │   └── cancel/         # Payment cancelled
│   └── legal/
│       ├── privacy/        # Privacy policy
│       ├── terms/          # Terms of service
│       ├── cookies/        # Cookie policy
│       └── dmca/           # DMCA policy
├── components/             # React components (73 total)
│   ├── ui/                # Reusable UI components
│   ├── onboarding/        # Onboarding flow components
│   └── [feature components]
├── hooks/                 # Custom React hooks
├── lib/                   # Utility functions and API clients
└── types/                 # TypeScript type definitions
```

---

## Component Catalog (73 Components)

### Core UI Components (`components/ui/`)

| Component | File | Description |
|-----------|------|-------------|
| `AnimatedWrapper` | `ui/AnimatedWrapper.tsx` | Animation wrapper component |
| `Avatar` | `ui/Avatar.tsx` | User avatar display |
| `Badge` | `ui/Badge.tsx` | Status/type badge |
| `Button` | `ui/Button.tsx` | Primary action button (variant, size, loading) |
| `Card` | `ui/Card.tsx` | Container with shadow/border |
| `ConfirmDialog` | `ui/ConfirmDialog.tsx` | Confirmation modal dialog |
| `EmptyState` | `ui/EmptyState.tsx` | Empty state placeholder |
| `ErrorDisplay` | `ui/ErrorDisplay.tsx` | Error state with retry |
| `Input` | `ui/Input.tsx` | Form input field |
| `Skeleton` | `ui/Skeleton.tsx` | Loading placeholder |
| `Tooltip` | `ui/Tooltip.tsx` | Hover tooltip |

### Page-Level / Feature Components

| Component | File | Description |
|-----------|------|-------------|
| `Dashboard` | `Dashboard.tsx` | Main authenticated view with tabs |
| `ContentTab` | `ContentTab.tsx` | Content creation and management |
| `ProjectsTab` | `ProjectsTab.tsx` | Project organization |
| `DistributionsTab` | `DistributionsTab.tsx` | Distribution channels |
| `AnalyticsTab` | `AnalyticsTab.tsx` | Usage analytics |
| `TeamTab` | `TeamTab.tsx` | Team member management |
| `SettingsTab` | `SettingsTab.tsx` | User preferences and account settings |
| `TrashTab` | `TrashTab.tsx` | Soft-deleted items and recovery |
| `RSSTab` | `RSSTab.tsx` | RSS feed management |
| `ScheduleTab` | `ScheduleTab.tsx` | Content scheduling |

### P4 Wave 1 — Content Intelligence Components

| Component | File | Description |
|-----------|------|-------------|
| `VersionHistory` | `VersionHistory.tsx` | Content version timeline, diff view, restore |
| `AuditLogs` | `AuditLogs.tsx` | Audit log browser with filters |
| `QualityDashboard` | `QualityDashboard.tsx` | Quality score overview and dimensions |
| `SentimentDashboard` | `SentimentDashboard.tsx` | Sentiment analysis visualization |
| `CustomDashboards` | `CustomDashboards.tsx` | Configurable dashboard builder |
| `TemplateGallery` | `TemplateGallery.tsx` | Report template browser |

### P4 Wave 2 — Smart Operations Components

| Component | File | Description |
|-----------|------|-------------|
| `SuggestionPanel` | `SuggestionPanel.tsx` | AI suggestion cards and actions |
| `CategorizationPanel` | `CategorizationPanel.tsx` | AI/auto categories with override |
| `PerformanceAnalytics` | `PerformanceAnalytics.tsx` | Deep performance charts and metrics |
| `DataRetentionManager` | `DataRetentionManager.tsx` | Retention policy configuration UI |
| `CommentsPanel` | `CommentsPanel.tsx` | Threaded comments, reactions, resolution |

### P4 Wave 3 — Enterprise Components

| Component | File | Description |
|-----------|------|-------------|
| `SAMLLogin` | `SAMLLogin.tsx` | SSO/SAML login page component |
| `CookieConsent` | `CookieConsent.tsx` | GDPR cookie consent banner |
| `PluginManager` | `PluginManager.tsx` | Plugin install/enable/config/uninstall |
| `TemplateMarketplace` | `TemplateMarketplace.tsx` | Browse and install marketplace items |
| `IntegrationHub` | `IntegrationHub.tsx` | Integration connector management |

### P4 Wave 4 — Analytics Components

| Component | File | Description |
|-----------|------|-------------|
| `AttributionDashboard` | `AttributionDashboard.tsx` | Multi-touch attribution visualization |
| `FunnelAnalytics` | `FunnelAnalytics.tsx` | Funnel conversion and drop-off charts |
| `SLAMonitoring` | `SLAMonitoring.tsx` | SLA compliance tracking and breaches |

### Content & AI Components

| Component | File | Description |
|-----------|------|-------------|
| `SmartEditor` | `SmartEditor.tsx` | AI-powered content editor |
| `FreshnessDashboard` | `FreshnessDashboard.tsx` | Content freshness scores |
| `TrendingTopics` | `TrendingTopics.tsx` | Trend discovery and tracking |
| `CompetitorAnalysis` | `CompetitorAnalysis.tsx` | Competitor tracking and gaps |
| `EngagementPrediction` | `EngagementPrediction.tsx` | AI engagement forecasting |
| `ABTestingFramework` | `ABTestingFramework.tsx` | A/B test configuration and results |
| `SearchModal` | `SearchModal.tsx` | Global search interface |

### Scheduling Components

| Component | File | Description |
|-----------|------|-------------|
| `ScheduleCalendar` | `ScheduleCalendar.tsx` | Visual calendar for content scheduling |
| `ScheduleModal` | `ScheduleModal.tsx` | Schedule creation/edit modal |
| `TeamCalendar` | `TeamCalendar.tsx` | Shared team calendar view |
| `UpcomingPostsWidget` | `UpcomingPostsWidget.tsx` | Upcoming scheduled posts list |

### RSS Components

| Component | File | Description |
|-----------|------|-------------|
| `RSSFeedManager` | `RSSFeedManager.tsx` | Feed add/edit/remove |
| `RSSEntriesPanel` | `RSSEntriesPanel.tsx` | Feed entry browser and import |

### Alerts & Notifications

| Component | File | Description |
|-----------|------|-------------|
| `AlertsCenter` | `AlertsCenter.tsx` | Alert management and rules |
| `OfflineBanner` | `OfflineBanner.tsx` | Network status indicator |

### Integrations & Marketplace

| Component | File | Description |
|-----------|------|-------------|
| `IntegrationsPanel` | `IntegrationsPanel.tsx` | Third-party integration configuration |
| `TemplateMarketplace` | `TemplateMarketplace.tsx` | Marketplace browser |
| `IntegrationHub` | `IntegrationHub.tsx` | Integration Hub connector management |

### Billing & Usage

| Component | File | Description |
|-----------|------|-------------|
| `UsageCounter` | `UsageCounter.tsx` | Usage tracking display |
| `UpgradeModal` | `UpgradeModal.tsx` | Plan upgrade prompt |
| `SubscriptionModal` | `SubscriptionModal.tsx` | Subscription management |

### Infrastructure

| Component | File | Description |
|-----------|------|-------------|
| `ErrorBoundary` | `ErrorBoundary.tsx` | React error boundary |
| `Footer` | `Footer.tsx` | App footer |
| `ThemeProvider` | `ThemeProvider.tsx` | Dark/light theme support |
| `BulkOperationsModal` | `BulkOperationsModal.tsx` | Bulk action interface |

### Onboarding Components

| Component | File | Description |
|-----------|------|-------------|
| `OnboardingStep` | `onboarding/animations/OnboardingStep.tsx` | Step container |
| `AnimatedFeature` | `onboarding/animations/AnimatedFeature.tsx` | Feature highlight animation |
| `ConfettiCelebration` | `onboarding/animations/ConfettiCelebration.tsx` | Celebration effect |
| `InteractiveHotspot` | `onboarding/animations/InteractiveHotspot.tsx` | Interactive tooltip |
| `ProgressIndicator` | `onboarding/animations/ProgressIndicator.tsx` | Step progress bar |
| `TooltipHighlight` | `onboarding/animations/TooltipHighlight.tsx` | Highlighted tooltip |
| `LottieAnimation` | `onboarding/lottie/LottieAnimation.tsx` | Lottie animation player |
| `OnboardingLottiePlayer` | `onboarding/lottie/OnboardingLottiePlayer.tsx` | Onboarding Lottie wrapper |

---

## Pages (16 Total)

| Route | Page | Description |
|-------|------|-------------|
| `/` | Home | Redirects to dashboard or login |
| `/login` | Login | Email/password authentication |
| `/sso` | SSO Login | SSO/SAML provider selection |
| `/pricing` | Pricing | Plan comparison and selection |
| `/settings` | Settings | User preferences and account |
| `/onboarding` | Onboarding | New user walkthrough |
| `/content/new` | New Content | Content creation form |
| `/content/[id]` | Content Detail | Content editor and management |
| `/projects/new` | New Project | Project creation |
| `/projects/[id]` | Project Detail | Project view and content list |
| `/payment/success` | Payment Success | Post-checkout success |
| `/payment/cancel` | Payment Cancelled | Post-checkout cancel |
| `/legal/privacy` | Privacy Policy | GDPR privacy policy |
| `/legal/terms` | Terms of Service | Platform terms |
| `/legal/cookies` | Cookie Policy | Cookie usage policy |
| `/legal/dmca` | DMCA Policy | DMCA takedown policy |

---

## How to Add a New Page

### 1. Create the Route Directory

```bash
mkdir -p src/app/new-page
```

### 2. Create `page.tsx`

```typescript
// src/app/new-page/page.tsx
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'

export default function NewPage() {
  const [data, setData] = useState(null)

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">New Page</h1>
      <Card>
        {/* Your content here */}
      </Card>
    </div>
  )
}
```

### 3. Add to Navigation

Update the Dashboard navigation in `components/Dashboard.tsx`.

### 4. Add Route Guard (if authenticated)

```typescript
import { redirect } from 'next/navigation'
import { getCurrentUser } from '@/lib/supabase'

export default async function ProtectedPage() {
  const user = await getCurrentUser()
  if (!user) redirect('/login')
  return <YourComponent user={user} />
}
```

### 5. Create API Integration

```typescript
export async function fetchNewPageData() {
  const response = await fetch('/api/new-endpoint')
  if (!response.ok) throw new Error('Failed to fetch')
  return response.json()
}
```

---

## Key Patterns

### Authentication

```typescript
import { getCurrentUser, signIn, signOut } from '@/lib/supabase'

// In async server component
const user = await getCurrentUser()

// In client component
const { error } = await signIn(email, password)
```

### Toast Notifications

```typescript
import { useToast } from '@/hooks/useToast'

const { showToast } = useToast()
showToast('Success message', 'success')
```

### API Calls with Error Handling

```typescript
import { api } from '@/lib/api'

try {
  const data = await api.get('/endpoint')
} catch (error) {
  // Handle error
}
```

### Styling with Tailwind

```typescript
import { cn } from '@/lib/utils'

<div className={cn(
  'base-classes',
  isActive && 'active-classes',
  isDisabled && 'opacity-50'
)}>
```

---

## Available Scripts

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |

---

## Environment Variables

Create `.env.local` in `src/frontend/`:

```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=your_stripe_key
NEXT_PUBLIC_API_URL=https://contentforge-ai-api.onrender.com
```

---

*Last Updated: 2026-04-14*  
*Components: 73 | Pages: 16 | UI Components: 11*