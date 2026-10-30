"""
TM Developer & Terminal Tools (PowerShell, Git, Winget)
"""

import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional
from tm.tools.base import tool


@tool(
    name="execute_powershell",
    description="Executes a PowerShell command or script on this laptop and captures stdout, stderr, and exit code.",
    parameters={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The exact PowerShell command to run (e.g. 'git status', 'npm run build', 'dir').",
            },
            "working_dir": {
                "type": "string",
                "description": "Optional working directory path.",
            },
            "timeout_seconds": {
                "type": "integer",
                "description": "Execution timeout in seconds (default: 60).",
                "default": 60,
            },
        },
        "required": ["command"],
    },
    tier=3,
)
def execute_powershell(
    command: str,
    working_dir: Optional[str] = None,
    timeout_seconds: int = 60,
) -> Dict[str, Any]:
    start_time = time.time()
    cwd = Path(working_dir) if working_dir else Path.cwd()

    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        duration_ms = int((time.time() - start_time) * 1000)
        return {
            "exit_code": res.returncode,
            "stdout": res.stdout.strip(),
            "stderr": res.stderr.strip(),
            "duration_ms": duration_ms,
        }
    except subprocess.TimeoutExpired:
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Command timed out after {timeout_seconds} seconds.",
            "duration_ms": int((time.time() - start_time) * 1000),
        }
    except Exception as e:
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Execution error: {e}",
            "duration_ms": int((time.time() - start_time) * 1000),
        }


@tool(
    name="git_status",
    description="Returns the current Git status of a project repository.",
    parameters={
        "type": "object",
        "properties": {
            "repo_path": {
                "type": "string",
                "description": "Path to the git repository (defaults to current working directory).",
            }
        },
    },
    tier=1,
)
def git_status(repo_path: Optional[str] = None) -> Dict[str, Any]:
    cwd = repo_path if repo_path else str(Path.cwd())
    try:
        res = subprocess.run(
            ["git", "status", "--short", "--branch"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if res.returncode == 0:
            return {"status": "success", "output": res.stdout.strip()}
        return {"status": "error", "message": res.stderr.strip()}
    except Exception as e:
        return {"status": "error", "message": f"Git command failed: {e}"}


@tool(
    name="install_winget_package",
    description="Installs or updates a Windows package using the native Windows Package Manager (winget).",
    parameters={
        "type": "object",
        "properties": {
            "package_id": {
                "type": "string",
                "description": "Winget package ID or name (e.g. 'VideoLAN.VLC', 'Spotify.Spotify', 'Git.Git').",
            }
        },
        "required": ["package_id"],
    },
    tier=3,
)
def install_winget_package(package_id: str) -> Dict[str, Any]:
    cmd = f"winget install --id {package_id} --silent --accept-package-agreements --accept-source-agreements"
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        if res.returncode == 0:
            return {"status": "success", "message": f"Successfully installed {package_id}."}
        return {"status": "error", "message": res.stdout.strip() or res.stderr.strip()}
    except Exception as e:
        return {"status": "error", "message": f"Winget installation failed: {e}"}


@tool(
    name="stackvet_health_check",
    description="Runs StackVet Universal Project Health audit on a codebase to evaluate dependencies, vulnerabilities, architecture, and overall score (0-100, Grade A-F).",
    parameters={
        "type": "object",
        "properties": {
            "project_path": {
                "type": "string",
                "description": "Path to the project directory to audit (defaults to current project).",
            }
        },
    },
    tier=1,
)
def stackvet_health_check(project_path: Optional[str] = None) -> Dict[str, Any]:
    import json
    cwd = project_path if project_path else str(Path.cwd())
    try:
        res = subprocess.run(
            ["stackvet", "doctor", "-f", "json"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if res.returncode == 0 and res.stdout.strip():
            try:
                data = json.loads(res.stdout)
                return {
                    "status": "success",
                    "health_score": data.get("health_score"),
                    "grade": data.get("grade"),
                    "total_issues": data.get("summary", {}).get("total_issues", 0),
                    "critical": data.get("summary", {}).get("critical_count", 0),
                    "errors": data.get("summary", {}).get("error_count", 0),
                    "warnings": data.get("summary", {}).get("warning_count", 0),
                    "vulnerabilities": data.get("summary", {}).get("vulnerability_check", {}).get("vulnerabilities_found", 0),
                    "root_causes": data.get("root_causes", []),
                }
            except Exception:
                return {"status": "success", "raw_output": res.stdout.strip()[:1000]}
        return {"status": "error", "message": res.stderr.strip() or res.stdout.strip()}
    except Exception as e:
        return {"status": "error", "message": f"StackVet execution failed: {e}"}


