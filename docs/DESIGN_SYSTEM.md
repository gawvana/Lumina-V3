# Lumina V3 — Design System

## Design Principles

1. **Clarity** — Every element communicates its purpose immediately
2. **Simplicity** — Remove everything unnecessary
3. **Hierarchy** — Visual weight guides attention
4. **Consistency** — Same patterns, same results
5. **Motion** — Purposeful animation that aids understanding
6. **Restraint** — Advanced features through progressive disclosure

## Design Tokens

### Typography
```css
--font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-size-xs: 0.75rem;    /* 12px */
--font-size-sm: 0.875rem;   /* 14px */
--font-size-base: 1rem;     /* 16px */
--font-size-lg: 1.125rem;   /* 18px */
--font-size-xl: 1.25rem;    /* 20px */
--font-size-2xl: 1.5rem;    /* 24px */
--font-size-3xl: 1.875rem;  /* 30px */
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;
```

### Spacing
```css
--space-0: 0;
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
```

### Color System
```css
/* Primary */
--color-primary-50: #f0f4ff;
--color-primary-500: #5c7cfa;
--color-primary-700: #4263eb;

/* Surface (adapts to Telegram theme) */
--color-bg: var(--tg-theme-bg-color, #ffffff);
--color-surface: var(--tg-theme-secondary-bg-color, #f1f3f5);
--color-text: var(--tg-theme-text-color, #212529);
--color-hint: var(--tg-theme-hint-color, #868e96);
--color-link: var(--tg-theme-link-color, #4263eb);
--color-button: var(--tg-theme-button-color, #5c7cfa);
--color-button-text: var(--tg-theme-button-text-color, #ffffff);

/* Semantic */
--color-success: #40c057;
--color-warning: #fab005;
--color-danger: #fa5252;
--color-info: #339af0;
```

### Border Radius
```css
--radius-sm: 8px;
--radius-md: 12px;
--radius-lg: 16px;
--radius-xl: 20px;
--radius-2xl: 24px;
--radius-full: 9999px;
```

### Elevation
```css
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.12);
```

### Motion
```css
--duration-fast: 150ms;
--duration-normal: 250ms;
--duration-slow: 350ms;
--easing-default: cubic-bezier(0.2, 0, 0, 1);
--easing-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
```

## Component Library

### Button
Variants: `primary`, `secondary`, `ghost`, `danger`
Sizes: `sm` (32px), `md` (40px), `lg` (48px)
States: default, hover, active, disabled, loading

### Card
Variants: `elevated` (with shadow), `flat` (background only)
Padding: `compact`, `default`, `spacious`

### Input
Types: text, password, search, textarea
Features: label, placeholder, error message, helper text, left/right icons

### Modal
Full-screen overlay with backdrop blur, centered content, close on backdrop click

### Sheet (Bottom Sheet)
Drag handle, snap points (25%, 50%, 75%, 100%), swipe to dismiss

### Toast
Variants: `success`, `error`, `warning`, `info`
Auto-dismiss with configurable duration, stack management

### Tabs
Horizontal tabs with animated indicator, scrollable overflow

### Avatar
Sizes: `xs` (24px), `sm` (32px), `md` (40px), `lg` (56px), `xl` (80px)
Fallback: initials from name

### Badge
Variants: `default`, `success`, `warning`, `danger`

### Skeleton
Pulse animation for loading states, rectangle and circle variants

### EmptyState
Icon + title + description + optional action button

### ErrorState
Error icon + message + retry button

### Table
Responsive with horizontal scroll, sortable headers, loading skeleton

### List
Items with left icon/avatar, title/subtitle, right content, dividers

## Responsive Breakpoints

| Width | Target |
|-------|--------|
| 320px | iPhone SE |
| 360px | Small Android |
| 390px | iPhone 14 |
| 430px | iPhone 14 Pro Max |
| 480px | Large phones |
| 768px | Tablets |
| 1024px | Small desktops |
| 1440px+ | Large desktops |

## Telegram Integration

### Theme Parameters
Sync with Telegram theme via CSS custom properties:
- `--tg-theme-bg-color`
- `--tg-theme-text-color`
- `--tg-theme-hint-color`
- `--tg-theme-link-color`
- `--tg-theme-button-color`
- `--tg-theme-button-text-color`
- `--tg-theme-secondary-bg-color`

### Platform Features
- `BackButton`: Show/hide based on navigation depth
- `MainButton`: Context-aware primary action
- `HapticFeedback`: Tactile feedback for key interactions
- `expand()`: Full-screen mode
- Safe area insets for notched devices

## Accessibility

- Color contrast ratio ≥ 4.5:1 (WCAG AA)
- Touch targets ≥ 44×44px
- Focus indicators for keyboard navigation
- Reduced motion support via `prefers-reduced-motion`
- Semantic HTML and ARIA attributes
- Screen reader-friendly content structure
