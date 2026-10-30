import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

try:
    import yaml
except ImportError:
    yaml = None


def load_env_file(env_path: Path) -> None:
    """Manually parse .env file into os.environ if python-dotenv is not installed."""
    if not env_path.exists():
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key not in os.environ or not os.environ[key]:
                        os.environ[key] = val
    except Exception:
        pass


@dataclass
class AgentConfig:
    name: str = "TM"
    user_title: str = "Sir"
    persona_style: str = "jarvis"
    max_react_turns: int = 10


@dataclass
class AutonomyConfig:
    level: str = "balanced"  # strict | balanced | autonomous
    rules: Dict[str, bool] = field(default_factory=lambda: {
        "allow_app_launch": True,
        "allow_app_close": True,
        "allow_system_volume_brightness": True,
        "allow_web_browsing": True,
        "allow_file_reading": True,
        "allow_file_writing": True,
        "require_confirmation_for_file_delete": True,
        "require_confirmation_for_shell_execution": False,
        "require_confirmation_for_process_kill": True,
        "require_confirmation_for_system_power": True,
    })
    forbidden_commands: List[str] = field(default_factory=lambda: [
        "format ",
        "rmdir /s /q c:\\",
        "Remove-Item -Recurse -Force C:\\",
        "del /f /s /q c:\\",
        "diskpart",
        "bcdedit",
        "Drop-Database",
        "TRUNCATE TABLE",
        "Stop-Computer",
    ])


@dataclass
class LLMConfig:
    provider: str = "auto"  # "auto" | "omniroute" | "openrouter" | "ollama"
    temperature: float = 0.2
    
    # OmniRoute (https://www.omniroute.online/)
    omniroute_enabled: bool = True
    omniroute_base_url: str = "http://localhost:20128/v1"
    omniroute_api_key: Optional[str] = None
    omniroute_model: str = "auto"

    # OpenRouter
    openrouter_api_key: Optional[str] = None
    free_models: List[str] = field(default_factory=lambda: [
        "meta-llama/llama-3.3-70b-instruct:free",
        "google/gemini-2.0-flash-exp:free",
        "deepseek/deepseek-r1:free",
        "qwen/qwen-2.5-coder-32b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
    ])
    
    # Local Offline Ollama
    ollama_enabled: bool = True
    ollama_endpoint: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:latest"


@dataclass
class VoiceConfig:
    enabled: bool = True
    wake_word: str = "hey tm"
    voice_id: str = "en-GB-RyanNeural"
    rate: str = "+0%"
    pitch: str = "+0Hz"
    barge_in: bool = True
    silence_threshold_seconds: float = 1.2


@dataclass
class PathsConfig:
    data_dir: Path = field(default_factory=lambda: Path.home() / ".treatman")
    recycle_bin_safety: bool = True


@dataclass
class Config:
    agent: AgentConfig = field(default_factory=AgentConfig)
    autonomy: AutonomyConfig = field(default_factory=AutonomyConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    voice: VoiceConfig = field(default_factory=VoiceConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)

    @classmethod
    def load(cls, project_root: Optional[Path] = None) -> "Config":
        if project_root is None:
            project_root = Path(__file__).resolve().parent.parent

        # 1. Load .env
        env_file = project_root / ".env"
        load_env_file(env_file)

        # 2. Load config.yaml if available
        config_path = project_root / "config.yaml"
        raw_cfg: Dict[str, Any] = {}
        if config_path.exists() and yaml is not None:
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    raw_cfg = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"[Warning] Failed to parse config.yaml: {e}", file=sys.stderr)

        instance = cls()

        # Populate Agent
        agent_raw = raw_cfg.get("agent", {})
        instance.agent.name = agent_raw.get("name", instance.agent.name)
        instance.agent.user_title = agent_raw.get("user_title", instance.agent.user_title)
        instance.agent.persona_style = agent_raw.get("persona_style", instance.agent.persona_style)
        instance.agent.max_react_turns = agent_raw.get("max_react_turns", instance.agent.max_react_turns)

        # Populate Autonomy
        auto_raw = raw_cfg.get("autonomy", {})
        instance.autonomy.level = auto_raw.get("level", instance.autonomy.level).lower()
        if "rules" in auto_raw:
            instance.autonomy.rules.update(auto_raw["rules"])
        if "forbidden_commands" in auto_raw:
            instance.autonomy.forbidden_commands = auto_raw["forbidden_commands"]

        # Populate LLM
        llm_raw = raw_cfg.get("llm", {})
        instance.llm.provider = llm_raw.get("provider", instance.llm.provider).lower()
        instance.llm.temperature = float(llm_raw.get("temperature", instance.llm.temperature))
        if "free_models" in llm_raw and isinstance(llm_raw["free_models"], list):
            instance.llm.free_models = llm_raw["free_models"]

        # OmniRoute (https://www.omniroute.online/)
        omniroute_raw = llm_raw.get("omniroute", {})
        instance.llm.omniroute_enabled = omniroute_raw.get("enabled", instance.llm.omniroute_enabled)
        instance.llm.omniroute_base_url = (
            os.environ.get("OMNIROUTE_BASE_URL")
            or omniroute_raw.get("base_url")
            or instance.llm.omniroute_base_url
        )
        instance.llm.omniroute_api_key = (
            os.environ.get("OMNIROUTE_API_KEY")
            or omniroute_raw.get("api_key")
        )
        instance.llm.omniroute_model = (
            os.environ.get("OMNIROUTE_MODEL")
            or omniroute_raw.get("model")
            or instance.llm.omniroute_model
        )

        # Ollama
        ollama_raw = llm_raw.get("ollama", {})
        instance.llm.ollama_enabled = ollama_raw.get("enabled", instance.llm.ollama_enabled)
        instance.llm.ollama_endpoint = (
            os.environ.get("OLLAMA_ENDPOINT")
            or ollama_raw.get("endpoint")
            or instance.llm.ollama_endpoint
        )
        instance.llm.ollama_model = ollama_raw.get("model", instance.llm.ollama_model)

        instance.llm.openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")

        # Populate Voice
        voice_raw = raw_cfg.get("voice", {})
        instance.voice.enabled = voice_raw.get("enabled", instance.voice.enabled)
        instance.voice.wake_word = voice_raw.get("wake_word", instance.voice.wake_word)
        tts_raw = voice_raw.get("text_to_speech", {})
        instance.voice.voice_id = tts_raw.get("voice", instance.voice.voice_id)
        instance.voice.rate = tts_raw.get("rate", instance.voice.rate)
        instance.voice.pitch = tts_raw.get("pitch", instance.voice.pitch)
        instance.voice.barge_in = tts_raw.get("barge_in", instance.voice.barge_in)

        # Populate Paths
        paths_raw = raw_cfg.get("paths", {})
        raw_data_dir = paths_raw.get("data_dir", "~/.treatman")
        instance.paths.data_dir = Path(os.path.expanduser(raw_data_dir))
        instance.paths.recycle_bin_safety = paths_raw.get("recycle_bin_safety", instance.paths.recycle_bin_safety)

        # Ensure data directory exists
        try:
            instance.paths.data_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

        return instance


# Global singleton
_config: Optional[Config] = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config.load()
    return _config

