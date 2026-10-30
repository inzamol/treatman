# TM (TreatMan) System Specification & Architecture Blueprint
**A JARVIS-Inspired Autonomous Operating System Agent for Windows**

---

## 1. Executive Summary & Vision

**TM** is an autonomous personal AI operator running natively on Windows 11, modeled directly after Tony Stark's **J.A.R.V.I.S.** (Just A Rather Very Intelligent System). 

Based on your exact requirements:
- **Zero-Cost / OpenRouter Brain**: Dynamic routing supporting OpenRouter's free tier models (e.g., `meta-llama/llama-3.3-70b-instruct:free`, `google/gemini-2.0-flash-exp:free`, `deepseek/deepseek-r1:free`, `qwen/qwen-2.5-coder-32b-instruct:free`) with fallbacks to local Ollama and direct free API keys.
- **Configurable Autonomy & Permissions**: Config-driven permission levels (`STRICT`, `BALANCED`, or full `AUTONOMOUS` "JARVIS" mode) with granular tool overrides in `config.yaml`.
- **All Interface Modalities Supported**: Unified core engine switchable between **Interactive Rich Terminal CLI**, **Voice-First (Hands-Free)**, **Background System Daemon with Global Hotkey (`Ctrl+Space`)**, and **Futuristic Floating HUD Widget**.
- **Complete 360° Operations**: Developer workflows, Windows hardware controls, filesystem management, live web research & browser automation, and computer-use vision (reading screens and clicking buttons).

```
+-----------------------------------------------------------------------------------------------+
|                                    UNIFIED INTERACTION LAYER                                  |
|   Rich CLI Console   |   Voice Engine ("Hey TM")   |   Global Hotkey   |   Floating HUD       |
+-----------------------------------------------+-----------------------------------------------+
                                                │
                                                ▼
+-----------------------------------------------------------------------------------------------+
|                                       TM CORE BRAIN                                           |
|   • OpenRouter Model Router (Auto-selects best available free models)                         |
|   • ReAct Planning Loop with Error Auto-Recovery                                              |
|   • JARVIS Persona (Calm, ultra-competent, respectful, concise)                               |
|   • Dual-Tier Memory (Short-term session context + Long-term SQLite preference store)         |
+-----------------------------------------------+-----------------------------------------------+
                                                │
                                                ▼
+-----------------------------------------------------------------------------------------------+
|                              CONFIGURABLE PERMISSION GUARD                                    |
|   Configured via config.yaml: STRICT | BALANCED | AUTONOMOUS                                  |
|   • Path Whitelists / Sandboxes              • Destructive Command Blocker                    |
|   • Confirmation Interceptors                • Real-time Audit Telemetry Log                  |
+-----------------------------------------------+-----------------------------------------------+
                                                │
       ┌────────────────────┬───────────────────┼───────────────────┬────────────────────┐
       ▼                    ▼                   ▼                   ▼                    ▼
┌──────────────┐     ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     ┌──────────────┐
│  Developer   │     │  Windows OS  │    │  Filesystem  │    │ Web & Browser│     │ Screen Eyes  │
│  & Terminal  │     │  & Hardware  │    │  & Storage   │    │  Automation  │     │ & Computer-  │
│              │     │              │    │              │    │              │     │ Use Vision   │
├──────────────┤     ├──────────────┤    ├──────────────┤    ├──────────────┤     ├──────────────┤
│• PowerShell  │     │• Launch/Kill │    │• Smart search│    │• Web search  │     │• MSS screen  │
│  runner      │     │  App by name │    │• Organize dir│    │  (DuckDuckGo)│       capture      │
│• Git & Docker│     │• Master Vol  │    │• Safe delete │    │• Page content│     │• Multi-modal │
│  automation  │       & Mute/Unmute│       (RecycleBin)│       extractor   │       vision OCR   │
│• Winget pack-│     │• Brightness  │    │• File convert│    │• Playwright  │     │• PyAutoGUI / │
│  age manager │     │• Battery info│    │• Read/Write  │       automated   │       UIAutomation │
│• Code runner │     │• Lock screen │    │  documents   │       browser     │       button click │
└──────────────┘     └──────────────┘    └──────────────┘    └──────────────┘     └──────────────┘
```

---

## 2. LLM Engine: OpenRouter & Free Model Strategy

To allow running TM with **zero API cost**, TM uses an intelligent OpenRouter client designed specifically around free model endpoints:

### 2.1 Model Registry & Fallback Hierarchy
1. **Primary Reasoning & Planning**:
   - `meta-llama/llama-3.3-70b-instruct:free` (exceptional tool-calling, 128k context)
   - `google/gemini-2.0-flash-exp:free` (ultra-fast, multimodal vision support)
   - `deepseek/deepseek-r1:free` (deep mathematical and algorithmic reasoning)
2. **Fast Sub-tasks & Routing**:
   - `qwen/qwen-2.5-coder-32b-instruct:free` (specialized code generation & script analysis)
   - `mistralai/mistral-7b-instruct:free` (fast classification and parsing)
3. **Local Offline Fallback**:
   - Native integration with **Ollama** (`http://localhost:11434`) if internet drops or OpenRouter rates limit.

### 2.2 Transparent Rate-Limit & Health Handler
When a free model endpoint on OpenRouter experiences a rate limit (HTTP 429) or queue congestion, TM automatically cascades to the next best free model without interrupting the user's ongoing task.

---

## 3. Configurable Permission & Autonomy Engine

In `config.yaml`, you have complete control over how much autonomy TM is granted:

```yaml
# config.yaml
autonomy:
  level: "balanced" # Options: "strict" | "balanced" | "autonomous"
  
  # Fine-grained action overrides
  rules:
    allow_app_launch: true
    allow_system_volume_brightness: true
    allow_web_browsing: true
    allow_file_reading: true
    allow_file_writing: true
    require_confirmation_for_file_delete: true
    require_confirmation_for_shell_execution: false # Set true to approve every script
    require_confirmation_for_process_kill: true
    require_confirmation_for_system_power: true   # Sleep, restart, shutdown

  # Security bounds
  forbidden_commands:
    - "format "
    - "rmdir /s /q c:\\"
    - "del /f /s /q c:\\"
    - "Drop-Database"
    - "Stop-Computer"
```

### Autonomy Level Definitions:
1. **STRICT Mode**: TM asks for explicit user confirmation (`[Y/n]`) before altering any state (writing files, killing apps, executing shell scripts). Ideal for initial testing.
2. **BALANCED Mode (Recommended)**: TM freely launches applications, adjusts volume/brightness, reads files, and conducts web searches. Prompts the user before deleting files, terminating unsaved processes, or running destructive shell scripts.
3. **AUTONOMOUS Mode (Full JARVIS)**: TM operates completely hands-free. All operations run immediately and are sequentially streamed to the user and recorded into the persistent SQLite audit trail.

---

## 4. Operational Capabilities ("The 5 Hands")

### 4.1 Developer & Terminal Workflows
- **PowerShell Runner**: Executes PowerShell commands natively via an asynchronous subprocess pipe with stdout/stderr real-time capture.
- **Git Assistant**: Can check git status, stage files, generate contextual commit messages, switch branches, and review git diffs.
- **Package Management**: Install and update Windows tools directly using `winget` (e.g., "TM, install VLC player").
- **Code Execution**: Run Python, Node.js, or batch scripts in the background and return parsed summaries.

### 4.2 Windows OS & Hardware Control
- **App Management**: Launch installed Windows applications by human-readable names (e.g. "Open Spotify", "Switch to Chrome", "Close Discord") using Windows Registry app paths, start menu shortcuts, and `psutil`.
- **Audio Control**: Set exact master volume levels (0-100%), mute/unmute, and toggle microphone input using Windows Core Audio API (`pycaw`).
- **Display Control**: Adjust screen brightness dynamically using `screen_brightness_control`.
- **Power & System Stats**: Check real-time CPU, RAM, battery percentage, charging state, and workstation lock (`ctypes.windll.user32.LockWorkStation()`).

### 4.3 Filesystem & Workspace Organization
- **Smart Search**: Quickly find documents, images, and projects across your drives using `pathlib` and Windows Indexing.
- **Auto-Cleanup**: "TM, clean up my Downloads folder" scans files, groups them into logical folders (`Images/`, `Archives/`, `Installers/`, `Documents/`, `Code/`), and moves them safely.
- **Safe Recycling**: Deletions never use destructive `os.remove`; they move items to the Windows Recycle Bin via `send2trash`.

### 4.4 Web & Browser Automation
- **DuckDuckGo / Open Web Search**: Zero-cost, instantaneous web search without requiring paid search API keys.
- **Smart Content Extractor**: Fetches and parses web pages, articles, and documentation into markdown for LLM comprehension.
- **Playwright Browser Agent**: Automates a real Chromium/Edge instance for tasks requiring interaction, clicking web buttons, taking web screenshots, or downloading assets.

### 4.5 Visual Eyes & Computer-Use (GUI Automation)
- **High-Speed Screen Capture**: Uses `mss` for lightning-fast sub-50ms screen captures of your monitor or current active window.
- **Multimodal Visual Inspection**: Feeds screenshots to free vision models (like `gemini-2.0-flash-exp:free`) to answer:
  - *"What is this error dialog saying?"*
  - *"Did my build finish in the other window?"*
  - *"Read the table from this image and format it into CSV."*
- **UI Automation Fallback**: Uses `pyautogui` and Windows UI Automation (`pywinauto`) to locate visual elements, click buttons, and send keystrokes when an application doesn't have an API.

---

## 5. Interaction Modalities (All 4 Included)

TM is designed with a **pluggable interaction architecture**:

```
                         ┌─────────────────────────────┐
                         │      tm.core.orchestrator   │
                         └──────────────┬──────────────┘
                                        │
           ┌────────────────┬───────────┴────────────┬────────────────┐
           ▼                ▼                         ▼                ▼
   ┌───────────────┐ ┌───────────────┐       ┌─────────────────┐ ┌────────────────┐
   │ 1. Rich CLI   │ │ 2. Voice      │       │ 3. Background   │ │ 4. Floating    │
   │    Console    │ │    Pipeline   │       │    Daemon       │ │    HUD Widget  │
   ├───────────────┤ ├───────────────┤       ├─────────────────┤ ├────────────────┤
   │ Terminal with │ │ Wake-word     │       │ Windows System  │ │ Sleek semi-    │
   │ streaming,    │ │ ("Hey TM"),   │       │ Tray icon +     │ │ transparent    │
   │ spinners, and │ │ Whisper STT,  │       │ Global Hotkey   │ │ desktop overlay│
   │ tables        │ │ Edge-TTS      │       │ (`Ctrl+Space`)  │ │ with waveforms │
   └───────────────┘ └───────────────┘       └─────────────────┘ └────────────────┘
```

1. **Rich CLI (`python run_tm.py --cli`)**:
   - Developer command center with syntax highlighting, live thought streams, tool status indicators, and permission prompts.
2. **Voice Pipeline (`python run_tm.py --voice`)**:
   - Mic listening with Voice Activity Detection (VAD).
   - "Hey TM" local wake-word detection.
   - Ultra-natural British JARVIS voice (`en-GB-RyanNeural` via `edge-tts`) with instant barge-in cancellation when interrupted.
3. **Background Daemon (`python run_tm.py --daemon`)**:
   - Sits in the Windows System Tray with minimal memory footprint.
   - Press `Ctrl + Space` anywhere in Windows to trigger audio listening or prompt input.
4. **Floating HUD Widget (`python run_tm.py --hud`)**:
   - Modern Iron Man-inspired translucent widget in the corner of your screen showing agent state (Idle, Thinking, Listening, Executing) with animated audio waveforms.

---

## 6. Complete Directory Structure

```
c:\Users\inzam\RND\treatman/
├── config.yaml                   # Main user settings: autonomy level, models, voice, paths
├── .env.example                  # Environment template (OPENROUTER_API_KEY, etc.)
├── .env                          # Local user environment (ignored by git)
├── run_tm.py                     # Unified entry point launcher
├── pyproject.toml                # Dependencies and project metadata
├── TM_SYSTEM_SPECIFICATION.md    # This master document
│
├── tm/
│   ├── __init__.py
│   ├── config.py                 # Loads & validates config.yaml and environment variables
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── agent.py              # Main ReAct planner loop with tool calling
│   │   ├── llm_router.py         # OpenRouter client with free-model fallback pool
│   │   ├── persona.py            # JARVIS persona instructions and tone constraints
│   │   ├── guardrails.py         # Permission checker (Strict/Balanced/Autonomous)
│   │   └── memory.py             # SQLite session history & long-term user preferences
│   │
│   ├── tools/
│   │   ├── __init__.py           # Unified tool registry
│   │   ├── base.py               # Abstract Tool definition and schema generator
│   │   ├── system_tools.py       # Apps, volume, brightness, battery, processes
│   │   ├── shell_tools.py        # Safe PowerShell & command execution
│   │   ├── file_tools.py         # Search, organize, read, write, recycle bin
│   │   ├── web_tools.py          # DuckDuckGo search & page content scraper
│   │   └── vision_tools.py       # Screen capture (mss) and GUI automation
│   │
│   ├── voice/
│   │   ├── __init__.py
│   │   ├── ear.py                # Microphone listener & Whisper STT
│   │   ├── speaker.py            # Edge-TTS speech synthesizer with barge-in
│   │   └── wakeword.py           # "Hey TM" audio trigger
│   │
│   └── interfaces/
│       ├── __init__.py
│       ├── cli.py                # Interactive Rich console interface
│       ├── daemon.py             # System tray & global hotkey listener
│       └── hud.py                # Floating translucent desktop HUD
│
└── tests/
    ├── test_router.py            # Validates OpenRouter free model connections
    ├── test_guardrails.py        # Tests permission rules
    └── test_system_tools.py      # Verifies Windows OS tool controls
```

---

## 7. Phased Implementation Roadmap

- [x] **Milestone 0: Technical Architecture & Specification Complete**
- [ ] **Milestone 1: Foundation & Brain (Day 1)**
  - Project configuration (`config.yaml`, `.env.example`, `pyproject.toml`).
  - OpenRouter dynamic free-model router with auto-fallback.
  - ReAct agent orchestrator with JARVIS persona.
  - Configurable guardrails and permission manager.
- [ ] **Milestone 2: Windows OS & Developer Tools (The Hands)**
  - App launcher and process manager.
  - Volume, mute, brightness, and battery monitor.
  - Safe PowerShell command runner with timeout and regex blocklist.
  - Filesystem organizer and Recycle Bin safe deletion.
  - DuckDuckGo live web search and summarizer.
- [ ] **Milestone 3: Interactive CLI Interface**
  - Rich-formatted terminal with live streaming, tool execution cards, and approval prompts.
- [ ] **Milestone 4: Voice Pipeline (The Ears & Voice)**
  - Speech synthesis via `edge-tts` (British JARVIS voice).
  - Speech recognition with Voice Activity Detection.
  - Wake-word listener ("Hey TM") and interrupt/barge-in support.
- [ ] **Milestone 5: Vision & Computer-Use (The Eyes)**
  - `mss` screen and window capture.
  - Visual reasoning for desktop errors and screenshots.
  - PyAutoGUI / pywinauto UI automation.
- [ ] **Milestone 6: Background Daemon & Floating HUD**
  - System tray icon with global hotkey (`Ctrl + Space`).
  - Sleek translucent HUD overlay.
