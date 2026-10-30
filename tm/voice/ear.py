"""
TM Microphone Listener & Speech-to-Text Subsystem
"""

import sys
from typing import Optional, Callable
from tm.config import Config, get_config

try:
    import speech_recognition as sr
except ImportError:
    sr = None


class Ear:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or get_config()
        self.recognizer = sr.Recognizer() if sr is not None else None
        if self.recognizer:
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = self.config.voice.silence_threshold_seconds

    def listen_phrase(self, status_callback: Optional[Callable[[str], None]] = None) -> Optional[str]:
        """
        Listens to the microphone until the user finishes speaking,
        then transcribes the speech into text.
        """
        if sr is None or not self.recognizer:
            if status_callback:
                status_callback("Error: SpeechRecognition or PyAudio is not installed.")
            return None

        try:
            with sr.Microphone() as source:
                if status_callback:
                    status_callback("Calibrating ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.8)

                if status_callback:
                    status_callback("Listening... (speak now)")

                audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=15)

                if status_callback:
                    status_callback("Processing speech...")

                # Transcribe using Google's free online speech API
                text = self.recognizer.recognize_google(audio)
                return text.strip()
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except Exception as e:
            if status_callback:
                status_callback(f"Ear error: {e}")
            return None

