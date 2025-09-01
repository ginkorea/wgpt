#!/usr/bin/env python3
"""
main.py - Controller for WGPT app
- Loads models from models/models.yaml
- Spawns llama-server instances
- Sets environment variables for the webui
- Cleans up on shutdown
"""

import os
import sys
import yaml
import signal
import subprocess
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).parent.resolve()
MODELS_YAML = ROOT_DIR / "models" / "models.yaml"
LLAMA_SERVER_BIN = ROOT_DIR / "engines" / "llama-server"
WEBUI_DIR = ROOT_DIR / "webui"

# Track running servers
running_procs = {}


def load_models():
    """Load model registry from models.yaml"""
    if not MODELS_YAML.exists():
        print(f"[ERROR] {MODELS_YAML} not found")
        sys.exit(1)

    with open(MODELS_YAML, "r") as f:
        models = yaml.safe_load(f)

    if not isinstance(models, dict) or "models" not in models:
        print("[ERROR] models.yaml must contain a 'models:' key")
        sys.exit(1)

    return models["models"]


def start_model_server(model_name, model_config):
    """Start a llama-server instance for a given model"""
    model_path = ROOT_DIR / "models" / model_config["path"]
    port = model_config.get("port", 8080)

    if not model_path.exists():
        print(f"[ERROR] Model path not found: {model_path}")
        return None

    cmd = [
        str(LLAMA_SERVER_BIN),
        "--model", str(model_path),
        "--host", "127.0.0.1",
        "--port", str(port),
    ]

    print(f"[INFO] Starting {model_name} on port {port}")
    proc = subprocess.Popen(cmd)
    running_procs[model_name] = proc
    return proc


def stop_servers():
    """Stop all running llama-server processes"""
    for name, proc in running_procs.items():
        print(f"[INFO] Stopping {name} (pid={proc.pid})")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    running_procs.clear()


def signal_handler(sig, frame):
    print("\n[INFO] Caught signal, shutting down...")
    stop_servers()
    sys.exit(0)


def start_webui():
    """Start the webui with npm run dev"""
    if not WEBUI_DIR.exists():
        print(f"[ERROR] WebUI directory not found: {WEBUI_DIR}")
        return None

    env = os.environ.copy()
    # Export model registry info so WebUI can connect
    # e.g. {"llama": "http://127.0.0.1:8080"}
    env["WGPT_MODELS"] = str({
        name: f"http://127.0.0.1:{cfg.get('port', 8080)}"
        for name, cfg in models.items()
    })

    cmd = ["npm", "run", "dev"]
    print("[INFO] Starting WebUI (npm run dev)...")
    return subprocess.Popen(cmd, cwd=WEBUI_DIR, env=env)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    models = load_models()

    # Start model servers
    for name, cfg in models.items():
        start_model_server(name, cfg)

    # Start webui
    webui_proc = start_webui()

    if webui_proc:
        running_procs["webui"] = webui_proc

    # Wait for webui to exit
    try:
        webui_proc.wait()
    finally:
        stop_servers()
