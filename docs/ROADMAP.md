# TM Project Roadmap & Milestones

This roadmap outlines the phased development of **TM (TreatMan)**, from foundational architecture to full multimodal autonomy.

---

## 🎯 Milestone Overview

| Milestone | Focus | Key Deliverables | Status |
| :---: | :--- | :--- | :---: |
| **0** | **Architecture & Documentation** | System blueprint, tech stack, comprehensive markdown documentation | **Completed ✅** |
| **1** | **Foundation & Brain (MVP)** | Project scaffolding, OpenRouter free model router, ReAct agent loop, persona | **Completed ✅** |
| **2** | **OS Tools (The Hands)** | Windows app launcher, volume/brightness/battery, PowerShell runner, file organizer | **Completed ✅** |
| **3** | **Interactive Rich CLI** | Streaming token responses, tool execution cards, interactive permission prompts | **Completed ✅** |
| **4** | **Voice Pipeline (Ears & Voice)** | Real-time mic STT, Edge-TTS British speech, continuous voice loop, barge-in interrupt | **Completed ✅** |
| **5** | **Vision Eyes & Computer-Use** | Sub-50ms screen capture, error diagnosis via vision model, GUI click/typing fallback | **Completed ✅** |
| **6** | **HUD & Background Daemon** | System tray icon, `Ctrl+Space` global hotkey, translucent floating HUD widget | **Completed ✅** |

---

## 📋 Detailed Task Breakdown

### Milestone 0: Architecture & Documentation (Completed ✅)
- [x] Create master specification: `TM_SYSTEM_SPECIFICATION.md`
- [x] Create project README with quickstart: `README.md`
- [x] Create in-depth architecture document: `docs/ARCHITECTURE.md`
- [x] Create complete configuration reference: `docs/CONFIGURATION.md`
- [x] Create tools catalog & schema document: `docs/TOOLS_REFERENCE.md`
- [x] Create voice & vision deep-dive guide: `docs/VOICE_AND_VISION_GUIDE.md`
- [x] Create roadmap and milestone tracker: `docs/ROADMAP.md`

---

### Milestone 1: Foundation & Brain (Completed ✅)
- [x] Configure `pyproject.toml` with dependencies (`httpx`, `rich`, `pydantic`, `pywin32`, `psutil`, `send2trash`, `ddgs`, `mss`, `edge-tts`).
- [x] Implement `config.yaml` loader and `.env` validator in `tm/config.py`.
- [x] Build `tm/core/llm_router.py`:
  - OpenRouter client configured with free model rotation (`llama-3.3-70b-instruct:free`, `gemini-2.0-flash-exp:free`, `deepseek-r1:free`).
  - Automatic rate-limit catch & model failover.
  - Local Ollama fallback connector.
- [x] Implement `tm/core/persona.py`:
  - J.A.R.V.I.S. system prompts, concise communication rules, and polite competence.
- [x] Implement `tm/core/agent.py`:
  - Main ReAct reasoning loop.
  - Tool execution dispatcher with JSON schema validation.
  - Max-turns safety circuit breaker.
- [x] Implement `tm/core/guardrails.py`:
  - Permission evaluator (`STRICT`, `BALANCED`, `AUTONOMOUS`).
  - Destructive command regex blocklist.
- [x] Build unit tests `tests/test_guardrails.py` and `tests/test_tools.py` (6/6 passing).

---

### Milestone 2: Windows OS Tools & Actuation ("The Hands") (Completed ✅)
- [x] Implement `tm/tools/system_tools.py`:
  - `launch_app` & `close_app` via Windows Registry and `psutil`.
  - `set_volume` & `mute_audio` via `pycaw` and PowerShell audio COM.
  - `set_brightness` via `screen_brightness_control` and WMI.
  - `get_system_stats` (CPU, RAM, Battery status, uptime).
  - `lock_workstation` via Win32 `LockWorkStation()`.
- [x] Implement `tm/tools/shell_tools.py`:
  - Safe asynchronous PowerShell executor with output capture and timeout guards.
  - `git_status` and developer helpers.
  - `winget` package installer.
- [x] Implement `tm/tools/file_tools.py`:
  - Recursive search using `pathlib`.
  - Downloads folder auto-categorizer.
  - Safe file deletion using `send2trash`.
- [x] Implement `tm/tools/web_tools.py`:
  - Zero-cost live web search via DuckDuckGo / `ddgs`.
  - Webpage content scraper and Markdown cleaner.

---

### Milestone 3: Interactive Rich Terminal CLI (Completed ✅)
- [x] Implement `tm/interfaces/cli.py`:
  - Live streaming tokens.
  - Animated status spinners during tool execution.
  - Color-coded tool execution results.
  - Interactive approval prompts `[Y/n]` for Tier 3 operations in Strict/Balanced modes.
- [x] Create main launcher `run_tm.py`:
  - Flags for `--cli`, `--voice`, `--test`, `--audit`, and one-shot execution.

---

### Milestone 4: Voice Pipeline ("The Ears & Voice")
- [ ] Implement `tm/voice/speaker.py`:
  - High-fidelity British speech synthesis using `edge-tts` (`en-GB-RyanNeural`).
  - Audio playback stream using `pygame` / `sounddevice`.
  - Instant barge-in interruption logic.
- [ ] Implement `tm/voice/ear.py`:
  - Microphone streaming listener with Voice Activity Detection (Silero VAD).
  - Fast local transcription using `faster-whisper`.
- [ ] Implement `tm/voice/wakeword.py`:
  - Low-CPU background wake-word listener ("Hey TM").
- [ ] Wire voice interface into `run_tm.py --voice`.

---

### Milestone 5: Vision Eyes & Computer-Use
- [ ] Implement `tm/tools/vision_tools.py`:
  - Sub-50ms screen capture via `mss`.
  - Active foreground window boundary isolation.
  - High-DPI Windows display scaling normalization.
  - Multimodal vision queries using `google/gemini-2.0-flash-exp:free`.
- [ ] Implement GUI actuation fallback:
  - Coordinate clicking and typing via `pyautogui`.
  - Accessibility tree traversal via `pywinauto`.

---

### Milestone 6: Background Daemon & Floating HUD
- [ ] Implement `tm/interfaces/daemon.py`:
  - Windows System Tray icon with menu (Status, Mute, Autonomy Switch, Exit).
  - Global system hotkey hook (`Ctrl + Space`) to summon TM from any game or app.
- [ ] Implement `tm/interfaces/hud.py`:
  - Translucent, frameless desktop overlay widget.
  - Dynamic audio waveform animation when speaking or listening.
  - Floating action notification toasts.

---

## 🔮 Future Horizons & Stretch Goals
- **Smart Home Integration**: Control Philips Hue / Home Assistant lights directly ("TM, dim the lights in my lab").
- **Local Spotify Connect**: Direct playback control of Spotify playlists and podcasts without switching windows.
- **Offline Self-Hosting**: Full local packaging with 4-bit quantized Llama-3 running purely on laptop NPU/GPU.

