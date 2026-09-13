import React from 'react';
import { clsx } from 'clsx';

export interface SkeletonProps {
  variant?: 'text' | 'circle' | 'rect';
  width?: string | number;
  height?: string | number;
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({ variant = 'rect', width, height, className }) => {
  return (
    <div
      style={{ width, height }}
      className={clsx(
        'bg-surface-200 animate-pulse',
        {
          'rounded-md': variant === 'text',
          'rounded-full': variant === 'circle',
          'rounded-xl': variant === 'rect',
          'h-4 w-full': variant === 'text' && !height && !width,
        },
        className
      )}
    />
  );
};
