import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const Layout: React.FC = () => {
  const { t } = useTranslation();
  return (
    <div className="flex flex-col h-screen pt-safe-top pb-safe-bottom">
      <main className="flex-1 overflow-y-auto p-4">
        <Outlet />
      </main>
      <nav className="flex justify-around p-4 border-t border-surface-200 bg-white">
        <Link to="/student" className="text-primary-600">{t('dashboard')}</Link>
        <Link to="/settings" className="text-surface-500">{t('settings')}</Link>
      </nav>
    </div>
  );
};
export default Layout;