export default function InfoScreen() {
  return (
    <div>
      <p className="page-title">How to Use</p>

      <div className="info-section">
        <h3>Home screen</h3>
        <p className="text-sm" style={{ color: 'var(--gray-700)' }}>
          Shows today's date, the current time, and whether the desk is
          available (green) or booked (red with the booker's name).
        </p>
      </div>

      <div className="info-section">
        <h3>Quick Book Today</h3>
        <ol className="info-steps">
          <li>On the Home screen, tap <strong>⚡ Quick Book Today</strong> (only visible when the desk is free).</li>
          <li>Type your name on the on-screen keyboard and tap <strong>✓ DONE</strong>.</li>
          <li>The desk is instantly booked for today — no extra steps needed.</li>
        </ol>
      </div>

      <div className="info-section">
        <h3>One-time booking</h3>
        <ol className="info-steps">
          <li>Tap <strong>Book Desk</strong> in the navigation bar.</li>
          <li>Tap the name field and type your name on the keyboard.</li>
          <li>Make sure <strong>One-time dates</strong> is selected.</li>
          <li>Tap the day(s) you want in the calendar (tap again to deselect).</li>
          <li>Tap <strong>Save Booking</strong> to confirm.</li>
        </ol>
      </div>

      <div className="info-section">
        <h3>Recurring booking (every week)</h3>
        <ol className="info-steps">
          <li>Tap <strong>Book Desk</strong> in the navigation bar.</li>
          <li>Enter your name, then switch to <strong>Repeat weekly</strong>.</li>
          <li>Select the weekday(s) to repeat.</li>
          <li>Tap <strong>Save Booking</strong> to confirm.</li>
        </ol>
      </div>

      <div className="info-section">
        <h3>Cancelling a booking</h3>
        <ol className="info-steps">
          <li>Tap <strong>Bookings</strong> in the navigation bar.</li>
          <li>Find the booking you want to remove.</li>
          <li>Tap <strong>✕ Remove</strong> and confirm inline — no pop-up.</li>
        </ol>
      </div>
    </div>
  )
}
