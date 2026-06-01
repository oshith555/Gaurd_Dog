import os
import json
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

ROOT      = os.path.dirname(os.path.dirname(__file__))
LOGS_FILE = os.path.join(ROOT, "data", "activity_log.json")

# Colors
BG       = "#0d0f14"
BG2      = "#161920"
BG3      = "#1e2230"
ACCENT   = "#00e676"
DANGER   = "#ff1744"
ACCENT2  = "#00b0ff"
TEXT     = "#e8eaf6"
TEXT_DIM = "#6b7280"


def write_log(event_type: str, name: str = None, details: str = ""):
    os.makedirs(os.path.dirname(LOGS_FILE), exist_ok=True)

    logs = _read_logs()
    entry = {
        "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event_type": event_type,
        "name"      : name or "Unknown",
        "details"   : details
    }
    logs.append(entry)

    with open(LOGS_FILE, "w") as f:
        json.dump(logs, f, indent=2)


def _read_logs() -> list:
    if not os.path.exists(LOGS_FILE):
        return []
    try:
        with open(LOGS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def has_intruder_since(timestamp: str) -> bool:
    logs = _read_logs()
    for entry in logs:
        if (entry["event_type"] == "intruder"
                and entry["timestamp"] > timestamp):
            return True
    return False


class LogsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def _build(self):
        # Header
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=30, pady=(20, 8))

        tk.Label(
            header, text="Activity Log",
            font=("Courier New", 16, "bold"),
            fg=ACCENT, bg=BG
        ).pack(side="left")

        tk.Button(
            header, text="REFRESH",
            font=("Courier New", 9, "bold"),
            bg=BG3, fg=TEXT, relief="flat",
            padx=12, pady=4,
            command=self._refresh
        ).pack(side="right")

        tk.Button(
            header, text="CLEAR ALL",
            font=("Courier New", 9, "bold"),
            bg=DANGER, fg="#fff", relief="flat",
            padx=12, pady=4,
            command=self._clear_all
        ).pack(side="right", padx=6)

        # Filter buttons
        filter_frame = tk.Frame(self, bg=BG)
        filter_frame.pack(fill="x", padx=30, pady=(0, 8))

        tk.Label(
            filter_frame, text="Filter:",
            font=("Courier New", 9),
            fg=TEXT_DIM, bg=BG
        ).pack(side="left", padx=(0, 8))

        self._filter_var = tk.StringVar(value="all")

        for label, value in [
            ("All", "all"),
            ("Owner", "owner"),
            ("Authorized", "authorized"),
            ("Intruder", "intruder")
        ]:
            tk.Radiobutton(
                filter_frame, text=label,
                variable=self._filter_var,
                value=value,
                bg=BG, fg=TEXT_DIM,
                selectcolor=BG3,
                activebackground=BG,
                activeforeground=ACCENT,
                font=("Courier New", 9),
                command=self._refresh
            ).pack(side="left", padx=6)

        # Log list
        list_frame = tk.Frame(self, bg=BG2)
        list_frame.pack(fill="both", expand=True, padx=30, pady=8)

        self._listbox = tk.Listbox(
            list_frame,
            bg=BG2, fg=TEXT,
            selectbackground=BG3,
            selectforeground=ACCENT,
            font=("Courier New", 10),
            bd=0, highlightthickness=0,
            activestyle="none"
        )
        sb = tk.Scrollbar(
            list_frame, orient="vertical",
            command=self._listbox.yview
        )
        self._listbox.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._listbox.pack(
            fill="both", expand=True, padx=6, pady=6
        )

        self._count_lbl = tk.Label(
            self, text="",
            font=("Courier New", 9),
            fg=TEXT_DIM, bg=BG
        )
        self._count_lbl.pack(pady=(0, 8))

        self._refresh()

    def _refresh(self):
        self._listbox.delete(0, tk.END)
        logs   = _read_logs()
        filter = self._filter_var.get()

        if filter != "all":
            logs = [l for l in logs if l["event_type"] == filter]

        logs.reverse()

        if not logs:
            self._listbox.insert(tk.END, "  (no activity yet)")
            self._count_lbl.config(text="")
            return

        for entry in logs:
            event = entry["event_type"]
            name  = entry["name"]
            time  = entry["timestamp"]

            if event == "owner":
                icon  = "👑"
                color = ACCENT
            elif event == "authorized":
                icon  = "✓"
                color = ACCENT2
            elif event == "intruder":
                icon  = "⚠"
                color = DANGER
            else:
                icon  = "•"
                color = TEXT_DIM

            self._listbox.insert(
                tk.END,
                f"  {icon}  {time}   {name.upper()}"
            )

        self._count_lbl.config(
            text=f"{len(logs)} event(s) shown"
        )

    def _clear_all(self):
        if not _read_logs():
            return
        if messagebox.askyesno(
            "Guard_Dog", "Clear all activity logs?"
        ):
            with open(LOGS_FILE, "w") as f:
                json.dump([], f)
            self._refresh()