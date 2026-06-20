# 🐾 Guard_Dog

A powerful desktop face recognition security system that automatically locks your PC when unauthorized users are detected. Real-time monitoring with intruder screenshot capture and activity logging.

## ✨ Features

- **Real-time Face Recognition** — Uses DeepFace with ArcFace model for 99.9% accuracy
- **Automatic PC Lock** — Instantly locks screen on intruder detection
- **Intruder Screenshots** — Captures and timestamps unauthorized access attempts
- **Activity Logging** — Complete audit trail of all face detection events
- **Owner Welcome** — Personalized greeting for authorized owner
- **Idle Detection** — Triggers action if nobody detected for X minutes
- **App Blocking** — Optional: Close specific apps instead of locking
- **Up to 10 Faces** — Support for 10 authorized users
- **Windows Auto-start** — Runs silently on system boot
- **Cross-Platform Ready** — Windows and Linux support

## 🎯 How It Works

1. **Enrollment** — Add up to 10 authorized faces via webcam or image file
2. **Continuous Scanning** — Background scanner checks camera every 10 seconds
3. **Face Match** — Compares detected face against enrolled database
4. **Actions**:
   - ✅ **Authorized** → Logs activity silently
   - ❌ **Intruder** → Locks screen + saves screenshot
   - ⏱️ **Idle Timeout** → No face for X minutes = trigger action
   - 🔍 **No Face** → Camera empty = no action

## 📦 Installation

### Requirements
- **OS**: Windows 10+ or Linux (Ubuntu/Debian)
- **Python**: 3.11+
- **Hardware**: Webcam, 4GB+ RAM

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Guard_Dog.git
cd Guard_Dog
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run Guard_Dog**
```bash
python main.py
```

5. **Enroll your face**
   - Open Guard_Dog window
   - Go to **Faces tab**
   - Enter your name and click **USE CAMERA**
   - Check "Set as Owner"
   - Click **SAVE SETTINGS**

## 🎮 Usage

### Dashboard Tab
- View protection status (active/disabled)
- Enable/Disable protection
- See enrolled faces count
- View owner name

### Faces Tab
- Enroll new authorized faces (camera or image file)
- Remove enrolled faces
- View face previews
- Set owner role

### Activity Log Tab
- View all detection events with timestamps
- Filter by: All / Owner / Authorized / Intruder
- Clear log history

### Screenshots Tab
- View intruder photos with timestamps
- Preview captured images
- Delete individual or all screenshots

### Settings Tab
- **Match Tolerance**: 0.35-0.60 (lower = stricter)
- **Idle Timer**: Minutes before triggering (1-30)
- **Action on Intruder**: Lock Screen or Block Apps
- **Block Specific Apps**: Add apps to close instead of locking
- **Camera Index**: Select which camera to use
- **Auto-start**: Run on Windows boot

## 🔧 Configuration

Edit `config.json` to customize:

```json
{
  "owner": "YourName",
  "action": "lock",
  "idle_time_minutes": 5,
  "camera_index": 0,
  "tolerance": 0.45,
  "save_screenshot": true,
  "startup_with_windows": false,
  "blocked_apps": [],
  "enabled": true
}
```

## 🏗️ Project Structure

Guard_Dog/
├── main.py                 # Entry point & background scanner
├── config.json             # User settings
├── requirements.txt        # Python dependencies
│
├── core/
│   ├── face_engine.py      # Face recognition & enrollment
│   ├── locker.py           # Screen lock & app blocking
│   └── screenshot.py       # Intruder photo capture
│
├── ui/
│   ├── app.py              # Main window & tabs
│   ├── dashboard.py        # Status & welcome messages
│   ├── faces.py            # Face management
│   ├── logs.py             # Activity log
│   ├── screenshots.py      # Intruder photos viewer
│   └── settings.py         # User preferences
│
├── data/
│   ├── faces/              # Enrolled face data & images
│   └── intruders/          # Intruder screenshots
│
└── assets/
└── guard_dog.png       # App icon

## 🔐 Security Notes

- **Local Storage Only** — All face data stored locally on your PC
- **No Cloud Upload** — Zero external data transmission
- **Offline Operation** — Works completely offline after first setup
- **ArcFace Model** — Military-grade face recognition accuracy
- **Tolerance Tuning** — Adjust sensitivity to prevent false positives

## ⚙️ How Face Recognition Works

Guard_Dog uses **DeepFace** with **ArcFace** neural network:

1. **Face Detection** — RetinaFace finds faces in images (99.8% accuracy)
2. **Face Encoding** — ArcFace converts face to 512-number vector
3. **Face Matching** — Compares live vector against enrolled vectors
4. **Distance Threshold** — If distance ≤ tolerance = match

Tolerance tuning:
- `0.35` = Very strict (reject slight variations)
- `0.45` = Recommended (balance security & convenience)
- `0.60` = Loose (accept variations in lighting/angle)

## 🚀 Performance

- **Scan Interval**: 10 seconds (adjustable)
- **Recognition Time**: 2-3 seconds per face
- **CPU Usage**: 15-25% during scan (low idle)
- **Memory**: ~500MB at runtime

## 📝 Logging

Guard_Dog creates activity logs automatically:

- `guard_dog.log` — System events & errors
- `data/activity_log.json` — Face detection history with timestamps
- `data/intruders/` — Screenshots of detected intruders

## 🛠️ Troubleshooting

### Camera not working
- Check Settings → Camera Index (try 0, 1, 2...)
- Ensure no other apps use camera
- Restart Guard_Dog

### Not recognizing your face
- Re-enroll with better lighting
- Face the camera straight on
- Increase tolerance in Settings (try 0.50)

### Too many false positives
- Decrease tolerance in Settings (try 0.40)
- Re-enroll with a clearer photo

### App crashes on startup
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
- Check Python version: `python --version` (must be 3.11+)

## 📦 Dependencies

- **deepface** — Face recognition engine
- **opencv-python** — Camera & image processing
- **tensorflow** — Neural network runtime
- **tkinter** — GUI (built-in with Python)
- **pillow** — Image manipulation
- **pystray** — System tray integration

See `requirements.txt` for complete list.

## 📄 License

MIT License — See LICENSE file for details

## 📧 Support

Found a bug? Have a feature request?

- Open an Issue on GitHub
- Include: OS version, Python version, error message
- Attach: `guard_dog.log` file

## ⚖️ Legal Notice

Guard_Dog is provided as-is for personal security use. Users are responsible for:
- Complying with local privacy laws
- Obtaining consent before monitoring shared devices
- Responsible use of biometric data

## 🙏 Acknowledgments

Built with:
- [DeepFace](https://github.com/serengil/deepface) — Face recognition
- [OpenCV](https://opencv.org/) — Computer vision
- [TensorFlow](https://tensorflow.org/) — Deep learning

🐾 Guard Your Screen. Guard Your Data.
