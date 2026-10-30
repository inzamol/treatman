"""
TM Multi-Provider Brain Router: OmniRoute & OpenRouter Free Tier Fallback Engine
"""

import json
import time
import os
from typing import List, Dict, Any, Optional, Tuple
from tm.config import Config

try:
    import httpx
except ImportError:
    httpx = None


class LLMRouter:
    def __init__(self, config: Config):
        self.config = config
        self.provider = config.llm.provider.lower()
        self.openrouter_api_key = config.llm.openrouter_api_key or os.environ.get("OPENROUTER_API_KEY")
        self.free_models = list(config.llm.free_models)
        self.current_model_index = 0
        self.cooldowns: Dict[str, float] = {}

    def get_active_model(self) -> str:
        """Returns the name of the currently targeted model or router."""
        if self.provider == "omniroute":
            return f"omniroute/{self.config.llm.omniroute_model}"
        elif self.provider == "auto":
            return f"auto (omniroute -> {self.free_models[0]})"
        
        now = time.time()
        for i, model in enumerate(self.free_models):
            cd = self.cooldowns.get(model, 0)
            if now > cd:
                self.current_model_index = i
                return model
        return self.free_models[0]

    def mark_model_cooldown(self, model: str, duration_seconds: float = 60.0) -> None:
        """Temporarily puts a rate-limited model on cooldown."""
        self.cooldowns[model] = time.time() + duration_seconds

    def generate_chat_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
    ) -> Tuple[Optional[str], Optional[List[Dict[str, Any]]], str]:
        """
        Routes chat completion requests according to provider settings:
        - "omniroute": Routes through OmniRoute AI Gateway (https://www.omniroute.online/)
        - "openrouter": Routes through OpenRouter Free Tier models pool
        - "auto": Tries OmniRoute first; cascades to OpenRouter free models, then Ollama
        - "ollama": Routes to local offline Ollama instance
        """
        temp = temperature if temperature is not None else self.config.llm.temperature

        # 1. OmniRoute Explicit Mode
        if self.provider == "omniroute":
            try:
                content, tool_calls = self._call_omniroute(messages, tools, temp)
                return content, tool_calls, f"omniroute/{self.config.llm.omniroute_model}"
            except Exception as e:
                return (
                    f"OmniRoute Gateway error ({self.config.llm.omniroute_base_url}):\n{e}",
                    None,
                    "omniroute_error",
                )

        # 2. Auto Routing (OmniRoute -> OpenRouter -> Ollama)
        if self.provider == "auto":
            diagnostics: List[str] = []

            # Step 1: Attempt OmniRoute
            if self.config.llm.omniroute_enabled:
                try:
                    content, tool_calls = self._call_omniroute(messages, tools, temp)
                    return content, tool_calls, f"omniroute/{self.config.llm.omniroute_model}"
                except Exception as e:
                    diagnostics.append(f"OmniRoute ({self.config.llm.omniroute_base_url}): {e}")

            # Step 2: Attempt OpenRouter free pool
            if self.openrouter_api_key:
                content, tool_calls, model = self._try_openrouter_pool(messages, tools, temp)
                if model != "error":
                    return content, tool_calls, model
                diagnostics.append(f"OpenRouter: {content}")
            else:
                diagnostics.append("OpenRouter: OPENROUTER_API_KEY not configured in .env")

            # Step 3: Attempt Ollama local fallback
            if self.config.llm.ollama_enabled:
                content, tool_calls, model = self._call_ollama(messages, tools)
                if "error" not in model.lower() and "none" not in model.lower():
                    return content, tool_calls, model
                diagnostics.append(f"Ollama ({self.config.llm.ollama_endpoint}): {content}")
            else:
                diagnostics.append("Ollama: Disabled in config")

            # All providers failed - report exact diagnosis
            error_report = (
                "⚠️ All AI Brain routing attempts failed:\n\n"
                + "\n\n".join(f"• {d}" for d in diagnostics)
            )
            return error_report, None, "routing_error"

        # 3. OpenRouter Explicit Mode
        if self.provider == "openrouter":
            if not self.openrouter_api_key:
                if self.config.llm.ollama_enabled:
                    return self._call_ollama(messages, tools)
                return (
                    "OpenRouter API key is missing. Set OPENROUTER_API_KEY in .env or switch provider to 'omniroute'.",
                    None,
                    "none",
                )
            return self._try_openrouter_pool(messages, tools, temp)

        # 4. Ollama Explicit Mode
        if self.provider == "ollama":
            return self._call_ollama(messages, tools)

        return f"Unknown LLM provider '{self.provider}'.", None, "error"

    def _call_omniroute(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]],
        temperature: float,
    ) -> Tuple[Optional[str], Optional[List[Dict[str, Any]]]]:
        """
        Calls OmniRoute AI Gateway (https://www.omniroute.online/).
        OmniRoute serves an OpenAI-compatible /v1/chat/completions route.
        """
        base_url = self.config.llm.omniroute_base_url.rstrip("/")
        if not base_url.endswith("/v1"):
            url = f"{base_url}/v1/chat/completions"
        else:
            url = f"{base_url}/chat/completions"

        api_key = self.config.llm.omniroute_api_key or "omniroute-local"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-Client": "TreatMan-Windows-Agent",
        }

        payload: Dict[str, Any] = {
            "model": self.config.llm.omniroute_model or "auto",
            "messages": messages,
            "temperature": temperature,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        return self._post_openai_compatible(url, headers, payload, timeout=45.0)

    def _try_openrouter_pool(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]],
        temperature: float,
    ) -> Tuple[Optional[str], Optional[List[Dict[str, Any]]], str]:
        """Tries each model in the OpenRouter free pool in order."""
        models_to_try = list(self.free_models)
        last_error = ""

        for model in models_to_try:
            now = time.time()
            if self.cooldowns.get(model, 0) > now:
                continue

            try:
                content, tool_calls = self._call_openrouter(model, messages, tools, temperature)
                return content, tool_calls, model
            except Exception as e:
                err_msg = str(e)
                last_error = err_msg
                if "429" in err_msg or "rate limit" in err_msg.lower() or "503" in err_msg or "502" in err_msg:
                    self.mark_model_cooldown(model, 60.0)
                else:
                    self.mark_model_cooldown(model, 30.0)
                continue

        if self.config.llm.ollama_enabled:
            return self._call_ollama(messages, tools)

        return (
            f"All OpenRouter free models exhausted. Last error: {last_error}",
            None,
            "error",
        )

    def _call_openrouter(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]],
        temperature: float,
    ) -> Tuple[Optional[str], Optional[List[Dict[str, Any]]]]:
        """Makes HTTP request to OpenRouter's completions endpoint."""
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "HTTP-Referer": "https://github.com/treatman/tm",
            "X-Title": "TreatMan Windows AI Agent",
            "Content-Type": "application/json",
        }

        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        return self._post_openai_compatible(url, headers, payload, timeout=60.0)

    def _post_openai_compatible(
        self,
        url: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
        timeout: float = 60.0,
    ) -> Tuple[Optional[str], Optional[List[Dict[str, Any]]]]:
        """Standardized handler for OpenAI-compatible completions endpoints (OmniRoute, OpenRouter)."""
        if httpx is not None:
            with httpx.Client(timeout=timeout) as client:
                resp = client.post(url, headers=headers, json=payload)
                if resp.status_code != 200:
                    try:
                        err_json = resp.json()
                        err_msg = err_json.get("error", {}).get("message") or resp.text
                    except Exception:
                        err_msg = resp.text
                    raise RuntimeError(f"HTTP {resp.status_code}: {err_msg}")
                data = resp.json()
        else:
            import urllib.request
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    data = json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="ignore")
                try:
                    err_json = json.loads(err_body)
                    err_msg = err_json.get("error", {}).get("message") or err_body
                except Exception:
                    err_msg = err_body
                raise RuntimeError(f"HTTP {e.code}: {err_msg}")

        choices = data.get("choices", [])
        if not choices:
            return None, None

        msg = choices[0].get("message", {})
        content = msg.get("content")
        raw_tool_calls = msg.get("tool_calls")

        tool_calls = None
        if raw_tool_calls:
            tool_calls = []
            for tc in raw_tool_calls:
                fn = tc.get("function", {})
                fn_name = fn.get("name")
                raw_args = fn.get("arguments", "{}")
                try:
                    parsed_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                except Exception:
                    parsed_args = {}
                tool_calls.append({
                    "id": tc.get("id", f"call_{int(time.time()*1000)}"),
                    "name": fn_name,
                    "arguments": parsed_args,
                })

        return content, tool_calls

    def _call_ollama(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]],
    ) -> Tuple[Optional[str], Optional[List[Dict[str, Any]]], str]:
        """Local Ollama offline fallback connector."""
        endpoint = f"{self.config.llm.ollama_endpoint.rstrip('/')}/api/chat"
        payload = {
            "model": self.config.llm.ollama_model,
            "messages": messages,
            "stream": False,
        }
        if tools:
            payload["tools"] = tools

        try:
            if httpx is not None:
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(endpoint, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        msg = data.get("message", {})
                        return msg.get("content"), msg.get("tool_calls"), f"ollama/{self.config.llm.ollama_model}"
            else:
                import urllib.request
                req = urllib.request.Request(
                    endpoint,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    msg = data.get("message", {})
                    return msg.get("content"), msg.get("tool_calls"), f"ollama/{self.config.llm.ollama_model}"
        except Exception as e:
            return f"Ollama local fallback error: {e}", None, "ollama_error"

        return "Ollama returned no message", None, "ollama_none"
