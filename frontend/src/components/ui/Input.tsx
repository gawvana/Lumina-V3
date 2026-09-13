import React, { useState } from 'react';
import { clsx } from 'clsx';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  onClear?: () => void;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, leftIcon, rightIcon, onClear, className, disabled, type, value, ...props }, ref) => {
    const isSearch = type === 'search';
    
    return (
      <div className={clsx('w-full flex flex-col gap-1.5', className)}>
        {label && <label className="text-sm font-medium text-surface-700">{label}</label>}
        <div className="relative flex items-center">
          {leftIcon && <div className="absolute left-3 text-surface-400">{leftIcon}</div>}
          <input
            ref={ref}
            type={isSearch ? 'text' : type}
            value={value}
            disabled={disabled}
            className={clsx(
              'w-full rounded-xl border bg-white px-4 py-2.5 text-surface-900 outline-none transition-all placeholder:text-surface-400',
              'focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20',
              {
                'border-danger-500 focus:border-danger-500 focus:ring-danger-500/20': error,
                'border-surface-200': !error,
                'pl-10': leftIcon,
                'pr-10': rightIcon || (isSearch && value),
                'opacity-50 cursor-not-allowed bg-surface-50': disabled
              }
            )}
            {...props}
          />
          {rightIcon && !isSearch && <div className="absolute right-3 text-surface-400">{rightIcon}</div>}
          {isSearch && value && onClear && (
            <button type="button" onClick={onClear} className="absolute right-3 text-surface-400 hover:text-surface-600">
              ✕
            </button>
          )}
        </div>
        {(error || helperText) && (
          <p className={clsx('text-xs', error ? 'text-danger-500' : 'text-surface-500')}>
            {error || helperText}
          </p>
        )}
      </div>
    );
  }
);
Input.displayName = 'Input';
