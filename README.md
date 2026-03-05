# DeskReservation

A touchscreen-friendly desk reservation app for the **Raspberry Pi 7″ display** (800 × 480 px).

## Features

- **Live status** – the home screen shows in real time whether the desk is free (green) or booked (red with the booker's name).
- **One-time booking** – pick any future days in an interactive calendar.
- **Recurring booking** – select weekdays that repeat every week.
- **Manage bookings** – view the full upcoming schedule and delete any entry.
- **On-screen keyboard** – type your name without a physical keyboard.
- **Info screen** – built-in instructions accessible via the ℹ button.
- **Auto-refresh** – the home screen updates every 60 seconds automatically.

## Requirements

| Requirement | Details |
|---|---|
| Hardware | Raspberry Pi (any model) + 7″ official touchscreen |
| OS | Raspberry Pi OS (Bullseye / Bookworm) |
| Python | 3.9 or newer |
| System package | `python3-tk` |

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/VladStoenescu/DeskReservation.git
cd DeskReservation

# 2. Install the system-level Tkinter binding (if not already present)
sudo apt-get install -y python3-tk
```

## Running

```bash
# Windowed mode (for development / testing)
python3 main.py

# Fullscreen kiosk mode (recommended for the Raspberry Pi touchscreen)
python3 main.py --fullscreen
```

Press **Escape** to exit fullscreen mode during development.

## Auto-start on boot (optional)

Add the following line to `/etc/rc.local` (before `exit 0`):

```bash
su pi -c "DISPLAY=:0 python3 /home/pi/DeskReservation/main.py --fullscreen &"
```

## Project structure

```
DeskReservation/
├── main.py        – Tkinter UI (screens, widgets, app controller)
├── database.py    – SQLite persistence layer
├── bookings.db    – created automatically on first run
└── requirements.txt
```

## Screens

| Screen | Description |
|---|---|
| **Home** | Current date, free/booked status, Book & navigation buttons |
| **New Booking** | Name entry, one-time calendar picker or recurring weekday selector |
| **Bookings list** | Scrollable list of upcoming bookings with delete option |
| **Info** | Step-by-step usage instructions |

