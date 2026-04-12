# ContentForge AI - UI Screenshots

This directory contains screenshots of the ContentForge AI user interface.

## Screenshots

### 1. Login Page (`login-page.png`)
The login page features a clean, centered card design with:
- Gradient background (blue to indigo)
- Centered authentication card
- Email and password inputs
- "Welcome Back" title with "Sign in to manage your content" subtitle
- Toggle between Sign In and Sign Up modes
- Loading state with spinner animation

**Components:**
- Card component with header and content sections
- Input fields with validation
- Button with loading state
- Error message display

### 2. Dashboard Overview (`dashboard-overview.png`)
The main dashboard interface includes:
- Sticky header with ContentForge logo and user email
- Left sidebar navigation with 5 tabs:
  - Content (active by default)
  - Projects
  - Distributions
  - Analytics
  - Settings
- Keyboard shortcuts info panel (Ctrl+N for new content, Ctrl+P for new project)
- Mobile-responsive hamburger menu
- Sign Out button

**Components:**
- Sidebar navigation with icons
- Header with logo and user info
- Responsive layout

### 3. Content Tab (`content-tab.png`)
The Content tab displays:
- "Your Content" header with "New Content" button
- List of content items in card format
- Each content card shows:
  - File icon
  - Title with status badge
  - Original text preview (truncated)
  - Creation date, source type, word count
  - Actions menu (View Details, Delete)
- Empty state with call-to-action
- Loading skeletons

**Components:**
- Content cards
- Status badges (pending, processing, completed, failed)
- Dropdown menus
- Skeleton loaders
- Empty state illustration

### 4. New Content Page (`content-new-page.png`)
The content creation interface:
- Form for adding new content
- Title input
- Original text textarea
- Source type selector
- Submit button
- Validation messages

### 5. Mobile Views (`*-mobile.png`)
Responsive design screenshots showing:
- Collapsed navigation
- Stacked layout
- Touch-friendly controls
- Bottom navigation on mobile

## Technical Details

**Stack:**
- Next.js 16.2.3 with App Router
- React 19.2.4
- Tailwind CSS 4.x
- Lucide React icons
- Supabase Auth

**UI Components:**
- Custom Card, Button, Input components in `/src/components/ui/`
- Consistent styling with Tailwind CSS
- Dark mode support (planned)
- Accessibility features (ARIA labels, keyboard navigation)

**Color Palette:**
- Primary: Blue (#3b82f6) to Indigo (#6366f1) gradient
- Background: Gray 50 (#f9fafb) to White
- Text: Gray 900 (#111827) for headings, Gray 600 (#6b7280) for secondary
- Status colors:
  - Pending: Yellow (#fef3c7)
  - Processing: Blue (#dbeafe)
  - Completed: Green (#dcfce7)
  - Failed: Red (#fee2e2)

## Notes

- All interactive elements have hover states
- Forms include loading and error states
- Responsive design works from mobile (375px) to desktop (1440px+)
- Keyboard shortcuts are documented in the UI
