import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const NAV_ITEMS = [
  { to: '/dashboard', icon: '⬡', label: 'Dashboard' },
  { to: '/tasks',     icon: '✓', label: 'Tasks'     },
  { to: '/documents', icon: '⊞', label: 'Documents' },
  { to: '/search',    icon: '⌕', label: 'Search'    },
];

const ADMIN_ITEMS = [
  { to: '/analytics', icon: '◈', label: 'Analytics' },
  { to: '/users',     icon: '◎', label: 'Users'     },
];

export default function Sidebar() {
  const { user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  const initials = user?.username
    ? user.username.slice(0, 2).toUpperCase()
    : '?';

  return (
    <aside className="sidebar" aria-label="Primary navigation">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon" aria-hidden="true">⚡</div>
        <div className="sidebar-logo-text">
          TaskFlow AI
          <span>Knowledge Manager</span>
        </div>
      </div>

      {/* Main nav */}
      <nav className="sidebar-nav" aria-label="Main navigation">
        <span className="nav-section-label">General</span>
        {NAV_ITEMS.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
            aria-current={({ isActive }) => isActive ? 'page' : undefined}
          >
            <span className="nav-icon" aria-hidden="true">{icon}</span>
            {label}
          </NavLink>
        ))}

        {isAdmin && (
          <>
            <span className="nav-section-label">Admin</span>
            {ADMIN_ITEMS.map(({ to, icon, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
              >
                <span className="nav-icon" aria-hidden="true">{icon}</span>
                {label}
              </NavLink>
            ))}
          </>
        )}
      </nav>

      {/* User footer */}
      <div className="sidebar-footer">
        <div className="user-chip" role="group" aria-label="User profile">
          <div className="user-avatar" aria-hidden="true">{initials}</div>
          <div className="user-chip-info">
            <div className="user-chip-name">{user?.username ?? '—'}</div>
            <div className="user-chip-role">{user?.role ?? ''}</div>
          </div>
          <button
            className="logout-btn"
            onClick={handleLogout}
            aria-label="Log out"
            title="Log out"
          >
            ⏻
          </button>
        </div>
      </div>
    </aside>
  );
}
