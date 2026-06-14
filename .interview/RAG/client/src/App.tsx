import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ChatPage from './pages/Chat/ChatPage';
import AdminPage from './pages/Admin/AdminPage';
import AdminLoginPage from './pages/Admin/AdminLoginPage';
import AuthCallbackPage from './pages/Auth/AuthCallbackPage';
import LocalLoginPage from './pages/Auth/LocalLoginPage';
import KnowledgePage from './pages/Knowledge/KnowledgePage';
import KbAnalyticsPage from './pages/Knowledge/KbAnalyticsPage';
import './index.css';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ChatPage />} />
        <Route path="/login" element={<LocalLoginPage />} />
        <Route path="/auth/callback" element={<AuthCallbackPage />} />
        <Route path="/admin/login" element={<AdminLoginPage />} />
        <Route path="/admin" element={<AdminPage />} />
        <Route path="/knowledge" element={<KnowledgePage />} />
        <Route path="/knowledge/analytics" element={<KbAnalyticsPage />} />
      </Routes>
    </BrowserRouter>
  );
}
