import { useState, useEffect } from 'react'

export default function BookingsList({ navigate, showToast }) {
  const [bookings, setBookings] = useState(null)
  const [error, setError] = useState(null)
  const [confirmId, setConfirmId] = useState(null)

  const fetchBookings = () => {
    fetch('/api/bookings')
      .then(r => r.json())
      .then(data => { setBookings(data); setError(null) })
      .catch(() => setError('Unable to reach the server.'))
  }

  useEffect(() => { fetchBookings() }, [])

  const handleDeleteClick = (id) => {
    // Show inline confirm; no pop-up
    setConfirmId(id)
  }

  const handleConfirmDelete = async (id) => {
    try {
      const res = await fetch(`/api/bookings/${id}`, { method: 'DELETE' })
      if (!res.ok) throw new Error('Delete failed')
      showToast('Booking removed.', 'success')
      setConfirmId(null)
      fetchBookings()
    } catch {
      showToast('Failed to delete booking.', 'error')
    }
  }

  const todayStr = new Date().toISOString().slice(0, 10)

  if (error) {
    return (
      <div>
        <p className="page-title">Upcoming Bookings</p>
        <div className="toast error">{error}</div>
      </div>
    )
  }

  if (bookings === null) {
    return (
      <div style={{ padding: 40, textAlign: 'center' }}>
        <div className="spinner" />
      </div>
    )
  }

  return (
    <div>
      <p className="page-title">Upcoming Bookings</p>

      {bookings.length === 0 ? (
        <p className="text-muted">No upcoming bookings.</p>
      ) : (
        bookings.map(bk => (
          <div key={`${bk.id}-${bk.date}`}>
            {/* ── Row ── */}
            <div className={`booking-row${bk.date === todayStr ? ' today-row' : ''}`}>
              <span className="booking-date">{bk.date}</span>
              <span className="booking-name">{bk.name}</span>

              {bk.date === todayStr && (
                <span className="booking-badge today">Today</span>
              )}
              {bk.recurring && (
                <span className="booking-badge recurring">Recurring</span>
              )}

              <button
                className="btn-danger"
                onClick={() => handleDeleteClick(bk.id)}
                aria-label={`Remove booking for ${bk.name} on ${bk.date}`}
              >
                ✕ Remove
              </button>
            </div>

            {/* ── Inline confirmation (no pop-up) ── */}
            {confirmId === bk.id && (
              <div className="confirm-inline">
                <span>Delete booking for <strong>{bk.name}</strong> on {bk.date}?</span>
                <button
                  className="btn-danger"
                  onClick={() => handleConfirmDelete(bk.id)}
                >
                  Yes, delete
                </button>
                <button
                  className="btn-secondary"
                  onClick={() => setConfirmId(null)}
                >
                  Cancel
                </button>
              </div>
            )}
          </div>
        ))
      )}
    </div>
  )
}
