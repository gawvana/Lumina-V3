import React from 'react';
import { Button } from './Button';
import { clsx } from 'clsx';

export interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
  compact?: boolean;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({ message = 'Произошла ошибка', onRetry, compact, className }) => {
  return (
    <div className={clsx('flex flex-col items-center justify-center text-center p-6', compact ? 'py-4' : 'py-12', className)}>
      <div className="w-12 h-12 rounded-full bg-danger-50 flex items-center justify-center text-danger-500 mb-4">
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <p className="text-sm text-surface-600 mb-4">{message}</p>
      {onRetry && (
        <Button variant="secondary" size={compact ? 'sm' : 'md'} onClick={onRetry}>
          Повторить
        </Button>
      )}
    </div>
  );
};
