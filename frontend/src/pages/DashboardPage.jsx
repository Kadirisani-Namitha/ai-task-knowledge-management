import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { tasksApi } from '../api/tasks';
import { documentsApi } from '../api/documents';
import { useAuth } from '../context/AuthContext';
import StatusBadge from '../components/StatusBadge';
import Spinner from '../components/Spinner';

const STATUS_LIST = ['todo', 'in_progress', 'done', 'cancelled'];

const STATUS_ICONS = {
  todo:        '○',
  in_progress: '◑',
  done:        '●',
  cancelled:   '✕',
};

const STAT_COLORS = {
  todo:        { bg: 'rgba(148,163,184,0.15)', color: '#94a3b8' },
  in_progress: { bg: 'var(--info-dim)',        color: 'var(--info)'    },
  done:        { bg: 'var(--success-dim)',      color: 'var(--success)' },
  cancelled:   { bg: 'var(--danger-dim)',       color: 'var(--danger)'  },
};

export default function DashboardPage() {
  const { user, isAdmin } = useAuth();
  const [tasks,   setTasks]   = useState([]);
  const [docs,    setDocs]    = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      tasksApi.list(),
      documentsApi.list(),
    ])
      .then(([tr, dr]) => {
        setTasks(tr.data);
        setDocs(dr.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const counts = STATUS_LIST.reduce((acc, s) => {
    acc[s] = tasks.filter(t => t.status === s).length;
    return acc;
  }, {});

  const recent = [...tasks]
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 5);

  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';

  if (loading) return <Spinner large text="Loading dashboard…" />;

  return (
    <div className="page-wrapper">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">{greeting}, {user?.username} 👋</h1>
          <p className="page-subtitle">
            {isAdmin ? 'Admin view — all tasks visible' : 'Your personal workspace'}
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        {STATUS_LIST.map(s => {
          const { bg, color } = STAT_COLORS[s];
          return (
            <div key={s} className="stat-card">
              <div className="stat-icon" style={{ background: bg, color }}>
                {STATUS_ICONS[s]}
              </div>
              <div className="stat-value" style={{ color }}>{counts[s]}</div>
              <div className="stat-label">
                {s === 'in_progress' ? 'In Progress' : s.charAt(0).toUpperCase() + s.slice(1)}
              </div>
            </div>
          );
        })}
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--accent-dim)', color: 'var(--accent-light)' }}>
            ⊞
          </div>
          <div className="stat-value" style={{ color: 'var(--accent-light)' }}>{docs.length}</div>
          <div className="stat-label">Documents</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--success-dim)', color: 'var(--success)' }}>
            ✓
          </div>
          <div className="stat-value" style={{ color: 'var(--success)' }}>
            {tasks.length ? Math.round((counts.done / tasks.length) * 100) : 0}%
          </div>
          <div className="stat-label">Completion Rate</div>
        </div>
      </div>

      {/* Recent Tasks */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, margin: 0 }}>Recent Tasks</h2>
          <Link to="/tasks" className="btn btn-ghost btn-sm">View all →</Link>
        </div>
        {recent.length === 0 ? (
          <div className="empty-state" style={{ padding: '2rem' }}>
            <div className="empty-state-icon">📋</div>
            <h3>No tasks yet</h3>
            <p>Tasks will appear here once created.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {recent.map(task => (
              <div key={task.id} style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.75rem 1rem',
                background: 'var(--bg-elevated)',
                borderRadius: 'var(--radius-md)',
                gap: '1rem',
                flexWrap: 'wrap',
              }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 500, fontSize: '0.9rem', marginBottom: '0.2rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {task.title}
                  </div>
                  {task.description && (
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {task.description}
                    </div>
                  )}
                </div>
                <StatusBadge value={task.status} />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick Links */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem' }}>
        {[
          { to: '/tasks',     icon: '✓', label: 'Manage Tasks',       desc: 'Create & track tasks'    },
          { to: '/documents', icon: '⊞', label: 'Knowledge Base',     desc: 'Browse documents'        },
          { to: '/search',    icon: '⌕', label: 'Semantic Search',    desc: 'AI-powered search'       },
          ...(isAdmin ? [{ to: '/analytics', icon: '◈', label: 'Analytics', desc: 'System insights' }] : []),
        ].map(({ to, icon, label, desc }) => (
          <Link key={to} to={to} style={{ textDecoration: 'none' }}>
            <div className="card" style={{ cursor: 'pointer', display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
              <div style={{
                width: 38, height: 38, borderRadius: 'var(--radius-md)',
                background: 'var(--accent-dim)', color: 'var(--accent-light)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '1.1rem', flexShrink: 0,
              }}>
                {icon}
              </div>
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-primary)' }}>{label}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{desc}</div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
