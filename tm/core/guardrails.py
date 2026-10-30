"""
TM Security Guardrails & Permission Evaluator
"""

import re
from typing import Tuple, Dict, Any
from tm.config import Config


class GuardrailManager:
    def __init__(self, config: Config):
        self.config = config

    def check_command_safety(self, command: str) -> Tuple[bool, str]:
        """
        Scans a shell command string against the hard-forbidden command blocklist.
        Returns: (is_safe, error_reason)
        """
        cmd_lower = command.lower().strip()

        for forbidden in self.config.autonomy.forbidden_commands:
            pattern = re.escape(forbidden.lower())
            if re.search(pattern, cmd_lower):
                return False, f"Command contains forbidden expression: '{forbidden}'"

        # Additional regex heuristics for dangerous system commands
        dangerous_patterns = [
            r"\bformat\s+[a-z]:",
            r"\bdel\s+.*[/\\]\*.*",
            r"rmdir\s+.*[/\\]s.*",
            r"remove-item\s+.*-recurse.*[c-z]:\\",
            r"\bdrop\s+database\b",
            r"\btruncate\s+table\b",
        ]

        for pat in dangerous_patterns:
            if re.search(pat, cmd_lower):
                return False, f"Command matches destructive pattern: '{pat}'"

        return True, ""

    def evaluate_tool_permission(self, tool_name: str, args: Dict[str, Any]) -> Tuple[bool, bool, str]:
        """
        Evaluates whether a tool invocation is allowed, blocked, or requires confirmation.
        Returns: (is_allowed, requires_confirmation, message)
        """
        level = self.config.autonomy.level
        rules = self.config.autonomy.rules

        # 1. Shell commands safety scan
        if tool_name == "execute_powershell":
            cmd = str(args.get("command", ""))
            is_safe, reason = self.check_command_safety(cmd)
            if not is_safe:
                return False, False, f"Blocked by security policy: {reason}"

            if level == "strict" or rules.get("require_confirmation_for_shell_execution", False):
                return True, True, f"Execute PowerShell command: '{cmd}'"
            return True, False, ""

        # 2. File deletions
        if tool_name in ["safe_delete_to_recycle_bin", "delete_file"]:
            path = str(args.get("path", ""))
            if level in ["strict", "balanced"] or rules.get("require_confirmation_for_file_delete", True):
                return True, True, f"Recycle/Delete file or directory: '{path}'"
            return True, False, ""

        # 3. Process termination
        if tool_name == "close_app":
            app = str(args.get("app_name", ""))
            if level == "strict" or rules.get("require_confirmation_for_process_kill", True):
                return True, True, f"Terminate application/process: '{app}'"
            return True, False, ""

        # 4. System power actions
        if tool_name in ["lock_workstation", "system_sleep", "system_reboot"]:
            if level in ["strict", "balanced"] or rules.get("require_confirmation_for_system_power", True):
                return True, True, f"Trigger system action: '{tool_name}'"
            return True, False, ""

        # 5. Strict mode blanket confirmation for state modifications
        if level == "strict":
            if tool_name in ["write_file_content", "organize_directory", "install_winget_package", "set_volume", "set_brightness"]:
                return True, True, f"Execute state-changing tool: '{tool_name}' with args {args}"

        # Otherwise allowed immediately
        return True, False, ""

