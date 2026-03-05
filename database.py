"""Database operations for the Desk Reservation app.

Schema
------
bookings
    id             INTEGER PK AUTOINCREMENT
    name           TEXT NOT NULL          – person who booked
    book_date      TEXT                   – 'YYYY-MM-DD' for one-time, NULL for recurring
    is_recurring   INTEGER DEFAULT 0      – 1 = weekly recurring rule
    recur_weekday  INTEGER DEFAULT -1     – 0=Mon … 6=Sun (only used when is_recurring=1)
    created_at     TEXT DEFAULT (datetime('now'))
"""

import os
import sqlite3
from datetime import date, timedelta
from typing import Dict, List, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bookings.db")


# ─── Connection helper ────────────────────────────────────────────────────────

def _connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


# ─── Initialisation ───────────────────────────────────────────────────────────

def init_db() -> None:
    """Create tables if they do not already exist."""
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL,
                book_date     TEXT,
                is_recurring  INTEGER NOT NULL DEFAULT 0,
                recur_weekday INTEGER NOT NULL DEFAULT -1,
                created_at    TEXT    DEFAULT (datetime('now'))
            )
        """)
        conn.commit()


# ─── Read helpers ─────────────────────────────────────────────────────────────

def get_booking_for_date(target_date: date) -> Optional[str]:
    """Return the booker's name for *target_date*, or ``None`` if the desk is free.

    Specific one-time bookings always take precedence over recurring rules.
    """
    date_str = target_date.strftime("%Y-%m-%d")
    weekday  = target_date.weekday()          # 0=Monday … 6=Sunday

    with _connect() as conn:
        # 1. Exact date match (one-time)
        row = conn.execute(
            "SELECT name FROM bookings WHERE book_date = ? AND is_recurring = 0",
            (date_str,),
        ).fetchone()
        if row:
            return row[0]

        # 2. Weekly recurring rule
        row = conn.execute(
            "SELECT name FROM bookings"
            " WHERE is_recurring = 1 AND recur_weekday = ?",
            (weekday,),
        ).fetchone()
        return row[0] if row else None


def get_future_bookings(days_ahead: int = 60) -> List[Dict]:
    """Return a date-sorted list of booking dicts for the next *days_ahead* days.

    Each dict contains: ``id``, ``name``, ``date`` (str), ``recurring`` (bool).
    Specific one-time bookings override recurring rules on the same date.
    """
    today    = date.today()
    end_date = today + timedelta(days=days_ahead)

    with _connect() as conn:
        one_time = conn.execute(
            "SELECT id, name, book_date FROM bookings"
            " WHERE is_recurring = 0"
            "   AND book_date BETWEEN ? AND ?"
            " ORDER BY book_date",
            (today.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
        ).fetchall()

        recurring = conn.execute(
            "SELECT id, name, recur_weekday FROM bookings WHERE is_recurring = 1"
        ).fetchall()

    result: Dict[str, Dict] = {}

    for bid, name, book_date in one_time:
        result[book_date] = {
            "id": bid, "name": name,
            "date": book_date, "recurring": False,
        }

    for rec_id, rec_name, weekday in recurring:
        for i in range(days_ahead + 1):
            d = today + timedelta(days=i)
            if d.weekday() == weekday:
                ds = d.strftime("%Y-%m-%d")
                if ds not in result:          # one-time takes precedence
                    result[ds] = {
                        "id": rec_id, "name": rec_name,
                        "date": ds, "recurring": True,
                    }

    return sorted(result.values(), key=lambda x: x["date"])


# ─── Write helpers ────────────────────────────────────────────────────────────

def add_bookings(name: str, dates: List[date]) -> None:
    """Insert one-time bookings for each date in *dates*.

    Any existing one-time booking for the same date is replaced.
    """
    with _connect() as conn:
        for d in dates:
            ds = d.strftime("%Y-%m-%d")
            # Remove any previous one-time booking for this date first.
            conn.execute(
                "DELETE FROM bookings WHERE book_date = ? AND is_recurring = 0",
                (ds,),
            )
            conn.execute(
                "INSERT INTO bookings (name, book_date, is_recurring, recur_weekday)"
                " VALUES (?, ?, 0, -1)",
                (name, ds),
            )
        conn.commit()


def add_recurring_booking(name: str, weekday: int) -> None:
    """Add a weekly recurring booking for *weekday* (0=Monday … 6=Sunday).

    Multiple recurring rules for the same weekday are allowed (different names).
    """
    with _connect() as conn:
        conn.execute(
            "INSERT INTO bookings (name, book_date, is_recurring, recur_weekday)"
            " VALUES (?, NULL, 1, ?)",
            (name, weekday),
        )
        conn.commit()


def delete_booking(booking_id: int) -> None:
    """Delete a booking (one-time or recurring rule) by its primary key."""
    with _connect() as conn:
        conn.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        conn.commit()
