# ContentForge AI — Frontend

Next.js 14 (App Router) frontend for ContentForge AI, an AI-powered content creation platform.

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 14.x | React framework (App Router) |
| **TypeScript** | 5.x | Type-safe development |
| **React** | 18.x | UI component library |
| **Tailwind CSS** | 3.x | Utility-first CSS framework |
| **Framer Motion** | 11.x | Animations and transitions |
| **Recharts** | 2.x | Charting library |
| **Lucide React** | 1.x | Icon library |
| **date-fns** | 3.x | Date utilities |

## Project Stats

| Metric | Count |
|--------|-------|
| **Components** | 73 |
| **Pages** | 16 |
| **API Routes** | Integrated with 375 backend endpoints |
| **Static Pages** | 16 (pre-rendered) |

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/` | Main dashboard with stats, widgets, analytics |
| Login | `/login` | Authentication (email, social, SSO) |
| Signup | `/login` (signup mode) | Account creation |
| Onboarding | `/onboarding` | 10-step interactive tour |
| Content | `/content` | Content library and management |
| Content New | `/content/new` | Create new content (URL, text, YouTube) |
| Projects | `/projects` | Project listing and management |
| Projects New | `/projects/new` | Create new project |
| Settings | `/settings` | User settings, SSO, plugins, data retention |
| Schedule | (tab in Dashboard) | Scheduled posts calendar and management |
| Analytics | (tab in Dashboard) | Performance, funnels, attribution, SLA |
| AI Editor | (modal/tab) | Smart content editing |

## P4 Frontend Components

The following components were added as part of P4 feature waves:

### Wave 1 — Content Intelligence
- `QualityScoreBadge` — Displays AI quality score (0-100) with color coding
- `SentimentBadge` — Shows sentiment (positive/neutral/negative) with confidence
- `VersionHistory` — Content version timeline with diff comparison
- `AuditLog` — Organization audit trail viewer
- `CustomDashboard` — Configurable dashboard with widget system
- `ReportGenerator` — Report creation and scheduling

### Wave 2 — Smart Features
- `AutoSuggestions` — Real-time categorized content suggestions
- `SmartCategorization` — Auto-tagging and project routing for RSS content
- `PerformanceAnalytics` — Publishing velocity, quality trends, platform efficiency
- `DataRetentionSettings` — Retention policy configuration per project
- `CommentsV2` — Threaded comments, inline comments, @mentions, action items, reactions

### Wave 3 — Enterprise & Collaboration
- `SSOConfig` — OIDC and SAML SSO configuration UI
- `PluginManager` — Plugin marketplace and installation management
- `Collaboration` — Real-time cursors, presence, conflict resolution
- `Marketplace` — Plugin browsing, installation, and management

### Wave 4 — Advanced Analytics
- `FunnelAnalytics` — Marketing funnel visualization with conversion rates
- `AttributionReport` — Attribution modeling (first/last touch, linear, time decay)
- `SLAMonitoring` — SLA compliance dashboard with alerts
- `IntegrationHub` — Integration framework for external services

## Build & Development

```bash
# Install dependencies
npm install

# Development server
npm run dev

# Production build
npm run build

# Lint
npm run lint

# Type check
npx tsc --noEmit
```

## Environment Variables

Copy `.env.local.example` to `.env.local` and configure:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

## Key Conventions

### TypeScript Rules
- **No `any` types** — Use proper type definitions for all variables
- Strict mode enabled
- All API responses typed with interfaces
- Union types for status/state enums

### Component Patterns
- Server Components by default (App Router)
- Client Components only when needed (`"use client"` directive)
- Props interfaces defined above each component
- Tailwind CSS for all styling (no CSS modules)

### API Integration
- All API calls go through `src/lib/api.ts`
- Toast notifications for success/error feedback
- Loading states for all async operations
- Error boundaries at route level

### Toast API
```typescript
import { showToast } from '@/hooks/useToast';

// Success
showToast('Content created successfully', 'success');

// Error
showToast('Failed to save content', 'error');

// Info
showToast('Auto-save in progress...', 'info');

// Warning
showToast('Approaching monthly limit', 'warning');
```

**Note:** Use `showToast(message, type)` — do NOT use the old `toast()` API.

### State Management
- React Context for global state (auth, theme, organization)
- Local state for component-specific data
- URL state for filters and pagination

## Project Structure

```
src/frontend/src/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Dashboard (home)
│   ├── login/             # Authentication
│   ├── onboarding/         # Interactive tour
│   ├── content/           # Content management
│   ├── projects/          # Project management
│   ├── settings/          # User settings
│   └── layout.tsx         # Root layout
├── components/            # React components (73 total)
│   ├── Dashboard.tsx      # Main dashboard
│   ├── SmartEditor.tsx    # AI content editor
│   ├── ScheduleTab.tsx    # Scheduling interface
│   ├── ScheduleModal.tsx  # Create/edit schedules
│   ├── ScheduleCalendar.tsx # Calendar view
│   ├── AnalyticsTab.tsx   # Analytics dashboard
│   ├── FunnelAnalytics.tsx # P4: Funnel visualization
│   ├── AttributionReport.tsx # P4: Attribution modeling
│   ├── SLAMonitoring.tsx  # P4: SLA compliance
│   ├── CustomDashboard.tsx # P4: Custom dashboards
│   ├── AutoSuggestions.tsx # P4: Content suggestions
│   ├── CommentsV2.tsx     # P4: Enhanced comments
│   ├── SSOConfig.tsx      # P4: SSO configuration
│   ├── Marketplace.tsx    # P4: Plugin marketplace
│   └── ...
├── hooks/                 # Custom React hooks
│   ├── useToast.tsx       # Toast notifications
│   ├── useOnboarding.ts   # Onboarding state
│   └── ...
├── lib/                   # Utilities
│   ├── api.ts             # API client (375 endpoints)
│   ├── supabase.ts        # Supabase client
│   └── utils.ts           # Helper functions
└── types/                 # TypeScript type definitions
```

## Testing

```bash
# Run component tests
npm run test

# Run tests with coverage
npm run test -- --coverage

# Run E2E tests
npm run test:e2e
```

## Deployment

```bash
# Build for production
npm run build

# Start production server
npm start

# Deploy to Vercel
vercel --prod
```

See [Deployment Guide](../../docs/DEPLOYMENT.md) for detailed instructions.

## Related Documentation

- [Backend API](../../docs/API.md) — Full API reference
- [Architecture](../../docs/ARCHITECTURE.md) — System design
- [Testing](../../docs/TESTING.md) — Testing guidelines
- [Tutorials](../../docs/TUTORIALS/) — User-facing tutorials