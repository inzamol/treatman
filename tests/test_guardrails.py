"""
Unit tests for TM Security Guardrails
"""

from tm.config import Config
from tm.core.guardrails import GuardrailManager


def test_destructive_command_blocking():
    cfg = Config()
    guard = GuardrailManager(cfg)

    # Hard-forbidden commands
    safe, reason = guard.check_command_safety("format c: /fs:NTFS")
    assert not safe
    assert "forbidden" in reason.lower() or "destructive" in reason.lower()

    safe, reason = guard.check_command_safety("rmdir /s /q C:\\Windows")
    assert not safe

    safe, reason = guard.check_command_safety("Remove-Item -Recurse -Force C:\\")
    assert not safe

    # Safe command
    safe, reason = guard.check_command_safety("git status")
    assert safe
    assert reason == ""


def test_permission_matrix_levels():
    cfg = Config()
    cfg.autonomy.level = "balanced"
    guard = GuardrailManager(cfg)

    # Tier 1 read-only: allowed without confirmation
    allowed, confirm, _ = guard.evaluate_tool_permission("list_running_apps", {})
    assert allowed
    assert not confirm

    # Tier 2 safe mod in balanced: allowed without confirmation
    allowed, confirm, _ = guard.evaluate_tool_permission("set_volume", {"level": 50})
    assert allowed
    assert not confirm

    # Tier 3 delete in balanced: requires confirmation
    allowed, confirm, _ = guard.evaluate_tool_permission("safe_delete_to_recycle_bin", {"path": "test.txt"})
    assert allowed
    assert confirm

    # Switch to STRICT: requires confirmation even for volume
    cfg.autonomy.level = "strict"
    allowed, confirm, _ = guard.evaluate_tool_permission("set_volume", {"level": 50})
    assert allowed
    assert confirm

