import { create } from 'zustand';

interface ThemeState {
  isDark: boolean;
  toggleDark: () => void;
}

export const useThemeStore = create<ThemeState>((set) => ({
  isDark: false,
  toggleDark: () => set((state) => ({ isDark: !state.isDark }))
}));