import { useState, useCallback } from 'react'
import StatusScreen from './components/StatusScreen'
import BookingScreen from './components/BookingScreen'
import BookingsList from './components/BookingsList'
import InfoScreen from './components/InfoScreen'
import Toast from './components/Toast'

export default function App() {
  const [screen, setScreen] = useState('home')
  const [toast, setToast] = useState(null)
  const [toastTimer, setToastTimer] = useState(null)

  const showToast = useCallback((message, type = 'success') => {
    if (toastTimer) clearTimeout(toastTimer)
    setToast({ message, type })
    const t = setTimeout(() => setToast(null), 3500)
    setToastTimer(t)
  }, [toastTimer])

  const navigate = useCallback((s) => {
    setToast(null)
    setScreen(s)
  }, [])

  const navItems = [
    { id: 'home',     label: 'Home' },
    { id: 'booking',  label: 'Book Desk' },
    { id: 'list',     label: 'Bookings' },
    { id: 'info',     label: 'Help' },
  ]

  return (
    <div className="app">
      {/* ── Header ── */}
      <header className="header">
        <div className="header-left">
          <span className="header-logo">Corp</span>
          <span className="header-title">Desk Reservation</span>
        </div>
        <nav className="header-nav">
          {navItems.map(({ id, label }) => (
            <button
              key={id}
              className={`btn-nav${screen === id ? ' active' : ''}`}
              onClick={() => navigate(id)}
            >
              {label}
            </button>
          ))}
        </nav>
      </header>

      {/* ── Toast ── */}
      {toast && (
        <div className="toast-container">
          <Toast message={toast.message} type={toast.type} />
        </div>
      )}

      {/* ── Screen ── */}
      <div className="content">
        <div key={screen} className="screen-enter">
          {screen === 'home'    && <StatusScreen navigate={navigate} showToast={showToast} />}
          {screen === 'booking' && <BookingScreen navigate={navigate} showToast={showToast} />}
          {screen === 'list'    && <BookingsList navigate={navigate} showToast={showToast} />}
          {screen === 'info'    && <InfoScreen />}
        </div>
      </div>
    </div>
  )
}
