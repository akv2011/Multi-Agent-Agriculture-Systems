import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import ChatBot from './ChatBot';
import './Layout.css';

interface NavItem {
  icon: React.ReactNode;
  name: string;
  path: string;
}

const Layout = () => {

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
          <img src="/logo.png" alt="AgriSens Logo" className="sidebar-logo" />
          <div className="user-info">
            <h3>AgriSens</h3>
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
              onClick={() => {
                // Direct navigation using window.location to ensure it works
                // This is a fallback solution if React Router isn't handling links properly
                console.log(`Navigating to: ${item.path}`);
                window.location.href = item.path;
              }}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-name">{item.name}</span>
            </NavLink>
          ))}
        </div>
        
        <div className="system-stats">
          <div className="stat-item">
            <span className="stat-icon">🔄</span>
            <span className="stat-label">Active Workflows:</span>
            <span className="stat-value" style={{color: '#FFD700', fontWeight: '700', fontSize: '1.9rem', textShadow: '0 0 2px rgba(255,215,0,0.8)'}}>3</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">📊</span>
            <span className="stat-label">Total Workflows:</span>
            <span className="stat-value" style={{color: '#FFD700', fontWeight: '700', fontSize: '1.9rem', textShadow: '0 0 2px rgba(255,215,0,0.8)'}}>7</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">🔌</span>
            <span className="stat-label">Connected Clients:</span>
            <span className="stat-value" style={{color: '#FFD700', fontWeight: '700', fontSize: '1.9rem', textShadow: '0 0 2px rgba(255,215,0,0.8)'}}>1</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">🤖</span>
            <span className="stat-label">Active Agents:</span>
            <span className="stat-value" style={{color: '#FFD700', fontWeight: '700', fontSize: '1.9rem', textShadow: '0 0 2px rgba(255,215,0,0.8)'}}>5</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">⚡</span>
            <span className="stat-label">System Status:</span>
            <span className="stat-value connected" style={{color: '#00FF7F', fontWeight: '700', fontSize: '1.9rem', textShadow: '0 0 2px rgba(0,255,127,0.8)'}}>Ready</span>
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
