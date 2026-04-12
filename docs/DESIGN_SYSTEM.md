# ContentForge AI - Design System

A modern, accessible, and stunning design system for ContentForge AI.

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

### Font Weights

- **400 (Regular)**: Body text
- **500 (Medium)**: Emphasis, labels
- **600 (Semibold)**: Headings, buttons
- **700 (Bold)**: Page titles, strong emphasis

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
/* Small - Inputs, buttons */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);

/* Medium - Cards */
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 
             0 2px 4px -2px rgba(0, 0, 0, 0.1);

/* Large - Modals, dropdowns */
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 
             0 4px 6px -4px rgba(0, 0, 0, 0.1);

/* Extra Large - Feature highlights */
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 
             0 8px 10px -6px rgba(0, 0, 0, 0.1);

/* Colored - Primary buttons */
--shadow-primary: 0 4px 14px 0 rgba(59, 130, 246, 0.39);

/* Colored Dark - Primary buttons (dark mode) */
--shadow-primary-dark: 0 4px 14px 0 rgba(59, 130, 246, 0.25);
```

---

## Component Patterns

### Buttons

**Primary Button**
- Background: `--gradient-primary`
- Text: White
- Shadow: `--shadow-primary`
- Hover: Scale 1.02, brighter shadow
- Active: Scale 0.98
- Border-radius: `rounded-lg`
- Padding: `px-4 py-2`

**Secondary Button**
- Background: `--bg-secondary`
- Border: 1px solid `--border`
- Text: `--text-primary`
- Hover: Background darken 5%

**Ghost Button**
- Background: Transparent
- Text: `--text-secondary`
- Hover: Background `--bg-secondary`

### Cards

**Standard Card**
- Background: `--bg-primary` / `--glass-bg` for glass
- Border: 1px solid `--border` / `--glass-border`
- Border-radius: `rounded-xl`
- Shadow: `--shadow-md`
- Padding: `p-6`

**Interactive Card**
- Hover: Shadow `--shadow-lg`, translateY -2px
- Transition: `all 0.2s ease-out`
- Cursor: Pointer

### Inputs

**Text Input**
- Background: `--bg-primary`
- Border: 1px solid `--border`
- Border-radius: `rounded-lg`
- Focus: Ring 2px `--primary-500`, border `--primary-500`
- Padding: `px-3 py-2`
- Min-height: 40px (touch)

**Floating Label Input**
- Label transitions up on focus/filled
- Scale: 0.85 on float
- Color: `--primary-500` on focus

### Badges

| Variant | Background | Text | Border |
|---------|------------|------|--------|
| Default | `--bg-secondary` | `--text-primary` | `--border` |
| Primary | `--primary-100` | `--primary-700` | `--primary-200` |
| Success | `rgba(16, 185, 129, 0.1)` | `#10b981` | `rgba(16, 185, 129, 0.2)` |
| Warning | `rgba(245, 158, 11, 0.1)` | `#f59e0b` | `rgba(245, 158, 11, 0.2)` |
| Error | `rgba(239, 68, 68, 0.1)` | `#ef4444` | `rgba(239, 68, 68, 0.2)` |

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
/* Fade In Up */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Scale In */
@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Slide In Right */
@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Pulse Ring */
@keyframes pulseRing {
  0% {
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(59, 130, 246, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0);
  }
}

/* Shimmer (Skeleton) */
@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}
```

---

## Glassmorphism

```css
.glass {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.glass-dark {
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.glass-card {
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.1) 0%,
    rgba(255, 255, 255, 0.05) 100%
  );
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
}
```

---

## Accessibility

### Focus States

- All interactive elements must have visible focus
- Focus ring: 2px solid `--primary-500`, offset 2px
- Focus-visible for keyboard only

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Color Contrast

- All text meets WCAG AA (4.5:1 for normal, 3:1 for large)
- Interactive elements have sufficient contrast
- Don't rely on color alone for information

### ARIA Patterns

- Use semantic HTML first
- Add ARIA labels when semantics aren't enough
- Include `aria-live` regions for dynamic content
- Support keyboard navigation

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

## Usage Examples

### Component Example

```tsx
// Button with gradient and hover effects
<button className="
  relative overflow-hidden
  px-6 py-3 rounded-lg
  bg-gradient-to-r from-blue-600 to-violet-600
  text-white font-semibold
  shadow-lg shadow-blue-500/30
  transition-all duration-200 ease-out
  hover:shadow-xl hover:shadow-blue-500/40
  hover:scale-[1.02]
  active:scale-[0.98]
  focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
">
  <span className="relative z-10">Get Started</span>
  <span className="absolute inset-0 bg-gradient-to-r from-blue-700 to-violet-700 opacity-0 hover:opacity-100 transition-opacity" />
</button>
```

### Glass Card Example

```tsx
<div className="
  relative
  rounded-2xl
  bg-white/70 dark:bg-slate-900/70
  backdrop-blur-xl
  border border-white/20 dark:border-white/10
  shadow-xl
  overflow-hidden
">
  <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-violet-500/5" />
  <div className="relative p-6">
    {/* Content */}
  </div>
</div>
```

---

## Implementation Notes

1. **Tailwind CSS v4**: Uses CSS-first configuration
2. **CSS Variables**: All colors defined as CSS custom properties
3. **Dark Mode**: Use `dark:` prefix classes
4. **Animations**: Framer Motion for React animations
5. **Icons**: Lucide React for consistent iconography
