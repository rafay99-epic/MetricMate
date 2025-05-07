import subprocess
import sys
from pathlib import Path

PROJECT_NAME = "MetricMate"
MAIN_SCRIPT = "gaming_analyzer_gui.py"
ICON_PNG = "icon.png"
REQUIREMENTS = "requirements.txt"


def install_dependencies():
    if Path(REQUIREMENTS).exists():
        print(f"[INFO] Installing dependencies from {REQUIREMENTS}...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS], check=True)
            print("[INFO] Dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to install dependencies: {e}")
            sys.exit(1)
    else:
        print(f"[INFO] No {REQUIREMENTS} file found. Skipping dependency installation.")

def build_exe():
    try:
        if not Path(MAIN_SCRIPT).exists():
            print(f"[ERROR] {MAIN_SCRIPT} not found.")
            sys.exit(1)
        if not Path(ICON_PNG).exists():
            print(f"[ERROR] {ICON_PNG} not found.")
            sys.exit(1)
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            f"--icon={ICON_PNG}",
            f"--name={PROJECT_NAME}",
            MAIN_SCRIPT
        ]
        print(f"[INFO] Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        print(f"[INFO] Build complete. Check the dist/ folder for {PROJECT_NAME}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Build failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error during build: {e}")
        sys.exit(1)

def main():
    install_dependencies()
    build_exe()

if __name__ == "__main__":
    main() 