import React from 'react';
import { clsx } from 'clsx';

export interface Column<T> {
  key: string;
  title: string;
  render?: (row: T) => React.ReactNode;
  sortable?: boolean;
}

export interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  emptyText?: string;
  onSort?: (key: string) => void;
  sortBy?: string;
  sortDesc?: boolean;
  className?: string;
}

export const Table = <T extends Record<string, any>>({ 
  columns, data, loading, emptyText = 'Нет данных', onSort, sortBy, sortDesc, className 
}: TableProps<T>) => {
  
  return (
    <div className={clsx('w-full overflow-x-auto rounded-xl border border-surface-200 bg-white shadow-sm no-scrollbar', className)}>
      <table className="w-full text-left text-sm text-surface-600">
        <thead className="bg-surface-50 text-surface-900 border-b border-surface-200">
          <tr>
            {columns.map(col => (
              <th 
                key={col.key} 
                className={clsx('px-4 py-3 font-medium whitespace-nowrap', col.sortable && 'cursor-pointer select-none hover:bg-surface-100')}
                onClick={() => col.sortable && onSort?.(col.key)}
              >
                <div className="flex items-center gap-1">
                  {col.title}
                  {col.sortable && sortBy === col.key && (
                    <span className="text-surface-400 text-xs">{sortDesc ? '↓' : '↑'}</span>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-surface-100">
          {loading ? (
            Array.from({ length: 3 }).map((_, i) => (
              <tr key={i}>
                {columns.map(col => (
                  <td key={col.key} className="px-4 py-3"><div className="h-4 bg-surface-200 rounded animate-pulse w-3/4" /></td>
                ))}
              </tr>
            ))
          ) : data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-4 py-8 text-center text-surface-500">
                {emptyText}
              </td>
            </tr>
          ) : (
            data.map((row, i) => (
              <tr key={i} className="hover:bg-surface-50 transition-colors">
                {columns.map(col => (
                  <td key={col.key} className="px-4 py-3">
                    {col.render ? col.render(row) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};
