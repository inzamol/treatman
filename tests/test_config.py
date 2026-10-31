"""
Unit tests for TM Configuration and Environment Parsing
"""

import tempfile
from pathlib import Path
from tm.config import Config, load_env_file


def test_default_config_structure():
    cfg = Config()
    assert cfg.agent.name == "TM"
    assert cfg.agent.user_title == "Sir"
    assert cfg.autonomy.level == "balanced"
    assert cfg.llm.provider in ["auto", "omniroute", "openrouter", "ollama"]
    assert cfg.voice.enabled is True
    assert cfg.paths.recycle_bin_safety is True
    assert cfg.interfaces.default_mode == "cli"
    assert cfg.interfaces.hotkeys.summon_agent == "ctrl+space"
    assert cfg.vision.enabled is True
    assert cfg.vision.max_resolution == [1280, 720]


def test_env_loader():
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".env", encoding="utf-8") as f:
        f.write("# Sample env file\n")
        f.write("TEST_CUSTOM_KEY_ABC=testing_value_xyz\n")
        f.write("TEST_QUOTED_KEY=\"quoted_val\"\n")
        env_path = Path(f.name)

    import os
    try:
        load_env_file(env_path)
        assert os.environ.get("TEST_CUSTOM_KEY_ABC") == "testing_value_xyz"
        assert os.environ.get("TEST_QUOTED_KEY") == "quoted_val"
    finally:
        os.environ.pop("TEST_CUSTOM_KEY_ABC", None)
        os.environ.pop("TEST_QUOTED_KEY", None)
        env_path.unlink(missing_ok=True)

