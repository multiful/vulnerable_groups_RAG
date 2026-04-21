import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Home, ShieldAlert, Award, Map, Calendar, Settings, Bell } from 'lucide-react';

const MainLayout: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { icon: <Home size={20} />, label: '홈', path: '/' },
    { icon: <ShieldAlert size={20} />, label: '위험군 진단', path: '/risk-assessment' },
    { icon: <Award size={20} />, label: '자격증 추천', path: '/recommendation' },
    { icon: <Map size={20} />, label: '성장 로드맵', path: '/roadmap' },
  ];

  return (
    <div className="layout-root">
      <header className="header glass-card">
        <div className="container header-content">
          <Link to="/" className="logo">
            <span className="gradient-text">VulnerableRAG</span>
          </Link>
          <div className="header-actions">
            <button className="icon-btn"><Bell size={20} /></button>
            <div className="user-profile">
              <div className="avatar">JD</div>
            </div>
          </div>
        </div>
      </header>

      <div className="main-container container">
        <aside className="sidebar">
          <nav className="nav">
            {navItems.map((item) => (
              <Link 
                key={item.path} 
                to={item.path} 
                className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
              >
                {item.icon}
                <span>{item.label}</span>
              </Link>
            ))}
          </nav>
        </aside>

        <main className="content-area">
          <Outlet />
        </main>
      </div>

      <style>{`
        .layout-root {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
          padding-bottom: 2rem;
        }
        .header {
          position: sticky;
          top: 0.5rem;
          margin: 0.5rem 1rem;
          z-index: 100;
          height: 4rem;
          display: flex;
          align-items: center;
          border-radius: 1rem;
        }
        .header-content {
          display: flex;
          justify-content: space-between;
          align-items: center;
          width: 100%;
        }
        .logo {
          font-size: 1.5rem;
          letter-spacing: -0.025em;
        }
        .header-actions {
          display: flex;
          align-items: center;
          gap: 1rem;
        }
        .icon-btn {
          color: var(--text-muted);
          transition: var(--transition);
        }
        .icon-btn:hover {
          color: var(--text);
        }
        .user-profile {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        .avatar {
          width: 2.5rem;
          height: 2.5rem;
          background: var(--primary);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          font-size: 0.875rem;
        }
        .main-container {
          display: grid;
          grid-template-columns: 240px 1fr;
          gap: 2rem;
        }
        .sidebar {
          position: sticky;
          top: 6rem;
          height: calc(100vh - 8rem);
        }
        .nav {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }
        .nav-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem 1rem;
          border-radius: 0.75rem;
          color: var(--text-muted);
          transition: var(--transition);
        }
        .nav-item:hover {
          background: var(--surface);
          color: var(--text);
        }
        .nav-item.active {
          background: var(--surface);
          color: var(--primary);
          font-weight: 600;
        }
        @media (max-width: 768px) {
          .main-container {
            grid-template-columns: 1fr;
          }
          .sidebar {
            display: none;
          }
        }
      `}</style>
    </div>
  );
};

export default MainLayout;
