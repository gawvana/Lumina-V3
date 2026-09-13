import React from 'react';
import { clsx } from 'clsx';

export interface ListItemProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'title'> {
  leftContent?: React.ReactNode;
  rightContent?: React.ReactNode;
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  divider?: boolean;
  interactive?: boolean;
}

export const ListItem = React.forwardRef<HTMLDivElement, ListItemProps>(
  ({ leftContent, rightContent, title, subtitle, divider, interactive, className, onClick, ...props }, ref) => {
    return (
      <div
        ref={ref}
        onClick={onClick}
        className={clsx(
          'flex items-center gap-3 py-3 px-4',
          {
            'border-b border-surface-100 last:border-b-0': divider,
            'cursor-pointer hover:bg-surface-50 active:bg-surface-100 transition-colors': interactive || onClick
          },
          className
        )}
        {...props}
      >
        {leftContent && <div className="flex-shrink-0">{leftContent}</div>}
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium text-surface-900 truncate">{title}</div>
          {subtitle && <div className="text-xs text-surface-500 truncate">{subtitle}</div>}
        </div>
        {rightContent && <div className="flex-shrink-0">{rightContent}</div>}
      </div>
    );
  }
);
ListItem.displayName = 'ListItem';

export const List = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, children, ...props }, ref) => (
    <div ref={ref} className={clsx('bg-white rounded-xl border border-surface-200 overflow-hidden', className)} {...props}>
      {children}
    </div>
  )
);
List.displayName = 'List';
