import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { RunCreatePage } from './pages/RunCreatePage';
import { RunDetailPage } from './pages/RunDetailPage';
import { DashboardPage } from './pages/DashboardPage';
import { ApprovalsPage } from './pages/ApprovalsPage';
import { ApprovalDetailPage } from './pages/ApprovalDetailPage';
import { RcaPage } from './pages/RcaPage';
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
              <LanguageSwitcher />
            </div>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-4 py-6">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/runs/new" element={<RunCreatePage />} />
            <Route path="/runs/:id" element={<RunDetailPage />} />
            <Route path="/runs/:id/rca" element={<RcaPage />} />
            <Route path="/approvals" element={<ApprovalsPage />} />
            <Route path="/approvals/:id" element={<ApprovalDetailPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
