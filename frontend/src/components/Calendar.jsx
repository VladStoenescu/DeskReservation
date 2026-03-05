import { useState, useEffect } from 'react'

/**
 * Monthly calendar widget.
 * Tapping a future date toggles it; past dates are disabled.
 * Already-booked dates are highlighted in red but still selectable (to override).
 */
export default function Calendar({ selectedDates, onChangeDates }) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const [viewYear, setViewYear] = useState(today.getFullYear())
  const [viewMonth, setViewMonth] = useState(today.getMonth())
  const [bookedDates, setBookedDates] = useState([])

  // Fetch booked dates once (for visual hint)
  useEffect(() => {
    fetch('/api/bookings')
      .then(r => r.json())
      .then(data => setBookedDates(data.map(b => b.date)))
      .catch(() => {})
  }, [])

  const prevMonth = () => {
    if (viewMonth === 0) { setViewMonth(11); setViewYear(y => y - 1) }
    else setViewMonth(m => m - 1)
  }
  const nextMonth = () => {
    if (viewMonth === 11) { setViewMonth(0); setViewYear(y => y + 1) }
    else setViewMonth(m => m + 1)
  }

  const toggle = (dateStr) => {
    onChangeDates(prev =>
      prev.includes(dateStr) ? prev.filter(d => d !== dateStr) : [...prev, dateStr]
    )
  }

  const DAY_NAMES = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
  const MONTH_NAMES = [
    'January','February','March','April','May','June',
    'July','August','September','October','November','December',
  ]

  // Build grid: first cell = Monday of the week that contains day 1
  const firstDay = new Date(viewYear, viewMonth, 1)
  // getDay() returns 0=Sun; we want 0=Mon
  const startOffset = (firstDay.getDay() + 6) % 7
  const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate()

  const cells = []
  for (let i = 0; i < startOffset; i++) cells.push(null)
  for (let d = 1; d <= daysInMonth; d++) cells.push(d)
  while (cells.length % 7 !== 0) cells.push(null)

  const rows = []
  for (let i = 0; i < cells.length; i += 7) rows.push(cells.slice(i, i + 7))

  return (
    <div className="calendar">
      {/* Nav */}
      <div className="cal-nav">
        <button className="cal-nav-btn" onClick={prevMonth}>‹</button>
        <span className="cal-month">{MONTH_NAMES[viewMonth]} {viewYear}</span>
        <button className="cal-nav-btn" onClick={nextMonth}>›</button>
      </div>

      {/* Day headers */}
      <div className="cal-grid">
        {DAY_NAMES.map(d => (
          <div key={d} className="cal-header-cell">{d}</div>
        ))}
      </div>

      {/* Day grid */}
      {rows.map((row, ri) => (
        <div key={ri} className="cal-grid" style={{ marginBottom: 3 }}>
          {row.map((day, di) => {
            if (!day) return <div key={di} />

            const dateStr = `${viewYear}-${String(viewMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
            const cellDate = new Date(viewYear, viewMonth, day)
            const isPast     = cellDate < today
            const isToday    = cellDate.getTime() === today.getTime()
            const isSelected = selectedDates.includes(dateStr)
            const isBooked   = bookedDates.includes(dateStr)

            let cls = 'cal-day'
            if (isSelected) cls += ' selected'
            else if (isBooked) cls += ' booked'
            if (isToday && !isSelected) cls += ' today'

            return (
              <button
                key={di}
                className={cls}
                disabled={isPast}
                onClick={() => toggle(dateStr)}
                aria-label={dateStr}
                aria-pressed={isSelected}
              >
                {day}
              </button>
            )
          })}
        </div>
      ))}
    </div>
  )
}
