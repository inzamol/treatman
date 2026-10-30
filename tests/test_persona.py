"""
Unit tests for TM J.A.R.V.I.S. Persona and Prompt Generation
"""

from tm.config import Config
from tm.core.persona import get_system_prompt


def test_persona_system_prompt_defaults():
    cfg = Config()
    cfg.agent.name = "TM"
    cfg.agent.user_title = "Sir"
    cfg.autonomy.level = "balanced"

    prompt = get_system_prompt(cfg)
    assert "TM" in prompt
    assert "Sir" in prompt
    assert "BALANCED" in prompt
    assert "Windows 11" in prompt
    assert "J.A.R.V.I.S." in prompt


def test_persona_custom_title_and_agent_name():
    cfg = Config()
    cfg.agent.name = "JARVIS"
    cfg.agent.user_title = "Mr. Stark"
    cfg.autonomy.level = "autonomous"

    prompt = get_system_prompt(cfg)
    assert "JARVIS" in prompt
    assert "Mr. Stark" in prompt
    assert "AUTONOMOUS" in prompt

