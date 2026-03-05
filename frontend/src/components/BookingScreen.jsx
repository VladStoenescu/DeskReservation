import { useState } from 'react'
import Calendar from './Calendar'
import OnScreenKeyboard from './OnScreenKeyboard'

const WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

export default function BookingScreen({ navigate, showToast }) {
  const [name, setName] = useState('')
  const [mode, setMode] = useState('onetime')  // 'onetime' | 'recurring'
  const [selectedDates, setSelectedDates] = useState([])
  const [selectedWeekdays, setSelectedWeekdays] = useState([])
  const [showKeyboard, setShowKeyboard] = useState(false)
  const [saving, setSaving] = useState(false)
  const [inlineError, setInlineError] = useState('')

  const setError = (msg) => {
    setInlineError(msg)
    setTimeout(() => setInlineError(''), 4000)
  }

  const toggleWeekday = (i) => {
    setSelectedWeekdays(prev =>
      prev.includes(i) ? prev.filter(x => x !== i) : [...prev, i]
    )
  }

  const handleSave = async () => {
    if (!name.trim()) { setError('Please enter your name.'); return }

    if (mode === 'onetime') {
      if (selectedDates.length === 0) { setError('Please select at least one date.'); return }
    } else {
      if (selectedWeekdays.length === 0) { setError('Please select at least one weekday.'); return }
    }

    setSaving(true)
    try {
      const body = mode === 'onetime'
        ? { name, type: 'onetime', dates: selectedDates }
        : { name, type: 'recurring', weekdays: selectedWeekdays }

      const res = await fetch('/api/bookings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (!res.ok) { setError(data.error || 'Failed to save booking.'); return }

      showToast(data.message, 'success')
      navigate('home')
    } catch {
      setError('Network error — please try again.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <p className="page-title">New Booking</p>

      {/* ── Inline error ── */}
      {inlineError && (
        <div className="toast error mb-12" role="alert">{inlineError}</div>
      )}

      {/* ── Name field ── */}
      <div className="form-group">
        <label className="form-label">Your name</label>
        <div className="flex gap-8">
          <input
            className="form-input"
            value={name}
            readOnly
            placeholder="Tap to enter your name"
            onClick={() => setShowKeyboard(true)}
          />
          <button
            className="btn-secondary"
            style={{ whiteSpace: 'nowrap' }}
            onClick={() => setShowKeyboard(true)}
          >
            ✏ Edit
          </button>
        </div>
      </div>

      {/* ── Mode tabs ── */}
      <div className="mode-tabs">
        <button
          className={`mode-tab${mode === 'onetime' ? ' active' : ''}`}
          onClick={() => setMode('onetime')}
        >
          One-time dates
        </button>
        <button
          className={`mode-tab${mode === 'recurring' ? ' active' : ''}`}
          onClick={() => setMode('recurring')}
        >
          Repeat weekly
        </button>
      </div>

      {/* ── One-time: calendar ── */}
      {mode === 'onetime' && (
        <div>
          <Calendar
            selectedDates={selectedDates}
            onChangeDates={setSelectedDates}
          />
          {selectedDates.length > 0 && (
            <p className="text-muted mt-4">
              {selectedDates.length} date{selectedDates.length > 1 ? 's' : ''} selected
            </p>
          )}
        </div>
      )}

      {/* ── Recurring: weekday chips ── */}
      {mode === 'recurring' && (
        <div>
          <label className="form-label">Select weekday(s)</label>
          <div className="weekday-grid">
            {WEEKDAYS.map((day, i) => (
              <button
                key={day}
                className={`weekday-chip${selectedWeekdays.includes(i) ? ' selected' : ''}`}
                onClick={() => toggleWeekday(i)}
              >
                {day}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ── Save button ── */}
      <div className="mt-16">
        <button className="btn-success" onClick={handleSave} disabled={saving}>
          {saving ? <span className="spinner" /> : '✓  Save Booking'}
        </button>
      </div>

      {/* ── On-screen keyboard ── */}
      {showKeyboard && (
        <OnScreenKeyboard
          initialValue={name}
          onConfirm={(val) => { setName(val); setShowKeyboard(false) }}
          onCancel={() => setShowKeyboard(false)}
        />
      )}
    </div>
  )
}
