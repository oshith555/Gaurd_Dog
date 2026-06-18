import os
import json
import pickle
import numpy as np
from deepface import DeepFace

# Paths
ROOT        = os.path.dirname(os.path.dirname(__file__))
FACES_DIR   = os.path.join(ROOT, "data", "faces")
DATA_FILE   = os.path.join(FACES_DIR, "face_data.pkl")
CONFIG_PATH = os.path.join(ROOT, "config.json")

# Model settings
MODEL    = "ArcFace"
DETECTOR = "retinaface"


class FaceEngine:
    def __init__(self):
        os.makedirs(FACES_DIR, exist_ok=True)
        self.known_faces = {}
        self._load_faces()

    def _load_faces(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "rb") as f:
                self.known_faces = pickle.load(f)
            print(f"[FaceEngine] Loaded {len(self.known_faces)} face(s): {list(self.known_faces.keys())}")
        else:
            self.known_faces = {}
            print("[FaceEngine] No face data found. Starting fresh.")

    def _save_faces(self):
        # Persist the enrolled faces cache to disk so known faces survive restarts.
        with open(DATA_FILE, "wb") as f:
            pickle.dump(self.known_faces, f)
        print(f"[FaceEngine] Saved {len(self.known_faces)} face(s).")

    def enroll_face(self, name: str, image_path: str) -> tuple:
        if len(self.known_faces) >= 10:
            return False, "Maximum 10 faces reached."

        if name in self.known_faces:
            return False, f"'{name}' is already enrolled."

        try:
            embedding = DeepFace.represent(
                img_path         = image_path,
                model_name       = MODEL,
                detector_backend = DETECTOR,
                enforce_detection = True
            )
            self.known_faces[name] = {
                "embedding" : embedding[0]["embedding"],
                "image_path": image_path
            }
            self._save_faces()
            return True, f"'{name}' enrolled successfully."

        except Exception as e:
            return False, f"Could not enroll '{name}': {str(e)}"

    def recognize_face(self, image_path: str) -> tuple:
        if not self.known_faces:
            return "no_faces_enrolled", None

        try:
            import tempfile
            import shutil
            
            # IMPORTANT: First check if there's actually a face in the image
            # We do NOT treat empty frames as unauthorized/intruders
            # Empty frames should be ignored, not flagged as threats
            try:
                face_objs = DeepFace.extract_faces(
                    img_path=image_path,
                    detector_backend=DETECTOR,
                    enforce_detection=True
                )
                if not face_objs or len(face_objs) == 0:
                    # No face detected - return early without flagging as intruder
                    return "no_face", None
            except Exception:
                # Exception during face detection - return early without flagging as intruder
                return "no_face", None
            
            # Create a temporary database folder for known faces
            temp_db = tempfile.mkdtemp()
            
            # Copy enrolled faces to temp db
            for name, data in self.known_faces.items():
                src = data["image_path"]
                dst = os.path.join(temp_db, f"{name}.jpg")
                if os.path.exists(src):
                    shutil.copy(src, dst)
            
            # Find matches in database
            dfs = DeepFace.find(
                img_path=image_path,
                db_path=temp_db,
                model_name=MODEL,
                detector_backend=DETECTOR,
                enforce_detection=False,
                silent=True
            )
            
            shutil.rmtree(temp_db)
            
            # If no matches found and a face WAS detected, then it's an unauthorized person (intruder)
            if dfs is None or len(dfs) == 0 or len(dfs[0]) == 0:
                return "intruder", None
            
            # Get best match
            matches = dfs[0]
            best_match = matches.iloc[0]
            distance = best_match["distance"]
            identity = best_match["identity"]
            
            # Extract name from path
            name = os.path.basename(identity).split(".")[0]
            
            cfg = json.load(open(CONFIG_PATH))
            threshold = cfg.get("tolerance", 0.6)
            
            if distance <= threshold:
                return "authorized", name
            else:
                return "intruder", None

        except Exception as e:
            return "no_face", None
        
    def remove_face(self, name: str) -> tuple:
        if name not in self.known_faces:
            return False, f"'{name}' not found."

        # Delete the image file too
        img_path = self.known_faces[name].get("image_path", "")
        if img_path and os.path.exists(img_path):
            os.remove(img_path)

        del self.known_faces[name]
        self._save_faces()
        return True, f"'{name}' removed successfully."

    def list_faces(self) -> list:
        return list(self.known_faces.keys())

    def get_face_image(self, name: str) -> str:
        if name in self.known_faces:
            return self.known_faces[name].get("image_path", None)
        return None

    def is_owner(self, name: str) -> bool:
        cfg = json.load(open(CONFIG_PATH))
        return name == cfg.get("owner", "")