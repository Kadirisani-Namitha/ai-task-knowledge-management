import { useEffect, useState } from 'react';
import { usersApi } from '../api/users';
import { useToast } from '../components/Toast';
import { useAuth } from '../context/AuthContext';
import StatusBadge from '../components/StatusBadge';
import Modal from '../components/Modal';
import Spinner from '../components/Spinner';

const EMPTY_FORM = { username: '', email: '', password: '', role: 'user' };

export default function UsersPage() {
  const { user: currentUser } = useAuth();
  const toast = useToast();

  const [users,      setUsers]      = useState([]);
  const [loading,    setLoading]    = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form,       setForm]       = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);

  const fetchUsers = () => {
    setLoading(true);
    usersApi.list()
      .then(r => setUsers(r.data))
      .catch(() => toast('Failed to load users', 'error'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchUsers(); }, []); // eslint-disable-line

  const handleChange = (e) =>
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));

  const ROLE_ID = { admin: 1, user: 2 };

  const handleCreate = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      // Backend UserCreate expects role_id (int), not role (string)
      const payload = {
        username: form.username,
        email: form.email,
        password: form.password,
        role_id: ROLE_ID[form.role] ?? 2,
      };
      await usersApi.create(payload);
      toast(`User "${form.username}" created!`, 'success');
      setShowCreate(false);
      setForm(EMPTY_FORM);
      fetchUsers();
    } catch (err) {
      toast(err.response?.data?.detail ?? 'Failed to create user', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <div>
          <h1 className="page-title">Users</h1>
          <p className="page-subtitle">Manage system users and roles</p>
        </div>
        <button id="create-user-btn" className="btn btn-primary" onClick={() => setShowCreate(true)}>
          + New User
        </button>
      </div>

      {loading ? (
        <Spinner large text="Loading users…" />
      ) : users.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">👤</div>
          <h3>No users found</h3>
          <p>Create the first user to get started.</p>
        </div>
      ) : (
        <div className="table-wrapper">
          <table aria-label="Users table">
            <thead>
              <tr>
                <th>#</th>
                <th>Username</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Joined</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id}>
                  <td style={{ color: 'var(--text-muted)', width: 40 }}>{u.id}</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
                      <div style={{
                        width: 28, height: 28,
                        borderRadius: '50%',
                        background: 'var(--grad-accent)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: '0.7rem', fontWeight: 700, color: 'white', flexShrink: 0,
                      }}>
                        {u.username.slice(0, 2).toUpperCase()}
                      </div>
                      <div>
                        <div style={{ fontWeight: 500 }}>
                          {u.username}
                          {u.id === currentUser?.id && (
                            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginLeft: '0.375rem' }}>(you)</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td style={{ color: 'var(--text-secondary)' }}>{u.email ?? '—'}</td>
                  <td><StatusBadge value={u.role} type="role" /></td>
                  <td>
                    <span className={`badge ${u.is_active ? 'badge-done' : 'badge-cancelled'}`}>
                      {u.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.8125rem' }}>
                    {u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create User Modal */}
      {showCreate && (
        <Modal
          title="Create New User"
          onClose={() => { setShowCreate(false); setForm(EMPTY_FORM); }}
          footer={
            <>
              <button className="btn btn-secondary" onClick={() => { setShowCreate(false); setForm(EMPTY_FORM); }}>
                Cancel
              </button>
              <button
                className="btn btn-primary"
                form="create-user-form"
                type="submit"
                disabled={submitting}
              >
                {submitting ? <><Spinner /> Creating…</> : 'Create User'}
              </button>
            </>
          }
        >
          <form id="create-user-form" onSubmit={handleCreate}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label" htmlFor="new-username">Username *</label>
                <input
                  id="new-username"
                  name="username"
                  type="text"
                  className="form-input"
                  value={form.username}
                  onChange={handleChange}
                  required
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="new-email">Email</label>
                <input
                  id="new-email"
                  name="email"
                  type="email"
                  className="form-input"
                  placeholder="user@example.com"
                  value={form.email}
                  onChange={handleChange}
                />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="new-password">Password *</label>
                <input
                  id="new-password"
                  name="password"
                  type="password"
                  className="form-input"
                  value={form.password}
                  onChange={handleChange}
                  required
                  minLength={8}
                />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="new-role">Role</label>
                <select
                  id="new-role"
                  name="role"
                  className="form-select"
                  value={form.role}
                  onChange={handleChange}
                >
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
