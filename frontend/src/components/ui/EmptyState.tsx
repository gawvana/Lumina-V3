import React from 'react';
import { clsx } from 'clsx';

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
  compact?: boolean;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ icon, title, description, action, compact, className }) => {
  return (
    <div className={clsx('flex flex-col items-center justify-center text-center p-6', compact ? 'py-6' : 'py-12', className)}>
      {icon && (
        <div className={clsx('text-surface-300 mb-4', compact ? 'text-4xl' : 'text-6xl')}>
          {icon}
        </div>
      )}
      <h3 className={clsx('font-medium text-surface-900', compact ? 'text-base mb-1' : 'text-lg mb-2')}>{title}</h3>
      {description && <p className="text-sm text-surface-500 max-w-sm mb-6">{description}</p>}
      {action}
    </div>
  );
};
