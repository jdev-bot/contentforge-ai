# Frontend Development Guidelines — ContentForge AI

> Rules and conventions for frontend development.

## Tech Stack

- **Next.js 14** (App Router) with TypeScript
- **React 18** with Server Components by default
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Recharts** for data visualization
- **Supabase** for auth and database

## TypeScript Rules

### No `any` Types

**This is a hard rule.** Every variable, parameter, return type, and generic must use a proper type.

```typescript
// ❌ NEVER
const data: any = response;
function process(item: any) { ... }
const list: any[] = [];

// ✅ ALWAYS
const data: ContentResponse = response;
function process(item: ContentItem): ProcessedItem { ... }
const list: ContentItem[] = [];
```

When you genuinely don't know the type, use:
- `unknown` for truly unknown values, then narrow with type guards
- Specific union types: `string | number | null`
- `Record<string, unknown>` for generic objects
- Interface with optional fields for partial shapes

### Strict Mode

TypeScript strict mode is enabled. This means:
- No implicit `any`
- No implicit returns
- Strict null checks
- No unused locals/parameters

### Type Definitions

- Define interfaces above each component file when local
- Use `types/` directory for shared types
- Use union types for status/state enums:

```typescript
type PostStatus = 'scheduled' | 'published' | 'failed' | 'cancelled' | 'processing';
type FunnelStage = 'awareness' | 'interest' | 'consideration' | 'conversion' | 'retention';
type AttributionModel = 'first_touch' | 'last_touch' | 'linear' | 'time_decay';
```

## Component Conventions

### Server vs Client Components

- **Default to Server Components** (no `"use client"` directive)
- Only use `"use client"` when the component needs:
  - State (`useState`, `useReducer`)
  - Effects (`useEffect`)
  - Event handlers (`onClick`, `onChange`)
  - Browser APIs (`window`, `localStorage`)
  - Custom hooks that use client features

### Component Structure

```typescript
// 1. Imports
import { useState } from 'react';
import { showToast } from '@/hooks/useToast';

// 2. Type definitions
interface ScheduleModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSchedule: (data: ScheduleData) => void;
}

// 3. Component
export function ScheduleModal({ isOpen, onClose, onSchedule }: ScheduleModalProps) {
  // State
  const [platform, setPlatform] = useState<Platform>('twitter');
  
  // Handlers
  const handleSubmit = () => {
    showToast('Post scheduled successfully', 'success');
    onSchedule(data);
  };
  
  // Render
  return (
    <div className="...">
      {/* JSX */}
    </div>
  );
}
```

### Props

- Always define a `Props` interface for components with props
- Use descriptive names: `ScheduleModalProps`, not `Props`
- Optional props with `?` and provide sensible defaults

## Toast API

Use the unified toast API for all user notifications:

```typescript
import { showToast } from '@/hooks/useToast';

// ✅ CORRECT — showToast(message, type)
showToast('Content created successfully', 'success');
showToast('Failed to save content', 'error');
showToast('Auto-save in progress...', 'info');
showToast('Approaching monthly limit', 'warning');

// ❌ WRONG — Do NOT use the old toast() API
toast('Content created'); // DON'T DO THIS
toast.success('Content created'); // DON'T DO THIS
```

### Toast Types

| Type | Usage | Auto-dismiss |
|------|-------|-------------|
| `success` | Successful operations | 3 seconds |
| `error` | Failed operations | 5 seconds |
| `info` | Informational messages | 4 seconds |
| `warning` | Warning messages | 4 seconds |

## API Integration

All API calls go through `src/lib/api.ts`:

```typescript
import { schedulePost, getScheduledPosts } from '@/lib/api';

// ✅ CORRECT
const posts = await getScheduledPosts({ page: 1, limit: 20 });

// ❌ WRONG — Don't call fetch directly
const res = await fetch('/api/v1/schedule');
```

### Error Handling Pattern

```typescript
try {
  const result = await schedulePost(data);
  showToast('Post scheduled successfully', 'success');
} catch (error) {
  const message = error instanceof Error ? error.message : 'Failed to schedule post';
  showToast(message, 'error');
}
```

## Styling

- **Tailwind CSS only** — No CSS modules, no styled-components, no inline styles
- Use `clsx()` for conditional classes
- Use `tailwind-merge` for class merging

```typescript
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

const className = twMerge(clsx(
  'rounded-lg p-4',
  isActive && 'bg-blue-500 text-white',
  isDisabled && 'opacity-50 cursor-not-allowed'
));
```

## Animation

- Use Framer Motion for all animations
- Respect `prefers-reduced-motion`:

```typescript
const prefersReducedMotion = typeof window !== 'undefined'
  ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
  : false;

const variants = prefersReducedMotion
  ? { enter: {}, center: {}, exit: {} }
  : defaultVariants;
```

## Current Project Stats

| Metric | Count |
|--------|-------|
| Components | 73 |
| Pages | 16 |
| Backend API routes | 375 |
| Backend services | 34 |
| P4 features (frontend) | 16 components |

## File Organization

```
src/frontend/src/
├── app/              # Next.js pages (16)
├── components/       # React components (73)
├── hooks/            # Custom hooks
├── lib/              # Utilities, API client
└── types/            # TypeScript types
```

## Key P4 Components

| Wave | Component | Feature |
|------|-----------|---------|
| 1 | `QualityScoreBadge` | AI quality scoring |
| 1 | `SentimentBadge` | Sentiment analysis |
| 1 | `VersionHistory` | Content versioning |
| 1 | `CustomDashboard` | Configurable dashboards |
| 2 | `AutoSuggestions` | Real-time suggestions |
| 2 | `SmartCategorization` | Auto-tagging |
| 2 | `PerformanceAnalytics` | Publishing analytics |
| 2 | `CommentsV2` | Enhanced comments |
| 3 | `SSOConfig` | OIDC/SAML configuration |
| 3 | `PluginManager` | Plugin management |
| 3 | `Collaboration` | Real-time editing |
| 3 | `Marketplace` | Plugin marketplace |
| 4 | `FunnelAnalytics` | Funnel visualization |
| 4 | `AttributionReport` | Attribution modeling |
| 4 | `SLAMonitoring` | SLA compliance |
| 4 | `IntegrationHub` | Integration framework |