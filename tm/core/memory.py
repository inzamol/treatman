"""
TM Memory and SQLite Audit Subsystem
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from tm.config import Config


class MemoryManager:
    def __init__(self, config: Config):
        self.config = config
        self.db_path = config.paths.data_dir / "tm.db"
        self._init_db()

    def _init_db(self) -> None:
        """Initializes tables for persistent user profile and audit telemetry."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profile (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    tool_name TEXT,
                    arguments TEXT,
                    status TEXT,
                    result TEXT,
                    duration_ms INTEGER
                )
            """)
            conn.commit()
        except Exception as e:
            print(f"[Warning] SQLite init error: {e}")
        finally:
            if conn:
                conn.close()

    def get_preference(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Fetch a saved preference from long-term memory."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM user_profile WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else default
        except Exception:
            return default
        finally:
            if conn:
                conn.close()

    def set_preference(self, key: str, value: str) -> None:
        """Store or update a preference in long-term memory."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO user_profile (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (key, value)
            )
            conn.commit()
        except Exception as e:
            print(f"[Warning] Failed to set preference: {e}")
        finally:
            if conn:
                conn.close()

    def record_audit(self, tool_name: str, args: Dict[str, Any], status: str, result: str, duration_ms: int = 0) -> None:
        """Records an execution event to the permanent audit log."""
        conn = None
        try:
            now_str = datetime.now().isoformat()
            args_str = json.dumps(args, default=str)
            # Truncate long results if necessary
            res_str = result[:2000] if result else ""
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO audit_log (timestamp, tool_name, arguments, status, result, duration_ms) VALUES (?, ?, ?, ?, ?, ?)",
                (now_str, tool_name, args_str, status, res_str, duration_ms)
            )
            conn.commit()
        except Exception as e:
            print(f"[Warning] Failed to record audit log: {e}")
        finally:
            if conn:
                conn.close()

    def get_recent_audit_logs(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Returns the most recent audit events."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, timestamp, tool_name, arguments, status, result, duration_ms FROM audit_log ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": r[0],
                    "timestamp": r[1],
                    "tool_name": r[2],
                    "arguments": r[3],
                    "status": r[4],
                    "result": r[5],
                    "duration_ms": r[6],
                }
                for r in rows
            ]
        except Exception:
            return []
        finally:
            if conn:
                conn.close()
