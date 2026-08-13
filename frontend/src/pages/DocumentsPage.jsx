import { useEffect, useState, useRef } from 'react';
import { documentsApi } from '../api/documents';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import Spinner from '../components/Spinner';

const ALLOWED_TYPES = ['.pdf', '.docx', '.txt'];
const MAX_SIZE_MB   = 20;

function formatBytes(b) {
  if (b < 1024)       return `${b} B`;
  if (b < 1024 ** 2)  return `${(b / 1024).toFixed(1)} KB`;
  return `${(b / 1024 ** 2).toFixed(1)} MB`;
}

function formatDate(str) {
  return new Date(str).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
}

export default function DocumentsPage() {
  const { isAdmin } = useAuth();
  const toast = useToast();

  const [docs,      setDocs]      = useState([]);
  const [loading,   setLoading]   = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragging,  setDragging]  = useState(false);
  const fileRef = useRef(null);

  const fetchDocs = () => {
    setLoading(true);
    documentsApi.list()
      .then(r => setDocs(r.data))
      .catch(() => toast('Failed to load documents', 'error'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchDocs(); }, []); // eslint-disable-line

function formatApiError(detail, fallback = 'Upload failed') {
  if (!detail) return fallback;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map(d => (typeof d === 'string' ? d : d.msg || JSON.stringify(d))).join(', ');
  }
  if (typeof detail === 'object') return detail.msg || fallback;
  return fallback;
}

  const upload = async (file) => {
    if (!file) return;
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!ALLOWED_TYPES.includes(ext)) {
      toast(`Unsupported file type. Allowed: ${ALLOWED_TYPES.join(', ')}`, 'error');
      return;
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      toast(`File too large. Max size: ${MAX_SIZE_MB} MB`, 'error');
      return;
    }
    setUploading(true);
    try {
      await documentsApi.upload(file);
      toast('Document uploaded and indexed!', 'success');
      fetchDocs();
    } catch (err) {
      toast(formatApiError(err.response?.data?.detail, 'Upload failed'), 'error');
    } finally {
      setUploading(false);
    }
  };

  const handleFileInput = (e) => { upload(e.target.files[0]); e.target.value = ''; };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    upload(e.dataTransfer.files[0]);
  };

  const EXT_ICONS = { pdf: '📄', docx: '📝', txt: '📃' };
  const getIcon = (name) => {
    const ext = name?.split('.').pop()?.toLowerCase();
    return EXT_ICONS[ext] ?? '📎';
  };

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <div>
          <h1 className="page-title">Documents</h1>
          <p className="page-subtitle">Upload and manage knowledge base documents</p>
        </div>
      </div>

      {/* Hidden file input placed outside upload zone to avoid event bubbling cancellation */}
      <input
        ref={fileRef}
        type="file"
        accept=".pdf,.docx,.txt"
        style={{ display: 'none' }}
        onChange={handleFileInput}
        aria-hidden="true"
      />

      {/* Upload zone */}
      <div
        id="upload-zone"
        className={`upload-zone${dragging ? ' dragging' : ''}`}
        onClick={() => !uploading && fileRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        role="button"
        tabIndex={0}
        aria-label="Upload document — click or drag and drop"
        onKeyDown={(e) => e.key === 'Enter' && fileRef.current?.click()}
      >
        {uploading ? (
          <Spinner large text="Uploading & indexing…" />
        ) : (
          <>
            <div className="upload-zone-icon" aria-hidden="true">
              {dragging ? '📂' : '☁'}
            </div>
            <div className="upload-zone-text">
              {dragging ? 'Drop to upload' : 'Click or drag & drop to upload'}
            </div>
            <div className="upload-zone-sub">
              PDF, DOCX, TXT — max {MAX_SIZE_MB} MB
            </div>
          </>
        )}
      </div>

      {/* Documents list */}
      {loading ? (
        <Spinner large text="Loading documents…" />
      ) : docs.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📚</div>
          <h3>No documents yet</h3>
          <p>{isAdmin ? 'Upload a document to get started.' : 'No documents have been uploaded.'}</p>
        </div>
      ) : (
        <div className="table-wrapper">
          <table aria-label="Documents table">
            <thead>
              <tr>
                <th>File</th>
                <th>Type</th>
                <th>Size</th>
                <th>Uploaded</th>
                <th>Chunks</th>
              </tr>
            </thead>
            <tbody>
              {docs.map(doc => {
                const ext = doc.filename?.split('.').pop()?.toUpperCase() ?? '—';
                return (
                  <tr key={doc.id}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontSize: '1.25rem' }} aria-hidden="true">{getIcon(doc.filename)}</span>
                        <div>
                          <div style={{ fontWeight: 500 }}>{doc.filename}</div>
                          {doc.description && (
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{doc.description}</div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className="badge badge-todo">{ext}</span>
                    </td>
                    <td style={{ color: 'var(--text-secondary)' }}>
                      {doc.file_size ? formatBytes(doc.file_size) : '—'}
                    </td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '0.8125rem' }}>
                      {doc.created_at ? formatDate(doc.created_at) : '—'}
                    </td>
                    <td style={{ color: 'var(--text-secondary)' }}>
                      {doc.chunk_count ?? '—'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
