# 🥧 Raspberry Pi 5 Setup + 🐿️ Ultralytics YOLO ONNX Inference (CPU-only)

This README walks you from **brand new Raspberry Pi** → **Python environment** → **clone your Git repo** → **run YOLO predictions** using an **exported ONNX model**.

Target: **Raspberry Pi 5 (8GB) — CPU only** 🥧

---

## 0) What you need 🧰

Hardware:
- 🥧 Raspberry Pi 5 (8GB)
- microSD card (32GB+ recommended)
- USB-C power supply (stable 5V, high current recommended)
- Internet (Wi‑Fi or Ethernet)

On your computer:
- Raspberry Pi Imager
- **microSD card reader** (USB‑C or USB‑A + adapter)

Files:
- Your project repo on GitHub
- Your trained YOLO model: `best.pt` (squirrel detector 🐿️)

---

## 1) Flash Raspberry Pi OS (64-bit) 🥧

1. Install **Raspberry Pi Imager** on your computer.
2. Insert microSD into your **USB microSD reader** and plug into your computer.
3. Open Imager:
   - **Device**: Raspberry Pi 5
   - **OS**: Raspberry Pi OS (64-bit)
   - **Storage**: select your microSD card
4. Click the **gear icon / settings** and set:
   - Hostname (e.g., `pi5`)
   - Username/password
   - Wi‑Fi SSID/password (if using Wi‑Fi)
   - ✅ **Enable SSH**
5. Flash the SD card.
6. Insert SD card into the Pi and power on 🥧

---

## 2) SSH into the Pi 🔐

From your computer terminal:

```bash
ssh <username>@<hostname>.local
# Example:
# ssh pi@pi5.local
```

If `.local` doesn’t work, find the Pi IP from your router and use:

```bash
ssh <username>@<pi-ip>
```

---

## 3) Update system packages ⬆️

```bash
sudo apt update
sudo apt full-upgrade -y
sudo reboot
```

SSH back in after reboot.

---

## 4) Install baseline dependencies 🧱

```bash
sudo apt install -y   git python3 python3-venv python3-pip   build-essential pkg-config   libatlas-base-dev libopenblas-dev   libjpeg-dev libpng-dev
```

---

## 5) Clone your repo from GitHub 🧬

```bash
mkdir -p ~/projects
cd ~/projects

git clone https://github.com/<you>/<repo>.git
cd <repo>
```

---

## 6) Create a Python virtual environment 🐍

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip setuptools wheel
```

> Tip: every time you come back later, run `source .venv/bin/activate`.

---

## 7) Install your repo dependencies 📦

### If your repo has `requirements.txt`
```bash
pip install -r requirements.txt
```

### If your repo uses `pyproject.toml`
```bash
pip install .
```

---

## 8) Install Ultralytics (runtime) 🐍

Inside the venv:

```bash
pip install ultralytics
```

---

## 9) Export your YOLO model to ONNX (do this on your laptop/desktop) 🐿️➡️📦

Do export on a faster computer (not the Pi), from the folder containing `best.pt`:

```bash
pip install ultralytics
yolo export model=best.pt format=onnx imgsz=640 simplify=False
```

### Why `imgsz=640`?
If your model was trained/validated at 640 (common), switching to 320 can reduce accuracy a lot—especially for small targets like 🐿️ squirrels.

After export you’ll have: `best.onnx`

---

## 10) Copy `best.onnx` to the Pi 📤🥧

From your computer:

```bash
# Create a folder on the Pi if needed:
# ssh <username>@<hostname>.local "mkdir -p ~/projects/<repo>/models"

scp best.onnx <username>@<hostname>.local:~/projects/<repo>/models/
```

---

## 11) Update your code to load ONNX 🧠

Wherever you currently do:

```python
from ultralytics import YOLO
model = YOLO("best.pt")
```

Change it to:

```python
from ultralytics import YOLO
model = YOLO("models/best.onnx")
```

Your `predict(...)` calls can usually stay the same.

---

## 12) Run a quick prediction test (image) 🐿️

On the Pi (inside your repo + venv):

```bash
cd ~/projects/<repo>
source .venv/bin/activate

yolo predict model=models/best.onnx source=path/to/test.jpg imgsz=640 conf=0.25
```

Outputs usually appear under `runs/`.

---

## 13) Predict from a USB webcam 📷🥧

```bash
yolo predict model=models/best.onnx source=0 imgsz=640 conf=0.25
```

---

## 14) If accuracy got worse after export: quick checklist ✅

1) Compare PT vs ONNX at the **same** `imgsz`:

```bash
yolo predict model=best.pt   source=path/to/test.jpg imgsz=640 conf=0.25
yolo predict model=best.onnx source=path/to/test.jpg imgsz=640 conf=0.25
```

2) If both are bad at smaller sizes (e.g., 320), it’s probably **resolution too low**.
3) If ONNX is worse than PT at the same size, try:
- Re-export with `simplify=False` (already used above)
- Lower confidence to see if detections are being filtered out:

```bash
yolo predict model=models/best.onnx source=path/to/test.jpg imgsz=640 conf=0.10
```

---

## 15) Performance tips for Pi 5 CPU-only 🥧⚡

- Start at `imgsz=640` to confirm quality, then try:
  - `imgsz=480` or `imgsz=416` for a speed/accuracy balance
  - `imgsz=320` only if accuracy is still OK
- For video:
  - Run inference every N frames (every 2nd/3rd frame)
- Smaller models help a lot (nano/tiny/small variants)
- Keep the Pi cool (throttling hurts performance) 🧊

---

## 16) Optional: one-command setup script 🧪

Create `scripts/setup_pi.sh`:

```bash
#!/usr/bin/env bash
set -e

sudo apt update
sudo apt full-upgrade -y
sudo apt install -y git python3 python3-venv python3-pip build-essential pkg-config   libatlas-base-dev libopenblas-dev libjpeg-dev libpng-dev

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel

if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi

pip install ultralytics
echo "✅ Setup complete. Activate with: source .venv/bin/activate"
```

Run it:

```bash
bash scripts/setup_pi.sh
```

---

## 17) Troubleshooting 🧯

### Raspberry Pi Imager shows no storage device (Mac)
- You need a **USB microSD card reader**
- Disk Utility → View → Show All Devices
- Try another reader/port if it doesn’t show up

### Random reboots / SD corruption
- Power supply may be weak
- Use stable USB‑C power and a good cable

### Install/import errors
- Copy/paste the full error output and we’ll adjust.

---

## Project placeholders to fill in 📝🐿️

- Repo: `https://github.com/<you>/<repo>`
- Model path on Pi: `models/best.onnx`
- Default inference size: `imgsz=640`

Happy squirrel spotting 🐿️🥧
