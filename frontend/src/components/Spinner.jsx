export default function Spinner({ large, text }) {
  return (
    <div className={large ? 'loading-state' : ''} style={large ? {} : { display: 'inline-block' }}>
      <div className={`spinner${large ? ' spinner-lg' : ''}`} />
      {large && text && <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>{text}</span>}
    </div>
  );
}
