import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { useState } from 'react';
import { RunCreatePage } from './pages/RunCreatePage';
import { RunDetailPage } from './pages/RunDetailPage';
import { DashboardPage } from './pages/DashboardPage';
import { ApprovalsPage } from './pages/ApprovalsPage';
import { ApprovalDetailPage } from './pages/ApprovalDetailPage';
import { RcaPage } from './pages/RcaPage';
import { LlmConfigModal } from './components/LlmConfigModal';
import { useI18n } from './i18n';

function LanguageSwitcher() {
  const { locale, setLocale } = useI18n();
  
  return (
    <div className="flex items-center gap-1">
      <button
        onClick={() => setLocale('en')}
        className={`px-3 py-1.5 text-sm rounded font-medium transition-fast cursor-pointer ${
          locale === 'en' 
            ? 'bg-[var(--accent-primary)] text-white !important' 
            : 'bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:bg-[var(--border-default)]'
        }`}
      >
        EN
      </button>
      <button
        onClick={() => setLocale('zh-CN')}
        className={`px-3 py-1.5 text-sm rounded font-medium transition-fast cursor-pointer ${
          locale === 'zh-CN' 
            ? 'bg-[var(--accent-primary)] text-white !important' 
            : 'bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:bg-[var(--border-default)]'
        }`}
      >
        中文
      </button>
    </div>
  );
}

function Navigation() {
  const { t } = useI18n();
  
  const navItems = [
    { path: '/', label: t('nav.dashboard'), icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
    { path: '/runs/new', label: t('nav.newIncident'), icon: 'M12 4v16m8-8H4' },
    { path: '/approvals', label: t('nav.approvals'), icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
  ];

  return (
    <nav className="flex items-center gap-2">
      {navItems.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          end={item.path === '/'}
          className={({ isActive }) =>
            `relative flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-all duration-150 cursor-pointer ${
              isActive
                ? 'bg-[var(--accent-primary)] shadow-sm'
                : 'text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)] hover:text-[var(--text-primary)]'
            }`
          }
        >
          {({ isActive }) => (
            <>
              <svg
                className={`w-4 h-4 transition-transform duration-150 ${isActive ? 'scale-110 text-white' : ''}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d={item.icon} />
              </svg>
              <span className={`${isActive ? 'text-white font-semibold' : ''}`}>{item.label}</span>
            </>
          )}
        </NavLink>
      ))}
    </nav>
  );
}

function App() {
  const [showLlmConfig, setShowLlmConfig] = useState(false);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[var(--bg-secondary)]">
        <header className="border-b border-[var(--border-subtle)] bg-[var(--bg-card)]">
          <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
            <h1 className="text-lg font-semibold tracking-tight font-heading text-[var(--text-primary)]">
              <span className="text-[var(--text-primary)]">Ops</span>
              <span className="text-[var(--text-muted)]">Pilot</span>
            </h1>
            <div className="flex items-center gap-4">
              <Navigation />
              <button
                onClick={() => setShowLlmConfig(true)}
                className="w-9 h-9 flex items-center justify-center rounded-md transition-fast cursor-pointer"
                style={{ color: 'var(--text-secondary)' }}
                title="LLM 配置"
                onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'var(--bg-tertiary)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'transparent'; }}
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
              <LanguageSwitcher />
            </div>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-4 py-6">
          <Routes>
            <Route path="/" element={<DashboardPage onOpenLlmConfig={() => setShowLlmConfig(true)} />} />
            <Route path="/runs/new" element={<RunCreatePage />} />
            <Route path="/runs/:id" element={<RunDetailPage />} />
            <Route path="/runs/:id/rca" element={<RcaPage />} />
            <Route path="/approvals" element={<ApprovalsPage />} />
            <Route path="/approvals/:id" element={<ApprovalDetailPage />} />
          </Routes>
        </main>

        <LlmConfigModal open={showLlmConfig} onClose={() => setShowLlmConfig(false)} />
      </div>
    </BrowserRouter>
  );
}

export default App;
