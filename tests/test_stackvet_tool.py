"""
Unit tests for StackVet Tool Integration in TreatMan
"""

import shutil
import pytest
from tm.tools.base import registry
import tm.tools.shell_tools  # noqa: F401


def test_stackvet_tool_registration():
    tool = registry.get("stackvet_health_check")
    assert tool is not None
    assert tool.tier == 1
    assert "health" in tool.description.lower() or "audit" in tool.description.lower()


def test_stackvet_tool_execution():
    tool = registry.get("stackvet_health_check")
    assert tool is not None

    if shutil.which("stackvet") is None:
        pytest.skip("stackvet executable not found on system PATH")

    res = tool.execute()
    assert res.get("status") == "success"
    assert "health_score" in res
    assert isinstance(res["health_score"], int)
    assert res["health_score"] >= 80
    assert "grade" in res
    assert "vulnerabilities" in res
    assert res["vulnerabilities"] == 0
