"""
TM Windows System & Hardware Tools
"""

import os
import sys
import subprocess
import ctypes
from typing import Dict, Any, List
from tm.tools.base import tool

try:
    import psutil
except ImportError:
    psutil = None


# Common App Alias Mapping on Windows
APP_ALIASES = {
    "spotify": "spotify",
    "chrome": "chrome",
    "google chrome": "chrome",
    "edge": "msedge",
    "microsoft edge": "msedge",
    "vscode": "code",
    "vs code": "code",
    "visual studio code": "code",
    "notepad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "terminal": "wt",
    "windows terminal": "wt",
    "powershell": "powershell",
    "cmd": "cmd",
    "explorer": "explorer",
    "file explorer": "explorer",
    "settings": "ms-settings:",
    "task manager": "taskmgr",
    "paint": "mspaint",
}


@tool(
    name="launch_app",
    description="Launches an installed Windows application or system utility by name (e.g. 'Spotify', 'Chrome', 'VS Code', 'Notepad', 'Calculator').",
    parameters={
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "description": "Name or alias of the application to open.",
            }
        },
        "required": ["app_name"],
    },
    tier=2,
)
def launch_app(app_name: str) -> Dict[str, Any]:
    norm_name = app_name.lower().strip()
    target = APP_ALIASES.get(norm_name, norm_name)

    try:
        # Use start via powershell to trigger Windows shell association
        cmd = f'Start-Process -FilePath "{target}"'
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if res.returncode == 0:
            return {"status": "success", "message": f"Launched '{app_name}' successfully."}
        else:
            # Fallback to direct shell start
            os.system(f'start "" "{target}"')
            return {"status": "success", "message": f"Invoked launch command for '{app_name}'."}
    except Exception as e:
        return {"status": "error", "message": f"Failed to launch '{app_name}': {e}"}


@tool(
    name="close_app",
    description="Closes or terminates a running application by process name or window title.",
    parameters={
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "description": "Process name or keyword (e.g. 'spotify', 'chrome', 'notepad').",
            },
            "force": {
                "type": "boolean",
                "description": "If true, forcefully terminates the process tree.",
                "default": False,
            },
        },
        "required": ["app_name"],
    },
    tier=3,
)
def close_app(app_name: str, force: bool = False) -> Dict[str, Any]:
    norm_name = app_name.lower().strip()
    target_alias = APP_ALIASES.get(norm_name, norm_name).replace(".exe", "")

    closed_count = 0
    if psutil is not None:
        try:
            for proc in psutil.process_iter(["pid", "name"]):
                pname = (proc.info.get("name") or "").lower()
                if norm_name in pname or target_alias in pname:
                    try:
                        if force:
                            proc.kill()
                        else:
                            proc.terminate()
                        closed_count += 1
                    except Exception:
                        pass
            if closed_count > 0:
                return {"status": "success", "message": f"Terminated {closed_count} instances of '{app_name}'."}
        except Exception as e:
            pass

    # Fallback to taskkill
    try:
        flag = "/F" if force else ""
        cmd = f'taskkill {flag} /IM "{target_alias}.exe" /T'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            return {"status": "success", "message": f"Closed '{app_name}' via taskkill."}
        return {"status": "not_found", "message": f"No running process found for '{app_name}'."}
    except Exception as e:
        return {"status": "error", "message": f"Error terminating '{app_name}': {e}"}


@tool(
    name="list_running_apps",
    description="Lists active running applications that have visible windows.",
    parameters={"type": "object", "properties": {}},
    tier=1,
)
def list_running_apps() -> Dict[str, Any]:
    apps: List[Dict[str, Any]] = []

    # PowerShell query for processes with MainWindowTitle
    ps_cmd = 'Get-Process | Where-Object { $_.MainWindowTitle -ne "" } | Select-Object Id, ProcessName, MainWindowTitle | ConvertTo-Json'
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if res.returncode == 0 and res.stdout.strip():
            import json
            data = json.loads(res.stdout)
            if isinstance(data, dict):
                data = [data]
            for item in data:
                apps.append({
                    "pid": item.get("Id"),
                    "process_name": item.get("ProcessName"),
                    "title": item.get("MainWindowTitle"),
                })
            return {"count": len(apps), "running_apps": apps}
    except Exception as e:
        pass

    # Fallback psutil
    if psutil is not None:
        for p in psutil.process_iter(["pid", "name"]):
            try:
                apps.append({"pid": p.info["pid"], "name": p.info["name"]})
            except Exception:
                pass
        return {"count": len(apps[:25]), "running_apps": apps[:25]}

    return {"status": "error", "message": "Unable to query running processes."}


@tool(
    name="set_volume",
    description="Sets the Windows master output volume to a specific percentage (0 to 100).",
    parameters={
        "type": "object",
        "properties": {
            "level": {
                "type": "integer",
                "description": "Volume level percentage from 0 to 100.",
                "minimum": 0,
                "maximum": 100,
            }
        },
        "required": ["level"],
    },
    tier=2,
)
def set_volume(level: int) -> Dict[str, Any]:
    level = max(0, min(100, int(level)))

    # Try pycaw first if installed
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
        # pycaw scalar volume is 0.0 to 1.0
        volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        return {"status": "success", "message": f"Master volume set to {level}%."}
    except Exception:
        pass

    # Fallback via PowerShell script with AudioEndpointVolume COM object
    ps_cmd = f"""
    $obj = New-Object -ComObject WScript.Shell
    # Fallback to key simulation if COM not available
    """
    # Or nirsoft/nircmd if available, or direct powershell audio dll:
    ps_audio = f"""
    Add-Type -TypeDefinition @'
    using System.Runtime.InteropServices;
    [Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    public interface IAudioEndpointVolume {{
        int f(); int g(); int h(); int i();
        int SetMasterVolumeLevelScalar(float fLevel, System.Guid pguidEventContext);
        int j();
        int GetMasterVolumeLevelScalar(out float pfLevel);
    }}
    [Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    public interface IMMDevice {{
        int Activate(ref System.Guid id, int clsCtx, int activationParams, out IAudioEndpointVolume aev);
    }}
    [Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    public interface IMMDeviceEnumerator {{
        int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice endpoint);
    }}
    [ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")] public class MMDeviceEnumeratorComObject {{ }}
    public class Audio {{
        public static void SetVolume(float v) {{
            var enumerator = new MMDeviceEnumeratorComObject() as IMMDeviceEnumerator;
            IMMDevice dev = null;
            enumerator.GetDefaultAudioEndpoint(0, 1, out dev);
            var iid = typeof(IAudioEndpointVolume).GUID;
            IAudioEndpointVolume aev = null;
            dev.Activate(ref iid, 23, 0, out aev);
            aev.SetMasterVolumeLevelScalar(v, System.Guid.Empty);
        }}
    }}
'@
    [Audio]::SetVolume({level / 100.0})
    """
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_audio],
            capture_output=True,
            text=True,
            timeout=8,
        )
        if res.returncode == 0:
            return {"status": "success", "message": f"Master volume set to {level}%."}
    except Exception as e:
        pass

    return {"status": "error", "message": "Failed to set master volume."}


@tool(
    name="mute_audio",
    description="Mutes or unmutes the Windows master audio output.",
    parameters={
        "type": "object",
        "properties": {
            "mute": {
                "type": "boolean",
                "description": "True to mute, False to unmute.",
            }
        },
        "required": ["mute"],
    },
    tier=2,
)
def mute_audio(mute: bool) -> Dict[str, Any]:
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
        volume.SetMute(1 if mute else 0, None)
        return {"status": "success", "is_muted": mute}
    except Exception:
        pass

    # Windows key simulation fallback
    ps_cmd = "$wsh = New-Object -ComObject WScript.Shell; $wsh.SendKeys([char]173)"
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], timeout=5)
        return {"status": "success", "message": f"Toggled audio mute state."}
    except Exception as e:
        return {"status": "error", "message": f"Failed to toggle mute: {e}"}


@tool(
    name="set_brightness",
    description="Sets the laptop screen brightness to a percentage (0 to 100).",
    parameters={
        "type": "object",
        "properties": {
            "percentage": {
                "type": "integer",
                "description": "Brightness percentage from 0 to 100.",
                "minimum": 0,
                "maximum": 100,
            }
        },
        "required": ["percentage"],
    },
    tier=2,
)
def set_brightness(percentage: int) -> Dict[str, Any]:
    pct = max(0, min(100, int(percentage)))

    # Try screen_brightness_control
    try:
        import screen_brightness_control as sbc
        sbc.set_brightness(pct)
        return {"status": "success", "brightness": pct}
    except Exception:
        pass

    # WMI PowerShell fallback
    ps_cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {pct})"
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=8,
        )
        if res.returncode == 0:
            return {"status": "success", "brightness": pct}
    except Exception as e:
        pass

    return {"status": "error", "message": "Failed to set display brightness (not supported on this monitor/desktop)."}


@tool(
    name="get_system_stats",
    description="Returns real-time laptop metrics: CPU load, RAM memory usage, battery percentage, and charging state.",
    parameters={"type": "object", "properties": {}},
    tier=1,
)
def get_system_stats() -> Dict[str, Any]:
    stats: Dict[str, Any] = {
        "os": "Windows 11",
        "cpu_percent": 0.0,
        "memory_used_gb": 0.0,
        "memory_total_gb": 0.0,
        "memory_percent": 0.0,
        "battery_percent": None,
        "power_plugged": None,
    }

    if psutil is not None:
        try:
            stats["cpu_percent"] = psutil.cpu_percent(interval=0.2)
            mem = psutil.virtual_memory()
            stats["memory_used_gb"] = round(mem.used / (1024**3), 2)
            stats["memory_total_gb"] = round(mem.total / (1024**3), 2)
            stats["memory_percent"] = mem.percent

            batt = psutil.sensors_battery()
            if batt:
                stats["battery_percent"] = round(batt.percent, 1)
                stats["power_plugged"] = batt.power_plugged
            return stats
        except Exception:
            pass

    return stats


@tool(
    name="lock_workstation",
    description="Locks the Windows workstation immediately.",
    parameters={"type": "object", "properties": {}},
    tier=3,
)
def lock_workstation() -> Dict[str, Any]:
    try:
        ctypes.windll.user32.LockWorkStation()
        return {"status": "success", "message": "Workstation locked."}
    except Exception as e:
        return {"status": "error", "message": f"Failed to lock workstation: {e}"}

