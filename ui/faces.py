import os
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

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


class FacesTab(tk.Frame):
    def __init__(self, parent, engine):
        super().__init__(parent, bg=BG)
        self._engine   = engine
        self._photo_ref = None
        self._build()

    def _build(self):
        tk.Label(
            self, text="Authorized Faces",
            font=("Courier New", 16, "bold"),
            fg=ACCENT, bg=BG
        ).pack(pady=(20, 2))

        tk.Label(
            self, text="Maximum 10 faces  |  One owner allowed",
            font=("Courier New", 9),
            fg=TEXT_DIM, bg=BG
        ).pack()

        # Main layout — list on left, preview on right
        content = tk.Frame(self, bg=BG)
        content.pack(fill="both", expand=True, padx=30, pady=14)

        # Left — face list
        left = tk.Frame(content, bg=BG)
        left.pack(side="left", fill="both", expand=True)

        list_frame = tk.Frame(left, bg=BG2)
        list_frame.pack(fill="both", expand=True)

        self._listbox = tk.Listbox(
            list_frame,
            bg=BG2, fg=TEXT,
            selectbackground=BG3,
            selectforeground=ACCENT,
            font=("Courier New", 11),
            bd=0, highlightthickness=0,
            activestyle="none"
        )
        sb = tk.Scrollbar(
            list_frame, orient="vertical",
            command=self._listbox.yview
        )
        self._listbox.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._listbox.pack(fill="both", expand=True, padx=6, pady=6)
        self._listbox.bind("<<ListboxSelect>>", self._on_select)

        # Right — face preview
        right = tk.Frame(content, bg=BG2, width=160)
        right.pack(side="right", fill="y", padx=(14, 0))
        right.pack_propagate(False)

        tk.Label(
            right, text="Preview",
            font=("Courier New", 9),
            fg=TEXT_DIM, bg=BG2
        ).pack(pady=(10, 4))

        self._preview = tk.Label(
            right, bg=BG2,
            text="No face\nselected",
            fg=TEXT_DIM,
            font=("Courier New", 9)
        )
        self._preview.pack(pady=10, padx=10)

        self._preview_name = tk.Label(
            right, text="",
            font=("Courier New", 9, "bold"),
            fg=ACCENT, bg=BG2
        )
        self._preview_name.pack()

        self._owner_badge = tk.Label(
            right, text="",
            font=("Courier New", 8),
            fg=BG, bg=ACCENT
        )
        self._owner_badge.pack(pady=4)

        # Enroll section
        enroll_frame = tk.Frame(self, bg=BG)
        enroll_frame.pack(fill="x", padx=30, pady=6)

        tk.Label(
            enroll_frame, text="Name:",
            font=("Courier New", 10),
            fg=TEXT_DIM, bg=BG
        ).pack(side="left", padx=(0, 6))

        self._name_var = tk.StringVar()
        tk.Entry(
            enroll_frame,
            textvariable=self._name_var,
            bg=BG3, fg=TEXT,
            insertbackground=ACCENT,
            font=("Courier New", 10),
            relief="flat",
            highlightthickness=1,
            highlightcolor=ACCENT,
            highlightbackground=BG3,
            width=18
        ).pack(side="left", padx=(0, 10), ipady=4)

        self._owner_var = tk.BooleanVar()
        tk.Checkbutton(
            enroll_frame,
            text="Set as Owner",
            variable=self._owner_var,
            bg=BG, fg=TEXT_DIM,
            selectcolor=BG3,
            activebackground=BG,
            activeforeground=ACCENT,
            font=("Courier New", 9)
        ).pack(side="left")

        # Buttons
        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(pady=8)

        tk.Button(
            btn_frame, text="USE CAMERA",
            font=("Courier New", 10, "bold"),
            bg=ACCENT, fg=BG, relief="flat",
            padx=16, pady=7,
            command=self._enroll_camera
        ).pack(side="left", padx=6)

        tk.Button(
            btn_frame, text="USE IMAGE FILE",
            font=("Courier New", 10, "bold"),
            bg=ACCENT2, fg=BG, relief="flat",
            padx=16, pady=7,
            command=self._enroll_file
        ).pack(side="left", padx=6)

        tk.Button(
            btn_frame, text="REMOVE",
            font=("Courier New", 10, "bold"),
            bg=DANGER, fg="#fff", relief="flat",
            padx=16, pady=7,
            command=self._remove
        ).pack(side="left", padx=6)

        self._msg_lbl = tk.Label(
            self, text="",
            font=("Courier New", 10),
            fg=ACCENT, bg=BG
        )
        self._msg_lbl.pack(pady=4)

        self._refresh_list()

    def _refresh_list(self):
        self._listbox.delete(0, tk.END)
        cfg   = _load_config()
        owner = cfg.get("owner", "")
        faces = self._engine.list_faces()

        if not faces:
            self._listbox.insert(tk.END, "  (no faces enrolled yet)")
            return

        for i, name in enumerate(faces, 1):
            tag = "  👑 OWNER" if name == owner else ""
            self._listbox.insert(tk.END, f"  {i}.  {name}{tag}")

    def _on_select(self, event):
        sel   = self._listbox.curselection()
        faces = self._engine.list_faces()
        if not sel or not faces:
            return
        idx = sel[0]
        if idx >= len(faces):
            return

        name      = faces[idx]
        img_path  = self._engine.get_face_image(name)
        cfg       = _load_config()
        is_owner  = name == cfg.get("owner", "")

        self._preview_name.config(text=name)
        self._owner_badge.config(
            text=" OWNER " if is_owner else "",
            bg=ACCENT if is_owner else BG2
        )
        if img_path and os.path.exists(img_path):
            img = Image.open(img_path).resize((130, 130))
            self._photo_ref = ImageTk.PhotoImage(img)
            self._preview.config(
                image=self._photo_ref, text=""
            )
        else:
            self._preview.config(
                image="", text="No image\nfound",
                fg=TEXT_DIM
            )

    def _get_name(self) -> str:
        name = self._name_var.get().strip()
        if not name:
            messagebox.showwarning(
                "Guard_Dog", "Please enter a name first."
            )
        return name

    def _enroll_camera(self):
        name = self._get_name()
        if not name:
            return

        from core.screenshot import capture_from_camera, save_screenshot
        self._msg_lbl.config(
            text="Capturing from camera...", fg=TEXT_DIM
        )
        self.update()

        def run():
            ok, frame, msg = capture_from_camera()
            if not ok:
                self._msg_lbl.config(text=f"✗ {msg}", fg=DANGER)
                return

            # Save captured image temporarily
            temp_path = os.path.join(
                ROOT, "data", "faces", f"{name}_temp.jpg"
            )
            import cv2
            cv2.imwrite(temp_path, frame)

            success, message = self._engine.enroll_face(name, temp_path)

            if success and self._owner_var.get():
                cfg          = _load_config()
                cfg["owner"] = name
                _save_config(cfg)

            color = ACCENT if success else DANGER
            self._msg_lbl.config(text=message, fg=color)
            self._name_var.set("")
            self._owner_var.set(False)
            self._refresh_list()

        threading.Thread(target=run, daemon=True).start()

    def _enroll_file(self):
        name = self._get_name()
        if not name:
            return

        path = filedialog.askopenfilename(
            title="Select Face Image",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not path:
            return

        self._msg_lbl.config(
            text="Processing image...", fg=TEXT_DIM
        )
        self.update()

        def run():
            success, message = self._engine.enroll_face(name, path)

            if success and self._owner_var.get():
                cfg          = _load_config()
                cfg["owner"] = name
                _save_config(cfg)

            color = ACCENT if success else DANGER
            self._msg_lbl.config(text=message, fg=color)
            self._name_var.set("")
            self._owner_var.set(False)
            self._refresh_list()

        threading.Thread(target=run, daemon=True).start()

    def _remove(self):
        sel   = self._listbox.curselection()
        faces = self._engine.list_faces()
        if not sel or not faces:
            messagebox.showinfo(
                "Guard_Dog", "Select a face to remove."
            )
            return

        idx  = sel[0]
        if idx >= len(faces):
            return
        name = faces[idx]

        if messagebox.askyesno(
            "Guard_Dog", f"Remove '{name}'?"
        ):
            ok, msg = self._engine.remove_face(name)
            cfg     = _load_config()

            if cfg.get("owner") == name:
                cfg["owner"] = ""
                _save_config(cfg)

            self._msg_lbl.config(
                text=msg,
                fg=ACCENT if ok else DANGER
            )
            self._preview.config(image="", text="No face\nselected")
            self._preview_name.config(text="")
            self._owner_badge.config(text="")
            self._refresh_list()