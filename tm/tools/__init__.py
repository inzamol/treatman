"""
TM Unified Tools Package
Importing this package automatically registers all available tools.
"""

from tm.tools.base import registry, tool
from tm.tools import (
    system_tools,
    shell_tools,
    file_tools,
    web_tools,
    vision_tools,
)

__all__ = [
    "registry",
    "tool",
    "system_tools",
    "shell_tools",
    "file_tools",
    "web_tools",
    "vision_tools",
]
