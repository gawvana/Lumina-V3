import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Auth from './pages/Auth';
import AdminDashboard from './pages/admin/Dashboard';
import TeacherToday from './pages/teacher/Today';
import StudentHome from './pages/student/Home';
import ParentDashboard from './pages/parent/Dashboard';

export default function App() {
  return (
    <Routes>
      <Route path="/auth" element={<Auth />} />
      <Route path="/" element={<Layout />}>
        <Route path="admin" element={<AdminDashboard />} />
        <Route path="teacher" element={<TeacherToday />} />
        <Route path="student" element={<StudentHome />} />
        <Route path="parent" element={<ParentDashboard />} />
      </Route>
    </Routes>
  );
}