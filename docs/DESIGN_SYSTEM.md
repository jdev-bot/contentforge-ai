# ContentForge AI - Design System

A modern, accessible, and stunning design system for ContentForge AI.

**Last Updated:** April 14, 2026  
**Status:** Complete through P4

---

## Philosophy

- **Modern & Premium**: Glassmorphism, gradients, and smooth animations
- **Accessible First**: WCAG 2.1 AA compliant, keyboard navigable
- **Dark Mode Ready**: Seamless light/dark switching
- **Mobile First**: Responsive by design, touch-friendly

---

## Color Palette

### Primary Colors

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `--primary-50` | `#eff6ff` | `#1e3a5f` | Light backgrounds |
| `--primary-100` | `#dbeafe` | `#1e4a7a` | Hover states |
| `--primary-500` | `#3b82f6` | `#60a5fa` | Primary actions |
| `--primary-600` | `#2563eb` | `#3b82f6` | Buttons, links |
| `--primary-700` | `#1d4ed8` | `#2563eb` | Active states |

### Gradient Definitions

```css
/* Primary Gradient */
--gradient-primary: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);

/* Success Gradient */
--gradient-success: linear-gradient(135deg, #10b981 0%, #34d399 100%);

/* Warning Gradient */
--gradient-warning: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);

/* Danger Gradient */
--gradient-danger: linear-gradient(135deg, #ef4444 0%, #f87171 100%);

/* Glass Effect */
--glass-bg: rgba(255, 255, 255, 0.7);
--glass-bg-dark: rgba(15, 23, 42, 0.7);
--glass-border: rgba(255, 255, 255, 0.2);
--glass-border-dark: rgba(255, 255, 255, 0.1);
```

### Semantic Colors

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `--bg-primary` | `#ffffff` | `#0f172a` | Main background |
| `--bg-secondary` | `#f8fafc` | `#1e293b` | Card backgrounds |
| `--bg-tertiary` | `#f1f5f9` | `#334155` | Elevated surfaces |
| `--text-primary` | `#0f172a` | `#f8fafc` | Primary text |
| `--text-secondary` | `#64748b` | `#94a3b8` | Secondary text |
| `--text-muted` | `#94a3b8` | `#64748b` | Muted text |
| `--border` | `#e2e8f0` | `#334155` | Borders |
| `--border-subtle` | `#f1f5f9` | `#1e293b` | Subtle dividers |

### Status Colors

| Status | Light | Dark |
|--------|-------|------|
| Success | `#10b981` | `#34d399` |
| Warning | `#f59e0b` | `#fbbf24` |
| Error | `#ef4444` | `#f87171` |
| Info | `#3b82f6` | `#60a5fa` |

---

## Typography

### Font Family

```css
--font-sans: 'Inter', system-ui, -apple-system, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

### Type Scale

| Token | Size | Line Height | Weight | Usage |
|-------|------|-------------|--------|-------|
| `text-xs` | 12px | 16px | 400 | Captions, badges |
| `text-sm` | 14px | 20px | 400 | Body small, labels |
| `text-base` | 16px | 24px | 400 | Body text |
| `text-lg` | 18px | 28px | 500 | Lead text |
| `text-xl` | 20px | 28px | 600 | Card titles |
| `text-2xl` | 24px | 32px | 600 | Section headings |
| `text-3xl` | 30px | 36px | 700 | Page titles |
| `text-4xl` | 36px | 40px | 700 | Hero text |

---

## Spacing System

### Base Unit: 4px

| Token | Value | Usage |
|-------|-------|-------|
| `space-1` | 4px | Tight spacing |
| `space-2` | 8px | Small gaps |
| `space-3` | 12px | Component padding |
| `space-4` | 16px | Standard padding |
| `space-5` | 20px | Medium gaps |
| `space-6` | 24px | Section spacing |
| `space-8` | 32px | Large gaps |
| `space-10` | 40px | Section margins |
| `space-12` | 48px | Page sections |

### Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `rounded-sm` | 4px | Tags, badges |
| `rounded-md` | 6px | Inputs, small buttons |
| `rounded-lg` | 8px | Cards, modals |
| `rounded-xl` | 12px | Large cards |
| `rounded-2xl` | 16px | Feature cards |
| `rounded-full` | 9999px | Pills, avatars |

---

## Shadows

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
--shadow-primary: 0 4px 14px 0 rgba(59, 130, 246, 0.39);
--shadow-primary-dark: 0 4px 14px 0 rgba(59, 130, 246, 0.25);
```

---

## Component Patterns

### Buttons

**Primary Button** — Gradient, shadow, hover scale 1.02, active 0.98  
**Secondary Button** — Bordered, hover darken  
**Ghost Button** — Transparent, hover background

### Cards

**Standard Card** — `rounded-xl`, `shadow-md`, glass option  
**Interactive Card** — Hover: `shadow-lg`, translateY -2px  
**Stat Card** — Used in dashboards for metrics display

### Inputs

**Text Input** — `rounded-lg`, focus ring `primary-500`  
**Floating Label Input** — Label transitions on focus/filled

### Badges

| Variant | Background | Text | Border |
|---------|------------|------|--------|
| Default | `--bg-secondary` | `--text-primary` | `--border` |
| Primary | `--primary-100` | `--primary-700` | `--primary-200` |
| Success | `rgba(16, 185, 129, 0.1)` | `#10b981` | `rgba(16, 185, 129, 0.2)` |
| Warning | `rgba(245, 158, 11, 0.1)` | `#f59e0b` | `rgba(245, 158, 11, 0.2)` |
| Error | `rgba(239, 68, 68, 0.1)` | `#ef4444` | `rgba(239, 68, 68, 0.2)` |

---

## P4 UI Components

### Enterprise & Analytics Components

| Component | Location | Description |
|-----------|----------|-------------|
| **SLAMonitoring** | `src/components/SLAMonitoring.tsx` | SLA compliance dashboard with uptime tracking, breach alerts, and credit calculation |
| **FunnelAnalytics** | `src/components/FunnelAnalytics.tsx` | Funnel visualization with stage-by-stage conversion rates |
| **AttributionModeling** | `src/components/AttributionModeling.tsx` | Multi-touch attribution display with channel attribution weights |
| **IntegrationHub** | `src/components/IntegrationHub.tsx` | Integration management with connection status, config, and marketplace browse |
| **MarketplaceBrowser** | `src/components/MarketplaceBrowser.tsx` | Plugin and theme marketplace with search, categories, and install |
| **PluginManager** | `src/components/PluginManager.tsx` | Installed plugin management with enable/disable/configure |
| **CollaborationEditor** | `src/components/CollaborationEditor.tsx` | Real-time multi-user editor with cursors and presence indicators |
| **CustomDashboard** | `src/components/CustomDashboard.tsx` | User-configurable dashboard with drag-and-drop widget layout |
| **AuditLogViewer** | `src/components/AuditLogViewer.tsx` | Filterable audit log table with export |
| **VersionHistory** | `src/components/VersionHistory.tsx` | Content version timeline with diff view and rollback |
| **QualityScore** | `src/components/QualityScore.tsx` | AI quality score display with breakdown metrics |
| **SentimentIndicator** | `src/components/SentimentIndicator.tsx` | Real-time sentiment badge with trend arrow |
| **DataRetentionPolicy** | `src/components/DataRetentionPolicy.tsx` | Retention policy configuration with schedule |
| **ReportsGenerator** | `src/components/ReportsGenerator.tsx` | Report builder with template selection and export |

### Component Design Patterns

**Dashboard Widget Pattern:**
- Draggable container with title bar
- Collapse/expand toggle
- Configurable refresh interval
- Loading skeleton state
- Error boundary with retry

**Real-Time Component Pattern:**
- WebSocket connection indicator
- Optimistic updates with rollback
- Presence indicators (avatars with status)
- Typing indicators for collaboration

**Enterprise Feature Pattern:**
- Feature gate badge (tier required)
- SSO configuration wizard
- Audit log entry formatting
- SLA compliance indicator (green/yellow/red)

---

## Animation System

### Durations

| Token | Value | Usage |
|-------|-------|-------|
| `--duration-fast` | 150ms | Micro-interactions |
| `--duration-normal` | 200ms | Standard transitions |
| `--duration-slow` | 300ms | Page transitions |
| `--duration-slower` | 500ms | Complex animations |

### Easing

| Token | Value | Usage |
|-------|-------|-------|
| `--ease-out` | `cubic-bezier(0.16, 1, 0.3, 1)` | Enter animations |
| `--ease-in` | `cubic-bezier(0.7, 0, 0.84, 0)` | Exit animations |
| `--ease-in-out` | `cubic-bezier(0.4, 0, 0.2, 1)` | Standard |
| `--ease-spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Bouncy effects |

### Key Animations

```css
@keyframes fadeInUp { /* Enter from below */ }
@keyframes scaleIn { /* Enter with scale */ }
@keyframes slideInRight { /* Enter from right */ }
@keyframes pulseRing { /* Notification pulse */ }
@keyframes shimmer { /* Skeleton loading */ }
```

---

## Glassmorphism

```css
.glass { backdrop-filter: blur(12px); background: rgba(255,255,255,0.7); }
.glass-dark { backdrop-filter: blur(12px); background: rgba(15,23,42,0.7); }
.glass-card { backdrop-filter: blur(20px); box-shadow: 0 8px 32px 0 rgba(0,0,0,0.1); }
```

---

## Accessibility

- All interactive elements have visible focus (2px solid `--primary-500`, offset 2px)
- Focus-visible for keyboard only
- Reduced motion support (`prefers-reduced-motion`)
- WCAG AA color contrast (4.5:1 normal, 3:1 large)
- Semantic HTML + ARIA labels
- `aria-live` regions for dynamic content
- Full keyboard navigation support

---

## Responsive Breakpoints

| Breakpoint | Width | Usage |
|------------|-------|-------|
| `sm` | 640px | Large phones |
| `md` | 768px | Tablets |
| `lg` | 1024px | Small laptops |
| `xl` | 1280px | Desktops |
| `2xl` | 1536px | Large screens |

---

## Implementation Notes

1. **Tailwind CSS v4**: CSS-first configuration
2. **CSS Variables**: All colors as custom properties
3. **Dark Mode**: `dark:` prefix classes
4. **Animations**: Framer Motion for React
5. **Icons**: Lucide React for consistent iconography
6. **TypeScript strict**: All components fully typed
7. **Zero `any`**: Proper interfaces for all props

---

*Last updated: April 14, 2026 — Neo DevOrg*