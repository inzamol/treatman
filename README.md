# TM (TreatMan) — Autonomous Windows AI Agent

> **"Just A Rather Very Intelligent System" for your Windows Laptop.**

[![Python](https://img.shields.io/badge/Python-3.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6.svg)](https://www.microsoft.com/windows)
[![Cost](https://img.shields.io/badge/API%20Cost-%240.00%20(Free%20Tier)-brightgreen.svg)](https://openrouter.ai/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**TM** is an autonomous AI desktop operator designed specifically for Windows 10/11. Inspired by Tony Stark's **J.A.R.V.I.S.** in the Avengers movies, TM gives your laptop hands, eyes, ears, and a voice. It can execute PowerShell commands, launch and control applications, adjust volume and brightness, search and organize your filesystem, browse the live web, see your screen, and converse with you in a natural British neural voice—all with **zero API cost** using free-tier models on OpenRouter.

---

## 🌟 Key Capabilities

```
                      ┌───────────────────────────────────────┐
                      │              USER INPUT               │
                      │  Voice ("Hey TM") • Hotkey • Terminal │
                      └──────────────────┬────────────────────┘
                                         │
                                         ▼
                      ┌───────────────────────────────────────┐
                      │             TM CORE BRAIN             │
                      │  OpenRouter Free Router • ReAct Loop  │
                      │    JARVIS Persona • SQLite Memory     │
                      └──────────────────┬────────────────────┘
                                         │
     ┌───────────────────┬───────────────┴───────────────┬───────────────────┐
     ▼                   ▼                               ▼                   ▼
┌───────────────┐ ┌───────────────┐             ┌───────────────┐   ┌───────────────┐
│   THE HANDS   │ │   THE EYES    │             │   THE EARS    │   │   THE VOICE   │
│  (OS & Web)   │ │ (Screen/GUI)  │             │  (Mic / STT)  │   │  (Neural TTS) │
├───────────────┤ ├───────────────┤             ├───────────────┤   ├───────────────┤
│• Launch apps  │ │• Sub-50ms     │             │• Wake word    │   │• Zero-cost    │
│• Master vol   │ │  screen grab  │             │  "Hey TM"     │   │  edge-tts     │
│  & brightness │ │• Error OCR &  │             │• Whisper STT  │   │• British      │
│• PowerShell   │ │  visual debug │             │• Voice Activity│  │  JARVIS accent│
│• Safe recycle │ │• Fallback GUI │             │  Detection    │   │• Instant      │
│• Web search   │ │  clicking     │             │  (VAD)        │   │  barge-in cut │
└───────────────┘ └───────────────┘             └───────────────┘   └───────────────┘
```

- **⚡ Zero-Cost Intelligence (OmniRoute & OpenRouter)**: Integrates directly with [OmniRoute AI Gateway](https://www.omniroute.online/) (pooling free accounts/endpoints locally at `http://localhost:20128/v1`) and OpenRouter's high-performance free models (`llama-3.3-70b-instruct:free`, `gemini-2.0-flash-exp:free`, `deepseek-r1:free`, `qwen-2.5-coder-32b-instruct:free`). Includes automatic rate-limit failover and local Ollama support.
- **🛡️ Configurable Permission Guard**: Three security tiers (`STRICT`, `BALANCED`, `AUTONOMOUS`) to control how much autonomy TM has over your system.
- **💻 Full Windows Hardware & OS Control**: Control master volume, mute, screen brightness, battery monitoring, and application lifecycles via direct Windows C-APIs (`pycaw`, `pywin32`, WMI).
- **📂 Safe Filesystem Operations**: Smart file search, automated directory cleanup (e.g. Downloads folder), and safe file recycling via Windows Recycle Bin (`send2trash`).
- **🌐 Web & Research Engine**: Unlimited free live web searching via DuckDuckGo and web page content extraction; automated browser workflows via Playwright.
- **👁️ Multimodal Screen Vision**: Instant multi-monitor screenshot capture (`mss`) allowing TM to analyze error dialogs, terminal logs, and diagrams directly on your screen.
- **🎙️ Hands-Free Voice Pipeline**: Local wake-word detection ("Hey TM"), fast speech recognition (Whisper), and Microsoft Edge Neural TTS featuring JARVIS-style British speech (`en-GB-RyanNeural`) with full barge-in interruption.
- **🎛️ 4 Switchable Interfaces**: Rich Terminal CLI, Hands-Free Voice Mode, Windows System Tray Daemon with `Ctrl+Space` global hotkey, and a Floating HUD Widget.

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Operating System**: Windows 10 or Windows 11 (64-bit)
- **Runtime**: Python 3.12 or 3.13
- **Git**: Installed and available in PATH
- **OpenRouter Free API Key**: Get a free key at [openrouter.ai](https://openrouter.ai/keys) (No credit card required).

### 2. Installation
```powershell
# Clone or navigate to the repository
cd c:\Users\inzam\RND\treatman

# Create and activate a Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install project dependencies
pip install -e .
```

### 3. Configuration
Copy the template `.env.example` file to `.env`:
```powershell
Copy-Item .env.example .env
```
Choose your AI Gateway in `.env`:
- **Option A (OmniRoute - Recommended for multi-account free pools)**:
  If running [OmniRoute](https://www.omniroute.online/) locally (default `http://localhost:20128/v1`), TM connects automatically!
  ```env
  OMNIROUTE_BASE_URL=http://localhost:20128/v1
  OMNIROUTE_API_KEY=your-omniroute-dashboard-key-if-set
  ```
- **Option B (OpenRouter Free Tier)**:
  Paste your free key from [openrouter.ai/keys](https://openrouter.ai/keys):
  ```env
  OPENROUTER_API_KEY=sk-or-v1-your-free-key-here
  ```

Review or customize your autonomy level in `config.yaml`:
```yaml
autonomy:
  level: "balanced" # Options: strict | balanced | autonomous
```

### 4. Running TM
Launch in your preferred interface mode:

```powershell
# 1. Interactive Rich Terminal CLI (Fastest for testing)
python run_tm.py --cli

# 2. Hands-Free Voice Mode ("Hey TM")
python run_tm.py --voice

# 3. Background System Tray Daemon (Summon via Ctrl + Space)
python run_tm.py --daemon

# 4. Floating HUD Desktop Widget
python run_tm.py --hud
```

---

## 🎮 Interface Modes

| Mode | Command | Description |
| :--- | :--- | :--- |
| **CLI Console** | `python run_tm.py --cli` | Developer-first command center with live streaming tokens, status spinners, syntax highlighting, and approval prompts. |
| **Voice Mode** | `python run_tm.py --voice` | Always-on microphone listener with "Hey TM" wake word, VAD speech-to-text, and natural neural voice responses. |
| **Background Daemon** | `python run_tm.py --daemon` | Sits quietly in your Windows system tray. Press `Ctrl + Space` anywhere in Windows to trigger audio listening or prompt input. |
| **Floating HUD** | `python run_tm.py --hud` | Sleek, translucent Iron Man-inspired desktop overlay showing agent thoughts, audio waveforms, and status pills. |

---

## 📁 Repository Structure

```
treatman/
├── config.yaml                   # Global user settings (autonomy, models, voice, paths)
├── .env.example                  # Environment template for API keys
├── run_tm.py                     # Central CLI launcher with mode switches
├── pyproject.toml                # Project packaging and dependencies
│
├── tm/
│   ├── __init__.py
│   ├── config.py                 # Configuration loader and environment validator
│   │
│   ├── core/
│   │   ├── agent.py              # Main ReAct loop with multi-step reasoning
│   │   ├── llm_router.py         # OpenRouter free model router with failover pool
│   │   ├── persona.py            # JARVIS system prompts and behavioral guidelines
│   │   ├── guardrails.py         # Permission validator (Strict / Balanced / Autonomous)
│   │   └── memory.py             # SQLite session history & long-term preferences
│   │
│   ├── tools/
│   │   ├── base.py               # Abstract Tool definition and schema generator
│   │   ├── system_tools.py       # Apps, volume, brightness, battery, processes
│   │   ├── shell_tools.py        # Safe PowerShell execution with regex blocker
│   │   ├── file_tools.py         # Smart search, auto-organizer, safe recycling
│   │   ├── web_tools.py          # Free DuckDuckGo search & page markdown scraper
│   │   └── vision_tools.py       # High-speed screen grab & GUI automation
│   │
│   ├── voice/
│   │   ├── ear.py                # Microphone listener & Whisper speech-to-text
│   │   ├── speaker.py            # Edge-TTS synthesizer with instant barge-in
│   │   └── wakeword.py           # "Hey TM" wake word engine
│   │
│   └── interfaces/
│       ├── cli.py                # Interactive Rich console interface
│       ├── daemon.py             # Windows system tray daemon & global hotkeys
│       └── hud.py                # Floating translucent desktop widget
│
├── docs/
│   ├── ARCHITECTURE.md           # Deep-dive architectural specification
│   ├── CONFIGURATION.md          # Comprehensive settings & .env reference
│   ├── TOOLS_REFERENCE.md        # Complete catalog of all agent tools & schemas
│   ├── VOICE_AND_VISION_GUIDE.md # Voice pipeline, VAD, and screen vision guide
│   └── ROADMAP.md                # Development milestones and checklist
```

---

## 🔒 Safety & Guardrail Tiers

TM is built with safety as a first-class citizen:

```
               ┌─────────────────────────────────────┐
               │          Command Intercept          │
               └──────────────────┬──────────────────┘
                                  │
      ┌───────────────────────────┼───────────────────────────┐
      ▼                           ▼                           ▼
┌───────────────┐           ┌───────────────┐           ┌───────────────┐
│    TIER 1     │           │    TIER 2     │           │    TIER 3     │
│  Safe / Read  │           │ Low-Risk Mod  │           │ Critical/High │
├───────────────┤           ├───────────────┤           ├───────────────┤
│• Read files   │           │• Launch apps  │           │• Delete files │
│• Check stats  │           │• Change vol   │           │• Shell write  │
│• Web search   │           │• Open URLs    │           │• System lock  │
├───────────────┤           ├───────────────┤           ├───────────────┤
│ Auto-executed │           │ Auto-executed │           │ USER APPROVAL │
│ immediately   │           │ and logged    │           │ REQUIRED      │
└───────────────┘           └───────────────┘           └───────────────┘
```

- **Permanent Deletion Blocked**: File deletions use `send2trash` to move items to the Windows Recycle Bin.
- **Destructive Command Filter**: Commands such as `format`, `rmdir /s /q c:\`, and `Drop-Database` are hard-blocked by an AST/regex guardrail.
- **Audit Log**: Every executed tool call and shell command is recorded to `~/.treatman/audit.log` for full visibility.

---

## 📖 Documentation Index

- **[System Specification](file:///c:/Users/inzam/RND/treatman/TM_SYSTEM_SPECIFICATION.md)** — Comprehensive architecture blueprint.
- **[Architecture Deep-Dive](file:///c:/Users/inzam/RND/treatman/docs/ARCHITECTURE.md)** — ReAct loop, model routing, and state machine.
- **[Configuration Reference](file:///c:/Users/inzam/RND/treatman/docs/CONFIGURATION.md)** — Options, model lists, and permission settings.
- **[Tools Reference](file:///c:/Users/inzam/RND/treatman/docs/TOOLS_REFERENCE.md)** — Complete schema documentation for all 25+ tools.
- **[Voice & Vision Guide](file:///c:/Users/inzam/RND/treatman/docs/VOICE_AND_VISION_GUIDE.md)** — Audio VAD, edge-tts, wake-word, and screen capture.
- **[Roadmap](file:///c:/Users/inzam/RND/treatman/docs/ROADMAP.md)** — Milestone delivery checklist.

---

## 📄 License
This project is licensed under the MIT License.

