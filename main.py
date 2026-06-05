import os
import sys
import json
import time
import threading
import tkinter as tk
from datetime import datetime

ROOT = os.path.dirname(__file__)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

CONFIG_PATH = os.path.join(ROOT, "config.json")

from core.face_engine import FaceEngine
from core.screenshot  import capture_from_camera, save_screenshot
from core.locker      import trigger_action
from ui.logs          import write_log, has_intruder_since


def load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


class Scanner:
    def __init__(self):
        self._engine        = FaceEngine()
        self._running       = False
        self._thread        = None
        self._last_seen     = None
        self._idle_notified = False
        self._app           = None

    def set_app(self, app):
        self._app = app

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread  = threading.Thread(
            target=self._loop, daemon=True
        )
        self._thread.start()
        print("[Scanner] Started.")

    def stop(self):
        self._running = False
        print("[Scanner] Stopped.")

    def reload_engine(self):
        self._engine = FaceEngine()
        print("[Scanner] Face engine reloaded.")

    def _loop(self):
        print("[Scanner] Scan loop running...")
        while self._running:
            cfg = load_config()

            if not cfg.get("enabled", True):
                time.sleep(2)
                continue

            ok, frame, msg = capture_from_camera(
                cfg.get("camera_index", 0)
            )

            if not ok:
                print(f"[Scanner] Camera error: {msg}")
                time.sleep(5)
                continue

            temp_path = os.path.join(
                ROOT, "data", "faces", "_scan_temp.jpg"
            )
            import cv2
            cv2.imwrite(temp_path, frame)

            result, name = self._engine.recognize_face(
                temp_path
            )

            if result == "authorized":
                self._handle_authorized(name, frame, cfg)
            elif result == "intruder":
                self._handle_intruder(frame, cfg)
            elif result == "no_face":
                self._handle_no_face(cfg)

            time.sleep(
                cfg.get("idle_time_minutes", 5) * 0.2
            )

    def _handle_authorized(self, name: str, frame, cfg: dict):
        is_owner = self._engine.is_owner(name)
        event    = "owner" if is_owner else "authorized"

        if is_owner and self._last_seen is None:
            had_intruder = has_intruder_since(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            if self._app:
                self._app.after(
                    0,
                    lambda: self._app.notify_owner_returned(
                        name, had_intruder
                    )
                )

        write_log(event, name)
        self._last_seen     = datetime.now()
        self._idle_notified = False

    def _handle_intruder(self, frame, cfg: dict):
        print("[Scanner] Intruder detected!")
        write_log("intruder", None, "Unknown face detected")

        if cfg.get("save_screenshot", True):
            filepath, timestamp = save_screenshot(
                frame, "intruder"
            )
            print(f"[Scanner] Screenshot saved: {filepath}")

        trigger_action()
        self._last_seen = None

    def _handle_no_face(self, cfg: dict):
        if self._last_seen is None:
            return

        idle_minutes = cfg.get("idle_time_minutes", 5)
        elapsed      = (
            datetime.now() - self._last_seen
        ).total_seconds() / 60

        if elapsed >= idle_minutes and not self._idle_notified:
            print(f"[Scanner] Idle for {elapsed:.1f} min — triggering action.")
            write_log("idle", None, f"No face for {idle_minutes} min")
            trigger_action()
            self._idle_notified = True


def run_tray(scanner, app):
    try:
        import pystray
        from PIL import Image, ImageDraw

        # Use Guard_Dog icon for tray
        icon_path = os.path.join(ROOT, "assets", "guard_dog.png")
        if os.path.exists(icon_path):
            img = Image.open(icon_path).resize((64, 64))
        else:
            img  = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.ellipse([4, 4, 60, 60], fill=(30, 180, 100))
            draw.ellipse([20, 20, 44, 44], fill=(13, 15, 20))

        def open_app(icon, item):
            app.after(0, app.show)

        def toggle(icon, item):
            cfg             = load_config()
            cfg["enabled"]  = not cfg["enabled"]
            with open(CONFIG_PATH, "w") as f:
                json.dump(cfg, f, indent=2)
            status = "ENABLED" if cfg["enabled"] else "DISABLED"
            print(f"[Tray] Guard_Dog {status}")

        def quit_app(icon, item):
            scanner.stop()
            icon.stop()
            app.after(0, app.destroy)

        menu = pystray.Menu(
            pystray.MenuItem("Open Guard_Dog", open_app,
                             default=True),
            pystray.MenuItem("Toggle Protection", toggle),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", quit_app)
        )

        icon = pystray.Icon(
            "Guard_Dog", img, "Guard_Dog 🐾", menu
        )
        icon.run()

    except ImportError:
        print("[Tray] pystray not found — skipping tray.")
        app.mainloop()


if __name__ == "__main__":
    from ui.app import GuardDogApp

    scanner = Scanner()
    app     = GuardDogApp(scanner)
    scanner.set_app(app)
    scanner.start()

    tray_thread = threading.Thread(
        target=run_tray,
        args=(scanner, app),
        daemon=True
    )
    tray_thread.start()

    app.mainloop()