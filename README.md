# DeskReservation

A desk reservation app for the **Raspberry Pi 7″ display** (800 × 480 px).

Available in two flavours:

| Interface | File | Description |
|---|---|---|
| **Web (React + Flask)** | `api.py` + `frontend/` | Modern corporate UI in any browser or kiosk Chromium |
| **Kiosk (Tkinter)** | `main.py` | Self-contained Tkinter app, no browser required |

## Features

- **Live status** — home screen shows in real time whether the desk is free or booked.
- **One-time booking** — pick any future days in an interactive calendar.
- **Recurring booking** — select weekdays that repeat every week.
- **Manage bookings** — view upcoming schedule and delete any entry inline.
- **On-screen keyboard** — type your name without a physical keyboard.
- **No pop-ups** — all feedback is shown inline (toast notifications / status messages).
- **Corporate design** — clean navy/white/gold palette suited for a professional environment.

---

## Web interface (React + Flask) — *recommended*

### Requirements

| Requirement | Details |
|---|---|
| Python | 3.9 or newer |
| Node.js | 18 or newer (for building the React frontend) |
| npm | bundled with Node.js |

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/VladStoenescu/DeskReservation.git
cd DeskReservation

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Build the React frontend
cd frontend
npm install
npm run build
cd ..
```

### Running

```bash
# Start the Flask API (serves the built React app on http://localhost:5000)
python3 api.py

# Custom port
python3 api.py --port 8080

# Development (Vite dev server with hot reload, API proxied to Flask)
python3 api.py &
cd frontend && npm run dev
```

### Kiosk mode on Raspberry Pi (Chromium fullscreen)

```bash
# Auto-start on boot via crontab / rc.local:
python3 /home/pi/DeskReservation/api.py &
chromium-browser --kiosk http://localhost:5000
```

---

## Tkinter kiosk (standalone, no browser)

### Requirements

| Requirement | Details |
|---|---|
| Hardware | Raspberry Pi (any model) + 7″ official touchscreen |
| OS | Raspberry Pi OS (Bullseye / Bookworm) |
| Python | 3.9 or newer |
| System package | `python3-tk` |

### Installation

```bash
sudo apt-get install -y python3-tk
```

### Running

```bash
# Windowed mode (development / testing)
python3 main.py

# Fullscreen kiosk mode
python3 main.py --fullscreen
```

Press **Escape** to exit fullscreen mode during development.

---

## Project structure

```
DeskReservation/
├── main.py           – Tkinter kiosk UI (no pop-ups, corporate design)
├── api.py            – Flask REST API for the React front-end
├── database.py       – SQLite persistence layer (shared by both interfaces)
├── bookings.db       – created automatically on first run
├── requirements.txt  – Python dependencies (flask, flask-cors)
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── App.jsx
        ├── index.css
        └── components/
            ├── StatusScreen.jsx
            ├── BookingScreen.jsx
            ├── BookingsList.jsx
            ├── Calendar.jsx
            ├── OnScreenKeyboard.jsx
            ├── InfoScreen.jsx
            └── Toast.jsx
```

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/status` | Today's booking status |
| `GET` | `/api/bookings?days=N` | Upcoming bookings (default 60 days) |
| `POST` | `/api/bookings` | Create a one-time or recurring booking |
| `DELETE` | `/api/bookings/<id>` | Delete a booking |

