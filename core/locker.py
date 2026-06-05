import os
import sys
import json
import subprocess

ROOT        = os.path.dirname(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(ROOT, "config.json")


def _load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def lock_screen():
    import ctypes
    ctypes.windll.user32.LockWorkStation()
    print("[Locker] Screen locked.")


def block_apps():
    cfg          = _load_config()
    blocked_apps = cfg.get("blocked_apps", [])

    if not blocked_apps:
        print("[Locker] No apps configured to block.")
        return

    for app in blocked_apps:
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", app],
                stdout = subprocess.DEVNULL,
                stderr = subprocess.DEVNULL
            )
            print(f"[Locker] Killed: {app}")
        except Exception as e:
            print(f"[Locker] Could not kill {app}: {e}")


def trigger_action():
    cfg    = _load_config()
    action = cfg.get("action", "lock")

    if action == "lock":
        lock_screen()
    elif action == "block_apps":
        block_apps()
    else:
        print(f"[Locker] Unknown action: {action}")