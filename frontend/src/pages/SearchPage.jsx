import { useState, useRef } from 'react';
import { searchApi } from '../api/search';
import { useToast } from '../components/Toast';
import Spinner from '../components/Spinner';

export default function SearchPage() {
  const toast = useToast();
  const inputRef = useRef(null);

  const [query,    setQuery]    = useState('');
  const [topK,     setTopK]     = useState(5);
  const [results,  setResults]  = useState(null);
  const [loading,  setLoading]  = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setSearched(true);
    try {
      const res = await searchApi.search(query.trim(), topK);
      setResults(res.data);
    } catch (err) {
      toast(err.response?.data?.detail ?? 'Search failed', 'error');
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const scoreColor = (score) => {
    if (score >= 0.75) return 'var(--success)';
    if (score >= 0.5)  return 'var(--info)';
    return 'var(--text-muted)';
  };

  const hits = results?.results ?? [];

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <div>
          <h1 className="page-title">Semantic Search</h1>
          <p className="page-subtitle">AI-powered search across your knowledge base using natural language</p>
        </div>
      </div>

      {/* Search bar */}
      <form onSubmit={handleSearch}>
        <div className="search-bar-row">
          <div style={{ flex: 1 }}>
            <input
              ref={inputRef}
              id="search-input"
              type="search"
              className="form-input"
              placeholder="Ask anything about your documents…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              autoFocus
            />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label" htmlFor="top-k-select" style={{ fontSize: '0.75rem', whiteSpace: 'nowrap' }}>
              Results
            </label>
            <select
              id="top-k-select"
              className="form-select"
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              style={{ width: 80 }}
            >
              {[3, 5, 10, 20].map(n => <option key={n} value={n}>{n}</option>)}
            </select>
          </div>
          <button
            type="submit"
            id="search-submit-btn"
            className="btn btn-primary"
            disabled={loading || !query.trim()}
            style={{ alignSelf: 'flex-end' }}
          >
            {loading ? <><Spinner /> Searching…</> : '⌕ Search'}
          </button>
        </div>
      </form>

      {/* Tips (before search) */}
      {!searched && (
        <div className="card" style={{ marginTop: '1rem' }}>
          <h3 style={{ marginBottom: '1rem', fontSize: '0.9375rem' }}>💡 Search Tips</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '0.75rem' }}>
            {[
              { icon: '🔍', text: 'Use natural language — describe what you\'re looking for' },
              { icon: '📄', text: 'Search across all indexed document types (PDF, DOCX, TXT)' },
              { icon: '🎯', text: 'Results are ranked by semantic similarity score' },
              { icon: '⚡', text: 'Powered by all-MiniLM-L6-v2 sentence embeddings' },
            ].map(({ icon, text }) => (
              <div key={text} style={{
                display: 'flex', gap: '0.625rem', alignItems: 'flex-start',
                padding: '0.75rem', borderRadius: 'var(--radius-md)',
                background: 'var(--bg-elevated)',
              }}>
                <span style={{ fontSize: '1.1rem' }}>{icon}</span>
                <span style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{text}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Loading */}
      {loading && <Spinner large text="Searching documents…" />}

      {/* Results */}
      {!loading && searched && (
        <>
          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            marginBottom: '1rem',
          }}>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', margin: 0 }}>
              {hits.length > 0
                ? `Found ${hits.length} result${hits.length !== 1 ? 's' : ''} for "${results.query}"`
                : `No results found for "${results?.query ?? query}"`}
            </p>
            {hits.length > 0 && (
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Searched {results?.chunks_searched ?? '—'} chunks
              </span>
            )}
          </div>

          {hits.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">🔍</div>
              <h3>No results found</h3>
              <p>Try different keywords or upload more documents to the knowledge base.</p>
            </div>
          ) : (
            <div>
              {hits.map((hit, i) => (
                <div key={i} className="search-result">
                  <div className="search-result-meta">
                    <span className="search-score" style={{ color: scoreColor(hit.score) }}>
                      {(hit.score * 100).toFixed(0)}% match
                    </span>
                    <span className="search-filename">📄 {hit.document?.filename ?? `Document #${hit.document_id}`}</span>
                    {hit.chunk_index !== undefined && (
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        Chunk {hit.chunk_index + 1}
                      </span>
                    )}
                  </div>
                  <p className="search-snippet">
                    {hit.text ?? hit.chunk_text ?? 'No preview available.'}
                  </p>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
