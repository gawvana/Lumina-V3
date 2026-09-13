import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx } from 'clsx';
import { create } from 'zustand';

export interface ToastItem {
  id: string;
  message: string;
  type?: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
}

interface ToastStore {
  toasts: ToastItem[];
  add: (toast: Omit<ToastItem, 'id'>) => void;
  remove: (id: string) => void;
}

export const useToastStore = create<ToastStore>((set) => ({
  toasts: [],
  add: (toast) => {
    const id = Math.random().toString(36).substr(2, 9);
    set((state) => ({ toasts: [...state.toasts, { ...toast, id }] }));
    setTimeout(() => { set((state) => ({ toasts: state.toasts.filter(t => t.id !== id) })); }, toast.duration || 3000);
  },
  remove: (id) => set((state) => ({ toasts: state.toasts.filter(t => t.id !== id) }))
}));

export const ToastContainer: React.FC = () => {
  const toasts = useToastStore(state => state.toasts);
  
  return (
    <div className="fixed top-safe-top left-0 right-0 z-50 flex flex-col items-center gap-2 p-4 pointer-events-none">
      <AnimatePresence>
        {toasts.map(toast => (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, y: -20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.2 } }}
            className={clsx(
              'px-4 py-3 rounded-xl shadow-lg pointer-events-auto max-w-sm w-full text-sm font-medium',
              {
                'bg-success-500 text-white': toast.type === 'success',
                'bg-danger-500 text-white': toast.type === 'error',
                'bg-warning-500 text-white': toast.type === 'warning',
                'bg-surface-800 text-white': !toast.type || toast.type === 'info',
              }
            )}
          >
            {toast.message}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};
