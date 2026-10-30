"""
TM (TreatMan) - Central CLI Launcher
"""

import sys

# Ensure UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
from tm.config import get_config
from tm.core.memory import MemoryManager
from tm.core.agent import TMAgent
from tm.tools.base import registry
import tm.tools  # Register tools


def run_diagnostics():
    """Runs a complete self-check of system components, tools, and configuration."""
    print("=" * 60)
    print("TM (TreatMan) System Diagnostics")
    print("=" * 60)
    config = get_config()

    print(f"\n[1] Configuration:")
    print(f"  • Agent Name:     {config.agent.name}")
    print(f"  • User Title:     {config.agent.user_title}")
    print(f"  • Autonomy Level: {config.autonomy.level.upper()}")
    print(f"  • LLM Provider:   {config.llm.provider.upper()}")
    print(f"  • OmniRoute URL:  {config.llm.omniroute_base_url} (Model: {config.llm.omniroute_model})")
    print(f"  • OpenRouter Key: {'[Configured]' if config.llm.openrouter_api_key else '[Not Set]'}")
    print(f"  • Data Directory: {config.paths.data_dir}")

    print(f"\n[2] Registered Tools ({len(registry.list_all())} total):")
    for t in registry.list_all():
        print(f"  • {t.name:<26} (Tier {t.tier}) - {t.description[:50]}...")

    print(f"\n[3] Free Model Hierarchy:")
    for i, m in enumerate(config.llm.free_models, 1):
        print(f"  {i}. {m}")

    print(f"\n[4] Local Hardware & OS Connectivity:")
    sys_stats = registry.get("get_system_stats").execute()
    print(f"  • CPU Percent:    {sys_stats.get('cpu_percent')}%")
    print(f"  • RAM Usage:      {sys_stats.get('memory_used_gb')}GB / {sys_stats.get('memory_total_gb')}GB")
    if sys_stats.get('battery_percent') is not None:
        print(f"  • Battery:        {sys_stats.get('battery_percent')}% (Plugged: {sys_stats.get('power_plugged')})")

    print("\nDiagnostics complete. System ready for operation.\n")


def print_audit_log():
    """Displays the recent execution audit history from SQLite."""
    config = get_config()
    mem = MemoryManager(config)
    logs = mem.get_recent_audit_logs(limit=20)
    print("=" * 80)
    print(f"Recent TM Execution Audit Log ({len(logs)} records)")
    print("=" * 80)
    if not logs:
        print("No audit records found yet.")
        return

    for entry in logs:
        ts = entry["timestamp"][:19]
        tool = entry["tool_name"]
        status = entry["status"]
        dur = f"{entry.get('duration_ms', 0)}ms"
        print(f"[{ts}] {tool:<22} -> {status:<8} ({dur}) | Args: {entry['arguments'][:50]}")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="TM (TreatMan) - Autonomous Windows AI Operator")
    parser.add_argument("--cli", action="store_true", help="Launch interactive Rich Terminal REPL")
    parser.add_argument("--voice", action="store_true", help="Launch interactive mode with neural JARVIS voice")
    parser.add_argument("--daemon", action="store_true", help="Run background system tray daemon")
    parser.add_argument("--hud", action="store_true", help="Launch floating desktop HUD widget")
    parser.add_argument("--test", action="store_true", help="Run diagnostic self-check")
    parser.add_argument("--audit", action="store_true", help="View recent execution audit log")
    parser.add_argument("command", nargs="*", help="One-shot prompt to execute")

    args = parser.parse_args()

    if args.test:
        run_diagnostics()
        return

    if args.audit:
        print_audit_log()
        return

    if args.voice:
        from tm.interfaces.voice_mode import run_voice_mode
        run_voice_mode()
        return

    if args.daemon:
        from tm.interfaces.daemon import run_daemon
        run_daemon()
        return

    if args.hud:
        from tm.interfaces.hud import run_hud
        run_hud()
        return

    if args.command:
        # One-shot command execution
        prompt = " ".join(args.command)
        config = get_config()
        agent = TMAgent(config)
        print(f"Executing: {prompt}")
        result = agent.execute_turn(prompt)
        print(f"\n{config.agent.name}: {result.get('response')}\n")
        return

    # Default to Interactive CLI
    from tm.interfaces.cli import run_cli
    run_cli()


if __name__ == "__main__":
    main()

