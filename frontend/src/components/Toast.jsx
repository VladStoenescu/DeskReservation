export default function Toast({ message, type }) {
  return (
    <div className={`toast ${type}`} role="status" aria-live="polite">
      {type === 'success' && <span>✓</span>}
      {type === 'error'   && <span>✕</span>}
      {type === 'info'    && <span>ℹ</span>}
      {message}
    </div>
  )
}
