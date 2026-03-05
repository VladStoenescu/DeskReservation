#!/usr/bin/env python3
"""Desk Reservation App — Raspberry Pi 7″ touchscreen edition.

Run with:
    python3 main.py              # windowed (development)
    python3 main.py --fullscreen # fullscreen kiosk mode (Raspberry Pi)
"""

import sys
import calendar
from datetime import date, timedelta
from typing import Dict, List, Optional, Set

import tkinter as tk
from tkinter import messagebox

from database import (
    init_db,
    get_booking_for_date,
    add_bookings,
    add_recurring_booking,
    get_future_bookings,
    delete_booking,
)

# ─── Layout ───────────────────────────────────────────────────────────────────
SCREEN_W = 800
SCREEN_H = 480

# ─── Colour palette (dark GitHub-inspired) ────────────────────────────────────
C_BG      = "#0d1117"
C_CARD    = "#161b22"
C_HEADER  = "#21262d"
C_BORDER  = "#30363d"
C_TEXT    = "#e6edf3"
C_SUBTEXT = "#8b949e"
C_FREE    = "#2ea043"    # green  – desk available
C_BOOKED  = "#da3633"    # red    – desk taken
C_ACCENT  = "#1f6feb"    # blue   – selected / primary action
C_WARN    = "#d29922"    # amber  – recurring
C_BTN     = "#21262d"
C_BTN_H   = "#30363d"

# ─── Typography ───────────────────────────────────────────────────────────────
F_HUGE  = ("Helvetica", 28, "bold")
F_TITLE = ("Helvetica", 17, "bold")
F_LARGE = ("Helvetica", 14, "bold")
F_MED   = ("Helvetica", 12)
F_MEDB  = ("Helvetica", 12, "bold")
F_SMALL = ("Helvetica", 10)

# ─── Weekday names ────────────────────────────────────────────────────────────
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEEKDAY_SHORT = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]


# ─── Reusable widget factories ────────────────────────────────────────────────

def _btn(parent: tk.Widget, text: str, cmd, *,
         bg: str = C_BTN, fg: str = C_TEXT, font=F_MED,
         padx: int = 12, pady: int = 7, **kw) -> tk.Button:
    return tk.Button(
        parent, text=text, command=cmd,
        bg=bg, fg=fg, font=font,
        activebackground=C_BTN_H, activeforeground=C_TEXT,
        relief=tk.FLAT, cursor="hand2",
        padx=padx, pady=pady, **kw,
    )


def _lbl(parent: tk.Widget, text: str, *,
         bg: str = C_BG, fg: str = C_TEXT, font=F_MED, **kw) -> tk.Label:
    return tk.Label(parent, text=text, bg=bg, fg=fg, font=font, **kw)


# ══════════════════════════════════════════════════════════════════════════════
# On-screen keyboard (Toplevel modal)
# ══════════════════════════════════════════════════════════════════════════════

class OnScreenKeyboard(tk.Toplevel):
    """Full-width on-screen QWERTY keyboard for name entry."""

    _ROWS = [
        list("1234567890"),
        list("QWERTYUIOP"),
        list("ASDFGHJKL"),
        list("ZXCVBNM"),
    ]

    def __init__(self, parent: tk.Widget, initial_text: str = "",
                 title: str = "Enter your name") -> None:
        super().__init__(parent)
        self.title(title)
        self.configure(bg=C_BG)
        self.geometry(f"{SCREEN_W}x{SCREEN_H}+0+0")
        self.resizable(False, False)
        self.grab_set()

        self._text = tk.StringVar(value=initial_text)
        self.result: Optional[str] = None
        self._build()

    # ── public ────────────────────────────────────────────────────────────────

    @classmethod
    def ask(cls, parent: tk.Widget,
            initial_text: str = "",
            title: str = "Enter your name") -> Optional[str]:
        """Show the keyboard and block until DONE/Cancel.  Returns the entered
        text (stripped) or ``None`` if the user cancelled."""
        kb = cls(parent, initial_text, title)
        parent.wait_window(kb)
        return kb.result

    # ── private ───────────────────────────────────────────────────────────────

    def _build(self) -> None:
        # ── title bar ──
        bar = tk.Frame(self, bg=C_HEADER, height=46)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)
        _lbl(bar, "Enter your name", bg=C_HEADER, fg=C_TEXT,
             font=F_TITLE).pack(side=tk.LEFT, padx=14)
        _btn(bar, "✕  Cancel", self.destroy,
             bg=C_HEADER, fg=C_SUBTEXT, font=F_MED, padx=10, pady=4
             ).pack(side=tk.RIGHT, padx=8)

        # ── text display ──
        disp = tk.Frame(self, bg=C_CARD, height=60)
        disp.pack(fill=tk.X, padx=8, pady=(6, 4))
        disp.pack_propagate(False)
        tk.Label(
            disp, textvariable=self._text,
            bg=C_CARD, fg=C_TEXT, font=F_HUGE,
            anchor="w",
        ).pack(fill=tk.BOTH, expand=True, padx=14)

        # ── key rows ──
        key_area = tk.Frame(self, bg=C_BG)
        key_area.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        for row_chars in self._ROWS:
            row = tk.Frame(key_area, bg=C_BG)
            row.pack(fill=tk.X, pady=2)
            for ch in row_chars:
                tk.Button(
                    row, text=ch, font=F_LARGE,
                    bg=C_BTN, fg=C_TEXT,
                    activebackground=C_ACCENT, activeforeground=C_TEXT,
                    relief=tk.FLAT, cursor="hand2",
                    width=4, height=2,
                    command=lambda c=ch: self._press(c),
                ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # ── bottom action row ──
        bot = tk.Frame(key_area, bg=C_BG)
        bot.pack(fill=tk.X, pady=2)

        tk.Button(
            bot, text="SPACE", font=F_MEDB,
            bg=C_BTN, fg=C_TEXT,
            activebackground=C_ACCENT, activeforeground=C_TEXT,
            relief=tk.FLAT, cursor="hand2", height=2,
            command=lambda: self._press(" "),
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        tk.Button(
            bot, text="⌫  DEL", font=F_MEDB,
            bg=C_WARN, fg=C_TEXT,
            activebackground="#c0851a", activeforeground=C_TEXT,
            relief=tk.FLAT, cursor="hand2", height=2,
            command=self._backspace,
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        tk.Button(
            bot, text="✓  DONE", font=F_MEDB,
            bg=C_FREE, fg=C_TEXT,
            activebackground="#27913c", activeforeground=C_TEXT,
            relief=tk.FLAT, cursor="hand2", height=2,
            command=self._done,
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

    def _press(self, ch: str) -> None:
        self._text.set(self._text.get() + ch)

    def _backspace(self) -> None:
        val = self._text.get()
        if val:
            self._text.set(val[:-1])

    def _done(self) -> None:
        name = self._text.get().strip()
        if not name:
            messagebox.showwarning("No name", "Please enter a name.", parent=self)
            return
        self.result = name
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
# Calendar widget
# ══════════════════════════════════════════════════════════════════════════════

class CalendarWidget(tk.Frame):
    """Interactive monthly calendar.

    * Click a future day to select / deselect it.
    * Already-booked days are shown in red (still selectable to override).
    * Past days are greyed out and disabled.
    """

    _DAY_W = 54   # cell width
    _DAY_H = 40   # cell height

    def __init__(self, parent: tk.Widget,
                 selected: Optional[Set[date]] = None,
                 on_change=None, **kw) -> None:
        super().__init__(parent, bg=C_CARD, **kw)
        self.selected: Set[date] = selected if selected is not None else set()
        self._on_change   = on_change   # callable() invoked after each toggle
        self._today       = date.today()
        self._view_year   = self._today.year
        self._view_month  = self._today.month
        self._render()

    # ── public ────────────────────────────────────────────────────────────────

    def get_selected(self) -> List[date]:
        return sorted(self.selected)

    # ── private ───────────────────────────────────────────────────────────────

    def _render(self) -> None:
        for w in self.winfo_children():
            w.destroy()

        # Month navigation header
        nav = tk.Frame(self, bg=C_CARD)
        nav.pack(fill=tk.X, pady=(4, 2))
        _btn(nav, "◄", self._prev_month,
             bg=C_CARD, padx=10, pady=4, font=F_LARGE).pack(side=tk.LEFT, padx=4)
        _lbl(nav,
             f"{calendar.month_name[self._view_month]}  {self._view_year}",
             bg=C_CARD, fg=C_TEXT, font=F_LARGE).pack(side=tk.LEFT, expand=True)
        _btn(nav, "►", self._next_month,
             bg=C_CARD, padx=10, pady=4, font=F_LARGE).pack(side=tk.RIGHT, padx=4)

        # Day-name labels
        names_row = tk.Frame(self, bg=C_CARD)
        names_row.pack(fill=tk.X)
        for dn in WEEKDAY_SHORT:
            tk.Label(
                names_row, text=dn, bg=C_CARD, fg=C_SUBTEXT,
                font=F_SMALL, width=5, anchor="center",
            ).pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Separator
        tk.Frame(self, bg=C_BORDER, height=1).pack(fill=tk.X)

        # Day grid
        grid = tk.Frame(self, bg=C_CARD)
        grid.pack(fill=tk.BOTH, expand=True)

        cal_weeks = calendar.monthcalendar(self._view_year, self._view_month)
        for week in cal_weeks:
            row_frame = tk.Frame(grid, bg=C_CARD)
            row_frame.pack(fill=tk.X)
            for day_num in week:
                if day_num == 0:
                    tk.Label(row_frame, text="", bg=C_CARD,
                             width=5, height=2).pack(
                        side=tk.LEFT, expand=True, fill=tk.X)
                    continue

                d = date(self._view_year, self._view_month, day_num)
                is_past     = d < self._today
                is_selected = d in self.selected
                booked_name = get_booking_for_date(d) if not is_past else None

                if is_past:
                    bg, fg, state = C_BORDER, C_SUBTEXT, tk.DISABLED
                elif is_selected:
                    bg, fg, state = C_ACCENT, C_TEXT, tk.NORMAL
                elif booked_name:
                    bg, fg, state = C_BOOKED, C_TEXT, tk.NORMAL
                else:
                    bg, fg, state = C_BTN, C_TEXT, tk.NORMAL

                tk.Button(
                    row_frame, text=str(day_num),
                    bg=bg, fg=fg,
                    font=F_MEDB if is_selected else F_SMALL,
                    relief=tk.FLAT,
                    width=5, height=2,
                    state=state,
                    cursor="hand2" if state == tk.NORMAL else "arrow",
                    command=lambda _d=d: self._toggle(_d),
                ).pack(side=tk.LEFT, expand=True, fill=tk.X)

    def _toggle(self, d: date) -> None:
        if d in self.selected:
            self.selected.discard(d)
        else:
            self.selected.add(d)
        self._render()
        if self._on_change is not None:
            self._on_change()

    def _prev_month(self) -> None:
        if self._view_month == 1:
            self._view_month, self._view_year = 12, self._view_year - 1
        else:
            self._view_month -= 1
        self._render()

    def _next_month(self) -> None:
        if self._view_month == 12:
            self._view_month, self._view_year = 1, self._view_year + 1
        else:
            self._view_month += 1
        self._render()


# ══════════════════════════════════════════════════════════════════════════════
# Screen base class
# ══════════════════════════════════════════════════════════════════════════════

class _Screen(tk.Frame):
    def __init__(self, parent: tk.Widget, app: "DeskReservationApp") -> None:
        super().__init__(parent, bg=C_BG)
        self.app = app

    def _make_header(self, title: str,
                     back_cmd=None) -> tk.Frame:
        bar = tk.Frame(self, bg=C_HEADER, height=52)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        _lbl(bar, title, bg=C_HEADER, fg=C_TEXT,
             font=F_TITLE).pack(side=tk.LEFT, padx=16)
        if back_cmd:
            _btn(bar, "← Back", back_cmd,
                 bg=C_HEADER, font=F_MED,
                 padx=10, pady=4).pack(side=tk.RIGHT, padx=8)
        return bar


# ══════════════════════════════════════════════════════════════════════════════
# Main screen
# ══════════════════════════════════════════════════════════════════════════════

class MainScreen(_Screen):
    def __init__(self, parent: tk.Widget, app: "DeskReservationApp") -> None:
        super().__init__(parent, app)
        self._build()

    def refresh(self) -> None:
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def _build(self) -> None:
        # ── header ──
        bar = self._make_header("🖥  Desk Reservation")
        _btn(bar, "ℹ  Info", self.app.show_info,
             bg=C_HEADER, font=F_SMALL, padx=8, pady=4
             ).pack(side=tk.RIGHT, padx=4)
        _btn(bar, "📋  Bookings", self.app.show_bookings_list,
             bg=C_HEADER, font=F_SMALL, padx=8, pady=4
             ).pack(side=tk.RIGHT, padx=4)

        # ── body ──
        body = tk.Frame(self, bg=C_BG)
        body.pack(fill=tk.BOTH, expand=True)

        today   = date.today()
        booker  = get_booking_for_date(today)
        day_str = today.strftime("%A, %d %B %Y").replace(" 0", " ")

        _lbl(body, day_str, bg=C_BG, fg=C_SUBTEXT,
             font=F_LARGE).pack(pady=(28, 10))

        # Status card
        if booker:
            card = tk.Frame(body, bg=C_BOOKED, pady=18, padx=50)
            card.pack(pady=6)
            _lbl(card, "● DESK IS BOOKED",
                 bg=C_BOOKED, fg=C_TEXT, font=F_TITLE).pack()
            _lbl(card, booker,
                 bg=C_BOOKED, fg=C_TEXT, font=F_HUGE).pack(pady=(6, 0))
        else:
            card = tk.Frame(body, bg=C_FREE, pady=18, padx=50)
            card.pack(pady=6)
            _lbl(card, "● DESK IS FREE",
                 bg=C_FREE, fg=C_TEXT, font=F_HUGE).pack()

        # Book button
        _btn(body, "  📅  BOOK THIS DESK  ", self.app.show_booking,
             bg=C_ACCENT, fg=C_TEXT, font=F_TITLE,
             padx=30, pady=14).pack(pady=20)


# ══════════════════════════════════════════════════════════════════════════════
# Booking screen
# ══════════════════════════════════════════════════════════════════════════════

class BookingScreen(_Screen):
    """Booking form with two modes: one-time (calendar) and recurring (weekdays)."""

    def __init__(self, parent: tk.Widget, app: "DeskReservationApp") -> None:
        super().__init__(parent, app)
        self._name: str = ""
        self._mode = tk.StringVar(value="onetime")   # "onetime" | "recurring"
        self._cal: Optional[CalendarWidget] = None
        self._wd_vars: List[tk.BooleanVar] = [tk.BooleanVar() for _ in range(7)]
        self._build()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build(self) -> None:
        # ── header ──
        self._make_header("📅  New Booking", back_cmd=self.app.show_main)

        # ── name row ──
        name_row = tk.Frame(self, bg=C_CARD, height=56)
        name_row.pack(fill=tk.X, padx=8, pady=(6, 0))
        name_row.pack_propagate(False)

        _lbl(name_row, "Name:", bg=C_CARD, fg=C_SUBTEXT,
             font=F_MEDB).pack(side=tk.LEFT, padx=(14, 6))

        self._name_lbl = _lbl(
            name_row,
            self._name if self._name else "tap to enter ▼",
            bg=C_CARD,
            fg=C_TEXT if self._name else C_SUBTEXT,
            font=F_LARGE,
        )
        self._name_lbl.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self._name_lbl.bind("<Button-1>", lambda _e: self._ask_name())

        _btn(name_row, "✏", self._ask_name,
             bg=C_BTN, font=F_LARGE, padx=10, pady=4
             ).pack(side=tk.RIGHT, padx=8)

        # ── mode toggle ──
        toggle = tk.Frame(self, bg=C_BG)
        toggle.pack(fill=tk.X, padx=8, pady=(6, 0))

        tk.Radiobutton(
            toggle, text="One-time dates", variable=self._mode,
            value="onetime",
            bg=C_BG, fg=C_TEXT, selectcolor=C_CARD,
            font=F_MEDB, activebackground=C_BG,
            command=self._refresh_mode,
        ).pack(side=tk.LEFT, padx=(8, 20))
        tk.Radiobutton(
            toggle, text="Repeat weekly", variable=self._mode,
            value="recurring",
            bg=C_BG, fg=C_TEXT, selectcolor=C_CARD,
            font=F_MEDB, activebackground=C_BG,
            command=self._refresh_mode,
        ).pack(side=tk.LEFT)

        # ── content area (swapped by mode) ──
        self._content = tk.Frame(self, bg=C_BG)
        self._content.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        self._refresh_mode()

    def _refresh_mode(self) -> None:
        for w in self._content.winfo_children():
            w.destroy()

        if self._mode.get() == "onetime":
            self._build_onetime()
        else:
            self._build_recurring()

    def _build_onetime(self) -> None:
        """Left: calendar.  Right: summary + save."""
        left = tk.Frame(self._content, bg=C_BG)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._cal = CalendarWidget(left, on_change=self._update_summary)
        self._cal.pack(fill=tk.BOTH, expand=True)

        right = tk.Frame(self._content, bg=C_BG, width=200)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(12, 0))
        right.pack_propagate(False)

        self._summary_lbl = _lbl(right, "No days selected",
                                 bg=C_BG, fg=C_SUBTEXT, font=F_SMALL)
        self._summary_lbl.pack(pady=(20, 0))
        # Show initial (empty) summary
        self._update_summary()

        _btn(right, "✓  Save Booking", self._save_onetime,
             bg=C_FREE, fg=C_TEXT, font=F_MEDB,
             padx=12, pady=10).pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 8))

    def _build_recurring(self) -> None:
        """Weekday checkboxes + save."""
        frm = tk.Frame(self._content, bg=C_BG)
        frm.pack(expand=True)

        _lbl(frm, "Select weekday(s) to repeat every week:",
             bg=C_BG, fg=C_SUBTEXT, font=F_MEDB).pack(pady=(16, 10))

        wd_frame = tk.Frame(frm, bg=C_BG)
        wd_frame.pack()
        for i, day_name in enumerate(WEEKDAYS):
            cb = tk.Checkbutton(
                wd_frame, text=day_name, variable=self._wd_vars[i],
                bg=C_BG, fg=C_TEXT, selectcolor=C_CARD,
                font=F_MED, activebackground=C_BG,
            )
            cb.pack(anchor=tk.W, pady=2)

        _btn(frm, "✓  Save Recurring Booking", self._save_recurring,
             bg=C_WARN, fg=C_TEXT, font=F_MEDB,
             padx=12, pady=10).pack(pady=20)

    # ── actions ───────────────────────────────────────────────────────────────

    def _ask_name(self) -> None:
        name = OnScreenKeyboard.ask(self, initial_text=self._name)
        if name is not None:
            self._name = name
            self._name_lbl.config(text=name, fg=C_TEXT)

    def _update_summary(self) -> None:
        if self._cal is None:
            return
        n = len(self._cal.get_selected())
        if n == 0:
            self._summary_lbl.config(text="No days selected", fg=C_SUBTEXT)
        elif n == 1:
            d = self._cal.get_selected()[0]
            self._summary_lbl.config(
                text=f"1 day selected:\n{d.strftime('%d %b %Y')}",
                fg=C_TEXT)
        else:
            self._summary_lbl.config(text=f"{n} days selected", fg=C_TEXT)

    def _save_onetime(self) -> None:
        if not self._name:
            messagebox.showwarning("No name",
                                   "Please enter your name first.", parent=self)
            return
        if self._cal is None or not self._cal.get_selected():
            messagebox.showwarning("No days",
                                   "Please select at least one day.", parent=self)
            return

        dates = self._cal.get_selected()
        add_bookings(self._name, dates)
        messagebox.showinfo("Booking saved",
                            f"Booked {len(dates)} day(s) for {self._name}.",
                            parent=self)
        self.app.show_main()

    def _save_recurring(self) -> None:
        if not self._name:
            messagebox.showwarning("No name",
                                   "Please enter your name first.", parent=self)
            return
        chosen = [i for i, v in enumerate(self._wd_vars) if v.get()]
        if not chosen:
            messagebox.showwarning("No weekdays",
                                   "Please select at least one weekday.", parent=self)
            return

        for wd in chosen:
            add_recurring_booking(self._name, wd)

        day_names = ", ".join(WEEKDAYS[i] for i in chosen)
        messagebox.showinfo(
            "Recurring booking saved",
            f"Booked every {day_names} for {self._name}.",
            parent=self,
        )
        self.app.show_main()


# ══════════════════════════════════════════════════════════════════════════════
# Bookings list screen
# ══════════════════════════════════════════════════════════════════════════════

class BookingsListScreen(_Screen):
    def __init__(self, parent: tk.Widget, app: "DeskReservationApp") -> None:
        super().__init__(parent, app)
        self._build()

    def _build(self) -> None:
        self._make_header("📋  Upcoming Bookings", back_cmd=self.app.show_main)

        container = tk.Frame(self, bg=C_BG)
        container.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        # Scrollable canvas
        canvas = tk.Canvas(container, bg=C_BG, highlightthickness=0)
        scroll = tk.Scrollbar(container, orient=tk.VERTICAL,
                              command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)

        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner = tk.Frame(canvas, bg=C_BG)
        inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_configure(_e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(inner_id, width=canvas.winfo_width())

        inner.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", _on_configure)

        bookings = get_future_bookings()
        if not bookings:
            _lbl(inner, "No upcoming bookings.",
                 bg=C_BG, fg=C_SUBTEXT, font=F_MED).pack(pady=20)
            return

        today_str = date.today().strftime("%Y-%m-%d")
        for bk in bookings:
            row = tk.Frame(inner, bg=C_CARD, pady=8)
            row.pack(fill=tk.X, padx=4, pady=3)

            colour = C_BOOKED if bk["date"] == today_str else C_TEXT
            tag    = "  ↺ " if bk["recurring"] else "  📌 "

            _lbl(row, tag + bk["date"],
                 bg=C_CARD, fg=C_SUBTEXT, font=F_SMALL).pack(side=tk.LEFT, padx=8)
            _lbl(row, bk["name"],
                 bg=C_CARD, fg=colour, font=F_MEDB).pack(side=tk.LEFT, padx=4)

            if bk["recurring"]:
                _lbl(row, "(recurring)",
                     bg=C_CARD, fg=C_WARN, font=F_SMALL).pack(side=tk.LEFT, padx=4)

            _btn(row, "✕", lambda bid=bk["id"]: self._delete(bid),
                 bg=C_BOOKED, fg=C_TEXT, font=F_SMALL,
                 padx=8, pady=2).pack(side=tk.RIGHT, padx=8)

    def _delete(self, booking_id: int) -> None:
        if messagebox.askyesno("Delete booking",
                               "Delete this booking?", parent=self):
            delete_booking(booking_id)
            for w in self.winfo_children():
                w.destroy()
            self._build()


# ══════════════════════════════════════════════════════════════════════════════
# Info / help screen
# ══════════════════════════════════════════════════════════════════════════════

class InfoScreen(_Screen):
    def __init__(self, parent: tk.Widget, app: "DeskReservationApp") -> None:
        super().__init__(parent, app)
        self._build()

    def _build(self) -> None:
        self._make_header("ℹ  How to Use", back_cmd=self.app.show_main)

        body = tk.Frame(self, bg=C_BG)
        body.pack(fill=tk.BOTH, expand=True, padx=24, pady=12)

        lines = [
            ("📋  Main screen", F_LARGE, C_TEXT),
            ("  Shows today's date and whether the desk is free (green) or", F_MED, C_SUBTEXT),
            ("  booked (red with the booker's name displayed).", F_MED, C_SUBTEXT),
            ("", F_SMALL, C_BG),
            ("📅  Booking a desk — one-time", F_LARGE, C_TEXT),
            ("  1. Tap  BOOK THIS DESK  on the home screen.", F_MED, C_SUBTEXT),
            ("  2. Tap the name bar and type your name on the on-screen keyboard.", F_MED, C_SUBTEXT),
            ("  3. Select the days you want in the calendar (tap to toggle).", F_MED, C_SUBTEXT),
            ("  4. Tap  Save Booking  to confirm.", F_MED, C_SUBTEXT),
            ("", F_SMALL, C_BG),
            ("🔁  Booking a desk — recurring (every week)", F_LARGE, C_TEXT),
            ("  1. Tap  BOOK THIS DESK  →  switch to  Repeat weekly  mode.", F_MED, C_SUBTEXT),
            ("  2. Enter your name, tick the weekday(s), tap  Save Recurring Booking.", F_MED, C_SUBTEXT),
            ("", F_SMALL, C_BG),
            ("🗑  Cancelling a booking", F_LARGE, C_TEXT),
            ("  Tap  Bookings  in the header, then tap the  ✕  button next to the", F_MED, C_SUBTEXT),
            ("  booking you want to remove.", F_MED, C_SUBTEXT),
        ]

        for text, font, fg in lines:
            _lbl(body, text, bg=C_BG, fg=fg, font=font,
                 anchor="w").pack(fill=tk.X, pady=1)


# ══════════════════════════════════════════════════════════════════════════════
# Application controller
# ══════════════════════════════════════════════════════════════════════════════

class DeskReservationApp:
    def __init__(self, root: tk.Tk, fullscreen: bool = False) -> None:
        self.root = root
        self.root.title("Desk Reservation")
        self.root.geometry(f"{SCREEN_W}x{SCREEN_H}")
        self.root.configure(bg=C_BG)
        self.root.resizable(False, False)

        if fullscreen:
            self.root.attributes("-fullscreen", True)
            self.root.bind("<Escape>", lambda _e: self.root.attributes("-fullscreen", False))

        self._frame: Optional[tk.Frame] = None
        self.show_main()
        self._auto_refresh()

    # ── navigation ────────────────────────────────────────────────────────────

    def _switch(self, cls, *args, **kwargs) -> None:
        if self._frame is not None:
            self._frame.destroy()
        self._frame = cls(self.root, self, *args, **kwargs)
        self._frame.pack(fill=tk.BOTH, expand=True)

    def show_main(self)         -> None: self._switch(MainScreen)
    def show_booking(self)      -> None: self._switch(BookingScreen)
    def show_bookings_list(self)-> None: self._switch(BookingsListScreen)
    def show_info(self)         -> None: self._switch(InfoScreen)

    # ── auto refresh ──────────────────────────────────────────────────────────

    def _auto_refresh(self) -> None:
        if isinstance(self._frame, MainScreen):
            self._frame.refresh()
        self.root.after(60_000, self._auto_refresh)   # every 60 s


# ══════════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    init_db()
    fullscreen = "--fullscreen" in sys.argv
    root = tk.Tk()
    DeskReservationApp(root, fullscreen=fullscreen)
    root.mainloop()


if __name__ == "__main__":
    main()
