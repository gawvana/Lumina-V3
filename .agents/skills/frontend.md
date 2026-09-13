# Lumina Mini App Frontend Skill

## Core Principles
- React 18, TypeScript strict, Vite 6, Tailwind CSS.
- Telegram Web App SDK: Viewport sizing, safe areas (`safe-top`, `safe-bottom`), BackButton, MainButton, HapticFeedback.
- Design System: Apple-inspired UX, progressive disclosure, 15 core UI components.
- State management: Zustand stores + TanStack Query.
- "No False Success": Never show "Saved" until server confirms with 200/201.
- UX States: `loading -> success -> error -> retry` for every operation.
- i18n: Zero hardcoded strings, complete RU/UZ translation catalogs.
