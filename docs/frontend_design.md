# Frontend Design Document

## Overview

The CompliantByDefault frontend is a Next.js application that provides an intuitive web interface for scanning repositories and viewing SOC 2 compliance reports.

## Design Principles

1. **Simplicity** - Clear, uncluttered interface focusing on essential actions
2. **Responsiveness** - Mobile-first design that works on all screen sizes
3. **Feedback** - Real-time updates on scan progress and clear error messages
4. **Accessibility** - WCAG 2.1 AA compliance with semantic HTML
5. **Performance** - Fast page loads with code splitting and lazy loading

## User Flows

### Flow 1: New User Journey

```
Landing Page → Learn about features → Click "Start Scanning"
    ↓
Scan Page → Select repository type → Enter details → Start scan
    ↓
Progress Page → Watch real-time updates → Auto-redirect
    ↓
Report Page → View scores → Explore findings → Download report
```

### Flow 2: Returning User

```
Landing Page → Click "Scan Repository" (navbar)
    ↓
Scan Page → Quick start (remembered preferences)
    ↓
Report Page → Access recent scans
```

## Page Designs

### 1. Landing Page (`/`)

**Purpose**: Introduce product and drive users to scan

**Sections**:
1. **Hero**
   - Large heading with emoji
   - Value proposition
   - Primary CTA button
   - Background gradient

2. **Features Grid**
   - 6 feature cards with icons
   - Concise descriptions
   - Visual consistency

3. **SOC 2 Controls**
   - Grid of 9 controls
   - Name + description
   - Educational content

4. **Bottom CTA**
   - Repeat call-to-action
   - Sticky or prominent placement

**Design Tokens**:
```css
Background: Linear gradient (blue-50 to indigo-100)
Card: White with shadow-md
Heading: 5xl-6xl font, bold, gray-900
CTA: primary-600 bg, hover:primary-700
```

### 2. Scan Page (`/scan`)

**Purpose**: Capture scan inputs and initiate analysis

**Components**:

1. **Page Header**
   - Title: "Scan Repository"
   - Subtitle with instructions
   - Breadcrumb navigation

2. **RepoSelector Component**
   - Tab switcher (GitHub / Local)
   - Dynamic form fields
   - Validation feedback
   - Loading state on submit

3. **ScanProgress Component** (after submit)
   - Replaces form
   - Animated spinner
   - Status messages
   - Progress bar
   - Job ID display

**States**:
- **Idle**: Form visible, ready for input
- **Submitting**: Button disabled, "Starting..." text
- **Scanning**: Progress component, polling backend
- **Error**: Red banner with error message, retry option

### 3. Report Page (`/report/[id]`)

**Purpose**: Display comprehensive compliance analysis

**Layout**:

```
┌─────────────────────────────────────────┐
│ Navbar                                   │
├─────────────────────────────────────────┤
│ Header (Title, Meta, Actions)           │
├─────────────────────────────────────────┤
│ Score Cards (4-column grid)             │
│ - Overall Score | Total Findings |      │
│   Controls Compliant | Risk Level       │
├─────────────────────────────────────────┤
│ AI Analysis (White card)                │
│ - Posture assessment                    │
├─────────────────────────────────────────┤
│ Top Recommendations (White card)        │
│ - Priority-sorted list                  │
│ - Color-coded badges                    │
├─────────────────────────────────────────┤
│ Control Coverage Grid                   │
│ - 3-column responsive grid              │
│ - Status icons (✅⚠️❌)                 │
├─────────────────────────────────────────┤
│ Findings Table                          │
│ - Filters (Severity, Control)           │
│ - Sort options                          │
│ - Pagination                            │
└─────────────────────────────────────────┘
```

**Interactions**:
- Click control card → scroll to findings for that control
- Filter/sort findings → instant update
- Pagination → smooth transition
- Download button → trigger file download

## Component Library

### Navbar

**Props**: None (static)

**Design**:
```
┌──────────────────────────────────────────────────────────┐
│ 🛡️ CompliantByDefault    Home  Scan Repository  │  Info │
└──────────────────────────────────────────────────────────┘
```

- Fixed height: 64px
- White background, shadow
- Logo/brand on left
- Nav links center
- Info/actions right
- Mobile: Hamburger menu

### RepoSelector

**Props**:
- `onScan: (type, value, token?) => void`
- `isLoading: boolean`

**Features**:
- Tab buttons for type selection
- Conditional field rendering
- Input validation (URL format, path existence)
- Helper text below inputs
- Full-width submit button
- Disabled state when loading

**Styling**:
- Card container (white, rounded, shadow)
- Primary color for active tab
- Gray for inactive
- Focus rings on inputs

### ScanProgress

**Props**:
- `jobId: string`

**Features**:
- Auto-polling (2s interval)
- Progress bar (0-100%)
- Status messages (rotating)
- Error handling with retry
- Timeout detection (2 min)
- Auto-redirect on completion

**Styling**:
- Centered layout
- Animated spinner (primary color)
- Progress bar with smooth animation
- Subtle text (job ID, timing)

### ReportCard

**Props**:
- `score: ScoreData`
- `summary: ReportSummary`

**Features**:
- 4-column responsive grid
- Dynamic color based on score
- Grade badge (A-F)
- Severity breakdown
- Progress indicators

**Design**:
```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Overall Score│ │Total Findings│ │   Controls   │ │  Risk Level  │
│              │ │              │ │   Compliant  │ │              │
│      73      │ │      42      │ │     7/9      │ │    Medium    │
│   Grade: C   │ │ 🔴2 🟠5 🟡15│ │  ████░░ 78%  │ │  High risks  │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

### FindingsTable

**Props**:
- `findings: Finding[]`

**Features**:
- Filter dropdowns (severity, control)
- Sort selector (severity, file, control)
- Pagination (20 items/page)
- Color-coded severity badges
- Expandable rows (future)
- Responsive (horizontal scroll on mobile)

**Columns**:
1. Severity (badge)
2. Type
3. File (truncated, tooltip on hover)
4. Line
5. Control
6. Message (with recommendation)

## Design System

### Colors

```css
Primary Blue:
  50:  #f0f9ff
  100: #e0f2fe
  200: #bae6fd
  500: #0ea5e9 (main)
  600: #0284c7 (dark)
  700: #0369a1 (darker)

Severity Colors:
  Critical: red-600 (#dc2626)
  High:     orange-600 (#ea580c)
  Medium:   yellow-600 (#ca8a04)
  Low:      blue-600 (#2563eb)
  Info:     gray-600 (#4b5563)

Status Colors:
  Compliant:     green-600 (#16a34a)
  Partial:       yellow-600 (#ca8a04)
  Non-compliant: red-600 (#dc2626)
```

### Typography

```css
Headings:
  h1: text-4xl md:text-5xl font-bold
  h2: text-3xl font-bold
  h3: text-2xl font-bold
  h4: text-xl font-semibold

Body:
  Base: text-base (16px)
  Small: text-sm (14px)
  Tiny: text-xs (12px)

Font Family: System UI stack
```

### Spacing

```css
Base unit: 0.25rem (4px)

Common values:
  1: 0.25rem (4px)
  2: 0.5rem (8px)
  4: 1rem (16px)
  6: 1.5rem (24px)
  8: 2rem (32px)
  12: 3rem (48px)
  16: 4rem (64px)
```

### Shadows

```css
sm: 0 1px 2px rgba(0,0,0,0.05)
md: 0 4px 6px rgba(0,0,0,0.07)
lg: 0 10px 15px rgba(0,0,0,0.1)
```

### Border Radius

```css
sm: 0.125rem (2px)
md: 0.375rem (6px)
lg: 0.5rem (8px)
xl: 0.75rem (12px)
full: 9999px (circle)
```

## Responsive Breakpoints

```css
sm: 640px   // Phone landscape, tablet portrait
md: 768px   // Tablet
lg: 1024px  // Desktop
xl: 1280px  // Large desktop
```

**Responsive Strategy**:
- Mobile-first CSS
- Grid collapses to single column on mobile
- Tables become scrollable
- Navbar collapses to hamburger menu
- Font sizes reduce slightly

## Accessibility

1. **Semantic HTML**
   - Proper heading hierarchy (h1 → h2 → h3)
   - `<nav>`, `<main>`, `<section>` landmarks
   - `<button>` for actions, `<a>` for navigation

2. **ARIA Labels**
   - `aria-label` on icon-only buttons
   - `aria-live` for dynamic content (scan progress)
   - `role="status"` for status messages

3. **Keyboard Navigation**
   - All interactive elements focusable
   - Visible focus indicators
   - Skip links for main content

4. **Color Contrast**
   - WCAG AA minimum (4.5:1 for normal text)
   - Don't rely solely on color (use icons + text)

5. **Screen Readers**
   - Alt text for meaningful images/icons
   - Descriptive link text (no "click here")

## Performance Optimizations

1. **Code Splitting**
   - Automatic route-based splitting (Next.js)
   - Dynamic imports for heavy components

2. **Image Optimization**
   - Next.js Image component
   - WebP format with fallbacks
   - Lazy loading below fold

3. **API Calls**
   - Debounce search inputs
   - Cache GET requests
   - Cancel pending requests on unmount

4. **Bundle Size**
   - Tree shaking
   - Minimize dependencies
   - Use production builds

5. **Rendering**
   - Static generation where possible
   - Client-side hydration
   - Avoid large list re-renders

## Testing Strategy

### Unit Tests
- Component rendering
- User interactions (clicks, form submits)
- API client functions
- Utility functions

### Integration Tests
- Page-to-page navigation
- Form submission → API call → redirect
- Error handling flows

### E2E Tests (Future)
- Full scan workflow
- Report viewing
- Filter/sort interactions

## Future Enhancements

1. **Dark Mode** - Toggle in navbar, persisted preference
2. **Historical Trends** - Chart showing score improvements over time
3. **Comparison View** - Side-by-side of two scans
4. **Export Options** - PDF, CSV, email reports
5. **Collaborative Features** - Share reports, comments
6. **Webhooks** - Notify Slack/email on scan completion
7. **Customization** - User-defined severity weights, control priorities
8. **Internationalization** - Multi-language support

## Browser Support

**Tested and Supported**:
- Chrome 90+ ✅
- Firefox 88+ ✅
- Safari 14+ ✅
- Edge 90+ ✅

**Mobile**:
- iOS Safari 14+ ✅
- Chrome Mobile ✅
- Samsung Internet ✅

**Not Supported**:
- IE 11 ❌
- Opera Mini ❌
