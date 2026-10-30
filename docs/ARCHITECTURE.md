# TM Architecture Specification

This document details the internal design, component interactions, and execution lifecycles of **TM (TreatMan)**.

---

## 1. High-Level Component Topology

```
+-------------------------------------------------------------------------------------------------------+
|                                        INTERACTION LAYER                                              |
|                                                                                                       |
|  [Rich CLI Terminal]      [Voice Pipeline]       [Windows System Tray]       [Floating HUD Widget]    |
|   - Streaming output       - Wake-word listener   - Global hotkey listener    - Translucent overlay   |
|   - Status spinners        - Whisper STT          - Background daemon         - Waveform visualizer   |
|   - Interactive approval   - Edge-TTS speaker     - Notification popups       - Thought stream        |
+---------------------------------------------------+---------------------------------------------------+
                                                    │
                                                    ▼
+-------------------------------------------------------------------------------------------------------+
|                                         AGENT CORE BRAIN                                              |
|                                                                                                       |
|  +------------------------+  +------------------------+  +-----------------------------------------+  |
|  |     Agent Orchestrator |  |   OpenRouter Router    |  |               Memory Engine             |  |
|  |  - ReAct Execution Loop|  |  - Free Model Failover |  |  - Sliding session conversation window  |  |
|  |  - Multi-step Planning |  |  - Rate-limit Retries  |  |  - SQLite Persistent User Profile       |  |
|  |  - Error Auto-Recovery |  |  - Ollama Local Fallback| |  - Audit Telemetry Logger               |  |
|  +------------------------+  +------------------------+  +-----------------------------------------+  |
|                                                                                                       |
|  +-------------------------------------------------------------------------------------------------+  |
|  |                                  Persona & Prompt Engine                                        |  |
|  |  - Calm, concise, respectful JARVIS personality ("Sir", proactive execution, zero fluff)        |  |
|  +-------------------------------------------------------------------------------------------------+  |
+---------------------------------------------------+---------------------------------------------------+
                                                    │
                                                    ▼
+-------------------------------------------------------------------------------------------------------+
|                                    SECURITY & GUARDRAIL LAYER                                         |
|                                                                                                       |
|  +-------------------------------------------------------------------------------------------------+  |
|  |                                    Permission Matrix Evaluator                                  |  |
|  |  - Level: STRICT | BALANCED | AUTONOMOUS                                                        |  |
|  |  - Per-Action Overrides (allow_app_launch, allow_web_browsing, require_confirmation_for_delete)   |  |
|  |  - AST & Regex Destructive Command Blocker (Hard-stops: format, rmdir /s /q c:\, Drop-Database) |  |
|  +-------------------------------------------------------------------------------------------------+  |
+---------------------------------------------------+---------------------------------------------------+
                                                    │
                                                    ▼
+-------------------------------------------------------------------------------------------------------+
|                                        UNIFIED TOOL REGISTRY                                          |
|                                                                                                       |
|  [System & Hardware]     [Developer & Shell]    [Filesystem]         [Web & Research]   [Screen Eyes]  |
|  - launch_app            - execute_powershell   - search_files       - web_search_ddg   - screen_grab  |
|  - close_app             - git_status           - organize_dir       - fetch_markdown   - inspect_win  |
|  - set_volume            - git_commit           - safe_delete        - playwright_browse- click_ui     |
|  - set_brightness        - winget_install       - read/write_file                                     |
|  - system_stats          - run_python_script                                                          |
+---------------------------------------------------+---------------------------------------------------+
                                                    │
                                                    ▼
+-------------------------------------------------------------------------------------------------------+
|                                      WINDOWS OS INTERFACES                                            |
|                                                                                                       |
|    Win32 / COM APIs        PowerShell Core        Core Audio (pycaw)        WMI / VCP Display         |
|    Windows Registry        Send2Trash             Windows UI Automation     MSS Screen Engine         |
+-------------------------------------------------------------------------------------------------------+
```

---

## 2. ReAct Execution Lifecycle

TM follows an augmented **Reasoning + Action (ReAct)** pattern with error self-correction and guardrail intervention:

```
        ┌─────────────────────────────────────────────────────────────┐
        │ 1. User Input Received (Voice transcript, CLI, or Hotkey)   │
        └──────────────────────────────┬──────────────────────────────┘
                                       │
                                       ▼
        ┌─────────────────────────────────────────────────────────────┐
        │ 2. Context Enrichment                                       │
        │    - Retrieve last N conversational turns                   │
        │    - Fetch user preferences & frequent paths from SQLite    │
        │    - Inject current system state (time, active window, OS)  │
        └──────────────────────────────┬──────────────────────────────┘
                                       │
                                       ▼
        ┌─────────────────────────────────────────────────────────────┐
        │ 3. LLM Reasoning Pass (OpenRouter Free Model)              │
        │    - Synthesize thought: What is the goal? What tool next?  │
        │    - Output Tool Call invocation in standard schema         │
        └──────────────────────────────┬──────────────────────────────┘
                                       │
                        ┌──────────────┴──────────────┐
                        ▼                             ▼
                 [Tool Call Emitted]          [Final Answer Generated]
                        │                             │
                        ▼                             ▼
        ┌─────────────────────────────┐       ┌────────────────────────┐
        │ 4. Guardrail Interception   │       │ Deliver to Interface   │
        │    - Check autonomy level   │       │ - Stream text to CLI   │
        │    - Scan for blocked cmd   │       │ - Synthesize speech    │
        │    - Request confirmation   │       │ - Update HUD waveform  │
        │      if Tier 3 or Strict    │       └────────────────────────┘
        └──────────────┬──────────────┘
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
       [Approved]            [Denied]
             │                   │
             ▼                   ▼
   ┌───────────────────┐ ┌───────────────────────────────────┐
   │ 5. Tool Execution │ │ Return Denial Observation to LLM  │
   │    via Windows API│ └─────────────────┬─────────────────┘
   └─────────┬─────────┘                   │
             │                             │
             ▼                             │
   ┌───────────────────┐                   │
   │ 6. Tool Result    │                   │
   │    Observation    │                   │
   └─────────┬─────────┘                   │
             │                             │
             └──────────────┬──────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────────────────────────────┐
        │ 7. Reflection & Loop Continuation                           │
        │    - If goal is satisfied -> Generate final JARVIS reply    │
        │    - If errors occurred -> Formulate recovery tool call     │
        │    - Max turns safety limit (Default: 10 steps)             │
        └─────────────────────────────────────────────────────────────┘
```

---

## 3. OpenRouter Free Model Routing Engine

### 3.1 Model Hierarchy
To ensure completely free operation with 99.9% uptime, TM maintains a ranked pool of free-tier endpoints:

```python
FREE_MODEL_ROUTING_POOL = [
    # Tier 1: Primary Reasoning & Tool Planning
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemini-2.0-flash-exp:free",
    "deepseek/deepseek-r1:free",
    
    # Tier 2: Coding & Script Analysis
    "qwen/qwen-2.5-coder-32b-instruct:free",
    
    # Tier 3: Fast Sub-tasks & Classification
    "mistralai/mistral-7b-instruct:free",
]
```

### 3.2 Dynamic Failover State Machine
When calling OpenRouter:
1. **Primary Request**: Send to the top-ranked active model.
2. **HTTP 429 (Rate Limit) / 503 (Overloaded)**: Catch status code, mark the current endpoint on a 60-second cooldown, and immediately replay the exact prompt to the next model in the pool.
3. **Context Length Handling**: If a model returns a context overflow, truncate previous tool observations using smart sliding-window condensation.
4. **Offline Fallback**: If network is disconnected or all OpenRouter models fail, automatically redirect to `http://localhost:11434/api/generate` (local Ollama instance).

---

## 4. Security & Guardrails Engine

The security engine inspects every action before the Python runtime touches the operating system.

### 4.1 Permission Matrix

| Operation Category | Default Tier | Strict Mode | Balanced Mode | Autonomous Mode |
| :--- | :---: | :---: | :---: | :---: |
| **System Read** (Battery, volume, running apps) | Tier 1 | Auto | Auto | Auto |
| **File Read** (Inspect code, read text files) | Tier 1 | Auto | Auto | Auto |
| **Web Search** (DuckDuckGo, fetch docs) | Tier 1 | Auto | Auto | Auto |
| **Hardware State** (Set volume, brightness) | Tier 2 | Confirm | Auto | Auto |
| **App Launch / Focus** | Tier 2 | Confirm | Auto | Auto |
| **Process Kill** (Terminate frozen app) | Tier 3 | Confirm | Confirm | Auto |
| **File Creation / Edit** | Tier 2 | Confirm | Auto | Auto |
| **File Deletion** (Move to Recycle Bin) | Tier 3 | Confirm | Confirm | Auto |
| **Shell Script Execution** (PowerShell) | Tier 3 | Confirm | Auto-filtered* | Auto-filtered* |
| **System Power** (Sleep, lock, reboot) | Tier 3 | Confirm | Confirm | Auto |

*\*Auto-filtered: In Balanced & Autonomous modes, safe shell commands run immediately, but commands matching the blocklist are hard-rejected.*

### 4.2 AST & Regex Blocklist
Commands containing the following signatures are **hard-blocked** regardless of autonomy mode:
- `format ` (Formatting physical drives)
- `rmdir /s /q c:\` or `Remove-Item -Recurse -Force C:\`
- `del /f /s /q c:\`
- `diskpart`
- `bcdedit`
- `Drop-Database` or `TRUNCATE TABLE`
- Deletion commands targeting `%WINDIR%` or `C:\Windows\System32`

---

## 5. Memory Architecture

```
                    ┌─────────────────────────────────┐
                    │          TM Memory Engine       │
                    └────────────────┬────────────────┘
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           ▼                                                   ▼
┌─────────────────────────────┐             ┌─────────────────────────────────────┐
│     Short-Term Memory       │             │       Long-Term Persistence         │
├─────────────────────────────┤             ├─────────────────────────────────────┤
│ • In-memory deque           │             │ SQLite Database (~/.treatman/tm.db) │
│ • Last 15 conversational    │             │                                     │
│   turns                     │             │ Tables:                             │
│ • Tool call & observation   │             │ 1. `user_profile`                   │
│   cache                     │             │    - Name, preferred player, etc.   │
│ • Downsampled image buffer  │             │ 2. `frequent_paths`                 │
│ • Cleared on session reset  │             │    - Project directories, bookmarks │
└─────────────────────────────┘             │ 3. `audit_log`                      │
                                            │    - Timestamp, tool, args, status  │
                                            └─────────────────────────────────────┘
```

1. **User Profile**: Key-value store storing your preferences:
   - Preferred code editor: `code`
   - Preferred browser: `chrome`
   - Music application: `spotify`
2. **Audit Log Table**:
   - Every single command, tool invocation, arguments, exit code, and timestamps are recorded immutably.
   - Queryable anytime via `python run_tm.py --audit` or by asking *"TM, what commands did you run today?"*.

---

## 6. Voice & Audio Architecture

```
Microphone In
     │
     ▼
[PyAudio Stream] ──► [Silero / WebRTC VAD] ──► [Silence Detected]
                             │
                             ▼
                    [faster-whisper STT]
                             │
                             ▼
                    [Prompt -> Agent Core]
                             │
                             ▼
                    [Agent Synthesizes Reply]
                             │
                             ▼
                    [edge-tts Engine] (en-GB-RyanNeural)
                             │
                             ▼
                    [Audio Playback Stream] ◄── [Barge-In Monitor]
                             │                        │
                             ▼                        │ (If user speaks or hits key)
                        Speakers Out ─────────────────┘ (INSTANT PLAYBACK CUTOFF)
```

1. **Local Wake-Word Detection**: Runs on a low-priority thread using `openWakeWord`. Continuously buffers 80ms audio frames. Triggers on *"Hey TM"*.
2. **Streaming VAD**: Uses Voice Activity Detection to automatically identify when you finish speaking, eliminating awkward manual pauses or push-to-talk delays.
3. **Full-Duplex Barge-In**: The audio player monitors keyboard and microphone inputs. The millisecond new audio or user interaction is detected while TM is talking, playback terminates instantly.

---

## 7. Multimodal Screen Perception Architecture

```
[Screen Grab Request] ──► [MSS Engine] (Captures active monitor in ~12ms)
                               │
                               ▼
                       [Pillow Processing]
                       - Identify active window bounds
                       - Downsample to max 1280x720 (reduces token load)
                       - Convert to base64 JPEG
                               │
                               ▼
                       [Multimodal Vision Model]
                       (e.g., google/gemini-2.0-flash-exp:free)
                               │
                               ▼
                       [Visual Analysis & Coordinate Extraction]
                               │
                               ▼
                       [PyAutoGUI / PyWinAuto Actuation]
```

1. **Active Window Cropping**: Rather than sending a 4K desktop to the model, TM crops to the active foreground window, keeping latency low and visual resolution sharp.
2. **UI Automation Hierarchy**: TM queries the Windows UI Automation tree first to find native element handles (buttons, textboxes). If the app is non-standard (e.g. game, custom canvas), it falls back to visual coordinate estimation.

