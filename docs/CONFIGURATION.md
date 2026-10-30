# TM Configuration Guide

This guide explains how to customize and configure **TM (TreatMan)**. Configuration is managed through two primary files:
1. `config.yaml` — Operational behavior, autonomy rules, voice options, and interface settings.
2. `.env` — Secrets and API keys (such as `OPENROUTER_API_KEY`).

---

## 1. `config.yaml` Reference

The main configuration file is located at the root of the project: `c:\Users\inzam\RND\treatman\config.yaml`.

```yaml
# ==============================================================================
# TM (TreatMan) Configuration File
# ==============================================================================

# 1. AGENT IDENTITY & PERSONA
agent:
  name: "TM"
  user_title: "Sir"                # How TM addresses you (e.g. "Sir", "Boss", your name)
  persona_style: "jarvis"          # Options: "jarvis" | "minimal" | "technical"
  max_react_turns: 10              # Max reasoning steps per command before stopping

# 2. AUTONOMY & PERMISSION GUARDRAILS
autonomy:
  level: "balanced"                # Master Level: "strict" | "balanced" | "autonomous"
  
  # Granular Action Permissions
  rules:
    allow_app_launch: true
    allow_app_close: true
    allow_system_volume_brightness: true
    allow_web_browsing: true
    allow_file_reading: true
    allow_file_writing: true
    require_confirmation_for_file_delete: true
    require_confirmation_for_shell_execution: false
    require_confirmation_for_process_kill: true
    require_confirmation_for_system_power: true # Sleep, restart, shutdown

  # Command Blocklist (Commands hard-rejected regardless of autonomy mode)
  forbidden_commands:
    - "format "
    - "rmdir /s /q c:\\"
    - "Remove-Item -Recurse -Force C:\\"
    - "del /f /s /q c:\\"
    - "diskpart"
    - "bcdedit"
    - "Drop-Database"
    - "TRUNCATE TABLE"
    - "Stop-Computer"

# 3. LLM BRAIN & GATEWAY ROUTING
llm:
  provider: "auto"                 # Options: "auto" (OmniRoute -> OpenRouter -> Ollama) | "omniroute" | "openrouter" | "ollama"
  temperature: 0.2                 # Low temperature for precise tool execution

  # OmniRoute AI Gateway (https://www.omniroute.online/)
  omniroute:
    enabled: true
    base_url: "http://localhost:20128/v1" # Local OmniRoute gateway or custom URL
    model: "auto"                          # "auto" or specific model from your OmniRoute pool
  
  # Ranked pool of free models on OpenRouter (tried in order)
  free_models:
    - "meta-llama/llama-3.3-70b-instruct:free"
    - "google/gemini-2.0-flash-exp:free"
    - "deepseek/deepseek-r1:free"
    - "qwen/qwen-2.5-coder-32b-instruct:free"
    - "mistralai/mistral-7b-instruct:free"

  # Local Offline Fallback (Ollama)
  ollama:
    enabled: true
    endpoint: "http://localhost:11434"
    model: "llama3.2:latest"

# 4. VOICE & AUDIO ENGINE
voice:
  enabled: true
  wake_word: "hey tm"              # Triggers listening in Voice/Daemon mode
  speech_to_text:
    engine: "whisper"              # Options: "whisper" | "google_cloud"
    model_size: "base.en"          # Options: "tiny.en" | "base.en" | "small.en"
    device: "auto"                 # Options: "auto" | "cuda" | "cpu"
    silence_threshold_seconds: 1.2 # VAD silence duration before processing speech
  
  text_to_speech:
    engine: "edge-tts"             # 100% Free Microsoft Edge Neural TTS
    voice: "en-GB-RyanNeural"      # Classic British JARVIS tone
    rate: "+0%"                    # Speech speed: e.g. "+5%", "-10%"
    pitch: "+0Hz"                  # Voice pitch
    barge_in: true                 # Stop speaking instantly when user starts talking

# 5. VISION & PERCEPTION
vision:
  enabled: true
  capture_active_window_only: false# If true, only screenshots the foreground app
  max_resolution: [1280, 720]      # Downsample to save tokens and latency
  jpeg_quality: 80                 # Screenshot compression quality

# 6. INTERFACES & HOTKEYS
interfaces:
  default_mode: "cli"              # Default when running `python run_tm.py`
  hotkeys:
    summon_agent: "ctrl+space"     # Global shortcut to activate TM
    push_to_talk: "win+shift+t"    # Global push-to-talk trigger
    stop_speaking: "escape"        # Instant kill-switch for audio speech
  
  hud:
    theme: "cyberpunk_dark"        # Options: "cyberpunk_dark" | "clean_light" | "ironman"
    opacity: 0.92                  # Window opacity (0.1 to 1.0)
    position: "bottom-right"       # Options: "bottom-right" | "top-right" | "center"

# 7. PATHS & DIRECTORIES
paths:
  data_dir: "~/.treatman"          # Stores tm.db, audit.log, and downsampled cache
  recycle_bin_safety: true         # Always use Recycle Bin rather than permanent delete
```

---

## 2. Environment Variables (`.env`)

Secrets and API credentials must be stored in `.env`. An example template is provided in `.env.example`:

```env
# ==============================================================================
# TM Environment Variables
# ==============================================================================

# OmniRoute AI Gateway (https://www.omniroute.online/)
OMNIROUTE_BASE_URL=http://localhost:20128/v1
OMNIROUTE_API_KEY=
OMNIROUTE_MODEL=auto

# OpenRouter Free API Key (Get at https://openrouter.ai/keys)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Direct Gemini API Key
GEMINI_API_KEY=

# Optional: ElevenLabs Key (if you wish to use hyper-custom cloned voices)
ELEVENLABS_API_KEY=

# System Telemetry & Log Level
TM_LOG_LEVEL=INFO   # Options: DEBUG | INFO | WARNING | ERROR
```

---

## 3. Autonomy Levels Explained

You can switch TM's autonomy level at any time in `config.yaml`:

### Level 1: `strict`
- **Behavior**: TM acts as an advisor and plan-drafter.
- **Approvals**: Prompts for explicit user confirmation before **every** command that modifies your laptop state (writing files, killing processes, adjusting settings, launching terminal commands).
- **Best For**: First-time testing and sensitive production environments.

### Level 2: `balanced` (Default & Recommended)
- **Behavior**: TM operates smoothly for day-to-day productivity.
- **Approvals**: 
  - Automatically executes read operations, web searches, app launches, and volume adjustments.
  - Prompts for confirmation before **deleting files**, **terminating processes**, or executing **destructive shell commands**.
- **Best For**: Everyday daily driver workflows.

### Level 3: `autonomous` (JARVIS Mode)
- **Behavior**: True hands-free autonomous assistant.
- **Approvals**: Executes multi-step plans without interruptions. Hard-blocked commands (e.g. disk formatting) remain strictly prohibited.
- **Best For**: Hands-free voice operation while multitasking.

---

## 4. Voice Configuration

TM uses Microsoft's **Edge-TTS** engine, providing dozens of natural human neural voices at zero cost.

### Popular Voice Selections:
| Voice ID | Accent | Persona Description |
| :--- | :--- | :--- |
| `en-GB-RyanNeural` *(Default)* | British (UK) | Classic, calm, distinguished butler/JARVIS tone |
| `en-GB-SoniaNeural` | British (UK) | Professional, clear, modern British female voice |
| `en-US-GuyNeural` | American (US) | Crisp, casual American male voice |
| `en-US-AriaNeural` | American (US) | Warm, expressive American female voice |
| `en-AU-WilliamNeural` | Australian (AU)| Relaxed, friendly Australian male voice |

To change the voice, simply update `voice.text_to_speech.voice` in `config.yaml`.

