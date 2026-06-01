import os
import json
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog

ROOT        = os.path.dirname(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(ROOT, "config.json")

# Colors
BG       = "#0d0f14"
BG2      = "#161920"
BG3      = "#1e2230"
ACCENT   = "#00e676"
DANGER   = "#ff1744"
ACCENT2  = "#00b0ff"
TEXT     = "#e8eaf6"
TEXT_DIM = "#6b7280"


def _load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def _save_config(cfg: dict):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


class SettingsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._vars        = {}
        self._blocked_apps = []
        self._build()

    def _build(self):
        tk.Label(
            self, text="Settings",
            font=("Courier New", 16, "bold"),
            fg=ACCENT, bg=BG
        ).pack(pady=(20, 16))

        # Scrollable content
        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True, padx=30)

        # ── Action section ─────────────────────────────────────
        self._section(container, "ON INTRUDER DETECTION")

        action_frame = tk.Frame(container, bg=BG2)
        action_frame.pack(fill="x", pady=(0, 12))

        self._action_var = tk.StringVar()
        for label, value in [
            ("Lock Screen",  "lock"),
            ("Block Apps",   "block_apps")
        ]:
            tk.Radiobutton(
                action_frame, text=label,
                variable=self._action_var,
                value=value,
                bg=BG2, fg=TEXT,
                selectcolor=BG3,
                activebackground=BG2,
                activeforeground=ACCENT,
                font=("Courier New", 10),
                command=self._toggle_apps_section
            ).pack(side="left", padx=16, pady=10)

        # ── Block apps section ─────────────────────────────────
        self._apps_frame = tk.Frame(container, bg=BG2)
        self._apps_frame.pack(fill="x", pady=(0, 12))

        tk.Label(
            self._apps_frame,
            text="Apps to block (e.g. chrome.exe, notepad.exe):",
            font=("Courier New", 9),
            fg=TEXT_DIM, bg=BG2
        ).pack(anchor="w", padx=12, pady=(8, 4))

        input_row = tk.Frame(self._apps_frame, bg=BG2)
        input_row.pack(fill="x", padx=12, pady=(0, 8))

        self._app_entry_var = tk.StringVar()
        tk.Entry(
            input_row,
            textvariable=self._app_entry_var,
            bg=BG3, fg=TEXT,
            insertbackground=ACCENT,
            font=("Courier New", 10),
            relief="flat",
            highlightthickness=1,
            highlightcolor=ACCENT,
            highlightbackground=BG3,
            width=24
        ).pack(side="left", ipady=4, padx=(0, 8))

        tk.Button(
            input_row, text="ADD",
            font=("Courier New", 9, "bold"),
            bg=ACCENT2, fg=BG, relief="flat",
            padx=10, pady=4,
            command=self._add_app
        ).pack(side="left", padx=(0, 6))

        tk.Button(
            input_row, text="REMOVE",
            font=("Courier New", 9, "bold"),
            bg=DANGER, fg="#fff", relief="flat",
            padx=10, pady=4,
            command=self._remove_app
        ).pack(side="left")

        self._apps_listbox = tk.Listbox(
            self._apps_frame,
            bg=BG3, fg=TEXT,
            selectbackground=BG2,
            selectforeground=ACCENT,
            font=("Courier New", 10),
            bd=0, highlightthickness=0,
            height=4
        )
        self._apps_listbox.pack(
            fill="x", padx=12, pady=(0, 8)
        )

        # ── Timing section ─────────────────────────────────────
        self._section(container, "TIMING")

        timing_frame = tk.Frame(container, bg=BG2)
        timing_frame.pack(fill="x", pady=(0, 12))

        self._add_slider(
            timing_frame,
            "Idle time before trigger (minutes):",
            "idle_time_minutes", 1, 30, 1
        )
        self._add_slider(
            timing_frame,
            "Match tolerance (lower = stricter):",
            "tolerance", 0.3, 0.8, 0.05
        )
        self._add_slider(
            timing_frame,
            "Camera index:",
            "camera_index", 0, 5, 1
        )

        # ── Startup section ────────────────────────────────────
        self._section(container, "SYSTEM")

        system_frame = tk.Frame(container, bg=BG2)
        system_frame.pack(fill="x", pady=(0, 12))

        self._startup_var = tk.BooleanVar()
        tk.Checkbutton(
            system_frame,
            text="Start Guard_Dog when Windows boots",
            variable=self._startup_var,
            bg=BG2, fg=TEXT,
            selectcolor=BG3,
            activebackground=BG2,
            activeforeground=ACCENT,
            font=("Courier New", 10)
        ).pack(anchor="w", padx=16, pady=10)

        # ── Save button ────────────────────────────────────────
        tk.Button(
            self, text="SAVE SETTINGS",
            font=("Courier New", 11, "bold"),
            bg=ACCENT, fg=BG, relief="flat",
            padx=24, pady=10,
            command=self._save
        ).pack(pady=16)

        self._msg_lbl = tk.Label(
            self, text="",
            font=("Courier New", 10),
            fg=ACCENT, bg=BG
        )
        self._msg_lbl.pack()

        self._load_into_ui()

    def _section(self, parent, title: str):
        tk.Label(
            parent, text=title,
            font=("Courier New", 8, "bold"),
            fg=TEXT_DIM, bg=BG
        ).pack(anchor="w", pady=(8, 2))

    def _add_slider(self, parent, label, key,
                    from_, to_, resolution):
        row = tk.Frame(parent, bg=BG2)
        row.pack(fill="x", padx=12, pady=6)

        tk.Label(
            row, text=label,
            font=("Courier New", 9),
            fg=TEXT, bg=BG2, width=38, anchor="w"
        ).pack(side="left")

        var = tk.DoubleVar()
        self._vars[key] = var

        val_lbl = tk.Label(
            row, textvariable=var,
            font=("Courier New", 9),
            fg=ACCENT, bg=BG2, width=5
        )
        val_lbl.pack(side="right")

        tk.Scale(
            row, from_=from_, to=to_,
            variable=var, orient="horizontal",
            resolution=resolution, length=160,
            bg=BG2, fg=TEXT,
            troughcolor=BG3,
            highlightthickness=0,
            showvalue=False
        ).pack(side="right", padx=8)

    def _toggle_apps_section(self):
        if self._action_var.get() == "block_apps":
            self._apps_frame.pack(fill="x", pady=(0, 12))
        else:
            self._apps_frame.pack_forget()

    def _add_app(self):
        import subprocess
        path = filedialog.askopenfilename(
            title="Select App to Block",
            filetypes=[("Executables", "*.exe"), ("All files", "*.*")]
        )
        if not path:
            return
        app = os.path.basename(path)
        if app not in self._blocked_apps:
            self._blocked_apps.append(app)
            self._apps_listbox.insert(tk.END, f"  {app}")

    def _remove_app(self):
        sel = self._apps_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        self._apps_listbox.delete(idx)
        self._blocked_apps.pop(idx)

    def _load_into_ui(self):
        cfg = _load_config()

        self._action_var.set(cfg.get("action", "lock"))
        self._startup_var.set(
            cfg.get("startup_with_windows", False)
        )

        for key, var in self._vars.items():
            var.set(cfg.get(key, 0))

        self._blocked_apps = cfg.get("blocked_apps", [])
        self._apps_listbox.delete(0, tk.END)
        for app in self._blocked_apps:
            self._apps_listbox.insert(tk.END, f"  {app}")

        self._toggle_apps_section()

    def _set_startup(self, enable: bool):
        app_path = os.path.join(ROOT, "main.py")
        key_name = "Guard_Dog"
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            if enable:
                python_path = os.path.join(
                    ROOT, "venv", "Scripts", "pythonw.exe"
                )
                winreg.SetValueEx(
                    key, key_name, 0,
                    winreg.REG_SZ,
                    f'"{python_path}" "{app_path}"'
                )
            else:
                try:
                    winreg.DeleteValue(key, key_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            print(f"[Settings] Startup error: {e}")

    def _save(self):
        cfg = _load_config()

        cfg["action"]               = self._action_var.get()
        cfg["blocked_apps"]         = self._blocked_apps
        cfg["startup_with_windows"] = self._startup_var.get()

        for key, var in self._vars.items():
            val = var.get()
            if key in ("idle_time_minutes", "camera_index"):
                val = int(round(val))
            cfg[key] = val

        _save_config(cfg)
        self._set_startup(self._startup_var.get())
        self._msg_lbl.config(text="✓ Settings saved!")
        self.after(
            3000,
            lambda: self._msg_lbl.config(text="")
        )