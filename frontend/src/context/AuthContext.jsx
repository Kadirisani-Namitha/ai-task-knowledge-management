import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { setupResponseInterceptors } from '../api/client';
import { usersApi } from '../api/users';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser]     = useState(null);
  const [token, setToken]   = useState(() => localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  }, []);

  // Install global 401 interceptor once
  useEffect(() => {
    setupResponseInterceptors(logout);
  }, [logout]);

  // On mount (or token change) fetch /users/me to populate user object
  useEffect(() => {
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    usersApi.me()
      .then(res => setUser(res.data))
      .catch(() => logout())
      .finally(() => setLoading(false));
  }, [token, logout]);

  const login = useCallback((accessToken) => {
    localStorage.setItem('token', accessToken);
    setToken(accessToken);
  }, []);

  const isAdmin = user?.role === 'admin';

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, isAdmin }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
