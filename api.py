#!/usr/bin/env python3
"""Flask REST API for the Desk Reservation web interface.

Endpoints
---------
GET  /api/status                  – today's booking status
GET  /api/bookings?days=N         – upcoming bookings (default 60 days)
POST /api/bookings                – create a booking (one-time or recurring)
DELETE /api/bookings/<id>         – delete a booking by id

The React front-end build is served as static files from frontend/dist/.
Run with:
    python3 api.py               # development (port 5000)
    python3 api.py --port 8080   # custom port
"""

import os
import sys
from datetime import date

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from database import (
    init_db,
    get_booking_for_date,
    get_future_bookings,
    add_bookings,
    add_recurring_booking,
    delete_booking,
)

# ─── App setup ────────────────────────────────────────────────────────────────

_DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist")

app = Flask(__name__, static_folder=_DIST, static_url_path="")
CORS(app, resources={r"/api/*": {"origins": "*"}})

WEEKDAYS = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday",
]


# ─── API routes ───────────────────────────────────────────────────────────────

@app.route("/api/status")
def api_status():
    """Return today's date and desk booking status."""
    today = date.today()
    booker = get_booking_for_date(today)
    return jsonify({
        "date": today.strftime("%Y-%m-%d"),
        "display_date": today.strftime("%A, %d %B %Y").replace(" 0", " "),
        "is_booked": bool(booker),
        "booker_name": booker or "",
    })


@app.route("/api/bookings")
def api_get_bookings():
    """Return upcoming bookings for the next *days* days (default 60)."""
    days = request.args.get("days", 60, type=int)
    return jsonify(get_future_bookings(days))


@app.route("/api/bookings", methods=["POST"])
def api_create_booking():
    """Create a one-time or recurring booking.

    Request body (JSON):
        {
            "name": "Alice",
            "type": "onetime",          // or "recurring"
            "dates": ["2025-06-01"],    // for onetime
            "weekdays": [0, 2]          // for recurring (0=Mon)
        }
    """
    data = request.get_json(force=True, silent=True) or {}
    name = (data.get("name") or "").strip()

    if not name:
        return jsonify({"error": "Name is required"}), 400

    booking_type = data.get("type", "onetime")

    if booking_type == "recurring":
        weekdays = data.get("weekdays") or []
        if not weekdays:
            return jsonify({"error": "Select at least one weekday"}), 400
        for wd in weekdays:
            add_recurring_booking(name, int(wd))
        day_names = ", ".join(WEEKDAYS[int(i)] for i in weekdays)
        return jsonify({
            "success": True,
            "message": f"Recurring booking saved for every {day_names}",
        })

    # one-time
    dates_str = data.get("dates") or []
    if not dates_str:
        return jsonify({"error": "Select at least one date"}), 400
    try:
        dates = [date.fromisoformat(d) for d in dates_str]
    except ValueError as exc:
        return jsonify({"error": f"Invalid date format: {exc}"}), 400

    add_bookings(name, dates)
    return jsonify({
        "success": True,
        "message": f"Booked {len(dates)} day(s) for {name}",
    })


@app.route("/api/bookings/<int:booking_id>", methods=["DELETE"])
def api_delete_booking(booking_id: int):
    """Delete a booking by its primary-key id."""
    delete_booking(booking_id)
    return jsonify({"success": True})


# ─── Serve React SPA ──────────────────────────────────────────────────────────

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path: str):
    """Serve the compiled React app or a friendly error when not yet built."""
    if path and os.path.exists(os.path.join(_DIST, path)):
        return send_from_directory(_DIST, path)

    index = os.path.join(_DIST, "index.html")
    if os.path.exists(index):
        return send_from_directory(_DIST, "index.html")

    return (
        "Frontend not built. Run:  cd frontend && npm install && npm run build",
        404,
    )


# ─── Entry point ─────────────────────────────────────────────────────────────

def main() -> None:
    init_db()

    port = 5000
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--port" and i + 1 < len(args):
            port = int(args[i + 1])
            i += 2
        else:
            i += 1

    host = os.environ.get("HOST", "0.0.0.0")
    # Debug mode is intentionally disabled; use a WSGI server (e.g. gunicorn) for production.
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    main()
