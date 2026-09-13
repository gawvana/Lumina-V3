import React from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Card, Button, Badge } from '../components/ui';

export default function Auth() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const isTelegram = typeof window !== 'undefined' && Boolean(window.Telegram?.WebApp?.initData);

  return (
    <div className="min-h-screen bg-surface-50 flex items-center justify-center p-4">
      <Card className="max-w-md w-full p-6 border border-surface-200 shadow-xl text-center space-y-6">
        <div className="w-16 h-16 rounded-3xl bg-gradient-to-tr from-primary-600 to-indigo-600 mx-auto flex items-center justify-center text-white font-extrabold text-2xl shadow-lg shadow-primary-500/30">
          L
        </div>

        <div>
          <h1 className="text-2xl font-black text-surface-900 tracking-tight">Lumina OS</h1>
          <p className="text-xs text-surface-500 font-medium mt-1">
            Telegram School Operating System
          </p>
          <div className="mt-2">
            <Badge variant={isTelegram ? 'success' : 'default'} size="sm">
              {isTelegram ? 'Telegram WebApp подключен' : 'Web Preview режим'}
            </Badge>
          </div>
        </div>

        <div className="space-y-2 pt-2">
          <p className="text-xs font-semibold text-surface-500 uppercase tracking-wide">
            Выберите профиль для входа:
          </p>
          <div className="grid grid-cols-2 gap-2">
            <Button variant="secondary" size="md" onClick={() => navigate('/student')}>
              🎓 Ученик
            </Button>
            <Button variant="secondary" size="md" onClick={() => navigate('/teacher')}>
              📚 Учитель
            </Button>
            <Button variant="secondary" size="md" onClick={() => navigate('/parent')}>
              👨‍👩‍👧 Родитель
            </Button>
            <Button variant="secondary" size="md" onClick={() => navigate('/admin')}>
              ⚙️ Админ
            </Button>
          </div>
        </div>

        <div className="pt-2 border-t border-surface-200">
          <Button
            variant="primary"
            size="lg"
            className="w-full"
            onClick={() => navigate('/student')}
          >
            {t('login')}
          </Button>
        </div>
      </Card>
    </div>
  );
}
