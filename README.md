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
