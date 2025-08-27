import React, { createContext, useState, useEffect } from 'react';
import type { User, AuthContextType } from '../types/auth';
import { validateDemoCredentials, isDemoMode } from '../utils/authUtils';

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in (from localStorage)
<<<<<<< HEAD
    const savedUser = localStorage.getItem('AgriMitr_user');
=======
    const savedUser = localStorage.getItem('agrisens_user');
>>>>>>> upstream/main
    if (savedUser) {
      try {
        const parsedUser = JSON.parse(savedUser);
        setUser(parsedUser);
      } catch {
<<<<<<< HEAD
        localStorage.removeItem('AgriMitr_user');
=======
        localStorage.removeItem('agrisens_user');
>>>>>>> upstream/main
      }
    }
    setIsLoading(false);
  }, []);

  const login = (username: string, password: string): boolean => {
    // In demo mode, use environment-based credentials
    if (isDemoMode()) {
      const userRole = validateDemoCredentials(username, password);
      
      if (userRole) {
        const newUser: User = {
          username,
          role: userRole,
          loginTime: new Date().toISOString()
        };
        
        setUser(newUser);
<<<<<<< HEAD
        localStorage.setItem('AgriMitr_user', JSON.stringify(newUser));
=======
        localStorage.setItem('agrisens_user', JSON.stringify(newUser));
>>>>>>> upstream/main
        return true;
      }
    } else {
      // In production mode, this should make an API call to your backend
      // For now, reject all logins when not in demo mode
      console.warn('Authentication attempted in non-demo mode. Backend authentication not implemented.');
    }
    
    return false;
  };

  const logout = () => {
    setUser(null);
<<<<<<< HEAD
    localStorage.removeItem('AgriMitr_user');
=======
    localStorage.removeItem('agrisens_user');
>>>>>>> upstream/main
  };

  const value = {
    user,
    isAuthenticated: !!user,
    login,
    logout,
    isLoading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
