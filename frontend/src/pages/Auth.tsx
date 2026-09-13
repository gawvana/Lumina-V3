import React from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from '../components/ui/Button';

export default function Auth() {
  const { t } = useTranslation();
  return (
    <div className="flex flex-col items-center justify-center h-screen space-y-6">
      <h1 className="text-3xl font-bold">{t('welcome')}</h1>
      <Button size="lg">{t('login')}</Button>
    </div>
  );
}