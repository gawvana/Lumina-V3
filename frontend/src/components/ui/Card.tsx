import React from 'react';
import { clsx } from 'clsx';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'elevated' | 'flat';
  padding?: 'none' | 'compact' | 'default' | 'spacious';
  interactive?: boolean;
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ variant = 'elevated', padding = 'default', interactive = false, className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={clsx(
          'rounded-2xl overflow-hidden transition-all',
          {
            'bg-white shadow-md': variant === 'elevated',
            'bg-surface-50 border border-surface-200': variant === 'flat',
            'p-0': padding === 'none',
            'p-3': padding === 'compact',
            'p-5': padding === 'default',
            'p-8': padding === 'spacious',
            'hover:shadow-lg cursor-pointer active:scale-[0.98]': interactive && props.onClick
          },
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);
Card.displayName = 'Card';
