"""
TM Windows Background System Tray Daemon with Global Hotkey (Ctrl+Space)
"""

import sys
import threading
import time
from typing import Optional
from tm.config import get_config
from tm.core.agent import TMAgent
from tm.voice.ear import Ear
from tm.voice.speaker import Speaker

try:
    import keyboard
except ImportError:
    keyboard = None

try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    pystray = None
    Image = None


def create_tray_icon_image():
    """Generates an Iron Man Arc Reactor tray icon dynamically."""
    size = 64
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Outer cyan circle
    draw.ellipse((4, 4, size - 4, size - 4), outline=(0, 220, 255, 255), width=4)
    # Middle ring
    draw.ellipse((14, 14, size - 14, size - 14), outline=(0, 180, 230, 200), width=3)
    # Core glowing center
    draw.ellipse((22, 22, size - 22, size - 22), fill=(100, 240, 255, 255))

    return image


class TMDaemon:
    def __init__(self):
        self.config = get_config()
        self.agent = TMAgent(self.config)
        self.ear = Ear(self.config)
        self.speaker = Speaker(self.config)
        self.is_busy = False
        self.tray_icon: Optional[pystray.Icon] = None

    def on_hotkey_triggered(self):
        """Called whenever Ctrl+Space is pressed globally anywhere on Windows."""
        if self.is_busy:
            return
        self.is_busy = True

        def run_worker():
            try:
                print(f"\n[Hotkey Triggered] Listening...")
                self.speaker.speak("Yes, Sir?", interruptable=True)

                query = self.ear.listen_phrase(status_callback=lambda s: print(f">> {s}"))
                if query:
                    print(f"User: {query}")
                    res = self.agent.execute_turn(query)
                    reply = res.get("response", "")
                    print(f"TM: {reply}")
                    self.speaker.speak(reply, interruptable=True)
            except Exception as e:
                print(f"[Daemon Error] {e}")
            finally:
                self.is_busy = False

        threading.Thread(target=run_worker, daemon=True).start()

    def run(self):
        print("=" * 60)
        print("TM Background Daemon Started")
        print(f"Press 'Ctrl + Space' anywhere in Windows to summon TM.")
        print("=" * 60)

        # 1. Register global hotkey
        if keyboard is not None:
            interfaces_cfg = getattr(self.config, "interfaces", None)
            hotkey_cfg = getattr(interfaces_cfg, "hotkeys", None) if interfaces_cfg else None
            hotkey = getattr(hotkey_cfg, "summon_agent", "ctrl+space") if hotkey_cfg else "ctrl+space"
            keyboard.add_hotkey(hotkey, self.on_hotkey_triggered)
            print(f"[Hotkey Registered] '{hotkey}' is active.")
        else:
            print("[Warning] 'keyboard' library not available for global hotkeys.")

        # 2. Start Windows System Tray Icon
        if pystray is not None and Image is not None:
            icon_image = create_tray_icon_image()

            def on_exit(icon, item):
                icon.stop()
                sys.exit(0)

            menu = pystray.Menu(
                pystray.MenuItem("TM: Online", lambda: None, enabled=False),
                pystray.MenuItem("Summon TM (Ctrl+Space)", lambda: self.on_hotkey_triggered()),
                pystray.MenuItem("Exit", on_exit)
            )

            self.tray_icon = pystray.Icon("TM", icon_image, "TM - Windows AI Agent", menu)
            self.tray_icon.run()
        else:
            # Fallback console keepalive
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("Daemon stopped.")


def run_daemon():
    daemon = TMDaemon()
    daemon.run()

