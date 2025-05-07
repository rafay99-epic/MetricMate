import subprocess
import sys
import os
from pathlib import Path
from PIL import Image

PROJECT_NAME = "MetricMate"
MAIN_SCRIPT = "gaming_analyzer_gui.py"
ICON_PNG = "icon.png"
ICON_ICO = "icon.ico"
REQUIREMENTS = "requirements.txt"

def install_dependencies():
    """Install dependencies from requirements.txt if it exists."""
    if Path(REQUIREMENTS).exists():
        print(f"[INFO] Found {REQUIREMENTS}. Listing dependencies:")
        with open(REQUIREMENTS, 'r') as f:
            deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        for dep in deps:
            print(f"  - {dep}")
        print(f"[INFO] Installing dependencies from {REQUIREMENTS}...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS], check=True)
            print("[INFO] Dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to install dependencies: {e}")
            sys.exit(1)
    else:
        print(f"[INFO] No {REQUIREMENTS} file found. Skipping dependency installation.")

def convert_icon():
    """Convert icon.png to icon.ico with multiple sizes for Windows executables."""
    try:
        if not Path(ICON_PNG).exists():
            print(f"[ERROR] {ICON_PNG} not found.")
            sys.exit(1)
        img = Image.open(ICON_PNG)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
        img.save(ICON_ICO, format='ICO', sizes=sizes)
        print(f"[INFO] Converted {ICON_PNG} to {ICON_ICO}")
    except Exception as e:
        print(f"[ERROR] Failed to convert icon: {e}")
        sys.exit(1)

def build_exe():
    """Build the executable using PyInstaller."""
    try:
        if not Path(MAIN_SCRIPT).exists():
            print(f"[ERROR] {MAIN_SCRIPT} not found.")
            sys.exit(1)
        if not Path(ICON_ICO).exists():
            print(f"[ERROR] {ICON_ICO} not found. Run convert_icon() first.")
            sys.exit(1)
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            f"--icon={ICON_ICO}",
            f"--name={PROJECT_NAME}",
            MAIN_SCRIPT
        ]
        print(f"[INFO] Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        print(f"[INFO] Build complete. Check the dist/ folder for {PROJECT_NAME}.exe")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Build failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error during build: {e}")
        sys.exit(1)

def main():
    install_dependencies()
    convert_icon()
    build_exe()

if __name__ == "__main__":
    main() 