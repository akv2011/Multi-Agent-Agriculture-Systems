import React from 'react';
import { isDemoMode, getDemoCredentials } from '../utils/authUtils';

const AuthDebug: React.FC = () => {
  const demoMode = isDemoMode();
  const credentials = getDemoCredentials();

  // Also console.log the debug info
  console.log('AuthDebug: Demo mode:', demoMode);
  console.log('AuthDebug: Credentials:', credentials);
  console.log('AuthDebug: Environment variables:', {
    VITE_DEMO_MODE: import.meta.env.VITE_DEMO_MODE,
    VITE_DEMO_ADMIN_HASH: import.meta.env.VITE_DEMO_ADMIN_HASH ? 'Present' : 'Missing',
    VITE_DEMO_USER_HASH: import.meta.env.VITE_DEMO_USER_HASH ? 'Present' : 'Missing',
    VITE_DEMO_FARMER_HASH: import.meta.env.VITE_DEMO_FARMER_HASH ? 'Present' : 'Missing',
    VITE_DEMO_AGRISENS_HASH: import.meta.env.VITE_DEMO_AGRISENS_HASH ? 'Present' : 'Missing',
  });

  return (
    <div style={{ 
      position: 'fixed', 
      top: '10px', 
      right: '10px', 
      background: '#ffeb3b', 
      padding: '15px', 
      border: '2px solid #f57f17',
      borderRadius: '8px',
      fontSize: '14px',
      zIndex: 9999,
      minWidth: '300px',
      fontFamily: 'monospace'
    }}>
      <h4 style={{ margin: '0 0 10px 0', color: '#f57f17' }}>🔍 Auth Debug Info</h4>
      <p><strong>Demo Mode:</strong> {demoMode ? '✅ ON' : '❌ OFF'}</p>
      <p><strong>VITE_DEMO_MODE:</strong> "{import.meta.env.VITE_DEMO_MODE}"</p>
      <p><strong>Credentials loaded:</strong> {Object.keys(credentials).length}</p>
      <p><strong>Available users:</strong> {Object.keys(credentials).join(', ') || 'None'}</p>
      <div style={{ marginTop: '10px', padding: '10px', background: '#fff3e0', borderRadius: '4px' }}>
        <p style={{ margin: '0', fontSize: '12px' }}>
          <strong>Demo Login Instructions:</strong><br/>
          {demoMode ? (
            <>
              Use the credentials configured in your environment variables.<br/>
              Check your .env file or deployment configuration for valid demo credentials.
            </>
          ) : (
            <>
              Demo mode is disabled. Enable by setting VITE_DEMO_MODE=true in your environment.
            </>
          )}
        </p>
      </div>
    </div>
  );
};

export default AuthDebug;
