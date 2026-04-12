# Frontend Documentation

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 16.2.3 | React framework with App Router |
| **React** | 19.2.4 | UI library |
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
├── app/                    # Next.js App Router pages
│   ├── layout.tsx          # Root layout with providers
│   ├── page.tsx            # Home page (redirects to dashboard or login)
│   ├── globals.css         # Global styles
│   ├── login/              # Login/signup page
│   ├── pricing/            # Pricing page
│   ├── content/            # Content-related routes
│   └── projects/           # Project-related routes
├── components/             # React components
│   ├── ui/                 # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Skeleton.tsx
│   │   ├── Tooltip.tsx
│   │   └── ErrorDisplay.tsx
│   ├── Dashboard.tsx       # Main dashboard
│   ├── ErrorBoundary.tsx   # Error handling
│   ├── OfflineBanner.tsx   # Network status
│   ├── ContentTab.tsx      # Content management tab
│   ├── ProjectsTab.tsx     # Projects tab
│   ├── DistributionsTab.tsx
│   ├── AnalyticsTab.tsx
│   ├── TeamTab.tsx
│   ├── SettingsTab.tsx
│   ├── UsageCounter.tsx
│   ├── UpgradeModal.tsx
│   └── SubscriptionModal.tsx
├── hooks/                  # Custom React hooks
│   ├── useToast.tsx        # Toast notifications
│   └── useNetworkStatus.tsx
├── lib/                    # Utility functions and API clients
│   ├── api.ts              # API client
│   ├── supabase.ts         # Supabase client & auth helpers
│   ├── stripe.ts           # Stripe integration
│   └── utils.ts            # Helper functions
└── types/                  # TypeScript type definitions
```

---

## Component Structure

### UI Components (`components/ui/`)

Reusable, low-level components following a consistent API:

| Component | Props | Description |
|-----------|-------|-------------|
| `Button` | `variant`, `size`, `disabled`, `loading` | Primary action button |
| `Card` | `className`, children | Container with shadow/border |
| `Input` | `type`, `placeholder`, `value`, `onChange` | Form input field |
| `Skeleton` | `className` | Loading placeholder |
| `Tooltip` | `content`, `children` | Hover tooltip |
| `ErrorDisplay` | `error`, `onRetry` | Error state UI |

### Page Components

Page-specific components located in `components/`:

- **Dashboard** - Main authenticated view with tabs
- **ContentTab** - Content creation and management
- **ProjectsTab** - Project organization
- **DistributionsTab** - Distribution channels
- **AnalyticsTab** - Usage analytics and charts
- **TeamTab** - Team member management
- **SettingsTab** - User preferences and account settings

---

## How to Add a New Page

### 1. Create the Route Directory

Create a new folder under `src/app/` with the route name:

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

### 3. Add to Navigation (if needed)

Update the Dashboard navigation in `components/Dashboard.tsx`:

```typescript
const navItems = [
  { id: 'content', label: 'Content', icon: FileText },
  { id: 'projects', label: 'Projects', icon: FolderOpen },
  { id: 'distributions', label: 'Distributions', icon: Share2 },
  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  { id: 'team', label: 'Team', icon: Users },
  { id: 'settings', label: 'Settings', icon: Settings },
  { id: 'new-page', label: 'New Page', icon: PlusCircle }, // Add this
]
```

### 4. Add Route Guard (if authenticated)

For protected pages, wrap with auth check in `page.tsx`:

```typescript
import { redirect } from 'next/navigation'
import { getCurrentUser } from '@/lib/supabase'

export default async function ProtectedPage() {
  const user = await getCurrentUser()
  
  if (!user) {
    redirect('/login')
  }
  
  return <YourComponent user={user} />
}
```

### 5. Create API Integration (if needed)

Add API functions to `src/lib/api.ts`:

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

Use Supabase auth helpers from `lib/supabase.ts`:

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

function MyComponent() {
  const { showToast } = useToast()
  
  const handleAction = () => {
    showToast('Success message', 'success')
    showToast('Error message', 'error')
  }
}
```

### API Calls with Error Handling

```typescript
import { api } from '@/lib/api'

try {
  const data = await api.get('/endpoint')
  // Handle success
} catch (error) {
  // Handle error
}
```

### Styling with Tailwind

Use `cn()` utility for conditional classes:

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
```
