"""
TM (TreatMan) - Autonomous Windows AI Agent (JARVIS-like)
"""

from tm.config import Config, get_config
from tm.core.agent import TMAgent
from tm.core.llm_router import LLMRouter
from tm.core.guardrails import GuardrailManager
from tm.core.memory import MemoryManager
from tm.tools.base import registry, tool
from tm.voice.ear import Ear
from tm.voice.speaker import Speaker

__version__ = "0.1.0"
__author__ = "TreatMan Project"
__all__ = [
    "Config",
    "get_config",
    "TMAgent",
    "LLMRouter",
    "GuardrailManager",
    "MemoryManager",
    "registry",
    "tool",
    "Ear",
    "Speaker",
]
