import { useState, useEffect } from 'react'
import OnScreenKeyboard from './OnScreenKeyboard'

export default function StatusScreen({ navigate, showToast }) {
  const [status, setStatus] = useState(null)
  const [clock, setClock] = useState('')
  const [error, setError] = useState(null)
  const [showQuickBook, setShowQuickBook] = useState(false)
  const [quickBooking, setQuickBooking] = useState(false)

  // Live clock
  useEffect(() => {
    const tick = () => {
      const now = new Date()
      const hh = String(now.getHours()).padStart(2, '0')
      const mm = String(now.getMinutes()).padStart(2, '0')
      const ss = String(now.getSeconds()).padStart(2, '0')
      setClock(`${hh}:${mm}:${ss}`)
    }
    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
  }, [])

  // Fetch status, then re-poll every 60 s
  const fetchStatus = () => {
    fetch('/api/status')
      .then(r => r.json())
      .then(data => { setStatus(data); setError(null) })
      .catch(() => setError('Unable to reach the server.'))
  }

  useEffect(() => {
    fetchStatus()
    const id = setInterval(fetchStatus, 60_000)
    return () => clearInterval(id)
  }, [])

  const handleQuickBook = async (name) => {
    setShowQuickBook(false)
    setQuickBooking(true)
    try {
      const today = new Date().toISOString().slice(0, 10)
      const res = await fetch('/api/bookings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, type: 'onetime', dates: [today] }),
      })
      const data = await res.json()
      if (!res.ok) {
        showToast(data.error || 'Failed to book desk.', 'error')
      } else {
        showToast(`Desk booked for ${name} today! ✓`, 'success')
        fetchStatus()
      }
    } catch {
      showToast('Network error — please try again.', 'error')
    } finally {
      setQuickBooking(false)
    }
  }

  if (error) {
    return (
      <div>
        <p className="page-title">Desk Status</p>
        <div className="toast error">{error}</div>
      </div>
    )
  }

  if (!status) {
    return (
      <div style={{ padding: 40, textAlign: 'center' }}>
        <div className="spinner" />
      </div>
    )
  }

  const free = !status.is_booked

  return (
    <div>
      {/* ── Meta row ── */}
      <div className="meta-row">
        <span className="meta-date">{status.display_date}</span>
        <span className="meta-clock">{clock}</span>
      </div>

      {/* ── Status card ── */}
      <div className="status-card">
        <div className={`status-bar ${free ? 'free' : 'booked'}`} />
        <div className="status-body">
          <div className={`status-label ${free ? 'free' : 'booked'}`}>
            {free ? 'Available' : 'Booked'}
          </div>
          {free ? (
            <div className="status-name">Desk is free today</div>
          ) : (
            <div className="status-name">{status.booker_name}</div>
          )}
          <div className="status-date">{status.display_date}</div>
        </div>
      </div>

      {/* ── CTA buttons ── */}
      <div className="cta-row">
        {free && (
          <button
            className="btn-quick-book"
            onClick={() => setShowQuickBook(true)}
            disabled={quickBooking}
          >
            {quickBooking ? <span className="spinner" /> : '⚡ Quick Book Today'}
          </button>
        )}
        <button className="btn-primary" onClick={() => navigate('booking')}>
          {free ? 'Pick Dates' : 'Book Another Day'}
        </button>
      </div>

      {/* ── Quick-book keyboard overlay ── */}
      {showQuickBook && (
        <OnScreenKeyboard
          initialValue=""
          onConfirm={handleQuickBook}
          onCancel={() => setShowQuickBook(false)}
        />
      )}
    </div>
  )
}
