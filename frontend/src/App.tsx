import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Sparkles, LogOut, Menu, X, RefreshCw } from 'lucide-react';
import LoginPage from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { TemplateGalleryPage } from './pages/TemplateGalleryPage';
import { CreateProjectPage } from './pages/CreateProjectPage';
import { ProjectDetailPage } from './pages/ProjectDetailPage';
import { RenewalPage } from './pages/RenewalPage';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = React.useState(false);
  const location = useLocation();

  // 로그인 페이지에서는 레이아웃 미표시
  if (location.pathname === '/login' || location.pathname === '/signup') {
    return <>{children}</>;
  }

  const navItems = [
    { path: '/dashboard', label: '대시보드', icon: LayoutDashboard },
    { path: '/templates', label: '템플릿', icon: Sparkles },
    { path: '/renewal', label: '페이지 리뉴얼', icon: RefreshCw },
  ];

  return (
    <div className="flex h-screen bg-background">
      {/* 사이드바 */}
      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-50 w-64 bg-card border-r border-white/10
          transform transition-transform duration-300 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        <div className="flex flex-col h-full">
          {/* 로고 */}
          <div className="flex items-center justify-between p-6 border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center text-2xl">
                🚀
              </div>
              <div>
                <h1 className="font-bold text-lg">Wadiz Builder</h1>
                <p className="text-xs text-muted-foreground">v4.2 Pro</p>
              </div>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-2 hover:bg-secondary rounded-lg"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* 네비게이션 */}
          <nav className="flex-1 p-4 space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setSidebarOpen(false)}
                  className={`
                    flex items-center gap-3 px-4 py-3 rounded-lg transition-all
                    ${isActive
                      ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/50'
                      : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                    }
                  `}
                >
                  <Icon className="h-5 w-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* 사용자 정보 */}
          <div className="p-4 border-t border-white/10">
            <div className="flex items-center gap-3 p-3 rounded-lg bg-secondary">
              <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-bold">
                U
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-medium truncate">사용자</div>
                <div className="text-xs text-muted-foreground truncate">user@example.com</div>
              </div>
              <button className="p-2 hover:bg-background rounded-lg transition-colors">
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* 모바일 오버레이 */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* 메인 컨텐츠 */}
      <main className="flex-1 overflow-auto">
        {/* 모바일 헤더 */}
        <div className="lg:hidden sticky top-0 z-30 bg-card border-b border-white/10 px-6 py-4 flex items-center justify-between">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 hover:bg-secondary rounded-lg"
          >
            <Menu className="h-6 w-6" />
          </button>
          <div className="flex items-center gap-2">
            <div className="text-2xl">🚀</div>
            <span className="font-bold">Wadiz Builder</span>
          </div>
          <div className="w-10" /> {/* Spacer for center alignment */}
        </div>

        {children}
      </main>
    </div>
  );
};

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/templates" element={<TemplateGalleryPage />} />
          <Route path="/create" element={<CreateProjectPage />} />
          <Route path="/project/:id" element={<ProjectDetailPage />} />
          <Route path="/renewal" element={<RenewalPage />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
