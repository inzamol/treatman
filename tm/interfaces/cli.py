"""
TM Interactive Rich Terminal CLI
"""

import sys

# Ensure UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
from typing import Dict, Any
from tm.config import Config, get_config
from tm.core.agent import TMAgent

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.prompt import Confirm
    from rich.table import Table
    from rich.text import Text
    console = Console()
except ImportError:
    console = None


BANNER = r"""
  _______ __  __   ____  _____ 
 |__   __|  \/  | / __ \|  __ \
    | |  | \  / || |  | | |__) |
    | |  | |\/| || |  | |  _  / 
    | |  | |  | || |__| | | \ \ 
    |_|  |_|  |_| \____/|_|  \_\
  Autonomous Windows AI Operator
"""


def print_banner(config: Config) -> None:
    if console:
        console.print(Panel(
            Text(BANNER, style="bold cyan", justify="center"),
            title=f"[bold green]TM v0.1.0[/bold green] - Autonomy: [bold yellow]{config.autonomy.level.upper()}[/bold yellow]",
            subtitle="Type your command or 'exit' to quit | 'reset' to clear context",
            border_style="bright_blue",
        ))
    else:
        print(BANNER)
        print(f"TM v0.1.0 - Autonomy: {config.autonomy.level.upper()}")
        print("Type your command or 'exit' to quit | 'reset' to clear context\n")


def confirmation_handler(tool_name: str, args: Dict[str, Any], reason: str) -> bool:
    """Prompts the user for interactive approval for sensitive operations."""
    if console:
        console.print(Panel(
            f"[bold yellow]⚠️ Permission Request[/bold yellow]\n\n"
            f"[bold cyan]Action:[/bold cyan] {reason}\n"
            f"[bold cyan]Tool:[/bold cyan] {tool_name}\n"
            f"[bold cyan]Arguments:[/bold cyan] {json.dumps(args, indent=2)}",
            border_style="yellow",
        ))
        try:
            return Confirm.ask("[bold yellow]Do you authorize TM to proceed?[/bold yellow]", default=True)
        except (KeyboardInterrupt, EOFError):
            return False
    else:
        print(f"\n[PERMISSION REQUIRED] {reason}")
        print(f"Tool: {tool_name} with args {args}")
        ans = input("Authorize? (Y/n): ").strip().lower()
        return ans in ["", "y", "yes"]


def status_handler(status_type: str, message: str) -> None:
    if console:
        if status_type == "thinking":
            console.print(f"[dim italic cyan]⚡ {message}[/dim italic cyan]")
        elif status_type == "executing":
            console.print(f"[bold yellow]⚙️  {message}[/bold yellow]")
    else:
        print(f">> {message}")


def run_cli():
    """Main interactive REPL loop."""
    config = get_config()
    agent = TMAgent(config)

    print_banner(config)

    # Check Provider Status
    info = (
        f"[bold cyan]Provider Mode:[/bold cyan] {config.llm.provider.upper()}\n"
        f"[bold cyan]OmniRoute Gateway:[/bold cyan] {config.llm.omniroute_base_url} (Model: {config.llm.omniroute_model})\n"
        f"[bold cyan]OpenRouter Fallback:[/bold cyan] {'Configured' if config.llm.openrouter_api_key else 'Not Set (Set in .env if desired)'}\n"
        f"[bold cyan]Local Ollama Fallback:[/bold cyan] {config.llm.ollama_endpoint if config.llm.ollama_enabled else 'Disabled'}"
    )
    if console:
        console.print(Panel(info, title="AI Brain Routing Status", border_style="cyan"))
    else:
        print(f"Provider: {config.llm.provider.upper()} | OmniRoute: {config.llm.omniroute_base_url}")

    while True:
        try:
            if console:
                prompt_text = f"\n[bold green]{config.agent.user_title}>[/bold green] "
                user_input = console.input(prompt_text).strip()
            else:
                user_input = input(f"\n{config.agent.user_title}> ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                if console:
                    console.print(f"[cyan]Shutting down. Good day, {config.agent.user_title}.[/cyan]")
                else:
                    print(f"Shutting down. Good day, {config.agent.user_title}.")
                break

            if user_input.lower() in ["reset", "clear"]:
                agent.reset_conversation()
                if console:
                    console.print("[green]Conversation context reset.[/green]")
                else:
                    print("Conversation context reset.")
                continue

            result = agent.execute_turn(
                user_message=user_input,
                confirmation_callback=confirmation_handler,
                status_callback=status_handler,
            )

            # Display actions summary if any were taken
            actions = result.get("actions", [])
            if actions and console:
                table = Table(title="Operations Executed", show_header=True, header_style="bold magenta")
                table.add_column("Tool", style="cyan")
                table.add_column("Status", style="green")
                table.add_column("Duration", justify="right")
                for a in actions:
                    dur = f"{a.get('duration_ms', 0)}ms"
                    st = a.get("status", "done")
                    style = "green" if st == "success" else ("yellow" if st == "cancelled" else "red")
                    table.add_row(a.get("tool"), f"[{style}]{st}[/{style}]", dur)
                console.print(table)

            # Display final JARVIS reply
            response_text = result.get("response", "")
            if console:
                console.print(Panel(
                    Markdown(response_text),
                    title=f"[bold cyan]{config.agent.name}[/bold cyan] ([dim]{result.get('model_used', 'ai')}[/dim])",
                    border_style="cyan",
                ))
            else:
                print(f"\n{config.agent.name}: {response_text}\n")

        except KeyboardInterrupt:
            print("\nInterrupt received. Exiting.")
            break
        except Exception as e:
            if console:
                console.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
            else:
                print(f"Error: {e}")

