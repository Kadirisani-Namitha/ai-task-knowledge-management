const STATUS_MAP = {
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
