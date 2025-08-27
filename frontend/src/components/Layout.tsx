import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import ChatBot from './ChatBot';
import './Layout.css';

interface NavItem {
  icon: React.ReactNode;
  name: string;
  path: string;
}

const Layout = () => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      logout();
    }
  };

  const navItems: NavItem[] = [
    { 
      icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 9L12 2L21 9V20C21 20.5304 20.7893 21.0391 20.4142 21.4142C20.0391 21.7893 19.5304 22 19 22H5C4.46957 22 3.96086 21.7893 3.58579 21.4142C3.21071 21.0391 3 20.5304 3 20V9Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M9 22V12H15V22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>, 
      name: 'Dashboard', 
      path: '/' 
    },
    { 
      icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M22 12H2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M5 5H19C20.1046 5 21 5.89543 21 7V17C21 18.1046 20.1046 19 19 19H5C3.89543 19 3 18.1046 3 17V7C3 5.89543 3.89543 5 5 5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M12 5V19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>, 
      name: 'Workflows', 
      path: '/workflows' 
    },
    { 
      icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M8 14C8 14 9.5 16 12 16C14.5 16 16 14 16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M9 9H9.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M15 9H15.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>, 
      name: 'Agents', 
      path: '/agents' 
    },
    { 
      icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M16 13H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M16 17H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M10 9H9H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>, 
      name: 'Reports', 
      path: '/reports' 
    },
    { 
      icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M18 20V10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M12 20V4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M6 20V14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>, 
      name: 'Statistics', 
      path: '/statistics' 
    },
    { 
      icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 9L12 2L21 9V20C21 20.5304 20.7893 21.0391 20.4142 21.4142C20.0391 21.7893 19.5304 22 19 22H5C4.46957 22 3.96086 21.7893 3.58579 21.4142C3.21071 21.0391 3 20.5304 3 20V9Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M7 13H17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M10 15H14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>, 
      name: 'Marketplace', 
      path: '/marketplace' 
    },
    { 
      icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M16 7C16 9.20914 14.2091 11 12 11C9.79086 11 8 9.20914 8 7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M12 14C16.4183 14 20 15.7909 20 18V21H4V18C4 15.7909 7.58172 14 12 14Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>, 
      name: 'Farmer Profiles', 
      path: '/farmer-profiles' 
    },
    { 
      icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>, 
      name: 'Business Intelligence', 
      path: '/business-intelligence' 
    },
    { 
      icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>, 
      name: 'Query', 
      path: '/demo' 
    },
  ];

  return (
    <div className="dashboard">
      {/* ChatBot positioned at the end for proper layering */}
      <nav className="sidebar">
        <div className="logo-container">
          <div className="sidebar-logo">
            {/* Updated professional AgriMitr logo: leaf + circuit motif */}
            <svg width="40" height="40" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="agLeaf" x1="8" y1="8" x2="56" y2="56" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#FFD60A"/>
                  <stop offset="1" stopColor="#F5B400"/>
                </linearGradient>
              </defs>
              <circle cx="32" cy="32" r="30" fill="rgba(255,214,10,0.08)" stroke="#FFD60A" strokeWidth="2" />
              <path d="M32 10C24 18 20 26 20 34C20 44 26 52 32 54C38 52 44 44 44 34C44 26 40 18 32 10Z" fill="url(#agLeaf)" stroke="#0F172A" strokeWidth="1.5" strokeLinejoin="round"/>
              <path d="M32 18V46" stroke="#0F172A" strokeWidth="2" strokeLinecap="round"/>
              <path d="M26 28H32M32 38H38" stroke="#0F172A" strokeWidth="2" strokeLinecap="round"/>
              <circle cx="32" cy="28" r="3" fill="#0F172A"/>
              <circle cx="32" cy="38" r="3" fill="#0F172A"/>
            </svg>
          </div>
          <div className="user-info">
            <h3>AgriMitr</h3>
            <p>Smart Agriculture Platform</p>
          </div>
        </div>
        
        <div className="nav-items">
          {navItems.map((item) => (
            <NavLink 
              key={item.path}
              to={item.path}
              className={({ isActive }) => 
                `nav-item ${isActive ? 'active' : ''}`
              }
              end={item.path === '/'}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-name">{item.name}</span>
            </NavLink>
          ))}
        </div>
        
        <div className="system-stats">
          <div className="stats-header">
            <h4>System Overview</h4>
            <div className="stats-indicator">
              <div className="indicator-dot"></div>
              <span>Live</span>
            </div>
          </div>
          {/* Stat Cards - updated icons (outlined, professional) */}
          <div className="stat-item">
            <span className="stat-icon" aria-hidden="true">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFD60A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="5" ry="5" strokeOpacity="0.9" />
                <path d="M12 7.5L13.05 10.45L16 11.5L13.05 12.55L12 15.5L10.95 12.55L8 11.5L10.95 10.45L12 7.5Z" />
              </svg>
            </span>
            <span className="stat-label">Active Workflows:</span>
            <span className="stat-value" style={{color:'#FFC400'}}>3</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon" aria-hidden="true">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFD60A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="5" ry="5" strokeOpacity="0.9" />
                <path d="M8 12l3 3 5-6" />
              </svg>
            </span>
            <span className="stat-label">Total Workflows:</span>
            <span className="stat-value" style={{color:'#FFC400'}}>7</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon" aria-hidden="true">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFD60A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="5" ry="5" strokeOpacity="0.9" />
                <path d="M12 11c1.657 0 3-1.567 3-3.5S13.657 4 12 4 9 5.567 9 7.5 10.343 11 12 11z" />
                <path d="M6.5 18c1.3-2 3.3-3 5.5-3s4.2 1 5.5 3" />
              </svg>
            </span>
            <span className="stat-label">Connected Clients:</span>
            <span className="stat-value" style={{color:'#FFC400'}}>1</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon" aria-hidden="true">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFD60A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="5" ry="5" strokeOpacity="0.9" />
                <rect x="9" y="8" width="6" height="4" rx="1" />
                <path d="M8 15h8" />
              </svg>
            </span>
            <span className="stat-label">Active Agents:</span>
            <span className="stat-value" style={{color:'#FFC400'}}>6</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon" aria-hidden="true">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFD60A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="5" ry="5" strokeOpacity="0.9" />
                <path d="M12 4l-2 7h4l-2 7" />
              </svg>
            </span>
            <span className="stat-label multi-line">System Status:</span>
            <span className="stat-value ready" style={{color:'#32D68A'}}>Ready</span>
          </div>
        </div>
        
        <div className="connected-users">
          <h4>Online Users</h4>
          <div className="user-avatars">
            <div className="user-avatar">AK</div>
            <div className="user-avatar">JD</div>
            <div className="user-avatar">RB</div>
            <div className="user-avatar">+2</div>
          </div>
        </div>

        <div className="sidebar-footer">
          <div className="user-profile">
            <div className="user-avatar-large">{user?.username?.charAt(0).toUpperCase()}</div>
            <div className="user-details">
              <p className="username">{user?.username}</p>
              <p className="user-role">{user?.role}</p>
            </div>
          </div>
          <button 
            onClick={handleLogout}
            className="logout-button"
            title="Logout"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <polyline points="16,17 21,12 16,7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <line x1="21" y1="12" x2="9" y2="12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>
      </nav>

      <div className="main-content">
        <Outlet />
      </div>
      
      {/* ChatBot added at the end to ensure proper stacking order */}
      <ChatBot />
    </div>
  );
};

export default Layout;
