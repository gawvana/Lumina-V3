import React from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const Layout: React.FC = () => {
  const { t, i18n } = useTranslation();
  const location = useLocation();

  const toggleLanguage = () => {
    const nextLang = i18n.language && i18n.language.startsWith('uz') ? 'ru' : 'uz';
    i18n.changeLanguage(nextLang);
  };

  const navItems = [
    { to: '/student', label: t('student_title'), icon: '🎓' },
    { to: '/teacher', label: t('teacher_title'), icon: '📚' },
    { to: '/parent', label: t('parent_title'), icon: '👨‍👩‍👧' },
    { to: '/admin', label: t('admin_title'), icon: '⚙️' },
  ];

  return (
    <div className="flex flex-col min-h-screen bg-surface-50 text-surface-900 font-sans pb-20">
      <header className="sticky top-0 z-30 flex items-center justify-between px-4 py-3 bg-white/90 backdrop-blur border-b border-surface-200 shadow-sm">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-primary-600 to-indigo-500 flex items-center justify-center text-white font-bold text-sm shadow-sm">
            L
          </div>
          <span className="font-bold tracking-tight text-surface-900 text-lg">Lumina OS</span>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={toggleLanguage}
            className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-surface-100 hover:bg-surface-200 border border-surface-300 transition-colors"
          >
            {i18n.language && i18n.language.startsWith('uz') ? "🇺🇿 O'zbek" : '🇷🇺 Русский'}
          </button>
        </div>
      </header>

      <main className="flex-1 p-4 max-w-2xl w-full mx-auto">
        <Outlet />
      </main>

      <nav className="fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur border-t border-surface-200 px-3 py-2 flex justify-around items-center max-w-2xl mx-auto shadow-lg">
        {navItems.map((item) => {
          const isActive = location.pathname.startsWith(item.to);
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={`flex flex-col items-center justify-center w-16 py-1 rounded-xl transition-all ${
                isActive
                  ? 'text-primary-600 font-semibold scale-105'
                  : 'text-surface-500 hover:text-surface-800'
              }`}
            >
              <span className="text-xl mb-0.5">{item.icon}</span>
              <span className="text-[10px] leading-tight truncate w-full text-center">
                {item.label.split(' ')[0]}
              </span>
            </NavLink>
          );
        })}
      </nav>
    </div>
  );
};

export default Layout;
