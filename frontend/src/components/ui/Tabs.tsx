import React from 'react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';

export interface Tab {
  id: string;
  label: string;
}

export interface TabsProps {
  tabs: Tab[];
  activeId: string;
  onChange: (id: string) => void;
  className?: string;
}

export const Tabs: React.FC<TabsProps> = ({ tabs, activeId, onChange, className }) => {
  return (
    <div className={clsx('flex w-full overflow-x-auto no-scrollbar border-b border-surface-200', className)}>
      {tabs.map((tab) => {
        const isActive = activeId === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={clsx(
              'relative px-4 py-3 text-sm font-medium transition-colors whitespace-nowrap',
              isActive ? 'text-primary-600' : 'text-surface-500 hover:text-surface-900'
            )}
          >
            {tab.label}
            {isActive && (
              <motion.div
                layoutId="tabs-indicator"
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-600 rounded-t-full"
                transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              />
            )}
          </button>
        );
      })}
    </div>
  );
};
