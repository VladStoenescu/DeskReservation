import { useState } from 'react'

const ROWS = [
  ['1','2','3','4','5','6','7','8','9','0'],
  ['Q','W','E','R','T','Y','U','I','O','P'],
  ['A','S','D','F','G','H','J','K','L'],
  ['Z','X','C','V','B','N','M'],
]

/**
 * Touch-friendly on-screen keyboard.
 * Renders as a bottom-sheet overlay (no modal pop-up).
 * Inline validation — no browser alert/confirm.
 */
export default function OnScreenKeyboard({ initialValue, onConfirm, onCancel }) {
  const [text, setText] = useState(initialValue || '')
  const [error, setError] = useState('')

  const press = (ch) => setText(prev => prev + ch)
  const backspace = () => setText(prev => prev.slice(0, -1))
  const handleDone = () => {
    const trimmed = text.trim()
    if (!trimmed) { setError('Please enter a name.'); return }
    onConfirm(trimmed)
  }

  return (
    <div
      className="osk-backdrop"
      role="button"
      tabIndex={0}
      aria-label="Close keyboard"
      onClick={(e) => { if (e.target === e.currentTarget) onCancel() }}
      onKeyDown={(e) => {
        if (e.key === 'Escape' || (e.key === 'Enter' && e.target === e.currentTarget)) onCancel()
      }}
    >
      <div className="osk" role="dialog" aria-label="On-screen keyboard">
        {/* Text display */}
        <div className="osk-display" aria-live="polite">
          <span>{text}</span>
          <span className="osk-cursor" aria-hidden="true" />
        </div>

        {/* Error (inline, no pop-up) */}
        {error && <div className="osk-error" role="alert">{error}</div>}

        {/* Key rows */}
        {ROWS.map((row, ri) => (
          <div key={ri} className="osk-row">
            {row.map(ch => (
              <button key={ch} className="osk-key" onClick={() => press(ch)}>
                {ch}
              </button>
            ))}
          </div>
        ))}

        {/* Bottom action row */}
        <div className="osk-row">
          <button className="osk-key wide cancel" onClick={onCancel}>Cancel</button>
          <button className="osk-key wide" style={{ flex: 3 }} onClick={() => press(' ')}>
            SPACE
          </button>
          <button className="osk-key wide del" onClick={backspace}>⌫ DEL</button>
          <button className="osk-key wide done" onClick={handleDone}>✓ DONE</button>
        </div>
      </div>
    </div>
  )
}
