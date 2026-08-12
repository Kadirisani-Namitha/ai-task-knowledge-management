import { useEffect, useState, useCallback } from 'react';
import { tasksApi } from '../api/tasks';
import { usersApi } from '../api/users';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import StatusBadge from '../components/StatusBadge';
import Modal from '../components/Modal';
import Spinner from '../components/Spinner';

const STATUSES = ['todo', 'in_progress', 'done', 'cancelled'];

const EMPTY_FORM = { title: '', description: '', status: 'todo', assigned_to: '' };

export default function TasksPage() {
  const { isAdmin } = useAuth();
  const toast = useToast();

  const [tasks,        setTasks]        = useState([]);
  const [users,        setUsers]        = useState([]);
  const [loading,      setLoading]      = useState(true);
  const [filterStatus, setFilterStatus] = useState('');
  const [showCreate,   setShowCreate]   = useState(false);
  const [editTask,     setEditTask]     = useState(null);
  const [deleteTask,   setDeleteTask]   = useState(null);
  const [form,         setForm]         = useState(EMPTY_FORM);
  const [submitting,   setSubmitting]   = useState(false);

  const fetchTasks = useCallback(() => {
    setLoading(true);
    tasksApi.list(filterStatus || undefined)
      .then(r => setTasks(r.data))
      .catch(() => toast('Failed to load tasks', 'error'))
      .finally(() => setLoading(false));
  }, [filterStatus, toast]);

  useEffect(() => { fetchTasks(); }, [fetchTasks]);

  useEffect(() => {
    if (isAdmin) {
      usersApi.list().then(r => setUsers(r.data)).catch(() => {});
    }
  }, [isAdmin]);

  const openCreate = () => { setForm(EMPTY_FORM); setShowCreate(true); };
  const openEdit   = (t) => {
    setForm({
      title:       t.title,
      description: t.description ?? '',
      status:      t.status,
      assigned_to: t.assigned_to ?? '',
    });
    setEditTask(t);
  };

  const handleFormChange = (e) =>
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));

  const handleCreate = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const payload = {
        title:       form.title,
        description: form.description || null,
        status:      form.status,
        assigned_to: form.assigned_to ? Number(form.assigned_to) : null,
      };
      await tasksApi.create(payload);
      toast('Task created!', 'success');
      setShowCreate(false);
      fetchTasks();
    } catch (err) {
      toast(err.response?.data?.detail ?? 'Failed to create task', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const payload = isAdmin
        ? {
            title:       form.title,
            description: form.description || null,
            status:      form.status,
            assigned_to: form.assigned_to ? Number(form.assigned_to) : null,
          }
        : { status: form.status };
      await tasksApi.update(editTask.id, payload);
      toast('Task updated!', 'success');
      setEditTask(null);
      fetchTasks();
    } catch (err) {
      toast(err.response?.data?.detail ?? 'Failed to update task', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    setSubmitting(true);
    try {
      await tasksApi.delete(deleteTask.id);
      toast('Task deleted', 'info');
      setDeleteTask(null);
      fetchTasks();
    } catch (err) {
      toast(err.response?.data?.detail ?? 'Failed to delete task', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const TaskForm = ({ onSubmit, isEdit }) => (
    <form id={isEdit ? 'edit-task-form' : 'create-task-form'} onSubmit={onSubmit}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div className="form-group">
          <label className="form-label" htmlFor="task-title">Title *</label>
          <input
            id="task-title"
            name="title"
            type="text"
            className="form-input"
            value={form.title}
            onChange={handleFormChange}
            required
            disabled={isEdit && !isAdmin}
          />
        </div>
        {(!isEdit || isAdmin) && (
          <div className="form-group">
            <label className="form-label" htmlFor="task-desc">Description</label>
            <textarea
              id="task-desc"
              name="description"
              className="form-textarea"
              value={form.description}
              onChange={handleFormChange}
            />
          </div>
        )}
        <div className="form-group">
          <label className="form-label" htmlFor="task-status">Status</label>
          <select
            id="task-status"
            name="status"
            className="form-select"
            value={form.status}
            onChange={handleFormChange}
          >
            {STATUSES.map(s => (
              <option key={s} value={s}>
                {s === 'in_progress' ? 'In Progress' : s.charAt(0).toUpperCase() + s.slice(1)}
              </option>
            ))}
          </select>
        </div>
        {isAdmin && (
          <div className="form-group">
            <label className="form-label" htmlFor="task-assign">Assign to</label>
            <select
              id="task-assign"
              name="assigned_to"
              className="form-select"
              value={form.assigned_to}
              onChange={handleFormChange}
            >
              <option value="">— Unassigned —</option>
              {users.map(u => (
                <option key={u.id} value={u.id}>{u.username}</option>
              ))}
            </select>
          </div>
        )}
      </div>
    </form>
  );

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <div>
          <h1 className="page-title">Tasks</h1>
          <p className="page-subtitle">
            {isAdmin ? 'Manage all tasks across the team' : 'Your assigned tasks'}
          </p>
        </div>
        {isAdmin && (
          <button id="create-task-btn" className="btn btn-primary" onClick={openCreate}>
            + New Task
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="filters-row">
        <span style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>Filter:</span>
        <button
          className={`btn btn-sm ${filterStatus === '' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setFilterStatus('')}
        >All</button>
        {STATUSES.map(s => (
          <button
            key={s}
            className={`btn btn-sm ${filterStatus === s ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setFilterStatus(s)}
          >
            {s === 'in_progress' ? 'In Progress' : s.charAt(0).toUpperCase() + s.slice(1)}
          </button>
        ))}
      </div>

      {/* Table */}
      {loading ? (
        <Spinner large text="Loading tasks…" />
      ) : tasks.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📋</div>
          <h3>No tasks found</h3>
          <p>{filterStatus ? 'Try a different filter.' : 'No tasks have been created yet.'}</p>
        </div>
      ) : (
        <div className="table-wrapper">
          <table aria-label="Tasks table">
            <thead>
              <tr>
                <th>#</th>
                <th>Title</th>
                <th>Status</th>
                <th>Assigned To</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map(task => (
                <tr key={task.id}>
                  <td style={{ color: 'var(--text-muted)', width: 40 }}>{task.id}</td>
                  <td>
                    <div style={{ fontWeight: 500 }}>{task.title}</div>
                    {task.description && (
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                        {task.description.length > 60
                          ? task.description.slice(0, 60) + '…'
                          : task.description}
                      </div>
                    )}
                  </td>
                  <td><StatusBadge value={task.status} /></td>
                  <td style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                    {task.assigned_to ?? '—'}
                  </td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', whiteSpace: 'nowrap' }}>
                    {new Date(task.created_at).toLocaleDateString()}
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.25rem' }}>
                      <button
                        className="btn-icon"
                        title="Edit task"
                        aria-label={`Edit task ${task.id}`}
                        onClick={() => openEdit(task)}
                      >✎</button>
                      {isAdmin && (
                        <button
                          className="btn-icon danger"
                          title="Delete task"
                          aria-label={`Delete task ${task.id}`}
                          onClick={() => setDeleteTask(task)}
                        >✕</button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Modal */}
      {showCreate && (
        <Modal
          title="Create New Task"
          onClose={() => setShowCreate(false)}
          footer={
            <>
              <button className="btn btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
              <button
                className="btn btn-primary"
                form="create-task-form"
                type="submit"
                disabled={submitting}
              >
                {submitting ? <><Spinner /> Saving…</> : 'Create Task'}
              </button>
            </>
          }
        >
          <TaskForm onSubmit={handleCreate} isEdit={false} />
        </Modal>
      )}

      {/* Edit Modal */}
      {editTask && (
        <Modal
          title={`Edit Task #${editTask.id}`}
          onClose={() => setEditTask(null)}
          footer={
            <>
              <button className="btn btn-secondary" onClick={() => setEditTask(null)}>Cancel</button>
              <button
                className="btn btn-primary"
                form="edit-task-form"
                type="submit"
                disabled={submitting}
              >
                {submitting ? <><Spinner /> Saving…</> : 'Save Changes'}
              </button>
            </>
          }
        >
          <TaskForm onSubmit={handleUpdate} isEdit={true} />
        </Modal>
      )}

      {/* Delete Confirm Modal */}
      {deleteTask && (
        <Modal
          title="Delete Task"
          onClose={() => setDeleteTask(null)}
          footer={
            <>
              <button className="btn btn-secondary" onClick={() => setDeleteTask(null)}>Cancel</button>
              <button
                className="btn btn-danger"
                onClick={handleDelete}
                disabled={submitting}
                id="confirm-delete-btn"
              >
                {submitting ? <><Spinner /> Deleting…</> : 'Delete'}
              </button>
            </>
          }
        >
          <p style={{ color: 'var(--text-secondary)' }}>
            Are you sure you want to delete <strong style={{ color: 'var(--text-primary)' }}>"{deleteTask.title}"</strong>?
            This action cannot be undone.
          </p>
        </Modal>
      )}
    </div>
  );
}
