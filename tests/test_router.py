"""
Unit tests for TM LLM Router (OmniRoute and OpenRouter)
"""

from tm.config import Config
from tm.core.llm_router import LLMRouter


def test_omniroute_config():
    cfg = Config()
    assert cfg.llm.omniroute_enabled is True
    assert "omniroute" in cfg.llm.omniroute_base_url.lower() or "20128" in cfg.llm.omniroute_base_url
    assert cfg.llm.omniroute_model == "auto"


def test_router_provider_modes():
    cfg = Config()
    
    # Auto mode
    cfg.llm.provider = "auto"
    router = LLMRouter(cfg)
    assert "auto" in router.get_active_model()

    # OmniRoute mode
    cfg.llm.provider = "omniroute"
    cfg.llm.omniroute_model = "claude-3-5-sonnet"
    router = LLMRouter(cfg)
    assert router.get_active_model() == "omniroute/claude-3-5-sonnet"

    # OpenRouter mode
    cfg.llm.provider = "openrouter"
    router = LLMRouter(cfg)
    assert router.get_active_model() in cfg.llm.free_models

