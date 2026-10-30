# TM Voice & Vision Deep-Dive Guide

This guide covers the technical mechanisms behind **TM's Audio Pipeline** (the ears & voice) and **Perception Engine** (the eyes & hands).

---

## Part 1: The Voice Pipeline

```
[Ambient Audio] ──► [openWakeWord] ──► ("Hey TM" detected)
                             │
                             ▼
                    [Microphone Capture]
                             │
                             ▼
                    [Silero / WebRTC VAD]
                             │ (User finishes sentence)
                             ▼
                    [faster-whisper STT] ──► (Transcribed text sent to TM Brain)
                                                              │
                                                              ▼
                                                     [edge-tts Synthesis]
                                                     (en-GB-RyanNeural)
                                                              │
                                                              ▼
                                                   [Audio Output Device]
                                                              │
                                                    (BARGE-IN LISTENER)
                                                    User speaks or hits ESC
                                                              │
                                                              ▼
                                                   [Immediate Stop Signal]
```

### 1.1 Wake-Word Detection ("Hey TM")
- **Engine**: `openWakeWord` (local, lightweight neural network).
- **Resource Footprint**: Consumes less than 1% CPU utilization on modern Intel/AMD laptops.
- **Trigger**: Listens for `"Hey TM"` or `"Jarvis"`.
- **Activation Sound**: Emits a soft, high-tech ping sound effect upon wake detection to let you know TM is ready.

### 1.2 Voice Activity Detection (VAD) & Listening
- **Problem with Traditional Voice Assistants**: Having to click a button or experiencing long, awkward silences before the AI processes your speech.
- **TM Solution**: Uses **Silero VAD** running in real time on the incoming microphone stream. 
- **Silence Window**: When speech transitions to silence for more than 1.2 seconds (`silence_threshold_seconds`), TM automatically cuts the recording and dispatches the audio buffer to the Speech-to-Text engine.

### 1.3 Speech-to-Text (`faster-whisper`)
- **Model**: `base.en` (approximately 74MB, runs locally in <250ms).
- **Offline Capable**: Works completely offline without streaming your private microphone audio to third-party cloud servers.
- **Accuracy**: Optimized for technical keywords, terminal commands, and English conversational speech.

### 1.4 Realistic Speech Synthesis (`edge-tts`)
- **Why Edge-TTS?**: Traditional local TTS engines (like `pyttsx3` or SAPI5) sound robotic and tinny. Cloud TTS providers like ElevenLabs require expensive paid subscriptions. **Edge-TTS** connects to Microsoft's neural voice servers, delivering ultra-expressive, natural human speech with **zero subscription or API costs**.
- **The JARVIS Voice Profile**:
  - Voice ID: `en-GB-RyanNeural`
  - Characteristics: Calm, distinguished British male accent, identical in tone and inflection to Tony Stark's assistant.
  - Customization: Adjustable speech rate (e.g. `rate: "+5%"`) and pitch in `config.yaml`.

### 1.5 The Barge-In (Interruption) Engine
- **How It Works**: While TM is speaking through your speakers, a background monitor continues to observe the microphone energy level and the `Escape` key.
- **Instant Cutoff**: If you say *"Stop"*, *"Nevermind"*, start speaking your next thought, or hit `Escape`, the audio playback buffer is dumped instantly (<50ms). You never have to wait for TM to finish a long sentence before giving your next command.

---

## Part 2: The Vision & Perception Engine

```
[User Command] ──► "TM, look at my screen and tell me why this build failed"
                          │
                          ▼
                  [MSS Screen Capture]
                  (Grabs active monitor in ~12ms)
                          │
                          ▼
                  [High-DPI Coordinate Normalization]
                  (Scales Windows 125%/150% scaling)
                          │
                          ▼
                  [Image Downsampler & Optimizer]
                  (Resizes to 1280x720 JPEG, ~120KB)
                          │
                          ▼
                  [OpenRouter Free Vision Model]
                  (google/gemini-2.0-flash-exp:free)
                          │
                          ▼
                  [Parsed Visual Diagnosis & Action]
```

### 2.1 Screen Capture with `mss`
- **Speed**: Standard Python screenshot libraries (`PIL.ImageGrab` or `pyautogui.screenshot()`) take 200–500ms per frame. `mss` interacts directly with the Windows DirectX / GDI surface, capturing a full 1080p/4K display in under **15 milliseconds**.
- **Multi-Monitor Support**: Automatically detects multi-monitor setups and captures either the monitor containing the active foreground window or the full combined desktop.

### 2.2 Windows High-DPI Display Scaling
- **The Problem**: Most modern laptops run at 125%, 150%, or 200% Windows display scaling. Raw pixel coordinates do not match logical UI coordinates, causing mouse clicks to miss buttons.
- **TM Solution**: TM calls `ctypes.windll.shcore.SetProcessDpiAwareness(2)` on initialization, ensuring 1:1 pixel accuracy for screen crops and mouse automation.

### 2.3 Multimodal Visual Troubleshooting
When you ask TM about what's on your screen:
1. TM takes a snapshot.
2. The snapshot is downsampled and sent with your prompt to a multimodal free model (e.g., `gemini-2.0-flash-exp:free`).
3. Example use cases:
   - *"TM, check the terminal window on the left and tell me what dependency is missing."*
   - *"Did the cloud deployment finish in my browser?"*
   - *"Extract the text from this error message popup that won't let me copy-paste."*

### 2.4 Computer-Use & GUI Automation Fallback
For legacy desktop software that lacks command-line interfaces or REST APIs:
- **UI Automation (Accessibility Tree)**: TM inspects the Windows UI Automation tree via `pywinauto` to locate buttons, list views, and text inputs by their accessibility labels.
- **Visual Coordinate Clicking**: If an element is rendered inside a custom graphical canvas (such as an electron app or game), TM uses visual object detection to find the center `(X, Y)` coordinate and executes a click using `pyautogui`.

