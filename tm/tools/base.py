"""
TM Base Tool Registry and Schema Generator
"""

import inspect
from typing import Callable, Dict, Any, List, Optional


class Tool:
    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        func: Callable,
        tier: int = 2,
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.func = func
        self.tier = tier  # 1: Read/Safe, 2: Safe Modification, 3: Critical/Destructive

    def to_openai_schema(self) -> Dict[str, Any]:
        """Converts tool definition to OpenAI/OpenRouter function calling schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def execute(self, **kwargs) -> Any:
        return self.func(**kwargs)


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def list_all(self) -> List[Tool]:
        return list(self._tools.values())

    def get_openai_schemas(self) -> List[Dict[str, Any]]:
        return [tool.to_openai_schema() for tool in self._tools.values()]


# Global Tool Registry
registry = ToolRegistry()


def tool(
    name: str,
    description: str,
    parameters: Dict[str, Any],
    tier: int = 2,
):
    """Decorator to register a function as a TM Tool."""
    def decorator(func: Callable):
        t = Tool(
            name=name,
            description=description,
            parameters=parameters,
            func=func,
            tier=tier,
        )
        registry.register(t)
        return func
    return decorator

