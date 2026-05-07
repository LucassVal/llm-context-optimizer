# @UBL @UBL @SCR-FR | LEXICO: #SCRIPTS
#!/usr/bin/env python3
"""NeoCortex MCP Tray Monitor — shows MCP status in system tray."""
import subprocess
import sys
import time
import threading
import os

try:
    import pystray
    from PIL import Image, ImageDraw
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False

MCP_PORT = 8765
MISSION_PORT = 3000
LITELLM_PORT = 4000
PICOCLAW_PORT = 18790

def check_port(port):
    """Check if a port is listening."""
    try:
        result = subprocess.run(
            ["netstat", "-ano"], capture_output=True, text=True, timeout=5
        )
        return f":{port} " in result.stdout and "LISTENING" in result.stdout
    except:
        return False

def get_status():
    status = []
    if check_port(MCP_PORT):
        status.append(f"MCP:{MCP_PORT} ON")
    else:
        status.append(f"MCP:{MCP_PORT} OFF")
    if check_port(LITELLM_PORT):
        status.append(f"LLM:{LITELLM_PORT} ON")
    else:
        status.append(f"LLM:{LITELLM_PORT} OFF")
    if check_port(PICOCLAW_PORT):
        status.append(f"Pico:{PICOCLAW_PORT} ON")
    else:
        status.append(f"Pico:{PICOCLAW_PORT} OFF")
    return " | ".join(status)

def create_image(color="green"):
    img = Image.new("RGB", (64, 64), "black")
    draw = ImageDraw.Draw(img)
    draw.ellipse([8, 8, 56, 56], fill=color)
    return img

def run_tray():
    icon = pystray.Icon(
        "neocortex",
        create_image("yellow"),
        "NeoCortex Stack",
        menu=pystray.Menu(
            pystray.MenuItem("Status", lambda: None, enabled=False),
            pystray.MenuItem("Refresh", lambda: update_icon(icon)),
            pystray.MenuItem("Start MCP", lambda: start_mcp()),
            pystray.MenuItem("Start All", lambda: start_all()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", lambda: icon.stop()),
        ),
    )

    def update_icon(ic):
        all_on = check_port(MCP_PORT) and check_port(LITELLM_PORT)
        ic.icon = create_image("green" if all_on else "red")
        ic.title = get_status()

    update_icon(icon)
    threading.Thread(target=lambda: periodic_update(icon), daemon=True).start()
    icon.run()

def periodic_update(icon):
    while True:
        time.sleep(10)
        update_icon(icon)

def start_mcp():
    subprocess.Popen(
        [
            r"C:\Program Files\Python312\python.exe",
            "-m", "neocortex.mcp.server",
            "--transport", "sse",
            "--port", str(MCP_PORT),
        ],
        cwd=r"C:\Users\Lucas Valerio\Desktop\TURBOQUANT_V42\01_neocortex_framework",
        creationflags=subprocess.CREATE_NO_WINDOW,
    )

def start_all():
    subprocess.Popen(
        [r"C:\Users\Lucas Valerio\Desktop\TURBOQUANT_V42\NC-SCR-FR-104-neocortex-launcher.bat"],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )

if __name__ == "__main__":
    if HAS_TRAY:
        run_tray()
    else:
        print("pystray+Pillow not installed. Install: pip install pystray Pillow")
        while True:
            print(f"\r{get_status()}", end="", flush=True)
            time.sleep(5)
