import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, Button, Badge, Avatar } from '../../components/ui';

export default function AdminDashboard() {
  const { t } = useTranslation();

  const [flags, setFlags] = useState({
    gamification: true,
    second_chance: true,
    voice_grading: false,
    video_circles: false,
  });

  const [inviteRole, setInviteRole] = useState('teacher');
  const [createdInvite, setCreatedInvite] = useState<string | null>(null);

  const toggleFlag = (key: keyof typeof flags) => {
    setFlags(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleCreateInvite = () => {
    const token = 'lumina_' + Math.random().toString(36).substring(2, 10);
    setCreatedInvite(`https://t.me/LuminzBot?start=inv_${token}`);
  };

  const auditLogs = [
    { time: '12:28', user: 'admin@school42.uz', action: 'FEATURE_FLAG_UPDATE', detail: 'voice_grading: off' },
    { time: '11:45', user: 'smirnov@school42.uz', action: 'GRADE_CREATE', detail: '9-A • Алгебра • 5' },
    { time: '10:15', user: 'admin@school42.uz', action: 'INVITE_CREATE', detail: 'role: teacher' },
    { time: '09:00', user: 'system', action: 'STREAK_SYNC', detail: '854 students processed' },
  ];

  return (
    <div className="space-y-4">
      <Card className="p-4 border border-surface-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Avatar name="Школа №42" size="lg" />
            <div>
              <h1 className="font-bold text-surface-900 text-lg">Школа-лицей №42</h1>
              <p className="text-xs text-surface-500 font-medium">Административная консоль • Ташкент</p>
            </div>
          </div>
          <Badge variant="default" size="sm">Admin</Badge>
        </div>
      </Card>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <Card className="p-3 text-center border border-surface-200">
          <p className="text-xs text-surface-500 font-medium">{t('total_students')}</p>
          <p className="text-xl font-extrabold text-primary-600 mt-0.5">854</p>
        </Card>
        <Card className="p-3 text-center border border-surface-200">
          <p className="text-xs text-surface-500 font-medium">{t('total_teachers')}</p>
          <p className="text-xl font-extrabold text-indigo-600 mt-0.5">62</p>
        </Card>
        <Card className="p-3 text-center border border-surface-200">
          <p className="text-xs text-surface-500 font-medium">{t('total_classes')}</p>
          <p className="text-xl font-extrabold text-surface-900 mt-0.5">28</p>
        </Card>
        <Card className="p-3 text-center border border-surface-200">
          <p className="text-xs text-surface-500 font-medium">{t('attendance_rate')}</p>
          <p className="text-xl font-extrabold text-emerald-600 mt-0.5">96.4%</p>
        </Card>
      </div>

      <Card className="p-4 border border-surface-200 space-y-3">
        <h2 className="font-bold text-surface-900 text-base">{t('create_invite')}</h2>
        <div className="flex flex-col sm:flex-row gap-2">
          <select
            value={inviteRole}
            onChange={(e) => setInviteRole(e.target.value)}
            className="p-2.5 text-sm rounded-xl border border-surface-300 bg-white font-medium focus:ring-2 focus:ring-primary-500 focus:outline-none"
          >
            <option value="teacher">Роль: Преподаватель</option>
            <option value="student">Роль: Ученик</option>
            <option value="parent">Роль: Родитель</option>
          </select>
          <Button size="md" variant="primary" onClick={handleCreateInvite}>
            {t('generate_link')}
          </Button>
        </div>

        {createdInvite && (
          <div className="p-3 bg-primary-50 border border-primary-200 rounded-xl space-y-1.5">
            <p className="text-xs font-semibold text-primary-800">Ссылка создана и готова к отправке:</p>
            <div className="flex items-center space-x-2">
              <input
                type="text"
                readOnly
                value={createdInvite}
                className="flex-1 p-2 text-xs font-mono bg-white rounded-lg border border-primary-300 select-all"
              />
              <Button size="sm" variant="secondary" onClick={() => navigator.clipboard?.writeText(createdInvite)}>
                Копировать
              </Button>
            </div>
          </div>
        )}
      </Card>

      <Card className="p-4 border border-surface-200">
        <h2 className="font-bold text-surface-900 text-base mb-3">{t('feature_flags')}</h2>
        <div className="space-y-2.5">
          {[
            { key: 'gamification', label: 'Геймификация (XP, Уровни, Достижения)', active: flags.gamification },
            { key: 'second_chance', label: 'Second Chance (Право на исправление оценок)', active: flags.second_chance },
            { key: 'voice_grading', label: 'AI Voice Grading (Экспериментально)', active: flags.voice_grading },
            { key: 'video_circles', label: 'Видеокружочки в домашних заданиях', active: flags.video_circles },
          ].map((item) => (
            <div key={item.key} className="flex items-center justify-between p-2.5 bg-surface-50 rounded-xl border border-surface-200">
              <span className="text-xs font-semibold text-surface-800">{item.label}</span>
              <button
                onClick={() => toggleFlag(item.key as any)}
                className={`w-11 h-6 flex items-center rounded-full p-1 transition-colors ${
                  item.active ? 'bg-primary-600' : 'bg-surface-300'
                }`}
              >
                <div
                  className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform ${
                    item.active ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-4 border border-surface-200">
        <h2 className="font-bold text-surface-900 text-base mb-3">{t('audit_logs')}</h2>
        <div className="divide-y divide-surface-200">
          {auditLogs.map((log, idx) => (
            <div key={idx} className="py-2 flex items-center justify-between text-xs first:pt-0 last:pb-0">
              <div className="flex items-center space-x-2">
                <span className="font-mono text-surface-400">{log.time}</span>
                <span className="font-semibold text-surface-800">{log.action}</span>
                <span className="text-surface-500">({log.detail})</span>
              </div>
              <span className="text-surface-400 font-mono">{log.user}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
