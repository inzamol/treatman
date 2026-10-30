"""
TM Vision & Screen Perception Tools
"""

import base64
import io
import time
from typing import Dict, Any
from tm.tools.base import tool

try:
    import mss
    from PIL import Image
except ImportError:
    mss = None
    Image = None


@tool(
    name="capture_screen",
    description="Takes a high-speed screenshot of your monitor to see errors, applications, or what's currently displayed.",
    parameters={
        "type": "object",
        "properties": {
            "active_window_only": {
                "type": "boolean",
                "description": "If true, attempts to capture only the active window.",
                "default": False,
            }
        },
    },
    tier=1,
)
def capture_screen(active_window_only: bool = False) -> Dict[str, Any]:
    img = None

    # Method 1: MSS fast DirectX/GDI capture
    if mss is not None and Image is not None:
        try:
            with mss.mss() as sct:
                mon = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                sct_img = sct.grab(mon)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        except Exception:
            pass

    # Method 2: PIL ImageGrab fallback
    if img is None and Image is not None:
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab()
        except Exception:
            pass

    if img is not None:
        try:
            img.thumbnail((1280, 720))
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=80)
            b64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

            return {
                "status": "success",
                "width": img.width,
                "height": img.height,
                "image_base64_preview": b64_str[:120] + "...",
                "image_bytes_len": len(buffer.getvalue()),
                "message": "Screenshot captured successfully.",
            }
        except Exception as e:
            return {"status": "error", "message": f"Processing screenshot failed: {e}"}

    return {"status": "error", "message": "Screen capture is not available in headless or locked session."}
