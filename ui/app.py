import os
import sys
import json
import tkinter as tk
from tkinter import ttk

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.face_engine  import FaceEngine
from ui.dashboard      import DashboardTab
from ui.faces          import FacesTab
from ui.logs           import LogsTab
from ui.screenshots    import ScreenshotsTab
from ui.settings       import SettingsTab

# Colors
BG       = "#0d0f14"
BG2      = "#161920"
BG3      = "#1e2230"
ACCENT   = "#00e676"
TEXT     = "#e8eaf6"
TEXT_DIM = "#6b7280"


class GuardDogApp(tk.Tk):
    def __init__(self, scanner=None):
        super().__init__()
        self._scanner = scanner
        self._engine  = FaceEngine()

        self.title("Guard_Dog")
        self.geometry("720x560")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # App icon
        icon_path = os.path.join(ROOT, "assets", "icon.ico")
        png_path  = os.path.join(ROOT, "assets", "guard_dog.png")
        if os.path.exists(icon_path):
            self.iconbitmap(default=icon_path)
        if os.path.exists(png_path):
            from PIL import Image, ImageTk
            img  = Image.open(png_path).resize((32, 32))
            icon = ImageTk.PhotoImage(img)
            self.iconphoto(True, icon)
            self._icon_ref = icon

        self._build()

    def _build(self):
        # Top bar
        top = tk.Frame(self, bg=BG3, height=50)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(
            top, text="🐾  GUARD_DOG",
            font=("Courier New", 14, "bold"),
            fg=ACCENT, bg=BG3
        ).pack(side="left", padx=20, pady=14)

        tk.Label(
            top, text="v1.0  |  Face Security System",
            font=("Courier New", 9),
            fg=TEXT_DIM, bg=BG3
        ).pack(side="right", padx=20)

        # Notebook (tabs)
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "TNotebook",
            background=BG2, borderwidth=0
        )
        style.configure(
            "TNotebook.Tab",
            background=BG2, foreground=TEXT_DIM,
            font=("Courier New", 10),
            padding=[14, 7]
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", BG)],
            foreground=[("selected", ACCENT)]
        )

        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill="both", expand=True)

        # Create tabs
        self._dash    = DashboardTab(
            self._notebook, self._engine, self._scanner
        )
        self._faces   = FacesTab(
            self._notebook, self._engine
        )
        self._logs    = LogsTab(self._notebook)
        self._shots   = ScreenshotsTab(self._notebook)
        self._setts   = SettingsTab(self._notebook)

        self._notebook.add(self._dash,  text="  Dashboard  ")
        self._notebook.add(self._faces, text="  Faces  ")
        self._notebook.add(self._logs,  text="  Activity Log  ")
        self._notebook.add(self._shots, text="  Screenshots  ")
        self._notebook.add(self._setts, text="  Settings  ")

        self._notebook.bind(
            "<<NotebookTabChanged>>", self._on_tab_change
        )

    def _on_tab_change(self, event):
        tab = self._notebook.index(
            self._notebook.select()
        )
        if tab == 0:
            self._dash.refresh()
        elif tab == 2:
            self._logs._refresh()
        elif tab == 3:
            self._shots._refresh()

    def notify_owner_returned(self, name: str,
                               had_intruder: bool):
        self._dash.show_welcome(name)
        if had_intruder:
            self.after(
                1500,
                self._dash.show_intruder_alert
            )

    def _on_close(self):
        self.withdraw()

    def show(self):
        self.deiconify()
        self.lift()
        self.focus_force()


def launch_ui(scanner=None):
    app = GuardDogApp(scanner)
    app.mainloop()


if __name__ == "__main__":
    launch_ui()