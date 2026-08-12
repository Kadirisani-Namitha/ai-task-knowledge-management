import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { authApi } from '../api/auth';
import { useAuth } from '../context/AuthContext';
import Spinner from '../components/Spinner';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate  = useNavigate();
  const location  = useLocation();
  const from      = location.state?.from?.pathname ?? '/dashboard';

  const [form, setForm]       = useState({ username: '', password: '' });
  const [error, setError]     = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) =>
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await authApi.login(form.username, form.password);
      login(res.data.access_token);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card" role="main">
        <div className="login-header">
          <div className="login-logo" aria-hidden="true">⚡</div>
          <h1 className="login-title">Welcome back</h1>
          <p className="login-subtitle">Sign in to your TaskFlow AI account</p>
        </div>

        <form className="login-form" onSubmit={handleSubmit} noValidate>
          {error && <div className="login-error" role="alert">{error}</div>}

          <div className="form-group">
            <label className="form-label" htmlFor="username">Username</label>
            <input
              id="username"
              name="username"
              type="text"
              className="form-input"
              placeholder="Enter your username"
              value={form.username}
              onChange={handleChange}
              required
              autoComplete="username"
              autoFocus
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              className="form-input"
              placeholder="Enter your password"
              value={form.password}
              onChange={handleChange}
              required
              autoComplete="current-password"
            />
          </div>

          <button
            type="submit"
            id="login-submit-btn"
            className="btn btn-primary login-submit"
            disabled={loading || !form.username || !form.password}
          >
            {loading ? <><Spinner /> Signing in…</> : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  );
}
