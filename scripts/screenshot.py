#!/usr/bin/env python3
"""Take a clean viewport-only screenshot of the current browser tab.
Usage: python3 screenshot.py [output_path]
Default output: ~/.openclaw/media/screenshot.jpg
"""
import json, base64, sys, os, subprocess

# Config
CDP_PORT = 18800
OUTPUT = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.openclaw/media/screenshot.jpg")
WIDTH = 1920
HEIGHT = 1080

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

# Get first non-devtools tab
try:
    tabs = json.loads(subprocess.check_output(
        ["curl", "-s", f"http://127.0.0.1:{CDP_PORT}/json/list"],
        stderr=subprocess.DEVNULL
    ).decode())
except FileNotFoundError:
    import urllib.request
    tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/list").read().decode())
target = next((t for t in tabs if "devtools" not in t.get("url", "") and t.get("type") == "page"), None)
if not target:
    print("ERROR: No browser tab found. Is Chrome running?")
    sys.exit(1)

ws_url = target["webSocketDebuggerUrl"]

try:
    import websocket
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "websocket-client", "-q"])
    import websocket

ws = websocket.create_connection(ws_url, suppress_origin=True, timeout=10)

# Set viewport size
ws.send(json.dumps({
    "id": 1,
    "method": "Emulation.setDeviceMetricsOverride",
    "params": {"width": WIDTH, "height": HEIGHT, "deviceScaleFactor": 1, "mobile": False}
}))
ws.recv()

# Wait for render
import time
time.sleep(0.5)

# Capture viewport only (no fullPage)
ws.send(json.dumps({
    "id": 2,
    "method": "Page.captureScreenshot",
    "params": {"format": "jpeg", "quality": 85}
}))
resp = json.loads(ws.recv())

# Reset viewport
ws.send(json.dumps({"id": 3, "method": "Emulation.clearDeviceMetricsOverride"}))
ws.recv()

ws.close()

with open(OUTPUT, "wb") as f:
    f.write(base64.b64decode(resp["result"]["data"]))

print(f"Screenshot saved: {OUTPUT} ({WIDTH}x{HEIGHT})")
