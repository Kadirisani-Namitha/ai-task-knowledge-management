import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './components/Toast';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage     from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import TasksPage     from './pages/TasksPage';
import DocumentsPage from './pages/DocumentsPage';
import SearchPage    from './pages/SearchPage';
import AnalyticsPage from './pages/AnalyticsPage';
import UsersPage     from './pages/UsersPage';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <Routes>
            {/* Public */}
            <Route path="/login" element={<LoginPage />} />

            {/* Protected — all authenticated users */}
            <Route element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/tasks"     element={<TasksPage />} />
              <Route path="/documents" element={<DocumentsPage />} />
              <Route path="/search"    element={<SearchPage />} />

              {/* Admin-only */}
              <Route path="/analytics" element={
                <ProtectedRoute adminOnly>
                  <AnalyticsPage />
                </ProtectedRoute>
              } />
              <Route path="/users" element={
                <ProtectedRoute adminOnly>
                  <UsersPage />
                </ProtectedRoute>
              } />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
