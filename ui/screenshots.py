import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

ROOT = os.path.dirname(os.path.dirname(__file__))

# Colors
BG       = "#0d0f14"
BG2      = "#161920"
BG3      = "#1e2230"
ACCENT   = "#00e676"
DANGER   = "#ff1744"
TEXT     = "#e8eaf6"
TEXT_DIM = "#6b7280"


class ScreenshotsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._thumb_refs = []
        self._screenshots = []
        self._build()

    def _build(self):
        # Header
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=30, pady=(20, 8))

        tk.Label(
            header, text="Intruder Screenshots",
            font=("Courier New", 16, "bold"),
            fg=DANGER, bg=BG
        ).pack(side="left")

        tk.Button(
            header, text="REFRESH",
            font=("Courier New", 9, "bold"),
            bg=BG3, fg=TEXT, relief="flat",
            padx=12, pady=4,
            command=self._refresh
        ).pack(side="right")

        tk.Button(
            header, text="DELETE ALL",
            font=("Courier New", 9, "bold"),
            bg=DANGER, fg="#fff", relief="flat",
            padx=12, pady=4,
            command=self._delete_all
        ).pack(side="right", padx=6)

        # Count label
        self._count_lbl = tk.Label(
            self, text="",
            font=("Courier New", 9),
            fg=TEXT_DIM, bg=BG
        )
        self._count_lbl.pack()

        # Scrollable canvas for thumbnails
        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True, padx=30, pady=8)

        self._canvas = tk.Canvas(
            container, bg=BG,
            highlightthickness=0
        )
        scrollbar = tk.Scrollbar(
            container, orient="vertical",
            command=self._canvas.yview
        )
        self._canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._grid_frame = tk.Frame(self._canvas, bg=BG)
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._grid_frame, anchor="nw"
        )

        self._grid_frame.bind(
            "<Configure>", self._on_frame_configure
        )
        self._canvas.bind(
            "<Configure>", self._on_canvas_configure
        )

        # Selected photo preview
        preview_frame = tk.Frame(self, bg=BG2)
        preview_frame.pack(fill="x", padx=30, pady=(0, 8))

        self._selected_preview = tk.Label(
            preview_frame, bg=BG2,
            text="Click a thumbnail to preview",
            fg=TEXT_DIM, font=("Courier New", 9)
        )
        self._selected_preview.pack(side="left", padx=10, pady=8)

        self._selected_info = tk.Label(
            preview_frame, text="",
            font=("Courier New", 9),
            fg=TEXT, bg=BG2
        )
        self._selected_info.pack(side="left", padx=10)

        tk.Button(
            preview_frame, text="DELETE SELECTED",
            font=("Courier New", 9, "bold"),
            bg=DANGER, fg="#fff", relief="flat",
            padx=12, pady=4,
            command=self._delete_selected
        ).pack(side="right", padx=10)

        self._selected_path = None
        self._refresh()

    def _on_frame_configure(self, event):
        self._canvas.configure(
            scrollregion=self._canvas.bbox("all")
        )

    def _on_canvas_configure(self, event):
        self._canvas.itemconfig(
            self._canvas_window, width=event.width
        )

    def _refresh(self):
        from core.screenshot import list_screenshots

        # Clear existing thumbnails
        for widget in self._grid_frame.winfo_children():
            widget.destroy()
        self._thumb_refs.clear()
        self._screenshots = list_screenshots()

        if not self._screenshots:
            tk.Label(
                self._grid_frame,
                text="No intruder screenshots yet.",
                font=("Courier New", 10),
                fg=TEXT_DIM, bg=BG
            ).grid(row=0, column=0, padx=20, pady=20)
            self._count_lbl.config(text="")
            return

        self._count_lbl.config(
            text=f"{len(self._screenshots)} screenshot(s) saved"
        )

        # Display thumbnails in a grid — 4 per row
        cols = 4
        for i, shot in enumerate(self._screenshots):
            row = i // cols
            col = i % cols

            cell = tk.Frame(
                self._grid_frame, bg=BG2,
                padx=4, pady=4
            )
            cell.grid(row=row, column=col, padx=6, pady=6)

            try:
                img = Image.open(shot["filepath"])
                img.thumbnail((120, 90))
                thumb = ImageTk.PhotoImage(img)
                self._thumb_refs.append(thumb)

                btn = tk.Label(
                    cell, image=thumb,
                    bg=BG2, cursor="hand2"
                )
                btn.pack()
                btn.bind(
                    "<Button-1>",
                    lambda e, s=shot: self._select(s)
                )

            except Exception:
                tk.Label(
                    cell, text="Error\nloading",
                    font=("Courier New", 8),
                    fg=DANGER, bg=BG2,
                    width=10, height=4
                ).pack()

            tk.Label(
                cell, text=shot["timestamp"],
                font=("Courier New", 7),
                fg=TEXT_DIM, bg=BG2
            ).pack()

    def _select(self, shot: dict):
        self._selected_path = shot["filepath"]
        self._selected_info.config(
            text=f"  {shot['filename']}\n  {shot['timestamp']}"
        )

        try:
            img = Image.open(shot["filepath"])
            img.thumbnail((160, 120))
            photo = ImageTk.PhotoImage(img)
            self._selected_preview.config(
                image=photo, text=""
            )
            self._selected_preview.image = photo
        except Exception:
            self._selected_preview.config(
                text="Could not load image"
            )

    def _delete_selected(self):
        if not self._selected_path:
            messagebox.showinfo(
                "Guard_Dog", "Click a thumbnail first."
            )
            return

        if messagebox.askyesno(
            "Guard_Dog", "Delete this screenshot?"
        ):
            from core.screenshot import delete_screenshot
            delete_screenshot(self._selected_path)
            self._selected_path = None
            self._selected_preview.config(
                image="",
                text="Click a thumbnail to preview"
            )
            self._selected_info.config(text="")
            self._refresh()

    def _delete_all(self):
        if not self._screenshots:
            return
        if messagebox.askyesno(
            "Guard_Dog",
            f"Delete ALL {len(self._screenshots)} screenshots?"
        ):
            from core.screenshot import delete_screenshot
            for shot in self._screenshots:
                delete_screenshot(shot["filepath"])
            self._selected_path = None
            self._selected_preview.config(
                image="",
                text="Click a thumbnail to preview"
            )
            self._selected_info.config(text="")
            self._refresh()