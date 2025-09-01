#!/usr/bin/env python3
"""
main.py - Start llama-server(s) and the WebUI (Vite Preview)
- Loads models from models/models.yaml
- Spawns llama-server instances (ports per runtime section; recommend 8081+)
- Launches `npm run preview -- --port 8080` to serve built UI
- Exposes /props for frontend config
- Cleans up on shutdown
"""

import requests
import sys
import yaml
import signal
import subprocess
from pathlib import Path
from flask import Flask, jsonify
from flask_cors import CORS

ROOT_DIR = Path(__file__).parent.resolve()
MODELS_YAML = ROOT_DIR / "models" / "models.yaml"
WEBUI_DIR = ROOT_DIR / "webui"
WEBUI_DIST = WEBUI_DIR / "dist"

procs = {}
models = {}

def load_models():
    global models
    if not MODELS_YAML.exists():
        print(f"[ERROR] {MODELS_YAML} not found")
        sys.exit(1)
    with open(MODELS_YAML, "r") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict) or "models" not in data:
        print("[ERROR] models.yaml must contain a 'models:' key")
        sys.exit(1)
    models = data["models"]
    return models

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

# ----------------------
# Flask app for /props
# ----------------------
app = Flask(__name__, static_folder=str(WEBUI_DIST), static_url_path="")
CORS(app, resources={r"/w/*": {"origins": "*"}})

@app.route("/w/models", methods=["GET"])
def wgpt_models():
    """
    Return enriched models list based on models.yaml
    This avoids clashing with llama-server's /v1/models
    """
    enriched = []
    for name, cfg in models.items():
        enriched.append({
            "id": name,  # short stable id
            "name": name,
            "display_name": cfg.get("display_name", Path(name).stem),
            "type": cfg.get("type", "llama"),
            "runtime": cfg.get("runtime", {}),
        })
    return {"object": "list", "data": enriched}

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    models = load_models()

    # Start llama-server(s)
    for name, cfg in models.items():
        start_model_server(name, cfg)

    # Start WebUI + Flask props on port 5000
    from threading import Thread
    Thread(target=lambda: app.run(port=5000, host="0.0.0.0", debug=False, use_reloader=False)).start()

    # Start Vite Preview
    webui_proc = start_webui_preview()
    try:
        webui_proc.wait()
    finally:
        stop_all()
