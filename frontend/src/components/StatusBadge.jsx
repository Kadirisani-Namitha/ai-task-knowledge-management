const STATUS_MAP = {
  // Backend TaskStatus enum values — uppercase (raw from API)
  PENDING:     { label: 'Pending',     cls: 'badge-todo'        },
  COMPLETED:   { label: 'Completed',   cls: 'badge-done'        },
  // Lowercase variants (used in filter comparisons and form values)
  pending:     { label: 'Pending',     cls: 'badge-todo'        },
  completed:   { label: 'Completed',   cls: 'badge-done'        },
  // Legacy/fallback mappings (kept for safety)
  todo:        { label: 'To Do',       cls: 'badge-todo'        },
  in_progress: { label: 'In Progress', cls: 'badge-in_progress' },
  done:        { label: 'Done',        cls: 'badge-done'        },
  cancelled:   { label: 'Cancelled',   cls: 'badge-cancelled'   },
};


const ROLE_MAP = {
  admin: { label: 'Admin', cls: 'badge-admin' },
  user:  { label: 'User',  cls: 'badge-user'  },
};

export default function StatusBadge({ value, type = 'status' }) {
  const map  = type === 'role' ? ROLE_MAP : STATUS_MAP;
  const info = map[value] ?? { label: value, cls: 'badge-todo' };
  return <span className={`badge ${info.cls}`}>{info.label}</span>;
}
