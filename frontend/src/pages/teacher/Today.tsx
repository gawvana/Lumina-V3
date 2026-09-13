import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, Button, Badge, Avatar } from '../../components/ui';

interface StudentRow {
  id: string;
  name: string;
  attendance: 'present' | 'absent' | 'late' | 'excused';
  grade: number | null;
}

export default function TeacherToday() {
  const { t } = useTranslation();

  const [selectedClass, setSelectedClass] = useState('9-A');
  const [randomStudent, setRandomStudent] = useState<string | null>(null);
  const [lastAction, setLastAction] = useState<{ studentId: string; prevGrade: number | null } | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const [students, setStudents] = useState<StudentRow[]>([
    { id: '1', name: 'Алимов Тимур', attendance: 'present', grade: 5 },
    { id: '2', name: 'Беляева София', attendance: 'present', grade: null },
    { id: '3', name: 'Васильев Даниил', attendance: 'late', grade: 4 },
    { id: '4', name: 'Дмитриева Анна', attendance: 'present', grade: null },
    { id: '5', name: 'Иванов Максим', attendance: 'absent', grade: null },
    { id: '6', name: 'Каримова Лейла', attendance: 'present', grade: 5 },
  ]);

  const handleAttendance = (id: string, status: 'present' | 'absent' | 'late' | 'excused') => {
    setStudents(prev => prev.map(s => s.id === id ? { ...s, attendance: status } : s));
  };

  const handleGrade = (id: string, grade: number) => {
    const student = students.find(s => s.id === id);
    if (!student) return;

    setLastAction({ studentId: id, prevGrade: student.grade });
    setStudents(prev => prev.map(s => s.id === id ? { ...s, grade } : s));
    setToastMessage(`Оценка ${grade} выставлена для ${student.name}`);
    setTimeout(() => setToastMessage(null), 4000);
  };

  const handleUndo = () => {
    if (!lastAction) return;
    setStudents(prev => prev.map(s => s.id === lastAction.studentId ? { ...s, grade: lastAction.prevGrade } : s));
    setLastAction(null);
    setToastMessage('Действие отменено');
    setTimeout(() => setToastMessage(null), 3000);
  };

  const pickRandomStudent = () => {
    const presentStudents = students.filter(s => s.attendance === 'present');
    if (presentStudents.length > 0) {
      const idx = Math.floor(Math.random() * presentStudents.length);
      setRandomStudent(presentStudents[idx].name);
    }
  };

  return (
    <div className="space-y-4">
      <Card className="p-4 border border-surface-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Avatar name="Смирнов В.П." size="lg" />
            <div>
              <h1 className="font-bold text-surface-900 text-lg">Смирнов Виктор Павлович</h1>
              <p className="text-xs text-surface-500 font-medium">Преподаватель математики • Кабинет 302</p>
            </div>
          </div>
          <Badge variant="success" size="sm">Идет урок</Badge>
        </div>

        <div className="flex space-x-2 mt-4 pt-3 border-t border-surface-200">
          {['9-A', '9-B', '10-A'].map((cls) => (
            <button
              key={cls}
              onClick={() => setSelectedClass(cls)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-colors ${
                selectedClass === cls
                  ? 'bg-primary-600 text-white shadow-sm'
                  : 'bg-surface-100 text-surface-600 hover:bg-surface-200'
              }`}
            >
              {cls} {cls === '9-A' && '• 2-й урок'}
            </button>
          ))}
        </div>
      </Card>

      <Card className="p-3 border border-surface-200 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Button size="sm" variant="secondary" onClick={pickRandomStudent}>
            {t('random_student')}
          </Button>
          {randomStudent && (
            <span className="text-xs font-bold text-primary-700 bg-primary-50 px-2.5 py-1 rounded-lg border border-primary-200">
              🎯 {randomStudent}
            </span>
          )}
        </div>
        {lastAction && (
          <Button size="sm" variant="ghost" onClick={handleUndo} className="text-amber-700 font-semibold">
            ↩ {t('undo')}
          </Button>
        )}
      </Card>

      {toastMessage && (
        <div className="p-2.5 bg-emerald-50 border border-emerald-300 text-emerald-800 text-xs font-semibold rounded-xl flex items-center justify-between shadow-sm">
          <span>✓ {toastMessage}</span>
          {lastAction && (
            <button onClick={handleUndo} className="underline font-bold ml-2">
              {t('undo')}
            </button>
          )}
        </div>
      )}

      <Card className="p-4 border border-surface-200">
        <div className="flex justify-between items-center mb-3">
          <div>
            <h2 className="font-bold text-surface-900 text-base">{t('quick_grading')} • {selectedClass}</h2>
            <p className="text-xs text-surface-500">Посещаемость и текущие оценки за урок</p>
          </div>
          <Badge variant="default" size="sm">Всего: {students.length}</Badge>
        </div>

        <div className="divide-y divide-surface-200">
          {students.map((st) => (
            <div key={st.id} className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center space-x-3">
                <Avatar name={st.name} size="sm" />
                <div>
                  <p className="font-semibold text-sm text-surface-900">{st.name}</p>
                  <div className="flex items-center space-x-1 mt-1">
                    {(['present', 'absent', 'late', 'excused'] as const).map((att) => (
                      <button
                        key={att}
                        onClick={() => handleAttendance(st.id, att)}
                        className={`px-1.5 py-0.5 text-[10px] font-semibold rounded ${
                          st.attendance === att
                            ? att === 'present' ? 'bg-emerald-600 text-white' :
                              att === 'absent' ? 'bg-red-600 text-white' :
                              att === 'late' ? 'bg-amber-500 text-white' : 'bg-blue-600 text-white'
                            : 'bg-surface-100 text-surface-600 hover:bg-surface-200'
                        }`}
                      >
                        {att === 'present' ? 'Б' : att === 'absent' ? 'Н' : att === 'late' ? 'О' : 'У'}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-1.5 self-end sm:self-center">
                {[5, 4, 3, 2].map((g) => (
                  <button
                    key={g}
                    onClick={() => handleGrade(st.id, g)}
                    className={`w-8 h-8 rounded-lg font-bold text-sm transition-all ${
                      st.grade === g
                        ? 'bg-primary-600 text-white shadow-md scale-105'
                        : 'bg-surface-100 text-surface-800 hover:bg-surface-200 border border-surface-300'
                    }`}
                  >
                    {g}
                  </button>
                ))}
                {st.grade !== null && (
                  <span className="ml-1 text-xs font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">
                    {st.grade}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
