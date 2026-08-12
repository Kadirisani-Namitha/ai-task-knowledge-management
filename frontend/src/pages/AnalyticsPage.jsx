import { useEffect, useState } from 'react';
import { analyticsApi } from '../api/analytics';
import { useToast } from '../components/Toast';
import Spinner from '../components/Spinner';
import StatusBadge from '../components/StatusBadge';

export default function AnalyticsPage() {
  const toast = useToast();
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsApi.get()
      .then(r => setData(r.data))
      .catch(() => toast('Failed to load analytics', 'error'))
      .finally(() => setLoading(false));
  }, [toast]);

  if (loading) return <Spinner large text="Loading analytics…" />;
  if (!data)   return null;

  const tasksByStatus   = data.tasks_by_status   ?? {};
  const tasksByAssignee = data.tasks_by_assignee  ?? {};
  const recentLogs      = data.recent_activity    ?? [];
  const totalTasks      = data.total_tasks        ?? 0;
  const totalDocs       = data.total_documents    ?? 0;
  const totalUsers      = data.total_users        ?? 0;
  const totalSearches   = data.total_searches     ?? 0;

  const maxStatus   = Math.max(1, ...Object.values(tasksByStatus));
  const maxAssignee = Math.max(1, ...Object.values(tasksByAssignee));

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <div>
          <h1 className="page-title">Analytics</h1>
          <p className="page-subtitle">System-wide insights — admin view</p>
        </div>
      </div>

      {/* KPI cards */}
      <div className="stats-grid" style={{ marginBottom: '2rem' }}>
        {[
          { label: 'Total Tasks',    value: totalTasks,   icon: '✓', color: 'var(--accent-light)', bg: 'var(--accent-dim)'  },
          { label: 'Documents',      value: totalDocs,    icon: '⊞', color: 'var(--info)',         bg: 'var(--info-dim)'    },
          { label: 'Users',          value: totalUsers,   icon: '◎', color: 'var(--success)',      bg: 'var(--success-dim)' },
          { label: 'Search Queries', value: totalSearches,icon: '⌕', color: 'var(--warning)',      bg: 'var(--warning-dim)' },
        ].map(({ label, value, icon, color, bg }) => (
          <div key={label} className="stat-card">
            <div className="stat-icon" style={{ background: bg, color }}>{icon}</div>
            <div className="stat-value" style={{ color }}>{value}</div>
            <div className="stat-label">{label}</div>
          </div>
        ))}
      </div>

      <div className="analytics-grid">
        {/* Tasks by Status */}
        <div className="card">
          <h3 style={{ marginBottom: '1.25rem', fontSize: '0.9375rem', fontWeight: 600 }}>Tasks by Status</h3>
          {Object.keys(tasksByStatus).length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>No data</p>
          ) : (
            <div className="bar-chart">
              {Object.entries(tasksByStatus).map(([status, count]) => (
                <div key={status} className="bar-row">
                  <span className="bar-label">{status === 'in_progress' ? 'In Prog.' : status}</span>
                  <div className="bar-track">
                    <div
                      className="bar-fill"
                      style={{ width: `${(count / maxStatus) * 100}%` }}
                    />
                  </div>
                  <span className="bar-count">{count}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Tasks by Assignee */}
        <div className="card">
          <h3 style={{ marginBottom: '1.25rem', fontSize: '0.9375rem', fontWeight: 600 }}>Top Assignees</h3>
          {Object.keys(tasksByAssignee).length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>No assigned tasks</p>
          ) : (
            <div className="bar-chart">
              {Object.entries(tasksByAssignee)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 8)
                .map(([name, count]) => (
                  <div key={name} className="bar-row">
                    <span className="bar-label">{name}</span>
                    <div className="bar-track">
                      <div
                        className="bar-fill"
                        style={{ width: `${(count / maxAssignee) * 100}%` }}
                      />
                    </div>
                    <span className="bar-count">{count}</span>
                  </div>
                ))}
            </div>
          )}
        </div>

        {/* Recent Activity */}
        <div className="card" style={{ gridColumn: '1 / -1' }}>
          <h3 style={{ marginBottom: '1.25rem', fontSize: '0.9375rem', fontWeight: 600 }}>Recent Activity Log</h3>
          {recentLogs.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>No activity recorded yet.</p>
          ) : (
            <div className="table-wrapper" style={{ border: 'none', borderRadius: 0, background: 'none' }}>
              <table aria-label="Activity log">
                <thead>
                  <tr>
                    <th>User</th>
                    <th>Action</th>
                    <th>Entity</th>
                    <th>Time</th>
                  </tr>
                </thead>
                <tbody>
                  {recentLogs.map((log, i) => (
                    <tr key={i}>
                      <td style={{ fontWeight: 500 }}>{log.username ?? log.user_id}</td>
                      <td>
                        <span style={{
                          fontSize: '0.75rem', padding: '0.2rem 0.5rem',
                          borderRadius: '999px', background: 'var(--bg-elevated)',
                          color: 'var(--text-secondary)', fontFamily: 'monospace',
                        }}>
                          {log.action}
                        </span>
                      </td>
                      <td style={{ color: 'var(--text-secondary)', fontSize: '0.8125rem' }}>
                        {log.entity_type} #{log.entity_id}
                      </td>
                      <td style={{ color: 'var(--text-muted)', fontSize: '0.8125rem' }}>
                        {new Date(log.created_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
