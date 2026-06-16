import os
import json
import tkinter as tk
from tkinter import messagebox

ROOT        = os.path.dirname(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(ROOT, "config.json")

# Colors
BG       = "#0d0f14"
BG2      = "#161920"
BG3      = "#1e2230"
ACCENT   = "#4ECDC4"
DANGER   = "#ff1744"
TEXT     = "#e8eaf6"
TEXT_DIM = "#6b7280"


def _load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


class DashboardTab(tk.Frame):
    def __init__(self, parent, engine, scanner):
        super().__init__(parent, bg=BG)
        self._engine  = engine
        self._scanner = scanner
        self._build()

    def _build(self):
        # Title
        tk.Label(
            self, text="🐾  GUARD_DOG",
            font=("Courier New", 26, "bold"),
            fg=ACCENT, bg=BG
        ).pack(pady=(30, 4))

        tk.Label(
            self, text="Face Recognition Security System",
            font=("Courier New", 10),
            fg=TEXT_DIM, bg=BG
        ).pack()

        # Status card
        card = tk.Frame(self, bg=BG2)
        card.pack(fill="x", padx=40, pady=24)

        self._dot = tk.Label(
            card, text="●",
            font=("Courier New", 20),
            fg=ACCENT, bg=BG2
        )
        self._dot.grid(row=0, column=0, padx=(20, 10), pady=20)

        self._status_lbl = tk.Label(
            card, text="PROTECTION ACTIVE",
            font=("Courier New", 13, "bold"),
            fg=TEXT, bg=BG2
        )
        self._status_lbl.grid(row=0, column=1, sticky="w")

        # Info rows
        self._faces_lbl = tk.Label(
            card, text="",
            font=("Courier New", 10),
            fg=TEXT_DIM, bg=BG2
        )
        self._faces_lbl.grid(row=1, column=0, columnspan=2,
                             sticky="w", padx=20, pady=(0, 4))

        self._owner_lbl = tk.Label(
            card, text="",
            font=("Courier New", 10),
            fg=TEXT_DIM, bg=BG2
        )
        self._owner_lbl.grid(row=2, column=0, columnspan=2,
                             sticky="w", padx=20, pady=(0, 4))

        self._action_lbl = tk.Label(
            card, text="",
            font=("Courier New", 10),
            fg=TEXT_DIM, bg=BG2
        )
        self._action_lbl.grid(row=3, column=0, columnspan=2,
                              sticky="w", padx=20, pady=(0, 16))

        # Buttons
        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame, text="ENABLE",
            font=("Courier New", 10, "bold"),
            bg=ACCENT, fg=BG, relief="flat",
            padx=20, pady=8,
            command=self._enable
        ).pack(side="left", padx=8)

        tk.Button(
            btn_frame, text="DISABLE",
            font=("Courier New", 10, "bold"),
            bg=BG3, fg=TEXT, relief="flat",
            padx=20, pady=8,
            command=self._disable
        ).pack(side="left", padx=8)

        # Welcome message label (hidden by default)
        self._welcome_lbl = tk.Label(
            self, text="",
            font=("Courier New", 12, "bold"),
            fg=ACCENT, bg=BG
        )
        self._welcome_lbl.pack(pady=8)

        self.refresh()

    def refresh(self):
        cfg    = _load_config()
        active = cfg.get("enabled", True)
        owner  = cfg.get("owner", "Not set")
        action = cfg.get("action", "lock")
        faces  = self._engine.list_faces()

        # Update status dot and label
        self._dot.config(fg=ACCENT if active else DANGER)
        self._status_lbl.config(
            text="PROTECTION ACTIVE" if active else "PROTECTION DISABLED",
            fg=TEXT if active else DANGER
        )

        self._faces_lbl.config(
            text=f"  Enrolled faces : {len(faces)} / 10"
        )
        self._owner_lbl.config(
            text=f"  Owner          : {owner}"
        )
        self._action_lbl.config(
            text=f"  Action         : {action.replace('_', ' ').upper()}"
        )

    def show_welcome(self, name: str):
        self._welcome_lbl.config(
            text=f"Welcome back, {name}! 👋"
        )
        # Hide after 5 seconds
        self.after(5000, lambda: self._welcome_lbl.config(text=""))

    def show_intruder_alert(self):
        self._welcome_lbl.config(
            text="⚠️  Intruder detected while you were away!",
            fg=DANGER
        )
        self.after(8000, lambda: self._welcome_lbl.config(
            text="", fg=ACCENT
        ))

    def _enable(self):
        cfg             = _load_config()
        cfg["enabled"]  = True
        with open(CONFIG_PATH, "w") as f:
            json.dump(cfg, f, indent=2)
        self.refresh()

    def _disable(self):
        cfg             = _load_config()
        cfg["enabled"]  = False
        with open(CONFIG_PATH, "w") as f:
            json.dump(cfg, f, indent=2)
        self.refresh()