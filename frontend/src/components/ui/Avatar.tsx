import React, { useState } from 'react';
import { clsx } from 'clsx';

export interface AvatarProps {
  src?: string;
  alt?: string;
  initials?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  online?: boolean;
  className?: string;
}

const sizeClasses = {
  xs: 'w-6 h-6 text-xs',
  sm: 'w-8 h-8 text-sm',
  md: 'w-10 h-10 text-base',
  lg: 'w-12 h-12 text-lg',
  xl: 'w-16 h-16 text-xl',
};

export const Avatar: React.FC<AvatarProps> = ({ src, alt, initials, size = 'md', online, className }) => {
  const [error, setError] = useState(false);
  const showFallback = !src || error;

  return (
    <div className={clsx('relative inline-flex flex-shrink-0', className)}>
      <div className={clsx(
        'rounded-full overflow-hidden flex items-center justify-center font-medium ring-2 ring-white',
        sizeClasses[size],
        showFallback ? 'bg-primary-100 text-primary-700' : 'bg-surface-200'
      )}>
        {showFallback ? (
          initials ? initials.slice(0, 2).toUpperCase() : '?'
        ) : (
          <img
            src={src}
            alt={alt || ''}
            onError={() => setError(true)}
            className="w-full h-full object-cover"
          />
        )}
      </div>
      {online !== undefined && (
        <span className={clsx(
          'absolute bottom-0 right-0 block rounded-full ring-2 ring-white bg-success-500',
          {
            'w-1.5 h-1.5': size === 'xs',
            'w-2 h-2': size === 'sm',
            'w-2.5 h-2.5': size === 'md',
            'w-3 h-3': size === 'lg' || size === 'xl',
            'bg-surface-400': !online
          }
        )} />
      )}
    </div>
  );
};
