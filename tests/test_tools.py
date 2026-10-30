"""
Unit tests for TM Tools and Memory Audit
"""

import tempfile
from pathlib import Path
from tm.config import Config
from tm.core.memory import MemoryManager
from tm.tools.base import registry
import tm.tools


def test_registry_populated():
    tools = registry.list_all()
    assert len(tools) >= 15
    tool_names = [t.name for t in tools]
    assert "launch_app" in tool_names
    assert "set_volume" in tool_names
    assert "get_system_stats" in tool_names
    assert "search_files" in tool_names
    assert "execute_powershell" in tool_names


def test_system_stats_tool():
    tool = registry.get("get_system_stats")
    assert tool is not None
    stats = tool.execute()
    assert "cpu_percent" in stats
    assert "memory_used_gb" in stats


def test_file_read_write_tool():
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
        tmp_path = tmp.name

    write_tool = registry.get("write_file_content")
    res = write_tool.execute(path=tmp_path, content="Hello TM Agent!")
    assert res["status"] == "success"

    read_tool = registry.get("read_file_content")
    read_res = read_tool.execute(path=tmp_path)
    assert read_res["status"] == "success"
    assert "Hello TM Agent!" in read_res["content"]

    Path(tmp_path).unlink(missing_ok=True)


def test_memory_and_audit():
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = Config()
        cfg.paths.data_dir = Path(tmpdir)
        mem = MemoryManager(cfg)

        mem.set_preference("user_title", "Tony")
        assert mem.get_preference("user_title") == "Tony"

        mem.record_audit("test_tool", {"arg": 1}, "success", "result_ok", 12)
        logs = mem.get_recent_audit_logs()
        assert len(logs) == 1
        assert logs[0]["tool_name"] == "test_tool"

