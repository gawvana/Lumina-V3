import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, Button, Badge, Avatar } from '../../components/ui';

export default function StudentHome() {
  const { t } = useTranslation();

  const [vibe, setVibe] = useState<string | null>('great');
  const [xp, setXp] = useState(450);
  const [streak] = useState(7);
  const [hwSubmitted, setHwSubmitted] = useState<Record<string, boolean>>({});

  const vibes = [
    { id: 'great', label: t('vibe_great') },
    { id: 'good', label: t('vibe_good') },
    { id: 'neutral', label: t('vibe_neutral') },
    { id: 'tired', label: t('vibe_tired') },
    { id: 'stressed', label: t('vibe_stressed') },
  ];

  const schedule = [
    { num: 1, subject: 'Алгебра', time: '08:30 - 09:15', room: '302', current: false },
    { num: 2, subject: 'Геометрия', time: '09:25 - 10:10', room: '302', current: true },
    { num: 3, subject: 'Физика', time: '10:25 - 11:10', room: '210', current: false },
    { num: 4, subject: 'Информатика', time: '11:20 - 12:05', room: '104', current: false },
    { num: 5, subject: 'Английский', time: '12:15 - 13:00', room: '405', current: false },
  ];

  const recentGrades = [
    { subject: 'Алгебра', grade: 5, date: 'Сегодня', teacher: 'Смирнов В.П.' },
    { subject: 'Физика', grade: 5, date: 'Вчера', teacher: 'Каримова Г.М.' },
    { subject: 'Английский', grade: 4, date: '11 сен', teacher: 'Иванова Е.А.' },
    { subject: 'История', grade: 5, date: '10 сен', teacher: 'Рахимов Д.Б.' },
  ];

  const homeworkList = [
    { id: 'hw-1', subject: 'Алгебра', title: 'Параграф 4, №124-130 (четные)', due: 'Завтра, 08:30' },
    { id: 'hw-2', subject: 'Физика', title: 'Лабораторная работа: Закон Ома', due: '15 сен, 10:00' },
  ];

  const handleSubmitHw = (id: string) => {
    if (!hwSubmitted[id]) {
      setHwSubmitted(prev => ({ ...prev, [id]: true }));
      setXp(prev => prev + 50);
    }
  };

  return (
    <div className="space-y-4">
      <Card className="p-4 bg-gradient-to-br from-indigo-500/10 via-white to-purple-500/10 border border-primary-200 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Avatar name="Тимур Алимов" size="lg" />
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="font-bold text-surface-900 text-lg leading-tight">Тимур Алимов</h1>
                <Badge variant="default" size="sm">Lvl 5</Badge>
              </div>
              <p className="text-xs text-surface-500 font-medium">9-А класс • №42 Мектеп</p>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center space-x-1 text-amber-600 font-bold text-sm bg-amber-50 px-2 py-1 rounded-lg border border-amber-200">
              <span>🔥</span>
              <span>{streak} {t('days')}</span>
            </div>
          </div>
        </div>

        <div className="mt-3 pt-3 border-t border-surface-200">
          <div className="flex justify-between text-xs font-semibold text-surface-600 mb-1">
            <span>{t('xp')}: {xp} XP</span>
            <span>Уровень 6 (600 XP)</span>
          </div>
          <div className="w-full bg-surface-200 h-2.5 rounded-full overflow-hidden">
            <div
              className="bg-gradient-to-r from-primary-500 to-indigo-600 h-full rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, (xp / 600) * 100)}%` }}
            />
          </div>
        </div>
      </Card>

      <Card className="p-3 border border-surface-200">
        <p className="text-xs font-semibold text-surface-500 mb-2 uppercase tracking-wide">
          {t('vibes_title')}
        </p>
        <div className="flex justify-between gap-1 overflow-x-auto pb-1">
          {vibes.map((v) => (
            <button
              key={v.id}
              onClick={() => setVibe(v.id)}
              className={`flex-1 py-1.5 px-2 text-xs font-medium rounded-xl border transition-all ${
                vibe === v.id
                  ? 'bg-primary-50 border-primary-500 text-primary-700 shadow-sm'
                  : 'bg-surface-50 border-surface-200 text-surface-700 hover:bg-surface-100'
              }`}
            >
              {v.label}
            </button>
          ))}
        </div>
      </Card>

      <div className="grid grid-cols-3 gap-2">
        <Card className="p-3 text-center border border-surface-200">
          <p className="text-xs text-surface-500 font-medium">GPA</p>
          <p className="text-xl font-extrabold text-emerald-600 mt-0.5">4.85</p>
          <span className="text-[10px] text-surface-500">из 5.0</span>
        </Card>
        <Card className="p-3 text-center border border-surface-200">
          <p className="text-xs text-surface-500 font-medium">Посещаемость</p>
          <p className="text-xl font-extrabold text-primary-600 mt-0.5">98%</p>
          <span className="text-[10px] text-surface-500">0 пропусков</span>
        </Card>
        <Card className="p-3 text-center border border-surface-200">
          <p className="text-xs text-surface-500 font-medium">Задания</p>
          <p className="text-xl font-extrabold text-indigo-600 mt-0.5">14/15</p>
          <span className="text-[10px] text-surface-500">Выполнено</span>
        </Card>
      </div>

      <Card className="p-4 border border-surface-200">
        <div className="flex justify-between items-center mb-3">
          <h2 className="font-bold text-surface-900 text-base">{t('today_schedule')}</h2>
          <Badge variant="default" size="sm">Пятница, 13 сен</Badge>
        </div>
        <div className="space-y-2">
          {schedule.map((item) => (
            <div
              key={item.num}
              className={`flex items-center justify-between p-2.5 rounded-xl border transition-all ${
                item.current
                  ? 'bg-primary-50/70 border-primary-300 ring-1 ring-primary-400'
                  : 'bg-surface-50 border-surface-200'
              }`}
            >
              <div className="flex items-center space-x-3">
                <div className={`w-6 h-6 rounded-lg font-bold text-xs flex items-center justify-center ${
                  item.current ? 'bg-primary-600 text-white' : 'bg-surface-200 text-surface-700'
                }`}>
                  {item.num}
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <p className="font-semibold text-sm text-surface-900">{item.subject}</p>
                    {item.current && (
                      <span className="inline-flex items-center px-1.5 py-0.2 text-[10px] font-bold bg-emerald-100 text-emerald-800 rounded">
                        Сейчас
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-surface-500">Кабинет {item.room}</p>
                </div>
              </div>
              <div className="text-xs text-surface-500 font-mono font-medium">
                {item.time}
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-4 border border-surface-200">
        <h2 className="font-bold text-surface-900 text-base mb-3">{t('pending_hw')}</h2>
        <div className="space-y-2.5">
          {homeworkList.map((hw) => {
            const isDone = hwSubmitted[hw.id];
            return (
              <div key={hw.id} className="p-3 bg-surface-50 rounded-xl border border-surface-200 flex flex-col gap-2">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-xs font-semibold text-primary-600 uppercase tracking-wide">{hw.subject}</span>
                    <h3 className="font-medium text-sm text-surface-900">{hw.title}</h3>
                  </div>
                  <Badge variant={isDone ? 'success' : 'warning'} size="sm">
                    {isDone ? 'Сдано' : hw.due}
                  </Badge>
                </div>
                <div className="flex justify-end">
                  <Button
                    size="sm"
                    variant={isDone ? 'secondary' : 'primary'}
                    disabled={isDone}
                    onClick={() => handleSubmitHw(hw.id)}
                  >
                    {isDone ? '✓ Отправлено' : t('submit_hw')}
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      <Card className="p-4 border border-surface-200">
        <h2 className="font-bold text-surface-900 text-base mb-3">{t('my_grades')}</h2>
        <div className="divide-y divide-surface-200">
          {recentGrades.map((g, idx) => (
            <div key={idx} className="py-2.5 flex items-center justify-between first:pt-0 last:pb-0">
              <div>
                <p className="font-semibold text-sm text-surface-900">{g.subject}</p>
                <p className="text-xs text-surface-500">{g.teacher} • {g.date}</p>
              </div>
              <div className={`w-8 h-8 rounded-xl font-bold flex items-center justify-center text-sm shadow-sm ${
                g.grade === 5
                  ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                  : 'bg-blue-100 text-blue-800 border border-blue-300'
              }`}>
                {g.grade}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
