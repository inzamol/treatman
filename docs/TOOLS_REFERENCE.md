# TM Tools Reference Catalog

This document provides the complete API reference for all native tools available to **TM (TreatMan)**. Every tool is defined with its function signature, parameter schemas, return value structure, and security permission tier.

---

## 1. System & Hardware Tools

### `launch_app`
Launches an installed Windows desktop application by its common name.
- **Permission Tier**: Tier 2 (Safe Modification)
- **Parameters**:
  - `app_name` (*string*, required): Name or executable alias of the application (e.g. `"Spotify"`, `"Chrome"`, `"VS Code"`, `"Notepad"`, `"Calculator"`).
- **Return**: `{"status": "success", "message": "Launched Spotify", "pid": 14208}`

### `close_app`
Gracefully closes or terminates an application.
- **Permission Tier**: Tier 3 (High-Risk - prompts in Strict/Balanced)
- **Parameters**:
  - `app_name` (*string*, required): Process or window name to terminate.
  - `force` (*boolean*, optional, default: `false`): If `true`, forcefully terminates the process tree (`SIGKILL`).
- **Return**: `{"status": "success", "message": "Terminated 2 instances of Spotify"}`

### `list_running_apps`
Returns all active applications currently running with visible windows.
- **Permission Tier**: Tier 1 (Safe Read-Only)
- **Parameters**: None
- **Return**: `{"running_apps": [{"name": "Code.exe", "title": "treatman - Visual Studio Code", "pid": 9840}, ...]}`

### `set_volume`
Sets the Windows master output volume to a specific percentage.
- **Permission Tier**: Tier 2 (Safe Modification)
- **Parameters**:
  - `level` (*integer*, required): Volume level from `0` (silent) to `100` (max).
- **Return**: `{"status": "success", "previous_volume": 40, "current_volume": 65}`

### `mute_audio`
Toggles or sets the audio mute state.
- **Permission Tier**: Tier 2 (Safe Modification)
- **Parameters**:
  - `mute` (*boolean*, required): `true` to mute, `false` to unmute.
- **Return**: `{"status": "success", "is_muted": true}`

### `set_brightness`
Adjusts the display brightness on supported laptop screens and monitors.
- **Permission Tier**: Tier 2 (Safe Modification)
- **Parameters**:
  - `percentage` (*integer*, required): Brightness level from `0` to `100`.
- **Return**: `{"status": "success", "brightness": 80}`

### `get_system_stats`
Queries real-time hardware metrics: CPU load, RAM usage, battery percentage, charging state, and uptime.
- **Permission Tier**: Tier 1 (Safe Read-Only)
- **Parameters**: None
- **Return**:
  ```json
  {
    "cpu_usage_percent": 14.2,
    "memory_used_gb": 11.4,
    "memory_total_gb": 31.8,
    "battery_percent": 88,
    "power_plugged": true,
    "os": "Windows 11 Pro 64-bit"
  }
  ```

### `lock_workstation`
Immediately locks the Windows user session.
- **Permission Tier**: Tier 3 (System Power)
- **Parameters**: None
- **Return**: `{"status": "success", "message": "Workstation locked"}`

---

## 2. Developer & Terminal Tools

### `execute_powershell`
Executes a PowerShell command or script block inside an asynchronous subprocess.
- **Permission Tier**: Tier 3 (Shell execution - checked against AST blocklist)
- **Parameters**:
  - `command` (*string*, required): The exact PowerShell command string (e.g., `git status`, `npm test`, `docker ps`).
  - `working_dir` (*string*, optional): Working directory path. Defaults to workspace.
  - `timeout_seconds` (*integer*, optional, default: `60`): Maximum execution time before aborting.
- **Return**:
  ```json
  {
    "exit_code": 0,
    "stdout": "On branch main\nYour branch is up to date with 'origin/main'.\n",
    "stderr": "",
    "execution_time_ms": 340
  }
  ```

### `git_status`
Specialized shortcut to query the git repository state in a directory.
- **Permission Tier**: Tier 1 (Safe Read-Only)
- **Parameters**:
  - `repo_path` (*string*, optional): Path to Git repository. Defaults to current directory.
- **Return**: `{"branch": "main", "staged": ["README.md"], "modified": ["config.py"], "untracked": []}`

### `install_winget_package`
Installs or updates a Windows application via the native Windows Package Manager (`winget`).
- **Permission Tier**: Tier 3 (Software Installation)
- **Parameters**:
  - `package_id` (*string*, required): Package ID or name (e.g. `"VideoLAN.VLC"`, `"Git.Git"`, `"Spotify.Spotify"`).
- **Return**: `{"status": "success", "message": "VLC media player installed successfully"}`

---

## 3. Filesystem Tools

### `search_files`
Recursively searches for files matching a wildcard pattern or keyword across directories.
- **Permission Tier**: Tier 1 (Safe Read-Only)
- **Parameters**:
  - `query` (*string*, required): Filename or glob pattern (e.g. `"*.pdf"`, `"invoice"`, `"budget_2026"`).
  - `root_path` (*string*, optional): Root directory to search. Defaults to user's home directory.
  - `max_results` (*integer*, optional, default: `20`): Limit on returned matches.
- **Return**: `{"matches": ["C:\\Users\\inzam\\Documents\\invoice_march.pdf", ...]}`

### `organize_directory`
Automatically categorizes and moves scattered files in a folder into organized subdirectories (`Images/`, `Documents/`, `Archives/`, `Installers/`, `Code/`).
- **Permission Tier**: Tier 2 (Safe Modification)
- **Parameters**:
  - `directory_path` (*string*, required): Directory to organize (e.g. `"Downloads"` or `"Desktop"`).
- **Return**: `{"status": "success", "moved_files": 42, "categories": ["Images (18)", "Documents (14)", "Archives (10)"]}`

### `read_file_content`
Reads text content from a local file with line range bounds.
- **Permission Tier**: Tier 1 (Safe Read-Only)
- **Parameters**:
  - `path` (*string*, required): Absolute path of the file.
  - `start_line` (*integer*, optional, default: `1`): First line to read.
  - `max_lines` (*integer*, optional, default: `500`): Maximum lines to return.
- **Return**: `{"content": "...", "total_lines": 140}`

### `write_file_content`
Creates or edits a file with specified content.
- **Permission Tier**: Tier 2 (Safe Modification)
- **Parameters**:
  - `path` (*string*, required): Target file path.
  - `content` (*string*, required): File contents to write.
  - `append` (*boolean*, optional, default: `false`): Append to end of file if `true`.
- **Return**: `{"status": "success", "bytes_written": 1024, "path": "..."}`

### `safe_delete_to_recycle_bin`
Moves a file or directory safely into the Windows Recycle Bin using `send2trash`.
- **Permission Tier**: Tier 3 (Deletion - confirmation required in Balanced mode)
- **Parameters**:
  - `path` (*string*, required): Path of file or folder to recycle.
- **Return**: `{"status": "success", "message": "Moved to Recycle Bin: C:\\Users\\...\\temp.zip"}`

---

## 4. Web & Research Tools

### `search_web_duckduckgo`
Conducts a live web search using DuckDuckGo (100% free, no API key required).
- **Permission Tier**: Tier 1 (Safe Read-Only)
- **Parameters**:
  - `query` (*string*, required): Search terms or question.
  - `max_results` (*integer*, optional, default: `5`): Maximum search results.
- **Return**:
  ```json
  {
    "results": [
      {
        "title": "Python 3.13 Release Notes",
        "url": "https://docs.python.org/3.13/whatsnew/",
        "snippet": "Python 3.13 introduces experimental free-threaded mode and JIT compiler..."
      }
    ]
  }
  ```

### `fetch_webpage_markdown`
Fetches a webpage, cleans boilerplate scripts/ads, and converts the core content into readable Markdown for LLM analysis.
- **Permission Tier**: Tier 1 (Safe Read-Only)
- **Parameters**:
  - `url` (*string*, required): The URL to scrape and format.
- **Return**: `{"title": "...", "markdown": "# Python 3.13...\n\nContent..."}`

---

## 5. Screen Eyes & Computer-Use Tools

### `capture_screen`
Captures a sub-50ms high-resolution screenshot of the desktop or active window.
- **Permission Tier**: Tier 1 (Safe Read-Only)
- **Parameters**:
  - `active_window_only` (*boolean*, optional, default: `false`): When `true`, clips strictly to the currently focused application window.
- **Return**: `{"status": "success", "image_base64": "...", "resolution": [1920, 1080], "active_window": "VS Code"}`

### `click_screen_coordinate`
Moves the mouse cursor and clicks a specified coordinate on the screen.
- **Permission Tier**: Tier 2 (GUI Actuation)
- **Parameters**:
  - `x` (*integer*, required): X coordinate in pixels.
  - `y` (*integer*, required): Y coordinate in pixels.
  - `button` (*string*, optional, default: `"left"`): `"left"`, `"right"`, or `"double"`.
- **Return**: `{"status": "success", "clicked_at": [960, 540]}`

### `type_text`
Sends keystrokes to the currently focused input element.
- **Permission Tier**: Tier 2 (GUI Actuation)
- **Parameters**:
  - `text` (*string*, required): String of text to type.
  - `press_enter` (*boolean*, optional, default: `false`): Simulates pressing `Enter` after typing.
- **Return**: `{"status": "success", "typed_characters": 18}`

