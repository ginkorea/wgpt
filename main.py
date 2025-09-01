#!/usr/bin/env python3
"""
main.py - Start llama-server(s) and the WebUI (Vite Preview)
- Loads models from models/models.yaml
- Spawns llama-server instances (ports per runtime section; recommend 8081+)
- Launches `npm run preview -- --port 8080` to serve built UI
- Cleans up on shutdown
"""

import os
import sys
import yaml
import signal
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).parent.resolve()
MODELS_YAML = ROOT_DIR / "models" / "models.yaml"
WEBUI_DIR = ROOT_DIR / "webui"

procs = {}

def load_models():
    if not MODELS_YAML.exists():
        print(f"[ERROR] {MODELS_YAML} not found")
        sys.exit(1)
    with open(MODELS_YAML, "r") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict) or "models" not in data:
        print("[ERROR] models.yaml must contain a 'models:' key")
        sys.exit(1)
    return data["models"]

def start_model_server(name, cfg):
    runtime = cfg.get("runtime", {})
    bin_path = runtime.get("bin")
    args = runtime.get("args", [])
    if not bin_path:
        print(f"[WARN] No runtime.bin for {name}, skipping")
        return None
    bin_abs = (ROOT_DIR / bin_path) if not Path(bin_path).is_absolute() else Path(bin_path)
    if not bin_abs.exists():
        print(f"[ERROR] Binary not found: {bin_abs}")
        return None

    cmd = [str(bin_abs)] + args
    print(f"[INFO] Starting {name}: {' '.join(cmd)}")
    proc = subprocess.Popen(cmd, cwd=ROOT_DIR)
    procs[name] = proc
    return proc

def start_webui_preview():
    if not WEBUI_DIR.exists():
        print(f"[ERROR] WebUI directory not found: {WEBUI_DIR}")
        return None
    # Serve the built UI on :8080
    cmd = ["npm", "run", "preview", "--", "--port", "8080"]
    print("[INFO] Starting WebUI Preview on http://127.0.0.1:8080")
    proc = subprocess.Popen(cmd, cwd=WEBUI_DIR)
    procs["webui"] = proc
    return proc

def stop_all():
    for name, p in list(procs.items()):
        if p.poll() is None:
            print(f"[INFO] Stopping {name} (pid={p.pid})")
            try:
                p.terminate()
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
    procs.clear()

def handle_signal(sig, frame):
    print("\n[INFO] Caught signal, shutting down...")
    stop_all()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    models = load_models()

    # 1) Start all model servers
    for name, cfg in models.items():
        start_model_server(name, cfg)

    # 2) Build UI (skip if already built)
    # You can uncomment this if you want `main.py` to build for you:
    # subprocess.run(["npm", "run", "build"], cwd=WEBUI_DIR, check=True)

    # 3) Start Vite Preview on 8080 (serves `webui/dist`)
    webui_proc = start_webui_preview()
    try:
        webui_proc.wait()
    finally:
        stop_all()
