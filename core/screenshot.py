import os
import cv2
from datetime import datetime

# Paths
ROOT          = os.path.dirname(os.path.dirname(__file__))
INTRUDERS_DIR = os.path.join(ROOT, "data", "intruders")


def capture_from_camera(camera_index: int = 0) -> tuple:
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

    if not cap.isOpened():
        return False, None, "Camera could not be opened."

    # Let camera warm up
    for _ in range(5):
        cap.read()

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return False, None, "Failed to capture frame."

    return True, frame, "Frame captured."


def save_screenshot(frame, label: str = "intruder") -> tuple:
    os.makedirs(INTRUDERS_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename  = f"{label}_{timestamp}.jpg"
    filepath  = os.path.join(INTRUDERS_DIR, filename)

    cv2.imwrite(filepath, frame)
    return filepath, timestamp


def list_screenshots() -> list:
    if not os.path.exists(INTRUDERS_DIR):
        return []

    files = [
        f for f in os.listdir(INTRUDERS_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    files.sort(reverse=True)

    results = []
    for f in files:
        filepath  = os.path.join(INTRUDERS_DIR, f)
        parts     = f.replace(".jpg", "").split("_")
        try:
            timestamp = f"{parts[1]} {parts[2].replace('-', ':')}"
        except IndexError:
            timestamp = "Unknown time"
        results.append({
            "filename" : f,
            "filepath" : filepath,
            "timestamp": timestamp
        })
    return results


def delete_screenshot(filepath: str) -> bool:
    try:
        os.remove(filepath)
        return True
    except Exception:
        return False