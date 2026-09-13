import React from 'react';
import { clsx } from 'clsx';

export interface BadgeProps {
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  dot?: boolean;
  count?: number;
  maxCount?: number;
  children?: React.ReactNode;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ variant = 'default', size = 'md', dot, count, maxCount = 99, children, className }) => {

  if (dot) {
    return (
      <span className={clsx(
        'inline-block w-2 h-2 rounded-full',
        {
          'bg-surface-500': variant === 'default',
          'bg-primary-500': variant === 'primary',
          'bg-success-500': variant === 'success',
          'bg-warning-500': variant === 'warning',
          'bg-danger-500': variant === 'danger',
        },
        className
      )} />
    );
  }

  const displayCount = count !== undefined ? (count > maxCount ? `${maxCount}+` : count) : children;

  return (
    <span className={clsx(
      'inline-flex items-center justify-center px-2 py-0.5 text-xs font-medium rounded-full',
      {
        'bg-surface-100 text-surface-800': variant === 'default',
        'bg-primary-100 text-primary-800': variant === 'primary',
        'bg-success-100 text-success-800': variant === 'success',
        'bg-warning-100 text-warning-800': variant === 'warning',
        'bg-danger-100 text-danger-800': variant === 'danger',
      },
      className
    )}>
      {displayCount}
    </span>
  );
};
