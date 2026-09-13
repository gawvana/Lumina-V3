import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, Button, Badge, Avatar } from '../../components/ui';

export default function ParentDashboard() {
  const { t } = useTranslation();

  const [activeChild, setActiveChild] = useState('1');
  const [absenceModal, setAbsenceModal] = useState(false);
  const [absenceReason, setAbsenceReason] = useState('');
  const [absenceSubmitted, setAbsenceSubmitted] = useState(false);

  const children = [
    { id: '1', name: 'Тимур', gradeLevel: '9-А класс', gpa: 4.85, attendance: '98%', streak: 7 },
    { id: '2', name: 'Алина', gradeLevel: '5-Б класс', gpa: 4.90, attendance: '100%', streak: 12 },
  ];

  const currentChild = children.find(c => c.id === activeChild) || children[0];

  const recentGrades = [
    { subject: 'Алгебра', grade: 5, date: 'Сегодня', comment: 'Отличная работа у доски' },
    { subject: 'Физика', grade: 5, date: 'Вчера', comment: 'Лабораторная работа выполнена на отлично' },
    { subject: 'Английский', grade: 4, date: '11 сен', comment: 'Устное эссе' },
  ];

  const announcements = [
    { id: '1', title: 'Родительское собрание', date: '20 сентября в 18:00', body: 'Обсуждение итогов первой четверти и подготовка к олимпиадам.' },
    { id: '2', title: 'Вакцинация и медосмотр', date: '18 сентября', body: 'Плановый медосмотр для учащихся 5-х и 9-х классов.' },
  ];

  const handleSendAbsence = (e: React.FormEvent) => {
    e.preventDefault();
    if (!absenceReason) return;
    setAbsenceSubmitted(true);
    setTimeout(() => {
      setAbsenceModal(false);
      setAbsenceSubmitted(false);
      setAbsenceReason('');
    }, 2000);
  };

  return (
    <div className="space-y-4">
      <Card className="p-4 border border-surface-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Avatar name="Алимова З." size="lg" />
            <div>
              <h1 className="font-bold text-surface-900 text-lg">Алимова Зарина</h1>
              <p className="text-xs text-surface-500 font-medium">Родительский контроль • {children.length} детей</p>
            </div>
          </div>
          <Badge variant="default" size="sm">Родитель</Badge>
        </div>

        <div className="mt-4 pt-3 border-t border-surface-200">
          <p className="text-xs font-semibold text-surface-500 mb-2 uppercase tracking-wide">{t('my_children')}</p>
          <div className="flex space-x-2">
            {children.map((child) => (
              <button
                key={child.id}
                onClick={() => setActiveChild(child.id)}
                className={`flex-1 p-2.5 rounded-xl border text-left transition-all ${
                  activeChild === child.id
                    ? 'bg-primary-50 border-primary-500 ring-1 ring-primary-500 text-primary-900 shadow-sm'
                    : 'bg-surface-50 border-surface-200 text-surface-700 hover:bg-surface-100'
                }`}
              >
                <p className="font-bold text-sm">{child.name}</p>
                <p className="text-xs text-surface-500">{child.gradeLevel}</p>
              </button>
            ))}
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-3 gap-2">
        <Card className="p-3 text-center border border-surface-200">
          <p className="text-xs text-surface-500 font-medium">GPA</p>
          <p className="text-xl font-extrabold text-emerald-600 mt-0.5">{currentChild.gpa}</p>
          <span className="text-[10px] text-surface-500">Отличник</span>
        </Card>
        <Card className="p-3 text-center border border-surface-200">
          <p className="text-xs text-surface-500 font-medium">Посещаемость</p>
          <p className="text-xl font-extrabold text-primary-600 mt-0.5">{currentChild.attendance}</p>
          <span className="text-[10px] text-surface-500">Без пропусков</span>
        </Card>
        <Card className="p-3 text-center border border-surface-200">
          <p className="text-xs text-surface-500 font-medium">Серия</p>
          <p className="text-xl font-extrabold text-amber-600 mt-0.5">🔥 {currentChild.streak}</p>
          <span className="text-[10px] text-surface-500">Дней подряд</span>
        </Card>
      </div>

      <Card className="p-4 border border-surface-200 bg-gradient-to-r from-primary-500/5 to-indigo-500/5">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-surface-900 text-sm">Заявление об отсутствии</h3>
            <p className="text-xs text-surface-500">Уведомите школу, если ребенок заболел или отсутствует</p>
          </div>
          <Button size="sm" variant="primary" onClick={() => setAbsenceModal(true)}>
            Подать заявку
          </Button>
        </div>
      </Card>

      {absenceModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-fade-in">
          <Card className="max-w-md w-full p-5 bg-white shadow-2xl border border-surface-200 space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="font-bold text-surface-900 text-base">Заявление об отсутствии ({currentChild.name})</h2>
              <button onClick={() => setAbsenceModal(false)} className="text-surface-400 hover:text-surface-700 font-bold text-lg">✕</button>
            </div>

            {absenceSubmitted ? (
              <div className="p-4 bg-emerald-50 border border-emerald-300 rounded-xl text-emerald-800 text-sm font-semibold text-center">
                ✓ Заявление успешно передано классному руководителю!
              </div>
            ) : (
              <form onSubmit={handleSendAbsence} className="space-y-3">
                <div>
                  <label className="block text-xs font-semibold text-surface-600 mb-1">Причина отсутствия</label>
                  <textarea
                    rows={3}
                    value={absenceReason}
                    onChange={(e) => setAbsenceReason(e.target.value)}
                    placeholder="Укажите причину (например: ОРВИ, справка будет предоставлена)..."
                    className="w-full p-2.5 text-sm rounded-xl border border-surface-300 focus:ring-2 focus:ring-primary-500 focus:outline-none"
                    required
                  />
                </div>
                <div className="flex justify-end space-x-2 pt-2">
                  <Button type="button" size="sm" variant="secondary" onClick={() => setAbsenceModal(false)}>
                    {t('cancel')}
                  </Button>
                  <Button type="submit" size="sm" variant="primary">
                    {t('submit')}
                  </Button>
                </div>
              </form>
            )}
          </Card>
        </div>
      )}

      <Card className="p-4 border border-surface-200">
        <h2 className="font-bold text-surface-900 text-base mb-3">Оценки и комментарии учителей</h2>
        <div className="divide-y divide-surface-200">
          {recentGrades.map((g, idx) => (
            <div key={idx} className="py-3 flex items-start justify-between first:pt-0 last:pb-0">
              <div>
                <div className="flex items-center space-x-2">
                  <p className="font-semibold text-sm text-surface-900">{g.subject}</p>
                  <span className="text-xs text-surface-400">• {g.date}</span>
                </div>
                <p className="text-xs text-surface-600 mt-0.5 italic">«{g.comment}»</p>
              </div>
              <div className="w-8 h-8 rounded-xl font-bold bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center justify-center text-sm shadow-sm">
                {g.grade}
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-4 border border-surface-200">
        <h2 className="font-bold text-surface-900 text-base mb-3">{t('announcements')}</h2>
        <div className="space-y-3">
          {announcements.map((ann) => (
            <div key={ann.id} className="p-3 bg-surface-50 rounded-xl border border-surface-200">
              <div className="flex justify-between items-center mb-1">
                <h3 className="font-bold text-sm text-surface-900">{ann.title}</h3>
                <span className="text-[10px] text-surface-500 font-medium">{ann.date}</span>
              </div>
              <p className="text-xs text-surface-600">{ann.body}</p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
