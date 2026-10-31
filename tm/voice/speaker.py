"""
TM Speech Synthesizer (Edge-TTS Neural JARVIS Voice with Barge-In)
"""

import os
import subprocess
import tempfile
import asyncio
from pathlib import Path
from typing import Optional
from tm.config import Config, get_config

try:
    import edge_tts
except ImportError:
    edge_tts = None


class Speaker:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or get_config()
        self.voice = self.config.voice.voice_id
        self.rate = self.config.voice.rate
        self.pitch = self.config.voice.pitch
        self._current_process: Optional[subprocess.Popen] = None
        self._temp_files: list = []

    def stop(self) -> None:
        """Instant barge-in cancellation: kills ongoing speech playback immediately."""
        if self._current_process and self._current_process.poll() is None:
            try:
                self._current_process.terminate()
            except Exception:
                pass
            self._current_process = None
        for f in list(self._temp_files):
            try:
                if os.path.exists(f):
                    os.unlink(f)
                self._temp_files.remove(f)
            except Exception:
                pass

    async def _generate_audio_file(self, text: str, output_path: str) -> bool:
        if edge_tts is not None:
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, pitch=self.pitch)
            await communicate.save(output_path)
            return True
        else:
            # Fallback to CLI edge-tts if python package was installed as tool
            cmd = [
                "edge-tts",
                "--voice", self.voice,
                "--text", text,
                "--write-media", output_path,
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            return res.returncode == 0

    def speak(self, text: str, interruptable: bool = True) -> None:
        """Synthesizes text and plays audio through speakers."""
        if not text or not self.config.voice.enabled:
            return

        # Stop any previous speech
        self.stop()

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Generate speech
            try:
                asyncio.run(self._generate_audio_file(text, tmp_path))
            except Exception as e:
                # Fallback to Windows SAPI5 robotic voice if edge-tts fails
                self._speak_sapi5(text)
                return

            if not os.path.exists(tmp_path) or os.path.getsize(tmp_path) == 0:
                self._speak_sapi5(text)
                return

            # Play MP3 asynchronously via Windows MediaPlayer PowerShell script
            clean_path = tmp_path.replace("'", "''")
            ps_script = f"""
            Add-Type -AssemblyName presentationCore
            $player = New-Object System.Windows.Media.MediaPlayer
            $player.Open('{clean_path}')
            $player.Play()
            Start-Sleep -Milliseconds 300
            $i = 0
            while (($player.NaturalDuration.HasTimeSpan -eq $false) -and ($i -lt 30)) {{ 
                Start-Sleep -Milliseconds 100
                $i++
            }}
            if ($player.NaturalDuration.HasTimeSpan) {{
                $dur = $player.NaturalDuration.TimeSpan.TotalSeconds
                Start-Sleep -Seconds ($dur + 0.3)
            }}
            $player.Close()
            """
            self._current_process = subprocess.Popen(
                ["powershell", "-NoProfile", "-Command", ps_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self._temp_files.append(tmp_path)

            if not interruptable:
                self._current_process.wait()
                try:
                    os.unlink(tmp_path)
                    if tmp_path in self._temp_files:
                        self._temp_files.remove(tmp_path)
                except Exception:
                    pass

        except Exception as e:
            self._speak_sapi5(text)
        finally:
            # Cleanup temp file after play in background or later
            pass

    def _speak_sapi5(self, text: str) -> None:
        """Standard Windows SAPI.SpVoice fallback."""
        clean_text = text.replace('"', '""')
        ps_cmd = f'(New-Object -ComObject SAPI.SpVoice).Speak("{clean_text}")'
        try:
            self._current_process = subprocess.Popen(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass

