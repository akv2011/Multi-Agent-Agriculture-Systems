import React, { createContext, useState, useEffect } from 'react';
import type { User, AuthContextType } from '../types/auth';

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Mock credentials with roles
  const mockCredentials = {
    admin: { password: 'admin123', role: 'Administrator' },
    user: { password: 'user123', role: 'User' },
    farmer: { password: 'farmer123', role: 'Farmer' },
    agrisens: { password: 'agrisens2025', role: 'AgriSens Expert' }
  };

  useEffect(() => {
    // Check if user is already logged in (from localStorage)
    const savedUser = localStorage.getItem('agrisens_user');
    if (savedUser) {
      try {
        const parsedUser = JSON.parse(savedUser);
        setUser(parsedUser);
      } catch {
        localStorage.removeItem('agrisens_user');
      }
    }
    setIsLoading(false);
  }, []);

  const login = (username: string, password: string): boolean => {
    const credentials = mockCredentials[username as keyof typeof mockCredentials];
    
    if (credentials && credentials.password === password) {
      const newUser: User = {
        username,
        role: credentials.role,
        loginTime: new Date().toISOString()
      };
      
      setUser(newUser);
      localStorage.setItem('agrisens_user', JSON.stringify(newUser));
      return true;
    }
    
    return false;
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('agrisens_user');
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
