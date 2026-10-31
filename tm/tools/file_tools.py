"""
TM Filesystem Tools (Search, Organize, Read, Write, Recycle)
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from tm.tools.base import tool

try:
    import send2trash
except ImportError:
    send2trash = None


FILE_CATEGORIES = {
    "Images": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg", ".ico"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv", ".md"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso"],
    "Installers": [".exe", ".msi", ".dmg", ".pkg"],
    "Audio": [".mp3", ".wav", ".flac", ".m4a", ".aac"],
    "Video": [".mp4", ".mkv", ".mov", ".avi", ".wmv"],
    "Code": [".py", ".js", ".ts", ".html", ".css", ".json", ".yaml", ".yml", ".rs", ".go"],
}


@tool(
    name="search_files",
    description="Recursively searches for files matching a pattern or keyword in a directory.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Filename keyword or glob pattern (e.g. '*.pdf', 'invoice', 'report').",
            },
            "root_path": {
                "type": "string",
                "description": "Directory to search in. Defaults to user's home folder.",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return (default: 20).",
                "default": 20,
            },
        },
        "required": ["query"],
    },
    tier=1,
)
def search_files(
    query: str,
    root_path: Optional[str] = None,
    max_results: int = 20,
) -> Dict[str, Any]:
    root = Path(root_path).expanduser() if root_path else Path.home()
    if not root.exists():
        return {"status": "error", "message": f"Path '{root}' does not exist."}

    results: List[str] = []
    pattern = f"*{query}*" if not any(c in query for c in "*?[]") else query

    try:
        for p in root.rglob(pattern):
            if p.is_file():
                results.append(str(p))
                if len(results) >= max_results:
                    break
        return {"status": "success", "count": len(results), "matches": results}
    except Exception as e:
        return {"status": "error", "message": f"Search failed: {e}"}


@tool(
    name="organize_directory",
    description="Automatically organizes cluttered files in a folder (such as Downloads or Desktop) into categorized subfolders (Images, Documents, Installers, Archives, etc.).",
    parameters={
        "type": "object",
        "properties": {
            "directory_path": {
                "type": "string",
                "description": "Folder path to organize (e.g. 'Downloads', 'Desktop', or full path).",
            }
        },
        "required": ["directory_path"],
    },
    tier=2,
)
def organize_directory(directory_path: str) -> Dict[str, Any]:
    dir_lower = directory_path.lower().strip()
    if dir_lower == "downloads":
        target_dir = Path.home() / "Downloads"
    elif dir_lower == "desktop":
        target_dir = Path.home() / "Desktop"
    else:
        target_dir = Path(directory_path).expanduser()

    if not target_dir.exists() or not target_dir.is_dir():
        return {"status": "error", "message": f"Directory '{target_dir}' not found."}

    moved_summary: Dict[str, int] = {}

    try:
        for item in target_dir.iterdir():
            if item.is_file():
                ext = item.suffix.lower()
                destination_category = "Others"
                for category, extensions in FILE_CATEGORIES.items():
                    if ext in extensions:
                        destination_category = category
                        break

                cat_folder = target_dir / destination_category
                cat_folder.mkdir(exist_ok=True)
                dest_file = cat_folder / item.name

                # Avoid overwriting
                if dest_file.exists():
                    dest_file = cat_folder / f"{item.stem}_{int(os.path.getmtime(item))}{item.suffix}"

                try:
                    shutil.move(str(item), str(dest_file))
                    moved_summary[destination_category] = moved_summary.get(destination_category, 0) + 1
                except Exception:
                    pass

        total_moved = sum(moved_summary.values())
        return {
            "status": "success",
            "message": f"Organized {total_moved} files in '{target_dir}'.",
            "breakdown": moved_summary,
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to organize directory: {e}"}


@tool(
    name="read_file_content",
    description="Reads lines of text from a specified file path.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Absolute or relative file path."},
            "start_line": {"type": "integer", "description": "Starting line number (1-based).", "default": 1},
            "max_lines": {"type": "integer", "description": "Max lines to read.", "default": 200},
        },
        "required": ["path"],
    },
    tier=1,
)
def read_file_content(path: str, start_line: int = 1, max_lines: int = 200) -> Dict[str, Any]:
    file_path = Path(path).expanduser()
    if not file_path.exists() or not file_path.is_file():
        return {"status": "error", "message": f"File '{file_path}' does not exist."}

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        total = len(lines)
        start_idx = max(0, start_line - 1)
        end_idx = min(total, start_idx + max_lines)
        selected_lines = lines[start_idx:end_idx]

        return {
            "status": "success",
            "total_lines": total,
            "start_line": start_line,
            "lines_read": len(selected_lines),
            "content": "".join(selected_lines),
        }
    except Exception as e:
        return {"status": "error", "message": f"Could not read file: {e}"}


@tool(
    name="write_file_content",
    description="Creates or appends text content to a file.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Target file path."},
            "content": {"type": "string", "description": "Text content to write."},
            "append": {"type": "boolean", "description": "If true, appends instead of overwriting.", "default": False},
        },
        "required": ["path", "content"],
    },
    tier=2,
)
def write_file_content(path: str, content: str, append: bool = False) -> Dict[str, Any]:
    file_path = Path(path).expanduser()
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        with open(file_path, mode, encoding="utf-8") as f:
            f.write(content)
        return {
            "status": "success",
            "message": f"Wrote {len(content)} characters to '{file_path}'.",
            "path": str(file_path),
        }
    except Exception as e:
        return {"status": "error", "message": f"Could not write to file: {e}"}


@tool(
    name="safe_delete_to_recycle_bin",
    description="Safely moves a file or folder into the Windows Recycle Bin so it can be restored if needed.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to file or folder to recycle."}
        },
        "required": ["path"],
    },
    tier=3,
)
def safe_delete_to_recycle_bin(path: str) -> Dict[str, Any]:
    target = Path(path).expanduser()
    if not target.exists():
        return {"status": "error", "message": f"Item '{target}' does not exist."}

    if send2trash is not None:
        try:
            send2trash.send2trash(str(target))
            return {"status": "success", "message": f"Safely moved to Recycle Bin: '{target}'."}
        except Exception as e:
            return {"status": "error", "message": f"Send2Trash error: {e}"}

    # Fallback to PowerShell Recycle Bin call
    method = "DeleteDirectory" if target.is_dir() else "DeleteFile"
    clean_target = str(target).replace("'", "''")
    ps_cmd = f"""
    Add-Type -AssemblyName Microsoft.VisualBasic
    [Microsoft.VisualBasic.FileIO.FileSystem]::{method}('{clean_target}', 'OnlyErrorDialogs', 'SendToRecycleBin')
    """
    try:
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], timeout=10)
        if res.returncode == 0:
            return {"status": "success", "message": f"Moved to Recycle Bin via Windows shell: '{target}'."}
    except Exception:
        pass

    return {"status": "error", "message": "Failed to send item to Recycle Bin."}

