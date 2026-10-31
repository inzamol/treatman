"""
TM ReAct Agent Orchestrator & Execution Loop
"""

import json
import time
from typing import List, Dict, Any, Optional, Callable, Generator
from tm.config import Config, get_config
from tm.core.persona import get_system_prompt
from tm.core.guardrails import GuardrailManager
from tm.core.memory import MemoryManager
from tm.core.llm_router import LLMRouter
import tm.tools  # Register all tools
from tm.tools.base import registry


class TMAgent:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or get_config()
        self.guardrails = GuardrailManager(self.config)
        self.memory = MemoryManager(self.config)
        self.router = LLMRouter(self.config)
        self.system_prompt = get_system_prompt(self.config)
        self.conversation_history: List[Dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt}
        ]

    def reset_conversation(self) -> None:
        """Resets active session conversation while preserving long-term SQLite memory."""
        self.conversation_history = [
            {"role": "system", "content": get_system_prompt(self.config)}
        ]

    def execute_turn(
        self,
        user_message: str,
        confirmation_callback: Optional[Callable[[str, Dict[str, Any], str], bool]] = None,
        status_callback: Optional[Callable[[str, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Runs a complete ReAct multi-step reasoning turn for a user prompt.
        - confirmation_callback(tool_name, args, reason) -> bool: returns True if user approves.
        - status_callback(status_type, message): informs UI of ongoing agent state.
        """
        self.conversation_history.append({"role": "user", "content": user_message})

        tools_schema = registry.get_openai_schemas()
        max_turns = self.config.agent.max_react_turns
        actions_taken: List[Dict[str, Any]] = []
        turn_count = 0

        while turn_count < max_turns:
            turn_count += 1
            if status_callback:
                status_callback("thinking", f"Reasoning with {self.router.get_active_model()}...")

            content, tool_calls, model_used = self.router.generate_chat_completion(
                messages=self.conversation_history,
                tools=tools_schema,
            )

            # If no tool calls were generated, we have our final text answer
            if not tool_calls:
                final_text = content or "Task completed, Sir."
                self.conversation_history.append({"role": "assistant", "content": final_text})
                return {
                    "response": final_text,
                    "actions": actions_taken,
                    "model_used": model_used,
                    "turns": turn_count,
                }

            # Assistant response with tool calls
            assistant_msg: Dict[str, Any] = {
                "role": "assistant",
                "content": content or "",
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["arguments"]),
                        },
                    }
                    for tc in tool_calls
                ],
            }
            self.conversation_history.append(assistant_msg)

            # Execute each requested tool call
            for tc in tool_calls:
                t_name = tc["name"]
                t_args = tc["arguments"]
                t_id = tc["id"]

                tool_obj = registry.get(t_name)
                if not tool_obj:
                    obs_content = f"Error: Tool '{t_name}' is not recognized."
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": t_id,
                        "name": t_name,
                        "content": json.dumps({"error": obs_content}),
                    })
                    continue

                # Guardrail evaluation
                is_allowed, req_confirm, reason = self.guardrails.evaluate_tool_permission(t_name, t_args)

                if not is_allowed:
                    obs_content = f"Operation denied by security policy: {reason}"
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": t_id,
                        "name": t_name,
                        "content": json.dumps({"error": obs_content}),
                    })
                    actions_taken.append({"tool": t_name, "args": t_args, "status": "blocked", "reason": reason})
                    continue

                # Confirmation check
                if req_confirm:
                    if confirmation_callback:
                        approved = confirmation_callback(t_name, t_args, reason)
                    else:
                        approved = False
                        reason = f"Confirmation required for '{t_name}', but no interactive confirmation callback was provided."

                    if not approved:
                        obs_content = reason if not confirmation_callback else "Action cancelled: User denied permission."
                        self.conversation_history.append({
                            "role": "tool",
                            "tool_call_id": t_id,
                            "name": t_name,
                            "content": json.dumps({"status": "cancelled", "message": obs_content}),
                        })
                        actions_taken.append({"tool": t_name, "args": t_args, "status": "cancelled", "reason": reason})
                        continue

                # Execute tool
                if status_callback:
                    status_callback("executing", f"Executing {t_name}...")

                start_time = time.time()
                try:
                    res = tool_obj.execute(**t_args)
                    duration_ms = int((time.time() - start_time) * 1000)
                    res_str = json.dumps(res, default=str)
                    if isinstance(res, dict) and res.get("status") in ["error", "blocked", "cancelled"]:
                        status_str = res["status"]
                    elif isinstance(res, dict) and res.get("exit_code", 0) != 0:
                        status_str = "error"
                    else:
                        status_str = "success"
                except Exception as e:
                    duration_ms = int((time.time() - start_time) * 1000)
                    res = {"status": "error", "message": str(e)}
                    res_str = json.dumps(res)
                    status_str = "error"

                # Record in persistent audit log
                self.memory.record_audit(t_name, t_args, status_str, res_str, duration_ms)
                actions_taken.append({
                    "tool": t_name,
                    "args": t_args,
                    "status": status_str,
                    "result": res,
                    "duration_ms": duration_ms,
                })

                # Append tool observation
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": t_id,
                    "name": t_name,
                    "content": res_str,
                })

        # Exceeded max turns
        fallback_msg = "Sir, I have executed the initial sequence of actions, but reached the maximum reasoning steps for this turn."
        self.conversation_history.append({"role": "assistant", "content": fallback_msg})
        return {
            "response": fallback_msg,
            "actions": actions_taken,
            "model_used": self.router.get_active_model(),
            "turns": turn_count,
        }

